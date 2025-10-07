#!/usr/bin/env python3
"""
Investigation script to check actual records in agentic_analysis collection
"""

import json
import os
from pymongo import MongoClient

def investigate_actual_records():
    """Check what records actually exist and look for text truncation"""
    
    print("=" * 80)
    print("ACTUAL RECORDS INVESTIGATION")
    print("=" * 80)
    
    try:
        # Connect to MongoDB
        connection_string = os.getenv('MONGODB_CONNECTION_STRING', 'mongodb://localhost:27017/')
        client = MongoClient(connection_string)
        db = client['csai']
        collection = db['agentic_analysis']
        
        print(f"✓ Connected to MongoDB")
        
        # Get all records
        records = list(collection.find({}))
        print(f"✓ Found {len(records)} records in agentic_analysis collection")
        
        if len(records) == 0:
            print("❌ No records found to analyze")
            return
        
        # Analyze each record for text truncation
        for i, record in enumerate(records):
            print(f"\n--- Record {i+1} ---")
            print(f"_id: {record.get('_id')}")
            print(f"conversation_id: {record.get('conversation_id')}")
            print(f"customer: {record.get('customer')}")
            
            # Check for truncated reasoning text
            categories = record.get('performance_metrics', {}).get('categories', {})
            
            truncated_fields = []
            
            for category_name, category_data in categories.items():
                kpis = category_data.get('kpis', {})
                
                for kpi_name, kpi_data in kpis.items():
                    reason = kpi_data.get('reason', '')
                    
                    if reason.endswith('…'):
                        truncated_fields.append(f"{category_name}.{kpi_name}")
                        print(f"🔍 TRUNCATED: {category_name}.{kpi_name}")
                        print(f"   Length: {len(reason)} chars")
                        print(f"   Text: {reason}")
                    
                    # Check sub-KPIs
                    sub_kpis = kpi_data.get('sub_kpis', {})
                    for sub_kpi_name, sub_kpi_data in sub_kpis.items():
                        sub_reason = sub_kpi_data.get('reason', '')
                        
                        if sub_reason.endswith('…'):
                            truncated_fields.append(f"{category_name}.{kpi_name}.{sub_kpi_name}")
                            print(f"🔍 TRUNCATED SUB-KPI: {category_name}.{kpi_name}.{sub_kpi_name}")
                            print(f"   Length: {len(sub_reason)} chars") 
                            print(f"   Text: {sub_reason}")
            
            if not truncated_fields:
                print("✓ No truncated text found in this record")
            else:
                print(f"❌ Found {len(truncated_fields)} truncated fields")
            
            # Save each record for analysis
            filename = f"record_{i+1}_analysis.json"
            with open(filename, 'w') as f:
                json.dump(record, f, indent=2, default=str)
            print(f"✓ Record saved to: {filename}")
        
        client.close()
        
    except Exception as e:
        print(f"❌ Investigation failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    investigate_actual_records()
