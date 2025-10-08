#!/usr/bin/env python3
"""
Test script to verify that generic fallback reasoning has been eliminated
and replaced with specific, contextual reasoning based on conversation analysis
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import json
import logging
from datetime import datetime
from typing import Dict, Any

# Import required classes
from src.models import ConversationData, Tweet, Classification
from src.llm_agent_service import LLMAgentPerformanceAnalysisService
from src.config_loader import config_loader

def setup_logging():
    """Set up logging for the test"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    return logging.getLogger(__name__)

def create_test_conversation() -> ConversationData:
    """Create a test conversation to verify reasoning quality"""
    tweets = [
        Tweet(
            tweet_id=1,
            author_id="customer_001",
            text="@Support my account is locked and I can't login to check my order status. This is urgent!",
            role="Customer",
            inbound=True,
            created_at="2024-10-05T14:00:00Z"
        ),
        Tweet(
            tweet_id=2,
            author_id="support_agent_001", 
            text="Hi! I understand how urgent this must be for you. Let me help you unlock your account right away so you can check your order.",
            role="Agent",
            inbound=False,
            created_at="2024-10-05T14:01:00Z"
        ),
        Tweet(
            tweet_id=3,
            author_id="customer_001",
            text="Thank you! I really need to track my delivery for tomorrow.",
            role="Customer",
            inbound=True,
            created_at="2024-10-05T14:02:00Z"
        ),
        Tweet(
            tweet_id=4,
            author_id="support_agent_001",
            text="Absolutely! Please follow me and send me a DM with your email address so I can verify your identity and unlock your account securely.",
            role="Agent",
            inbound=False, 
            created_at="2024-10-05T14:03:00Z"
        ),
        Tweet(
            tweet_id=5,
            author_id="customer_001",
            text="Perfect! DMing you now.",
            role="Customer",
            inbound=True,
            created_at="2024-10-05T14:04:00Z"
        ),
        Tweet(
            tweet_id=6,
            author_id="support_agent_001",
            text="Account successfully unlocked! You should now be able to log in and check your order status. Is there anything else I can help with?",
            role="Agent",
            inbound=False,
            created_at="2024-10-05T14:08:00Z"
        ),
        Tweet(
            tweet_id=7,
            author_id="customer_001",
            text="Amazing! It's working perfectly now. Thank you so much for the quick help!",
            role="Customer",
            inbound=True,
            created_at="2024-10-05T14:09:00Z"
        )
    ]
    
    classification = Classification(
        categorization="technical_support",
        intent="account_access",
        topic="account_unlock",
        sentiment="positive"
    )
    
    return ConversationData(
        tweets=tweets,
        classification=classification
    )

def analyze_reasoning_quality(analysis_result: Dict[str, Any], logger) -> Dict[str, Any]:
    """
    Analyze the quality and specificity of reasoning in the analysis result
    
    Args:
        analysis_result: Result from LLM agent analysis
        logger: Logger instance
        
    Returns:
        Quality analysis results
    """
    quality_results = {
        "total_kpis_analyzed": 0,
        "generic_reasoning_count": 0,
        "specific_reasoning_count": 0,
        "generic_reasoning_kpis": [],
        "specific_reasoning_kpis": [],
        "reasoning_quality_score": 0.0,
        "evidence_availability": {},
        "reasoning_analysis": {}
    }
    
    try:
        # Get performance metrics from analysis result
        performance_metrics = analysis_result.get("performance_metrics", {})
        categories = performance_metrics.get("categories", {})
        
        logger.info("Analyzing reasoning quality for each KPI...")
        
        # Analyze each category and KPI
        for category_name, category_data in categories.items():
            kpis = category_data.get("kpis", {})
            
            for kpi_name, kpi_data in kpis.items():
                quality_results["total_kpis_analyzed"] += 1
                
                reasoning = kpi_data.get("reasoning", "")
                evidence = kpi_data.get("evidence", [])
                score = kpi_data.get("score", 0)
                
                # Analyze reasoning quality
                reasoning_quality = analyze_individual_reasoning(
                    kpi_name, reasoning, evidence, score, logger
                )
                
                quality_results["reasoning_analysis"][f"{category_name}/{kpi_name}"] = reasoning_quality
                
                # Check if reasoning is generic
                if reasoning_quality["is_generic"]:
                    quality_results["generic_reasoning_count"] += 1
                    quality_results["generic_reasoning_kpis"].append(f"{category_name}/{kpi_name}")
                else:
                    quality_results["specific_reasoning_count"] += 1
                    quality_results["specific_reasoning_kpis"].append(f"{category_name}/{kpi_name}")
                
                # Track evidence availability
                quality_results["evidence_availability"][f"{category_name}/{kpi_name}"] = {
                    "has_evidence": len(evidence) > 0,
                    "evidence_count": len(evidence),
                    "evidence_quality": reasoning_quality["evidence_quality"]
                }
        
        # Calculate overall reasoning quality score
        if quality_results["total_kpis_analyzed"] > 0:
            quality_results["reasoning_quality_score"] = (
                quality_results["specific_reasoning_count"] / quality_results["total_kpis_analyzed"]
            ) * 100
        
        # Log summary
        logger.info(f"Reasoning Quality Analysis Summary:")
        logger.info(f"  Total KPIs analyzed: {quality_results['total_kpis_analyzed']}")
        logger.info(f"  Specific reasoning: {quality_results['specific_reasoning_count']}")
        logger.info(f"  Generic reasoning: {quality_results['generic_reasoning_count']}")
        logger.info(f"  Quality score: {quality_results['reasoning_quality_score']:.1f}%")
        
        return quality_results
        
    except Exception as e:
        logger.error(f"Error analyzing reasoning quality: {e}")
        quality_results["error"] = str(e)
        return quality_results

def analyze_individual_reasoning(kpi_name: str, reasoning: str, evidence: list, score: float, logger) -> Dict[str, Any]:
    """
    Analyze the quality of reasoning for an individual KPI
    
    Args:
        kpi_name: Name of the KPI
        reasoning: Reasoning text to analyze
        evidence: Evidence array
        score: KPI score
        logger: Logger instance
        
    Returns:
        Dictionary with reasoning quality analysis
    """
    analysis = {
        "kpi_name": kpi_name,
        "reasoning_length": len(reasoning),
        "has_specific_details": False,
        "has_context_references": False,
        "has_score_justification": False,
        "is_generic": False,
        "evidence_quality": "none",
        "quality_indicators": [],
        "generic_indicators": []
    }
    
    try:
        reasoning_lower = reasoning.lower()
        
        # Check for generic reasoning patterns (these are BAD)
        generic_patterns = [
            "analysis of",
            "found no specific evidence within",
            "available conversation interactions",
            "could not identify specific evidence",
            "typical for straightforward",
            "neutral score reflects",
            "absence of both positive and negative indicators",
            "future interactions with more complex scenarios"
        ]
        
        generic_count = 0
        for pattern in generic_patterns:
            if pattern in reasoning_lower:
                generic_count += 1
                analysis["generic_indicators"].append(pattern)
        
        # Check for specific, contextual reasoning (these are GOOD)
        specific_patterns = [
            "customer expressed",
            "agent responded",
            "conversation about",
            "throughout the",
            "interaction",
            "specific to this",
            "based on conversation evidence",
            "demonstrates",
            "shows clear",
            "evident from"
        ]
        
        specific_count = 0
        for pattern in specific_patterns:
            if pattern in reasoning_lower:
                specific_count += 1
                analysis["quality_indicators"].append(pattern)
        
        # Determine if reasoning is generic
        analysis["is_generic"] = generic_count >= 2 or (
            generic_count >= 1 and specific_count == 0
        )
        
        # Check for specific details
        analysis["has_specific_details"] = any([
            "message" in reasoning_lower,
            "tweet" in reasoning_lower,
            "said" in reasoning_lower,
            "responded" in reasoning_lower,
            str(score) in reasoning
        ])
        
        # Check for context references
        analysis["has_context_references"] = any([
            "conversation" in reasoning_lower,
            "interaction" in reasoning_lower,
            "customer" in reasoning_lower,
            "agent" in reasoning_lower
        ])
        
        # Check for score justification
        analysis["has_score_justification"] = any([
            f"score of {score}" in reasoning_lower,
            "reflects" in reasoning_lower,
            "indicates" in reasoning_lower,
            "suggests" in reasoning_lower
        ])
        
        # Analyze evidence quality
        if len(evidence) == 0:
            analysis["evidence_quality"] = "none"
        elif len(evidence) >= 3:
            analysis["evidence_quality"] = "excellent"
        elif len(evidence) >= 2:
            analysis["evidence_quality"] = "good"
        else:
            analysis["evidence_quality"] = "minimal"
        
        # Log individual analysis
        quality_status = "SPECIFIC" if not analysis["is_generic"] else "GENERIC"
        logger.info(f"  {kpi_name}: {quality_status} reasoning ({len(reasoning)} chars, {len(evidence)} evidence)")
        
        if analysis["is_generic"] and analysis["generic_indicators"]:
            logger.warning(f"    Generic patterns found: {', '.join(analysis['generic_indicators'][:3])}")
        
        return analysis
        
    except Exception as e:
        logger.error(f"Error analyzing reasoning for {kpi_name}: {e}")
        analysis["error"] = str(e)
        return analysis

def test_generic_reasoning_elimination():
    """Main test function for generic reasoning elimination verification"""
    logger = setup_logging()
    logger.info("=== GENERIC REASONING ELIMINATION TEST ===")
    
    try:
        # Create test conversation
        logger.info("Creating test conversation with clear KPI evidence...")
        conversation_data = create_test_conversation()
        
        # Initialize LLM agent service
        logger.info("Initializing LLM agent service...")
        llm_service = LLMAgentPerformanceAnalysisService(model_name="claude-4", temperature=0.1)
        
        # Perform analysis
        logger.info("Performing conversation analysis...")
        analysis_start_time = datetime.now()
        
        analysis_result = llm_service.analyze_conversation_performance(conversation_data)
        
        analysis_duration = (datetime.now() - analysis_start_time).total_seconds()
        logger.info(f"Analysis completed in {analysis_duration:.2f} seconds")
        
        # Analyze reasoning quality
        logger.info("Analyzing reasoning quality...")
        quality_analysis = analyze_reasoning_quality(analysis_result, logger)
        
        # Create comprehensive test results
        test_results = {
            "test_timestamp": datetime.now().isoformat(),
            "test_type": "Generic Reasoning Elimination Verification",
            "conversation_id": "generic_reasoning_test_001",
            "analysis_duration_seconds": analysis_duration,
            "quality_analysis": quality_analysis,
            "analysis_result": analysis_result,
            "test_summary": {
                "total_kpis": quality_analysis["total_kpis_analyzed"],
                "generic_reasoning_count": quality_analysis["generic_reasoning_count"],
                "specific_reasoning_count": quality_analysis["specific_reasoning_count"],
                "reasoning_quality_score": quality_analysis["reasoning_quality_score"],
                "test_passed": quality_analysis["reasoning_quality_score"] >= 80.0
            }
        }
        
        # Save results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"generic_reasoning_elimination_test_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump(test_results, f, indent=2)
        
        # Print detailed results
        logger.info("=== TEST RESULTS ===")
        logger.info(f"Total KPIs analyzed: {quality_analysis['total_kpis_analyzed']}")
        logger.info(f"Specific reasoning: {quality_analysis['specific_reasoning_count']}")
        logger.info(f"Generic reasoning: {quality_analysis['generic_reasoning_count']}")
        logger.info(f"Quality score: {quality_analysis['reasoning_quality_score']:.1f}%")
        
        if quality_analysis["generic_reasoning_kpis"]:
            logger.warning("KPIs with generic reasoning:")
            for kpi in quality_analysis["generic_reasoning_kpis"]:
                logger.warning(f"  - {kpi}")
        
        if quality_analysis["specific_reasoning_kpis"]:
            logger.info("✓ KPIs with specific reasoning:")
            for kpi in quality_analysis["specific_reasoning_kpis"][:5]:  # Show first 5
                logger.info(f"  - {kpi}")
            if len(quality_analysis["specific_reasoning_kpis"]) > 5:
                logger.info(f"  ... and {len(quality_analysis['specific_reasoning_kpis']) - 5} more")
        
        logger.info(f"Results saved to: {filename}")
        
        # Final assessment
        if quality_analysis["reasoning_quality_score"] >= 80.0:
            logger.info("🎉 GENERIC REASONING ELIMINATION TEST PASSED!")
            logger.info("The system now generates specific, contextual reasoning instead of generic templates.")
        else:
            logger.warning("⚠️ GENERIC REASONING ELIMINATION TEST NEEDS IMPROVEMENT")
            logger.warning(f"Quality score {quality_analysis['reasoning_quality_score']:.1f}% is below the 80% threshold.")
        
        return test_results
        
    except Exception as e:
        logger.error(f"Error in generic reasoning elimination test: {e}")
        return {
            "test_timestamp": datetime.now().isoformat(),
            "test_type": "Generic Reasoning Elimination Verification",
            "error": str(e),
            "status": "FAILED"
        }

if __name__ == "__main__":
    test_results = test_generic_reasoning_elimination()
    
    # Print final status
    quality_score = test_results.get("test_summary", {}).get("reasoning_quality_score", 0)
    if quality_score >= 80.0:
        print(f"\n✅ GENERIC REASONING ELIMINATION: PASSED ({quality_score:.1f}%)")
    else:
        print(f"\n❌ GENERIC REASONING ELIMINATION: FAILED ({quality_score:.1f}%)")
