import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
from backend.main import app

client = TestClient(app)

def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to Buzz2Remote API v3"}

def test_health_check():
    with patch('backend.main.get_async_db') as mock_db:
        mock_db.return_value.command.return_value = True
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "database" in data
        assert "timestamp" in data
        assert data["version"] == "3.0.0"

def test_api_health_check():
    with patch('backend.main.get_async_db') as mock_db:
        mock_db.return_value.command.return_value = True
        response = client.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"

def test_api_v1_health():
    response = client.get("/api/v1/health")
    assert response.status_code == 200

def test_api_v1_status():
    response = client.get("/api/v1/status")
    assert response.status_code == 200

def test_job_statistics():
    response = client.get("/api/jobs/statistics")
    assert response.status_code == 200

def test_featured_jobs():
    response = client.get("/api/jobs/featured")
    assert response.status_code == 200

def test_companies_statistics():
    response = client.get("/api/companies/statistics")
    assert response.status_code == 200

def test_featured_companies():
    response = client.get("/api/companies/featured")
    assert response.status_code == 200

def test_search_suggestions():
    response = client.get("/api/search/suggestions?q=python")
    assert response.status_code == 200

def test_cors_headers():
    response = client.options("/")
    assert "access-control-allow-origin" in response.headers

def test_error_handling():
    response = client.get("/invalid-endpoint")
    assert response.status_code == 404

def test_method_not_allowed():
    response = client.post("/")
    assert response.status_code == 405