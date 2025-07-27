"""
Input Validation Middleware
Comprehensive input sanitization and validation for security
"""

import re
import html
import logging
from typing import Any, Dict, List, Optional, Union
from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
import urllib.parse
import json
from datetime import datetime

logger = logging.getLogger(__name__)

class InputValidator:
    """Comprehensive input validation and sanitization"""
    
    def __init__(self):
        # XSS patterns to detect and block
        self.xss_patterns = [
            r'<script[^>]*>.*?</script>',
            r'javascript:',
            r'onload\s*=',
            r'onerror\s*=',
            r'onclick\s*=',
            r'onmouseover\s*=',
            r'onfocus\s*=',
            r'onblur\s*=',
            r'onchange\s*=',
            r'onsubmit\s*=',
            r'<iframe[^>]*>',
            r'<object[^>]*>',
            r'<embed[^>]*>',
            r'<link[^>]*>',
            r'<meta[^>]*>',
            r'data:text/html',
            r'vbscript:',
            r'expression\s*\(',
            r'url\s*\(',
            r'@import',
            r'<\s*img[^>]+src[^>]*=',
        ]
        
        # SQL injection patterns
        self.sql_patterns = [
            r'(\b(union|select|insert|update|delete|drop|create|alter|exec|execute)\b)',
            r'(\b(or|and)\b\s+\d+\s*=\s*\d+)',
            r'(\b(or|and)\b\s+[\'"].*[\'"])',
            r'(--|#|/\*|\*/)',
            r'(\bselect\b.*\bfrom\b)',
            r'(\bunion\b.*\bselect\b)',
            r'(\binsert\b.*\binto\b)',
            r'(\bupdate\b.*\bset\b)',
            r'(\bdelete\b.*\bfrom\b)',
            r'(\bdrop\b.*\btable\b)',
        ]
        
        # Command injection patterns
        self.cmd_patterns = [
            r'(\||&|;|\$\(|\`)',
            r'(\bcat\b|\bls\b|\bpwd\b|\bwhoami\b)',
            r'(\brm\b|\bmv\b|\bcp\b|\bchmod\b)',
            r'(\bcurl\b|\bwget\b|\bnc\b|\btelnet\b)',
            r'(\becho\b.*>\s*)',
            r'(\bsudo\b|\bsu\b)',
        ]
        
        # Path traversal patterns
        self.path_patterns = [
            r'\.\./',
            r'\.\.\\',
            r'%2e%2e%2f',
            r'%2e%2e%5c',
            r'%252e%252e%252f',
            r'/etc/passwd',
            r'/etc/shadow',
            r'\\windows\\system32',
        ]
        
        # Email validation pattern
        self.email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        
        # Phone validation pattern (international)
        self.phone_pattern = r'^\+?[1-9]\d{1,14}$'
        
        # URL validation pattern
        self.url_pattern = r'^https?://[^\s/$.?#].[^\s]*$'
        
        # Safe characters for different input types
        self.safe_patterns = {
            'alphanumeric': r'^[a-zA-Z0-9\s]+$',
            'alpha': r'^[a-zA-Z\s]+$',
            'numeric': r'^\d+$',
            'username': r'^[a-zA-Z0-9_-]+$',
            'filename': r'^[a-zA-Z0-9._-]+$',
            'slug': r'^[a-zA-Z0-9-]+$',
        }
        
    def sanitize_string(self, data: str, max_length: int = 1000, allow_html: bool = False) -> str:
        """Sanitize string input"""
        if not isinstance(data, str):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Input must be a string"
            )
        
        # Trim whitespace
        data = data.strip()
        
        # Check length
        if len(data) > max_length:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Input too long (max {max_length} characters)"
            )
        
        # HTML encode if not allowing HTML
        if not allow_html:
            data = html.escape(data)
        
        # Check for malicious patterns
        self._check_malicious_patterns(data)
        
        return data
    
    def validate_email(self, email: str) -> str:
        """Validate email format"""
        email = email.strip().lower()
        
        if not re.match(self.email_pattern, email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid email format"
            )
        
        # Additional email security checks
        if len(email) > 254:  # RFC 5321 limit
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email address too long"
            )
        
        return email
    
    def validate_phone(self, phone: str) -> str:
        """Validate phone number"""
        # Remove common formatting characters
        phone = re.sub(r'[\s\-\(\)]+', '', phone)
        
        if not re.match(self.phone_pattern, phone):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid phone number format"
            )
        
        return phone
    
    def validate_url(self, url: str) -> str:
        """Validate URL format and security"""
        url = url.strip()
        
        if not re.match(self.url_pattern, url, re.IGNORECASE):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid URL format"
            )
        
        # Security checks for URLs
        parsed = urllib.parse.urlparse(url)
        
        # Block localhost and private IPs in production
        if parsed.hostname:
            if parsed.hostname.lower() in ['localhost', '127.0.0.1', '0.0.0.0']:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Local URLs not allowed"
                )
            
            # Block private IP ranges
            if self._is_private_ip(parsed.hostname):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Private IP addresses not allowed"
                )
        
        return url
    
    def validate_filename(self, filename: str) -> str:
        """Validate filename for uploads"""
        filename = filename.strip()
        
        # Check for path traversal
        if '..' in filename or '/' in filename or '\\' in filename:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid filename"
            )
        
        # Check for valid filename pattern
        if not re.match(self.safe_patterns['filename'], filename):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Filename contains invalid characters"
            )
        
        # Check length
        if len(filename) > 255:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Filename too long"
            )
        
        return filename
    
    def validate_json_data(self, data: Dict[str, Any], max_depth: int = 10) -> Dict[str, Any]:
        """Validate and sanitize JSON data"""
        try:
            # Check JSON depth to prevent attacks
            self._check_json_depth(data, max_depth)
            
            # Recursively validate all string values
            return self._sanitize_json_recursive(data)
            
        except Exception as e:
            logger.warning(f"JSON validation error: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid JSON data"
            )
    
    def _check_malicious_patterns(self, data: str):
        """Check for malicious patterns in input"""
        data_lower = data.lower()
        
        # Check XSS patterns
        for pattern in self.xss_patterns:
            if re.search(pattern, data_lower, re.IGNORECASE):
                logger.warning(f"XSS pattern detected: {pattern}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Potentially malicious input detected"
                )
        
        # Check SQL injection patterns
        for pattern in self.sql_patterns:
            if re.search(pattern, data_lower, re.IGNORECASE):
                logger.warning(f"SQL injection pattern detected: {pattern}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Potentially malicious input detected"
                )
        
        # Check command injection patterns
        for pattern in self.cmd_patterns:
            if re.search(pattern, data_lower, re.IGNORECASE):
                logger.warning(f"Command injection pattern detected: {pattern}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Potentially malicious input detected"
                )
        
        # Check path traversal patterns
        for pattern in self.path_patterns:
            if re.search(pattern, data_lower, re.IGNORECASE):
                logger.warning(f"Path traversal pattern detected: {pattern}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Potentially malicious input detected"
                )
    
    def _is_private_ip(self, hostname: str) -> bool:
        """Check if hostname is a private IP address"""
        try:
            import ipaddress
            ip = ipaddress.ip_address(hostname)
            return ip.is_private
        except ValueError:
            return False
    
    def _check_json_depth(self, data: Any, max_depth: int, current_depth: int = 0):
        """Check JSON depth to prevent deeply nested attacks"""
        if current_depth > max_depth:
            raise ValueError("JSON too deeply nested")
        
        if isinstance(data, dict):
            for value in data.values():
                self._check_json_depth(value, max_depth, current_depth + 1)
        elif isinstance(data, list):
            for item in data:
                self._check_json_depth(item, max_depth, current_depth + 1)
    
    def _sanitize_json_recursive(self, data: Any) -> Any:
        """Recursively sanitize JSON data"""
        if isinstance(data, str):
            return self.sanitize_string(data, max_length=10000)
        elif isinstance(data, dict):
            return {key: self._sanitize_json_recursive(value) for key, value in data.items()}
        elif isinstance(data, list):
            return [self._sanitize_json_recursive(item) for item in data]
        else:
            return data
    
    def validate_search_query(self, query: str) -> str:
        """Validate search query input"""
        query = query.strip()
        
        # Limit length
        if len(query) > 200:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Search query too long"
            )
        
        # Basic sanitization
        query = html.escape(query)
        
        # Check for malicious patterns (less strict for search)
        dangerous_patterns = [
            r'<script',
            r'javascript:',
            r'onload\s*=',
            r'<iframe',
        ]
        
        for pattern in dangerous_patterns:
            if re.search(pattern, query, re.IGNORECASE):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid search query"
                )
        
        return query

# Global validator instance
input_validator = InputValidator()

class InputValidationMiddleware(BaseHTTPMiddleware):
    """Middleware for automatic input validation"""
    
    def __init__(self, app):
        super().__init__(app)
        self.validator = input_validator
        
        # Endpoints that need special validation
        self.validation_rules = {
            '/api/v1/auth/register': {
                'email': 'email',
                'password': 'password',
                'name': 'name',
                'phone': 'phone'
            },
            '/api/v1/auth/login': {
                'username': 'email'
            },
            '/api/v1/jobs/search': {
                'q': 'search'
            },
            '/api/v1/profile': {
                'email': 'email',
                'phone': 'phone',
                'website': 'url'
            }
        }
    
    async def dispatch(self, request: Request, call_next):
        """Process request with input validation"""
        try:
            # Get request path
            path = request.url.path
            method = request.method
            
            # Skip validation for GET requests without query params
            if method == "GET" and not request.query_params:
                return await call_next(request)
            
            # Validate query parameters
            if request.query_params:
                await self._validate_query_params(request, path)
            
            # Validate request body for POST/PUT requests
            if method in ["POST", "PUT", "PATCH"]:
                await self._validate_request_body(request, path)
            
            response = await call_next(request)
            return response
            
        except HTTPException:
            raise
        except Exception as e:
            logger.warning(f"Input validation middleware error: {e}")
            # Continue without validation on error
            return await call_next(request)
    
    async def _validate_query_params(self, request: Request, path: str):
        """Validate query parameters"""
        for key, value in request.query_params.items():
            if key == 'q' and 'search' in path:
                # Special handling for search queries
                self.validator.validate_search_query(value)
            else:
                # General validation
                self.validator.sanitize_string(value, max_length=500)
    
    async def _validate_request_body(self, request: Request, path: str):
        """Validate request body"""
        try:
            # Get content type
            content_type = request.headers.get("content-type", "")
            
            if "application/json" in content_type:
                # Read and validate JSON body
                body = await request.body()
                if body:
                    try:
                        data = json.loads(body)
                        self.validator.validate_json_data(data)
                    except json.JSONDecodeError:
                        raise HTTPException(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Invalid JSON format"
                        )
            
        except HTTPException:
            raise
        except Exception as e:
            logger.warning(f"Request body validation error: {e}")

# Create middleware instance (placeholder - will be initialized when app is created)
input_validation_middleware = None

# Initialize middleware instance
def initialize_input_validation_middleware(app):
    """Initialize input validation middleware instance with app"""
    global input_validation_middleware
    
    input_validation_middleware = InputValidationMiddleware(app)
    
    return input_validation_middleware

# Utility functions for manual validation
def validate_email(email: str) -> str:
    """Validate email - utility function"""
    return input_validator.validate_email(email)

def validate_phone(phone: str) -> str:
    """Validate phone - utility function"""
    return input_validator.validate_phone(phone)

def validate_url(url: str) -> str:
    """Validate URL - utility function"""
    return input_validator.validate_url(url)

def sanitize_string(data: str, max_length: int = 1000, allow_html: bool = False) -> str:
    """Sanitize string - utility function"""
    return input_validator.sanitize_string(data, max_length, allow_html)

def validate_search_query(query: str) -> str:
    """Validate search query - utility function"""
    return input_validator.validate_search_query(query)

# Security headers middleware
class SecurityHeadersMiddleware:
    """Add security headers to responses"""
    
    async def __call__(self, request: Request, call_next):
        response = await call_next(request)
        
        # Add security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        
        # CSP header
        csp = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: https:; "
            "font-src 'self' https:; "
            "connect-src 'self' https:; "
            "frame-ancestors 'none'"
        )
        response.headers["Content-Security-Policy"] = csp
        
        return response

# Create security headers middleware instance
security_headers_middleware = SecurityHeadersMiddleware()