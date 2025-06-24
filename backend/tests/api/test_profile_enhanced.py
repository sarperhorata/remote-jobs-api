import pytest
from httpx import AsyncClient
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime
import json

from backend.main import app

class TestProfileAPIEnhanced:
    """Enhanced test suite for profile API endpoints"""
    
    @pytest.fixture
    async def client(self):
        """Create test client"""
        async with AsyncClient(app=app, base_url="http://test") as ac:
            yield ac
    
    @pytest.fixture
    def mock_user(self):
        """Mock authenticated user"""
        return {
            "_id": "test_user_id",
            "email": "test@example.com",
            "name": "John Doe",
            "is_active": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
    
    @pytest.fixture
    def mock_db(self):
        """Mock database"""
        db = AsyncMock()
        db.users = AsyncMock()
        db.user_profiles = AsyncMock()
        return db
    
    async def test_get_profile_success(self, client, mock_user, mock_db):
        """Test successful profile retrieval"""
        mock_profile = {
            "_id": "profile_id",
            "user_id": "test_user_id",
            "first_name": "John",
            "last_name": "Doe",
            "bio": "Software developer",
            "skills": ["Python", "React", "MongoDB"],
            "experience": [
                {
                    "title": "Senior Developer",
                    "company": "Tech Corp",
                    "duration": "2 years",
                    "current": True
                }
            ]
        }
        
        mock_db.user_profiles.find_one.return_value = mock_profile
        
        with patch('backend.routes.profile.get_current_user_dependency', return_value=mock_user):
            with patch('backend.routes.profile.get_async_db', return_value=mock_db):
                response = await client.get("/api/profile")
        
        assert response.status_code == 200
        data = response.json()
        assert data["first_name"] == "John"
        assert data["last_name"] == "Doe"
        assert "Python" in data["skills"]
    
    async def test_get_profile_not_found(self, client, mock_user, mock_db):
        """Test profile not found"""
        mock_db.user_profiles.find_one.return_value = None
        
        with patch('backend.routes.profile.get_current_user_dependency', return_value=mock_user):
            with patch('backend.routes.profile.get_async_db', return_value=mock_db):
                response = await client.get("/api/profile")
        
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"].lower()
    
    async def test_update_profile_success(self, client, mock_user, mock_db):
        """Test successful profile update"""
        update_data = {
            "first_name": "Jane",
            "last_name": "Smith",
            "bio": "Full-stack developer with 5+ years experience",
            "skills": ["Python", "React", "Node.js", "PostgreSQL"],
            "location": "San Francisco, CA"
        }
        
        mock_db.user_profiles.update_one.return_value = AsyncMock(modified_count=1)
        mock_db.user_profiles.find_one.return_value = {**update_data, "_id": "profile_id"}
        
        with patch('backend.routes.profile.get_current_user_dependency', return_value=mock_user):
            with patch('backend.routes.profile.get_async_db', return_value=mock_db):
                response = await client.put("/api/profile", json=update_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["first_name"] == "Jane"
        assert data["last_name"] == "Smith"
        assert "Node.js" in data["skills"]
    
    async def test_update_profile_validation_error(self, client, mock_user):
        """Test profile update with validation errors"""
        invalid_data = {
            "first_name": "",  # Empty name
            "email": "invalid-email",  # Invalid email format
            "skills": "not-a-list"  # Should be a list
        }
        
        with patch('backend.routes.profile.get_current_user_dependency', return_value=mock_user):
            response = await client.put("/api/profile", json=invalid_data)
        
        assert response.status_code == 422
    
    async def test_create_profile_success(self, client, mock_user, mock_db):
        """Test successful profile creation"""
        profile_data = {
            "first_name": "Alice",
            "last_name": "Johnson",
            "bio": "DevOps engineer passionate about automation",
            "skills": ["Docker", "Kubernetes", "AWS", "Python"],
            "experience": [
                {
                    "title": "DevOps Engineer",
                    "company": "Cloud Solutions Inc",
                    "start_date": "2022-01-01",
                    "end_date": None,
                    "current": True,
                    "description": "Managing cloud infrastructure and CI/CD pipelines"
                }
            ],
            "education": [
                {
                    "degree": "Bachelor of Computer Science",
                    "institution": "Tech University",
                    "graduation_year": 2021
                }
            ]
        }
        
        mock_db.user_profiles.find_one.return_value = None  # No existing profile
        mock_db.user_profiles.insert_one.return_value = AsyncMock(inserted_id="new_profile_id")
        
        with patch('backend.routes.profile.get_current_user_dependency', return_value=mock_user):
            with patch('backend.routes.profile.get_async_db', return_value=mock_db):
                response = await client.post("/api/profile", json=profile_data)
        
        assert response.status_code == 201
        data = response.json()
        assert data["message"] == "Profile created successfully"
        assert "profile_id" in data
    
    async def test_create_profile_already_exists(self, client, mock_user, mock_db):
        """Test creating profile when one already exists"""
        profile_data = {
            "first_name": "Bob",
            "last_name": "Wilson"
        }
        
        mock_db.user_profiles.find_one.return_value = {"_id": "existing_profile"}
        
        with patch('backend.routes.profile.get_current_user_dependency', return_value=mock_user):
            with patch('backend.routes.profile.get_async_db', return_value=mock_db):
                response = await client.post("/api/profile", json=profile_data)
        
        assert response.status_code == 400
        data = response.json()
        assert "already exists" in data["detail"].lower()
    
    async def test_upload_profile_picture(self, client, mock_user):
        """Test profile picture upload"""
        # Mock file upload
        files = {"file": ("profile.jpg", b"fake_image_data", "image/jpeg")}
        
        with patch('backend.routes.profile.get_current_user_dependency', return_value=mock_user):
            with patch('backend.routes.profile.upload_file_to_storage') as mock_upload:
                mock_upload.return_value = "https://storage.example.com/profiles/profile.jpg"
                
                response = await client.post("/api/profile/picture", files=files)
        
        assert response.status_code == 200
        data = response.json()
        assert "picture_url" in data
        assert data["picture_url"].endswith(".jpg")
    
    async def test_upload_invalid_file_type(self, client, mock_user):
        """Test uploading invalid file type for profile picture"""
        files = {"file": ("document.pdf", b"fake_pdf_data", "application/pdf")}
        
        with patch('backend.routes.profile.get_current_user_dependency', return_value=mock_user):
            response = await client.post("/api/profile/picture", files=files)
        
        assert response.status_code == 400
        data = response.json()
        assert "invalid file type" in data["detail"].lower()
    
    async def test_delete_profile(self, client, mock_user, mock_db):
        """Test profile deletion"""
        mock_db.user_profiles.delete_one.return_value = AsyncMock(deleted_count=1)
        
        with patch('backend.routes.profile.get_current_user_dependency', return_value=mock_user):
            with patch('backend.routes.profile.get_async_db', return_value=mock_db):
                response = await client.delete("/api/profile")
        
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Profile deleted successfully"
    
    async def test_delete_nonexistent_profile(self, client, mock_user, mock_db):
        """Test deleting non-existent profile"""
        mock_db.user_profiles.delete_one.return_value = AsyncMock(deleted_count=0)
        
        with patch('backend.routes.profile.get_current_user_dependency', return_value=mock_user):
            with patch('backend.routes.profile.get_async_db', return_value=mock_db):
                response = await client.delete("/api/profile")
        
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"].lower()
    
    async def test_get_profile_public(self, client, mock_db):
        """Test getting public profile by user ID"""
        user_id = "public_user_id"
        mock_profile = {
            "_id": "profile_id",
            "user_id": user_id,
            "first_name": "Public",
            "last_name": "User",
            "bio": "This is a public bio",
            "skills": ["JavaScript", "CSS"],
            "is_public": True
        }
        
        mock_db.user_profiles.find_one.return_value = mock_profile
        
        with patch('backend.routes.profile.get_async_db', return_value=mock_db):
            response = await client.get(f"/api/profile/public/{user_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["first_name"] == "Public"
        # Should not include private information
        assert "email" not in data
    
    async def test_get_private_profile_unauthorized(self, client, mock_db):
        """Test getting private profile without authorization"""
        user_id = "private_user_id"
        mock_profile = {
            "_id": "profile_id",
            "user_id": user_id,
            "first_name": "Private",
            "last_name": "User",
            "is_public": False
        }
        
        mock_db.user_profiles.find_one.return_value = mock_profile
        
        with patch('backend.routes.profile.get_async_db', return_value=mock_db):
            response = await client.get(f"/api/profile/public/{user_id}")
        
        assert response.status_code == 403
        data = response.json()
        assert "private" in data["detail"].lower()
    
    async def test_search_profiles(self, client):
        """Test searching user profiles"""
        search_params = {
            "skills": "Python,React",
            "location": "San Francisco",
            "experience_level": "senior"
        }
        
        with patch('backend.routes.profile.search_profiles') as mock_search:
            mock_search.return_value = {
                "profiles": [
                    {
                        "user_id": "user1",
                        "name": "John Smith",
                        "skills": ["Python", "React"],
                        "location": "San Francisco, CA"
                    }
                ],
                "total": 1
            }
            
            response = await client.get("/api/profile/search", params=search_params)
        
        assert response.status_code == 200
        data = response.json()
        assert "profiles" in data
        assert data["total"] == 1
    
    async def test_profile_analytics(self, client, mock_user, mock_db):
        """Test profile analytics endpoint"""
        mock_analytics = {
            "profile_views": 150,
            "skill_matches": 25,
            "profile_completeness": 85,
            "recent_activity": [
                {"action": "profile_updated", "date": "2024-01-15"},
                {"action": "skill_added", "date": "2024-01-10"}
            ]
        }
        
        with patch('backend.routes.profile.get_current_user_dependency', return_value=mock_user):
            with patch('backend.routes.profile.get_profile_analytics', return_value=mock_analytics):
                response = await client.get("/api/profile/analytics")
        
        assert response.status_code == 200
        data = response.json()
        assert data["profile_views"] == 150
        assert data["profile_completeness"] == 85
        assert len(data["recent_activity"]) == 2
    
    async def test_profile_skills_suggestions(self, client, mock_user):
        """Test skill suggestions based on profile"""
        current_skills = ["Python", "Django"]
        
        with patch('backend.routes.profile.get_current_user_dependency', return_value=mock_user):
            with patch('backend.routes.profile.get_skill_suggestions') as mock_suggestions:
                mock_suggestions.return_value = {
                    "suggested_skills": [
                        {"skill": "PostgreSQL", "relevance": 0.9},
                        {"skill": "Docker", "relevance": 0.8},
                        {"skill": "Redis", "relevance": 0.7}
                    ],
                    "reasoning": "Based on your Python and Django experience"
                }
                
                response = await client.post("/api/profile/skill-suggestions", 
                                           json={"current_skills": current_skills})
        
        assert response.status_code == 200
        data = response.json()
        assert "suggested_skills" in data
        assert len(data["suggested_skills"]) == 3
        assert data["suggested_skills"][0]["skill"] == "PostgreSQL"
    
    async def test_profile_export(self, client, mock_user, mock_db):
        """Test profile data export"""
        mock_profile = {
            "_id": "profile_id",
            "user_id": "test_user_id",
            "first_name": "John",
            "last_name": "Doe",
            "skills": ["Python", "React"],
            "experience": [],
            "education": []
        }
        
        mock_db.user_profiles.find_one.return_value = mock_profile
        
        with patch('backend.routes.profile.get_current_user_dependency', return_value=mock_user):
            with patch('backend.routes.profile.get_async_db', return_value=mock_db):
                response = await client.get("/api/profile/export")
        
        assert response.status_code == 200
        # Should return downloadable file or JSON data
        assert response.headers.get("content-type") in ["application/json", "application/octet-stream"]
    
    async def test_profile_privacy_settings(self, client, mock_user, mock_db):
        """Test updating profile privacy settings"""
        privacy_data = {
            "is_public": False,
            "show_email": False,
            "show_phone": True,
            "allow_contact": True
        }
        
        mock_db.user_profiles.update_one.return_value = AsyncMock(modified_count=1)
        
        with patch('backend.routes.profile.get_current_user_dependency', return_value=mock_user):
            with patch('backend.routes.profile.get_async_db', return_value=mock_db):
                response = await client.put("/api/profile/privacy", json=privacy_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Privacy settings updated"
    
    async def test_profile_unauthenticated_access(self, client):
        """Test accessing profile endpoints without authentication"""
        endpoints = [
            "/api/profile",
            "/api/profile/analytics",
            "/api/profile/export"
        ]
        
        for endpoint in endpoints:
            response = await client.get(endpoint)
            assert response.status_code in [401, 403]
    
    async def test_profile_data_validation(self, client, mock_user):
        """Test comprehensive profile data validation"""
        test_cases = [
            # Invalid email format
            {"email": "invalid-email", "expected_status": 422},
            # Invalid phone format
            {"phone": "123", "expected_status": 422},
            # Invalid URL format
            {"linkedin_url": "not-a-url", "expected_status": 422},
            # Skills as string instead of list
            {"skills": "Python, React", "expected_status": 422},
            # Invalid date format
            {"date_of_birth": "not-a-date", "expected_status": 422}
        ]
        
        for test_data in test_cases:
            expected_status = test_data.pop("expected_status")
            
            with patch('backend.routes.profile.get_current_user_dependency', return_value=mock_user):
                response = await client.put("/api/profile", json=test_data)
            
            assert response.status_code == expected_status 