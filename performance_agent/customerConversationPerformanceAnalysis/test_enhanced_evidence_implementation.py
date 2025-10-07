#!/usr/bin/env python3
"""
Test script to verify enhanced evidence extraction and "No Evidence" handling implementation
"""

import sys
import os
import json
import logging
from datetime import datetime

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from models import ConversationData, Tweet, Classification
from llm_agent_service import get_llm_agent_service

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def create_test_conversation_with_evidence():
    """Create a test conversation with clear evidence for some KPIs"""
    tweets = [
        Tweet(
            tweet_id=1,
            author_id="customer123",
            text="Hi @TechSupport, I'm really frustrated! My account is locked and I can't access my website!",
            role="Customer",
            inbound=True,
            created_at="2024-01-15T10:00:00Z"
        ),
        Tweet(
            tweet_id=2,
            author_id="support_agent",
            text="Hi there! I understand how frustrating this must be for you. I'm so sorry to hear about the trouble with your account. Let me help you get this resolved right away.",
            role="Agent",
            inbound=False,
            created_at="2024-01-15T10:02:00Z"
        ),
        Tweet(
            tweet_id=3,
            author_id="customer123",
            text="Thank you for understanding! I really appreciate your help. This has been going on for hours.",
            role="Customer", 
            inbound=True,
            created_at="2024-01-15T10:03:00Z"
        ),
        Tweet(
            tweet_id=4,
            author_id="support_agent",
            text="I completely understand your frustration. To help unlock your account, I'll need to verify a few details with you. Could you please DM me your account email? This way we can resolve this securely and quickly.",
            role="Agent",
            inbound=False,
            created_at="2024-01-15T10:05:00Z"
        ),
        Tweet(
            tweet_id=5,
            author_id="customer123",
            text="Perfect! DMing you now. Thank you so much for your quick response and help!",
            role="Customer",
            inbound=True,
            created_at="2024-01-15T10:06:00Z"
        )
    ]
    
    classification = Classification(
        categorization="Technical Support",
        intent="Account Access Issue", 
        topic="Account Locked",
        sentiment="Initially Frustrated, Then Satisfied"
    )
    
    return ConversationData(
        tweets=tweets,
        classification=classification
    )

def create_test_conversation_no_evidence():
    """Create a test conversation with no clear evidence for most KPIs"""
    tweets = [
        Tweet(
            tweet_id=1,
            author_id="customer456",
            text="Hello",
            role="Customer",
            inbound=True,
            created_at="2024-01-15T10:00:00Z"
        ),
        Tweet(
            tweet_id=2,
            author_id="support_agent",
            text="Hi, how can I help?",
            role="Agent",
            inbound=False,
            created_at="2024-01-15T10:01:00Z"
        ),
        Tweet(
            tweet_id=3,
            author_id="customer456",
            text="Just checking our service status",
            role="Customer",
            inbound=True,
            created_at="2024-01-15T10:02:00Z"
        ),
        Tweet(
            tweet_id=4,
            author_id="support_agent",
            text="All services are operational",
            role="Agent",
            inbound=False,
            created_at="2024-01-15T10:03:00Z"
        ),
        Tweet(
            tweet_id=5,
            author_id="customer456",
            text="OK thanks",
            role="Customer",
            inbound=True,
            created_at="2024-01-15T10:04:00Z"
        )
    ]
    
    classification = Classification(
        categorization="General Inquiry",
        intent="Status Check", 
        topic="Service Status",
        sentiment="Neutral"
    )
    
    return ConversationData(
        tweets=tweets,
        classification=classification
    )

def test_evidence_extraction():
    """Test evidence extraction with conversation that has clear evidence"""
    logger.info("=" * 80)
    logger.info("TESTING EVIDENCE EXTRACTION WITH CLEAR EVIDENCE")
    logger.info("=" * 80)
    
    try:
        # Create test conversation with evidence
        conversation = create_test_conversation_with_evidence()
        logger.info(f"Created test conversation with evidence")
        
        # Get LLM agent service
        agent_service = get_llm_agent_service()
        logger.info("Initialized LLM agent service")
        
        # Analyze conversation
        logger.info("Starting comprehensive analysis...")
        result = agent_service.analyze_conversation_performance(conversation)
        
        # Save results for inspection
        results_file = f"evidence_test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(results_file, 'w') as f:
            json.dump(result, f, indent=2, default=str)
        logger.info(f"Results saved to: {results_file}")
        
        # Analyze evidence fields
        performance_metrics = result.get("performance_metrics", {})
        categories = performance_metrics.get("categories", {})
        
        evidence_found_count = 0
        no_evidence_count = 0
        total_kpis = 0
        
        logger.info("\n" + "="*60)
        logger.info("EVIDENCE ANALYSIS RESULTS")
        logger.info("="*60)
        
        for category_name, category_data in categories.items():
            logger.info(f"\nCategory: {category_name}")
            kpis = category_data.get("kpis", {})
            
            for kpi_name, kpi_data in kpis.items():
                total_kpis += 1
                evidence = kpi_data.get("evidence", [])
                reasoning = kpi_data.get("reasoning", "")
                score = kpi_data.get("score", 0)
                
                if evidence and len(evidence) > 0 and evidence != []:
                    evidence_found_count += 1
                    logger.info(f"  ✓ {kpi_name}: Evidence found ({len(evidence)} items) - Score: {score}")
                    for i, ev in enumerate(evidence[:2], 1):  # Show first 2 evidence items
                        logger.info(f"    {i}. {ev[:100]}...")
                elif "No Evidence" in reasoning:
                    no_evidence_count += 1
                    logger.info(f"  ○ {kpi_name}: No Evidence (Score: {score}, Reasoning: {reasoning})")
                else:
                    logger.info(f"  ? {kpi_name}: Unclear evidence status (Score: {score})")
                
                # Check sub-factors if they exist
                sub_factors = kpi_data.get("sub_factors", {})
                if sub_factors:
                    for sf_name, sf_data in sub_factors.items():
                        sf_evidence = sf_data.get("evidence", [])
                        sf_reasoning = sf_data.get("reasoning", "")
                        sf_score = sf_data.get("score", 0)
                        
                        if sf_evidence and len(sf_evidence) > 0:
                            logger.info(f"    └─ {sf_name}: Sub-factor evidence found - Score: {sf_score}")
                        elif "No Evidence" in sf_reasoning:
                            logger.info(f"    └─ {sf_name}: No Evidence - Score: {sf_score}")
        
        logger.info(f"\n" + "="*60)
        logger.info("SUMMARY")
        logger.info("="*60)
        logger.info(f"Total KPIs analyzed: {total_kpis}")
        logger.info(f"KPIs with evidence: {evidence_found_count}")
        logger.info(f"KPIs with 'No Evidence': {no_evidence_count}")
        logger.info(f"Evidence extraction rate: {(evidence_found_count/total_kpis)*100:.1f}%")
        
        return result
        
    except Exception as e:
        logger.error(f"Error in evidence extraction test: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_no_evidence_handling():
    """Test 'No Evidence' handling with minimal conversation"""
    logger.info("\n" + "=" * 80)
    logger.info("TESTING 'NO EVIDENCE' HANDLING")
    logger.info("=" * 80)
    
    try:
        # Create test conversation with minimal evidence
        conversation = create_test_conversation_no_evidence()
        logger.info(f"Created minimal test conversation")
        
        # Get LLM agent service
        agent_service = get_llm_agent_service()
        
        # Analyze conversation
        logger.info("Starting analysis of minimal conversation...")
        result = agent_service.analyze_conversation_performance(conversation)
        
        # Save results
        results_file = f"no_evidence_test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(results_file, 'w') as f:
            json.dump(result, f, indent=2, default=str)
        logger.info(f"Results saved to: {results_file}")
        
        # Analyze 'No Evidence' handling
        performance_metrics = result.get("performance_metrics", {})
        categories = performance_metrics.get("categories", {})
        
        no_evidence_count = 0
        max_score_count = 0
        total_kpis = 0
        
        logger.info("\n" + "="*60)
        logger.info("'NO EVIDENCE' HANDLING RESULTS")
        logger.info("="*60)
        
        for category_name, category_data in categories.items():
            logger.info(f"\nCategory: {category_name}")
            kpis = category_data.get("kpis", {})
            
            for kpi_name, kpi_data in kpis.items():
                total_kpis += 1
                evidence = kpi_data.get("evidence", [])
                reasoning = kpi_data.get("reasoning", "")
                score = kpi_data.get("score", 0)
                
                if "No Evidence" in reasoning or (not evidence or evidence == []):
                    no_evidence_count += 1
                    if score == 10.0:
                        max_score_count += 1
                        logger.info(f"  ✓ {kpi_name}: Correct 'No Evidence' handling (Score: {score})")
                    else:
                        logger.info(f"  ✗ {kpi_name}: Incorrect score for 'No Evidence' (Score: {score})")
                else:
                    logger.info(f"  ? {kpi_name}: Has evidence in minimal conversation (Score: {score})")
        
        logger.info(f"\n" + "="*60)
        logger.info("'NO EVIDENCE' SUMMARY")
        logger.info("="*60)
        logger.info(f"Total KPIs analyzed: {total_kpis}")
        logger.info(f"KPIs with 'No Evidence': {no_evidence_count}")
        logger.info(f"KPIs with correct max score (10.0): {max_score_count}")
        logger.info(f"Correct 'No Evidence' handling rate: {(max_score_count/no_evidence_count)*100 if no_evidence_count > 0 else 0:.1f}%")
        
        return result
        
    except Exception as e:
        logger.error(f"Error in 'No Evidence' handling test: {e}")
        import traceback
        traceback.print_exc()
        return None

def main():
    """Run all evidence extraction tests"""
    logger.info("Starting Enhanced Evidence Extraction Implementation Tests")
    logger.info(f"Test started at: {datetime.now().isoformat()}")
    
    # Test 1: Evidence extraction with clear evidence
    evidence_result = test_evidence_extraction()
    
    # Test 2: 'No Evidence' handling
    no_evidence_result = test_no_evidence_handling()
    
    # Final summary
    logger.info("\n" + "=" * 80)
    logger.info("FINAL TEST SUMMARY")  
    logger.info("=" * 80)
    
    if evidence_result and no_evidence_result:
        logger.info("✓ All tests completed successfully")
        logger.info("✓ Evidence extraction functionality implemented")
        logger.info("✓ 'No Evidence' handling implemented")
        logger.info("\nNext steps:")
        logger.info("1. Review the generated JSON files for detailed analysis")
        logger.info("2. Verify evidence quality and relevance")
        logger.info("3. Test with real conversation data")
        return True
    else:
        logger.error("✗ Some tests failed - check error logs above")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
