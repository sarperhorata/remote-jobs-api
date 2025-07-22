"""
Input validation middleware for security
"""
import re
import logging
from typing import Dict, Any, List
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)

class InputValidationMiddleware:
    """Middleware for validating and sanitizing input data"""
    
    def __init__(self):
        # SQL injection patterns
        self.sql_patterns = [
            r"(\b(union|select|insert|update|delete|drop|create|alter|exec|execute|script)\b)",
            r"(\b(or|and)\b\s+\d+\s*=\s*\d+)",
            r"(\b(union|select|insert|update|delete|drop|create|alter|exec|execute|script)\b.*\b(union|select|insert|update|delete|drop|create|alter|exec|execute|script)\b)",
            r"(--|#|/\*|\*/)",
            r"(\b(xp_|sp_)\w+)",
            r"(\b(cast|convert)\b)",
            r"(\b(declare|set)\b)",
        ]
        
        # XSS patterns
        self.xss_patterns = [
            r"<script[^>]*>.*?</script>",
            r"<iframe[^>]*>.*?</iframe>",
            r"<object[^>]*>.*?</object>",
            r"<embed[^>]*>.*?</embed>",
            r"<applet[^>]*>.*?</applet>",
            r"<form[^>]*>.*?</form>",
            r"<input[^>]*>",
            r"<textarea[^>]*>.*?</textarea>",
            r"<select[^>]*>.*?</select>",
            r"<button[^>]*>.*?</button>",
            r"<link[^>]*>",
            r"<meta[^>]*>",
            r"<style[^>]*>.*?</style>",
            r"<link[^>]*>",
            r"javascript:",
            r"vbscript:",
            r"onload\s*=",
            r"onerror\s*=",
            r"onclick\s*=",
            r"onmouseover\s*=",
            r"onfocus\s*=",
            r"onblur\s*=",
        ]
        
        # Path traversal patterns
        self.path_traversal_patterns = [
            r"\.\./",
            r"\.\.\\",
            r"\.\.%2f",
            r"\.\.%5c",
            r"\.\.%2e%2e",
            r"\.\.%252e%252e",
            r"\.\.%c0%af",
            r"\.\.%c1%9c",
        ]
        
        # Command injection patterns
        self.command_injection_patterns = [
            r"[;&|`$(){}[\]]",
            r"\b(cat|ls|pwd|whoami|id|uname|hostname|ps|top|kill|rm|cp|mv|chmod|chown|sudo|su|ssh|scp|wget|curl|nc|netcat|telnet|ftp|sftp)\b",
            r"\b(echo|printf|grep|sed|awk|cut|sort|uniq|head|tail|less|more|vi|vim|nano|emacs)\b",
            r"\b(python|perl|ruby|php|bash|sh|zsh|tcsh|ksh|fish)\b",
        ]
        
        # Compile patterns for better performance
        self.sql_regex = re.compile("|".join(self.sql_patterns), re.IGNORECASE)
        self.xss_regex = re.compile("|".join(self.xss_patterns), re.IGNORECASE)
        self.path_traversal_regex = re.compile("|".join(self.path_traversal_patterns), re.IGNORECASE)
        self.command_injection_regex = re.compile("|".join(self.command_injection_patterns), re.IGNORECASE)
    
    async def __call__(self, request: Request, call_next):
        """Validate input data before processing"""
        try:
            # Validate query parameters
            await self._validate_query_params(request)
            
            # Validate path parameters
            await self._validate_path_params(request)
            
            # Validate headers
            await self._validate_headers(request)
            
            # Validate body for POST/PUT requests
            if request.method in ["POST", "PUT", "PATCH"]:
                await self._validate_request_body(request)
            
            response = await call_next(request)
            return response
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Input validation error: {e}")
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"detail": "Invalid input data"}
            )
    
    async def _validate_query_params(self, request: Request):
        """Validate query parameters"""
        for param_name, param_value in request.query_params.items():
            if isinstance(param_value, str):
                await self._validate_string(param_value, f"query parameter '{param_name}'")
    
    async def _validate_path_params(self, request: Request):
        """Validate path parameters"""
        for param_name, param_value in request.path_params.items():
            if isinstance(param_value, str):
                await self._validate_string(param_value, f"path parameter '{param_name}'")
    
    async def _validate_headers(self, request: Request):
        """Validate request headers"""
        for header_name, header_value in request.headers.items():
            if isinstance(header_value, str):
                # Skip validation for certain headers
                if header_name.lower() in ["user-agent", "accept", "accept-language", "accept-encoding"]:
                    continue
                await self._validate_string(header_value, f"header '{header_name}'")
    
    async def _validate_request_body(self, request: Request):
        """Validate request body"""
        try:
            # Get the raw body
            body = await request.body()
            if body:
                body_str = body.decode('utf-8', errors='ignore')
                await self._validate_string(body_str, "request body")
        except Exception as e:
            logger.warning(f"Could not validate request body: {e}")
    
    async def _validate_string(self, value: str, context: str):
        """Validate a string value for various security threats"""
        if not isinstance(value, str):
            return
        
        # Check for SQL injection
        if self.sql_regex.search(value):
            logger.warning(f"Potential SQL injection detected in {context}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid input in {context}"
            )
        
        # Check for XSS
        if self.xss_regex.search(value):
            logger.warning(f"Potential XSS detected in {context}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid input in {context}"
            )
        
        # Check for path traversal
        if self.path_traversal_regex.search(value):
            logger.warning(f"Potential path traversal detected in {context}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid input in {context}"
            )
        
        # Check for command injection
        if self.command_injection_regex.search(value):
            logger.warning(f"Potential command injection detected in {context}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid input in {context}"
            )
    
    def sanitize_string(self, value: str) -> str:
        """Sanitize a string by removing dangerous characters"""
        if not isinstance(value, str):
            return value
        
        # Remove HTML tags
        value = re.sub(r'<[^>]*>', '', value)
        
        # Remove script tags and their content
        value = re.sub(r'<script[^>]*>.*?</script>', '', value, flags=re.IGNORECASE | re.DOTALL)
        
        # Remove dangerous attributes
        value = re.sub(r'\s*on\w+\s*=\s*["\'][^"\']*["\']', '', value, flags=re.IGNORECASE)
        
        # Remove javascript: and vbscript: protocols
        value = re.sub(r'javascript:', '', value, flags=re.IGNORECASE)
        value = re.sub(r'vbscript:', '', value, flags=re.IGNORECASE)
        
        return value.strip()
    
    def validate_email(self, email: str) -> bool:
        """Validate email format"""
        if not email:
            return False
        
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    def validate_url(self, url: str) -> bool:
        """Validate URL format"""
        if not url:
            return False
        
        pattern = r'^https?://[^\s/$.?#].[^\s]*$'
        return bool(re.match(pattern, url))
    
    def validate_phone(self, phone: str) -> bool:
        """Validate phone number format"""
        if not phone:
            return False
        
        # Remove all non-digit characters
        digits_only = re.sub(r'\D', '', phone)
        
        # Check if it's a reasonable length (7-15 digits)
        return 7 <= len(digits_only) <= 15
    
    def validate_password_strength(self, password: str) -> Dict[str, Any]:
        """Validate password strength"""
        if not password:
            return {"valid": False, "errors": ["Password cannot be empty"]}
        
        errors = []
        
        if len(password) < 8:
            errors.append("Password must be at least 8 characters long")
        
        if not re.search(r'[A-Z]', password):
            errors.append("Password must contain at least one uppercase letter")
        
        if not re.search(r'[a-z]', password):
            errors.append("Password must contain at least one lowercase letter")
        
        if not re.search(r'\d', password):
            errors.append("Password must contain at least one digit")
        
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            errors.append("Password must contain at least one special character")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "strength": self._calculate_password_strength(password)
        }
    
    def _calculate_password_strength(self, password: str) -> str:
        """Calculate password strength"""
        score = 0
        
        # Length
        if len(password) >= 8:
            score += 1
        if len(password) >= 12:
            score += 1
        
        # Character types
        if re.search(r'[A-Z]', password):
            score += 1
        if re.search(r'[a-z]', password):
            score += 1
        if re.search(r'\d', password):
            score += 1
        if re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            score += 1
        
        # Complexity
        if len(set(password)) >= len(password) * 0.8:
            score += 1
        
        if score <= 2:
            return "weak"
        elif score <= 4:
            return "medium"
        elif score <= 6:
            return "strong"
        else:
            return "very_strong"

# Create singleton instance
input_validator = InputValidationMiddleware()