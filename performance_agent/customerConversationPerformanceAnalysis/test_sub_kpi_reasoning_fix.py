#!/usr/bin/env python3
"""
Test to verify that sub-KPI reasoning has been fixed and is no longer generic
"""

import json
import logging
from datetime import datetime
from typing import Dict, Any

# Set up basic logging
logging.basicConfig(level=logging.INFO)

# Import required modules
try:
    from src.periodic_job_service import PeriodicJobService
    from src.models import ConversationData, Tweet, Classification
except ImportError as e:
    print(f"Import error: {e}")
    print("Please run this test from the project root directory")
    exit(1)

def test_sub_kpi_reasoning_fix():
    """Test to verify sub-KPI reasoning improvements"""
    
    print("🧪 Starting Sub-KPI Reasoning Fix Test")
    print("=" * 80)
    
    # Initialize the service
    service = PeriodicJobService("mongodb://localhost:27017/", "test_db")
    
    # Create test conversation data  
    test_conversation = ConversationData(
        tweets=[
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
        ],
        classification=Classification(
            categorization="Password Reset",
            intent="Technical Support", 
            topic="Account Access",
            sentiment="Positive"
        )
    )
    
    print("✓ Test conversation data created")
    
    # Test the enhanced sub-KPI generation method directly
    print("\n🔍 Testing sub-KPI reasoning generation...")
    
    # Test empathy_score sub-KPIs
    print("\n   📋 Testing empathy_score sub-KPIs...")
    empathy_sub_kpis = service._generate_synthetic_sub_kpis("empathy_score", 8.5, test_conversation)
    
    # Test resolution_completeness sub-KPIs  
    print("   📋 Testing resolution_completeness sub-KPIs...")
    resolution_sub_kpis = service._generate_synthetic_sub_kpis("resolution_completeness", 9.0, test_conversation)
    
    # Test customer_effort_score sub-KPIs
    print("   📋 Testing customer_effort_score sub-KPIs...")
    effort_sub_kpis = service._generate_synthetic_sub_kpis("customer_effort_score", 7.5, test_conversation)
    
    print("✓ Sub-KPI generation completed")
    
    # Analyze the quality of sub-KPI reasoning
    print("\n📊 Analyzing sub-KPI reasoning quality...")
    
    def analyze_reasoning_quality(sub_kpis: Dict[str, Any], kpi_name: str) -> Dict[str, Any]:
        """Analyze the quality of sub-KPI reasoning"""
        
        print(f"\n   📋 {kpi_name}:")
        quality_stats = {
            "total_sub_kpis": len(sub_kpis),
            "detailed_reasoning": 0,
            "conversation_specific": 0,
            "generic_reasoning": 0,
            "evidence_based": 0
        }
        
        for sub_kpi_name, sub_kpi_data in sub_kpis.items():
            reason = sub_kpi_data.get("reason", "")
            
            # Check reasoning length (detailed reasoning should be longer)
            reasoning_length = len(reason)
            
            # Check for conversation-specific content
            conversation_specific = any(phrase in reason.lower() for phrase in [
                "password", "frustrat", "30 minutes", "dm", "temporary password", 
                "understand", "help", "2 minutes", "works perfectly", "amazing"
            ])
            
            # Check for evidence-based reasoning (specific quotes or references)
            evidence_based = any(phrase in reason for phrase in [
                '"', "customer stating", "agent", "conversation shows", "evidence from"
            ])
            
            # Check for generic reasoning patterns
            generic_patterns = [
                "standard", "basic", "general", "typical", "normal approach",
                "handled through", "without specific"
            ]
            is_generic = any(pattern in reason.lower() for pattern in generic_patterns)
            
            # Categorize reasoning quality
            if reasoning_length > 200 and conversation_specific and evidence_based:
                quality = "EXCELLENT"
                quality_stats["detailed_reasoning"] += 1
            elif reasoning_length > 150 and conversation_specific:
                quality = "GOOD" 
                quality_stats["conversation_specific"] += 1
            elif is_generic or reasoning_length < 100:
                quality = "POOR"
                quality_stats["generic_reasoning"] += 1
            else:
                quality = "FAIR"
            
            if evidence_based:
                quality_stats["evidence_based"] += 1
            
            print(f"      {sub_kpi_name}:")
            print(f"         Length: {reasoning_length} chars")
            print(f"         Quality: {quality}")
            print(f"         Conversation-specific: {'Yes' if conversation_specific else 'No'}")
            print(f"         Evidence-based: {'Yes' if evidence_based else 'No'}")
            print(f"         Reasoning: {reason[:100]}{'...' if len(reason) > 100 else ''}")
        
        return quality_stats
    
    # Analyze each KPI's sub-KPIs
    empathy_stats = analyze_reasoning_quality(empathy_sub_kpis, "empathy_score")
    resolution_stats = analyze_reasoning_quality(resolution_sub_kpis, "resolution_completeness")  
    effort_stats = analyze_reasoning_quality(effort_sub_kpis, "customer_effort_score")
    
    # Calculate overall statistics
    total_stats = {
        "total_sub_kpis": empathy_stats["total_sub_kpis"] + resolution_stats["total_sub_kpis"] + effort_stats["total_sub_kpis"],
        "detailed_reasoning": empathy_stats["detailed_reasoning"] + resolution_stats["detailed_reasoning"] + effort_stats["detailed_reasoning"],
        "conversation_specific": empathy_stats["conversation_specific"] + resolution_stats["conversation_specific"] + effort_stats["conversation_specific"], 
        "generic_reasoning": empathy_stats["generic_reasoning"] + resolution_stats["generic_reasoning"] + effort_stats["generic_reasoning"],
        "evidence_based": empathy_stats["evidence_based"] + resolution_stats["evidence_based"] + effort_stats["evidence_based"]
    }
    
    print(f"\n📈 OVERALL SUB-KPI REASONING QUALITY ASSESSMENT:")
    print(f"Total sub-KPIs analyzed: {total_stats['total_sub_kpis']}")
    print(f"Sub-KPIs with detailed reasoning: {total_stats['detailed_reasoning']} ({total_stats['detailed_reasoning']/total_stats['total_sub_kpis']*100:.1f}%)")
    print(f"Sub-KPIs with conversation-specific reasoning: {total_stats['conversation_specific']} ({total_stats['conversation_specific']/total_stats['total_sub_kpis']*100:.1f}%)")
    print(f"Sub-KPIs with evidence-based reasoning: {total_stats['evidence_based']} ({total_stats['evidence_based']/total_stats['total_sub_kpis']*100:.1f}%)")
    print(f"Sub-KPIs with generic reasoning: {total_stats['generic_reasoning']} ({total_stats['generic_reasoning']/total_stats['total_sub_kpis']*100:.1f}%)")
    
    # Test results assessment
    detailed_percentage = (total_stats['detailed_reasoning'] + total_stats['conversation_specific']) / total_stats['total_sub_kpis'] * 100
    generic_percentage = total_stats['generic_reasoning'] / total_stats['total_sub_kpis'] * 100
    
    if detailed_percentage >= 70 and generic_percentage <= 20:
        print("✅ SUCCESS: Sub-KPI reasoning has been significantly improved!")
        print("✅ Most sub-KPIs now have detailed, conversation-specific reasoning")
    elif detailed_percentage >= 50 and generic_percentage <= 30:
        print("⚠️ PARTIAL SUCCESS: Sub-KPI reasoning has improved but could be better")
    else:
        print("❌ FAILURE: Sub-KPI reasoning still needs improvement")
    
    # Save detailed test results
    test_results = {
        "test_name": "Sub-KPI Reasoning Fix Test",
        "test_timestamp": datetime.now().isoformat(),
        "empathy_sub_kpis": empathy_sub_kpis,
        "resolution_sub_kpis": resolution_sub_kpis,
        "effort_sub_kpis": effort_sub_kpis,
        "quality_statistics": {
            "empathy_stats": empathy_stats,
            "resolution_stats": resolution_stats,
            "effort_stats": effort_stats,
            "total_stats": total_stats
        },
        "success_criteria": {
            "detailed_percentage": detailed_percentage,
            "generic_percentage": generic_percentage,
            "test_passed": detailed_percentage >= 70 and generic_percentage <= 20
        }
    }
    
    results_filename = f"sub_kpi_reasoning_test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(results_filename, 'w') as f:
        json.dump(test_results, f, indent=2, default=str)
    
    print(f"\n📄 Detailed test results saved to: {results_filename}")
    
    print("\n" + "=" * 80)
    print("🏁 SUB-KPI REASONING FIX TEST COMPLETED!")
    
    if test_results["success_criteria"]["test_passed"]:
        print("✅ The sub-KPI reasoning has been successfully improved!")
        print("✅ Sub-KPIs now use detailed, conversation-specific reasoning instead of generic templates")
    else:
        print("⚠️ The sub-KPI reasoning improvements are partial - further enhancements may be needed")
    
    print("=" * 80)

if __name__ == "__main__":
    test_sub_kpi_reasoning_fix()
