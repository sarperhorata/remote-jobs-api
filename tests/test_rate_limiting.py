import pytest
import time
from unittest.mock import MagicMock, AsyncMock
from fastapi import Request, HTTPException
from backend.middleware.rate_limiting import RateLimitingMiddleware

pytestmark = pytest.mark.asyncio

class TestRateLimiting:
    """Test rate limiting middleware"""
    
    def test_init_rate_limiter(self):
        """Test rate limiter initialization"""
        middleware = RateLimitingMiddleware()
        
        assert hasattr(middleware, 'rate_limits')
        assert hasattr(middleware, 'ip_rate_limits')
        assert hasattr(middleware, 'user_rate_limits')
        assert 'default' in middleware.rate_limits
    
    def test_get_client_ip(self):
        """Test getting client IP from request"""
        middleware = RateLimitingMiddleware()
        
        # Mock request with X-Forwarded-For header
        mock_request = MagicMock()
        mock_request.headers = {"X-Forwarded-For": "192.168.1.1, 10.0.0.1"}
        mock_request.client.host = "127.0.0.1"
        
        ip = middleware._get_client_ip(mock_request)
        assert ip == "192.168.1.1"
        
        # Mock request without X-Forwarded-For
        mock_request.headers = {}
        ip = middleware._get_client_ip(mock_request)
        assert ip == "127.0.0.1"
        
        # Mock request with no client
        mock_request.client = None
        ip = middleware._get_client_ip(mock_request)
        assert ip == "unknown"
    
    def test_get_user_id_authenticated(self):
        """Test getting user ID from authenticated request"""
        middleware = RateLimitingMiddleware()
        
        # Mock request with user in state
        mock_request = MagicMock()
        mock_request.state.user = {"_id": "user123"}
        
        user_id = middleware._get_user_id(mock_request)
        assert user_id == "user123"
    
    def test_get_user_id_unauthenticated(self):
        """Test getting user ID from unauthenticated request"""
        middleware = RateLimitingMiddleware()
        
        # Mock request without user
        mock_request = MagicMock()
        mock_request.state.user = None
        
        user_id = middleware._get_user_id(mock_request)
        assert user_id is None
        
        # Mock request without state
        mock_request.state = None
        user_id = middleware._get_user_id(mock_request)
        assert user_id is None
    
    def test_rate_limiter_is_allowed(self):
        """Test rate limiter is_allowed method"""
        from backend.middleware.rate_limiting import RateLimiter
        
        limiter = RateLimiter(max_requests=2, window_seconds=60)
        
        # First two requests should be allowed
        assert limiter.is_allowed("test_key") is True
        assert limiter.is_allowed("test_key") is True
        
        # Third request should be blocked
        assert limiter.is_allowed("test_key") is False
    
    def test_rate_limiter_get_remaining(self):
        """Test rate limiter get_remaining_requests method"""
        from backend.middleware.rate_limiting import RateLimiter
        
        limiter = RateLimiter(max_requests=5, window_seconds=60)
        
        # Initially should have 5 remaining
        assert limiter.get_remaining_requests("test_key") == 5
        
        # After one request, should have 4 remaining
        limiter.is_allowed("test_key")
        assert limiter.get_remaining_requests("test_key") == 4
    
    def test_get_rate_limit_key(self):
        """Test getting rate limit key for different endpoints"""
        middleware = RateLimitingMiddleware()
        
        # Mock request for auth endpoint
        mock_request = MagicMock()
        mock_request.url.path = "/auth/login"
        
        key = middleware._get_rate_limit_key(mock_request)
        assert key == "/auth/login"
        
        # Mock request for admin endpoint
        mock_request.url.path = "/admin/users"
        
        key = middleware._get_rate_limit_key(mock_request)
        assert key == "/admin/"
        
        # Mock request for default endpoint
        mock_request.url.path = "/api/test"
        
        key = middleware._get_rate_limit_key(mock_request)
        assert key == "default"
    
    async def test_middleware_success(self):
        """Test middleware successfully processes request"""
        middleware = RateLimitingMiddleware()
        
        # Mock request
        mock_request = MagicMock()
        mock_request.headers = {}
        mock_request.client.host = "192.168.1.1"
        mock_request.state.user = None
        mock_request.url.path = "/api/test"
        
        # Mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.headers = {}
        
        # Mock call_next
        mock_call_next = AsyncMock(return_value=mock_response)
        
        # Test middleware
        response = await middleware(mock_request, mock_call_next)
        
        assert response == mock_response
        mock_call_next.assert_called_once_with(mock_request)
    
    def test_brute_force_protection(self):
        """Test brute force protection functionality"""
        from backend.middleware.rate_limiting import BruteForceProtection
        
        protection = BruteForceProtection()
        
        # Test recording failed attempts
        protection.record_failed_attempt("test@example.com", "192.168.1.1")
        protection.record_failed_attempt("test@example.com", "192.168.1.1")
        protection.record_failed_attempt("test@example.com", "192.168.1.1")
        protection.record_failed_attempt("test@example.com", "192.168.1.1")
        protection.record_failed_attempt("test@example.com", "192.168.1.1")
        
        # Should be blocked after 5 failed attempts
        assert protection.is_blocked("test@example.com") is True
        
        # Test successful attempt
        protection.record_successful_attempt("test@example.com")
        
        # Should not be blocked after successful attempt
        assert protection.is_blocked("test@example.com") is False