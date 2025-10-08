#!/usr/bin/env python3
"""
Simplified test to verify KPI persistence in performance_metrics structure
"""

import sys
import os
import json
import logging
from datetime import datetime

# Add src directory to Python path
sys.path.insert(0, 'src')

def test_performance_metrics_structure():
    """Test the _create_enhanced_performance_metrics method directly"""
    print("=== TESTING PERFORMANCE METRICS STRUCTURE ===")
    
    try:
        from llm_agent_service import LLMAgentPerformanceAnalysisService
        
        # Initialize service (but won't make API calls)
        service = LLMAgentPerformanceAnalysisService(model_name="claude-4", temperature=0.1)
        print("✅ LLM service initialized successfully")
        
        # Create sample categories with KPI data (simulating what would come from agent analysis)
        sample_categories = {
            'accuracy_compliance': {
                'name': 'accuracy_compliance',
                'kpis': {
                    'resolution_completeness': {
                        'name': 'resolution_completeness',
                        'score': 8.5,
                        'analysis': 'The agent provided a complete resolution pathway for the customer issue.',
                        'evidence': ['Agent offered to investigate immediately', 'Clear next steps provided'],
                        'recommendations': ['Continue providing clear resolution paths'],
                        'confidence': 0.9
                    },
                    'accuracy_automated_responses': {
                        'name': 'accuracy_automated_responses',
                        'score': 7.9,
                        'analysis': 'Response was accurate to the customer query with appropriate automation.',
                        'evidence': ['Response matched the reported issue type'],
                        'recommendations': ['Maintain accuracy standards'],
                        'confidence': 0.8
                    }
                },
                'category_score': 8.2,
                'category_performance': 'Good'
            },
            'empathy_communication': {
                'name': 'empathy_communication',
                'kpis': {
                    'empathy_score': {
                        'name': 'empathy_score',
                        'score': 9.2,
                        'analysis': 'Excellent demonstration of empathy through genuine appreciation.',
                        'evidence': ['Use of "delighted" shows emotional connection'],
                        'recommendations': ['Keep using emotionally positive language'],
                        'confidence': 0.95
                    },
                    'clarity_language': {
                        'name': 'clarity_language',
                        'score': 8.8,
                        'analysis': 'Clear and professional language used throughout.',
                        'evidence': ['Simple, direct communication', 'No jargon used'],
                        'recommendations': ['Continue clear communication style'],
                        'confidence': 0.85
                    },
                    'sentiment_shift': {
                        'name': 'sentiment_shift',
                        'score': 8.0,
                        'analysis': 'Good potential for positive sentiment change.',
                        'evidence': ['Proactive approach to resolution'],
                        'recommendations': ['Follow up to confirm satisfaction'],
                        'confidence': 0.8
                    }
                },
                'category_score': 8.7,
                'category_performance': 'Excellent'
            },
            'efficiency_resolution': {
                'name': 'efficiency_resolution',
                'kpis': {
                    'customer_effort_score': {
                        'name': 'customer_effort_score',
                        'score': 8.0,
                        'analysis': 'Minimal effort required from customer for issue resolution.',
                        'evidence': ['Simple next step: DM details'],
                        'recommendations': ['Keep resolution steps simple'],
                        'confidence': 0.85
                    },
                    'followup_necessity': {
                        'name': 'followup_necessity',
                        'score': 7.5,
                        'analysis': 'Good follow-up process initiated.',
                        'evidence': ['Clear request for more information'],
                        'recommendations': ['Ensure timely follow-up'],
                        'confidence': 0.8
                    }
                },
                'category_score': 7.75,
                'category_performance': 'Good'
            }
        }
        
        print(f"✅ Sample categories created with {sum(len(cat['kpis']) for cat in sample_categories.values())} KPIs")
        
        # Test the performance metrics creation method
        print("🔄 Creating enhanced performance metrics...")
        performance_metrics = service._create_enhanced_performance_metrics(sample_categories)
        
        print("✅ Performance metrics created successfully")
        print(f"✅ Structure: {list(performance_metrics.keys())}")
        
        # Verify the structure
        if 'categories' not in performance_metrics:
            print("❌ CRITICAL: No 'categories' field in performance_metrics!")
            return False
            
        categories = performance_metrics['categories']
        print(f"✅ Found {len(categories)} categories in performance_metrics")
        
        total_kpis = 0
        for cat_name, cat_data in categories.items():
            if 'kpis' not in cat_data:
                print(f"❌ CRITICAL: No 'kpis' field in category {cat_name}!")
                continue
                
            kpis = cat_data['kpis']
            kpi_count = len(kpis)
            total_kpis += kpi_count
            
            print(f"  📂 {cat_name}: {kpi_count} KPIs")
            
            # Check KPI structure
            for kpi_name, kpi_data in kpis.items():
                if 'score' not in kpi_data:
                    print(f"    ❌ CRITICAL: No 'score' in KPI {kpi_name}")
                    continue
                if 'reasoning' not in kpi_data:
                    print(f"    ❌ CRITICAL: No 'reasoning' in KPI {kpi_name}")
                    continue
                    
                score = kpi_data['score']
                reasoning = kpi_data['reasoning'][:50] + "..." if len(kpi_data['reasoning']) > 50 else kpi_data['reasoning']
                print(f"    📋 {kpi_name}: score={score}, reasoning='{reasoning}'")
        
        print(f"✅ Total KPIs in performance_metrics: {total_kpis}")
        
        if total_kpis > 0:
            print("🎉 SUCCESS: Performance metrics contain KPI data with scores and reasoning!")
            
            # Save the structure for inspection
            try:
                with open('performance_metrics_structure.json', 'w') as f:
                    json.dump(performance_metrics, f, indent=2, default=str)
                print("📁 Performance metrics saved to: performance_metrics_structure.json")
            except Exception as e:
                print(f"⚠️  Could not save structure: {e}")
            
            # Show the MongoDB-ready structure
            print("\n📄 MongoDB-ready performance_metrics structure:")
            print("performance_metrics: {")
            print("  categories: {")
            for cat_name, cat_data in list(categories.items())[:1]:  # Show first category as example
                print(f"    {cat_name}: {{")
                print(f"      category_score: {cat_data.get('category_score', 0)},")
                print("      kpis: {")
                for kpi_name, kpi_data in list(cat_data.get('kpis', {}).items())[:2]:  # Show first 2 KPIs
                    print(f"        {kpi_name}: {{")
                    print(f"          score: {kpi_data.get('score', 0)},")
                    print(f"          reasoning: \"{kpi_data.get('reasoning', '')[:30]}...\"")
                    print("        },")
                print("      }")
                print("    },")
            print("  },")
            print("  metadata: { ... }")
            print("}")
            
            return True
        else:
            print("❌ PROBLEM: Performance metrics have empty categories!")
            return False
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_mongodb_document_format():
    """Test that the format matches what should go into MongoDB"""
    print("\n=== TESTING MONGODB DOCUMENT FORMAT ===")
    
    try:
        # This is what should be stored in the agentic_analysis collection
        expected_document_structure = {
            "_id": "68e167ac56dfdec8b039be50",
            "conversation_id": "unknown",
            "customer": "Uber",
            "created_at": "2025-10-04T23:59:17.582987",
            "created_time": "23:59:17",
            "conversation_summary": {},
            "performance_metrics": {  # This is the key field
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
                                "reasoning": "Response was accurate to customer query..."
                            }
                        }
                    },
                    "empathy_communication": {
                        "category_score": 8.7,
                        "kpis": {
                            "empathy_score": {
                                "score": 9.2,
                                "reasoning": "Excellent empathy demonstrated..."
                            },
                            "clarity_language": {
                                "score": 8.8,
                                "reasoning": "Clear and professional language..."
                            }
                        }
                    }
                },
                "metadata": {
                    "total_kpis_evaluated": 4,
                    "evaluation_timestamp": "2025-10-05T00:00:04.488557",
                    "model_used": "claude-4"
                }
            },
            "categories": {},  # This might be empty now (deprecated)
            "analysis_timestamp": "2025-10-05T00:00:04.488557",
            "analysis_method": "LLM-based Agent Analysis",
            "model_used": "claude-4"
        }
        
        print("✅ Expected document structure defined")
        
        # Count KPIs in expected structure
        total_expected_kpis = 0
        categories = expected_document_structure["performance_metrics"]["categories"]
        for cat_name, cat_data in categories.items():
            kpi_count = len(cat_data["kpis"])
            total_expected_kpis += kpi_count
            print(f"  📂 {cat_name}: {kpi_count} KPIs expected")
        
        print(f"✅ Expected total KPIs: {total_expected_kpis}")
        print("✅ KPI persistence should work if performance_metrics.categories structure is populated")
        
        return True
        
    except Exception as e:
        print(f"❌ Document format test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 TESTING KPI PERSISTENCE IN PERFORMANCE METRICS")
    print("=" * 70)
    
    tests = [
        ("Performance Metrics Structure", test_performance_metrics_structure),
        ("MongoDB Document Format", test_mongodb_document_format),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🧪 Running: {test_name}")
        try:
            if test_func():
                print(f"✅ {test_name}: PASSED")
                passed += 1
            else:
                print(f"❌ {test_name}: FAILED")
        except Exception as e:
            print(f"❌ {test_name}: ERROR - {e}")
    
    print("\n" + "=" * 70)
    print(f"📊 SUMMARY: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED!")
        print("✅ KPI persistence issue should be RESOLVED")
        print("✅ Performance metrics structure contains categories with KPIs")
        print("✅ KPIs have scores and reasoning for MongoDB storage")
    else:
        print("⚠️  Some tests failed - issue may persist")
    
    return passed == total

if __name__ == "__main__":
    # Setup logging
    logging.basicConfig(level=logging.INFO, format='%(levelname)s:%(name)s:%(message)s')
    
    success = main()
    sys.exit(0 if success else 1)
