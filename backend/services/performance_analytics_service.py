import time
import logging
from typing import Dict, List, Any
from datetime import datetime, timedelta
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
                "date": datetime.utcnow().date().isoformat()
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
                {"$group": {
                    "_id": "$endpoint",
                    "avg_duration": {"$avg": "$duration_ms"},
                    "max_duration": {"$max": "$duration_ms"},
                    "min_duration": {"$min": "$duration_ms"},
                    "call_count": {"$sum": 1},
                    "error_count": {
                        "$sum": {"$cond": [{"$gte": ["$status_code", 400]}, 1, 0]}
                    }
                }},
                {"$sort": {"call_count": -1}}
            ]
            
            results = await self.db.performance_metrics.aggregate(pipeline).to_list(None)
            
            return {
                "endpoints": results,
                "total_calls": sum(r["call_count"] for r in results),
                "total_errors": sum(r["error_count"] for r in results),
                "period": "24 hours"
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
                {"$group": {
                    "_id": "$endpoint",
                    "avg_duration": {"$avg": "$duration_ms"},
                    "max_duration": {"$max": "$duration_ms"},
                    "count": {"$sum": 1}
                }},
                {"$sort": {"avg_duration": -1}},
                {"$limit": 10}
            ]
            
            return await self.db.performance_metrics.aggregate(pipeline).to_list(None)
        except Exception as e:
            logger.error(f"Error analyzing slow queries: {e}")
            return []
