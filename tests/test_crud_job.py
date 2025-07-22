import pytest
from unittest.mock import patch, MagicMock, AsyncMock

pytestmark = pytest.mark.asyncio
from backend.crud.job import (
    create_job,
    get_job,
    get_jobs,
    update_job,
    delete_job,
    search_jobs,
    get_job_statistics
)

# Mock job data
mock_job = {
    "_id": "test_job_id",
    "title": "Python Developer",
    "company": "Test Company",
    "location": "Remote",
    "description": "Test job description",
    "salary_min": 50000,
    "salary_max": 80000,
    "skills": ["Python", "Django", "FastAPI"],
    "is_active": True,
    "created_at": "2024-01-01T00:00:00Z"
}

mock_jobs = [
    mock_job,
    {
        "_id": "test_job_id_2",
        "title": "Frontend Developer",
        "company": "Test Company 2",
        "location": "Remote",
        "description": "Test job description 2",
        "salary_min": 40000,
        "salary_max": 70000,
        "skills": ["React", "JavaScript", "TypeScript"],
        "is_active": True,
        "created_at": "2024-01-02T00:00:00Z"
    }
]

class TestCRUDJob:
    """Test CRUD operations for jobs"""
    
    async def test_create_job_success(self):
        """Test successful job creation"""
        # Mock database
        mock_db = MagicMock()
        mock_db.jobs.insert_one.return_value = MagicMock(inserted_id="new_job_id")
        
        # Test function
        result = await create_job(mock_db, mock_job)
        
        assert result == "new_job_id"
        mock_db.jobs.insert_one.assert_called_once()
    
    @patch('backend.crud.job.get_database')
    async def test_create_job_failure(self, mock_get_db):
        """Test job creation failure"""
        # Mock database to raise exception
        mock_db = MagicMock()
        mock_db.jobs.insert_one.side_effect = Exception("Database error")
        mock_get_db.return_value = mock_db
        
        # Test function should raise exception
        with pytest.raises(Exception):
            await create_job(mock_job)
    
    @patch('backend.crud.job.get_database')
    async def test_get_job_success(self, mock_get_db):
        """Test successful job retrieval"""
        # Mock database
        mock_db = MagicMock()
        mock_db.jobs.find_one.return_value = mock_job
        mock_get_db.return_value = mock_db
        
        # Test function
        result = await get_job("test_job_id")
        
        assert result == mock_job
        mock_db.jobs.find_one.assert_called_once_with({"_id": "test_job_id"})
    
    @patch('backend.crud.job.get_database')
    async def test_get_job_not_found(self, mock_get_db):
        """Test job retrieval when not found"""
        # Mock database - job not found
        mock_db = MagicMock()
        mock_db.jobs.find_one.return_value = None
        mock_get_db.return_value = mock_db
        
        # Test function
        result = await get_job("nonexistent_job_id")
        
        assert result is None
        mock_db.jobs.find_one.assert_called_once_with({"_id": "nonexistent_job_id"})
    
    @patch('backend.crud.job.get_database')
    async def test_get_jobs_success(self, mock_get_db):
        """Test successful jobs retrieval"""
        # Mock database
        mock_db = MagicMock()
        mock_db.jobs.find.return_value.to_list.return_value = mock_jobs
        mock_get_db.return_value = mock_db
        
        # Test function
        result = await get_jobs(skip=0, limit=10)
        
        assert result == mock_jobs
        mock_db.jobs.find.assert_called_once()
    
    @patch('backend.crud.job.get_database')
    async def test_get_jobs_with_filters(self, mock_get_db):
        """Test jobs retrieval with filters"""
        # Mock database
        mock_db = MagicMock()
        mock_db.jobs.find.return_value.to_list.return_value = [mock_job]
        mock_get_db.return_value = mock_db
        
        # Test function with filters
        filters = {"location": "Remote", "is_active": True}
        result = await get_jobs(skip=0, limit=10, **filters)
        
        assert result == [mock_job]
        mock_db.jobs.find.assert_called_once()
    
    @patch('backend.crud.job.get_database')
    async def test_update_job_success(self, mock_get_db):
        """Test successful job update"""
        # Mock database
        mock_db = MagicMock()
        mock_db.jobs.update_one.return_value = MagicMock(modified_count=1)
        mock_get_db.return_value = mock_db
        
        # Test function
        update_data = {"title": "Updated Python Developer"}
        result = await update_job("test_job_id", update_data)
        
        assert result is True
        mock_db.jobs.update_one.assert_called_once_with(
            {"_id": "test_job_id"}, 
            {"$set": update_data}
        )
    
    @patch('backend.crud.job.get_database')
    async def test_update_job_not_found(self, mock_get_db):
        """Test job update when not found"""
        # Mock database - no job updated
        mock_db = MagicMock()
        mock_db.jobs.update_one.return_value = MagicMock(modified_count=0)
        mock_get_db.return_value = mock_db
        
        # Test function
        update_data = {"title": "Updated Python Developer"}
        result = await update_job("nonexistent_job_id", update_data)
        
        assert result is False
        mock_db.jobs.update_one.assert_called_once_with(
            {"_id": "nonexistent_job_id"}, 
            {"$set": update_data}
        )
    
    @patch('backend.crud.job.get_database')
    async def test_delete_job_success(self, mock_get_db):
        """Test successful job deletion"""
        # Mock database
        mock_db = MagicMock()
        mock_db.jobs.delete_one.return_value = MagicMock(deleted_count=1)
        mock_get_db.return_value = mock_db
        
        # Test function
        result = await delete_job("test_job_id")
        
        assert result is True
        mock_db.jobs.delete_one.assert_called_once_with({"_id": "test_job_id"})
    
    @patch('backend.crud.job.get_database')
    async def test_delete_job_not_found(self, mock_get_db):
        """Test job deletion when not found"""
        # Mock database - no job deleted
        mock_db = MagicMock()
        mock_db.jobs.delete_one.return_value = MagicMock(deleted_count=0)
        mock_get_db.return_value = mock_db
        
        # Test function
        result = await delete_job("nonexistent_job_id")
        
        assert result is False
        mock_db.jobs.delete_one.assert_called_once_with({"_id": "nonexistent_job_id"})
    
    @patch('backend.crud.job.get_database')
    async def test_search_jobs_success(self, mock_get_db):
        """Test successful job search"""
        # Mock database
        mock_db = MagicMock()
        mock_db.jobs.find.return_value.to_list.return_value = [mock_job]
        mock_get_db.return_value = mock_db
        
        # Test function
        result = await search_jobs("Python", skip=0, limit=10)
        
        assert result == [mock_job]
        mock_db.jobs.find.assert_called_once()
    
    @patch('backend.crud.job.get_database')
    async def test_search_jobs_empty_query(self, mock_get_db):
        """Test job search with empty query"""
        # Mock database
        mock_db = MagicMock()
        mock_db.jobs.find.return_value.to_list.return_value = mock_jobs
        mock_get_db.return_value = mock_db
        
        # Test function with empty query
        result = await search_jobs("", skip=0, limit=10)
        
        assert result == mock_jobs
        mock_db.jobs.find.assert_called_once()
    
    @patch('backend.crud.job.get_database')
    async def test_get_job_statistics_success(self, mock_get_db):
        """Test successful job statistics retrieval"""
        # Mock database
        mock_db = MagicMock()
        mock_db.jobs.count_documents.return_value = 100
        mock_db.jobs.aggregate.return_value.to_list.return_value = [
            {"_id": "Remote", "count": 60},
            {"_id": "On-site", "count": 40}
        ]
        mock_get_db.return_value = mock_db
        
        # Test function
        result = await get_job_statistics()
        
        assert "total_jobs" in result
        assert "location_stats" in result
        assert result["total_jobs"] == 100
        assert len(result["location_stats"]) == 2
    
    @patch('backend.crud.job.get_database')
    async def test_get_job_statistics_empty(self, mock_get_db):
        """Test job statistics when no jobs exist"""
        # Mock database - no jobs
        mock_db = MagicMock()
        mock_db.jobs.count_documents.return_value = 0
        mock_db.jobs.aggregate.return_value.to_list.return_value = []
        mock_get_db.return_value = mock_db
        
        # Test function
        result = await get_job_statistics()
        
        assert "total_jobs" in result
        assert "location_stats" in result
        assert result["total_jobs"] == 0
        assert result["location_stats"] == []