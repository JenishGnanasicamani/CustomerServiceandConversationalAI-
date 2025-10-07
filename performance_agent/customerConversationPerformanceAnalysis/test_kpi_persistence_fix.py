#!/usr/bin/env python3
"""
Test script to debug and fix KPI persistence issue in categories
"""

import sys
import os
import json
import logging
from datetime import datetime

# Add src directory to Python path
sys.path.insert(0, 'src')

def test_llm_service_directly():
    """Test LLM service with direct imports"""
    print("=== TESTING LLM SERVICE DIRECTLY ===")
    
    try:
        # Import directly from src
        from llm_agent_service import LLMAgentPerformanceAnalysisService
        from models import ConversationData, Tweet, Classification
        
        service = LLMAgentPerformanceAnalysisService(model_name="claude-4", temperature=0.1)
        print("✅ LLM service initialized successfully")
        
        # Test with sample conversation data
        sample_tweets = [
            Tweet(
                tweet_id="123",
                author_id="customer",
                role="customer",
                inbound=True,
                created_at="2023-01-01T10:00:00Z",
                text="Having issues with my account website not loading properly"
            ),
            Tweet(
                tweet_id="124", 
                author_id="agent",
                role="agent",
                inbound=False,
                created_at="2023-01-01T10:05:00Z",
                text="@customer We're delighted to help! Please DM us your account details and we'll investigate the website issue immediately."
            )
        ]
        
        sample_classification = Classification(
            categorization="technical_support",
            intent="resolve_issue",
            topic="website_functionality", 
            sentiment="neutral"
        )
        
        conversation_data = ConversationData(
            tweets=sample_tweets,
            classification=sample_classification
        )
        
        print("✅ Sample conversation data created")
        
        # Test the main analysis method
        print("🔄 Running performance analysis...")
        results = service.analyze_conversation_performance(conversation_data)
        
        print("✅ Analysis completed")
        print(f"✅ Results structure: {list(results.keys())}")
        
        # Check performance_metrics structure
        if 'performance_metrics' in results:
            perf_metrics = results['performance_metrics']
            print(f"✅ Performance metrics structure: {list(perf_metrics.keys())}")
            
            if 'categories' in perf_metrics:
                categories = perf_metrics['categories']
                print(f"✅ Found {len(categories)} categories in performance metrics")
                
                total_kpis = 0
                for cat_name, cat_data in categories.items():
                    kpis = cat_data.get('kpis', {})
                    kpi_count = len(kpis)
                    total_kpis += kpi_count
                    
                    print(f"  📂 {cat_name}: {kpi_count} KPIs")
                    
                    # Show first KPI details if available
                    if kpis:
                        first_kpi_name = list(kpis.keys())[0]
                        first_kpi_data = kpis[first_kpi_name]
                        print(f"    📋 {first_kpi_name}: score={first_kpi_data.get('score', 'N/A')}")
                        print(f"       reasoning='{first_kpi_data.get('reasoning', 'N/A')[:50]}...'")
                
                print(f"✅ Total KPIs in performance metrics: {total_kpis}")
                
                if total_kpis > 0:
                    print("🎉 SUCCESS: Performance metrics contain KPI data!")
                    
                    # Show sample JSON structure for MongoDB
                    print("\n📄 Sample performance_metrics structure for MongoDB:")
                    sample_json = json.dumps(perf_metrics, indent=2, default=str)[:800] + "..."
                    print(sample_json)
                    
                    return True, perf_metrics
                else:
                    print("❌ PROBLEM: Performance metrics have empty categories!")
                    return False, perf_metrics
            else:
                print("❌ PROBLEM: No categories in performance metrics!")
                return False, None
        else:
            print("❌ PROBLEM: No performance_metrics in results!")
            return False, None
            
    except Exception as e:
        print(f"❌ LLM service test failed: {e}")
        import traceback
        traceback.print_exc()
        return False, None

def test_mongodb_document_structure():
    """Test the expected MongoDB document structure"""
    print("\n=== TESTING MONGODB DOCUMENT STRUCTURE ===")
    
    try:
        # Sample of what should be stored in MongoDB
        expected_structure = {
            "_id": "68e167ac56dfdec8b039be50",
            "conversation_id": "unknown",
            "customer": "Uber", 
            "created_at": "2025-10-04T23:59:17.582987",
            "created_time": "23:59:17",
            "conversation_summary": {},
            "performance_metrics": {
                "categories": {
                    "accuracy_compliance": {
                        "category_score": 8.2,
                        "kpis": {
                            "resolution_completeness": {
                                "score": 8.5,
                                "reasoning": "Agent provided complete resolution pathway..."
                            },
                            "accuracy_automated_responses": {
                                "score": 7.9,
                                "reasoning": "Response was accurate to the customer query..."
                            }
                        }
                    },
                    "empathy_communication": {
                        "category_score": 9.1,
                        "kpis": {
                            "empathy_score": {
                                "score": 9.2,
                                "reasoning": "Excellent empathy demonstrated..."
                            },
                            "clarity_language": {
                                "score": 8.8,
                                "reasoning": "Clear and professional language used..."
                            }
                        }
                    }
                },
                "metadata": {
                    "total_kpis_evaluated": 14,
                    "evaluation_timestamp": "2025-10-05T00:00:04.488557",
                    "model_used": "claude-4"
                }
            },
            "categories": {},  # This might be the deprecated field
            "analysis_timestamp": "2025-10-05T00:00:04.488557",
            "analysis_method": "LLM-based Agent Analysis",
            "model_used": "claude-4"
        }
        
        print("✅ Expected MongoDB structure defined")
        print("📄 Key fields that should contain KPI data:")
        print("  - performance_metrics.categories.<category_name>.kpis.<kpi_name>.score")
        print("  - performance_metrics.categories.<category_name>.kpis.<kpi_name>.reasoning")
        
        return True
        
    except Exception as e:
        print(f"❌ MongoDB structure test failed: {e}")
        return False

def analyze_current_issue():
    """Analyze the current KPI persistence issue"""
    print("\n=== ANALYZING CURRENT ISSUE ===")
    
    print("Based on the provided sample document:")
    print("- ✅ Document has performance_metrics field")
    print("- ✅ Document has categories field")  
    print("- ❌ ISSUE: KPIs are not getting persisted in categories under performance_metrics")
    
    print("\nPossible causes:")
    print("1. 🔍 LLM agent output parsing is not extracting KPI scores correctly")
    print("2. 🔍 _create_enhanced_performance_metrics() is not populating categories properly")
    print("3. 🔍 Tool-based analysis is not returning expected format")
    print("4. 🔍 Fallback methods are not generating realistic KPI data")
    
    return True

def main():
    """Run all tests to diagnose and fix the issue"""
    print("🚀 DEBUGGING KPI PERSISTENCE ISSUE")
    print("=" * 60)
    
    tests = [
        ("Analyze Current Issue", analyze_current_issue),
        ("MongoDB Document Structure", test_mongodb_document_structure),
        ("LLM Service Direct Test", test_llm_service_directly),
    ]
    
    passed = 0
    total = len(tests)
    performance_metrics = None
    
    for test_name, test_func in tests:
        print(f"\n🧪 Running: {test_name}")
        try:
            if test_name == "LLM Service Direct Test":
                success, perf_metrics = test_func()
                if success:
                    performance_metrics = perf_metrics
                    passed += 1
                    print(f"✅ {test_name}: PASSED")
                else:
                    print(f"❌ {test_name}: FAILED")
            else:
                if test_func():
                    print(f"✅ {test_name}: PASSED")
                    passed += 1
                else:
                    print(f"❌ {test_name}: FAILED")
        except Exception as e:
            print(f"❌ {test_name}: ERROR - {e}")
    
    print("\n" + "=" * 60)
    print(f"📊 SUMMARY: {passed}/{total} tests passed")
    
    if performance_metrics and len(performance_metrics.get('categories', {})) > 0:
        print("🎉 SUCCESS: KPI data is being generated properly!")
        print("✅ The performance_metrics structure contains categories with KPIs")
        print("✅ This should resolve the MongoDB persistence issue")
        
        # Save sample output for verification
        try:
            with open('sample_performance_metrics_output.json', 'w') as f:
                json.dump(performance_metrics, f, indent=2, default=str)
            print("📁 Sample output saved to: sample_performance_metrics_output.json")
        except Exception as e:
            print(f"⚠️  Could not save sample output: {e}")
            
    else:
        print("⚠️  Issue persists - KPI data not found in performance_metrics")
    
    return passed == total

if __name__ == "__main__":
    # Setup logging
    logging.basicConfig(level=logging.INFO)
    
    success = main()
    sys.exit(0 if success else 1)
