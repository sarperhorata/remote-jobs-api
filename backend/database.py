import os
import logging
from pymongo import MongoClient
from typing import Dict, Any

logger = logging.getLogger(__name__)

# Dummy data for fallback
DUMMY_DATA = {
    "jobs": [
        {
            "_id": "dummy_job_1",
            "title": "Senior Frontend Developer",
            "company": "Remote Tech Co",
            "location": "Remote",
            "description": "We are looking for a senior frontend developer...",
            "skills": ["React", "TypeScript", "Node.js"],
            "salary": 80000,
            "posted_at": "2024-01-15T10:00:00Z",
            "is_active": True
        },
        {
            "_id": "dummy_job_2", 
            "title": "Backend Engineer",
            "company": "Global Solutions",
            "location": "Remote",
            "description": "Join our backend team to build scalable APIs...",
            "skills": ["Python", "FastAPI", "MongoDB"],
            "salary": 90000,
            "posted_at": "2024-01-14T15:30:00Z",
            "is_active": True
        }
    ],
    "users": [],
    "ads": []
}

class DummyCollection:
    def __init__(self, data):
        self.data = data
    
    def find(self, query=None):
        return self.data
    
    def find_one(self, query=None):
        return self.data[0] if self.data else None
    
    def insert_one(self, document):
        return type('Result', (), {'inserted_id': 'dummy_id'})()
    
    def update_one(self, query, update):
        return type('Result', (), {'modified_count': 1})()
    
    def delete_one(self, query):
        return type('Result', (), {'deleted_count': 1})()
    
    def count_documents(self, query=None):
        return len(self.data)

class DummyDatabase:
    def __init__(self):
        self.collections = {
            "jobs": DummyCollection(DUMMY_DATA["jobs"]),
            "users": DummyCollection(DUMMY_DATA["users"]),
            "ads": DummyCollection(DUMMY_DATA["ads"])
        }
    
    def __getitem__(self, collection_name):
        return self.collections.get(collection_name, DummyCollection([]))
    
    def command(self, command):
        return {"ok": 1}

def get_db():
    # Try Atlas first, fallback to local MongoDB, then dummy data
    atlas_uri = os.environ.get("MONGODB_URI")
    local_uri = "mongodb://localhost:27017/"
    db_name = os.environ.get("MONGODB_DB_NAME", "buzz2remote")
    
    # Try Atlas connection first if configured
    if atlas_uri and atlas_uri != "mongodb://localhost:27017/" and atlas_uri != "your_mongodb_uri":
        try:
            logger.info(f"Attempting Atlas connection...")
            client = MongoClient(atlas_uri, serverSelectionTimeoutMS=5000)
            # Test connection
            client.server_info()
            logger.info("✅ Connected to MongoDB Atlas")
            return client[db_name]
        except Exception as e:
            logger.warning(f"❌ Atlas connection failed: {str(e)}")
            logger.info("🔄 Falling back to local MongoDB...")
    
    # Try local MongoDB
    try:
        logger.info(f"Connecting to local MongoDB: {local_uri}")
        client = MongoClient(local_uri, serverSelectionTimeoutMS=5000)
        # Test connection
        client.server_info()
        logger.info(f"✅ Connected to local MongoDB")
        logger.info(f"Database name: {db_name}")
        return client[db_name]
    except Exception as e:
        logger.warning(f"❌ Local MongoDB connection failed: {str(e)}")
        logger.info("🔄 Using dummy data for development...")
        return DummyDatabase() 