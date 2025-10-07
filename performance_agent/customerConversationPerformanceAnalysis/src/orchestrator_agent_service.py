"""
Orchestrator Agent Service for managing per-category LLM analysis
This service coordinates multiple LLM calls per category to avoid incomplete responses
"""

import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

try:
    from .models import ConversationData, Tweet, Classification
    from .config_loader import config_loader, KPIConfig
    from .llm_agent_service import LLMAgentPerformanceAnalysisService
except ImportError:
    # Fallback for direct execution
    from models import ConversationData, Tweet, Classification
    from config_loader import config_loader, KPIConfig
    from llm_agent_service import LLMAgentPerformanceAnalysisService


class OrchestratorAgent:
    """
    Orchestrator Agent that manages per-category LLM analysis and collates results
    This approach ensures complete analysis by breaking down the task into smaller, manageable chunks
    """
    
    def __init__(self, model_name: str = "claude-4", temperature: float = 0.1, 
                 max_retries: int = 3, parallel_categories: bool = False):
        """
        Initialize the Orchestrator Agent
        
        Args:
            model_name: Name of the LLM model to use
            temperature: Temperature setting for the LLM
            max_retries: Maximum number of retries for failed category analysis
            parallel_categories: Whether to analyze categories in parallel
        """
        self.logger = logging.getLogger(__name__)
        self.model_name = model_name
        self.temperature = temperature
        self.max_retries = max_retries
        self.parallel_categories = parallel_categories
        
        # Initialize the LLM agent service for category-specific analysis
        self.llm_agent = LLMAgentPerformanceAnalysisService(
            model_name=model_name,
            temperature=temperature
        )
        
        # Load configuration
        try:
            self.config = config_loader.load_config()
            self.logger.info("Configuration loaded successfully for Orchestrator Agent")
        except Exception as e:
            self.logger.error(f"Failed to load configuration: {e}")
            raise
    
    def analyze_conversation_comprehensive(self, conversation_data: ConversationData) -> Dict[str, Any]:
        """
        Main entry point for comprehensive conversation analysis using orchestrator approach
        
        Args:
            conversation_data: Input conversation data
            
        Returns:
            Dictionary with comprehensive performance metrics
        """
        try:
            self.logger.info("Starting orchestrator-based comprehensive analysis")
            start_time = time.time()
            
            # Get all categories that need to be analyzed
            all_categories = list(config_loader.get_all_categories())
            self.logger.info(f"Orchestrator will analyze {len(all_categories)} categories: {all_categories}")
            
            # Analyze categories either in parallel or sequentially
            if self.parallel_categories:
                category_results = self._analyze_categories_parallel(conversation_data, all_categories)
            else:
                category_results = self._analyze_categories_sequential(conversation_data, all_categories)
            
            # Collate results from all categories
            comprehensive_results = self._collate_category_results(
                category_results, 
                conversation_data,
                start_time
            )
            
            analysis_duration = time.time() - start_time
            self.logger.info(f"Orchestrator analysis completed in {analysis_duration:.2f} seconds")
            
            return comprehensive_results
            
        except Exception as e:
            self.logger.error(f"Error in orchestrator comprehensive analysis: {e}")
            return {
                "error": str(e),
                "conversation_id": getattr(conversation_data, 'conversation_number', None) or getattr(conversation_data, 'conversation_id', 'unknown'),
                "analysis_timestamp": datetime.now().isoformat(),
                "analysis_method": "Orchestrator-based Analysis (Failed)"
            }
    
    def _analyze_categories_sequential(self, conversation_data: ConversationData, 
                                     categories: List[str]) -> Dict[str, Dict[str, Any]]:
        """
        Analyze categories sequentially (one after another)
        
        Args:
            conversation_data: Input conversation data
            categories: List of category names to analyze
            
        Returns:
            Dictionary mapping category names to their analysis results
        """
        category_results = {}
        
        for i, category_name in enumerate(categories, 1):
            self.logger.info(f"Analyzing category {i}/{len(categories)}: {category_name}")
            
            # Analyze this specific category with retry logic
            category_result = self._analyze_single_category_with_retry(
                conversation_data, 
                category_name
            )
            
            if category_result:
                category_results[category_name] = category_result
                kpi_count = len(category_result.get('kpis', {}))
                self.logger.info(f"✓ Category {category_name} analyzed successfully ({kpi_count} KPIs)")
            else:
                self.logger.error(f"✗ Failed to analyze category {category_name} after retries")
                # Create fallback result for failed category
                category_results[category_name] = self._create_fallback_category_result(
                    category_name, 
                    "Analysis failed after retries"
                )
        
        return category_results
    
    def _analyze_categories_parallel(self, conversation_data: ConversationData, 
                                   categories: List[str]) -> Dict[str, Dict[str, Any]]:
        """
        Analyze categories in parallel (simultaneously)
        
        Args:
            conversation_data: Input conversation data
            categories: List of category names to analyze
            
        Returns:
            Dictionary mapping category names to their analysis results
        """
        category_results = {}
        max_workers = min(len(categories), 3)  # Limit concurrent LLM calls
        
        self.logger.info(f"Starting parallel analysis of {len(categories)} categories with {max_workers} workers")
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all category analysis tasks
            future_to_category = {
                executor.submit(
                    self._analyze_single_category_with_retry, 
                    conversation_data, 
                    category_name
                ): category_name
                for category_name in categories
            }
            
            # Collect results as they complete
            for future in as_completed(future_to_category):
                category_name = future_to_category[future]
                
                try:
                    category_result = future.result(timeout=120)  # 2-minute timeout per category
                    
                    if category_result:
                        category_results[category_name] = category_result
                        kpi_count = len(category_result.get('kpis', {}))
                        self.logger.info(f"✓ Category {category_name} analyzed successfully ({kpi_count} KPIs)")
                    else:
                        self.logger.error(f"✗ Failed to analyze category {category_name}")
                        category_results[category_name] = self._create_fallback_category_result(
                            category_name, 
                            "Analysis failed"
                        )
                        
                except Exception as e:
                    self.logger.error(f"Exception analyzing category {category_name}: {e}")
                    category_results[category_name] = self._create_fallback_category_result(
                        category_name, 
                        f"Analysis exception: {str(e)}"
                    )
        
        return category_results
    
    def _analyze_single_category_with_retry(self, conversation_data: ConversationData, 
                                          category_name: str) -> Optional[Dict[str, Any]]:
        """
        Analyze a single category with retry logic
        
        Args:
            conversation_data: Input conversation data
            category_name: Name of the category to analyze
            
        Returns:
            Category analysis result or None if all retries failed
        """
        for attempt in range(1, self.max_retries + 1):
            try:
                self.logger.info(f"Analyzing category '{category_name}' (attempt {attempt}/{self.max_retries})")
                
                # Use the existing LLM agent's category-specific analysis
                result = self.llm_agent.analyze_conversation_category(conversation_data, category_name)
                
                # Parse and validate the result
                parsed_result = self._parse_category_analysis_result(result, category_name)
                
                if parsed_result and self._validate_category_result(parsed_result, category_name):
                    self.logger.info(f"✓ Category '{category_name}' analysis successful on attempt {attempt}")
                    return parsed_result
                else:
                    self.logger.warning(f"Category '{category_name}' analysis incomplete on attempt {attempt}")
                    if attempt < self.max_retries:
                        time.sleep(1 * attempt)  # Exponential backoff
                        continue
                
            except Exception as e:
                self.logger.error(f"Error analyzing category '{category_name}' on attempt {attempt}: {e}")
                if attempt < self.max_retries:
                    time.sleep(2 * attempt)  # Exponential backoff
                    continue
                else:
                    self.logger.error(f"All retry attempts failed for category '{category_name}'")
        
        return None
    
    def _parse_category_analysis_result(self, raw_result: Dict[str, Any], 
                                      category_name: str) -> Optional[Dict[str, Any]]:
        """
        Parse the raw category analysis result from LLM agent
        
        Args:
            raw_result: Raw result from LLM agent category analysis
            category_name: Name of the category being analyzed
            
        Returns:
            Parsed category result or None if parsing failed
        """
        try:
            # Extract analysis result from the raw result
            analysis_result = raw_result.get("analysis_result", "")
            
            if not analysis_result:
                self.logger.warning(f"No analysis result found for category {category_name}")
                return None
            
            # Parse the analysis result to extract KPI scores and details
            parsed_kpis = self._extract_kpis_from_analysis_result(analysis_result, category_name)
            
            if not parsed_kpis:
                self.logger.warning(f"No KPIs extracted from analysis for category {category_name}")
                return None
            
            # Create structured category result
            category_result = {
                "name": category_name,
                "kpis": parsed_kpis,
                "category_score": self._calculate_category_score(parsed_kpis),
                "analysis_timestamp": raw_result.get("analysis_timestamp", datetime.now().isoformat()),
                "analysis_method": "Orchestrator per-category analysis"
            }
            
            category_result["category_performance"] = self._get_performance_level(
                category_result["category_score"]
            )
            
            return category_result
            
        except Exception as e:
            self.logger.error(f"Error parsing category analysis result for {category_name}: {e}")
            return None
    
    def _extract_kpis_from_analysis_result(self, analysis_result: str, 
                                         category_name: str) -> Dict[str, Any]:
        """
        Extract KPI analysis from the LLM analysis result
        
        Args:
            analysis_result: Raw analysis text from LLM
            category_name: Name of the category
            
        Returns:
            Dictionary of KPI analyses
        """
        try:
            import re
            import json
            
            kpis = {}
            
            # Get expected KPIs for this category
            category_kpis = config_loader.get_category_kpis(category_name)
            expected_kpi_names = list(category_kpis.keys())
            
            self.logger.info(f"Extracting KPIs for category {category_name}: {expected_kpi_names}")
            
            # Look for JSON analysis blocks in the result
            json_pattern = r'```json\s*(\{[^`]+\})\s*```'
            json_matches = re.findall(json_pattern, analysis_result, re.DOTALL)
            
            for json_str in json_matches:
                try:
                    json_data = json.loads(json_str.strip())
                    
                    if 'score' in json_data and 'reasoning' in json_data:
                        # Try to identify which KPI this belongs to
                        json_start = analysis_result.find(json_str)
                        context_before = analysis_result[max(0, json_start-1000):json_start]
                        
                        kpi_name = self._extract_kpi_name_from_context(context_before, expected_kpi_names)
                        
                        if kpi_name:
                            kpis[kpi_name] = {
                                "name": kpi_name,
                                "score": float(json_data.get('score', 5.0)),
                                "normalized_score": float(json_data.get('normalized_score', json_data.get('score', 5.0) / 10.0)),
                                "reasoning": json_data.get('reasoning', ''),
                                "evidence": json_data.get('evidence', []),
                                "confidence": float(json_data.get('confidence', 0.8)),
                                "interpretation": json_data.get('interpretation', self._get_performance_level(json_data.get('score', 5.0))),
                                "recommendations": json_data.get('recommendations', [])
                            }
                            
                            self.logger.info(f"✓ Extracted KPI analysis for {kpi_name} (score: {json_data.get('score')})")
                
                except json.JSONDecodeError:
                    continue
            
            # Fill in any missing KPIs with fallback analysis
            for expected_kpi in expected_kpi_names:
                if expected_kpi not in kpis:
                    self.logger.warning(f"KPI {expected_kpi} not found in analysis, creating fallback")
                    kpis[expected_kpi] = self._create_fallback_kpi_analysis(expected_kpi, category_name)
            
            self.logger.info(f"Successfully extracted {len(kpis)} KPIs for category {category_name}")
            return kpis
            
        except Exception as e:
            self.logger.error(f"Error extracting KPIs from analysis result for {category_name}: {e}")
            return {}
    
    def _extract_kpi_name_from_context(self, context: str, expected_kpis: List[str]) -> Optional[str]:
        """
        Extract KPI name from context, prioritizing expected KPIs for this category
        
        Args:
            context: Context text around JSON analysis
            expected_kpis: List of expected KPI names for this category
            
        Returns:
            KPI name if found, None otherwise
        """
        try:
            import re
            
            # Look for exact matches with expected KPIs first
            for expected_kpi in expected_kpis:
                if expected_kpi.lower() in context.lower():
                    return expected_kpi
            
            # General pattern matching as fallback
            patterns = [
                r'analyzing\s+([^\n\r]+)\s+(?:kpi|analysis)',
                r'kpi[:\s]+([^\n\r]+)',
                r'configuration for\s+([^\n\r]+)',
            ]
            
            for pattern in patterns:
                match = re.search(pattern, context, re.IGNORECASE)
                if match:
                    potential_kpi = match.group(1).strip().strip('"\'')
                    
                    # Check if this matches any expected KPI
                    for expected_kpi in expected_kpis:
                        if (potential_kpi.lower() in expected_kpi.lower() or 
                            expected_kpi.lower() in potential_kpi.lower()):
                            return expected_kpi
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error extracting KPI name from context: {e}")
            return None
    
    def _create_fallback_kpi_analysis(self, kpi_name: str, category_name: str) -> Dict[str, Any]:
        """
        Create fallback KPI analysis when LLM analysis is not available
        
        Args:
            kpi_name: Name of the KPI
            category_name: Category name
            
        Returns:
            Fallback KPI analysis dictionary
        """
        try:
            return {
                "name": kpi_name,
                "score": 6.0,  # Neutral score
                "normalized_score": 0.6,
                "reasoning": f"Fallback analysis for {kpi_name.replace('_', ' ')} in category {category_name}. Limited evidence available for detailed assessment.",
                "evidence": [],
                "confidence": 0.5,
                "interpretation": "Good",
                "recommendations": [f"Review {kpi_name.replace('_', ' ')} performance in future interactions"]
            }
        except Exception as e:
            self.logger.error(f"Error creating fallback KPI analysis for {kpi_name}: {e}")
            return {
                "name": kpi_name,
                "score": 5.0,
                "normalized_score": 0.5,
                "reasoning": f"Error creating analysis for {kpi_name}",
                "evidence": [],
                "confidence": 0.3,
                "interpretation": "Needs Improvement",
                "recommendations": []
            }
    
    def _validate_category_result(self, category_result: Dict[str, Any], 
                                category_name: str) -> bool:
        """
        Validate that a category result is complete and valid
        
        Args:
            category_result: Category analysis result to validate
            category_name: Name of the category
            
        Returns:
            True if valid, False otherwise
        """
        try:
            # Check required fields
            required_fields = ["name", "kpis", "category_score"]
            for field in required_fields:
                if field not in category_result:
                    self.logger.warning(f"Missing required field '{field}' in category {category_name}")
                    return False
            
            # Check that we have KPIs
            kpis = category_result.get("kpis", {})
            if not kpis:
                self.logger.warning(f"No KPIs found in category {category_name}")
                return False
            
            # Check that each KPI has required fields
            for kpi_name, kpi_data in kpis.items():
                required_kpi_fields = ["score", "reasoning"]
                for field in required_kpi_fields:
                    if field not in kpi_data:
                        self.logger.warning(f"Missing field '{field}' in KPI {kpi_name} for category {category_name}")
                        return False
            
            # Get expected KPI count for this category
            expected_kpis = config_loader.get_category_kpis(category_name)
            expected_count = len(expected_kpis)
            actual_count = len(kpis)
            
            if actual_count < expected_count:
                self.logger.warning(f"Category {category_name} has {actual_count} KPIs, expected {expected_count}")
                # Allow if we have at least 50% of expected KPIs
                return actual_count >= (expected_count * 0.5)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error validating category result for {category_name}: {e}")
            return False
    
    def _calculate_category_score(self, kpis: Dict[str, Any]) -> float:
        """
        Calculate category-level score from KPI scores
        
        Args:
            kpis: Dictionary of KPI analyses
            
        Returns:
            Category-level score
        """
        try:
            if not kpis:
                return 0.0
            
            scores = [kpi.get("score", 5.0) for kpi in kpis.values()]
            return round(sum(scores) / len(scores), 2)
            
        except Exception as e:
            self.logger.error(f"Error calculating category score: {e}")
            return 5.0
    
    def _create_fallback_category_result(self, category_name: str, error_message: str) -> Dict[str, Any]:
        """
        Create fallback category result when analysis fails
        
        Args:
            category_name: Name of the category
            error_message: Error message explaining the failure
            
        Returns:
            Fallback category result
        """
        try:
            # Get expected KPIs for this category
            category_kpis = config_loader.get_category_kpis(category_name)
            
            fallback_kpis = {}
            for kpi_name in category_kpis.keys():
                fallback_kpis[kpi_name] = self._create_fallback_kpi_analysis(kpi_name, category_name)
            
            return {
                "name": category_name,
                "kpis": fallback_kpis,
                "category_score": 5.0,
                "category_performance": "Needs Improvement",
                "analysis_timestamp": datetime.now().isoformat(),
                "analysis_method": "Fallback analysis",
                "error": error_message
            }
            
        except Exception as e:
            self.logger.error(f"Error creating fallback category result for {category_name}: {e}")
            return {
                "name": category_name,
                "kpis": {},
                "category_score": 0.0,
                "category_performance": "Poor",
                "analysis_timestamp": datetime.now().isoformat(),
                "analysis_method": "Fallback analysis (failed)",
                "error": f"{error_message}; Additional error: {str(e)}"
            }
    
    def _collate_category_results(self, category_results: Dict[str, Dict[str, Any]], 
                                conversation_data: ConversationData, 
                                start_time: float) -> Dict[str, Any]:
        """
        Collate results from all category analyses into final comprehensive result
        
        Args:
            category_results: Dictionary of category analysis results
            conversation_data: Original conversation data
            start_time: Analysis start time
            
        Returns:
            Comprehensive analysis results
        """
        try:
            # Create comprehensive performance metrics
            performance_metrics = {
                "categories": category_results,
                "metadata": {
                    "total_categories_analyzed": len(category_results),
                    "total_kpis_evaluated": sum(len(cat.get('kpis', {})) for cat in category_results.values()),
                    "evaluation_timestamp": datetime.now().isoformat(),
                    "model_used": self.model_name,
                    "analysis_duration_seconds": round(time.time() - start_time, 2),
                    "analysis_method": "Orchestrator per-category analysis"
                }
            }
            
            # Calculate overall performance
            overall_performance = self._calculate_overall_performance(category_results)
            
            # Create final comprehensive result
            comprehensive_result = {
                "conversation_id": getattr(conversation_data, 'conversation_id', 'unknown'),
                "analysis_timestamp": datetime.now().isoformat(),
                "analysis_method": "Orchestrator-based per-category Analysis",
                "model_used": self.model_name,
                "performance_metrics": performance_metrics,
                "overall_performance": overall_performance
            }
            
            # Add summary statistics
            successful_categories = sum(1 for cat in category_results.values() if not cat.get('error'))
            failed_categories = len(category_results) - successful_categories
            
            comprehensive_result["analysis_summary"] = {
                "successful_categories": successful_categories,
                "failed_categories": failed_categories,
                "success_rate": round(successful_categories / len(category_results) * 100, 1) if category_results else 0,
                "total_analysis_time": round(time.time() - start_time, 2),
                "categories_analyzed": list(category_results.keys())
            }
            
            self.logger.info(f"Collated results: {successful_categories}/{len(category_results)} categories successful")
            
            return comprehensive_result
            
        except Exception as e:
            self.logger.error(f"Error collating category results: {e}")
            return {
                "conversation_id": getattr(conversation_data, 'conversation_id', 'unknown'),
                "analysis_timestamp": datetime.now().isoformat(),
                "analysis_method": "Orchestrator-based Analysis (Failed)",
                "error": f"Failed to collate results: {str(e)}",
                "performance_metrics": {
                    "categories": category_results,
                    "metadata": {
                        "error": str(e),
                        "total_categories_analyzed": len(category_results),
                        "evaluation_timestamp": datetime.now().isoformat()
                    }
                }
            }
    
    def _calculate_overall_performance(self, category_results: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """
        Calculate overall performance metrics from category results
        
        Args:
            category_results: Dictionary of category analysis results
            
        Returns:
            Overall performance metrics
        """
        try:
            if not category_results:
                return {
                    "overall_score": 0.0,
                    "performance_level": "Poor",
                    "summary": "No category results available"
                }
            
            # Calculate overall score
            category_scores = []
            for category_result in category_results.values():
                if not category_result.get('error'):  # Only include successful categories
                    category_scores.append(category_result.get('category_score', 5.0))
            
            if category_scores:
                overall_score = sum(category_scores) / len(category_scores)
            else:
                overall_score = 0.0
            
            # Generate performance summary
            successful_categories = [name for name, result in category_results.items() if not result.get('error')]
            failed_categories = [name for name, result in category_results.items() if result.get('error')]
            
            summary_parts = []
            if successful_categories:
                summary_parts.append(f"Successfully analyzed {len(successful_categories)} categories")
            if failed_categories:
                summary_parts.append(f"{len(failed_categories)} categories failed analysis")
            
            return {
                "overall_score": round(overall_score, 2),
                "normalized_score": round(overall_score / 10.0, 3),
                "performance_level": self._get_performance_level(overall_score),
                "summary": "; ".join(summary_parts) if summary_parts else "Analysis completed",
                "successful_categories": successful_categories,
                "failed_categories": failed_categories,
                "method": "Orchestrator per-category aggregation"
            }
            
        except Exception as e:
            self.logger.error(f"Error calculating overall performance: {e}")
            return {
                "overall_score": 0.0,
                "performance_level": "Poor",
                "summary": f"Error calculating overall performance: {str(e)}"
            }
    
    def _get_performance_level(self, score: float) -> str:
        """
        Get performance level based on score
        
        Args:
            score: Numeric score (0-10)
            
        Returns:
            Performance level string
        """
        if score >= 8.0:
            return "Excellent"
        elif score >= 6.0:
            return "Good"
        elif score >= 4.0:
            return "Needs Improvement"
        else:
            return "Poor"


# Factory function for creating orchestrator agent
def create_orchestrator_agent(model_name: str = "claude-4", 
                            temperature: float = 0.1,
                            max_retries: int = 3,
                            parallel_categories: bool = False) -> OrchestratorAgent:
    """
    Factory function to create an OrchestratorAgent instance
    
    Args:
        model_name: Name of the LLM model to use
        temperature: Temperature setting for the LLM  
        max_retries: Maximum number of retries for failed category analysis
        parallel_categories: Whether to analyze categories in parallel
        
    Returns:
        OrchestratorAgent instance
    """
    return OrchestratorAgent(
        model_name=model_name,
        temperature=temperature,
        max_retries=max_retries,
        parallel_categories=parallel_categories
    )
