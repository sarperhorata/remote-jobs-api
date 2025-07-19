import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from fastapi.testclient import TestClient
from backend.main import app
import os
from datetime import datetime

client = TestClient(app)

# JWT authentication mock'u
@pytest.fixture(autouse=True)
def mock_jwt_auth():
    with patch('backend.routes.auth.get_current_user') as mock_auth:
        mock_auth.return_value = {"user_id": "user_id_123", "email": "test@example.com"}
        yield mock_auth

class TestLinkedInCV:
    """LinkedIn CV çekme özelliği için test sınıfı"""
    
    @patch('backend.utils.linkedin.LinkedInIntegration.get_user_cv_data')
    @patch('backend.database.get_async_db')
    def test_linkedin_fetch_cv_success(self, mock_db, mock_get_cv_data, mock_jwt_auth):
        """LinkedIn CV fetch başarılı durumda çalışmalı"""
        # Mock setup
        mock_cv_data = {
            "name": "Test User",
            "email": "test@example.com",
            "experience": [
                {
                    "title": "Software Engineer",
                    "company": "Tech Corp",
                    "start_date": "2020",
                    "end_date": "Present",
                    "summary": "Developed web applications"
                }
            ],
            "education": [
                {
                    "school": "University of Test",
                    "degree": "Bachelor's",
                    "field": "Computer Science",
                    "start_date": "2016",
                    "end_date": "2020"
                }
            ],
            "skills": [
                {"name": "Python", "id": "1"},
                {"name": "JavaScript", "id": "2"}
            ],
            "summary": "Experienced software engineer",
            "location": "San Francisco",
            "industry": "Technology"
        }
        
        mock_get_cv_data.return_value = mock_cv_data
        
        mock_user = {
            "_id": "user_id_123",
            "linkedin_connected": True,
            "linkedin_access_token": "test_token"
        }
        
        mock_db_instance = MagicMock()
        mock_db_instance.users.find_one.return_value = mock_user
        mock_db_instance.users.update_one.return_value = MagicMock()
        mock_db.return_value = mock_db_instance
        
        # Test request
        response = client.post(
            "/api/v1/auth/linkedin/fetch-cv",
            headers={"Authorization": "Bearer test_token"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "CV data successfully imported from LinkedIn"
        assert data["cv_data"]["experience_count"] == 1
        assert data["cv_data"]["education_count"] == 1
        assert data["cv_data"]["skills_count"] == 2
        
        # Verify database update was called
        mock_db_instance.users.update_one.assert_called_once()
    
    @patch('backend.database.get_async_db')
    def test_linkedin_fetch_cv_not_connected(self, mock_db, mock_jwt_auth):
        """LinkedIn bağlı değilse hata dönmeli"""
        mock_user = {
            "_id": "user_id_123",
            "linkedin_connected": False
        }
        
        mock_db_instance = MagicMock()
        mock_db_instance.users.find_one.return_value = mock_user
        mock_db.return_value = mock_db_instance
        
        response = client.post(
            "/api/v1/auth/linkedin/fetch-cv",
            headers={"Authorization": "Bearer test_token"}
        )
        
        assert response.status_code == 400
        assert "LinkedIn account not connected" in response.json()["detail"]
    
    @patch('backend.database.get_async_db')
    def test_linkedin_fetch_cv_no_token(self, mock_db, mock_jwt_auth):
        """LinkedIn access token yoksa hata dönmeli"""
        mock_user = {
            "_id": "user_id_123",
            "linkedin_connected": True
            # No linkedin_access_token
        }
        
        mock_db_instance = MagicMock()
        mock_db_instance.users.find_one.return_value = mock_user
        mock_db.return_value = mock_db_instance
        
        response = client.post(
            "/api/v1/auth/linkedin/fetch-cv",
            headers={"Authorization": "Bearer test_token"}
        )
        
        assert response.status_code == 400
        assert "LinkedIn access token not available" in response.json()["detail"]
    
    @patch('backend.utils.linkedin.LinkedInIntegration.get_user_cv_data')
    @patch('backend.database.get_async_db')
    def test_linkedin_fetch_cv_api_failure(self, mock_db, mock_get_cv_data, mock_jwt_auth):
        """LinkedIn API hatası durumunda hata dönmeli"""
        mock_get_cv_data.return_value = None
        
        mock_user = {
            "_id": "user_id_123",
            "linkedin_connected": True,
            "linkedin_access_token": "test_token"
        }
        
        mock_db_instance = MagicMock()
        mock_db_instance.users.find_one.return_value = mock_user
        mock_db.return_value = mock_db_instance
        
        response = client.post(
            "/api/v1/auth/linkedin/fetch-cv",
            headers={"Authorization": "Bearer test_token"}
        )
        
        assert response.status_code == 400
        assert "Failed to fetch LinkedIn CV data" in response.json()["detail"]

class TestLinkedInCVIntegration:
    """LinkedIn CV Integration sınıfı için testler"""
    
    @patch.dict(os.environ, {
        'LINKEDIN_CLIENT_ID': 'test_client_id',
        'LINKEDIN_CLIENT_SECRET': 'test_client_secret',
        'LINKEDIN_REDIRECT_URI': 'http://localhost:3000/auth/linkedin/callback'
    })
    def test_get_user_cv_data_success(self):
        """get_user_cv_data başarılı durumda çalışmalı"""
        from backend.utils.linkedin import LinkedInIntegration
        
        linkedin = LinkedInIntegration()
        
        with patch.object(linkedin, 'get_user_profile') as mock_profile, \
             patch.object(linkedin, '_get_experience') as mock_exp, \
             patch.object(linkedin, '_get_education') as mock_edu, \
             patch.object(linkedin, '_get_skills') as mock_skills:
            
            mock_profile.return_value = {
                "name": "Test User",
                "email": "test@example.com",
                "title": "Software Engineer"
            }
            mock_exp.return_value = [{"title": "Engineer", "company": "Tech"}]
            mock_edu.return_value = [{"school": "University", "degree": "BS"}]
            mock_skills.return_value = [{"name": "Python", "id": "1"}]
            
            result = linkedin.get_user_cv_data("test_token")
            
            assert result is not None
            assert result["name"] == "Test User"
            assert result["email"] == "test@example.com"
            assert len(result["experience"]) == 1
            assert len(result["education"]) == 1
            assert len(result["skills"]) == 1
            assert result["cv_source"] == "linkedin"
            assert "cv_updated_at" in result
    
    def test_get_experience_success(self):
        """_get_experience başarılı durumda çalışmalı"""
        from backend.utils.linkedin import LinkedInIntegration
        
        linkedin = LinkedInIntegration()
        
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "positions": {
                "elements": [
                    {
                        "title": "Software Engineer",
                        "company": {"name": "Tech Corp"},
                        "startDate": {"year": "2020"},
                        "endDate": None,
                        "summary": "Developed apps",
                        "location": {"name": "SF"}
                    }
                ]
            }
        }
        
        with patch('requests.get', return_value=mock_response):
            result = linkedin._get_experience("test_token")
            
            assert len(result) == 1
            assert result[0]["title"] == "Software Engineer"
            assert result[0]["company"] == "Tech Corp"
            assert result[0]["start_date"] == "2020"
            assert result[0]["end_date"] == "Present"
    
    def test_get_education_success(self):
        """_get_education başarılı durumda çalışmalı"""
        from backend.utils.linkedin import LinkedInIntegration
        
        linkedin = LinkedInIntegration()
        
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "educations": {
                "elements": [
                    {
                        "schoolName": "University of Test",
                        "degreeName": "Bachelor's",
                        "fieldOfStudy": "Computer Science",
                        "startDate": {"year": "2016"},
                        "endDate": {"year": "2020"},
                        "grade": "3.8",
                        "description": "Computer Science degree"
                    }
                ]
            }
        }
        
        with patch('requests.get', return_value=mock_response):
            result = linkedin._get_education("test_token")
            
            assert len(result) == 1
            assert result[0]["school"] == "University of Test"
            assert result[0]["degree"] == "Bachelor's"
            assert result[0]["field"] == "Computer Science"
            assert result[0]["start_date"] == "2016"
            assert result[0]["end_date"] == "2020"
    
    def test_get_skills_success(self):
        """_get_skills başarılı durumda çalışmalı"""
        from backend.utils.linkedin import LinkedInIntegration
        
        linkedin = LinkedInIntegration()
        
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "skills": {
                "elements": [
                    {
                        "skill": {
                            "name": "Python",
                            "id": "1"
                        }
                    },
                    {
                        "skill": {
                            "name": "JavaScript",
                            "id": "2"
                        }
                    }
                ]
            }
        }
        
        with patch('requests.get', return_value=mock_response):
            result = linkedin._get_skills("test_token")
            
            assert len(result) == 2
            assert result[0]["name"] == "Python"
            assert result[0]["id"] == "1"
            assert result[1]["name"] == "JavaScript"
            assert result[1]["id"] == "2" 