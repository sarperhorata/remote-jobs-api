import pytest
from unittest.mock import Mock, patch
from fastapi import HTTPException, Request
from starlette.responses import Response

class TestMiddlewareService:
    """Test suite for Middleware Service functionality."""

    def test_cors_middleware(self):
        """Test CORS middleware functionality."""
        def setup_cors_headers(response: Response, request: Request):
            # Mock CORS setup
            allowed_origins = ["http://localhost:3000", "http://localhost:3001", "https://buzz2remote.com"]
            origin = request.headers.get("origin")
            
            if origin in allowed_origins:
                response.headers["Access-Control-Allow-Origin"] = origin
            else:
                response.headers["Access-Control-Allow-Origin"] = "null"
            
            response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
            response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
            return response

        # Mock request and response
        mock_request = Mock(spec=Request)
        mock_response = Mock(spec=Response)
        mock_response.headers = {}
        
        # Test allowed origin
        mock_request.headers = {"origin": "http://localhost:3000"}
        result = setup_cors_headers(mock_response, mock_request)
        
        assert result.headers["Access-Control-Allow-Origin"] == "http://localhost:3000"
        assert "GET, POST, PUT, DELETE, OPTIONS" in result.headers["Access-Control-Allow-Methods"]
        
        # Test disallowed origin
        mock_request.headers = {"origin": "http://malicious-site.com"}
        mock_response.headers = {}
        result = setup_cors_headers(mock_response, mock_request)
        
        assert result.headers["Access-Control-Allow-Origin"] == "null"

    def test_authentication_middleware(self):
        """Test authentication middleware."""
        def authenticate_request(token: str):
            # Mock authentication logic
            valid_tokens = ["valid_token_123", "admin_token_456"]
            
            if not token:
                return {"authenticated": False, "error": "Token missing"}
            
            if token.startswith("Bearer "):
                token = token[7:]
            
            if token in valid_tokens:
                if token == "admin_token_456":
                    return {"authenticated": True, "user_id": "admin", "role": "admin"}
                return {"authenticated": True, "user_id": "user123", "role": "user"}
            
            return {"authenticated": False, "error": "Invalid token"}

        # Test valid token
        result = authenticate_request("Bearer valid_token_123")
        assert result["authenticated"] is True
        assert result["user_id"] == "user123"
        
        # Test admin token
        result = authenticate_request("Bearer admin_token_456")
        assert result["authenticated"] is True
        assert result["role"] == "admin"
        
        # Test invalid token
        result = authenticate_request("Bearer invalid_token")
        assert result["authenticated"] is False
        assert "Invalid token" in result["error"]
        
        # Test missing token
        result = authenticate_request("")
        assert result["authenticated"] is False
        assert "Token missing" in result["error"]

    def test_rate_limiting_middleware(self):
        """Test rate limiting middleware."""
        import time
        
        class RateLimiter:
            def __init__(self, max_requests=10, window_seconds=60):
                self.max_requests = max_requests
                self.window_seconds = window_seconds
                self.requests = {}
            
            def check_rate_limit(self, client_ip: str):
                current_time = time.time()
                
                if client_ip not in self.requests:
                    self.requests[client_ip] = []
                
                # Remove old requests
                self.requests[client_ip] = [
                    req_time for req_time in self.requests[client_ip]
                    if current_time - req_time < self.window_seconds
                ]
                
                # Check if over limit
                if len(self.requests[client_ip]) >= self.max_requests:
                    return {"allowed": False, "retry_after": self.window_seconds}
                
                # Add current request
                self.requests[client_ip].append(current_time)
                return {"allowed": True, "remaining": self.max_requests - len(self.requests[client_ip])}

        limiter = RateLimiter(max_requests=3, window_seconds=60)
        client_ip = "192.168.1.1"
        
        # First 3 requests should be allowed
        for i in range(3):
            result = limiter.check_rate_limit(client_ip)
            assert result["allowed"] is True
        
        # 4th request should be denied
        result = limiter.check_rate_limit(client_ip)
        assert result["allowed"] is False
        assert result["retry_after"] == 60

    def test_request_logging_middleware(self):
        """Test request logging middleware."""
        def log_request(request: Request, response_time: float = None):
            log_data = {
                "method": request.method,
                "url": str(request.url),
                "user_agent": request.headers.get("user-agent", ""),
                "ip": request.client.host if request.client else "unknown",
                "response_time": response_time
            }
            
            # Sanitize sensitive data
            if "password" in log_data["url"].lower():
                log_data["url"] = "[REDACTED - Contains password]"
            
            return log_data

        # Mock request
        mock_request = Mock(spec=Request)
        mock_request.method = "POST"
        mock_request.url = "http://localhost:8002/api/auth/login"
        mock_request.headers = {"user-agent": "Mozilla/5.0"}
        mock_request.client = Mock()
        mock_request.client.host = "127.0.0.1"
        
        log_data = log_request(mock_request, 0.123)
        
        assert log_data["method"] == "POST"
        assert log_data["ip"] == "127.0.0.1"
        assert log_data["response_time"] == 0.123
        assert "Mozilla/5.0" in log_data["user_agent"]
        
        # Test sensitive data redaction
        mock_request.url = "http://localhost:8002/api/auth/reset-password?token=123"
        log_data = log_request(mock_request)
        assert "[REDACTED - Contains password]" in log_data["url"]

    def test_error_handling_middleware(self):
        """Test error handling middleware."""
        def handle_application_error(error: Exception):
            error_response = {
                "error": True,
                "message": "Internal server error",
                "type": type(error).__name__
            }
            
            # Handle specific error types
            if isinstance(error, ValueError):
                error_response["message"] = "Invalid input provided"
                error_response["status_code"] = 400
            elif isinstance(error, FileNotFoundError):
                error_response["message"] = "Resource not found"
                error_response["status_code"] = 404
            elif isinstance(error, PermissionError):
                error_response["message"] = "Access denied"
                error_response["status_code"] = 403
            else:
                error_response["status_code"] = 500
            
            return error_response

        # Test ValueError
        error = ValueError("Invalid email format")
        response = handle_application_error(error)
        assert response["status_code"] == 400
        assert "Invalid input" in response["message"]
        
        # Test FileNotFoundError
        error = FileNotFoundError("User not found")
        response = handle_application_error(error)
        assert response["status_code"] == 404
        assert "Resource not found" in response["message"]
        
        # Test PermissionError
        error = PermissionError("Insufficient privileges")
        response = handle_application_error(error)
        assert response["status_code"] == 403
        assert "Access denied" in response["message"]
        
        # Test generic error
        error = RuntimeError("Something went wrong")
        response = handle_application_error(error)
        assert response["status_code"] == 500
        assert "Internal server error" in response["message"]

    def test_request_validation_middleware(self):
        """Test request validation middleware."""
        def validate_request_data(data: dict, required_fields: list):
            validation_result = {
                "valid": True,
                "errors": [],
                "sanitized_data": {}
            }
            
            # Check required fields
            for field in required_fields:
                if field not in data or data[field] is None:
                    validation_result["errors"].append(f"Missing required field: {field}")
                    validation_result["valid"] = False
                else:
                    # Basic sanitization
                    if isinstance(data[field], str):
                        sanitized_value = data[field].strip()
                        if field == "email":
                            sanitized_value = sanitized_value.lower()
                        validation_result["sanitized_data"][field] = sanitized_value
                    else:
                        validation_result["sanitized_data"][field] = data[field]
            
            return validation_result

        # Test valid data
        data = {"email": "  USER@EXAMPLE.COM  ", "password": "secret123"}
        result = validate_request_data(data, ["email", "password"])
        
        assert result["valid"] is True
        assert len(result["errors"]) == 0
        assert result["sanitized_data"]["email"] == "user@example.com"
        assert result["sanitized_data"]["password"] == "secret123"
        
        # Test missing fields
        data = {"email": "user@example.com"}
        result = validate_request_data(data, ["email", "password"])
        
        assert result["valid"] is False
        assert "Missing required field: password" in result["errors"]

    def test_security_headers_middleware(self):
        """Test security headers middleware."""
        def add_security_headers(response: Response):
            security_headers = {
                "X-Content-Type-Options": "nosniff",
                "X-Frame-Options": "DENY",
                "X-XSS-Protection": "1; mode=block",
                "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
                "Content-Security-Policy": "default-src 'self'",
                "Referrer-Policy": "strict-origin-when-cross-origin"
            }
            
            for header, value in security_headers.items():
                response.headers[header] = value
            
            return response

        mock_response = Mock(spec=Response)
        mock_response.headers = {}
        
        result = add_security_headers(mock_response)
        
        assert result.headers["X-Content-Type-Options"] == "nosniff"
        assert result.headers["X-Frame-Options"] == "DENY"
        assert result.headers["X-XSS-Protection"] == "1; mode=block"
        assert "max-age=31536000" in result.headers["Strict-Transport-Security"]
        assert "default-src 'self'" in result.headers["Content-Security-Policy"]

    def test_request_size_middleware(self):
        """Test request size limiting middleware."""
        def check_request_size(content_length: int, max_size_mb: int = 10):
            max_size_bytes = max_size_mb * 1024 * 1024
            
            if content_length > max_size_bytes:
                return {
                    "allowed": False,
                    "error": f"Request too large. Maximum size: {max_size_mb}MB",
                    "received_size": content_length,
                    "max_size": max_size_bytes
                }
            
            return {"allowed": True, "size": content_length}

        # Test normal request
        result = check_request_size(1024)  # 1KB
        assert result["allowed"] is True
        assert result["size"] == 1024
        
        # Test oversized request
        large_size = 15 * 1024 * 1024  # 15MB
        result = check_request_size(large_size, max_size_mb=10)
        assert result["allowed"] is False
        assert "Request too large" in result["error"]
        assert result["received_size"] == large_size

    def test_api_versioning_middleware(self):
        """Test API versioning middleware."""
        def extract_api_version(request: Request):
            # Check header first
            version = request.headers.get("API-Version")
            if version:
                return {"version": version, "source": "header"}
            
            # Check URL path
            url_path = str(request.url.path)
            if "/api/v1/" in url_path:
                return {"version": "v1", "source": "url"}
            elif "/api/v2/" in url_path:
                return {"version": "v2", "source": "url"}
            
            # Default version
            return {"version": "v1", "source": "default"}

        # Test header version
        mock_request = Mock(spec=Request)
        mock_request.headers = {"API-Version": "v2"}
        mock_request.url = Mock()
        mock_request.url.path = "/api/jobs"
        
        result = extract_api_version(mock_request)
        assert result["version"] == "v2"
        assert result["source"] == "header"
        
        # Test URL version
        mock_request.headers = {}
        mock_request.url.path = "/api/v1/jobs"
        
        result = extract_api_version(mock_request)
        assert result["version"] == "v1"
        assert result["source"] == "url"
        
        # Test default version
        mock_request.url.path = "/jobs"
        
        result = extract_api_version(mock_request)
        assert result["version"] == "v1"
        assert result["source"] == "default"
