#!/usr/bin/env python3
"""
Test script for data source configuration functionality
"""

import requests
import json
import os
from pathlib import Path

# Configuration
API_BASE_URL = "http://localhost:8003"
SAMPLE_DATA_FOLDER = Path(__file__).parent / "sample_sentiment_data"

def test_data_source_configuration():
    """Test the data source configuration endpoints"""
    
    print("🧪 Testing Data Source Configuration API")
    print("=" * 50)
    
    # Test 1: Get current configuration
    print("\n1️⃣ Getting current data source configuration...")
    try:
        response = requests.get(f"{API_BASE_URL}/config/datasource")
        if response.status_code == 200:
            config = response.json()
            print(f"✅ Current config: {json.dumps(config, indent=2)}")
        else:
            print(f"❌ Failed to get config: {response.status_code} - {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"❌ Connection error: {e}")
        return
    
    # Test 2: Configure file-based data source
    print("\n2️⃣ Configuring file-based data source...")
    
    # Create sample data folder if it doesn't exist
    SAMPLE_DATA_FOLDER.mkdir(exist_ok=True)
    
    # Create sample JSON file for testing
    sample_data = [
        {
            "conversation_id": "conv_test_001",
            "customer": "test_customer_123",
            "created_at": "2023-06-15T10:30:00Z",
            "conversation_summary": {
                "final_sentiment": "Positive",
                "intent": "Technical Support",
                "topic": "Account Issues",
                "total_messages": 4
            },
            "performance_metrics": {
                "accuracy_compliance": {
                    "resolution_completeness": 0.95,
                    "accuracy_automated_responses": 92.5
                },
                "empathy_communication": {
                    "empathy_score": 8.2,
                    "sentiment_shift": 0.6,
                    "clarity_language": 8.8,
                    "cultural_sensitivity": 4.1,
                    "adaptability_quotient": 84,
                    "conversation_flow": 4.2
                },
                "efficiency_resolution": {
                    "followup_necessity": 0,
                    "customer_effort_score": 2.3,
                    "first_response_accuracy": 93.0,
                    "csat_resolution": 4.7,
                    "escalation_rate": 2.5,
                    "customer_effort_reduction": 16.8
                }
            }
        },
        {
            "conversation_id": "conv_test_002", 
            "customer": "test_customer_123",
            "created_at": "2023-06-16T14:15:00Z",
            "conversation_summary": {
                "final_sentiment": "Neutral",
                "intent": "Billing Inquiry",
                "topic": "Payment Issues",
                "total_messages": 6
            },
            "performance_metrics": {
                "accuracy_compliance": {
                    "resolution_completeness": 0.88,
                    "accuracy_automated_responses": 87.2
                },
                "empathy_communication": {
                    "empathy_score": 7.1,
                    "sentiment_shift": 0.1,
                    "clarity_language": 7.9,
                    "cultural_sensitivity": 3.8,
                    "adaptability_quotient": 76,
                    "conversation_flow": 3.7
                },
                "efficiency_resolution": {
                    "followup_necessity": 1,
                    "customer_effort_score": 3.1,
                    "first_response_accuracy": 84.0,
                    "csat_resolution": 4.0,
                    "escalation_rate": 8.5,
                    "customer_effort_reduction": 4.2
                }
            }
        }
    ]
    
    sample_file = SAMPLE_DATA_FOLDER / "test_sentiment_data.json"
    with open(sample_file, 'w') as f:
        json.dump(sample_data, f, indent=2)
    
    print(f"📁 Created sample data file: {sample_file}")
    
    try:
        config_request = {
            "source_type": "file",
            "file_path": str(SAMPLE_DATA_FOLDER)
        }
        
        response = requests.post(
            f"{API_BASE_URL}/config/datasource",
            json=config_request
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ File source configured: {json.dumps(result, indent=2)}")
        else:
            print(f"❌ Failed to configure file source: {response.status_code} - {response.text}")
            return
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Connection error: {e}")
        return
    
    # Test 3: Generate report using file data
    print("\n3️⃣ Generating report using file-based data...")
    
    try:
        report_request = {
            "start_date": "2023-06-01",
            "end_date": "2023-06-30",
            "customer": "test_customer_123"
        }
        
        response = requests.post(
            f"{API_BASE_URL}/reports/generate",
            json=report_request
        )
        
        if response.status_code == 200:
            report = response.json()
            print(f"✅ Report generated from file data:")
            print(f"   📊 Records found: {report['query_parameters']['records_found']}")
            print(f"   📈 Total conversations: {report['aggregated_insights']['total_conversations']}")
            print(f"   😊 Sentiment distribution: {report['aggregated_insights']['sentiment_distribution']}")
            print(f"   🎯 Intent distribution: {report['aggregated_insights']['intent_distribution']}")
            print(f"   📝 Summary insights: {len(report['summary']['what_went_well'])} positive points")
        else:
            print(f"❌ Failed to generate report: {response.status_code} - {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Connection error: {e}")
    
    # Test 4: Switch back to MongoDB
    print("\n4️⃣ Switching back to MongoDB data source...")
    
    try:
        config_request = {
            "source_type": "mongodb",
            "collection_name": "agentic_analysis"
        }
        
        response = requests.post(
            f"{API_BASE_URL}/config/datasource",
            json=config_request
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ MongoDB source configured: {json.dumps(result, indent=2)}")
        else:
            print(f"❌ Failed to configure MongoDB source: {response.status_code} - {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Connection error: {e}")
    
    # Test 5: Final configuration check
    print("\n5️⃣ Final configuration verification...")
    
    try:
        response = requests.get(f"{API_BASE_URL}/config/datasource")
        if response.status_code == 200:
            config = response.json()
            print(f"✅ Final config: {json.dumps(config, indent=2)}")
        else:
            print(f"❌ Failed to get final config: {response.status_code} - {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"❌ Connection error: {e}")
    
    print("\n🎉 Data source configuration testing completed!")
    print(f"🗂️  Sample data remains at: {SAMPLE_DATA_FOLDER}")

def show_usage_examples():
    """Show usage examples for the new endpoints"""
    
    print("\n📖 Usage Examples")
    print("=" * 50)
    
    print("\n🔧 Configure File Data Source:")
    print("POST /config/datasource")
    print(json.dumps({
        "source_type": "file",
        "file_path": "/path/to/sentiment/data/folder"
    }, indent=2))
    
    print("\n🔧 Configure MongoDB Data Source:")
    print("POST /config/datasource")
    print(json.dumps({
        "source_type": "mongodb",
        "collection_name": "custom_analysis_collection"
    }, indent=2))
    
    print("\n📋 Get Current Configuration:")
    print("GET /config/datasource")
    
    print("\n📊 Generate Report (works with any configured source):")
    print("POST /reports/generate")
    print(json.dumps({
        "start_date": "2023-01-01",
        "end_date": "2023-01-31",
        "customer": "customer_123"
    }, indent=2))

if __name__ == "__main__":
    print("🚀 Starting Data Source Configuration Test")
    
    # Check if API is running
    try:
        response = requests.get(f"{API_BASE_URL}/health")
        if response.status_code == 200:
            print("✅ API is running and healthy")
        else:
            print("⚠️  API is running but may have issues")
    except requests.exceptions.RequestException:
        print("❌ API is not running. Please start the reporting API first:")
        print("   python run_reporting_api.py")
        exit(1)
    
    # Run tests
    test_data_source_configuration()
    
    # Show usage examples
    show_usage_examples()
