import pytest
from unittest.mock import Mock, AsyncMock, patch
from fastapi.testclient import TestClient
from backend.main import app

pytestmark = pytest.mark.asyncio


class TestAdminCleanup:
    """Admin cleanup routes testleri"""
    
    @pytest.fixture
    def client(self):
        """Test client"""
        return TestClient(app)
    
    @pytest.fixture
    def mock_db(self):
        """Mock database"""
        mock_db = Mock()
        mock_jobs = Mock()
        mock_db.jobs = mock_jobs
        return mock_db, mock_jobs
    
    @patch('backend.routes.admin_cleanup.get_db')
    async def test_cleanup_unknown_company_no_jobs(self, mock_get_db, client, mock_db):
        """Test cleanup when no unknown company jobs exist"""
        mock_db_instance, mock_jobs = mock_db
        mock_get_db.return_value = mock_db_instance
        
        # Mock count_documents to return 0
        mock_jobs.count_documents.return_value = 0
        
        response = client.post("/admin/cleanup/unknown-company")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["message"] == "No unknown company jobs found"
        assert data["cleaned"] == 0
    
    @patch('backend.routes.admin_cleanup.get_db')
    async def test_cleanup_unknown_company_with_jobs(self, mock_get_db, client, mock_db):
        """Test cleanup with unknown company jobs"""
        mock_db_instance, mock_jobs = mock_db
        mock_get_db.return_value = mock_db_instance
        
        # Mock count_documents to return some jobs
        mock_jobs.count_documents.return_value = 5
        
        # Mock find cursor
        mock_cursor = Mock()
        mock_jobs.find.return_value = mock_cursor
        
        # Mock jobs data
        mock_jobs_data = [
            {
                "_id": "job1",
                "title": "Developer at Test Company",
                "url": "https://test-company.greenhouse.io/boards/job/123",
                "company": "Unknown Company"
            },
            {
                "_id": "job2", 
                "title": "Engineer at Another Corp",
                "url": "https://another-corp.lever.co/jobs/456",
                "company": ""
            }
        ]
        
        # Mock cursor methods
        mock_cursor.limit.return_value = mock_cursor
        mock_cursor.to_list = AsyncMock(return_value=mock_jobs_data)
        
        # Mock update_one
        mock_jobs.update_one = AsyncMock()
        
        response = client.post("/admin/cleanup/unknown-company")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "Processed" in data["message"]
        assert data["updated"] >= 0
        assert data["remaining"] >= 0
    
    @patch('backend.routes.admin_cleanup.get_db')
    async def test_cleanup_unknown_company_database_error(self, mock_get_db, client):
        """Test cleanup with database error"""
        mock_get_db.return_value = None
        
        response = client.post("/admin/cleanup/unknown-company")
        
        assert response.status_code == 503
        data = response.json()
        assert "Database not available" in data["detail"]
    
    @patch('backend.routes.admin_cleanup.get_db')
    async def test_cleanup_unknown_company_exception(self, mock_get_db, client, mock_db):
        """Test cleanup with general exception"""
        mock_db_instance, mock_jobs = mock_db
        mock_get_db.return_value = mock_db_instance
        
        # Mock count_documents to raise exception
        mock_jobs.count_documents.side_effect = Exception("Database error")
        
        response = client.post("/admin/cleanup/unknown-company")
        
        assert response.status_code == 500
        data = response.json()
        assert "Database error" in data["detail"]
    
    @patch('backend.routes.admin_cleanup.get_db')
    async def test_get_unknown_company_stats_success(self, mock_get_db, client, mock_db):
        """Test getting unknown company statistics successfully"""
        mock_db_instance, mock_jobs = mock_db
        mock_get_db.return_value = mock_db_instance
        
        # Mock count_documents for different queries
        mock_jobs.count_documents.side_effect = [10, 5, 3, 2]  # Different counts for different queries
        
        # Mock find cursor for samples
        mock_cursor = Mock()
        mock_jobs.find.return_value = mock_cursor
        
        # Mock sample jobs
        mock_samples = [
            {
                "_id": "job1",
                "title": "Test Job 1",
                "url": "https://example.com/job1",
                "company": "Unknown Company"
            },
            {
                "_id": "job2",
                "title": "Test Job 2", 
                "url": "https://example.com/job2",
                "company": ""
            }
        ]
        
        # Mock async iterator
        async def mock_async_iterator():
            for sample in mock_samples:
                yield sample
        
        mock_cursor.__aiter__ = mock_async_iterator
        
        response = client.get("/admin/stats/unknown-company")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "stats" in data
        assert "samples" in data
        assert data["stats"]["total"] == 20  # 10 + 5 + 3 + 2
        assert len(data["samples"]) == 2
    
    @patch('backend.routes.admin_cleanup.get_db')
    async def test_get_unknown_company_stats_database_error(self, mock_get_db, client):
        """Test getting stats with database error"""
        mock_get_db.return_value = None
        
        response = client.get("/admin/stats/unknown-company")
        
        assert response.status_code == 503
        data = response.json()
        assert "Database not available" in data["detail"]
    
    @patch('backend.routes.admin_cleanup.get_db')
    async def test_get_unknown_company_stats_exception(self, mock_get_db, client, mock_db):
        """Test getting stats with general exception"""
        mock_db_instance, mock_jobs = mock_db
        mock_get_db.return_value = mock_db_instance
        
        # Mock count_documents to raise exception
        mock_jobs.count_documents.side_effect = Exception("Database error")
        
        response = client.get("/admin/stats/unknown-company")
        
        assert response.status_code == 500
        data = response.json()
        assert "Database error" in data["detail"]
    
    @patch('backend.routes.admin_cleanup.get_db')
    async def test_cleanup_extract_company_from_greenhouse_url(self, mock_get_db, client, mock_db):
        """Test extracting company from Greenhouse URL"""
        mock_db_instance, mock_jobs = mock_db
        mock_get_db.return_value = mock_db_instance
        
        mock_jobs.count_documents.return_value = 1
        
        mock_cursor = Mock()
        mock_jobs.find.return_value = mock_cursor
        
        # Job with Greenhouse URL
        mock_jobs_data = [{
            "_id": "job1",
            "title": "Developer",
            "url": "https://test-company.greenhouse.io/boards/job/123",
            "company": "Unknown Company"
        }]
        
        mock_cursor.limit.return_value = mock_cursor
        mock_cursor.to_list = AsyncMock(return_value=mock_jobs_data)
        mock_jobs.update_one = AsyncMock()
        
        response = client.post("/admin/cleanup/unknown-company")
        
        assert response.status_code == 200
        # Verify update_one was called with extracted company name
        mock_jobs.update_one.assert_called_once()
        call_args = mock_jobs.update_one.call_args
        assert call_args[0][1]["$set"]["company"] == "Test Company"
    
    @patch('backend.routes.admin_cleanup.get_db')
    async def test_cleanup_extract_company_from_lever_url(self, mock_get_db, client, mock_db):
        """Test extracting company from Lever URL"""
        mock_db_instance, mock_jobs = mock_db
        mock_get_db.return_value = mock_db_instance
        
        mock_jobs.count_documents.return_value = 1
        
        mock_cursor = Mock()
        mock_jobs.find.return_value = mock_cursor
        
        # Job with Lever URL
        mock_jobs_data = [{
            "_id": "job1",
            "title": "Engineer",
            "url": "https://lever.co/another-corp/jobs/456",
            "company": ""
        }]
        
        mock_cursor.limit.return_value = mock_cursor
        mock_cursor.to_list = AsyncMock(return_value=mock_jobs_data)
        mock_jobs.update_one = AsyncMock()
        
        response = client.post("/admin/cleanup/unknown-company")
        
        assert response.status_code == 200
        # Verify update_one was called with extracted company name
        mock_jobs.update_one.assert_called_once()
        call_args = mock_jobs.update_one.call_args
        assert call_args[0][1]["$set"]["company"] == "Another Corp"
    
    @patch('backend.routes.admin_cleanup.get_db')
    async def test_cleanup_extract_company_from_title(self, mock_get_db, client, mock_db):
        """Test extracting company from job title"""
        mock_db_instance, mock_jobs = mock_db
        mock_get_db.return_value = mock_db_instance
        
        mock_jobs.count_documents.return_value = 1
        
        mock_cursor = Mock()
        mock_jobs.find.return_value = mock_cursor
        
        # Job with company in title
        mock_jobs_data = [{
            "_id": "job1",
            "title": "Senior Developer at Tech Corp",
            "url": "https://example.com/job",
            "company": None
        }]
        
        mock_cursor.limit.return_value = mock_cursor
        mock_cursor.to_list = AsyncMock(return_value=mock_jobs_data)
        mock_jobs.update_one = AsyncMock()
        
        response = client.post("/admin/cleanup/unknown-company")
        
        assert response.status_code == 200
        # Verify update_one was called with extracted company name
        mock_jobs.update_one.assert_called_once()
        call_args = mock_jobs.update_one.call_args
        assert call_args[0][1]["$set"]["company"] == "Tech Corp"
    
    @patch('backend.routes.admin_cleanup.get_db')
    async def test_cleanup_no_company_extracted(self, mock_get_db, client, mock_db):
        """Test cleanup when no company can be extracted"""
        mock_db_instance, mock_jobs = mock_db
        mock_get_db.return_value = mock_db_instance
        
        mock_jobs.count_documents.return_value = 1
        
        mock_cursor = Mock()
        mock_jobs.find.return_value = mock_cursor
        
        # Job with no extractable company info
        mock_jobs_data = [{
            "_id": "job1",
            "title": "Developer",
            "url": "https://example.com/job",
            "company": "Unknown Company"
        }]
        
        mock_cursor.limit.return_value = mock_cursor
        mock_cursor.to_list = AsyncMock(return_value=mock_jobs_data)
        mock_jobs.update_one = AsyncMock()
        
        response = client.post("/admin/cleanup/unknown-company")
        
        assert response.status_code == 200
        data = response.json()
        assert data["updated"] == 0  # No company extracted
        assert data["remaining"] == 1  # One job remains unchanged 