"""
Security Headers Middleware
Implements comprehensive security headers for production protection
"""

from fastapi import Request
from fastapi.responses import Response
from starlette.middleware.base import BaseHTTPMiddleware
import os
from typing import Dict, Optional

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Comprehensive security headers middleware"""
    
    def __init__(self, app):
        super().__init__(app)
        self.environment = os.getenv("ENVIRONMENT", "development")
        
        # Base security headers (always applied)
        self.base_headers = {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            "Referrer-Policy": "strict-origin-when-cross-origin",
            "X-Download-Options": "noopen",
            "X-Permitted-Cross-Domain-Policies": "none"
        }
        
        # Environment-specific headers
        if self.environment == "production":
            # Production: Strict security
            self.security_headers = {
                **self.base_headers,
                "Strict-Transport-Security": "max-age=31536000; includeSubDomains; preload",
                "Content-Security-Policy": self._get_production_csp(),
                "Permissions-Policy": self._get_permissions_policy(),
                "Cache-Control": "private, no-cache, no-store, must-revalidate",
                "Pragma": "no-cache",
                "Expires": "0"
            }
        else:
            # Development: Relaxed for debugging
            self.security_headers = {
                **self.base_headers,
                "Content-Security-Policy": self._get_development_csp(),
                "Cache-Control": "no-cache"
            }
    
    def _get_production_csp(self) -> str:
        """Enhanced Production Content Security Policy with strict security"""
        return (
            "default-src 'self'; "
            "script-src 'self' "
            "https://www.google-analytics.com "
            "https://www.googletagmanager.com "
            "https://apis.google.com "
            "https://js.stripe.com "
            "'sha256-XYZ123' 'nonce-random123'; "  # Use nonces in production
            "style-src 'self' 'unsafe-inline' "
            "https://fonts.googleapis.com "
            "https://cdnjs.cloudflare.com; "
            "img-src 'self' data: https: blob: "
            "https://www.google-analytics.com "
            "https://*.stripe.com; "
            "font-src 'self' "
            "https://fonts.gstatic.com "
            "https://cdnjs.cloudflare.com; "
            "connect-src 'self' "
            "https://remote-jobs-api-k9v1.onrender.com "
            "https://api.buzz2remote.com "
            "https://www.google-analytics.com "
            "https://api.stripe.com; "
            "media-src 'self' data: blob:; "
            "object-src 'none'; "
            "embed-src 'none'; "
            "frame-src 'none'; "
            "frame-ancestors 'none'; "
            "base-uri 'self'; "
            "form-action 'self' "
            "https://api.stripe.com; "
            "manifest-src 'self'; "
            "worker-src 'self' blob:; "
            "child-src 'none'; "
            "script-src-attr 'none'; "
            "style-src-attr 'unsafe-inline'; "
            "upgrade-insecure-requests; "
            "block-all-mixed-content"
        )
    
    def _get_development_csp(self) -> str:
        """Development Content Security Policy (more permissive)"""
        return (
            "default-src 'self' 'unsafe-inline' 'unsafe-eval'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval' "
            "http://localhost:* "
            "https://www.google-analytics.com; "
            "style-src 'self' 'unsafe-inline' "
            "http://localhost:* "
            "https://fonts.googleapis.com; "
            "img-src 'self' data: https: blob: http:; "
            "font-src 'self' "
            "http://localhost:* "
            "https://fonts.gstatic.com; "
            "connect-src 'self' "
            "http://localhost:* "
            "ws://localhost:* "
            "wss://localhost:*; "
            "media-src 'self' data: blob:; "
            "object-src 'none'; "
            "frame-ancestors 'self'; "
            "base-uri 'self'; "
            "form-action 'self'"
        )
    
    def _get_permissions_policy(self) -> str:
        """Permissions Policy for browser features"""
        return (
            "accelerometer=(), "
            "ambient-light-sensor=(), "
            "autoplay=(), "
            "battery=(), "
            "camera=(), "
            "cross-origin-isolated=(), "
            "display-capture=(), "
            "document-domain=(), "
            "encrypted-media=(), "
            "execution-while-not-rendered=(), "
            "execution-while-out-of-viewport=(), "
            "fullscreen=(self), "
            "geolocation=(), "
            "gyroscope=(), "
            "keyboard-map=(), "
            "magnetometer=(), "
            "microphone=(), "
            "midi=(), "
            "navigation-override=(), "
            "payment=(), "
            "picture-in-picture=(), "
            "publickey-credentials-get=(), "
            "screen-wake-lock=(), "
            "sync-xhr=(), "
            "usb=(), "
            "web-share=(), "
            "xr-spatial-tracking=()"
        )
    
    async def dispatch(self, request: Request, call_next):
        """Apply security headers to all responses"""
        try:
            # Process the request
            response = await call_next(request)
            
            # Add security headers to response
            for header_name, header_value in self.security_headers.items():
                response.headers[header_name] = header_value
            
            # Add additional headers based on content type
            content_type = response.headers.get("content-type", "")
            
            # JSON API responses
            if "application/json" in content_type:
                response.headers["X-API-Version"] = "1.0"
                response.headers["X-Response-Time"] = str(getattr(request.state, 'response_time', 0))
            
            # HTML responses
            elif "text/html" in content_type:
                response.headers["X-UA-Compatible"] = "IE=edge"
            
            # Add rate limiting headers if available
            if hasattr(request.state, 'rate_limit_remaining'):
                response.headers["X-RateLimit-Remaining"] = str(request.state.rate_limit_remaining)
                response.headers["X-RateLimit-Reset"] = str(getattr(request.state, 'rate_limit_reset', 0))
            
            return response
            
        except Exception as e:
            # Ensure security headers are added even on errors
            from fastapi.responses import JSONResponse
            error_response = JSONResponse(
                status_code=500,
                content={"error": "Internal server error"}
            )
            
            # Add security headers to error response
            for header_name, header_value in self.security_headers.items():
                error_response.headers[header_name] = header_value
            
            return error_response

class SecurityReportingMiddleware(BaseHTTPMiddleware):
    """Security reporting and monitoring middleware"""
    
    def __init__(self, app):
        super().__init__(app)
        self.security_violations = []
        self.max_violations = 100  # Keep last 100 violations
    
    async def dispatch(self, request: Request, call_next):
        """Monitor for security violations"""
        response = await call_next(request)
        
        # Check for potential security issues
        await self._check_security_violations(request, response)
        
        return response
    
    async def _check_security_violations(self, request: Request, response: Response):
        """Check for potential security violations"""
        violations = []
        
        # Check for missing security headers
        security_headers = [
            "X-Content-Type-Options",
            "X-Frame-Options", 
            "X-XSS-Protection",
            "Content-Security-Policy"
        ]
        
        for header in security_headers:
            if header not in response.headers:
                violations.append(f"Missing security header: {header}")
        
        # Check for suspicious user agents
        user_agent = request.headers.get("user-agent", "").lower()
        suspicious_patterns = [
            "sqlmap", "nmap", "nikto", "dirb", "gobuster", 
            "burp", "owasp", "scanner", "crawler"
        ]
        
        for pattern in suspicious_patterns:
            if pattern in user_agent:
                violations.append(f"Suspicious user agent: {pattern}")
        
        # Check for suspicious request patterns
        path = request.url.path.lower()
        suspicious_paths = [
            "admin", "phpmyadmin", "wp-admin", "config", 
            ".env", ".git", "backup", "dump"
        ]
        
        for suspicious in suspicious_paths:
            if suspicious in path:
                violations.append(f"Suspicious path access: {path}")
        
        # Log violations
        if violations:
            self._log_security_violation(request, violations)
    
    def _log_security_violation(self, request: Request, violations: list):
        """Log security violations"""
        violation_data = {
            "timestamp": str(request.state.timestamp if hasattr(request.state, 'timestamp') else "unknown"),
            "ip": request.client.host if request.client else "unknown",
            "user_agent": request.headers.get("user-agent", "unknown"),
            "path": request.url.path,
            "method": request.method,
            "violations": violations
        }
        
        # Add to in-memory storage (limited)
        self.security_violations.append(violation_data)
        if len(self.security_violations) > self.max_violations:
            self.security_violations.pop(0)
        
        # Log to console (in production, send to security monitoring)
        import logging
        logger = logging.getLogger(__name__)
        logger.warning(f"Security violation detected: {violation_data}")
    
    def get_violations(self) -> list:
        """Get recent security violations"""
        return self.security_violations.copy()

# Global instances (placeholder - will be initialized when app is created)
security_headers_middleware = None
security_reporting_middleware = None

# Initialize middleware instances
def initialize_security_middleware(app):
    """Initialize security middleware instances with app"""
    global security_headers_middleware, security_reporting_middleware
    
    security_headers_middleware = SecurityHeadersMiddleware(app)
    security_reporting_middleware = SecurityReportingMiddleware(app)
    
    return security_headers_middleware, security_reporting_middleware

# Health check for security
def get_security_health() -> Dict[str, any]:
    """Get security middleware health status"""
    violations = security_reporting_middleware.get_violations()
    recent_violations = [v for v in violations if v.get("timestamp")]  # Filter valid timestamps
    
    return {
        "status": "healthy" if len(recent_violations) < 10 else "warning" if len(recent_violations) < 50 else "critical",
        "total_violations": len(violations),
        "recent_violations": len(recent_violations),
        "environment": security_headers_middleware.environment,
        "headers_active": len(security_headers_middleware.security_headers),
        "last_violations": recent_violations[-5:] if recent_violations else []
    } 