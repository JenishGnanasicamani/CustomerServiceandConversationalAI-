#!/usr/bin/env python3
"""
Simple debug script to identify the empty categories issue
"""

import sys
import os
import json
import logging
from datetime import datetime

# Add src directory to Python path
sys.path.insert(0, 'src')

def test_config_loading():
    """Test if configuration loading works"""
    print("=== TESTING CONFIG LOADING ===")
    
    try:
        from config_loader import config_loader
        
        # Test basic config loading
        config = config_loader.load_config()
        print(f"✅ Config loaded successfully")
        
        # Check categories
        categories = config_loader.get_all_categories()
        print(f"✅ Found {len(categories)} categories: {categories}")
        
        # Check KPIs in each category
        total_kpis = 0
        for category in categories:
            kpis = config_loader.get_category_kpis(category)
            kpi_count = len(kpis)
            total_kpis += kpi_count
            print(f"  📂 {category}: {kpi_count} KPIs")
            
        print(f"✅ Total KPIs configured: {total_kpis}")
        return True
        
    except Exception as e:
        print(f"❌ Config loading failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_llm_service_initialization():
    """Test LLM service initialization"""
    print("\n=== TESTING LLM SERVICE INITIALIZATION ===")
    
    try:
        from llm_agent_service import LLMAgentPerformanceAnalysisService
        
        service = LLMAgentPerformanceAnalysisService(model_name="claude-4", temperature=0.1)
        print("✅ LLM service initialized successfully")
        
        # Test getting available KPIs
        available_kpis = service.get_available_kpis()
        print(f"✅ Available KPIs: {available_kpis}")
        
        return True
        
    except Exception as e:
        print(f"❌ LLM service initialization failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_analysis_parsing():
    """Test the analysis parsing methods"""
    print("\n=== TESTING ANALYSIS PARSING ===")
    
    try:
        from llm_agent_service import LLMAgentPerformanceAnalysisService
        
        service = LLMAgentPerformanceAnalysisService(model_name="claude-4", temperature=0.1)
        
        # Test with sample agent output that contains tool invocations
        mock_agent_output = """
Here's my analysis of the conversation:

## KPI Analysis: resolution_completeness
**Score: 8.5/10**
**Analysis:** The agent provided a complete response addressing the customer's positive feedback.
**Evidence:** Agent acknowledged the feedback and thanked the customer appropriately.
**Recommendations:** Continue maintaining this level of responsiveness to positive feedback.

## KPI Analysis: empathy_score  
**Score: 9.2/10**
**Analysis:** Excellent demonstration of empathy through genuine appreciation of customer feedback.
**Evidence:** Use of "delighted" shows emotional connection and appreciation.
**Recommendations:** Keep using emotionally positive language to reinforce customer satisfaction.

## KPI Analysis: customer_effort_score
**Score: 8.0/10**
**Analysis:** Minimal effort required from customer, appropriate response to positive feedback.
**Evidence:** Simple acknowledgment without requiring further customer action.
**Recommendations:** Maintain this efficient handling of positive feedback scenarios.

Overall, this conversation demonstrates excellent customer service performance.
"""
        
        # Test the new parsing method
        categories = service._parse_tool_based_agent_output(mock_agent_output)
        
        print(f"✅ Parsing completed")
        print(f"✅ Found {len(categories)} categories")
        
        total_kpis = 0
        for cat_name, cat_data in categories.items():
            kpis = cat_data.get('kpis', {})
            kpi_count = len(kpis)
            total_kpis += kpi_count
            print(f"  📂 {cat_name}: {kpi_count} KPIs")
            
            for kpi_name, kpi_data in kpis.items():
                score = kpi_data.get('score', 'N/A')
                print(f"    📋 {kpi_name}: {score}")
        
        print(f"✅ Total KPIs parsed: {total_kpis}")
        
        if total_kpis > 0:
            print("🎉 SUCCESS: Categories contain KPI data!")
            return True
        else:
            print("❌ PROBLEM: No KPIs found in categories!")
            return False
            
    except Exception as e:
        print(f"❌ Analysis parsing failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_performance_metrics_creation():
    """Test performance metrics creation"""
    print("\n=== TESTING PERFORMANCE METRICS CREATION ===")
    
    try:
        from llm_agent_service import LLMAgentPerformanceAnalysisService
        
        service = LLMAgentPerformanceAnalysisService(model_name="claude-4", temperature=0.1)
        
        # Create sample categories with KPI data
        sample_categories = {
            'accuracy_compliance': {
                'name': 'accuracy_compliance',
                'kpis': {
                    'resolution_completeness': {
                        'name': 'resolution_completeness',
                        'score': 8.5,
                        'analysis': 'Complete resolution provided'
                    }
                },
                'category_score': 8.5
            },
            'empathy_communication': {
                'name': 'empathy_communication', 
                'kpis': {
                    'empathy_score': {
                        'name': 'empathy_score',
                        'score': 9.2,
                        'analysis': 'Excellent empathy demonstrated'
                    }
                },
                'category_score': 9.2
            }
        }
        
        # Test performance metrics creation
        performance_metrics = service._create_enhanced_performance_metrics(sample_categories)
        
        print("✅ Performance metrics created")
        print(f"✅ Structure: {list(performance_metrics.keys())}")
        
        if 'categories' in performance_metrics:
            categories = performance_metrics['categories']
            print(f"✅ Categories in metrics: {len(categories)}")
            
            total_kpis = 0
            for cat_name, cat_data in categories.items():
                kpis = cat_data.get('kpis', {})
                kpi_count = len(kpis)
                total_kpis += kpi_count
                print(f"  📂 {cat_name}: {kpi_count} KPIs")
                
                for kpi_name, kpi_data in kpis.items():
                    score = kpi_data.get('score', 'N/A')
                    print(f"    📋 {kpi_name}: {score}")
            
            print(f"✅ Total KPIs in performance metrics: {total_kpis}")
            
            if total_kpis > 0:
                print("🎉 SUCCESS: Performance metrics contain KPI data!")
                
                # Show sample JSON
                print("\n📄 Sample JSON structure:")
                sample_json = json.dumps(performance_metrics, indent=2, default=str)[:500] + "..."
                print(sample_json)
                
                return True
            else:
                print("❌ PROBLEM: Performance metrics have empty categories!")
                return False
        else:
            print("❌ PROBLEM: No categories in performance metrics!")
            return False
            
    except Exception as e:
        print(f"❌ Performance metrics creation failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print("🚀 DEBUGGING EMPTY CATEGORIES ISSUE")
    print("=" * 60)
    
    tests = [
        ("Config Loading", test_config_loading),
        ("LLM Service Initialization", test_llm_service_initialization), 
        ("Analysis Parsing", test_analysis_parsing),
        ("Performance Metrics Creation", test_performance_metrics_creation)
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
    
    print("\n" + "=" * 60)
    print(f"📊 SUMMARY: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED - Issue should be resolved!")
    else:
        print("⚠️  Some tests failed - Issue persists")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
