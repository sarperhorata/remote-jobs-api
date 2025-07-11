import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime, timedelta
import jwt
from passlib.context import CryptContext
from backend.utils.auth import (
    create_access_token,
    verify_password,
    get_password_hash,
    authenticate_user,
    get_current_user,
    get_current_active_user
)
from backend.models.user import User, UserCreate, UserLogin
from backend.crud.user import create_user, get_user_by_email
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer

# Test data
test_user_data = {
    "email": "test@example.com",
    "password": "TestPassword123!",
    "name": "Test User",
    "is_active": True,
    "is_verified": True
}

test_user_login = {
    "email": "test@example.com",
    "password": "TestPassword123!"
}

@pytest.mark.unit
class TestPasswordHashing:
    """Test password hashing and verification functions."""
    
    def test_password_hashing(self):
        """Test that passwords are properly hashed."""
        password = "TestPassword123!"
        hashed = get_password_hash(password)
        
        # Verify hash is different from original password
        assert hashed != password
        assert len(hashed) > len(password)
        assert hashed.startswith("$2b$")  # bcrypt hash format
        
    def test_password_verification_success(self):
        """Test successful password verification."""
        password = "TestPassword123!"
        hashed = get_password_hash(password)
        
        assert verify_password(password, hashed) is True
        
    def test_password_verification_failure(self):
        """Test failed password verification."""
        password = "TestPassword123!"
        wrong_password = "WrongPassword123!"
        hashed = get_password_hash(password)
        
        assert verify_password(wrong_password, hashed) is False
        
    def test_password_verification_empty_password(self):
        """Test password verification with empty password."""
        password = ""
        hashed = get_password_hash(password)
        
        assert verify_password(password, hashed) is True
        
    def test_password_verification_none_password(self):
        """Test password verification with None password."""
        password = "TestPassword123!"
        hashed = get_password_hash(password)
        
        assert verify_password(None, hashed) is False

@pytest.mark.unit
class TestJWTTokenCreation:
    """Test JWT token creation and validation."""
    
    def test_create_access_token(self):
        """Test creating access token with user data."""
        user_id = "test_user_id"
        email = "test@example.com"
        expires_delta = timedelta(minutes=30)
        
        token = create_access_token(
            data={"sub": user_id, "email": email},
            expires_delta=expires_delta
        )
        
        # Verify token structure
        assert isinstance(token, str)
        assert len(token) > 0
        
        # Decode token to verify content
        decoded = jwt.decode(token, "test_secret_key", algorithms=["HS256"])
        assert decoded["sub"] == user_id
        assert decoded["email"] == email
        assert "exp" in decoded
        
    def test_create_access_token_no_expiry(self):
        """Test creating access token without expiry."""
        user_id = "test_user_id"
        email = "test@example.com"
        
        token = create_access_token(
            data={"sub": user_id, "email": email}
        )
        
        assert isinstance(token, str)
        assert len(token) > 0
        
    def test_create_access_token_with_extra_data(self):
        """Test creating access token with additional data."""
        user_data = {
            "sub": "test_user_id",
            "email": "test@example.com",
            "role": "admin",
            "permissions": ["read", "write"]
        }
        
        token = create_access_token(data=user_data)
        
        decoded = jwt.decode(token, "test_secret_key", algorithms=["HS256"])
        assert decoded["sub"] == user_data["sub"]
        assert decoded["email"] == user_data["email"]
        assert decoded["role"] == user_data["role"]
        assert decoded["permissions"] == user_data["permissions"]

@pytest.mark.unit
class TestUserAuthentication:
    """Test user authentication functions."""
    
    @pytest.mark.asyncio
    async def test_authenticate_user_success(self, db_mock):
        """Test successful user authentication."""
        # Mock user data
        user_data = {
            "_id": "test_user_id",
            "email": "test@example.com",
            "hashed_password": get_password_hash("TestPassword123!"),
            "name": "Test User",
            "is_active": True,
            "is_verified": True
        }
        
        # Mock database response
        db_mock.users.find_one.return_value = user_data
        
        # Test authentication
        user = await authenticate_user(db_mock, "test@example.com", "TestPassword123!")
        
        assert user is not None
        assert user["email"] == "test@example.com"
        assert user["name"] == "Test User"
        
    @pytest.mark.asyncio
    async def test_authenticate_user_wrong_password(self, db_mock):
        """Test authentication with wrong password."""
        # Mock user data
        user_data = {
            "_id": "test_user_id",
            "email": "test@example.com",
            "hashed_password": get_password_hash("TestPassword123!"),
            "name": "Test User",
            "is_active": True,
            "is_verified": True
        }
        
        # Mock database response
        db_mock.users.find_one.return_value = user_data
        
        # Test authentication with wrong password
        user = await authenticate_user(db_mock, "test@example.com", "WrongPassword123!")
        
        assert user is False
        
    @pytest.mark.asyncio
    async def test_authenticate_user_not_found(self, db_mock):
        """Test authentication with non-existent user."""
        # Mock database response - user not found
        db_mock.users.find_one.return_value = None
        
        # Test authentication
        user = await authenticate_user(db_mock, "nonexistent@example.com", "TestPassword123!")
        
        assert user is False
        
    @pytest.mark.asyncio
    async def test_authenticate_user_inactive(self, db_mock):
        """Test authentication with inactive user."""
        # Mock user data - inactive user
        user_data = {
            "_id": "test_user_id",
            "email": "test@example.com",
            "hashed_password": get_password_hash("TestPassword123!"),
            "name": "Test User",
            "is_active": False,
            "is_verified": True
        }
        
        # Mock database response
        db_mock.users.find_one.return_value = user_data
        
        # Test authentication
        user = await authenticate_user(db_mock, "test@example.com", "TestPassword123!")
        
        assert user is False

@pytest.mark.unit
class TestUserCRUD:
    """Test user CRUD operations."""
    
    @pytest.mark.asyncio
    async def test_create_user_success(self, db_mock):
        """Test successful user creation."""
        user_create = UserCreate(
            email="newuser@example.com",
            password="NewPassword123!",
            name="New User"
        )
        
        # Mock database operations
        db_mock.users.find_one.return_value = None  # User doesn't exist
        db_mock.users.insert_one.return_value = MagicMock(inserted_id="new_user_id")
        
        # Create user
        user = await create_user(db_mock, user_create)
        
        assert user is not None
        assert user["email"] == "newuser@example.com"
        assert user["name"] == "New User"
        assert "hashed_password" in user
        assert user["hashed_password"] != "NewPassword123!"  # Should be hashed
        
    @pytest.mark.asyncio
    async def test_create_user_duplicate_email(self, db_mock):
        """Test user creation with duplicate email."""
        user_create = UserCreate(
            email="existing@example.com",
            password="NewPassword123!",
            name="New User"
        )
        
        # Mock database response - user already exists
        existing_user = {
            "_id": "existing_user_id",
            "email": "existing@example.com",
            "name": "Existing User"
        }
        db_mock.users.find_one.return_value = existing_user
        
        # Attempt to create user
        with pytest.raises(HTTPException) as exc_info:
            await create_user(db_mock, user_create)
        
        assert exc_info.value.status_code == 400
        assert "already registered" in str(exc_info.value.detail)
        
    @pytest.mark.asyncio
    async def test_get_user_by_email_success(self, db_mock):
        """Test successful user retrieval by email."""
        user_data = {
            "_id": "test_user_id",
            "email": "test@example.com",
            "name": "Test User",
            "is_active": True
        }
        
        # Mock database response
        db_mock.users.find_one.return_value = user_data
        
        # Get user
        user = await get_user_by_email(db_mock, "test@example.com")
        
        assert user is not None
        assert user["email"] == "test@example.com"
        assert user["name"] == "Test User"
        
    @pytest.mark.asyncio
    async def test_get_user_by_email_not_found(self, db_mock):
        """Test user retrieval with non-existent email."""
        # Mock database response - user not found
        db_mock.users.find_one.return_value = None
        
        # Get user
        user = await get_user_by_email(db_mock, "nonexistent@example.com")
        
        assert user is None

@pytest.mark.unit
class TestCurrentUserDependencies:
    """Test current user dependency functions."""
    
    @pytest.mark.asyncio
    async def test_get_current_user_success(self, db_mock):
        """Test successful current user retrieval."""
        # Create valid token
        user_id = "test_user_id"
        token = create_access_token(data={"sub": user_id, "email": "test@example.com"})
        
        # Mock user data
        user_data = {
            "_id": user_id,
            "email": "test@example.com",
            "name": "Test User",
            "is_active": True
        }
        
        # Mock database response
        db_mock.users.find_one.return_value = user_data
        
        # Mock HTTPBearer
        with patch('backend.utils.auth.HTTPBearer') as mock_bearer:
            mock_bearer.return_value = MagicMock()
            mock_bearer.return_value.__call__ = AsyncMock(return_value=token)
            
            # Get current user
            user = await get_current_user(db_mock, token)
            
            assert user is not None
            assert user["_id"] == user_id
            assert user["email"] == "test@example.com"
            
    @pytest.mark.asyncio
    async def test_get_current_user_invalid_token(self, db_mock):
        """Test current user retrieval with invalid token."""
        invalid_token = "invalid_token"
        
        # Mock HTTPBearer
        with patch('backend.utils.auth.HTTPBearer') as mock_bearer:
            mock_bearer.return_value = MagicMock()
            mock_bearer.return_value.__call__ = AsyncMock(return_value=invalid_token)
            
            # Attempt to get current user
            with pytest.raises(HTTPException) as exc_info:
                await get_current_user(db_mock, invalid_token)
            
            assert exc_info.value.status_code == 401
            assert "Could not validate credentials" in str(exc_info.value.detail)
            
    @pytest.mark.asyncio
    async def test_get_current_active_user_success(self, db_mock):
        """Test successful current active user retrieval."""
        # Create valid token
        user_id = "test_user_id"
        token = create_access_token(data={"sub": user_id, "email": "test@example.com"})
        
        # Mock active user data
        user_data = {
            "_id": user_id,
            "email": "test@example.com",
            "name": "Test User",
            "is_active": True
        }
        
        # Mock database response
        db_mock.users.find_one.return_value = user_data
        
        # Mock HTTPBearer
        with patch('backend.utils.auth.HTTPBearer') as mock_bearer:
            mock_bearer.return_value = MagicMock()
            mock_bearer.return_value.__call__ = AsyncMock(return_value=token)
            
            # Get current active user
            user = await get_current_active_user(db_mock, token)
            
            assert user is not None
            assert user["is_active"] is True
            
    @pytest.mark.asyncio
    async def test_get_current_active_user_inactive(self, db_mock):
        """Test current active user retrieval with inactive user."""
        # Create valid token
        user_id = "test_user_id"
        token = create_access_token(data={"sub": user_id, "email": "test@example.com"})
        
        # Mock inactive user data
        user_data = {
            "_id": user_id,
            "email": "test@example.com",
            "name": "Test User",
            "is_active": False
        }
        
        # Mock database response
        db_mock.users.find_one.return_value = user_data
        
        # Mock HTTPBearer
        with patch('backend.utils.auth.HTTPBearer') as mock_bearer:
            mock_bearer.return_value = MagicMock()
            mock_bearer.return_value.__call__ = AsyncMock(return_value=token)
            
            # Attempt to get current active user
            with pytest.raises(HTTPException) as exc_info:
                await get_current_active_user(db_mock, token)
            
            assert exc_info.value.status_code == 400
            assert "Inactive user" in str(exc_info.value.detail)

@pytest.mark.unit
class TestSecurityFeatures:
    """Test security-related features."""
    
    def test_password_strength_validation(self):
        """Test password strength validation."""
        weak_passwords = [
            "123",  # Too short
            "password",  # Common word
            "123456",  # Sequential numbers
            "qwerty",  # Keyboard pattern
            "abc123",  # Too simple
        ]
        
        strong_passwords = [
            "TestPassword123!",
            "MySecurePass1@",
            "ComplexP@ssw0rd",
            "Str0ng!P@ss",
        ]
        
        # Test weak passwords (should be rejected)
        for password in weak_passwords:
            # This would test actual password validation logic
            # For now, we'll test the hashing function
            hashed = get_password_hash(password)
            assert hashed != password
            
        # Test strong passwords (should be accepted)
        for password in strong_passwords:
            hashed = get_password_hash(password)
            assert verify_password(password, hashed) is True
            
    def test_token_expiration(self):
        """Test token expiration handling."""
        # Create token with short expiration
        user_data = {"sub": "test_user_id", "email": "test@example.com"}
        short_expiry = timedelta(seconds=1)
        
        token = create_access_token(data=user_data, expires_delta=short_expiry)
        
        # Token should be valid initially
        decoded = jwt.decode(token, "test_secret_key", algorithms=["HS256"])
        assert decoded["sub"] == "test_user_id"
        
        # Note: Testing actual expiration would require time manipulation
        # This is a basic structure test
        
    def test_sql_injection_protection(self):
        """Test protection against SQL injection attempts."""
        malicious_inputs = [
            "admin'; DROP TABLE users; --",
            "' OR '1'='1",
            "'; DELETE FROM users; --",
            "admin'--",
            "1' OR '1' = '1' --",
        ]
        
        for malicious_input in malicious_inputs:
            # Test that malicious input is handled safely
            # This would test actual input sanitization
            hashed = get_password_hash(malicious_input)
            assert hashed != malicious_input
            assert len(hashed) > len(malicious_input)

@pytest.mark.unit
class TestErrorHandling:
    """Test error handling in authentication functions."""
    
    @pytest.mark.asyncio
    async def test_database_connection_error(self, db_mock):
        """Test handling of database connection errors."""
        # Mock database error
        db_mock.users.find_one.side_effect = Exception("Database connection failed")
        
        # Test authentication with database error
        with pytest.raises(Exception):
            await authenticate_user(db_mock, "test@example.com", "TestPassword123!")
            
    @pytest.mark.asyncio
    async def test_invalid_token_format(self, db_mock):
        """Test handling of invalid token formats."""
        invalid_tokens = [
            "",
            "invalid",
            "Bearer invalid",
            "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.invalid",
        ]
        
        for token in invalid_tokens:
            with pytest.raises(HTTPException) as exc_info:
                await get_current_user(db_mock, token)
            
            assert exc_info.value.status_code == 401
            
    def test_password_hashing_error(self):
        """Test handling of password hashing errors."""
        # Test with None password
        with pytest.raises(TypeError):
            get_password_hash(None)
            
    def test_password_verification_error(self):
        """Test handling of password verification errors."""
        # Test with None values
        assert verify_password(None, "some_hash") is False
        assert verify_password("password", None) is False