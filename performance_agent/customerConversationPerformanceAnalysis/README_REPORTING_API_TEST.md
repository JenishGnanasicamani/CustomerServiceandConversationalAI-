# Reporting API Test Script Usage Guide

## Overview
The `test_reporting_api_full_records.py` script is designed to test the Reporting API by fetching all records from the MongoDB `agentic_analysis` collection and saving them to a JSON file.

## Features
- **Health Check**: Verifies API connectivity and MongoDB connection
- **Collection Statistics**: Shows total records, unique customers, and date ranges
- **Maximum Date Range**: Uses 2000-01-01 to 2100-12-31 to capture all possible records
- **Flexible HTTP Methods**: Supports both POST and GET requests
- **Customer Filtering**: Optional customer-specific filtering
- **JSON Output**: Saves all retrieved records with metadata to a JSON file
- **Comprehensive Logging**: Detailed logging of all operations

## Prerequisites
1. **Python Dependencies**: Ensure `requests` library is installed
   ```bash
   pip install requests
   ```

2. **Reporting API Server**: The reporting API must be running on port 8003
   ```bash
   python src/reporting_api.py
   ```

3. **MongoDB**: MongoDB should be accessible with the `agentic_analysis` collection

## Usage

### Basic Usage (All Records)
```bash
python test_reporting_api_full_records.py
```

### Using Environment Variables
```bash
# Set custom API URL
export REPORTING_API_URL="http://localhost:8003"

# Filter by specific customer
export CUSTOMER_FILTER="customer_123"

# Use GET method instead of POST
export HTTP_METHOD="GET"

python test_reporting_api_full_records.py
```

### Configuration Options
- **REPORTING_API_URL**: API base URL (default: `http://localhost:8003`)
- **CUSTOMER_FILTER**: Customer ID to filter by (default: `None` for all customers)
- **HTTP_METHOD**: HTTP method to use - "POST" or "GET" (default: `POST`)

## Output

### Console Output
The script provides detailed logging including:
- API health status
- Collection statistics (total records, unique customers, date ranges)
- Report generation progress
- File save confirmation
- Test summary

### JSON Output File
The script creates a timestamped JSON file (e.g., `reporting_api_records_20251005_185822.json`) containing:

```json
{
  "metadata": {
    "extraction_timestamp": "2025-10-05T18:58:22.116233",
    "source_api": "reporting_api",
    "total_records": 0,
    "query_parameters": {
      "start_date": "2000-01-01",
      "end_date": "2100-12-31",
      "customer": null
    },
    "report_status": "success",
    "api_version": "1.0.0"
  },
  "selected_records": [
    // All retrieved records from agentic_analysis collection
  ],
  "summary": {
    "what_went_well": [],
    "what_needs_improvement": [],
    "training_needs": []
  },
  "aggregated_insights": {
    // LLM-generated insights if records are available
  },
  "report_metadata": {
    "generated_at": "2025-10-05T18:58:22.115712",
    "total_records": 0
  }
}
```

## API Endpoints Tested

The script tests the following Reporting API endpoints:
- `GET /health` - Health check
- `GET /reports/stats` - Collection statistics  
- `POST /reports/generate` - Generate report (POST method)
- `GET /reports/generate` - Generate report (GET method with query parameters)

## Example Scenarios

### 1. Test All Records
```bash
python test_reporting_api_full_records.py
```

### 2. Test Specific Customer
```bash
export CUSTOMER_FILTER="customer_123"
python test_reporting_api_full_records.py
```

### 3. Test with GET Method
```bash
export HTTP_METHOD="GET"
python test_reporting_api_full_records.py
```

### 4. Test with Different API URL
```bash
export REPORTING_API_URL="http://production-server:8003"
python test_reporting_api_full_records.py
```

## Troubleshooting

### Connection Refused Error
```
Failed to connect to API for health check: HTTPConnectionPool(host='localhost', port=8003): Max retries exceeded
```
**Solution**: Start the reporting API server first:
```bash
python src/reporting_api.py
```

### MongoDB Connection Issues
Check the MongoDB connection string in environment variables:
```bash
export MONGODB_CONNECTION_STRING="mongodb://localhost:27017/"
export MONGODB_DB_NAME="csai"
```

### Empty Results
If you get 0 records, it means:
1. The `agentic_analysis` collection is empty
2. Records don't have the expected date format in `created_at` field
3. Customer filter doesn't match any records

## Integration with Other Systems

This test script can be integrated into:
- **CI/CD Pipelines**: For automated API testing
- **Data Validation**: To verify data persistence
- **Monitoring Systems**: For regular health checks
- **Data Export**: For backing up analysis results

## Expected Record Structure

The script expects records in the `agentic_analysis` collection to have this structure:
```json
{
  "conversation_id": "string",
  "customer": "string",
  "created_at": "ISO datetime string",
  "conversation_summary": {},
  "performance_metrics": {},
  "analysis_results": {}
}
```

## Notes
- The script uses a maximum date range (2000-01-01 to 2100-12-31) to ensure all records are captured
- Output files are timestamped to prevent overwrites
- All HTTP errors and exceptions are properly handled and logged
- The script supports both POST and GET methods for maximum flexibility
