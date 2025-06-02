#!/usr/bin/env python3

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime
from fastapi.testclient import TestClient
from fastapi import HTTPException
import sys
import os
from bson import ObjectId

# Add proper paths for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from backend.main import app
from backend.admin_panel.routes import build_safe_filter, get_sort_indicator

class TestAdminRoutes:
    """Comprehensive admin routes tests for maximum coverage"""
    
    @pytest.fixture
    def client(self):
        """Create test client."""
        return TestClient(app)
    
    @pytest.fixture
    def authenticated_client(self, client):
        """Create authenticated client session."""
        # Login first
        response = client.post("/admin/login", data={
            "username": "admin",
            "password": "buzz2remote2024"
        })
        return client
    
    def test_admin_dashboard_with_database_available(self, authenticated_client):
        """Test admin dashboard with database available"""
        with patch('backend.admin_panel.routes.DATABASE_AVAILABLE', True):
            with patch('backend.admin_panel.routes.db') as mock_db:
                mock_db.jobs.count_documents = AsyncMock(return_value=1500)
                
                response = authenticated_client.get("/admin/")
                assert response.status_code == 200
                assert "1,500" in response.text
                assert "Admin Dashboard" in response.text
    
    def test_admin_dashboard_without_database(self, authenticated_client):
        """Test admin dashboard without database"""
        with patch('backend.admin_panel.routes.DATABASE_AVAILABLE', False):
            response = authenticated_client.get("/admin/")
            assert response.status_code == 200
            assert "36,531" in response.text
            assert "Admin Dashboard" in response.text
    
    def test_admin_jobs_with_database_available(self, authenticated_client):
        """Test admin jobs page with database"""
        with patch('backend.admin_panel.routes.DATABASE_AVAILABLE', True):
            with patch('backend.admin_panel.routes.db') as mock_db:
                mock_db.jobs.count_documents = AsyncMock(return_value=10)
                mock_jobs = [
                    {
                        "_id": ObjectId(),
                        "title": "Test Job",
                        "company": "Test Company",
                        "location": "Remote",
                        "type": "Full-time",
                        "created_at": datetime.now(),
                        "url": "https://test.com",
                        "description": "Test description"
                    }
                ]
                mock_cursor = AsyncMock()
                mock_cursor.to_list = AsyncMock(return_value=mock_jobs)
                mock_db.jobs.find.return_value.sort.return_value.skip.return_value.limit.return_value = mock_cursor
                
                response = authenticated_client.get("/admin/jobs")
                assert response.status_code == 200
                assert "Test Job" in response.text
                assert "Test Company" in response.text
    
    def test_admin_jobs_with_pagination(self, authenticated_client):
        """Test admin jobs pagination"""
        with patch('backend.admin_panel.routes.DATABASE_AVAILABLE', True):
            with patch('backend.admin_panel.routes.db') as mock_db:
                mock_db.jobs.count_documents = AsyncMock(return_value=100)
                mock_cursor = AsyncMock()
                mock_cursor.to_list = AsyncMock(return_value=[])
                mock_db.jobs.find.return_value.sort.return_value.skip.return_value.limit.return_value = mock_cursor
                
                response = authenticated_client.get("/admin/jobs?page=2")
                assert response.status_code == 200
                assert "Page 2" in response.text
    
    def test_admin_jobs_with_company_filter(self, authenticated_client):
        """Test admin jobs with company filter"""
        with patch('backend.admin_panel.routes.DATABASE_AVAILABLE', True):
            with patch('backend.admin_panel.routes.db') as mock_db:
                mock_db.jobs.count_documents = AsyncMock(return_value=5)
                mock_cursor = AsyncMock()
                mock_cursor.to_list = AsyncMock(return_value=[])
                mock_db.jobs.find.return_value.sort.return_value.skip.return_value.limit.return_value = mock_cursor
                
                response = authenticated_client.get("/admin/jobs?company_filter=TestCorp")
                assert response.status_code == 200
                assert "TestCorp" in response.text
    
    def test_admin_companies_with_database_available(self, authenticated_client):
        """Test admin companies page with database"""
        with patch('backend.admin_panel.routes.DATABASE_AVAILABLE', True):
            with patch('backend.admin_panel.routes.db') as mock_db:
                mock_companies = [
                    {
                        "_id": "Test Company",
                        "job_count": 15,
                        "latest_job": datetime.now(),
                        "website": "https://test.com",
                        "careers_url": "https://test.com/careers"
                    }
                ]
                
                # Mock aggregation pipeline
                mock_cursor = AsyncMock()
                mock_cursor.to_list = AsyncMock(side_effect=[mock_companies, [{"total": 1}]])
                mock_db.jobs.aggregate = AsyncMock(return_value=mock_cursor)
                
                response = authenticated_client.get("/admin/companies")
                assert response.status_code == 200
                assert "Test Company" in response.text
    
    def test_admin_companies_with_search(self, authenticated_client):
        """Test admin companies with search"""
        with patch('backend.admin_panel.routes.DATABASE_AVAILABLE', True):
            with patch('backend.admin_panel.routes.db') as mock_db:
                mock_cursor = AsyncMock()
                mock_cursor.to_list = AsyncMock(side_effect=[[], [{"total": 0}]])
                mock_db.jobs.aggregate = AsyncMock(return_value=mock_cursor)
                
                response = authenticated_client.get("/admin/companies?search=Tech")
                assert response.status_code == 200
                assert "Tech" in response.text
    
    def test_admin_status_page(self, authenticated_client):
        """Test admin status page"""
        with patch('backend.admin_panel.routes.DATABASE_AVAILABLE', True):
            with patch('backend.admin_panel.routes.db') as mock_db:
                mock_db.jobs.count_documents = AsyncMock(return_value=1000)
                
                response = authenticated_client.get("/admin/status")
                assert response.status_code == 200
                assert "System Status" in response.text
                assert "Operational" in response.text
    
    def test_admin_apis_page(self, authenticated_client):
        """Test admin APIs page"""
        response = authenticated_client.get("/admin/apis")
        assert response.status_code == 200
        assert "API Services" in response.text
        assert "remoteok" in response.text
        assert "weworkremotely" in response.text
    
    def test_get_job_details_success(self, authenticated_client):
        """Test job details endpoint success"""
        job_id = str(ObjectId())
        mock_job = {
            "_id": ObjectId(job_id),
            "title": "Test Job",
            "company": "Test Company",
            "description": "Test description"
        }
        
        with patch('backend.admin_panel.routes.DATABASE_AVAILABLE', True):
            with patch('backend.admin_panel.routes.db') as mock_db:
                mock_db.jobs.find_one = AsyncMock(return_value=mock_job)
                
                response = authenticated_client.get(f"/admin/job-details/{job_id}")
                assert response.status_code == 200
                assert "Test Job" in response.text
    
    def test_get_job_details_not_found(self, authenticated_client):
        """Test job details endpoint not found"""
        job_id = str(ObjectId())
        
        with patch('backend.admin_panel.routes.DATABASE_AVAILABLE', True):
            with patch('backend.admin_panel.routes.db') as mock_db:
                mock_db.jobs.find_one = AsyncMock(return_value=None)
                
                response = authenticated_client.get(f"/admin/job-details/{job_id}")
                assert response.status_code == 404
    
    def test_get_job_details_database_unavailable(self, authenticated_client):
        """Test job details with database unavailable"""
        job_id = str(ObjectId())
        
        with patch('backend.admin_panel.routes.DATABASE_AVAILABLE', False):
            response = authenticated_client.get(f"/admin/job-details/{job_id}")
            assert response.status_code == 503

class TestAdminActions:
    """Test admin action endpoints"""
    
    @pytest.fixture
    def client(self):
        """Create test client."""
        return TestClient(app)
    
    @pytest.fixture
    def authenticated_client(self, client):
        """Create authenticated client session."""
        response = client.post("/admin/login", data={
            "username": "admin",
            "password": "buzz2remote2024"
        })
        return client
    
    def test_run_crawler_action_success(self, authenticated_client):
        """Test run crawler action success"""
        with patch('backend.admin_panel.routes.DATABASE_AVAILABLE', True):
            with patch('backend.admin_panel.routes.db') as mock_db:
                mock_db.processes.insert_one = AsyncMock()
                
                response = authenticated_client.post("/admin/actions/run-crawler")
                assert response.status_code == 200
                data = response.json()
                assert data["status"] == "success"
                assert "process_id" in data
    
    def test_fetch_external_apis_action_success(self, authenticated_client):
        """Test fetch external APIs action success"""
        with patch('backend.admin_panel.routes.DATABASE_AVAILABLE', True):
            with patch('backend.admin_panel.routes.db') as mock_db:
                mock_db.processes.insert_one = AsyncMock()
                
                response = authenticated_client.post("/admin/actions/fetch-external-apis")
                assert response.status_code == 200
                data = response.json()
                assert data["status"] == "success"
    
    def test_analyze_positions_action_success(self, authenticated_client):
        """Test analyze positions action success"""
        with patch('backend.admin_panel.routes.DATABASE_AVAILABLE', True):
            with patch('backend.admin_panel.routes.db') as mock_db:
                mock_db.processes.insert_one = AsyncMock()
                
                response = authenticated_client.post("/admin/actions/analyze-positions")
                assert response.status_code == 200
                data = response.json()
                assert data["status"] == "success"
    
    def test_actions_database_unavailable(self, authenticated_client):
        """Test actions with database unavailable"""
        with patch('backend.admin_panel.routes.DATABASE_AVAILABLE', False):
            response = authenticated_client.post("/admin/actions/run-crawler")
            assert response.status_code == 500
    
    def test_run_api_service_success(self, authenticated_client):
        """Test run specific API service"""
        response = authenticated_client.post("/admin/api-services/remoteok")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "remoteok" in data["message"]

class TestAdminUtilities:
    """Test admin utility functions"""
    
    def test_build_safe_filter_with_search_term(self):
        """Test build_safe_filter function"""
        result = build_safe_filter("TestCompany", "company")
        assert "company" in result
        regex_field = result.get("company", {})
        assert "$regex" in regex_field
        assert "TestCompany" in regex_field.get("$regex", "")
        assert "$options" in regex_field
        assert regex_field.get("$options") == "i"
    
    def test_build_safe_filter_empty_search(self):
        """Test build_safe_filter with empty search"""
        result = build_safe_filter("", "company")
        assert result == {}
        
        result = build_safe_filter(None, "company")
        assert result == {}
    
    def test_build_safe_filter_sanitizes_input(self):
        """Test build_safe_filter sanitizes dangerous input"""
        result = build_safe_filter("test$company{}", "company")
        # Should remove dangerous characters
        regex_field = result.get("company", {})
        regex_value = regex_field.get("$regex", "")
        assert "$" not in regex_value
        assert "{" not in regex_value
        assert "}" not in regex_value
    
    def test_get_sort_indicator_current_desc(self):
        """Test get_sort_indicator with current column desc"""
        result = get_sort_indicator("name", "name", "desc")
        assert result == "▼"
    
    def test_get_sort_indicator_current_asc(self):
        """Test get_sort_indicator with current column asc"""
        result = get_sort_indicator("name", "name", "asc")
        assert result == "▲"
    
    def test_get_sort_indicator_other_column(self):
        """Test get_sort_indicator with other column"""
        result = get_sort_indicator("date", "name", "desc")
        assert result == "↕"

class TestAdminErrorHandling:
    """Test admin panel error handling"""
    
    @pytest.fixture
    def client(self):
        """Create test client."""
        return TestClient(app)
    
    @pytest.fixture
    def authenticated_client(self, client):
        """Create authenticated client session."""
        response = client.post("/admin/login", data={
            "username": "admin",
            "password": "buzz2remote2024"
        })
        return client
    
    def test_admin_dashboard_exception_handling(self, authenticated_client):
        """Test admin dashboard exception handling"""
        with patch('backend.admin_panel.routes.DATABASE_AVAILABLE', True):
            with patch('backend.admin_panel.routes.db') as mock_db:
                mock_db.jobs.count_documents.side_effect = Exception("Database error")
                
                response = authenticated_client.get("/admin/")
                assert response.status_code == 500
                assert "Dashboard Error" in response.text
    
    def test_admin_jobs_exception_handling(self, authenticated_client):
        """Test admin jobs exception handling"""
        with patch('backend.admin_panel.routes.DATABASE_AVAILABLE', True):
            with patch('backend.admin_panel.routes.db') as mock_db:
                mock_db.jobs.count_documents.side_effect = Exception("Database error")
                
                response = authenticated_client.get("/admin/jobs")
                assert response.status_code == 200
                # Should show demo data when database fails
                assert "Demo Company" in response.text
    
    def test_admin_companies_exception_handling(self, authenticated_client):
        """Test admin companies exception handling"""
        with patch('backend.admin_panel.routes.DATABASE_AVAILABLE', True):
            with patch('backend.admin_panel.routes.db') as mock_db:
                mock_db.jobs.aggregate.side_effect = Exception("Database error")
                
                response = authenticated_client.get("/admin/companies")
                assert response.status_code == 200
                # Should show demo data when database fails
                assert "Remote Company" in response.text
    
    def test_admin_status_exception_handling(self, authenticated_client):
        """Test admin status exception handling"""
        with patch('backend.admin_panel.routes.DATABASE_AVAILABLE', True):
            with patch('backend.admin_panel.routes.db') as mock_db:
                mock_db.jobs.count_documents.side_effect = Exception("Database error")
                
                response = authenticated_client.get("/admin/status")
                assert response.status_code == 500
                assert "Status Error" in response.text
    
    def test_get_service_status_error(self, authenticated_client):
        """Test get service status error handling"""
        with patch('backend.admin_panel.routes.DATABASE_AVAILABLE', True):
            with patch('backend.admin_panel.routes.db') as mock_db:
                mock_db.service_logs.find.side_effect = Exception("Database error")
                
                response = authenticated_client.get("/admin/service-status")
                assert response.status_code == 500

class TestAdminSorting:
    """Test admin panel sorting functionality"""
    
    @pytest.fixture
    def client(self):
        """Create test client."""
        return TestClient(app)
    
    @pytest.fixture
    def authenticated_client(self, client):
        """Create authenticated client session."""
        response = client.post("/admin/login", data={
            "username": "admin",
            "password": "buzz2remote2024"
        })
        return client
    
    def test_admin_jobs_sorting_by_title(self, authenticated_client):
        """Test admin jobs sorting by title"""
        with patch('backend.admin_panel.routes.DATABASE_AVAILABLE', True):
            with patch('backend.admin_panel.routes.db') as mock_db:
                mock_db.jobs.count_documents = AsyncMock(return_value=10)
                mock_cursor = AsyncMock()
                mock_cursor.to_list = AsyncMock(return_value=[])
                mock_db.jobs.find.return_value.sort.return_value.skip.return_value.limit.return_value = mock_cursor
                
                response = authenticated_client.get("/admin/jobs?sort_by=title&sort_order=asc")
                assert response.status_code == 200
                
                # Verify sort was called with correct parameters
                mock_db.jobs.find.return_value.sort.assert_called_with([("title", 1)])
    
    def test_admin_jobs_sorting_by_company_desc(self, authenticated_client):
        """Test admin jobs sorting by company descending"""
        with patch('backend.admin_panel.routes.DATABASE_AVAILABLE', True):
            with patch('backend.admin_panel.routes.db') as mock_db:
                mock_db.jobs.count_documents = AsyncMock(return_value=10)
                mock_cursor = AsyncMock()
                mock_cursor.to_list = AsyncMock(return_value=[])
                mock_db.jobs.find.return_value.sort.return_value.skip.return_value.limit.return_value = mock_cursor
                
                response = authenticated_client.get("/admin/jobs?sort_by=company&sort_order=desc")
                assert response.status_code == 200
                
                # Verify sort was called with correct parameters
                mock_db.jobs.find.return_value.sort.assert_called_with([("company", -1)])
    
    def test_admin_companies_sorting_by_job_count(self, authenticated_client):
        """Test admin companies sorting by job count"""
        with patch('backend.admin_panel.routes.DATABASE_AVAILABLE', True):
            with patch('backend.admin_panel.routes.db') as mock_db:
                mock_cursor = AsyncMock()
                mock_cursor.to_list = AsyncMock(side_effect=[[], [{"total": 0}]])
                mock_db.jobs.aggregate = AsyncMock(return_value=mock_cursor)
                
                response = authenticated_client.get("/admin/companies?sort_by=job_count&sort_order=desc")
                assert response.status_code == 200
                
                # Verify aggregation pipeline includes correct sort
                calls = mock_db.jobs.aggregate.call_args_list
                assert len(calls) >= 1
                pipeline = calls[0][0][0]
                sort_stage = next((stage for stage in pipeline if "$sort" in stage), None)
                assert sort_stage is not None
                assert sort_stage["$sort"]["job_count"] == -1

    def test_admin_companies_jobs_link_functionality(self, authenticated_client):
        """Test that companies page includes job count links"""
        with patch('backend.admin_panel.routes.DATABASE_AVAILABLE', True):
            with patch('backend.admin_panel.routes.db') as mock_db:
                mock_companies = [
                    {
                        "name": "Test Company",
                        "jobs_count": 15,
                        "latest_job": datetime.now()
                    }
                ]
                
                mock_cursor = AsyncMock()
                mock_cursor.to_list = AsyncMock(return_value=mock_companies)
                mock_db.jobs.aggregate = AsyncMock(return_value=mock_cursor)
                
                response = authenticated_client.get("/admin/companies")
                assert response.status_code == 200
                assert "Test Company" in response.text
                assert "Jobs: 15" in response.text
                # Check for the jobs link
                assert "/admin/jobs?company_filter=Test Company" in response.text
    
    def test_admin_jobs_company_filter(self, authenticated_client):
        """Test jobs page with company filter"""
        with patch('backend.admin_panel.routes.DATABASE_AVAILABLE', True):
            with patch('backend.admin_panel.routes.db') as mock_db:
                mock_jobs = [
                    {
                        "_id": "test_id",
                        "title": "Test Job",
                        "company": "Test Company", 
                        "location": "Remote",
                        "source": "test",
                        "created_at": datetime.now(),
                        "url": "https://test.com"
                    }
                ]
                
                mock_db.jobs.count_documents = AsyncMock(return_value=1)
                mock_cursor = AsyncMock()
                mock_cursor.to_list = AsyncMock(return_value=mock_jobs)
                mock_db.jobs.find = AsyncMock(return_value=mock_cursor)
                
                response = authenticated_client.get("/admin/jobs?company_filter=Test Company")
                assert response.status_code == 200
                assert "filtered by company: Test Company" in response.text
                assert "Test Job" in response.text
    
    def test_admin_jobs_page_structure_without_description_and_type(self, authenticated_client):
        """Test that jobs page doesn't show job description and type column"""
        with patch('backend.admin_panel.routes.DATABASE_AVAILABLE', True):
            with patch('backend.admin_panel.routes.db') as mock_db:
                mock_jobs = [
                    {
                        "_id": "test_id",
                        "title": "Test Job",
                        "company": "Test Company",
                        "location": "Remote", 
                        "source": "test",
                        "created_at": datetime.now(),
                        "url": "https://test.com",
                        "description": "This is a long job description that should not be displayed"
                    }
                ]
                
                mock_db.jobs.count_documents = AsyncMock(return_value=1)
                mock_cursor = AsyncMock()
                mock_cursor.to_list = AsyncMock(return_value=mock_jobs)
                mock_db.jobs.find = AsyncMock(return_value=mock_cursor)
                
                response = authenticated_client.get("/admin/jobs")
                assert response.status_code == 200
                # Check that Type column header is not present
                assert "Type</th>" not in response.text
                # Check that job description is not displayed in table
                assert "This is a long job description" not in response.text
                # But title should be there
                assert "Test Job" in response.text
    
    def test_admin_apis_status_corrections(self, authenticated_client):
        """Test API services status page with corrected data"""
        with patch('backend.admin_panel.routes.DATABASE_AVAILABLE', True):
            with patch('backend.admin_panel.routes.db') as mock_db:
                today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
                
                # Mock database calls for API services
                mock_db.jobs.count_documents = AsyncMock(return_value=100)
                mock_db.jobs.find_one = AsyncMock(return_value={
                    "created_at": datetime.now(),
                    "source_type": "remoteok"
                })
                
                response = authenticated_client.get("/admin/apis")
                assert response.status_code == 200
                assert "Real-time Statistics" in response.text
                assert "Total jobs fetched today:" in response.text
                assert "Active services:" in response.text
                # Should not show "0" as total jobs fetched
                assert "📊 Total jobs fetched today: 0" not in response.text
    
    def test_admin_apis_with_database_unavailable(self, authenticated_client):
        """Test API services page when database is unavailable"""
        with patch('backend.admin_panel.routes.DATABASE_AVAILABLE', False):
            response = authenticated_client.get("/admin/apis")
            assert response.status_code == 200
            assert "Real-time Statistics" in response.text
            # Should show demo data instead of errors
            assert "Total jobs fetched today: 60" in response.text  # 12 services * 5 demo jobs each 