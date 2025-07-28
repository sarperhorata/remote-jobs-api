"""
Test Authentication Middleware
"""

import pytest
from fastapi import FastAPI, Request
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch

from backend.middleware.auth_middleware import AuthMiddleware, get_current_user
from backend.tests.utils.auth_helper import test_auth_helper


@pytest.fixture
def app():
    """Create test FastAPI app"""
    app = FastAPI()
    
    @app.get("/public")
    async def public_endpoint():
        return {"message": "public"}
    
    @app.get("/protected")
    async def protected_endpoint(request: Request):
        user = get_current_user(request)
        return {"message": "protected", "user": user}
    
    @app.get("/admin")
    async def admin_endpoint(request: Request):
        user = get_current_user(request)
        if user.get("role") != "admin":
            raise Exception("Admin required")
        return {"message": "admin", "user": user}
    
    return app


@pytest.fixture
def auth_middleware():
    """Create auth middleware instance"""
    return AuthMiddleware(secret_key="test-secret-key")


@pytest.fixture
def client(app, auth_middleware):
    """Create test client with auth middleware"""
    app.add_middleware(auth_middleware.__class__, secret_key="test-secret-key")
    return TestClient(app)


class TestAuthMiddleware:
    """Test authentication middleware"""
    
    def test_public_endpoint_no_auth_required(self, client):
        """Test public endpoint doesn't require authentication"""
        response = client.get("/public")
        assert response.status_code == 200
        assert response.json()["message"] == "public"
    
    def test_protected_endpoint_no_token(self, client):
        """Test protected endpoint without token returns 401"""
        response = client.get("/protected")
        assert response.status_code == 401
        assert response.json()["error"] == "Unauthorized"
    
    def test_protected_endpoint_valid_token(self, client):
        """Test protected endpoint with valid token"""
        token = test_auth_helper.create_user_token()
        headers = test_auth_helper.get_auth_headers(token)
        
        response = client.get("/protected", headers=headers)
        assert response.status_code == 200
        assert response.json()["message"] == "protected"
    
    def test_protected_endpoint_expired_token(self, client):
        """Test protected endpoint with expired token"""
        token = test_auth_helper.create_expired_token()
        headers = test_auth_helper.get_auth_headers(token)
        
        response = client.get("/protected", headers=headers)
        assert response.status_code == 401
        assert response.json()["error"] == "Unauthorized"
    
    def test_protected_endpoint_invalid_token(self, client):
        """Test protected endpoint with invalid token"""
        token = test_auth_helper.create_invalid_token()
        headers = test_auth_helper.get_auth_headers(token)
        
        response = client.get("/protected", headers=headers)
        assert response.status_code == 401
        assert response.json()["error"] == "Unauthorized"
    
    def test_admin_endpoint_user_token(self, client):
        """Test admin endpoint with user token"""
        token = test_auth_helper.create_user_token()
        headers = test_auth_helper.get_auth_headers(token)
        
        response = client.get("/admin", headers=headers)
        assert response.status_code == 500  # Exception raised
    
    def test_admin_endpoint_admin_token(self, client):
        """Test admin endpoint with admin token"""
        token = test_auth_helper.create_admin_token()
        headers = test_auth_helper.get_auth_headers(token)
        
        response = client.get("/admin", headers=headers)
        assert response.status_code == 200
        assert response.json()["message"] == "admin"


class TestAuthHelper:
    """Test authentication helper functions"""
    
    def test_create_test_token(self):
        """Test creating test token"""
        token = test_auth_helper.create_test_token(
            user_id="test123",
            email="test@example.com",
            role="user"
        )
        
        payload = test_auth_helper.decode_token(token)
        assert payload["sub"] == "test123"
        assert payload["email"] == "test@example.com"
        assert payload["role"] == "user"
    
    def test_create_admin_token(self):
        """Test creating admin token"""
        token = test_auth_helper.create_admin_token("admin123")
        
        payload = test_auth_helper.decode_token(token)
        assert payload["sub"] == "admin123"
        assert payload["role"] == "admin"
        assert "admin" in payload["permissions"]
    
    def test_create_user_token(self):
        """Test creating user token"""
        token = test_auth_helper.create_user_token("user123")
        
        payload = test_auth_helper.decode_token(token)
        assert payload["sub"] == "user123"
        assert payload["role"] == "user"
        assert "read" in payload["permissions"]
    
    def test_create_expired_token(self):
        """Test creating expired token"""
        token = test_auth_helper.create_expired_token("expired123")
        
        assert test_auth_helper.is_token_expired(token)
    
    def test_token_not_expired(self):
        """Test valid token is not expired"""
        token = test_auth_helper.create_user_token("valid123")
        
        assert not test_auth_helper.is_token_expired(token)
    
    def test_get_auth_headers(self):
        """Test getting auth headers"""
        token = "test.token.here"
        headers = test_auth_helper.get_auth_headers(token)
        
        assert headers["Authorization"] == "Bearer test.token.here"
    
    def test_get_admin_headers(self):
        """Test getting admin headers"""
        headers = test_auth_helper.get_admin_headers()
        
        assert "Authorization" in headers
        assert headers["Authorization"].startswith("Bearer ")
        
        token = headers["Authorization"][7:]  # Remove "Bearer " prefix
        payload = test_auth_helper.decode_token(token)
        assert payload["role"] == "admin"
    
    def test_get_user_headers(self):
        """Test getting user headers"""
        headers = test_auth_helper.get_user_headers()
        
        assert "Authorization" in headers
        assert headers["Authorization"].startswith("Bearer ")
        
        token = headers["Authorization"][7:]  # Remove "Bearer " prefix
        payload = test_auth_helper.decode_token(token)
        assert payload["role"] == "user"


class TestAuthMiddlewareMethods:
    """Test auth middleware methods"""
    
    def test_is_public_endpoint(self, auth_middleware):
        """Test public endpoint detection"""
        assert auth_middleware._is_public_endpoint("/api/v1/health")
        assert auth_middleware._is_public_endpoint("/api/v1/jobs")
        assert auth_middleware._is_public_endpoint("/api/v1/ads")
        assert not auth_middleware._is_public_endpoint("/api/v1/users")
    
    def test_extract_token(self, auth_middleware):
        """Test token extraction"""
        # Mock request
        request = Mock()
        
        # Test with Bearer token
        request.headers = {"Authorization": "Bearer test.token.here"}
        token = auth_middleware._extract_token(request)
        assert token == "test.token.here"
        
        # Test without Authorization header
        request.headers = {}
        token = auth_middleware._extract_token(request)
        assert token is None
        
        # Test with invalid format
        request.headers = {"Authorization": "Invalid test.token.here"}
        token = auth_middleware._extract_token(request)
        assert token is None
    
    def test_validate_token(self, auth_middleware):
        """Test token validation"""
        # Test valid token
        token = test_auth_helper.create_user_token("test123")
        user_data = auth_middleware._validate_token(token)
        
        assert user_data is not None
        assert user_data["user_id"] == "test123"
        assert user_data["role"] == "user"
        
        # Test expired token
        expired_token = test_auth_helper.create_expired_token()
        with pytest.raises(Exception):
            auth_middleware._validate_token(expired_token)
        
        # Test invalid token
        invalid_token = "invalid.token.here"
        with pytest.raises(Exception):
            auth_middleware._validate_token(invalid_token)
    
    def test_create_token(self, auth_middleware):
        """Test token creation"""
        user_data = {
            "_id": "test123",
            "email": "test@example.com",
            "role": "user",
            "permissions": ["read", "write"]
        }
        
        token = auth_middleware.create_token(user_data)
        
        # Verify token
        payload = test_auth_helper.decode_token(token)
        assert payload["sub"] == "test123"
        assert payload["email"] == "test@example.com"
        assert payload["role"] == "user"
    
    def test_verify_permissions(self, auth_middleware):
        """Test permission verification"""
        user_data = {
            "role": "user",
            "permissions": ["read", "write"]
        }
        
        # Test user with required permissions
        assert auth_middleware.verify_permissions(user_data, ["read"])
        assert auth_middleware.verify_permissions(user_data, ["read", "write"])
        
        # Test user without required permissions
        assert not auth_middleware.verify_permissions(user_data, ["delete"])
        
        # Test admin role (has all permissions)
        admin_data = {
            "role": "admin",
            "permissions": []
        }
        assert auth_middleware.verify_permissions(admin_data, ["any_permission"])
        
        # Test no user data
        assert not auth_middleware.verify_permissions(None, ["read"]) 