#!/usr/bin/env python3
"""
Test to verify that "No Evidence" behavior has been completely removed
- Score should not be reset to 10 when no evidence is found
- Reasoning should not be updated to "No Evidence"
"""

import sys
import os
import json
import logging
from datetime import datetime

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from models import ConversationData, Tweet, Classification
from llm_agent_service import LLMAgentPerformanceAnalysisService

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def create_test_conversation_with_no_evidence():
    """Create a test conversation that should have no evidence for most KPIs"""
    
    # Create a very basic conversation with minimal content
    tweets = [
        Tweet(
            tweet_id=1001,
            author_id="customer_1",
            role="Customer",
            text="Hi there",
            created_at="2024-01-01T10:00:00Z",
            inbound=True
        ),
        Tweet(
            tweet_id=1002,
            author_id="agent_1",
            role="Agent", 
            text="Hello",
            created_at="2024-01-01T10:01:00Z",
            inbound=False
        ),
        Tweet(
            tweet_id=1003,
            author_id="customer_1",
            role="Customer",
            text="Ok",
            created_at="2024-01-01T10:02:00Z",
            inbound=True
        )
    ]
    
    classification = Classification(
        categorization="General Inquiry",
        intent="Information",
        topic="General",
        sentiment="Neutral"
    )
    
    return ConversationData(
        conversation_id="test_no_evidence_001",
        tweets=tweets,
        classification=classification
    )

def test_no_evidence_behavior_removal():
    """Test that No Evidence behavior has been completely removed"""
    
    logger.info("=== Testing No Evidence Behavior Removal ===")
    
    try:
        # Create LLM agent service
        service = LLMAgentPerformanceAnalysisService(model_name="claude-4", temperature=0.1)
        
        # Create test conversation with minimal content (should have no evidence for most KPIs)
        conversation_data = create_test_conversation_with_no_evidence()
        
        logger.info("Testing conversation with minimal content that should produce no evidence for most KPIs")
        
        # Analyze the conversation
        result = service.analyze_conversation_performance(conversation_data)
        
        # Check if analysis was successful
        if "error" in result:
            logger.error(f"Analysis failed: {result['error']}")
            return False
        
        # Extract performance metrics
        performance_metrics = result.get("performance_metrics", {})
        categories = performance_metrics.get("categories", {})
        
        logger.info(f"Found {len(categories)} categories to check")
        
        # Check each KPI for "No Evidence" behavior
        no_evidence_violations = []
        max_score_violations = []
        total_kpis_checked = 0
        
        for category_name, category_data in categories.items():
            kpis = category_data.get("kpis", {})
            
            for kpi_name, kpi_data in kpis.items():
                total_kpis_checked += 1
                score = kpi_data.get("score", 0)
                reasoning = kpi_data.get("reasoning", "")
                evidence = kpi_data.get("evidence", [])
                
                logger.info(f"Checking {category_name}/{kpi_name}: score={score}, evidence_count={len(evidence)}")
                
                # Check for "No Evidence" in reasoning (this should not happen)
                if "No Evidence" in reasoning:
                    no_evidence_violations.append({
                        "category": category_name,
                        "kpi": kpi_name,
                        "reasoning": reasoning,
                        "score": score,
                        "evidence_count": len(evidence)
                    })
                    logger.warning(f"❌ VIOLATION: Found 'No Evidence' in reasoning for {kpi_name}")
                
                # Check if score is exactly 10.0 when no evidence (this should not happen automatically)
                if len(evidence) == 0 and score == 10.0:
                    max_score_violations.append({
                        "category": category_name,
                        "kpi": kpi_name,
                        "reasoning": reasoning,
                        "score": score,
                        "evidence_count": len(evidence)
                    })
                    logger.warning(f"❌ POTENTIAL VIOLATION: Score is 10.0 with no evidence for {kpi_name}")
                
                # Check sub-factors if they exist
                sub_factors = kpi_data.get("sub_factors", {})
                for sub_factor_name, sub_factor_data in sub_factors.items():
                    total_kpis_checked += 1
                    sub_score = sub_factor_data.get("score", 0)
                    sub_reasoning = sub_factor_data.get("reasoning", "")
                    sub_evidence = sub_factor_data.get("evidence", [])
                    
                    logger.info(f"Checking sub-factor {sub_factor_name}: score={sub_score}, evidence_count={len(sub_evidence)}")
                    
                    # Check for "No Evidence" in sub-factor reasoning
                    if "No Evidence" in sub_reasoning:
                        no_evidence_violations.append({
                            "category": category_name,
                            "kpi": f"{kpi_name}.{sub_factor_name}",
                            "reasoning": sub_reasoning,
                            "score": sub_score,
                            "evidence_count": len(sub_evidence)
                        })
                        logger.warning(f"❌ VIOLATION: Found 'No Evidence' in sub-factor reasoning for {sub_factor_name}")
        
        # Report results
        logger.info(f"\n=== TEST RESULTS ===")
        logger.info(f"Total KPIs/Sub-factors checked: {total_kpis_checked}")
        logger.info(f"'No Evidence' reasoning violations: {len(no_evidence_violations)}")
        logger.info(f"Max score (10.0) with no evidence: {len(max_score_violations)}")
        
        if no_evidence_violations:
            logger.error("\n❌ FOUND 'NO EVIDENCE' VIOLATIONS:")
            for violation in no_evidence_violations:
                logger.error(f"  - {violation['category']}/{violation['kpi']}: '{violation['reasoning'][:100]}...'")
        
        if max_score_violations:
            logger.warning("\n⚠️  FOUND MAX SCORE VIOLATIONS (may be acceptable if not automatic):")
            for violation in max_score_violations:
                logger.warning(f"  - {violation['category']}/{violation['kpi']}: score={violation['score']}, reasoning='{violation['reasoning'][:50]}...'")
        
        # Test passes if no "No Evidence" violations found
        test_passed = len(no_evidence_violations) == 0
        
        if test_passed:
            logger.info("\n✅ TEST PASSED: No 'No Evidence' behavior found in reasoning")
        else:
            logger.error("\n❌ TEST FAILED: Found 'No Evidence' behavior that should be removed")
        
        # Save detailed results for inspection
        detailed_results = {
            "test_timestamp": datetime.now().isoformat(),
            "test_conversation_id": getattr(conversation_data, 'conversation_id', 'test_no_evidence_001'),
            "total_kpis_checked": total_kpis_checked,
            "no_evidence_violations": no_evidence_violations,
            "max_score_violations": max_score_violations,
            "test_passed": test_passed,
            "full_analysis_result": result
        }
        
        with open("no_evidence_behavior_test_results.json", "w") as f:
            json.dump(detailed_results, f, indent=2)
        
        logger.info("Detailed test results saved to: no_evidence_behavior_test_results.json")
        
        return test_passed
        
    except Exception as e:
        logger.error(f"Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_no_evidence_behavior_removal()
    sys.exit(0 if success else 1)
