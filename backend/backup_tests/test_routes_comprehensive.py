import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

class TestRoutesCoverage:
    def test_root_endpoint(self):
        response = client.get("/")
        assert response.status_code == 200
        
    def test_health_endpoint(self):
        response = client.get("/health")
        assert response.status_code == 200
        
    def test_job_titles_search(self):
        response = client.get("/api/jobs/job-titles/search?q=developer")
        assert response.status_code == 200
        
    def test_skills_search(self):
        response = client.get("/api/jobs/skills/search?q=python")
        assert response.status_code == 200
