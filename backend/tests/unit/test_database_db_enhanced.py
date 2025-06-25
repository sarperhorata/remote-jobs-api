import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from motor.motor_asyncio import AsyncIOMotorDatabase
from backend.database.db import get_async_db, get_database, ensure_indexes, close_db_connections

class TestDatabaseDB:
    """Test database.db module comprehensively"""
    
    @pytest.mark.asyncio
    async def test_get_async_db_returns_database(self):
        """Test that get_async_db returns database instance"""
        db = await get_async_db()
        assert db is not None
        
    @pytest.mark.asyncio 
    async def test_get_database_function(self):
        """Test get_database function"""
        db = await get_database()
        assert db is not None
        
    @pytest.mark.asyncio
    async def test_ensure_indexes_success(self):
        """Test successful index creation"""
        with patch("backend.database.db.async_db") as mock_db:
            mock_db.jobs.create_index = AsyncMock()
            mock_db.users.create_index = AsyncMock() 
            await ensure_indexes()
            
    @pytest.mark.asyncio
    async def test_ensure_indexes_error_handling(self):
        """Test index creation error handling"""
        with patch("backend.database.db.async_db") as mock_db:
            mock_db.jobs.create_index = AsyncMock(side_effect=Exception("Index error"))
            # Should not raise exception
            await ensure_indexes()
            
    @pytest.mark.asyncio
    async def test_close_db_connections(self):
        """Test database connection closing"""
        with patch("backend.database.db.async_client") as mock_client:
            mock_client.close = Mock()
            await close_db_connections()
            mock_client.close.assert_called_once()
            
    def test_database_configuration(self):
        """Test database configuration"""
        from backend.database.db import DATABASE_URL
        assert DATABASE_URL is not None
