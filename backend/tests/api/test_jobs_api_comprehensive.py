import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock, MagicMock
import json
from datetime import datetime, timedelta
from bson import ObjectId

# Test data
sample_jobs = [
    {
        "_id": str(ObjectId()),
        "title": "Senior Python Developer",
        "company": "TechCorp",
        "location": "Remote",
        "description": "We are looking for a senior Python developer...",
        "salary_range": "$80,000 - $120,000",
        "job_type": "Full-time",
        "experience_level": "Senior",
        "skills": ["Python", "Django", "PostgreSQL"],
        "is_active": True,
        "created_at": datetime.utcnow(),
        "source": "internal",
        "url": "https://example.com/job1",
        "apply_url": "https://example.com/apply1"
    },
    {
        "_id": str(ObjectId()),
        "title": "Frontend Developer",
        "company": "StartupCorp",
        "location": "New York",
        "description": "Join our team as a frontend developer...",
        "salary_range": "$70,000 - $90,000",
        "job_type": "Full-time",
        "experience_level": "Mid-level",
        "skills": ["React", "JavaScript", "TypeScript"],
        "is_active": True,
        "created_at": datetime.utcnow(),
        "source": "external",
        "url": "https://example.com/job2",
        "apply_url": "https://example.com/apply2"
    },
    {
        "_id": str(ObjectId()),
        "title": "DevOps Engineer",
        "company": "BigCorp",
        "location": "San Francisco",
        "description": "We need a DevOps engineer to help us scale...",
        "salary_range": "$100,000 - $140,000",
        "job_type": "Full-time",
        "experience_level": "Senior",
        "skills": ["Docker", "Kubernetes", "AWS"],
        "is_active": False,
        "created_at": datetime.utcnow(),
        "source": "internal",
        "url": "https://example.com/job3",
        "apply_url": "https://example.com/apply3"
    }
]

@pytest.mark.api
class TestJobsAPIEndpoints:
    """Comprehensive tests for jobs API endpoints."""

    def test_get_jobs_list_success(self, client, db_mock):
        """Test successful retrieval of jobs list."""
        # Mock database response
        db_mock.jobs.find.return_value.to_list.return_value = sample_jobs
        db_mock.jobs.count_documents.return_value = len(sample_jobs)
        
        with patch('backend.routes.jobs.get_database', return_value=db_mock):
            response = client.get("/api/v1/jobs")
            
        assert response.status_code == 200
        data = response.json()
        assert "items" in data or "jobs" in data
        assert "total" in data
        assert "page" in data
        assert "limit" in data
        
        # Verify job data structure
        jobs = data.get("items", data.get("jobs", []))
        if jobs:
            job = jobs[0]
            required_fields = ["title", "company", "location", "description"]
            for field in required_fields:
                assert field in job

    def test_get_jobs_with_pagination(self, client, db_mock):
        """Test jobs list with pagination parameters."""
        # Mock database response
        db_mock.jobs.find.return_value.skip.return_value.limit.return_value.to_list.return_value = sample_jobs[:2]
        db_mock.jobs.count_documents.return_value = len(sample_jobs)
        
        with patch('backend.routes.jobs.get_database', return_value=db_mock):
            response = client.get("/api/v1/jobs?page=1&limit=2")
            
        assert response.status_code == 200
        data = response.json()
        assert data["page"] == 1
        assert data["limit"] == 2
        assert data["total"] == len(sample_jobs)

    def test_get_jobs_with_filters(self, client, db_mock):
        """Test jobs list with various filters."""
        # Mock database response for filtered results
        filtered_jobs = [job for job in sample_jobs if job["location"] == "Remote"]
        db_mock.jobs.find.return_value.to_list.return_value = filtered_jobs
        db_mock.jobs.count_documents.return_value = len(filtered_jobs)
        
        with patch('backend.routes.jobs.get_database', return_value=db_mock):
            response = client.get("/api/v1/jobs?location=Remote")
            
        assert response.status_code == 200
        data = response.json()
        jobs = data.get("items", data.get("jobs", []))
        assert len(jobs) == len(filtered_jobs)

    def test_get_jobs_with_search(self, client, db_mock):
        """Test jobs list with search parameter."""
        # Mock database response for search results
        search_results = [job for job in sample_jobs if "Python" in job["title"]]
        db_mock.jobs.find.return_value.to_list.return_value = search_results
        db_mock.jobs.count_documents.return_value = len(search_results)
        
        with patch('backend.routes.jobs.get_database', return_value=db_mock):
            response = client.get("/api/v1/jobs?search=Python")
            
        assert response.status_code == 200
        data = response.json()
        jobs = data.get("items", data.get("jobs", []))
        assert len(jobs) == len(search_results)

    def test_get_job_by_id_success(self, client, db_mock):
        """Test successful retrieval of a specific job."""
        job_id = sample_jobs[0]["_id"]
        db_mock.jobs.find_one.return_value = sample_jobs[0]
        
        with patch('backend.routes.jobs.get_database', return_value=db_mock):
            response = client.get(f"/api/v1/jobs/{job_id}")
            
        assert response.status_code == 200
        data = response.json()
        assert data["_id"] == job_id
        assert data["title"] == sample_jobs[0]["title"]
        assert data["company"] == sample_jobs[0]["company"]

    def test_get_job_by_id_not_found(self, client, db_mock):
        """Test job retrieval with non-existent ID."""
        job_id = str(ObjectId())
        db_mock.jobs.find_one.return_value = None
        
        with patch('backend.routes.jobs.get_database', return_value=db_mock):
            response = client.get(f"/api/v1/jobs/{job_id}")
            
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data

    def test_get_job_by_id_invalid_format(self, client):
        """Test job retrieval with invalid ID format."""
        invalid_ids = ["invalid-id", "123", "", "not-an-object-id"]
        
        for invalid_id in invalid_ids:
            response = client.get(f"/api/v1/jobs/{invalid_id}")
            assert response.status_code in [400, 404, 422]

    def test_create_job_success(self, client, db_mock, auth_headers):
        """Test successful job creation."""
        new_job_data = {
            "title": "New Job Position",
            "company": "New Company",
            "location": "Remote",
            "description": "This is a new job position",
            "salary_range": "$60,000 - $80,000",
            "job_type": "Full-time",
            "experience_level": "Mid-level",
            "skills": ["Python", "FastAPI"],
            "url": "https://example.com/new-job",
            "apply_url": "https://example.com/apply-new"
        }
        
        # Mock database operations
        db_mock.jobs.insert_one.return_value = MagicMock(inserted_id=str(ObjectId()))
        db_mock.jobs.find_one.return_value = {**new_job_data, "_id": str(ObjectId())}
        
        with patch('backend.routes.jobs.get_database', return_value=db_mock):
            response = client.post(
                "/api/v1/jobs",
                json=new_job_data,
                headers=auth_headers
            )
            
        assert response.status_code in [200, 201]
        data = response.json()
        assert data["title"] == new_job_data["title"]
        assert data["company"] == new_job_data["company"]

    def test_create_job_missing_required_fields(self, client, auth_headers):
        """Test job creation with missing required fields."""
        incomplete_job_data = {
            "title": "Incomplete Job",
            # Missing company, location, description
        }
        
        response = client.post(
            "/api/v1/jobs",
            json=incomplete_job_data,
            headers=auth_headers
        )
        
        assert response.status_code in [400, 422]

    def test_create_job_unauthorized(self, client):
        """Test job creation without authentication."""
        job_data = {
            "title": "Unauthorized Job",
            "company": "Test Company",
            "location": "Remote",
            "description": "This should fail"
        }
        
        response = client.post("/api/v1/jobs", json=job_data)
        assert response.status_code in [401, 403]

    def test_update_job_success(self, client, db_mock, auth_headers):
        """Test successful job update."""
        job_id = sample_jobs[0]["_id"]
        update_data = {
            "title": "Updated Job Title",
            "salary_range": "$90,000 - $110,000"
        }
        
        # Mock database operations
        db_mock.jobs.update_one.return_value = MagicMock(modified_count=1)
        updated_job = {**sample_jobs[0], **update_data}
        db_mock.jobs.find_one.return_value = updated_job
        
        with patch('backend.routes.jobs.get_database', return_value=db_mock):
            response = client.put(
                f"/api/v1/jobs/{job_id}",
                json=update_data,
                headers=auth_headers
            )
            
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == update_data["title"]
        assert data["salary_range"] == update_data["salary_range"]

    def test_update_job_not_found(self, client, db_mock, auth_headers):
        """Test job update with non-existent ID."""
        job_id = str(ObjectId())
        update_data = {"title": "Updated Title"}
        
        # Mock database response - job not found
        db_mock.jobs.update_one.return_value = MagicMock(modified_count=0)
        
        with patch('backend.routes.jobs.get_database', return_value=db_mock):
            response = client.put(
                f"/api/v1/jobs/{job_id}",
                json=update_data,
                headers=auth_headers
            )
            
        assert response.status_code == 404

    def test_delete_job_success(self, client, db_mock, auth_headers):
        """Test successful job deletion."""
        job_id = sample_jobs[0]["_id"]
        
        # Mock database operations
        db_mock.jobs.delete_one.return_value = MagicMock(deleted_count=1)
        
        with patch('backend.routes.jobs.get_database', return_value=db_mock):
            response = client.delete(
                f"/api/v1/jobs/{job_id}",
                headers=auth_headers
            )
            
        assert response.status_code in [200, 204]

    def test_delete_job_not_found(self, client, db_mock, auth_headers):
        """Test job deletion with non-existent ID."""
        job_id = str(ObjectId())
        
        # Mock database response - job not found
        db_mock.jobs.delete_one.return_value = MagicMock(deleted_count=0)
        
        with patch('backend.routes.jobs.get_database', return_value=db_mock):
            response = client.delete(
                f"/api/v1/jobs/{job_id}",
                headers=auth_headers
            )
            
        assert response.status_code == 404

@pytest.mark.api
class TestJobsAPISearchAndFiltering:
    """Test advanced search and filtering functionality."""

    def test_search_jobs_by_title(self, client, db_mock):
        """Test searching jobs by title."""
        search_term = "Python"
        search_results = [job for job in sample_jobs if search_term.lower() in job["title"].lower()]
        
        db_mock.jobs.find.return_value.to_list.return_value = search_results
        db_mock.jobs.count_documents.return_value = len(search_results)
        
        with patch('backend.routes.jobs.get_database', return_value=db_mock):
            response = client.get(f"/api/v1/jobs?search={search_term}")
            
        assert response.status_code == 200
        data = response.json()
        jobs = data.get("items", data.get("jobs", []))
        assert len(jobs) == len(search_results)

    def test_filter_jobs_by_company(self, client, db_mock):
        """Test filtering jobs by company."""
        company = "TechCorp"
        filtered_jobs = [job for job in sample_jobs if job["company"] == company]
        
        db_mock.jobs.find.return_value.to_list.return_value = filtered_jobs
        db_mock.jobs.count_documents.return_value = len(filtered_jobs)
        
        with patch('backend.routes.jobs.get_database', return_value=db_mock):
            response = client.get(f"/api/v1/jobs?company={company}")
            
        assert response.status_code == 200
        data = response.json()
        jobs = data.get("items", data.get("jobs", []))
        assert len(jobs) == len(filtered_jobs)

    def test_filter_jobs_by_location(self, client, db_mock):
        """Test filtering jobs by location."""
        location = "Remote"
        filtered_jobs = [job for job in sample_jobs if job["location"] == location]
        
        db_mock.jobs.find.return_value.to_list.return_value = filtered_jobs
        db_mock.jobs.count_documents.return_value = len(filtered_jobs)
        
        with patch('backend.routes.jobs.get_database', return_value=db_mock):
            response = client.get(f"/api/v1/jobs?location={location}")
            
        assert response.status_code == 200
        data = response.json()
        jobs = data.get("items", data.get("jobs", []))
        assert len(jobs) == len(filtered_jobs)

    def test_filter_jobs_by_job_type(self, client, db_mock):
        """Test filtering jobs by job type."""
        job_type = "Full-time"
        filtered_jobs = [job for job in sample_jobs if job["job_type"] == job_type]
        
        db_mock.jobs.find.return_value.to_list.return_value = filtered_jobs
        db_mock.jobs.count_documents.return_value = len(filtered_jobs)
        
        with patch('backend.routes.jobs.get_database', return_value=db_mock):
            response = client.get(f"/api/v1/jobs?job_type={job_type}")
            
        assert response.status_code == 200
        data = response.json()
        jobs = data.get("items", data.get("jobs", []))
        assert len(jobs) == len(filtered_jobs)

    def test_filter_jobs_by_experience_level(self, client, db_mock):
        """Test filtering jobs by experience level."""
        experience_level = "Senior"
        filtered_jobs = [job for job in sample_jobs if job["experience_level"] == experience_level]
        
        db_mock.jobs.find.return_value.to_list.return_value = filtered_jobs
        db_mock.jobs.count_documents.return_value = len(filtered_jobs)
        
        with patch('backend.routes.jobs.get_database', return_value=db_mock):
            response = client.get(f"/api/v1/jobs?experience_level={experience_level}")
            
        assert response.status_code == 200
        data = response.json()
        jobs = data.get("items", data.get("jobs", []))
        assert len(jobs) == len(filtered_jobs)

    def test_filter_jobs_by_salary_range(self, client, db_mock):
        """Test filtering jobs by salary range."""
        min_salary = 80000
        max_salary = 120000
        
        # Mock filtered results
        filtered_jobs = [job for job in sample_jobs if job["salary_range"]]
        db_mock.jobs.find.return_value.to_list.return_value = filtered_jobs
        db_mock.jobs.count_documents.return_value = len(filtered_jobs)
        
        with patch('backend.routes.jobs.get_database', return_value=db_mock):
            response = client.get(f"/api/v1/jobs?min_salary={min_salary}&max_salary={max_salary}")
            
        assert response.status_code == 200
        data = response.json()
        jobs = data.get("items", data.get("jobs", []))
        assert len(jobs) == len(filtered_jobs)

    def test_multiple_filters_combined(self, client, db_mock):
        """Test combining multiple filters."""
        # Mock filtered results for multiple criteria
        filtered_jobs = [job for job in sample_jobs if 
                        job["location"] == "Remote" and 
                        job["job_type"] == "Full-time"]
        
        db_mock.jobs.find.return_value.to_list.return_value = filtered_jobs
        db_mock.jobs.count_documents.return_value = len(filtered_jobs)
        
        with patch('backend.routes.jobs.get_database', return_value=db_mock):
            response = client.get("/api/v1/jobs?location=Remote&job_type=Full-time")
            
        assert response.status_code == 200
        data = response.json()
        jobs = data.get("items", data.get("jobs", []))
        assert len(jobs) == len(filtered_jobs)

@pytest.mark.api
class TestJobsAPISorting:
    """Test job sorting functionality."""

    def test_sort_jobs_by_date_created(self, client, db_mock):
        """Test sorting jobs by creation date."""
        # Mock sorted results
        sorted_jobs = sorted(sample_jobs, key=lambda x: x["created_at"], reverse=True)
        
        db_mock.jobs.find.return_value.sort.return_value.to_list.return_value = sorted_jobs
        db_mock.jobs.count_documents.return_value = len(sorted_jobs)
        
        with patch('backend.routes.jobs.get_database', return_value=db_mock):
            response = client.get("/api/v1/jobs?sort=created_at&order=desc")
            
        assert response.status_code == 200
        data = response.json()
        jobs = data.get("items", data.get("jobs", []))
        assert len(jobs) == len(sorted_jobs)

    def test_sort_jobs_by_title(self, client, db_mock):
        """Test sorting jobs by title."""
        # Mock sorted results
        sorted_jobs = sorted(sample_jobs, key=lambda x: x["title"])
        
        db_mock.jobs.find.return_value.sort.return_value.to_list.return_value = sorted_jobs
        db_mock.jobs.count_documents.return_value = len(sorted_jobs)
        
        with patch('backend.routes.jobs.get_database', return_value=db_mock):
            response = client.get("/api/v1/jobs?sort=title&order=asc")
            
        assert response.status_code == 200
        data = response.json()
        jobs = data.get("items", data.get("jobs", []))
        assert len(jobs) == len(sorted_jobs)

    def test_sort_jobs_by_company(self, client, db_mock):
        """Test sorting jobs by company."""
        # Mock sorted results
        sorted_jobs = sorted(sample_jobs, key=lambda x: x["company"])
        
        db_mock.jobs.find.return_value.sort.return_value.to_list.return_value = sorted_jobs
        db_mock.jobs.count_documents.return_value = len(sorted_jobs)
        
        with patch('backend.routes.jobs.get_database', return_value=db_mock):
            response = client.get("/api/v1/jobs?sort=company&order=asc")
            
        assert response.status_code == 200
        data = response.json()
        jobs = data.get("items", data.get("jobs", []))
        assert len(jobs) == len(sorted_jobs)

    def test_invalid_sort_field(self, client, db_mock):
        """Test sorting with invalid field."""
        db_mock.jobs.find.return_value.sort.return_value.to_list.return_value = sample_jobs
        db_mock.jobs.count_documents.return_value = len(sample_jobs)
        
        with patch('backend.routes.jobs.get_database', return_value=db_mock):
            response = client.get("/api/v1/jobs?sort=invalid_field")
            
        # Should either return 400/422 or ignore invalid sort field
        assert response.status_code in [200, 400, 422]

@pytest.mark.api
class TestJobsAPIErrorHandling:
    """Test error handling in jobs API."""

    def test_invalid_pagination_parameters(self, client):
        """Test invalid pagination parameters."""
        invalid_params = [
            "?page=-1",
            "?limit=0",
            "?page=abc",
            "?limit=invalid"
        ]
        
        for param in invalid_params:
            response = client.get(f"/api/v1/jobs{param}")
            assert response.status_code in [400, 422]

    def test_large_pagination_limit(self, client):
        """Test pagination with very large limit."""
        response = client.get("/api/v1/jobs?limit=10000")
        # Should either return 400/422 or cap the limit
        assert response.status_code in [200, 400, 422]

    def test_malformed_json_request(self, client, auth_headers):
        """Test malformed JSON in request body."""
        response = client.post(
            "/api/v1/jobs",
            data="invalid json",
            headers={**auth_headers, "Content-Type": "application/json"}
        )
        assert response.status_code in [400, 422]

    def test_missing_content_type(self, client, auth_headers):
        """Test request without content type header."""
        job_data = {"title": "Test Job", "company": "Test Company"}
        response = client.post("/api/v1/jobs", data=job_data, headers=auth_headers)
        # Should handle gracefully
        assert response.status_code in [200, 201, 400, 422]

    def test_large_request_body(self, client, auth_headers):
        """Test request with very large body."""
        large_description = "x" * 10000
        job_data = {
            "title": "Test Job",
            "company": "Test Company",
            "location": "Remote",
            "description": large_description
        }
        
        response = client.post("/api/v1/jobs", json=job_data, headers=auth_headers)
        # Should either accept or reject based on size limits
        assert response.status_code in [200, 201, 400, 413, 422]

@pytest.mark.api
class TestJobsAPISecurity:
    """Test security aspects of jobs API."""

    def test_sql_injection_protection(self, client):
        """Test protection against SQL injection attempts."""
        malicious_inputs = [
            "'; DROP TABLE jobs; --",
            "' OR '1'='1",
            "'; DELETE FROM jobs; --",
            "admin'--",
            "1' OR '1' = '1' --",
        ]
        
        for malicious_input in malicious_inputs:
            response = client.get(f"/api/v1/jobs?search={malicious_input}")
            # Should handle safely without errors
            assert response.status_code in [200, 400, 422]

    def test_xss_protection(self, client, auth_headers):
        """Test protection against XSS attacks."""
        xss_payload = "<script>alert('xss')</script>"
        job_data = {
            "title": xss_payload,
            "company": "Test Company",
            "location": "Remote",
            "description": "Test description"
        }
        
        response = client.post("/api/v1/jobs", json=job_data, headers=auth_headers)
        # Should either sanitize or reject
        assert response.status_code in [200, 201, 400, 422]

    def test_special_characters_handling(self, client):
        """Test handling of special characters in search/filter."""
        special_chars = [
            "test@example.com",
            "user+name",
            "file/path",
            "query?param=value",
            "text with spaces",
            "text with 'quotes'",
            'text with "double quotes"',
        ]
        
        for chars in special_chars:
            response = client.get(f"/api/v1/jobs?search={chars}")
            # Should handle gracefully
            assert response.status_code in [200, 400, 422]

@pytest.mark.api
class TestJobsAPIPerformance:
    """Test performance aspects of jobs API."""

    def test_response_time_acceptable(self, client, db_mock):
        """Test that response time is within acceptable limits."""
        import time
        
        db_mock.jobs.find.return_value.to_list.return_value = sample_jobs
        db_mock.jobs.count_documents.return_value = len(sample_jobs)
        
        with patch('backend.routes.jobs.get_database', return_value=db_mock):
            start_time = time.time()
            response = client.get("/api/v1/jobs")
            end_time = time.time()
            
        response_time = end_time - start_time
        assert response.status_code == 200
        assert response_time < 2.0  # Should respond within 2 seconds

    def test_large_dataset_handling(self, client, db_mock):
        """Test handling of large datasets."""
        # Mock large dataset
        large_jobs_list = sample_jobs * 100  # 300 jobs
        db_mock.jobs.find.return_value.to_list.return_value = large_jobs_list
        db_mock.jobs.count_documents.return_value = len(large_jobs_list)
        
        with patch('backend.routes.jobs.get_database', return_value=db_mock):
            response = client.get("/api/v1/jobs?limit=50")
            
        assert response.status_code == 200
        data = response.json()
        jobs = data.get("items", data.get("jobs", []))
        assert len(jobs) <= 50  # Should respect limit

    def test_concurrent_requests(self, client, db_mock):
        """Test handling of concurrent requests."""
        import threading
        import time
        
        db_mock.jobs.find.return_value.to_list.return_value = sample_jobs
        db_mock.jobs.count_documents.return_value = len(sample_jobs)
        
        responses = []
        errors = []
        
        def make_request():
            try:
                with patch('backend.routes.jobs.get_database', return_value=db_mock):
                    response = client.get("/api/v1/jobs")
                    responses.append(response.status_code)
            except Exception as e:
                errors.append(str(e))
        
        # Start multiple threads
        threads = []
        for _ in range(5):
            thread = threading.Thread(target=make_request)
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # All requests should succeed
        assert len(errors) == 0
        assert all(status == 200 for status in responses)