import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import sys
import os

# Add proper paths for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from backend.main import app
from backend.admin_panel.routes import get_admin_auth, build_safe_filter, get_sort_indicator


class TestAdminAuthentication:
    """Test admin authentication functionality"""

    def test_get_admin_auth_success(self):
        """Test successful admin authentication"""
        mock_request = MagicMock()
        mock_request.session = {"admin_logged_in": True}
        
        result = get_admin_auth(mock_request)
        assert result is True

    def test_get_admin_auth_failure(self):
        """Test failed admin authentication"""
        mock_request = MagicMock()
        mock_request.session = {"admin_logged_in": False}
        
        with pytest.raises(Exception):
            get_admin_auth(mock_request)


class TestAdminHelperFunctions:
    """Test admin panel helper functions"""

    def test_build_safe_filter_valid(self):
        """Test build_safe_filter with valid input"""
        result = build_safe_filter("TechCorp", "company")
        expected = {
            "company": {
                "$regex": "TechCorp",
                "$options": "i"
            }
        }
        assert result == expected

    def test_build_safe_filter_empty(self):
        """Test build_safe_filter with empty input"""
        result = build_safe_filter("", "company")
        assert result == {}

    def test_get_sort_indicator_desc(self):
        """Test descending sort indicator"""
        result = get_sort_indicator("test", "test", "desc")
        assert result == "▼"

    def test_get_sort_indicator_asc(self):
        """Test ascending sort indicator"""
        result = get_sort_indicator("test", "test", "asc")
        assert result == "▲"


class TestAdminRoutes:
    """Test admin panel routes"""

    def test_admin_test_endpoint(self):
        """Test admin test endpoint"""
        with TestClient(app) as client:
            response = client.get("/admin/test")
            assert response.status_code == 200

    def test_admin_login_page(self):
        """Test admin login page"""
        with TestClient(app) as client:
            response = client.get("/admin/login")
            assert response.status_code == 200
            assert "Login" in response.text

    @patch('backend.admin_panel.routes.get_admin_auth')
    def test_admin_apis_page(self, mock_auth):
        """Test APIs page with authentication"""
        mock_auth.return_value = True
        
        with TestClient(app) as client:
            response = client.get("/admin/apis")
            assert response.status_code == 200

    @patch('backend.admin_panel.routes.get_admin_auth')
    def test_run_api_service(self, mock_auth):
        """Test running API service"""
        mock_auth.return_value = True
        
        with TestClient(app) as client:
            response = client.post("/admin/api-services/remoteok")
            assert response.status_code == 200

    def test_unauthenticated_access(self):
        """Test unauthenticated access"""
        with TestClient(app) as client:
            response = client.get("/admin/")
            # Should redirect or return error
            assert response.status_code in [302, 401, 404] 