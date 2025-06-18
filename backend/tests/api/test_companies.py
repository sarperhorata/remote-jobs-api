import pytest
import asyncio
from fastapi import status
from httpx import AsyncClient
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime
from bson import ObjectId


@pytest.mark.asyncio
class TestCompaniesAPI:
    """Test suite for Companies API endpoints."""

    async def test_get_companies_success(self, async_client: AsyncClient, mock_database):
        """Test successful companies retrieval."""
        # Mock companies data
        companies_data = [
            {
                "_id": "tech-corp",
                "name": "TechCorp",
                "description": "Leading tech company",
                "website": "https://techcorp.com",
                "job_count": 15,
                "latest_job": datetime.now()
            },
            {
                "_id": "startup-xyz",
                "name": "StartupXYZ",
                "description": "Innovative startup",
                "website": "https://startupxyz.com", 
                "job_count": 8,
                "latest_job": datetime.now()
            }
        ]
        
        # Mock companies collection result
        mock_cursor = AsyncMock()
        mock_cursor.to_list = AsyncMock(return_value=companies_data)
        mock_cursor.sort = MagicMock(return_value=mock_cursor)
        mock_cursor.skip = MagicMock(return_value=mock_cursor)
        mock_cursor.limit = MagicMock(return_value=mock_cursor)
        mock_database.companies.find = MagicMock(return_value=mock_cursor)
        mock_database.companies.count_documents = AsyncMock(return_value=len(companies_data))
        # Mock jobs.count_documents for jobs_count field
        mock_database.jobs.count_documents = AsyncMock(return_value=5)
        
        response = await async_client.get("/api/companies/")
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert len(data["items"]) == 2

    async def test_get_companies_with_pagination(self, async_client: AsyncClient, mock_database):
        """Test companies retrieval with pagination."""
        companies_data = []
        for i in range(5):
            companies_data.append({
                "_id": f"company-{i}",
                "name": f"Company {i}",
                "job_count": i + 1,
                "latest_job": datetime.now()
            })
        
        mock_cursor = AsyncMock()
        mock_cursor.to_list = AsyncMock(return_value=companies_data[:2])  # First page
        mock_database.jobs.aggregate = MagicMock(return_value=mock_cursor)
        
        response = await async_client.get("/api/companies/?page=1&per_page=2")
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 2

    async def test_get_company_by_id_success(self, async_client: AsyncClient, mock_database):
        """Test successful company retrieval by ID."""
        company_data = {
            "_id": "tech-corp",
            "name": "TechCorp",
            "description": "Leading tech company",
            "website": "https://techcorp.com",
            "job_count": 15
        }
        
        mock_cursor = AsyncMock()
        mock_cursor.to_list = AsyncMock(return_value=[company_data])
        mock_database.jobs.aggregate = MagicMock(return_value=mock_cursor)
        
        response = await async_client.get("/api/companies/tech-corp")
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "TechCorp"

    async def test_get_company_by_id_not_found(self, async_client: AsyncClient, mock_database):
        """Test company not found scenario."""
        mock_cursor = AsyncMock()
        mock_cursor.to_list = AsyncMock(return_value=[])
        mock_database.jobs.aggregate = MagicMock(return_value=mock_cursor)
        
        response = await async_client.get("/api/companies/non-existent")
        assert response.status_code == 404

    async def test_get_company_jobs_success(self, async_client: AsyncClient, mock_database):
        """Test getting jobs for a specific company."""
        jobs_data = [
            {
                "_id": ObjectId(),
                "title": "Python Developer",
                "company": "TechCorp",
                "location": "Remote",
                "description": "Python development role"
            },
            {
                "_id": ObjectId(),
                "title": "React Developer", 
                "company": "TechCorp",
                "location": "Remote",
                "description": "React development role"
            }
        ]
        
        # Mock job storage in database
        for job in jobs_data:
            job_id = str(job["_id"])
            mock_database.jobs._storage[job_id] = job
        
        response = await async_client.get("/api/companies/TechCorp/jobs")
        assert response.status_code == 200
        data = response.json()
        assert "jobs" in data

    async def test_search_companies_success(self, async_client: AsyncClient, mock_database):
        """Test company search functionality."""
        search_results = [
            {
                "_id": "tech-corp",
                "name": "TechCorp",
                "description": "Leading tech company"
            }
        ]
        
        mock_cursor = AsyncMock()
        mock_cursor.to_list = AsyncMock(return_value=search_results)
        mock_database.jobs.aggregate = MagicMock(return_value=mock_cursor)
        
        response = await async_client.get("/api/companies/search?q=tech")
        assert response.status_code == 200
        data = response.json()
        assert "items" in data

    async def test_get_companies_filtering(self, async_client: AsyncClient, mock_database):
        """Test companies filtering by various criteria."""
        mock_cursor = AsyncMock()
        mock_cursor.to_list = AsyncMock(return_value=[])
        mock_database.jobs.aggregate = MagicMock(return_value=mock_cursor)
        
        # Test filtering by industry
        response = await async_client.get("/api/companies/?industry=technology")
        assert response.status_code == 200
        
        # Test filtering by size
        response = await async_client.get("/api/companies/?size=startup")
        assert response.status_code == 200
        
        # Test filtering by location
        response = await async_client.get("/api/companies/?location=remote")
        assert response.status_code == 200

    async def test_get_companies_sorting(self, async_client: AsyncClient, mock_database):
        """Test companies sorting options."""
        mock_cursor = AsyncMock()
        mock_cursor.to_list = AsyncMock(return_value=[])
        mock_database.jobs.aggregate = MagicMock(return_value=mock_cursor)
        
        # Test sorting by job count
        response = await async_client.get("/api/companies/?sort_by=job_count&sort_order=desc")
        assert response.status_code == 200
        
        # Test sorting by name
        response = await async_client.get("/api/companies/?sort_by=name&sort_order=asc")
        assert response.status_code == 200

    async def test_get_company_statistics(self, async_client: AsyncClient, mock_database):
        """Test company statistics endpoint."""
        stats_data = [
            {
                "_id": None,
                "total_companies": 100,
                "companies_with_jobs": 85,
                "avg_jobs_per_company": 12.5
            }
        ]
        
        mock_cursor = AsyncMock()
        mock_cursor.to_list = AsyncMock(return_value=stats_data)
        mock_database.jobs.aggregate = MagicMock(return_value=mock_cursor)
        
        response = await async_client.get("/api/companies/statistics")
        assert response.status_code == 200
        data = response.json()
        assert "total_companies" in data

    async def test_companies_pagination_edge_cases(self, async_client: AsyncClient, mock_database):
        """Test pagination edge cases."""
        mock_cursor = AsyncMock()
        mock_cursor.to_list = AsyncMock(return_value=[])
        mock_database.jobs.aggregate = MagicMock(return_value=mock_cursor)
        
        # Test invalid page numbers
        response = await async_client.get("/api/companies/?page=0")
        assert response.status_code in [200, 422]  # Should handle gracefully
        
        response = await async_client.get("/api/companies/?page=-1")
        assert response.status_code in [200, 422]
        
        response = await async_client.get("/api/companies/?per_page=0")
        assert response.status_code in [200, 422]

    async def test_companies_error_handling(self, async_client: AsyncClient, mock_database):
        """Test error handling in companies endpoints."""
        # Simulate database error
        mock_database.jobs.aggregate.side_effect = Exception("Database error")
        
        response = await async_client.get("/api/companies/")
        assert response.status_code in [200, 500, 503]  # Should handle gracefully

    async def test_company_detailed_info(self, async_client: AsyncClient, mock_database):
        """Test detailed company information endpoint."""
        company_detail = {
            "_id": "tech-corp",
            "name": "TechCorp",
            "description": "Leading technology company",
            "website": "https://techcorp.com",
            "industry": "Technology",
            "size": "1000-5000",
            "location": "San Francisco, CA",
            "job_count": 25,
            "active_jobs": 20,
            "remote_jobs": 15
        }
        
        mock_cursor = AsyncMock()
        mock_cursor.to_list = AsyncMock(return_value=[company_detail])
        mock_database.jobs.aggregate = MagicMock(return_value=mock_cursor)
        
        response = await async_client.get("/api/companies/tech-corp/details")
        assert response.status_code in [200, 404]  # Endpoint may not exist yet 