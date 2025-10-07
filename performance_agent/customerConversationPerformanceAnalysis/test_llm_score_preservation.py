#!/usr/bin/env python3
"""
Test to verify that LLM-provided scores are preserved when available,
regardless of evidence presence/absence
"""

import json
import logging
from datetime import datetime
from typing import Dict, Any, List

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

try:
    from src.llm_agent_service import LLMAgentPerformanceAnalysisService
    from src.models import ConversationData, Tweet, Classification
except ImportError as e:
    logger.error(f"Import error: {e}")
    exit(1)


def create_test_conversation_with_mixed_evidence() -> ConversationData:
    """
    Create a test conversation that has evidence for some KPIs but not others
    This will test the system's ability to handle mixed evidence situations
    """
    tweets = [
        Tweet(
            tweet_id=1,
            author_id="customer_001",
            role="Customer",
            inbound=True,
            created_at="2024-10-05T15:00:00Z",
            text="@Support I need help with my account - it's locked and I can't access it!"
        ),
        Tweet(
            tweet_id=2,
            author_id="support_agent_001", 
            role="Agent",
            inbound=False,
            created_at="2024-10-05T15:01:00Z",
            text="Hi! I completely understand how frustrating this must be. I'm here to help you unlock your account right away."
        ),
        Tweet(
            tweet_id=3,
            author_id="customer_001",
            role="Customer", 
            inbound=True,
            created_at="2024-10-05T15:02:00Z",
            text="Thank you for understanding. This is really important to me."
        ),
        Tweet(
            tweet_id=4,
            author_id="support_agent_001",
            role="Agent",
            inbound=False,
            created_at="2024-10-05T15:03:00Z",
            text="I can see how important this is. Please DM me your email address for verification and I'll unlock your account immediately."
        ),
        Tweet(
            tweet_id=5,
            author_id="customer_001",
            role="Customer",
            inbound=True,
            created_at="2024-10-05T15:04:00Z",
            text="Perfect! Sending it now."
        ),
        Tweet(
            tweet_id=6,
            author_id="support_agent_001",
            role="Agent",
            inbound=False,
            created_at="2024-10-05T15:07:00Z",
            text="Account unlocked! You should be able to access everything now. Is there anything else I can help you with?"
        ),
        Tweet(
            tweet_id=7,
            author_id="customer_001",
            role="Customer",
            inbound=True,
            created_at="2024-10-05T15:08:00Z",
            text="Excellent! Working perfectly now. Thank you so much for the amazing help!"
        )
    ]
    
    classification = Classification(
        categorization="technical_support",
        intent="account_access", 
        topic="account_unlock",
        sentiment="positive"
    )
    
    return ConversationData(
        tweets=tweets,
        classification=classification
    )


def analyze_llm_score_preservation(result: Dict[str, Any]) -> Dict[str, Any]:
    """
    Analyze the results to check if LLM scores are being preserved correctly
    
    Args:
        result: Analysis result from LLM agent
        
    Returns:
        Dictionary with preservation analysis
    """
    analysis = {
        "total_kpis": 0,
        "llm_scores_preserved": 0,
        "artificial_scores_used": 0,
        "evidence_vs_score_correlation": [],
        "preservation_issues": [],
        "success_rate": 0.0
    }
    
    try:
        performance_metrics = result.get("performance_metrics", {})
        categories = performance_metrics.get("categories", {})
        
        for category_name, category_data in categories.items():
            kpis = category_data.get("kpis", {})
            
            for kpi_name, kpi_data in kpis.items():
                analysis["total_kpis"] += 1
                
                score = kpi_data.get("score", 0)
                evidence = kpi_data.get("evidence", [])
                reasoning = kpi_data.get("reasoning", "")
                
                # Check if this appears to be LLM-generated vs artificial
                has_evidence = len(evidence) > 0
                has_detailed_reasoning = len(reasoning) > 100
                
                # Indicators of artificial score generation
                artificial_indicators = [
                    "based on conversation evidence" in reasoning.lower(),
                    "evidence-based scoring" in reasoning.lower(),
                    "fallback analysis" in reasoning.lower(),
                    "analysis of" in reasoning.lower() and "found no specific evidence" in reasoning.lower()
                ]
                
                # Indicators of LLM analysis preservation
                llm_preservation_indicators = [
                    "customer expressed" in reasoning.lower(),
                    "agent demonstrated" in reasoning.lower(),
                    "throughout the conversation" in reasoning.lower(),
                    has_detailed_reasoning and not any(artificial_indicators)
                ]
                
                is_artificial = any(artificial_indicators)
                is_llm_preserved = any(llm_preservation_indicators) and not is_artificial
                
                if is_llm_preserved:
                    analysis["llm_scores_preserved"] += 1
                    logger.info(f"✓ LLM score preserved for {kpi_name}: {score} (evidence: {len(evidence)}, reasoning: {len(reasoning)} chars)")
                elif is_artificial:
                    analysis["artificial_scores_used"] += 1
                    logger.warning(f"⚠ Artificial score detected for {kpi_name}: {score} (evidence: {len(evidence)})")
                    analysis["preservation_issues"].append({
                        "kpi": kpi_name,
                        "category": category_name,
                        "score": score,
                        "evidence_count": len(evidence),
                        "issue": "Artificial score used instead of LLM score"
                    })
                
                # Track evidence vs score correlation
                analysis["evidence_vs_score_correlation"].append({
                    "kpi": kpi_name,
                    "category": category_name,
                    "score": score,
                    "evidence_count": len(evidence),
                    "reasoning_length": len(reasoning),
                    "appears_llm_preserved": is_llm_preserved,
                    "appears_artificial": is_artificial
                })
        
        # Calculate success rate
        if analysis["total_kpis"] > 0:
            analysis["success_rate"] = (analysis["llm_scores_preserved"] / analysis["total_kpis"]) * 100
        
        return analysis
        
    except Exception as e:
        logger.error(f"Error analyzing LLM score preservation: {e}")
        analysis["error"] = str(e)
        return analysis


def main():
    """Main test execution"""
    logger.info("=== LLM SCORE PRESERVATION TEST ===")
    logger.info("Testing that LLM-provided scores are preserved when available, regardless of evidence")
    
    try:
        # Create test conversation
        logger.info("Creating test conversation with mixed evidence scenarios...")
        conversation_data = create_test_conversation_with_mixed_evidence()
        
        # Initialize LLM agent service
        logger.info("Initializing LLM agent service...")
        llm_service = LLMAgentPerformanceAnalysisService(model_name="claude-4", temperature=0.1)
        
        # Perform analysis
        logger.info("Performing comprehensive conversation analysis...")
        start_time = datetime.now()
        result = llm_service.analyze_conversation_performance(conversation_data)
        end_time = datetime.now()
        
        analysis_duration = (end_time - start_time).total_seconds()
        logger.info(f"Analysis completed in {analysis_duration:.2f} seconds")
        
        # Analyze preservation behavior
        logger.info("Analyzing LLM score preservation behavior...")
        preservation_analysis = analyze_llm_score_preservation(result)
        
        # Display results
        logger.info("=== SCORE PRESERVATION TEST RESULTS ===")
        logger.info(f"Total KPIs analyzed: {preservation_analysis['total_kpis']}")
        logger.info(f"LLM scores preserved: {preservation_analysis['llm_scores_preserved']}")
        logger.info(f"Artificial scores used: {preservation_analysis['artificial_scores_used']}")
        logger.info(f"Preservation success rate: {preservation_analysis['success_rate']:.1f}%")
        
        # Check for issues
        if preservation_analysis["preservation_issues"]:
            logger.warning("⚠ PRESERVATION ISSUES FOUND:")
            for issue in preservation_analysis["preservation_issues"]:
                logger.warning(f"  - {issue['kpi']} in {issue['category']}: {issue['issue']}")
        else:
            logger.info("✓ No preservation issues detected")
        
        # Evidence vs Score correlation analysis
        logger.info("=== EVIDENCE VS SCORE CORRELATION ===")
        for item in preservation_analysis["evidence_vs_score_correlation"][:5]:  # Show first 5
            status = "LLM" if item["appears_llm_preserved"] else ("ARTIFICIAL" if item["appears_artificial"] else "UNCLEAR")
            logger.info(f"  {item['kpi']}: score={item['score']}, evidence={item['evidence_count']}, status={status}")
        
        # Save detailed results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_file = f"llm_score_preservation_test_{timestamp}.json"
        
        with open(results_file, 'w') as f:
            json.dump({
                "test_metadata": {
                    "test_name": "LLM Score Preservation Test",
                    "timestamp": timestamp,
                    "duration_seconds": analysis_duration,
                    "conversation_id": "test_llm_score_preservation"
                },
                "preservation_analysis": preservation_analysis,
                "full_analysis_result": result
            }, f, indent=2, default=str)
        
        logger.info(f"Detailed results saved to: {results_file}")
        
        # Test conclusion
        if preservation_analysis["success_rate"] >= 80.0:
            logger.info("🎉 LLM SCORE PRESERVATION TEST PASSED!")
            logger.info("The system correctly preserves LLM scores when available")
        elif preservation_analysis["success_rate"] >= 60.0:
            logger.warning("⚠ LLM SCORE PRESERVATION TEST PARTIALLY PASSED")
            logger.warning("Some artificial score generation detected - needs improvement")
        else:
            logger.error("❌ LLM SCORE PRESERVATION TEST FAILED")
            logger.error("System is still generating artificial scores instead of preserving LLM analysis")
        
        logger.info(f"Final preservation rate: {preservation_analysis['success_rate']:.1f}%")
        
    except Exception as e:
        logger.error(f"Test execution failed: {e}")
        raise


if __name__ == "__main__":
    main()
