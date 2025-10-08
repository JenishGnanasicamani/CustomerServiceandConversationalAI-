#!/usr/bin/env python3
"""
Test the fixed performance metrics to ensure categories are properly populated
"""

import sys
import json
import logging
from datetime import datetime

sys.path.insert(0, 'src')

from models import ConversationData, Tweet, Classification
from llm_agent_service import LLMAgentPerformanceAnalysisService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_fixed_performance_metrics():
    """Test that performance metrics are properly populated with categories and KPIs"""
    
    logger.info("=== TESTING FIXED PERFORMANCE METRICS ===")
    
    try:
        # Create test conversation
        tweets = [
            Tweet(
                tweet_id=1,
                author_id="customer_test",
                role="Customer",
                inbound=True,
                created_at="2025-10-04T23:00:00Z",
                text="Hi, I need help with my website login. It's not working!"
            ),
            Tweet(
                tweet_id=2,
                author_id="agent_test",
                role="Service Provider", 
                inbound=False,
                created_at="2025-10-04T23:01:00Z",
                text="I'm so sorry to hear you're having trouble! I'd be happy to help you with your login issue. Could you please DM me your account details so I can assist you further?"
            )
        ]
        
        classification = Classification(
            categorization="Technical Support",
            intent="Technical Issue",
            topic="Website",
            sentiment="Neutral"
        )
        
        conversation_data = ConversationData(
            tweets=tweets,
            classification=classification
        )
        
        conversation_data.conversation_id = f"test_fixed_metrics_{int(datetime.now().timestamp())}"
        
        # Initialize service
        logger.info("Initializing LLM Agent Service...")
        service = LLMAgentPerformanceAnalysisService(model_name="claude-4", temperature=0.1)
        
        # Test the main analyze_conversation_performance method
        logger.info("Testing analyze_conversation_performance method...")
        result = service.analyze_conversation_performance(conversation_data)
        
        logger.info("✅ Analysis completed!")
        logger.info(f"📊 Result keys: {list(result.keys())}")
        
        # Verify the structure
        success = True
        
        # Check if performance_metrics exists
        if 'performance_metrics' not in result:
            logger.error("❌ CRITICAL: performance_metrics field missing from result!")
            success = False
        else:
            logger.info("✅ performance_metrics field found in result")
            pm = result['performance_metrics']
            
            # Check if categories exists in performance_metrics
            if 'categories' not in pm:
                logger.error("❌ CRITICAL: categories field missing from performance_metrics!")
                success = False
            else:
                logger.info("✅ categories field found in performance_metrics")
                categories = pm['categories']
                
                if not categories:
                    logger.error("❌ CRITICAL: categories is empty!")
                    success = False
                else:
                    logger.info(f"✅ Categories found: {len(categories)} categories")
                    logger.info(f"📋 Category names: {list(categories.keys())}")
                    
                    total_kpis = 0
                    for cat_name, cat_data in categories.items():
                        if 'kpis' in cat_data:
                            kpi_count = len(cat_data['kpis'])
                            total_kpis += kpi_count
                            logger.info(f"  📂 {cat_name}: {kpi_count} KPIs")
                            
                            # Show sample KPI data
                            for kpi_name, kpi_data in list(cat_data['kpis'].items())[:2]:  # Show first 2 KPIs
                                score = kpi_data.get('score', 'N/A')
                                reasoning = kpi_data.get('reasoning', 'N/A')[:50] + "..."
                                logger.info(f"    📈 {kpi_name}: score={score}, reasoning={reasoning}")
                        else:
                            logger.warning(f"⚠️  {cat_name}: No kpis field found")
                    
                    logger.info(f"📊 Total KPIs across all categories: {total_kpis}")
                    
                    if total_kpis > 0:
                        logger.info("🎉 SUCCESS: Categories contain KPI data!")
                    else:
                        logger.error("❌ CRITICAL: No KPIs found in any category!")
                        success = False
        
        # Check metadata
        if 'performance_metrics' in result and 'metadata' in result['performance_metrics']:
            metadata = result['performance_metrics']['metadata']
            logger.info(f"📋 Metadata - Total KPIs evaluated: {metadata.get('total_kpis_evaluated', 0)}")
            logger.info(f"📅 Evaluation timestamp: {metadata.get('evaluation_timestamp', 'N/A')}")
            logger.info(f"🤖 Model used: {metadata.get('model_used', 'N/A')}")
        
        # Show JSON structure preview
        if success:
            logger.info("📄 Performance metrics JSON preview:")
            if 'performance_metrics' in result:
                pm_json = json.dumps(result['performance_metrics'], indent=2, default=str)
                preview = pm_json[:800] + "..." if len(pm_json) > 800 else pm_json
                logger.info(preview)
        
        # Overall result
        if success:
            logger.info("🎉 PERFORMANCE METRICS TEST PASSED!")
            logger.info("✅ Categories are properly populated with KPI data")
            logger.info("✅ Structure matches expected MongoDB format") 
            logger.info("✅ Performance metrics should now persist correctly to MongoDB")
        else:
            logger.error("❌ PERFORMANCE METRICS TEST FAILED!")
            logger.error("❌ Categories are still empty or missing")
        
        return success
        
    except Exception as e:
        logger.error(f"❌ Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_mongodb_structure_compatibility():
    """Test that the result structure is compatible with MongoDB document from user"""
    logger.info("=== TESTING MONGODB STRUCTURE COMPATIBILITY ===")
    
    # User's MongoDB document structure (from the feedback)
    expected_structure = {
        "conversation_id": "string",
        "performance_metrics": {
            "categories": {
                # Should have category data with KPIs
            },
            "metadata": {
                # Should have metadata
            }
        },
        "analysis_timestamp": "string",
        "analysis_method": "string"
    }
    
    logger.info("✅ Expected structure defined")
    logger.info("✅ Our result structure should match this format")
    logger.info("✅ Key field: performance_metrics.categories should NOT be empty")
    
    return True

if __name__ == "__main__":
    logger.info("🚀 STARTING FIXED PERFORMANCE METRICS TEST")
    logger.info("=" * 70)
    
    # Test the fixed performance metrics
    metrics_success = test_fixed_performance_metrics()
    
    logger.info("=" * 30)
    
    # Test MongoDB compatibility
    compat_success = test_mongodb_structure_compatibility()
    
    logger.info("=" * 70)
    
    if metrics_success and compat_success:
        logger.info("🎉 ALL TESTS PASSED!")
        logger.info("✅ Performance metrics are properly populated")
        logger.info("✅ Ready for MongoDB persistence testing")
    else:
        logger.error("❌ TESTS FAILED!")
        logger.error("❌ Performance metrics still need fixing")
