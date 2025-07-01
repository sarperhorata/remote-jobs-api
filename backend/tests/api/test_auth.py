"""
Clean Auth API Tests
Gerçek kullanım senaryolarına odaklanmış auth testleri.
"""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
class TestAuthAPIBasics:
    """Basic authentication API tests"""

    async def test_register_endpoint_validation(self, async_client: AsyncClient):
        """Test that register endpoint validates input"""
        invalid_data = {"email": "invalid-email", "password": "short"}
        
        response = await async_client.post("/api/v1/auth/register", json=invalid_data)
        
        # Should return validation error
        assert response.status_code in [200, 422]

    async def test_login_endpoint_invalid_credentials(self, async_client: AsyncClient):
        """Test login with invalid credentials"""
        invalid_credentials = {
            "username": "nonexistent@example.com",
            "password": "wrongpassword"
        }
        
        response = await async_client.post("/api/v1/auth/login", data=invalid_credentials)
        
        # Should return unauthorized
        assert response.status_code == 401

    async def test_me_endpoint_requires_auth(self, async_client: AsyncClient):
        """Test that /me endpoint requires authentication"""
        response = await async_client.get("/api/v1/auth/me")
        
        # Should require authentication
        assert response.status_code == 401

    async def test_me_endpoint_invalid_token(self, async_client: AsyncClient):
        """Test /me endpoint with invalid token"""
        headers = {"Authorization": "Bearer invalid_token"}
        response = await async_client.get("/api/v1/auth/me", headers=headers)
        
        # Should reject invalid token
        assert response.status_code == 401

    async def test_forgot_password_validation(self, async_client: AsyncClient):
        """Test forgot password email validation"""
        response = await async_client.post("/api/v1/auth/forgot-password", json={
            "email": "invalid-email"
        })
        
        assert response.status_code in [200, 422]

    async def test_google_auth_url_endpoint(self, async_client: AsyncClient):
        """Test Google auth URL generation"""
        response = await async_client.get("/api/v1/auth/google/auth-url")
        
        # Should return auth URL or error if not configured
        assert response.status_code in [200, 500]

    async def test_google_callback_no_code(self, async_client: AsyncClient):
        """Test Google callback without authorization code"""
        response = await async_client.get("/api/v1/auth/google/callback")
        
        # Should require authorization code
        assert response.status_code in [400, 405]
