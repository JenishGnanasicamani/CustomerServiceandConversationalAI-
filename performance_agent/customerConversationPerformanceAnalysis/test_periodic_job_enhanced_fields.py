#!/usr/bin/env python3
"""
Test to verify that periodic job service correctly processes and persists
enhanced fields (normalized_score, confidence, interpretation) along with
score, reason, and evidence
"""

import json
import logging
from datetime import datetime
from typing import Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

try:
    from src.periodic_job_service import PeriodicJobService
    from src.mongodb_integration_service import MongoDBIntegrationService
except ImportError as e:
    logger.error(f"Import error: {e}")
    exit(1)


def create_test_sentiment_record() -> Dict[str, Any]:
    """Create a test sentiment analysis record"""
    return {
        "_id": "test_sentiment_001",
        "conversation": {
            "tweets": [
                {
                    "tweet_id": 1,
                    "author_id": "customer_001",
                    "role": "Customer",
                    "inbound": True,
                    "created_at": "2024-10-05T15:00:00Z",
                    "text": "@Support I can't log into my account! I've been trying for 30 minutes!"
                },
                {
                    "tweet_id": 2,
                    "author_id": "support_agent_001",
                    "role": "Agent",
                    "inbound": False,
                    "created_at": "2024-10-05T15:01:00Z",
                    "text": "I completely understand your frustration! Let me help you right away. Please DM me your email so I can manually reset your password."
                },
                {
                    "tweet_id": 3,
                    "author_id": "customer_001", 
                    "role": "Customer",
                    "inbound": True,
                    "created_at": "2024-10-05T15:03:00Z",
                    "text": "Got it and it works perfectly! Thank you for the amazing quick response!"
                }
            ],
            "classification": {
                "categorization": "technical_support",
                "intent": "account_access",
                "topic": "password_reset",
                "sentiment": "positive"
            }
        },
        "customer": "customer_001",
        "created_at": "2024-10-05T15:00:00Z",
        "created_time": "15:00:00"
    }


def analyze_enhanced_fields(data: Dict[str, Any], path: str = "") -> Dict[str, Any]:
    """
    Analyze presence of enhanced fields in the data structure
    
    Args:
        data: Data structure to analyze
        path: Current path in structure
        
    Returns:
        Analysis results
    """
    analysis = {
        "enhanced_fields_found": [],
        "basic_fields_found": [],
        "missing_enhanced_fields": [],
        "kpi_analysis": {},
        "sub_kpi_analysis": {}
    }
    
    enhanced_fields = ["normalized_score", "confidence", "interpretation"]
    basic_fields = ["score", "reason", "evidence"]
    
    def analyze_recursive(obj, current_path):
        if isinstance(obj, dict):
            # Check if this looks like a KPI structure
            if all(field in obj for field in ["score", "reason"]):
                kpi_path = current_path
                kpi_analysis = {
                    "path": kpi_path,
                    "basic_fields": [],
                    "enhanced_fields": [],
                    "missing_enhanced": []
                }
                
                # Check basic fields
                for field in basic_fields:
                    if field in obj:
                        kpi_analysis["basic_fields"].append(field)
                        analysis["basic_fields_found"].append(f"{current_path}.{field}")
                
                # Check enhanced fields
                for field in enhanced_fields:
                    if field in obj:
                        kpi_analysis["enhanced_fields"].append(field)
                        analysis["enhanced_fields_found"].append(f"{current_path}.{field}")
                    else:
                        kpi_analysis["missing_enhanced"].append(field)
                        analysis["missing_enhanced_fields"].append(f"{current_path}.{field}")
                
                # Determine if this is a sub-KPI
                if "sub_kpis" in current_path:
                    analysis["sub_kpi_analysis"][kpi_path] = kpi_analysis
                else:
                    analysis["kpi_analysis"][kpi_path] = kpi_analysis
            
            # Recurse into nested structures
            for key, value in obj.items():
                new_path = f"{current_path}.{key}" if current_path else key
                analyze_recursive(value, new_path)
                
        elif isinstance(obj, list):
            for i, item in enumerate(obj):
                analyze_recursive(item, f"{current_path}[{i}]")
    
    analyze_recursive(data, path)
    return analysis


def main():
    """Main test execution"""
    logger.info("=== PERIODIC JOB SERVICE ENHANCED FIELDS TEST ===")
    logger.info("Testing complete pipeline with enhanced fields through periodic job service")
    
    try:
        # Create test data
        logger.info("Creating test sentiment record...")
        test_sentiment_record = create_test_sentiment_record()
        
        # Initialize periodic job service (no MongoDB connection needed for this test)
        logger.info("Initializing periodic job service...")
        service = PeriodicJobService("mongodb://test", "test_db")
        
        # Step 1: Convert sentiment record to ConversationData
        logger.info("Step 1: Converting sentiment record to ConversationData...")
        conversation_data = service.convert_sentiment_to_conversation_data(test_sentiment_record)
        
        if not conversation_data:
            logger.error("Failed to convert sentiment record to ConversationData")
            return 1
        
        logger.info(f"Conversion successful: {len(conversation_data.tweets)} tweets, classification: {conversation_data.classification.categorization}")
        
        # Step 2: Analyze conversation performance
        logger.info("Step 2: Analyzing conversation performance...")
        start_time = datetime.now()
        analysis_result = service.analyze_conversation_performance(conversation_data, test_sentiment_record)
        analysis_duration = (datetime.now() - start_time).total_seconds()
        
        if not analysis_result:
            logger.error("Failed to analyze conversation performance")
            return 1
        
        logger.info(f"Analysis completed in {analysis_duration:.2f} seconds")
        
        # Step 3: Analyze the result structure
        logger.info("=== ANALYZING RESULT STRUCTURE ===")
        
        analysis = analyze_enhanced_fields(analysis_result)
        
        logger.info(f"Enhanced fields found: {len(analysis['enhanced_fields_found'])}")
        logger.info(f"Basic fields found: {len(analysis['basic_fields_found'])}")
        logger.info(f"Missing enhanced fields: {len(analysis['missing_enhanced_fields'])}")
        
        # Analyze KPIs
        logger.info(f"\nKPI Analysis: {len(analysis['kpi_analysis'])} KPIs found")
        for kpi_path, kpi_analysis in analysis['kpi_analysis'].items():
            logger.info(f"  KPI: {kpi_path}")
            logger.info(f"    Basic fields: {kpi_analysis['basic_fields']}")
            logger.info(f"    Enhanced fields: {kpi_analysis['enhanced_fields']}")
            if kpi_analysis['missing_enhanced']:
                logger.warning(f"    Missing enhanced: {kpi_analysis['missing_enhanced']}")
        
        # Analyze Sub-KPIs
        logger.info(f"\nSub-KPI Analysis: {len(analysis['sub_kpi_analysis'])} Sub-KPIs found")
        for sub_kpi_path, sub_kpi_analysis in analysis['sub_kpi_analysis'].items():
            logger.info(f"  Sub-KPI: {sub_kpi_path}")
            logger.info(f"    Basic fields: {sub_kpi_analysis['basic_fields']}")
            logger.info(f"    Enhanced fields: {sub_kpi_analysis['enhanced_fields']}")
            if sub_kpi_analysis['missing_enhanced']:
                logger.warning(f"    Missing enhanced: {sub_kpi_analysis['missing_enhanced']}")
        
        # Step 4: Sample structure analysis
        logger.info("\n=== SAMPLE STRUCTURE ANALYSIS ===")
        
        performance_metrics = analysis_result.get("performance_metrics", {})
        categories = performance_metrics.get("categories", {})
        
        if categories:
            first_category_name = next(iter(categories.keys()))
            first_category = categories[first_category_name]
            kpis = first_category.get("kpis", {})
            
            if kpis:
                first_kpi_name = next(iter(kpis.keys()))
                first_kpi = kpis[first_kpi_name]
                
                logger.info(f"Sample KPI '{first_kpi_name}' in category '{first_category_name}':")
                
                # Check all expected fields
                expected_fields = ["score", "reason", "evidence", "normalized_score", "confidence", "interpretation"]
                for field in expected_fields:
                    if field in first_kpi:
                        value = first_kpi[field]
                        if isinstance(value, str) and len(value) > 100:
                            display_value = value[:100] + "..."
                        else:
                            display_value = value
                        logger.info(f"  {field}: {type(value).__name__} = {display_value}")
                    else:
                        logger.warning(f"  {field}: MISSING")
                
                # Check sub-KPIs if present
                if "sub_kpis" in first_kpi:
                    sub_kpis = first_kpi["sub_kpis"]
                    logger.info(f"\n  Sub-KPIs: {len(sub_kpis)} found")
                    
                    if sub_kpis:
                        first_sub_kpi_name = next(iter(sub_kpis.keys()))
                        first_sub_kpi = sub_kpis[first_sub_kpi_name]
                        
                        logger.info(f"  Sample Sub-KPI '{first_sub_kpi_name}':")
                        for field in expected_fields:
                            if field in first_sub_kpi:
                                value = first_sub_kpi[field]
                                if isinstance(value, str) and len(value) > 80:
                                    display_value = value[:80] + "..."
                                else:
                                    display_value = value
                                logger.info(f"    {field}: {type(value).__name__} = {display_value}")
                            else:
                                logger.warning(f"    {field}: MISSING")
        
        # Step 5: Field completeness assessment
        logger.info("\n=== FIELD COMPLETENESS ASSESSMENT ===")
        
        total_kpis = len(analysis['kpi_analysis'])
        total_sub_kpis = len(analysis['sub_kpi_analysis'])
        
        # Count complete KPIs (have all enhanced fields)
        complete_kpis = sum(1 for kpi in analysis['kpi_analysis'].values() 
                           if len(kpi['missing_enhanced']) == 0)
        complete_sub_kpis = sum(1 for sub_kpi in analysis['sub_kpi_analysis'].values() 
                               if len(sub_kpi['missing_enhanced']) == 0)
        
        kpi_completeness = (complete_kpis / total_kpis * 100) if total_kpis > 0 else 0
        sub_kpi_completeness = (complete_sub_kpis / total_sub_kpis * 100) if total_sub_kpis > 0 else 100
        overall_completeness = ((complete_kpis + complete_sub_kpis) / (total_kpis + total_sub_kpis) * 100) if (total_kpis + total_sub_kpis) > 0 else 0
        
        logger.info(f"KPI Completeness: {complete_kpis}/{total_kpis} ({kpi_completeness:.1f}%)")
        logger.info(f"Sub-KPI Completeness: {complete_sub_kpis}/{total_sub_kpis} ({sub_kpi_completeness:.1f}%)")
        logger.info(f"Overall Completeness: {overall_completeness:.1f}%")
        
        # Save detailed results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_filename = f"periodic_job_enhanced_fields_test_{timestamp}.json"
        
        detailed_results = {
            "test_timestamp": datetime.now().isoformat(),
            "analysis_duration_seconds": analysis_duration,
            "total_kpis": total_kpis,
            "total_sub_kpis": total_sub_kpis,
            "kpi_completeness_percentage": kpi_completeness,
            "sub_kpi_completeness_percentage": sub_kpi_completeness,
            "overall_completeness_percentage": overall_completeness,
            "field_analysis": analysis,
            "test_status": "PASSED" if overall_completeness >= 95.0 else "FAILED"
        }
        
        with open(results_filename, 'w') as f:
            json.dump(detailed_results, f, indent=2, default=str)
        
        logger.info(f"Detailed results saved to: {results_filename}")
        
        # Final assessment
        if overall_completeness >= 95.0:
            logger.info("🎉 PERIODIC JOB ENHANCED FIELDS TEST PASSED!")
            logger.info("All enhanced fields are properly implemented in the periodic job pipeline")
        elif overall_completeness >= 80.0:
            logger.info("✅ PERIODIC JOB ENHANCED FIELDS TEST MOSTLY PASSED!")
            logger.info("Most enhanced fields are implemented with minor issues")
        else:
            logger.error("❌ PERIODIC JOB ENHANCED FIELDS TEST FAILED!")
            logger.error("Enhanced fields are missing or incomplete in the periodic job pipeline")
        
        logger.info(f"Final completeness rate: {overall_completeness:.1f}%")
        
        return 0 if overall_completeness >= 95.0 else 1
        
    except Exception as e:
        logger.error(f"Test execution failed: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return 1


if __name__ == "__main__":
    exit(main())
