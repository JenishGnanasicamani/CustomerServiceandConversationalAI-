#!/usr/bin/env python3
"""
Test Periodic Job Service with Detailed Reasoning
Verifies that the periodic job service now uses detailed LLM reasoning instead of generic fallbacks
"""

import json
import logging
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

# Add src directory to Python path
src_dir = Path(__file__).parent / "src"
sys.path.insert(0, str(src_dir))

from periodic_job_service import PeriodicJobService
from models import ConversationData, Tweet, Classification

def setup_logging():
    """Setup test logging"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

def create_test_conversation_data() -> ConversationData:
    """Create test conversation data for analysis"""
    tweets = [
        Tweet(
            tweet_id=1001,
            author_id="customer_1", 
            role="Customer",
            inbound=True,
            created_at="2024-01-01T10:00:00Z",
            text="Hi @Support, I'm really frustrated because I can't reset my password. I've been trying for 30 minutes and nothing works!"
        ),
        Tweet(
            tweet_id=1002,
            author_id="agent_1",
            role="Agent", 
            inbound=False,
            created_at="2024-01-01T10:01:00Z",
            text="I completely understand how frustrating that must be! I'm here to help you get this resolved right away. Let me assist you with a manual password reset - please DM me your email address so I can verify your account."
        ),
        Tweet(
            tweet_id=1003,
            author_id="customer_1",
            role="Customer",
            inbound=True, 
            created_at="2024-01-01T10:03:00Z",
            text="Thank you! Just sent you my email via DM. I really appreciate your quick response!"
        ),
        Tweet(
            tweet_id=1004,
            author_id="agent_1",
            role="Agent",
            inbound=False,
            created_at="2024-01-01T10:05:00Z", 
            text="Perfect! I've processed your password reset and sent you a new temporary password. You should receive it within 2 minutes. Is there anything else I can help you with today?"
        ),
        Tweet(
            tweet_id=1005,
            author_id="customer_1", 
            role="Customer",
            inbound=True,
            created_at="2024-01-01T10:07:00Z",
            text="Got it and it works perfectly! You're amazing - thank you so much for the excellent help!"
        )
    ]
    
    classification = Classification(
        categorization="Password Reset",
        intent="Technical Support", 
        topic="Account Access",
        sentiment="Positive"
    )
    
    return ConversationData(tweets=tweets, classification=classification)

def create_test_source_record() -> Dict[str, Any]:
    """Create test source record that mimics MongoDB sentiment_analysis record"""
    return {
        "_id": "test_object_id_123",
        "customer": "TestCustomer",
        "created_at": "2024-01-01T10:00:00Z",
        "conversation": {
            "tweets": [
                {
                    "tweet_id": 1001,
                    "author_id": "customer_1",
                    "role": "Customer", 
                    "inbound": True,
                    "created_at": "2024-01-01T10:00:00Z",
                    "text": "Hi @Support, I'm really frustrated because I can't reset my password. I've been trying for 30 minutes and nothing works!"
                },
                {
                    "tweet_id": 1002,
                    "author_id": "agent_1",
                    "role": "Agent",
                    "inbound": False, 
                    "created_at": "2024-01-01T10:01:00Z",
                    "text": "I completely understand how frustrating that must be! I'm here to help you get this resolved right away. Let me assist you with a manual password reset - please DM me your email address so I can verify your account."
                },
                {
                    "tweet_id": 1003,
                    "author_id": "customer_1",
                    "role": "Customer",
                    "inbound": True,
                    "created_at": "2024-01-01T10:03:00Z", 
                    "text": "Thank you! Just sent you my email via DM. I really appreciate your quick response!"
                },
                {
                    "tweet_id": 1004,
                    "author_id": "agent_1",
                    "role": "Agent",
                    "inbound": False,
                    "created_at": "2024-01-01T10:05:00Z",
                    "text": "Perfect! I've processed your password reset and sent you a new temporary password. You should receive it within 2 minutes. Is there anything else I can help you with today?"
                },
                {
                    "tweet_id": 1005,
                    "author_id": "customer_1",
                    "role": "Customer", 
                    "inbound": True,
                    "created_at": "2024-01-01T10:07:00Z",
                    "text": "Got it and it works perfectly! You're amazing - thank you so much for the excellent help!"
                }
            ],
            "classification": {
                "categorization": "Password Reset",
                "intent": "Technical Support",
                "topic": "Account Access", 
                "sentiment": "Positive"
            }
        }
    }

def analyze_reasoning_quality(reasoning: str, kpi_name: str) -> Dict[str, Any]:
    """
    Analyze quality of reasoning for a KPI
    
    Args:
        reasoning: The reasoning text to analyze
        kpi_name: Name of the KPI
        
    Returns:
        Dict with analysis results
    """
    analysis = {
        "kpi_name": kpi_name,
        "reasoning_length": len(reasoning),
        "is_generic": False,
        "contains_specific_details": False,
        "quality_score": 0
    }
    
    # Check for generic patterns
    generic_patterns = [
        "comprehensive analysis",
        "based on conversation evaluation", 
        "thorough assessment",
        "detailed examination",
        "overall performance"
    ]
    
    reasoning_lower = reasoning.lower()
    generic_matches = sum(1 for pattern in generic_patterns if pattern in reasoning_lower)
    analysis["generic_matches"] = generic_matches
    analysis["is_generic"] = generic_matches >= 2
    
    # Check for specific conversation details
    specific_patterns = [
        "password reset",
        "frustrating", 
        "understand",
        "dm me your email",
        "temporary password",
        "works perfectly",
        "thank you",
        "excellent help"
    ]
    
    specific_matches = sum(1 for pattern in specific_patterns if pattern in reasoning_lower)
    analysis["specific_matches"] = specific_matches
    analysis["contains_specific_details"] = specific_matches >= 2
    
    # Calculate quality score
    if analysis["contains_specific_details"] and not analysis["is_generic"]:
        analysis["quality_score"] = 10
    elif analysis["contains_specific_details"]:
        analysis["quality_score"] = 7
    elif not analysis["is_generic"]:
        analysis["quality_score"] = 5
    else:
        analysis["quality_score"] = 2
    
    return analysis

def main():
    """Main test function"""
    logger = logging.getLogger(__name__)
    
    print("🧪 Starting Periodic Job Service Detailed Reasoning Test")
    print("=" * 80)
    
    setup_logging()
    
    try:
        # Initialize periodic job service (without MongoDB connection for this test)
        service = PeriodicJobService("mongodb://localhost:27017/", "test_db")
        
        print("✓ Periodic Job Service initialized")
        
        # Create test data
        conversation_data = create_test_conversation_data()
        source_record = create_test_source_record()
        
        print("✓ Test conversation data created")
        
        # Test conversation performance analysis
        print("\n🔍 Testing analyze_conversation_performance...")
        
        analysis_result = service.analyze_conversation_performance(conversation_data, source_record)
        
        if not analysis_result:
            print("❌ FAIL: No analysis result returned")
            return False
        
        print("✓ Analysis completed successfully")
        
        # Analyze the performance metrics structure
        print("\n📊 Analyzing reasoning quality...")
        
        performance_metrics = analysis_result.get("performance_metrics", {})
        categories = performance_metrics.get("categories", {})
        
        if not categories:
            print("❌ FAIL: No categories found in performance metrics")
            return False
        
        reasoning_analysis = []
        kpis_with_detailed_reasoning = 0
        kpis_with_generic_reasoning = 0
        total_kpis = 0
        
        for category_name, category_data in categories.items():
            kpis = category_data.get("kpis", {})
            
            for kpi_name, kpi_data in kpis.items():
                total_kpis += 1
                reasoning = kpi_data.get("reason", "")
                
                if reasoning:
                    analysis = analyze_reasoning_quality(reasoning, kpi_name)
                    reasoning_analysis.append(analysis)
                    
                    if analysis["quality_score"] >= 7:
                        kpis_with_detailed_reasoning += 1
                    elif analysis["is_generic"]:
                        kpis_with_generic_reasoning += 1
                    
                    print(f"   📋 {kpi_name}:")
                    print(f"      Reasoning length: {analysis['reasoning_length']} chars")
                    print(f"      Quality score: {analysis['quality_score']}/10")
                    print(f"      Generic: {'Yes' if analysis['is_generic'] else 'No'}")
                    print(f"      Specific details: {'Yes' if analysis['contains_specific_details'] else 'No'}")
                    
                    if analysis["quality_score"] >= 7:
                        print(f"      ✅ GOOD: Detailed, specific reasoning")
                    elif analysis["is_generic"]:
                        print(f"      ❌ POOR: Generic reasoning detected")
                    else:
                        print(f"      ⚠️ FAIR: Moderate reasoning quality")
                    
                    print()
        
        # Overall assessment
        print(f"📈 OVERALL REASONING QUALITY ASSESSMENT:")
        print(f"Total KPIs analyzed: {total_kpis}")
        print(f"KPIs with detailed reasoning: {kpis_with_detailed_reasoning} ({kpis_with_detailed_reasoning/total_kpis*100:.1f}%)")
        print(f"KPIs with generic reasoning: {kpis_with_generic_reasoning} ({kpis_with_generic_reasoning/total_kpis*100:.1f}%)")
        
        # Success criteria
        success = kpis_with_detailed_reasoning >= (total_kpis * 0.7)  # At least 70% should have detailed reasoning
        
        if success:
            print(f"✅ SUCCESS: Periodic Job Service is using detailed reasoning!")
            print(f"✅ Most KPIs now have specific, conversation-based analysis instead of generic fallbacks")
        else:
            print(f"❌ FAIL: Too many KPIs still have generic reasoning")
            print(f"❌ Need to improve LLM analysis integration in periodic job service")
        
        # Save detailed results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_file = f"periodic_job_reasoning_test_results_{timestamp}.json"
        
        detailed_results = {
            "test_timestamp": datetime.now().isoformat(),
            "test_name": "Periodic Job Service Detailed Reasoning Test",
            "total_kpis": total_kpis,
            "kpis_with_detailed_reasoning": kpis_with_detailed_reasoning,
            "kpis_with_generic_reasoning": kpis_with_generic_reasoning,
            "detailed_reasoning_percentage": kpis_with_detailed_reasoning/total_kpis*100 if total_kpis > 0 else 0,
            "success": success,
            "reasoning_analysis": reasoning_analysis,
            "full_analysis_result": analysis_result
        }
        
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(detailed_results, f, indent=2, default=str, ensure_ascii=False)
        
        print(f"\n📄 Detailed test results saved to: {results_file}")
        
        print("\n" + "=" * 80)
        print("🏁 PERIODIC JOB SERVICE REASONING TEST COMPLETED!")
        
        if success:
            print("✅ The periodic job service now uses detailed LLM reasoning instead of generic fallbacks")
        else:
            print("❌ The periodic job service still needs improvement in reasoning quality")
        
        print("=" * 80)
        
        return success
        
    except Exception as e:
        logger.error(f"Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
