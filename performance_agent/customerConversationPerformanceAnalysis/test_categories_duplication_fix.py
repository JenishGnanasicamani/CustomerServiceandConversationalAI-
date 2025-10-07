#!/usr/bin/env python3
"""
Test script to verify that the categories duplication issue has been resolved.

This test ensures that:
1. KPI data exists in performance_metrics.categories
2. There is NO duplicate top-level categories field
3. The MongoDB document structure is clean and efficient
"""

import json
import logging
import sys
from datetime import datetime
from pathlib import Path

# Add src directory to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from llm_agent_service import get_llm_agent_service
from periodic_job_service import PeriodicJobService
from models import ConversationData, Tweet, Classification

def setup_logging():
    logging.basicConfig(level=logging.INFO)
    return logging.getLogger(__name__)

def create_test_conversation_data():
    """Create sample conversation data for testing"""
    tweets = [
        Tweet(
            tweet_id=1,
            author_id="customer123",
            role="Customer",
            inbound=True,
            created_at="2025-10-05T00:00:00Z",
            text="I'm having trouble accessing my account. Can you help?"
        ),
        Tweet(
            tweet_id=2,
            author_id="agent456",
            role="Agent",
            inbound=False,
            created_at="2025-10-05T00:01:00Z",
            text="I'd be happy to help you with your account access issue. Let me check your account details."
        ),
        Tweet(
            tweet_id=3,
            author_id="customer123",
            role="Customer",
            inbound=True,
            created_at="2025-10-05T00:02:00Z",
            text="Thank you! I've been locked out since yesterday."
        ),
        Tweet(
            tweet_id=4,
            author_id="agent456",
            role="Agent",
            inbound=False,
            created_at="2025-10-05T00:03:00Z",
            text="I can see the issue. I've reset your account and sent you a new temporary password. You should be able to log in now."
        )
    ]
    
    classification = Classification(
        categorization="Technical Support",
        intent="Account Access",
        topic="Login Issues",
        sentiment="Neutral"
    )
    
    return ConversationData(tweets=tweets, classification=classification)

def test_categories_duplication_fix():
    """Test that categories duplication has been resolved"""
    logger = setup_logging()
    
    print("TESTING CATEGORIES DUPLICATION FIX")
    print("=" * 70)
    
    try:
        # Initialize services
        print("✅ Initializing services...")
        llm_service = get_llm_agent_service()
        
        # Create test data
        print("✅ Creating test conversation data...")
        conversation_data = create_test_conversation_data()
        
        # Create a mock source record
        source_record = {
            '_id': "test_object_id_67890",
            'customer': 'TestCustomer',
            'created_at': '2025-10-05T00:00:00Z',
            'created_time': '00:00:00'
        }
        
        # Run analysis
        print("🔄 Running comprehensive analysis...")
        raw_analysis_result = llm_service.analyze_conversation_comprehensive(conversation_data)
        
        # Create periodic job service to test restructuring
        service = PeriodicJobService("mongodb://localhost:27017/", "test_db")
        
        # Extract customer info
        customer_info = {
            "customer": "TestCustomer",
            "created_at": "2025-10-05T00:00:00Z",
            "created_time": "00:00:00"
        }
        
        # Test the restructuring method
        print("🔄 Testing result restructuring...")
        structured_result = service._restructure_analysis_result(
            raw_analysis_result,
            conversation_data,
            customer_info,
            source_record
        )
        
        print("✅ Analysis completed - testing result structure...")
        
        # VERIFICATION TESTS
        print("\n📊 DUPLICATION FIX VERIFICATION:")
        print("-" * 50)
        
        # Test 1: Check if performance_metrics.categories exists and has KPI data
        has_performance_metrics_categories = (
            "performance_metrics" in structured_result and
            "categories" in structured_result["performance_metrics"] and
            len(structured_result["performance_metrics"]["categories"]) > 0
        )
        
        # Test 2: Check if top-level categories field exists (should NOT exist)
        has_top_level_categories = "categories" in structured_result
        
        # Test 3: Count KPIs in performance_metrics.categories
        kpi_count_in_performance_metrics = 0
        if has_performance_metrics_categories:
            for category_data in structured_result["performance_metrics"]["categories"].values():
                if "kpis" in category_data:
                    kpi_count_in_performance_metrics += len(category_data["kpis"])
        
        # Results
        print(f"📂 performance_metrics.categories exists: {'✅' if has_performance_metrics_categories else '❌'}")
        print(f"📂 performance_metrics.categories KPI count: {kpi_count_in_performance_metrics}")
        print(f"📂 top-level categories field exists: {'❌ (DUPLICATE!)' if has_top_level_categories else '✅ (REMOVED)'}")
        
        # Detailed structure analysis
        if has_performance_metrics_categories:
            print(f"\n📋 PERFORMANCE METRICS STRUCTURE:")
            for category_name, category_data in structured_result["performance_metrics"]["categories"].items():
                kpi_count = len(category_data.get("kpis", {}))
                print(f"  📂 {category_name}: {kpi_count} KPIs")
                for kpi_name, kpi_data in category_data.get("kpis", {}).items():
                    score = kpi_data.get("score", "N/A")
                    print(f"    📋 {kpi_name}: {score}")
        
        # Final assessment
        duplication_fixed = has_performance_metrics_categories and not has_top_level_categories and kpi_count_in_performance_metrics > 0
        
        print(f"\n📁 Test result saved to: categories_duplication_fix_verification.json")
        
        # Save test results
        test_results = {
            "test_timestamp": datetime.now().isoformat(),
            "duplication_fix_verification": {
                "performance_metrics_categories_exists": has_performance_metrics_categories,
                "performance_metrics_kpi_count": kpi_count_in_performance_metrics,
                "top_level_categories_exists": has_top_level_categories,
                "duplication_fixed": duplication_fixed
            },
            "structured_result_keys": list(structured_result.keys()),
            "performance_metrics_keys": list(structured_result.get("performance_metrics", {}).keys()) if "performance_metrics" in structured_result else [],
            "sample_structure": {
                k: type(v).__name__ for k, v in structured_result.items()
            }
        }
        
        with open("categories_duplication_fix_verification.json", "w") as f:
            json.dump(test_results, f, indent=2, default=str, ensure_ascii=False)
        
        # Final result
        if duplication_fixed:
            print(f"\n🎉 CATEGORIES DUPLICATION FIX VERIFICATION: PASSED!")
            print(f"✅ KPI data exists only in performance_metrics.categories")
            print(f"✅ No duplicate top-level categories field")
            print(f"✅ Clean, efficient MongoDB document structure")
            print(f"✅ Categories duplication issue has been resolved!")
            return True
        else:
            print(f"\n❌ CATEGORIES DUPLICATION FIX VERIFICATION: FAILED!")
            if not has_performance_metrics_categories:
                print(f"❌ performance_metrics.categories missing or empty")
            if has_top_level_categories:
                print(f"❌ Duplicate top-level categories field still exists")
            if kpi_count_in_performance_metrics == 0:
                print(f"❌ No KPI data found in performance_metrics.categories")
            return False
            
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_categories_duplication_fix()
    exit(0 if success else 1)
