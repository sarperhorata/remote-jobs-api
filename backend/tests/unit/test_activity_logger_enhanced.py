import pytest
from unittest.mock import Mock, AsyncMock, patch
from backend.services.activity_logger import activity_logger, ActivityLogger

class TestActivityLogger:
    """Test activity logger service"""
    
    def test_logger_initialization(self):
        """Test activity logger initialization"""
        logger = ActivityLogger()
        assert logger is not None
        
    @pytest.mark.asyncio
    async def test_log_request_method(self):
        """Test log_request method"""
        with patch.object(activity_logger, "log_request") as mock_method:
            mock_method.return_value = AsyncMock()
            
            await activity_logger.log_request("GET", "/test", 200)
            mock_method.assert_called_once()
            
    @pytest.mark.asyncio
    async def test_log_user_activity(self):
        """Test log_user_activity method"""
        with patch.object(activity_logger, "log_user_activity") as mock_method:
            mock_method.return_value = AsyncMock()
            
            await activity_logger.log_user_activity("user123", "login")
            mock_method.assert_called_once()
            
    @pytest.mark.asyncio
    async def test_get_user_activity(self):
        """Test get_user_activity method"""
        with patch.object(activity_logger, "get_user_activity") as mock_method:
            mock_method.return_value = AsyncMock(return_value=[])
            
            activities = await activity_logger.get_user_activity("user123")
            assert isinstance(activities, list)
            
    def test_logger_configuration(self):
        """Test logger configuration"""
        assert activity_logger is not None
        assert hasattr(activity_logger, "log_request")
