# Customer Conversation Performance Analysis

A comprehensive Python project for analyzing customer service conversations and evaluating agent performance using configurable KPIs, machine learning, and NLP techniques.

## Features

- **Configuration-Based Analysis**: Flexible YAML-based configuration system for KPIs and evaluation criteria
- **Comprehensive Performance Metrics**: Evaluate agents across Accuracy & Compliance, Empathy & Communication Skills, and Efficiency & Resolution Effectiveness
- **Multi-Layered Analysis**: Support for conversation, category, and individual KPI analysis
- **RESTful API**: Easy-to-use API endpoints with comprehensive documentation
- **Advanced Service Layer**: Enhanced service with configurable evaluation framework
- **Extensive Testing**: Full test coverage including configuration system tests

## Project Structure

```
customerConversationPerformanceAnalysis/
├── config/
│   └── agent_performance_config.yaml  # Configuration for KPIs and evaluation criteria
├── src/
│   ├── __init__.py
│   ├── models.py                       # Data models and schemas
│   ├── service.py                      # Original business logic
│   ├── api.py                         # Original FastAPI endpoints
│   ├── config_loader.py               # Configuration loading and validation
│   ├── enhanced_service.py            # Enhanced service with config support
│   └── enhanced_api.py                # Enhanced API endpoints
├── tests/
│   ├── __init__.py
│   ├── test_main.py                   # Main functionality tests
│   ├── test_api.py                    # API endpoint tests
│   └── test_config_system.py          # Configuration system tests
├── main.py                            # Entry point
├── run_api.py                         # Original API server runner
├── run_enhanced_api.py                # Enhanced API server runner
├── sample_conversation.json           # Example data
├── requirements.txt                   # Dependencies
├── setup.cfg                          # Configuration for tools
├── pytest.ini                        # Pytest configuration
└── README.md                          # This file
```

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd customerConversationPerformanceAnalysis
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure AI Core Credentials:

The system now uses SAP AI Core instead of OpenAI. Configure your AI Core credentials in `config/aicore_credentials.yaml`:

```yaml
aicore:
  oauth:
    clientid: "your-client-id"
    clientsecret: "your-client-secret"
    url: "https://your-auth-url.authentication.sap.hana.ondemand.com"
    identityzone: "your-identity-zone"
    identityzoneid: "your-identity-zone-id"
    appname: "your-app-name"
  
  services:
    ai_api_url: "https://api.ai.your-region.aws.ml.hana.ondemand.com"
  
  model:
    default_model: "claude-4"
    temperature: 0.1
    max_tokens: 4000
  
  security:
    verify_ssl: true
    token_refresh:
      refresh_buffer: 300
      max_retries: 3
  
  logging:
    enable_request_logging: false
```

Replace the placeholder values with your actual AI Core credentials.

## Usage

### Running the Reporting API Server (New)

```bash
python run_reporting_api.py
```

The Reporting API will be available at `http://localhost:8003`

**Features:**
- Date range and customer-based reporting
- LLM-powered performance summaries
- Aggregated insights across multiple conversations
- "What went well", "What needs improvement", and "Training needs" analysis
- **Configurable data sources** - Switch between MongoDB and file-based data sources

**Data Source Configuration:**
The Reporting API now supports configurable data sources for sentiment analysis data:

- **MongoDB Source (Default)**: Reads from MongoDB collections
- **File Source**: Reads from JSON files or folders containing JSON files

Use the configuration endpoints to switch data sources:
```bash
# Configure file-based data source
curl -X POST "http://localhost:8003/config/datasource" \
  -H "Content-Type: application/json" \
  -d '{"source_type": "file", "file_path": "/path/to/sentiment/data"}'

# Configure MongoDB data source  
curl -X POST "http://localhost:8003/config/datasource" \
  -H "Content-Type: application/json" \
  -d '{"source_type": "mongodb", "collection_name": "agentic_analysis"}'

# Get current configuration
curl "http://localhost:8003/config/datasource"
```

Test the data source configuration:
```bash
python test_datasource_config.py
```

### Running the LLM Agent-based API Server (Recommended)

```bash
python run_llm_agent_api.py
```

The LLM Agent-based API will be available at `http://localhost:8002`

**Features:**
- AI-powered analysis using LLM agents
- Dynamic adaptation to configuration changes
- No code changes needed when updating KPIs
- Evidence-based scoring with detailed reasoning

### Running the Enhanced API Server

```bash
python run_enhanced_api.py
```

The Enhanced API will be available at `http://localhost:8001`

### Running the Original API Server

```bash
python run_api.py
```

The Original API will be available at `http://localhost:8000`

### API Documentation

- Reporting API: Visit `http://localhost:8003/docs` for interactive documentation
- Enhanced API: Visit `http://localhost:8001/docs` for interactive documentation
- Original API: Visit `http://localhost:8000/docs` for interactive documentation

## Enhanced API Endpoints

### Core Analysis Endpoints

- `POST /analyze/comprehensive` - Complete analysis across all configured KPIs and categories
- `POST /analyze/category/{category}` - Analysis for a specific category
- `POST /analyze/kpi/{category}/{kpi}` - Analysis for a specific KPI

### Configuration Endpoints

- `GET /config/info` - Basic configuration information
- `GET /config/categories` - All categories and their KPIs
- `GET /config/kpi/{category}/{kpi}` - Detailed KPI configuration
- `GET /config/validate` - Validate configuration
- `GET /analyze/benchmark` - Performance benchmarks and targets

### Utility Endpoints

- `GET /health` - Health check with configuration status
- `GET /` - API information and endpoint listing

## Performance Evaluation Framework

The system evaluates agent performance across three main categories:

### 1. Accuracy & Compliance
- **Resolution Completeness**: Whether issues are fully resolved
- **Accuracy of Automated Responses**: Quality of automated/AI responses

### 2. Empathy & Communication Skills
- **Empathy Score**: Comprehensive empathy evaluation with sub-factors:
  - Emotion Recognition
  - Acknowledgment of Feelings
  - Appropriate Response
  - Personalization
  - Supportive Language
  - Active Listening Indicators
- **Sentiment Shift**: Change in customer sentiment throughout conversation
- **Clarity of Language**: Language readability and comprehensibility with sub-factors:
  - Readability Level
  - Jargon Usage
  - Sentence Structure
  - Coherence
  - Active Voice Usage
  - Conciseness
- **Cultural Sensitivity Index**: Cultural awareness and sensitivity
- **Adaptability Quotient**: Ability to adjust communication style
- **Conversation Flow Smoothness**: Natural progression of conversation

### 3. Efficiency & Resolution Effectiveness
- **Follow-up Necessity**: Whether additional follow-ups are needed
- **Customer Effort Score**: Ease of issue resolution from customer perspective
- **First Response Accuracy**: Quality of initial response
- **Customer Satisfaction with Resolution**: Resolution-specific satisfaction
- **Escalation Rate**: Rate of escalation to higher support tiers
- **Customer Effort Reduction Rate**: Improvement in customer effort over time

## Configuration System

The system uses a flexible YAML-based configuration located at `config/agent_performance_config.yaml`. This allows for:

- **Configurable KPIs**: Add, modify, or remove KPIs without code changes
- **Flexible Scoring**: Define custom scales, targets, and interpretations
- **Weighted Sub-factors**: Complex KPIs with multiple weighted components
- **Target Setting**: Set specific targets for each KPI with operators (>=, >, <=, <, =)
- **Category Management**: Organize KPIs into logical categories

### Example Configuration Structure

```yaml
evaluation_framework:
  categories:
    empathy_communication:
      kpis:
        empathy_score:
          name: "Empathy Score"
          description: "Comprehensive measure of empathetic communication"
          sub_factors:
            emotion_recognition:
              weight: 0.2
              scale:
                type: "numeric"
                range: [0, 10]
            # ... more sub-factors
          target:
            value: 7
            operator: ">="
```

## Example Usage

### Comprehensive Analysis

```python
import requests

# Sample conversation data
conversation_data = {
    "tweets": [
        {
            "tweet_id": 1,
            "author_id": "customer1",
            "role": "Customer",
            "inbound": True,
            "created_at": "2023-01-01T10:00:00",
            "text": "I'm frustrated with my billing issue"
        },
        {
            "tweet_id": 2,
            "author_id": "agent1",
            "role": "Service Provider",
            "inbound": False,
            "created_at": "2023-01-01T10:05:00",
            "text": "I understand your frustration with the billing issue. Let me review your account and resolve this for you right away."
        },
        {
            "tweet_id": 3,
            "author_id": "customer1",
            "role": "Customer",
            "inbound": True,
            "created_at": "2023-01-01T10:10:00",
            "text": "Thank you so much! The issue has been resolved perfectly."
        }
    ],
    "classification": {
        "categorization": "Billing Issue",
        "intent": "Support Request",
        "topic": "Billing",
        "sentiment": "Positive"
    }
}

# Perform comprehensive analysis
response = requests.post("http://localhost:8001/analyze/comprehensive", json=conversation_data)
results = response.json()

# Results include:
# - categories: Analysis for each category (accuracy_compliance, empathy_communication, efficiency_resolution)
# - overall_performance: Overall scores and ratings
# - analysis_timestamp: When the analysis was performed
```

### Category-Specific Analysis

```python
# Analyze only empathy and communication skills
response = requests.post("http://localhost:8001/analyze/category/empathy_communication", json=conversation_data)
empathy_results = response.json()
```

### Configuration Information

```python
# Get configuration info
config_info = requests.get("http://localhost:8001/config/info").json()

# Get all categories
categories = requests.get("http://localhost:8001/config/categories").json()

# Get specific KPI configuration
kpi_config = requests.get("http://localhost:8001/config/kpi/empathy_communication/empathy_score").json()
```

## Development

### Running Tests

```bash
# Run all tests
pytest

# Run specific test files
pytest tests/test_config_system.py
pytest tests/test_api.py

# Run with coverage
pytest --cov=src --cov-report=html
```

### Code Quality

```bash
# Format code
black src/ tests/

# Linting
flake8 src/ tests/

# Type checking
mypy src/
```

### Adding New KPIs

1. Update the configuration file (`config/agent_performance_config.yaml`)
2. Add calculation logic in the enhanced service (`src/enhanced_service.py`)
3. Add tests for the new KPI
4. Update documentation

## Configuration Validation

The system includes comprehensive configuration validation:

```bash
# Validate configuration via API
curl http://localhost:8001/config/validate

# Or programmatically
from src.config_loader import validate_agent_performance_config
is_valid = validate_agent_performance_config()
```

## Advanced Features

### Customer and Timestamp Extraction
The periodic job service automatically extracts customer identification and timestamp information for each conversation analysis:

- **Customer Identification**: Extracts customer IDs from various sources:
  - Root-level `customer` field in sentiment analysis records
  - Nested `conversation.customer` field
  - First customer tweet's `author_id`
  - Fallback to `conversation_set` collection lookup
  - Defaults to "unknown" if not found

- **Timestamp Information**: Extracts `created_at` and `created_time`:
  - Root-level timestamp fields
  - Nested conversation timestamps
  - First tweet timestamps with automatic time extraction
  - Fallback collection lookup
  - Current timestamp as default

- **Final Output Schema**: All analysis results include at the root level:
  ```json
  {
    "customer": "customer_123",
    "created_at": "2023-01-15T14:30:00Z",
    "created_time": "14:30:00",
    "conversation_id": "conv_...",
    "conversation_summary": {...},
    "performance_metrics": {...}
  }
  ```

### Recommendations System
Each KPI analysis includes specific recommendations for improvement based on performance against targets.

### Interpretations
KPIs include interpretations (e.g., "Excellent", "Good", "Needs Improvement") based on score ranges.

### Flexible Scoring
Support for different scale types:
- Numeric (0-10, 1-5, etc.)
- Percentage (0-100%)
- Binary (0 or 1)
- Custom ranges

### Weighted Calculations
Complex KPIs can have multiple sub-factors with different weights for nuanced evaluation.

## Troubleshooting

### Configuration Issues
- Check YAML syntax in the configuration file
- Use the `/config/validate` endpoint to validate configuration
- Review logs for specific validation errors

### API Issues
- Check the `/health` endpoint for system status
- Ensure all required dependencies are installed
- Verify the configuration file exists and is readable

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add/update tests
5. Update configuration if needed
6. Run the test suite
7. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For questions or issues:
1. Check the API documentation at `/docs`
2. Review the configuration file structure
3. Run the test suite to identify issues
4. Open an issue in the project repository
