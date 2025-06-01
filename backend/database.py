from motor.motor_asyncio import AsyncIOMotorClient
from backend.config import settings
import logging
import os
from sqlalchemy.ext.declarative import declarative_base
import asyncio

logger = logging.getLogger(__name__)

# Global client and database references
motor_client = None
db = None
DATABASE_NAME = settings.MONGODB_DB_NAME

# Add Base for SQLAlchemy models
Base = declarative_base()

async def init_database():
    """Initialize database connection."""
    global motor_client, db
    
    try:
        if os.getenv("PYTEST_CURRENT_TEST") or settings.ENVIRONMENT == "test":
            # Use mongomock for tests
            try:
                import mongomock_motor
                motor_client = mongomock_motor.AsyncMongoMockClient()
                db = motor_client[settings.MONGODB_DB_NAME]
                logger.info("Using mongomock for testing")
            except ImportError:
                # Fallback to regular client
                motor_client = AsyncIOMotorClient(settings.MONGODB_URL)
                db = motor_client[settings.MONGODB_DB_NAME]
        else:
            motor_client = AsyncIOMotorClient(settings.MONGODB_URL)
            db = motor_client[settings.MONGODB_DB_NAME]
            
        logger.info("Database connection initialized")
        
    except Exception as e:
        logger.warning(f"Database connection failed, using mock: {e}")
        try:
            import mongomock_motor
            motor_client = mongomock_motor.AsyncMongoMockClient()
            db = motor_client[settings.MONGODB_DB_NAME]
        except ImportError:
            raise Exception("Could not connect to database and mongomock not available")

# Initialize on import for backwards compatibility
if motor_client is None:
    try:
        if os.getenv("PYTEST_CURRENT_TEST") or settings.ENVIRONMENT == "test":
            # Use mongomock for tests
            try:
                import mongomock_motor
                motor_client = mongomock_motor.AsyncMongoMockClient()
                db = motor_client[settings.MONGODB_DB_NAME]
                logger.info("Using mongomock for testing")
            except ImportError:
                # Fallback to regular client
                motor_client = AsyncIOMotorClient(settings.MONGODB_URL)
                db = motor_client[settings.MONGODB_DB_NAME]
        else:
            motor_client = AsyncIOMotorClient(settings.MONGODB_URL)
            db = motor_client[settings.MONGODB_DB_NAME]
    except Exception as e:
        logger.warning(f"Database connection failed, using mock: {e}")
        try:
            import mongomock_motor
            motor_client = mongomock_motor.AsyncMongoMockClient()
            db = motor_client[settings.MONGODB_DB_NAME]
        except ImportError:
            raise Exception("Could not connect to database and mongomock not available")

def get_db():
    """Get MongoDB database instance (sync version for admin panel)."""
    return db

async def get_async_db():
    """Get MongoDB database instance for dependency injection."""
    try:
        return db
    except Exception as e:
        logger.error(f"Database error in get_async_db: {e}")
        return None

async def get_async_db_dependency():
    """FastAPI dependency function that yields database."""
    try:
        yield db
    except Exception as e:
        logger.error(f"Database error in get_async_db_dependency: {e}")
        yield None

def get_db_sync():
    """Get MongoDB database instance synchronously (for admin panel)."""
    return db

async def close_db_connections():
    """Close database connections (async version)."""
    global motor_client
    try:
        if motor_client:
            motor_client.close()
            motor_client = None
            logger.info("Database connections closed")
    except Exception as e:
        logger.error(f"Error closing database connections: {e}")

def close_db_connections_sync():
    """Close database connections (sync version for backward compatibility)."""
    global motor_client
    try:
        if motor_client:
            motor_client.close()
            motor_client = None
            logger.info("Database connections closed")
    except Exception as e:
        logger.error(f"Error closing database connections: {e}")

async def ensure_indexes():
    """Create database indexes."""
    try:
        if not db:
            logger.warning("Database not available for index creation")
            return
            
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