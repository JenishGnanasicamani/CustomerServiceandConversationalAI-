#!/usr/bin/env python3
"""
Test to verify complete removal of "No Evidence" behavior from all services
Tests both LLM agent service and periodic job service
"""

import json
import logging
from datetime import datetime
from pathlib import Path
import sys

# Add src directory to Python path
src_dir = Path(__file__).parent / "src"
sys.path.insert(0, str(src_dir))

from models import ConversationData, Tweet, Classification
from llm_agent_service import get_llm_agent_service
from periodic_job_service import PeriodicJobService

def test_complete_no_evidence_removal():
    """Test that 'No Evidence' behavior is completely removed from all services"""
    
    print("🧪 Testing complete removal of 'No Evidence' behavior...")
    
    # Create minimal conversation with very little evidence
    conversation_data = ConversationData(
        tweets=[
            Tweet(
                tweet_id=1001, 
                author_id="customer_1", 
                role="Customer", 
                inbound=True, 
                created_at="2024-01-01T10:00:00Z", 
                text="Hi"
            ),
            Tweet(
                tweet_id=1002, 
                author_id="agent_1", 
                role="Agent", 
                inbound=False, 
                created_at="2024-01-01T10:01:00Z", 
                text="Hello"
            )
        ],
        classification=Classification(
            categorization="General Inquiry",
            intent="Information",
            topic="General",
            sentiment="Neutral"
        )
    )
    
    test_results = {
        "test_timestamp": datetime.now().isoformat(),
        "llm_service_violations": [],
        "periodic_service_violations": [],
        "total_violations": 0,
        "test_passed": False
    }
    
    try:
        # Test 1: LLM Agent Service
        print("📊 Testing LLM Agent Service...")
        llm_service = get_llm_agent_service()
        llm_result = llm_service.analyze_conversation_comprehensive(conversation_data)
        
        # Check LLM service result for "No Evidence" violations
        llm_violations = check_no_evidence_violations(llm_result, "LLM Service")
        test_results["llm_service_violations"] = llm_violations
        
        # Test 2: Periodic Job Service (simulation mode)
        print("📊 Testing Periodic Job Service...")
        
        # Create mock source record
        mock_source_record = {
            "_id": "test_id_12345",
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
                        "text": "Hi"
                    },
                    {
                        "tweet_id": 1002,
                        "author_id": "agent_1",
                        "role": "Agent",
                        "inbound": False,
                        "created_at": "2024-01-01T10:01:00Z",
                        "text": "Hello"
                    }
                ]
            }
        }
        
        # Initialize periodic service in test mode (no MongoDB required)
        periodic_service = PeriodicJobService("mongodb://test", "test_db")
        
        # Test the analysis method directly (uses simulation when LLM unavailable)
        periodic_result = periodic_service.analyze_conversation_performance(conversation_data, mock_source_record)
        
        if periodic_result:
            # Check periodic service result for "No Evidence" violations
            periodic_violations = check_no_evidence_violations(periodic_result, "Periodic Service")
            test_results["periodic_service_violations"] = periodic_violations
        else:
            print("⚠️  Periodic service returned no result")
            test_results["periodic_service_violations"] = ["No result returned"]
        
        # Calculate total violations
        total_violations = len(test_results["llm_service_violations"]) + len(test_results["periodic_service_violations"])
        test_results["total_violations"] = total_violations
        test_results["test_passed"] = total_violations == 0
        
        # Print results
        print(f"\n📊 TEST RESULTS:")
        print(f"LLM Service Violations: {len(test_results['llm_service_violations'])}")
        print(f"Periodic Service Violations: {len(test_results['periodic_service_violations'])}")
        print(f"Total Violations: {total_violations}")
        
        if test_results["test_passed"]:
            print("✅ TEST PASSED: No 'No Evidence' violations found!")
        else:
            print("❌ TEST FAILED: 'No Evidence' violations still exist!")
            
            # Print violation details
            for violation in test_results["llm_service_violations"]:
                print(f"  🔥 LLM Service: {violation}")
            
            for violation in test_results["periodic_service_violations"]:
                print(f"  🔥 Periodic Service: {violation}")
        
        # Save detailed results
        with open("test_complete_no_evidence_removal_results.json", "w") as f:
            json.dump(test_results, f, indent=2, ensure_ascii=False)
        
        print(f"\n📄 Detailed results saved to: test_complete_no_evidence_removal_results.json")
        
        return test_results["test_passed"]
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        test_results["error"] = str(e)
        return False

def check_no_evidence_violations(result, service_name):
    """Check a result for 'No Evidence' violations"""
    violations = []
    
    def check_nested_dict(data, path=""):
        """Recursively check nested dictionaries"""
        if isinstance(data, dict):
            for key, value in data.items():
                current_path = f"{path}.{key}" if path else key
                
                # Check for "No Evidence" reasoning
                if key == "reason" and isinstance(value, str) and "No Evidence" in value:
                    violations.append(f"Found 'No Evidence' reason at {current_path}: {value}")
                
                if key == "reasoning" and isinstance(value, str) and "No Evidence" in value:
                    violations.append(f"Found 'No Evidence' reasoning at {current_path}: {value}")
                
                # Check for score = 10 with empty evidence (suspicious pattern)
                if key == "score" and value == 10:
                    # Look for corresponding evidence field
                    parent_dict = data
                    if "evidence" in parent_dict:
                        evidence = parent_dict["evidence"]
                        if not evidence or (isinstance(evidence, list) and len(evidence) == 0):
                            # Check if reason/reasoning contains "No Evidence"
                            reason = parent_dict.get("reason", parent_dict.get("reasoning", ""))
                            if "No Evidence" in str(reason):
                                violations.append(f"Found score=10 with 'No Evidence' pattern at {current_path}")
                
                # Recursively check nested structures
                check_nested_dict(value, current_path)
                
        elif isinstance(data, list):
            for i, item in enumerate(data):
                check_nested_dict(item, f"{path}[{i}]")
    
    check_nested_dict(result)
    return violations

if __name__ == "__main__":
    # Setup logging
    logging.basicConfig(level=logging.INFO)
    
    try:
        success = test_complete_no_evidence_removal()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"❌ Test execution failed: {e}")
        sys.exit(1)
