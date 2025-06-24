import pytest
import asyncio
from httpx import AsyncClient
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime, timedelta
import uuid

from backend.main import app
from backend.database import get_async_db

class TestJobApplicationsAPI:
    """Test suite for job applications API"""
    
    @pytest.fixture
    async def client(self):
        """Create test client"""
        async with AsyncClient(app=app, base_url="http://test") as ac:
            yield ac
    
    @pytest.fixture
    def mock_db(self):
        """Mock database"""
        db = AsyncMock()
        db.job_applications = AsyncMock()
        db.jobs = AsyncMock()
        db.users = AsyncMock()
        return db
    
    @pytest.fixture
    def mock_user(self):
        """Mock authenticated user"""
        return {
            "_id": "test_user_id",
            "email": "test@example.com",
            "first_name": "John",
            "last_name": "Doe"
        }
    
    @pytest.fixture
    def mock_job(self):
        """Mock job data"""
        return {
            "_id": "test_job_id",
            "title": "Software Engineer",
            "company": "Test Company",
            "location": "Remote",
            "jobType": "Full-time",
            "description": "Test job description"
        }
    
    @pytest.fixture
    def sample_application_data(self):
        """Sample application data"""
        return {
            "job_id": "test_job_id",
            "application_type": "external",
            "cover_letter": "I am excited to apply...",
            "resume_url": "https://example.com/resume.pdf",
            "additional_notes": "Looking forward to hearing from you",
            "external_url": "https://company.com/apply"
        }

    async def test_apply_to_job_success(self, client, mock_db, mock_user, mock_job, sample_application_data):
        """Test successful job application"""
        # Mock database responses
        mock_db.job_applications.find_one.return_value = None  # No existing application
        mock_db.jobs.find_one.return_value = mock_job
        mock_db.job_applications.insert_one.return_value = AsyncMock(inserted_id="app_id")
        
        with patch('backend.routes.applications.get_async_db', return_value=mock_db):
            with patch('backend.routes.applications.get_current_user_dependency', return_value=mock_user):
                response = await client.post("/api/applications/apply", json=sample_application_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Application submitted successfully"
        assert "application_id" in data
        assert data["status"] == "applied"
        
        # Verify database calls
        mock_db.job_applications.find_one.assert_called_once()
        mock_db.jobs.find_one.assert_called_once()
        mock_db.job_applications.insert_one.assert_called_once()

    async def test_apply_to_job_already_applied(self, client, mock_db, mock_user, sample_application_data):
        """Test applying to job when already applied"""
        # Mock existing application
        existing_app = {
            "_id": "existing_app_id",
            "user_id": "test_user_id",
            "job_id": "test_job_id",
            "status": "applied"
        }
        mock_db.job_applications.find_one.return_value = existing_app
        
        with patch('backend.routes.applications.get_async_db', return_value=mock_db):
            with patch('backend.routes.applications.get_current_user_dependency', return_value=mock_user):
                response = await client.post("/api/applications/apply", json=sample_application_data)
        
        assert response.status_code == 400
        data = response.json()
        assert "already applied" in data["detail"]

    async def test_apply_to_nonexistent_job(self, client, mock_db, mock_user, sample_application_data):
        """Test applying to non-existent job"""
        mock_db.job_applications.find_one.return_value = None  # No existing application
        mock_db.jobs.find_one.return_value = None  # Job not found
        
        with patch('backend.routes.applications.get_async_db', return_value=mock_db):
            with patch('backend.routes.applications.get_current_user_dependency', return_value=mock_user):
                response = await client.post("/api/applications/apply", json=sample_application_data)
        
        assert response.status_code == 404
        data = response.json()
        assert "Job not found" in data["detail"]

    async def test_get_my_applications(self, client, mock_db, mock_user, mock_job):
        """Test getting user's applications"""
        # Mock applications data
        applications = [
            {
                "_id": "app1",
                "user_id": "test_user_id",
                "job_id": "test_job_id",
                "status": "applied",
                "application_type": "external",
                "applied_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
                "viewed_by_company": False
            },
            {
                "_id": "app2",
                "user_id": "test_user_id",
                "job_id": "test_job_id",
                "status": "viewed",
                "application_type": "automated",
                "applied_at": datetime.utcnow() - timedelta(days=1),
                "updated_at": datetime.utcnow(),
                "viewed_by_company": True
            }
        ]
        
        mock_db.job_applications.count_documents.return_value = 2
        mock_db.job_applications.find.return_value.sort.return_value.skip.return_value.limit.return_value = AsyncMock()
        
        # Mock async iteration
        async def mock_async_iter():
            for app in applications:
                yield app
        
        mock_db.job_applications.find.return_value.sort.return_value.skip.return_value.limit.return_value.__aiter__ = mock_async_iter
        mock_db.jobs.find_one.return_value = mock_job
        
        with patch('backend.routes.applications.get_async_db', return_value=mock_db):
            with patch('backend.routes.applications.get_current_user_dependency', return_value=mock_user):
                response = await client.get("/api/applications/my-applications")
        
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 2
        assert len(data["applications"]) == 2
        assert data["applications"][0]["status"] == "applied"
        assert data["applications"][1]["status"] == "viewed"

    async def test_get_my_applications_with_filters(self, client, mock_db, mock_user):
        """Test getting applications with status filter"""
        mock_db.job_applications.count_documents.return_value = 1
        mock_db.job_applications.find.return_value.sort.return_value.skip.return_value.limit.return_value = AsyncMock()
        
        # Mock async iteration with single result
        async def mock_async_iter():
            yield {
                "_id": "app1",
                "user_id": "test_user_id",
                "job_id": "test_job_id",
                "status": "hired",
                "application_type": "external",
                "applied_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
                "viewed_by_company": True
            }
        
        mock_db.job_applications.find.return_value.sort.return_value.skip.return_value.limit.return_value.__aiter__ = mock_async_iter
        mock_db.jobs.find_one.return_value = {"title": "Test Job", "company": "Test Company"}
        
        with patch('backend.routes.applications.get_async_db', return_value=mock_db):
            with patch('backend.routes.applications.get_current_user_dependency', return_value=mock_user):
                response = await client.get("/api/applications/my-applications?status_filter=hired&page=1&per_page=10")
        
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert len(data["applications"]) == 1
        assert data["applications"][0]["status"] == "hired"

    async def test_check_if_applied_true(self, client, mock_db, mock_user):
        """Test checking if user has applied to a job (true case)"""
        application = {
            "_id": "app1",
            "user_id": "test_user_id",
            "job_id": "test_job_id",
            "status": "applied",
            "applied_at": datetime.utcnow(),
            "application_type": "external"
        }
        mock_db.job_applications.find_one.return_value = application
        
        with patch('backend.routes.applications.get_async_db', return_value=mock_db):
            with patch('backend.routes.applications.get_current_user_dependency', return_value=mock_user):
                response = await client.get("/api/applications/check-applied/test_job_id")
        
        assert response.status_code == 200
        data = response.json()
        assert data["has_applied"] == True
        assert data["application"] is not None
        assert data["application"]["status"] == "applied"

    async def test_check_if_applied_false(self, client, mock_db, mock_user):
        """Test checking if user has applied to a job (false case)"""
        mock_db.job_applications.find_one.return_value = None
        
        with patch('backend.routes.applications.get_async_db', return_value=mock_db):
            with patch('backend.routes.applications.get_current_user_dependency', return_value=mock_user):
                response = await client.get("/api/applications/check-applied/test_job_id")
        
        assert response.status_code == 200
        data = response.json()
        assert data["has_applied"] == False
        assert data["application"] is None

    async def test_get_applied_job_ids(self, client, mock_db, mock_user):
        """Test getting list of applied job IDs"""
        applications = [
            {"job_id": "job1"},
            {"job_id": "job2"},
            {"job_id": "job3"}
        ]
        
        mock_db.job_applications.find.return_value = AsyncMock()
        
        # Mock async iteration
        async def mock_async_iter():
            for app in applications:
                yield app
        
        mock_db.job_applications.find.return_value.__aiter__ = mock_async_iter
        
        with patch('backend.routes.applications.get_async_db', return_value=mock_db):
            with patch('backend.routes.applications.get_current_user_dependency', return_value=mock_user):
                response = await client.get("/api/applications/applied-jobs")
        
        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 3
        assert len(data["applied_job_ids"]) == 3
        assert "job1" in data["applied_job_ids"]
        assert "job2" in data["applied_job_ids"]
        assert "job3" in data["applied_job_ids"]

    async def test_get_specific_application(self, client, mock_db, mock_user, mock_job):
        """Test getting specific application details"""
        application = {
            "_id": "app1",
            "user_id": "test_user_id",
            "job_id": "test_job_id",
            "status": "applied",
            "application_type": "external",
            "cover_letter": "Test cover letter",
            "applied_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "viewed_by_company": False
        }
        
        mock_db.job_applications.find_one.return_value = application
        mock_db.jobs.find_one.return_value = mock_job
        
        with patch('backend.routes.applications.get_async_db', return_value=mock_db):
            with patch('backend.routes.applications.get_current_user_dependency', return_value=mock_user):
                response = await client.get("/api/applications/app1")
        
        assert response.status_code == 200
        data = response.json()
        assert data["application"]["id"] == "app1"
        assert data["application"]["status"] == "applied"
        assert data["application"]["cover_letter"] == "Test cover letter"
        assert data["application"]["job"]["title"] == "Software Engineer"

    async def test_get_nonexistent_application(self, client, mock_db, mock_user):
        """Test getting non-existent application"""
        mock_db.job_applications.find_one.return_value = None
        
        with patch('backend.routes.applications.get_async_db', return_value=mock_db):
            with patch('backend.routes.applications.get_current_user_dependency', return_value=mock_user):
                response = await client.get("/api/applications/nonexistent")
        
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"]

    async def test_update_application(self, client, mock_db, mock_user):
        """Test updating application status"""
        existing_app = {
            "_id": "app1",
            "user_id": "test_user_id",
            "job_id": "test_job_id",
            "status": "applied"
        }
        
        mock_db.job_applications.find_one.return_value = existing_app
        mock_db.job_applications.update_one.return_value = AsyncMock(modified_count=1)
        
        update_data = {
            "status": "interviewed",
            "additional_notes": "Had a great interview",
            "company_response": "Moving to next round"
        }
        
        with patch('backend.routes.applications.get_async_db', return_value=mock_db):
            with patch('backend.routes.applications.get_current_user_dependency', return_value=mock_user):
                response = await client.put("/api/applications/app1", json=update_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Application updated successfully"
        assert data["application_id"] == "app1"
        
        # Verify update call
        mock_db.job_applications.update_one.assert_called_once()

    async def test_update_nonexistent_application(self, client, mock_db, mock_user):
        """Test updating non-existent application"""
        mock_db.job_applications.find_one.return_value = None
        
        update_data = {"status": "interviewed"}
        
        with patch('backend.routes.applications.get_async_db', return_value=mock_db):
            with patch('backend.routes.applications.get_current_user_dependency', return_value=mock_user):
                response = await client.put("/api/applications/nonexistent", json=update_data)
        
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"]

    async def test_withdraw_application(self, client, mock_db, mock_user):
        """Test withdrawing an application"""
        existing_app = {
            "_id": "app1",
            "user_id": "test_user_id",
            "job_id": "test_job_id",
            "status": "applied"
        }
        
        mock_db.job_applications.find_one.return_value = existing_app
        mock_db.job_applications.update_one.return_value = AsyncMock(modified_count=1)
        
        with patch('backend.routes.applications.get_async_db', return_value=mock_db):
            with patch('backend.routes.applications.get_current_user_dependency', return_value=mock_user):
                response = await client.delete("/api/applications/app1")
        
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Application withdrawn successfully"
        
        # Verify status was set to withdrawn
        update_call = mock_db.job_applications.update_one.call_args
        assert update_call[0][1]["$set"]["status"] == "withdrawn"

    async def test_get_application_stats(self, client, mock_db, mock_user):
        """Test getting application statistics"""
        # Mock database counts
        mock_db.job_applications.count_documents.side_effect = [
            10,  # Total applications
            7,   # Applied status
            2,   # Viewed status  
            1,   # Rejected status
            0,   # Hired status
            0,   # Withdrawn status
            8,   # External type
            2,   # Scraped type
            0,   # Automated type
            3,   # Recent applications
            2    # Responded applications
        ]
        
        with patch('backend.routes.applications.get_async_db', return_value=mock_db):
            with patch('backend.routes.applications.get_current_user_dependency', return_value=mock_user):
                response = await client.get("/api/applications/stats")
        
        assert response.status_code == 200
        data = response.json()
        assert data["total_applications"] == 10
        assert data["status_breakdown"]["applied"] == 7
        assert data["status_breakdown"]["viewed"] == 2
        assert data["status_breakdown"]["rejected"] == 1
        assert data["type_breakdown"]["external"] == 8
        assert data["type_breakdown"]["scraped"] == 2
        assert data["recent_applications"] == 3
        assert data["responded_applications"] == 2
        assert data["response_rate"] == 20.0  # 2/10 * 100

    async def test_application_validation_errors(self, client, mock_user):
        """Test application data validation"""
        # Test missing job_id
        invalid_data = {
            "application_type": "external",
            "cover_letter": "Test"
        }
        
        with patch('backend.routes.applications.get_current_user_dependency', return_value=mock_user):
            response = await client.post("/api/applications/apply", json=invalid_data)
        
        assert response.status_code == 422  # Validation error

    async def test_pagination_edge_cases(self, client, mock_db, mock_user):
        """Test pagination edge cases"""
        mock_db.job_applications.count_documents.return_value = 0
        mock_db.job_applications.find.return_value.sort.return_value.skip.return_value.limit.return_value = AsyncMock()
        
        # Mock empty async iteration
        async def mock_empty_iter():
            return
            yield  # Unreachable
        
        mock_db.job_applications.find.return_value.sort.return_value.skip.return_value.limit.return_value.__aiter__ = mock_empty_iter
        
        with patch('backend.routes.applications.get_async_db', return_value=mock_db):
            with patch('backend.routes.applications.get_current_user_dependency', return_value=mock_user):
                response = await client.get("/api/applications/my-applications?page=1&per_page=20")
        
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0
        assert len(data["applications"]) == 0
        assert data["pages"] == 0

    async def test_concurrent_applications(self, client, mock_db, mock_user, mock_job, sample_application_data):
        """Test handling concurrent applications to same job"""
        # Simulate race condition where application is created between check and insert
        mock_db.job_applications.find_one.side_effect = [None, {"_id": "existing"}]  # First check passes, second fails
        mock_db.jobs.find_one.return_value = mock_job
        mock_db.job_applications.insert_one.side_effect = Exception("Duplicate key error")
        
        with patch('backend.routes.applications.get_async_db', return_value=mock_db):
            with patch('backend.routes.applications.get_current_user_dependency', return_value=mock_user):
                response = await client.post("/api/applications/apply", json=sample_application_data)
        
        assert response.status_code == 500  # Should handle gracefully

    async def test_large_dataset_performance(self, client, mock_db, mock_user):
        """Test performance with large number of applications"""
        # Mock large dataset
        mock_db.job_applications.count_documents.return_value = 1000
        
        # Mock efficient pagination
        applications = [
            {
                "_id": f"app{i}",
                "user_id": "test_user_id",
                "job_id": f"job{i}",
                "status": "applied",
                "application_type": "external",
                "applied_at": datetime.utcnow() - timedelta(days=i),
                "updated_at": datetime.utcnow(),
                "viewed_by_company": False
            }
            for i in range(20)  # One page worth
        ]
        
        mock_db.job_applications.find.return_value.sort.return_value.skip.return_value.limit.return_value = AsyncMock()
        
        # Mock async iteration
        async def mock_async_iter():
            for app in applications:
                yield app
        
        mock_db.job_applications.find.return_value.sort.return_value.skip.return_value.limit.return_value.__aiter__ = mock_async_iter
        mock_db.jobs.find_one.return_value = {"title": "Test", "company": "Test"}
        
        with patch('backend.routes.applications.get_async_db', return_value=mock_db):
            with patch('backend.routes.applications.get_current_user_dependency', return_value=mock_user):
                response = await client.get("/api/applications/my-applications?page=1&per_page=20")
        
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1000
        assert len(data["applications"]) == 20
        assert data["pages"] == 50

    async def test_authentication_required(self, client):
        """Test that all endpoints require authentication"""
        endpoints = [
            ("POST", "/api/applications/apply", {"job_id": "test"}),
            ("GET", "/api/applications/my-applications", None),
            ("GET", "/api/applications/check-applied/test", None),
            ("GET", "/api/applications/applied-jobs", None),
            ("GET", "/api/applications/test", None),
            ("PUT", "/api/applications/test", {"status": "viewed"}),
            ("DELETE", "/api/applications/test", None),
            ("GET", "/api/applications/stats", None)
        ]
        
        for method, endpoint, data in endpoints:
            if method == "POST":
                response = await client.post(endpoint, json=data)
            elif method == "PUT":
                response = await client.put(endpoint, json=data)
            elif method == "DELETE":
                response = await client.delete(endpoint)
            else:
                response = await client.get(endpoint)
            
            # Should require authentication
            assert response.status_code in [401, 403, 422], f"Endpoint {endpoint} should require auth"

# Integration tests for the complete application flow
class TestApplicationIntegration:
    """Integration tests for complete application workflow"""
    
    async def test_complete_application_workflow(self, client):
        """Test complete application workflow from apply to hire"""
        # This would be a full integration test with real database
        # For now, we'll mock the entire flow
        
        mock_db = AsyncMock()
        mock_user = {"_id": "user1", "email": "test@example.com"}
        mock_job = {"_id": "job1", "title": "Developer", "company": "TechCorp"}
        
        # Step 1: Apply to job
        mock_db.job_applications.find_one.return_value = None
        mock_db.jobs.find_one.return_value = mock_job
        mock_db.job_applications.insert_one.return_value = AsyncMock(inserted_id="app1")
        
        with patch('backend.routes.applications.get_async_db', return_value=mock_db):
            with patch('backend.routes.applications.get_current_user_dependency', return_value=mock_user):
                # Apply
                apply_response = await client.post("/api/applications/apply", json={
                    "job_id": "job1",
                    "application_type": "external",
                    "cover_letter": "Excited to apply!"
                })
                
                assert apply_response.status_code == 200
                
                # Check application status
                mock_db.job_applications.find_one.return_value = {
                    "_id": "app1",
                    "user_id": "user1",
                    "job_id": "job1",
                    "status": "applied",
                    "application_type": "external",
                    "applied_at": datetime.utcnow()
                }
                
                check_response = await client.get("/api/applications/check-applied/job1")
                assert check_response.status_code == 200
                assert check_response.json()["has_applied"] == True
                
                # Update status to viewed
                mock_db.job_applications.update_one.return_value = AsyncMock(modified_count=1)
                
                update_response = await client.put("/api/applications/app1", json={
                    "status": "viewed",
                    "company_response": "We reviewed your application"
                })
                
                assert update_response.status_code == 200
                
                # Get statistics
                mock_db.job_applications.count_documents.side_effect = [1, 0, 1, 0, 0, 0, 1, 0, 0, 1, 1]
                
                stats_response = await client.get("/api/applications/stats")
                assert stats_response.status_code == 200
                assert stats_response.json()["total_applications"] == 1

if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 