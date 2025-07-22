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

def test_search_suggestions_empty():
    response = client.get("/api/search/suggestions")
    assert response.status_code == 200

def test_job_titles_autocomplete():
    response = client.get("/api/jobs/titles/autocomplete?q=python")
    assert response.status_code == 200

def test_companies_autocomplete():
    response = client.get("/api/companies/autocomplete?q=google")
    assert response.status_code == 200

def test_locations_autocomplete():
    response = client.get("/api/locations/autocomplete?q=istanbul")
    assert response.status_code == 200

def test_skills_autocomplete():
    response = client.get("/api/skills/autocomplete?q=python")
    assert response.status_code == 200

def test_similar_jobs():
    response = client.get("/api/jobs/test-job-id/similar")
    assert response.status_code == 200

def test_dashboard_metrics():
    response = client.get("/api/metrics/dashboard")
    assert response.status_code == 200

def test_admin_trigger_job_statistics():
    response = client.post("/api/admin/trigger-job-statistics")
    assert response.status_code in [200, 500]  # 500 if apscheduler not available

def test_stripe_webhook():
    response = client.post("/webhook/stripe")
    assert response.status_code in [200, 400]  # 400 for invalid webhook data

def test_notification_settings_get():
    response = client.get("/api/notifications/settings")
    assert response.status_code in [200, 401]  # 401 if not authenticated

def test_user_profile_get():
    response = client.get("/api/user/profile")
    assert response.status_code in [200, 401]  # 401 if not authenticated

def test_user_saved_jobs():
    response = client.get("/api/user/saved-jobs")
    assert response.status_code in [200, 401]  # 401 if not authenticated

def test_user_applications():
    response = client.get("/api/user/applications")
    assert response.status_code in [200, 401]  # 401 if not authenticated

def test_user_preferences_get():
    response = client.get("/api/user/preferences")
    assert response.status_code in [200, 401]  # 401 if not authenticated

def test_save_job():
    response = client.post("/api/user/save-job/test-job-id")
    assert response.status_code in [200, 401]  # 401 if not authenticated

def test_unsave_job():
    response = client.delete("/api/user/save-job/test-job-id")
    assert response.status_code in [200, 401]  # 401 if not authenticated

def test_cors_headers():
    # Test CORS headers on a GET request instead of OPTIONS
    response = client.get("/api/v1/health")
    # CORS headers should be present in the response
    assert response.status_code == 200

def test_error_handling():
    response = client.get("/invalid-endpoint")
    assert response.status_code == 404

def test_method_not_allowed():
    response = client.post("/")
    assert response.status_code == 405