import time
import logging
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

logger = logging.getLogger(__name__)


class PerformanceMonitoringMiddleware(BaseHTTPMiddleware):
    """
    Middleware for monitoring API performance and response times.
    """

    def __init__(self, app: ASGIApp):
        super().__init__(app)
        self.slow_query_threshold = 1.0  # 1 second
        self.performance_stats = {
            "total_requests": 0,
            "slow_requests": 0,
            "average_response_time": 0.0,
            "total_response_time": 0.0
        }

    async def dispatch(self, request: Request, call_next):
        # Record start time
        start_time = time.time()
        
        # Process the request
        response = await call_next(request)
        
        # Calculate response time
        process_time = time.time() - start_time
        
        # Update performance stats
        self.performance_stats["total_requests"] += 1
        self.performance_stats["total_response_time"] += process_time
        self.performance_stats["average_response_time"] = (
            self.performance_stats["total_response_time"] / 
            self.performance_stats["total_requests"]
        )
        
        # Add response time header
        response.headers["X-Response-Time"] = f"{process_time:.3f}s"
        response.headers["X-Process-Time"] = f"{process_time * 1000:.2f}ms"
        
        # Log slow requests
        if process_time > self.slow_query_threshold:
            self.performance_stats["slow_requests"] += 1
            logger.warning(
                f"🐌 Slow request detected: {request.method} {request.url.path} "
                f"took {process_time:.3f}s from {request.client.host}"
            )
        
        # Log performance metrics for high-traffic endpoints
        if request.url.path in ["/api/v1/jobs/search", "/api/v1/jobs/", "/api/v1/jobs/quick-search-count"]:
            logger.info(
                f"📊 Performance: {request.method} {request.url.path} "
                f"took {process_time:.3f}s (avg: {self.performance_stats['average_response_time']:.3f}s)"
            )
        
        return response

    def get_performance_stats(self):
        """Get current performance statistics."""
        return {
            **self.performance_stats,
            "slow_request_percentage": (
                (self.performance_stats["slow_requests"] / 
                 max(self.performance_stats["total_requests"], 1)) * 100
            )
        }


def initialize_performance_monitoring(app: ASGIApp) -> PerformanceMonitoringMiddleware:
    """Initialize performance monitoring middleware."""
    return PerformanceMonitoringMiddleware(app) 