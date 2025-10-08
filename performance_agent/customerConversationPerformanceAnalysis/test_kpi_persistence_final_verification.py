#!/usr/bin/env python3
"""
Final verification test for KPI persistence fix
This test verifies that both 'performance_metrics' and 'categories' fields contain KPI data
"""

import sys
import os
import json
import logging
from datetime import datetime

# Add src directory to Python path
sys.path.insert(0, 'src')

def test_kpi_persistence_fix():
    """Test that the KPI persistence fix works correctly"""
    print("🔍 TESTING KPI PERSISTENCE FIX")
    print("=" * 70)
    
    try:
        # Import the necessary components
        from llm_agent_service import get_llm_agent_service
        from models import ConversationData, Tweet, Classification
        from periodic_job_service import PeriodicJobService
        
        # Initialize services
        print("✅ Initializing services...")
        llm_service = get_llm_agent_service()
        
        # Create sample conversation data
        sample_conversation = ConversationData(
            tweets=[
                Tweet(
                    tweet_id=1,
                    author_id="customer123",
                    role="Customer",
                    inbound=True,
                    created_at="2025-10-05T00:00:00Z",
                    text="Hello, I need help with my account login issue."
                ),
                Tweet(
                    tweet_id=2,
                    author_id="agent456",
                    role="Agent",
                    inbound=False,
                    created_at="2025-10-05T00:01:00Z",
                    text="I'd be happy to help you with your login issue. Let me check your account."
                )
            ],
            classification=Classification(
                categorization="Technical Support",
                intent="Account Access",
                topic="Login Issues",
                sentiment="Neutral"
            )
        )
        
        print("✅ Sample conversation data created")
        
        # Analyze conversation to get raw results
        print("🔄 Running comprehensive analysis...")
        raw_analysis_result = llm_service.analyze_conversation_comprehensive(sample_conversation)
        
        print(f"✅ Analysis completed - found {len(raw_analysis_result.get('categories', {}))} categories")
        
        # Create mock periodic job service to test restructuring
        print("🔄 Testing result restructuring...")
        periodic_service = PeriodicJobService("mongodb://localhost:27017/", "test_db")
        
        # Mock customer info and source record
        customer_info = {
            "customer": "TestCustomer",
            "created_at": "2025-10-05T00:00:00Z",
            "created_time": "00:00:00"
        }
        
        source_record = {
            "_id": "test_object_id_12345",
            "created_at": "2025-10-05T00:00:00Z"
        }
        
        # Test the restructuring method
        restructured_result = periodic_service._restructure_analysis_result(
            raw_analysis_result,
            sample_conversation,
            customer_info,
            source_record
        )
        
        print("✅ Result restructuring completed")
        
        # Verify the fix
        print("\n📊 VERIFICATION RESULTS:")
        print("-" * 50)
        
        # Check performance_metrics field
        performance_metrics = restructured_result.get("performance_metrics", {})
        pm_categories = performance_metrics.get("categories", {})
        pm_kpi_count = sum(len(cat.get("kpis", {})) for cat in pm_categories.values())
        
        print(f"📂 performance_metrics.categories: {len(pm_categories)} categories, {pm_kpi_count} KPIs")
        
        # Check top-level categories field
        top_level_categories = restructured_result.get("categories", {})
        tl_kpi_count = sum(len(cat.get("kpis", {})) for cat in top_level_categories.values())
        
        print(f"📂 top-level categories: {len(top_level_categories)} categories, {tl_kpi_count} KPIs")
        
        # Detailed verification
        success = True
        
        if pm_kpi_count == 0:
            print("❌ CRITICAL: performance_metrics.categories has no KPIs!")
            success = False
        else:
            print(f"✅ performance_metrics.categories contains {pm_kpi_count} KPIs")
        
        if tl_kpi_count == 0:
            print("❌ CRITICAL: top-level categories field is empty!")
            success = False
        else:
            print(f"✅ top-level categories field contains {tl_kpi_count} KPIs")
        
        if pm_kpi_count != tl_kpi_count:
            print("❌ WARNING: KPI count mismatch between performance_metrics and categories fields!")
            success = False
        else:
            print("✅ KPI counts match between both fields")
        
        # Check specific KPI data
        print("\n📋 KPI DETAILS:")
        for cat_name, cat_data in pm_categories.items():
            kpis = cat_data.get("kpis", {})
            print(f"  📂 {cat_name}: {len(kpis)} KPIs")
            for kpi_name, kpi_data in kpis.items():
                score = kpi_data.get("score", "N/A")
                print(f"    📋 {kpi_name}: {score}")
        
        # Save test result for inspection
        test_result = {
            "test_timestamp": datetime.now().isoformat(),
            "restructured_result": restructured_result,
            "verification": {
                "performance_metrics_kpi_count": pm_kpi_count,
                "top_level_categories_kpi_count": tl_kpi_count,
                "kpi_counts_match": pm_kpi_count == tl_kpi_count,
                "success": success
            }
        }
        
        with open('kpi_persistence_fix_verification.json', 'w') as f:
            json.dump(test_result, f, indent=2, default=str)
        
        print(f"\n📁 Test result saved to: kpi_persistence_fix_verification.json")
        
        if success:
            print("\n🎉 KPI PERSISTENCE FIX VERIFICATION: PASSED!")
            print("✅ Both performance_metrics.categories and top-level categories contain KPI data")
            print("✅ The original issue is RESOLVED")
        else:
            print("\n❌ KPI PERSISTENCE FIX VERIFICATION: FAILED!")
            print("⚠️  Fix needs additional work")
        
        return success
        
    except Exception as e:
        print(f"\n❌ VERIFICATION TEST ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run the verification test"""
    logging.basicConfig(level=logging.INFO, format='%(levelname)s:%(name)s:%(message)s')
    
    success = test_kpi_persistence_fix()
    
    if success:
        print("\n✅ KPI persistence issue has been successfully resolved!")
    else:
        print("\n❌ KPI persistence issue still exists - additional work needed")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
