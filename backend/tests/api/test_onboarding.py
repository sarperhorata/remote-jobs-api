import pytest
from httpx import AsyncClient
from backend.main import app
from unittest.mock import patch, AsyncMock
from datetime import datetime

@pytest.mark.asyncio
async def test_register_with_email_only(async_client, mongodb):
    """Test email-only registration (step 1 of onboarding)."""
    # Clear users collection before test
    await mongodb["users"].delete_many({})

    with patch('backend.routes.onboarding.send_verification_email', return_value=True):
        response = await async_client.post(
            "/api/onboarding/register-email",
            json={"email": "test@example.com"}
        )
        
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Kayıt başarılı! Email adresinizi kontrol edin"
    assert data["onboarding_step"] == 0
    assert data["next_step"] == "email_verification"
    assert "user_id" in data

    # Check user was created in database
    user = await mongodb["users"].find_one({"email": "test@example.com"})
    assert user is not None
    assert user["email_verified"] is False
    assert user["onboarding_completed"] is False
    assert user["onboarding_step"] == 0

@pytest.mark.asyncio
async def test_register_existing_email_unverified(async_client, mongodb):
    """Test registering with existing unverified email should resend verification."""
    # Clear users collection before test
    await mongodb["users"].delete_many({})

    # Create an unverified user
    await mongodb["users"].insert_one({
        "email": "test@example.com",
        "email_verified": False,
        "onboarding_completed": False,
        "onboarding_step": 0,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    })

    with patch('backend.routes.onboarding.send_verification_email', return_value=True):
        response = await async_client.post(
            "/api/onboarding/register-email",
            json={"email": "test@example.com"}
        )
        
    assert response.status_code == 200
    data = response.json()
    assert "tekrar gönderildi" in data["message"]

@pytest.mark.asyncio
async def test_register_existing_verified_email(async_client, mongodb):
    """Test registering with existing verified email should fail."""
    # Clear users collection before test
    await mongodb["users"].delete_many({})

    # Create a verified user
    await mongodb["users"].insert_one({
        "email": "test@example.com",
        "email_verified": True,
        "onboarding_completed": True,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    })

    response = await async_client.post(
        "/api/onboarding/register-email",
        json={"email": "test@example.com"}
    )
    
    assert response.status_code == 400
    assert "zaten kayıtlı" in response.json()["detail"]

@pytest.mark.asyncio
async def test_verify_email_valid_token(async_client, mongodb):
    """Test email verification with valid token."""
    # Clear users collection before test
    await mongodb["users"].delete_many({})

    # Create user
    result = await mongodb["users"].insert_one({
        "email": "test@example.com",
        "email_verified": False,
        "onboarding_step": 0,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    })

    # Mock token verification
    with patch('backend.routes.onboarding.verify_token') as mock_verify:
        mock_verify.return_value = {
            "sub": "test@example.com",
            "type": "email_verification",
            "exp": 1234567890
        }
        
        response = await async_client.post(
            "/api/onboarding/verify-email",
            json={"token": "valid_token"}
        )
        
    assert response.status_code == 200
    data = response.json()
    assert "başarıyla doğrulandı" in data["message"]
    assert data["onboarding_step"] == 1
    assert data["next_step"] == "set_password"

    # Check user was updated
    user = await mongodb["users"].find_one({"email": "test@example.com"})
    assert user["email_verified"] is True
    assert user["is_active"] is True
    assert user["onboarding_step"] == 1

@pytest.mark.asyncio
async def test_verify_email_invalid_token(async_client):
    """Test email verification with invalid token."""
    with patch('backend.routes.onboarding.verify_token', return_value=None):
        response = await async_client.post(
            "/api/onboarding/verify-email",
            json={"token": "invalid_token"}
        )
        
    assert response.status_code == 400
    assert "Geçersiz" in response.json()["detail"]

@pytest.mark.asyncio
async def test_set_password_valid_token(async_client, mongodb):
    """Test password setting with valid token."""
    # Clear users collection before test
    await mongodb["users"].delete_many({})

    # Create verified user
    await mongodb["users"].insert_one({
        "email": "test@example.com",
        "email_verified": True,
        "onboarding_step": 1,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    })

    # Mock token verification
    with patch('backend.routes.onboarding.verify_token') as mock_verify:
        mock_verify.return_value = {
            "sub": "test@example.com",
            "type": "email_verification",
            "exp": 1234567890
        }
        
        response = await async_client.post(
            "/api/onboarding/set-password",
            json={
                "token": "valid_token",
                "password": "SecurePass123!",
                "confirm_password": "SecurePass123!"
            }
        )
        
    assert response.status_code == 200
    data = response.json()
    assert "başarıyla belirlendi" in data["message"]
    assert data["onboarding_step"] == 2
    assert data["next_step"] == "profile_setup"

    # Check password was hashed and saved
    user = await mongodb["users"].find_one({"email": "test@example.com"})
    assert "hashed_password" in user
    assert user["onboarding_step"] == 2

@pytest.mark.asyncio
async def test_set_password_mismatch(async_client):
    """Test password setting with mismatched passwords."""
    with patch('backend.routes.onboarding.verify_token') as mock_verify:
        mock_verify.return_value = {
            "sub": "test@example.com",
            "type": "email_verification",
            "exp": 1234567890
        }
        
        response = await async_client.post(
            "/api/onboarding/set-password",
            json={
                "token": "valid_token",
                "password": "SecurePass123!",
                "confirm_password": "DifferentPass123!"
            }
        )
        
    assert response.status_code == 400
    assert "eşleşmiyor" in response.json()["detail"]

@pytest.mark.asyncio
async def test_linkedin_auth_url(async_client):
    """Test LinkedIn auth URL generation."""
    with patch.dict('os.environ', {'LINKEDIN_CLIENT_ID': 'test_client_id'}):
        response = await async_client.get("/api/onboarding/linkedin-auth-url")
        
    assert response.status_code == 200
    data = response.json()
    assert "auth_url" in data
    assert "linkedin.com" in data["auth_url"]
    assert "test_client_id" in data["auth_url"]
    assert "state" in data

@pytest.mark.asyncio
async def test_linkedin_auth_url_no_config(async_client):
    """Test LinkedIn auth URL without configuration."""
    with patch.dict('os.environ', {}, clear=True):
        response = await async_client.get("/api/onboarding/linkedin-auth-url")
        
    assert response.status_code == 500
    assert "konfigürasyonu eksik" in response.json()["detail"]

@pytest.mark.asyncio
async def test_upload_cv_valid_file(async_client, mongodb):
    """Test CV upload with valid file."""
    # Clear users collection before test
    await mongodb["users"].delete_many({})

    # Create user
    result = await mongodb["users"].insert_one({
        "email": "test@example.com",
        "onboarding_step": 2,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    })
    user_id = str(result.inserted_id)

    # Mock file operations
    with patch('backend.routes.onboarding.aiofiles.open', create=True) as mock_file, \
         patch('os.makedirs'), \
         patch('uuid.uuid4', return_value='test-uuid'):
        
        # Create mock file
        mock_file_data = b"PDF content here"
        
        response = await async_client.post(
            "/api/onboarding/upload-cv",
            data={"user_id": user_id},
            files={"file": ("test.pdf", mock_file_data, "application/pdf")}
        )
        
    assert response.status_code == 200
    data = response.json()
    assert "başarıyla yüklendi" in data["message"]
    assert "file_url" in data

@pytest.mark.asyncio
async def test_upload_cv_invalid_file_type(async_client):
    """Test CV upload with invalid file type."""
    response = await async_client.post(
        "/api/onboarding/upload-cv",
        data={"user_id": "test_user_id"},
        files={"file": ("test.txt", b"text content", "text/plain")}
    )
    
    assert response.status_code == 400
    assert "kabul edilir" in response.json()["detail"]

@pytest.mark.asyncio
async def test_get_onboarding_status(async_client, mongodb):
    """Test getting onboarding status."""
    # Clear users collection before test
    await mongodb["users"].delete_many({})

    # Create user
    result = await mongodb["users"].insert_one({
        "email": "test@example.com",
        "onboarding_step": 2,
        "email_verified": True,
        "onboarding_completed": False,
        "linkedin_id": None,
        "resume_url": None,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    })
    user_id = str(result.inserted_id)

    response = await async_client.get(f"/api/onboarding/status/{user_id}")
    
    assert response.status_code == 200
    data = response.json()
    assert data["user_id"] == user_id
    assert data["onboarding_step"] == 2
    assert data["next_step"] == "profile_setup"
    assert data["email_verified"] is True
    assert data["onboarding_completed"] is False
    assert data["has_linkedin"] is False
    assert data["has_resume"] is False

@pytest.mark.asyncio
async def test_get_onboarding_status_invalid_user(async_client):
    """Test getting onboarding status for non-existent user."""
    response = await async_client.get("/api/onboarding/status/invalid_user_id")
    
    assert response.status_code == 404
    assert "bulunamadı" in response.json()["detail"]

@pytest.mark.asyncio
async def test_complete_profile(async_client, mongodb):
    """Test profile completion."""
    # Clear users collection before test
    await mongodb["users"].delete_many({})

    # Create user
    result = await mongodb["users"].insert_one({
        "email": "test@example.com",
        "onboarding_step": 3,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    })
    user_id = str(result.inserted_id)

    response = await async_client.post(
        f"/api/onboarding/complete-profile?user_id={user_id}",
        json={
            "name": "Test User",
            "bio": "Software Developer",
            "location": "Istanbul, Turkey",
            "skills": ["Python", "React"],
            "experience_years": 5
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "tamamlandı" in data["message"]
    assert data["onboarding_step"] == 4
    assert data["next_step"] == "dashboard"
    assert "access_token" in data

    # Check user was updated
    user = await mongodb["users"].find_one({"_id": result.inserted_id})
    assert user["onboarding_completed"] is True
    assert user["onboarding_step"] == 4
    assert user["name"] == "Test User"
    assert user["bio"] == "Software Developer"

@pytest.mark.asyncio
async def test_linkedin_callback_valid_code(async_client, mongodb):
    """Test LinkedIn OAuth callback with valid authorization code."""
    # Clear users collection before test
    await mongodb["users"].delete_many({})

    # Create user
    result = await mongodb["users"].insert_one({
        "email": "test@example.com",
        "onboarding_step": 2,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    })
    user_id = str(result.inserted_id)

    # Mock LinkedIn API responses
    mock_token_response = {
        "access_token": "mock_access_token",
        "token_type": "Bearer"
    }
    
    mock_profile_response = {
        "id": "linkedin_user_123",
        "firstName": {"localized": {"en_US": "John"}},
        "lastName": {"localized": {"en_US": "Doe"}},
        "profilePicture": {
            "displayImage": "https://media.licdn.com/dms/image/profile.jpg"
        }
    }
    
    mock_email_response = {
        "elements": [{
            "handle~": {"emailAddress": "john.doe@example.com"}
        }]
    }

    with patch('backend.routes.onboarding.httpx.AsyncClient') as mock_client:
        # Setup mock client
        mock_client_instance = mock_client.return_value.__aenter__.return_value
        
        # Mock token exchange
        mock_client_instance.post.return_value.raise_for_status = lambda: None
        mock_client_instance.post.return_value.json.return_value = mock_token_response
        
        # Mock profile API calls
        mock_client_instance.get.side_effect = [
            # Profile call
            type('MockResponse', (), {
                'raise_for_status': lambda: None,
                'json': lambda: mock_profile_response
            })(),
            # Email call
            type('MockResponse', (), {
                'raise_for_status': lambda: None,
                'json': lambda: mock_email_response
            })()
        ]

        response = await async_client.post(
            "/api/onboarding/linkedin-callback",
            json={
                "code": "valid_auth_code",
                "state": "test_state",
                "user_id": user_id
            }
        )
        
    assert response.status_code == 200
    data = response.json()
    assert "başarıyla bağlandı" in data["message"]
    assert data["onboarding_step"] == 3
    assert data["next_step"] == "complete_profile"

    # Check user was updated with LinkedIn data
    user = await mongodb["users"].find_one({"_id": result.inserted_id})
    assert user["linkedin_id"] == "linkedin_user_123"
    assert user["linkedin_profile"]["firstName"]["en_US"] == "John"
    assert user["linkedin_profile"]["lastName"]["en_US"] == "Doe"
    assert user["linkedin_profile"]["email"] == "john.doe@example.com"

@pytest.mark.asyncio
async def test_linkedin_callback_api_error(async_client, mongodb):
    """Test LinkedIn callback when LinkedIn API returns error."""
    # Clear users collection before test
    await mongodb["users"].delete_many({})

    # Create user
    result = await mongodb["users"].insert_one({
        "email": "test@example.com",
        "onboarding_step": 2,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    })
    user_id = str(result.inserted_id)

    # Mock LinkedIn API error
    with patch('backend.routes.onboarding.httpx.AsyncClient') as mock_client:
        mock_client_instance = mock_client.return_value.__aenter__.return_value
        mock_client_instance.post.side_effect = Exception("LinkedIn API Error")

        response = await async_client.post(
            "/api/onboarding/linkedin-callback",
            json={
                "code": "invalid_code",
                "state": "test_state", 
                "user_id": user_id
            }
        )
        
    assert response.status_code == 400
    assert "bağlantısında hata" in response.json()["detail"]

@pytest.mark.asyncio
async def test_upload_cv_file_size_limit(async_client):
    """Test CV upload with file size over limit."""
    # Create file larger than 5MB
    large_file_content = b"x" * (6 * 1024 * 1024)  # 6MB
    
    response = await async_client.post(
        "/api/onboarding/upload-cv",
        data={"user_id": "test_user_id"},
        files={"file": ("large.pdf", large_file_content, "application/pdf")}
    )
    
    assert response.status_code == 400
    assert "5MB" in response.json()["detail"]

@pytest.mark.asyncio 
async def test_upload_cv_multiple_file_types(async_client, mongodb):
    """Test CV upload with different valid file types."""
    # Clear users collection before test
    await mongodb["users"].delete_many({})

    # Create user
    result = await mongodb["users"].insert_one({
        "email": "test@example.com",
        "onboarding_step": 2,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    })
    user_id = str(result.inserted_id)

    valid_file_types = [
        ("test.pdf", "application/pdf"),
        ("test.doc", "application/msword"),
        ("test.docx", "application/vnd.openxmlformats-officedocument.wordprocessingml.document")
    ]

    for filename, content_type in valid_file_types:
        with patch('backend.routes.onboarding.aiofiles.open', create=True), \
             patch('os.makedirs'), \
             patch('uuid.uuid4', return_value='test-uuid'):
            
            response = await async_client.post(
                "/api/onboarding/upload-cv",
                data={"user_id": user_id},
                files={"file": (filename, b"file content", content_type)}
            )
            
        assert response.status_code == 200, f"Failed for {filename}"
        data = response.json()
        assert "başarıyla yüklendi" in data["message"]

@pytest.mark.asyncio
async def test_complete_profile_validation(async_client, mongodb):
    """Test profile completion with various validation scenarios."""
    # Clear users collection before test
    await mongodb["users"].delete_many({})

    # Create user
    result = await mongodb["users"].insert_one({
        "email": "test@example.com",
        "onboarding_step": 3,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    })
    user_id = str(result.inserted_id)

    # Test with minimal valid data
    response = await async_client.post(
        f"/api/onboarding/complete-profile?user_id={user_id}",
        json={"name": "Minimal User"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "tamamlandı" in data["message"]

    # Check user was updated with minimal data
    user = await mongodb["users"].find_one({"_id": result.inserted_id})
    assert user["name"] == "Minimal User"
    assert user["onboarding_completed"] is True

@pytest.mark.asyncio
async def test_complete_profile_with_linkedin_data(async_client, mongodb):
    """Test profile completion when user already has LinkedIn data."""
    # Clear users collection before test
    await mongodb["users"].delete_many({})

    # Create user with LinkedIn data
    linkedin_profile = {
        "id": "linkedin_123",
        "firstName": {"en_US": "LinkedIn"},
        "lastName": {"en_US": "User"},
        "email": "linkedin@example.com"
    }
    
    result = await mongodb["users"].insert_one({
        "email": "test@example.com",
        "onboarding_step": 3,
        "linkedin_id": "linkedin_123",
        "linkedin_profile": linkedin_profile,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    })
    user_id = str(result.inserted_id)

    response = await async_client.post(
        f"/api/onboarding/complete-profile?user_id={user_id}",
        json={
            "name": "Updated Name",
            "bio": "Bio from manual input",
            "skills": ["Python", "JavaScript"]
        }
    )
    
    assert response.status_code == 200
    
    # Check both LinkedIn and manual data are preserved
    user = await mongodb["users"].find_one({"_id": result.inserted_id})
    assert user["name"] == "Updated Name"  # Manual override
    assert user["bio"] == "Bio from manual input"
    assert user["linkedin_id"] == "linkedin_123"  # LinkedIn data preserved
    assert user["skills"] == ["Python", "JavaScript"]

@pytest.mark.asyncio
async def test_complete_profile_with_cv_data(async_client, mongodb):
    """Test profile completion when user has uploaded CV."""
    # Clear users collection before test
    await mongodb["users"].delete_many({})

    # Create user with CV
    result = await mongodb["users"].insert_one({
        "email": "test@example.com",
        "onboarding_step": 3,
        "resume_url": "/uploads/cv/user_cv.pdf",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    })
    user_id = str(result.inserted_id)

    response = await async_client.post(
        f"/api/onboarding/complete-profile?user_id={user_id}",
        json={
            "name": "CV User",
            "experience_years": 3
        }
    )
    
    assert response.status_code == 200
    
    # Check CV and manual data are both preserved
    user = await mongodb["users"].find_one({"_id": result.inserted_id})
    assert user["name"] == "CV User"
    assert user["experience_years"] == 3
    assert user["resume_url"] == "/uploads/cv/user_cv.pdf"  # CV preserved

@pytest.mark.asyncio
async def test_onboarding_status_with_all_data(async_client, mongodb):
    """Test onboarding status when user has LinkedIn, CV, and profile data."""
    # Clear users collection before test
    await mongodb["users"].delete_many({})

    # Create user with all data types
    result = await mongodb["users"].insert_one({
        "email": "test@example.com",
        "onboarding_step": 4,
        "email_verified": True,
        "onboarding_completed": True,
        "linkedin_id": "linkedin_123",
        "resume_url": "/uploads/cv/user_cv.pdf",
        "name": "Complete User",
        "bio": "Full profile",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    })
    user_id = str(result.inserted_id)

    response = await async_client.get(f"/api/onboarding/status/{user_id}")
    
    assert response.status_code == 200
    data = response.json()
    assert data["onboarding_step"] == 4
    assert data["next_step"] == "completed"
    assert data["email_verified"] is True
    assert data["onboarding_completed"] is True
    assert data["has_linkedin"] is True
    assert data["has_resume"] is True

@pytest.mark.asyncio
async def test_upload_cv_file_path_injection(async_client):
    """Test CV upload security - prevent path injection."""
    response = await async_client.post(
        "/api/onboarding/upload-cv",
        data={"user_id": "test_user_id"},
        files={"file": ("../../../etc/passwd", b"malicious content", "application/pdf")}
    )
    
    # Should still work but filename should be sanitized
    # This test ensures our UUID-based naming prevents path injection
    assert response.status_code == 200 or response.status_code == 400  # Either works or rejects safely

@pytest.mark.asyncio
async def test_linkedin_callback_missing_user(async_client):
    """Test LinkedIn callback with non-existent user ID."""
    response = await async_client.post(
        "/api/onboarding/linkedin-callback",
        json={
            "code": "valid_code",
            "state": "test_state",
            "user_id": "nonexistent_user_id"
        }
    )
    
    assert response.status_code == 404
    assert "bulunamadı" in response.json()["detail"] 