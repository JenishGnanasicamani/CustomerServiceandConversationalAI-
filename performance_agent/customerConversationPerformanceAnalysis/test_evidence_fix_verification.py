#!/usr/bin/env python3
"""
Test Evidence Fix Verification
Focused test to verify evidence attribute is properly added to ALL KPIs and sub-KPIs
Based on the MongoDB document structure provided by user
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
    exit(1)


def create_rich_conversation() -> ConversationData:
    """Create a rich conversation with plenty of evidence for KPIs"""
    
    tweets = [
        Tweet(
            tweet_id=1,
            author_id="customer_001",
            text="Hi @Support, I'm really frustrated! I can't access my account and I have an important meeting in 10 minutes. This is so stressful!",
            role="Customer",
            inbound=True,
            created_at="2024-01-15T10:30:00Z"
        ),
        Tweet(
            tweet_id=2,
            author_id="support_agent",
            text="Hi there! I completely understand how frustrating and stressful this must be, especially with your important meeting coming up. I'm here to help you get this resolved quickly. Can you please tell me what error message you're seeing when trying to log in?",
            role="Agent",
            inbound=False,
            created_at="2024-01-15T10:32:00Z"
        ),
        Tweet(
            tweet_id=3,
            author_id="customer_001",
            text="Thank you for understanding! The error says 'Account temporarily locked'. I tried entering my password a few times because I thought I mistyped it.",
            role="Customer", 
            inbound=True,
            created_at="2024-01-15T10:33:00Z"
        ),
        Tweet(
            tweet_id=4,
            author_id="support_agent",
            text="I see exactly what happened - no worries at all! Multiple password attempts triggered our security system. I can unlock your account right now. Please check your email in about 2 minutes for a password reset link, then you'll be all set for your meeting!",
            role="Agent",
            inbound=False,
            created_at="2024-01-15T10:35:00Z"
        ),
        Tweet(
            tweet_id=5,
            author_id="customer_001",
            text="Perfect! Got the email and I'm logged in now. Thank you so much for your quick help and understanding - you saved my meeting! Your service is excellent!",
            role="Customer",
            inbound=True,
            created_at="2024-01-15T10:37:00Z"
        )
    ]
    
    classification = Classification(
        categorization="Technical Support",
        intent="Account Access Issue",
        topic="Account Locked", 
        sentiment="Initially Frustrated, Then Very Satisfied"
    )
    
    return ConversationData(
        tweets=tweets,
        classification=classification
    )


def analyze_evidence_structure(result: Dict[str, Any]) -> Dict[str, Any]:
    """Analyze the evidence structure in the result"""
    
    analysis = {
        'kpis_checked': 0,
        'kpis_with_evidence': 0,
        'kpis_with_empty_evidence': 0,
        'kpis_with_actual_evidence': 0,
        'sub_kpis_checked': 0,
        'sub_kpis_with_evidence': 0,
        'sub_kpis_with_empty_evidence': 0,
        'sub_kpis_with_actual_evidence': 0,
        'missing_evidence_fields': [],
        'sample_evidence': []
    }
    
    # Navigate to performance metrics
    performance_metrics = result.get('performance_metrics', {})
    categories = performance_metrics.get('categories', {})
    
    for category_name, category_data in categories.items():
        kpis = category_data.get('kpis', {})
        
        for kpi_name, kpi_data in kpis.items():
            analysis['kpis_checked'] += 1
            
            # Check evidence field in main KPI
            if 'evidence' in kpi_data:
                analysis['kpis_with_evidence'] += 1
                evidence = kpi_data['evidence']
                
                if not evidence or (isinstance(evidence, list) and len(evidence) == 0):
                    analysis['kpis_with_empty_evidence'] += 1
                else:
                    analysis['kpis_with_actual_evidence'] += 1
                    # Sample some evidence
                    if len(analysis['sample_evidence']) < 3:
                        analysis['sample_evidence'].append({
                            'kpi': f"{category_name}/{kpi_name}",
                            'evidence': evidence[:2] if isinstance(evidence, list) else str(evidence)[:100]
                        })
            else:
                analysis['missing_evidence_fields'].append(f"KPI: {category_name}/{kpi_name}")
            
            # Check sub-KPIs
            sub_factors = kpi_data.get('sub_factors', {})
            for sub_factor_name, sub_factor_data in sub_factors.items():
                analysis['sub_kpis_checked'] += 1
                
                if 'evidence' in sub_factor_data:
                    analysis['sub_kpis_with_evidence'] += 1
                    sub_evidence = sub_factor_data['evidence']
                    
                    if not sub_evidence or (isinstance(sub_evidence, list) and len(sub_evidence) == 0):
                        analysis['sub_kpis_with_empty_evidence'] += 1
                    else:
                        analysis['sub_kpis_with_actual_evidence'] += 1
                else:
                    analysis['missing_evidence_fields'].append(f"Sub-KPI: {category_name}/{kpi_name}/{sub_factor_name}")
    
    return analysis


def test_evidence_fix():
    """Test that evidence attribute is properly implemented and populated"""
    
    print("=" * 80)
    print("EVIDENCE FIX VERIFICATION TEST")
    print("=" * 80)
    
    try:
        # Create rich conversation with plenty of evidence
        conversation_data = create_rich_conversation()
        print(f"\n✓ Created rich conversation with {len(conversation_data.tweets)} tweets")
        print("✓ Conversation includes:")
        print("  - Customer frustration and emotion")
        print("  - Agent empathy and understanding")
        print("  - Clear problem resolution")
        print("  - Positive sentiment shift")
        
        # Get agent service
        agent_service = get_llm_agent_service(model_name="claude-4", temperature=0.1)
        print("✓ Initialized LLM agent service")
        
        # Perform analysis
        print("\n📊 Performing comprehensive performance analysis...")
        result = agent_service.analyze_conversation_performance(conversation_data)
        
        # Analyze evidence structure
        evidence_analysis = analyze_evidence_structure(result)
        
        print("\n" + "=" * 60)
        print("EVIDENCE STRUCTURE ANALYSIS")
        print("=" * 60)
        
        print(f"📊 KPIs Analyzed:")
        print(f"   Total KPIs checked: {evidence_analysis['kpis_checked']}")
        print(f"   ✅ KPIs WITH evidence field: {evidence_analysis['kpis_with_evidence']}")
        print(f"   📝 KPIs with actual evidence: {evidence_analysis['kpis_with_actual_evidence']}")
        print(f"   🚫 KPIs with empty evidence: {evidence_analysis['kpis_with_empty_evidence']}")
        
        print(f"\n📊 Sub-KPIs Analyzed:")
        print(f"   Total sub-KPIs checked: {evidence_analysis['sub_kpis_checked']}")
        print(f"   ✅ Sub-KPIs WITH evidence field: {evidence_analysis['sub_kpis_with_evidence']}")
        print(f"   📝 Sub-KPIs with actual evidence: {evidence_analysis['sub_kpis_with_actual_evidence']}")
        print(f"   🚫 Sub-KPIs with empty evidence: {evidence_analysis['sub_kpis_with_empty_evidence']}")
        
        # Show missing evidence fields (the main issue)
        if evidence_analysis['missing_evidence_fields']:
            print(f"\n❌ MISSING EVIDENCE FIELDS ({len(evidence_analysis['missing_evidence_fields'])}):")
            for missing in evidence_analysis['missing_evidence_fields'][:10]:  # Show first 10
                print(f"   - {missing}")
            if len(evidence_analysis['missing_evidence_fields']) > 10:
                print(f"   ... and {len(evidence_analysis['missing_evidence_fields']) - 10} more")
        else:
            print(f"\n✅ ALL KPIs and sub-KPIs have evidence fields!")
        
        # Show sample evidence
        if evidence_analysis['sample_evidence']:
            print(f"\n📝 SAMPLE EVIDENCE FOUND:")
            for sample in evidence_analysis['sample_evidence']:
                print(f"   {sample['kpi']}:")
                if isinstance(sample['evidence'], list):
                    for ev in sample['evidence']:
                        print(f"     - {ev[:80]}...")
                else:
                    print(f"     - {sample['evidence']}")
        
        # Calculate success metrics
        kpi_evidence_coverage = (evidence_analysis['kpis_with_evidence'] / 
                               max(evidence_analysis['kpis_checked'], 1)) * 100
        sub_kpi_evidence_coverage = (evidence_analysis['sub_kpis_with_evidence'] / 
                                   max(evidence_analysis['sub_kpis_checked'], 1)) * 100
        
        actual_evidence_rate = ((evidence_analysis['kpis_with_actual_evidence'] + 
                               evidence_analysis['sub_kpis_with_actual_evidence']) /
                              max(evidence_analysis['kpis_checked'] + evidence_analysis['sub_kpis_checked'], 1)) * 100
        
        print("\n" + "=" * 60)
        print("FINAL TEST RESULTS")
        print("=" * 60)
        
        print(f"📊 Evidence Field Coverage:")
        print(f"   KPIs: {kpi_evidence_coverage:.1f}% ({evidence_analysis['kpis_with_evidence']}/{evidence_analysis['kpis_checked']})")
        print(f"   Sub-KPIs: {sub_kpi_evidence_coverage:.1f}% ({evidence_analysis['sub_kpis_with_evidence']}/{evidence_analysis['sub_kpis_checked']})")
        
        print(f"\n📝 Actual Evidence Rate: {actual_evidence_rate:.1f}%")
        
        # Determine pass/fail
        kpi_pass = kpi_evidence_coverage >= 100.0
        sub_kpi_pass = sub_kpi_evidence_coverage >= 100.0
        evidence_quality_pass = actual_evidence_rate > 10.0  # At least some evidence should be found
        
        print(f"\n✅ KPI Evidence Fields: {'PASS' if kpi_pass else 'FAIL'}")
        print(f"✅ Sub-KPI Evidence Fields: {'PASS' if sub_kpi_pass else 'FAIL'}")
        print(f"✅ Evidence Quality: {'PASS' if evidence_quality_pass else 'FAIL'}")
        
        overall_pass = kpi_pass and sub_kpi_pass
        print(f"\n🏆 OVERALL TEST: {'PASS' if overall_pass else 'FAIL'}")
        
        if overall_pass:
            print("✅ Evidence attribute implementation is working correctly!")
            print("✅ All KPIs and sub-KPIs have evidence fields")
            if evidence_quality_pass:
                print("✅ Evidence extraction is finding actual conversation content")
        else:
            print("❌ Evidence attribute implementation needs fixes:")
            if not kpi_pass:
                print("   - Some KPIs are missing evidence fields")
            if not sub_kpi_pass:
                print("   - Some sub-KPIs are missing evidence fields")
            if not evidence_quality_pass:
                print("   - Evidence extraction is not finding enough actual content")
        
        # Save detailed results
        output_file = "evidence_fix_verification_results.json"
        with open(output_file, 'w') as f:
            result_with_analysis = result.copy()
            result_with_analysis['evidence_analysis'] = evidence_analysis
            json.dump(result_with_analysis, f, indent=2, default=str)
        print(f"\n💾 Detailed results saved to: {output_file}")
        
        return overall_pass
        
    except Exception as e:
        print(f"❌ ERROR during testing: {e}")
        logger.exception("Full error details:")
        return False


if __name__ == "__main__":
    print("Starting Evidence Fix Verification Test...")
    success = test_evidence_fix()
    
    if success:
        print("\n🎉 Evidence fix verification completed successfully!")
        exit(0)
    else:
        print("\n💥 Evidence fix verification failed - see details above")
        exit(1)
