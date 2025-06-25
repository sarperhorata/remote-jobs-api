import pytest
from backend.schemas.user import UserCreate, UserLogin
from pydantic import ValidationError

class TestUserSchemasSimple:
    """Simple user schemas tests that work"""
    
    def test_user_create_with_valid_data(self):
        """Test user creation with valid data"""
        user_data = {
            "email": "test@example.com",
            "password": "password123"
        }
        user = UserCreate(**user_data)
        assert user.email == "test@example.com"
        
    def test_user_create_invalid_email_format(self):
        """Test user creation with invalid email"""
        with pytest.raises(ValidationError):
            UserCreate(email="not-an-email", password="password123")
            
    def test_user_login_schema_works(self):
        """Test user login schema"""
        login_data = {"email": "test@example.com", "password": "password123"}
        user_login = UserLogin(**login_data)
        assert user_login.email == "test@example.com"
        
    def test_user_schema_serialization_works(self):
        """Test user schema serialization"""
        user = UserCreate(email="test@example.com", password="password123")
        user_dict = user.model_dump()
        assert "email" in user_dict
        assert "password" in user_dict
        
    def test_user_schema_email_validation(self):
        """Test email validation works"""
        valid_emails = ["test@example.com", "user@domain.co.uk", "name+tag@gmail.com"]
        for email in valid_emails:
            user = UserCreate(email=email, password="password123")
            assert user.email == email
