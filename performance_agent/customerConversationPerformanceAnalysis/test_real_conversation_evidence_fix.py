#!/usr/bin/env python3

"""
Test script to fix evidence extraction for real conversations from MongoDB
The issue is that even with actual conversation data, all KPIs show "No Evidence"
"""

import logging
import json
from datetime import datetime
from src.llm_agent_service import LLMAgentPerformanceAnalysisService
from src.models import ConversationData, Tweet, Classification

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def create_test_conversation_with_evidence():
    """Create a test conversation that should generate actual evidence"""
    tweets = [
        Tweet(
            tweet_id=1,
            author_id="customer123",
            role="Customer", 
            inbound=True,
            created_at="2024-01-15T10:00:00Z",
            text="Hi, I'm really frustrated! My account has been locked for hours and I can't access anything!"
        ),
        Tweet(
            tweet_id=2,
            author_id="support_agent",
            role="Agent",
            inbound=False, 
            created_at="2024-01-15T10:02:00Z",
            text="I'm so sorry to hear about your frustration. I completely understand how stressful this must be. Let me help you get this resolved right away."
        ),
        Tweet(
            tweet_id=3,
            author_id="customer123", 
            role="Customer",
            inbound=True,
            created_at="2024-01-15T10:03:00Z",
            text="Thank you for understanding! This has been really affecting my work."
        ),
        Tweet(
            tweet_id=4,
            author_id="support_agent",
            role="Agent", 
            inbound=False,
            created_at="2024-01-15T10:05:00Z",
            text="I appreciate your patience. To unlock your account, I need to verify your identity. Can you please provide your email address and I'll reset it immediately?"
        ),
        Tweet(
            tweet_id=5,
            author_id="customer123",
            role="Customer",
            inbound=True, 
            created_at="2024-01-15T10:06:00Z",
            text="Perfect! My email is john@company.com. Thank you so much for your quick help!"
        ),
        Tweet(
            tweet_id=6,
            author_id="support_agent",
            role="Agent",
            inbound=False,
            created_at="2024-01-15T10:08:00Z", 
            text="Great! I've unlocked your account and sent you a confirmation email. You should be able to access everything now. Is there anything else I can help you with?"
        ),
        Tweet(
            tweet_id=7,
            author_id="customer123",
            role="Customer", 
            inbound=True,
            created_at="2024-01-15T10:09:00Z",
            text="Amazing! It's working perfectly now. Thank you so much for your excellent help and understanding!"
        )
    ]
    
    classification = Classification(
        categorization="Technical Support",
        intent="Account Access Issue", 
        topic="Account Locked",
        sentiment="Initially Frustrated, Then Very Satisfied"
    )
    
    return ConversationData(
        conversation_id="test_evidence_conversation_001",
        tweets=tweets,
        classification=classification
    )

def test_evidence_extraction_debugging():
    """Test evidence extraction with debugging to see what's happening"""
    
    logger.info("="*80)
    logger.info("TESTING EVIDENCE EXTRACTION FOR REAL CONVERSATIONS")
    logger.info("="*80)
    
    # Create test conversation
    conversation_data = create_test_conversation_with_evidence()
    logger.info(f"Created test conversation with {len(conversation_data.tweets)} tweets")
    
    # Print conversation content
    logger.info("\nCONVERSATION CONTENT:")
    for tweet in conversation_data.tweets:
        logger.info(f"  {tweet.role}: \"{tweet.text}\"")
    
    # Initialize LLM service
    try:
        service = LLMAgentPerformanceAnalysisService()
        logger.info("✓ LLM Agent Service initialized successfully")
    except Exception as e:
        logger.error(f"✗ Failed to initialize LLM service: {e}")
        return
    
    # Test the main analysis method
    logger.info("\nTesting main analysis method...")
    try:
        result = service.analyze_conversation_performance(conversation_data)
        logger.info("✓ Analysis completed successfully")
        
        # Check if conversation data was stored
        if hasattr(service, '_current_conversation_data'):
            logger.info("✓ Conversation data was stored in service")
            stored_data = service._current_conversation_data
            logger.info(f"  - Stored tweets: {len(stored_data.get('tweets', []))}")
            logger.info(f"  - Classification: {stored_data.get('classification', {}).get('categorization', 'None')}")
        else:
            logger.error("✗ Conversation data was NOT stored in service")
        
        # Analyze the results
        performance_metrics = result.get('performance_metrics', {})
        categories = performance_metrics.get('categories', {})
        
        logger.info(f"\nRESULTS ANALYSIS:")
        logger.info(f"Categories found: {list(categories.keys())}")
        
        evidence_found_count = 0
        no_evidence_count = 0
        total_kpis = 0
        
        for category_name, category_data in categories.items():
            kpis = category_data.get('kpis', {})
            logger.info(f"\nCategory: {category_name}")
            logger.info(f"  KPIs: {len(kpis)}")
            
            for kpi_name, kpi_data in kpis.items():
                total_kpis += 1
                evidence = kpi_data.get('evidence', [])
                reasoning = kpi_data.get('reasoning', '')
                score = kpi_data.get('score', 0)
                
                if evidence and len(evidence) > 0:
                    evidence_found_count += 1
                    logger.info(f"  ✓ {kpi_name}: Evidence found ({len(evidence)} pieces) - Score: {score}")
                    for i, ev in enumerate(evidence[:2]):  # Show first 2 pieces
                        logger.info(f"    Evidence {i+1}: {ev[:100]}...")
                else:
                    no_evidence_count += 1
                    if "No Evidence" in reasoning:
                        logger.info(f"  ○ {kpi_name}: No Evidence (correct handling) - Score: {score}")
                    else:
                        logger.info(f"  ✗ {kpi_name}: No evidence but wrong reasoning - Score: {score}")
                        logger.info(f"    Reasoning: {reasoning}")
        
        logger.info(f"\nEVIDENCE EXTRACTION SUMMARY:")
        logger.info(f"  Total KPIs: {total_kpis}")
        logger.info(f"  KPIs with evidence: {evidence_found_count}")
        logger.info(f"  KPIs with no evidence: {no_evidence_count}")
        logger.info(f"  Evidence extraction rate: {(evidence_found_count/total_kpis)*100:.1f}%")
        
        # Save detailed results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"real_conversation_evidence_test_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump(result, f, indent=2, default=str)
        logger.info(f"  Results saved to: {filename}")
        
        # Test specific evidence extraction methods directly
        logger.info("\nTesting direct evidence extraction methods...")
        test_direct_evidence_extraction(service)
        
        return result
        
    except Exception as e:
        logger.error(f"✗ Analysis failed: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_direct_evidence_extraction(service):
    """Test the evidence extraction methods directly"""
    
    logger.info("Testing _extract_real_evidence_from_conversation directly...")
    
    # Test some specific KPIs
    test_kpis = [
        ("empathy_score", "empathy_communication"),
        ("resolution_completeness", "accuracy_compliance"), 
        ("sentiment_shift", "empathy_communication"),
        ("clarity_language", "empathy_communication")
    ]
    
    for kpi_name, category_name in test_kpis:
        try:
            evidence = service._extract_real_evidence_from_conversation(kpi_name, category_name)
            logger.info(f"  {kpi_name}: {len(evidence)} evidence pieces")
            for i, ev in enumerate(evidence):
                logger.info(f"    {i+1}: {ev}")
        except Exception as e:
            logger.error(f"  {kpi_name}: Error - {e}")

def run_comprehensive_evidence_test():
    """Run comprehensive test of evidence extraction"""
    
    logger.info("Starting comprehensive evidence extraction test...")
    
    result = test_evidence_extraction_debugging()
    
    if result:
        logger.info("\n" + "="*80)
        logger.info("TEST COMPLETED SUCCESSFULLY")
        logger.info("="*80)
        
        # Check if we need to fix the evidence extraction
        performance_metrics = result.get('performance_metrics', {})
        categories = performance_metrics.get('categories', {})
        
        evidence_kpis = 0
        no_evidence_kpis = 0
        
        for category_data in categories.values():
            for kpi_data in category_data.get('kpis', {}).values():
                evidence = kpi_data.get('evidence', [])
                if evidence and len(evidence) > 0:
                    evidence_kpis += 1
                else:
                    no_evidence_kpis += 1
        
        total_kpis = evidence_kpis + no_evidence_kpis
        evidence_rate = (evidence_kpis / total_kpis) * 100 if total_kpis > 0 else 0
        
        logger.info(f"Final Evidence Extraction Rate: {evidence_rate:.1f}%")
        
        if evidence_rate < 50:
            logger.warning("⚠️  Evidence extraction rate is too low - needs improvement")
            logger.info("The issue is likely in how conversation data is passed to evidence extraction methods")
        else:
            logger.info("✅ Evidence extraction is working well")
    else:
        logger.error("Test failed - check the error messages above")

if __name__ == "__main__":
    run_comprehensive_evidence_test()
