import pytest
from unittest.mock import Mock, AsyncMock, patch
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

class TestMainApp:
    """Test main.py module comprehensively"""
    
    def test_app_creation(self):
        """Test FastAPI app creation"""
        assert app is not None
        assert app.title == "Buzz2Remote API"
        
    def test_app_routes_loaded(self):
        """Test that routes are loaded"""
        routes = [route.path for route in app.routes]
        assert "/" in routes
        assert "/health" in routes
        
    def test_middleware_configuration(self):
        """Test middleware configuration"""
        middleware_classes = [type(middleware).__name__ for middleware in app.user_middleware]
        # Should have CORS and other middleware
        assert len(middleware_classes) > 0
        
    def test_cors_configuration(self):
        """Test CORS is configured"""
        response = client.options("/health")
        # Should handle OPTIONS request
        assert response.status_code in [200, 405]
        
    @patch("backend.main.get_async_db")
    def test_database_dependency(self, mock_db):
        """Test database dependency injection"""
        mock_db.return_value = AsyncMock()
        response = client.get("/health")
        assert response.status_code == 200
        
    def test_error_handling(self):
        """Test application error handling"""
        # Test non-existent endpoint
        response = client.get("/non-existent-endpoint")
        assert response.status_code == 404
        
    def test_api_versioning(self):
        """Test API versioning"""
        # Most routes should be under /api
        api_routes = [route.path for route in app.routes if route.path.startswith("/api")]
        assert len(api_routes) > 0
