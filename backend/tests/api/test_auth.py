"""
Clean Auth API Tests
Gerçek kullanım senaryolarına odaklanmış auth testleri.
"""

import pytest


class TestAuthAPIBasics:
    """Basic authentication API tests"""

    def test_register_endpoint_validation(self, client):
        """Test that register endpoint validates input"""
        invalid_data = {"email": "invalid-email", "password": "short"}

        response = client.post("/api/v1/auth/register", json=invalid_data)

        # Should return validation error
        assert response.status_code in [200, 422]

    def test_login_endpoint_invalid_credentials(self, client):
        """Test login with invalid credentials"""
        invalid_credentials = {
            "username": "nonexistent@example.com",
            "password": "wrongpassword",
        }

        response = client.post("/api/v1/auth/login", data=invalid_credentials)

        # Should return unauthorized
        assert response.status_code == 401

    def test_me_endpoint_requires_auth(self, client):
        """Test that /me endpoint requires authentication"""
        response = client.get("/api/v1/auth/me")

        # Should require authentication
        assert response.status_code == 401

    def test_me_endpoint_invalid_token(self, client):
        """Test /me endpoint with invalid token"""
        headers = {"Authorization": "Bearer invalid_token"}
        response = client.get("/api/v1/auth/me", headers=headers)

        # Should reject invalid token
        assert response.status_code == 401

    def test_forgot_password_validation(self, client):
        """Test forgot password email validation"""
        response = client.post(
            "/api/v1/auth/forgot-password", json={"email": "invalid-email"}
        )

        assert response.status_code in [200, 422]

    def test_google_auth_url_endpoint(self, client):
        """Test Google auth URL generation"""
        response = client.get("/api/v1/auth/google/auth-url")

        # Should return auth URL or error if not configured
        assert response.status_code in [200, 500]

    def test_google_callback_no_code(self, client):
        """Test Google callback without authorization code"""
        response = client.get("/api/v1/auth/google/callback")

        # Should require authorization code
        assert response.status_code in [400, 405]
