import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from fastapi import HTTPException, status
from fastapi.testclient import TestClient
from backend.routes.auth import router
from backend.main import app
from backend.models.user import UserCreate, UserResponse
from backend.core.security import get_password_hash

pytestmark = pytest.mark.asyncio

class TestAuth:
    """Test authentication routes"""
    
    def test_register_user_success(self):
        """Test successful user registration"""
        with patch('backend.routes.auth.get_async_db') as mock_get_db:
            # Mock database
            mock_db = MagicMock()
            mock_db.users.find_one.return_value = None  # User doesn't exist
            mock_db.users.insert_one.return_value.inserted_id = "user123"
            mock_get_db.return_value = mock_db
            
            # Create test client
            test_app = app
            test_app.include_router(router, prefix="/auth")
            client = TestClient(test_app)
            
            # Test registration
            user_data = {
                "email": "test@example.com",
                "password": "StrongPass123!",
                "name": "Test User"
            }
            
            response = client.post("/auth/register", json=user_data)
            
            assert response.status_code == 200
            data = response.json()
            assert data["email"] == "test@example.com"
            assert data["name"] == "Test User"
            assert "id" in data
            assert "hashed_password" not in data
    
    def test_register_user_already_exists(self):
        """Test registration with existing user"""
        with patch('backend.routes.auth.get_async_db') as mock_get_db:
            # Mock database - user already exists
            mock_db = MagicMock()
            mock_db.users.find_one.return_value = {
                "_id": "existing_user",
                "email": "test@example.com",
                "name": "Existing User"
            }
            mock_get_db.return_value = mock_db
            
            # Create test client
            test_app = app
            test_app.include_router(router, prefix="/auth")
            client = TestClient(test_app)
            
            # Test registration
            user_data = {
                "email": "test@example.com",
                "password": "StrongPass123!",
                "name": "Test User"
            }
            
            response = client.post("/auth/register", json=user_data)
            
            assert response.status_code == 400
            assert "already registered" in response.json()["detail"]
    
    def test_register_user_invalid_email(self):
        """Test registration with invalid email"""
        with patch('backend.routes.auth.get_async_db') as mock_get_db:
            # Mock database
            mock_db = MagicMock()
            mock_get_db.return_value = mock_db
            
            # Create test client
            test_app = app
            test_app.include_router(router, prefix="/auth")
            client = TestClient(test_app)
            
            # Test registration with invalid email
            user_data = {
                "email": "invalid-email",
                "password": "StrongPass123!",
                "name": "Test User"
            }
            
            response = client.post("/auth/register", json=user_data)
            
            assert response.status_code == 400
            assert "Invalid email format" in response.json()["detail"]
    
    def test_register_user_weak_password(self):
        """Test registration with weak password"""
        with patch('backend.routes.auth.get_async_db') as mock_get_db:
            # Mock database
            mock_db = MagicMock()
            mock_get_db.return_value = mock_db
            
            # Create test client
            test_app = app
            test_app.include_router(router, prefix="/auth")
            client = TestClient(test_app)
            
            # Test registration with weak password
            user_data = {
                "email": "test@example.com",
                "password": "weak",
                "name": "Test User"
            }
            
            response = client.post("/auth/register", json=user_data)
            
            assert response.status_code == 400
            assert "Password validation failed" in response.json()["detail"]
    
    def test_login_success(self):
        """Test successful login"""
        with patch('backend.routes.auth.get_async_db') as mock_get_db:
            # Mock database
            mock_db = MagicMock()
            hashed_password = get_password_hash("StrongPass123!")
            mock_db.users.find_one.return_value = {
                "_id": "user123",
                "email": "test@example.com",
                "name": "Test User",
                "hashed_password": hashed_password,
                "is_active": True
            }
            mock_get_db.return_value = mock_db
            
            # Create test client
            test_app = app
            test_app.include_router(router, prefix="/auth")
            client = TestClient(test_app)
            
            # Test login
            login_data = {
                "username": "test@example.com",
                "password": "StrongPass123!"
            }
            
            response = client.post("/auth/login", data=login_data)
            
            assert response.status_code == 200
            data = response.json()
            assert "access_token" in data
            assert data["token_type"] == "bearer"
    
    def test_login_invalid_credentials(self):
        """Test login with invalid credentials"""
        with patch('backend.routes.auth.get_async_db') as mock_get_db:
            # Mock database
            mock_db = MagicMock()
            mock_db.users.find_one.return_value = None  # User not found
            mock_get_db.return_value = mock_db
            
            # Create test client
            test_app = app
            test_app.include_router(router, prefix="/auth")
            client = TestClient(test_app)
            
            # Test login with invalid credentials
            login_data = {
                "username": "test@example.com",
                "password": "WrongPassword123!"
            }
            
            response = client.post("/auth/login", data=login_data)
            
            assert response.status_code == 401
            assert "Incorrect username or password" in response.json()["detail"]
    
    def test_login_inactive_user(self):
        """Test login with inactive user"""
        with patch('backend.routes.auth.get_async_db') as mock_get_db:
            # Mock database
            mock_db = MagicMock()
            hashed_password = get_password_hash("StrongPass123!")
            mock_db.users.find_one.return_value = {
                "_id": "user123",
                "email": "test@example.com",
                "name": "Test User",
                "hashed_password": hashed_password,
                "is_active": False  # Inactive user
            }
            mock_get_db.return_value = mock_db
            
            # Create test client
            test_app = app
            test_app.include_router(router, prefix="/auth")
            client = TestClient(test_app)
            
            # Test login
            login_data = {
                "username": "test@example.com",
                "password": "StrongPass123!"
            }
            
            response = client.post("/auth/login", data=login_data)
            
            assert response.status_code == 400
            assert "Inactive user" in response.json()["detail"]
    
    def test_forgot_password_success(self):
        """Test successful forgot password request"""
        with patch('backend.routes.auth.get_async_db') as mock_get_db:
            # Mock database
            mock_db = MagicMock()
            mock_db.users.find_one.return_value = {
                "_id": "user123",
                "email": "test@example.com",
                "name": "Test User"
            }
            mock_db.users.update_one.return_value.modified_count = 1
            mock_get_db.return_value = mock_db
            
            # Create test client
            test_app = app
            test_app.include_router(router, prefix="/auth")
            client = TestClient(test_app)
            
            # Test forgot password
            response = client.post("/auth/forgot-password", json={
                "email": "test@example.com"
            })
            
            assert response.status_code == 200
            assert "Password reset email sent" in response.json()["message"]
    
    def test_forgot_password_user_not_found(self):
        """Test forgot password with non-existent user"""
        with patch('backend.routes.auth.get_async_db') as mock_get_db:
            # Mock database
            mock_db = MagicMock()
            mock_db.users.find_one.return_value = None  # User not found
            mock_get_db.return_value = mock_db
            
            # Create test client
            test_app = app
            test_app.include_router(router, prefix="/auth")
            client = TestClient(test_app)
            
            # Test forgot password
            response = client.post("/auth/forgot-password", json={
                "email": "nonexistent@example.com"
            })
            
            assert response.status_code == 404
            assert "User not found" in response.json()["detail"]
    
    def test_reset_password_success(self):
        """Test successful password reset"""
        with patch('backend.routes.auth.get_async_db') as mock_get_db:
            # Mock database
            mock_db = MagicMock()
            mock_db.users.find_one.return_value = {
                "_id": "user123",
                "email": "test@example.com",
                "reset_token": "valid_token",
                "reset_token_expires": "2024-12-31T23:59:59Z"
            }
            mock_db.users.update_one.return_value.modified_count = 1
            mock_get_db.return_value = mock_db
            
            # Create test client
            test_app = app
            test_app.include_router(router, prefix="/auth")
            client = TestClient(test_app)
            
            # Test password reset
            response = client.post("/auth/reset-password", json={
                "token": "valid_token",
                "new_password": "NewStrongPass123!"
            })
            
            assert response.status_code == 200
            assert "Password reset successfully" in response.json()["message"]
    
    def test_reset_password_invalid_token(self):
        """Test password reset with invalid token"""
        with patch('backend.routes.auth.get_async_db') as mock_get_db:
            # Mock database
            mock_db = MagicMock()
            mock_db.users.find_one.return_value = None  # Token not found
            mock_get_db.return_value = mock_db
            
            # Create test client
            test_app = app
            test_app.include_router(router, prefix="/auth")
            client = TestClient(test_app)
            
            # Test password reset
            response = client.post("/auth/reset-password", json={
                "token": "invalid_token",
                "new_password": "NewStrongPass123!"
            })
            
            assert response.status_code == 400
            assert "Invalid or expired token" in response.json()["detail"]
    
    def test_verify_email_success(self):
        """Test successful email verification"""
        with patch('backend.routes.auth.get_async_db') as mock_get_db:
            # Mock database
            mock_db = MagicMock()
            mock_db.users.find_one.return_value = {
                "_id": "user123",
                "email": "test@example.com",
                "verification_token": "valid_token",
                "is_verified": False
            }
            mock_db.users.update_one.return_value.modified_count = 1
            mock_get_db.return_value = mock_db
            
            # Create test client
            test_app = app
            test_app.include_router(router, prefix="/auth")
            client = TestClient(test_app)
            
            # Test email verification
            response = client.get("/auth/verify-email?token=valid_token")
            
            assert response.status_code == 200
            assert "Email verified successfully" in response.json()["message"]
    
    def test_verify_email_invalid_token(self):
        """Test email verification with invalid token"""
        with patch('backend.routes.auth.get_async_db') as mock_get_db:
            # Mock database
            mock_db = MagicMock()
            mock_db.users.find_one.return_value = None  # Token not found
            mock_get_db.return_value = mock_db
            
            # Create test client
            test_app = app
            test_app.include_router(router, prefix="/auth")
            client = TestClient(test_app)
            
            # Test email verification
            response = client.get("/auth/verify-email?token=invalid_token")
            
            assert response.status_code == 400
            assert "Invalid verification token" in response.json()["detail"]
    
    def test_refresh_token_success(self):
        """Test successful token refresh"""
        with patch('backend.routes.auth.get_async_db') as mock_get_db:
            # Mock database
            mock_db = MagicMock()
            mock_db.users.find_one.return_value = {
                "_id": "user123",
                "email": "test@example.com",
                "name": "Test User",
                "is_active": True
            }
            mock_get_db.return_value = mock_db
            
            # Create test client
            test_app = app
            test_app.include_router(router, prefix="/auth")
            client = TestClient(test_app)
            
            # Mock current user dependency
            with patch('backend.routes.auth.get_current_user') as mock_current_user:
                mock_current_user.return_value = {
                    "_id": "user123",
                    "email": "test@example.com",
                    "name": "Test User"
                }
                
                # Test token refresh
                response = client.post("/auth/refresh-token")
                
                assert response.status_code == 200
                data = response.json()
                assert "access_token" in data
                assert data["token_type"] == "bearer"
    
    def test_logout_success(self):
        """Test successful logout"""
        with patch('backend.routes.auth.get_async_db') as mock_get_db:
            # Mock database
            mock_db = MagicMock()
            mock_get_db.return_value = mock_db
            
            # Create test client
            test_app = app
            test_app.include_router(router, prefix="/auth")
            client = TestClient(test_app)
            
            # Mock current user dependency
            with patch('backend.routes.auth.get_current_user') as mock_current_user:
                mock_current_user.return_value = {
                    "_id": "user123",
                    "email": "test@example.com",
                    "name": "Test User"
                }
                
                # Test logout
                response = client.post("/auth/logout")
                
                assert response.status_code == 200
                assert "Successfully logged out" in response.json()["message"]
    
    def test_get_current_user_success(self):
        """Test getting current user successfully"""
        with patch('backend.routes.auth.get_async_db') as mock_get_db:
            # Mock database
            mock_db = MagicMock()
            mock_db.users.find_one.return_value = {
                "_id": "user123",
                "email": "test@example.com",
                "name": "Test User",
                "is_active": True
            }
            mock_get_db.return_value = mock_db
            
            # Create test client
            test_app = app
            test_app.include_router(router, prefix="/auth")
            client = TestClient(test_app)
            
            # Mock current user dependency
            with patch('backend.routes.auth.get_current_user') as mock_current_user:
                mock_current_user.return_value = {
                    "_id": "user123",
                    "email": "test@example.com",
                    "name": "Test User"
                }
                
                # Test get current user
                response = client.get("/auth/me")
                
                assert response.status_code == 200
                data = response.json()
                assert data["email"] == "test@example.com"
                assert data["name"] == "Test User"
                assert "id" in data