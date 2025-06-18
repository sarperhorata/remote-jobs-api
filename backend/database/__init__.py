"""
Database package initialization.
"""
from sqlalchemy.orm import declarative_base
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

Base = declarative_base()

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

 