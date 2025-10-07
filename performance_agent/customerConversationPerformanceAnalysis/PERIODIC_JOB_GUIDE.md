# Periodic Job System Guide
## Customer Conversation Performance Analysis

This guide explains how to use the automated periodic job system that reads sentiment analysis data from MongoDB and produces performance analysis results.

## 🎯 Overview

The periodic job system automates the analysis of customer conversations by:

1. **Reading** from `csai.sentiment_analysis` collection
2. **Analyzing** conversation performance using Claude-4 via SAP AI Core
3. **Persisting** results to `csai.agentic_analysis` collection
4. **Tracking** processing state to avoid duplicate analysis

## 📁 Key Files

```
customerConversationPerformanceAnalysis/
├── src/periodic_job_service.py          # Core job logic
├── run_periodic_job.py                  # Main execution script
├── config/periodic_job_config.yaml     # Configuration settings
├── tests/test_periodic_job.py          # Unit tests
└── PERIODIC_JOB_GUIDE.md               # This guide
```

## 🚀 Quick Start

### 1. Install Dependencies

```bash
cd customerConversationPerformanceAnalysis
pip install -r requirements.txt
```

### 2. Configure MongoDB Connection

Set environment variable:
```bash
export MONGODB_CONNECTION_STRING="mongodb://your-connection-string:27017/"
```

Or use default localhost connection.

### 3. Run Single Batch (Testing)

```bash
python run_periodic_job.py --single-batch
```

### 4. View Job Statistics

```bash
python run_periodic_job.py --stats-only
```

### 5. Run Continuous Job

```bash
python run_periodic_job.py --interval 5
```

## 📊 Data Flow

```
┌─────────────────────┐    ┌─────────────────────┐    ┌─────────────────────┐
│  sentiment_analysis │───▶│  Periodic Job       │───▶│  agentic_analysis   │
│  (Source Data)      │    │  Service            │    │  (Results)          │
└─────────────────────┘    └─────────────────────┘    └─────────────────────┘
                                      │
                                      ▼
                           ┌─────────────────────┐
                           │  job_state          │
                           │  (Progress Tracker) │
                           └─────────────────────┘
```

### Input Schema (sentiment_analysis)
```json
{
  "_id": "ObjectId",
  "conversation": {
    "tweets": [
      {
        "tweet_id": 1,
        "author_id": "user123",
        "role": "Customer",
        "inbound": true,
        "created_at": "2023-01-01T10:00:00Z",
        "text": "I need help with my account"
      }
    ],
    "classification": {
      "categorization": "Technical Support",
      "intent": "Account Support",
      "topic": "Technical",
      "sentiment": "Neutral"
    }
  },
  "sentiment_analysis": {
    "overall_sentiment": "Positive",
    "intent": "Support Request",
    "topic": "Account"
  }
}
```

### Output Schema (agentic_analysis)
```json
{
  "_id": "ObjectId",
  "conversation_id": "conv_66f7c8e123456789abcdef01",
  "source_object_id": "66f7c8e123456789abcdef01",
  "source_timestamp": "2023-01-01T10:00:00Z",
  "conversation_summary": {
    "total_messages": 4,
    "customer_messages": 2,
    "agent_messages": 2,
    "conversation_type": "Technical Support",
    "intent": "Account Support",
    "topic": "Technical",
    "final_sentiment": "Positive",
    "categorization": "Technical Support - Account Issues"
  },
  "performance_metrics": {
    "accuracy_compliance": {
      "resolution_completeness": 1,
      "accuracy_automated_responses": 92.5
    },
    "empathy_communication": {
      "empathy_score": 8.7,
      "empathy_subfactors": {
        "emotion_recognition": 8.5,
        "acknowledgment_feelings": 9.0,
        "appropriate_response": 8.8,
        "personalization": 8.2,
        "supportive_language": 8.9,
        "active_listening": 8.1
      },
      "sentiment_shift": 0.6,
      "clarity_language": 8.9,
      "clarity_subfactors": {
        "readability_level": 8.8,
        "jargon_usage": 9.2,
        "sentence_structure": 8.7,
        "coherence": 9.0,
        "active_voice": 8.5,
        "conciseness": 8.9
      },
      "cultural_sensitivity": 4.1,
      "adaptability_quotient": 85,
      "conversation_flow": 4.3
    },
    "efficiency_resolution": {
      "followup_necessity": 0,
      "customer_effort_score": 2.1,
      "first_response_accuracy": 94.0,
      "csat_resolution": 4.8,
      "escalation_rate": 3.0,
      "customer_effort_reduction": 15.5
    }
  },
  "analysis_metadata": {
    "processed_timestamp": "2023-01-01T10:05:00Z",
    "source_collection": "sentiment_analysis",
    "analysis_version": "4.1.0",
    "model_used": "claude-4"
  },
  "persistence_metadata": {
    "inserted_timestamp": "2023-01-01T10:05:01Z",
    "collection": "agentic_analysis",
    "job_name": "conversation_performance_analysis"
  }
}
```

## ⚙️ Configuration Options

### Command Line Arguments

```bash
python run_periodic_job.py [OPTIONS]

Options:
  --mongo-uri TEXT        MongoDB connection string
  --db-name TEXT         Database name (default: csai)
  --interval INTEGER     Interval between runs in minutes (default: 5)
  --batch-size INTEGER   Records per batch (default: 50)
  --max-iterations INTEGER  Maximum iterations (default: infinite)
  --single-batch         Run only one batch
  --reset-state          Reset job state before starting
  --stats-only           Show statistics only
  --log-level TEXT       Logging level (DEBUG/INFO/WARNING/ERROR)
```

### Environment Variables

```bash
# MongoDB connection
export MONGODB_CONNECTION_STRING="mongodb://localhost:27017/"

# AI Core credentials (automatically loaded from config)
# See config/aicore_credentials.yaml
```

## 🔄 Job State Management

The system tracks processing progress using the `job_state` collection:

```json
{
  "_id": "ObjectId",
  "job_name": "conversation_performance_analysis",
  "last_processed_object_id": "66f7c8e123456789abcdef01",
  "last_updated": "2023-01-01T10:05:00Z",
  "status": "running",
  "data": {
    "iteration": 5,
    "batch_stats": {...},
    "total_stats": {...}
  }
}
```

### State Management Commands

```bash
# Reset job state (start from beginning)
python run_periodic_job.py --reset-state --single-batch

# Check current state
python run_periodic_job.py --stats-only
```

## 📈 Performance Metrics

The system analyzes **14 main KPIs** across **3 categories**:

### 1. Accuracy & Compliance (2 KPIs)
- **Resolution Completeness**: Binary (0/1) - Was the issue resolved?
- **Accuracy Automated Responses**: Percentage (0-100%) - Response accuracy

### 2. Empathy & Communication (6 KPIs)
- **Empathy Score**: (0-10) with 6 weighted sub-factors
- **Sentiment Shift**: (-1 to +1) - Customer sentiment change
- **Clarity of Language**: (1-10) with 6 weighted sub-factors  
- **Cultural Sensitivity**: (1-5) - Cultural awareness
- **Adaptability Quotient**: (0-100%) - Agent adaptability
- **Conversation Flow**: (1-5) - Natural conversation flow

### 3. Efficiency & Resolution (6 KPIs)
- **Follow-up Necessity**: Binary (0/1) - Follow-up required?
- **Customer Effort Score**: (1-7) - Customer effort level
- **First Response Accuracy**: (0-100%) - First response quality
- **Customer Satisfaction**: (1-5) - Resolution satisfaction
- **Escalation Rate**: (0-100%) - Escalation probability
- **Customer Effort Reduction**: (-100 to +100%) - Effort improvement

## 🚨 Error Handling

### Retry Logic
- **Max Retries**: 3 attempts per record
- **Backoff Strategy**: Exponential (5s, 10s, 20s)
- **Retriable Errors**: Connection, timeout, rate limit
- **Non-retriable**: Data validation, authentication

### Dead Letter Queue
Failed records are stored in `failed_analysis_records` collection for manual review.

### Logging
- **Log Level**: Configurable (DEBUG/INFO/WARNING/ERROR)
- **Log Files**: `periodic_job_YYYYMMDD.log`
- **Console Output**: Real-time status updates

## 🧪 Testing

### Run Unit Tests
```bash
cd customerConversationPerformanceAnalysis
python -m pytest tests/test_periodic_job.py -v
```

### Test Single Batch
```bash
python run_periodic_job.py --single-batch --log-level DEBUG
```

### Simulate Production Load
```bash
python run_periodic_job.py --batch-size 100 --max-iterations 10
```

## 📊 Monitoring

### Real-time Statistics
```bash
python run_periodic_job.py --stats-only
```

Expected output:
```
================================================================================
JOB STATISTICS
================================================================================
Job Status: completed
Last Updated: 2023-01-01 10:05:00
Last Processed ID: 66f7c8e123456789abcdef01
Agentic Analysis Records: 1,250
Latest Results: 10

Recent Analysis Results:
  • conv_66f7c8e123456789abcdef01 - 2023-01-01T10:05:00Z - claude-4
  • conv_66f7c8e123456789abcdef02 - 2023-01-01T10:04:55Z - claude-4
  ...
```

### Batch Processing Results
```bash
python run_periodic_job.py --single-batch
```

Expected output:
```
================================================================================
BATCH RESULTS
================================================================================
Records Processed: 50
Records Analyzed: 48
Records Persisted: 48
Errors: 2
Duration: 45.23 seconds
Last Processed ID: 66f7c8e123456789abcdef32
```

## 🔧 Troubleshooting

### Common Issues

1. **MongoDB Connection Failed**
   ```bash
   # Check connection string
   echo $MONGODB_CONNECTION_STRING
   
   # Test connection
   mongosh $MONGODB_CONNECTION_STRING
   ```

2. **No Records to Process**
   ```bash
   # Check source collection
   python -c "
   from pymongo import MongoClient
   client = MongoClient('$MONGODB_CONNECTION_STRING')
   print(f'sentiment_analysis count: {client.csai.sentiment_analysis.count_documents({})}')
   "
   ```

3. **AI Core Authentication Failed**
   ```bash
   # Check credentials file
   cat config/aicore_credentials.yaml
   
   # Test AI Core connection
   python -c "
   from src.aicore_service import AICoreService
   service = AICoreService()
   print('AI Core connection:', 'OK' if service.client else 'FAILED')
   "
   ```

4. **High Error Rate**
   ```bash
   # Check logs for specific errors
   tail -f periodic_job_$(date +%Y%m%d).log
   
   # Reset job state if needed
   python run_periodic_job.py --reset-state --stats-only
   ```

### Performance Optimization

1. **Increase Batch Size** (for high-volume processing)
   ```bash
   python run_periodic_job.py --batch-size 100
   ```

2. **Reduce Interval** (for real-time processing)
   ```bash
   python run_periodic_job.py --interval 1
   ```

3. **Enable Debug Logging** (for troubleshooting)
   ```bash
   python run_periodic_job.py --log-level DEBUG --single-batch
   ```

## 🏭 Production Deployment

### 1. Environment Setup
```bash
# Production environment
export ENVIRONMENT=production
export MONGODB_CONNECTION_STRING="mongodb+srv://prod-cluster/"
export LOG_LEVEL=INFO
```

### 2. Systemd Service (Linux)
```ini
# /etc/systemd/system/conversation-analysis.service
[Unit]
Description=Customer Conversation Performance Analysis
After=network.target

[Service]
Type=simple
User=appuser
WorkingDirectory=/opt/conversation-analysis
ExecStart=/opt/conversation-analysis/venv/bin/python run_periodic_job.py --interval 5
Restart=always
RestartSec=30

[Install]
WantedBy=multi-user.target
```

### 3. Docker Deployment
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["python", "run_periodic_job.py", "--interval", "5"]
```

### 4. Health Checks
```bash
# Health check endpoint (to be implemented)
curl http://localhost:8080/health

# Process monitoring
ps aux | grep run_periodic_job.py
```

## 📋 Maintenance

### Daily Tasks
- Check job statistics
- Review error logs
- Monitor processing rate

### Weekly Tasks  
- Analyze performance trends
- Review failed records
- Update configurations if needed

### Monthly Tasks
- Archive old logs
- Performance optimization review
- Capacity planning

## 🔗 Related Documentation

- [Main Project README](README.md)
- [Project Overview](PROJECT_OVERVIEW.md)
- [Agent Performance Configuration](config/agent_performance_config.yaml)
- [AI Core Integration Guide](src/aicore_service.py)

---

## 💡 Tips

1. **Start Small**: Use `--single-batch` for initial testing
2. **Monitor First**: Use `--stats-only` regularly to check progress
3. **Reset Carefully**: `--reset-state` will reprocess all data
4. **Log Everything**: Use appropriate log levels for troubleshooting
5. **Batch Size**: Adjust based on system performance and data volume

## 🆘 Support

For issues or questions:
1. Check logs: `tail -f periodic_job_*.log`  
2. Run diagnostics: `python run_periodic_job.py --stats-only`
3. Review test results: `python -m pytest tests/test_periodic_job.py -v`
4. Reset if needed: `python run_periodic_job.py --reset-state`
