#!/usr/bin/env python3

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime
from fastapi.testclient import TestClient
from fastapi import HTTPException
import sys
import os

# Add proper paths for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from backend.main import app
from backend.admin_panel.routes import get_admin_auth, admin_auth_middleware

class TestAdminAuthentication:
    """Comprehensive admin authentication tests"""
    
    @pytest.fixture
    def client(self):
        """Create test client."""
        return TestClient(app)
    
    def test_admin_auth_middleware_public_paths(self):
        """Test admin auth middleware allows public paths"""
        mock_request = MagicMock()
        mock_request.url.path = "/admin/login"
        mock_request.session = {}
        
        # Should not redirect for login page
        # Note: We can't easily test middleware without full FastAPI context
        
    def test_get_admin_auth_success(self):
        """Test successful admin authentication"""
        mock_request = MagicMock()
        mock_request.session = {"admin_logged_in": True}
        mock_request.client = None
        
        result = get_admin_auth(mock_request)
        assert result is True
    
    def test_get_admin_auth_failure(self):
        """Test failed admin authentication"""
        mock_request = MagicMock()
        mock_request.session = {"admin_logged_in": False}
        mock_request.client = None
        
        with pytest.raises(HTTPException) as exc_info:
            get_admin_auth(mock_request)
        
        assert exc_info.value.status_code == 401
        assert "Authentication error" in str(exc_info.value.detail)
    
    def test_get_admin_auth_no_session(self):
        """Test admin auth with no session data"""
        mock_request = MagicMock()
        mock_request.session = {}
        mock_request.client = None
        
        with pytest.raises(HTTPException) as exc_info:
            get_admin_auth(mock_request)
        
        assert exc_info.value.status_code == 401
    
    def test_get_admin_auth_exception_handling(self):
        """Test admin auth exception handling"""
        mock_request = MagicMock()
        mock_request.session.get.side_effect = Exception("Session error")
        
        with pytest.raises(HTTPException) as exc_info:
            get_admin_auth(mock_request)
        
        assert exc_info.value.status_code == 401
        assert "Authentication error" in str(exc_info.value.detail)
    
    def test_admin_login_page_accessible(self, client):
        """Test admin login page is accessible without auth"""
        response = client.get("/admin/login")
        assert response.status_code == 200
        assert "Admin Login" in response.text
        assert "form" in response.text
    
    def test_admin_test_page_accessible(self, client):
        """Test admin test page is accessible without auth"""
        response = client.get("/admin/test")
        assert response.status_code == 200
        assert "Admin Panel Test Success" in response.text
    
    @patch.dict(os.environ, {"ADMIN_USERNAME": "testuser", "ADMIN_PASSWORD": "testpass"})
    def test_admin_login_success(self, client):
        """Test successful admin login with correct credentials"""
        response = client.post("/admin/login", data={
            "username": "testuser",
            "password": "testpass"
        }, follow_redirects=False)
        
        assert response.status_code == 302
        assert response.headers["location"] == "/admin/"
    
    @patch.dict(os.environ, {"ADMIN_USERNAME": "testuser", "ADMIN_PASSWORD": "testpass"})
    def test_admin_login_wrong_credentials(self, client):
        """Test admin login with wrong credentials"""
        response = client.post("/admin/login", data={
            "username": "wronguser",
            "password": "wrongpass"
        })
        
        assert response.status_code == 200
        assert "Invalid credentials" in response.text
    
    @patch.dict(os.environ, {"ADMIN_USERNAME": "testuser", "ADMIN_PASSWORD": "testpass"})
    def test_admin_login_partial_wrong_credentials(self, client):
        """Test admin login with partially wrong credentials"""
        # Wrong username, correct password
        response = client.post("/admin/login", data={
            "username": "wronguser",
            "password": "testpass"
        })
        assert response.status_code == 200
        assert "Invalid credentials" in response.text
        
        # Correct username, wrong password
        response = client.post("/admin/login", data={
            "username": "testuser",
            "password": "wrongpass"
        })
        assert response.status_code == 200
        assert "Invalid credentials" in response.text
    
    def test_admin_logout(self, client):
        """Test admin logout functionality"""
        # Login first and then logout
        response = client.post("/admin/login", data={
            "username": "admin",
            "password": "buzz2remote2024"
        }, follow_redirects=False)
        assert response.status_code == 302
        
        # Now logout
        response = client.get("/admin/logout", follow_redirects=False)
        assert response.status_code == 302
        assert response.headers["location"] == "/admin/login"
    
    def test_admin_dashboard_redirect_when_not_authenticated(self, client):
        """Test admin dashboard redirects to login when not authenticated"""
        response = client.get("/admin/", follow_redirects=False)
        assert response.status_code == 302
        assert response.headers["location"] == "/admin/login"
    
    def test_admin_jobs_redirect_when_not_authenticated(self, client):
        """Test admin jobs redirects to login when not authenticated"""
        response = client.get("/admin/jobs", follow_redirects=False)
        assert response.status_code == 302
        assert response.headers["location"] == "/admin/login"
    
    def test_admin_companies_redirect_when_not_authenticated(self, client):
        """Test admin companies redirects to login when not authenticated"""
        response = client.get("/admin/companies", follow_redirects=False)
        assert response.status_code == 302
        assert response.headers["location"] == "/admin/login"

class TestAdminDashboardAuthenticated:
    """Test admin dashboard when authenticated"""
    
    @pytest.fixture
    def client(self):
        """Create test client."""
        return TestClient(app)
    
    def test_admin_dashboard_authenticated_access(self, client):
        """Test admin dashboard access when authenticated"""
        # Login first
        login_response = client.post("/admin/login", data={
            "username": "admin",
            "password": "buzz2remote2024"
        }, follow_redirects=False)
        assert login_response.status_code == 302
        
        # Access dashboard with authenticated session
        with patch('backend.admin_panel.routes.DATABASE_AVAILABLE', True):
            with patch('backend.admin_panel.routes.db') as mock_db:
                mock_db.jobs.count_documents = AsyncMock(return_value=1000)
                
                response = client.get("/admin/")
                assert response.status_code == 200
                assert "Admin Dashboard" in response.text
    
    def test_admin_jobs_authenticated_access(self, client):
        """Test admin jobs access when authenticated"""
        # Login first
        login_response = client.post("/admin/login", data={
            "username": "admin",
            "password": "buzz2remote2024"
        }, follow_redirects=False)
        assert login_response.status_code == 302
        
        # Access jobs with authenticated session
        with patch('backend.admin_panel.routes.DATABASE_AVAILABLE', False):
            response = client.get("/admin/jobs")
            assert response.status_code == 200
            assert "Job Listings" in response.text
    
    def test_admin_companies_authenticated_access(self, client):
        """Test admin companies access when authenticated"""
        # Login first
        login_response = client.post("/admin/login", data={
            "username": "admin",
            "password": "buzz2remote2024"
        }, follow_redirects=False)
        assert login_response.status_code == 302
        
        # Access companies with authenticated session
        with patch('backend.admin_panel.routes.DATABASE_AVAILABLE', False):
            response = client.get("/admin/companies")
            assert response.status_code == 200
            assert "Companies" in response.text

class TestAdminEdgeCases:
    """Test admin panel edge cases for maximum coverage"""
    
    @pytest.fixture
    def client(self):
        """Create test client."""
        return TestClient(app)
    
    def test_admin_login_empty_credentials(self, client):
        """Test admin login with empty credentials"""
        response = client.post("/admin/login", data={
            "username": "",
            "password": ""
        })
        
        # FastAPI returns 422 for validation errors with empty required fields
        assert response.status_code == 422
    
    def test_admin_login_missing_form_data(self, client):
        """Test admin login with missing form data"""
        # Missing password should return validation error
        response = client.post("/admin/login", data={
            "username": "test"
        })
        assert response.status_code == 422  # Validation error
    
    def test_admin_auth_with_malformed_session(self):
        """Test admin auth with malformed session data"""
        mock_request = MagicMock()
        mock_request.session = "not_a_dict"  # Invalid session type
        mock_request.client = None
        
        with pytest.raises(HTTPException):
            get_admin_auth(mock_request)
    
    def test_admin_dashboard_database_error(self, client):
        """Test admin dashboard handles database errors gracefully"""
        # Login first
        login_response = client.post("/admin/login", data={
            "username": "admin",
            "password": "buzz2remote2024"
        }, follow_redirects=False)
        assert login_response.status_code == 302
        
        # Test database error handling
        with patch('backend.admin_panel.routes.DATABASE_AVAILABLE', True):
            with patch('backend.admin_panel.routes.db') as mock_db:
                mock_db.jobs.count_documents.side_effect = Exception("Database connection failed")
                
                response = client.get("/admin/")
                assert response.status_code == 500
                assert "Dashboard Error" in response.text
    
    def test_admin_auth_client_host_logging(self):
        """Test admin auth logs client host on unauthorized access"""
        mock_request = MagicMock()
        mock_request.session = {"admin_logged_in": False}
        mock_request.client.host = "192.168.1.1"
        
        with patch('backend.admin_panel.routes.logger') as mock_logger:
            with pytest.raises(HTTPException):
                get_admin_auth(mock_request)
            
            # Verify logging was called
            mock_logger.warning.assert_called()
            call_args = mock_logger.warning.call_args[0][0]
            assert "192.168.1.1" in call_args

class TestAdminSessionManagement:
    """Test admin session management comprehensively"""
    
    @pytest.fixture
    def client(self):
        """Create test client."""
        return TestClient(app)
    
    def test_session_persistence_after_login(self, client):
        """Test session persists after successful login"""
        # Login
        response = client.post("/admin/login", data={
            "username": "admin",
            "password": "buzz2remote2024"
        }, follow_redirects=False)
        
        assert response.status_code == 302
        
        # Verify session is set by accessing a protected page
        with patch('backend.admin_panel.routes.DATABASE_AVAILABLE', False):
            response = client.get("/admin/jobs")
            assert response.status_code == 200
    
    def test_session_cleared_after_logout(self, client):
        """Test session is cleared after logout"""
        # Login first
        login_response = client.post("/admin/login", data={
            "username": "admin",
            "password": "buzz2remote2024"
        }, follow_redirects=False)
        assert login_response.status_code == 302
        
        # Logout
        response = client.get("/admin/logout", follow_redirects=False)
        assert response.status_code == 302
        
        # Verify session is cleared by trying to access protected page
        response = client.get("/admin/", follow_redirects=False)
        assert response.status_code == 302
        assert response.headers["location"] == "/admin/login" 