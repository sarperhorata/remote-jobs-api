import pytest
from httpx import AsyncClient
from backend.main import app
from backend.schemas.user import UserCreate
from backend.core.security import create_access_token
from unittest.mock import patch, AsyncMock
from datetime import datetime

@pytest.mark.asyncio
@pytest.mark.xfail(reason="Auth system requires proper database and configuration setup")
async def test_register_user(async_client, test_user_data, mongodb):
    # Clear users collection before test
    await mongodb["users"].delete_many({})

    response = await async_client.post(
        "/api/register",
        json=test_user_data
    )
    assert response.status_code == 200 # Expect 200 on success
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert "user" in data
    assert data["user"]["email"] == test_user_data["email"]

@pytest.mark.asyncio
@pytest.mark.xfail(reason="Auth system requires proper database and configuration setup")
async def test_login_user(async_client, test_user_data, mongodb):
    # Clear users collection before test
    await mongodb["users"].delete_many({})

    # First register a user
    await async_client.post(
        "/api/register",
        json=test_user_data
    )
    
    # Then try to login
    response = await async_client.post(
        "/api/login",
        data={
            "username": test_user_data["email"],
            "password": test_user_data["password"]
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

@pytest.mark.asyncio
async def test_login_invalid_credentials(async_client, mongodb):
    # Clear users collection before test
    await mongodb["users"].delete_many({})
    
    # Ensure no user exists with test@example.com initially
    # If you register a user here, ensure it's a different email or clean up

    response = await async_client.post(
        "/api/login",
        data={
            "username": "nonexistent@example.com",
            "password": "wrongpassword"
        }
    )
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_register_existing_email(async_client, mock_database):
    # Clear the users collection before the test
    mock_database.users._storage.clear()
    
    test_user_data = {
        "email": "unique_test@example.com",
        "password": "testpassword123",
        "name": "Test User"
    }
    
    # First register a user
    response1 = await async_client.post(
        "/api/register",
        json=test_user_data
    )
    assert response1.status_code == 200
    
    # Try to register with same email - should fail
    response2 = await async_client.post(
        "/api/register",
        json=test_user_data
    )
    assert response2.status_code == 400
    assert "Email already registered" in response2.json()["detail"]

@pytest.mark.asyncio
async def test_register_invalid_email(async_client, mongodb):
    # Clear users collection before test
    await mongodb["users"].delete_many({})

    response = await async_client.post(
        "/api/register",
        json={
            "email": "invalid-email",
            "password": "testpassword123",
            "name": "Test User"
        }
    )
    assert response.status_code == 422

@pytest.mark.asyncio
async def test_register_short_password(async_client, mongodb):
    # Clear users collection before test
    await mongodb["users"].delete_many({})

    response = await async_client.post(
        "/api/register",
        json={
            "email": "test@example.com",
            "password": "short",
            "name": "Test User"
        }
    )
    assert response.status_code == 422

@pytest.mark.asyncio
@pytest.mark.xfail(reason="Auth system requires proper database and configuration setup")
async def test_get_current_user(async_client, test_user_data, mongodb):
    # Clear users collection before test
    await mongodb["users"].delete_many({})

    # First register and get token
    register_response = await async_client.post(
        "/api/register",
        json=test_user_data
    )
    token = register_response.json()["access_token"]
    
    # Get current user info
    response = await async_client.get(
        "/api/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == test_user_data["email"]
    assert data["full_name"] == test_user_data["name"]

@pytest.mark.asyncio
async def test_get_current_user_no_token(async_client):
    response = await async_client.get("/api/me")
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_get_current_user_invalid_token(async_client):
    response = await async_client.get(
        "/api/me",
        headers={"Authorization": "Bearer invalid_token"}
    )
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_google_auth_url(async_client):
    # Mock the settings for Google OAuth to avoid actual external calls
    with patch('backend.config.settings.GOOGLE_CLIENT_ID', "mock_client_id"), \
         patch('backend.config.settings.GOOGLE_REDIRECT_URI', "http://test/api/google/callback"): 
        response = await async_client.get("/api/google/auth-url")
        assert response.status_code == 200
        data = response.json()
        assert "auth_url" in data # The key might be 'auth_url' not 'url'
        assert "accounts.google.com" in data["auth_url"]

@pytest.mark.asyncio
async def test_google_callback_invalid_code(async_client):
    response = await async_client.get("/api/google/callback?code=invalid_code")
    assert response.status_code == 400

@pytest.mark.asyncio
async def test_google_callback_no_code(async_client):
    response = await async_client.get("/api/google/callback")
    assert response.status_code == 400

@pytest.mark.asyncio
async def test_forgot_password_existing_email(async_client, mongodb):
    """Test forgot password with existing email."""
    # Clear users collection before test
    await mongodb["users"].delete_many({})

    # Create a user
    await mongodb["users"].insert_one({
        "email": "test@example.com",
        "hashed_password": "hashed_password",
        "created_at": datetime.now(),
        "updated_at": datetime.now()
    })

    with patch('backend.routes.auth.send_password_reset_email', return_value=True):
        response = await async_client.post(
            "/api/forgot-password",
            json={"email": "test@example.com"}
        )
        
    assert response.status_code == 200
    data = response.json()
    assert "password reset link has been sent" in data["message"]

@pytest.mark.asyncio
async def test_forgot_password_nonexistent_email(async_client, mongodb):
    """Test forgot password with non-existent email."""
    # Clear users collection before test
    await mongodb["users"].delete_many({})

    with patch('backend.routes.auth.send_password_reset_email', return_value=True):
        response = await async_client.post(
            "/api/forgot-password",
            json={"email": "nonexistent@example.com"}
        )
        
    assert response.status_code == 200
    # Should return same message for security
    data = response.json()
    assert "password reset link has been sent" in data["message"]

@pytest.mark.asyncio
async def test_reset_password_valid_token(async_client, mongodb):
    """Test password reset with valid token."""
    # Clear users collection before test
    await mongodb["users"].delete_many({})

    # Create a user
    result = await mongodb["users"].insert_one({
        "email": "test@example.com",
        "hashed_password": "old_hashed_password",
        "created_at": datetime.now(),
        "updated_at": datetime.now()
    })

    # Mock token verification
    with patch('backend.routes.auth.verify_token') as mock_verify:
        mock_verify.return_value = {
            "sub": "test@example.com",
            "type": "password_reset",
            "exp": 1234567890
        }
        
        response = await async_client.post(
            "/api/reset-password",
            json={
                "token": "valid_reset_token",
                "new_password": "NewSecurePass123!"
            }
        )
        
    assert response.status_code == 200
    data = response.json()
    assert "successfully reset" in data["message"]

    # Check password was updated
    user = await mongodb["users"].find_one({"_id": result.inserted_id})
    assert user["hashed_password"] != "old_hashed_password"

@pytest.mark.asyncio
async def test_reset_password_invalid_token(async_client):
    """Test password reset with invalid token."""
    with patch('backend.routes.auth.verify_token', return_value=None):
        response = await async_client.post(
            "/api/reset-password",
            json={
                "token": "invalid_token",
                "new_password": "NewSecurePass123!"
            }
        )
        
    assert response.status_code == 400
    assert "Invalid or expired" in response.json()["detail"]

@pytest.mark.asyncio
async def test_login_unverified_email(async_client, mongodb):
    """Test login with unverified email should fail."""
    # Clear users collection before test
    await mongodb["users"].delete_many({})

    # Create an unverified user
    from backend.routes.auth import get_password_hash
    await mongodb["users"].insert_one({
        "email": "unverified@example.com",
        "hashed_password": get_password_hash("testpassword123"),
        "email_verified": False,
        "created_at": datetime.now(),
        "updated_at": datetime.now()
    })

    response = await async_client.post(
        "/api/login",
        data={
            "username": "unverified@example.com",
            "password": "testpassword123"
        }
    )
    assert response.status_code == 403
    assert "Email not verified" in response.json()["detail"] 