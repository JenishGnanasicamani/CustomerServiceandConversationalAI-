#!/usr/bin/env python3
"""
Runner script for LLM Agent-based Conversation Performance Analysis API

This script starts the AI-powered API that uses LLM agents for dynamic conversation analysis.
The system automatically adapts to configuration changes without requiring code modifications.
"""

import os
import sys
import logging
from pathlib import Path

# Add src directory to Python path
src_dir = Path(__file__).parent / "src"
sys.path.insert(0, str(src_dir))

try:
    import uvicorn
    from src.llm_agent_api import app
    from src.config_loader import validate_agent_performance_config
except ImportError as e:
    print(f"Error importing required modules: {e}")
    print("Make sure to install dependencies: pip install -r requirements.txt")
    sys.exit(1)


def setup_logging():
    """Setup logging configuration"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('llm_agent_api.log')
        ]
    )


def check_environment():
    """Check if environment is properly configured"""
    logger = logging.getLogger(__name__)
    
    # Check AI Core credentials
    try:
        from src.aicore_service import get_aicore_client
        client = get_aicore_client()
        health_status = client.health_check()
        if health_status.get("status") == "healthy":
            logger.info("AI Core connection verified successfully")
            print("✅ AI Core connection verified successfully")
        else:
            logger.warning(f"AI Core health check failed: {health_status.get('error', 'Unknown error')}")
            print(f"⚠️  AI Core health check failed: {health_status.get('error', 'Unknown error')}")
            print("The API will still start but LLM functionality may be limited.\n")
    except Exception as e:
        logger.warning(f"Failed to verify AI Core connection: {e}")
        print(f"⚠️  Failed to verify AI Core connection: {e}")
        print("Please check your AI Core credentials in config/aicore_credentials.yaml")
        print("The API will still start but LLM functionality may be limited.\n")
    
    # Check configuration
    try:
        config_valid = validate_agent_performance_config()
        if config_valid:
            logger.info("Configuration validation successful")
        else:
            logger.warning("Configuration validation failed - some features may not work")
    except Exception as e:
        logger.error(f"Configuration check failed: {e}")
        print(f"Configuration error: {e}")
        print("Please check your configuration file: config/agent_performance_config.yaml")


def main():
    """Main function to run the LLM Agent API server"""
    setup_logging()
    logger = logging.getLogger(__name__)
    
    print("=" * 80)
    print("🤖 LLM Agent-based Conversation Performance Analysis API")
    print("=" * 80)
    print("🚀 AI-powered analysis using configurable KPIs with LLM agents")
    print("📋 Dynamic adaptation to configuration changes without code modifications")
    print("🔧 Powered by LangChain and Claude-4 model via SAP AI Core")
    print()
    
    # Environment checks
    check_environment()
    
    # Configuration info
    print("📁 Configuration:")
    print(f"   - Config file: config/agent_performance_config.yaml")
    print(f"   - Log file: llm_agent_api.log")
    print()
    
    print("🌐 API Information:")
    print(f"   - Host: 0.0.0.0")
    print(f"   - Port: 8002")
    print(f"   - Documentation: http://localhost:8002/docs")
    print(f"   - ReDoc: http://localhost:8002/redoc")
    print(f"   - Health Check: http://localhost:8002/health")
    print()
    
    print("🔍 Key Features:")
    print("   - LLM Agent-based analysis using LangChain")
    print("   - Dynamic KPI evaluation without code changes")
    print("   - Configuration-driven analysis framework")
    print("   - Evidence-based scoring with reasoning")
    print("   - Comprehensive, category, and KPI-level analysis")
    print()
    
    print("🛠️ Available Endpoints:")
    print("   Analysis:")
    print("     POST /analyze/comprehensive - Complete analysis across all KPIs")
    print("     POST /analyze/category/{category} - Category-specific analysis")
    print("     POST /analyze/kpi/{category}/{kpi} - Individual KPI analysis")
    print("   Agent:")
    print("     GET /agent/info - Agent configuration and status")
    print("     GET /agent/validate - Validate agent configuration")
    print("     GET /agent/available-kpis - List all available KPIs")
    print("   Configuration:")
    print("     GET /config/info - Configuration information")
    print("     GET /config/validate - Validate configuration")
    print("   Utility:")
    print("     GET /health - Health check")
    print("     GET / - API information")
    print()
    
    print("💡 Usage Tips:")
    print("   - The agent automatically adapts to configuration changes")
    print("   - Add/modify KPIs in the YAML config without code changes")
    print("   - Use /docs for interactive API testing")
    print("   - Monitor /health for system status")
    print("   - Check logs for detailed analysis information")
    print()
    
    try:
        logger.info("Starting LLM Agent-based API server on port 8002")
        print("🟢 Starting server... (Press Ctrl+C to stop)")
        print("=" * 80)
        
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=8002,
            log_level="info",
            access_log=True,
            reload=False  # Disable reload in production
        )
        
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
        print("\n🔴 Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {e}")
        print(f"\n❌ Server error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
