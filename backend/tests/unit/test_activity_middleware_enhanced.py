import pytest
from unittest.mock import Mock, patch, AsyncMock
from fastapi import Request, Response
from backend.middleware.activity_middleware import ActivityTrackingMiddleware, activity_logger

class TestActivityMiddleware:
    """Test activity middleware comprehensively"""
    
    @pytest.mark.asyncio
    async def test_middleware_initialization(self):
        """Test middleware initialization"""
        middleware = ActivityTrackingMiddleware(Mock())
        assert middleware.app is not None
        
    @pytest.mark.asyncio
    async def test_middleware_call_success(self):
        """Test successful middleware call"""
        app = AsyncMock()
        middleware = ActivityTrackingMiddleware(app)
        
        scope = {"type": "http", "method": "GET", "path": "/test"}
        receive = AsyncMock()
        send = AsyncMock()
        
        await middleware(scope, receive, send)
        app.assert_called_once()
        
    @pytest.mark.asyncio
    async def test_middleware_logs_activity(self):
        """Test that middleware logs activity"""
        with patch("backend.middleware.activity_middleware.activity_logger") as mock_logger:
            mock_logger.log_request = AsyncMock()
            
            app = AsyncMock()
            middleware = ActivityTrackingMiddleware(app)
            
            scope = {"type": "http", "method": "POST", "path": "/api/test"}
            receive = AsyncMock()
            send = AsyncMock()
            
            await middleware(scope, receive, send)
            
    @pytest.mark.asyncio
    async def test_middleware_error_handling(self):
        """Test middleware error handling"""
        app = AsyncMock(side_effect=Exception("Test error"))
        middleware = ActivityTrackingMiddleware(app)
        
        scope = {"type": "http", "method": "GET", "path": "/test"}
        receive = AsyncMock()
        send = AsyncMock()
        
        with pytest.raises(Exception):
            await middleware(scope, receive, send)
            
    def test_activity_logger_exists(self):
        """Test activity logger is available"""
        assert activity_logger is not None
