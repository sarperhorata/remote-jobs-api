"""
Rate Limiting Middleware
Handles rate limiting for API endpoints
"""

import logging
import time
from typing import Dict, Optional, Tuple
from datetime import datetime, UTC
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)


class RateLimiter:
    """Rate limiter implementation"""
    
    def __init__(self, requests_per_minute: int = 60, requests_per_hour: int = 1000):
        self.requests_per_minute = requests_per_minute
        self.requests_per_hour = requests_per_hour
        self.minute_requests: Dict[str, list] = {}
        self.hour_requests: Dict[str, list] = {}
    
    def _get_client_ip(self, request: Request) -> str:
        """Get client IP address"""
        # Check for forwarded headers
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        # Fallback to direct IP
        return request.client.host if request.client else "unknown"
    
    def _cleanup_old_requests(self, requests_list: list, window_seconds: int):
        """Remove old requests outside the time window"""
        current_time = time.time()
        cutoff_time = current_time - window_seconds
        
        # Remove requests older than the window
        while requests_list and requests_list[0] < cutoff_time:
            requests_list.pop(0)
    
    def _check_rate_limit(self, client_ip: str) -> Tuple[bool, Optional[str]]:
        """Check if request is within rate limits"""
        current_time = time.time()
        
        # Initialize request lists if not exists
        if client_ip not in self.minute_requests:
            self.minute_requests[client_ip] = []
        if client_ip not in self.hour_requests:
            self.hour_requests[client_ip] = []
        
        # Cleanup old requests
        self._cleanup_old_requests(self.minute_requests[client_ip], 60)
        self._cleanup_old_requests(self.hour_requests[client_ip], 3600)
        
        # Check minute limit
        if len(self.minute_requests[client_ip]) >= self.requests_per_minute:
            return False, "Rate limit exceeded: too many requests per minute"
        
        # Check hour limit
        if len(self.hour_requests[client_ip]) >= self.requests_per_hour:
            return False, "Rate limit exceeded: too many requests per hour"
        
        # Add current request
        self.minute_requests[client_ip].append(current_time)
        self.hour_requests[client_ip].append(current_time)
        
        return True, None
    
    def _get_retry_after(self, client_ip: str) -> int:
        """Get retry after seconds"""
        if client_ip in self.minute_requests and self.minute_requests[client_ip]:
            oldest_request = self.minute_requests[client_ip][0]
            return max(1, int(60 - (time.time() - oldest_request)))
        return 60
    
    async def __call__(self, request: Request, call_next):
        """Rate limiting middleware"""
        try:
            # Skip rate limiting for certain endpoints
            if self._should_skip_rate_limit(request.url.path):
                return await call_next(request)
            
            client_ip = self._get_client_ip(request)
            is_allowed, error_message = self._check_rate_limit(client_ip)
            
            if not is_allowed:
                retry_after = self._get_retry_after(client_ip)
                
                logger.warning(f"Rate limit exceeded for {client_ip}: {error_message}")
                
                return JSONResponse(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    content={
                        "error": "Rate limit exceeded",
                        "message": error_message,
                        "retry_after": retry_after,
                        "timestamp": datetime.now(UTC).isoformat()
                    },
                    headers={
                        "Retry-After": str(retry_after),
                        "X-RateLimit-Limit": str(self.requests_per_minute),
                        "X-RateLimit-Remaining": "0",
                        "X-RateLimit-Reset": str(int(time.time() + retry_after))
                    }
                )
            
            # Add rate limit headers to response
            response = await call_next(request)
            
            # Calculate remaining requests
            minute_remaining = max(0, self.requests_per_minute - len(self.minute_requests.get(client_ip, [])))
            hour_remaining = max(0, self.requests_per_hour - len(self.hour_requests.get(client_ip, [])))
            
            response.headers["X-RateLimit-Limit"] = str(self.requests_per_minute)
            response.headers["X-RateLimit-Remaining"] = str(minute_remaining)
            response.headers["X-RateLimit-Reset"] = str(int(time.time() + 60))
            response.headers["X-RateLimit-Hourly-Limit"] = str(self.requests_per_hour)
            response.headers["X-RateLimit-Hourly-Remaining"] = str(hour_remaining)
            
            return response
            
        except Exception as e:
            logger.error(f"Rate limiting error: {e}")
            # Continue without rate limiting on error
            return await call_next(request)
    
    def _should_skip_rate_limit(self, path: str) -> bool:
        """Check if rate limiting should be skipped for this path"""
        skip_paths = [
            "/health",
            "/docs",
            "/redoc",
            "/openapi.json",
            "/favicon.ico"
        ]
        
        return any(path.startswith(skip_path) for skip_path in skip_paths)


class TokenBucketRateLimiter:
    """Token bucket rate limiter implementation"""
    
    def __init__(self, capacity: int = 100, refill_rate: float = 1.0):
        self.capacity = capacity
        self.refill_rate = refill_rate  # tokens per second
        self.tokens: Dict[str, float] = {}
        self.last_refill: Dict[str, float] = {}
    
    def _get_client_ip(self, request: Request) -> str:
        """Get client IP address"""
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        return request.client.host if request.client else "unknown"
    
    def _refill_tokens(self, client_ip: str):
        """Refill tokens for client"""
        current_time = time.time()
        
        if client_ip not in self.tokens:
            self.tokens[client_ip] = self.capacity
            self.last_refill[client_ip] = current_time
            return
        
        # Calculate time since last refill
        time_passed = current_time - self.last_refill[client_ip]
        
        # Calculate tokens to add
        tokens_to_add = time_passed * self.refill_rate
        
        # Refill tokens (don't exceed capacity)
        self.tokens[client_ip] = min(self.capacity, self.tokens[client_ip] + tokens_to_add)
        self.last_refill[client_ip] = current_time
    
    def _consume_token(self, client_ip: str) -> bool:
        """Consume a token if available"""
        self._refill_tokens(client_ip)
        
        if self.tokens[client_ip] >= 1:
            self.tokens[client_ip] -= 1
            return True
        
        return False
    
    async def __call__(self, request: Request, call_next):
        """Token bucket rate limiting middleware"""
        try:
            if self._should_skip_rate_limit(request.url.path):
                return await call_next(request)
            
            client_ip = self._get_client_ip(request)
            
            if not self._consume_token(client_ip):
                retry_after = int(1 / self.refill_rate)
                
                logger.warning(f"Token bucket rate limit exceeded for {client_ip}")
                
                return JSONResponse(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    content={
                        "error": "Rate limit exceeded",
                        "message": "Too many requests, please try again later",
                        "retry_after": retry_after,
                        "timestamp": datetime.now(UTC).isoformat()
                    },
                    headers={
                        "Retry-After": str(retry_after),
                        "X-RateLimit-Limit": str(self.capacity),
                        "X-RateLimit-Remaining": "0"
                    }
                )
            
            response = await call_next(request)
            
            # Add rate limit headers
            remaining_tokens = int(self.tokens[client_ip])
            response.headers["X-RateLimit-Limit"] = str(self.capacity)
            response.headers["X-RateLimit-Remaining"] = str(remaining_tokens)
            
            return response
            
        except Exception as e:
            logger.error(f"Token bucket rate limiting error: {e}")
            return await call_next(request)
    
    def _should_skip_rate_limit(self, path: str) -> bool:
        """Check if rate limiting should be skipped for this path"""
        skip_paths = [
            "/health",
            "/docs",
            "/redoc",
            "/openapi.json",
            "/favicon.ico"
        ]
        
        return any(path.startswith(skip_path) for skip_path in skip_paths)


# Global rate limiter instances
rate_limiter = RateLimiter(requests_per_minute=60, requests_per_hour=1000)
token_bucket_limiter = TokenBucketRateLimiter(capacity=100, refill_rate=1.0)


def get_rate_limiter() -> RateLimiter:
    """Get rate limiter instance"""
    return rate_limiter


def get_token_bucket_limiter() -> TokenBucketRateLimiter:
    """Get token bucket rate limiter instance"""
    return token_bucket_limiter 