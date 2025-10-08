#!/usr/bin/env python3
"""
Reporting Service for Customer Conversation Performance Analysis
Provides reporting functionality with LLM-generated summaries
"""

import json
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional
from pathlib import Path
import sys

# MongoDB imports with fallback for testing
try:
    from bson import ObjectId
    import pymongo
    from pymongo import MongoClient
    MONGODB_AVAILABLE = True
except ImportError as e:
    # Create mock classes for testing without MongoDB
    class ObjectId:
        def __init__(self, oid=None):
            self._id = oid or "507f1f77bcf86cd799439011"
        def __str__(self):
            return str(self._id)
    
    class MongoClient:
        def __init__(self, *args, **kwargs):
            pass
    
    MONGODB_AVAILABLE = False
    logging.warning(f"MongoDB not available: {e}. Running in test mode.")

# Add src directory to Python path
src_dir = Path(__file__).parent
sys.path.insert(0, str(src_dir))

try:
    from .llm_agent_service import get_llm_agent_service
except ImportError:
    # Fallback for direct execution
    import llm_agent_service
    get_llm_agent_service = llm_agent_service.get_llm_agent_service

class ReportingService:
    """Service for generating performance reports with LLM summaries"""
    
    def __init__(self, mongo_connection_string: str, db_name: str = "csai"):
        """
        Initialize the reporting service
        
        Args:
            mongo_connection_string: MongoDB connection string
            db_name: Database name (default: csai)
        """
        self.mongo_connection_string = mongo_connection_string
        self.db_name = db_name
        self.client = None
        self.db = None
        self.agentic_collection = None
        
        # Data source configuration
        self.data_source_config = {
            "type": "mongodb",  # mongodb or file
            "collection_name": "agentic_analysis",
            "file_path": None
        }
        
        # Initialize logging
        self.logger = logging.getLogger(__name__)
        
        # Initialize LLM service
        try:
            self.llm_service = get_llm_agent_service()
            self.logger.info(f"LLM service initialized for reporting with model: {self.llm_service.model_name}")
        except Exception as e:
            self.logger.error(f"Failed to initialize LLM service for reporting: {e}")
            self.llm_service = None

    def connect_to_mongodb(self) -> bool:
        """
        Connect to MongoDB and initialize collections
        
        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            self.client = MongoClient(self.mongo_connection_string)
            self.db = self.client[self.db_name]
            
            # Initialize collections
            self.agentic_collection = self.db['agentic_analysis']
            
            # Test connection
            self.client.admin.command('ping')
            self.logger.info(f"Successfully connected to MongoDB database: {self.db_name}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to connect to MongoDB: {e}")
            return False

    def configure_data_source(self, source_type: str = "mongodb", collection_name: str = "agentic_analysis", file_path: Optional[str] = None) -> bool:
        """
        Configure the data source for fetching sentiment analysis data
        
        Args:
            source_type: Type of data source ("mongodb" or "file")
            collection_name: MongoDB collection name (for mongodb source)
            file_path: File path or folder path (for file source)
            
        Returns:
            bool: True if configuration successful, False otherwise
        """
        try:
            self.data_source_config = {
                "type": source_type,
                "collection_name": collection_name,
                "file_path": file_path
            }
            
            self.logger.info(f"Data source configured: {self.data_source_config}")
            
            # If switching to file source, close MongoDB connection
            if source_type == "file" and self.client:
                self.client.close()
                self.client = None
                self.db = None
                self.agentic_collection = None
            
            # If switching to mongodb source, ensure connection
            elif source_type == "mongodb" and not self.client:
                self.connect_to_mongodb()
                
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to configure data source: {e}")
            return False

    def fetch_records_by_date_range(self, start_date: str, end_date: str, customer: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Fetch records by date range and customer from configured data source
        
        Args:
            start_date: Start date in ISO format (YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS)
            end_date: End date in ISO format (YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS)
            customer: Optional customer filter
            
        Returns:
            List of analysis records
        """
        try:
            if self.data_source_config["type"] == "file":
                return self._fetch_records_from_file(start_date, end_date, customer)
            else:
                return self._fetch_records_from_mongodb(start_date, end_date, customer)
                
        except Exception as e:
            self.logger.error(f"Failed to fetch records by date range: {e}")
            return []

    def _convert_objectid_to_string(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert MongoDB ObjectId fields to strings for JSON serialization
        
        Args:
            record: MongoDB record that may contain ObjectId fields
            
        Returns:
            Record with ObjectId fields converted to strings
        """
        if isinstance(record, dict):
            converted_record = {}
            for key, value in record.items():
                if isinstance(value, ObjectId):
                    converted_record[key] = str(value)
                elif isinstance(value, dict):
                    converted_record[key] = self._convert_objectid_to_string(value)
                elif isinstance(value, list):
                    converted_record[key] = [
                        self._convert_objectid_to_string(item) if isinstance(item, dict) 
                        else str(item) if isinstance(item, ObjectId) 
                        else item 
                        for item in value
                    ]
                else:
                    converted_record[key] = value
            return converted_record
        else:
            return record

    def _fetch_records_from_mongodb(self, start_date: str, end_date: str, customer: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Fetch records from MongoDB collection by date range and customer
        
        Args:
            start_date: Start date in ISO format
            end_date: End date in ISO format
            customer: Optional customer filter
            
        Returns:
            List of analysis records
        """
        try:
            # Parse dates to datetime objects for proper comparison
            from datetime import datetime
            
            # Handle start date
            if 'T' not in start_date:
                start_date += 'T00:00:00'
            if start_date.endswith('Z'):
                start_date = start_date[:-1]
            
            # Handle end date  
            if 'T' not in end_date:
                end_date += 'T23:59:59.999999'  # Add microseconds to ensure we catch records with microseconds
            else:
                # If time is specified but no microseconds, add them
                if '.' not in end_date:
                    end_date += '.999999'
            if end_date.endswith('Z'):
                end_date = end_date[:-1]
            
            # Convert to datetime objects for comparison
            try:
                start_dt = datetime.fromisoformat(start_date)
                end_dt = datetime.fromisoformat(end_date)
            except ValueError as e:
                self.logger.error(f"Invalid date format: {e}")
                return []
            
            # Use configured collection name
            collection = self.db[self.data_source_config["collection_name"]]
            
            # Fetch all records first, then filter in Python since string comparison fails with microseconds
            self.logger.info(f"Fetching all records from MongoDB for date filtering")
            
            # Get all records - explicitly set no limit and ensure we get all documents
            query = {}
            if customer and customer.strip() and customer.strip() != "all":
                query["customer"] = customer.strip()
            
            # Use find() with explicit parameters to ensure we get all records
            cursor = collection.find(query, batch_size=0, limit=0)
            all_records = list(cursor)
            
            self.logger.info(f"MongoDB query executed: {query}")
            self.logger.info(f"Retrieved {len(all_records)} total records from MongoDB before date filtering")
            
            # Filter records by date range in Python and convert ObjectIds
            filtered_records = []
            for record in all_records:
                record_date_str = record.get("created_at")
                if record_date_str:
                    try:
                        # Parse the record's created_at timestamp
                        record_dt = datetime.fromisoformat(record_date_str)
                        
                        # Check if record falls within date range
                        if start_dt <= record_dt <= end_dt:
                            # Convert ObjectId fields to strings for JSON serialization
                            converted_record = self._convert_objectid_to_string(record)
                            filtered_records.append(converted_record)
                            
                    except ValueError:
                        self.logger.warning(f"Invalid date format in record: {record_date_str}")
                        continue
            
            # Sort by created_at
            filtered_records.sort(key=lambda x: x.get("created_at", ""))
            
            self.logger.info(f"Found {len(filtered_records)} records matching criteria from MongoDB (filtered from {len(all_records)} total)")
            self.logger.info(f"Date range: {start_date} to {end_date}")
            
            return filtered_records
            
        except Exception as e:
            self.logger.error(f"Failed to fetch records from MongoDB: {e}")
            import traceback
            traceback.print_exc()
            return []

    def _fetch_records_from_file(self, start_date: str, end_date: str, customer: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Fetch records from file(s) by date range and customer
        
        Args:
            start_date: Start date in ISO format
            end_date: End date in ISO format
            customer: Optional customer filter
            
        Returns:
            List of analysis records
        """
        try:
            file_path = self.data_source_config["file_path"]
            if not file_path:
                self.logger.error("No file path configured for file data source")
                return []
            
            path_obj = Path(file_path)
            records = []
            
            # Parse dates for comparison
            start_dt = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
            end_dt = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
            
            if path_obj.is_file():
                # Single file
                records.extend(self._load_records_from_single_file(path_obj))
            elif path_obj.is_dir():
                # Directory - load all JSON files
                for json_file in path_obj.glob('*.json'):
                    records.extend(self._load_records_from_single_file(json_file))
            else:
                self.logger.error(f"Invalid file path: {file_path}")
                return []
            
            # Filter records by date range and customer
            filtered_records = []
            for record in records:
                # Check date range
                record_date_str = record.get("created_at")
                if record_date_str:
                    try:
                        if 'T' not in record_date_str:
                            record_date_str += 'T00:00:00'
                        if 'Z' not in record_date_str:
                            record_date_str += 'Z'
                        
                        record_dt = datetime.fromisoformat(record_date_str.replace('Z', '+00:00'))
                        
                        if not (start_dt <= record_dt <= end_dt):
                            continue
                    except ValueError:
                        self.logger.warning(f"Invalid date format in record: {record_date_str}")
                        continue
                
                # Check customer filter
                if customer and customer.strip() and customer.strip() != "all":
                    record_customer = record.get("customer", "")
                    if record_customer != customer.strip():
                        continue
                
                filtered_records.append(record)
            
            self.logger.info(f"Found {len(filtered_records)} records matching criteria from files")
            return filtered_records
            
        except Exception as e:
            self.logger.error(f"Failed to fetch records from file: {e}")
            return []

    def _load_records_from_single_file(self, file_path: Path) -> List[Dict[str, Any]]:
        """
        Load records from a single JSON file
        
        Args:
            file_path: Path to JSON file
            
        Returns:
            List of records from the file
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Handle different JSON structures
            if isinstance(data, list):
                return data
            elif isinstance(data, dict):
                # If it's a single record, wrap in list
                return [data]
            else:
                self.logger.warning(f"Unexpected JSON structure in file: {file_path}")
                return []
                
        except Exception as e:
            self.logger.error(f"Failed to load records from file {file_path}: {e}")
            return []

    def get_data_source_config(self) -> Dict[str, Any]:
        """
        Get current data source configuration
        
        Returns:
            Current data source configuration
        """
        return self.data_source_config.copy()

    def prepare_data_for_analysis(self, records: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Prepare and aggregate data for LLM analysis with sentiment-intent-topic combinations
        
        Args:
            records: List of analysis records
            
        Returns:
            Aggregated data for analysis including performance metrics per combination
        """
        if not records:
            return {
                "total_conversations": 0,
                "summary_stats": {},
                "performance_breakdown": {},
                "sentiment_analysis": {},
                "intent_analysis": {},
                "topic_analysis": {},
                "combination_analysis": {}
            }
        
        try:
            # Initialize aggregation structures
            total_conversations = len(records)
            performance_metrics = {
                "accuracy_compliance": [],
                "empathy_communication": [],
                "efficiency_resolution": []
            }
            
            sentiments = {}
            intents = {}
            topics = {}
            customers = set()
            date_range = {"earliest": None, "latest": None}
            
            # Track combinations: sentiment-intent-topic
            combination_metrics = {}
            
            # Process each record
            for record in records:
                # Collect customer info
                if record.get("customer"):
                    customers.add(record["customer"])
                
                # Track date range
                created_at = record.get("created_at")
                if created_at:
                    if not date_range["earliest"] or created_at < date_range["earliest"]:
                        date_range["earliest"] = created_at
                    if not date_range["latest"] or created_at > date_range["latest"]:
                        date_range["latest"] = created_at
                
                # Extract conversation summary info
                conv_summary = record.get("conversation_summary", {})
                sentiment = conv_summary.get("final_sentiment", "Unknown")
                intent = conv_summary.get("intent", "Unknown")
                topic = conv_summary.get("topic", "Unknown")
                
                # Create combination key
                combination_key = f"{sentiment}|{intent}|{topic}"
                
                # Initialize combination if not exists
                if combination_key not in combination_metrics:
                    combination_metrics[combination_key] = {
                        "sentiment": sentiment,
                        "intent": intent,
                        "topic": topic,
                        "count": 0,
                        "performance_metrics": {
                            "accuracy_compliance": [],
                            "empathy_communication": [],
                            "efficiency_resolution": []
                        }
                    }
                
                combination_metrics[combination_key]["count"] += 1
                
                # Extract performance metrics for overall and combination analysis
                perf_metrics = record.get("performance_metrics", {})
                # The categories are nested under 'categories' key in performance_metrics
                categories_data = perf_metrics.get("categories", {})
                for category in performance_metrics:
                    if category in categories_data:
                        performance_metrics[category].append(categories_data[category])
                        combination_metrics[combination_key]["performance_metrics"][category].append(categories_data[category])
                
                # Aggregate sentiment, intent, topic counts
                sentiments[sentiment] = sentiments.get(sentiment, 0) + 1
                intents[intent] = intents.get(intent, 0) + 1
                topics[topic] = topics.get(topic, 0) + 1
            
            # Calculate overall performance averages
            performance_averages = self._calculate_performance_averages(performance_metrics)
            
            # Calculate performance averages per combination
            combination_analysis = {}
            for combo_key, combo_data in combination_metrics.items():
                combo_perf_avg = self._calculate_performance_averages(combo_data["performance_metrics"])
                combination_analysis[combo_key] = {
                    "sentiment": combo_data["sentiment"],
                    "intent": combo_data["intent"],
                    "topic": combo_data["topic"],
                    "conversation_count": combo_data["count"],
                    "performance_averages": combo_perf_avg,
                    "percentage_of_total": round((combo_data["count"] / total_conversations) * 100, 1)
                }
            
            # Sort combinations by conversation count (most frequent first)
            sorted_combinations = dict(sorted(combination_analysis.items(), 
                                            key=lambda x: x[1]["conversation_count"], 
                                            reverse=True))
            
            return {
                "total_conversations": total_conversations,
                "unique_customers": len(customers),
                "date_range": date_range,
                "performance_averages": performance_averages,
                "intent_distribution": intents,
                "topic_distribution": topics,
                "combination_analysis": sorted_combinations,
                "raw_records_sample": records[:3] if len(records) > 3 else records  # Include sample for context
            }
            
        except Exception as e:
            self.logger.error(f"Failed to prepare data for analysis: {e}")
            return {
                "total_conversations": len(records),
                "error": str(e)
            }

    def _calculate_performance_averages(self, performance_metrics: Dict[str, List[Dict]]) -> Dict[str, Dict]:
        """
        Calculate performance averages from a collection of metrics using normalized_score and interpretations
        
        Args:
            performance_metrics: Dictionary of metric categories with lists of category data records
            
        Returns:
            Dictionary of averaged performance metrics with normalized scores and interpretations
        """
        performance_averages = {}
        
        for category, metrics_list in performance_metrics.items():
            if not metrics_list:
                continue
                
            category_avg = {}
            category_interpretations = {}
            
            # Process each category record in the metrics list
            # Now the records are the category data directly, not wrapped in 'categories'
            for category_data in metrics_list:
                if not isinstance(category_data, dict):
                    continue
                    
                # Get overall category score (convert to normalized if needed)
                if 'overall_score' in category_data:
                    if 'overall_score' not in category_avg:
                        category_avg['overall_score'] = []
                    # Convert overall score to normalized (assuming scale 0-10 to 0-1)
                    normalized_overall = category_data['overall_score'] / 10.0
                    category_avg['overall_score'].append(normalized_overall)
                
                # Process individual KPIs within the category
                kpis = category_data.get('kpis', {})
                for kpi_name, kpi_data in kpis.items():
                    if isinstance(kpi_data, dict):
                        # Use normalized_score if available, otherwise convert score to normalized
                        if 'normalized_score' in kpi_data:
                            if kpi_name not in category_avg:
                                category_avg[kpi_name] = []
                            category_avg[kpi_name].append(kpi_data['normalized_score'])
                        elif 'score' in kpi_data:
                            if kpi_name not in category_avg:
                                category_avg[kpi_name] = []
                            # Convert score to normalized (assuming scale 0-10 to 0-1)
                            normalized_score = kpi_data['score'] / 10.0
                            category_avg[kpi_name].append(normalized_score)
                        
                        # Collect interpretation if available
                        if 'interpretation' in kpi_data:
                            if kpi_name not in category_interpretations:
                                category_interpretations[kpi_name] = []
                            category_interpretations[kpi_name].append(kpi_data['interpretation'])
                        
                        # Also process sub_kpis if they exist (these typically only have score)
                        if 'sub_kpis' in kpi_data:
                            for sub_kpi_name, sub_kpi_data in kpi_data['sub_kpis'].items():
                                if isinstance(sub_kpi_data, dict) and 'score' in sub_kpi_data:
                                    sub_key = f"{kpi_name}_{sub_kpi_name}"
                                    if sub_key not in category_avg:
                                        category_avg[sub_key] = []
                                    # Convert sub-KPI score to normalized
                                    normalized_sub_score = sub_kpi_data['score'] / 10.0
                                    category_avg[sub_key].append(normalized_sub_score)
            
            # Calculate averages from collected values and determine overall interpretations
            final_averages = {}
            for metric_key, values in category_avg.items():
                if values and isinstance(values, list):
                    avg_normalized = round(sum(values) / len(values), 3)  # 3 decimals for normalized scores
                    final_averages[metric_key] = {
                        "normalized_score": avg_normalized,
                        "score": round(avg_normalized * 10, 2)  # Convert back to 0-10 scale for reference
                    }
                    
                    # Add interpretation if available
                    if metric_key in category_interpretations:
                        interpretations = category_interpretations[metric_key]
                        # Use the most common interpretation or the first one if all are different
                        final_averages[metric_key]["interpretation"] = self._get_most_common_interpretation(interpretations)
                    else:
                        # Generate interpretation based on normalized score
                        final_averages[metric_key]["interpretation"] = self._generate_interpretation_from_score(avg_normalized)
            
            if final_averages:
                performance_averages[category] = final_averages
        
        return performance_averages

    def _get_most_common_interpretation(self, interpretations: List[str]) -> str:
        """
        Get the most common interpretation from a list of interpretations
        
        Args:
            interpretations: List of interpretation strings
            
        Returns:
            Most common interpretation or the first one if all are different
        """
        if not interpretations:
            return "performance needs evaluation"
        
        # Count occurrences
        from collections import Counter
        interpretation_counts = Counter(interpretations)
        
        # Return the most common interpretation
        most_common = interpretation_counts.most_common(1)[0]
        return most_common[0]

    def _generate_interpretation_from_score(self, normalized_score: float) -> str:
        """
        Generate an interpretation based on normalized score
        
        Args:
            normalized_score: Score between 0 and 1
            
        Returns:
            Performance interpretation string
        """
        if normalized_score >= 0.9:
            return "excellent - exceeds expectations significantly"
        elif normalized_score >= 0.8:
            return "very good - consistently above average performance"
        elif normalized_score >= 0.7:
            return "good - meets expectations with solid performance"
        elif normalized_score >= 0.6:
            return "satisfactory - adequate performance with room for improvement"
        elif normalized_score >= 0.5:
            return "needs improvement - below average performance"
        elif normalized_score >= 0.4:
            return "poor - significant improvement required"
        else:
            return "critical - immediate attention and intervention needed"

    def generate_llm_summary(self, aggregated_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate LLM summary based on aggregated performance data
        
        Args:
            aggregated_data: Aggregated performance data
            
        Returns:
            LLM-generated summary with insights
        """
        try:
            if not self.llm_service:
                return self.generate_fallback_summary(aggregated_data)
            
            # Prepare prompt for LLM
            prompt = self._build_analysis_prompt(aggregated_data)
            
            # Get LLM response using the correct method
            messages = [
                {
                    "role": "system",
                    "content": "You are an expert customer service performance analyst. Analyze the provided conversation performance data and provide insights in the requested format."
                },
                {
                    "role": "user", 
                    "content": prompt
                }
            ]
            
            # Use the LLM service's analyze method or appropriate method
            if hasattr(self.llm_service, 'analyze'):
                response = self.llm_service.analyze(prompt)
                summary_text = response
            elif hasattr(self.llm_service, 'client'):
                response = self.llm_service.client.predict(messages=messages)
                summary_text = response.content[0].text if hasattr(response, 'content') else str(response)
            else:
                # Fallback if we can't determine the correct method
                self.logger.warning("LLM service method not found, using fallback")
                return self.generate_fallback_summary(aggregated_data)
            
            # Try to extract structured data from response
            summary = self._parse_llm_response(summary_text)
            
            return {
                "summary": summary,
                "analysis_metadata": {
                    "generated_at": datetime.now().isoformat(),
                    "model_used": self.llm_service.model_name,
                    "data_points_analyzed": aggregated_data.get("total_conversations", 0)
                }
            }
            
        except Exception as e:
            self.logger.error(f"Failed to generate LLM summary: {e}")
            return self.generate_fallback_summary(aggregated_data)

    def _build_analysis_prompt(self, data: Dict[str, Any]) -> str:
        """Build the analysis prompt for the LLM"""
        
        # Format combination analysis for better readability
        combination_analysis = data.get('combination_analysis', {})
        top_combinations = list(combination_analysis.items())[:5]  # Top 5 combinations
        
        combination_summary = ""
        for combo_key, combo_data in top_combinations:
            combination_summary += f"""
**{combo_data['sentiment']} | {combo_data['intent']} | {combo_data['topic']}:**
  - Conversations: {combo_data['conversation_count']} ({combo_data['percentage_of_total']}%)
  - Performance Averages: {json.dumps(combo_data['performance_averages'], indent=4)}
"""
        
        prompt = f"""
Please analyze the following customer service performance data and provide insights for these three key questions:

**Data Overview:**
- Total Conversations: {data.get('total_conversations', 0)}
- Unique Customers: {data.get('unique_customers', 0)}
- Date Range: {data.get('date_range', {}).get('earliest', 'Unknown')} to {data.get('date_range', {}).get('latest', 'Unknown')}

**Overall Performance Metrics Summary:**
{json.dumps(data.get('performance_averages', {}), indent=2)}

**Sentiment Distribution:**
{json.dumps(data.get('sentiment_distribution', {}), indent=2)}

**Intent Distribution:**
{json.dumps(data.get('intent_distribution', {}), indent=2)}

**Topic Distribution:**
{json.dumps(data.get('topic_distribution', {}), indent=2)}

**Performance by Sentiment-Intent-Topic Combinations (Top 5):**
{combination_summary}

**Please provide analysis in this exact format:**

**WHAT WENT WELL:**
1. [Point 1 - focus on strengths in performance metrics, positive sentiment trends, successful intent resolution, and high-performing combinations]
2. [Point 2]
3. [Point 3]

**WHAT NEEDS TO BE IMPROVED:**
1. [Point 1 - focus on weak performance areas, negative sentiment patterns, resolution gaps, and underperforming combinations]
2. [Point 2]
3. [Point 3]

**TRAINING NEEDS:**
1. [Point 1 - specific training recommendations based on performance gaps, topic/intent analysis, and combination-specific insights]
2. [Point 2]

Limit to maximum 8 points total across all three sections. Focus on actionable insights based on:
- Overall performance metrics vs combination-specific performance
- Sentiment-intent-topic patterns that show strong or weak performance
- Specific combinations that need attention or are performing exceptionally well
- Training recommendations that target specific conversation types (combinations)
"""
        return prompt

    def _parse_llm_response(self, response_text: str) -> Dict[str, List[str]]:
        """Parse the LLM response into structured format"""
        try:
            sections = {
                "what_went_well": [],
                "what_needs_improvement": [],
                "training_needs": []
            }
            
            current_section = None
            lines = response_text.split('\n')
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                # Identify sections
                if "WHAT WENT WELL" in line.upper():
                    current_section = "what_went_well"
                elif "WHAT NEEDS TO BE IMPROVED" in line.upper() or "NEEDS IMPROVEMENT" in line.upper():
                    current_section = "what_needs_improvement"
                elif "TRAINING NEEDS" in line.upper():
                    current_section = "training_needs"
                elif line.startswith(('1.', '2.', '3.', '4.', '5.', '6.', '7.', '8.', '-', '•')) and current_section:
                    # Extract the point text
                    point_text = line.split('.', 1)[-1].strip() if '.' in line else line[1:].strip()
                    if point_text:
                        sections[current_section].append(point_text)
            
            return sections
            
        except Exception as e:
            self.logger.error(f"Failed to parse LLM response: {e}")
            return {
                "what_went_well": ["Analysis parsing failed"],
                "what_needs_improvement": ["Unable to generate detailed insights"],
                "training_needs": ["General performance review recommended"]
            }

    def generate_fallback_summary(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a fallback summary when LLM is not available"""
        
        total_conversations = data.get("total_conversations", 0)
        performance_avg = data.get("performance_averages", {})
        sentiment_dist = data.get("sentiment_distribution", {})
        
        # Generate basic insights
        what_went_well = []
        what_needs_improvement = []
        training_needs = []
        
        # Analyze sentiment
        positive_sentiments = sentiment_dist.get("Positive", 0) + sentiment_dist.get("Very Positive", 0)
        negative_sentiments = sentiment_dist.get("Negative", 0) + sentiment_dist.get("Very Negative", 0)
        
        if total_conversations > 0:
            positive_rate = (positive_sentiments / total_conversations) * 100
            negative_rate = (negative_sentiments / total_conversations) * 100
            
            # Basic insights based on data
            if positive_rate > 70:
                what_went_well.append(f"High positive sentiment rate ({positive_rate:.1f}%)")
            if negative_rate < 10:
                what_went_well.append("Low negative sentiment incidents")
            
            # Performance insights - handle new dict structure with normalized_score
            empathy_metrics = performance_avg.get("empathy_communication", {})
            empathy_score_data = empathy_metrics.get("empathy_score", {})
            empathy_score = empathy_score_data.get("score", 0) if isinstance(empathy_score_data, dict) else empathy_score_data
            
            if empathy_score > 7:
                what_went_well.append("Strong empathy scores in customer interactions")
            
            # Areas for improvement
            if negative_rate > 20:
                what_needs_improvement.append(f"High negative sentiment rate ({negative_rate:.1f}%)")
            if empathy_score < 6:
                what_needs_improvement.append("Empathy scores below target")
            
            # Training recommendations
            if empathy_score < 7:
                training_needs.append("Empathy and emotional intelligence training")
            if negative_rate > 15:
                training_needs.append("Conflict resolution and de-escalation training")
        
        return {
            "summary": {
                "what_went_well": what_went_well or ["Baseline performance maintained"],
                "what_needs_improvement": what_needs_improvement or ["Continue monitoring trends"],
                "training_needs": training_needs or ["Regular performance reviews recommended"]
            },
            "analysis_metadata": {
                "generated_at": datetime.now().isoformat(),
                "model_used": "fallback-analysis",
                "data_points_analyzed": total_conversations
            }
        }

    def generate_performance_report(self, start_date: str, end_date: str, customer: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate a comprehensive performance report
        
        Args:
            start_date: Start date for the report
            end_date: End date for the report
            customer: Optional customer filter
            
        Returns:
            Complete performance report with records and summary
        """
        try:
            # Fetch records
            records = self.fetch_records_by_date_range(start_date, end_date, customer)
            
            if not records:
                return {
                    "status": "success",
                    "message": "No records found for the specified criteria",
                    "query_parameters": {
                        "start_date": start_date,
                        "end_date": end_date,
                        "customer": customer
                    },
                    "selected_records": [],
                    "summary": {
                        "what_went_well": ["No data available for analysis"],
                        "what_needs_improvement": ["Ensure data is being collected properly"],
                        "training_needs": ["Data collection process review needed"]
                    },
                    "report_metadata": {
                        "generated_at": datetime.now().isoformat(),
                        "total_records": 0
                    }
                }
            
            # Prepare data for analysis
            aggregated_data = self.prepare_data_for_analysis(records)
            
            # Generate LLM summary
            summary_result = self.generate_llm_summary(aggregated_data)
            
            # Prepare final report
            report = {
                "status": "success",
                "query_parameters": {
                    "start_date": start_date,
                    "end_date": end_date,
                    "customer": customer,
                    "records_found": len(records)
                },
                "selected_records": records,
                "summary": summary_result.get("summary", {}),
                "aggregated_insights": {
                    "total_conversations": aggregated_data.get("total_conversations", 0),
                    "unique_customers": aggregated_data.get("unique_customers", 0),
                    "date_range": aggregated_data.get("date_range", {}),
                    "performance_averages": aggregated_data.get("performance_averages", {}),
                    "intent_distribution": aggregated_data.get("intent_distribution", {}),
                    "topic_distribution": aggregated_data.get("topic_distribution", {}),
                    "combination_analysis": aggregated_data.get("combination_analysis", {})
                },
                "report_metadata": {
                    "generated_at": datetime.now().isoformat(),
                    "analysis_method": summary_result.get("analysis_metadata", {}).get("model_used", "unknown"),
                    "total_records": len(records)
                }
            }
            
            return report
            
        except Exception as e:
            self.logger.error(f"Failed to generate performance report: {e}")
            import traceback
            traceback.print_exc()
            
            # Try to provide partial results if possible
            try:
                records = self.fetch_records_by_date_range(start_date, end_date, customer)
                record_count = len(records) if records else 0
            except:
                records = []
                record_count = 0
            
            return {
                "status": "error",
                "message": f"Report generation failed: {str(e)}",
                "query_parameters": {
                    "start_date": start_date,
                    "end_date": end_date,
                    "customer": customer
                },
                "selected_records": records[:5] if records else [],  # Include first 5 records if available
                "partial_data": {
                    "records_found": record_count,
                    "data_retrieval_successful": record_count > 0
                },
                "summary": {
                    "what_went_well": ["Data retrieval working" if record_count > 0 else "System partially functional"],
                    "what_needs_improvement": [f"Report processing error: {str(e)[:100]}"],
                    "training_needs": ["System maintenance required"]
                },
                "report_metadata": {
                    "generated_at": datetime.now().isoformat(),
                    "error": str(e),
                    "error_type": type(e).__name__
                }
            }

    def cleanup(self):
        """Cleanup resources"""
        try:
            if self.client:
                self.client.close()
                self.logger.info("MongoDB connection closed")
        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")


def main():
    """Main function for testing the reporting service"""
    
    # MongoDB connection string (should be provided via environment variable in production)
    import os
    mongo_connection_string = os.getenv('MONGODB_CONNECTION_STRING', 'mongodb://localhost:27017/')
    
    # Initialize service
    service = ReportingService(mongo_connection_string)
    
    try:
        # Connect to MongoDB
        if not service.connect_to_mongodb():
            print("Failed to connect to MongoDB")
            return
        
        # Test report generation
        print("Testing report generation...")
        report = service.generate_performance_report(
            start_date="2023-01-01",
            end_date="2023-12-31",
            customer="customer_123"
        )
        
        print(f"Report generated: {json.dumps(report, indent=2, default=str)}")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        service.cleanup()


if __name__ == "__main__":
    main()
