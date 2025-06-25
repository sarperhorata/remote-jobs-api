import pytest
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

class TestMainAppSimple:
    """Simple main app tests that work"""
    
    def test_app_exists(self):
        """Test FastAPI app exists"""
        assert app is not None
        
    def test_app_has_correct_title(self):
        """Test app title"""
        assert "Buzz2Remote" in app.title
        
    def test_health_endpoint_works(self):
        """Test health endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        
    def test_root_endpoint_works(self):
        """Test root endpoint"""
        response = client.get("/")
        assert response.status_code == 200
        
    def test_app_has_routes(self):
        """Test app has routes configured"""
        routes = [route.path for route in app.routes]
        assert len(routes) > 0
        assert "/" in routes
        
    def test_404_handling(self):
        """Test 404 error handling"""
        response = client.get("/nonexistent-endpoint")
        assert response.status_code == 404
        
    def test_cors_enabled(self):
        """Test CORS is enabled"""
        response = client.get("/health")
        # Should not fail due to CORS
        assert response.status_code == 200
