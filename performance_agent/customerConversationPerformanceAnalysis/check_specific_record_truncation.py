#!/usr/bin/env python3
"""
Check the specific record mentioned by user for truncation issues
"""

import json
import os
import requests
from pymongo import MongoClient

def check_specific_record():
    """Check the specific record mentioned by user"""
    
    print("=" * 80)
    print("SPECIFIC RECORD TRUNCATION CHECK")
    print("=" * 80)
    
    try:
        # Connect to MongoDB
        connection_string = os.getenv('MONGODB_CONNECTION_STRING', 'mongodb://localhost:27017/')
        client = MongoClient(connection_string)
        db = client['csai']
        collection = db['agentic_analysis']
        
        print(f"✓ Connected to MongoDB")
        
        # Check the specific record ID from user feedback
        record_id = "68e29e53f61d7c49fea920f8"
        record = collection.find_one({"_id": record_id})
        
        if record:
            print(f"✓ Found record with ID: {record_id}")
            print(f"   conversation_id: {record.get('conversation_id')}")
            print(f"   customer: {record.get('customer')}")
            
            # Extract the specific field mentioned by user
            categories = record.get('performance_metrics', {}).get('categories', {})
            accuracy_compliance = categories.get('accuracy_compliance', {})
            resolution_kpi = accuracy_compliance.get('kpis', {}).get('resolution_completeness', {})
            reason_text = resolution_kpi.get('reason', '')
            
            print(f"\n📝 RESOLUTION COMPLETENESS REASON:")
            print(f"   Length: {len(reason_text)} characters")
            print(f"   Full text: '{reason_text}'")
            print(f"   Ends with ellipsis: {reason_text.endswith('…')}")
            
            # Check if there's a difference between 'reason' and 'reasoning'
            reasoning_text = resolution_kpi.get('reasoning', '')
            if reasoning_text:
                print(f"\n📝 RESOLUTION COMPLETENESS REASONING:")
                print(f"   Length: {len(reasoning_text)} characters")
                print(f"   Full text: '{reasoning_text}'")
            
            # Check all KPIs in this record for truncation
            print(f"\n🔍 CHECKING ALL KPIs FOR TRUNCATION:")
            
            truncation_found = False
            for category_name, category_data in categories.items():
                kpis = category_data.get('kpis', {})
                
                for kpi_name, kpi_data in kpis.items():
                    reason = kpi_data.get('reason', '')
                    reasoning = kpi_data.get('reasoning', '')
                    
                    if reason.endswith('…'):
                        print(f"   ❌ TRUNCATED 'reason': {category_name}.{kpi_name}")
                        print(f"      Text: {reason}")
                        truncation_found = True
                    
                    if reasoning.endswith('…'):
                        print(f"   ❌ TRUNCATED 'reasoning': {category_name}.{kpi_name}")
                        print(f"      Text: {reasoning}")
                        truncation_found = True
                    
                    if not reason.endswith('…') and not reasoning.endswith('…'):
                        print(f"   ✅ OK: {category_name}.{kpi_name} (reason: {len(reason)} chars, reasoning: {len(reasoning)} chars)")
            
            if not truncation_found:
                print(f"\n✅ NO TRUNCATION FOUND in record {record_id}")
            
            # Save the full record
            with open(f'record_{record_id}_analysis.json', 'w') as f:
                json.dump(record, f, indent=2, default=str)
            
            print(f"\n✓ Record saved to: record_{record_id}_analysis.json")
            
        else:
            print(f"❌ Record with ID {record_id} not found")
            
            # Try to find records with conversation_id 3751
            conv_records = list(collection.find({"conversation_id": "3751"}))
            if conv_records:
                print(f"✓ Found {len(conv_records)} records with conversation_id 3751")
                for i, conv_record in enumerate(conv_records):
                    print(f"   Record {i+1}: ID = {conv_record.get('_id')}")
            else:
                print(f"❌ No records found with conversation_id 3751")
        
        client.close()
        
    except Exception as e:
        print(f"❌ Check failed: {e}")
        import traceback
        traceback.print_exc()

def check_reporting_api_display():
    """Check if the reporting API is truncating display"""
    
    print("\n" + "=" * 80)
    print("REPORTING API DISPLAY CHECK")
    print("=" * 80)
    
    try:
        # Test the reporting API endpoint
        api_url = "http://localhost:8003"
        
        # Test the records endpoint
        response = requests.get(f"{api_url}/records", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            records = data.get('records', [])
            
            print(f"✓ Retrieved {len(records)} records from API")
            
            # Check if any records have truncated reason text
            for i, record in enumerate(records):
                record_id = record.get('_id')
                conversation_id = record.get('conversation_id')
                
                print(f"\n--- API Record {i+1} ---")
                print(f"   ID: {record_id}")
                print(f"   Conversation ID: {conversation_id}")
                
                # Check for truncated text in API response
                categories = record.get('performance_metrics', {}).get('categories', {})
                
                api_truncation_found = False
                for category_name, category_data in categories.items():
                    kpis = category_data.get('kpis', {})
                    
                    for kpi_name, kpi_data in kpis.items():
                        reason = kpi_data.get('reason', '')
                        
                        if reason.endswith('…'):
                            print(f"   ❌ API TRUNCATED: {category_name}.{kpi_name}")
                            print(f"      Text: {reason}")
                            api_truncation_found = True
                        elif len(reason) > 0:
                            print(f"   ✅ API OK: {category_name}.{kpi_name} ({len(reason)} chars)")
                
                if not api_truncation_found and len(categories) > 0:
                    print(f"   ✅ No truncation found in API response")
            
            # Save API response for analysis
            with open('reporting_api_response_analysis.json', 'w') as f:
                json.dump(data, f, indent=2, default=str)
            
            print(f"\n✓ API response saved to: reporting_api_response_analysis.json")
            
        else:
            print(f"❌ API request failed with status: {response.status_code}")
            print(f"   Response: {response.text}")
        
    except Exception as e:
        print(f"❌ API check failed: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Run specific record truncation checks"""
    
    print("🔍 SPECIFIC RECORD TRUNCATION INVESTIGATION")
    print("Checking the exact record mentioned by user")
    
    # Check the specific record in MongoDB
    check_specific_record()
    
    # Check how it appears in the API
    check_reporting_api_display()
    
    print("\n" + "=" * 80)
    print("SPECIFIC RECORD CHECK COMPLETE")
    print("=" * 80)

if __name__ == "__main__":
    main()
