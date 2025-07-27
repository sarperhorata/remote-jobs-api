"""
Rate Limiting Middleware
Implements comprehensive API rate limiting for production security
"""

from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
import logging
import os
from typing import Optional

logger = logging.getLogger(__name__)

# Rate limiter configuration
def get_client_id(request: Request) -> str:
    """
    Get client identifier for rate limiting
    Priority: API key > User ID > IP address
    """
    # Check for API key in headers
    api_key = request.headers.get("X-API-Key") or request.headers.get("Authorization")
    if api_key:
        return f"api:{api_key[:10]}..."  # Truncate for privacy
    
    # Check for authenticated user
    user_id = getattr(request.state, 'user_id', None)
    if user_id:
        return f"user:{user_id}"
    
    # Fall back to IP address
    return f"ip:{get_remote_address(request)}"

# Initialize limiter with custom key function
limiter = Limiter(
    key_func=get_client_id,
    default_limits=["100/minute", "1000/hour"],  # Default limits
    storage_uri=os.getenv("RATE_LIMIT_STORAGE", "memory://"),  # Can use Redis: redis://localhost:6379
    strategy="fixed-window"  # or "moving-window"
)

# Custom rate limit exceeded handler
async def custom_rate_limit_handler(request: Request, exc: RateLimitExceeded):
    """Custom handler for rate limit exceeded responses"""
    client_id = get_client_id(request)
    endpoint = request.url.path
    
    logger.warning(
        f"Rate limit exceeded for {client_id} on {endpoint}. "
        f"Limit: {exc.detail}"
    )
    
    response = JSONResponse(
        status_code=429,
        content={
            "error": "Rate limit exceeded",
            "message": "Too many requests. Please try again later.",
            "detail": exc.detail,
            "retry_after": getattr(exc, 'retry_after', 60),
            "endpoint": endpoint,
            "timestamp": None  # Will be added by error handler
        },
        headers={"Retry-After": str(getattr(exc, 'retry_after', 60))}
    )
    
    return response

def get_rate_limits():
    """Get rate limiting configuration"""
    return {
        # Public endpoints - more restrictive
        "public": {
            "jobs_search": "30/minute",
            "jobs_list": "50/minute", 
            "company_list": "20/minute",
            "health_check": "10/minute"
        },
        
        # Authenticated users - moderate limits
        "authenticated": {
            "jobs_search": "100/minute",
            "jobs_list": "200/minute",
            "applications": "20/minute",
            "profile_update": "5/minute",
            "file_upload": "3/minute"
        },
        
        # Premium users - higher limits
        "premium": {
            "jobs_search": "300/minute",
            "jobs_list": "500/minute",
            "applications": "50/minute",
            "ai_services": "20/minute",
            "analytics": "100/minute"
        },
        
        # Admin users - very high limits
        "admin": {
            "admin_actions": "1000/minute",
            "data_export": "10/minute",
            "bulk_operations": "5/minute"
        },
        
        # API keys - configurable limits
        "api_key": {
            "standard": "500/minute",
            "premium": "2000/minute", 
            "enterprise": "10000/minute"
        },
        
        # Critical endpoints - very restrictive
        "critical": {
            "auth_login": "5/minute",
            "auth_register": "3/minute",
            "password_reset": "2/minute",
            "email_verification": "3/minute"
        },
        
        # Resource intensive endpoints
        "intensive": {
            "cv_analysis": "5/minute",
            "job_matching": "10/minute",
            "report_generation": "2/minute",
            "data_export": "1/minute"
        }
    }

def get_user_tier(request: Request) -> str:
    """Determine user tier for rate limiting"""
    # Check if user is authenticated
    user = getattr(request.state, 'user', None)
    if not user:
        return "public"
    
    # Check user type
    user_type = getattr(user, 'account_type', 'basic')
    is_admin = getattr(user, 'is_admin', False)
    is_premium = getattr(user, 'is_premium', False)
    
    if is_admin:
        return "admin"
    elif is_premium:
        return "premium"
    elif user:
        return "authenticated"
    else:
        return "public"

def apply_dynamic_limits(request: Request) -> Optional[str]:
    """Apply dynamic rate limits based on endpoint and user"""
    endpoint = request.url.path
    method = request.method
    user_tier = get_user_tier(request)
    
    limits = get_rate_limits()
    
    # Critical authentication endpoints
    if endpoint.startswith("/api/auth/"):
        if "login" in endpoint:
            return limits["critical"]["auth_login"]
        elif "register" in endpoint:
            return limits["critical"]["auth_register"]
        elif "reset" in endpoint:
            return limits["critical"]["password_reset"]
        elif "verify" in endpoint:
            return limits["critical"]["email_verification"]
    
    # Job search endpoints
    elif endpoint.startswith("/api/jobs") or endpoint.startswith("/api/v1/jobs"):
        if method == "GET":
            if user_tier in limits:
                return limits[user_tier].get("jobs_search", limits["public"]["jobs_search"])
    
    # Application endpoints
    elif endpoint.startswith("/api/applications"):
        if user_tier in limits:
            return limits[user_tier].get("applications", "10/minute")
    
    # AI service endpoints
    elif "/ai/" in endpoint or "/cv-analysis" in endpoint:
        return limits["intensive"]["cv_analysis"]
    
    # Admin endpoints
    elif endpoint.startswith("/api/admin"):
        if user_tier == "admin":
            return limits["admin"]["admin_actions"]
        else:
            return "0/minute"  # Block non-admin access
    
    # File upload endpoints
    elif "/upload" in endpoint:
        if user_tier in limits:
            return limits[user_tier].get("file_upload", "2/minute")
    
    # Default based on user tier
    if user_tier == "premium":
        return "200/minute"
    elif user_tier == "authenticated":
        return "100/minute"
    else:
        return "30/minute"

class RateLimitingMiddleware:
    """Enhanced rate limiting middleware"""
    
    def __init__(self):
        self.limiter = limiter
        self.limits_config = get_rate_limits()
        
    async def __call__(self, request: Request, call_next):
        """Process request with rate limiting"""
        try:
            # Apply dynamic rate limiting
            dynamic_limit = apply_dynamic_limits(request)
            if dynamic_limit:
                # This would require custom implementation
                # For now, we'll use the decorator approach
                pass
            
            response = await call_next(request)
            return response
            
        except RateLimitExceeded as e:
            return await custom_rate_limit_handler(request, e)
        except Exception as e:
            logger.error(f"Rate limiting middleware error: {e}")
            # Continue without rate limiting on error
            return await call_next(request)

# Decorator factory for easy application
def rate_limit(limit: str):
    """Decorator factory for applying rate limits to endpoints"""
    def decorator(func):
        return limiter.limit(limit)(func)
    return decorator

# Common rate limit decorators
class RateLimits:
    """Pre-configured rate limit decorators"""
    
    # Public endpoints
    public_search = rate_limit("30/minute")
    public_list = rate_limit("50/minute")
    
    # Authentication endpoints  
    auth_login = rate_limit("5/minute")
    auth_register = rate_limit("3/minute")
    password_reset = rate_limit("2/minute")
    
    # User endpoints
    user_profile = rate_limit("20/minute")
    user_applications = rate_limit("15/minute")
    
    # File operations
    file_upload = rate_limit("3/minute")
    file_download = rate_limit("10/minute")
    
    # AI services
    ai_analysis = rate_limit("5/minute")
    ai_matching = rate_limit("10/minute")
    
    # Admin operations
    admin_actions = rate_limit("100/minute")
    bulk_operations = rate_limit("5/minute")
    
    # API endpoints
    api_standard = rate_limit("500/minute")
    api_premium = rate_limit("2000/minute")

# Usage statistics tracking
class RateLimitStats:
    """Track rate limiting statistics"""
    
    def __init__(self):
        self.stats = {
            "requests_total": 0,
            "requests_blocked": 0,
            "endpoints": {},
            "clients": {}
        }
    
    def record_request(self, client_id: str, endpoint: str, blocked: bool = False):
        """Record rate limiting statistics"""
        self.stats["requests_total"] += 1
        
        if blocked:
            self.stats["requests_blocked"] += 1
        
        # Track by endpoint
        if endpoint not in self.stats["endpoints"]:
            self.stats["endpoints"][endpoint] = {"total": 0, "blocked": 0}
        
        self.stats["endpoints"][endpoint]["total"] += 1
        if blocked:
            self.stats["endpoints"][endpoint]["blocked"] += 1
        
        # Track by client
        if client_id not in self.stats["clients"]:
            self.stats["clients"][client_id] = {"total": 0, "blocked": 0}
        
        self.stats["clients"][client_id]["total"] += 1
        if blocked:
            self.stats["clients"][client_id]["blocked"] += 1
    
    def get_stats(self):
        """Get current statistics"""
        return self.stats
    
    def reset_stats(self):
        """Reset statistics"""
        self.stats = {
            "requests_total": 0,
            "requests_blocked": 0,
            "endpoints": {},
            "clients": {}
        }

# Global stats instance
rate_limit_stats = RateLimitStats()

# Health check for rate limiting
def get_rate_limit_health():
    """Get rate limiting system health"""
    stats = rate_limit_stats.get_stats()
    total_requests = stats["requests_total"]
    blocked_requests = stats["requests_blocked"]
    
    block_rate = (blocked_requests / total_requests * 100) if total_requests > 0 else 0
    
    return {
        "status": "healthy" if block_rate < 10 else "warning" if block_rate < 25 else "critical",
        "total_requests": total_requests,
        "blocked_requests": blocked_requests,
        "block_rate_percent": round(block_rate, 2),
        "active_limits": len(get_rate_limits()),
        "storage_type": "memory" if "memory://" in os.getenv("RATE_LIMIT_STORAGE", "memory://") else "redis"
    }