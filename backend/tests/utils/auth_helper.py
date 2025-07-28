"""
Authentication Helper for Tests
Provides test authentication utilities
"""

import jwt
from datetime import datetime, UTC, timedelta
from typing import Dict, Any, Optional
from fastapi.testclient import TestClient


class TestAuthHelper:
    """Helper class for authentication in tests"""
    
    def __init__(self, secret_key: str = "test-secret-key"):
        self.secret_key = secret_key
        self.algorithm = "HS256"
    
    def create_test_token(
        self, 
        user_id: str = "test_user_id",
        email: str = "test@example.com",
        role: str = "user",
        permissions: list = None,
        expires_in: int = 3600
    ) -> str:
        """Create a test JWT token"""
        payload = {
            "sub": user_id,
            "email": email,
            "role": role,
            "permissions": permissions or [],
            "exp": datetime.now(UTC).timestamp() + expires_in,
            "iat": datetime.now(UTC).timestamp()
        }
        
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
    
    def create_admin_token(self, user_id: str = "admin_user_id") -> str:
        """Create admin test token"""
        return self.create_test_token(
            user_id=user_id,
            email="admin@example.com",
            role="admin",
            permissions=["admin", "read", "write", "delete"]
        )
    
    def create_user_token(self, user_id: str = "user_id") -> str:
        """Create regular user test token"""
        return self.create_test_token(
            user_id=user_id,
            email="user@example.com",
            role="user",
            permissions=["read", "write"]
        )
    
    def create_expired_token(self, user_id: str = "expired_user_id") -> str:
        """Create expired test token"""
        payload = {
            "sub": user_id,
            "email": "expired@example.com",
            "role": "user",
            "permissions": [],
            "exp": datetime.now(UTC).timestamp() - 3600,  # Expired 1 hour ago
            "iat": datetime.now(UTC).timestamp() - 7200
        }
        
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
    
    def create_invalid_token(self) -> str:
        """Create invalid test token"""
        return "invalid.token.here"
    
    def get_auth_headers(self, token: str) -> Dict[str, str]:
        """Get authorization headers for requests"""
        return {"Authorization": f"Bearer {token}"}
    
    def get_admin_headers(self) -> Dict[str, str]:
        """Get admin authorization headers"""
        token = self.create_admin_token()
        return self.get_auth_headers(token)
    
    def get_user_headers(self) -> Dict[str, str]:
        """Get user authorization headers"""
        token = self.create_user_token()
        return self.get_auth_headers(token)
    
    def get_expired_headers(self) -> Dict[str, str]:
        """Get expired token headers"""
        token = self.create_expired_token()
        return self.get_auth_headers(token)
    
    def get_invalid_headers(self) -> Dict[str, str]:
        """Get invalid token headers"""
        token = self.create_invalid_token()
        return self.get_auth_headers(token)
    
    def decode_token(self, token: str) -> Dict[str, Any]:
        """Decode JWT token"""
        try:
            return jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
        except jwt.InvalidTokenError:
            return {}
    
    def is_token_expired(self, token: str) -> bool:
        """Check if token is expired"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            exp = payload.get("exp")
            if exp:
                return datetime.now(UTC).timestamp() > exp
            return False
        except jwt.InvalidTokenError:
            return True


# Global test auth helper instance
test_auth_helper = TestAuthHelper()


def get_test_user_data(user_id: str = "test_user_id") -> Dict[str, Any]:
    """Get test user data"""
    return {
        "_id": user_id,
        "email": "test@example.com",
        "name": "Test User",
        "role": "user",
        "permissions": ["read", "write"],
        "is_active": True,
        "created_at": datetime.now(UTC).isoformat()
    }


def get_test_admin_data(admin_id: str = "admin_user_id") -> Dict[str, Any]:
    """Get test admin data"""
    return {
        "_id": admin_id,
        "email": "admin@example.com",
        "name": "Admin User",
        "role": "admin",
        "permissions": ["admin", "read", "write", "delete"],
        "is_active": True,
        "created_at": datetime.now(UTC).isoformat()
    }


def create_test_user_in_db(db, user_data: Dict[str, Any] = None) -> Dict[str, Any]:
    """Create test user in database"""
    if user_data is None:
        user_data = get_test_user_data()
    
    # Insert user into database
    result = db.users.insert_one(user_data)
    user_data["_id"] = str(result.inserted_id)
    
    return user_data


def create_test_admin_in_db(db, admin_data: Dict[str, Any] = None) -> Dict[str, Any]:
    """Create test admin in database"""
    if admin_data is None:
        admin_data = get_test_admin_data()
    
    # Insert admin into database
    result = db.users.insert_one(admin_data)
    admin_data["_id"] = str(result.inserted_id)
    
    return admin_data


def cleanup_test_users(db, user_ids: list):
    """Clean up test users from database"""
    if user_ids:
        db.users.delete_many({"_id": {"$in": user_ids}})


def assert_unauthorized_response(response):
    """Assert response is unauthorized"""
    assert response.status_code == 401
    assert "error" in response.json()
    assert response.json()["error"] == "Unauthorized"


def assert_forbidden_response(response):
    """Assert response is forbidden"""
    assert response.status_code == 403
    assert "detail" in response.json()


def assert_authorized_response(response):
    """Assert response is authorized (not 401/403)"""
    assert response.status_code not in [401, 403] 