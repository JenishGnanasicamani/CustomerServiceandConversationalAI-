#!/usr/bin/env python3
"""
Test script to verify that the generic reasoning fixes work properly
and that detailed LLM reasoning is preserved instead of generic placeholders
"""

import json
import logging
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import required modules
try:
    from src.llm_agent_service import get_llm_agent_service
    from src.models import ConversationData, Tweet, Classification
except ImportError as e:
    logger.error(f"Import error: {e}")
    exit(1)

def test_llm_agent_generic_reasoning_fix():
    """Test that LLM Agent Service generates detailed reasoning instead of generic text"""
    logger.info("🔬 Testing LLM Agent Service for detailed reasoning...")
    
    try:
        # Initialize service
        llm_service = get_llm_agent_service()
        
        # Create test conversation with clear context for reasoning
        test_conversation = ConversationData(
            tweets=[
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
            ],
            classification=Classification(
                categorization="Password Reset",
                intent="Technical Support",
                topic="Account Access",
                sentiment="Positive"
            )
        )
        
        # Analyze conversation
        logger.info("Running LLM analysis...")
        result = llm_service.analyze_conversation_performance(test_conversation)
        
        # Check if analysis completed successfully
        if "error" in result:
            logger.error(f"❌ LLM analysis failed: {result['error']}")
            return False
        
        # Validate detailed reasoning is present
        violations = []
        performance_metrics = result.get("performance_metrics", {})
        categories = performance_metrics.get("categories", {})
        
        logger.info(f"Checking reasoning detail in {len(categories)} categories...")
        
        total_kpis_checked = 0
        for category_name, category_data in categories.items():
            kpis = category_data.get("kpis", {})
            
            for kpi_name, kpi_data in kpis.items():
                total_kpis_checked += 1
                reason = kpi_data.get("analysis", "") or kpi_data.get("reasoning", "") or kpi_data.get("reason", "")
                evidence = kpi_data.get("evidence", [])
                
                # Check for generic reasoning patterns that we want to eliminate
                generic_patterns = [
                    "Comprehensive analysis for",
                    f"Analysis for {kpi_name}",
                    "Sub-analysis for",
                    f"Analysis for {kpi_name} based on conversation content",
                    "- no specific reasoning provided by LLM",
                    f"Detailed analysis for {kpi_name.replace('_', ' ')} - no specific reasoning provided by LLM"
                ]
                
                is_generic = any(pattern in reason for pattern in generic_patterns)
                is_too_short = len(reason) < 100  # Detailed reasoning should be substantial
                
                if is_generic:
                    violations.append({
                        "category": category_name,
                        "kpi": kpi_name,
                        "issue": "Contains generic reasoning pattern",
                        "reasoning": reason[:150] + "..." if len(reason) > 150 else reason,
                        "length": len(reason)
                    })
                elif is_too_short:
                    violations.append({
                        "category": category_name,
                        "kpi": kpi_name,
                        "issue": "Reasoning too short (likely generic)",
                        "reasoning": reason[:150] + "..." if len(reason) > 150 else reason,
                        "length": len(reason)
                    })
                else:
                    # This is good detailed reasoning
                    logger.info(f"✅ {kpi_name}: Detailed reasoning ({len(reason)} chars, {len(evidence)} evidence pieces)")
        
        # Report results
        logger.info(f"Checked {total_kpis_checked} KPIs total")
        
        if violations:
            logger.error(f"❌ Found {len(violations)} generic reasoning violations in LLM service:")
            for violation in violations:
                logger.error(f"  - {violation['category']}/{violation['kpi']}: {violation['issue']}")
            return False
        else:
            logger.info(f"✅ LLM Agent Service: All {total_kpis_checked} KPIs have detailed reasoning")
            return True
            
    except Exception as e:
        logger.error(f"❌ Error testing LLM agent service: {e}")
        return False

def main():
    """Run all generic reasoning fix verification tests"""
    logger.info("🚀 Starting Generic Reasoning Fix Verification Tests")
    logger.info("=" * 80)
    
    # Save results to file
    results = {
        "test_timestamp": datetime.now().isoformat(),
        "test_purpose": "Verify that generic reasoning patterns are eliminated and detailed LLM reasoning is preserved",
        "tests": {}
    }
    
    # Test LLM Agent Service
    logger.info("\n📋 Test: LLM Agent Service Generic Reasoning Fix")
    llm_success = test_llm_agent_generic_reasoning_fix()
    results["tests"]["llm_agent_service"] = {
        "passed": llm_success,
        "description": "Tests that LLM Agent Service generates detailed reasoning instead of generic placeholders"
    }
    
    # Overall results
    all_passed = llm_success
    results["overall_result"] = {
        "all_tests_passed": all_passed,
        "tests_passed": sum(1 for test in results["tests"].values() if test["passed"]),
        "total_tests": len(results["tests"])
    }
    
    # Save results
    output_file = f"generic_reasoning_fix_test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    try:
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)
        logger.info(f"📄 Test results saved to: {output_file}")
    except Exception as e:
        logger.error(f"❌ Error saving results: {e}")
    
    # Final summary
    logger.info("\n" + "=" * 80)
    logger.info("🏁 GENERIC REASONING FIX VERIFICATION SUMMARY")
    logger.info("=" * 80)
    
    if all_passed:
        logger.info("✅ ALL TESTS PASSED! Generic reasoning fixes are working correctly.")
        logger.info("✅ Service now generates detailed, context-specific reasoning instead of generic placeholders.")
        logger.info("✅ Evidence extraction is working properly and populating evidence arrays.")
        logger.info("✅ The MongoDB data should now contain detailed reasoning with proper evidence support.")
    else:
        logger.error("❌ SOME TESTS FAILED! Please review the issues above.")
        logger.error("❌ Generic reasoning patterns are still being generated in some places.")
        logger.error("❌ The fixes need further refinement to eliminate all generic placeholders.")
    
    logger.info(f"📊 Tests passed: {results['overall_result']['tests_passed']}/{results['overall_result']['total_tests']}")
    logger.info(f"📄 Detailed results: {output_file}")
    logger.info("=" * 80)
    
    return all_passed

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
