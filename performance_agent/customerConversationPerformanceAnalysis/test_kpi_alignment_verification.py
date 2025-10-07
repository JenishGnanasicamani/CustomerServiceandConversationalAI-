#!/usr/bin/env python3
"""
Test script to verify KPI alignment between LLM analysis and configuration
This test ensures the LLM analyzes only configured KPIs and validates against the configuration
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
    """Create a test conversation with clear KPI evidence"""
    tweets = [
        Tweet(
            tweet_id=1,
            author_id="customer_001",
            text="Hi @AirlineSupport, I'm locked out of my account and can't access my booking. Very frustrated!",
            role="Customer",
            inbound=True,
            created_at="2024-10-05T10:00:00Z"
        ),
        Tweet(
            tweet_id=2,
            author_id="support_agent_001", 
            text="Hi there! I completely understand how frustrating that must be. I'm delighted to help you unlock your account right away.",
            role="Agent",
            inbound=False,
            created_at="2024-10-05T10:01:00Z"
        ),
        Tweet(
            tweet_id=3,
            author_id="customer_001",
            text="Thank you! I need to access my booking for tomorrow's flight.",
            role="Customer",
            inbound=True,
            created_at="2024-10-05T10:02:00Z"
        ),
        Tweet(
            tweet_id=4,
            author_id="support_agent_001",
            text="I can definitely help with that! Let me assist you with unlocking your account. Please follow me and DM me your confirmation number for identity verification.",
            role="Agent",
            inbound=False, 
            created_at="2024-10-05T10:03:00Z"
        ),
        Tweet(
            tweet_id=5,
            author_id="customer_001",
            text="Perfect! DMing you now. Thank you for the quick help!",
            role="Customer",
            inbound=True,
            created_at="2024-10-05T10:04:00Z"
        ),
        Tweet(
            tweet_id=6,
            author_id="support_agent_001",
            text="Account unlocked! You should be able to access your booking now. Is there anything else I can help you with?",
            role="Agent",
            inbound=False,
            created_at="2024-10-05T10:08:00Z"
        ),
        Tweet(
            tweet_id=7,
            author_id="customer_001",
            text="Working perfectly now! Thank you so much for the excellent help!",
            role="Customer",
            inbound=True,
            created_at="2024-10-05T10:09:00Z"
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

def get_all_configured_kpis() -> Dict[str, list]:
    """Get all configured KPIs from the system"""
    configured_kpis = {}
    
    try:
        for category_name in config_loader.get_all_categories():
            category_kpis = config_loader.get_category_kpis(category_name)
            configured_kpis[category_name] = list(category_kpis.keys())
        
        return configured_kpis
    except Exception as e:
        print(f"Error getting configured KPIs: {e}")
        return {}

def validate_kpi_alignment(analysis_result: Dict[str, Any], configured_kpis: Dict[str, list], logger) -> Dict[str, Any]:
    """
    Validate that the analysis result contains only configured KPIs
    
    Args:
        analysis_result: Result from LLM agent analysis
        configured_kpis: Dictionary of configured KPIs by category
        logger: Logger instance
        
    Returns:
        Validation results
    """
    validation_results = {
        "alignment_status": "UNKNOWN",
        "total_configured_kpis": 0,
        "total_analyzed_kpis": 0,
        "aligned_kpis": [],
        "misaligned_kpis": [],
        "missing_kpis": [],
        "extra_kpis": [],
        "alignment_percentage": 0.0,
        "details": {}
    }
    
    try:
        # Get performance metrics from analysis result
        performance_metrics = analysis_result.get("performance_metrics", {})
        analyzed_categories = performance_metrics.get("categories", {})
        
        # Count total configured KPIs
        for category, kpis in configured_kpis.items():
            validation_results["total_configured_kpis"] += len(kpis)
        
        logger.info(f"Total configured KPIs: {validation_results['total_configured_kpis']}")
        
        # Analyze each category
        for category_name, category_kpis in configured_kpis.items():
            category_validation = {
                "configured_kpis": category_kpis,
                "analyzed_kpis": [],
                "aligned": [],
                "missing": [],
                "extra": []
            }
            
            # Check if category exists in analysis
            if category_name in analyzed_categories:
                analyzed_kpis = list(analyzed_categories[category_name].get("kpis", {}).keys())
                category_validation["analyzed_kpis"] = analyzed_kpis
                validation_results["total_analyzed_kpis"] += len(analyzed_kpis)
                
                # Find aligned KPIs (exact matches)
                for config_kpi in category_kpis:
                    if config_kpi in analyzed_kpis:
                        category_validation["aligned"].append(config_kpi)
                        validation_results["aligned_kpis"].append(f"{category_name}/{config_kpi}")
                    else:
                        category_validation["missing"].append(config_kpi)
                        validation_results["missing_kpis"].append(f"{category_name}/{config_kpi}")
                
                # Find extra KPIs (analyzed but not configured)
                for analyzed_kpi in analyzed_kpis:
                    if analyzed_kpi not in category_kpis:
                        category_validation["extra"].append(analyzed_kpi)
                        validation_results["extra_kpis"].append(f"{category_name}/{analyzed_kpi}")
                        validation_results["misaligned_kpis"].append(f"{category_name}/{analyzed_kpi}")
            else:
                # Entire category missing from analysis
                for config_kpi in category_kpis:
                    category_validation["missing"].append(config_kpi)
                    validation_results["missing_kpis"].append(f"{category_name}/{config_kpi}")
            
            validation_results["details"][category_name] = category_validation
            
            logger.info(f"Category {category_name}: {len(category_validation['aligned'])} aligned, {len(category_validation['missing'])} missing, {len(category_validation['extra'])} extra")
        
        # Calculate alignment percentage
        if validation_results["total_configured_kpis"] > 0:
            validation_results["alignment_percentage"] = (
                len(validation_results["aligned_kpis"]) / validation_results["total_configured_kpis"]
            ) * 100
        
        # Determine overall alignment status
        if validation_results["alignment_percentage"] == 100.0 and len(validation_results["extra_kpis"]) == 0:
            validation_results["alignment_status"] = "PERFECT"
        elif validation_results["alignment_percentage"] >= 80.0 and len(validation_results["extra_kpis"]) == 0:
            validation_results["alignment_status"] = "GOOD"
        elif validation_results["alignment_percentage"] >= 50.0:
            validation_results["alignment_status"] = "PARTIAL"
        else:
            validation_results["alignment_status"] = "POOR"
        
        logger.info(f"Overall alignment: {validation_results['alignment_status']} ({validation_results['alignment_percentage']:.1f}%)")
        
        return validation_results
        
    except Exception as e:
        logger.error(f"Error validating KPI alignment: {e}")
        validation_results["alignment_status"] = "ERROR"
        validation_results["error"] = str(e)
        return validation_results

def test_kpi_alignment():
    """Main test function for KPI alignment verification"""
    logger = setup_logging()
    logger.info("=== KPI ALIGNMENT VERIFICATION TEST ===")
    
    try:
        # Get configured KPIs
        logger.info("Loading configured KPIs...")
        configured_kpis = get_all_configured_kpis()
        
        if not configured_kpis:
            logger.error("No configured KPIs found - cannot proceed with test")
            return
        
        logger.info("Configured KPIs by category:")
        for category, kpis in configured_kpis.items():
            logger.info(f"  {category}: {len(kpis)} KPIs - {', '.join(kpis)}")
        
        # Create test conversation
        logger.info("Creating test conversation with clear KPI evidence...")
        conversation_data = create_test_conversation()
        
        # Initialize LLM agent service
        logger.info("Initializing LLM agent service with KPI alignment fixes...")
        llm_service = LLMAgentPerformanceAnalysisService(model_name="claude-4", temperature=0.1)
        
        # Perform analysis
        logger.info("Performing conversation analysis...")
        analysis_start_time = datetime.now()
        
        analysis_result = llm_service.analyze_conversation_performance(conversation_data)
        
        analysis_duration = (datetime.now() - analysis_start_time).total_seconds()
        logger.info(f"Analysis completed in {analysis_duration:.2f} seconds")
        
        # Validate KPI alignment
        logger.info("Validating KPI alignment...")
        validation_results = validate_kpi_alignment(analysis_result, configured_kpis, logger)
        
        # Create comprehensive test results
        test_results = {
            "test_timestamp": datetime.now().isoformat(),
            "test_type": "KPI Alignment Verification",
            "conversation_id": "kpi_alignment_test_001",
            "analysis_duration_seconds": analysis_duration,
            "configured_kpis": configured_kpis,
            "validation_results": validation_results,
            "analysis_result": analysis_result,
            "test_summary": {
                "alignment_status": validation_results["alignment_status"],
                "alignment_percentage": validation_results["alignment_percentage"],
                "total_configured_kpis": validation_results["total_configured_kpis"],
                "total_analyzed_kpis": validation_results["total_analyzed_kpis"],
                "aligned_kpis_count": len(validation_results["aligned_kpis"]),
                "missing_kpis_count": len(validation_results["missing_kpis"]),
                "extra_kpis_count": len(validation_results["extra_kpis"])
            }
        }
        
        # Save results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"kpi_alignment_test_results_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump(test_results, f, indent=2)
        
        # Print summary
        logger.info("=== KPI ALIGNMENT TEST RESULTS ===")
        logger.info(f"Alignment Status: {validation_results['alignment_status']}")
        logger.info(f"Alignment Percentage: {validation_results['alignment_percentage']:.1f}%")
        logger.info(f"Configured KPIs: {validation_results['total_configured_kpis']}")
        logger.info(f"Analyzed KPIs: {validation_results['total_analyzed_kpis']}")
        logger.info(f"Aligned KPIs: {len(validation_results['aligned_kpis'])}")
        logger.info(f"Missing KPIs: {len(validation_results['missing_kpis'])}")
        logger.info(f"Extra KPIs: {len(validation_results['extra_kpis'])}")
        
        if validation_results["aligned_kpis"]:
            logger.info("✓ Aligned KPIs:")
            for kpi in validation_results["aligned_kpis"]:
                logger.info(f"  - {kpi}")
        
        if validation_results["missing_kpis"]:
            logger.warning("⚠ Missing KPIs:")
            for kpi in validation_results["missing_kpis"]:
                logger.warning(f"  - {kpi}")
        
        if validation_results["extra_kpis"]:
            logger.error("❌ Extra/Misaligned KPIs:")
            for kpi in validation_results["extra_kpis"]:
                logger.error(f"  - {kpi}")
        
        logger.info(f"Results saved to: {filename}")
        
        # Final assessment
        if validation_results["alignment_status"] in ["PERFECT", "GOOD"]:
            logger.info("🎉 KPI ALIGNMENT TEST PASSED!")
            logger.info("The LLM is analyzing only configured KPIs as expected.")
        else:
            logger.warning("⚠️ KPI ALIGNMENT TEST NEEDS ATTENTION")
            logger.warning("The LLM is not perfectly aligned with configured KPIs.")
        
        return test_results
        
    except Exception as e:
        logger.error(f"Error in KPI alignment test: {e}")
        return {
            "test_timestamp": datetime.now().isoformat(),
            "test_type": "KPI Alignment Verification",
            "error": str(e),
            "status": "FAILED"
        }

if __name__ == "__main__":
    test_results = test_kpi_alignment()
    
    # Print final status
    if test_results.get("validation_results", {}).get("alignment_status") in ["PERFECT", "GOOD"]:
        print("\n✅ KPI ALIGNMENT VERIFICATION: PASSED")
        exit(0)
    else:
        print("\n❌ KPI ALIGNMENT VERIFICATION: NEEDS IMPROVEMENT")
        exit(1)
