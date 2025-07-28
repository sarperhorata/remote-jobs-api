import logging
import time
from datetime import datetime, timedelta
from typing import Any, Dict, List

from motor.motor_asyncio import AsyncIOMotorDatabase

logger = logging.getLogger(__name__)


class PerformanceAnalyticsService:
    """Service for tracking and analyzing application performance metrics."""

    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.metrics_cache = {}

    async def track_api_call(self, endpoint: str, duration_ms: float, status_code: int):
        """Track API call performance."""
        try:
            metric = {
                "endpoint": endpoint,
                "duration_ms": duration_ms,
                "status_code": status_code,
                "timestamp": datetime.utcnow(),
                "date": datetime.utcnow().date().isoformat(),
            }
            await self.db.performance_metrics.insert_one(metric)
        except Exception as e:
            logger.error(f"Error tracking API call: {e}")

    async def get_performance_summary(self) -> Dict[str, Any]:
        """Get performance summary for the last 24 hours."""
        try:
            since = datetime.utcnow() - timedelta(hours=24)

            pipeline = [
                {"$match": {"timestamp": {"$gte": since}}},
                {
                    "$group": {
                        "_id": "$endpoint",
                        "avg_duration": {"$avg": "$duration_ms"},
                        "max_duration": {"$max": "$duration_ms"},
                        "min_duration": {"$min": "$duration_ms"},
                        "call_count": {"$sum": 1},
                        "error_count": {
                            "$sum": {"$cond": [{"$gte": ["$status_code", 400]}, 1, 0]}
                        },
                    }
                },
                {"$sort": {"call_count": -1}},
            ]

            results = await self.db.performance_metrics.aggregate(pipeline).to_list(
                None
            )

            return {
                "endpoints": results,
                "total_calls": sum(r["call_count"] for r in results),
                "total_errors": sum(r["error_count"] for r in results),
                "period": "24 hours",
            }
        except Exception as e:
            logger.error(f"Error getting performance summary: {e}")
            return {}

    def measure_time(self):
        """Context manager for measuring execution time."""

        class TimeMeasurer:
            def __init__(self, service):
                self.service = service
                self.start_time = None

            def __enter__(self):
                self.start_time = time.time()
                return self

            def __exit__(self, exc_type, exc_val, exc_tb):
                if self.start_time:
                    duration = (time.time() - self.start_time) * 1000
                    self.duration_ms = duration

        return TimeMeasurer(self)

    async def analyze_slow_queries(self) -> List[Dict[str, Any]]:
        """Analyze slow performing queries."""
        try:
            pipeline = [
                {"$match": {"duration_ms": {"$gte": 1000}}},  # Queries > 1 second
                {
                    "$group": {
                        "_id": "$endpoint",
                        "avg_duration": {"$avg": "$duration_ms"},
                        "max_duration": {"$max": "$duration_ms"},
                        "count": {"$sum": 1},
                    }
                },
                {"$sort": {"avg_duration": -1}},
            ]

            results = await self.db.performance_metrics.aggregate(pipeline).to_list(None)
            return results
        except Exception as e:
            logger.error(f"Error analyzing slow queries: {e}")
            return []

    async def track_user_activity(self, user_id: str, activity_type: str, data: Dict[str, Any] = None):
        """Track user activity for analytics."""
        try:
            activity = {
                "user_id": user_id,
                "activity_type": activity_type,
                "data": data or {},
                "timestamp": datetime.utcnow(),
                "date": datetime.utcnow().date().isoformat(),
            }
            await self.db.user_activities.insert_one(activity)
        except Exception as e:
            logger.error(f"Error tracking user activity: {e}")

    async def track_job_view(self, job_id: str, user_id: str = None):
        """Track job view activity."""
        await self.track_user_activity(
            user_id or "anonymous", 
            "job_view", 
            {"job_id": job_id}
        )

    async def track_search_query(self, query: str, user_id: str = None, results_count: int = 0):
        """Track search query activity."""
        await self.track_user_activity(
            user_id or "anonymous",
            "search_query",
            {"query": query, "results_count": results_count}
        )

    async def track_error(self, error_type: str, error_message: str, endpoint: str = None):
        """Track error occurrences."""
        try:
            error = {
                "error_type": error_type,
                "error_message": error_message,
                "endpoint": endpoint,
                "timestamp": datetime.utcnow(),
                "date": datetime.utcnow().date().isoformat(),
            }
            await self.db.error_logs.insert_one(error)
        except Exception as e:
            logger.error(f"Error tracking error: {e}")

    async def get_api_performance_metrics(self) -> Dict[str, Any]:
        """Get API performance metrics."""
        try:
            since = datetime.utcnow() - timedelta(hours=1)
            
            pipeline = [
                {"$match": {"timestamp": {"$gte": since}}},
                {
                    "$group": {
                        "_id": "$endpoint",
                        "avg_response_time": {"$avg": "$duration_ms"},
                        "total_requests": {"$sum": 1},
                        "error_rate": {
                            "$avg": {"$cond": [{"$gte": ["$status_code", 400]}, 1, 0]}
                        }
                    }
                }
            ]
            
            results = await self.db.performance_metrics.aggregate(pipeline).to_list(None)
            return {"metrics": results, "period": "1 hour"}
        except Exception as e:
            logger.error(f"Error getting API performance metrics: {e}")
            return {}

    async def get_user_activity_summary(self) -> Dict[str, Any]:
        """Get user activity summary."""
        try:
            since = datetime.utcnow() - timedelta(days=7)
            
            pipeline = [
                {"$match": {"timestamp": {"$gte": since}}},
                {
                    "$group": {
                        "_id": "$activity_type",
                        "count": {"$sum": 1},
                        "unique_users": {"$addToSet": "$user_id"}
                    }
                }
            ]
            
            results = await self.db.user_activities.aggregate(pipeline).to_list(None)
            
            summary = {}
            for result in results:
                summary[result["_id"]] = {
                    "count": result["count"],
                    "unique_users": len(result["unique_users"])
                }
            
            return summary
        except Exception as e:
            logger.error(f"Error getting user activity summary: {e}")
            return {}

    async def get_popular_jobs(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get most viewed jobs."""
        try:
            pipeline = [
                {"$match": {"activity_type": "job_view"}},
                {"$group": {"_id": "$data.job_id", "views": {"$sum": 1}}},
                {"$sort": {"views": -1}},
                {"$limit": limit}
            ]
            
            results = await self.db.user_activities.aggregate(pipeline).to_list(None)
            return results
        except Exception as e:
            logger.error(f"Error getting popular jobs: {e}")
            return []

    async def get_popular_search_queries(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get most popular search queries."""
        try:
            pipeline = [
                {"$match": {"activity_type": "search_query"}},
                {"$group": {"_id": "$data.query", "count": {"$sum": 1}}},
                {"$sort": {"count": -1}},
                {"$limit": limit}
            ]
            
            results = await self.db.user_activities.aggregate(pipeline).to_list(None)
            return results
        except Exception as e:
            logger.error(f"Error getting popular search queries: {e}")
            return []

    async def get_error_summary(self) -> Dict[str, Any]:
        """Get error summary."""
        try:
            since = datetime.utcnow() - timedelta(hours=24)
            
            pipeline = [
                {"$match": {"timestamp": {"$gte": since}}},
                {
                    "$group": {
                        "_id": "$error_type",
                        "count": {"$sum": 1},
                        "endpoints": {"$addToSet": "$endpoint"}
                    }
                },
                {"$sort": {"count": -1}}
            ]
            
            results = await self.db.error_logs.aggregate(pipeline).to_list(None)
            return {"errors": results, "period": "24 hours"}
        except Exception as e:
            logger.error(f"Error getting error summary: {e}")
            return {}

    async def get_performance_dashboard_data(self) -> Dict[str, Any]:
        """Get comprehensive performance dashboard data."""
        try:
            return {
                "api_metrics": await self.get_api_performance_metrics(),
                "user_activity": await self.get_user_activity_summary(),
                "popular_jobs": await self.get_popular_jobs(),
                "popular_queries": await self.get_popular_search_queries(),
                "error_summary": await self.get_error_summary(),
                "slow_queries": await self.analyze_slow_queries()
            }
        except Exception as e:
            logger.error(f"Error getting dashboard data: {e}")
            return {}

    async def get_cached_metrics(self, cache_key: str) -> Any:
        """Get cached metrics."""
        try:
            if cache_key in self.metrics_cache:
                cache_entry = self.metrics_cache[cache_key]
                if datetime.utcnow() - cache_entry["timestamp"] < timedelta(minutes=5):
                    return cache_entry["data"]
            return None
        except Exception as e:
            logger.error(f"Error getting cached metrics: {e}")
            return None

    async def set_cached_metrics(self, cache_key: str, data: Any):
        """Set cached metrics."""
        try:
            self.metrics_cache[cache_key] = {
                "data": data,
                "timestamp": datetime.utcnow()
            }
        except Exception as e:
            logger.error(f"Error setting cached metrics: {e}")

    async def clear_cache(self):
        """Clear metrics cache."""
        try:
            self.metrics_cache.clear()
        except Exception as e:
            logger.error(f"Error clearing cache: {e}")

    async def get_system_health_metrics(self) -> Dict[str, Any]:
        """Get system health metrics."""
        try:
            # Mock system health metrics
            return {
                "database_connections": 10,
                "memory_usage": "75%",
                "cpu_usage": "45%",
                "disk_usage": "60%",
                "uptime": "7 days",
                "last_backup": datetime.utcnow().isoformat()
            }
        except Exception as e:
            logger.error(f"Error getting system health metrics: {e}")
            return {}
                {"$limit": 10},
            ]

            return await self.db.performance_metrics.aggregate(pipeline).to_list(None)
        except Exception as e:
            logger.error(f"Error analyzing slow queries: {e}")
            return []
