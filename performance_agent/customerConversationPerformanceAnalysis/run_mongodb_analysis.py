#!/usr/bin/env python3
"""
MongoDB Performance Analysis Runner

This script processes conversations from MongoDB sentimental_analysis collection
and stores performance analysis results in agentic_analysis collection.
"""

import os
import sys
import json
import logging
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime

# Set OpenAI API key
os.environ["OPENAI_API_KEY"] = "sapaicore"

# Add src directory to Python path
src_dir = Path(__file__).parent / "src"
sys.path.insert(0, str(src_dir))

try:
    from src.mongodb_integration_service import create_mongodb_integration_service
    from src.models import ConversationData, Tweet, Classification
    from src.llm_agent_service import get_llm_agent_service
except ImportError as e:
    print(f"Error importing required modules: {e}")
    sys.exit(1)


def setup_logging():
    """Setup logging"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )


def process_sample_conversations():
    """Process the sample conversations we fetched"""
    
    # Sample conversations from MongoDB
    conversations = [
        {
            "_id": "68d581f05aabfd4596f3093c",
            "conversation_number": "4",
            "messages": None,
            "tweets": [
                {
                    "tweet_id": 5523,
                    "author_id": "117001",
                    "role": "Customer",
                    "inbound": True,
                    "created_at": "Tue Oct 31 23:12:51 +0000 2017",
                    "text": "@sprintcare @115714 thinking about upgrading my wife's iPhone 6.  What is your best offer?"
                },
                {
                    "tweet_id": 5522,
                    "author_id": "sprintcare",
                    "role": "Service Provider",
                    "inbound": False,
                    "created_at": "Tue Oct 31 23:16:16 +0000 2017",
                    "text": "@117001 Hey! We would need to see what offers are available to you. Send us a DM so we can further assist you. -CD"
                }
            ],
            "classification": {
                "categorization": "Inquiring about phone upgrade and offers",
                "intent": "Product Inquiry",
                "topic": "Product Info",
                "sentiment": "Neutral"
            }
        },
        {
            "_id": "68d581f05aabfd4596f3093f",
            "conversation_number": "7",
            "messages": None,
            "tweets": [
                {
                    "tweet_id": 8867,
                    "author_id": "117592",
                    "role": "Customer",
                    "inbound": True,
                    "created_at": "Tue Oct 31 23:28:34 +0000 2017",
                    "text": "@sprintcare @115714 the sad part is i'm at my own house. and everyone else that i live with, has service. https://t.co/OHhmkBfr0B"
                },
                {
                    "tweet_id": 8866,
                    "author_id": "117592",
                    "role": "Customer",
                    "inbound": True,
                    "created_at": "Tue Oct 31 23:30:23 +0000 2017",
                    "text": "@sprintcare @115714 never mind i can't even send txts. https://t.co/iWFDZrLDzF"
                },
                {
                    "tweet_id": 8864,
                    "author_id": "sprintcare",
                    "role": "Service Provider",
                    "inbound": False,
                    "created_at": "Tue Oct 31 23:52:12 +0000 2017",
                    "text": "@117592 We will like to take a look into this for you. Shoot us a DM to assist. -JA"
                },
                {
                    "tweet_id": 8865,
                    "author_id": "117592",
                    "role": "Customer",
                    "inbound": True,
                    "created_at": "Tue Oct 31 23:52:48 +0000 2017",
                    "text": "@sprintcare well i just tried calling you guys but it automatically fails. i had this problem an hour ago and it's back. just messaged you."
                }
            ],
            "classification": {
                "categorization": "No service or connectivity issue",
                "intent": "Technical Support",
                "topic": "Technical",
                "sentiment": "Negative"
            }
        },
        {
            "_id": "68d581f05aabfd4596f30942",
            "conversation_number": "10",
            "messages": None,
            "tweets": [
                {
                    "tweet_id": 11327,
                    "author_id": "118160",
                    "role": "Customer",
                    "inbound": True,
                    "created_at": "Wed Nov 01 00:49:44 +0000 2017",
                    "text": "@sprintcare WTF THEY JUST HUNG UP ON ME AGAIN!!!!"
                },
                {
                    "tweet_id": 11326,
                    "author_id": "sprintcare",
                    "role": "Service Provider",
                    "inbound": False,
                    "created_at": "Wed Nov 01 00:52:07 +0000 2017",
                    "text": "@118160 We want to help you, in order for us to do so, you'll need to send us a Direct Message so we can better assist. -AG"
                }
            ],
            "classification": {
                "categorization": "Frustration with previous interaction",
                "intent": "Technical Support",
                "topic": "Technical",
                "sentiment": "Negative"
            }
        }
    ]
    
    logger = logging.getLogger(__name__)
    integration_service = create_mongodb_integration_service()
    
    print("=" * 80)
    print("🚀 MongoDB Performance Analysis Processing")
    print("=" * 80)
    print(f"📊 Processing {len(conversations)} sample conversations")
    print("🤖 Using LLM Agent-based analysis with OpenAI GPT-4")
    print("💾 Preparing results for MongoDB storage")
    print()
    
    processed_results = []
    
    for i, conversation_doc in enumerate(conversations, 1):
        try:
            print(f"🔄 Processing conversation {i}/{len(conversations)} (ID: {conversation_doc['_id']})")
            
            # Convert to ConversationData model
            conversation_data = integration_service.convert_mongo_document_to_conversation_data(conversation_doc)
            
            # Get LLM service and analyze
            llm_service = get_llm_agent_service()
            analysis_results = llm_service.analyze_conversation_comprehensive(conversation_data)
            
            # Create result document
            result_doc = integration_service.create_analysis_result_document(conversation_doc, analysis_results)
            processed_results.append(result_doc)
            
            print(f"✅ Successfully analyzed conversation {i}/{len(conversations)}")
            
            # Display key results
            if "empathy_communication" in analysis_results.get("category_results", {}):
                empathy_score = analysis_results["category_results"]["empathy_communication"].get("empathy_score", {}).get("score", "N/A")
                print(f"   📈 Empathy Score: {empathy_score}")
            
            print()
            
        except Exception as e:
            logger.error(f"Error processing conversation {i}: {e}")
            print(f"❌ Failed to process conversation {i}: {e}")
            
            # Create error document
            error_doc = {
                "conversation_number": conversation_doc.get("conversation_number"),
                "original_id": str(conversation_doc.get("_id")),
                "tweets": conversation_doc.get("tweets", []),
                "classification": conversation_doc.get("classification", {}),
                "performance_analysis": {
                    "error": f"Analysis failed: {str(e)}",
                    "analysis_timestamp": datetime.utcnow().isoformat(),
                    "analysis_method": "Failed"
                }
            }
            processed_results.append(error_doc)
    
    # Generate summary
    summary = integration_service.extract_summary_statistics(processed_results)
    
    print("=" * 80)
    print("📊 Processing Summary")
    print("=" * 80)
    print(f"✅ Total Conversations: {summary['processing_summary']['total_conversations']}")
    print(f"✅ Successfully Analyzed: {summary['processing_summary']['successful_analyses']}")
    print(f"❌ Failed Analyses: {summary['processing_summary']['failed_analyses']}")
    print(f"📈 Success Rate: {summary['processing_summary']['success_rate']:.2f}%")
    print()
    
    # Save results to file for inspection
    output_file = "processed_conversations_sample.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(processed_results, f, indent=2, ensure_ascii=False, default=str)
    
    print(f"💾 Results saved to: {output_file}")
    print("🔍 Review the processed results before storing to MongoDB")
    print()
    
    return processed_results, summary


def main():
    """Main function"""
    setup_logging()
    
    try:
        processed_results, summary = process_sample_conversations()
        
        print("🎉 Sample processing completed!")
        print("📋 Next steps:")
        print("   1. Review processed_conversations_sample.json")
        print("   2. If satisfied, store results to MongoDB agentic_analysis collection")
        print("   3. Scale up to process all 917 conversations in batches")
        
        return processed_results
        
    except Exception as e:
        print(f"❌ Error in main processing: {e}")
        return None


if __name__ == "__main__":
    results = main()
