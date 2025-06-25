import pytest
from unittest.mock import Mock, AsyncMock
from datetime import datetime
from backend.services.performance_analytics_service import PerformanceAnalyticsService

class TestPerformanceAnalyticsService:
    """Test performance analytics service."""
    
    @pytest.fixture
    def mock_db(self):
        db = Mock()
        db.performance_metrics = AsyncMock()
        return db
    
    @pytest.fixture
    def analytics_service(self, mock_db):
        return PerformanceAnalyticsService(mock_db)
    
    @pytest.mark.asyncio
    async def test_track_api_call(self, analytics_service, mock_db):
        """Test tracking API calls."""
        await analytics_service.track_api_call("/api/jobs", 250.5, 200)
        
        mock_db.performance_metrics.insert_one.assert_called_once()
        call_args = mock_db.performance_metrics.insert_one.call_args[0][0]
        assert call_args["endpoint"] == "/api/jobs"
        assert call_args["duration_ms"] == 250.5
        assert call_args["status_code"] == 200
    
    @pytest.mark.asyncio
    async def test_get_performance_summary(self, analytics_service, mock_db):
        """Test getting performance summary."""
        mock_results = [
            {
                "_id": "/api/jobs",
                "avg_duration": 200.5,
                "max_duration": 500.0,
                "min_duration": 100.0,
                "call_count": 150,
                "error_count": 5
            }
        ]
        
        mock_db.performance_metrics.aggregate.return_value.to_list.return_value = mock_results
        
        summary = await analytics_service.get_performance_summary()
        
        assert "endpoints" in summary
        assert "total_calls" in summary
        assert "total_errors" in summary
        assert summary["total_calls"] == 150
        assert summary["total_errors"] == 5
    
    def test_measure_time_context_manager(self, analytics_service):
        """Test time measurement context manager."""
        measurer = analytics_service.measure_time()
        
        with measurer:
            # Simulate some work
            import time
            time.sleep(0.001)  # 1ms
        
        assert hasattr(measurer, "duration_ms")
        assert measurer.duration_ms > 0
    
    @pytest.mark.asyncio
    async def test_analyze_slow_queries(self, analytics_service, mock_db):
        """Test slow query analysis."""
        mock_slow_queries = [
            {
                "_id": "/api/heavy-operation",
                "avg_duration": 2500.0,
                "max_duration": 5000.0,
                "count": 10
            }
        ]
        
        mock_db.performance_metrics.aggregate.return_value.to_list.return_value = mock_slow_queries
        
        slow_queries = await analytics_service.analyze_slow_queries()
        
        assert len(slow_queries) == 1
        assert slow_queries[0]["_id"] == "/api/heavy-operation"
        assert slow_queries[0]["avg_duration"] == 2500.0
    
    def test_service_initialization(self, mock_db):
        """Test service initialization."""
        service = PerformanceAnalyticsService(mock_db)
        assert service.db == mock_db
        assert service.metrics_cache == {}
