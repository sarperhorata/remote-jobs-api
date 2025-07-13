import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from backend.main import app

client = TestClient(app)

class TestComprehensiveEndpoints:
    def test_jobs_statistics(self):
        response = client.get("/api/jobs/statistics")
        assert response.status_code == 200
        data = response.json()
        assert "total_positions" in data
        assert "active_positions" in data
        assert "remote_positions" in data
        assert "recent_positions" in data

    def test_user_profile_unauth(self):
        response = client.get("/api/user/profile")
        assert response.status_code in [401, 403]

    @patch("backend.services.mailgun_service.mailgun_service.send_email")
    def test_email_test_endpoint(self, mock_send_email):
        mock_send_email.return_value = {"success": True, "message": "Email sent successfully"}
        response = client.post("/email-test/send-test-email?email=test@example.com")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "Test email sent successfully" in data["message"]

    def test_notifications_settings_unauth(self):
        response = client.get("/api/notifications/settings")
        assert response.status_code in [401, 403]

    def test_health_endpoint(self):
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"

    def test_status_endpoint(self):
        response = client.get("/api/status")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "database" in data

    def test_jobs_featured(self):
        response = client.get("/api/jobs/featured")
        assert response.status_code == 200
        data = response.json()
        assert "jobs" in data
        assert "total" in data

    def test_companies_featured(self):
        response = client.get("/api/companies/featured")
        assert response.status_code == 200
        data = response.json()
        assert "companies" in data
        assert "total" in data 