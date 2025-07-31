"""
Rate Limiting Middleware
Handles rate limiting for API endpoints with special handling for cron jobs
"""

import time
import logging
from collections import defaultdict
from typing import Dict, Tuple, Optional
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)

class RateLimiter:
    def __init__(self):
        self.requests: Dict[str, list] = defaultdict(list)
        self.cron_ips = {
            "165.227.83.0/24",  # cron-job.org IP range
            "159.89.49.0/24",   # cron-job.org IP range
            "127.0.0.1",        # localhost
            "::1"               # localhost IPv6
        }
        
    def is_cron_request(self, request: Request) -> bool:
        """Check if request is from cron-job.org or local"""
        client_ip = request.client.host if request.client else "unknown"
        
        # Check if IP is in cron-job.org range
        for cron_ip in self.cron_ips:
            if self._ip_in_range(client_ip, cron_ip):
                return True
        
        # Check for cron-job.org user agent
        user_agent = request.headers.get("user-agent", "").lower()
        if "cron-job.org" in user_agent:
            return True
            
        # Check for cron token in query params or headers
        cron_token = request.query_params.get("token") or request.headers.get("x-api-key")
        if cron_token and cron_token in ["buzz2remote-cron-2024", "buzz2remote_cron_2024"]:
            return True
            
        return False
    
    def _ip_in_range(self, ip: str, ip_range: str) -> bool:
        """Check if IP is in range (simple implementation)"""
        if "/" not in ip_range:
            return ip == ip_range
        
        # Simple CIDR check
        base_ip = ip_range.split("/")[0]
        return ip == base_ip
    
    def check_rate_limit(
        self, 
        request: Request, 
        max_requests: int = 100, 
        window_seconds: int = 60,
        cron_max_requests: int = 10,
        cron_window_seconds: int = 300  # 5 minutes for cron jobs
    ) -> bool:
        """
        Check rate limit for request
        
        Args:
            request: FastAPI request object
            max_requests: Maximum requests per window for normal users
            window_seconds: Time window in seconds for normal users
            cron_max_requests: Maximum requests per window for cron jobs
            cron_window_seconds: Time window in seconds for cron jobs
        """
        client_ip = request.client.host if request.client else "unknown"
        current_time = time.time()
        
        # Use different limits for cron jobs
        if self.is_cron_request(request):
            max_req = cron_max_requests
            window = cron_window_seconds
            logger.info(f"Cron request detected from {client_ip}, using cron limits: {max_req}/{window}s")
        else:
            max_req = max_requests
            window = window_seconds
        
        # Clean old requests
        self.requests[client_ip] = [
            req_time for req_time in self.requests[client_ip]
            if current_time - req_time < window
        ]
        
        # Check if limit exceeded
        if len(self.requests[client_ip]) >= max_req:
            logger.warning(f"Rate limit exceeded for {client_ip}: {len(self.requests[client_ip])}/{max_req} requests in {window}s")
            return False
        
        # Add current request
        self.requests[client_ip].append(current_time)
        return True

# Global rate limiter instance
rate_limiter = RateLimiter()

def rate_limit_middleware(request: Request, call_next):
    """Rate limiting middleware"""
    
    # Skip rate limiting for certain endpoints
    skip_endpoints = [
        "/health",
        "/api/health", 
        "/api/v1/health",
        "/api/monitor/health",
        "/api/monitor/status"
    ]
    
    if any(request.url.path.endswith(endpoint) for endpoint in skip_endpoints):
        return call_next(request)
    
    # Check rate limit
    if not rate_limiter.check_rate_limit(request):
        return JSONResponse(
            status_code=429,
            content={
                "error": "Too Many Requests",
                "message": "Rate limit exceeded. Please try again later.",
                "retry_after": 60
            }
        )
    
    return call_next(request)

def get_rate_limiter() -> RateLimiter:
    """Get rate limiter instance"""
    return rate_limiter 