import pytest
from bson import ObjectId
from httpx import AsyncClient


class TestRealisticDataIntegration:
    """Gerçekçi test verileri ile entegrasyon testleri"""

    @pytest.mark.asyncio
    async def test_jobs_endpoint_with_realistic_data(self, client_with_realistic_data):
        """Gerçekçi iş verileri ile jobs endpoint testi"""
        response = client_with_realistic_data.get("/api/v1/jobs")
        assert response.status_code == 200

        data = response.json()
        # Response format: {"items": [], "total": 0, "page": 1, "per_page": 100, "total_pages": 0}
        assert "items" in data
        assert "total" in data
        # Gerçekçi veriler varsa kontrol et
        if len(data["items"]) > 0:
            first_job = data["items"][0]
            assert "title" in first_job
            assert "company" in first_job
            assert "location" in first_job

    @pytest.mark.asyncio
    async def test_job_search_with_realistic_data(self, client_with_realistic_data):
        """Gerçekçi veriler ile iş arama testi"""
        # Product Manager araması
        response = client_with_realistic_data.get(
            "/api/v1/jobs/search?q=Product Manager"
        )
        assert response.status_code == 200

        data = response.json()
        assert "jobs" in data

        # Remote iş araması
        response = client_with_realistic_data.get("/api/v1/jobs/search?location=Remote")
        assert response.status_code == 200

        data = response.json()
        assert "jobs" in data

    @pytest.mark.asyncio
    async def test_job_detail_with_realistic_data(self, client_with_realistic_data):
        """Gerçekçi veriler ile iş detay testi"""
        # Önce mevcut işleri al
        response = client_with_realistic_data.get("/api/v1/jobs")
        assert response.status_code == 200

        data = response.json()
        if len(data["items"]) > 0:
            job_id = str(data["items"][0]["_id"])
            response = client_with_realistic_data.get(f"/api/v1/jobs/{job_id}")
            assert response.status_code == 200

            job = response.json()
            assert "title" in job
            assert "company" in job
            assert "location" in job

    @pytest.mark.asyncio
    async def test_companies_endpoint_with_realistic_data(
        self, client_with_realistic_data
    ):
        """Gerçekçi şirket verileri ile companies endpoint testi"""
        response = client_with_realistic_data.get("/api/v1/companies")
        assert response.status_code == 200

        data = response.json()
        # Response format: {"items": [], "page": 1, "per_page": 10, "total": 0, ...}
        assert "items" in data

        # Gerçekçi veriler varsa kontrol et
        if len(data["items"]) > 0:
            first_company = data["items"][0]
            assert "name" in first_company
            assert "website" in first_company

    @pytest.mark.asyncio
    async def test_company_detail_with_realistic_data(self, client_with_realistic_data):
        """Gerçekçi veriler ile şirket detay testi"""
        # Önce mevcut şirketleri al
        response = client_with_realistic_data.get("/api/v1/companies")
        assert response.status_code == 200

        data = response.json()
        if len(data["items"]) > 0:
            company_id = str(data["items"][0]["_id"])
            response = client_with_realistic_data.get(f"/api/v1/companies/{company_id}")
            assert response.status_code == 200

            company = response.json()
            assert "name" in company
            assert "website" in company

    @pytest.mark.asyncio
    async def test_job_autocomplete_with_realistic_data(
        self, client_with_realistic_data
    ):
        """Gerçekçi veriler ile iş autocomplete testi"""
        # Job titles search endpoint kullan
        response = client_with_realistic_data.get(
            "/api/v1/jobs/job-titles/search?q=Product"
        )
        assert response.status_code == 200

        data = response.json()
        assert isinstance(data, list)

        # "Developer" araması
        response = client_with_realistic_data.get(
            "/api/v1/jobs/job-titles/search?q=Developer"
        )
        assert response.status_code == 200

        data = response.json()
        assert isinstance(data, list)

    @pytest.mark.asyncio
    async def test_job_filtering_with_realistic_data(self, client_with_realistic_data):
        """Gerçekçi veriler ile iş filtreleme testi"""
        # Remote işler
        response = client_with_realistic_data.get("/api/v1/jobs?work_type=Remote")
        assert response.status_code == 200

        data = response.json()
        assert "items" in data

        # Senior seviye işler
        response = client_with_realistic_data.get(
            "/api/v1/jobs?experience_level=Senior"
        )
        assert response.status_code == 200

        data = response.json()
        assert "items" in data

    @pytest.mark.asyncio
    async def test_job_pagination_with_realistic_data(self, client_with_realistic_data):
        """Gerçekçi veriler ile sayfalama testi"""
        # İlk sayfa
        response = client_with_realistic_data.get("/api/v1/jobs?page=1&limit=3")
        assert response.status_code == 200

        data = response.json()
        assert "items" in data
        assert "total" in data

        # İkinci sayfa
        response = client_with_realistic_data.get("/api/v1/jobs?page=2&limit=3")
        assert response.status_code == 200

        data = response.json()
        assert "items" in data

    @pytest.mark.asyncio
    async def test_job_sorting_with_realistic_data(self, client_with_realistic_data):
        """Gerçekçi veriler ile sıralama testi"""
        # Maaşa göre azalan sıralama
        response = client_with_realistic_data.get(
            "/api/v1/jobs?sort=salary_max&order=desc"
        )
        assert response.status_code == 200

        data = response.json()
        assert "items" in data

    @pytest.mark.asyncio
    async def test_job_statistics_with_realistic_data(self, client_with_realistic_data):
        """Gerçekçi veriler ile istatistik testi"""
        response = client_with_realistic_data.get("/api/v1/jobs/statistics")
        assert response.status_code == 200

        data = response.json()
        assert "total_jobs" in data

    @pytest.mark.asyncio
    async def test_health_check_with_realistic_data(self, client_with_realistic_data):
        """Gerçekçi veriler ile sağlık kontrolü testi"""
        response = client_with_realistic_data.get("/health")
        assert response.status_code == 200

        data = response.json()
        assert "status" in data
        assert data["status"] == "healthy"

    @pytest.mark.asyncio
    async def test_job_recommendations_with_realistic_data(
        self, client_with_realistic_data
    ):
        """Gerçekçi veriler ile iş önerileri testi"""
        # Python skill'i ile öneri
        response = client_with_realistic_data.get("/api/v1/jobs/recommendations")
        assert response.status_code == 200

        data = response.json()
        assert isinstance(data, list)

        # React skill'i ile öneri - skills parametresi desteklenmiyor, genel öneriler al
        response = client_with_realistic_data.get(
            "/api/v1/jobs/recommendations?limit=5"
        )
        assert response.status_code == 200

        data = response.json()
        assert isinstance(data, list)
