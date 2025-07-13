import pytest
from fastapi import status
from fastapi.testclient import TestClient
from main import app

@pytest.fixture
def client():
    """Create a test client for the FastAPI app."""
    return TestClient(app)

@pytest.mark.api
class TestHealthAPI:
    """Test health check endpoints."""

    def test_root_endpoint(self, client):
        """Test root endpoint returns 200."""
        response = client.get("/")
        assert response.status_code == status.HTTP_200_OK

    def test_health_endpoint(self, client):
        """Test health endpoint if it exists."""
        response = client.get("/health")
        # Should either return 200 or 404 if endpoint doesn't exist
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]

    def test_docs_endpoint(self, client):
        """Test docs endpoint is accessible."""
        response = client.get("/docs")
        assert response.status_code == status.HTTP_200_OK 