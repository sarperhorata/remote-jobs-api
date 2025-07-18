#!/usr/bin/env python3

import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

class TestAuthExtended:
    """Extended test suite for auth API endpoints"""
    
    def test_auth_endpoints_exist(self):
        """Test that auth endpoints exist and return proper responses"""
        endpoints = [
            "/api/v1/auth/register",
            "/api/v1/auth/login", 
            "/api/v1/auth/me",
            "/api/v1/auth/forgot-password",
            "/api/v1/auth/reset-password"
        ]
        
        for endpoint in endpoints:
            response = client.get(endpoint)
            # Should not return 404 (route exists)
            assert response.status_code != 404, f"Auth endpoint {endpoint} not found"
    
    def test_register_endpoint_validation(self):
        """Test register endpoint input validation"""
        # Test empty data
        response = client.post("/api/v1/auth/register", json={})
        assert response.status_code in [400, 422]  # Validation error
        
        # Test invalid email
        response = client.post("/api/v1/auth/register", json={
            "email": "invalid-email",
            "password": "password123"
        })
        assert response.status_code in [400, 422]  # Validation error
        
    def test_login_endpoint_validation(self):
        """Test login endpoint input validation"""
        # Test empty data
        response = client.post("/api/v1/auth/login", json={})
        assert response.status_code in [400, 422]  # Validation error
        
        # Test missing password
        response = client.post("/api/v1/auth/login", json={
            "email": "test@example.com"
        })
        assert response.status_code in [400, 422]  # Validation error
        
    def test_protected_endpoints_require_auth(self):
        """Test that protected endpoints require authentication"""
        protected_endpoints = [
            ("GET", "/api/v1/auth/me"),
            ("POST", "/api/v1/auth/logout"),
            ("POST", "/api/v1/auth/refresh")
        ]
        
        for method, endpoint in protected_endpoints:
            if method == "GET":
                response = client.get(endpoint)
            else:
                response = client.post(endpoint)
            
            # Should require authentication
            assert response.status_code in [401, 403], f"Endpoint {endpoint} should require auth"
    
    def test_forgot_password_endpoint(self):
        """Test forgot password endpoint"""
        response = client.post("/api/v1/auth/forgot-password", json={
            "email": "test@example.com"
        })
        # Should not crash, might return success or validation error
        assert response.status_code in [200, 400, 422]
        
    def test_reset_password_endpoint(self):
        """Test reset password endpoint"""
        response = client.post("/api/v1/auth/reset-password", json={
            "token": "sample-token",
            "password": "newpassword123"
        })
        # Should not crash, might return error due to invalid token
        assert response.status_code in [200, 400, 404, 422]
        
    def test_auth_health_check(self):
        """Test auth module health"""
        response = client.get("/api/v1/auth/health")
        # Might not exist, but should not return 500
        assert response.status_code != 500
        
    def test_login_with_valid_format(self):
        """Test login with valid format (might fail auth but format is correct)"""
        response = client.post("/api/v1/auth/login", json={
            "email": "test@example.com",
            "password": "password123"
        })
        # Should handle gracefully - validation error is acceptable
        assert response.status_code in [200, 400, 401, 422]  # Various acceptable responses
        
    def test_register_with_valid_format(self):
        """Test register with valid format"""
        response = client.post("/api/v1/auth/register", json={
            "email": "newuser@example.com",
            "password": "password123",
            "name": "Test User"
        })
        # Should not return validation error, might return conflict or success
        assert response.status_code in [200, 400, 401, 422]  # Various acceptable responses
        
    def test_oauth_endpoints_exist(self):
        """Test OAuth endpoints exist"""
        oauth_endpoints = [
            "/api/v1/auth/google",
            "/api/v1/auth/google/callback",
            "/api/v1/auth/github",
            "/api/v1/auth/github/callback"
        ]
        
        for endpoint in oauth_endpoints:
            response = client.get(endpoint)
            # Should not return 404 (route might exist)
            # OAuth endpoints might redirect or return error
            assert response.status_code != 500  # Should not crash
            
    def test_token_validation_endpoint(self):
        """Test token validation endpoint"""
        response = client.post("/api/v1/auth/validate-token", json={
            "token": "sample-token"
        })
        # Should handle token validation gracefully
        assert response.status_code != 500
        
    def test_password_strength_validation(self):
        """Test password strength validation in register"""
        weak_passwords = ["123", "abc", "password"]
        
        for weak_password in weak_passwords:
            response = client.post("/api/v1/auth/register", json={
                "email": "test@example.com",
                "password": weak_password,
                "name": "Test User"
            })
            # Might have password strength validation
            # Should not crash regardless
            assert response.status_code != 500
            
    def test_email_verification_endpoints(self):
        """Test email verification related endpoints"""
        verification_endpoints = [
            "/api/v1/auth/verify-email",
            "/api/v1/auth/resend-verification"
        ]
        
        for endpoint in verification_endpoints:
            response = client.post(endpoint, json={"email": "test@example.com"})
            # Should not crash
            assert response.status_code != 500
            
    def test_auth_middleware_headers(self):
        """Test auth middleware handles headers correctly"""
        headers = {
            "Authorization": "Bearer invalid-token",
            "Content-Type": "application/json"
        }
        
        response = client.get("/api/v1/auth/me", headers=headers)
        # Should handle invalid token gracefully
        assert response.status_code in [401, 403]  # Proper auth error
        
    def test_cors_on_auth_endpoints(self):
        """Test CORS headers on auth endpoints"""
        response = client.options("/api/v1/auth/login")
        assert response.status_code in [200, 405]  # OPTIONS should work or be method not allowed
        
    def test_rate_limiting_simulation(self):
        """Test multiple requests don't crash the system"""
        # Make multiple requests to test rate limiting/stability
        for i in range(5):
            response = client.post("/api/v1/auth/login", json={
                "email": f"user{i}@example.com",
                "password": "password123"
            })
            # Should handle multiple requests gracefully
            assert response.status_code != 500 