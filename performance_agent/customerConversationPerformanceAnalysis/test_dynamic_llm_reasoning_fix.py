#!/usr/bin/env python3
"""
DYNAMIC LLM REASONING FIX TEST
Fix the issue where some categories get generic reasoning while others get proper LLM reasoning.
This test will verify and fix the parsing logic to ensure ALL KPIs get LLM-generated reasoning.
"""

import json
import logging
from datetime import datetime
from typing import Dict, Any, List

# Set up logging
logging.basicConfig(level=logging.INFO)

# Import required modules
try:
    from src.llm_agent_service import get_llm_agent_service
    from src.models import ConversationData, Tweet, Classification
except ImportError as e:
    print(f"Import error: {e}")
    exit(1)

def test_dynamic_llm_reasoning_fix():
    """Test and fix the LLM reasoning extraction to ensure ALL categories get proper reasoning"""
    
    print("🔧 DYNAMIC LLM REASONING FIX TEST")
    print("=" * 80)
    
    # Test conversation that should trigger analysis for all categories
    test_conversation = ConversationData(
        tweets=[
            Tweet(
                tweet_id=3001,
                author_id="customer_test",
                role="Customer",
                inbound=True,
                created_at="2024-01-01T16:00:00Z",
                text="Hi @Support, I'm really frustrated because I've been trying to access my account for 30 minutes and it keeps saying my password is wrong. I have an important meeting in an hour and need to get some documents. This is really stressing me out!"
            ),
            Tweet(
                tweet_id=3002,
                author_id="agent_test",
                role="Agent",
                inbound=False,
                created_at="2024-01-01T16:02:00Z",
                text="I completely understand how frustrating that must be, especially with your important meeting coming up. Let me help you get this resolved right away. Can you please DM me your email address so I can check your account status and do a manual password reset?"
            ),
            Tweet(
                tweet_id=3003,
                author_id="customer_test",
                role="Customer",
                inbound=True,
                created_at="2024-01-01T16:04:00Z",
                text="Just sent you my email. I really appreciate the quick response - I was getting worried about missing my meeting."
            ),
            Tweet(
                tweet_id=3004,
                author_id="agent_test",
                role="Agent",
                inbound=False,
                created_at="2024-01-01T16:06:00Z",
                text="Got it! I've manually reset your password and sent you a temporary one to your email. You should receive it within 2 minutes. After you log in, the system will prompt you to create a new permanent password. Is there anything else I can help you with today?"
            ),
            Tweet(
                tweet_id=3005,
                author_id="customer_test",
                role="Customer",
                inbound=True,
                created_at="2024-01-01T16:08:00Z",
                text="Got it and it works perfectly! Thank you so much for the amazing quick help - you saved my meeting! This was exactly what I needed."
            )
        ],
        classification=Classification(
            categorization="Account Access Issue",
            intent="Technical Support",
            topic="Password Reset",
            sentiment="Positive"
        )
    )
    
    print("✓ Created test conversation with rich content for all KPI categories")
    
    # Test LLM service analysis
    print("\n📊 Testing LLM Service Analysis")
    print("-" * 50)
    
    try:
        llm_service = get_llm_agent_service()
        print(f"✓ LLM service initialized: {llm_service.model_name}")
        
        # Run the analysis
        result = llm_service.analyze_conversation_performance(test_conversation)
        
        print(f"✓ Analysis completed")
        print(f"   - Analysis method: {result.get('analysis_method', 'unknown')}")
        print(f"   - Model used: {result.get('model_used', 'unknown')}")
        
        # Analyze the performance metrics for reasoning quality
        performance_metrics = result.get('performance_metrics', {})
        categories = performance_metrics.get('categories', {})
        
        print(f"\n📋 ANALYZING REASONING QUALITY FOR ALL CATEGORIES")
        print("-" * 60)
        
        reasoning_analysis = {
            "total_kpis": 0,
            "proper_llm_reasoning": 0,
            "generic_reasoning": 0,
            "empty_reasoning": 0,
            "categories_with_issues": [],
            "kpis_with_issues": []
        }
        
        # Define patterns that indicate generic/fallback reasoning
        generic_patterns = [
            "found no specific evidence within the available",
            "analysis found no specific",
            "no specific reasoning provided",
            "detailed analysis",
            "standard approach", 
            "basic evaluation",
            "general assessment",
            "sub-factor analysis for",
            "analysis of [kpi_name] found no specific evidence"
        ]
        
        for category_name, category_data in categories.items():
            print(f"\n🏷️  CATEGORY: {category_name}")
            category_issues = []
            
            kpis = category_data.get('kpis', {})
            if not kpis:
                print(f"   ❌ No KPIs found in category")
                continue
                
            for kpi_name, kpi_data in kpis.items():
                reasoning_analysis["total_kpis"] += 1
                
                # Check main KPI reasoning
                main_reason = kpi_data.get('reason', '')
                
                # Analyze reasoning quality
                is_generic = any(pattern.lower() in main_reason.lower() for pattern in generic_patterns)
                is_empty = len(main_reason.strip()) < 20
                is_proper_llm = not is_generic and not is_empty and len(main_reason) > 50
                
                if is_proper_llm:
                    reasoning_analysis["proper_llm_reasoning"] += 1
                    status = "✅ LLM"
                elif is_generic:
                    reasoning_analysis["generic_reasoning"] += 1
                    status = "❌ GENERIC"
                    category_issues.append(f"{kpi_name}: Generic reasoning")
                else:
                    reasoning_analysis["empty_reasoning"] += 1
                    status = "⚠️  EMPTY"
                    category_issues.append(f"{kpi_name}: Empty reasoning")
                
                print(f"   • {kpi_name}: {status}")
                print(f"     Reasoning: {main_reason[:100]}...")
                
                # Check evidence
                evidence = kpi_data.get('evidence', [])
                evidence_status = f"{len(evidence)} pieces" if evidence else "No evidence"
                print(f"     Evidence: {evidence_status}")
                
                # Check sub-KPIs if they exist
                sub_kpis = kpi_data.get('sub_kpis', {})
                if sub_kpis:
                    print(f"     Sub-KPIs: {len(sub_kpis)} found")
                    for sub_kpi_name, sub_kpi_data in sub_kpis.items():
                        sub_reason = sub_kpi_data.get('reason', '')
                        sub_is_generic = any(pattern.lower() in sub_reason.lower() for pattern in generic_patterns)
                        sub_status = "❌ GENERIC" if sub_is_generic else ("✅ LLM" if len(sub_reason) > 50 else "⚠️  SHORT")
                        print(f"       - {sub_kpi_name}: {sub_status}")
                        
                        if sub_is_generic:
                            category_issues.append(f"{kpi_name}.{sub_kpi_name}: Generic sub-KPI reasoning")
            
            if category_issues:
                reasoning_analysis["categories_with_issues"].append({
                    "category": category_name,
                    "issues": category_issues
                })
        
        # Print summary
        print(f"\n📈 REASONING QUALITY SUMMARY")
        print("-" * 40)
        total_kpis = reasoning_analysis["total_kpis"]
        proper_llm = reasoning_analysis["proper_llm_reasoning"]
        generic = reasoning_analysis["generic_reasoning"]
        empty = reasoning_analysis["empty_reasoning"]
        
        print(f"Total KPIs analyzed: {total_kpis}")
        print(f"✅ Proper LLM reasoning: {proper_llm} ({proper_llm/total_kpis*100:.1f}%)")
        print(f"❌ Generic reasoning: {generic} ({generic/total_kpis*100:.1f}%)")
        print(f"⚠️  Empty reasoning: {empty} ({empty/total_kpis*100:.1f}%)")
        
        # Show issues by category
        if reasoning_analysis["categories_with_issues"]:
            print(f"\n🚨 CATEGORIES WITH REASONING ISSUES:")
            for category_issue in reasoning_analysis["categories_with_issues"]:
                print(f"   Category: {category_issue['category']}")
                for issue in category_issue["issues"]:
                    print(f"     - {issue}")
        else:
            print(f"\n🎉 ALL CATEGORIES HAVE PROPER LLM REASONING!")
        
        # Save detailed results for analysis
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_file = f"dynamic_llm_reasoning_fix_results_{timestamp}.json"
        
        detailed_results = {
            "test_timestamp": datetime.now().isoformat(),
            "test_conversation": {
                "tweets": [tweet.dict() for tweet in test_conversation.tweets],
                "classification": test_conversation.classification.dict()
            },
            "analysis_result": result,
            "reasoning_analysis": reasoning_analysis,
            "categories_analyzed": list(categories.keys()),
            "total_categories": len(categories),
            "total_kpis": total_kpis
        }
        
        with open(results_file, 'w') as f:
            json.dump(detailed_results, f, indent=2, default=str)
        
        print(f"\n💾 Detailed results saved to: {results_file}")
        
        # Determine if fix is needed
        success_rate = proper_llm / total_kpis * 100 if total_kpis > 0 else 0
        
        if success_rate >= 90.0:
            print(f"\n🎯 SUCCESS: {success_rate:.1f}% of KPIs have proper LLM reasoning!")
            print("✅ The dynamic LLM reasoning extraction is working correctly.")
            return True
        else:
            print(f"\n⚠️  NEEDS FIX: Only {success_rate:.1f}% of KPIs have proper LLM reasoning")
            print("❌ Generic reasoning patterns detected - fix required.")
            
            # Show specific fix recommendations
            print(f"\n🔧 RECOMMENDED FIXES:")
            print("1. Improve LLM response parsing in _parse_tool_based_agent_output()")
            print("2. Enhance fallback reasoning generation in _create_fallback_categories_with_realistic_scores()")
            print("3. Ensure _extract_llm_reasoning_from_agent_output() captures all LLM analysis")
            print("4. Update reasoning extraction patterns to match actual LLM output format")
            
            return False
            
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        return False

if __name__ == "__main__":
    success = test_dynamic_llm_reasoning_fix()
    if success:
        print("\n🏆 Dynamic LLM reasoning fix test PASSED!")
    else:
        print("\n💥 Dynamic LLM reasoning fix test FAILED!")
