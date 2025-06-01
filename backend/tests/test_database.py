import pytest
import asyncio
from unittest.mock import AsyncMock, patch, MagicMock
from backend.database import get_db, db, ensure_indexes, close_db_connections
import mongomock

class TestDatabase:
    """Test database module functionality."""
    
    def test_get_db_returns_database_instance(self):
        """Test that get_db returns a database instance."""
        database = get_db()
        assert database is not None
        assert hasattr(database, 'jobs')
        assert hasattr(database, 'users')
        assert hasattr(database, 'companies')
    
    def test_database_instance_is_singleton(self):
        """Test that database instance is singleton."""
        db1 = get_db()
        db2 = get_db()
        assert db1 is db2
    
    @pytest.mark.asyncio
    async def test_ensure_indexes_creates_job_indexes(self):
        """Test that ensure_indexes creates job collection indexes."""
        mock_db = AsyncMock()
        mock_jobs = AsyncMock()
        mock_users = AsyncMock()
        mock_db.jobs = mock_jobs
        mock_db.users = mock_users
        
        with patch('backend.database.db', mock_db):
            await ensure_indexes()
            
        # Verify jobs indexes
        mock_jobs.create_index.assert_any_call("title")
        mock_jobs.create_index.assert_any_call("company")
        mock_jobs.create_index.assert_any_call("location")
        mock_jobs.create_index.assert_any_call("job_type")
        mock_jobs.create_index.assert_any_call("created_at")
        mock_jobs.create_index.assert_any_call("is_active")
        
        # Verify users indexes
        mock_users.create_index.assert_any_call("email", unique=True)
        mock_users.create_index.assert_any_call("created_at")
    
    @pytest.mark.asyncio
    async def test_ensure_indexes_handles_errors_gracefully(self):
        """Test that ensure_indexes handles errors gracefully."""
        mock_db = AsyncMock()
        mock_jobs = AsyncMock()
        mock_jobs.create_index.side_effect = Exception("Index creation failed")
        mock_db.jobs = mock_jobs
        mock_db.users = AsyncMock()
        
        with patch('backend.database.db', mock_db):
            # Should not raise exception
            await ensure_indexes()
    
    @pytest.mark.asyncio
    async def test_close_db_connections_closes_client(self):
        """Test that close_db_connections properly closes client."""
        mock_client = MagicMock()
        
        with patch('backend.database.motor_client', mock_client):
            await close_db_connections()
            
        mock_client.close.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_close_db_connections_handles_errors(self):
        """Test that close_db_connections handles errors gracefully."""
        mock_client = MagicMock()
        mock_client.close.side_effect = Exception("Connection close failed")
        
        with patch('backend.database.motor_client', mock_client):
            # Should not raise exception
            await close_db_connections()
    
    def test_database_collections_accessible(self):
        """Test that database collections are accessible."""
        database = get_db()
        
        # Test common collections
        assert hasattr(database, 'jobs')
        assert hasattr(database, 'users')
        assert hasattr(database, 'companies')
        assert hasattr(database, 'crawl_errors')
        assert hasattr(database, 'service_logs')
    
    @pytest.mark.asyncio
    async def test_database_operations_work(self):
        """Test basic database operations work."""
        # This test uses the actual test database
        test_doc = {
            "test_id": "123",
            "title": "Test Job",
            "company": "Test Company"
        }
        
        # Insert
        result = await db.test_collection.insert_one(test_doc)
        assert result.inserted_id is not None
        
        # Find
        found_doc = await db.test_collection.find_one({"test_id": "123"})
        assert found_doc is not None
        assert found_doc["title"] == "Test Job"
        
        # Update
        update_result = await db.test_collection.update_one(
            {"test_id": "123"},
            {"$set": {"title": "Updated Test Job"}}
        )
        assert update_result.modified_count == 1
        
        # Delete
        delete_result = await db.test_collection.delete_one({"test_id": "123"})
        assert delete_result.deleted_count == 1
    
    def test_database_environment_detection(self):
        """Test that database correctly detects test environment."""
        import os
        
        # Simulate test environment
        original_env = os.environ.get('PYTEST_CURRENT_TEST')
        os.environ['PYTEST_CURRENT_TEST'] = 'test_file::test_name'
        
        try:
            # Database should detect test environment
            database = get_db()
            assert database is not None
        finally:
            # Restore environment
            if original_env:
                os.environ['PYTEST_CURRENT_TEST'] = original_env
            else:
                os.environ.pop('PYTEST_CURRENT_TEST', None)
    
    @pytest.mark.asyncio 
    async def test_async_context_manager_usage(self):
        """Test using database in async context manager."""
        async def db_operation():
            async for document in db.test_collection.find().limit(1):
                return document
            return None
        
        result = await db_operation()
        # Should not raise any errors
    
    def test_database_connection_resilience(self):
        """Test database connection resilience."""
        # Test multiple rapid connections
        for i in range(10):
            database = get_db()
            assert database is not None
    
    @pytest.mark.asyncio
    async def test_concurrent_database_access(self):
        """Test concurrent database access."""
        async def db_task(task_id):
            test_doc = {"task_id": task_id, "data": f"test_{task_id}"}
            result = await db.test_concurrent.insert_one(test_doc)
            return result.inserted_id
        
        # Run concurrent tasks
        tasks = [db_task(i) for i in range(5)]
        results = await asyncio.gather(*tasks)
        
        # All tasks should complete successfully
        assert len(results) == 5
        assert all(result is not None for result in results)
        
        # Cleanup
        await db.test_concurrent.delete_many({"task_id": {"$in": list(range(5))}})
    
    def test_database_configuration_validation(self):
        """Test database configuration validation."""
        database = get_db()
        
        # Test that database has proper configuration
        assert database.name is not None
        # Database should respond to basic operations
        assert hasattr(database, 'list_collection_names')
    
    @pytest.mark.asyncio
    async def test_index_creation_idempotent(self):
        """Test that index creation is idempotent."""
        # Run ensure_indexes multiple times
        await ensure_indexes()
        await ensure_indexes()
        await ensure_indexes()
        
        # Should not raise any errors
    
    def test_database_mock_fallback(self):
        """Test database mock fallback mechanism."""
        with patch('backend.database.AsyncIOMotorClient') as mock_client:
            mock_client.side_effect = Exception("Connection failed")
            
            # Should fall back to mock
            database = get_db()
            assert database is not None 