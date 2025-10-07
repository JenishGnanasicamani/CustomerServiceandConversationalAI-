#!/usr/bin/env python3
"""
Test Evidence Attribute Implementation
Tests that evidence attribute is properly added to both KPIs and sub-KPIs with specific evidence per KPI
"""

import json
import logging
from datetime import datetime
from typing import Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    from src.llm_agent_service import get_llm_agent_service
    from src.models import ConversationData, Tweet, Classification
except ImportError as e:
    logger.error(f"Import error: {e}")
    logger.info("Please ensure you're running from the project root directory")
    exit(1)


def create_sample_conversation() -> ConversationData:
    """Create a sample conversation for testing evidence extraction"""
    
    tweets = [
        Tweet(
            tweet_id=1,
            author_id="customer_001",
            text="@TechSupportCorp Hi, I'm having trouble accessing my website. It keeps showing an error message when I try to log in. This is really frustrating!",
            role="Customer",
            inbound=True,
            created_at="2024-01-15T10:30:00Z"
        ),
        Tweet(
            tweet_id=2,
            author_id="techsupport_agent",
            text="@Customer Hi there! I understand how frustrating website access issues can be. I'm here to help you resolve this quickly. Can you please DM me your account details so I can look into this for you? 😊",
            role="Agent",
            inbound=False,
            created_at="2024-01-15T10:35:00Z"
        ),
        Tweet(
            tweet_id=3,
            author_id="customer_001",
            text="@TechSupportCorp Thank you so much for the quick response! I really appreciate your help. I'll send you a DM right now with my details.",
            role="Customer", 
            inbound=True,
            created_at="2024-01-15T10:37:00Z"
        ),
        Tweet(
            tweet_id=4,
            author_id="techsupport_agent",
            text="@Customer Perfect! I've received your DM and I can see the issue with your account. I'm working on unlocking your access right now. You should be able to log in within the next few minutes. Please let me know if you need any further assistance!",
            role="Agent",
            inbound=False,
            created_at="2024-01-15T10:45:00Z"
        ),
        Tweet(
            tweet_id=5,
            author_id="customer_001",
            text="@TechSupportCorp Amazing! It's working perfectly now. Thank you so much for your excellent help! You've made my day! 🙏",
            role="Customer",
            inbound=True,
            created_at="2024-01-15T10:50:00Z"
        )
    ]
    
    classification = Classification(
        categorization="Technical Support",
        intent="Account Access Issue",
        topic="Website Login Problem", 
        sentiment="Initially Frustrated, Then Satisfied"
    )
    
    return ConversationData(
        tweets=tweets,
        classification=classification
    )


def test_evidence_attribute_implementation():
    """Test that evidence attribute is properly implemented for both KPIs and sub-KPIs"""
    
    print("=" * 80)
    print("TESTING EVIDENCE ATTRIBUTE IMPLEMENTATION")
    print("=" * 80)
    
    try:
        # Create sample conversation
        conversation_data = create_sample_conversation()
        print(f"\n✓ Created sample conversation with {len(conversation_data.tweets)} tweets")
        
        # Get LLM agent service
        agent_service = get_llm_agent_service(model_name="claude-4", temperature=0.1)
        print("✓ Initialized LLM agent service")
        
        # Perform comprehensive analysis
        print("\n📊 Performing comprehensive performance analysis...")
        result = agent_service.analyze_conversation_performance(conversation_data)
        
        # Print basic result info
        print(f"✓ Analysis completed at: {result.get('analysis_timestamp', 'N/A')}")
        print(f"✓ Method: {result.get('analysis_method', 'N/A')}")
        
        # Check performance metrics structure
        performance_metrics = result.get('performance_metrics', {})
        if not performance_metrics:
            print("❌ ERROR: No performance_metrics found in result")
            return False
            
        categories = performance_metrics.get('categories', {})
        if not categories:
            print("❌ ERROR: No categories found in performance_metrics")
            return False
            
        print(f"✓ Found {len(categories)} categories in performance metrics")
        
        # Test evidence attribute implementation
        evidence_test_results = {
            'kpis_with_evidence': 0,
            'kpis_without_evidence': 0,
            'sub_kpis_with_evidence': 0,
            'sub_kpis_without_evidence': 0,
            'specific_evidence_found': 0,
            'generic_evidence_found': 0,
            'no_evidence_cases': 0
        }
        
        print("\n" + "=" * 60)
        print("EVIDENCE ATTRIBUTE ANALYSIS")
        print("=" * 60)
        
        for category_name, category_data in categories.items():
            print(f"\n📂 Category: {category_name}")
            print(f"   Category Score: {category_data.get('category_score', 'N/A')}")
            
            kpis = category_data.get('kpis', {})
            if not kpis:
                print("   ⚠️  No KPIs found in this category")
                continue
                
            for kpi_name, kpi_data in kpis.items():
                print(f"\n   📊 KPI: {kpi_name}")
                print(f"      Score: {kpi_data.get('score', 'N/A')}")
                print(f"      Reasoning: {kpi_data.get('reasoning', 'N/A')[:100]}...")
                
                # Check evidence attribute for KPI
                if 'evidence' in kpi_data:
                    evidence_test_results['kpis_with_evidence'] += 1
                    evidence = kpi_data.get('evidence', [])
                    
                    if not evidence:
                        evidence_test_results['no_evidence_cases'] += 1
                        print(f"      Evidence: [] (No Evidence case)")
                    else:
                        # Check if evidence is specific or generic
                        evidence_str = str(evidence)
                        if ("Evidence extracted from conversation supporting" in evidence_str and 
                            len(evidence) == 1):
                            evidence_test_results['generic_evidence_found'] += 1
                            print(f"      Evidence: [GENERIC] {evidence[0][:80]}...")
                        else:
                            evidence_test_results['specific_evidence_found'] += 1
                            print(f"      Evidence: [SPECIFIC] Found {len(evidence)} pieces:")
                            for i, ev in enumerate(evidence[:2]):  # Show first 2
                                print(f"        {i+1}. {ev[:80]}...")
                else:
                    evidence_test_results['kpis_without_evidence'] += 1
                    print(f"      ❌ Evidence: MISSING!")
                
                # Check sub-factors if they exist
                sub_factors = kpi_data.get('sub_factors', {})
                if sub_factors:
                    print(f"      📋 Sub-factors: {len(sub_factors)} found")
                    
                    for sub_factor_name, sub_factor_data in sub_factors.items():
                        print(f"         ├── {sub_factor_name}: Score {sub_factor_data.get('score', 'N/A')}")
                        
                        # Check evidence attribute for sub-factor
                        if 'evidence' in sub_factor_data:
                            evidence_test_results['sub_kpis_with_evidence'] += 1
                            sub_evidence = sub_factor_data.get('evidence', [])
                            
                            if not sub_evidence:
                                print(f"         │   Evidence: [] (No Evidence)")
                            else:
                                print(f"         │   Evidence: {len(sub_evidence)} pieces")
                                for ev in sub_evidence[:1]:  # Show first piece
                                    print(f"         │     - {ev[:60]}...")
                        else:
                            evidence_test_results['sub_kpis_without_evidence'] += 1
                            print(f"         │   ❌ Evidence: MISSING!")
        
        # Print evidence test summary
        print("\n" + "=" * 60)
        print("EVIDENCE ATTRIBUTE TEST SUMMARY")
        print("=" * 60)
        
        total_kpis = evidence_test_results['kpis_with_evidence'] + evidence_test_results['kpis_without_evidence']
        total_sub_kpis = evidence_test_results['sub_kpis_with_evidence'] + evidence_test_results['sub_kpis_without_evidence']
        
        print(f"📊 KPIs:")
        print(f"   ✅ With evidence attribute: {evidence_test_results['kpis_with_evidence']}/{total_kpis}")
        print(f"   ❌ Without evidence attribute: {evidence_test_results['kpis_without_evidence']}/{total_kpis}")
        
        print(f"\n📊 Sub-KPIs:")
        print(f"   ✅ With evidence attribute: {evidence_test_results['sub_kpis_with_evidence']}/{total_sub_kpis}")
        print(f"   ❌ Without evidence attribute: {evidence_test_results['sub_kpis_without_evidence']}/{total_sub_kpis}")
        
        print(f"\n📋 Evidence Quality:")
        print(f"   🎯 Specific evidence: {evidence_test_results['specific_evidence_found']}")
        print(f"   📝 Generic evidence: {evidence_test_results['generic_evidence_found']}")
        print(f"   🚫 No evidence cases: {evidence_test_results['no_evidence_cases']}")
        
        # Determine test results
        kpi_evidence_success = evidence_test_results['kpis_without_evidence'] == 0
        sub_kpi_evidence_success = evidence_test_results['sub_kpis_without_evidence'] == 0
        evidence_quality_success = evidence_test_results['specific_evidence_found'] > evidence_test_results['generic_evidence_found']
        
        print(f"\n" + "=" * 60)
        print("FINAL TEST RESULTS")
        print("=" * 60)
        
        print(f"✅ KPI Evidence Attribute: {'PASS' if kpi_evidence_success else 'FAIL'}")
        print(f"✅ Sub-KPI Evidence Attribute: {'PASS' if sub_kpi_evidence_success else 'FAIL'}")
        print(f"✅ Evidence Quality (Specific vs Generic): {'PASS' if evidence_quality_success else 'FAIL'}")
        
        overall_success = kpi_evidence_success and sub_kpi_evidence_success and evidence_quality_success
        print(f"\n🏆 OVERALL TEST: {'PASS' if overall_success else 'FAIL'}")
        
        if overall_success:
            print("✅ Evidence attribute implementation is working correctly!")
            print("✅ Both KPIs and sub-KPIs have evidence attributes")
            print("✅ Evidence is specific per KPI rather than generic")
        else:
            print("❌ Evidence attribute implementation needs fixes:")
            if not kpi_evidence_success:
                print("   - Some KPIs are missing evidence attribute")
            if not sub_kpi_evidence_success:
                print("   - Some sub-KPIs are missing evidence attribute")
            if not evidence_quality_success:
                print("   - Evidence is too generic, needs to be specific per KPI")
        
        # Save sample result for inspection
        output_file = "evidence_implementation_test_results.json"
        with open(output_file, 'w') as f:
            json.dump(result, f, indent=2, default=str)
        print(f"\n💾 Full results saved to: {output_file}")
        
        return overall_success
        
    except Exception as e:
        print(f"❌ ERROR during testing: {e}")
        logger.exception("Full error details:")
        return False


if __name__ == "__main__":
    print("Starting Evidence Attribute Implementation Test...")
    success = test_evidence_attribute_implementation()
    
    if success:
        print("\n🎉 Test completed successfully!")
        exit(0)
    else:
        print("\n💥 Test failed - see details above")
        exit(1)
