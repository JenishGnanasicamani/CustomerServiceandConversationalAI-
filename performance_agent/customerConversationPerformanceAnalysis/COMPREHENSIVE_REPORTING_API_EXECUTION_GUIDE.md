# Comprehensive Guide: Steps to Execute Reports/Generate API

## Overview
This guide provides detailed steps to execute the Customer Conversation Performance Analysis Reporting API, which generates LLM-powered performance reports from MongoDB conversation data.

## System Architecture
- **API Framework**: FastAPI (Python)
- **Database**: MongoDB (csai.agentic_analysis collection)
- **LLM Service**: Claude-4 for intelligent report generation
- **Port**: 8003 (default)

## Prerequisites

### 1. Environment Setup
```bash
# Install required dependencies
pip install -r requirements.txt

# Key dependencies include:
# - fastapi>=0.100.0
# - uvicorn[standard]>=0.23.0
# - pymongo>=4.6.0
# - pydantic>=2.0.0
# - requests>=2.31.0
```

### 2. Environment Variables
```bash
# MongoDB Configuration
export MONGODB_CONNECTION_STRING="mongodb://localhost:27017/"
export MONGODB_DB_NAME="csai"

# API Configuration (optional)
export HOST="0.0.0.0"
export PORT="8003"

# For testing specific scenarios
export CUSTOMER_FILTER="customer_123"  # Optional customer filter
export HTTP_METHOD="POST"  # POST or GET
```

### 3. MongoDB Setup
Ensure MongoDB is running and contains data in the `csai.agentic_analysis` collection with this structure:
```json
{
  "conversation_id": "conv_507f1f77bcf86cd799439011",
  "customer": "customer_123",
  "created_at": "2023-01-15T14:30:00.123456Z",
  "conversation_summary": {
    "final_sentiment": "Positive",
    "intent": "Technical Support",
    "topic": "Account Issues"
  },
  "performance_metrics": {
    "empathy_communication": {
      "empathy_score": 8.5
    },
    "accuracy_compliance": {
      "accuracy_score": 9.0
    },
    "efficiency_resolution": {
      "resolution_time": 120
    }
  }
}
```

## Execution Methods

### Method 1: Start the API Server

#### Step 1: Launch the Reporting API
```bash
# Navigate to project directory
cd /Users/I032294/iisc_cds/CustomerServiceandConversationalAI-/performance_agent/customerConversationPerformanceAnalysis

# Start the API server
python src/reporting_api.py
```

Expected output:
```
INFO:     Started server process [12345]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8003 (Press CTRL+C to quit)
```

#### Step 2: Test API Endpoints

**Health Check:**
```bash
curl http://localhost:8003/health
```

**Collection Statistics:**
```bash
curl http://localhost:8003/reports/stats
```

**Generate Report (GET):**
```bash
curl "http://localhost:8003/reports/generate?start_date=2023-01-01&end_date=2023-12-31&customer=customer_123"
```

**Generate Report (POST):**
```bash
curl -X POST "http://localhost:8003/reports/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "start_date": "2023-01-01",
    "end_date": "2023-12-31",
    "customer": "customer_123"
  }'
```

### Method 2: Run Comprehensive Test Suite

#### Execute the Full Test Script
```bash
python test_reporting_api_full_records.py
```

This script will:
- ✅ Test all API endpoints
- ✅ Validate API responses
- ✅ Generate sample reports
- ✅ Save results to timestamped JSON files
- ✅ Display comprehensive test results

#### Expected Test Output:
```
🧪 REPORTING API COMPREHENSIVE TEST
=====================================
✓ Root endpoint working
✓ Health check passed - API healthy, database connected
✓ Collection stats retrieved: 5 records found
✓ Sample report structure verified
✓ Report generation (POST) successful - 5 records processed
✓ Report generation (GET) successful - 5 records processed
✓ All endpoints responding correctly

📊 REPORT RESULTS SUMMARY:
- Total conversations analyzed: 5
- Unique customers: 3
- Date range: 2023-01-15T14:30:00Z to 2023-12-20T16:45:00Z
- Sentiment distribution: {'Positive': 4, 'Neutral': 1}
- Intent distribution: {'Technical Support': 3, 'Billing Inquiry': 2}

✅ Test results saved to: reporting_api_test_results_20251005_224630.json
```

## API Endpoints Reference

### Core Endpoints

| Endpoint | Method | Description | Parameters |
|----------|--------|-------------|------------|
| `/` | GET | API information and available endpoints | None |
| `/health` | GET | Health check and system status | None |
| `/reports/stats` | GET | Collection statistics and data overview | None |
| `/reports/generate` | POST/GET | Generate performance report | start_date, end_date, customer (optional) |
| `/reports/sample` | GET | Sample report structure for reference | None |
| `/config/datasource` | POST/GET | Configure/get data source settings | source_type, collection_name, file_path |

### Request/Response Examples

**Generate Report Request (POST):**
```json
{
  "start_date": "2023-01-01",
  "end_date": "2023-12-31",
  "customer": "customer_123"
}
```

**Report Response Structure:**
```json
{
  "status": "success",
  "query_parameters": {
    "start_date": "2023-01-01",
    "end_date": "2023-12-31",
    "customer": "customer_123",
    "records_found": 5
  },
  "selected_records": [...],
  "summary": {
    "what_went_well": [
      "High positive sentiment rate (80.0%)",
      "Strong empathy scores in customer interactions"
    ],
    "what_needs_improvement": [
      "Response time could be improved"
    ],
    "training_needs": [
      "Advanced technical troubleshooting training"
    ]
  },
  "aggregated_insights": {
    "total_conversations": 5,
    "unique_customers": 3,
    "sentiment_distribution": {"Positive": 4, "Neutral": 1},
    "combination_analysis": {...}
  },
  "report_metadata": {
    "generated_at": "2023-01-31T12:00:00Z",
    "analysis_method": "claude-4",
    "total_records": 5
  }
}
```

## Data Source Configuration

### MongoDB Source (Default)
```bash
curl -X POST "http://localhost:8003/config/datasource" \
  -H "Content-Type: application/json" \
  -d '{
    "source_type": "mongodb",
    "collection_name": "agentic_analysis"
  }'
```

### File Source (Alternative)
```bash
curl -X POST "http://localhost:8003/config/datasource" \
  -H "Content-Type: application/json" \
  -d '{
    "source_type": "file",
    "file_path": "/path/to/conversation/data.json"
  }'
```

## Advanced Usage Scenarios

### 1. Generate Reports for All Customers
```bash
curl "http://localhost:8003/reports/generate?start_date=2023-01-01&end_date=2023-12-31"
```

### 2. Generate Reports with Specific Date Range
```bash
curl "http://localhost:8003/reports/generate?start_date=2023-06-01T00:00:00&end_date=2023-06-30T23:59:59"
```

### 3. Batch Report Generation Script
```python
import requests
import json
from datetime import datetime, timedelta

base_url = "http://localhost:8003"
customers = ["customer_123", "customer_456", "customer_789"]

for customer in customers:
    response = requests.post(f"{base_url}/reports/generate", json={
        "start_date": "2023-01-01",
        "end_date": "2023-12-31",
        "customer": customer
    })
    
    if response.status_code == 200:
        with open(f"report_{customer}_{datetime.now().strftime('%Y%m%d')}.json", "w") as f:
            json.dump(response.json(), f, indent=2)
        print(f"✅ Report generated for {customer}")
    else:
        print(f"❌ Failed to generate report for {customer}: {response.status_code}")
```

## Troubleshooting Guide

### Common Issues and Solutions

#### 1. Connection Refused Error
```
Failed to connect to API: Max retries exceeded
```
**Solution:**
```bash
# Check if API is running
ps aux | grep reporting_api

# Start the API if not running
python src/reporting_api.py
```

#### 2. MongoDB Connection Issues
```
Failed to connect to MongoDB
```
**Solutions:**
```bash
# Check MongoDB status
brew services list | grep mongodb  # macOS
sudo systemctl status mongod       # Linux

# Start MongoDB if needed
brew services start mongodb-community  # macOS
sudo systemctl start mongod            # Linux

# Verify connection string
echo $MONGODB_CONNECTION_STRING
```

#### 3. Empty Results
```
No records found for the specified criteria
```
**Solutions:**
```bash
# Check collection contents
python -c "
from pymongo import MongoClient
client = MongoClient('mongodb://localhost:27017/')
db = client['csai']
collection = db['agentic_analysis']
print(f'Total records: {collection.count_documents({})}')
print('Sample record:', collection.find_one())
"

# Verify date formats
curl "http://localhost:8003/reports/stats"
```

#### 4. LLM Service Issues
```
Failed to initialize LLM service
```
**Solutions:**
```bash
# Check AI Core credentials
cat config/aicore_credentials.yaml

# Test LLM service separately
python -c "
from src.llm_agent_service import get_llm_agent_service
service = get_llm_agent_service()
print('LLM service:', service.model_name if service else 'Failed')
"
```

## Performance Optimization

### 1. Database Indexing
```javascript
// MongoDB shell commands for better performance
use csai
db.agentic_analysis.createIndex({"created_at": 1})
db.agentic_analysis.createIndex({"customer": 1})
db.agentic_analysis.createIndex({"created_at": 1, "customer": 1})
```

### 2. API Configuration for Production
```bash
# Production environment variables
export HOST="0.0.0.0"
export PORT="8003"
export WORKERS=4  # Multiple worker processes
export LOG_LEVEL="info"

# Start with Gunicorn for production
pip install gunicorn
gunicorn -w 4 -k uvicorn.workers.UvicornWorker src.reporting_api:app --bind 0.0.0.0:8003
```

### 3. Caching and Rate Limiting
```python
# Add to reporting_api.py for production
from fastapi import FastAPI
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.get("/reports/generate")
@limiter.limit("10/minute")  # Rate limiting
async def generate_report_get(...):
    # Implementation
```

## Monitoring and Logging

### 1. Health Monitoring Script
```bash
#!/bin/bash
# health_monitor.sh
while true; do
    response=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8003/health)
    if [ $response -eq 200 ]; then
        echo "$(date): API healthy"
    else
        echo "$(date): API unhealthy (HTTP $response)"
        # Send alert or restart service
    fi
    sleep 60
done
```

### 2. Log Analysis
```bash
# Monitor API logs
tail -f /var/log/reporting_api.log

# Search for errors
grep -i error /var/log/reporting_api.log

# Monitor database queries
grep "MongoDB query" /var/log/reporting_api.log
```

## Integration Examples

### 1. Dashboard Integration
```javascript
// Frontend JavaScript for dashboard
async function generateReport(startDate, endDate, customer = null) {
    const response = await fetch('http://localhost:8003/reports/generate', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            start_date: startDate,
            end_date: endDate,
            customer: customer
        })
    });
    
    const report = await response.json();
    displayReport(report);
}

function displayReport(report) {
    // Update dashboard with report data
    document.getElementById('sentiment-chart').data = report.aggregated_insights.sentiment_distribution;
    document.getElementById('insights-panel').innerHTML = formatInsights(report.summary);
}
```

### 2. Scheduled Report Generation
```python
# scheduler.py - For automated report generation
import schedule
import time
from datetime import datetime, timedelta
import requests

def generate_daily_report():
    yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
    
    response = requests.post('http://localhost:8003/reports/generate', json={
        'start_date': yesterday,
        'end_date': yesterday
    })
    
    if response.status_code == 200:
        with open(f'daily_report_{yesterday}.json', 'w') as f:
            json.dump(response.json(), f, indent=2)
        print(f"Daily report generated for {yesterday}")

# Schedule daily report at 9 AM
schedule.every().day.at("09:00").do(generate_daily_report)

while True:
    schedule.run_pending()
    time.sleep(60)
```

## Quick Start Commands

### Complete Setup and Test
```bash
# 1. Navigate to project
cd /Users/I032294/iisc_cds/CustomerServiceandConversationalAI-/performance_agent/customerConversationPerformanceAnalysis

# 2. Install dependencies
pip install -r requirements.txt

# 3. Set environment variables
export MONGODB_CONNECTION_STRING="mongodb://localhost:27017/"
export MONGODB_DB_NAME="csai"

# 4. Start API server (in one terminal)
python src/reporting_api.py

# 5. Run comprehensive test (in another terminal)
python test_reporting_api_full_records.py

# 6. Test specific endpoint
curl "http://localhost:8003/reports/generate?start_date=2023-01-01&end_date=2023-12-31"
```

## Summary

The Reporting API provides a comprehensive solution for generating intelligent performance reports from customer conversation data. With support for multiple data sources, LLM-powered insights, and flexible filtering options, it serves as a powerful tool for customer service performance analysis.

**Key Features:**
- ✅ FastAPI-based RESTful endpoints
- ✅ MongoDB integration with flexible querying
- ✅ LLM-powered intelligent summaries
- ✅ Comprehensive performance metrics analysis
- ✅ Multiple data source support (MongoDB/Files)
- ✅ Date range and customer filtering
- ✅ Production-ready with health checks and error handling
- ✅ Extensive testing and validation
