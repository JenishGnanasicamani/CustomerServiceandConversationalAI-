#!/usr/bin/env python3
"""
Direct MongoDB query to examine agentic_analysis collection records
"""

import os
import json
from datetime import datetime
from pymongo import MongoClient

def connect_to_mongodb():
    """Connect to MongoDB and return client and database"""
    try:
        mongo_connection_string = os.getenv('MONGODB_CONNECTION_STRING', 'mongodb://localhost:27017/')
        db_name = os.getenv('MONGODB_DB_NAME', 'csai')
        
        client = MongoClient(mongo_connection_string)
        db = client[db_name]
        
        # Test connection
        client.admin.command('ping')
        print(f"✅ Connected to MongoDB database: {db_name}")
        
        return client, db
        
    except Exception as e:
        print(f"❌ Failed to connect to MongoDB: {e}")
        return None, None

def examine_agentic_collection(db):
    """Examine the agentic_analysis collection"""
    try:
        collection = db['agentic_analysis']
        
        # Get collection stats
        total_count = collection.count_documents({})
        print(f"\n📊 Collection Statistics:")
        print(f"   Total documents: {total_count}")
        
        if total_count == 0:
            print("   No documents found in collection")
            return
        
        # Get all documents
        print(f"\n📋 All Documents:")
        documents = list(collection.find({}))
        
        for i, doc in enumerate(documents, 1):
            print(f"\n--- Document {i} ---")
            print(f"_id: {doc.get('_id')}")
            print(f"conversation_id: {doc.get('conversation_id')}")
            print(f"customer: {doc.get('customer')}")
            print(f"created_at: {doc.get('created_at')}")
            print(f"created_time: {doc.get('created_time')}")
            
            # Show structure
            print(f"Fields: {list(doc.keys())}")
            
            # Save full document to file for inspection
            filename = f"mongodb_document_{i}.json"
            with open(filename, 'w') as f:
                json.dump(doc, f, indent=2, default=str)
            print(f"Full document saved to: {filename}")
        
        # Test various queries to understand the filtering issue
        print(f"\n🔍 Testing Various Queries:")
        
        # Query 1: Find all records (no filter)
        query1 = {}
        count1 = collection.count_documents(query1)
        print(f"Query 1 - No filter: {count1} records")
        
        # Query 2: Find by customer "Apple"
        query2 = {"customer": "Apple"}
        count2 = collection.count_documents(query2)
        print(f"Query 2 - Customer 'Apple': {count2} records")
        
        # Query 3: Find by date range (loose)
        query3 = {"created_at": {"$exists": True}}
        count3 = collection.count_documents(query3)
        print(f"Query 3 - Has created_at field: {count3} records")
        
        # Query 4: Find by date range (original API query)
        query4 = {
            "created_at": {
                "$gte": "2000-01-01T00:00:00Z",
                "$lte": "2100-12-31T23:59:59Z"
            }
        }
        count4 = collection.count_documents(query4)
        print(f"Query 4 - Original API date range: {count4} records")
        
        # Query 5: Find by date range without Z suffix
        query5 = {
            "created_at": {
                "$gte": "2000-01-01",
                "$lte": "2100-12-31"
            }
        }
        count5 = collection.count_documents(query5)
        print(f"Query 5 - Date range without Z: {count5} records")
        
        # Query 6: Find by date range with regex pattern
        query6 = {
            "created_at": {
                "$regex": "^2025-10-05"
            }
        }
        count6 = collection.count_documents(query6)
        print(f"Query 6 - Date regex pattern: {count6} records")
        
        # Query 7: Combined query (customer + date)
        query7 = {
            "customer": "Apple",
            "created_at": {"$exists": True}
        }
        count7 = collection.count_documents(query7)
        print(f"Query 7 - Customer 'Apple' + has date: {count7} records")
        
        # Show sample records for successful queries
        if count7 > 0:
            print(f"\n📄 Sample record from Query 7:")
            sample = collection.find_one(query7)
            print(json.dumps(sample, indent=2, default=str))
        
    except Exception as e:
        print(f"❌ Error examining collection: {e}")

def main():
    """Main function"""
    print("🔍 MongoDB Collection Examination Tool")
    print("=" * 50)
    
    # Connect to MongoDB
    client, db = connect_to_mongodb()
    if not client:
        return 1
    
    try:
        # Examine the collection
        examine_agentic_collection(db)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1
    
    finally:
        if client:
            client.close()
            print(f"\n✅ MongoDB connection closed")
    
    return 0

if __name__ == "__main__":
    import sys
    sys.exit(main())
