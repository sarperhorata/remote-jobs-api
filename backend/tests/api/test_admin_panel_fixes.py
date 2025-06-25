import pytest
from fastapi.testclient import TestClient
from backend.main import app

class TestAdminPanelFixes:
    """Test admin panel fixes and improvements"""
    
    def setup_method(self):
        """Setup test client"""
        self.client = TestClient(app)
    
    def test_admin_companies_statistics_endpoint(self):
        """Test companies statistics endpoint for admin dashboard"""
        response = self.client.get("/admin/api/companies/statistics")
        assert response.status_code in [200, 401]  # 401 if not authenticated
        
        if response.status_code == 200:
            data = response.json()
            assert "total_companies" in data
            assert "active_companies" in data
            assert "companies_with_jobs" in data
            assert isinstance(data["total_companies"], int)
    
    def test_unknown_company_analysis_endpoint(self):
        """Test unknown company analysis endpoint"""
        response = self.client.get("/admin/api/unknown-company-analysis")
        assert response.status_code in [200, 401]  # 401 if not authenticated
        
        if response.status_code == 200:
            data = response.json()
            assert "total_unknown_jobs" in data or "error" in data
    
    def test_fix_unknown_companies_endpoint(self):
        """Test fix unknown companies endpoint"""
        response = self.client.post("/admin/api/fix-unknown-companies")
        assert response.status_code in [200, 401]  # 401 if not authenticated
        
        if response.status_code == 200:
            data = response.json()
            assert "status" in data or "error" in data
    
    def test_admin_jobs_with_page_size(self):
        """Test admin jobs page with different page sizes"""
        # Test different page sizes
        for page_size in [10, 20, 50, 100]:
            response = self.client.get(f"/admin/jobs?page_size={page_size}")
            assert response.status_code in [200, 302]  # 302 for redirect to login
    
    def test_admin_jobs_pagination(self):
        """Test admin jobs pagination functionality"""
        response = self.client.get("/admin/jobs?page=1&page_size=20")
        assert response.status_code in [200, 302]  # 302 for redirect to login
        
        # Test with filters
        response = self.client.get("/admin/jobs?page=1&page_size=50&company_filter=test")
        assert response.status_code in [200, 302]
    
    def test_admin_companies_page_accessible(self):
        """Test admin companies page is accessible"""
        response = self.client.get("/admin/companies")
        assert response.status_code in [200, 302]  # 302 for redirect to login
    
    def test_admin_apis_page_accessible(self):
        """Test admin APIs page is accessible"""
        response = self.client.get("/admin/apis")
        assert response.status_code in [200, 302]  # 302 for redirect to login
    
    def test_admin_status_page_accessible(self):
        """Test admin status page is accessible"""
        response = self.client.get("/admin/status")
        assert response.status_code in [200, 302]  # 302 for redirect to login
    
    def test_admin_dashboard_accessible(self):
        """Test admin dashboard is accessible"""
        response = self.client.get("/admin/")
        assert response.status_code in [200, 302]  # 302 for redirect to login
        
        response = self.client.get("/admin/dashboard")
        assert response.status_code in [200, 302]  # 302 for redirect to login
    
    def test_admin_login_page(self):
        """Test admin login page"""
        response = self.client.get("/admin/login")
        assert response.status_code == 200
        assert "Admin Panel" in response.text
        assert "Username" in response.text
        assert "Password" in response.text
    
    def test_admin_test_page(self):
        """Test admin test page"""
        response = self.client.get("/admin/test")
        assert response.status_code == 200
        assert "Admin Panel Test Success" in response.text 