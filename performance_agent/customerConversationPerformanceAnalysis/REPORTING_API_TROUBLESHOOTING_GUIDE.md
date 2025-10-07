# Reporting API Troubleshooting Guide

## Common Issues and Solutions

### 1. API Connection Issues

#### Problem: "Connection refused" Error
```
Failed to connect to API: Max retries exceeded
HTTPConnectionPool(host='localhost', port=8003): Max retries exceeded
```

**Solutions:**
```bash
# Check if API process is running
ps aux | grep reporting_api

# Check if port 8003 is in use
lsof -i :8003

# Start the API server
python src/reporting_api.py

# Alternative: Start in background
nohup python src/reporting_api.py > reporting_api.log 2>&1 &
```

#### Problem: Port Already in Use
```
OSError: [Errno 48] Address already in use
```

**Solutions:**
```bash
# Find and kill process using port 8003
lsof -ti:8003 | xargs kill -9

# Or use a different port
export PORT=8004
python src/reporting_api.py
```

### 2. MongoDB Connection Issues

#### Problem: MongoDB Connection Failed
```
Failed to connect to MongoDB
pymongo.errors.ServerSelectionTimeoutError
```

**Solutions:**
```bash
# Check MongoDB status (macOS)
brew services list | grep mongodb

# Start MongoDB (macOS)
brew services start mongodb-community

# Check MongoDB status (Linux)
sudo systemctl status mongod

# Start MongoDB (Linux)
sudo systemctl start mongod

# Test MongoDB connection
python -c "from pymongo import MongoClient; print('MongoDB OK' if MongoClient().admin.command('ping') else 'MongoDB Error')"
```

#### Problem: Database/Collection Not Found
```
Collection 'agentic_analysis' not found
```

**Solutions:**
```bash
# Check available collections
python -c "
from pymongo import MongoClient
client = MongoClient('mongodb://localhost:27017/')
db = client['csai']
print('Collections:', db.list_collection_names())
"

# Create test data if needed
python -c "
from pymongo import MongoClient
from datetime import datetime
client = MongoClient('mongodb://localhost:27017/')
db = client['csai']
collection = db['agentic_analysis']
test_record = {
    'conversation_id': 'test_conv_001',
    'customer': 'test_customer',
    'created_at': datetime.now().isoformat(),
    'conversation_summary': {
        'final_sentiment': 'Positive',
        'intent': 'Test Intent',
        'topic': 'Test Topic'
    },
    'performance_metrics': {
        'empathy_communication': {'empathy_score': 8.0}
    }
}
collection.insert_one(test_record)
print('Test record inserted')
"
```

### 3. LLM Service Issues

#### Problem: LLM Service Initialization Failed
```
Failed to initialize LLM service for reporting
```

**Solutions:**
```bash
# Check AI Core credentials
cat config/aicore_credentials.yaml

# Verify credentials format
python -c "
import yaml
with open('config/aicore_credentials.yaml', 'r') as f:
    config = yaml.safe_load(f)
    print('Config keys:', list(config.keys()))
"

# Test LLM service separately
python -c "
from src.llm_agent_service import get_llm_agent_service
try:
    service = get_llm_agent_service()
    print('LLM service OK:', service.model_name if service else 'Failed')
except Exception as e:
    print('LLM Error:', e)
"
```

### 4. Data and Results Issues

#### Problem: No Records Found
```
No records found for the specified criteria
Records found: 0
```

**Solutions:**
```bash
# Check total records in collection
python -c "
from pymongo import MongoClient
client = MongoClient('mongodb://localhost:27017/')
db = client['csai']
collection = db['agentic_analysis']
total = collection.count_documents({})
print(f'Total records: {total}')
if total > 0:
    sample = collection.find_one()
    print('Sample record created_at:', sample.get('created_at'))
"

# Test with broader date range
curl "http://localhost:8003/reports/generate?start_date=1900-01-01&end_date=2100-12-31"

# Check collection statistics
curl http://localhost:8003/reports/stats
```

#### Problem: Date Format Issues
```
Invalid date format in record
```

**Solutions:**
```bash
# Check date formats in your data
python -c "
from pymongo import MongoClient
from datetime import datetime
client = MongoClient('mongodb://localhost:27017/')
db = client['csai']
collection = db['agentic_analysis']
for record in collection.find().limit(5):
    created_at = record.get('created_at')
    print(f'Record ID: {record.get(\"_id\")}, Date: {created_at}, Type: {type(created_at)}')
"

# Fix date format if needed
python -c "
from pymongo import MongoClient
from datetime import datetime
client = MongoClient('mongodb://localhost:27017/')
db = client['csai']
collection = db['agentic_analysis']
# Update records with proper ISO format
for record in collection.find():
    if 'created_at' in record:
        try:
            # Ensure ISO format
            dt = datetime.fromisoformat(str(record['created_at']).replace('Z', '+00:00'))
            iso_string = dt.isoformat()
            collection.update_one(
                {'_id': record['_id']}, 
                {'$set': {'created_at': iso_string}}
            )
        except Exception as e:
            print(f'Error updating record {record[\"_id\"]}: {e}')
print('Date format update completed')
"
```

### 5. Performance Issues

#### Problem: Slow Response Times
```
Request timeout or very slow responses
```

**Solutions:**
```bash
# Add MongoDB indexes for better performance
python -c "
from pymongo import MongoClient
client = MongoClient('mongodb://localhost:27017/')
db = client['csai']
collection = db['agentic_analysis']
# Create indexes
collection.create_index('created_at')
collection.create_index('customer')
collection.create_index([('created_at', 1), ('customer', 1)])
print('Indexes created')
"

# Monitor MongoDB queries
# Add this to your MongoDB config to log slow queries
# In /etc/mongod.conf or similar:
# systemLog:
#   verbosity: 1
#   component:
#     query:
#       verbosity: 2
```

### 6. Environment and Dependencies

#### Problem: Missing Dependencies
```
ModuleNotFoundError: No module named 'fastapi'
```

**Solutions:**
```bash
# Install all required dependencies
pip install -r requirements.txt

# Install specific missing packages
pip install fastapi uvicorn pymongo pydantic requests

# Check installed packages
pip list | grep -E "(fastapi|uvicorn|pymongo|pydantic|requests)"
```

#### Problem: Python Path Issues
```
ImportError: cannot import name 'ReportingService'
```

**Solutions:**
```bash
# Ensure you're in the correct directory
cd /Users/I032294/iisc_cds/CustomerServiceandConversationalAI-/performance_agent/customerConversationPerformanceAnalysis

# Check Python path
python -c "import sys; print('\n'.join(sys.path))"

# Add current directory to Python path
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

## Testing and Validation Commands

### Quick Health Check
```bash
#!/bin/bash
echo "=== Reporting API Health Check ==="

# 1. Check if API is running
echo "1. API Status:"
curl -s http://localhost:8003/health | jq '.' 2>/dev/null || echo "API not responding"
echo ""

# 2. Check MongoDB connection
echo "2. MongoDB Status:"
python -c "
from pymongo import MongoClient
try:
    client = MongoClient('mongodb://localhost:27017/', serverSelectionTimeoutMS=5000)
    client.admin.command('ping')
    print('✅ MongoDB connected')
except Exception as e:
    print('❌ MongoDB error:', e)
"

# 3. Check collection stats
echo "3. Collection Stats:"
curl -s http://localhost:8003/reports/stats | jq '.total_records' 2>/dev/null || echo "Cannot get stats"
echo ""
```

### Complete System Test
```bash
#!/bin/bash
echo "=== Complete Reporting API System Test ==="

# Test all endpoints
endpoints=(
    "/"
    "/health"
    "/reports/stats"
    "/reports/sample"
)

for endpoint in "${endpoints[@]}"; do
    echo "Testing: $endpoint"
    response=$(curl -s -w "%{http_code}" http://localhost:8003$endpoint)
    http_code=$(echo "$response" | tail -c 4)
    if [ "$http_code" -eq 200 ]; then
        echo "✅ $endpoint - OK"
    else
        echo "❌ $endpoint - HTTP $http_code"
    fi
done

# Test report generation
echo "Testing report generation:"
response=$(curl -s -w "%{http_code}" -X POST http://localhost:8003/reports/generate \
  -H "Content-Type: application/json" \
  -d '{"start_date": "2020-01-01", "end_date": "2025-12-31"}')
http_code=$(echo "$response" | tail -c 4)
if [ "$http_code" -eq 200 ]; then
    echo "✅ Report generation - OK"
else
    echo "❌ Report generation - HTTP $http_code"
fi
```

## Production Deployment Considerations

### Environment Variables for Production
```bash
# Production environment setup
export MONGODB_CONNECTION_STRING="mongodb://prod-server:27017/"
export MONGODB_DB_NAME="production_csai"
export HOST="0.0.0.0"
export PORT="8003"
export LOG_LEVEL="info"
export WORKERS=4
```

### Production Startup Script
```bash
#!/bin/bash
# production_start.sh

# Set production environment
export ENVIRONMENT="production"
export HOST="0.0.0.0"
export PORT="8003"
export WORKERS=4

# Start with Gunicorn for production
gunicorn -w $WORKERS -k uvicorn.workers.UvicornWorker \
  --bind $HOST:$PORT \
  --access-logfile /var/log/reporting_api_access.log \
  --error-logfile /var/log/reporting_api_error.log \
  --pid /var/run/reporting_api.pid \
  --daemon \
  src.reporting_api:app

echo "Reporting API started in production mode"
echo "PID: $(cat /var/run/reporting_api.pid)"
echo "Logs: /var/log/reporting_api_*.log"
```

### Health Monitoring Script
```bash
#!/bin/bash
# monitor_health.sh

LOGFILE="/var/log/reporting_api_monitor.log"
API_URL="http://localhost:8003/health"

while true; do
    timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    
    # Check API health
    response=$(curl -s -w "%{http_code}" $API_URL)
    http_code=$(echo "$response" | tail -c 4)
    
    if [ "$http_code" -eq 200 ]; then
        echo "[$timestamp] ✅ API healthy" >> $LOGFILE
    else
        echo "[$timestamp] ❌ API unhealthy (HTTP $http_code)" >> $LOGFILE
        
        # Send alert (customize as needed)
        echo "Reporting API is down! HTTP code: $http_code" | \
          mail -s "API Alert" admin@company.com 2>/dev/null || \
          echo "[$timestamp] Alert: API down, email failed" >> $LOGFILE
    fi
    
    sleep 60  # Check every minute
done
```

## Recovery Procedures

### API Server Recovery
```bash
#!/bin/bash
# recover_api.sh

echo "Starting API recovery procedure..."

# 1. Stop any existing processes
pkill -f "reporting_api.py"
sleep 5

# 2. Check and start MongoDB if needed
if ! pgrep mongod > /dev/null; then
    echo "Starting MongoDB..."
    brew services start mongodb-community  # macOS
    # sudo systemctl start mongod  # Linux
    sleep 10
fi

# 3. Restart API server
echo "Starting Reporting API..."
cd /Users/I032294/iisc_cds/CustomerServiceandConversationalAI-/performance_agent/customerConversationPerformanceAnalysis
nohup python src/reporting_api.py > reporting_api_recovery.log 2>&1 &

# 4. Wait and test
sleep 15
if curl -s http://localhost:8003/health | grep -q "healthy"; then
    echo "✅ API recovery successful"
else
    echo "❌ API recovery failed"
    echo "Check logs: reporting_api_recovery.log"
fi
```

### Database Recovery
```bash
#!/bin/bash
# recover_database.sh

echo "Starting database recovery procedure..."

# 1. Backup current data
echo "Creating backup..."
mongodump --db csai --out /tmp/mongodb_backup_$(date +%Y%m%d_%H%M%S)

# 2. Check and repair if needed
echo "Checking database..."
mongo csai --eval "db.runCommand({validate: 'agentic_analysis'})"

# 3. Recreate indexes if missing
echo "Recreating indexes..."
python -c "
from pymongo import MongoClient
client = MongoClient('mongodb://localhost:27017/')
db = client['csai']
collection = db['agentic_analysis']
collection.create_index('created_at')
collection.create_index('customer')
collection.create_index([('created_at', 1), ('customer', 1)])
print('Indexes recreated')
"

echo "Database recovery completed"
```

This troubleshooting guide covers the most common issues you might encounter when running the Reporting API and provides practical solutions for each scenario.
