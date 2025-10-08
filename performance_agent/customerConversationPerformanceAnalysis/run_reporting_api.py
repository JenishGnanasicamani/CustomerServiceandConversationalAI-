#!/usr/bin/env python3
"""
Runner script for the Customer Conversation Performance Reporting API
Starts the FastAPI server for generating performance reports with LLM summaries
"""

import os
import sys
from pathlib import Path
import uvicorn

# Add src directory to Python path
src_dir = Path(__file__).parent / "src"
sys.path.insert(0, str(src_dir))

from src.reporting_api import app

if __name__ == "__main__":
    # Configuration
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8003"))
    
    print("="*80)
    print("🚀 CUSTOMER CONVERSATION PERFORMANCE REPORTING API SERVER")
    print("="*80)
    print(f"🌐 Server starting on: http://{host}:{port}/")
    print(f"📊 API Documentation: http://{host}:{port}/docs")
    print(f"🔍 Interactive API: http://{host}:{port}/redoc")
    print("="*80)
    print("📋 Available Endpoints:")
    print("   • POST /reports/generate - Generate performance report (JSON body)")
    print("   • GET  /reports/generate - Generate performance report (query params)")
    print("   • GET  /reports/sample   - Get sample report structure")
    print("   • GET  /reports/stats    - Get collection statistics")
    print("   • GET  /health           - Health check")
    print("="*80)
    print("🎯 Key Features:")
    print("   • Date range filtering (start_date, end_date)")
    print("   • Customer-specific reports")
    print("   • LLM-powered insights and summaries")
    print("   • Performance metrics aggregation")
    print("   • Sentiment, Intent, and Topic analysis")
    print("="*80)
    print("📝 Sample Usage:")
    print("   POST /reports/generate")
    print("   {")
    print('     "start_date": "2023-01-01",')
    print('     "end_date": "2023-01-31",')
    print('     "customer": "customer_123"')
    print("   }")
    print("="*80)
    print("🔧 Environment Variables:")
    print(f"   • MONGODB_CONNECTION_STRING: {os.getenv('MONGODB_CONNECTION_STRING', 'mongodb://localhost:27017/')}")
    print(f"   • MONGODB_DB_NAME: {os.getenv('MONGODB_DB_NAME', 'csai')}")
    print("="*80)
    
    # Run the server
    uvicorn.run(
        app,
        host=host,
        port=port,
        reload=True,
        log_level="info"
    )
