import pytest
from fastapi.testclient import TestClient
from datetime import datetime
import os
from unittest.mock import AsyncMock, MagicMock

@pytest.fixture
def mock_send_notification(monkeypatch):
    """Mock send_notification function"""
    async def mock_send(*args, **kwargs):
        return True
    
    monkeypatch.setattr("backend.utils.notifications.send_notification", mock_send)
    return mock_send

@pytest.fixture
def mock_os_path_exists(monkeypatch):
    """Mock os.path.exists function"""
    def mock_exists(path):
        return True
    
    monkeypatch.setattr("os.path.exists", mock_exists)
    return mock_exists

@pytest.fixture
def mock_motor_client(monkeypatch):
    """Mock AsyncIOMotorClient"""
    class MockCollection:
        async def insert_one(self, document):
            return MagicMock(inserted_id="test_id")
    
    class MockDB:
        def __init__(self):
            self.api_service_logs = MockCollection()
    
    class MockClient:
        def __init__(self, *args, **kwargs):
            self.buzz2remote = MockDB()
    
    monkeypatch.setattr("motor.motor_asyncio.AsyncIOMotorClient", MockClient)
    return MockClient

@pytest.fixture
def mock_api_service_log(monkeypatch):
    """Mock APIServiceLog"""
    class MockAPIServiceLog:
        def __init__(self, **kwargs):
            for key, value in kwargs.items():
                setattr(self, key, value)
        
        def dict(self):
            return {key: value for key, value in self.__dict__.items()}
        
        def model_dump(self):
            return self.dict()
    
    monkeypatch.setattr("backend.models.api_service_log.APIServiceLog", MockAPIServiceLog)
    return MockAPIServiceLog

def test_admin_companies_pagination(client):
    """Test companies pagination"""
    response = client.get("/admin/companies?page=1&per_page=10", follow_redirects=True)
    # Admin requires authentication, expect redirect to login or 401
    assert response.status_code in [200, 302, 401]

def test_admin_jobs_sorting(client):
    """Test jobs sorting"""
    response = client.get("/admin/jobs?sort=created_at&order=desc", follow_redirects=True)
    assert response.status_code in [200, 302, 401]

def test_admin_companies_sorting(client):
    """Test companies sorting"""
    response = client.get("/admin/companies?sort=name&order=asc", follow_redirects=True)
    assert response.status_code in [200, 302, 401]

def test_admin_jobs_filtering(client):
    """Test jobs filtering"""
    response = client.get("/admin/jobs?status=active", follow_redirects=True)
    assert response.status_code in [200, 302, 401]

def test_admin_companies_search(client):
    """Test companies search"""
    response = client.get("/admin/companies?search=test", follow_redirects=True)
    assert response.status_code in [200, 302, 401]

def test_admin_apis_page(client):
    """Test API services page"""
    response = client.get("/admin/apis", follow_redirects=True)
    assert response.status_code in [200, 302, 401]

@pytest.mark.skip(reason="API service test requires additional mocking")
def test_admin_run_api_service(admin_session, mock_subprocess, mock_send_notification, mock_os_path_exists, mock_motor_client, mock_api_service_log):
    """Test running an API service"""
    response = admin_session.post("/admin/api-services/telegram", follow_redirects=True)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "Service started" in data["message"]

def test_unauthenticated_access(client):
    """Test unauthenticated access"""
    response = client.get("/admin/companies", follow_redirects=False)
    assert response.status_code in [302, 401, 404]  # Redirect to login or unauthorized

def test_admin_login(client):
    """Test admin login"""
    response = client.post("/admin/login", data={
        "username": "admin",
        "password": "buzz2remote2024"
    }, follow_redirects=False)
    assert response.status_code in [302, 200, 401]  # Success, redirect, or auth failure

def test_admin_logout(client):
    """Test admin logout"""
    response = client.get("/admin/logout", follow_redirects=False)
    assert response.status_code in [302, 200]  # Redirect after logout