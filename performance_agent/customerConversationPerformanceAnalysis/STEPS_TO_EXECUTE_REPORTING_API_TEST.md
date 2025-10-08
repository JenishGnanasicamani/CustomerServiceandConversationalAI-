# Steps to Execute test_reporting_api_full_records.py

## Prerequisites ✅

1. **Reporting API Server Running**
   - The reporting API server is already running on `http://localhost:8003`
   - Confirmed by the active terminal showing: `python src/reporting_api.py`

2. **MongoDB Connection**
   - MongoDB is connected and accessible
   - Collection `csai.agentic_analysis` contains 5 records

## Step-by-Step Execution Guide

### Step 1: Open Terminal
```bash
# Navigate to the project directory (if not already there)
cd /Users/I032294/iisc_cds/CustomerServiceandConversationalAI-/performance_agent/customerConversationPerformanceAnalysis
```

### Step 2: Execute the Test Script
```bash
python test_reporting_api_full_records.py
```

### Step 3: Expected Output
The script will:
1. **Test all available endpoints** on the reporting API
2. **Generate sample reports** using actual data
3. **Validate API responses** and data structure
4. **Create output files** with test results
5. **Display comprehensive results** in the terminal

### Step 4: Check Generated Files
After execution, check for these output files:
- `reporting_api_test_results_[timestamp].json` - Detailed API test results
- `sample_report_output.json` - Sample report generated from API
- Console output showing endpoint testing progress

## What the Script Does

### 1. **API Endpoint Testing**
- Tests root endpoint (`/`)
- Tests health check (`/health`)
- Tests collection stats (`/reports/stats`)
- Tests report generation (`/reports/generate`)
- Tests sample report (`/reports/sample`)

### 2. **Data Validation**
- Verifies API responses are valid JSON
- Checks for required fields in responses
- Validates data structure consistency
- Tests with actual MongoDB data

### 3. **Report Generation**
- Generates reports using current date ranges
- Tests both GET and POST methods for report generation
- Validates report structure and content
- Saves sample reports for reference

## Expected Results

### ✅ Successful Execution Should Show:
```
🧪 REPORTING API COMPREHENSIVE TEST
=====================================
✓ Root endpoint working
✓ Health check passed
✓ Collection stats retrieved: X records
✓ Report generation successful
✓ All endpoints responding correctly
✓ Test results saved to: reporting_api_test_results_[timestamp].json
```

### 📊 Generated Files Will Contain:
- Complete API response data
- Endpoint status and response times
- Sample performance reports
- Data structure validation results

## Troubleshooting

### If the script fails:

1. **Check API Server Status**
   ```bash
   curl http://localhost:8003/health
   ```

2. **Verify MongoDB Connection**
   ```bash
   # Check if MongoDB is accessible
   python -c "from pymongo import MongoClient; print('MongoDB OK' if MongoClient().admin.command('ping') else 'MongoDB Error')"
   ```

3. **Check Dependencies**
   ```bash
   pip install requests pymongo fastapi uvicorn
   ```

## Alternative Execution Methods

### Method 1: Direct Python Execution
```bash
python test_reporting_api_full_records.py
```

### Method 2: With Virtual Environment (if using one)
```bash
source venv/bin/activate  # or your virtual environment activation command
python test_reporting_api_full_records.py
```

### Method 3: With Detailed Output
```bash
python test_reporting_api_full_records.py | tee test_execution_log.txt
```

## Quick Verification Commands

Before running the test, verify the system is ready:

```bash
# 1. Check if reporting API is running
curl -s http://localhost:8003/ | grep -q "Customer Conversation Performance Reporting API" && echo "✅ API Running" || echo "❌ API Not Running"

# 2. Check MongoDB records
python -c "from pymongo import MongoClient; print(f'Records: {MongoClient()[\"csai\"][\"agentic_analysis\"].count_documents({})}')"

# 3. Test API health
curl -s http://localhost:8003/health | grep -q "healthy" && echo "✅ API Healthy" || echo "❌ API Issues"
```

---

## Ready to Execute! 🚀

**Current Status:**
- ✅ Reporting API server running on port 8003
- ✅ MongoDB connected with 5 records
- ✅ Test script ready for execution
- ✅ All dependencies verified

**Execute now with:**
```bash
python test_reporting_api_full_records.py
