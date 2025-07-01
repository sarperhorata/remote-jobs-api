import pytest
from fastapi.testclient import TestClient

from backend.main import app


class TestApplicationsAPI:
    """Simplified Applications API tests focusing on endpoint availability"""
    
    @pytest.fixture
    def client(self):
        """Test client"""
        return TestClient(app)
    
    def test_applications_endpoints_exist(self, client):
        """Test that applications endpoints are accessible (should return auth errors, not 404)"""
        
        # Test POST endpoint
        response = client.post("/api/v1/applications/apply", json={
            "job_id": "test123",
            "application_type": "external"
        })
        
        # Should return auth error (401/403), not 404 Not Found
        assert response.status_code != 404, f"Applications apply endpoint not found - got {response.status_code}"
        assert response.status_code in [401, 403, 422], f"Expected auth/validation error, got {response.status_code}"
        
        # Test GET endpoints
        get_endpoints = [
            "/api/v1/applications/my-applications",
            "/api/v1/applications/applied-jobs", 
            "/api/v1/applications/check-applied/test123",
            "/api/v1/applications/stats"
        ]
        
        for endpoint in get_endpoints:
            response = client.get(endpoint)
            assert response.status_code != 404, f"Endpoint {endpoint} not found - got 404"
            assert response.status_code in [401, 403], f"Expected auth error for {endpoint}, got {response.status_code}"
    
    def test_applications_validation(self, client):
        """Test applications endpoint validates input properly"""
        
        # Test with missing required fields
        response = client.post("/api/v1/applications/apply", json={})
        
        # Should return validation error or auth error (not 404)
        assert response.status_code != 404, "Applications endpoint not found"
        assert response.status_code in [401, 403, 422], f"Expected validation/auth error, got {response.status_code}"
    
    def test_applications_check_applied_endpoint(self, client):
        """Test check-applied endpoint with job ID parameter"""
        
        response = client.get("/api/v1/applications/check-applied/job123")
        
        # Should return auth error, not 404
        assert response.status_code != 404, "Check-applied endpoint not found"
        assert response.status_code in [401, 403], f"Expected auth error, got {response.status_code}"
    
    def test_applications_applied_jobs_endpoint(self, client):
        """Test applied-jobs endpoint"""
        
        response = client.get("/api/v1/applications/applied-jobs")
        
        # Should return auth error, not 404
        assert response.status_code != 404, "Applied-jobs endpoint not found"  
        assert response.status_code in [401, 403], f"Expected auth error, got {response.status_code}"


class TestApplicationsIntegration:
    """Integration tests for applications router"""
    
    @pytest.fixture
    def client(self):
        """Test client"""
        return TestClient(app)
    
    def test_applications_router_included(self, client):
        """Test that applications router is properly included in main app"""
        
        # Check openapi docs include applications endpoints
        response = client.get("/openapi.json")
        assert response.status_code == 200
        
        openapi_data = response.json()
        paths = openapi_data.get("paths", {})
        
        # Look for applications endpoints in OpenAPI spec
        applications_paths = [path for path in paths.keys() if "/applications/" in path]
        assert len(applications_paths) > 0, "No applications endpoints found in OpenAPI spec"
        
        # Check specific endpoints exist in OpenAPI
        expected_paths = [
            "/api/v1/applications/apply",
            "/api/v1/applications/my-applications",
            "/api/v1/applications/applied-jobs"
        ]
        
        for expected_path in expected_paths:
            found = any(expected_path in path for path in paths.keys())
            assert found, f"Expected path {expected_path} not found in OpenAPI spec" 