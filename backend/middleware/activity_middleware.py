import json
import logging
import time
import uuid
from datetime import datetime
from typing import Any, Callable, Dict, Optional

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from ..services.activity_logger import activity_logger

logger = logging.getLogger(__name__)


class ActivityTrackingMiddleware(BaseHTTPMiddleware):
    """Middleware to track all user activities and API calls"""

    def __init__(self, app, exclude_paths: list = None):
        super().__init__(app)
        self.exclude_paths = exclude_paths or [
            "/docs",
            "/redoc",
            "/openapi.json",
            "/favicon.ico",
            "/health",
            "/admin/static",
            "/static",
        ]

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Skip tracking for excluded paths
        if any(request.url.path.startswith(path) for path in self.exclude_paths):
            return await call_next(request)

        # Start tracking
        start_time = time.time()
        request_id = str(uuid.uuid4())

        # Extract user info from request
        user_id = await self._extract_user_id(request)
        session_id = await self._extract_session_id(request)

        # Prepare request data for logging
        request_data = {
            "request_id": request_id,
            "method": request.method,
            "endpoint": request.url.path,
            "query_params": dict(request.query_params),
            "headers": {
                k: v
                for k, v in request.headers.items()
                if k.lower() not in ["authorization", "cookie"]
            },
            "ip_address": self._get_client_ip(request),
            "user_agent": request.headers.get("user-agent", ""),
            "referer": request.headers.get("referer", ""),
        }

        # Process request
        response = None
        error_occurred = False
        error_message = None

        try:
            response = await call_next(request)
        except Exception as e:
            error_occurred = True
            error_message = str(e)
            logger.error(f"Request {request_id} failed: {error_message}")
            raise
        finally:
            # Calculate response time
            process_time = (time.time() - start_time) * 1000  # Convert to milliseconds

            # Log the activity
            try:
                await self._log_request_activity(
                    request_data=request_data,
                    user_id=user_id,
                    session_id=session_id,
                    response_time_ms=process_time,
                    status_code=response.status_code if response else 500,
                    error_occurred=error_occurred,
                    error_message=error_message,
                )
            except Exception as log_error:
                logger.error(f"Failed to log activity: {str(log_error)}")

        # Add response headers
        if response:
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Response-Time"] = f"{process_time:.2f}ms"

        return response

    def _get_client_ip(self, request: Request) -> str:
        """Extract real client IP from request"""
        # Check proxy headers
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()

        real_ip = request.headers.get("x-real-ip")
        if real_ip:
            return real_ip

        # Fallback to client IP
        return request.client.host if request.client else "unknown"

    async def _extract_user_id(self, request: Request) -> Optional[str]:
        """Extract user ID from JWT token or session"""
        try:
            # Try to get from JWT token
            authorization = request.headers.get("authorization")
            if authorization and authorization.startswith("Bearer "):
                # Import here to avoid circular imports
                from utils.auth import decode_token

                token = authorization.split(" ")[1]
                payload = decode_token(token)
                return payload.get("sub") if payload else None

            # Try to get from session
            session_user = request.session.get("user")
            if session_user:
                return session_user.get("id")

        except Exception as e:
            logger.debug(f"Could not extract user ID: {str(e)}")

        return None

    async def _extract_session_id(self, request: Request) -> Optional[str]:
        """Extract session ID from request"""
        try:
            # Try to get from session
            return request.session.get("session_id")
        except Exception:
            return None

    async def _log_request_activity(
        self,
        request_data: Dict[str, Any],
        user_id: Optional[str],
        session_id: Optional[str],
        response_time_ms: float,
        status_code: int,
        error_occurred: bool = False,
        error_message: Optional[str] = None,
    ):
        """Log the request as a user activity"""

        # Determine activity type based on endpoint
        activity_type = self._determine_activity_type(
            request_data["endpoint"], request_data["method"]
        )

        # Prepare activity data
        activity_data = {
            "endpoint": request_data["endpoint"],
            "method": request_data["method"],
            "query_params": request_data["query_params"],
            "response_time_ms": response_time_ms,
            "status_code": status_code,
            "user_agent": request_data["user_agent"],
            "referer": request_data["referer"],
            "request_id": request_data["request_id"],
        }

        if error_occurred:
            activity_data["error_message"] = error_message
            activity_type = "error_occurred"

        # Log the activity
        await activity_logger.log_activity(
            activity_type=activity_type,
            user_id=user_id,
            session_id=session_id,
            activity_data=activity_data,
            ip_address=request_data["ip_address"],
            response_time_ms=response_time_ms,
            status_code=status_code,
            is_success=not error_occurred,
        )

    def _determine_activity_type(self, endpoint: str, method: str) -> str:
        """Determine activity type based on endpoint and method"""

        # Authentication endpoints
        if "/api/auth" in endpoint:
            if "login" in endpoint:
                return "login"
            elif "register" in endpoint:
                return "register"
            elif "logout" in endpoint:
                return "logout"
            elif "reset-password" in endpoint:
                return "password_reset"
            else:
                return "auth_action"

        # Job-related endpoints
        if "/api/jobs" in endpoint:
            if method == "GET":
                if "/search" in endpoint:
                    return "job_search"
                elif endpoint.count("/") > 2:  # Specific job ID
                    return "job_view"
                else:
                    return "job_list"
            elif method == "POST":
                if "/apply" in endpoint:
                    return "job_apply"
                elif "/save" in endpoint:
                    return "job_save"
                else:
                    return "job_action"

        # Application endpoints
        if "/api/applications" in endpoint:
            if method == "POST":
                return "job_apply"
            elif method == "GET":
                return "application_view"
            else:
                return "application_action"

        # Profile endpoints
        if "/api/profile" in endpoint or "/api/onboarding" in endpoint:
            return "profile_update"

        # Company endpoints
        if "/api/companies" in endpoint:
            return "company_view"

        # Payment endpoints
        if "/api/payment" in endpoint:
            return "payment_action"

        # Admin endpoints
        if "/admin" in endpoint:
            return "admin_action"

        # Default
        return "api_call"
