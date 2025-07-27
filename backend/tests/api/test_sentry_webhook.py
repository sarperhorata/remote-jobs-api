import json
from datetime import datetime
from unittest.mock import AsyncMock, Mock, patch

import pytest
from fastapi.testclient import TestClient


class TestSentryWebhookRoutes:
    """Test Sentry webhook routes"""

    def test_sentry_webhook_endpoint_exists(self, client: TestClient):
        """Test that Sentry webhook endpoint exists"""
        response = client.get("/api/v1/webhooks/sentry")
        assert response.status_code in [
            405,
            422,
        ]  # Method not allowed or validation error

    def test_sentry_webhook_post_success(self, client: TestClient):
        """Test successful Sentry webhook POST request"""
        webhook_data = {
            "event": {
                "id": "test_event_123",
                "message": "Test error message",
                "level": "error",
                "timestamp": datetime.now().isoformat(),
                "project": "buzz2remote-backend",
            },
            "project": {"name": "buzz2remote-backend", "slug": "buzz2remote-backend"},
        }

        response = client.post(
            "/api/v1/webhooks/sentry",
            json=webhook_data,
            headers={"Content-Type": "application/json"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "Webhook processed" in data["message"]

    def test_sentry_webhook_invalid_json(self, client: TestClient):
        """Test Sentry webhook with invalid JSON"""
        response = client.post(
            "/api/v1/webhooks/sentry",
            data="invalid json data",
            headers={"Content-Type": "application/json"},
        )

        assert response.status_code == 400
        data = response.json()
        assert "Invalid JSON" in data["detail"]

    def test_sentry_webhook_missing_content_type(self, client: TestClient):
        """Test Sentry webhook without content type header"""
        response = client.post("/api/v1/webhooks/sentry", json={"test": "data"})

        # Should still work as FastAPI handles JSON automatically
        assert response.status_code == 200

    def test_sentry_webhook_empty_body(self, client: TestClient):
        """Test Sentry webhook with empty body"""
        response = client.post("/api/v1/webhooks/sentry", json={})

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

    def test_sentry_webhook_with_error_event(self, client: TestClient):
        """Test Sentry webhook with error event data"""
        error_data = {
            "event": {
                "id": "error_event_456",
                "message": "Database connection failed",
                "level": "error",
                "timestamp": datetime.now().isoformat(),
                "project": "buzz2remote-backend",
                "exception": {
                    "values": [
                        {
                            "type": "ConnectionError",
                            "value": "Failed to connect to database",
                        }
                    ]
                },
            },
            "project": {"name": "buzz2remote-backend", "slug": "buzz2remote-backend"},
        }

        response = client.post("/api/v1/webhooks/sentry", json=error_data)

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

    def test_sentry_webhook_with_warning_event(self, client: TestClient):
        """Test Sentry webhook with warning event data"""
        warning_data = {
            "event": {
                "id": "warning_event_789",
                "message": "High memory usage detected",
                "level": "warning",
                "timestamp": datetime.now().isoformat(),
                "project": "buzz2remote-backend",
            },
            "project": {"name": "buzz2remote-backend", "slug": "buzz2remote-backend"},
        }

        response = client.post("/api/v1/webhooks/sentry", json=warning_data)

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

    @patch("routes.sentry_webhook.process_sentry_webhook")
    def test_sentry_webhook_background_processing(
        self, mock_process, client: TestClient
    ):
        """Test that Sentry webhook processes data in background"""
        webhook_data = {
            "event": {
                "id": "bg_event_123",
                "message": "Background processing test",
                "level": "info",
                "timestamp": datetime.now().isoformat(),
            }
        }

        mock_process.return_value = None

        response = client.post("/api/v1/webhooks/sentry", json=webhook_data)

        assert response.status_code == 200
        # Background task should be added
        mock_process.assert_called_once()

    def test_sentry_webhook_large_payload(self, client: TestClient):
        """Test Sentry webhook with large payload"""
        # Create a large payload
        large_data = {
            "event": {
                "id": "large_event_123",
                "message": "Large payload test",
                "level": "info",
                "timestamp": datetime.now().isoformat(),
                "data": "x" * 10000,  # 10KB of data
            }
        }

        response = client.post("/api/v1/webhooks/sentry", json=large_data)

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

    def test_sentry_webhook_malformed_data(self, client: TestClient):
        """Test Sentry webhook with malformed data structure"""
        malformed_data = {"invalid_field": "invalid_value", "missing_event": True}

        response = client.post("/api/v1/webhooks/sentry", json=malformed_data)

        # Should still process as webhook might be from different Sentry version
        assert response.status_code == 200

    def test_sentry_webhook_method_not_allowed(self, client: TestClient):
        """Test that other HTTP methods are not allowed"""
        methods = ["GET", "PUT", "DELETE", "PATCH"]

        for method in methods:
            if method == "GET":
                response = client.get("/api/v1/webhooks/sentry")
            elif method == "PUT":
                response = client.put("/api/v1/webhooks/sentry", json={})
            elif method == "DELETE":
                response = client.delete("/api/v1/webhooks/sentry")
            elif method == "PATCH":
                response = client.patch("/api/v1/webhooks/sentry", json={})

            assert response.status_code == 405  # Method Not Allowed

    def test_sentry_webhook_rate_limiting(self, client: TestClient):
        """Test Sentry webhook rate limiting (if implemented)"""
        webhook_data = {
            "event": {
                "id": "rate_limit_test",
                "message": "Rate limit test",
                "level": "info",
                "timestamp": datetime.now().isoformat(),
            }
        }

        # Send multiple requests quickly
        responses = []
        for i in range(10):
            response = client.post("/api/v1/webhooks/sentry", json=webhook_data)
            responses.append(response.status_code)

        # All should succeed (no rate limiting implemented)
        assert all(status == 200 for status in responses)
