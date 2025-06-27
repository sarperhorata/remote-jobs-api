import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta
from fastapi import HTTPException
from utils.auth import (
    verify_password,
    get_password_hash,
    create_access_token,
    verify_token,
    pwd_context
)


class TestPasswordFunctions:
    """Test password hashing and verification"""

    def test_get_password_hash_returns_string(self):
        """Test password hashing returns string"""
        password = "testpassword123"
        hashed = get_password_hash(password)
        
        assert isinstance(hashed, str)
        assert len(hashed) > 0
        assert hashed != password  # Should not be plain text

    def test_get_password_hash_different_for_same_password(self):
        """Test same password gets different hashes (salt)"""
        password = "testpassword123"
        hash1 = get_password_hash(password)
        hash2 = get_password_hash(password)
        
        # Should be different due to salt
        assert hash1 != hash2

    def test_verify_password_correct_password(self):
        """Test verify_password with correct password"""
        password = "testpassword123"
        hashed = get_password_hash(password)
        
        result = verify_password(password, hashed)
        assert result is True

    def test_verify_password_incorrect_password(self):
        """Test verify_password with incorrect password"""
        password = "testpassword123"
        wrong_password = "wrongpassword456"
        hashed = get_password_hash(password)
        
        result = verify_password(wrong_password, hashed)
        assert result is False

    def test_verify_password_empty_password(self):
        """Test verify_password with empty password"""
        password = "testpassword123"
        hashed = get_password_hash(password)
        
        result = verify_password("", hashed)
        assert result is False

    def test_verify_password_with_bcrypt_hash(self):
        """Test verify_password works with bcrypt hashes"""
        password = "testpassword123"
        # Use the context directly to ensure bcrypt
        hashed = pwd_context.hash(password)
        
        result = verify_password(password, hashed)
        assert result is True


class TestJWTFunctions:
    """Test JWT token functions"""

    def test_create_access_token_basic(self):
        """Test creating basic access token"""
        data = {"sub": "user123", "role": "user"}
        token = create_access_token(data)
        
        assert isinstance(token, str)
        assert len(token) > 0
        # JWT tokens have 3 parts separated by dots
        assert token.count('.') == 2

    def test_create_access_token_with_expiry(self):
        """Test creating token with custom expiry"""
        data = {"sub": "user123"}
        expires_delta = timedelta(minutes=60)
        
        token = create_access_token(data, expires_delta)
        assert isinstance(token, str)
        assert len(token) > 0

    def test_create_access_token_with_different_data(self):
        """Test creating tokens with different data"""
        data1 = {"sub": "user123", "role": "user"}
        data2 = {"sub": "admin456", "role": "admin"}
        
        token1 = create_access_token(data1)
        token2 = create_access_token(data2)
        
        assert token1 != token2

    def test_verify_token_valid_token(self):
        """Test verifying valid token"""
        data = {"sub": "user123", "role": "user"}
        token = create_access_token(data)
        
        payload = verify_token(token)
        
        assert isinstance(payload, dict)
        assert payload["sub"] == "user123"
        assert payload["role"] == "user"
        assert "exp" in payload

    def test_verify_token_invalid_token(self):
        """Test verifying invalid token"""
        invalid_token = "invalid.token.here"
        
        with pytest.raises(HTTPException) as exc_info:
            verify_token(invalid_token)
        
        assert exc_info.value.status_code == 401
        assert "Invalid token" in str(exc_info.value.detail)

    def test_verify_token_expired_token(self):
        """Test verifying expired token"""
        data = {"sub": "user123"}
        # Create token that expires immediately
        expires_delta = timedelta(seconds=-1)
        token = create_access_token(data, expires_delta)
        
        with pytest.raises(HTTPException) as exc_info:
            verify_token(token)
        
        assert exc_info.value.status_code == 401

    def test_verify_token_malformed_token(self):
        """Test verifying malformed token"""
        malformed_tokens = [
            "",
            "not.a.jwt",
            "header.payload",  # Missing signature
            "too.many.parts.here.invalid"
        ]
        
        for token in malformed_tokens:
            with pytest.raises(HTTPException) as exc_info:
                verify_token(token)
            
            assert exc_info.value.status_code == 401

    def test_token_roundtrip_consistency(self):
        """Test creating and verifying token maintains data"""
        original_data = {
            "sub": "user123",
            "role": "admin",
            "email": "test@example.com",
            "is_active": True
        }
        
        token = create_access_token(original_data)
        decoded_data = verify_token(token)
        
        # Check that original data is preserved
        for key, value in original_data.items():
            assert decoded_data[key] == value

    def test_create_access_token_includes_expiry(self):
        """Test that created tokens include expiry"""
        data = {"sub": "user123"}
        token = create_access_token(data)
        payload = verify_token(token)
        
        assert "exp" in payload
        assert isinstance(payload["exp"], int)
        
        # Should expire in the future
        exp_datetime = datetime.fromtimestamp(payload["exp"])
        assert exp_datetime > datetime.utcnow()

    @patch('utils.auth.datetime')
    def test_create_access_token_with_fixed_time(self, mock_datetime):
        """Test token creation with fixed time for consistency"""
        # Mock current time
        fixed_time = datetime(2024, 1, 1, 12, 0, 0)
        mock_datetime.utcnow.return_value = fixed_time
        
        data = {"sub": "user123"}
        expires_delta = timedelta(minutes=30)
        
        token = create_access_token(data, expires_delta)
        payload = verify_token(token)
        
        expected_exp = fixed_time + expires_delta
        token_exp = datetime.fromtimestamp(payload["exp"])
        
        # Allow some small variance
        assert abs((token_exp - expected_exp).total_seconds()) < 1


class TestAuthUtilityFunctions:
    """Test auth utility functions"""

    def test_password_hash_format(self):
        """Test password hash format"""
        password = "testpassword123"
        hashed = get_password_hash(password)
        
        # Bcrypt hashes start with $2b$
        assert hashed.startswith('$2b$')
        # Should be around 60 characters
        assert 50 < len(hashed) < 70

    def test_password_verification_edge_cases(self):
        """Test password verification edge cases"""
        password = "testpassword123"
        hashed = get_password_hash(password)
        
        # Test case sensitivity
        assert verify_password(password.upper(), hashed) is False
        assert verify_password(password.lower(), hashed) is False
        
        # Test with extra characters
        assert verify_password(password + "x", hashed) is False
        assert verify_password("x" + password, hashed) is False

    def test_jwt_token_structure(self):
        """Test JWT token has correct structure"""
        data = {"sub": "user123"}
        token = create_access_token(data)
        
        parts = token.split('.')
        assert len(parts) == 3
        
        # Each part should be base64-like (no whitespace)
        for part in parts:
            assert ' ' not in part
            assert '\n' not in part
            assert len(part) > 0 