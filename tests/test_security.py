import pytest
from unittest.mock import patch, MagicMock
from fastapi import HTTPException, status
from fastapi.security import HTTPBearer

pytestmark = pytest.mark.asyncio
from backend.core.security import (
    get_current_user,
    create_access_token,
    verify_password,
    get_password_hash
)

# Mock database and user data
mock_user = {
    "_id": "test_user_id",
    "email": "test@example.com",
    "name": "Test User",
    "is_active": True,
    "is_superuser": False,
    "email_verified": True
}

mock_superuser = {
    "_id": "test_superuser_id", 
    "email": "admin@example.com",
    "name": "Admin User",
    "is_active": True,
    "is_superuser": True,
    "email_verified": True
}

mock_inactive_user = {
    "_id": "test_inactive_user_id",
    "email": "inactive@example.com", 
    "name": "Inactive User",
    "is_active": False,
    "is_superuser": False,
    "email_verified": True
}

class TestSecurity:
    """Test security functions"""
    
    def test_verify_password_success(self):
        """Test successful password verification"""
        # Hash a password
        hashed_password = get_password_hash("test_password")
        
        # Verify the password
        result = verify_password("test_password", hashed_password)
        
        assert result is True
    
    def test_verify_password_failure(self):
        """Test failed password verification"""
        # Hash a password
        hashed_password = get_password_hash("test_password")
        
        # Verify with wrong password
        result = verify_password("wrong_password", hashed_password)
        
        assert result is False
    
    def test_get_password_hash(self):
        """Test password hashing"""
        # Hash a password
        hashed_password = get_password_hash("test_password")
        
        # Should not be the same as original
        assert hashed_password != "test_password"
        
        # Should be a string
        assert isinstance(hashed_password, str)
        
        # Should be different each time (due to salt)
        hashed_password2 = get_password_hash("test_password")
        assert hashed_password != hashed_password2
    
    @patch('backend.core.security.jwt.encode')
    @patch('backend.core.security.get_settings')
    def test_create_access_token(self, mock_get_settings, mock_jwt_encode):
        """Test access token creation"""
        # Mock settings
        mock_settings = MagicMock()
        mock_settings.SECRET_KEY = "test_secret"
        mock_settings.ALGORITHM = "HS256"
        mock_settings.ACCESS_TOKEN_EXPIRE_MINUTES = 30
        mock_get_settings.return_value = mock_settings
        
        # Mock JWT encode
        mock_jwt_encode.return_value = "test_token"
        
        # Test function
        result = create_access_token(data={"sub": "test@example.com"})
        
        assert result == "test_token"
        mock_jwt_encode.assert_called_once()
    
    @patch('backend.core.security.jwt.encode')
    def test_create_access_token_with_expires_delta(self, mock_jwt_encode):
        """Test access token creation with custom expiration"""
        from datetime import timedelta
        
        # Mock JWT encode
        mock_jwt_encode.return_value = "test_token"
        
        # Test function with custom expiration
        result = create_access_token(
            data={"sub": "test@example.com"}, 
            expires_delta=timedelta(minutes=60)
        )
        
        assert result == "test_token"
        mock_jwt_encode.assert_called_once()