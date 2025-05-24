import os
import logging
from pymongo import MongoClient

logger = logging.getLogger(__name__)

def get_db():
    # Try Atlas first, fallback to local MongoDB
    atlas_uri = os.environ.get("MONGODB_URI")
    local_uri = "mongodb://localhost:27017/"
    db_name = os.environ.get("MONGODB_DB_NAME", "buzz2remote")
    
    # Try Atlas connection first if configured
    if atlas_uri and atlas_uri != "mongodb://localhost:27017/":
        try:
            logger.info(f"Attempting Atlas connection: {atlas_uri}")
            client = MongoClient(atlas_uri, serverSelectionTimeoutMS=5000)
            # Test connection
            client.server_info()
            logger.info("✅ Connected to MongoDB Atlas")
            return client[db_name]
        except Exception as e:
            logger.warning(f"❌ Atlas connection failed: {str(e)}")
            logger.info("🔄 Falling back to local MongoDB...")
    
    # Use local MongoDB
    try:
        logger.info(f"Connecting to local MongoDB: {local_uri}")
        client = MongoClient(local_uri, serverSelectionTimeoutMS=5000)
        # Test connection
        client.server_info()
        logger.info(f"✅ Connected to local MongoDB")
        logger.info(f"Database name: {db_name}")
        return client[db_name]
    except Exception as e:
        logger.error(f"❌ Local MongoDB connection failed: {str(e)}")
        raise Exception(f"Could not connect to any MongoDB instance: {str(e)}") 