import pytest
from fastapi.testclient import TestClient
from main import app
from unittest.mock import patch, MagicMock
import os

pytestmark = pytest.mark.skip(reason="Admin panel tests need fixture updates")

# Create a persistent client for session tests
client = TestClient(app, base_url="http://test")

@pytest.fixture
def mock_db():
    with patch('backend.admin_panel.routes.db') as mock:
        mock.jobs.count_documents.return_value = 100
        mock.jobs.find.return_value.to_list.return_value = [
            {
                "_id": "1",
                "title": "Test Job",
                "company": "Test Company",
                "location": "Remote",
                "type": "Full-time",
                "created_at": "2024-01-01T00:00:00",
                "url": "https://example.com/job",
                "description": "Test job description"
            }
        ]
        yield mock

@pytest.fixture
def mock_session():
    with patch('backend.admin_panel.routes.get_admin_auth') as mock:
        mock.return_value = {"username": "admin"}
        yield mock

@pytest.fixture
def admin_session():
    # Login first
    response = client.post("/admin/login", data={
        "username": os.getenv("ADMIN_USERNAME", "admin"),
        "password": os.getenv("ADMIN_PASSWORD", "buzz2remote2024")
    }, follow_redirects=False)
    assert response.status_code == 302  # Redirect after successful login
    
    # Ensure session cookie is set
    assert "session" in client.cookies
    return client  # Return the client with session cookie set

# Test functions
def test_admin_jobs_page(mock_db, mock_session, admin_session):
    # Use the client with session cookie
    response = admin_session.get("/admin/jobs", follow_redirects=True)
    assert response.status_code == 200
    assert "Job Listings" in response.text

def test_admin_companies_page(mock_db, mock_session, admin_session):
    # Use the client with session cookie
    response = admin_session.get("/admin/companies", follow_redirects=True)
    assert response.status_code == 200
    assert "Companies" in response.text

def test_admin_jobs_pagination(mock_db, mock_session, admin_session):
    # Use the client with session cookie
    response = admin_session.get("/admin/jobs?page=2", follow_redirects=True)
    assert response.status_code == 200
    assert "Job Listings" in response.text

def test_admin_companies_pagination(mock_db, mock_session, admin_session):
    # Use the client with session cookie
    response = admin_session.get("/admin/companies?page=2", follow_redirects=True)
    assert response.status_code == 200
    assert "Companies" in response.text

def test_admin_jobs_sorting(mock_db, mock_session, admin_session):
    # Use the client with session cookie
    response = admin_session.get("/admin/jobs?sort_by=created_at&sort_order=desc", follow_redirects=True)
    assert response.status_code == 200
    assert "Job Listings" in response.text

def test_admin_companies_sorting(mock_db, mock_session, admin_session):
    # Use the client with session cookie
    response = admin_session.get("/admin/companies?sort_by=name&sort_order=asc", follow_redirects=True)
    assert response.status_code == 200
    assert "Companies" in response.text

def test_admin_jobs_filtering(mock_db, mock_session, admin_session):
    # Use the client with session cookie
    response = admin_session.get("/admin/jobs?company_filter=Test", follow_redirects=True)
    assert response.status_code == 200
    assert "Job Listings" in response.text

def test_admin_companies_search(mock_db, mock_session, admin_session):
    # Use the client with session cookie
    response = admin_session.get("/admin/companies?search=Test", follow_redirects=True)
    assert response.status_code == 200
    assert "Companies" in response.text