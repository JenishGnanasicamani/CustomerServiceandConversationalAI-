# System Endpoints Comprehensive Summary

This document provides a complete overview of all exposed endpoints across the Customer Service and Conversational AI Performance Analysis system.

## System Overview

The system consists of multiple FastAPI services that provide different analysis capabilities:

1. **Main API** (`src/api.py`) - Basic conversation analysis
2. **Enhanced API** (`src/enhanced_api.py`) - Comprehensive agent performance evaluation
3. **LLM Agent API** (`src/llm_agent_api.py`) - LLM-based dynamic analysis
4. **Reporting API** (`src/reporting_api.py`) - MongoDB reporting and data access

---

## 1. Main API Endpoints (`src/api.py`)

**Base URL**: `http://localhost:8000`

### Core Analysis Endpoints
- `GET /` - Root endpoint with API information
- `POST /analyze` - Basic conversation analysis
- `GET /health` - Health check endpoint

---

## 2. Enhanced API Endpoints (`src/enhanced_api.py`)

**Base URL**: `http://localhost:8001`

### Analysis Endpoints
- `GET /` - Root endpoint with API information
- `POST /analyze/comprehensive` - Comprehensive analysis across all KPIs
- `POST /analyze/category/{category}` - Category-specific analysis
- `POST /analyze/kpi/{category}/{kpi}` - Individual KPI analysis

### Configuration Endpoints
- `GET /config/info` - Basic configuration information
- `GET /config/categories` - Detailed category information
- `GET /config/kpi/{category}/{kpi}` - Specific KPI configuration
- `GET /config/validate` - Configuration validation

### Benchmark Endpoints
- `GET /analyze/benchmark` - Performance benchmarks for all KPIs

### System Endpoints
- `GET /health` - Health check endpoint

---

## 3. LLM Agent API Endpoints (`src/llm_agent_api.py`)

**Base URL**: `http://localhost:8002`

### Analysis Endpoints
- `GET /` - Root endpoint with API information
- `POST /analyze/comprehensive` - LLM-based comprehensive analysis
- `POST /analyze/category/{category}` - LLM-based category analysis
- `POST /analyze/kpi/{category}/{kpi}` - LLM-based KPI analysis

### Configuration Endpoints
- `GET /available-kpis` - List all available KPIs
- `GET /validate-config` - Configuration validation

### System Endpoints
- `GET /health` - Health check endpoint

---

## 4. Reporting API Endpoints (`src/reporting_api.py`)

**Base URL**: `http://localhost:8003`

### Root and Health Endpoints
- `GET /` - Root endpoint with API information and available endpoints
- `GET /health` - Health check endpoint

### MongoDB Collection Endpoints
- `GET /collections` - List all available MongoDB collections
- `GET /collection/{collection_name}/info` - Collection information and statistics
- `GET /collection/{collection_name}/sample` - Sample documents from collection

### Data Analysis Endpoints
- `GET /analysis/performance-metrics` - Retrieve all performance analysis results
- `GET /analysis/performance-metrics/{limit}` - Retrieve limited performance analysis results
- `GET /analysis/conversation/{conversation_id}` - Get analysis for specific conversation
- `GET /analysis/summary` - Summary statistics of all analyses

### Data Export Endpoints
- `GET /export/performance-metrics` - Export all performance metrics to JSON
- `GET /export/performance-metrics/{limit}` - Export limited performance metrics to JSON

### Raw Data Access Endpoints
- `GET /raw/sentiment-analysis` - Access raw sentiment analysis data
- `GET /raw/sentiment-analysis/{limit}` - Access limited raw sentiment analysis data
- `GET /raw/conversation-set` - Access raw conversation set data
- `GET /raw/conversation-set/{limit}` - Access limited conversation set data

### Database Management Endpoints
- `GET /database/stats` - Database statistics and health information
- `POST /database/reset-counters` - Reset processing counters (admin endpoint)

---

## Endpoint Categories by Function

### 🔍 Analysis Endpoints
- **Basic Analysis**: `/analyze` (Main API)
- **Comprehensive Analysis**: `/analyze/comprehensive` (Enhanced API, LLM Agent API)
- **Category Analysis**: `/analyze/category/{category}` (Enhanced API, LLM Agent API)
- **KPI Analysis**: `/analyze/kpi/{category}/{kpi}` (Enhanced API, LLM Agent API)

### ⚙️ Configuration Endpoints
- **Config Info**: `/config/info` (Enhanced API)
- **Categories**: `/config/categories` (Enhanced API)
- **KPI Config**: `/config/kpi/{category}/{kpi}` (Enhanced API)
- **Available KPIs**: `/available-kpis` (LLM Agent API)
- **Validation**: `/config/validate` (Enhanced API), `/validate-config` (LLM Agent API)

### 📊 Data Access Endpoints
- **Collections**: `/collections` (Reporting API)
- **Collection Info**: `/collection/{collection_name}/info` (Reporting API)
- **Sample Data**: `/collection/{collection_name}/sample` (Reporting API)
- **Performance Metrics**: `/analysis/performance-metrics` (Reporting API)
- **Analysis Summary**: `/analysis/summary` (Reporting API)

### 📤 Export Endpoints
- **Export Metrics**: `/export/performance-metrics` (Reporting API)
- **Raw Data Access**: `/raw/sentiment-analysis`, `/raw/conversation-set` (Reporting API)

### 🏥 System Health Endpoints
- **Health Check**: `/health` (All APIs)
- **Database Stats**: `/database/stats` (Reporting API)

### 🛠️ Administrative Endpoints
- **Reset Counters**: `/database/reset-counters` (Reporting API)
- **Benchmarks**: `/analyze/benchmark` (Enhanced API)

---

## Port Allocation

| Service | Port | Purpose |
|---------|------|---------|
| Main API | 8000 | Basic conversation analysis |
| Enhanced API | 8001 | Comprehensive agent performance evaluation |
| LLM Agent API | 8002 | LLM-based dynamic analysis |
| Reporting API | 8003 | MongoDB reporting and data access |

---

## Authentication and Security

Currently, all endpoints are open and do not require authentication. For production deployment, consider implementing:
- API key authentication
- Rate limiting
- Input validation
- CORS configuration

---

## Testing Endpoints

### Quick Health Check
```bash
# Test all services
curl http://localhost:8000/health
curl http://localhost:8001/health  
curl http://localhost:8002/health
curl http://localhost:8003/health
```

### Sample Analysis Request
```bash
# Enhanced API comprehensive analysis
curl -X POST http://localhost:8001/analyze/comprehensive \
  -H "Content-Type: application/json" \
  -d '{
    "tweets": [
      {
        "tweet_id": 1,
        "author_id": "customer1",
        "role": "Customer",
        "inbound": true,
        "created_at": "2024-01-01T10:00:00Z",
        "text": "I need help with my account"
      }
    ],
    "classification": {
      "categorization": "Account Support",
      "intent": "Account Help",
      "topic": "Account",
      "sentiment": "Neutral"
    }
  }'
```

### Data Access Examples
```bash
# Get performance metrics
curl http://localhost:8003/analysis/performance-metrics/5

# Get collection info
curl http://localhost:8003/collections

# Export data
curl http://localhost:8003/export/performance-metrics/10
```

---

## Error Handling

All APIs follow consistent error response format:
```json
{
  "error": "Error type",
  "message": "Detailed error message",
  "timestamp": "2024-01-01T10:00:00Z"
}
```

Common HTTP status codes:
- `200` - Success
- `400` - Bad Request (invalid input)
- `404` - Not Found (resource doesn't exist)
- `500` - Internal Server Error

---

## Next Steps

1. **Production Deployment**: Configure proper authentication and security
2. **Load Balancing**: Consider load balancers for high-traffic scenarios
3. **Monitoring**: Implement logging and monitoring for all endpoints
4. **Documentation**: Generate OpenAPI/Swagger documentation for each service
5. **Testing**: Implement comprehensive endpoint testing suites

---

## Summary

The system exposes **47 total endpoints** across 4 services:
- **Main API**: 3 endpoints
- **Enhanced API**: 10 endpoints  
- **LLM Agent API**: 7 endpoints
- **Reporting API**: 17 endpoints

This comprehensive API ecosystem provides complete coverage for conversation analysis, performance evaluation, configuration management, data access, and system administration.
