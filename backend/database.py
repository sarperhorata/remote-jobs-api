from motor.motor_asyncio import AsyncIOMotorClient
import logging
import os
# Removed SQLAlchemy import as we're using MongoDB only
import asyncio

# Import configuration
try:
    from utils.config import DATABASE_URL, IS_PRODUCTION
except ImportError:
    try:
        from utils.config import DATABASE_URL, IS_PRODUCTION
    except ImportError:
        # Fallback configuration
        DATABASE_URL = os.getenv("DATABASE_URL") or os.getenv("MONGODB_URI") or "mongodb://localhost:27017/buzz2remote"
        IS_PRODUCTION = os.getenv("ENVIRONMENT", "development").lower() == "production"

logger = logging.getLogger(__name__)

# Global client and database references
motor_client = None
db = None
DATABASE_NAME = os.getenv("MONGODB_DB_NAME", "buzz2remote")

# Removed SQLAlchemy Base as we're using MongoDB with Pydantic models

async def init_database():
    """Initialize database connection with improved error handling."""
    global motor_client, db
    
    try:
        if os.getenv("PYTEST_CURRENT_TEST"):
            # Use mongomock for tests
            try:
                import mongomock_motor
                motor_client = mongomock_motor.AsyncMongoMockClient()
                db = motor_client[DATABASE_NAME]
                logger.info("Using mongomock for testing")
                return
            except ImportError:
                logger.warning("mongomock_motor not available, using regular client for tests")
        
        # Production/Development database connection
        logger.info(f"Connecting to database: {DATABASE_URL[:20]}...")
        motor_client = AsyncIOMotorClient(
            DATABASE_URL,
            serverSelectionTimeoutMS=5000,  # 5 second timeout
            connectTimeoutMS=5000,
            maxPoolSize=10,
            minPoolSize=1
        )
        db = motor_client[DATABASE_NAME]
        
        # Test connection
        await motor_client.admin.command('ping')
        logger.info("Database connection initialized successfully")
        
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        
        # In production, try to continue with mock database
        if IS_PRODUCTION:
            logger.critical("Production database connection failed! Using mock database.")
            try:
                import mongomock_motor
                motor_client = mongomock_motor.AsyncMongoMockClient()
                db = motor_client[DATABASE_NAME]
                logger.warning("Using mongomock in production as fallback")
            except ImportError:
                raise Exception(f"Critical: Production database unavailable and no fallback: {e}")
        else:
            # In development, can continue with mock
            try:
                import mongomock_motor
                motor_client = mongomock_motor.AsyncMongoMockClient()
                db = motor_client[DATABASE_NAME]
                logger.info("Using mongomock in development")
            except ImportError:
                raise Exception(f"Database connection failed and no mock available: {e}")

# Initialize on import for backwards compatibility
if motor_client is None:
    try:
        if os.getenv("PYTEST_CURRENT_TEST"):
            # Use mongomock for tests
            try:
                import mongomock_motor
                motor_client = mongomock_motor.AsyncMongoMockClient()
                db = motor_client[DATABASE_NAME]
                logger.info("Using mongomock for testing")
            except ImportError:
                # Fallback to regular client
                motor_client = AsyncIOMotorClient(DATABASE_URL)
                db = motor_client[DATABASE_NAME]
        else:
            motor_client = AsyncIOMotorClient(DATABASE_URL)
            db = motor_client[DATABASE_NAME]
    except Exception as e:
        logger.warning(f"Database connection failed, using mock: {e}")
        try:
            import mongomock_motor
            motor_client = mongomock_motor.AsyncMongoMockClient()
            db = motor_client[DATABASE_NAME]
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