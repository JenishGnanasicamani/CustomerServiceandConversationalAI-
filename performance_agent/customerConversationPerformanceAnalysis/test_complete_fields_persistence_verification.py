#!/usr/bin/env python3
"""
Complete Fields Persistence Verification Test

This test verifies that ALL required fields (score, reasoning, evidence, normalized_score, 
confidence, interpretation) are properly included in the performance metrics structure
and would be persisted to MongoDB correctly.
"""

import json
import logging
from datetime import datetime
from typing import Dict, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def test_complete_fields_persistence():
    """Test that all required fields are included in performance metrics"""
    
    logger.info("🚀 Starting Complete Fields Persistence Verification Test")
    logger.info("=" * 80)
    logger.info("")
    
    try:
        # Import required modules
        from src.models import ConversationData, Tweet, Classification
        from src.llm_agent_service import get_llm_agent_service
        
        # Create test conversation data
        tweets = [
            Tweet(
                tweet_id=1001,
                author_id="customer_1",
                role="Customer",
                inbound=True,
                created_at="2024-01-01T10:00:00Z",
                text="Hi @Support, I'm really frustrated because I can't reset my password. I've been trying for 30 minutes and nothing works!"
            ),
            Tweet(
                tweet_id=1002,
                author_id="agent_1", 
                role="Agent",
                inbound=False,
                created_at="2024-01-01T10:01:00Z",
                text="I completely understand how frustrating that must be! I'm here to help you get this resolved right away. Let me assist you with a manual password reset - please DM me your email address so I can verify your account."
            ),
            Tweet(
                tweet_id=1003,
                author_id="customer_1",
                role="Customer", 
                inbound=True,
                created_at="2024-01-01T10:03:00Z",
                text="Thank you! Just sent you my email via DM. I really appreciate your quick response!"
            ),
            Tweet(
                tweet_id=1004,
                author_id="agent_1",
                role="Agent",
                inbound=False, 
                created_at="2024-01-01T10:05:00Z",
                text="Perfect! I've processed your password reset and sent you a new temporary password. You should receive it within 2 minutes. Is there anything else I can help you with today?"
            ),
            Tweet(
                tweet_id=1005,
                author_id="customer_1",
                role="Customer",
                inbound=True,
                created_at="2024-01-01T10:07:00Z", 
                text="Got it and it works perfectly! You're amazing - thank you so much for the excellent help!"
            )
        ]
        
        classification = Classification(
            categorization="Password Reset",
            intent="Technical Support", 
            topic="Account Access",
            sentiment="Positive"
        )
        
        conversation_data = ConversationData(tweets=tweets, classification=classification)
        
        # Initialize LLM Agent Service
        logger.info("📋 Test: Complete Fields Persistence Verification")
        logger.info("🔬 Testing LLM Agent Service for complete field structure...")
        
        service = get_llm_agent_service()
        
        # Call the analyze_conversation_performance method (what MongoDB integration uses)
        logger.info("Running performance analysis with complete field structure...")
        result = service.analyze_conversation_performance(conversation_data)
        
        # Verify result structure
        logger.info("🔍 Verifying complete performance metrics structure...")
        
        required_top_level_fields = [
            "conversation_id", 
            "analysis_timestamp", 
            "analysis_method",
            "model_used",
            "performance_metrics"
        ]
        
        # Check top-level fields
        missing_top_fields = []
        for field in required_top_level_fields:
            if field not in result:
                missing_top_fields.append(field)
        
        if missing_top_fields:
            logger.error(f"❌ Missing top-level fields: {missing_top_fields}")
            return False
        else:
            logger.info("✅ All top-level fields present")
        
        # Check performance_metrics structure
        performance_metrics = result.get("performance_metrics", {})
        
        if "categories" not in performance_metrics:
            logger.error("❌ Missing 'categories' in performance_metrics")
            return False
        
        categories = performance_metrics["categories"]
        logger.info(f"Found {len(categories)} categories: {list(categories.keys())}")
        
        # Required fields for each KPI
        required_kpi_fields = [
            "score",
            "reasoning", 
            "evidence",
            "normalized_score",
            "confidence", 
            "interpretation"
        ]
        
        total_kpis_checked = 0
        kpis_with_all_fields = 0
        field_coverage = {field: 0 for field in required_kpi_fields}
        
        # Check each category and KPI
        for category_name, category_data in categories.items():
            logger.info(f"\n📂 Checking category: {category_name}")
            
            if "kpis" not in category_data:
                logger.warning(f"⚠️  No KPIs found in category {category_name}")
                continue
                
            kpis = category_data["kpis"]
            logger.info(f"  Found {len(kpis)} KPIs in {category_name}")
            
            for kpi_name, kpi_data in kpis.items():
                total_kpis_checked += 1
                logger.info(f"    🔍 Checking KPI: {kpi_name}")
                
                # Check each required field
                missing_fields = []
                present_fields = []
                
                for field in required_kpi_fields:
                    if field in kpi_data:
                        present_fields.append(field)
                        field_coverage[field] += 1
                        
                        # Validate field content
                        field_value = kpi_data[field]
                        if field == "score" and not isinstance(field_value, (int, float)):
                            logger.warning(f"      ⚠️  {field} is not numeric: {type(field_value)}")
                        elif field == "reasoning" and (not field_value or len(str(field_value)) < 10):
                            logger.warning(f"      ⚠️  {field} is too short or empty: {len(str(field_value))} chars")
                        elif field == "evidence" and not isinstance(field_value, list):
                            logger.warning(f"      ⚠️  {field} is not a list: {type(field_value)}")
                        elif field == "normalized_score" and not isinstance(field_value, (int, float)):
                            logger.warning(f"      ⚠️  {field} is not numeric: {type(field_value)}")
                        elif field == "confidence" and not isinstance(field_value, (int, float)):
                            logger.warning(f"      ⚠️  {field} is not numeric: {type(field_value)}")
                        elif field == "interpretation" and not isinstance(field_value, str):
                            logger.warning(f"      ⚠️  {field} is not a string: {type(field_value)}")
                        else:
                            logger.info(f"      ✅ {field}: {str(field_value)[:50]}{'...' if len(str(field_value)) > 50 else ''}")
                    else:
                        missing_fields.append(field)
                
                if not missing_fields:
                    kpis_with_all_fields += 1
                    logger.info(f"      ✅ {kpi_name}: ALL required fields present")
                else:
                    logger.error(f"      ❌ {kpi_name}: Missing fields: {missing_fields}")
                    logger.info(f"      ✅ {kpi_name}: Present fields: {present_fields}")
        
        # Summary statistics
        logger.info(f"\n📊 FIELD COVERAGE SUMMARY:")
        logger.info(f"Total KPIs checked: {total_kpis_checked}")
        logger.info(f"KPIs with ALL required fields: {kpis_with_all_fields}")
        logger.info(f"Coverage rate: {(kpis_with_all_fields/total_kpis_checked)*100:.1f}%" if total_kpis_checked > 0 else "N/A")
        
        logger.info(f"\n📈 INDIVIDUAL FIELD COVERAGE:")
        for field, count in field_coverage.items():
            coverage_pct = (count/total_kpis_checked)*100 if total_kpis_checked > 0 else 0
            status = "✅" if coverage_pct == 100 else "❌"
            logger.info(f"{status} {field}: {count}/{total_kpis_checked} ({coverage_pct:.1f}%)")
        
        # Check critical fields that were missing
        critical_missing_fields = []
        for field, count in field_coverage.items():
            if count < total_kpis_checked:
                critical_missing_fields.append(field)
        
        if critical_missing_fields:
            logger.error(f"\n❌ CRITICAL ISSUE: Missing fields detected: {critical_missing_fields}")
            logger.error("These fields are required for proper MongoDB persistence!")
            
            # Show sample KPI structure for debugging
            if categories:
                sample_category = list(categories.keys())[0]
                sample_kpis = categories[sample_category].get("kpis", {})
                if sample_kpis:
                    sample_kpi = list(sample_kpis.keys())[0]
                    sample_data = sample_kpis[sample_kpi]
                    logger.error(f"\nSample KPI structure for {sample_kpi}:")
                    logger.error(json.dumps(sample_data, indent=2))
            
            return False
        else:
            logger.info(f"\n✅ SUCCESS: All {len(required_kpi_fields)} required fields present in all {total_kpis_checked} KPIs!")
        
        # Save detailed results for debugging
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_file = f"complete_fields_persistence_test_results_{timestamp}.json"
        
        test_results = {
            "test_name": "Complete Fields Persistence Verification",
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_kpis_checked": total_kpis_checked,
                "kpis_with_all_fields": kpis_with_all_fields,
                "coverage_rate": (kpis_with_all_fields/total_kpis_checked)*100 if total_kpis_checked > 0 else 0,
                "required_fields": required_kpi_fields,
                "field_coverage": field_coverage,
                "critical_missing_fields": critical_missing_fields
            },
            "full_performance_metrics": performance_metrics,
            "test_passed": len(critical_missing_fields) == 0
        }
        
        with open(results_file, 'w') as f:
            json.dump(test_results, f, indent=2)
        
        logger.info(f"📄 Test results saved to: {results_file}")
        
        return len(critical_missing_fields) == 0
        
    except Exception as e:
        logger.error(f"❌ Test failed with error: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False


if __name__ == "__main__":
    logger.info("🚀 Starting Complete Fields Persistence Verification Tests")
    logger.info("=" * 80)
    logger.info("")
    
    test_passed = test_complete_fields_persistence()
    
    logger.info("")
    logger.info("=" * 80)
    logger.info("🏁 COMPLETE FIELDS PERSISTENCE VERIFICATION SUMMARY")
    logger.info("=" * 80)
    
    if test_passed:
        logger.info("✅ ALL TESTS PASSED! All required fields are properly included.")
        logger.info("✅ normalized_score, confidence, and interpretation are present.")
        logger.info("✅ MongoDB persistence will include all required fields.")
        logger.info("📊 Tests passed: 1/1")
    else:
        logger.error("❌ TESTS FAILED! Some required fields are missing.")
        logger.error("❌ normalized_score, confidence, or interpretation may be missing.")
        logger.error("❌ MongoDB persistence will be incomplete.")
        logger.error("📊 Tests passed: 0/1")
    
    logger.info("=" * 80)
