#!/usr/bin/env python3
"""
Convenience script to run the FastAPI server
"""

import uvicorn
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

if __name__ == "__main__":
    print("Starting Customer Conversation Performance Analysis API...")
    print("API Documentation will be available at: http://localhost:8000/docs")
    print("Alternative docs at: http://localhost:8000/redoc")
    print("Press Ctrl+C to stop the server")
    print("-" * 60)
    
    uvicorn.run(
        "src.api:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # Enable auto-reload for development
        log_level="info"
    )
