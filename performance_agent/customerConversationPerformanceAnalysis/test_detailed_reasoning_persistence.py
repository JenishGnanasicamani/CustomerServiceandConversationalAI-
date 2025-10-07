#!/usr/bin/env python3
"""
Test script to verify that detailed LLM reasoning is properly persisted
instead of generic placeholder text like "Comprehensive analysis for..."
"""

import json
import logging
from datetime import datetime
from typing import Dict, Any

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import required modules
try:
    from src.llm_agent_service import get_llm_agent_service
    from src.periodic_job_service import PeriodicJobService
    from src.models import ConversationData, Tweet, Classification
except ImportError as e:
    logger.error(f"Import error: {e}")
    exit(1)

def test_llm_agent_detailed_reasoning():
    """Test LLM Agent Service for detailed reasoning instead of generic text"""
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
                    text="Hi @UberSupport, I'm really frustrated because I can't access my account. I've been locked out for 2 hours and have an important meeting to get to!"
                ),
                Tweet(
                    tweet_id=1002,
                    author_id="agent_1", 
                    role="Agent",
                    inbound=False,
                    created_at="2024-01-01T10:01:00Z",
                    text="Hi there! I understand how frustrating that must be, especially with your important meeting coming up. I'm delighted to help you get back into your account right away. Please DM me your email address so I can verify your identity and unlock your account immediately."
                ),
                Tweet(
                    tweet_id=1003,
                    author_id="customer_1",
                    role="Customer", 
                    inbound=True,
                    created_at="2024-01-01T10:05:00Z",
                    text="Perfect! Just sent you a DM with my email. Thank you so much for the quick help!"
                ),
                Tweet(
                    tweet_id=1004,
                    author_id="agent_1",
                    role="Agent",
                    inbound=False, 
                    created_at="2024-01-01T10:07:00Z",
                    text="Amazing! I've unlocked your account and reset your password. You should be able to access everything now. Is there anything else I can help you with today?"
                ),
                Tweet(
                    tweet_id=1005,
                    author_id="customer_1",
                    role="Customer",
                    inbound=True,
                    created_at="2024-01-01T10:08:00Z", 
                    text="It's working perfectly now! You're a lifesaver. Thank you for resolving this so quickly!"
                )
            ],
            classification=Classification(
                categorization="Account Access Issue",
                intent="Technical Support",
                topic="Account Unlock",
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
        categories = result.get("performance_metrics", {}).get("categories", {})
        
        logger.info(f"Checking reasoning detail in {len(categories)} categories...")
        
        for category_name, category_data in categories.items():
            kpis = category_data.get("kpis", {})
            
            for kpi_name, kpi_data in kpis.items():
                reason = kpi_data.get("reason", "") or kpi_data.get("reasoning", "") or kpi_data.get("analysis", "")
                
                # Check for generic reasoning patterns
                generic_patterns = [
                    "Comprehensive analysis for",
                    "Analysis for " + kpi_name,
                    "Sub-analysis for",
                    f"Analysis for {kpi_name} based on conversation content",
                    "- no specific reasoning provided by LLM"
                ]
                
                is_generic = any(pattern in reason for pattern in generic_patterns)
                is_too_short = len(reason) < 50  # Very short reasoning is likely generic
                
                if is_generic or is_too_short:
                    violations.append({
                        "category": category_name,
                        "kpi": kpi_name,
                        "issue": "Generic reasoning",
                        "reasoning": reason[:100] + "..." if len(reason) > 100 else reason,
                        "length": len(reason)
                    })
                else:
                    logger.info(f"✅ {kpi_name}: Detailed reasoning ({len(reason)} chars)")
                
                # Check sub-KPIs if they exist
                if "sub_kpis" in kpi_data:
                    for sub_kpi_name, sub_kpi_data in kpi_data["sub_kpis"].items():
                        sub_reason = sub_kpi_data.get("reason", "") or sub_kpi_data.get("reasoning", "")
                        
                        sub_generic_patterns = [
                            "Sub-factor analysis for",
                            f"Sub-analysis for {sub_kpi_name}",
                            "- no specific reasoning provided by LLM"
                        ]
                        
                        sub_is_generic = any(pattern in sub_reason for pattern in sub_generic_patterns)
                        
                        if sub_is_generic or len(sub_reason) < 30:
                            violations.append({
                                "category": category_name,
                                "kpi": kpi_name,
                                "sub_kpi": sub_kpi_name, 
                                "issue": "Generic sub-KPI reasoning",
                                "reasoning": sub_reason[:100] + "..." if len(sub_reason) > 100 else sub_reason,
                                "length": len(sub_reason)
                            })
        
        # Report results
        if violations:
            logger.error(f"❌ Found {len(violations)} generic reasoning violations in LLM service:")
            for violation in violations:
                logger.error(f"  - {violation['category']}/{violation['kpi']}: {violation['issue']}")
                logger.error(f"    Reasoning: {violation['reasoning']} (length: {violation['length']})")
            return False
        else:
            logger.info(f"✅ LLM Agent Service: All reasoning is detailed and specific")
            return True
            
    except Exception as e:
        logger.error(f"❌ Error testing LLM agent service: {e}")
        return False

def test_periodic_job_detailed_reasoning():
    """Test Periodic Job Service for detailed reasoning preservation"""
    logger.info("🔬 Testing Periodic Job Service for detailed reasoning...")
    
    try:
        # Create test record that looks like a sentiment analysis record
        test_record = {
            "_id": "test_id_12345",
            "conversation": {
                "tweets": [
                    {
                        "tweet_id": 2001,
                        "author_id": "customer_2",
                        "role": "Customer", 
                        "inbound": True,
                        "created_at": "2024-01-01T11:00:00Z",
                        "text": "@UberSupport I'm having trouble with my password reset. The email isn't coming through and I need to book a ride urgently!"
                    },
                    {
                        "tweet_id": 2002,
                        "author_id": "agent_2",
                        "role": "Agent",
                        "inbound": False,
                        "created_at": "2024-01-01T11:02:00Z", 
                        "text": "I understand how urgent this is for you! Let me help you right away. I can see the issue with the email delivery. Please DM me your registered email so I can manually send you a reset link and get you back on the road quickly."
                    },
                    {
                        "tweet_id": 2003,
                        "author_id": "customer_2",
                        "role": "Customer",
                        "inbound": True,
                        "created_at": "2024-01-01T11:05:00Z",
                        "text": "Perfect! Got the reset email and I'm back in my account. Thank you so much for the fast response!"
                    }
                ],
                "classification": {
                    "categorization": "Password Reset",
                    "intent": "Technical Support", 
                    "topic": "Account Access",
                    "sentiment": "Satisfied"
                }
            },
            "customer": "customer_2",
            "created_at": "2024-01-01T11:00:00Z"
        }
        
        # Initialize periodic job service with mock data
        periodic_service = PeriodicJobService("mongodb://localhost:27017/", "test_db")
        
        # Convert to conversation data
        conversation_data = periodic_service.convert_sentiment_to_conversation_data(test_record)
        if not conversation_data:
            logger.error("❌ Failed to convert test record to conversation data")
            return False
        
        # Analyze performance
        logger.info("Running periodic job analysis...")
        analysis_result = periodic_service.analyze_conversation_performance(conversation_data, test_record)
        
        if not analysis_result:
            logger.error("❌ Periodic job analysis failed")
            return False
        
        # Check the structured result from _build_performance_metrics
        performance_metrics = analysis_result.get("performance_metrics", {})
        categories = performance_metrics.get("categories", {})
        
        violations = []
        
        logger.info(f"Checking reasoning detail in {len(categories)} categories...")
        
        for category_name, category_data in categories.items():
            kpis = category_data.get("kpis", {})
            
            for kpi_name, kpi_data in kpis.items():
                reason = kpi_data.get("reason", "") or kpi_data.get("reasoning", "")
                
                # Check for the FIXED generic patterns we want to avoid
                problematic_patterns = [
                    "Detailed analysis for " + kpi_name.replace('_', ' ') + " - no specific reasoning provided by LLM",
                    "Comprehensive analysis for " + kpi_name,
                    f"Analysis for {kpi_name} based on conversation content"
                ]
                
                is_problematic = any(pattern in reason for pattern in problematic_patterns)
                
                if is_problematic:
                    violations.append({
                        "category": category_name,
                        "kpi": kpi_name,
                        "issue": "Generic fallback reasoning used",
                        "reasoning": reason[:150] + "..." if len(reason) > 150 else reason
                    })
                elif len(reason) > 50:  # Good detailed reasoning
                    logger.info(f"✅ {kpi_name}: Detailed reasoning preserved ({len(reason)} chars)")
                
                # Check sub-KPIs if they exist  
                if "sub_kpis" in kpi_data:
                    for sub_kpi_name, sub_kpi_data in kpi_data["sub_kpis"].items():
                        sub_reason = sub_kpi_data.get("reason", "") or sub_kpi_data.get("reasoning", "")
                        
                        sub_problematic_patterns = [
                            "Detailed sub-factor analysis for " + sub_kpi_name + " - no specific reasoning provided by LLM"
                        ]
                        
                        sub_is_problematic = any(pattern in sub_reason for pattern in sub_problematic_patterns)
                        
                        if sub_is_problematic:
                            violations.append({
                                "category": category_name,
                                "kpi": kpi_name,
                                "sub_kpi": sub_kpi_name,
                                "issue": "Generic sub-KPI fallback reasoning used", 
                                "reasoning": sub_reason[:150] + "..." if len(sub_reason) > 150 else sub_reason
                            })
        
        # Report results
        if violations:
            logger.error(f"❌ Found {len(violations)} generic reasoning violations in Periodic Job Service:")
            for violation in violations:
                if "sub_kpi" in violation:
                    logger.error(f"  - {violation['category']}/{violation['kpi']}/{violation['sub_kpi']}: {violation['issue']}")
                else:
                    logger.error(f"  - {violation['category']}/{violation['kpi']}: {violation['issue']}")
                logger.error(f"    Reasoning: {violation['reasoning']}")
            return False
        else:
            logger.info(f"✅ Periodic Job Service: All reasoning is detailed and specific")
            return True
            
    except Exception as e:
        logger.error(f"❌ Error testing periodic job service: {e}")
        return False

def main():
    """Run detailed reasoning persistence tests"""
    logger.info("🚀 Starting Detailed Reasoning Persistence Tests")
    logger.info("=" * 60)
    
    # Track results
    results = {
        "llm_agent_service": False,
        "periodic_job_service": False
    }
    
    # Test LLM Agent Service
    logger.info("\n📊 Testing LLM Agent Service...")
    results["llm_agent_service"] = test_llm_agent_detailed_reasoning()
    
    # Test Periodic Job Service
    logger.info("\n📊 Testing Periodic Job Service...")
    results["periodic_job_service"] = test_periodic_job_detailed_reasoning()
    
    # Summary
    logger.info("\n" + "=" * 60)
    logger.info("📋 DETAILED REASONING PERSISTENCE TEST RESULTS")
    logger.info("=" * 60)
    
    passed = 0
    total = len(results)
    
    for service, passed_test in results.items():
        status = "✅ PASS" if passed_test else "❌ FAIL"
        logger.info(f"{service}: {status}")
        if passed_test:
            passed += 1
    
    # Overall result
    overall_pass = passed == total
    overall_status = "✅ ALL TESTS PASSED" if overall_pass else f"❌ {total - passed}/{total} TESTS FAILED"
    
    logger.info("-" * 60)
    logger.info(f"Overall Result: {overall_status}")
    
    # Save results
    test_results = {
        "test_timestamp": datetime.now().isoformat(),
        "test_type": "detailed_reasoning_persistence",
        "results": results,
        "total_tests": total,
        "passed_tests": passed,
        "overall_pass": overall_pass,
        "summary": "Tests verify that detailed LLM reasoning is persisted instead of generic placeholder text"
    }
    
    with open("test_detailed_reasoning_persistence_results.json", "w") as f:
        json.dump(test_results, f, indent=2)
    
    logger.info(f"Test results saved to: test_detailed_reasoning_persistence_results.json")
    
    if overall_pass:
        logger.info("🎉 All detailed reasoning persistence tests passed!")
        return 0
    else:
        logger.error("💥 Some detailed reasoning persistence tests failed!")
        return 1

if __name__ == "__main__":
    exit(main())
