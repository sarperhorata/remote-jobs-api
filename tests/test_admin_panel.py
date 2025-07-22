import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from fastapi import HTTPException, status
from fastapi.testclient import TestClient
from backend.admin_panel.routes import admin_router
from backend.main import app

pytestmark = pytest.mark.asyncio

class TestAdminPanel:
    """Test admin panel routes"""
    
    def test_admin_login_success(self):
        """Test successful admin login"""
        with patch('backend.admin_panel.routes.os.getenv') as mock_getenv:
            mock_getenv.side_effect = lambda key, default="": {
                "ADMIN_USERNAME": "admin",
                "ADMIN_PASSWORD": "admin123"
            }.get(key, default)
            
            # Create test client
            test_app = app
            test_app.include_router(admin_router, prefix="/admin")
            client = TestClient(test_app)
            
            # Test login
            response = client.post("/admin/login", data={
                "username": "admin",
                "password": "admin123"
            }, follow_redirects=False)
            
            assert response.status_code == 302  # Redirect
            assert "admin_auth" in response.cookies
            assert response.cookies["admin_auth"].value == "true"
    
    def test_admin_login_failure(self):
        """Test failed admin login"""
        with patch('backend.admin_panel.routes.os.getenv') as mock_getenv:
            mock_getenv.side_effect = lambda key, default="": {
                "ADMIN_USERNAME": "admin",
                "ADMIN_PASSWORD": "admin123"
            }.get(key, default)
            
            # Create test client
            test_app = app
            test_app.include_router(admin_router, prefix="/admin")
            client = TestClient(test_app)
            
            # Test login with wrong credentials
            response = client.post("/admin/login", data={
                "username": "admin",
                "password": "wrongpassword"
            }, follow_redirects=False)
            
            assert response.status_code == 200  # Returns login page
            assert "Invalid credentials" in response.text
    
    def test_admin_login_missing_credentials(self):
        """Test admin login with missing credentials"""
        with patch('backend.admin_panel.routes.os.getenv') as mock_getenv:
            mock_getenv.side_effect = lambda key, default="": {
                "ADMIN_USERNAME": "admin",
                "ADMIN_PASSWORD": "admin123"
            }.get(key, default)
            
            # Create test client
            test_app = app
            test_app.include_router(admin_router, prefix="/admin")
            client = TestClient(test_app)
            
            # Test login with missing password
            response = client.post("/admin/login", data={
                "username": "admin"
            }, follow_redirects=False)
            
            assert response.status_code == 422  # Validation error
    
    def test_admin_dashboard_authenticated(self):
        """Test admin dashboard access when authenticated"""
        with patch('backend.admin_panel.routes.os.getenv') as mock_getenv:
            mock_getenv.side_effect = lambda key, default="": {
                "ADMIN_USERNAME": "admin",
                "ADMIN_PASSWORD": "admin123"
            }.get(key, default)
            
            # Create test client
            test_app = app
            test_app.include_router(admin_router, prefix="/admin")
            client = TestClient(test_app)
            
            # First login to get auth cookie
            login_response = client.post("/admin/login", data={
                "username": "admin",
                "password": "admin123"
            }, follow_redirects=False)
            
            # Get auth cookie
            auth_cookie = login_response.cookies.get("admin_auth")
            
            # Test dashboard access with auth cookie
            response = client.get("/admin/dashboard", cookies={"admin_auth": auth_cookie.value})
            
            assert response.status_code == 200
            assert "Admin Dashboard" in response.text
    
    def test_admin_dashboard_unauthenticated(self):
        """Test admin dashboard access when not authenticated"""
        with patch('backend.admin_panel.routes.os.getenv') as mock_getenv:
            mock_getenv.side_effect = lambda key, default="": {
                "ADMIN_USERNAME": "admin",
                "ADMIN_PASSWORD": "admin123"
            }.get(key, default)
            
            # Create test client
            test_app = app
            test_app.include_router(admin_router, prefix="/admin")
            client = TestClient(test_app)
            
            # Test dashboard access without auth cookie
            response = client.get("/admin/dashboard", follow_redirects=False)
            
            assert response.status_code == 302  # Redirect to login
            assert "/admin/login" in response.headers.get("location", "")
    
    def test_admin_logout(self):
        """Test admin logout"""
        with patch('backend.admin_panel.routes.os.getenv') as mock_getenv:
            mock_getenv.side_effect = lambda key, default="": {
                "ADMIN_USERNAME": "admin",
                "ADMIN_PASSWORD": "admin123"
            }.get(key, default)
            
            # Create test client
            test_app = app
            test_app.include_router(admin_router, prefix="/admin")
            client = TestClient(test_app)
            
            # Test logout
            response = client.get("/admin/logout", follow_redirects=False)
            
            assert response.status_code == 302  # Redirect
            assert "admin_auth" in response.cookies
            assert response.cookies["admin_auth"].value == ""  # Cleared
    
    def test_admin_users_authenticated(self):
        """Test admin users endpoint when authenticated"""
        with patch('backend.admin_panel.routes.os.getenv') as mock_getenv:
            mock_getenv.side_effect = lambda key, default="": {
                "ADMIN_USERNAME": "admin",
                "ADMIN_PASSWORD": "admin123"
            }.get(key, default)
            
            # Create test client
            test_app = app
            test_app.include_router(admin_router, prefix="/admin")
            client = TestClient(test_app)
            
            # First login to get auth cookie
            login_response = client.post("/admin/login", data={
                "username": "admin",
                "password": "admin123"
            }, follow_redirects=False)
            
            # Get auth cookie
            auth_cookie = login_response.cookies.get("admin_auth")
            
            # Test users endpoint with auth cookie
            response = client.get("/admin/users", cookies={"admin_auth": auth_cookie.value})
            
            assert response.status_code == 200
            assert "Users" in response.text
    
    def test_admin_users_unauthenticated(self):
        """Test admin users endpoint when not authenticated"""
        with patch('backend.admin_panel.routes.os.getenv') as mock_getenv:
            mock_getenv.side_effect = lambda key, default="": {
                "ADMIN_USERNAME": "admin",
                "ADMIN_PASSWORD": "admin123"
            }.get(key, default)
            
            # Create test client
            test_app = app
            test_app.include_router(admin_router, prefix="/admin")
            client = TestClient(test_app)
            
            # Test users endpoint without auth cookie
            response = client.get("/admin/users", follow_redirects=False)
            
            assert response.status_code == 302  # Redirect to login
            assert "/admin/login" in response.headers.get("location", "")
    
    def test_admin_jobs_authenticated(self):
        """Test admin jobs endpoint when authenticated"""
        with patch('backend.admin_panel.routes.os.getenv') as mock_getenv:
            mock_getenv.side_effect = lambda key, default="": {
                "ADMIN_USERNAME": "admin",
                "ADMIN_PASSWORD": "admin123"
            }.get(key, default)
            
            # Create test client
            test_app = app
            test_app.include_router(admin_router, prefix="/admin")
            client = TestClient(test_app)
            
            # First login to get auth cookie
            login_response = client.post("/admin/login", data={
                "username": "admin",
                "password": "admin123"
            }, follow_redirects=False)
            
            # Get auth cookie
            auth_cookie = login_response.cookies.get("admin_auth")
            
            # Test jobs endpoint with auth cookie
            response = client.get("/admin/jobs", cookies={"admin_auth": auth_cookie.value})
            
            assert response.status_code == 200
            assert "Jobs" in response.text
    
    def test_admin_jobs_unauthenticated(self):
        """Test admin jobs endpoint when not authenticated"""
        with patch('backend.admin_panel.routes.os.getenv') as mock_getenv:
            mock_getenv.side_effect = lambda key, default="": {
                "ADMIN_USERNAME": "admin",
                "ADMIN_PASSWORD": "admin123"
            }.get(key, default)
            
            # Create test client
            test_app = app
            test_app.include_router(admin_router, prefix="/admin")
            client = TestClient(test_app)
            
            # Test jobs endpoint without auth cookie
            response = client.get("/admin/jobs", follow_redirects=False)
            
            assert response.status_code == 302  # Redirect to login
            assert "/admin/login" in response.headers.get("location", "")
    
    def test_admin_statistics_authenticated(self):
        """Test admin statistics endpoint when authenticated"""
        with patch('backend.admin_panel.routes.os.getenv') as mock_getenv:
            mock_getenv.side_effect = lambda key, default="": {
                "ADMIN_USERNAME": "admin",
                "ADMIN_PASSWORD": "admin123"
            }.get(key, default)
            
            # Create test client
            test_app = app
            test_app.include_router(admin_router, prefix="/admin")
            client = TestClient(test_app)
            
            # First login to get auth cookie
            login_response = client.post("/admin/login", data={
                "username": "admin",
                "password": "admin123"
            }, follow_redirects=False)
            
            # Get auth cookie
            auth_cookie = login_response.cookies.get("admin_auth")
            
            # Test statistics endpoint with auth cookie
            response = client.get("/admin/statistics", cookies={"admin_auth": auth_cookie.value})
            
            assert response.status_code == 200
            assert "Statistics" in response.text
    
    def test_admin_statistics_unauthenticated(self):
        """Test admin statistics endpoint when not authenticated"""
        with patch('backend.admin_panel.routes.os.getenv') as mock_getenv:
            mock_getenv.side_effect = lambda key, default="": {
                "ADMIN_USERNAME": "admin",
                "ADMIN_PASSWORD": "admin123"
            }.get(key, default)
            
            # Create test client
            test_app = app
            test_app.include_router(admin_router, prefix="/admin")
            client = TestClient(test_app)
            
            # Test statistics endpoint without auth cookie
            response = client.get("/admin/statistics", follow_redirects=False)
            
            assert response.status_code == 302  # Redirect to login
            assert "/admin/login" in response.headers.get("location", "")
    
    def test_admin_settings_authenticated(self):
        """Test admin settings endpoint when authenticated"""
        with patch('backend.admin_panel.routes.os.getenv') as mock_getenv:
            mock_getenv.side_effect = lambda key, default="": {
                "ADMIN_USERNAME": "admin",
                "ADMIN_PASSWORD": "admin123"
            }.get(key, default)
            
            # Create test client
            test_app = app
            test_app.include_router(admin_router, prefix="/admin")
            client = TestClient(test_app)
            
            # First login to get auth cookie
            login_response = client.post("/admin/login", data={
                "username": "admin",
                "password": "admin123"
            }, follow_redirects=False)
            
            # Get auth cookie
            auth_cookie = login_response.cookies.get("admin_auth")
            
            # Test settings endpoint with auth cookie
            response = client.get("/admin/settings", cookies={"admin_auth": auth_cookie.value})
            
            assert response.status_code == 200
            assert "Settings" in response.text
    
    def test_admin_settings_unauthenticated(self):
        """Test admin settings endpoint when not authenticated"""
        with patch('backend.admin_panel.routes.os.getenv') as mock_getenv:
            mock_getenv.side_effect = lambda key, default="": {
                "ADMIN_USERNAME": "admin",
                "ADMIN_PASSWORD": "admin123"
            }.get(key, default)
            
            # Create test client
            test_app = app
            test_app.include_router(admin_router, prefix="/admin")
            client = TestClient(test_app)
            
            # Test settings endpoint without auth cookie
            response = client.get("/admin/settings", follow_redirects=False)
            
            assert response.status_code == 302  # Redirect to login
            assert "/admin/login" in response.headers.get("location", "")