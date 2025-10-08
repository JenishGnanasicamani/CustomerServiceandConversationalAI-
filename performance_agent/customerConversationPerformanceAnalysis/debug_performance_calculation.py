#!/usr/bin/env python3

import json

def _calculate_performance_averages(performance_metrics):
    """
    Calculate performance averages from a collection of metrics
    """
    performance_averages = {}
    
    for category, metrics_list in performance_metrics.items():
        print(f"Processing category: {category}")
        print(f"Number of records: {len(metrics_list)}")
        
        if not metrics_list:
            continue
            
        category_avg = {}
        
        # Process each record in the metrics list
        for i, record in enumerate(metrics_list):
            print(f"  Processing record {i}: {type(record)}")
            
            if not isinstance(record, dict) or 'categories' not in record:
                print(f"    Skipping record {i} - invalid structure")
                continue
                
            # Navigate to the actual KPI scores within the record structure
            categories = record.get('categories', {})
            if category in categories:
                category_data = categories[category]
                print(f"    Found category data for {category}")
                
                # Get overall category score
                if 'overall_score' in category_data:
                    if 'overall_score' not in category_avg:
                        category_avg['overall_score'] = []
                    category_avg['overall_score'].append(category_data['overall_score'])
                    print(f"    Added overall_score: {category_data['overall_score']}")
                
                # Process individual KPIs within the category
                kpis = category_data.get('kpis', {})
                for kpi_name, kpi_data in kpis.items():
                    if isinstance(kpi_data, dict) and 'score' in kpi_data:
                        if kpi_name not in category_avg:
                            category_avg[kpi_name] = []
                        category_avg[kpi_name].append(kpi_data['score'])
                        print(f"    Added {kpi_name}: {kpi_data['score']}")
                        
                        # Also process sub_kpis if they exist
                        if 'sub_kpis' in kpi_data:
                            for sub_kpi_name, sub_kpi_data in kpi_data['sub_kpis'].items():
                                if isinstance(sub_kpi_data, dict) and 'score' in sub_kpi_data:
                                    sub_key = f"{kpi_name}_{sub_kpi_name}"
                                    if sub_key not in category_avg:
                                        category_avg[sub_key] = []
                                    category_avg[sub_key].append(sub_kpi_data['score'])
                                    print(f"    Added {sub_key}: {sub_kpi_data['score']}")
        
        # Calculate averages from collected values
        final_averages = {}
        for metric_key, values in category_avg.items():
            if values and isinstance(values, list):
                final_averages[metric_key] = round(sum(values) / len(values), 2)
                print(f"  Final average for {metric_key}: {final_averages[metric_key]} (from {len(values)} values)")
        
        if final_averages:
            performance_averages[category] = final_averages
    
    return performance_averages

# Load the test data
with open('debug_performance_averages_report.json', 'r') as f:
    report = json.load(f)

# Extract performance metrics from records
records = report['selected_records']
performance_metrics = {
    "accuracy_compliance": [],
    "empathy_communication": [],
    "efficiency_resolution": []
}

for record in records:
    perf_metrics = record.get("performance_metrics", {})
    for category in performance_metrics:
        if category in perf_metrics:
            performance_metrics[category].append(perf_metrics[category])

print("=== DEBUGGING PERFORMANCE CALCULATION ===")
result = _calculate_performance_averages(performance_metrics)
print(f"\nFinal result: {json.dumps(result, indent=2)}")
