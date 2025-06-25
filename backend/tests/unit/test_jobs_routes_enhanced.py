import pytest
from unittest.mock import Mock, AsyncMock, patch
from fastapi.testclient import TestClient
from backend.main import app
from backend.routes.jobs import router

client = TestClient(app)

class TestJobsRoutes:
    """Test jobs routes comprehensively"""
    
    @patch("backend.routes.jobs.get_async_db")
    def test_get_jobs_endpoint(self, mock_db):
        """Test GET /api/jobs/ endpoint"""
        mock_db_instance = AsyncMock()
        mock_db_instance.jobs.count_documents = AsyncMock(return_value=5)
        mock_db_instance.jobs.find.return_value.sort.return_value.skip.return_value.limit.return_value.to_list = AsyncMock(return_value=[])
        mock_db.return_value = mock_db_instance
        
        response = client.get("/api/jobs/")
        assert response.status_code == 200
        data = response.json()
        assert "jobs" in data
        assert "total" in data
        
    @patch("backend.routes.jobs.get_async_db")  
    def test_search_jobs_endpoint(self, mock_db):
        """Test GET /api/jobs/search endpoint"""
        mock_db_instance = AsyncMock()
        mock_db_instance.jobs.find.return_value.skip.return_value.limit.return_value.to_list = AsyncMock(return_value=[])
        mock_db.return_value = mock_db_instance
        
        response = client.get("/api/jobs/search?q=developer")
        assert response.status_code == 200
        
    @patch("backend.routes.jobs.get_async_db")
    def test_get_job_by_id(self, mock_db):
        """Test GET /api/jobs/{job_id} endpoint"""
        mock_db_instance = AsyncMock()
        mock_job = {"_id": "123", "title": "Developer", "company": "Tech Corp"}
        mock_db_instance.jobs.find_one = AsyncMock(return_value=mock_job)
        mock_db.return_value = mock_db_instance
        
        response = client.get("/api/jobs/123")
        assert response.status_code == 200
        
    @patch("backend.routes.jobs.get_async_db")
    def test_job_statistics(self, mock_db):
        """Test GET /api/jobs/statistics endpoint"""
        mock_db_instance = AsyncMock()
        mock_db_instance.jobs.count_documents = AsyncMock(return_value=100)
        mock_db_instance.jobs.aggregate.return_value.to_list = AsyncMock(return_value=[])
        mock_db.return_value = mock_db_instance
        
        response = client.get("/api/jobs/statistics")
        assert response.status_code == 200
        
    def test_job_titles_search(self):
        """Test job titles search endpoint"""
        response = client.get("/api/jobs/job-titles/search?q=dev")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        
    def test_skills_search(self):
        """Test skills search endpoint"""
        response = client.get("/api/jobs/skills/search?q=python")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        
    def test_invalid_job_id(self):
        """Test invalid job ID handling"""
        response = client.get("/api/jobs/invalid_id_format")
        assert response.status_code in [400, 404, 422]
