import logging
import os
import time

from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
from utils.captcha import CaptchaVerifier
from utils.security import SecurityUtils

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
            "/api/auth/login": 5,  # 5 requests per minute
            "/api/auth/register": 3,  # 3 requests per minute
            "/api/user/password-reset": 3,  # 3 requests per minute
        }

        # Enhanced security headers
        self.security_headers = {
            "X-Frame-Options": "DENY",
            "X-Content-Type-Options": "nosniff",
            "X-XSS-Protection": "1; mode=block",
            "Referrer-Policy": "strict-origin-when-cross-origin",
            "X-Download-Options": "noopen",
            "X-Permitted-Cross-Domain-Policies": "none",
            "X-DNS-Prefetch-Control": "off",
            "X-Robots-Tag": "noindex, nofollow",
            "Permissions-Policy": "geolocation=(), microphone=(), camera=()",
        }

        # Enhanced CSP headers
        self.csp_headers = {
            "Content-Security-Policy": (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://www.google-analytics.com; "
                "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
                "img-src 'self' data: https: blob:; "
                "font-src 'self' https://fonts.gstatic.com; "
                "connect-src 'self' https://api.buzz2remote.com; "
                "media-src 'self' data: blob:; "
                "object-src 'none'; "
                "frame-ancestors 'self'; "
                "base-uri 'self'; "
                "form-action 'self'"
            )
        }

        logger.info(
            f"Security middleware initialized with {len(self.blocked_ips)} blocked IPs"
        )

    async def dispatch(self, request: Request, call_next):
        # Get client IP address
        client_ip = self._get_client_ip(request)

        # Check if IP is blocked
        if client_ip in self.blocked_ips:
            logger.warning(f"Blocked request from banned IP: {client_ip}")
            return JSONResponse(status_code=403, content={"detail": "Access denied"})

        # Handle CORS preflight requests
        if request.method == "OPTIONS":
            response = await call_next(request)
            return response

        # Rate limiting for all endpoints
        endpoint = request.url.path
        rate_limit = self.sensitive_endpoints.get(
            endpoint, 30
        )  # Default: 30 requests per minute

        is_within_limit, remaining = SecurityUtils.check_rate_limit(
            client_ip, endpoint, rate_limit
        )

        if not is_within_limit:
            logger.warning(
                f"Rate limit exceeded for IP {client_ip} on endpoint {endpoint}"
            )

            # If too many rate limit violations, block the IP
            rate_violations = SecurityUtils.get_rate_violations(client_ip)
            if rate_violations > 10:
                logger.warning(
                    f"Adding IP {client_ip} to blocked list due to repeated rate limit violations"
                )
                self.blocked_ips.add(client_ip)

            return JSONResponse(
                status_code=429,
                content={"detail": "Too many requests"},
                headers={"Retry-After": "60"},
            )

        # Captcha verification for auth endpoints
        if (
            endpoint in ["/api/auth/register", "/api/auth/login"]
            and request.method == "POST"
        ):
            try:
                # For register/login we check captcha from form data
                form_data = await request.form()
                captcha_token = form_data.get("captchaToken")

                if not captcha_token:
                    return JSONResponse(
                        status_code=400,
                        content={"detail": "Captcha verification required"},
                    )

                # Verify the captcha token
                captcha_valid = await CaptchaVerifier.verify_token(
                    captcha_token, client_ip
                )
                if not captcha_valid:
                    logger.warning(f"Invalid captcha from IP {client_ip}")
                    return JSONResponse(
                        status_code=400,
                        content={"detail": "Invalid captcha"},
                    )

            except Exception as e:
                logger.error(f"Error verifying captcha: {e}")
                return JSONResponse(
                    status_code=500,
                    content={"detail": "Captcha verification failed"},
                )

        # Process the request
        response = await call_next(request)

        # Add enhanced security headers to all responses
        for header_name, header_value in self.security_headers.items():
            response.headers[header_name] = header_value

        # Add CSP headers
        for header_name, header_value in self.csp_headers.items():
            response.headers[header_name] = header_value

        # Add additional security headers based on response type
        if "application/json" in response.headers.get("content-type", ""):
            response.headers["X-Content-Type-Options"] = "nosniff"

        # Add timing headers for performance monitoring
        response.headers["X-Response-Time"] = f"{time.time() * 1000:.2f}ms"

        return response

    def _get_client_ip(self, request: Request) -> str:
        """Get the real client IP address."""
        # Check for forwarded headers (when behind proxy)
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()

        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip

        # Fallback to direct connection
        return request.client.host if request.client else "unknown"
