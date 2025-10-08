#!/usr/bin/env python3
"""
Runner script for the Enhanced Agent Performance Analysis API
"""

import uvicorn
import sys
import os
from pathlib import Path

# Add the src directory to the Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def main():
    """Run the enhanced API server"""
    try:
        print("Starting Enhanced Agent Performance Analysis API...")
        print("API Documentation will be available at: http://localhost:8001/docs")
        print("API will be running at: http://localhost:8001")
        print("\nAvailable endpoints:")
        print("  - POST /analyze/comprehensive - Comprehensive analysis")
        print("  - POST /analyze/category/{category} - Category-specific analysis")
        print("  - POST /analyze/kpi/{category}/{kpi} - KPI-specific analysis")
        print("  - GET /config/info - Configuration information")
        print("  - GET /config/categories - All categories")
        print("  - GET /config/kpi/{category}/{kpi} - KPI configuration")
        print("  - GET /analyze/benchmark - Performance benchmarks")
        print("  - GET /health - Health check")
        print("\nPress Ctrl+C to stop the server")
        
        uvicorn.run(
            "enhanced_api:app",
            host="0.0.0.0",
            port=8001,
            reload=True,
            reload_dirs=["src"],
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\nShutting down Enhanced API server...")
    except Exception as e:
        print(f"Failed to start server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
