import time
import logging
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

try:
    from config.sentry_config import start_transaction, set_tag, capture_exception
except ImportError:
    # Mock functions if sentry config is not available
    def start_transaction(name, operation):
        return None
    def set_tag(key, value):
        pass
    def capture_exception(error, context=None):
        pass

logger = logging.getLogger(__name__)

class PerformanceMiddleware(BaseHTTPMiddleware):
    """API performansını izleyen middleware"""
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
        self.slow_request_threshold = 1.0  # 1 saniye
        self.critical_request_threshold = 5.0  # 5 saniye
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.time()
        
        # Sentry transaction başlat
        transaction = start_transaction(
            name=f"{request.method} {request.url.path}",
            operation="http.server"
        )
        
        try:
            # Request context'ini ayarla
            if transaction:
                set_tag("http.method", request.method)
                set_tag("http.url", str(request.url))
                set_tag("http.route", request.url.path)
            
            # Response'u al
            response = await call_next(request)
            
            # Response time hesapla
            response_time = time.time() - start_time
            
            # Status code'u ayarla
            if transaction:
                set_tag("http.status_code", response.status_code)
            
            # Performans logları
            self.log_performance(request, response, response_time)
            
            # Yavaş request'leri uyar
            if response_time > self.critical_request_threshold:
                logger.warning(
                    f"Critical slow request: {request.method} {request.url.path} "
                    f"took {response_time:.2f}s (status: {response.status_code})"
                )
                if transaction:
                    set_tag("performance.slow", "critical")
                    
            elif response_time > self.slow_request_threshold:
                logger.info(
                    f"Slow request: {request.method} {request.url.path} "
                    f"took {response_time:.2f}s (status: {response.status_code})"
                )
                if transaction:
                    set_tag("performance.slow", "warning")
            
            return response
            
        except Exception as e:
            # Hata durumunda
            response_time = time.time() - start_time
            
            logger.error(
                f"Request failed: {request.method} {request.url.path} "
                f"took {response_time:.2f}s - Error: {str(e)}"
            )
            
            if transaction:
                set_tag("error", "true")
                set_tag("error.type", type(e).__name__)
            
            # Sentry'ye gönder
            capture_exception(e, {
                "request_method": request.method,
                "request_url": str(request.url),
                "response_time": response_time,
            })
            
            raise
            
        finally:
            # Transaction'ı bitir
            if transaction:
                transaction.finish()
    
    def log_performance(self, request: Request, response: Response, response_time: float):
        """Performans metriklerini logla"""
        
        # Endpoint'e göre farklı log seviyeleri
        endpoint = request.url.path
        
        # Kritik endpoint'ler için detaylı log
        critical_endpoints = [
            '/api/jobs/search',
            '/api/jobs/apply',
            '/api/user/profile',
            '/api/admin/',
        ]
        
        if any(critical in endpoint for critical in critical_endpoints):
            logger.info(
                f"API Performance - {request.method} {endpoint}: "
                f"{response_time:.3f}s (status: {response.status_code})"
            )
        
        # Genel endpoint'ler için sadece yavaş olanları logla
        elif response_time > self.slow_request_threshold:
            logger.info(
                f"Slow API - {request.method} {endpoint}: "
                f"{response_time:.3f}s (status: {response.status_code})"
            )

class DatabasePerformanceMiddleware:
    """Database performansını izleyen middleware"""
    
    def __init__(self):
        self.slow_query_threshold = 0.5  # 500ms
        self.critical_query_threshold = 2.0  # 2 saniye
    
    def track_query(self, query: str, execution_time: float, success: bool = True):
        """Database query performansını izle"""
        
        if execution_time > self.critical_query_threshold:
            logger.warning(
                f"Critical slow database query: {execution_time:.3f}s - {query[:100]}..."
            )
            set_tag("db.slow", "critical")
            
        elif execution_time > self.slow_query_threshold:
            logger.info(
                f"Slow database query: {execution_time:.3f}s - {query[:100]}..."
            )
            set_tag("db.slow", "warning")
        
        # Sentry'ye gönder
        if success:
            set_tag("db.query.success", "true")
        else:
            set_tag("db.query.success", "false")
            set_tag("db.query.error", "true")

class CachePerformanceMiddleware:
    """Cache performansını izleyen middleware"""
    
    def __init__(self):
        self.slow_cache_threshold = 0.1  # 100ms
    
    def track_cache_operation(self, operation: str, key: str, execution_time: float, hit: bool = True):
        """Cache operasyon performansını izle"""
        
        if execution_time > self.slow_cache_threshold:
            logger.info(
                f"Slow cache {operation}: {execution_time:.3f}s - {key[:50]}..."
            )
            set_tag("cache.slow", "true")
        
        # Cache hit/miss oranını izle
        if hit:
            set_tag("cache.hit", "true")
        else:
            set_tag("cache.miss", "true")

# Global instance'lar
db_performance = DatabasePerformanceMiddleware()
cache_performance = CachePerformanceMiddleware() 