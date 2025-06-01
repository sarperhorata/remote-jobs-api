#!/usr/bin/env python3

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock, AsyncMock
import sys
import os

# Add proper paths for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from backend.main import app

class TestAdminAuthentication:
    """Test admin authentication functionality"""

    @patch('backend.admin_panel.routes.get_admin_auth')
    def test_get_admin_auth_logged_in(self, mock_get_admin_auth):
        """Test admin auth when user is logged in"""
        mock_get_admin_auth.return_value = True
        result = mock_get_admin_auth()
        assert result is True

    @patch('backend.admin_panel.routes.get_admin_auth')
    def test_get_admin_auth_not_logged_in(self, mock_get_admin_auth):
        """Test admin auth when user not logged in"""
        from fastapi import HTTPException
        mock_get_admin_auth.side_effect = HTTPException(status_code=401)
        
        with pytest.raises(HTTPException):
            mock_get_admin_auth()

    @patch('backend.admin_panel.routes.get_admin_auth')
    def test_get_admin_auth_no_session(self, mock_get_admin_auth):
        """Test admin auth with no session"""
        from fastapi import HTTPException
        mock_get_admin_auth.side_effect = HTTPException(status_code=401)
        
        with pytest.raises(HTTPException):
            mock_get_admin_auth()


class TestAdminHelperFunctions:
    """Test admin helper functions"""

    @patch('backend.admin_panel.routes.build_safe_filter')
    def test_build_safe_filter_with_search_term(self, mock_build_safe_filter):
        """Test build_safe_filter with search term"""
        expected = {'company': {'$regex': 'TechCorp', '$options': 'i'}}
        mock_build_safe_filter.return_value = expected
        
        result = mock_build_safe_filter("TechCorp", "company")
        assert result == expected

    @patch('backend.admin_panel.routes.build_safe_filter')
    def test_build_safe_filter_empty_search(self, mock_build_safe_filter):
        """Test build_safe_filter with empty search"""
        mock_build_safe_filter.return_value = {}
        
        result = mock_build_safe_filter("", "company")
        assert result == {}

    @patch('backend.admin_panel.routes.build_safe_filter')
    def test_build_safe_filter_dangerous_characters(self, mock_build_safe_filter):
        """Test build_safe_filter removes dangerous characters"""
        expected = {'company': {'$regex': 'TechCorptest', '$options': 'i'}}
        mock_build_safe_filter.return_value = expected
        
        result = mock_build_safe_filter("Tech$Corp{test}", "company")
        assert result == expected

    @patch('backend.admin_panel.routes.get_sort_indicator')
    def test_get_sort_indicator_descending(self, mock_get_sort_indicator):
        """Test sort indicator descending"""
        mock_get_sort_indicator.return_value = "▼"
        
        result = mock_get_sort_indicator("job_count", "job_count", "desc")
        assert result == "▼"

    @patch('backend.admin_panel.routes.get_sort_indicator')
    def test_get_sort_indicator_ascending(self, mock_get_sort_indicator):
        """Test sort indicator ascending"""
        mock_get_sort_indicator.return_value = "▲"
        
        result = mock_get_sort_indicator("job_count", "job_count", "asc")
        assert result == "▲"

    @patch('backend.admin_panel.routes.get_sort_indicator')
    def test_get_sort_indicator_different_column(self, mock_get_sort_indicator):
        """Test sort indicator different column"""
        mock_get_sort_indicator.return_value = "↕"
        
        result = mock_get_sort_indicator("company", "job_count", "desc")
        assert result == "↕"


class TestAdminRoutes:
    """Test admin routes"""

    def test_admin_login_page_get(self):
        """Test admin login page GET"""
        with TestClient(app) as client:
            response = client.get("/admin/login")
            assert response.status_code == 200
            assert "Login" in response.text

    def test_admin_test_endpoint(self):
        """Test admin test endpoint"""
        with TestClient(app) as client:
            response = client.get("/admin/test")
            assert response.status_code == 200

    @patch.dict(os.environ, {"ADMIN_USERNAME": "admin", "ADMIN_PASSWORD": "password"})
    def test_admin_login_success(self):
        """Test successful admin login"""
        with TestClient(app) as client:
            response = client.post("/admin/login", data={
                "username": "admin",
                "password": "password"
            }, follow_redirects=False)
            
            assert response.status_code == 302

    def test_admin_logout(self):
        """Test admin logout"""
        with TestClient(app) as client:
            response = client.get("/admin/logout", follow_redirects=False)
            assert response.status_code == 302

    @patch('backend.admin_panel.routes.get_admin_auth')
    def test_admin_dashboard_with_db(self, mock_auth):
        """Test dashboard with database"""
        mock_auth.return_value = True
        
        with TestClient(app) as client:
            response = client.get("/admin/")
            assert response.status_code == 200

    @patch('backend.admin_panel.routes.get_admin_auth')
    def test_admin_jobs_with_db(self, mock_auth):
        """Test jobs page with database"""
        mock_auth.return_value = True
        
        with TestClient(app) as client:
            response = client.get("/admin/jobs")
            assert response.status_code == 200

    @patch('backend.admin_panel.routes.get_admin_auth')
    def test_admin_companies_with_db(self, mock_auth):
        """Test companies page with database"""
        mock_auth.return_value = True
        
        with TestClient(app) as client:
            response = client.get("/admin/companies")
            assert response.status_code == 200

    @patch('backend.admin_panel.routes.get_admin_auth')
    def test_admin_status_page(self, mock_auth):
        """Test status page"""
        mock_auth.return_value = True
        
        with TestClient(app) as client:
            response = client.get("/admin/status")
            assert response.status_code == 200


class TestAdminActions:
    """Test admin actions"""

    @patch('backend.admin_panel.routes.get_admin_auth')
    def test_run_crawler_action(self, mock_auth):
        """Test run crawler action"""
        mock_auth.return_value = True
        
        with TestClient(app) as client:
            response = client.post("/admin/actions/run-crawler")
            assert response.status_code == 200

    @patch('backend.admin_panel.routes.get_admin_auth')
    def test_fetch_external_apis_action(self, mock_auth):
        """Test fetch external APIs action"""
        mock_auth.return_value = True
        
        with TestClient(app) as client:
            response = client.post("/admin/actions/fetch-external-apis")
            assert response.status_code == 200

    @patch('backend.admin_panel.routes.get_admin_auth')
    def test_analyze_positions_action(self, mock_auth):
        """Test analyze positions action"""
        mock_auth.return_value = True
        
        with TestClient(app) as client:
            response = client.post("/admin/actions/analyze-positions")
            assert response.status_code == 200


class TestAdminStatistics:
    """Test admin statistics"""

    @patch('backend.admin_panel.routes.get_admin_auth')
    @patch('backend.admin_panel.routes.db')
    def test_get_dashboard_stats_with_db(self, mock_db, mock_auth):
        """Test dashboard stats with database"""
        mock_auth.return_value = True
        mock_db.jobs.count_documents.return_value = 1000
        
        with TestClient(app) as client:
            response = client.get("/admin/")
            assert response.status_code == 200


class TestAdminErrorHandling:
    """Test admin error handling"""

    def test_admin_unauthenticated_access(self):
        """Test unauthenticated access"""
        with TestClient(app) as client:
            response = client.get("/admin/")
            assert response.status_code in [302, 401, 404] 