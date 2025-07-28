"""
Error Handling Middleware
Standardizes error responses and provides comprehensive error logging
"""

import json
import logging
import time
import traceback
import uuid
from datetime import datetime, UTC
from typing import Any, Dict, Optional

from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)


class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    """Comprehensive error handling and logging middleware"""

    def __init__(self, app):
        super().__init__(app)
        self.error_counts = {}
        self.error_patterns = {}

    async def dispatch(self, request: Request, call_next):
        """Process request with comprehensive error handling"""
        start_time = time.time()
        error_id = str(uuid.uuid4())[:8]

        try:
            # Add error ID to request state
            request.state.error_id = error_id
            request.state.start_time = start_time

            response = await call_next(request)

            # Log successful requests for monitoring
            if response.status_code >= 400:
                await self._log_error_response(request, response, start_time, error_id)

            return response

        except HTTPException as exc:
            return await self._handle_http_exception(request, exc, start_time, error_id)

        except Exception as exc:
            return await self._handle_generic_exception(
                request, exc, start_time, error_id
            )

    async def _handle_http_exception(
        self, request: Request, exc: HTTPException, start_time: float, error_id: str
    ) -> JSONResponse:
        """Handle FastAPI HTTP exceptions with standardized response"""

        duration = time.time() - start_time

        # Log the exception
        await self._log_http_exception(request, exc, duration, error_id)

        # Track error counts
        self._track_error(exc.status_code, request.url.path)

        # Create standardized error response
        error_response = {
            "error": {
                "code": exc.status_code,
                "message": (
                    exc.detail if isinstance(exc.detail, str) else "An error occurred"
                ),
                "type": self._get_error_type(exc.status_code),
                "error_id": error_id,
                "timestamp": datetime.now(UTC).isoformat(),
                "path": request.url.path,
                "method": request.method,
            }
        }

        # Add debug info in development
        if self._is_development():
            error_response["debug"] = {
                "duration_ms": round(duration * 1000, 2),
                "headers": dict(request.headers),
                "query_params": dict(request.query_params),
            }

        return JSONResponse(
            status_code=exc.status_code,
            content=error_response,
            headers=self._get_error_headers(error_id),
        )

    async def _handle_generic_exception(
        self, request: Request, exc: Exception, start_time: float, error_id: str
    ) -> JSONResponse:
        """Handle unexpected exceptions with proper logging and response"""

        duration = time.time() - start_time

        # Log the exception with full traceback
        await self._log_generic_exception(request, exc, duration, error_id)

        # Track error counts
        self._track_error(500, request.url.path)

        # Create standardized error response
        error_response = {
            "error": {
                "code": 500,
                "message": "Internal server error",
                "type": "internal_error",
                "error_id": error_id,
                "timestamp": datetime.now(UTC).isoformat(),
                "path": request.url.path,
                "method": request.method,
            }
        }

        # Add debug info in development
        if self._is_development():
            error_response["debug"] = {
                "exception_type": type(exc).__name__,
                "exception_message": str(exc),
                "duration_ms": round(duration * 1000, 2),
                "traceback": traceback.format_exc().split("\n")[-10:],  # Last 10 lines
            }

        return JSONResponse(
            status_code=500,
            content=error_response,
            headers=self._get_error_headers(error_id),
        )

    async def _log_http_exception(
        self, request: Request, exc: HTTPException, duration: float, error_id: str
    ):
        """Log HTTP exceptions with context"""

        log_data = {
            "error_id": error_id,
            "status_code": exc.status_code,
            "message": exc.detail,
            "path": request.url.path,
            "method": request.method,
            "duration_ms": round(duration * 1000, 2),
            "client_ip": self._get_client_ip(request),
            "user_agent": request.headers.get("user-agent", "unknown"),
            "timestamp": datetime.now(UTC).isoformat(),
        }

        # Log level based on status code
        if exc.status_code >= 500:
            logger.error(f"HTTP {exc.status_code} Error: {json.dumps(log_data)}")
        elif exc.status_code >= 400:
            logger.warning(f"HTTP {exc.status_code} Error: {json.dumps(log_data)}")
        else:
            logger.info(f"HTTP {exc.status_code}: {json.dumps(log_data)}")

    async def _log_generic_exception(
        self, request: Request, exc: Exception, duration: float, error_id: str
    ):
        """Log generic exceptions with full context"""

        log_data = {
            "error_id": error_id,
            "exception_type": type(exc).__name__,
            "exception_message": str(exc),
            "path": request.url.path,
            "method": request.method,
            "duration_ms": round(duration * 1000, 2),
            "client_ip": self._get_client_ip(request),
            "user_agent": request.headers.get("user-agent", "unknown"),
            "timestamp": datetime.now(UTC).isoformat(),
            "traceback": traceback.format_exc(),
        }

        logger.error(f"Unhandled Exception: {json.dumps(log_data, indent=2)}")

    async def _log_error_response(
        self, request: Request, response, start_time: float, error_id: str
    ):
        """Log error responses from endpoints"""

        duration = time.time() - start_time

        log_data = {
            "error_id": error_id,
            "status_code": response.status_code,
            "path": request.url.path,
            "method": request.method,
            "duration_ms": round(duration * 1000, 2),
            "client_ip": self._get_client_ip(request),
            "timestamp": datetime.now(UTC).isoformat(),
        }

        if response.status_code >= 500:
            logger.error(f"Error Response: {json.dumps(log_data)}")
        elif response.status_code >= 400:
            logger.warning(f"Client Error Response: {json.dumps(log_data)}")

    def _track_error(self, status_code: int, path: str):
        """Track error statistics"""

        # Track by status code
        if status_code not in self.error_counts:
            self.error_counts[status_code] = 0
        self.error_counts[status_code] += 1

        # Track by path pattern
        path_pattern = self._normalize_path(path)
        if path_pattern not in self.error_patterns:
            self.error_patterns[path_pattern] = {}
        if status_code not in self.error_patterns[path_pattern]:
            self.error_patterns[path_pattern][status_code] = 0
        self.error_patterns[path_pattern][status_code] += 1

    def _normalize_path(self, path: str) -> str:
        """Normalize path for pattern tracking"""
        # Replace IDs with placeholders
        import re

        path = re.sub(r"/\d+/", "/{id}/", path)
        path = re.sub(r"/[a-f0-9-]{36}/", "/{uuid}/", path)
        return path

    def _get_error_type(self, status_code: int) -> str:
        """Get error type based on status code"""
        error_types = {
            400: "validation_error",
            401: "authentication_error",
            403: "authorization_error",
            404: "not_found_error",
            405: "method_not_allowed",
            409: "conflict_error",
            422: "validation_error",
            429: "rate_limit_error",
            500: "internal_error",
            502: "gateway_error",
            503: "service_unavailable",
            504: "timeout_error",
        }
        return error_types.get(status_code, "unknown_error")

    def _get_error_headers(self, error_id: str) -> Dict[str, str]:
        """Get standard error headers"""
        return {
            "X-Error-ID": error_id,
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "Cache-Control": "no-cache, no-store, must-revalidate",
        }

    def _get_client_ip(self, request: Request) -> str:
        """Get client IP address"""
        # Check for forwarded headers first
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()

        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip

        return request.client.host if request.client else "unknown"

    def _is_development(self) -> bool:
        """Check if running in development mode"""
        import os

        return os.getenv("ENVIRONMENT", "development") == "development"

    def get_error_stats(self) -> Dict[str, Any]:
        """Get error statistics"""
        total_errors = sum(self.error_counts.values())

        return {
            "total_errors": total_errors,
            "error_counts_by_code": self.error_counts,
            "error_patterns": self.error_patterns,
            "most_common_errors": sorted(
                self.error_counts.items(), key=lambda x: x[1], reverse=True
            )[:5],
        }


# Custom exception classes for better error handling
class ValidationError(HTTPException):
    """Custom validation error"""

    def __init__(self, detail: str, field: str = None):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={"message": detail, "field": field} if field else detail,
        )


class BusinessLogicError(HTTPException):
    """Custom business logic error"""

    def __init__(self, detail: str, code: str = None):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"message": detail, "code": code} if code else detail,
        )


class ResourceNotFoundError(HTTPException):
    """Custom resource not found error"""

    def __init__(self, resource: str, identifier: str = None):
        message = f"{resource} not found"
        if identifier:
            message += f" with identifier: {identifier}"

        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=message)


class AuthenticationError(HTTPException):
    """Custom authentication error"""

    def __init__(self, detail: str = "Authentication required"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"},
        )


class AuthorizationError(HTTPException):
    """Custom authorization error"""

    def __init__(self, detail: str = "Insufficient permissions"):
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail=detail)


# Utility functions for error handling
def handle_database_error(exc: Exception) -> HTTPException:
    """Convert database errors to appropriate HTTP exceptions"""
    error_message = str(exc).lower()

    if "duplicate key" in error_message or "unique constraint" in error_message:
        return BusinessLogicError("Resource already exists", "duplicate_resource")
    elif "foreign key" in error_message:
        return BusinessLogicError(
            "Referenced resource does not exist", "invalid_reference"
        )
    elif "connection" in error_message or "timeout" in error_message:
        return HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database temporarily unavailable",
        )
    else:
        return HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database operation failed",
        )


def handle_external_api_error(exc: Exception, service_name: str) -> HTTPException:
    """Convert external API errors to appropriate HTTP exceptions"""
    error_message = str(exc).lower()

    if "timeout" in error_message:
        return HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail=f"{service_name} service timeout",
        )
    elif "connection" in error_message:
        return HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"{service_name} service unavailable",
        )
    else:
        return HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"{service_name} service error",
        )


# Global error handler instance
error_handler_middleware = None


def get_error_handler() -> Optional[ErrorHandlingMiddleware]:
    """Get global error handler instance"""
    return error_handler_middleware


def initialize_error_handler(app) -> ErrorHandlingMiddleware:
    """Initialize and return error handler middleware"""
    global error_handler_middleware
    error_handler_middleware = ErrorHandlingMiddleware(app)
    return error_handler_middleware
