"""
Authentication Middleware
Handles JWT token validation and user authentication
"""

import logging
from typing import Optional, Dict, Any
from datetime import datetime, UTC
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
import jwt
from jwt.exceptions import InvalidTokenError, ExpiredSignatureError

logger = logging.getLogger(__name__)


class AuthMiddleware:
    """Authentication middleware for JWT token validation"""
    
    def __init__(self, secret_key: str = None):
        self.secret_key = secret_key or "test-secret-key"
        self.algorithm = "HS256"
        
    async def __call__(self, request: Request, call_next):
        """Process request and validate authentication"""
        try:
            # Skip authentication for public endpoints
            if self._is_public_endpoint(request.url.path):
                return await call_next(request)
            
            # Extract token from headers
            token = self._extract_token(request)
            if not token:
                return self._create_unauthorized_response("No token provided")
            
            # Validate token
            user_data = self._validate_token(token)
            if not user_data:
                return self._create_unauthorized_response("Invalid token")
            
            # Add user data to request state
            request.state.user = user_data
            
            # Continue with the request
            response = await call_next(request)
            return response
            
        except ExpiredSignatureError:
            return self._create_unauthorized_response("Token expired")
        except InvalidTokenError:
            return self._create_unauthorized_response("Invalid token format")
        except Exception as e:
            logger.error(f"Authentication error: {e}")
            return self._create_unauthorized_response("Authentication failed")
    
    def _is_public_endpoint(self, path: str) -> bool:
        """Check if endpoint is public (no auth required)"""
        public_paths = [
            "/api/v1/health",
            "/api/v1/docs",
            "/api/v1/openapi.json",
            "/api/v1/auth/login",
            "/api/v1/auth/register",
            "/api/v1/jobs",
            "/api/v1/jobs/search",
            "/api/v1/companies",
            "/api/v1/ads",
            "/api/v1/ads/search"
        ]
        
        # Check exact matches
        if path in public_paths:
            return True
        
        # Check pattern matches
        for public_path in public_paths:
            if path.startswith(public_path):
                return True
        
        return False
    
    def _extract_token(self, request: Request) -> Optional[str]:
        """Extract JWT token from request headers"""
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            return None
        
        # Check for Bearer token
        if auth_header.startswith("Bearer "):
            return auth_header[7:]  # Remove "Bearer " prefix
        
        return None
    
    def _validate_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Validate JWT token and return user data"""
        try:
            payload = jwt.decode(
                token, 
                self.secret_key, 
                algorithms=[self.algorithm]
            )
            
            # Check if token is expired
            exp = payload.get("exp")
            if exp and datetime.now(UTC).timestamp() > exp:
                raise ExpiredSignatureError("Token expired")
            
            # Return user data
            return {
                "user_id": payload.get("sub"),
                "email": payload.get("email"),
                "role": payload.get("role", "user"),
                "permissions": payload.get("permissions", [])
            }
            
        except (InvalidTokenError, ExpiredSignatureError):
            raise
        except Exception as e:
            logger.error(f"Token validation error: {e}")
            return None
    
    def _create_unauthorized_response(self, message: str) -> JSONResponse:
        """Create unauthorized response"""
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={
                "error": "Unauthorized",
                "message": message,
                "timestamp": datetime.now(UTC).isoformat()
            }
        )
    
    def create_token(self, user_data: Dict[str, Any], expires_in: int = 3600) -> str:
        """Create JWT token for user"""
        try:
            payload = {
                "sub": str(user_data.get("_id") or user_data.get("user_id")),
                "email": user_data.get("email"),
                "role": user_data.get("role", "user"),
                "permissions": user_data.get("permissions", []),
                "exp": datetime.now(UTC).timestamp() + expires_in,
                "iat": datetime.now(UTC).timestamp()
            }
            
            token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
            return token
            
        except Exception as e:
            logger.error(f"Error creating token: {e}")
            raise
    
    def verify_permissions(self, user_data: Dict[str, Any], required_permissions: list) -> bool:
        """Verify user has required permissions"""
        if not user_data:
            return False
        
        user_permissions = user_data.get("permissions", [])
        user_role = user_data.get("role", "user")
        
        # Admin role has all permissions
        if user_role == "admin":
            return True
        
        # Check if user has all required permissions
        for permission in required_permissions:
            if permission not in user_permissions:
                return False
        
        return True


# Global auth middleware instance
auth_middleware = AuthMiddleware()


def get_current_user(request: Request) -> Dict[str, Any]:
    """Get current user from request state"""
    user = getattr(request.state, "user", None)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not authenticated"
        )
    return user


def require_auth(required_permissions: list = None):
    """Decorator to require authentication"""
    def decorator(func):
        async def wrapper(request: Request, *args, **kwargs):
            user = get_current_user(request)
            
            if required_permissions:
                if not auth_middleware.verify_permissions(user, required_permissions):
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="Insufficient permissions"
                    )
            
            return await func(request, *args, **kwargs)
        return wrapper
    return decorator


def require_role(required_role: str):
    """Decorator to require specific role"""
    def decorator(func):
        async def wrapper(request: Request, *args, **kwargs):
            user = get_current_user(request)
            
            if user.get("role") != required_role:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Role '{required_role}' required"
                )
            
            return await func(request, *args, **kwargs)
        return wrapper
    return decorator 