import pytest
from unittest.mock import Mock, patch
from pydantic import ValidationError
from backend.schemas.user import UserCreate, UserUpdate, UserLogin, UserResponse

class TestUserSchemas:
    """Test user schemas comprehensively"""
    
    def test_user_create_valid(self):
        """Test valid user creation schema"""
        user_data = {
            "email": "test@example.com",
            "password": "password123",
            "name": "Test User"
        }
        user = UserCreate(**user_data)
        assert user.email == "test@example.com"
        assert user.password == "password123"
        
    def test_user_create_invalid_email(self):
        """Test user creation with invalid email"""
        with pytest.raises(ValidationError):
            UserCreate(email="invalid-email", password="password123")
            
    def test_user_create_weak_password(self):
        """Test user creation with weak password"""
        with pytest.raises(ValidationError):
            UserCreate(email="test@example.com", password="123")
            
    def test_user_update_partial(self):
        """Test partial user update"""
        update_data = {"name": "Updated Name"}
        user_update = UserUpdate(**update_data)
        assert user_update.name == "Updated Name"
        assert user_update.email is None
        
    def test_user_login_schema(self):
        """Test user login schema"""
        login_data = {"email": "test@example.com", "password": "password123"}
        user_login = UserLogin(**login_data)
        assert user_login.email == "test@example.com"
        
    def test_user_response_schema(self):
        """Test user response schema"""
        response_data = {
            "id": "123",
            "email": "test@example.com", 
            "name": "Test User",
            "is_active": True
        }
        user_response = UserResponse(**response_data)
        assert user_response.id == "123"
        assert user_response.email == "test@example.com"
        
    def test_user_schema_serialization(self):
        """Test user schema serialization"""
        user = UserCreate(email="test@example.com", password="password123")
        user_dict = user.model_dump()
        assert "email" in user_dict
        assert "password" in user_dict
