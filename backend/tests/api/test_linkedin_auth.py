import os
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from backend.main import app

client = TestClient(app)


class TestLinkedInAuth:
    """LinkedIn OAuth endpointleri için test sınıfı"""

    @patch.dict(
        os.environ,
        {
            "LINKEDIN_CLIENT_ID": "test_client_id",
            "LINKEDIN_CLIENT_SECRET": "test_client_secret",
            "LINKEDIN_REDIRECT_URI": "http://localhost:3000/auth/linkedin/callback",
        },
    )
    def test_linkedin_auth_url_success(self):
        """LinkedIn auth URL endpoint'i başarılı durumda çalışmalı"""
        response = client.get("/api/v1/auth/linkedin/auth-url")

        assert response.status_code == 200
        data = response.json()
        assert "auth_url" in data
        assert "linkedin.com/oauth/v2/authorization" in data["auth_url"]
        assert "test_client_id" in data["auth_url"]
        assert "r_liteprofile" in data["auth_url"]
        assert "r_emailaddress" in data["auth_url"]

    @patch.dict(
        os.environ,
        {
            "LINKEDIN_CLIENT_ID": "",
            "LINKEDIN_CLIENT_SECRET": "",
            "LINKEDIN_REDIRECT_URI": "",
        },
    )
    def test_linkedin_auth_url_missing_config(self):
        """LinkedIn config eksikse hata dönmeli"""
        response = client.get("/api/v1/auth/linkedin/auth-url")

        assert response.status_code == 200  # URL oluşturulur ama boş değerlerle
        data = response.json()
        assert "auth_url" in data

    @patch("backend.utils.linkedin.LinkedInIntegration.exchange_code_for_token")
    @patch("backend.utils.linkedin.LinkedInIntegration.get_user_profile")
    @patch("backend.database.get_async_db")
    async def test_linkedin_callback_success_new_user(
        self, mock_db, mock_get_profile, mock_exchange_token
    ):
        """LinkedIn callback başarılı - yeni kullanıcı"""
        # Mock setup
        mock_exchange_token.return_value = "test_access_token"
        mock_get_profile.return_value = {
            "email": "test@example.com",
            "name": "Test User",
            "linkedin_url": "https://linkedin.com/in/testuser",
            "profile_photo_url": "https://example.com/photo.jpg",
        }

        mock_db_instance = MagicMock()
        mock_db_instance.users.find_one.return_value = None  # Kullanıcı yok
        mock_db_instance.users.insert_one.return_value.inserted_id = "test_user_id"
        mock_db.return_value = mock_db_instance

        response = client.post(
            "/api/v1/auth/linkedin/callback", json={"code": "test_auth_code"}
        )

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "token_type" in data
        assert data["token_type"] == "bearer"
        assert "user" in data
        assert data["user"]["email"] == "test@example.com"
        assert data["user"]["full_name"] == "Test User"

    @patch("backend.utils.linkedin.LinkedInIntegration.exchange_code_for_token")
    @patch("backend.utils.linkedin.LinkedInIntegration.get_user_profile")
    @patch("backend.database.get_async_db")
    async def test_linkedin_callback_success_existing_user(
        self, mock_db, mock_get_profile, mock_exchange_token
    ):
        """LinkedIn callback başarılı - mevcut kullanıcı"""
        # Mock setup
        mock_exchange_token.return_value = "test_access_token"
        mock_get_profile.return_value = {
            "email": "existing@example.com",
            "name": "Existing User",
            "linkedin_url": "https://linkedin.com/in/existinguser",
            "profile_photo_url": "https://example.com/photo.jpg",
        }

        existing_user = {
            "_id": "existing_user_id",
            "email": "existing@example.com",
            "name": "Old Name",
        }

        mock_db_instance = MagicMock()
        mock_db_instance.users.find_one.return_value = existing_user
        mock_db_instance.users.update_one.return_value = None
        mock_db.return_value = mock_db_instance

        response = client.post(
            "/api/v1/auth/linkedin/callback", json={"code": "test_auth_code"}
        )

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "user" in data
        assert data["user"]["id"] == "existing_user_id"

    def test_linkedin_callback_missing_code(self):
        """LinkedIn callback - code eksik"""
        response = client.post("/api/v1/auth/linkedin/callback", json={})

        assert response.status_code == 400
        data = response.json()
        assert "No authorization code provided" in data["detail"]

    @patch("backend.utils.linkedin.LinkedInIntegration.exchange_code_for_token")
    def test_linkedin_callback_token_exchange_failed(self, mock_exchange_token):
        """LinkedIn callback - token exchange başarısız"""
        mock_exchange_token.return_value = None

        response = client.post(
            "/api/v1/auth/linkedin/callback", json={"code": "invalid_code"}
        )

        assert response.status_code == 400
        data = response.json()
        assert "Failed to get access token from LinkedIn" in data["detail"]

    @patch("backend.utils.linkedin.LinkedInIntegration.exchange_code_for_token")
    @patch("backend.utils.linkedin.LinkedInIntegration.get_user_profile")
    def test_linkedin_callback_profile_fetch_failed(
        self, mock_get_profile, mock_exchange_token
    ):
        """LinkedIn callback - profil fetch başarısız"""
        mock_exchange_token.return_value = "test_access_token"
        mock_get_profile.return_value = None

        response = client.post(
            "/api/v1/auth/linkedin/callback", json={"code": "test_code"}
        )

        assert response.status_code == 400
        data = response.json()
        assert "Failed to fetch LinkedIn profile or email" in data["detail"]

    @patch("backend.utils.linkedin.LinkedInIntegration.exchange_code_for_token")
    @patch("backend.utils.linkedin.LinkedInIntegration.get_user_profile")
    def test_linkedin_callback_profile_no_email(
        self, mock_get_profile, mock_exchange_token
    ):
        """LinkedIn callback - profil var ama email yok"""
        mock_exchange_token.return_value = "test_access_token"
        mock_get_profile.return_value = {
            "name": "Test User",
            "linkedin_url": "https://linkedin.com/in/testuser",
            # email yok
        }

        response = client.post(
            "/api/v1/auth/linkedin/callback", json={"code": "test_code"}
        )

        assert response.status_code == 400
        data = response.json()
        assert "Failed to fetch LinkedIn profile or email" in data["detail"]

    @patch("backend.utils.linkedin.LinkedInIntegration.exchange_code_for_token")
    def test_linkedin_callback_exception_handling(self, mock_exchange_token):
        """LinkedIn callback - exception handling"""
        mock_exchange_token.side_effect = Exception("Network error")

        response = client.post(
            "/api/v1/auth/linkedin/callback", json={"code": "test_code"}
        )

        assert response.status_code == 400
        data = response.json()
        assert "Failed to get access token from LinkedIn" in data["detail"]


class TestLinkedInIntegration:
    """LinkedInIntegration sınıfı için testler"""

    @patch.dict(
        os.environ,
        {
            "LINKEDIN_CLIENT_ID": "test_client_id",
            "LINKEDIN_CLIENT_SECRET": "test_client_secret",
            "LINKEDIN_REDIRECT_URI": "http://localhost:3000/auth/linkedin/callback",
        },
    )
    def test_get_authorization_url(self):
        """Authorization URL oluşturma testi"""
        from backend.utils.linkedin import LinkedInIntegration

        linkedin = LinkedInIntegration()
        url = linkedin.get_authorization_url()

        assert "linkedin.com/oauth/v2/authorization" in url
        assert "test_client_id" in url
        assert "r_liteprofile" in url
        assert "r_emailaddress" in url

    @patch("requests.post")
    def test_exchange_code_for_token_success(self, mock_post):
        """Token exchange başarılı testi"""
        from backend.utils.linkedin import LinkedInIntegration

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"access_token": "test_token"}
        mock_post.return_value = mock_response

        linkedin = LinkedInIntegration()
        token = linkedin.exchange_code_for_token("test_code")

        assert token == "test_token"

    @patch("requests.post")
    def test_exchange_code_for_token_failure(self, mock_post):
        """Token exchange başarısız testi"""
        from backend.utils.linkedin import LinkedInIntegration

        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.text = "Invalid code"
        mock_post.return_value = mock_response

        linkedin = LinkedInIntegration()
        token = linkedin.exchange_code_for_token("invalid_code")

        assert token is None

    @patch("requests.get")
    def test_get_user_profile_success(self, mock_get):
        """Profil fetch başarılı testi"""
        from backend.utils.linkedin import LinkedInIntegration

        # Mock profile response
        profile_response = MagicMock()
        profile_response.status_code = 200
        profile_response.json.return_value = {
            "localizedFirstName": "Test",
            "localizedLastName": "User",
            "profilePicture": {
                "displayImage~": {
                    "elements": [
                        {
                            "identifiers": [
                                {"identifier": "https://example.com/photo.jpg"}
                            ]
                        }
                    ]
                }
            },
        }

        # Mock email response
        email_response = MagicMock()
        email_response.status_code = 200
        email_response.json.return_value = {
            "elements": [{"handle~": {"emailAddress": "test@example.com"}}]
        }

        mock_get.side_effect = [profile_response, email_response]

        linkedin = LinkedInIntegration()
        profile = linkedin.get_user_profile("test_token")

        assert profile is not None
        assert profile["email"] == "test@example.com"
        assert profile["name"] == "Test User"
        assert profile["profile_photo_url"] == "https://example.com/photo.jpg"

    @patch("requests.get")
    def test_get_user_profile_failure(self, mock_get):
        """Profil fetch başarısız testi"""
        from backend.utils.linkedin import LinkedInIntegration

        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_response.text = "Unauthorized"
        mock_get.return_value = mock_response

        linkedin = LinkedInIntegration()
        profile = linkedin.get_user_profile("invalid_token")

        assert profile is None
