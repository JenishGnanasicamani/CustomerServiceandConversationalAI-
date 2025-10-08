#!/usr/bin/env python3
"""
Complete Fields Verification Test
Tests that normalized_score, confidence, and interpretation are included in final MongoDB output
"""

import json
import logging
from datetime import datetime
from typing import Dict, Any

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

try:
    from src.llm_agent_service import LLMAgentPerformanceAnalysisService
    from src.models import ConversationData, Tweet, Classification
except ImportError as e:
    logger.error(f"Import error: {e}")
    exit(1)

def create_test_conversation() -> ConversationData:
    """Create a test conversation with evidence for field verification"""
    
    tweets = [
        Tweet(
            tweet_id=1, 
            author_id="customer_001",
            role="Customer",
            inbound=True,
            created_at="2024-01-01T10:00:00Z",
            text="Hi, I'm extremely frustrated! My account has been locked for 3 hours and I can't access my important documents. This is affecting my work productivity!"
        ),
        Tweet(
            tweet_id=2, 
            author_id="agent_001",
            role="Agent",
            inbound=False,
            created_at="2024-01-01T10:01:00Z",
            text="I'm truly sorry to hear about your frustration, and I completely understand how stressful this situation must be for you, especially when it's impacting your work. Let me help you resolve this right away."
        ),
        Tweet(
            tweet_id=3, 
            author_id="customer_001",
            role="Customer",
            inbound=True,
            created_at="2024-01-01T10:02:00Z",
            text="Thank you for understanding! I really appreciate your empathy. This has been incredibly stressful as I have a deadline today."
        ),
        Tweet(
            tweet_id=4, 
            author_id="agent_001",
            role="Agent",
            inbound=False,
            created_at="2024-01-01T10:03:00Z",
            text="I appreciate your patience. To unlock your account quickly, I need to verify your identity. Can you please provide your registered email address? I'll reset your access immediately once verified."
        ),
        Tweet(
            tweet_id=5, 
            author_id="customer_001",
            role="Customer",
            inbound=True,
            created_at="2024-01-01T10:04:00Z",
            text="Perfect! My email is john.smith@company.com. Thank you so much for being so helpful and quick to respond!"
        ),
        Tweet(
            tweet_id=6, 
            author_id="agent_001",
            role="Agent",
            inbound=False,
            created_at="2024-01-01T10:05:00Z",
            text="Excellent! I've successfully unlocked your account and sent you a confirmation email. You should be able to access everything now. Is there anything else I can help you with today?"
        ),
        Tweet(
            tweet_id=7, 
            author_id="customer_001",
            role="Customer",
            inbound=True,
            created_at="2024-01-01T10:06:00Z",
            text="Amazing! It's working perfectly now! Thank you so much for your excellent help, understanding, and quick resolution. You've saved my day!"
        )
    ]
    
    classification = Classification(
        categorization="Account Access Issue",
        intent="Account Unlock Request",
        topic="Account Management",
        sentiment="Initially Negative, Ended Positive"
    )
    
    return ConversationData(
        conversation_id="test_complete_fields_verification",
        tweets=tweets,
        classification=classification
    )

def verify_complete_fields_in_output(performance_metrics: Dict[str, Any]) -> Dict[str, bool]:
    """
    Verify that all required fields are present in the performance metrics
    
    Args:
        performance_metrics: Performance metrics dictionary
        
    Returns:
        Dictionary with verification results
    """
    verification_results = {
        "normalized_score_present": False,
        "confidence_present": False,
        "interpretation_present": False,
        "evidence_present": False,
        "categories_found": 0,
        "kpis_found": 0,
        "sub_factors_found": 0,
        "field_completeness": 0.0
    }
    
    try:
        categories = performance_metrics.get("categories", {})
        verification_results["categories_found"] = len(categories)
        
        total_kpis = 0
        total_sub_factors = 0
        fields_present = 0
        total_fields_expected = 0
        
        for category_name, category_data in categories.items():
            logger.info(f"\n--- Checking Category: {category_name} ---")
            
            kpis = category_data.get("kpis", {})
            total_kpis += len(kpis)
            
            for kpi_name, kpi_data in kpis.items():
                logger.info(f"  KPI: {kpi_name}")
                
                # Check main KPI fields
                has_normalized_score = "normalized_score" in kpi_data
                has_confidence = "confidence" in kpi_data
                has_interpretation = "interpretation" in kpi_data
                has_evidence = "evidence" in kpi_data
                
                logger.info(f"    - normalized_score: {'✓' if has_normalized_score else '✗'} ({kpi_data.get('normalized_score', 'N/A')})")
                logger.info(f"    - confidence: {'✓' if has_confidence else '✗'} ({kpi_data.get('confidence', 'N/A')})")
                logger.info(f"    - interpretation: {'✓' if has_interpretation else '✗'} ({kpi_data.get('interpretation', 'N/A')})")
                logger.info(f"    - evidence: {'✓' if has_evidence else '✗'} ({len(kpi_data.get('evidence', []))} pieces)")
                
                # Count field presence
                total_fields_expected += 4  # 4 fields per KPI
                if has_normalized_score:
                    fields_present += 1
                    verification_results["normalized_score_present"] = True
                if has_confidence:
                    fields_present += 1
                    verification_results["confidence_present"] = True
                if has_interpretation:
                    fields_present += 1
                    verification_results["interpretation_present"] = True
                if has_evidence:
                    fields_present += 1
                    verification_results["evidence_present"] = True
                
                # Check sub-factors if they exist
                sub_factors = kpi_data.get("sub_factors", {})
                if sub_factors:
                    logger.info(f"    Sub-factors: {len(sub_factors)}")
                    total_sub_factors += len(sub_factors)
                    
                    for sf_name, sf_data in sub_factors.items():
                        # Sub-factors should also have evidence field
                        sf_has_evidence = "evidence" in sf_data
                        logger.info(f"      - {sf_name}: evidence {'✓' if sf_has_evidence else '✗'}")
                        
                        if sf_has_evidence:
                            total_fields_expected += 1
                            fields_present += 1
        
        verification_results["kpis_found"] = total_kpis
        verification_results["sub_factors_found"] = total_sub_factors
        verification_results["field_completeness"] = (fields_present / max(total_fields_expected, 1)) * 100
        
        return verification_results
        
    except Exception as e:
        logger.error(f"Error verifying fields: {e}")
        return verification_results

def main():
    """Main test execution"""
    logger.info("=" * 80)
    logger.info("COMPLETE FIELDS VERIFICATION TEST")
    logger.info("Testing normalized_score, confidence, interpretation, and evidence fields")
    logger.info("=" * 80)
    
    try:
        # Create test conversation
        conversation = create_test_conversation()
        logger.info(f"✓ Created test conversation with {len(conversation.tweets)} tweets")
        
        # Initialize LLM agent service
        llm_service = LLMAgentPerformanceAnalysisService()
        logger.info("✓ LLM Agent Service initialized successfully")
        
        # Perform analysis
        logger.info("\nPerforming comprehensive analysis...")
        result = llm_service.analyze_conversation_performance(conversation)
        
        # Extract performance metrics
        performance_metrics = result.get("performance_metrics", {})
        
        if not performance_metrics:
            logger.error("❌ No performance metrics found in result")
            return
        
        # Verify all required fields are present
        logger.info("\n" + "=" * 60)
        logger.info("FIELD VERIFICATION RESULTS")
        logger.info("=" * 60)
        
        verification = verify_complete_fields_in_output(performance_metrics)
        
        # Print summary
        logger.info(f"\n📊 SUMMARY:")
        logger.info(f"  Categories found: {verification['categories_found']}")
        logger.info(f"  KPIs found: {verification['kpis_found']}")
        logger.info(f"  Sub-factors found: {verification['sub_factors_found']}")
        logger.info(f"  Field completeness: {verification['field_completeness']:.1f}%")
        
        logger.info(f"\n🔍 REQUIRED FIELD PRESENCE:")
        logger.info(f"  ✓ normalized_score: {'Present' if verification['normalized_score_present'] else '❌ MISSING'}")
        logger.info(f"  ✓ confidence: {'Present' if verification['confidence_present'] else '❌ MISSING'}")
        logger.info(f"  ✓ interpretation: {'Present' if verification['interpretation_present'] else '❌ MISSING'}")
        logger.info(f"  ✓ evidence: {'Present' if verification['evidence_present'] else '❌ MISSING'}")
        
        # Check if all required fields are present
        all_fields_present = all([
            verification['normalized_score_present'],
            verification['confidence_present'],
            verification['interpretation_present'],
            verification['evidence_present']
        ])
        
        if all_fields_present:
            logger.info("\n🎉 SUCCESS: All required fields are present in the MongoDB output!")
        else:
            logger.error("\n❌ FAILURE: Some required fields are missing from the MongoDB output!")
        
        # Save detailed results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"complete_fields_verification_{timestamp}.json"
        
        output_data = {
            "test_timestamp": datetime.now().isoformat(),
            "conversation_id": "test_complete_fields_verification",
            "verification_results": verification,
            "performance_metrics_sample": performance_metrics,
            "test_success": all_fields_present
        }
        
        with open(filename, 'w') as f:
            json.dump(output_data, f, indent=2, default=str)
        
        logger.info(f"📄 Detailed results saved to: {filename}")
        
        return all_fields_present
        
    except Exception as e:
        logger.error(f"❌ Test failed with error: {e}")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
