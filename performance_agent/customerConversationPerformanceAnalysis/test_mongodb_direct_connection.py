#!/usr/bin/env python3
"""
Direct MongoDB connection test to diagnose the reporting API issue
"""

import os
from pymongo import MongoClient
import json
from datetime import datetime

def test_mongodb_direct_connection():
    """Test direct MongoDB connection and data retrieval"""
    
    print("🔧 DIRECT MONGODB CONNECTION TEST")
    print("=" * 60)
    
    # MongoDB connection
    connection_string = os.getenv('MONGODB_CONNECTION_STRING', 'mongodb://localhost:27017/')
    client = MongoClient(connection_string)
    db = client['csai']
    collection = db['agentic_analysis']
    
    print(f"✓ Connected to MongoDB: {connection_string}")
    print(f"✓ Database: {db.name}")
    print(f"✓ Collection: {collection.name}")
    
    # Test 1: Count total documents
    total_count = collection.count_documents({})
    print(f"\n📊 TOTAL DOCUMENTS IN COLLECTION: {total_count}")
    
    # Test 2: Find all documents (no limit)
    print(f"\n🔍 TESTING FIND ALL DOCUMENTS:")
    cursor = collection.find({})
    all_docs = list(cursor)
    print(f"   Documents retrieved with find({{}}): {len(all_docs)}")
    
    # Test 3: Find with explicit batch_size and limit parameters
    print(f"\n🔍 TESTING FIND WITH EXPLICIT PARAMETERS:")
    cursor = collection.find({}, batch_size=0, limit=0)
    explicit_docs = list(cursor)
    print(f"   Documents retrieved with find({{}}, batch_size=0, limit=0): {len(explicit_docs)}")
    
    # Test 4: Find with no batch size or limit
    print(f"\n🔍 TESTING FIND WITH NO PARAMETERS:")
    cursor = collection.find({})
    no_param_docs = list(cursor)
    print(f"   Documents retrieved with find({{}}): {len(no_param_docs)}")
    
    # Test 5: Check customer field in documents
    print(f"\n📋 ANALYZING CUSTOMER FIELD:")
    customer_values = set()
    for doc in all_docs:
        customer = doc.get('customer')
        customer_values.add(customer)
        print(f"   Document {doc.get('_id')}: customer = '{customer}'")
    
    print(f"\n   Unique customer values: {list(customer_values)}")
    
    # Test 6: Query by customer field
    print(f"\n🔍 TESTING CUSTOMER FILTER:")
    for customer_val in customer_values:
        if customer_val:
            cursor = collection.find({"customer": customer_val})
            customer_docs = list(cursor)
            print(f"   Documents with customer='{customer_val}': {len(customer_docs)}")
    
    # Test 7: Test different query approaches
    print(f"\n🧪 TESTING DIFFERENT QUERY APPROACHES:")
    
    # Approach 1: Simple find
    docs_1 = list(collection.find({}))
    print(f"   Approach 1 - collection.find({{}}): {len(docs_1)} documents")
    
    # Approach 2: Find with hint
    try:
        docs_2 = list(collection.find({}).hint("_id_"))
        print(f"   Approach 2 - collection.find({{}}).hint('_id_'): {len(docs_2)} documents")
    except Exception as e:
        print(f"   Approach 2 - Failed: {e}")
    
    # Approach 3: Aggregate instead of find
    try:
        pipeline = [{"$match": {}}]
        docs_3 = list(collection.aggregate(pipeline))
        print(f"   Approach 3 - collection.aggregate([{{'$match': {{}}}}]): {len(docs_3)} documents")
    except Exception as e:
        print(f"   Approach 3 - Failed: {e}")
    
    # Test 8: Check if there are any indexes or constraints
    print(f"\n📋 COLLECTION INDEXES:")
    indexes = list(collection.list_indexes())
    for idx in indexes:
        print(f"   Index: {idx}")
    
    # Close connection
    client.close()
    
    print(f"\n" + "=" * 60)
    print("MONGODB DIRECT CONNECTION TEST COMPLETE")
    
    if total_count != len(all_docs):
        print(f"❌ ISSUE FOUND: count_documents() returns {total_count} but find() returns {len(all_docs)}")
        print("   This indicates a cursor or connection issue")
    else:
        print(f"✅ MongoDB connection working correctly")
        print(f"   Both count_documents() and find() return {total_count} documents")
    
    return {
        "total_count": total_count,
        "find_count": len(all_docs),
        "customer_values": list(customer_values),
        "docs_sample": all_docs[:2] if all_docs else []
    }

def main():
    """Main function"""
    
    print("🔧 MONGODB DIRECT CONNECTION DIAGNOSTIC")
    print("Testing direct MongoDB connection to identify reporting API issue")
    print(f"Test run at: {datetime.now().isoformat()}")
    
    try:
        result = test_mongodb_direct_connection()
        
        print(f"\n🎯 DIAGNOSTIC RESULTS:")
        print(f"   Total documents (count): {result['total_count']}")
        print(f"   Documents via find(): {result['find_count']}")
        print(f"   Customer values found: {result['customer_values']}")
        
        if result['total_count'] == 5 and result['find_count'] == 5:
            print(f"✅ MongoDB is working correctly - issue is in the reporting service logic")
        elif result['total_count'] != result['find_count']:
            print(f"❌ MongoDB cursor issue detected")
        else:
            print(f"⚠️  Unexpected result - need further investigation")
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
