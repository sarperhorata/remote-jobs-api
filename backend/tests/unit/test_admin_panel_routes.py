#!/usr/bin/env python3

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, PropertyMock
import sys
import os

# Add proper paths for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from backend.main import app

class TestAdminRoutes:
    """Test admin routes - simple but effective"""

    def test_admin_login_page_exists(self):
        """Test admin login page exists"""
        with TestClient(app) as client:
            response = client.get("/admin/login")
            assert response.status_code == 200
            assert "login" in response.text.lower()

    def test_admin_test_endpoint_exists(self):
        """Test admin test endpoint exists"""
        with TestClient(app) as client:
            response = client.get("/admin/test")
            assert response.status_code == 200

    def test_admin_dashboard_requires_auth(self):
        """Test admin dashboard requires authentication"""
        with TestClient(app) as client:
            response = client.get("/admin/", follow_redirects=False)
            # Should redirect to login when not authenticated
            assert response.status_code == 302
            assert "/admin/login" in response.headers.get("location", "")

    def test_admin_logout_works(self):
        """Test admin logout works"""
        with TestClient(app) as client:
            response = client.get("/admin/logout", follow_redirects=False)
            assert response.status_code == 302

    @patch.dict(os.environ, {"ADMIN_USERNAME": "admin", "ADMIN_PASSWORD": "password"})
    def test_admin_login_with_credentials(self):
        """Test admin login with valid credentials"""
        with TestClient(app) as client:
            response = client.post("/admin/login", data={
                "username": "admin",
                "password": "password"
            }, follow_redirects=False)
            
            # Should redirect after successful login
            assert response.status_code == 302

    def test_admin_routes_exist(self):
        """Test that admin routes exist and respond appropriately"""
        with TestClient(app) as client:
            # These routes should exist and either redirect to login or show content
            routes_to_test = [
                "/admin/jobs",
                "/admin/companies", 
                "/admin/status"
            ]
            
            for route in routes_to_test:
                response = client.get(route, follow_redirects=False)
                # Should not return 404 (route exists), may redirect (302) or return 200/401/500
                assert response.status_code != 404, f"Route {route} should exist"
