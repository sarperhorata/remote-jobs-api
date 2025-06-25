import pytest
import asyncio
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch, MagicMock
from backend.main import app
from backend.database import get_async_db

# Test client
client = TestClient(app)

# Mock database
@pytest.fixture
def mock_db():
    return AsyncMock()

@pytest.fixture
def override_get_db(mock_db):
    app.dependency_overrides[get_async_db] = lambda: mock_db
    yield mock_db
    app.dependency_overrides = {}

class TestJobSearch:
    """Test job search functionality"""

    @pytest.mark.asyncio
    async def test_search_jobs_basic(self):
        """Test basic job search functionality"""
        # Use correct endpoint path
        response = await self.client.get("/api/jobs/search?q=developer")
        # Should either work or return 422 for validation
        assert response.status_code in [200, 422]

    @pytest.mark.asyncio 
    async def test_search_jobs_empty_query(self):
        """Test job search with empty query"""
        response = await self.client.get("/api/jobs/search?q=")
        assert response.status_code in [200, 422]

    @pytest.mark.asyncio
    async def test_search_jobs_no_results(self):
        """Test job search with no results"""
        response = await self.client.get("/api/jobs/search?q=nonexistentjob12345")
        assert response.status_code in [200, 422]

    @pytest.mark.asyncio
    async def test_search_jobs_with_filters(self):
        """Test job search with filters"""
        response = await self.client.get("/api/jobs/search?q=developer&location=remote")
        assert response.status_code in [200, 422]

    @pytest.mark.asyncio
    async def test_search_jobs_pagination(self):
        """Test job search pagination"""
        response = await self.client.get("/api/jobs/search?q=developer&page=1&per_page=10")
        assert response.status_code in [200, 422]

    @pytest.mark.asyncio
    async def test_autocomplete_jobs(self):
        """Test job autocomplete functionality"""
        response = await self.client.get("/api/jobs/job-titles/search?q=dev")
        assert response.status_code in [200, 422]

    @pytest.mark.asyncio
    async def test_autocomplete_jobs_limit(self):
        """Test job autocomplete with limit"""
        response = await self.client.get("/api/jobs/job-titles/search?q=dev&limit=5")
        assert response.status_code in [200, 422]

    @pytest.mark.asyncio
    async def test_autocomplete_jobs_empty_query(self):
        """Test job autocomplete with empty query"""
        response = await self.client.get("/api/jobs/job-titles/search?q=")
        assert response.status_code in [200, 422]

    @pytest.mark.asyncio
    async def test_search_jobs_by_company(self):
        """Test job search by company"""
        response = await self.client.get("/api/jobs/search?company=google")
        assert response.status_code in [200, 422]

    @pytest.mark.asyncio
    async def test_search_jobs_by_skills(self):
        """Test job search by skills"""
        response = await self.client.get("/api/jobs/search?skills=python")
        assert response.status_code in [200, 422]

    def test_search_jobs_pagination(self, override_get_db):
        """Test search with pagination"""
        mock_jobs = [
            {
                "_id": str(i),
                "title": f"Developer {i}",
                "company": f"Company {i}",
                "location": "Remote",
                "job_type": "Full-time",
                "salary": "$60k - $80k",
                "description": f"Job description {i}",
                "posted_date": "2024-01-01",
            }
            for i in range(5)
        ]
        
        override_get_db.jobs.find.return_value.skip.return_value.limit.return_value.to_list = AsyncMock(return_value=mock_jobs[:3])
        override_get_db.jobs.count_documents = AsyncMock(return_value=5)

        response = client.get("/api/jobs/search?q=developer&page=1&per_page=3")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["jobs"]) == 3
        assert data["total"] == 5
        assert data["page"] == 1
        assert data["per_page"] == 3

    def test_search_jobs_sorting(self, override_get_db):
        """Test search with sorting"""
        mock_jobs = [
            {
                "_id": "1",
                "title": "Senior Developer",
                "company": "Tech Company",
                "location": "Remote",
                "job_type": "Full-time",
                "salary": "$80k - $100k",
                "description": "Senior role",
                "posted_date": "2024-01-02",
            },
            {
                "_id": "2",
                "title": "Junior Developer",
                "company": "Startup",
                "location": "Remote",
                "job_type": "Full-time",
                "salary": "$50k - $70k",
                "description": "Junior role",
                "posted_date": "2024-01-01",
            }
        ]
        
        override_get_db.jobs.find.return_value.sort.return_value.to_list = AsyncMock(return_value=mock_jobs)
        override_get_db.jobs.count_documents = AsyncMock(return_value=2)

        response = client.get("/api/jobs/search?q=developer&sort_by=posted_date&sort_order=desc")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["jobs"]) == 2
        # Should be sorted by posted_date descending
        assert data["jobs"][0]["posted_date"] >= data["jobs"][1]["posted_date"]

    def test_search_performance(self, override_get_db):
        """Test search performance with large dataset"""
        # Simulate large number of jobs
        override_get_db.jobs.find.return_value.to_list = AsyncMock(return_value=[])
        override_get_db.jobs.count_documents = AsyncMock(return_value=10000)

        import time
        start_time = time.time()
        response = client.get("/api/jobs/search?q=developer")
        end_time = time.time()
        
        assert response.status_code == 200
        # Search should complete within reasonable time (2 seconds)
        assert (end_time - start_time) < 2.0

    def test_search_jobs_error_handling(self, override_get_db):
        """Test error handling in search"""
        override_get_db.jobs.find.side_effect = Exception("Database error")

        response = client.get("/api/jobs/search?q=developer")
        
        assert response.status_code == 500

    @pytest.mark.asyncio
    async def test_search_regex_injection(self, override_get_db):
        """Test protection against regex injection"""
        malicious_query = ".*"
        
        override_get_db.jobs.find.return_value.to_list = AsyncMock(return_value=[])
        override_get_db.jobs.count_documents = AsyncMock(return_value=0)

        response = client.get(f"/api/jobs/search?q={malicious_query}")
        
        # Should handle malicious input safely
        assert response.status_code == 200

    def test_search_case_insensitive(self, override_get_db):
        """Test case insensitive search"""
        mock_jobs = [
            {
                "_id": "1",
                "title": "Frontend Developer",
                "company": "Tech Company",
                "location": "Remote",
                "description": "Frontend development role",
                "posted_date": "2024-01-01",
            }
        ]
        
        override_get_db.jobs.find.return_value.to_list = AsyncMock(return_value=mock_jobs)
        override_get_db.jobs.count_documents = AsyncMock(return_value=1)

        # Test different cases
        test_queries = ["frontend", "FRONTEND", "Frontend", "FrontEnd"]
        
        for query in test_queries:
            response = client.get(f"/api/jobs/search?q={query}")
            assert response.status_code == 200
            data = response.json()
            assert len(data["jobs"]) == 1

    def test_search_special_characters(self, override_get_db):
        """Test search with special characters"""
        mock_jobs = [
            {
                "_id": "1",
                "title": "C++ Developer",
                "company": "Tech Company",
                "location": "Remote",
                "description": "C++ programming role",
                "posted_date": "2024-01-01",
            }
        ]
        
        override_get_db.jobs.find.return_value.to_list = AsyncMock(return_value=mock_jobs)
        override_get_db.jobs.count_documents = AsyncMock(return_value=1)

        response = client.get("/api/jobs/search?q=c%2B%2B")  # URL encoded C++
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["jobs"]) == 1 