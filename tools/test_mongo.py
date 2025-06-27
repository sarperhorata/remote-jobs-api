#!/usr/bin/env python3

import sys
import os
sys.path.append('backend')

from database import get_db
from datetime import datetime

def test_mongodb_connection():
    """Test MongoDB connection and basic operations"""
    
    try:
        print("🔌 Testing MongoDB connection...")
        
        # Get database connection
        db = get_db()
        
        # Test connection with a simple operation
        server_info = db.client.server_info()
        print(f"✅ Connected to MongoDB!")
        print(f"   Server version: {server_info.get('version', 'Unknown')}")
        
        # Test collections access
        collections = db.list_collection_names()
        print(f"📁 Available collections: {collections}")
        
        # Test write operation with a simple document
        test_collection = db["connection_test"]
        test_doc = {
            "test": True,
            "timestamp": datetime.now(),
            "message": "MongoDB connection test successful"
        }
        
        result = test_collection.insert_one(test_doc)
        print(f"✅ Test write successful! ID: {result.inserted_id}")
        
        # Test read operation
        retrieved_doc = test_collection.find_one({"_id": result.inserted_id})
        print(f"✅ Test read successful! Doc: {retrieved_doc['message']}")
        
        # Clean up test document
        test_collection.delete_one({"_id": result.inserted_id})
        print("🧹 Test document cleaned up")
        
        # Test jobs collection structure
        jobs_col = db["jobs"]
        job_count = jobs_col.count_documents({})
        print(f"📊 Current jobs in database: {job_count}")
        
        return True
        
    except Exception as e:
        print(f"❌ MongoDB connection failed: {str(e)}")
        print(f"🔧 Error details: {type(e).__name__}")
        
        # Check if it's an authentication error
        if "auth" in str(e).lower():
            print("🚨 This looks like an authentication error.")
            print("   Please check your MONGODB_URI in the .env file")
        
        return False

if __name__ == '__main__':
    success = test_mongodb_connection()
    
    if success:
        print("\n🎉 MongoDB is ready for use!")
    else:
        print("\n🔧 MongoDB connection needs to be fixed")
        print("   We can use local MongoDB for now") 