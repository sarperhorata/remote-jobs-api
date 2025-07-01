import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from datetime import datetime, timedelta
from bson import ObjectId

from backend.services.activity_logger import ActivityLogger, activity_logger
from backend.models.user_activity import ActivityType, UserSession, UserActivity


class TestActivityLogger:
    """Activity Logger service testleri"""
    
    @pytest.fixture
    async def mock_db(self):
        """Mock database"""
        db = Mock()
        db.user_activities = Mock()
        db.user_sessions = Mock()
        db.activity_summaries = Mock()
        
        # Mock collection methods
        db.user_activities.create_index = AsyncMock()
        db.user_activities.insert_one = AsyncMock(return_value=Mock(inserted_id=ObjectId()))
        db.user_activities.find = Mock(return_value=Mock(
            sort=Mock(return_value=Mock(
                skip=Mock(return_value=Mock(
                    limit=Mock(return_value=Mock(
                        to_list=AsyncMock(return_value=[])
                    ))
                ))
            ))
        ))
        db.user_activities.aggregate = Mock(return_value=Mock(
            to_list=AsyncMock(return_value=[])
        ))
        
        db.user_sessions.create_index = AsyncMock()
        db.user_sessions.insert_one = AsyncMock(return_value=Mock(inserted_id=ObjectId()))
        db.user_sessions.find_one = AsyncMock(return_value=None)
        db.user_sessions.update_one = AsyncMock()
        db.user_sessions.find = Mock(return_value=Mock(
            sort=Mock(return_value=Mock(
                skip=Mock(return_value=Mock(
                    limit=Mock(return_value=Mock(
                        to_list=AsyncMock(return_value=[])
                    ))
                ))
            ))
        ))
        
        db.activity_summaries.create_index = AsyncMock()
        db.activity_summaries.update_one = AsyncMock()
        
        return db
    
    @pytest.fixture
    def logger_service(self, mock_db):
        """Activity logger service instance"""
        logger = ActivityLogger()
        logger.db = mock_db
        return logger
    
    @pytest.mark.asyncio
    async def test_initialization(self):
        """Service başlatma testi"""
        logger = ActivityLogger()
        assert logger.db is None
        assert logger._session_cache == {}
        
        with patch('backend.services.activity_logger.get_async_db') as mock_get_db:
            mock_get_db.return_value = Mock()
            await logger.initialize()
            assert logger.db is not None
    
    @pytest.mark.asyncio
    async def test_create_indexes(self, logger_service, mock_db):
        """Index oluşturma testi"""
        await logger_service._create_indexes()
        
        # Verify all indexes are created
        assert mock_db.user_activities.create_index.call_count >= 4
        assert mock_db.user_sessions.create_index.call_count >= 3
        assert mock_db.activity_summaries.create_index.call_count >= 2
    
    @pytest.mark.asyncio
    async def test_create_indexes_mock_database(self):
        """Mock database için index oluşturma testi"""
        logger = ActivityLogger()
        mock_db = Mock()
        mock_db._MockDatabase__name = "test"
        logger.db = mock_db
        
        await logger._create_indexes()
        # Mock database için index oluşturmaması gerek
        assert not hasattr(mock_db, 'create_index') or not mock_db.create_index.called
    
    def test_parse_user_agent(self, logger_service):
        """User agent parsing testi"""
        # Test normal user agent
        ua_string = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        result = logger_service._parse_user_agent(ua_string)
        
        assert "browser" in result
        assert "os" in result
        assert "device_type" in result
        assert result["device_type"] in ["desktop", "mobile", "tablet"]
        
        # Test empty user agent
        result = logger_service._parse_user_agent("")
        assert result["browser"] == "Unknown"
        assert result["os"] == "Unknown"
        assert result["device_type"] == "desktop"
        
        # Test mobile user agent
        mobile_ua = "Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X)"
        result = logger_service._parse_user_agent(mobile_ua)
        # Note: Actual parsing may vary, test basic structure
        assert "browser" in result
        assert "os" in result
        assert "device_type" in result
    
    def test_get_client_ip(self, logger_service):
        """Client IP extraction testi"""
        # Test X-Forwarded-For header
        headers = {"X-Forwarded-For": "192.168.1.1, 10.0.0.1"}
        ip = logger_service._get_client_ip(headers)
        assert ip == "192.168.1.1"
        
        # Test X-Real-IP header
        headers = {"X-Real-IP": "203.0.113.1"}
        ip = logger_service._get_client_ip(headers)
        assert ip == "203.0.113.1"
        
        # Test invalid IP
        headers = {"X-Forwarded-For": "invalid-ip"}
        ip = logger_service._get_client_ip(headers)
        assert ip == "unknown"
        
        # Test no headers
        headers = {}
        ip = logger_service._get_client_ip(headers)
        assert ip == "unknown"
    
    @pytest.mark.asyncio
    async def test_log_activity_success(self, logger_service, mock_db):
        """Başarılı activity logging testi"""
        activity_id = await logger_service.log_activity(
            activity_type=ActivityType.JOB_SEARCH,
            user_id="user123",
            session_id="session123",
            activity_data={"query": "python developer"}
        )
        
        assert activity_id is not None
        mock_db.user_activities.insert_one.assert_called_once()
        
        call_args = mock_db.user_activities.insert_one.call_args[0][0]
        assert call_args["activity_type"] == ActivityType.JOB_SEARCH
        assert call_args["user_id"] == "user123"
        assert call_args["session_id"] == "session123"
        assert call_args["activity_data"]["query"] == "python developer"
        assert "timestamp" in call_args
    
    @pytest.mark.asyncio
    async def test_log_activity_mock_database(self):
        """Mock database için activity logging testi"""
        logger = ActivityLogger()
        mock_db = Mock()
        mock_db._MockDatabase__name = "test"
        logger.db = mock_db
        
        activity_id = await logger.log_activity(
            activity_type=ActivityType.LOGIN,
            user_id="user123"
        )
        
        assert activity_id == "mock_activity_id"
    
    @pytest.mark.asyncio
    async def test_start_session(self, logger_service, mock_db):
        """Session başlatma testi"""
        request_data = {
            "headers": {
                "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
                "x-forwarded-for": "192.168.1.1"
            }
        }
        
        session_id = await logger_service.start_session(
            user_id="user123",
            session_token="token123",
            request_data=request_data
        )
        
        assert session_id is not None
        mock_db.user_sessions.insert_one.assert_called_once()
        
        # Check session cache
        assert "token123" in logger_service._session_cache
    
    @pytest.mark.asyncio
    async def test_end_session(self, logger_service, mock_db):
        """Session sonlandırma testi"""
        # Setup existing session
        session_data = {
            "_id": ObjectId(),
            "user_id": "user123",
            "started_at": datetime.utcnow() - timedelta(hours=1)
        }
        mock_db.user_sessions.find_one.return_value = session_data
        
        # Add to cache
        logger_service._session_cache["token123"] = str(session_data["_id"])
        
        await logger_service.end_session("token123")
        
        # Verify session updated
        mock_db.user_sessions.update_one.assert_called_once()
        update_call = mock_db.user_sessions.update_one.call_args
        assert update_call[0][0]["session_token"] == "token123"
        assert "ended_at" in update_call[0][1]["$set"]
        assert update_call[0][1]["$set"]["is_active"] is False
        
        # Check cache cleared
        assert "token123" not in logger_service._session_cache
    
    @pytest.mark.asyncio
    async def test_end_session_not_found(self, logger_service, mock_db):
        """Bulunamayan session sonlandırma testi"""
        mock_db.user_sessions.find_one.return_value = None
        
        await logger_service.end_session("nonexistent_token")
        
        # Should not call update if session not found
        mock_db.user_sessions.update_one.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_get_user_activities(self, logger_service, mock_db):
        """User activities alma testi"""
        # Setup mock activities
        mock_activities = [
            {
                "_id": ObjectId(),
                "user_id": "user123",
                "activity_type": ActivityType.JOB_SEARCH,
                "timestamp": datetime.utcnow()
            }
        ]
        
        # Configure mock chain
        mock_cursor = Mock()
        mock_cursor.to_list = AsyncMock(return_value=mock_activities)
        mock_db.user_activities.find.return_value.sort.return_value.skip.return_value.limit.return_value = mock_cursor
        
        activities = await logger_service.get_user_activities("user123", limit=10)
        
        assert len(activities) == 1
        assert isinstance(activities[0]["_id"], str)  # ObjectId converted to string
        
        # Verify query parameters
        mock_db.user_activities.find.assert_called_once_with({"user_id": "user123"})
    
    @pytest.mark.asyncio
    async def test_get_user_activities_with_filters(self, logger_service, mock_db):
        """Filtreli user activities alma testi"""
        start_date = datetime.utcnow() - timedelta(days=7)
        end_date = datetime.utcnow()
        
        await logger_service.get_user_activities(
            "user123",
            activity_type=ActivityType.JOB_VIEW,
            start_date=start_date,
            end_date=end_date
        )
        
        # Verify query includes filters
        call_args = mock_db.user_activities.find.call_args[0][0]
        assert call_args["user_id"] == "user123"
        assert call_args["activity_type"] == ActivityType.JOB_VIEW
        assert "$gte" in call_args["timestamp"]
        assert "$lte" in call_args["timestamp"]
    
    @pytest.mark.asyncio
    async def test_get_user_sessions(self, logger_service, mock_db):
        """User sessions alma testi"""
        mock_sessions = [
            {
                "_id": ObjectId(),
                "user_id": "user123",
                "session_token": "token123",
                "is_active": True
            }
        ]
        
        mock_cursor = Mock()
        mock_cursor.to_list = AsyncMock(return_value=mock_sessions)
        mock_db.user_sessions.find.return_value.sort.return_value.skip.return_value.limit.return_value = mock_cursor
        
        sessions = await logger_service.get_user_sessions("user123", active_only=True)
        
        assert len(sessions) == 1
        assert isinstance(sessions[0]["_id"], str)
        
        # Verify query includes active filter
        call_args = mock_db.user_sessions.find.call_args[0][0]
        assert call_args["user_id"] == "user123"
        assert call_args["is_active"] is True
    
    @pytest.mark.asyncio
    async def test_get_activity_analytics(self, logger_service, mock_db):
        """Activity analytics testi"""
        mock_results = [
            {
                "activity_type": ActivityType.JOB_SEARCH,
                "count": 50,
                "unique_users": 10
            },
            {
                "activity_type": ActivityType.JOB_VIEW,
                "count": 150,
                "unique_users": 15
            }
        ]
        
        mock_aggregate = Mock()
        mock_aggregate.to_list = AsyncMock(return_value=mock_results)
        mock_db.user_activities.aggregate.return_value = mock_aggregate
        
        start_date = datetime.utcnow() - timedelta(days=7)
        analytics = await logger_service.get_activity_analytics(
            user_id="user123",
            start_date=start_date
        )
        
        assert analytics["total_activities"] == 200
        assert ActivityType.JOB_SEARCH in analytics["activity_breakdown"]
        assert analytics["activity_breakdown"][ActivityType.JOB_SEARCH] == 50
        assert analytics["period"]["start_date"] is not None
    
    @pytest.mark.asyncio
    async def test_update_session_activity(self, logger_service, mock_db):
        """Session activity güncelleme testi"""
        session_id = "session123"
        
        await logger_service._update_session_activity(session_id, ActivityType.JOB_SEARCH)
        
        mock_db.user_sessions.update_one.assert_called_once()
        call_args = mock_db.user_sessions.update_one.call_args
        
        assert call_args[0][0]["_id"] == session_id
        assert "$inc" in call_args[0][1]
        assert call_args[0][1]["$inc"]["total_requests"] == 1
    
    @pytest.mark.asyncio
    async def test_update_session_activity_error(self, logger_service, mock_db):
        """Error activity için session güncelleme testi"""
        session_id = "session123"
        
        await logger_service._update_session_activity(session_id, ActivityType.ERROR_OCCURRED)
        
        call_args = mock_db.user_sessions.update_one.call_args[0][1]
        assert call_args["$inc"]["total_errors"] == 1
    
    @pytest.mark.asyncio
    async def test_update_activity_summary(self, logger_service, mock_db):
        """Activity summary güncelleme testi"""
        await logger_service._update_activity_summary("user123", ActivityType.JOB_SEARCH)
        
        mock_db.activity_summaries.update_one.assert_called_once()
        call_args = mock_db.activity_summaries.update_one.call_args
        
        assert call_args[0][0]["user_id"] == "user123"
        assert call_args[0][0]["period_type"] == "daily"
        assert "$inc" in call_args[0][1]
        assert call_args[0][1]["$inc"]["job_searches"] == 1
        assert call_args[1]["upsert"] is True
    
    def test_global_activity_logger_instance(self):
        """Global activity logger instance testi"""
        assert activity_logger is not None
        assert isinstance(activity_logger, ActivityLogger)
    
    @pytest.mark.asyncio
    async def test_error_handling(self, logger_service, mock_db):
        """Error handling testi"""
        # Make database operations fail
        mock_db.user_activities.insert_one.side_effect = Exception("Database error")
        
        # Should not raise exception, should return empty string or mock_id
        activity_id = await logger_service.log_activity(
            activity_type=ActivityType.LOGIN,
            user_id="user123"
        )
        
        # Should handle error gracefully
        assert activity_id in ["", "mock_activity_id"]
    
    @pytest.mark.asyncio
    async def test_log_activity_uninitialized_db(self):
        """Başlatılmamış DB ile activity logging testi"""
        logger = ActivityLogger()
        
        with patch.object(logger, 'initialize') as mock_init:
            mock_init.return_value = AsyncMock()
            
            await logger.log_activity(
                activity_type=ActivityType.LOGIN,
                user_id="user123"
            )
            
            mock_init.assert_called_once() 