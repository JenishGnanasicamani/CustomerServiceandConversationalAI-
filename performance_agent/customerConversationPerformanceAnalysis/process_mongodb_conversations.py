#!/usr/bin/env python3
"""
MongoDB Conversation Processing Script

This script processes all conversations from the MongoDB sentimental_analysis collection,
runs performance analysis on them, and stores the results in the agentic_analysis collection.
"""

import os
import sys
import json
import logging
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime

# Add src directory to Python path
src_dir = Path(__file__).parent / "src"
sys.path.insert(0, str(src_dir))

try:
    from src.mongodb_integration_service import create_mongodb_integration_service
    from src.llm_agent_service import get_llm_agent_service
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
            logging.FileHandler('mongodb_processing.log')
        ]
    )


def check_environment():
    """Check if environment is properly configured"""
    logger = logging.getLogger(__name__)
    
    # Check OpenAI API key
    if not os.getenv("OPENAI_API_KEY"):
        logger.error("OPENAI_API_KEY environment variable not set")
        print("\nERROR: OPENAI_API_KEY environment variable not set.")
        print("Please set your OpenAI API key:")
        print("export OPENAI_API_KEY='your-api-key-here'")
        return False
    
    # Check configuration
    try:
        config_valid = validate_agent_performance_config()
        if config_valid:
            logger.info("Configuration validation successful")
            return True
        else:
            logger.error("Configuration validation failed")
            print("Configuration validation failed - please check config/agent_performance_config.yaml")
            return False
    except Exception as e:
        logger.error(f"Configuration check failed: {e}")
        print(f"Configuration error: {e}")
        return False


class MongoDBProcessor:
    """MongoDB conversation processor using MCP tools"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.integration_service = create_mongodb_integration_service()
    
    def fetch_all_conversations(self) -> List[Dict[str, Any]]:
        """
        Fetch all conversations from sentimental_analysis collection
        Note: This will be implemented using MCP tools in the actual execution
        """
        # This is a placeholder - actual implementation will use MCP tools
        # The calling script will handle the MCP tool calls
        pass
    
    def store_processed_conversations(self, processed_docs: List[Dict[str, Any]]):
        """
        Store processed conversations to agentic_analysis collection
        Note: This will be implemented using MCP tools in the actual execution
        """
        # This is a placeholder - actual implementation will use MCP tools
        # The calling script will handle the MCP tool calls
        pass
    
    def process_conversation_batch(self, conversations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Process a batch of conversations"""
        return self.integration_service.process_conversations_batch(conversations)
    
    def extract_summary_statistics(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Extract summary statistics"""
        return self.integration_service.extract_summary_statistics(results)


def main():
    """Main processing function"""
    setup_logging()
    logger = logging.getLogger(__name__)
    
    print("=" * 80)
    print("🔄 MongoDB Conversation Performance Analysis Processor")
    print("=" * 80)
    print("📊 Processing conversations from sentimental_analysis collection")
    print("🤖 Using LLM Agent-based performance analysis")
    print("💾 Storing results in agentic_analysis collection")
    print()
    
    # Environment checks
    if not check_environment():
        print("❌ Environment check failed. Please fix the issues above.")
        sys.exit(1)
    
    # Initialize processor
    try:
        processor = MongoDBProcessor()
        logger.info("MongoDB processor initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize processor: {e}")
        print(f"❌ Failed to initialize processor: {e}")
        sys.exit(1)
    
    print("✅ Environment validation passed")
    print("✅ MongoDB processor initialized")
    print()
    
    print("📋 Processing Instructions:")
    print("This script requires MongoDB connection using MCP tools.")
    print("Please run the following commands manually or use the MCP-integrated version:")
    print()
    print("1. Connect to MongoDB:")
    print("   mongodb+srv://cia_db_user:qG5hStEqWkvAHrVJ@capstone-project.yyfpvqh.mongodb.net/...")
    print()
    print("2. Fetch conversations from csai.sentimental_analysis")
    print("3. Process each conversation through performance analysis")
    print("4. Store results in csai.agentic_analysis")
    print()
    print("⚠️  This is a preparation script. The actual processing requires MCP MongoDB tools.")
    print("   Please use the integrated MCP processing approach.")
    
    return {
        "status": "prepared",
        "message": "MongoDB processor ready for MCP-integrated execution",
        "timestamp": datetime.utcnow().isoformat()
    }


if __name__ == "__main__":
    try:
        result = main()
        print(f"\n✅ Status: {result['status']}")
        print(f"📝 Message: {result['message']}")
    except KeyboardInterrupt:
        print("\n🔴 Process interrupted by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)
