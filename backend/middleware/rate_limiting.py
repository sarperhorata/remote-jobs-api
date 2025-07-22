"""
Rate limiting middleware for API protection
"""
import time
import logging
from typing import Dict, Any, Optional
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from collections import defaultdict, deque
import asyncio

logger = logging.getLogger(__name__)

class RateLimiter:
    """Rate limiting implementation"""
    
    def __init__(self, max_requests: int = 100, window_seconds: int = 3600):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests = defaultdict(deque)
    
    def is_allowed(self, key: str) -> bool:
        """Check if request is allowed"""
        now = time.time()
        
        # Clean old requests
        while self.requests[key] and self.requests[key][0] < now - self.window_seconds:
            self.requests[key].popleft()
        
        # Check if under limit
        if len(self.requests[key]) < self.max_requests:
            self.requests[key].append(now)
            return True
        
        return False
    
    def get_remaining_requests(self, key: str) -> int:
        """Get remaining requests for a key"""
        now = time.time()
        
        # Clean old requests
        while self.requests[key] and self.requests[key][0] < now - self.window_seconds:
            self.requests[key].popleft()
        
        return max(0, self.max_requests - len(self.requests[key]))
    
    def get_reset_time(self, key: str) -> Optional[float]:
        """Get reset time for a key"""
        if not self.requests[key]:
            return None
        
        return self.requests[key][0] + self.window_seconds

class RateLimitingMiddleware:
    """Rate limiting middleware for FastAPI"""
    
    def __init__(self):
        # Different rate limits for different endpoints
        self.rate_limits = {
            # Auth endpoints - stricter limits
            "/auth/login": RateLimiter(max_requests=5, window_seconds=300),  # 5 attempts per 5 minutes
            "/auth/register": RateLimiter(max_requests=3, window_seconds=3600),  # 3 registrations per hour
            "/auth/forgot-password": RateLimiter(max_requests=3, window_seconds=3600),  # 3 attempts per hour
            
            # Job search endpoints - moderate limits
            "/jobs/search": RateLimiter(max_requests=100, window_seconds=3600),  # 100 searches per hour
            "/jobs/": RateLimiter(max_requests=200, window_seconds=3600),  # 200 requests per hour
            
            # Admin endpoints - very strict limits
            "/admin/": RateLimiter(max_requests=10, window_seconds=300),  # 10 requests per 5 minutes
            
            # Default rate limit
            "default": RateLimiter(max_requests=1000, window_seconds=3600),  # 1000 requests per hour
        }
        
        # IP-based rate limiting
        self.ip_rate_limits = defaultdict(lambda: RateLimiter(max_requests=100, window_seconds=3600))
        
        # User-based rate limiting (when authenticated)
        self.user_rate_limits = defaultdict(lambda: RateLimiter(max_requests=500, window_seconds=3600))
    
    async def __call__(self, request: Request, call_next):
        """Apply rate limiting to requests"""
        try:
            # Get client IP
            client_ip = self._get_client_ip(request)
            
            # Get user ID if authenticated
            user_id = self._get_user_id(request)
            
            # Check rate limits
            rate_limit_key = self._get_rate_limit_key(request)
            rate_limiter = self.rate_limits.get(rate_limit_key, self.rate_limits["default"])
            
            # Check IP-based rate limiting
            if not self.ip_rate_limits[client_ip].is_allowed():
                return self._rate_limit_response("IP rate limit exceeded", client_ip)
            
            # Check endpoint-specific rate limiting
            if not rate_limiter.is_allowed(client_ip):
                return self._rate_limit_response("Endpoint rate limit exceeded", client_ip)
            
            # Check user-based rate limiting (if authenticated)
            if user_id:
                user_limiter = self.user_rate_limits[user_id]
                if not user_limiter.is_allowed():
                    return self._rate_limit_response("User rate limit exceeded", user_id)
            
            # Add rate limit headers to response
            response = await call_next(request)
            self._add_rate_limit_headers(response, rate_limiter, client_ip, user_id)
            
            return response
            
        except Exception as e:
            logger.error(f"Rate limiting error: {e}")
            # Continue without rate limiting if there's an error
            return await call_next(request)
    
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
    
    def _get_user_id(self, request: Request) -> Optional[str]:
        """Get user ID from request (if authenticated)"""
        try:
            # Try to get user from request state
            if hasattr(request.state, "user") and request.state.user:
                return str(request.state.user.get("_id", ""))
            
            # Try to get from authorization header
            auth_header = request.headers.get("Authorization")
            if auth_header and auth_header.startswith("Bearer "):
                # In a real implementation, you would decode the JWT here
                # For now, we'll just return None
                return None
            
            return None
        except Exception:
            return None
    
    def _get_rate_limit_key(self, request: Request) -> str:
        """Get rate limit key based on endpoint"""
        path = request.url.path
        
        # Check for exact matches first
        if path in self.rate_limits:
            return path
        
        # Check for prefix matches
        for prefix in self.rate_limits:
            if path.startswith(prefix):
                return prefix
        
        return "default"
    
    def _rate_limit_response(self, message: str, identifier: str) -> JSONResponse:
        """Create rate limit exceeded response"""
        logger.warning(f"Rate limit exceeded for {identifier}: {message}")
        
        return JSONResponse(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            content={
                "detail": message,
                "retry_after": 60,  # Retry after 1 minute
                "identifier": identifier
            },
            headers={
                "Retry-After": "60",
                "X-RateLimit-Reset": str(int(time.time()) + 60)
            }
        )
    
    def _add_rate_limit_headers(self, response, rate_limiter: RateLimiter, client_ip: str, user_id: Optional[str]):
        """Add rate limit headers to response"""
        try:
            # Get remaining requests
            remaining = rate_limiter.get_remaining_requests(client_ip)
            reset_time = rate_limiter.get_reset_time(client_ip)
            
            # Add headers
            response.headers["X-RateLimit-Limit"] = str(rate_limiter.max_requests)
            response.headers["X-RateLimit-Remaining"] = str(remaining)
            
            if reset_time:
                response.headers["X-RateLimit-Reset"] = str(int(reset_time))
            
            # Add user-specific headers if authenticated
            if user_id:
                user_limiter = self.user_rate_limits[user_id]
                user_remaining = user_limiter.get_remaining_requests()
                response.headers["X-User-RateLimit-Remaining"] = str(user_remaining)
                
        except Exception as e:
            logger.warning(f"Could not add rate limit headers: {e}")

# Create singleton instance
rate_limiter = RateLimitingMiddleware()

# Additional rate limiting utilities
class BruteForceProtection:
    """Brute force protection for sensitive endpoints"""
    
    def __init__(self):
        self.failed_attempts = defaultdict(list)
        self.blocked_ips = {}
        self.max_failed_attempts = 5
        self.block_duration = 900  # 15 minutes
    
    def record_failed_attempt(self, identifier: str, ip: str):
        """Record a failed attempt"""
        now = time.time()
        
        # Clean old attempts
        self.failed_attempts[identifier] = [
            attempt_time for attempt_time in self.failed_attempts[identifier]
            if now - attempt_time < self.block_duration
        ]
        
        # Add new attempt
        self.failed_attempts[identifier].append(now)
        
        # Check if should be blocked
        if len(self.failed_attempts[identifier]) >= self.max_failed_attempts:
            self.blocked_ips[identifier] = now + self.block_duration
            logger.warning(f"IP {identifier} blocked due to brute force attempts")
    
    def is_blocked(self, identifier: str) -> bool:
        """Check if identifier is blocked"""
        if identifier not in self.blocked_ips:
            return False
        
        # Check if block has expired
        if time.time() > self.blocked_ips[identifier]:
            del self.blocked_ips[identifier]
            return False
        
        return True
    
    def get_block_remaining(self, identifier: str) -> int:
        """Get remaining block time in seconds"""
        if identifier not in self.blocked_ips:
            return 0
        
        remaining = self.blocked_ips[identifier] - time.time()
        return max(0, int(remaining))
    
    def record_successful_attempt(self, identifier: str):
        """Record a successful attempt (clear failed attempts)"""
        if identifier in self.failed_attempts:
            del self.failed_attempts[identifier]
        
        if identifier in self.blocked_ips:
            del self.blocked_ips[identifier]

# Create singleton instance
brute_force_protection = BruteForceProtection()