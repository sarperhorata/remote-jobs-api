"""
Middleware Tests
Middleware fonksiyonları için testler
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from fastapi import Request, Response
from fastapi.testclient import TestClient
from backend.middleware.auth_middleware import AuthMiddleware
from backend.middleware.rate_limiter import RateLimiter
from backend.middleware.input_validation import validate_url, sanitize_input
from backend.middleware.security_headers import SecurityHeadersMiddleware


class TestAuthMiddleware:
    """AuthMiddleware testleri"""
    
    def test_auth_middleware_creation(self):
        """AuthMiddleware oluşturma testi"""
        middleware = AuthMiddleware()
        assert middleware is not None
        
    @pytest.mark.asyncio
    async def test_auth_middleware_valid_token(self):
        """Geçerli token testi"""
        middleware = AuthMiddleware()
        request = Mock()
        request.headers = {"Authorization": "Bearer valid_token"}
        
        # Mock token verification
        with patch('backend.middleware.auth_middleware.verify_token') as mock_verify:
            mock_verify.return_value = {"user_id": "123"}
            result = await middleware.authenticate(request)
            assert result is True
            
    @pytest.mark.asyncio
    async def test_auth_middleware_invalid_token(self):
        """Geçersiz token testi"""
        middleware = AuthMiddleware()
        request = Mock()
        request.headers = {"Authorization": "Bearer invalid_token"}
        
        with patch('backend.middleware.auth_middleware.verify_token') as mock_verify:
            mock_verify.return_value = None
            result = await middleware.authenticate(request)
            assert result is False
            
    @pytest.mark.asyncio
    async def test_auth_middleware_no_token(self):
        """Token yok testi"""
        middleware = AuthMiddleware()
        request = Mock()
        request.headers = {}
        
        result = await middleware.authenticate(request)
        assert result is False


class TestRateLimiter:
    """RateLimiter testleri"""
    
    def test_rate_limiter_creation(self):
        """RateLimiter oluşturma testi"""
        limiter = RateLimiter()
        assert limiter is not None
        
    def test_rate_limiter_check_limit(self):
        """Rate limit kontrolü testi"""
        limiter = RateLimiter(max_requests=5, window_seconds=60)
        
        # İlk 5 istek geçmeli
        for i in range(5):
            assert limiter.check_limit("test_ip") is True
            
        # 6. istek reddedilmeli
        assert limiter.check_limit("test_ip") is False
        
    def test_rate_limiter_reset_after_window(self):
        """Pencere sonrası reset testi"""
        limiter = RateLimiter(max_requests=1, window_seconds=1)
        
        assert limiter.check_limit("test_ip") is True
        assert limiter.check_limit("test_ip") is False
        
        # 1 saniye bekle (test ortamında)
        import time
        time.sleep(1.1)
        
        # Tekrar deneme
        assert limiter.check_limit("test_ip") is True


class TestInputValidation:
    """Input validation testleri"""
    
    def test_validate_url_valid(self):
        """Geçerli URL testi"""
        assert validate_url("https://example.com") is True
        assert validate_url("http://localhost:3000") is True
        
    def test_validate_url_invalid(self):
        """Geçersiz URL testi"""
        assert validate_url("not-a-url") is False
        assert validate_url("") is False
        assert validate_url(None) is False
        
    def test_sanitize_input_basic(self):
        """Temel input sanitization testi"""
        result = sanitize_input("test<script>alert('xss')</script>")
        assert "<script>" not in result
        assert "alert" not in result
        
    def test_sanitize_input_sql_injection(self):
        """SQL injection koruması testi"""
        result = sanitize_input("'; DROP TABLE users; --")
        assert "DROP TABLE" not in result
        assert ";" not in result
        
    def test_sanitize_input_empty(self):
        """Boş input testi"""
        assert sanitize_input("") == ""
        assert sanitize_input(None) == ""


class TestSecurityHeadersMiddleware:
    """SecurityHeadersMiddleware testleri"""
    
    def test_security_headers_middleware_creation(self):
        """SecurityHeadersMiddleware oluşturma testi"""
        middleware = SecurityHeadersMiddleware()
        assert middleware is not None
        
    def test_security_headers_added(self):
        """Güvenlik header'ları ekleme testi"""
        middleware = SecurityHeadersMiddleware()
        response = Response()
        
        middleware.add_security_headers(response)
        
        assert "X-Content-Type-Options" in response.headers
        assert "X-Frame-Options" in response.headers
        assert "X-XSS-Protection" in response.headers
        
    def test_csp_header_content(self):
        """CSP header içeriği testi"""
        middleware = SecurityHeadersMiddleware()
        response = Response()
        
        middleware.add_security_headers(response)
        
        csp_header = response.headers.get("Content-Security-Policy")
        assert csp_header is not None
        assert "default-src 'self'" in csp_header 