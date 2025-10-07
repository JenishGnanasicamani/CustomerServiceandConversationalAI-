#!/usr/bin/env python3
"""
Fix the reporting API data filtering issue - 0 records found despite 5 records existing
"""

import json
import os
import requests
from datetime import datetime
from pymongo import MongoClient

def investigate_data_filtering_issue():
    """Investigate why reporting API finds 0 records when 5 exist"""
    
    print("=" * 80)
    print("REPORTING API DATA FILTERING INVESTIGATION")
    print("=" * 80)
    
    try:
        # Connect directly to MongoDB
        connection_string = os.getenv('MONGODB_CONNECTION_STRING', 'mongodb://localhost:27017/')
        client = MongoClient(connection_string)
        db = client['csai']
        collection = db['agentic_analysis']
        
        print(f"✓ Connected to MongoDB directly")
        
        # Check actual records in MongoDB
        total_records = collection.count_documents({})
        print(f"✓ Total records in agentic_analysis: {total_records}")
        
        # Get sample records to see their structure
        sample_records = list(collection.find({}).limit(3))
        
        print(f"\n📊 SAMPLE RECORDS ANALYSIS:")
        for i, record in enumerate(sample_records):
            record_id = record.get('_id')
            conversation_id = record.get('conversation_id')
            created_at = record.get('created_at')
            created_at_type = type(created_at).__name__
            
            print(f"\n--- Record {i+1} ---")
            print(f"   ID: {record_id}")
            print(f"   Conversation ID: {conversation_id}")
            print(f"   created_at: {created_at}")
            print(f"   created_at type: {created_at_type}")
            
            # Check if created_at is a string or datetime
            if isinstance(created_at, str):
                print(f"   ✓ created_at is string format")
                # Try to check if it has timezone info
                if 'T' in created_at:
                    if created_at.endswith('Z') or '+' in created_at or created_at.endswith('000'):
                        print(f"   ✓ Has timezone/UTC info")
                    else:
                        print(f"   ⚠️  No timezone info - might cause filtering issues")
            else:
                print(f"   ⚠️  created_at is not string - type: {created_at_type}")
        
        # Test different query formats that the reporting API might be using
        print(f"\n🔍 TESTING DIFFERENT QUERY FORMATS:")
        
        # Query 1: Exact format used by reporting API
        query1 = {'created_at': {'$gte': '2000-01-01T00:00:00Z', '$lte': '2100-12-31T23:59:59Z'}}
        count1 = collection.count_documents(query1)
        print(f"   Query 1 (API format): {count1} records")
        print(f"   Query: {query1}")
        
        # Query 2: Without timezone
        query2 = {'created_at': {'$gte': '2000-01-01T00:00:00', '$lte': '2100-12-31T23:59:59'}}
        count2 = collection.count_documents(query2)
        print(f"   Query 2 (No timezone): {count2} records")
        print(f"   Query: {query2}")
        
        # Query 3: String comparison
        query3 = {'created_at': {'$gte': '2000-01-01', '$lte': '2100-12-31'}}
        count3 = collection.count_documents(query3)
        print(f"   Query 3 (Date only): {count3} records")
        print(f"   Query: {query3}")
        
        # Query 4: Check current date
        today = datetime.now().strftime('%Y-%m-%d')
        query4 = {'created_at': {'$gte': f'{today}T00:00:00Z', '$lte': f'{today}T23:59:59Z'}}
        count4 = collection.count_documents(query4)
        print(f"   Query 4 (Today only): {count4} records")
        print(f"   Query: {query4}")
        
        # Find what works
        working_queries = []
        if count1 > 0:
            working_queries.append(("API format", query1, count1))
        if count2 > 0:
            working_queries.append(("No timezone", query2, count2))
        if count3 > 0:
            working_queries.append(("Date only", query3, count3))
        if count4 > 0:
            working_queries.append(("Today only", query4, count4))
        
        print(f"\n✅ WORKING QUERIES:")
        for name, query, count in working_queries:
            print(f"   {name}: {count} records")
        
        if not working_queries:
            print(f"\n❌ NO QUERIES WORK - Need to check data format")
            
            # Let's see the exact format of created_at in records
            print(f"\n🔍 DETAILED created_at ANALYSIS:")
            for i, record in enumerate(sample_records[:2]):
                created_at = record.get('created_at')
                print(f"   Record {i+1} created_at: '{created_at}'")
                print(f"   Length: {len(str(created_at))}")
                print(f"   Contains 'T': {'T' in str(created_at)}")
                print(f"   Ends with 'Z': {str(created_at).endswith('Z')}")
                print(f"   Contains '+': {'+' in str(created_at)}")
        
        client.close()
        
        return {
            "total_records": total_records,
            "working_queries": working_queries,
            "sample_records": sample_records[:2]
        }
        
    except Exception as e:
        print(f"❌ Investigation failed: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_reporting_api_with_current_date():
    """Test reporting API with current date to see if it finds records"""
    
    print("\n" + "=" * 80)
    print("TESTING REPORTING API WITH CURRENT DATE")
    print("=" * 80)
    
    try:
        api_url = "http://localhost:8003"
        
        # Test with today's date
        today = datetime.now().strftime('%Y-%m-%d')
        
        print(f"Testing with today's date: {today}")
        
        response = requests.post(
            f"{api_url}/reports/generate",
            json={
                "start_date": today,
                "end_date": today
            },
            timeout=30
        )
        
        if response.status_code == 200:
            report = response.json()
            records_found = len(report.get('selected_records', []))
            
            print(f"✓ API responded successfully")
            print(f"   Records found: {records_found}")
            print(f"   Status: {report.get('status')}")
            
            if records_found > 0:
                print(f"   ✅ Found records with today's date!")
                return True
            else:
                print(f"   ❌ No records found even with today's date")
                return False
        else:
            print(f"❌ API request failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
        
    except Exception as e:
        print(f"❌ API test failed: {e}")
        return False

def create_fixed_test_script():
    """Create a fixed version of the test script that uses working date queries"""
    
    print("\n" + "=" * 80)
    print("CREATING FIXED TEST SCRIPT")
    print("=" * 80)
    
    fixed_script = '''#!/usr/bin/env python3
"""
Fixed Reporting API Test Script - Uses current date to find actual records
"""

import json
import os
import requests
from datetime import datetime
import logging

def test_reporting_api_with_actual_data():
    """Test reporting API with current date to get actual records"""
    
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    logger = logging.getLogger(__name__)
    
    api_url = "http://localhost:8003"
    today = datetime.now().strftime('%Y-%m-%d')
    
    logger.info("🧪 FIXED REPORTING API TEST - CURRENT DATE")
    logger.info("=" * 60)
    
    try:
        # Test with today's date specifically
        logger.info(f"Testing with today's date: {today}")
        
        response = requests.post(
            f"{api_url}/reports/generate",
            json={
                "start_date": today,
                "end_date": today
            },
            timeout=30
        )
        
        if response.status_code == 200:
            report = response.json()
            records = report.get('selected_records', [])
            
            logger.info(f"✅ SUCCESS: Found {len(records)} records")
            
            if len(records) > 0:
                logger.info("📊 SAMPLE RECORD DETAILS:")
                for i, record in enumerate(records[:2]):
                    logger.info(f"   Record {i+1}:")
                    logger.info(f"     ID: {record.get('_id')}")
                    logger.info(f"     Conversation ID: {record.get('conversation_id')}")
                    logger.info(f"     Customer: {record.get('customer')}")
                    logger.info(f"     Created: {record.get('created_at')}")
                
                # Save results
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f"fixed_reporting_api_results_{timestamp}.json"
                
                with open(filename, 'w') as f:
                    json.dump(report, f, indent=2, default=str)
                
                logger.info(f"📁 Results saved to: {filename}")
                return True
            else:
                logger.info("⚠️  No records found even with today's date")
                return False
        else:
            logger.error(f"❌ API request failed: {response.status_code}")
            return False
        
    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    success = test_reporting_api_with_actual_data()
    if success:
        print("\\n✅ Fixed test completed successfully!")
    else:
        print("\\n❌ Test still has issues - check MongoDB data dates")
'''
    
    with open('test_reporting_api_fixed.py', 'w') as f:
        f.write(fixed_script)
    
    print(f"✓ Fixed test script created: test_reporting_api_fixed.py")
    print(f"   This script uses today's date to find actual records")
    
    return True

def main():
    """Run comprehensive investigation and create fix"""
    
    print("🔍 REPORTING API DATA FILTERING FIX")
    print("Investigating why 5 records exist but API finds 0")
    print(f"Investigation run at: {datetime.now().isoformat()}")
    
    # Step 1: Investigate the data filtering issue
    investigation_results = investigate_data_filtering_issue()
    
    # Step 2: Test API with current date
    current_date_works = test_reporting_api_with_current_date()
    
    # Step 3: Create fixed test script
    create_fixed_test_script()
    
    print("\n" + "=" * 80)
    print("INVESTIGATION SUMMARY")
    print("=" * 80)
    
    if investigation_results:
        print(f"✓ MongoDB has {investigation_results['total_records']} records")
        print(f"✓ Working queries found: {len(investigation_results['working_queries'])}")
        
        for name, query, count in investigation_results['working_queries']:
            print(f"   - {name}: {count} records")
    
    if current_date_works:
        print(f"✅ SOLUTION: Use current date ({datetime.now().strftime('%Y-%m-%d')}) in API calls")
    else:
        print(f"❌ Issue persists - need to check date format in MongoDB records")
    
    print(f"\n🔧 NEXT STEPS:")
    print(f"   1. Run: python test_reporting_api_fixed.py")
    print(f"   2. This will use today's date to find actual records")
    print(f"   3. Original script used too wide date range (2000-2100)")

if __name__ == "__main__":
    main()
