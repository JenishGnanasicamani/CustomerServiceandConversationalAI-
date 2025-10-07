#!/usr/bin/env python3
"""
Debug script to check MongoDB query and record selection logic
"""

import os
import sys
from datetime import datetime
from pathlib import Path

# Add src directory to Python path
src_dir = Path(__file__).parent / "src"
sys.path.insert(0, str(src_dir))

try:
    from pymongo import MongoClient
    from bson import ObjectId
    MONGODB_AVAILABLE = True
except ImportError as e:
    print(f"MongoDB not available: {e}")
    MONGODB_AVAILABLE = False
    sys.exit(1)

def debug_mongodb_records():
    """Debug MongoDB records and query logic"""
    
    # MongoDB connection
    mongo_connection_string = os.getenv('MONGODB_CONNECTION_STRING', 'mongodb://localhost:27017/')
    client = MongoClient(mongo_connection_string)
    db = client['csai']
    
    # Collections
    sentiment_collection = db['sentiment_analysis']
    job_state_collection = db['job_state']
    agentic_collection = db['agentic_analysis']
    
    print("=" * 80)
    print("MONGODB DEBUG INFORMATION")
    print("=" * 80)
    
    # Check total records in sentiment_analysis
    total_sentiment_records = sentiment_collection.count_documents({})
    print(f"Total records in sentiment_analysis collection: {total_sentiment_records}")
    
    # Check agentic_analysis records
    total_agentic_records = agentic_collection.count_documents({})
    print(f"Total records in agentic_analysis collection: {total_agentic_records}")
    
    # Check job state
    job_name = "conversation_performance_analysis"
    job_state = job_state_collection.find_one({"job_name": job_name})
    print(f"\nJob state for '{job_name}':")
    if job_state:
        print(f"  - Status: {job_state.get('status', 'N/A')}")
        print(f"  - Last processed ObjectId: {job_state.get('last_processed_object_id', 'None')}")
        print(f"  - Last updated: {job_state.get('last_updated', 'N/A')}")
    else:
        print("  - No job state found (first run)")
    
    # Get sample records from sentiment_analysis
    print(f"\nSample records from sentiment_analysis (first 3):")
    sample_records = list(sentiment_collection.find({}).sort("_id", 1).limit(3))
    for i, record in enumerate(sample_records, 1):
        print(f"  Record {i}:")
        print(f"    - _id: {record['_id']}")
        print(f"    - Type: {type(record['_id'])}")
        print(f"    - Has conversation: {'conversation' in record}")
        if 'conversation' in record:
            conv = record['conversation']
            print(f"    - Has tweets: {'tweets' in conv}")
            if 'tweets' in conv:
                print(f"    - Tweet count: {len(conv['tweets'])}")
    
    # Test the query logic
    print(f"\nTesting query logic:")
    
    # Query without any filter (what should be returned on first run)
    query_no_filter = {}
    count_no_filter = sentiment_collection.count_documents(query_no_filter)
    print(f"  - Records with no filter: {count_no_filter}")
    
    # Query with last_processed_object_id filter (simulating incremental processing)
    last_processed_id = job_state.get('last_processed_object_id') if job_state else None
    if last_processed_id:
        try:
            last_object_id = ObjectId(last_processed_id)
            query_with_filter = {"_id": {"$gt": last_object_id}}
            count_with_filter = sentiment_collection.count_documents(query_with_filter)
            print(f"  - Records after ObjectId {last_processed_id}: {count_with_filter}")
            
            # Get the ObjectId range
            first_record = sentiment_collection.find_one({}, sort=[("_id", 1)])
            last_record = sentiment_collection.find_one({}, sort=[("_id", -1)])
            
            if first_record and last_record:
                print(f"  - First ObjectId in collection: {first_record['_id']}")
                print(f"  - Last ObjectId in collection: {last_record['_id']}")
                print(f"  - Last processed ObjectId: {last_object_id}")
                print(f"  - Comparison: last_processed >= last_in_collection? {last_object_id >= last_record['_id']}")
        
        except Exception as e:
            print(f"  - Error with ObjectId filter: {e}")
    else:
        print(f"  - No last processed ObjectId, should return all records")
    
    # Check if records have required structure
    print(f"\nChecking record structure:")
    records_with_conversation = sentiment_collection.count_documents({"conversation": {"$exists": True}})
    records_with_tweets = sentiment_collection.count_documents({"conversation.tweets": {"$exists": True}})
    print(f"  - Records with 'conversation' field: {records_with_conversation}")
    print(f"  - Records with 'conversation.tweets' field: {records_with_tweets}")
    
    # Show some sample record structures
    print(f"\nSample record structure:")
    sample_record = sentiment_collection.find_one({})
    if sample_record:
        print(f"  - Keys in record: {list(sample_record.keys())}")
        if 'conversation' in sample_record:
            print(f"  - Keys in conversation: {list(sample_record['conversation'].keys())}")
    
    client.close()

if __name__ == "__main__":
    debug_mongodb_records()
