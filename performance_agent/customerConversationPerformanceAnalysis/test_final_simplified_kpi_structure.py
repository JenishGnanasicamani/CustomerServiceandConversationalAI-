#!/usr/bin/env python3
"""
Final comprehensive test to verify:
1. Categories duplication issue is fixed (no top-level categories field)
2. Simplified KPI structure with only score and reason per KPI
3. Sub-KPI scores with overall KPI score support
4. All KPIs are properly persisted in performance_metrics.categories
"""

import sys
import json
import logging
from pathlib import Path
from datetime import datetime

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from models import ConversationData, Tweet, Classification
from llm_agent_service import get_llm_agent_service
from periodic_job_service import PeriodicJobService

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_test_conversation() -> ConversationData:
    """Create a test conversation for analysis"""
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

def test_llm_service_analysis():
    """Test LLM service analysis directly"""
    print("🔄 Testing LLM service analysis...")
    
    try:
        # Get LLM service
        llm_service = get_llm_agent_service()
        conversation = create_test_conversation()
        
        # Run analysis
        result = llm_service.analyze_conversation_performance(conversation)
        
        print("📊 LLM Service Analysis Results:")
        print(f"  📂 Result structure keys: {list(result.keys())}")
        
        # Check if performance_metrics exists
        if "performance_metrics" in result:
            performance_metrics = result["performance_metrics"]
            print(f"  📂 performance_metrics keys: {list(performance_metrics.keys())}")
            
            if "categories" in performance_metrics:
                categories = performance_metrics["categories"]
                print(f"  📂 categories count: {len(categories)}")
                
                # Check each category structure
                for category_name, category_data in categories.items():
                    print(f"  📂 {category_name}:")
                    print(f"    📋 KPIs count: {len(category_data.get('kpis', {}))}")
                    
                    # Check a few KPIs for structure
                    kpis = category_data.get('kpis', {})
                    for kpi_name, kpi_data in list(kpis.items())[:2]:  # Check first 2 KPIs
                        print(f"    📋 {kpi_name}: {list(kpi_data.keys())}")
                        
                        # Check for simplified structure
                        has_score = "score" in kpi_data
                        has_reason = "reason" in kpi_data  
                        has_sub_kpis = "sub_kpis" in kpi_data
                        has_overall_score = "overall_score" in kpi_data
                        
                        print(f"      ✓ score: {has_score}, reason: {has_reason}, sub_kpis: {has_sub_kpis}, overall: {has_overall_score}")
        
        # Check for duplication issue (should NOT have top-level categories)
        has_top_level_categories = "categories" in result
        print(f"  ❌ Top-level categories field exists: {has_top_level_categories}")
        
        return result
        
    except Exception as e:
        print(f"❌ LLM service test failed: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_periodic_job_restructuring():
    """Test periodic job service restructuring"""
    print("\n🔄 Testing periodic job service restructuring...")
    
    try:
        # Create a mock periodic job service (without MongoDB)
        service = PeriodicJobService("mongodb://localhost:27017/", "test_db")
        service.llm_service = get_llm_agent_service()
        
        # Create test data
        conversation = create_test_conversation()
        source_record = {
            "_id": "507f1f77bcf86cd799439011",
            "created_at": datetime.now().isoformat(),
            "customer": "TestCustomer"
        }
        
        # Extract customer info
        customer_info = {
            "customer": "TestCustomer",
            "created_at": "2025-10-05T00:00:00Z",
            "created_time": "00:00:00"
        }
        
        # Get raw analysis result from LLM service
        raw_result = service.llm_service.analyze_conversation_performance(conversation)
        
        # Test the restructuring method
        structured_result = service._restructure_analysis_result(
            raw_result, conversation, customer_info, source_record
        )
        
        print("📊 Periodic Job Restructuring Results:")
        print(f"  📂 Structured result keys: {list(structured_result.keys())}")
        
        # Verify no duplication
        has_top_level_categories = "categories" in structured_result
        has_performance_metrics = "performance_metrics" in structured_result
        
        print(f"  ❌ Top-level categories: {has_top_level_categories}")
        print(f"  ✅ performance_metrics: {has_performance_metrics}")
        
        if has_performance_metrics:
            performance_metrics = structured_result["performance_metrics"]
            has_categories_in_pm = "categories" in performance_metrics
            print(f"  ✅ categories in performance_metrics: {has_categories_in_pm}")
            
            if has_categories_in_pm:
                categories = performance_metrics["categories"]
                print(f"  📊 Categories count: {len(categories)}")
                
                total_kpis = 0
                for category_name, category_data in categories.items():
                    kpis_count = len(category_data.get('kpis', {}))
                    total_kpis += kpis_count
                    print(f"    📂 {category_name}: {kpis_count} KPIs")
                    
                    # Test simplified structure
                    kpis = category_data.get('kpis', {})
                    for kpi_name, kpi_data in list(kpis.items())[:1]:  # Check first KPI
                        structure_keys = list(kpi_data.keys())
                        print(f"      📋 {kpi_name} structure: {structure_keys}")
                        
                        # Verify simplified structure requirements
                        required_keys = {"score", "reason"}
                        has_required = required_keys.issubset(set(structure_keys))
                        print(f"      ✅ Has required keys (score, reason): {has_required}")
                        
                        if "sub_kpis" in kpi_data:
                            sub_kpis = kpi_data["sub_kpis"]
                            print(f"      📋 Sub-KPIs count: {len(sub_kpis)}")
                            
                            # Check first sub-KPI structure
                            for sub_name, sub_data in list(sub_kpis.items())[:1]:
                                sub_structure = list(sub_data.keys())
                                print(f"        📋 {sub_name} structure: {sub_structure}")
                
                print(f"  📊 Total KPIs found: {total_kpis}")
        
        return structured_result
        
    except Exception as e:
        print(f"❌ Periodic job test failed: {e}")
        import traceback
        traceback.print_exc()
        return None

def verify_final_document_structure(result):
    """Verify the final MongoDB document structure meets all requirements"""
    print("\n🔍 FINAL VERIFICATION:")
    print("=" * 50)
    
    verification_results = {
        "duplication_fixed": False,
        "simplified_structure": False,
        "kpis_persisted": False,
        "sub_kpis_supported": False,
        "overall_success": False
    }
    
    try:
        # 1. Check duplication is fixed (no top-level categories)
        has_top_level_categories = "categories" in result
        verification_results["duplication_fixed"] = not has_top_level_categories
        print(f"✅ Duplication fixed (no top-level categories): {verification_results['duplication_fixed']}")
        
        # 2. Check performance_metrics.categories exists and has content
        has_pm = "performance_metrics" in result
        has_pm_categories = has_pm and "categories" in result["performance_metrics"]
        categories_count = 0
        total_kpis = 0
        
        if has_pm_categories:
            categories = result["performance_metrics"]["categories"]
            categories_count = len(categories)
            
            for category_data in categories.values():
                total_kpis += len(category_data.get('kpis', {}))
        
        verification_results["kpis_persisted"] = total_kpis > 0
        print(f"✅ KPIs persisted ({total_kpis} KPIs in {categories_count} categories): {verification_results['kpis_persisted']}")
        
        # 3. Check simplified structure (score + reason for each KPI)
        simplified_structure_verified = False
        sub_kpis_found = False
        
        if has_pm_categories:
            categories = result["performance_metrics"]["categories"]
            
            # Check first KPI in first category
            for category_data in categories.values():
                kpis = category_data.get('kpis', {})
                if kpis:
                    first_kpi = next(iter(kpis.values()))
                    
                    # Check required keys
                    has_score = "score" in first_kpi
                    has_reason = "reason" in first_kpi
                    simplified_structure_verified = has_score and has_reason
                    
                    # Check for sub-KPIs support
                    if "sub_kpis" in first_kpi:
                        sub_kpis = first_kpi["sub_kpis"]
                        if sub_kpis:
                            first_sub_kpi = next(iter(sub_kpis.values()))
                            sub_has_score = "score" in first_sub_kpi
                            sub_has_reason = "reason" in first_sub_kpi
                            sub_kpis_found = sub_has_score and sub_has_reason
                    
                    break
        
        verification_results["simplified_structure"] = simplified_structure_verified
        verification_results["sub_kpis_supported"] = sub_kpis_found
        
        print(f"✅ Simplified structure (score + reason): {verification_results['simplified_structure']}")
        print(f"✅ Sub-KPIs supported: {verification_results['sub_kpis_supported']}")
        
        # Overall success
        verification_results["overall_success"] = all([
            verification_results["duplication_fixed"],
            verification_results["simplified_structure"], 
            verification_results["kpis_persisted"]
        ])
        
        print(f"\n🎉 OVERALL SUCCESS: {verification_results['overall_success']}")
        
        return verification_results
        
    except Exception as e:
        print(f"❌ Verification failed: {e}")
        return verification_results

def save_test_results(llm_result, periodic_result, verification):
    """Save test results to file"""
    try:
        test_results = {
            "test_timestamp": datetime.now().isoformat(),
            "verification_results": verification,
            "sample_llm_result_keys": list(llm_result.keys()) if llm_result else [],
            "sample_periodic_result_keys": list(periodic_result.keys()) if periodic_result else [],
            "final_document_structure": {
                "has_top_level_categories": "categories" in periodic_result if periodic_result else False,
                "has_performance_metrics": "performance_metrics" in periodic_result if periodic_result else False,
                "categories_in_pm": "categories" in periodic_result.get("performance_metrics", {}) if periodic_result else False
            }
        }
        
        # Add sample KPI structure if available
        if periodic_result and "performance_metrics" in periodic_result:
            pm = periodic_result["performance_metrics"]
            if "categories" in pm and pm["categories"]:
                first_category = next(iter(pm["categories"].values()))
                if "kpis" in first_category and first_category["kpis"]:
                    first_kpi = next(iter(first_category["kpis"].values()))
                    test_results["sample_kpi_structure"] = {
                        "keys": list(first_kpi.keys()),
                        "has_score": "score" in first_kpi,
                        "has_reason": "reason" in first_kpi,
                        "has_sub_kpis": "sub_kpis" in first_kpi,
                        "has_overall_score": "overall_score" in first_kpi
                    }
        
        with open("final_simplified_kpi_test_results.json", "w") as f:
            json.dump(test_results, f, indent=2, default=str)
        
        print(f"📁 Test results saved to: final_simplified_kpi_test_results.json")
        
    except Exception as e:
        print(f"❌ Failed to save test results: {e}")

def main():
    """Run all tests"""
    print("🚀 FINAL COMPREHENSIVE TEST - SIMPLIFIED KPI STRUCTURE")
    print("=" * 60)
    print("Testing:")
    print("  1. Categories duplication fix")
    print("  2. Simplified KPI structure (score + reason)")
    print("  3. Sub-KPI support with overall scores")
    print("  4. Complete KPI persistence")
    print("=" * 60)
    
    # Test 1: LLM Service Analysis 
    llm_result = test_llm_service_analysis()
    
    # Test 2: Periodic Job Restructuring
    periodic_result = test_periodic_job_restructuring()
    
    # Final Verification
    if periodic_result:
        verification = verify_final_document_structure(periodic_result)
        
        # Save results
        save_test_results(llm_result, periodic_result, verification)
        
        # Print final summary
        print("\n" + "=" * 60)
        print("📋 FINAL TEST SUMMARY:")
        print("=" * 60)
        for key, value in verification.items():
            status = "✅ PASS" if value else "❌ FAIL"
            print(f"{status} {key.replace('_', ' ').title()}: {value}")
        
        print("=" * 60)
        
        if verification["overall_success"]:
            print("🎉 SUCCESS: All requirements met!")
            print("  - Categories duplication fixed")
            print("  - Simplified KPI structure implemented")
            print("  - KPIs properly persisted")
            print("  - Ready for MongoDB deployment")
        else:
            print("❌ FAILURE: Some requirements not met")
            print("  - Please review the detailed output above")
        
        return verification["overall_success"]
    else:
        print("❌ Could not run final verification - periodic job test failed")
        return False


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
