import pytest
from unittest.mock import MagicMock, AsyncMock
from backend.crud.job import (
    create_job,
    get_job,
    get_jobs,
    update_job,
    delete_job,
    search_jobs,
    get_job_statistics
)
from backend.schemas.job import JobCreate

pytestmark = pytest.mark.asyncio

# Mock job data
mock_job = {
    "title": "Python Developer",
    "company": "Test Company",
    "location": "Remote",
    "description": "Test job description",
    "salary_min": 50000,
    "salary_max": 80000,
    "skills": ["Python", "Django", "FastAPI"]
}

class TestCRUDJobSimple:
    """Simple tests for CRUD operations for jobs"""
    
    async def test_create_job_success(self):
        """Test successful job creation"""
        # Mock database
        mock_db = MagicMock()
        mock_db.jobs.insert_one.return_value = MagicMock(inserted_id="new_job_id")
        
        # Create JobCreate object
        job_create = JobCreate(**mock_job)
        
        # Test function
        result = await create_job(mock_db, job_create)
        
        assert result == "new_job_id"
        mock_db.jobs.insert_one.assert_called_once()
    
    async def test_get_job_success(self):
        """Test successful job retrieval"""
        # Mock database
        mock_db = MagicMock()
        mock_db.jobs.find_one.return_value = {
            "_id": "test_job_id",
            **mock_job,
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-01T00:00:00Z",
            "is_active": True,
            "views_count": 0,
            "applications_count": 0
        }
        
        # Test function
        result = await get_job(mock_db, "test_job_id")
        
        assert result is not None
        assert result.title == "Python Developer"
        mock_db.jobs.find_one.assert_called_once()
    
    async def test_get_jobs_success(self):
        """Test successful jobs retrieval"""
        # Mock database
        mock_db = MagicMock()
        mock_cursor = AsyncMock()
        mock_cursor.to_list.return_value = [
            {
                "_id": "test_job_id",
                **mock_job,
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-01T00:00:00Z",
                "is_active": True,
                "views_count": 0,
                "applications_count": 0
            }
        ]
        mock_db.jobs.find.return_value = mock_cursor
        
        # Test function
        result = await get_jobs(mock_db, skip=0, limit=10)
        
        assert len(result) == 1
        assert result[0].title == "Python Developer"
        mock_db.jobs.find.assert_called_once()
    
    async def test_delete_job_success(self):
        """Test successful job deletion"""
        # Mock database
        mock_db = MagicMock()
        mock_db.jobs.delete_one.return_value = MagicMock(deleted_count=1)
        
        # Test function
        result = await delete_job(mock_db, "test_job_id")
        
        assert result is True
        mock_db.jobs.delete_one.assert_called_once()
    
    async def test_search_jobs_success(self):
        """Test successful job search"""
        # Mock database
        mock_db = MagicMock()
        mock_cursor = AsyncMock()
        mock_cursor.to_list.return_value = [
            {
                "_id": "test_job_id",
                **mock_job,
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-01T00:00:00Z",
                "is_active": True,
                "views_count": 0,
                "applications_count": 0
            }
        ]
        mock_db.jobs.find.return_value = mock_cursor
        
        # Test function
        result = await search_jobs(mock_db, "Python", skip=0, limit=10)
        
        assert len(result) == 1
        assert result[0].title == "Python Developer"
        mock_db.jobs.find.assert_called_once()
    
    async def test_get_job_statistics_success(self):
        """Test successful job statistics retrieval"""
        # Mock database
        mock_db = MagicMock()
        mock_db.jobs.count_documents = AsyncMock(return_value=100)
        mock_aggregate_cursor = AsyncMock()
        mock_aggregate_cursor.to_list.return_value = [
            {"_id": "Remote", "count": 60},
            {"_id": "On-site", "count": 40}
        ]
        mock_db.jobs.aggregate.return_value = mock_aggregate_cursor
        
        # Test function
        result = await get_job_statistics(mock_db)
        
        assert "total_jobs" in result
        assert "location_stats" in result
        assert result["total_jobs"] == 100
        assert len(result["location_stats"]) == 2