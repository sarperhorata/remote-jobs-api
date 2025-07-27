import logging
import os
from contextlib import asynccontextmanager
from datetime import datetime
from typing import AsyncGenerator, Optional

from fastapi import Depends
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

# Database configuration
MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
DATABASE_NAME = os.getenv("DATABASE_NAME", "buzz2remote")

# Initialize logger
logger = logging.getLogger(__name__)

# Global client instance
_client: Optional[AsyncIOMotorClient] = None


async def get_database_client() -> AsyncIOMotorClient:
    """Get MongoDB client instance."""
    global _client

    if _client is None:
        try:
            if os.getenv("PYTEST_CURRENT_TEST"):
                # Use mongomock for testing
                try:
                    import mongomock_motor

                    _client = mongomock_motor.AsyncMongoMockClient()
                    logger.info("Using mongomock for testing")
                except ImportError:
                    _client = AsyncIOMotorClient(MONGODB_URI)
                    logger.info("Using real MongoDB client for testing")
            else:
                _client = AsyncIOMotorClient(MONGODB_URI)
                logger.info("Using real MongoDB client")
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise

    return _client


@asynccontextmanager
async def get_database_context() -> AsyncGenerator[AsyncIOMotorDatabase, None]:
    """Get database instance as async context manager."""
    client = await get_database_client()
    db = client[DATABASE_NAME]
    try:
        yield db
    finally:
        pass  # Connection will be closed by the client


async def get_async_db() -> AsyncIOMotorDatabase:
    """Get database instance for FastAPI dependency injection."""
    client = await get_database_client()
    return client[DATABASE_NAME]


async def get_database() -> AsyncIOMotorDatabase:
    """Get database instance."""
    client = await get_database_client()
    return client[DATABASE_NAME]


async def get_jobs_collection():
    """Get jobs collection."""
    db = await get_database()
    return db.jobs


async def get_companies_collection():
    """Get companies collection."""
    db = await get_database()
    return db.companies


async def get_users_collection():
    """Get users collection."""
    db = await get_database()
    return db.users


async def get_ads_collection():
    """Get ads collection."""
    db = await get_database()
    return db.ads


async def get_notifications_collection():
    """Get notifications collection."""
    db = await get_database()
    return db.notifications


async def get_notification_settings_collection():
    """Get notification settings collection."""
    db = await get_database()
    return db.notification_settings


async def ensure_indexes():
    """Ensure all required indexes exist."""
    try:
        db = await get_database()

        # Helper function to create index safely
        async def safe_create_index(collection, index_spec, **kwargs):
            try:
                await collection.create_index(index_spec, **kwargs)
                logger.debug(f"Created index on {collection.name}: {index_spec}")
            except Exception as e:
                if "already exists" in str(e) or "IndexKeySpecsConflict" in str(e):
                    logger.debug(
                        f"Index already exists on {collection.name}: {index_spec}"
                    )
                else:
                    logger.warning(f"Failed to create index on {collection.name}: {e}")

        # Jobs collection indexes
        await safe_create_index(db.jobs, "title")
        await safe_create_index(db.jobs, "company")
        await safe_create_index(db.jobs, "location")
        await safe_create_index(db.jobs, "created_at")

        # Companies collection indexes
        await safe_create_index(db.companies, "name")
        await safe_create_index(db.companies, "created_at")

        # Users collection indexes
        await safe_create_index(db.users, "email", unique=True)
        await safe_create_index(db.users, "username", unique=True)

        # Ads collection indexes
        await safe_create_index(db.ads, "title")
        await safe_create_index(db.ads, "company")
        await safe_create_index(db.ads, "created_at")

        # Notifications collection indexes
        await safe_create_index(db.notifications, "user_id")
        await safe_create_index(db.notifications, "created_at")

        logger.info("Database indexes ensured successfully")
    except Exception as e:
        logger.error(f"Error ensuring indexes: {e}")
        # Don't raise the error, just log it to prevent startup failure
        pass


async def close_db_connections():
    """Close database connections."""
    global _client
    if _client:
        _client.close()
        _client = None
        logger.info("Database connections closed")


async def init_database():
    """Initialize database with required collections and indexes."""
    try:
        await ensure_indexes()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        raise


# Test collection for concurrent operations
async def get_test_collection():
    """Get test collection for concurrent operations."""
    db = await get_database()
    return db.test_collection


async def test_concurrent():
    """Test concurrent database operations."""
    collection = await get_test_collection()
    doc = await collection.find_one({"test": "concurrent"})
    return doc


async def get_db():
    """Get database instance."""
    return await get_database()
