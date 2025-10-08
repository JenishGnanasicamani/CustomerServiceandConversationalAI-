#!/usr/bin/env python3
"""
Test to verify that enhanced fields (normalized_score, confidence, interpretation) 
are properly persisted to MongoDB through the complete pipeline
"""

import json
import logging
from datetime import datetime
from typing import Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

try:
    from src.llm_agent_service import LLMAgentPerformanceAnalysisService
    from src.mongodb_integration_service import MongoDBIntegrationService
    from src.models import ConversationData, Tweet, Classification
except ImportError as e:
    logger.error(f"Import error: {e}")
    exit(1)


def create_test_mongo_document() -> Dict[str, Any]:
    """Create a test MongoDB document structure"""
    return {
        "_id": "test_conversation_001",
        "conversation_number": 1,
        "tweets": [
            {
                "tweet_id": 1,
                "author_id": "customer_001",
                "role": "Customer",
                "inbound": True,
                "created_at": "2024-10-05T15:00:00Z",
                "text": "@Support I'm having trouble accessing my account - it's been locked for hours!"
            },
            {
                "tweet_id": 2,
                "author_id": "support_agent_001",
                "role": "Agent", 
                "inbound": False,
                "created_at": "2024-10-05T15:01:00Z",
                "text": "Hi! I completely understand how frustrating this must be. I'll help unlock your account right away."
            },
            {
                "tweet_id": 3,
                "author_id": "customer_001",
                "role": "Customer",
                "inbound": True,
                "created_at": "2024-10-05T15:08:00Z",
                "text": "Perfect! Everything is working now. Thank you so much for the amazing help!"
            }
        ],
        "classification": {
            "categorization": "technical_support",
            "intent": "account_access",
            "topic": "account_unlock",
            "sentiment": "positive"
        }
    }


def analyze_field_presence(data: Dict[str, Any], path: str = "") -> Dict[str, Any]:
    """
    Recursively analyze which fields are present in the data structure
    
    Args:
        data: Data structure to analyze
        path: Current path in the structure
        
    Returns:
        Dictionary with field analysis
    """
    field_analysis = {
        "enhanced_fields_found": [],
        "basic_fields_found": [],
        "missing_enhanced_fields": [],
        "field_paths": {},
        "structure_issues": []
    }
    
    enhanced_fields = ["normalized_score", "confidence", "interpretation"]
    basic_fields = ["score", "reasoning", "evidence"]
    
    def analyze_recursive(obj, current_path):
        if isinstance(obj, dict):
            for key, value in obj.items():
                new_path = f"{current_path}.{key}" if current_path else key
                
                # Check if this is an enhanced field
                if key in enhanced_fields:
                    field_analysis["enhanced_fields_found"].append(new_path)
                    field_analysis["field_paths"][new_path] = {
                        "type": type(value).__name__,
                        "value": value if not isinstance(value, (dict, list)) else f"<{type(value).__name__}>"
                    }
                
                # Check if this is a basic field
                if key in basic_fields:
                    field_analysis["basic_fields_found"].append(new_path)
                    field_analysis["field_paths"][new_path] = {
                        "type": type(value).__name__,
                        "value": value if not isinstance(value, (dict, list)) else f"<{type(value).__name__}>"
                    }
                
                # Recurse into nested structures
                analyze_recursive(value, new_path)
                
        elif isinstance(obj, list):
            for i, item in enumerate(obj):
                analyze_recursive(item, f"{current_path}[{i}]")
    
    analyze_recursive(data, path)
    
    # Check for missing enhanced fields in KPI structures
    kpi_paths = [p for p in field_analysis["field_paths"].keys() if "kpis" in p and "score" in p]
    for kpi_path in kpi_paths:
        kpi_base = kpi_path.rsplit(".score", 1)[0]
        for enhanced_field in enhanced_fields:
            enhanced_path = f"{kpi_base}.{enhanced_field}"
            if enhanced_path not in field_analysis["enhanced_fields_found"]:
                field_analysis["missing_enhanced_fields"].append(enhanced_path)
    
    return field_analysis


def main():
    """Main test execution"""
    logger.info("=== MONGODB PERSISTENCE ENHANCED FIELDS TEST ===")
    logger.info("Testing persistence of normalized_score, confidence, and interpretation through complete pipeline")
    
    try:
        # Create test data
        logger.info("Creating test MongoDB document...")
        test_mongo_doc = create_test_mongo_document()
        
        # Initialize services
        logger.info("Initializing services...")
        llm_service = LLMAgentPerformanceAnalysisService(model_name="claude-4", temperature=0.1)
        mongodb_service = MongoDBIntegrationService()
        
        # Step 1: Convert MongoDB document to ConversationData
        logger.info("Step 1: Converting MongoDB document to ConversationData...")
        conversation_data = mongodb_service.convert_mongo_document_to_conversation_data(test_mongo_doc)
        
        # Step 2: Perform LLM analysis
        logger.info("Step 2: Performing LLM analysis...")
        start_time = datetime.now()
        analysis_results = llm_service.analyze_conversation_performance(conversation_data)
        analysis_duration = (datetime.now() - start_time).total_seconds()
        
        logger.info(f"Analysis completed in {analysis_duration:.2f} seconds")
        
        # Step 3: Create result document for MongoDB
        logger.info("Step 3: Creating MongoDB result document...")
        result_document = mongodb_service.create_analysis_result_document(test_mongo_doc, analysis_results)
        
        # Step 4: Analyze what fields are present at each stage
        logger.info("=== FIELD PRESENCE ANALYSIS ===")
        
        # Analyze LLM analysis results
        logger.info("Analyzing LLM analysis results...")
        llm_analysis = analyze_field_presence(analysis_results, "llm_results")
        
        logger.info(f"Enhanced fields in LLM results: {len(llm_analysis['enhanced_fields_found'])}")
        for field in llm_analysis["enhanced_fields_found"][:5]:  # Show first 5
            logger.info(f"  - {field}: {llm_analysis['field_paths'][field]}")
        
        logger.info(f"Missing enhanced fields in LLM results: {len(llm_analysis['missing_enhanced_fields'])}")
        for missing in llm_analysis["missing_enhanced_fields"][:3]:  # Show first 3
            logger.info(f"  - Missing: {missing}")
        
        # Analyze MongoDB result document
        logger.info("\nAnalyzing MongoDB result document...")
        mongodb_analysis = analyze_field_presence(result_document, "mongodb_result")
        
        logger.info(f"Enhanced fields in MongoDB document: {len(mongodb_analysis['enhanced_fields_found'])}")
        for field in mongodb_analysis["enhanced_fields_found"][:5]:  # Show first 5
            logger.info(f"  - {field}: {mongodb_analysis['field_paths'][field]}")
        
        logger.info(f"Missing enhanced fields in MongoDB document: {len(mongodb_analysis['missing_enhanced_fields'])}")
        for missing in mongodb_analysis["missing_enhanced_fields"][:3]:  # Show first 3
            logger.info(f"  - Missing: {missing}")
        
        # Compare the two stages
        logger.info("\n=== FIELD PRESERVATION ANALYSIS ===")
        
        # Check if enhanced fields are preserved through the pipeline
        llm_enhanced_count = len(llm_analysis['enhanced_fields_found'])
        mongodb_enhanced_count = len(mongodb_analysis['enhanced_fields_found'])
        
        preservation_rate = (mongodb_enhanced_count / llm_enhanced_count * 100) if llm_enhanced_count > 0 else 0
        
        logger.info(f"Enhanced field preservation rate: {preservation_rate:.1f}%")
        logger.info(f"LLM stage: {llm_enhanced_count} enhanced fields")
        logger.info(f"MongoDB stage: {mongodb_enhanced_count} enhanced fields")
        
        # Check specific field preservation
        logger.info("\nSpecific field preservation:")
        for enhanced_field in ["normalized_score", "confidence", "interpretation"]:
            llm_count = len([f for f in llm_analysis['enhanced_fields_found'] if enhanced_field in f])
            mongodb_count = len([f for f in mongodb_analysis['enhanced_fields_found'] if enhanced_field in f])
            logger.info(f"  {enhanced_field}: LLM={llm_count}, MongoDB={mongodb_count}")
        
        # Sample the actual structure
        logger.info("\n=== SAMPLE STRUCTURE ANALYSIS ===")
        
        # Extract a sample KPI structure from both stages
        performance_metrics = analysis_results.get("performance_metrics", {})
        categories = performance_metrics.get("categories", {})
        
        if categories:
            first_category = next(iter(categories.values()))
            kpis = first_category.get("kpis", {})
            if kpis:
                first_kpi_name = next(iter(kpis.keys()))
                first_kpi_data = kpis[first_kpi_name]
                
                logger.info(f"Sample KPI '{first_kpi_name}' structure in LLM results:")
                for field in ["score", "normalized_score", "reasoning", "evidence", "confidence", "interpretation"]:
                    if field in first_kpi_data:
                        value = first_kpi_data[field]
                        logger.info(f"  {field}: {type(value).__name__} = {value if not isinstance(value, (dict, list)) else f'<{type(value).__name__} with {len(value)} items>'}")
                    else:
                        logger.warning(f"  {field}: MISSING")
        
        # Check MongoDB result document structure
        mongodb_performance = result_document.get("performance_analysis", {}).get("performance_metrics", {})
        mongodb_categories = mongodb_performance.get("categories", {})
        
        if mongodb_categories:
            first_category = next(iter(mongodb_categories.values()))
            kpis = first_category.get("kpis", {})
            if kpis:
                first_kpi_name = next(iter(kpis.keys()))
                first_kpi_data = kpis[first_kpi_name]
                
                logger.info(f"\nSample KPI '{first_kpi_name}' structure in MongoDB document:")
                for field in ["score", "normalized_score", "reasoning", "evidence", "confidence", "interpretation"]:
                    if field in first_kpi_data:
                        value = first_kpi_data[field]
                        logger.info(f"  {field}: {type(value).__name__} = {value if not isinstance(value, (dict, list)) else f'<{type(value).__name__} with {len(value)} items>'}")
                    else:
                        logger.warning(f"  {field}: MISSING")
        
        # Save detailed results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_filename = f"mongodb_persistence_test_{timestamp}.json"
        
        detailed_results = {
            "test_timestamp": datetime.now().isoformat(),
            "analysis_duration_seconds": analysis_duration,
            "llm_field_analysis": llm_analysis,
            "mongodb_field_analysis": mongodb_analysis,
            "preservation_rate": preservation_rate,
            "test_status": "PASSED" if preservation_rate >= 95.0 else "FAILED",
            "sample_llm_structure": {},
            "sample_mongodb_structure": {}
        }
        
        # Add sample structures to results
        if categories and kpis:
            detailed_results["sample_llm_structure"] = first_kpi_data
        
        if mongodb_categories and mongodb_categories:
            first_category = next(iter(mongodb_categories.values()))
            kpis = first_category.get("kpis", {})
            if kpis:
                first_kpi_data = next(iter(kpis.values()))
                detailed_results["sample_mongodb_structure"] = first_kpi_data
        
        with open(results_filename, 'w') as f:
            json.dump(detailed_results, f, indent=2)
        
        logger.info(f"Detailed results saved to: {results_filename}")
        
        # Final assessment
        if preservation_rate >= 95.0:
            logger.info("🎉 MONGODB PERSISTENCE TEST PASSED!")
            logger.info("All enhanced fields are properly preserved through the complete pipeline")
        elif preservation_rate >= 80.0:
            logger.info("✅ MONGODB PERSISTENCE TEST MOSTLY PASSED!")
            logger.info("Most enhanced fields are preserved with minor issues")
        else:
            logger.error("❌ MONGODB PERSISTENCE TEST FAILED!")
            logger.error("Enhanced fields are being lost in the persistence pipeline")
        
        logger.info(f"Final preservation rate: {preservation_rate:.1f}%")
        
    except Exception as e:
        logger.error(f"Test execution failed: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
