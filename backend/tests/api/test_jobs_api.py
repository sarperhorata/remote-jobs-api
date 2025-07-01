"""
Clean Jobs API Tests
Gerçek test data ile kaliteli, odaklanmış testler.
"""

import pytest
from fastapi import status
from httpx import AsyncClient


@pytest.mark.asyncio
class TestJobsAPICore:
    """Core Job API functionality tests"""

    async def test_get_jobs_endpoint_works(self, async_client: AsyncClient):
        """Test that jobs endpoint returns correct structure"""
        response = await async_client.get("/api/v1/jobs/search")
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify response structure
        assert "jobs" in data
        assert "total" in data
        assert "page" in data
        assert "limit" in data
        assert isinstance(data["jobs"], list)

    async def test_get_jobs_pagination(self, async_client: AsyncClient):
        """Test jobs pagination parameters"""
        response = await async_client.get("/api/v1/jobs/search?page=1&limit=5")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["page"] == 1
        assert data["limit"] == 5
        assert len(data["jobs"]) <= 5

    async def test_job_search_with_query(self, async_client: AsyncClient):
        """Test job search with query parameter"""
        response = await async_client.get("/api/v1/jobs/search?q=python")
        
        assert response.status_code == 200
        data = response.json()
        
        # Should return valid structure even if no results
        assert "jobs" in data
        assert isinstance(data["jobs"], list)

    async def test_job_titles_autocomplete(self, async_client: AsyncClient):
        """Test job titles autocomplete endpoint"""
        response = await async_client.get("/api/v1/jobs/job-titles/search?q=dev&limit=5")
        
        assert response.status_code == 200
        data = response.json()
        
        assert isinstance(data, list)
        assert len(data) <= 5

    async def test_pagination_validation(self, async_client: AsyncClient):
        """Test pagination parameter validation"""
        # Test excessive limit (>100 should be invalid)
        response = await async_client.get("/api/v1/jobs/search?limit=150")
        assert response.status_code == 422  # Validation error expected
        
        # Test valid large limit
        response = await async_client.get("/api/v1/jobs/search?limit=100") 
        assert response.status_code == 200
        data = response.json()
        assert data["limit"] == 100

    async def test_search_response_time(self, async_client: AsyncClient):
        """Test that search responses are reasonably fast"""
        import time
        
        start_time = time.time()
        response = await async_client.get("/api/v1/jobs/search?limit=20")
        end_time = time.time()
        
        response_time = end_time - start_time
        
        assert response.status_code == 200
        assert response_time < 5.0  # Should respond within 5 seconds
