#!/usr/bin/env python3
"""
Script to setup and test AWS Cloud MongoDB connection
"""

import os
import sys
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

def test_mongodb_connection(connection_string: str, db_name: str = "csai"):
    """Test MongoDB connection and list collections"""
    
    try:
        print(f"Testing connection to: {connection_string[:50]}...")
        client = MongoClient(connection_string)
        
        # Test connection
        client.admin.command('ping')
        print("✓ Successfully connected to MongoDB!")
        
        # Get database
        db = client[db_name]
        collections = db.list_collection_names()
        
        print(f"\nDatabase: {db_name}")
        print(f"Available collections: {collections}")
        
        # Check for expected collections
        expected_collections = ["sentiment_analysis", "conversation_set", "conversations"]
        found_collections = []
        
        for collection_name in collections:
            collection = db[collection_name]
            count = collection.count_documents({})
            print(f"  - {collection_name}: {count} documents")
            
            if collection_name in expected_collections and count > 0:
                found_collections.append(collection_name)
                
                # Show sample document structure
                sample_doc = collection.find_one({})
                if sample_doc:
                    print(f"    Sample keys: {list(sample_doc.keys())}")
        
        if found_collections:
            print(f"\n✓ Found collections with data: {found_collections}")
            return True, found_collections[0]  # Return first collection with data
        else:
            print("\n⚠ No collections with conversation data found")
            return False, None
            
    except Exception as e:
        print(f"✗ Connection failed: {e}")
        return False, None
    finally:
        try:
            client.close()
        except:
            pass

def main():
    """Main function to setup cloud MongoDB connection"""
    
    print("=" * 80)
    print("AWS CLOUD MONGODB SETUP")
    print("=" * 80)
    
    # Check if connection string is provided as environment variable
    connection_string = os.getenv('MONGODB_CONNECTION_STRING')
    
    if not connection_string:
        print("Please provide your AWS MongoDB connection string.")
        print("You can either:")
        print("1. Set the MONGODB_CONNECTION_STRING environment variable")
        print("2. Enter it directly below")
        print()
        
        connection_string = input("Enter MongoDB connection string: ").strip()
        
        if not connection_string:
            print("No connection string provided. Exiting.")
            return
    
    # Test the connection
    success, collection_name = test_mongodb_connection(connection_string)
    
    if success and collection_name:
        print(f"\n✓ Connection successful! Found data in collection: {collection_name}")
        
        # Set environment variable for the session
        os.environ['MONGODB_CONNECTION_STRING'] = connection_string
        os.environ['ENVIRONMENT'] = 'production'  # Use production config
        
        print(f"\nEnvironment variables set:")
        print(f"  MONGODB_CONNECTION_STRING: {connection_string[:50]}...")
        print(f"  ENVIRONMENT: production")
        
        print(f"\nYou can now run the periodic job:")
        print(f"  export MONGODB_CONNECTION_STRING='{connection_string}'")
        print(f"  export ENVIRONMENT=production")
        print(f"  python run_periodic_job.py --single-batch --batch-size 50")
        
    else:
        print("\n✗ Connection failed or no data found. Please check your connection string.")

if __name__ == "__main__":
    main()
