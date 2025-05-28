import os
import logging
from pymongo import MongoClient
from motor.motor_asyncio import AsyncIOMotorClient
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

class DummyAsyncCollection:
    def __init__(self, data):
        self.data = data
    
    async def find(self, query=None):
        return self.data
    
    async def find_one(self, query=None):
        return self.data[0] if self.data else None
    
    async def insert_one(self, document):
        return type('Result', (), {'inserted_id': 'dummy_id'})()
    
    async def update_one(self, query, update):
        return type('Result', (), {'modified_count': 1})()
    
    async def delete_one(self, query):
        return type('Result', (), {'deleted_count': 1})()
    
    async def count_documents(self, query=None):
        return len(self.data)
    
    def aggregate(self, pipeline):
        # Simple mock for aggregation
        return self.data

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

class DummyAsyncDatabase:
    def __init__(self):
        self.collections = {
            "jobs": DummyAsyncCollection(DUMMY_DATA["jobs"]),
            "users": DummyAsyncCollection(DUMMY_DATA["users"]),
            "ads": DummyAsyncCollection(DUMMY_DATA["ads"])
        }
    
    def __getitem__(self, collection_name):
        return self.collections.get(collection_name, DummyAsyncCollection([]))
    
    async def command(self, command):
        return {"ok": 1}

# Global connection instances
_sync_client = None
_async_client = None
_sync_db = None
_async_db = None

def get_db():
    """Get synchronous database connection with connection pooling"""
    global _sync_client, _sync_db
    
    if _sync_db is not None:
        return _sync_db
    
    # Try Atlas first, fallback to local MongoDB, then dummy data
    atlas_uri = os.environ.get("MONGODB_URI")
    local_uri = "mongodb://localhost:27017/"
    db_name = os.environ.get("MONGODB_DB_NAME", "buzz2remote")
    
    # Try Atlas connection first if configured
    if atlas_uri and atlas_uri != "mongodb://localhost:27017/" and atlas_uri != "your_mongodb_uri":
        try:
            logger.info(f"Attempting Atlas connection...")
            _sync_client = MongoClient(
                atlas_uri, 
                serverSelectionTimeoutMS=5000,
                maxPoolSize=50,  # Connection pool optimization
                minPoolSize=5,
                maxIdleTimeMS=30000,
                waitQueueTimeoutMS=5000
            )
            # Test connection
            _sync_client.server_info()
            logger.info("✅ Connected to MongoDB Atlas")
            _sync_db = _sync_client[db_name]
            return _sync_db
        except Exception as e:
            logger.warning(f"❌ Atlas connection failed: {str(e)}")
            logger.info("🔄 Falling back to local MongoDB...")
    
    # Try local MongoDB
    try:
        logger.info(f"Connecting to local MongoDB: {local_uri}")
        _sync_client = MongoClient(
            local_uri, 
            serverSelectionTimeoutMS=5000,
            maxPoolSize=50,
            minPoolSize=5,
            maxIdleTimeMS=30000,
            waitQueueTimeoutMS=5000
        )
        # Test connection
        _sync_client.server_info()
        logger.info(f"✅ Connected to local MongoDB")
        logger.info(f"Database name: {db_name}")
        _sync_db = _sync_client[db_name]
        return _sync_db
    except Exception as e:
        logger.warning(f"❌ Local MongoDB connection failed: {str(e)}")
        logger.info("🔄 Using dummy data for development...")
        _sync_db = DummyDatabase()
        return _sync_db

async def get_async_db():
    """Get asynchronous database connection with connection pooling"""
    global _async_client, _async_db
    
    if _async_db is not None:
        return _async_db
    
    # Try Atlas first, fallback to local MongoDB, then dummy data
    atlas_uri = os.environ.get("MONGODB_URI")
    local_uri = "mongodb://localhost:27017/"
    db_name = os.environ.get("MONGODB_DB_NAME", "buzz2remote")
    
    # Try Atlas connection first if configured
    if atlas_uri and atlas_uri != "mongodb://localhost:27017/" and atlas_uri != "your_mongodb_uri":
        try:
            logger.info(f"Attempting async Atlas connection...")
            _async_client = AsyncIOMotorClient(
                atlas_uri, 
                serverSelectionTimeoutMS=5000,
                maxPoolSize=50,  # Connection pool optimization
                minPoolSize=5,
                maxIdleTimeMS=30000,
                waitQueueTimeoutMS=5000
            )
            # Test connection
            await _async_client.admin.command('ping')
            logger.info("✅ Connected to MongoDB Atlas (async)")
            _async_db = _async_client[db_name]
            return _async_db
        except Exception as e:
            logger.warning(f"❌ Async Atlas connection failed: {str(e)}")
            logger.info("🔄 Falling back to local MongoDB...")
    
    # Try local MongoDB
    try:
        logger.info(f"Connecting to local MongoDB (async): {local_uri}")
        _async_client = AsyncIOMotorClient(
            local_uri, 
            serverSelectionTimeoutMS=5000,
            maxPoolSize=50,
            minPoolSize=5,
            maxIdleTimeMS=30000,
            waitQueueTimeoutMS=5000
        )
        # Test connection
        await _async_client.admin.command('ping')
        logger.info(f"✅ Connected to local MongoDB (async)")
        logger.info(f"Database name: {db_name}")
        _async_db = _async_client[db_name]
        return _async_db
    except Exception as e:
        logger.warning(f"❌ Local MongoDB connection failed (async): {str(e)}")
        logger.info("🔄 Using dummy data for development...")
        _async_db = DummyAsyncDatabase()
        return _async_db

async def ensure_indexes():
    """Ensure database indexes for optimal performance"""
    try:
        db = await get_async_db()
        
        # Jobs collection indexes
        await db.jobs.create_index("company")
        await db.jobs.create_index("created_at")
        await db.jobs.create_index("location")
        await db.jobs.create_index("is_active")
        await db.jobs.create_index([("company", 1), ("created_at", -1)])  # Compound index
        await db.jobs.create_index([("location", 1), ("is_active", 1)])   # Compound index
        
        # Users collection indexes
        await db.users.create_index("email", unique=True)
        await db.users.create_index("telegram_user_id", unique=True, sparse=True)
        
        logger.info("✅ Database indexes created successfully")
        
    except Exception as e:
        logger.warning(f"Failed to create indexes: {e}")

def close_db_connections():
    """Close database connections"""
    global _sync_client, _async_client, _sync_db, _async_db
    
    if _sync_client:
        _sync_client.close()
        _sync_client = None
        _sync_db = None
        
    if _async_client:
        _async_client.close()
        _async_client = None
        _async_db = None 