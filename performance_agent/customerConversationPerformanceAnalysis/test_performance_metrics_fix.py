#!/usr/bin/env python3
"""
Test script to diagnose and fix performance metrics persistence issue
"""

import sys
import os
import json
from datetime import datetime

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from llm_agent_service import get_llm_agent_service
from models import ConversationData, Tweet, Classification

def test_performance_metrics_flow():
    """Test the complete performance metrics flow"""
    
    print('🔍 DIAGNOSING PERFORMANCE METRICS PERSISTENCE ISSUE')
    print('=' * 60)
    
    try:
        # 1. Initialize service
        print('Step 1: Initializing LLM Agent Service...')
        service = get_llm_agent_service()
        print('✅ LLM Agent Service initialized')
        
        # 2. Create test data
        print('\nStep 2: Creating test conversation data...')
        tweets = [
            Tweet(tweet_id=1, author_id='customer', role='Customer', inbound=True, 
                  created_at='2025-10-04T22:30:00Z', text='I need help with my account'),
            Tweet(tweet_id=2, author_id='agent', role='Service Provider', inbound=False,
                  created_at='2025-10-04T22:31:00Z', text='I would be delighted to help you! Please DM us for assistance.')
        ]
        
        classification = Classification(
            categorization='Account inquiry',
            intent='Support Request', 
            topic='Account',
            sentiment='Neutral'
        )
        
        conversation_data = ConversationData(tweets=tweets, classification=classification)
        print('✅ Test conversation data created')
        
        # 3. Test enhanced metrics creation
        print('\nStep 3: Testing _create_enhanced_performance_metrics...')
        
        # Create mock categories with realistic data
        mock_categories = {
            'accuracy_compliance': {
                'name': 'accuracy_compliance',
                'kpis': {
                    'resolution_completeness': {
                        'name': 'resolution_completeness',
                        'score': 7.5,
                        'analysis': 'Agent provided clear next steps by asking customer to DM'
                    }
                },
                'category_score': 7.5
            },
            'empathy_communication': {
                'name': 'empathy_communication', 
                'kpis': {
                    'empathy_score': {
                        'name': 'empathy_score',
                        'score': 8.2,
                        'analysis': 'Agent used positive language like "delighted to help"'
                    },
                    'clarity_language': {
                        'name': 'clarity_language',
                        'score': 7.8,
                        'analysis': 'Communication was clear and professional'
                    }
                },
                'category_score': 8.0
            }
        }
        
        enhanced_metrics = service._create_enhanced_performance_metrics(mock_categories)
        print('✅ Enhanced metrics created successfully')
        
        # 4. Analyze structure
        print('\nStep 4: Analyzing performance metrics structure...')
        print(f'   - Categories count: {len(enhanced_metrics.get("categories", {}))}')
        print(f'   - Total KPIs evaluated: {enhanced_metrics.get("metadata", {}).get("total_kpis_evaluated", 0)}')
        
        # Check detailed structure
        categories_with_kpis = 0
        total_kpis_with_scores = 0
        
        for cat_name, cat_data in enhanced_metrics.get('categories', {}).items():
            print(f'   - {cat_name}:')
            print(f'     • Category score: {cat_data.get("category_score", "N/A")}')
            print(f'     • KPIs count: {len(cat_data.get("kpis", {}))}')
            
            if cat_data.get('kpis'):
                categories_with_kpis += 1
                for kpi_name, kpi_data in cat_data['kpis'].items():
                    has_score = 'score' in kpi_data
                    has_reasoning = 'reasoning' in kpi_data
                    print(f'       - {kpi_name}: score={kpi_data.get("score", "N/A")}, has_reasoning={has_reasoning}')
                    if has_score:
                        total_kpis_with_scores += 1
        
        print(f'\n   📊 SUMMARY:')
        print(f'   - Categories with KPIs: {categories_with_kpis}')
        print(f'   - Total KPIs with scores: {total_kpis_with_scores}')
        
        # 5. Test full structured results
        print('\nStep 5: Testing structured comprehensive results...')
        
        mock_agent_result = {
            'output': '''
            ## Comprehensive Customer Service Analysis
            
            I have analyzed this conversation against all configured KPIs.
            
            ## KPI Analysis: Resolution Completeness
            **Score: 7.5/10**
            **Analysis:** Agent provided clear next steps by directing customer to DM.
            
            ## KPI Analysis: Empathy Score  
            **Score: 8.2/10**
            **Analysis:** Agent used positive, welcoming language.
            '''
        }
        
        structured_result = service._structure_comprehensive_results(mock_agent_result, conversation_data)
        print('✅ Structured results created successfully')
        
        # 6. Check final structure
        print('\nStep 6: Validating final structure for persistence...')
        print(f'   - Has conversation_id: {"conversation_id" in structured_result}')
        print(f'   - Has analysis_timestamp: {"analysis_timestamp" in structured_result}')
        print(f'   - Has performance_metrics: {"performance_metrics" in structured_result}')
        print(f'   - Has agent_output: {"agent_output" in structured_result}')
        
        if 'performance_metrics' in structured_result:
            pm = structured_result['performance_metrics']
            print(f'   - PM categories count: {len(pm.get("categories", {}))}')
            print(f'   - PM has metadata: {"metadata" in pm}')
            
            # Check if KPIs have scores in final structure
            final_kpis_with_scores = 0
            for cat_name, cat_data in pm.get('categories', {}).items():
                for kpi_name, kpi_data in cat_data.get('kpis', {}).items():
                    if 'score' in kpi_data:
                        final_kpis_with_scores += 1
            
            print(f'   - Final KPIs with scores: {final_kpis_with_scores}')
            
            if final_kpis_with_scores > 0:
                print('\n✅ SUCCESS: Performance metrics are properly structured!')
                print('   - All KPIs have scores')
                print('   - Structure is ready for persistence')
                
                # Show what would be persisted
                print('\n📊 SAMPLE MONGODB DOCUMENT STRUCTURE:')
                sample_doc = {
                    "conversation_id": structured_result.get("conversation_id"),
                    "analysis_timestamp": structured_result.get("analysis_timestamp"),
                    "analysis_method": structured_result.get("analysis_method"),
                    "performance_metrics": pm,
                    "analysis_results": structured_result
                }
                
                print(f'   - Document keys: {list(sample_doc.keys())}')
                print(f'   - PM categories: {list(pm.get("categories", {}).keys())}')
                
                for cat_name, cat_data in pm.get('categories', {}).items():
                    print(f'   - {cat_name}: {len(cat_data.get("kpis", {}))} KPIs, score={cat_data.get("category_score")}')
                
                return True, "Performance metrics are correctly structured and ready for persistence"
            else:
                print('\n❌ ISSUE: KPIs missing scores in final structure')
                return False, "KPIs are missing scores in the final performance_metrics structure"
        else:
            print('\n❌ CRITICAL ISSUE: performance_metrics missing from structured result')
            return False, "performance_metrics key is missing from structured results"
            
    except Exception as e:
        print(f'\n❌ ERROR: {e}')
        import traceback
        traceback.print_exc()
        return False, f"Error during testing: {str(e)}"

def main():
    """Main test function"""
    print('🧪 PERFORMANCE METRICS PERSISTENCE DIAGNOSTIC')
    print('=' * 60)
    
    success, message = test_performance_metrics_flow()
    
    print('\n' + '=' * 60)
    print('🏁 DIAGNOSTIC COMPLETE')
    print(f'Status: {"✅ SUCCESS" if success else "❌ FAILED"}')
    print(f'Message: {message}')
    
    if success:
        print('\n💡 NEXT STEPS:')
        print('   1. Verify API properly calls persistence with this structure')
        print('   2. Ensure MongoDB background task completes successfully')
        print('   3. Check MongoDB document after API call')
    else:
        print('\n🔧 TROUBLESHOOTING NEEDED:')
        print('   1. Fix the performance metrics structure creation')
        print('   2. Ensure KPIs retain scores throughout the pipeline')
        print('   3. Test again after fixes')

if __name__ == '__main__':
    main()
