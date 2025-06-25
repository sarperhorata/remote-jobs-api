import pytest
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

class TestJobsRoutesSimple:
    """Simple jobs routes tests that work"""
    
    def test_jobs_endpoint_accessible(self):
        """Test jobs endpoint is accessible"""
        response = client.get("/api/jobs/")
        assert response.status_code == 200
        
    def test_jobs_search_endpoint(self):
        """Test jobs search endpoint"""
        response = client.get("/api/jobs/search?q=developer")
        assert response.status_code == 200
        
    def test_job_titles_search_works(self):
        """Test job titles search"""
        response = client.get("/api/jobs/job-titles/search?q=dev")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        
    def test_skills_search_works(self):
        """Test skills search"""
        response = client.get("/api/jobs/skills/search?q=python")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        
    def test_job_statistics_endpoint(self):
        """Test job statistics endpoint"""
        response = client.get("/api/jobs/statistics")
        assert response.status_code == 200
        
    def test_jobs_response_structure(self):
        """Test jobs response has correct structure"""
        response = client.get("/api/jobs/")
        assert response.status_code == 200
        data = response.json()
        assert "jobs" in data
        assert "total" in data
        
    def test_search_without_query(self):
        """Test search without query parameter"""
        response = client.get("/api/jobs/search")
        # Should handle gracefully
        assert response.status_code in [400, 422]
