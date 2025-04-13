import os
import logging
from typing import Optional
from pymongo import MongoClient
from pymongo.database import Database
from pymongo.errors import ConnectionFailure, ConfigurationError

logger = logging.getLogger(__name__)

# MongoDB connection cache
_db_client = None
_db_instance = None

def get_database_client() -> Database:
    """
    Returns a MongoDB database client instance.
    Uses cached instance if available, otherwise creates a new one.
    
    Returns:
        pymongo.database.Database: MongoDB database instance
    
    Raises:
        ConnectionFailure: If connection to MongoDB fails
        ConfigurationError: If MongoDB configuration is invalid
    """
    global _db_client, _db_instance
    
    if _db_instance is not None:
        return _db_instance
    
    # Get MongoDB connection string from environment variables
    mongo_uri = os.environ.get("MONGODB_URI")
    db_name = os.environ.get("MONGODB_DB_NAME", "remote_jobs")
    
    if not mongo_uri:
        logger.warning("MONGODB_URI not set in environment variables. Using default localhost connection.")
        mongo_uri = "mongodb://localhost:27017/"
    
    try:
        # Create MongoDB client
        logger.info(f"Connecting to MongoDB database: {db_name}")
        _db_client = MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)
        
        # Test connection
        _db_client.admin.command('ping')
        logger.info("MongoDB connection successful")
        
        # Get database instance
        _db_instance = _db_client[db_name]
        return _db_instance
        
    except ConnectionFailure as e:
        logger.error(f"MongoDB connection failed: {e}")
        raise
    except ConfigurationError as e:
        logger.error(f"MongoDB configuration error: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error connecting to MongoDB: {e}")
        raise

def close_database_connection() -> None:
    """
    Closes the MongoDB client connection if it exists.
    """
    global _db_client, _db_instance
    
    if _db_client is not None:
        logger.info("Closing MongoDB connection")
        _db_client.close()
        _db_client = None
        _db_instance = None 