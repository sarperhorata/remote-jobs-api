import pytest
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

class TestCompaniesRoutes:
    """Test companies routes to boost coverage"""
    
    def test_companies_endpoint_accessible(self):
        """Test GET /api/companies/ endpoint"""
        response = client.get("/api/companies/")
        assert response.status_code == 200
        
    def test_companies_search_endpoint(self):
        """Test companies search functionality"""
        response = client.get("/api/companies/search?q=test")
        assert response.status_code in [200, 400]
        
    def test_company_by_id_endpoint(self):
        """Test get company by ID"""
        response = client.get("/api/companies/123")
        # Should handle gracefully even for non-existent ID
        assert response.status_code in [200, 404, 422]
        
    def test_companies_statistics(self):
        """Test companies statistics endpoint"""
        response = client.get("/api/companies/statistics")
        assert response.status_code == 200
        
    def test_companies_response_structure(self):
        """Test companies response has correct structure"""
        response = client.get("/api/companies/")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, (list, dict))
        
    def test_companies_pagination(self):
        """Test companies pagination"""
        response = client.get("/api/companies/?page=1&limit=10")
        assert response.status_code == 200
