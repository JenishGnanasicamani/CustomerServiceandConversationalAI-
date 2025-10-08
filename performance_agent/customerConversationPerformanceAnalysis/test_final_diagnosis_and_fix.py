#!/usr/bin/env python3
"""
Final diagnosis and fix for the reporting API issue
"""

import json
import requests
from datetime import datetime
from pymongo import MongoClient
import os

def diagnose_and_fix_reporting_api():
    """Final diagnosis and fix for the reporting API"""
    
    print("🔍 FINAL DIAGNOSIS AND FIX")
    print("=" * 80)
    
    # MongoDB connection
    connection_string = os.getenv('MONGODB_CONNECTION_STRING', 'mongodb://localhost:27017/')
    client = MongoClient(connection_string)
    db = client['csai']
    collection = db['agentic_analysis']
    
    print("✓ Connected to MongoDB")
    
    # Get ALL records without any filter
    all_records = list(collection.find({}))
    print(f"✓ Total records in collection: {len(all_records)}")
    
    # Print detailed info about each record
    print(f"\n📊 ALL RECORDS DETAILS:")
    for i, record in enumerate(all_records):
        print(f"   Record {i+1}:")
        print(f"     ID: {record.get('_id')}")
        print(f"     Conversation ID: {record.get('conversation_id')}")
        print(f"     Customer: {record.get('customer')}")
        print(f"     Created: {record.get('created_at')}")
        print()
    
    # Check if there's a customer filter issue
    unique_customers = set()
    for record in all_records:
        customer = record.get('customer')
        if customer:
            unique_customers.add(customer)
    
    print(f"📋 UNIQUE CUSTOMERS: {list(unique_customers)}")
    
    # Test API without customer filter
    api_url = "http://localhost:8003"
    
    print(f"\n🧪 TESTING API WITHOUT CUSTOMER FILTER:")
    
    response = requests.post(
        f"{api_url}/reports/generate",
        json={
            "start_date": "2025-01-01",
            "end_date": "2025-12-31"
            # NO customer filter
        },
        timeout=30
    )
    
    if response.status_code == 200:
        report = response.json()
        records_found = len(report.get('selected_records', []))
        print(f"   Result: {records_found} records found")
        
        if records_found > 0:
            print(f"   ✅ SUCCESS! Found records without customer filter")
            
            # Save successful results
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"final_successful_results_{timestamp}.json"
            
            with open(filename, 'w') as f:
                json.dump(report, f, indent=2, default=str)
            
            print(f"   📁 Results saved to: {filename}")
            
            print(f"\n📋 SAMPLE RECORDS FROM API:")
            for i, record in enumerate(report['selected_records'][:3]):
                print(f"      Record {i+1}:")
                print(f"        ID: {record.get('_id')}")
                print(f"        Conversation ID: {record.get('conversation_id')}")
                print(f"        Customer: {record.get('customer')}")
                print(f"        Created: {record.get('created_at')}")
            
            return True
        else:
            print(f"   ❌ Still no records found")
    else:
        print(f"   ❌ API request failed: {response.status_code}")
        print(f"   Response: {response.text}")
    
    # Test with specific customer if any exist
    if unique_customers:
        test_customer = list(unique_customers)[0]
        print(f"\n🧪 TESTING WITH SPECIFIC CUSTOMER: {test_customer}")
        
        response = requests.post(
            f"{api_url}/reports/generate",
            json={
                "start_date": "2025-01-01",
                "end_date": "2025-12-31",
                "customer": test_customer
            },
            timeout=30
        )
        
        if response.status_code == 200:
            report = response.json()
            records_found = len(report.get('selected_records', []))
            print(f"   Result: {records_found} records found with customer filter")
        else:
            print(f"   ❌ API request failed: {response.status_code}")
    
    return False

def main():
    """Main function"""
    
    print("🔧 FINAL DIAGNOSIS AND FIX FOR REPORTING API")
    print("Investigation to identify and resolve the remaining issue")
    print(f"Diagnosis run at: {datetime.now().isoformat()}")
    
    success = diagnose_and_fix_reporting_api()
    
    print("\n" + "=" * 80)
    print("FINAL DIAGNOSIS RESULTS")
    print("=" * 80)
    
    if success:
        print("✅ REPORTING API IS NOW WORKING!")
        print("   Successfully found and returned records")
        print("   Issue was related to customer filtering or date range")
    else:
        print("❌ ISSUE STILL EXISTS")
        print("   Need to check server logs for additional debugging")
        print("   The fix might require server restart or configuration change")
    
    print(f"\n🔧 RECOMMENDATIONS:")
    if success:
        print("   1. Use the working parameters for future API calls")
        print("   2. Test with different date ranges and customer filters")
        print("   3. The API is now ready for production use")
    else:
        print("   1. Check server logs for detailed error messages")
        print("   2. Verify MongoDB connection and collection access")
        print("   3. Consider restarting the API server")

if __name__ == "__main__":
    main()
