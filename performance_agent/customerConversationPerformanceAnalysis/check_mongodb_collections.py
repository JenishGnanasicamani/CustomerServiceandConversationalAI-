#!/usr/bin/env python3
"""
Script to check all available databases and collections in MongoDB
"""

import os
import sys
from datetime import datetime
from pathlib import Path

try:
    from pymongo import MongoClient
    from bson import ObjectId
    MONGODB_AVAILABLE = True
except ImportError as e:
    print(f"MongoDB not available: {e}")
    MONGODB_AVAILABLE = False
    sys.exit(1)

def check_mongodb_collections():
    """Check all available databases and collections"""
    
    # MongoDB connection
    mongo_connection_string = os.getenv('MONGODB_CONNECTION_STRING', 'mongodb://localhost:27017/')
    client = MongoClient(mongo_connection_string)
    
    print("=" * 80)
    print("MONGODB DATABASES AND COLLECTIONS")
    print("=" * 80)
    
    # List all databases
    databases = client.list_database_names()
    print(f"Available databases: {databases}")
    
    for db_name in databases:
        if db_name in ['admin', 'config', 'local']:
            continue  # Skip system databases
        
        print(f"\nDatabase: {db_name}")
        db = client[db_name]
        collections = db.list_collection_names()
        
        for collection_name in collections:
            collection = db[collection_name]
            count = collection.count_documents({})
            print(f"  - Collection: {collection_name} ({count} documents)")
            
            # Show sample document structure for collections with data
            if count > 0:
                sample_doc = collection.find_one({})
                if sample_doc:
                    print(f"    Sample keys: {list(sample_doc.keys())}")
                    
                    # Check for conversation-related fields
                    if 'conversation' in sample_doc:
                        print(f"    Has conversation field with keys: {list(sample_doc['conversation'].keys())}")
                    if 'tweets' in sample_doc:
                        print(f"    Has tweets field")
                    if 'classification' in sample_doc:
                        print(f"    Has classification field")
                    if 'sentiment_analysis' in sample_doc:
                        print(f"    Has sentiment_analysis field")
    
    client.close()

if __name__ == "__main__":
    check_mongodb_collections()
