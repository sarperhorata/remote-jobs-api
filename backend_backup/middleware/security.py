from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
import time
import logging
from utils.security import SecurityUtils
from utils.captcha import CaptchaVerifier
import os

logger = logging.getLogger(__name__)

class SecurityMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp):
        super().__init__(app)
        # IP addresses that have been blocked due to malicious activity
        self.blocked_ips = set()
        # Permanent IP block list from environment variable
        if os.getenv("BLOCKED_IPS"):
            self.blocked_ips.update(os.getenv("BLOCKED_IPS").split(","))
        
        # Sensitive endpoints that require stricter rate limiting
        self.sensitive_endpoints = {
            "/api/auth/login": 5,          # 5 requests per minute
            "/api/auth/register": 3,       # 3 requests per minute
            "/api/user/password-reset": 3  # 3 requests per minute
        }
        
        logger.info(f"Security middleware initialized with {len(self.blocked_ips)} blocked IPs")

    async def dispatch(self, request: Request, call_next):
        # Get client IP address
        client_ip = self._get_client_ip(request)
        
        # Check if IP is blocked
        if client_ip in self.blocked_ips:
            logger.warning(f"Blocked request from banned IP: {client_ip}")
            return JSONResponse(
                status_code=403,
                content={"detail": "Access denied"}
            )
        
        # Handle CORS preflight requests
        if request.method == "OPTIONS":
            response = await call_next(request)
            return response
        
        # Rate limiting for all endpoints
        endpoint = request.url.path
        rate_limit = self.sensitive_endpoints.get(endpoint, 30)  # Default: 30 requests per minute
        
        is_within_limit, remaining = SecurityUtils.check_rate_limit(client_ip, endpoint, rate_limit)
        
        if not is_within_limit:
            logger.warning(f"Rate limit exceeded for IP {client_ip} on endpoint {endpoint}")
            
            # If too many rate limit violations, block the IP
            rate_violations = SecurityUtils.get_rate_violations(client_ip)
            if rate_violations > 10:
                logger.warning(f"Adding IP {client_ip} to blocked list due to repeated rate limit violations")
                self.blocked_ips.add(client_ip)
            
            return JSONResponse(
                status_code=429,
                content={"detail": "Too many requests"},
                headers={"Retry-After": "60"}
            )
        
        # Captcha verification for auth endpoints
        if endpoint in ["/api/auth/register", "/api/auth/login"] and request.method == "POST":
            try:
                # For register/login we check captcha from form data
                form_data = await request.form()
                captcha_token = form_data.get("captchaToken")
                
                if not captcha_token:
                    return JSONResponse(
                        status_code=400,
                        content={"detail": "Captcha verification required"}
                    )
                
                # Verify the captcha token
                captcha_valid = await CaptchaVerifier.verify_token(captcha_token, client_ip)
                if not captcha_valid:
                    logger.warning(f"Invalid captcha from IP {client_ip}")
                    return JSONResponse(
                        status_code=400,
                        content={"detail": "Captcha verification failed"}
                    )
            except Exception as e:
                logger.error(f"Error during captcha verification: {str(e)}")
        
        # Process the request
        start_time = time.time()
        
        try:
            response = await call_next(request)
            process_time = time.time() - start_time
            
            # Log slow requests
            if process_time > 1.0:
                logger.warning(f"Slow request: {request.method} {request.url.path} took {process_time:.2f}s")
            
            # Add security headers to the response
            response.headers["X-Content-Type-Options"] = "nosniff"
            response.headers["X-Frame-Options"] = "DENY"
            response.headers["X-XSS-Protection"] = "1; mode=block"
            response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
            
            # Content Security Policy
            response.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self' https://www.google.com/recaptcha/ https://www.gstatic.com/recaptcha/; frame-src 'self' https://www.google.com/recaptcha/ https://hcaptcha.com; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; connect-src 'self' https://api.example.com"
            
            # Add rate limit headers
            response.headers["X-RateLimit-Limit"] = str(rate_limit)
            response.headers["X-RateLimit-Remaining"] = str(remaining)
            
            return response
            
        except Exception as e:
            logger.error(f"Error processing request: {str(e)}")
            return JSONResponse(
                status_code=500, 
                content={"detail": "Internal server error"}
            )
    
    def _get_client_ip(self, request: Request) -> str:
        """Extract client's real IP address from various headers or connection info"""
        forwarded = request.headers.get("X-Forwarded-For")
        
        if forwarded:
            # Get the first IP in the list (client's original IP)
            return forwarded.split(",")[0].strip()
        
        client_host = request.client.host if request.client else None
        return client_host or "unknown" 