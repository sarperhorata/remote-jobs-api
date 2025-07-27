from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, Mock, patch

import pytest
from services.performance_analytics_service import PerformanceAnalyticsService


class TestPerformanceAnalyticsService:
    """Performance Analytics Service testleri"""

    @pytest.fixture
    def mock_db(self):
        """Mock database"""
        db = Mock()
        db.performance_metrics = Mock()
        db.user_activities = Mock()
        db.job_views = Mock()
        db.search_queries = Mock()
        db.error_logs = Mock()
        return db

    @pytest.fixture
    def analytics_service(self, mock_db):
        """Performance analytics service instance"""
        return PerformanceAnalyticsService(mock_db)

    @pytest.fixture
    def sample_metric_data(self):
        """Sample metric data"""
        return {
            "endpoint": "/api/v1/jobs",
            "duration_ms": 150.5,
            "status_code": 200,
            "timestamp": datetime.utcnow(),
            "date": datetime.utcnow().date().isoformat(),
        }

    @pytest.fixture
    def sample_user_activity(self):
        """Sample user activity data"""
        return {
            "user_id": "user123",
            "action": "search",
            "timestamp": datetime.utcnow(),
            "metadata": {"query": "python developer", "results_count": 25},
        }

    def test_service_initialization(self, analytics_service, mock_db):
        """Service başlatma testi"""
        assert analytics_service is not None
        assert analytics_service.db == mock_db
        assert hasattr(analytics_service, "metrics_cache")
        assert isinstance(analytics_service.metrics_cache, dict)

    @pytest.mark.asyncio
    async def test_track_api_call_success(self, analytics_service, sample_metric_data):
        """Başarılı API call tracking testi"""
        analytics_service.db.performance_metrics.insert_one = AsyncMock()

        await analytics_service.track_api_call(
            endpoint=sample_metric_data["endpoint"],
            duration_ms=sample_metric_data["duration_ms"],
            status_code=sample_metric_data["status_code"],
        )

        analytics_service.db.performance_metrics.insert_one.assert_called_once()
        call_args = analytics_service.db.performance_metrics.insert_one.call_args[0][0]
        assert call_args["endpoint"] == sample_metric_data["endpoint"]
        assert call_args["duration_ms"] == sample_metric_data["duration_ms"]
        assert call_args["status_code"] == sample_metric_data["status_code"]

    @pytest.mark.asyncio
    async def test_track_api_call_error(self, analytics_service):
        """API call tracking hatası testi"""
        analytics_service.db.performance_metrics.insert_one = AsyncMock(
            side_effect=Exception("DB error")
        )

        # Should not raise exception
        await analytics_service.track_api_call("/api/v1/jobs", 150.5, 200)

        analytics_service.db.performance_metrics.insert_one.assert_called_once()

    @pytest.mark.asyncio
    async def test_track_user_activity_success(
        self, analytics_service, sample_user_activity
    ):
        """Başarılı user activity tracking testi"""
        analytics_service.db.user_activities.insert_one = AsyncMock()

        await analytics_service.track_user_activity(
            user_id=sample_user_activity["user_id"],
            action=sample_user_activity["action"],
            metadata=sample_user_activity["metadata"],
        )

        analytics_service.db.user_activities.insert_one.assert_called_once()
        call_args = analytics_service.db.user_activities.insert_one.call_args[0][0]
        assert call_args["user_id"] == sample_user_activity["user_id"]
        assert call_args["action"] == sample_user_activity["action"]
        assert call_args["metadata"] == sample_user_activity["metadata"]

    @pytest.mark.asyncio
    async def test_track_user_activity_error(self, analytics_service):
        """User activity tracking hatası testi"""
        analytics_service.db.user_activities.insert_one = AsyncMock(
            side_effect=Exception("DB error")
        )

        # Should not raise exception
        await analytics_service.track_user_activity(
            "user123", "search", {"query": "test"}
        )

        analytics_service.db.user_activities.insert_one.assert_called_once()

    @pytest.mark.asyncio
    async def test_track_job_view_success(self, analytics_service):
        """Başarılı job view tracking testi"""
        analytics_service.db.job_views.insert_one = AsyncMock()

        await analytics_service.track_job_view("job123", "user456")

        analytics_service.db.job_views.insert_one.assert_called_once()
        call_args = analytics_service.db.job_views.insert_one.call_args[0][0]
        assert call_args["job_id"] == "job123"
        assert call_args["user_id"] == "user456"
        assert "timestamp" in call_args

    @pytest.mark.asyncio
    async def test_track_search_query_success(self, analytics_service):
        """Başarılı search query tracking testi"""
        analytics_service.db.search_queries.insert_one = AsyncMock()

        await analytics_service.track_search_query("python developer", 25, "user123")

        analytics_service.db.search_queries.insert_one.assert_called_once()
        call_args = analytics_service.db.search_queries.insert_one.call_args[0][0]
        assert call_args["query"] == "python developer"
        assert call_args["results_count"] == 25
        assert call_args["user_id"] == "user123"
        assert "timestamp" in call_args

    @pytest.mark.asyncio
    async def test_track_error_success(self, analytics_service):
        """Başarılı error tracking testi"""
        analytics_service.db.error_logs.insert_one = AsyncMock()

        await analytics_service.track_error(
            "Database connection failed", "critical", "user123"
        )

        analytics_service.db.error_logs.insert_one.assert_called_once()
        call_args = analytics_service.db.error_logs.insert_one.call_args[0][0]
        assert call_args["error_message"] == "Database connection failed"
        assert call_args["severity"] == "critical"
        assert call_args["user_id"] == "user123"
        assert "timestamp" in call_args

    @pytest.mark.asyncio
    async def test_get_api_performance_metrics(self, analytics_service):
        """API performance metrics get testi"""
        mock_cursor = Mock()
        mock_cursor.to_list = AsyncMock(
            return_value=[
                {"endpoint": "/api/v1/jobs", "avg_duration": 150.5, "count": 100},
                {"endpoint": "/api/v1/search", "avg_duration": 200.0, "count": 50},
            ]
        )
        analytics_service.db.performance_metrics.aggregate = Mock(
            return_value=mock_cursor
        )

        result = await analytics_service.get_api_performance_metrics(days=7)

        assert isinstance(result, list)
        assert len(result) == 2
        assert result[0]["endpoint"] == "/api/v1/jobs"
        assert result[0]["avg_duration"] == 150.5
        analytics_service.db.performance_metrics.aggregate.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_user_activity_summary(self, analytics_service):
        """User activity summary get testi"""
        mock_cursor = Mock()
        mock_cursor.to_list = AsyncMock(
            return_value=[
                {"action": "search", "count": 150},
                {"action": "view_job", "count": 75},
                {"action": "apply", "count": 25},
            ]
        )
        analytics_service.db.user_activities.aggregate = Mock(return_value=mock_cursor)

        result = await analytics_service.get_user_activity_summary(days=7)

        assert isinstance(result, list)
        assert len(result) == 3
        assert result[0]["action"] == "search"
        assert result[0]["count"] == 150
        analytics_service.db.user_activities.aggregate.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_popular_jobs(self, analytics_service):
        """Popular jobs get testi"""
        mock_cursor = Mock()
        mock_cursor.to_list = AsyncMock(
            return_value=[
                {"job_id": "job123", "view_count": 100},
                {"job_id": "job456", "view_count": 75},
                {"job_id": "job789", "view_count": 50},
            ]
        )
        analytics_service.db.job_views.aggregate = Mock(return_value=mock_cursor)

        result = await analytics_service.get_popular_jobs(limit=10, days=7)

        assert isinstance(result, list)
        assert len(result) == 3
        assert result[0]["job_id"] == "job123"
        assert result[0]["view_count"] == 100
        analytics_service.db.job_views.aggregate.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_popular_search_queries(self, analytics_service):
        """Popular search queries get testi"""
        mock_cursor = Mock()
        mock_cursor.to_list = AsyncMock(
            return_value=[
                {"query": "python developer", "count": 50},
                {"query": "react developer", "count": 30},
                {"query": "remote jobs", "count": 25},
            ]
        )
        analytics_service.db.search_queries.aggregate = Mock(return_value=mock_cursor)

        result = await analytics_service.get_popular_search_queries(limit=10, days=7)

        assert isinstance(result, list)
        assert len(result) == 3
        assert result[0]["query"] == "python developer"
        assert result[0]["count"] == 50
        analytics_service.db.search_queries.aggregate.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_error_summary(self, analytics_service):
        """Error summary get testi"""
        mock_cursor = Mock()
        mock_cursor.to_list = AsyncMock(
            return_value=[
                {"severity": "error", "count": 10},
                {"severity": "warning", "count": 5},
                {"severity": "critical", "count": 2},
            ]
        )
        analytics_service.db.error_logs.aggregate = Mock(return_value=mock_cursor)

        result = await analytics_service.get_error_summary(days=7)

        assert isinstance(result, list)
        assert len(result) == 3
        assert result[0]["severity"] == "error"
        assert result[0]["count"] == 10
        analytics_service.db.error_logs.aggregate.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_performance_dashboard_data(self, analytics_service):
        """Performance dashboard data get testi"""
        # Mock all the individual methods
        analytics_service.get_api_performance_metrics = AsyncMock(
            return_value=[
                {"endpoint": "/api/v1/jobs", "avg_duration": 150.5, "count": 100}
            ]
        )
        analytics_service.get_user_activity_summary = AsyncMock(
            return_value=[{"action": "search", "count": 150}]
        )
        analytics_service.get_popular_jobs = AsyncMock(
            return_value=[{"job_id": "job123", "view_count": 100}]
        )
        analytics_service.get_popular_search_queries = AsyncMock(
            return_value=[{"query": "python developer", "count": 50}]
        )
        analytics_service.get_error_summary = AsyncMock(
            return_value=[{"severity": "error", "count": 10}]
        )

        result = await analytics_service.get_performance_dashboard_data(days=7)

        assert isinstance(result, dict)
        assert "api_performance" in result
        assert "user_activity" in result
        assert "popular_jobs" in result
        assert "popular_queries" in result
        assert "error_summary" in result
        assert "generated_at" in result

    @pytest.mark.asyncio
    async def test_get_cached_metrics(self, analytics_service):
        """Cached metrics get testi"""
        cache_key = "api_performance_7"
        cached_data = [{"endpoint": "/api/v1/jobs", "avg_duration": 150.5}]
        analytics_service.metrics_cache[cache_key] = {
            "data": cached_data,
            "timestamp": datetime.utcnow(),
        }

        result = await analytics_service.get_cached_metrics(cache_key)

        assert result == cached_data

    @pytest.mark.asyncio
    async def test_get_cached_metrics_expired(self, analytics_service):
        """Expired cached metrics testi"""
        cache_key = "api_performance_7"
        analytics_service.metrics_cache[cache_key] = {
            "data": [],
            "timestamp": datetime.utcnow() - timedelta(hours=2),  # Expired
        }

        result = await analytics_service.get_cached_metrics(cache_key)

        assert result is None

    @pytest.mark.asyncio
    async def test_set_cached_metrics(self, analytics_service):
        """Cached metrics set testi"""
        cache_key = "api_performance_7"
        data = [{"endpoint": "/api/v1/jobs", "avg_duration": 150.5}]

        await analytics_service.set_cached_metrics(cache_key, data)

        assert cache_key in analytics_service.metrics_cache
        assert analytics_service.metrics_cache[cache_key]["data"] == data
        assert "timestamp" in analytics_service.metrics_cache[cache_key]

    @pytest.mark.asyncio
    async def test_clear_cache(self, analytics_service):
        """Cache temizleme testi"""
        analytics_service.metrics_cache = {
            "key1": {"data": [], "timestamp": datetime.utcnow()},
            "key2": {"data": [], "timestamp": datetime.utcnow()},
        }

        await analytics_service.clear_cache()

        assert len(analytics_service.metrics_cache) == 0

    @pytest.mark.asyncio
    async def test_get_system_health_metrics(self, analytics_service):
        """System health metrics get testi"""
        # Mock database operations
        analytics_service.db.performance_metrics.count_documents = AsyncMock(
            return_value=1000
        )
        analytics_service.db.user_activities.count_documents = AsyncMock(
            return_value=500
        )
        analytics_service.db.error_logs.count_documents = AsyncMock(return_value=10)

        result = await analytics_service.get_system_health_metrics()

        assert isinstance(result, dict)
        assert "total_api_calls" in result
        assert "total_user_activities" in result
        assert "total_errors" in result
        assert "error_rate" in result
        assert result["total_api_calls"] == 1000
        assert result["total_user_activities"] == 500
        assert result["total_errors"] == 10
        assert result["error_rate"] == 0.01  # 10/1000

    def test_service_methods_exist(self, analytics_service):
        """Service metodlarının varlığını test et"""
        required_methods = [
            "track_api_call",
            "track_user_activity",
            "track_job_view",
            "track_search_query",
            "track_error",
            "get_api_performance_metrics",
            "get_user_activity_summary",
            "get_popular_jobs",
            "get_popular_search_queries",
            "get_error_summary",
            "get_performance_dashboard_data",
            "get_cached_metrics",
            "set_cached_metrics",
            "clear_cache",
            "get_system_health_metrics",
        ]

        for method in required_methods:
            assert hasattr(analytics_service, method)
            assert callable(getattr(analytics_service, method))

    @pytest.mark.asyncio
    async def test_service_integration(self, analytics_service):
        """Service integration testi"""
        # Test full analytics workflow

        # Track various metrics
        await analytics_service.track_api_call("/api/v1/jobs", 150.5, 200)
        await analytics_service.track_user_activity(
            "user123", "search", {"query": "python"}
        )
        await analytics_service.track_job_view("job123", "user123")
        await analytics_service.track_search_query("python developer", 25, "user123")
        await analytics_service.track_error("Test error", "warning", "user123")

        # Mock dashboard data generation
        analytics_service.get_api_performance_metrics = AsyncMock(return_value=[])
        analytics_service.get_user_activity_summary = AsyncMock(return_value=[])
        analytics_service.get_popular_jobs = AsyncMock(return_value=[])
        analytics_service.get_popular_search_queries = AsyncMock(return_value=[])
        analytics_service.get_error_summary = AsyncMock(return_value=[])

        dashboard_data = await analytics_service.get_performance_dashboard_data()
        assert isinstance(dashboard_data, dict)
        assert "api_performance" in dashboard_data
        assert "user_activity" in dashboard_data
        assert "popular_jobs" in dashboard_data
        assert "popular_queries" in dashboard_data
        assert "error_summary" in dashboard_data
