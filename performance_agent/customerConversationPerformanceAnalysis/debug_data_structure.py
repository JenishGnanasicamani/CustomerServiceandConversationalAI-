#!/usr/bin/env python3

import json

# Load the test data
with open('debug_performance_averages_report.json', 'r') as f:
    report = json.load(f)

records = report['selected_records']
print(f"Number of records: {len(records)}")

# Check the structure of the first record
if records:
    record = records[0]
    print(f"Record keys: {list(record.keys())}")
    
    # Check performance_metrics structure
    perf_metrics = record.get("performance_metrics", {})
    print(f"Performance metrics keys: {list(perf_metrics.keys())}")
    
    # Check if it has categories directly in performance_metrics
    if 'categories' in perf_metrics:
        categories = perf_metrics['categories']
        print(f"Categories in performance_metrics: {list(categories.keys())}")
        
        for cat_name, cat_data in categories.items():
            print(f"  {cat_name} has keys: {list(cat_data.keys())}")
            if 'kpis' in cat_data:
                print(f"    KPIs: {list(cat_data['kpis'].keys())}")
    
    # Debug the extraction logic that's currently failing
    print("\n=== Current extraction logic ===")
    performance_metrics = {
        "accuracy_compliance": [],
        "empathy_communication": [],
        "efficiency_resolution": []
    }
    
    for record in records:
        perf_metrics = record.get("performance_metrics", {})
        for category in performance_metrics:
            if category in perf_metrics:
                print(f"Found {category} in perf_metrics")
                performance_metrics[category].append(perf_metrics[category])
            else:
                print(f"Did NOT find {category} in perf_metrics")
                print(f"Available keys in perf_metrics: {list(perf_metrics.keys())}")
                break
