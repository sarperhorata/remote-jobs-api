import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime, timedelta
from bson import ObjectId
import json

# Test data for integration tests
test_user_data = {
    "_id": str(ObjectId()),
    "email": "testuser@example.com",
    "name": "Test User",
    "hashed_password": "$2b$12$test_hash",
    "is_active": True,
    "is_verified": True,
    "created_at": datetime.utcnow()
}

test_company_data = {
    "_id": str(ObjectId()),
    "name": "Test Company",
    "description": "A test company for integration tests",
    "website": "https://testcompany.com",
    "logo_url": "https://testcompany.com/logo.png",
    "is_verified": True,
    "created_at": datetime.utcnow()
}

test_job_data = {
    "_id": str(ObjectId()),
    "title": "Senior Software Engineer",
    "company": "Test Company",
    "company_id": str(ObjectId()),
    "location": "Remote",
    "description": "We are looking for a senior software engineer...",
    "requirements": ["Python", "FastAPI", "MongoDB"],
    "salary_range": "$80,000 - $120,000",
    "job_type": "Full-time",
    "experience_level": "Senior",
    "is_active": True,
    "created_at": datetime.utcnow(),
    "created_by": test_user_data["_id"]
}

test_application_data = {
    "_id": str(ObjectId()),
    "job_id": test_job_data["_id"],
    "user_id": test_user_data["_id"],
    "status": "pending",
    "cover_letter": "I am interested in this position...",
    "resume_url": "https://example.com/resume.pdf",
    "applied_at": datetime.utcnow()
}

@pytest.mark.integration
class TestJobWorkflowIntegration:
    """Integration tests for complete job workflow."""

    @pytest.mark.asyncio
    async def test_complete_job_workflow(self, client, db_mock):
        """Test complete workflow: create job -> apply -> track application."""
        
        # Step 1: Create a company
        with patch('backend.routes.companies.get_database', return_value=db_mock):
            db_mock.companies.insert_one.return_value = MagicMock(inserted_id=test_company_data["_id"])
            db_mock.companies.find_one.return_value = test_company_data
            
            company_response = client.post(
                "/api/v1/companies",
                json={
                    "name": test_company_data["name"],
                    "description": test_company_data["description"],
                    "website": test_company_data["website"]
                },
                headers={"Authorization": f"Bearer test_token"}
            )
            
            assert company_response.status_code in [200, 201]
            company_id = company_response.json().get("_id")
            
        # Step 2: Create a job for the company
        with patch('backend.routes.jobs.get_database', return_value=db_mock):
            db_mock.jobs.insert_one.return_value = MagicMock(inserted_id=test_job_data["_id"])
            db_mock.jobs.find_one.return_value = {**test_job_data, "company_id": company_id}
            
            job_response = client.post(
                "/api/v1/jobs",
                json={
                    "title": test_job_data["title"],
                    "company": test_company_data["name"],
                    "company_id": company_id,
                    "location": test_job_data["location"],
                    "description": test_job_data["description"],
                    "requirements": test_job_data["requirements"],
                    "salary_range": test_job_data["salary_range"],
                    "job_type": test_job_data["job_type"],
                    "experience_level": test_job_data["experience_level"]
                },
                headers={"Authorization": f"Bearer test_token"}
            )
            
            assert job_response.status_code in [200, 201]
            job_id = job_response.json().get("_id")
            
        # Step 3: Search and find the job
        with patch('backend.routes.jobs.get_database', return_value=db_mock):
            db_mock.jobs.find.return_value.to_list.return_value = [{**test_job_data, "_id": job_id}]
            db_mock.jobs.count_documents.return_value = 1
            
            search_response = client.get(f"/api/v1/jobs?search=Software Engineer")
            
            assert search_response.status_code == 200
            jobs = search_response.json().get("items", search_response.json().get("jobs", []))
            assert len(jobs) > 0
            assert jobs[0]["_id"] == job_id
            
        # Step 4: Apply for the job
        with patch('backend.routes.applications.get_database', return_value=db_mock):
            db_mock.applications.insert_one.return_value = MagicMock(inserted_id=test_application_data["_id"])
            db_mock.applications.find_one.return_value = {**test_application_data, "job_id": job_id}
            
            application_response = client.post(
                "/api/v1/applications",
                json={
                    "job_id": job_id,
                    "cover_letter": test_application_data["cover_letter"],
                    "resume_url": test_application_data["resume_url"]
                },
                headers={"Authorization": f"Bearer test_token"}
            )
            
            assert application_response.status_code in [200, 201]
            application_id = application_response.json().get("_id")
            
        # Step 5: Track application status
        with patch('backend.routes.applications.get_database', return_value=db_mock):
            db_mock.applications.find_one.return_value = {**test_application_data, "_id": application_id}
            
            status_response = client.get(
                f"/api/v1/applications/{application_id}",
                headers={"Authorization": f"Bearer test_token"}
            )
            
            assert status_response.status_code == 200
            application = status_response.json()
            assert application["status"] == "pending"
            assert application["job_id"] == job_id

    @pytest.mark.asyncio
    async def test_job_search_and_filter_integration(self, client, db_mock):
        """Test integration of search and filtering functionality."""
        
        # Create multiple jobs for testing
        jobs_data = [
            {**test_job_data, "_id": str(ObjectId()), "title": "Python Developer", "location": "Remote", "company": "TechCorp"},
            {**test_job_data, "_id": str(ObjectId()), "title": "Frontend Developer", "location": "New York", "company": "StartupCorp"},
            {**test_job_data, "_id": str(ObjectId()), "title": "DevOps Engineer", "location": "Remote", "company": "BigCorp"},
            {**test_job_data, "_id": str(ObjectId()), "title": "Data Scientist", "location": "San Francisco", "company": "DataCorp"}
        ]
        
        with patch('backend.routes.jobs.get_database', return_value=db_mock):
            # Test search by title
            db_mock.jobs.find.return_value.to_list.return_value = [jobs_data[0]]  # Python Developer
            db_mock.jobs.count_documents.return_value = 1
            
            search_response = client.get("/api/v1/jobs?search=Python")
            assert search_response.status_code == 200
            jobs = search_response.json().get("items", search_response.json().get("jobs", []))
            assert len(jobs) == 1
            assert "Python" in jobs[0]["title"]
            
            # Test filter by location
            remote_jobs = [jobs_data[0], jobs_data[2]]  # Remote jobs
            db_mock.jobs.find.return_value.to_list.return_value = remote_jobs
            db_mock.jobs.count_documents.return_value = 2
            
            filter_response = client.get("/api/v1/jobs?location=Remote")
            assert filter_response.status_code == 200
            jobs = filter_response.json().get("items", filter_response.json().get("jobs", []))
            assert len(jobs) == 2
            assert all(job["location"] == "Remote" for job in jobs)
            
            # Test combined search and filter
            db_mock.jobs.find.return_value.to_list.return_value = [jobs_data[0]]  # Remote Python job
            db_mock.jobs.count_documents.return_value = 1
            
            combined_response = client.get("/api/v1/jobs?search=Python&location=Remote")
            assert combined_response.status_code == 200
            jobs = combined_response.json().get("items", combined_response.json().get("jobs", []))
            assert len(jobs) == 1
            assert "Python" in jobs[0]["title"] and jobs[0]["location"] == "Remote"

    @pytest.mark.asyncio
    async def test_job_application_workflow_integration(self, client, db_mock):
        """Test complete job application workflow."""
        
        # Mock user authentication
        with patch('backend.routes.auth.get_database', return_value=db_mock):
            db_mock.users.find_one.return_value = test_user_data
            
            # Step 1: User logs in
            login_response = client.post(
                "/api/v1/auth/login",
                json={
                    "email": test_user_data["email"],
                    "password": "testpassword"
                }
            )
            
            # Mock successful login
            if login_response.status_code == 200:
                token = login_response.json().get("access_token", "test_token")
            else:
                token = "test_token"  # Fallback for testing
                
        # Step 2: Browse available jobs
        with patch('backend.routes.jobs.get_database', return_value=db_mock):
            db_mock.jobs.find.return_value.to_list.return_value = [test_job_data]
            db_mock.jobs.count_documents.return_value = 1
            
            browse_response = client.get("/api/v1/jobs")
            assert browse_response.status_code == 200
            jobs = browse_response.json().get("items", browse_response.json().get("jobs", []))
            assert len(jobs) > 0
            
        # Step 3: Get job details
        with patch('backend.routes.jobs.get_database', return_value=db_mock):
            db_mock.jobs.find_one.return_value = test_job_data
            
            job_detail_response = client.get(f"/api/v1/jobs/{test_job_data['_id']}")
            assert job_detail_response.status_code == 200
            job_detail = job_detail_response.json()
            assert job_detail["title"] == test_job_data["title"]
            
        # Step 4: Submit application
        with patch('backend.routes.applications.get_database', return_value=db_mock):
            db_mock.applications.insert_one.return_value = MagicMock(inserted_id=test_application_data["_id"])
            db_mock.applications.find_one.return_value = test_application_data
            
            application_response = client.post(
                "/api/v1/applications",
                json={
                    "job_id": test_job_data["_id"],
                    "cover_letter": "I am very interested in this position...",
                    "resume_url": "https://example.com/my-resume.pdf"
                },
                headers={"Authorization": f"Bearer {token}"}
            )
            
            assert application_response.status_code in [200, 201]
            
        # Step 5: Track application status
        with patch('backend.routes.applications.get_database', return_value=db_mock):
            db_mock.applications.find.return_value.to_list.return_value = [test_application_data]
            
            applications_response = client.get(
                "/api/v1/applications",
                headers={"Authorization": f"Bearer {token}"}
            )
            
            assert applications_response.status_code == 200
            applications = applications_response.json().get("items", applications_response.json().get("applications", []))
            assert len(applications) > 0
            assert applications[0]["job_id"] == test_job_data["_id"]

    @pytest.mark.asyncio
    async def test_job_recommendation_integration(self, client, db_mock):
        """Test job recommendation system integration."""
        
        # Create multiple jobs with different characteristics
        jobs_data = [
            {**test_job_data, "_id": str(ObjectId()), "title": "Python Backend Developer", "skills": ["Python", "Django", "PostgreSQL"]},
            {**test_job_data, "_id": str(ObjectId()), "title": "Frontend React Developer", "skills": ["React", "JavaScript", "TypeScript"]},
            {**test_job_data, "_id": str(ObjectId()), "title": "Full Stack Developer", "skills": ["Python", "React", "MongoDB"]},
            {**test_job_data, "_id": str(ObjectId()), "title": "DevOps Engineer", "skills": ["Docker", "Kubernetes", "AWS"]}
        ]
        
        # Mock user profile with skills
        user_profile = {
            **test_user_data,
            "skills": ["Python", "Django", "PostgreSQL", "React"],
            "experience_level": "Senior",
            "preferred_locations": ["Remote", "New York"]
        }
        
        with patch('backend.routes.jobs.get_database', return_value=db_mock):
            # Mock AI recommendation service
            with patch('backend.services.ai_job_matching_service.get_job_recommendations') as mock_recommendations:
                mock_recommendations.return_value = [jobs_data[0], jobs_data[2]]  # Python and Full Stack jobs
                
                # Test job recommendations endpoint
                recommendations_response = client.get(
                    "/api/v1/jobs/recommendations",
                    headers={"Authorization": f"Bearer test_token"}
                )
                
                if recommendations_response.status_code == 200:
                    recommendations = recommendations_response.json()
                    assert len(recommendations) > 0
                    # Verify recommendations match user skills
                    recommended_jobs = recommendations.get("items", recommendations.get("jobs", []))
                    if recommended_jobs:
                        job_titles = [job["title"] for job in recommended_jobs]
                        assert any("Python" in title for title in job_titles)

    @pytest.mark.asyncio
    async def test_job_notification_integration(self, client, db_mock):
        """Test job notification system integration."""
        
        # Mock notification service
        with patch('backend.services.notification_service.send_notification') as mock_send_notification:
            mock_send_notification.return_value = True
            
            # Test job alert creation
            with patch('backend.routes.jobs.get_database', return_value=db_mock):
                db_mock.user_activities.insert_one.return_value = MagicMock(inserted_id=str(ObjectId()))
                
                alert_response = client.post(
                    "/api/v1/jobs/alerts",
                    json={
                        "keywords": ["Python", "Remote"],
                        "location": "Remote",
                        "job_type": "Full-time"
                    },
                    headers={"Authorization": f"Bearer test_token"}
                )
                
                # Should create job alert
                assert alert_response.status_code in [200, 201]
                
            # Test notification when new matching job is posted
            with patch('backend.routes.jobs.get_database', return_value=db_mock):
                db_mock.jobs.insert_one.return_value = MagicMock(inserted_id=str(ObjectId()))
                
                # Create a job that matches the alert
                new_job_data = {
                    **test_job_data,
                    "_id": str(ObjectId()),
                    "title": "Python Developer - Remote",
                    "location": "Remote",
                    "job_type": "Full-time"
                }
                
                job_response = client.post(
                    "/api/v1/jobs",
                    json={
                        "title": new_job_data["title"],
                        "company": new_job_data["company"],
                        "location": new_job_data["location"],
                        "description": new_job_data["description"],
                        "job_type": new_job_data["job_type"]
                    },
                    headers={"Authorization": f"Bearer test_token"}
                )
                
                assert job_response.status_code in [200, 201]
                
                # Verify notification was sent
                mock_send_notification.assert_called()

    @pytest.mark.asyncio
    async def test_job_analytics_integration(self, client, db_mock):
        """Test job analytics and reporting integration."""
        
        # Create test data for analytics
        analytics_data = {
            "total_jobs": 100,
            "active_jobs": 85,
            "applications_received": 250,
            "top_companies": [
                {"name": "TechCorp", "job_count": 15},
                {"name": "StartupCorp", "job_count": 12},
                {"name": "BigCorp", "job_count": 10}
            ],
            "popular_skills": [
                {"skill": "Python", "count": 45},
                {"skill": "JavaScript", "count": 38},
                {"skill": "React", "count": 32}
            ]
        }
        
        with patch('backend.routes.jobs.get_database', return_value=db_mock):
            # Mock analytics aggregation
            db_mock.jobs.aggregate.return_value.to_list.return_value = [
                {"_id": "total", "count": analytics_data["total_jobs"]},
                {"_id": "active", "count": analytics_data["active_jobs"]}
            ]
            
            # Test analytics endpoint
            analytics_response = client.get("/api/v1/jobs/analytics")
            
            if analytics_response.status_code == 200:
                analytics = analytics_response.json()
                assert "total_jobs" in analytics or "stats" in analytics
                
            # Test company analytics
            db_mock.jobs.aggregate.return_value.to_list.return_value = analytics_data["top_companies"]
            
            company_analytics_response = client.get("/api/v1/jobs/analytics/companies")
            
            if company_analytics_response.status_code == 200:
                company_stats = company_analytics_response.json()
                assert len(company_stats) > 0

    @pytest.mark.asyncio
    async def test_job_data_consistency_integration(self, client, db_mock):
        """Test data consistency across different endpoints."""
        
        # Create a job
        with patch('backend.routes.jobs.get_database', return_value=db_mock):
            db_mock.jobs.insert_one.return_value = MagicMock(inserted_id=test_job_data["_id"])
            db_mock.jobs.find_one.return_value = test_job_data
            
            create_response = client.post(
                "/api/v1/jobs",
                json={
                    "title": test_job_data["title"],
                    "company": test_job_data["company"],
                    "location": test_job_data["location"],
                    "description": test_job_data["description"]
                },
                headers={"Authorization": f"Bearer test_token"}
            )
            
            assert create_response.status_code in [200, 201]
            created_job = create_response.json()
            job_id = created_job["_id"]
            
        # Verify job appears in list
        with patch('backend.routes.jobs.get_database', return_value=db_mock):
            db_mock.jobs.find.return_value.to_list.return_value = [test_job_data]
            db_mock.jobs.count_documents.return_value = 1
            
            list_response = client.get("/api/v1/jobs")
            assert list_response.status_code == 200
            jobs = list_response.json().get("items", list_response.json().get("jobs", []))
            assert len(jobs) > 0
            assert jobs[0]["_id"] == job_id
            
        # Verify job details match
        with patch('backend.routes.jobs.get_database', return_value=db_mock):
            db_mock.jobs.find_one.return_value = test_job_data
            
            detail_response = client.get(f"/api/v1/jobs/{job_id}")
            assert detail_response.status_code == 200
            job_detail = detail_response.json()
            
            # Verify consistency
            assert job_detail["title"] == created_job["title"]
            assert job_detail["company"] == created_job["company"]
            assert job_detail["location"] == created_job["location"]

    @pytest.mark.asyncio
    async def test_error_handling_integration(self, client, db_mock):
        """Test error handling across the job workflow."""
        
        # Test database connection failure
        with patch('backend.routes.jobs.get_database', side_effect=Exception("Database connection failed")):
            response = client.get("/api/v1/jobs")
            assert response.status_code in [500, 503]
            
        # Test invalid job ID format
        invalid_ids = ["invalid-id", "123", "", "not-an-object-id"]
        
        for invalid_id in invalid_ids:
            response = client.get(f"/api/v1/jobs/{invalid_id}")
            assert response.status_code in [400, 404, 422]
            
        # Test unauthorized access
        response = client.post(
            "/api/v1/jobs",
            json={
                "title": "Unauthorized Job",
                "company": "Test Company",
                "location": "Remote",
                "description": "This should fail"
            }
        )
        assert response.status_code in [401, 403]
        
        # Test malformed request data
        response = client.post(
            "/api/v1/jobs",
            data="invalid json",
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code in [400, 422]

    @pytest.mark.asyncio
    async def test_performance_integration(self, client, db_mock):
        """Test performance characteristics of the job workflow."""
        
        import time
        
        # Test response time for job listing
        with patch('backend.routes.jobs.get_database', return_value=db_mock):
            db_mock.jobs.find.return_value.to_list.return_value = [test_job_data]
            db_mock.jobs.count_documents.return_value = 1
            
            start_time = time.time()
            response = client.get("/api/v1/jobs")
            end_time = time.time()
            
            response_time = end_time - start_time
            assert response.status_code == 200
            assert response_time < 2.0  # Should respond within 2 seconds
            
        # Test concurrent job creation
        import threading
        
        responses = []
        errors = []
        
        def create_job():
            try:
                with patch('backend.routes.jobs.get_database', return_value=db_mock):
                    db_mock.jobs.insert_one.return_value = MagicMock(inserted_id=str(ObjectId()))
                    response = client.post(
                        "/api/v1/jobs",
                        json={
                            "title": f"Concurrent Job {threading.current_thread().name}",
                            "company": "Test Company",
                            "location": "Remote",
                            "description": "Test description"
                        },
                        headers={"Authorization": f"Bearer test_token"}
                    )
                    responses.append(response.status_code)
            except Exception as e:
                errors.append(str(e))
        
        # Start multiple threads
        threads = []
        for i in range(3):
            thread = threading.Thread(target=create_job)
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # All requests should succeed
        assert len(errors) == 0
        assert all(status in [200, 201] for status in responses)