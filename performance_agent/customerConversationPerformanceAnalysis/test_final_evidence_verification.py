#!/usr/bin/env python3

"""
Final test to verify evidence extraction works properly for MongoDB conversations
This addresses the user's feedback that all KPIs still show "No Evidence"
"""

import logging
import json
from datetime import datetime
from src.llm_agent_service import LLMAgentPerformanceAnalysisService
from src.models import ConversationData, Tweet, Classification

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def create_rich_test_conversation():
    """Create a conversation with clear evidence for multiple KPIs"""
    
    tweets = [
        Tweet(
            tweet_id=1,
            author_id="customer_001",
            role="Customer", 
            inbound=True,
            created_at="2024-01-15T10:00:00Z",
            text="Hi, I'm extremely frustrated! My account has been locked for 3 hours and I can't access my important documents. This is affecting my work productivity!"
        ),
        Tweet(
            tweet_id=2,
            author_id="support_agent_001",
            role="Agent",
            inbound=False, 
            created_at="2024-01-15T10:02:00Z",
            text="I'm truly sorry to hear about your frustration, and I completely understand how stressful this situation must be for you, especially when it's impacting your work. Let me help you resolve this right away."
        ),
        Tweet(
            tweet_id=3,
            author_id="customer_001", 
            role="Customer",
            inbound=True,
            created_at="2024-01-15T10:03:00Z",
            text="Thank you for understanding! I really appreciate your empathy. This has been incredibly stressful as I have a deadline today."
        ),
        Tweet(
            tweet_id=4,
            author_id="support_agent_001",
            role="Agent", 
            inbound=False,
            created_at="2024-01-15T10:05:00Z",
            text="I appreciate your patience. To unlock your account quickly, I need to verify your identity. Can you please provide your registered email address? I'll reset your access immediately once verified."
        ),
        Tweet(
            tweet_id=5,
            author_id="customer_001",
            role="Customer",
            inbound=True, 
            created_at="2024-01-15T10:06:00Z",
            text="Perfect! My email is john.smith@company.com. Thank you so much for being so helpful and quick to respond!"
        ),
        Tweet(
            tweet_id=6,
            author_id="support_agent_001",
            role="Agent",
            inbound=False,
            created_at="2024-01-15T10:08:00Z", 
            text="Excellent! I've successfully unlocked your account and sent you a confirmation email. You should be able to access everything now. Is there anything else I can help you with today?"
        ),
        Tweet(
            tweet_id=7,
            author_id="customer_001",
            role="Customer", 
            inbound=True,
            created_at="2024-01-15T10:09:00Z",
            text="Amazing! It's working perfectly now! Thank you so much for your excellent help, understanding, and quick resolution. You've saved my day!"
        )
    ]
    
    classification = Classification(
        categorization="Account Access Support",
        intent="Account Unlock Request", 
        topic="Account Locked - Identity Verification",
        sentiment="Frustrated initially, Very Satisfied at completion"
    )
    
    return ConversationData(
        conversation_id="evidence_test_conversation_final",
        tweets=tweets,
        classification=classification
    )

def test_comprehensive_evidence_extraction():
    """Test that evidence extraction works properly for all KPI types"""
    
    logger.info("="*80)
    logger.info("FINAL COMPREHENSIVE EVIDENCE EXTRACTION TEST")
    logger.info("="*80)
    
    # Create rich test conversation
    conversation_data = create_rich_test_conversation()
    logger.info(f"Created rich test conversation with {len(conversation_data.tweets)} tweets")
    
    # Print conversation content for analysis
    logger.info("\nCONVERSATION CONTENT FOR EVIDENCE ANALYSIS:")
    for i, tweet in enumerate(conversation_data.tweets, 1):
        logger.info(f"  {i}. {tweet.role}: \"{tweet.text}\"")
    
    # Initialize LLM service
    try:
        service = LLMAgentPerformanceAnalysisService()
        logger.info("✓ LLM Agent Service initialized successfully")
    except Exception as e:
        logger.error(f"✗ Failed to initialize LLM service: {e}")
        return False
    
    # Perform analysis
    logger.info("\nPerforming comprehensive analysis...")
    try:
        result = service.analyze_conversation_performance(conversation_data)
        logger.info("✓ Analysis completed successfully")
        
        # Analyze evidence extraction results
        success = analyze_evidence_results(result)
        
        # Save detailed results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"final_evidence_verification_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump(result, f, indent=2, default=str)
        logger.info(f"Results saved to: {filename}")
        
        return success
        
    except Exception as e:
        logger.error(f"✗ Analysis failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def analyze_evidence_results(result):
    """Analyze the results to check evidence extraction quality"""
    
    logger.info("\n" + "="*80)
    logger.info("EVIDENCE EXTRACTION ANALYSIS")
    logger.info("="*80)
    
    try:
        performance_metrics = result.get('performance_metrics', {})
        categories = performance_metrics.get('categories', {})
        
        if not categories:
            logger.error("✗ No categories found in results")
            return False
        
        total_kpis = 0
        kpis_with_evidence = 0
        kpis_with_no_evidence = 0
        kpis_with_realistic_scores = 0
        evidence_examples = []
        
        # Analyze each category and KPI
        for category_name, category_data in categories.items():
            logger.info(f"\n📊 CATEGORY: {category_name.upper()}")
            logger.info(f"   Category Score: {category_data.get('category_score', 'N/A')}")
            
            kpis = category_data.get('kpis', {})
            logger.info(f"   KPIs in category: {len(kpis)}")
            
            for kpi_name, kpi_data in kpis.items():
                total_kpis += 1
                score = kpi_data.get('score', 0)
                reasoning = kpi_data.get('reasoning', '')
                evidence = kpi_data.get('evidence', [])
                
                # Analyze evidence quality
                if evidence and len(evidence) > 0:
                    kpis_with_evidence += 1
                    # Check if evidence is realistic (not generic)
                    has_real_evidence = any(
                        'Customer:' in ev or 'Agent:' in ev for ev in evidence
                    )
                    
                    if has_real_evidence:
                        logger.info(f"   ✅ {kpi_name}")
                        logger.info(f"      Score: {score}")
                        logger.info(f"      Evidence: {len(evidence)} pieces")
                        for i, ev in enumerate(evidence[:2], 1):
                            logger.info(f"        {i}. {ev[:80]}...")
                            evidence_examples.append(f"{kpi_name}: {ev[:100]}")
                    else:
                        logger.info(f"   ⚠️  {kpi_name}")
                        logger.info(f"      Score: {score} (has evidence but may be generic)")
                        logger.info(f"      Evidence: {evidence}")
                else:
                    kpis_with_no_evidence += 1
                    if "No Evidence" in reasoning:
                        logger.info(f"   ⭕ {kpi_name}")
                        logger.info(f"      Score: {score} (No Evidence - correct handling)")
                    else:
                        logger.info(f"   ❌ {kpi_name}")
                        logger.info(f"      Score: {score} (No evidence, incorrect reasoning)")
                        logger.info(f"      Reasoning: {reasoning}")
                
                # Check score realism (not all 10s)
                if 3.0 <= score <= 9.5:
                    kpis_with_realistic_scores += 1
        
        # Calculate success metrics
        evidence_rate = (kpis_with_evidence / total_kpis) * 100 if total_kpis > 0 else 0
        realistic_score_rate = (kpis_with_realistic_scores / total_kpis) * 100 if total_kpis > 0 else 0
        
        logger.info(f"\n📈 FINAL RESULTS SUMMARY:")
        logger.info(f"   Total KPIs analyzed: {total_kpis}")
        logger.info(f"   KPIs with evidence: {kpis_with_evidence} ({evidence_rate:.1f}%)")
        logger.info(f"   KPIs with no evidence: {kpis_with_no_evidence}")
        logger.info(f"   KPIs with realistic scores: {kpis_with_realistic_scores} ({realistic_score_rate:.1f}%)")
        
        # Show evidence examples
        if evidence_examples:
            logger.info(f"\n🔍 EVIDENCE EXAMPLES:")
            for example in evidence_examples[:5]:
                logger.info(f"   • {example}")
        
        # Determine success
        success_criteria = [
            evidence_rate >= 40,  # At least 40% of KPIs should have evidence
            realistic_score_rate >= 50,  # At least 50% should have realistic scores
            total_kpis >= 10  # Should analyze substantial number of KPIs
        ]
        
        success = all(success_criteria)
        
        if success:
            logger.info(f"\n✅ EVIDENCE EXTRACTION TEST: PASSED")
            logger.info(f"   - Evidence extraction rate: {evidence_rate:.1f}% (Target: ≥40%)")
            logger.info(f"   - Realistic scoring rate: {realistic_score_rate:.1f}% (Target: ≥50%)")
            logger.info(f"   - KPI coverage: {total_kpis} KPIs (Target: ≥10)")
        else:
            logger.info(f"\n❌ EVIDENCE EXTRACTION TEST: FAILED")
            logger.info(f"   - Evidence extraction rate: {evidence_rate:.1f}% (Target: ≥40%)")
            logger.info(f"   - Realistic scoring rate: {realistic_score_rate:.1f}% (Target: ≥50%)")
            logger.info(f"   - KPI coverage: {total_kpis} KPIs (Target: ≥10)")
        
        return success
        
    except Exception as e:
        logger.error(f"Error analyzing evidence results: {e}")
        return False

def run_final_verification():
    """Run the final evidence extraction verification"""
    
    logger.info("Starting final evidence extraction verification...")
    
    success = test_comprehensive_evidence_extraction()
    
    logger.info("\n" + "="*80)
    if success:
        logger.info("🎉 FINAL VERIFICATION: SUCCESS!")
        logger.info("Evidence extraction is working properly for MongoDB conversations")
        logger.info("The system should now show actual evidence instead of 'No Evidence' for relevant KPIs")
    else:
        logger.error("💥 FINAL VERIFICATION: FAILED!")
        logger.error("Evidence extraction needs further improvement")
        logger.error("Check the logs above for specific issues")
    logger.info("="*80)
    
    return success

if __name__ == "__main__":
    run_final_verification()
