"""
Database package initialization.
"""
# Removed sqlalchemy import as it's not needed for MongoDB
from .db import (
    get_database_client,
    get_database,
    get_db,
    get_async_db,
    get_jobs_collection,
    get_companies_collection,
    get_users_collection,
    get_ads_collection,
    ensure_indexes,
    close_db_connections,
    init_database,
    get_test_collection,
    test_concurrent,
    MONGODB_URI,
    DATABASE_NAME
)

# Define a dummy Base for compatibility with legacy code
class Base:
    """Dummy base class for compatibility"""
    pass

__all__ = [
    'get_database_client',
    'get_database',
    'get_db',
    'get_async_db',
    'get_jobs_collection',
    'get_companies_collection',
    'get_users_collection',
    'get_ads_collection',
    'ensure_indexes',
    'close_db_connections',
    'init_database',
    'get_test_collection',
    'test_concurrent',
    'MONGODB_URI',
    'DATABASE_NAME',
    'Base'
]

 