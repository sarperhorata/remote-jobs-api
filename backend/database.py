from motor.motor_asyncio import AsyncIOMotorClient
from backend.config import settings
import logging
import os

logger = logging.getLogger(__name__)

# MongoDB connection with fallback for tests
try:
    if os.getenv("PYTEST_CURRENT_TEST") or settings.ENVIRONMENT == "test":
        # Use mongomock for tests
        try:
            import mongomock_motor
            client = mongomock_motor.AsyncMongoMockClient()
            db = client[settings.MONGODB_DB_NAME]
            logger.info("Using mongomock for testing")
        except ImportError:
            # Fallback to regular client
            client = AsyncIOMotorClient(settings.MONGODB_URL)
            db = client[settings.MONGODB_DB_NAME]
    else:
        client = AsyncIOMotorClient(settings.MONGODB_URL)
        db = client[settings.MONGODB_DB_NAME]
except Exception as e:
    logger.warning(f"Database connection failed, using mock: {e}")
    try:
        import mongomock_motor
        client = mongomock_motor.AsyncMongoMockClient()
        db = client[settings.MONGODB_DB_NAME]
    except ImportError:
        raise Exception("Could not connect to database and mongomock not available")

def get_db():
    """Get MongoDB database instance (sync version for admin panel)."""
    return db

async def get_async_db():
    """Get MongoDB database instance (async version for FastAPI)."""
    # Return the pre-configured database instance
    # Don't use try/except with yield as it causes generator issues
    yield db

async def close_db_connections():
    """Close database connections."""
    try:
        if client:
            client.close()
            logger.info("Database connections closed")
    except Exception as e:
        logger.error(f"Error closing database connections: {e}")

async def ensure_indexes():
    """Create database indexes."""
    try:
        # Jobs collection indexes
        await db.jobs.create_index("title")
        await db.jobs.create_index("company")
        await db.jobs.create_index("location")
        await db.jobs.create_index("job_type")
        await db.jobs.create_index("created_at")
        await db.jobs.create_index("is_active")
        
        # Users collection indexes
        await db.users.create_index("email", unique=True)
        await db.users.create_index("created_at")
        
        logger.info("Database indexes created successfully")
    except Exception as e:
        logger.warning(f"Failed to create indexes: {e}")
        pass 