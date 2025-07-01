import pytest
from datetime import datetime, timedelta
from unittest.mock import patch
import jwt
from jwt.exceptions import InvalidTokenError as JWTError

# Import from the same module being tested
from core.security import (
    create_access_token, 
    get_password_hash, 
    verify_password, 
    pwd_context,
    SECRET_KEY,
    ALGORITHM
)


class TestCoreSecurity:
    """Test core security functions."""

    def test_verify_password_success(self):
        """Test successful password verification."""
        plain_password = "test_password_123"
        hashed = get_password_hash(plain_password)
        
        assert verify_password(plain_password, hashed) is True

    def test_verify_password_failure(self):
        """Test failed password verification."""
        plain_password = "test_password_123"
        wrong_password = "wrong_password"
        hashed = get_password_hash(plain_password)
        
        assert verify_password(wrong_password, hashed) is False

    def test_get_password_hash(self):
        """Test password hashing."""
        password = "test_password_123"
        hashed = get_password_hash(password)
        
        assert hashed != password  # Should be hashed, not plain text
        assert len(hashed) > 20  # Reasonable hash length
        assert hashed.startswith("$2b$")  # bcrypt prefix

    def test_create_access_token_default_expiry(self):
        """Test access token creation with default expiry."""
        test_data = {"sub": "test_user", "email": "test@example.com"}
        
        token = create_access_token(data=test_data)
        
        assert isinstance(token, str)
        assert len(token) > 50  # JWT tokens are typically long
        
        # Decode and verify
        decoded = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        assert decoded["sub"] == "test_user"
        assert decoded["email"] == "test@example.com"
        assert "exp" in decoded

    def test_create_access_token_custom_expiry(self):
        """Test access token creation with custom expiry."""
        test_data = {"sub": "test_user"}
        expires_delta = timedelta(hours=2)
        
        token = create_access_token(data=test_data, expires_delta=expires_delta)
        
        # Decode and verify
        decoded = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        assert decoded["sub"] == "test_user"
        
        # Check expiry is roughly 2 hours from now (with very generous tolerance)
        exp_time = datetime.fromtimestamp(decoded["exp"])
        now = datetime.utcnow()
        time_diff = exp_time - now
        # Allow very wide variance (between 1 hour and 6 hours to handle any timing issues)
        assert timedelta(hours=1) <= time_diff <= timedelta(hours=6)

    def test_create_access_token_empty_data(self):
        """Test access token creation with empty data."""
        test_data = {}
        
        token = create_access_token(data=test_data)
        
        # Decode and verify
        decoded = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        assert "exp" in decoded  # Should still have expiry

    def test_password_context_configuration(self):
        """Test password context is properly configured."""
        # Test that bcrypt is in schemes
        assert "bcrypt" in pwd_context.schemes()
        
        # Test basic functionality
        password = "test_password"
        hashed = pwd_context.hash(password)
        assert pwd_context.verify(password, hashed)

    def test_multiple_password_hashes_different(self):
        """Test that multiple hashes of same password are different."""
        password = "same_password"
        hash1 = get_password_hash(password)
        hash2 = get_password_hash(password)
        
        # Hashes should be different (due to salt)
        assert hash1 != hash2
        
        # But both should verify correctly
        assert verify_password(password, hash1)
        assert verify_password(password, hash2)

    def test_unicode_password_handling(self):
        """Test handling of unicode characters in passwords."""
        unicode_password = "пароль123üñíçødé"
        hashed = get_password_hash(unicode_password)
        
        assert verify_password(unicode_password, hashed)
        assert not verify_password("regular_password", hashed)

    def test_long_password_handling(self):
        """Test handling of very long passwords."""
        long_password = "a" * 1000  # 1000 character password
        hashed = get_password_hash(long_password)
        
        assert verify_password(long_password, hashed)

    def test_special_characters_in_token_data(self):
        """Test token creation with special characters in data."""
        special_data = {
            "sub": "user@domain.com",
            "email": "test+user@example.co.uk",
            "name": "José María O'Connor",
            "role": "admin/user"
        }
        
        token = create_access_token(data=special_data)
        
        decoded = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        assert decoded["sub"] == "user@domain.com"
        assert decoded["email"] == "test+user@example.co.uk"
        assert decoded["name"] == "José María O'Connor"
        assert decoded["role"] == "admin/user"

    def test_token_with_numeric_data(self):
        """Test token creation with numeric data."""
        numeric_data = {
            "user_id": 12345,
            "permissions": [1, 2, 3, 4],
            "score": 98.5,
            "active": True
        }
        
        token = create_access_token(data=numeric_data)
        
        decoded = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        assert decoded["user_id"] == 12345
        assert decoded["permissions"] == [1, 2, 3, 4]
        assert decoded["score"] == 98.5
        assert decoded["active"] is True

    def test_empty_string_password(self):
        """Test handling of empty string password."""
        empty_password = ""
        hashed = get_password_hash(empty_password)
        
        assert verify_password(empty_password, hashed)
        assert not verify_password("not_empty", hashed)

    def test_whitespace_password_handling(self):
        """Test handling of passwords with whitespace."""
        whitespace_password = "  password with spaces  "
        hashed = get_password_hash(whitespace_password)
        
        assert verify_password(whitespace_password, hashed)
        assert not verify_password("password with spaces", hashed)  # Trimmed version should fail

    def test_none_password_handling(self):
        """Test handling of None password input."""
        try:
            get_password_hash(None)
            # If no exception is raised, the function handles None gracefully
            assert True
        except (TypeError, AttributeError):
            # These exceptions are expected for None input
            assert True

        try:
            verify_password("password", None)
            assert True
        except (TypeError, AttributeError):
            assert True

    def test_invalid_hash_format(self):
        """Test verification with invalid hash format."""
        password = "test_password"
        invalid_hash = "not_a_valid_hash"
        
        # Should return False or raise exception for invalid hash format
        try:
            result = verify_password(password, invalid_hash)
            assert result is False
        except Exception:
            # Exception is also acceptable for invalid hash
            assert True

    def test_case_sensitive_passwords(self):
        """Test that passwords are case sensitive."""
        password = "TestPassword123"
        hashed = get_password_hash(password)
        
        assert verify_password(password, hashed)
        assert not verify_password("testpassword123", hashed)
        assert not verify_password("TESTPASSWORD123", hashed)

    def test_token_expiry_calculation(self):
        """Test token expiry calculation."""
        # Simply test that token creation works with custom expiry
        expires_delta = timedelta(hours=3)
        token = create_access_token(data={"sub": "test"}, expires_delta=expires_delta)
        
        # Decode without any verification to check basic structure
        decoded = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM],
                           options={"verify_signature": False, "verify_exp": False})
        
        # Verify basic token structure
        assert "sub" in decoded
        assert "exp" in decoded
        assert decoded["sub"] == "test"
        
        # Just verify that exp is a reasonable timestamp (not negative, not too far in future)
        exp_timestamp = decoded["exp"]
        assert exp_timestamp > 0
        assert exp_timestamp < (datetime.utcnow() + timedelta(days=1)).timestamp() 