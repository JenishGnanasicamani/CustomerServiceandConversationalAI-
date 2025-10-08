#!/usr/bin/env python3
"""
Test the improved LLM prompt to ensure it returns proper JSON with detailed reasoning
"""

import sys
import os
import json
import logging
from datetime import datetime

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from models import ConversationData, Tweet, Classification
from llm_agent_service import LLMAgentPerformanceAnalysisService

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Sample conversation data
sample_conversation = {
    "tweets": [
        {
            "tweet_id": 1001,
            "author_id": "customer_1", 
            "role": "Customer",
            "inbound": True,
            "created_at": "2024-01-01T10:00:00Z",
            "text": "Hi @Support, I'm really frustrated because I can't reset my password. I've been trying for 30 minutes and nothing works!"
        },
        {
            "tweet_id": 1002,
            "author_id": "agent_1",
            "role": "Agent", 
            "inbound": False,
            "created_at": "2024-01-01T10:01:00Z",
            "text": "I completely understand how frustrating that must be! I'm here to help you get this resolved right away. Let me assist you with a manual password reset - please DM me your email address so I can verify your account."
        },
        {
            "tweet_id": 1003,
            "author_id": "customer_1",
            "role": "Customer",
            "inbound": True, 
            "created_at": "2024-01-01T10:03:00Z",
            "text": "Thank you! Just sent you my email via DM. I really appreciate your quick response!"
        },
        {
            "tweet_id": 1004,
            "author_id": "agent_1",
            "role": "Agent",
            "inbound": False,
            "created_at": "2024-01-01T10:05:00Z", 
            "text": "Perfect! I've processed your password reset and sent you a new temporary password. You should receive it within 2 minutes. Is there anything else I can help you with today?"
        },
        {
            "tweet_id": 1005,
            "author_id": "customer_1",
            "role": "Customer",
            "inbound": True,
            "created_at": "2024-01-01T10:07:00Z",
            "text": "Got it and it works perfectly! You're amazing - thank you so much for the excellent help!"
        }
    ],
    "classification": {
        "categorization": "Password Reset",
        "intent": "Technical Support", 
        "topic": "Account Access",
        "sentiment": "Positive"
    }
}

def create_conversation_data():
    """Create ConversationData object from sample"""
    tweets = [Tweet(**tweet) for tweet in sample_conversation["tweets"]]
    classification = Classification(**sample_conversation["classification"])
    return ConversationData(tweets=tweets, classification=classification)

def test_improved_llm_prompt():
    """Test the improved LLM prompt to ensure proper JSON output"""
    logger.info("🚀 Starting Improved LLM Prompt Test")
    logger.info("=" * 80)
    logger.info("")
    
    try:
        # Create conversation data
        conversation_data = create_conversation_data()
        logger.info("✓ Created conversation data with improved prompt test")
        
        # Initialize LLM agent service
        logger.info("🔧 Initializing LLM Agent Service...")
        llm_service = LLMAgentPerformanceAnalysisService(model_name="claude-4", temperature=0.1)
        logger.info("✓ LLM Agent Service initialized")
        
        # Test the analyze_conversation_performance method
        logger.info("🧪 Testing analyze_conversation_performance with improved prompt...")
        performance_results = llm_service.analyze_conversation_performance(conversation_data)
        
        # Verify the results structure
        logger.info("🔍 Analyzing performance results structure...")
        
        required_fields = ["conversation_id", "analysis_timestamp", "performance_metrics", "agent_output"]
        missing_fields = [field for field in required_fields if field not in performance_results]
        
        if missing_fields:
            logger.error(f"❌ Missing required fields: {missing_fields}")
            return False
        
        logger.info("✅ All required top-level fields present")
        
        # Check performance metrics structure
        performance_metrics = performance_results.get("performance_metrics", {})
        categories = performance_metrics.get("categories", {})
        
        logger.info(f"📊 Found {len(categories)} categories in performance metrics")
        
        # Analyze each category for detailed reasoning
        total_kpis_checked = 0
        kpis_with_detailed_reasoning = 0
        kpis_with_evidence = 0
        kpis_with_json_parsing = 0
        
        for category_name, category_data in categories.items():
            logger.info(f"\n📂 Analyzing category: {category_name}")
            kpis = category_data.get("kpis", {})
            logger.info(f"   Found {len(kpis)} KPIs in {category_name}")
            
            for kpi_name, kpi_data in kpis.items():
                total_kpis_checked += 1
                
                # Check reasoning quality
                reasoning = kpi_data.get("reasoning", "")
                if reasoning and not reasoning.startswith("Comprehensive analysis for") and len(reasoning) > 100:
                    kpis_with_detailed_reasoning += 1
                    logger.info(f"     ✓ {kpi_name}: Detailed reasoning ({len(reasoning)} chars)")
                else:
                    logger.warning(f"     ⚠️ {kpi_name}: Generic reasoning ({len(reasoning)} chars)")
                
                # Check evidence
                evidence = kpi_data.get("evidence", [])
                if evidence and len(evidence) > 0:
                    kpis_with_evidence += 1
                    logger.info(f"     ✓ {kpi_name}: Has evidence ({len(evidence)} pieces)")
                    # Log first evidence piece
                    if evidence:
                        logger.info(f"       Evidence: {evidence[0][:80]}...")
                else:
                    logger.info(f"     ℹ️ {kpi_name}: No evidence")
        
        # Check agent output for JSON blocks (indicates LLM followed new prompt)
        agent_output = performance_results.get("agent_output", "")
        json_blocks = agent_output.count("```json")
        
        if json_blocks > 0:
            logger.info(f"✅ Found {json_blocks} JSON blocks in agent output - LLM followed new prompt format!")
            kpis_with_json_parsing = json_blocks
        else:
            logger.warning("⚠️ No JSON blocks found in agent output - LLM may not be following new prompt")
        
        # Summary statistics
        logger.info(f"\n📈 IMPROVED PROMPT TEST RESULTS:")
        logger.info(f"Total KPIs analyzed: {total_kpis_checked}")
        logger.info(f"KPIs with detailed reasoning: {kpis_with_detailed_reasoning}/{total_kpis_checked} ({(kpis_with_detailed_reasoning/total_kpis_checked*100) if total_kpis_checked > 0 else 0:.1f}%)")
        logger.info(f"KPIs with evidence: {kpis_with_evidence}/{total_kpis_checked} ({(kpis_with_evidence/total_kpis_checked*100) if total_kpis_checked > 0 else 0:.1f}%)")
        logger.info(f"JSON blocks from LLM: {kpis_with_json_parsing}")
        
        # Save detailed results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_file = f"improved_llm_prompt_test_results_{timestamp}.json"
        
        test_results = {
            "test_timestamp": datetime.now().isoformat(),
            "test_type": "Improved LLM Prompt Test",
            "statistics": {
                "total_kpis_analyzed": total_kpis_checked,
                "kpis_with_detailed_reasoning": kpis_with_detailed_reasoning,
                "kpis_with_evidence": kpis_with_evidence,
                "json_blocks_found": kpis_with_json_parsing,
                "detailed_reasoning_percentage": (kpis_with_detailed_reasoning/total_kpis_checked*100) if total_kpis_checked > 0 else 0,
                "evidence_percentage": (kpis_with_evidence/total_kpis_checked*100) if total_kpis_checked > 0 else 0
            },
            "performance_results": performance_results,
            "agent_output_sample": agent_output[:2000] if len(agent_output) > 2000 else agent_output
        }
        
        with open(results_file, 'w') as f:
            json.dump(test_results, f, indent=2, default=str)
        
        logger.info(f"📄 Detailed test results saved to: {results_file}")
        
        # Determine test success
        success_threshold = 50  # At least 50% should have detailed reasoning
        success = (kpis_with_detailed_reasoning/total_kpis_checked*100) >= success_threshold if total_kpis_checked > 0 else False
        
        if success:
            logger.info("✅ SUCCESS: Improved LLM prompt is working - detailed reasoning found!")
        else:
            logger.warning("⚠️ PARTIAL SUCCESS: Some improvement detected but still room for enhancement")
        
        return success
        
    except Exception as e:
        logger.error(f"❌ Error in improved LLM prompt test: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    logger.info("🧪 Starting Improved LLM Prompt Test")
    logger.info("=" * 80)
    
    success = test_improved_llm_prompt()
    
    logger.info("")
    logger.info("=" * 80)
    if success:
        logger.info("🏁 IMPROVED LLM PROMPT TEST COMPLETED SUCCESSFULLY!")
        logger.info("✅ LLM is now providing detailed reasoning instead of generic fallbacks")
    else:
        logger.info("🏁 IMPROVED LLM PROMPT TEST COMPLETED WITH WARNINGS")
        logger.info("⚠️ Further prompt improvements may be needed")
    logger.info("=" * 80)
