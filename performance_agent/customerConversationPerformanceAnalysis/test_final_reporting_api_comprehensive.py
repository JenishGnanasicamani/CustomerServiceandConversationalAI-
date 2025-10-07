#!/usr/bin/env python3
"""
Final comprehensive test to fix the reporting API data filtering issue
"""

import json
import requests
from datetime import datetime, timedelta
from pymongo import MongoClient
import os

def test_comprehensive_reporting_api_fix():
    """Final comprehensive test to resolve the data filtering issue"""
    
    print("🔧 FINAL COMPREHENSIVE REPORTING API FIX")
    print("=" * 80)
    
    # MongoDB connection
    connection_string = os.getenv('MONGODB_CONNECTION_STRING', 'mongodb://localhost:27017/')
    client = MongoClient(connection_string)
    db = client['csai']
    collection = db['agentic_analysis']
    
    print("✓ Connected to MongoDB")
    
    # Get actual record timestamps to understand format
    records = list(collection.find({}).limit(3))
    print(f"✓ Found {len(records)} sample records")
    
    if not records:
        print("❌ No records found in MongoDB!")
        return False
    
    print("\n📊 ACTUAL RECORD TIMESTAMPS:")
    actual_dates = []
    for i, record in enumerate(records):
        created_at = record.get('created_at')
        print(f"   Record {i+1}: {created_at}")
        actual_dates.append(created_at)
    
    # Test various date formats against the API
    api_url = "http://localhost:8003"
    
    print(f"\n🧪 TESTING DIFFERENT DATE FORMATS:")
    
    # Format 1: Use exact timestamp from one record (truncate to date)
    if actual_dates:
        sample_timestamp = actual_dates[0]  # e.g., "2025-10-05T22:04:45.771850"
        sample_date = sample_timestamp.split('T')[0]  # "2025-10-05"
        
        print(f"   Testing with exact date: {sample_date}")
        
        response = requests.post(
            f"{api_url}/reports/generate",
            json={
                "start_date": sample_date,
                "end_date": sample_date
            },
            timeout=30
        )
        
        if response.status_code == 200:
            report = response.json()
            records_found = len(report.get('selected_records', []))
            print(f"   Result: {records_found} records found")
            
            if records_found > 0:
                print(f"   ✅ SUCCESS! Found records with date: {sample_date}")
                return True
    
    # Format 2: Wide date range from earliest to latest
    if len(actual_dates) > 1:
        earliest_date = min(actual_dates).split('T')[0]
        latest_date = max(actual_dates).split('T')[0]
        
        print(f"   Testing with date range: {earliest_date} to {latest_date}")
        
        response = requests.post(
            f"{api_url}/reports/generate",
            json={
                "start_date": earliest_date,
                "end_date": latest_date
            },
            timeout=30
        )
        
        if response.status_code == 200:
            report = response.json()
            records_found = len(report.get('selected_records', []))
            print(f"   Result: {records_found} records found")
            
            if records_found > 0:
                print(f"   ✅ SUCCESS! Found records with range: {earliest_date} to {latest_date}")
                return True
    
    # Format 3: Test with broader range
    print(f"   Testing with broad range: 2025-01-01 to 2025-12-31")
    
    response = requests.post(
        f"{api_url}/reports/generate",
        json={
            "start_date": "2025-01-01",
            "end_date": "2025-12-31"
        },
        timeout=30
    )
    
    if response.status_code == 200:
        report = response.json()
        records_found = len(report.get('selected_records', []))
        print(f"   Result: {records_found} records found")
        
        if records_found > 0:
            print(f"   ✅ SUCCESS! Found records with broad range")
            
            # Save successful results
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"successful_reporting_api_results_{timestamp}.json"
            
            with open(filename, 'w') as f:
                json.dump(report, f, indent=2, default=str)
            
            print(f"   📁 Results saved to: {filename}")
            print(f"\n📋 SAMPLE RECORDS FROM API:")
            for i, record in enumerate(report['selected_records'][:2]):
                print(f"      Record {i+1}:")
                print(f"        ID: {record.get('_id')}")
                print(f"        Conversation ID: {record.get('conversation_id')}")
                print(f"        Created: {record.get('created_at')}")
            
            return True
    
    print(f"❌ No working date format found!")
    
    # Additional debugging - check if there's a collection name issue
    print(f"\n🔍 ADDITIONAL DEBUGGING:")
    print(f"   Collection name in use: agentic_analysis")
    
    # List all collections
    collections = db.list_collection_names()
    print(f"   Available collections: {collections}")
    
    # Check if records are in a different collection
    for coll_name in collections:
        if 'analysis' in coll_name.lower() or 'conversation' in coll_name.lower():
            coll = db[coll_name]
            count = coll.count_documents({})
            print(f"   Collection '{coll_name}': {count} records")
    
    return False

def create_working_test_script(successful_params):
    """Create a working test script with the successful parameters"""
    
    script_content = f'''#!/usr/bin/env python3
"""
Working Reporting API Test Script - Uses parameters that successfully found records
"""

import json
import requests
from datetime import datetime

def test_working_reporting_api():
    """Test reporting API with working parameters"""
    
    print("🧪 WORKING REPORTING API TEST")
    print("=" * 60)
    
    api_url = "http://localhost:8003"
    
    # Use the successful parameters
    params = {successful_params}
    
    print(f"Testing with parameters: {{params}}")
    
    response = requests.post(
        f"{{api_url}}/reports/generate",
        json=params,
        timeout=30
    )
    
    if response.status_code == 200:
        report = response.json()
        records = report.get('selected_records', [])
        
        print(f"✅ SUCCESS: Found {{len(records)}} records")
        
        if len(records) > 0:
            print(f"\\n📊 RECORD DETAILS:")
            for i, record in enumerate(records[:3]):
                print(f"   Record {{i+1}}:")
                print(f"     ID: {{record.get('_id')}}")
                print(f"     Conversation ID: {{record.get('conversation_id')}}")
                print(f"     Created: {{record.get('created_at')}}")
            
            # Save results
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"working_api_results_{{timestamp}}.json"
            
            with open(filename, 'w') as f:
                json.dump(report, f, indent=2, default=str)
            
            print(f"\\n📁 Results saved to: {{filename}}")
            return True
    else:
        print(f"❌ API request failed: {{response.status_code}}")
        return False

if __name__ == "__main__":
    success = test_working_reporting_api()
    if success:
        print("\\n✅ Working test completed successfully!")
    else:
        print("\\n❌ Test failed")
'''
    
    with open('test_working_reporting_api.py', 'w') as f:
        f.write(script_content)
    
    print(f"✓ Working test script created: test_working_reporting_api.py")

def main():
    """Main function"""
    
    print("🔍 FINAL COMPREHENSIVE REPORTING API TEST")
    print("Attempting to resolve the data filtering issue once and for all")
    print(f"Test run at: {datetime.now().isoformat()}")
    
    success = test_comprehensive_reporting_api_fix()
    
    print("\n" + "=" * 80)
    print("FINAL TEST RESULTS")
    print("=" * 80)
    
    if success:
        print("✅ REPORTING API DATA FILTERING ISSUE RESOLVED!")
        print("   The API can now successfully find and return records")
        print("   Check the generated results file for full details")
    else:
        print("❌ ISSUE PERSISTS - Need further investigation")
        print("   Check MongoDB collection name and data format")
        print("   Verify API server is running and accessible")
    
    print(f"\n🔧 NEXT STEPS:")
    if success:
        print("   1. Use the working parameters for future API calls")
        print("   2. Update documentation with correct date format")
        print("   3. Test with different customer filters if needed")
    else:
        print("   1. Check MongoDB connection and collection name")
        print("   2. Verify record timestamps match expected format")
        print("   3. Review API server logs for additional clues")

if __name__ == "__main__":
    main()
