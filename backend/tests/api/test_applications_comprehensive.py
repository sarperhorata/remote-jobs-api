import pytest
from fastapi.testclient import TestClient

from main import app


class TestApplicationsRoutesComprehensive:
    @pytest.fixture
    def client(self):
        return TestClient(app)

    def test_applications_endpoints_exist(self, client):
        """Test applications endpoints exist and return auth errors (not 404)"""
        endpoints = [
            "/api/v1/applications/apply",
            "/api/v1/applications/my-applications",
            "/api/v1/applications/applied-jobs",
            "/api/v1/applications/stats",
        ]

        for endpoint in endpoints:
            if "apply" in endpoint:
                response = client.post(endpoint, json={})
            else:
                response = client.get(endpoint)
            # Should require auth (401) not missing endpoint (404)
            assert response.status_code in [401, 422]
