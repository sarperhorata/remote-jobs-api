import pytest
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

class TestApplicationsAPI:
    """Test suite for applications API - simple but effective"""
    
    def test_applications_endpoints_exist(self):
        """Test that applications endpoints exist"""
        # Test apply endpoint (should require auth)
        response = client.post("/api/v1/applications/apply", json={"job_id": "test"})
        assert response.status_code in [401, 403, 422], "Apply endpoint should exist and require auth"
        
        # Test my-applications endpoint (should require auth)
        response = client.get("/api/v1/applications/my-applications")
        assert response.status_code in [401, 403], "My applications endpoint should exist and require auth"
        
    def test_applications_validation(self):
        """Test request validation"""
        # Test apply with invalid data
        response = client.post("/api/v1/applications/apply", json={})
        assert response.status_code in [401, 403, 422], "Should validate application data"
        
    def test_applications_check_applied_endpoint(self):
        """Test check applied endpoint"""
        response = client.get("/api/v1/applications/check-applied/test_job_id")
        assert response.status_code in [401, 403], "Check applied endpoint should require auth"
        
    def test_applications_applied_jobs_endpoint(self):
        """Test applied jobs endpoint"""
        response = client.get("/api/v1/applications/applied-jobs")
        assert response.status_code in [401, 403], "Applied jobs endpoint should require auth"

class TestApplicationsIntegration:
    """Basic integration tests for applications"""
    
    def test_applications_router_included(self):
        """Test that applications router is properly included"""
        response = client.get("/api/v1/applications/my-applications")
        assert response.status_code != 404, "Applications router should be included with correct prefix"
