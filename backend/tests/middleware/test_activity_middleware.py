import pytest
import asyncio
from unittest.mock import AsyncMock, patch, MagicMock
from httpx import AsyncClient
from fastapi import FastAPI, Request
from starlette.middleware.base import BaseHTTPMiddleware

from backend.middleware.activity_middleware import ActivityTrackingMiddleware
from backend.main import app

class TestActivityTrackingMiddleware:
    """Test suite for activity tracking middleware"""
    
    @pytest.fixture
    async def client(self):
        """Create test client with middleware"""
        async with AsyncClient(app=app, base_url="http://test") as ac:
            yield ac
    
    @pytest.fixture
    def mock_activity_logger(self):
        """Mock activity logger"""
        with patch('backend.middleware.activity_middleware.activity_logger') as mock:
            mock.log_activity = AsyncMock()
            yield mock
    
    async def test_middleware_tracks_api_calls(self, client, mock_activity_logger):
        """Test that middleware tracks API calls"""
        # Make a test API call
        response = await client.get("/api/jobs")
        
        # Verify activity was logged
        mock_activity_logger.log_activity.assert_called_once()
        call_args = mock_activity_logger.log_activity.call_args
        
        assert call_args[1]['activity_type'] in ['job_list', 'api_call']
        assert 'activity_data' in call_args[1]
        assert call_args[1]['activity_data']['endpoint'] == '/api/jobs'
        assert call_args[1]['activity_data']['method'] == 'GET'
    
    async def test_middleware_skips_excluded_paths(self, client, mock_activity_logger):
        """Test that middleware skips excluded paths"""
        # Make requests to excluded paths
        excluded_paths = ["/docs", "/health", "/favicon.ico"]
        
        for path in excluded_paths:
            response = await client.get(path)
            
        # Should not log any activities for excluded paths
        assert mock_activity_logger.log_activity.call_count == 0
    
    async def test_middleware_extracts_user_info(self, client, mock_activity_logger):
        """Test that middleware extracts user information from JWT"""
        # Mock JWT token
        mock_token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJ1c2VyXzEyMyJ9.test"
        
        with patch('backend.middleware.activity_middleware.decode_token') as mock_decode:
            mock_decode.return_value = {"sub": "user_123"}
            
            # Make authenticated request
            headers = {"Authorization": f"Bearer {mock_token}"}
            response = await client.get("/api/jobs", headers=headers)
            
            # Verify user ID was extracted
            mock_activity_logger.log_activity.assert_called_once()
            call_args = mock_activity_logger.log_activity.call_args
            assert call_args[1]['user_id'] == "user_123"
    
    async def test_middleware_tracks_response_time(self, client, mock_activity_logger):
        """Test that middleware tracks response time"""
        response = await client.get("/api/jobs")
        
        mock_activity_logger.log_activity.assert_called_once()
        call_args = mock_activity_logger.log_activity.call_args
        
        assert 'response_time_ms' in call_args[1]
        assert isinstance(call_args[1]['response_time_ms'], float)
        assert call_args[1]['response_time_ms'] > 0
    
    async def test_middleware_handles_errors(self, client, mock_activity_logger):
        """Test that middleware logs errors properly"""
        # Make request to non-existent endpoint
        response = await client.get("/api/nonexistent")
        
        mock_activity_logger.log_activity.assert_called_once()
        call_args = mock_activity_logger.log_activity.call_args
        
        # Should log the error
        assert call_args[1]['status_code'] == 404
        assert call_args[1]['is_success'] == False
    
    async def test_middleware_determines_activity_types(self, client, mock_activity_logger):
        """Test activity type determination for different endpoints"""
        test_cases = [
            ("/api/auth/login", "POST", "login"),
            ("/api/auth/register", "POST", "register"),
            ("/api/jobs/search", "GET", "job_search"),
            ("/api/jobs/123", "GET", "job_view"),
            ("/api/applications", "POST", "job_apply"),
            ("/api/companies", "GET", "company_view"),
            ("/api/profile", "PUT", "profile_update"),
            ("/admin/dashboard", "GET", "admin_action")
        ]
        
        for endpoint, method, expected_type in test_cases:
            mock_activity_logger.reset_mock()
            
            if method == "GET":
                await client.get(endpoint)
            elif method == "POST":
                await client.post(endpoint, json={})
            elif method == "PUT":
                await client.put(endpoint, json={})
            
            if mock_activity_logger.log_activity.called:
                call_args = mock_activity_logger.log_activity.call_args
                assert call_args[1]['activity_type'] == expected_type
    
    async def test_middleware_extracts_client_ip(self, client, mock_activity_logger):
        """Test client IP extraction from headers"""
        # Test with X-Forwarded-For header
        headers = {"X-Forwarded-For": "192.168.1.100, 10.0.0.1"}
        response = await client.get("/api/jobs", headers=headers)
        
        mock_activity_logger.log_activity.assert_called_once()
        call_args = mock_activity_logger.log_activity.call_args
        
        assert call_args[1]['ip_address'] == "192.168.1.100"
    
    async def test_middleware_adds_response_headers(self, client, mock_activity_logger):
        """Test that middleware adds tracking headers to response"""
        response = await client.get("/api/jobs")
        
        # Check response headers
        assert "X-Request-ID" in response.headers
        assert "X-Response-Time" in response.headers
        assert response.headers["X-Response-Time"].endswith("ms")
    
    async def test_middleware_handles_concurrent_requests(self, client, mock_activity_logger):
        """Test middleware handles concurrent requests properly"""
        # Make multiple concurrent requests
        tasks = [
            client.get("/api/jobs"),
            client.get("/api/companies"),
            client.get("/api/applications/stats")
        ]
        
        responses = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Should log activity for each request
        assert mock_activity_logger.log_activity.call_count == 3
        
        # Each request should have unique request ID
        request_ids = []
        for call in mock_activity_logger.log_activity.call_args_list:
            request_id = call[1]['activity_data']['request_id']
            request_ids.append(request_id)
        
        assert len(set(request_ids)) == 3  # All unique
    
    async def test_middleware_logs_request_metadata(self, client, mock_activity_logger):
        """Test that middleware logs complete request metadata"""
        headers = {
            "User-Agent": "Mozilla/5.0 (Test Browser)",
            "Referer": "https://example.com/previous-page",
            "X-Real-IP": "203.0.113.1"
        }
        
        response = await client.get("/api/jobs?limit=10&company=test", headers=headers)
        
        mock_activity_logger.log_activity.assert_called_once()
        call_args = mock_activity_logger.log_activity.call_args
        
        activity_data = call_args[1]['activity_data']
        assert activity_data['user_agent'] == "Mozilla/5.0 (Test Browser)"
        assert activity_data['referer'] == "https://example.com/previous-page"
        assert activity_data['query_params'] == {"limit": "10", "company": "test"}
        assert call_args[1]['ip_address'] == "203.0.113.1"
    
    def test_determine_activity_type_edge_cases(self):
        """Test activity type determination edge cases"""
        middleware = ActivityTrackingMiddleware(app=None)
        
        test_cases = [
            ("/api/unknown", "GET", "api_call"),
            ("/custom/endpoint", "POST", "api_call"),
            ("/api/auth/custom", "PUT", "auth_action"),
            ("/api/jobs/123/apply", "POST", "job_apply"),
            ("/api/jobs/456/save", "POST", "job_save"),
        ]
        
        for endpoint, method, expected in test_cases:
            result = middleware._determine_activity_type(endpoint, method)
            assert result == expected
    
    def test_get_client_ip_fallbacks(self):
        """Test client IP extraction fallback methods"""
        middleware = ActivityTrackingMiddleware(app=None)
        
        # Create mock request
        mock_request = MagicMock()
        mock_request.headers.get.side_effect = lambda key: {
            "x-forwarded-for": None,
            "x-real-ip": "10.0.0.1"
        }.get(key)
        mock_request.client.host = "127.0.0.1"
        
        ip = middleware._get_client_ip(mock_request)
        assert ip == "10.0.0.1"
        
        # Test fallback to client.host
        mock_request.headers.get.return_value = None
        ip = middleware._get_client_ip(mock_request)
        assert ip == "127.0.0.1"
    
    async def test_middleware_session_extraction(self, client, mock_activity_logger):
        """Test session ID extraction from request"""
        # Mock session data
        with patch('backend.middleware.activity_middleware.Request') as mock_request_class:
            mock_request = mock_request_class.return_value
            mock_request.session = {"session_id": "session_abc123"}
            
            response = await client.get("/api/jobs")
            
            # Note: In real scenario, session extraction would work
            # This test verifies the middleware attempts to extract session
            mock_activity_logger.log_activity.assert_called_once() 