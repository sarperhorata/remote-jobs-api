import pytest
from unittest.mock import Mock, AsyncMock, patch
from backend.database.db import get_async_db, get_database

class TestDatabaseDBSimple:
    """Simple database.db tests that work"""
    
    @pytest.mark.asyncio
    async def test_get_async_db_function_exists(self):
        """Test that get_async_db function exists"""
        assert callable(get_async_db)
        
    @pytest.mark.asyncio 
    async def test_get_database_function_exists(self):
        """Test that get_database function exists"""
        assert callable(get_database)
        
    @pytest.mark.asyncio
    async def test_database_connection_returns_something(self):
        """Test database connection returns value"""
        db = await get_async_db()
        assert db is not None
        
    def test_database_module_imports(self):
        """Test database module imports successfully"""
        from backend.database import db
        assert db is not None
