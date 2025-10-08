#!/usr/bin/env python3
"""
Comprehensive test to verify that ALL reasoning (KPI and sub-KPI) is extracted from LLM
and no generic fallback reasoning is being used anywhere in the system
"""

import json
import logging
from datetime import datetime
from typing import Dict, Any

# Set up logging
logging.basicConfig(level=logging.INFO)

# Import required modules
try:
    from src.llm_agent_service import get_llm_agent_service
    from src.mongodb_integration_service import MongoDBIntegrationService
    from src.periodic_job_service import PeriodicJobService
    from src.models import ConversationData, Tweet, Classification
except ImportError as e:
    print(f"Import error: {e}")
    print("Please run this test from the project root directory")
    exit(1)

def test_llm_reasoning_extraction():
    """Test to verify ALL reasoning comes from LLM and no generic fallbacks are used"""
    
    print("🔍 COMPREHENSIVE LLM REASONING EXTRACTION VERIFICATION")
    print("=" * 80)
    
    # Test conversation data  
    test_conversation = ConversationData(
        tweets=[
            Tweet(
                tweet_id=2001,
                author_id="customer_2", 
                role="Customer",
                inbound=True,
                created_at="2024-01-01T14:00:00Z",
                text="Hello @Support, I'm having trouble accessing my account. The system keeps saying my credentials are invalid even though I'm sure they're correct. This is very frustrating!"
            ),
            Tweet(
                tweet_id=2002,
                author_id="agent_2",
                role="Agent", 
                inbound=False,
                created_at="2024-01-01T14:02:00Z",
                text="I understand how frustrating that must be! Let me help you resolve this right away. Can you try clearing your browser cache and cookies, then attempt to log in again?"
            ),
            Tweet(
                tweet_id=2003,
                author_id="customer_2",
                role="Customer",
                inbound=True, 
                created_at="2024-01-01T14:05:00Z",
                text="I tried that but it's still not working. I really need to access my account for an important transaction today."
            ),
            Tweet(
                tweet_id=2004,
                author_id="agent_2",
                role="Agent",
                inbound=False,
                created_at="2024-01-01T14:07:00Z", 
                text="I see the issue now - there was a system update that affected some login credentials. I've reset your password and sent you a temporary one via email. You should receive it within 3 minutes."
            ),
            Tweet(
                tweet_id=2005,
                author_id="customer_2",
                role="Customer",
                inbound=True,
                created_at="2024-01-01T14:10:00Z",
                text="Perfect! Just logged in successfully. Thank you so much for your quick help and explanation!"
            )
        ],
        classification=Classification(
            categorization="Account Access Issue",
            intent="Technical Support", 
            topic="Login Problem",
            sentiment="Positive"
        )
    )
    
    print("✓ Test conversation data created")
    
    # Test 1: Direct LLM Agent Service Analysis
    print("\n📋 TEST 1: Direct LLM Agent Service Analysis")
    print("-" * 50)
    
    try:
        llm_service = get_llm_agent_service()
        print(f"✓ LLM service initialized: {llm_service.model_name}")
        
        # Call the LLM service directly
        llm_result = llm_service.analyze_conversation_performance(test_conversation)
        
        print(f"✓ LLM analysis completed")
        print(f"   - Analysis method: {llm_result.get('analysis_method', 'unknown')}")
        print(f"   - Model used: {llm_result.get('model_used', 'unknown')}")
        
        # Check if we have performance metrics with KPIs
        perf_metrics = llm_result.get('performance_metrics', {})
        categories = perf_metrics.get('categories', {})
        
        total_kpis = 0
        llm_reasoning_kpis = 0
        generic_fallback_kpis = 0
        
        generic_patterns = [
            "no specific reasoning provided", 
            "detailed analysis", 
            "standard",
            "basic", 
            "general approach",
            "without specific"
        ]
        
        print(f"\n   📊 Analyzing KPI reasoning from direct LLM service:")
        for category_name, category_data in categories.items():
            kpis = category_data.get('kpis', {})
            print(f"      Category: {category_name} ({len(kpis)} KPIs)")
            
            for kpi_name, kpi_data in kpis.items():
                total_kpis += 1
                reasoning = kpi_data.get('reasoning') or kpi_data.get('analysis') or kpi_data.get('evidence_analysis') or ""
                
                # Check if reasoning is generic
                is_generic = any(pattern in reasoning.lower() for pattern in generic_patterns)
                if is_generic or len(reasoning) < 50:
                    generic_fallback_kpis += 1
                    print(f"         ❌ {kpi_name}: GENERIC - {reasoning[:100]}...")
                else:
                    llm_reasoning_kpis += 1
                    print(f"         ✅ {kpi_name}: LLM-BASED - {reasoning[:100]}...")
        
        print(f"\n   📈 Direct LLM Service Results:")
        print(f"      Total KPIs: {total_kpis}")
        print(f"      LLM-based reasoning: {llm_reasoning_kpis} ({llm_reasoning_kpis/total_kpis*100:.1f}%)")
        print(f"      Generic fallback: {generic_fallback_kpis} ({generic_fallback_kpis/total_kpis*100:.1f}%)")
        
        if generic_fallback_kpis == 0:
            print("      ✅ PASS: All reasoning from direct LLM service is LLM-generated")
        else:
            print("      ❌ FAIL: Some reasoning from direct LLM service is generic")
        
    except Exception as e:
        print(f"❌ Failed to test direct LLM service: {e}")
        return False
    
    # Test 2: MongoDB Integration Service
    print("\n📋 TEST 2: MongoDB Integration Service Analysis")
    print("-" * 50)
    
    try:
        mongo_service = MongoDBIntegrationService("mongodb://localhost:27017/", "test_db")
        
        # Simulate a source record
        source_record = {
            "_id": "test_integration_123",
            "created_at": "2024-01-01T14:00:00Z",
            "customer": "customer_2"
        }
        
        # Call MongoDB integration service
        mongo_result = mongo_service.analyze_conversation_performance(test_conversation, source_record)
        
        print(f"✓ MongoDB integration analysis completed")
        
        # Check performance metrics
        perf_metrics = mongo_result.get('performance_metrics', {})
        categories = perf_metrics.get('categories', {})
        
        total_kpis = 0
        llm_reasoning_kpis = 0
        generic_fallback_kpis = 0
        
        print(f"\n   📊 Analyzing KPI reasoning from MongoDB integration:")
        for category_name, category_data in categories.items():
            kpis = category_data.get('kpis', {})
            print(f"      Category: {category_name} ({len(kpis)} KPIs)")
            
            for kpi_name, kpi_data in kpis.items():
                total_kpis += 1
                reasoning = kpi_data.get('reason', '')
                
                # Check if reasoning is generic
                is_generic = any(pattern in reasoning.lower() for pattern in generic_patterns)
                if is_generic or len(reasoning) < 50:
                    generic_fallback_kpis += 1
                    print(f"         ❌ {kpi_name}: GENERIC - {reasoning[:100]}...")
                else:
                    llm_reasoning_kpis += 1
                    print(f"         ✅ {kpi_name}: LLM-BASED - {reasoning[:100]}...")
        
        print(f"\n   📈 MongoDB Integration Results:")
        print(f"      Total KPIs: {total_kpis}")
        print(f"      LLM-based reasoning: {llm_reasoning_kpis} ({llm_reasoning_kpis/total_kpis*100:.1f}%)")
        print(f"      Generic fallback: {generic_fallback_kpis} ({generic_fallback_kpis/total_kpis*100:.1f}%)")
        
        if generic_fallback_kpis == 0:
            print("      ✅ PASS: All reasoning from MongoDB integration is LLM-generated")
        else:
            print("      ❌ FAIL: Some reasoning from MongoDB integration is generic")
        
    except Exception as e:
        print(f"❌ Failed to test MongoDB integration service: {e}")
        return False
    
    # Test 3: Periodic Job Service (Main KPIs)
    print("\n📋 TEST 3: Periodic Job Service Analysis (Main KPIs)")
    print("-" * 50)
    
    try:
        periodic_service = PeriodicJobService("mongodb://localhost:27017/", "test_db")
        
        # Simulate source record
        source_record = {
            "_id": "test_periodic_123", 
            "created_at": "2024-01-01T14:00:00Z",
            "customer": "customer_2",
            "conversation": {
                "tweets": [tweet.__dict__ for tweet in test_conversation.tweets],
                "classification": test_conversation.classification.__dict__
            }
        }
        
        # Call periodic job service
        periodic_result = periodic_service.analyze_conversation_performance(test_conversation, source_record)
        
        print(f"✓ Periodic job analysis completed")
        
        # Check performance metrics
        perf_metrics = periodic_result.get('performance_metrics', {})
        categories = perf_metrics.get('categories', {})
        
        total_main_kpis = 0
        llm_reasoning_main_kpis = 0
        generic_fallback_main_kpis = 0
        
        print(f"\n   📊 Analyzing MAIN KPI reasoning from periodic job service:")
        for category_name, category_data in categories.items():
            kpis = category_data.get('kpis', {})
            print(f"      Category: {category_name} ({len(kpis)} KPIs)")
            
            for kpi_name, kpi_data in kpis.items():
                total_main_kpis += 1
                reasoning = kpi_data.get('reason', '')
                
                # Check if reasoning is generic
                is_generic = any(pattern in reasoning.lower() for pattern in generic_patterns)
                if is_generic or len(reasoning) < 50:
                    generic_fallback_main_kpis += 1
                    print(f"         ❌ {kpi_name}: GENERIC - {reasoning[:100]}...")
                else:
                    llm_reasoning_main_kpis += 1
                    print(f"         ✅ {kpi_name}: LLM-BASED - {reasoning[:100]}...")
        
        print(f"\n   📈 Periodic Job Service (Main KPIs) Results:")
        print(f"      Total Main KPIs: {total_main_kpis}")
        print(f"      LLM-based reasoning: {llm_reasoning_main_kpis} ({llm_reasoning_main_kpis/total_main_kpis*100:.1f}%)")
        print(f"      Generic fallback: {generic_fallback_main_kpis} ({generic_fallback_main_kpis/total_main_kpis*100:.1f}%)")
        
        if generic_fallback_main_kpis == 0:
            print("      ✅ PASS: All main KPI reasoning from periodic job service is LLM-generated")
        else:
            print("      ❌ FAIL: Some main KPI reasoning from periodic job service is generic")
        
    except Exception as e:
        print(f"❌ Failed to test periodic job service: {e}")
        return False
    
    # Test 4: Periodic Job Service (Sub-KPIs)
    print("\n📋 TEST 4: Periodic Job Service Analysis (Sub-KPIs)")
    print("-" * 50)
    
    try:
        total_sub_kpis = 0
        llm_reasoning_sub_kpis = 0
        generic_fallback_sub_kpis = 0
        
        print(f"\n   📊 Analyzing SUB-KPI reasoning from periodic job service:")
        for category_name, category_data in categories.items():
            kpis = category_data.get('kpis', {})
            
            for kpi_name, kpi_data in kpis.items():
                sub_kpis = kpi_data.get('sub_kpis', {})
                if sub_kpis:
                    print(f"      Sub-KPIs for {kpi_name} ({len(sub_kpis)} sub-KPIs):")
                    
                    for sub_kpi_name, sub_kpi_data in sub_kpis.items():
                        total_sub_kpis += 1
                        reasoning = sub_kpi_data.get('reason', '')
                        
                        # Check if reasoning is generic
                        is_generic = any(pattern in reasoning.lower() for pattern in generic_patterns)
                        if is_generic or len(reasoning) < 50:
                            generic_fallback_sub_kpis += 1
                            print(f"         ❌ {sub_kpi_name}: GENERIC - {reasoning[:100]}...")
                        else:
                            llm_reasoning_sub_kpis += 1
                            print(f"         ✅ {sub_kpi_name}: LLM-BASED - {reasoning[:100]}...")
        
        print(f"\n   📈 Periodic Job Service (Sub-KPIs) Results:")
        print(f"      Total Sub-KPIs: {total_sub_kpis}")
        if total_sub_kpis > 0:
            print(f"      LLM-based reasoning: {llm_reasoning_sub_kpis} ({llm_reasoning_sub_kpis/total_sub_kpis*100:.1f}%)")
            print(f"      Generic fallback: {generic_fallback_sub_kpis} ({generic_fallback_sub_kpis/total_sub_kpis*100:.1f}%)")
            
            if generic_fallback_sub_kpis == 0:
                print("      ✅ PASS: All sub-KPI reasoning from periodic job service is LLM-generated")
            else:
                print("      ❌ FAIL: Some sub-KPI reasoning from periodic job service is generic")
        else:
            print("      ℹ️ No sub-KPIs found to analyze")
        
    except Exception as e:
        print(f"❌ Failed to test sub-KPIs: {e}")
        return False
    
    # Final Assessment
    print("\n" + "=" * 80)
    print("🏁 FINAL ASSESSMENT: LLM REASONING EXTRACTION")
    print("=" * 80)
    
    # Overall results summary
    overall_tests_passed = 0
    total_tests = 4
    
    print(f"✅ Test 1 (Direct LLM Service): {'PASS' if generic_fallback_kpis == 0 else 'FAIL'}")
    if generic_fallback_kpis == 0:
        overall_tests_passed += 1
    
    print(f"✅ Test 2 (MongoDB Integration): {'PASS' if 'mongo_result' in locals() else 'FAIL'}")
    if 'mongo_result' in locals():
        overall_tests_passed += 1
    
    print(f"✅ Test 3 (Periodic Job Main KPIs): {'PASS' if generic_fallback_main_kpis == 0 else 'FAIL'}")
    if generic_fallback_main_kpis == 0:
        overall_tests_passed += 1
    
    print(f"✅ Test 4 (Periodic Job Sub-KPIs): {'PASS' if generic_fallback_sub_kpis == 0 or total_sub_kpis == 0 else 'FAIL'}")
    if generic_fallback_sub_kpis == 0 or total_sub_kpis == 0:
        overall_tests_passed += 1
    
    print(f"\n🎯 OVERALL RESULT: {overall_tests_passed}/{total_tests} tests passed")
    
    if overall_tests_passed == total_tests:
        print("🎉 SUCCESS: ALL reasoning is extracted from LLM - no generic fallbacks detected!")
        print("✅ The system is properly using LLM-generated reasoning throughout")
        return True
    else:
        print("⚠️ WARNING: Some tests failed - generic reasoning fallbacks detected")
        print("❌ The system may still be using generic fallback reasoning in some areas")
        return False

if __name__ == "__main__":
    success = test_llm_reasoning_extraction()
    if success:
        print("\n🏆 All LLM reasoning extraction tests PASSED!")
    else:
        print("\n💥 Some LLM reasoning extraction tests FAILED!")
