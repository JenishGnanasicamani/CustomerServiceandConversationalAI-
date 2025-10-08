#!/usr/bin/env python3
"""
Debug why performance_metrics.categories is empty in MongoDB
"""

import sys
import json
import logging
from datetime import datetime

sys.path.insert(0, 'src')

from models import ConversationData, Tweet, Classification
from llm_agent_service import LLMAgentPerformanceAnalysisService

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def debug_empty_categories():
    """Debug why categories are empty in performance_metrics"""
    
    logger.info("=== DEBUGGING EMPTY CATEGORIES ISSUE ===")
    
    try:
        # Create test conversation
        tweets = [
            Tweet(
                tweet_id=1,
                author_id="customer_test",
                role="Customer",
                inbound=True,
                created_at="2025-10-04T23:00:00Z",
                text="Hi, I had a great experience with your service today!"
            ),
            Tweet(
                tweet_id=2,
                author_id="agent_test",
                role="Service Provider", 
                inbound=False,
                created_at="2025-10-04T23:01:00Z",
                text="Thank you so much for the positive feedback! We're delighted to hear you had a great experience."
            )
        ]
        
        classification = Classification(
            categorization="Positive feedback",
            intent="Feedback",
            topic="General",
            sentiment="Positive"
        )
        
        conversation_data = ConversationData(
            tweets=tweets,
            classification=classification
        )
        
        conversation_data.conversation_id = f"debug_empty_categories_{int(datetime.now().timestamp())}"
        
        # Initialize service
        logger.info("Initializing LLM Agent Service...")
        service = LLMAgentPerformanceAnalysisService(model_name="claude-4", temperature=0.1)
        
        # Test the parsing with mock agent output that would normally come from the LLM
        logger.info("Testing with mock agent output...")
        
        mock_agent_output = """
I'll analyze this conversation systematically:

<tool_invocation>
<tool_name>analyze_kpi_performance</tool_name>
<parameters>
<category>accuracy_compliance</category>
<kpi_name>resolution_completeness</kpi_name>
<score>8.5</score>
<reasoning>The agent provided a complete and appropriate response to the positive feedback, acknowledging the customer's satisfaction.</reasoning>
</parameters>
</tool_invocation>

<tool_invocation>  
<tool_name>analyze_kpi_performance</tool_name>
<parameters>
<category>empathy_communication</category>
<kpi_name>empathy_score</kpi_name>
<score>9.0</score>
<reasoning>The agent's response showed excellent empathy by expressing genuine delight at the customer's positive experience.</reasoning>
</parameters>
</tool_invocation>

<tool_invocation>
<tool_name>analyze_kpi_performance</tool_name>
<parameters>
<category>efficiency_resolution</category>
<kpi_name>customer_effort_score</kpi_name>
<score>8.2</score>
<reasoning>No effort required from customer as this was positive feedback, agent appropriately acknowledged it.</reasoning>
</parameters>
</tool_invocation>

Based on my analysis, this conversation shows excellent customer service performance with high scores across all categories.
"""
        
        # Test the tool-based parsing
        logger.info("Step 1: Testing tool-based parsing...")
        try:
            categories_from_tools = service._parse_tool_based_agent_output(mock_agent_output)
            logger.info(f"✅ Tool parsing successful. Found {len(categories_from_tools)} categories:")
            for cat_name, cat_data in categories_from_tools.items():
                kpi_count = len(cat_data.get('kpis', {}))
                logger.info(f"  📂 {cat_name}: {kpi_count} KPIs")
                for kpi_name, kpi_data in cat_data.get('kpis', {}).items():
                    score = kpi_data.get('score', 'N/A')
                    logger.info(f"    📋 {kpi_name}: {score}")
        except Exception as e:
            logger.error(f"❌ Tool parsing failed: {e}")
            categories_from_tools = {}
        
        # Test the enhanced performance metrics creation
        logger.info("Step 2: Testing enhanced performance metrics creation...")
        try:
            if categories_from_tools:
                performance_metrics = service._create_enhanced_performance_metrics(categories_from_tools)
                logger.info("✅ Performance metrics creation successful!")
                
                # Check the structure
                logger.info("📊 Performance metrics structure:")
                logger.info(f"  - Has categories: {'categories' in performance_metrics}")
                
                if 'categories' in performance_metrics:
                    categories = performance_metrics['categories']
                    logger.info(f"  - Categories count: {len(categories)}")
                    logger.info(f"  - Category names: {list(categories.keys())}")
                    
                    total_kpis = 0
                    for cat_name, cat_data in categories.items():
                        kpis = cat_data.get('kpis', {})
                        kpi_count = len(kpis)
                        total_kpis += kpi_count
                        logger.info(f"    📂 {cat_name}: {kpi_count} KPIs")
                        
                        for kpi_name, kpi_data in kpis.items():
                            score = kpi_data.get('score', 'N/A')
                            reasoning = kpi_data.get('reasoning', 'N/A')[:50] + "..."
                            logger.info(f"      📋 {kpi_name}: {score} - {reasoning}")
                    
                    logger.info(f"  - Total KPIs: {total_kpis}")
                    
                    if total_kpis > 0:
                        logger.info("🎉 SUCCESS: Categories contain KPI data!")
                        
                        # Show the JSON structure
                        logger.info("📄 JSON structure preview:")
                        sample_json = json.dumps(performance_metrics, indent=2, default=str)[:500] + "..."
                        logger.info(sample_json)
                        
                    else:
                        logger.error("❌ PROBLEM: Categories exist but no KPIs found!")
                else:
                    logger.error("❌ PROBLEM: No categories field in performance_metrics!")
            else:
                logger.error("❌ PROBLEM: No categories from tool parsing!")
                
        except Exception as e:
            logger.error(f"❌ Performance metrics creation failed: {e}")
            import traceback
            traceback.print_exc()
        
        # Test what happens with the real comprehensive analysis method
        logger.info("Step 3: Testing comprehensive analysis method...")
        try:
            # This is what the API actually calls
            result = service.analyze_conversation_performance(conversation_data)
            
            logger.info("✅ Comprehensive analysis completed!")
            logger.info(f"📊 Result keys: {list(result.keys())}")
            
            if 'performance_metrics' in result:
                pm = result['performance_metrics']
                logger.info("✅ performance_metrics found in result!")
                
                if 'categories' in pm:
                    categories = pm['categories']
                    logger.info(f"📂 Categories in result: {len(categories)} categories")
                    logger.info(f"📋 Category names: {list(categories.keys())}")
                    
                    total_kpis = sum(len(cat.get('kpis', {})) for cat in categories.values())
                    logger.info(f"📈 Total KPIs in final result: {total_kpis}")
                    
                    if total_kpis > 0:
                        logger.info("🎉 FINAL SUCCESS: Complete analysis has KPI data!")
                    else:
                        logger.error("❌ FINAL PROBLEM: Complete analysis has empty categories!")
                        
                        # Debug each category
                        for cat_name, cat_data in categories.items():
                            logger.error(f"  ❌ {cat_name}: {cat_data}")
                else:
                    logger.error("❌ No categories in performance_metrics from comprehensive analysis!")
            else:
                logger.error("❌ No performance_metrics in comprehensive analysis result!")
                
        except Exception as e:
            logger.error(f"❌ Comprehensive analysis failed: {e}")
            import traceback
            traceback.print_exc()
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Debug failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    logger.info("🚀 STARTING EMPTY CATEGORIES DEBUG")
    logger.info("=" * 60)
    
    success = debug_empty_categories()
    
    if success:
        logger.info("✅ Debug completed successfully!")
    else:
        logger.error("❌ Debug failed!")
        
    logger.info("=" * 60)
