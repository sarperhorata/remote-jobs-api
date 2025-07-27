import json
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from bson import ObjectId
from fastapi.testclient import TestClient


class TestJobsComprehensive:
    """Comprehensive tests for jobs routes to increase coverage"""

    def test_create_job_success(self, client: TestClient):
        """Test successful job creation"""
        job_data = {
            "title": "Senior Python Developer",
            "company": "Tech Corp",
            "location": "Remote",
            "description": "We are looking for a senior Python developer",
            "salary_min": 80000,
            "salary_max": 120000,
            "job_type": "Full-time",
            "isRemote": True,
        }

        with patch("backend.routes.jobs.get_async_db") as mock_db:
            mock_db.return_value.jobs.insert_one.return_value.inserted_id = ObjectId()
            mock_db.return_value.jobs.find_one.return_value = {
                "_id": ObjectId(),
                **job_data,
            }

            response = client.post("/api/v1/jobs/", json=job_data)

            assert response.status_code == 201
            data = response.json()
            assert data["title"] == job_data["title"]
            assert data["company"] == job_data["company"]

    def test_create_job_invalid_data(self, client: TestClient):
        """Test job creation with invalid data"""
        invalid_job_data = {"title": "", "company": "Tech Corp"}  # Empty title

        response = client.post("/api/v1/jobs/", json=invalid_job_data)
        assert response.status_code in [400, 422]

    def test_read_jobs_pagination(self, client: TestClient):
        """Test jobs listing with pagination"""
        mock_jobs = [
            {"_id": str(ObjectId()), "title": f"Job {i}", "company": f"Company {i}"}
            for i in range(5)
        ]

        with patch("backend.routes.jobs.get_async_db") as mock_db:
            mock_db.return_value.jobs.find.return_value.skip.return_value.limit.return_value.to_list.return_value = (
                mock_jobs
            )
            mock_db.return_value.jobs.count_documents.return_value = 100

            response = client.get("/api/v1/jobs/?skip=0&limit=5")

            assert response.status_code == 200
            data = response.json()
            assert len(data["items"]) == 5
            assert data["total"] == 100
            assert data["page"] == 1

    def test_search_jobs_basic_query(self, client: TestClient):
        """Test basic job search functionality"""
        mock_jobs = [
            {
                "_id": str(ObjectId()),
                "title": "Python Developer",
                "company": "Tech Corp",
            }
        ]

        with patch("backend.routes.jobs.get_async_db") as mock_db:
            mock_db.return_value.jobs.find.return_value.skip.return_value.limit.return_value.to_list.return_value = (
                mock_jobs
            )
            mock_db.return_value.jobs.count_documents.return_value = 1

            response = client.get("/api/v1/jobs/search?q=python")

            assert response.status_code == 200
            data = response.json()
            assert len(data["jobs"]) == 1
            assert "Python" in data["jobs"][0]["title"]

    def test_search_jobs_remote_filter(self, client: TestClient):
        """Test job search with remote work filter"""
        mock_jobs = [
            {"_id": str(ObjectId()), "title": "Remote Developer", "isRemote": True}
        ]

        with patch("backend.routes.jobs.get_async_db") as mock_db:
            mock_db.return_value.jobs.find.return_value.skip.return_value.limit.return_value.to_list.return_value = (
                mock_jobs
            )
            mock_db.return_value.jobs.count_documents.return_value = 1

            response = client.get("/api/v1/jobs/search?work_type=remote")

            assert response.status_code == 200
            data = response.json()
            assert len(data["jobs"]) == 1

    def test_search_jobs_salary_filter(self, client: TestClient):
        """Test job search with salary range filter"""
        mock_jobs = [
            {"_id": str(ObjectId()), "title": "High Salary Job", "salary_min": 100000}
        ]

        with patch("backend.routes.jobs.get_async_db") as mock_db:
            mock_db.return_value.jobs.find.return_value.skip.return_value.limit.return_value.to_list.return_value = (
                mock_jobs
            )
            mock_db.return_value.jobs.count_documents.return_value = 1

            response = client.get("/api/v1/jobs/search?salary_range=100000+")

            assert response.status_code == 200
            data = response.json()
            assert len(data["jobs"]) == 1

    def test_search_jobs_experience_filter(self, client: TestClient):
        """Test job search with experience level filter"""
        mock_jobs = [
            {
                "_id": str(ObjectId()),
                "title": "Senior Developer",
                "experience_level": "senior",
            }
        ]

        with patch("backend.routes.jobs.get_async_db") as mock_db:
            mock_db.return_value.jobs.find.return_value.skip.return_value.limit.return_value.to_list.return_value = (
                mock_jobs
            )
            mock_db.return_value.jobs.count_documents.return_value = 1

            response = client.get("/api/v1/jobs/search?experience=senior")

            assert response.status_code == 200
            data = response.json()
            assert len(data["jobs"]) == 1

    def test_search_jobs_grouped(self, client: TestClient):
        """Test grouped job search functionality"""
        mock_jobs = [
            {
                "_id": str(ObjectId()),
                "title": "Python Developer",
                "company": "Tech Corp",
            },
            {
                "_id": str(ObjectId()),
                "title": "Python Developer",
                "company": "Another Corp",
            },
        ]

        with patch("backend.routes.jobs.get_async_db") as mock_db:
            mock_db.return_value.jobs.find.return_value.limit.return_value.to_list.return_value = (
                mock_jobs
            )

            response = client.get("/api/v1/jobs/search/grouped?q=python")

            assert response.status_code == 200
            data = response.json()
            assert "grouped_results" in data

    def test_update_job_success(self, client: TestClient):
        """Test successful job update"""
        job_id = str(ObjectId())
        update_data = {"title": "Updated Job Title", "salary_max": 150000}

        with patch("backend.routes.jobs.get_async_db") as mock_db:
            mock_db.return_value.jobs.update_one.return_value.modified_count = 1
            mock_db.return_value.jobs.find_one.return_value = {
                "_id": ObjectId(job_id),
                **update_data,
            }

            response = client.put(f"/api/v1/jobs/{job_id}", json=update_data)

            assert response.status_code == 200
            data = response.json()
            assert data["title"] == update_data["title"]

    def test_update_job_not_found(self, client: TestClient):
        """Test job update when job doesn't exist"""
        job_id = str(ObjectId())
        update_data = {"title": "Updated Title"}

        with patch("backend.routes.jobs.get_async_db") as mock_db:
            mock_db.return_value.jobs.update_one.return_value.modified_count = 0

            response = client.put(f"/api/v1/jobs/{job_id}", json=update_data)

            assert response.status_code == 404

    def test_delete_job_success(self, client: TestClient):
        """Test successful job deletion"""
        job_id = str(ObjectId())

        with patch("backend.routes.jobs.get_async_db") as mock_db:
            mock_db.return_value.jobs.delete_one.return_value.deleted_count = 1

            response = client.delete(f"/api/v1/jobs/{job_id}")

            assert response.status_code == 204

    def test_delete_job_not_found(self, client: TestClient):
        """Test job deletion when job doesn't exist"""
        job_id = str(ObjectId())

        with patch("backend.routes.jobs.get_async_db") as mock_db:
            mock_db.return_value.jobs.delete_one.return_value.deleted_count = 0

            response = client.delete(f"/api/v1/jobs/{job_id}")

            assert response.status_code == 404

    def test_get_job_statistics(self, client: TestClient):
        """Test job statistics endpoint"""
        with patch("backend.routes.jobs.get_async_db") as mock_db:
            mock_db.return_value.jobs.count_documents.side_effect = [100, 50, 30, 20]
            mock_db.return_value.jobs.aggregate.return_value.to_list.return_value = [
                {"_id": "Remote", "count": 50},
                {"_id": "On-site", "count": 30},
            ]

            response = client.get("/api/v1/jobs/statistics")

            assert response.status_code == 200
            data = response.json()
            assert "total_jobs" in data
            assert "remote_jobs" in data
            assert "work_type_distribution" in data

    def test_search_job_titles(self, client: TestClient):
        """Test job titles search functionality"""
        mock_titles = [
            {"_id": "Python Developer", "count": 10},
            {"_id": "Python Engineer", "count": 5},
        ]

        with patch("backend.routes.jobs.get_async_db") as mock_db:
            mock_db.return_value.jobs.aggregate.return_value.to_list.return_value = (
                mock_titles
            )

            response = client.get("/api/v1/jobs/job-titles/search?q=python")

            assert response.status_code == 200
            data = response.json()
            assert len(data) == 2
            assert "Python" in data[0]["_id"]

    def test_search_companies(self, client: TestClient):
        """Test companies search functionality"""
        mock_companies = [
            {"_id": "Tech Corp", "count": 15},
            {"_id": "Tech Solutions", "count": 8},
        ]

        with patch("backend.routes.jobs.get_async_db") as mock_db:
            mock_db.return_value.jobs.aggregate.return_value.to_list.return_value = (
                mock_companies
            )

            response = client.get("/api/v1/jobs/companies/search?q=tech")

            assert response.status_code == 200
            data = response.json()
            assert len(data) == 2
            assert "Tech" in data[0]["_id"]

    def test_search_locations(self, client: TestClient):
        """Test locations search functionality"""
        mock_locations = [
            {"_id": "San Francisco", "count": 20},
            {"_id": "San Diego", "count": 12},
        ]

        with patch("backend.routes.jobs.get_async_db") as mock_db:
            mock_db.return_value.jobs.aggregate.return_value.to_list.return_value = (
                mock_locations
            )

            response = client.get("/api/v1/jobs/locations/search?q=san")

            assert response.status_code == 200
            data = response.json()
            assert len(data) == 2
            assert "San" in data[0]["_id"]

    def test_search_skills(self, client: TestClient):
        """Test skills search functionality"""
        response = client.get("/api/v1/jobs/skills/search?q=python")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_get_recent_jobs(self, client: TestClient):
        """Test recent jobs endpoint"""
        mock_jobs = [
            {
                "_id": str(ObjectId()),
                "title": "Recent Job",
                "created_at": datetime.now(),
            }
        ]

        with patch("backend.routes.jobs.get_async_db") as mock_db:
            mock_db.return_value.jobs.find.return_value.sort.return_value.limit.return_value.to_list.return_value = (
                mock_jobs
            )

            response = client.get("/api/v1/jobs/recent?limit=5")

            assert response.status_code == 200
            data = response.json()
            assert len(data) == 1

    def test_get_job_recommendations(self, client: TestClient):
        """Test job recommendations endpoint"""
        mock_jobs = [{"_id": str(ObjectId()), "title": "Recommended Job", "score": 0.9}]

        with patch("backend.routes.jobs.get_async_db") as mock_db:
            mock_db.return_value.jobs.find.return_value.sort.return_value.limit.return_value.to_list.return_value = (
                mock_jobs
            )

            response = client.get("/api/v1/jobs/recommendations?limit=5")

            assert response.status_code == 200
            data = response.json()
            assert len(data) == 1

    def test_get_jobs_with_filters(self, client: TestClient):
        """Test jobs endpoint with various filters"""
        mock_jobs = [
            {"_id": str(ObjectId()), "title": "Filtered Job", "company": "Test Corp"}
        ]

        with patch("backend.routes.jobs.get_async_db") as mock_db:
            mock_db.return_value.jobs.find.return_value.skip.return_value.limit.return_value.sort.return_value.to_list.return_value = (
                mock_jobs
            )
            mock_db.return_value.jobs.count_documents.return_value = 1

            response = client.get("/api/v1/jobs/?company=Test&sort_by=title")

            assert response.status_code == 200
            data = response.json()
            assert len(data["jobs"]) == 1

    def test_get_similar_jobs(self, client: TestClient, auth_headers):
        """Test similar jobs endpoint"""
        job_id = str(ObjectId())
        mock_jobs = [
            {"_id": str(ObjectId()), "title": "Similar Job", "similarity_score": 0.8}
        ]

        with patch("backend.routes.jobs.get_async_db") as mock_db:
            mock_db.return_value.jobs.find_one.return_value = {
                "_id": ObjectId(job_id),
                "title": "Original Job",
                "skills": ["Python", "Django"],
            }
            mock_db.return_value.jobs.find.return_value.limit.return_value.to_list.return_value = (
                mock_jobs
            )

            response = client.get(
                f"/api/v1/jobs/{job_id}/similar", headers=auth_headers
            )

            assert response.status_code == 200
            data = response.json()
            assert len(data) == 1

    def test_apply_for_job_success(self, client: TestClient, auth_headers):
        """Test successful job application"""
        job_id = str(ObjectId())

        with patch("backend.routes.jobs.get_async_db") as mock_db:
            mock_db.return_value.jobs.find_one.return_value = {
                "_id": ObjectId(job_id),
                "title": "Test Job",
            }
            mock_db.return_value.job_applications.insert_one.return_value.inserted_id = (
                ObjectId()
            )

            response = client.post(f"/api/v1/jobs/{job_id}/apply", headers=auth_headers)

            assert response.status_code == 201

    def test_apply_for_job_not_found(self, client: TestClient, auth_headers):
        """Test job application when job doesn't exist"""
        job_id = str(ObjectId())

        with patch("backend.routes.jobs.get_async_db") as mock_db:
            mock_db.return_value.jobs.find_one.return_value = None

            response = client.post(f"/api/v1/jobs/{job_id}/apply", headers=auth_headers)

            assert response.status_code == 404

    def test_save_job_success(self, client: TestClient, auth_headers):
        """Test successful job saving"""
        job_id = str(ObjectId())

        with patch("backend.routes.jobs.get_async_db") as mock_db:
            mock_db.return_value.jobs.find_one.return_value = {
                "_id": ObjectId(job_id),
                "title": "Test Job",
            }
            mock_db.return_value.users.update_one.return_value.modified_count = 1

            response = client.post(f"/api/v1/jobs/{job_id}/save", headers=auth_headers)

            assert response.status_code == 201

    def test_remove_saved_job(self, client: TestClient, auth_headers):
        """Test removing saved job"""
        job_id = str(ObjectId())

        with patch("backend.routes.jobs.get_async_db") as mock_db:
            mock_db.return_value.users.update_one.return_value.modified_count = 1

            response = client.delete(
                f"/api/v1/jobs/{job_id}/save", headers=auth_headers
            )

            assert response.status_code == 204

    def test_get_saved_jobs(self, client: TestClient, auth_headers):
        """Test getting saved jobs"""
        mock_jobs = [{"_id": str(ObjectId()), "title": "Saved Job"}]

        with patch("backend.routes.jobs.get_async_db") as mock_db:
            mock_db.return_value.users.find_one.return_value = {
                "saved_jobs": [ObjectId()]
            }
            mock_db.return_value.jobs.find.return_value.skip.return_value.limit.return_value.to_list.return_value = (
                mock_jobs
            )

            response = client.get("/api/v1/jobs/saved", headers=auth_headers)

            assert response.status_code == 200
            data = response.json()
            assert len(data) == 1

    def test_bookmark_job_success(self, client: TestClient, auth_headers):
        """Test successful job bookmarking"""
        job_id = str(ObjectId())

        with patch("backend.routes.jobs.get_async_db") as mock_db:
            mock_db.return_value.jobs.find_one.return_value = {
                "_id": ObjectId(job_id),
                "title": "Test Job",
            }
            mock_db.return_value.users.update_one.return_value.modified_count = 1

            response = client.post(
                f"/api/v1/jobs/{job_id}/bookmark", headers=auth_headers
            )

            assert response.status_code == 200

    def test_track_job_interaction(self, client: TestClient):
        """Test job interaction tracking"""
        job_id = str(ObjectId())
        tracking_data = {"interaction_type": "view", "duration": 30}

        with patch("backend.routes.jobs.get_async_db") as mock_db:
            mock_db.return_value.job_interactions.insert_one.return_value.inserted_id = (
                ObjectId()
            )

            response = client.post(f"/api/v1/jobs/{job_id}/track", json=tracking_data)

            assert response.status_code == 200

    def test_get_job_application_analytics(self, client: TestClient, auth_headers):
        """Test job application analytics"""
        job_id = str(ObjectId())

        with patch("backend.routes.jobs.get_async_db") as mock_db:
            mock_db.return_value.job_applications.count_documents.return_value = 10
            mock_db.return_value.job_applications.aggregate.return_value.to_list.return_value = [
                {"status": "applied", "count": 5},
                {"status": "interviewed", "count": 3},
            ]

            response = client.get(
                f"/api/v1/jobs/{job_id}/application-analytics", headers=auth_headers
            )

            assert response.status_code == 200
            data = response.json()
            assert "total_applications" in data
            assert "status_distribution" in data

    def test_get_job_by_id(self, client: TestClient):
        """Test getting job by ID"""
        job_id = str(ObjectId())
        mock_job = {
            "_id": ObjectId(job_id),
            "title": "Test Job",
            "company": "Test Corp",
            "location": "Remote",
        }

        with patch("backend.routes.jobs.get_async_db") as mock_db:
            mock_db.return_value.jobs.find_one.return_value = mock_job

            response = client.get(f"/api/v1/jobs/{job_id}")

            assert response.status_code == 200
            data = response.json()
            assert data["title"] == mock_job["title"]

    def test_get_job_by_id_not_found(self, client: TestClient):
        """Test getting job by ID when not found"""
        job_id = str(ObjectId())

        with patch("backend.routes.jobs.get_async_db") as mock_db:
            mock_db.return_value.jobs.find_one.return_value = None

            response = client.get(f"/api/v1/jobs/{job_id}")

            assert response.status_code == 404

    def test_clean_job_title(self, client: TestClient):
        """Test job title cleaning utility function"""
        from backend.routes.jobs import clean_job_title

        # Test various title formats
        assert clean_job_title("Senior Python Developer") == "Senior Python Developer"
        assert clean_job_title("  Python Developer  ") == "Python Developer"
        assert clean_job_title("Python Developer (Remote)") == "Python Developer"

    def test_normalize_job_title(self, client: TestClient):
        """Test job title normalization utility function"""
        from backend.routes.jobs import normalize_job_title

        # Test title normalization
        assert normalize_job_title("Python Developer") == "python developer"
        assert (
            normalize_job_title("SENIOR PYTHON DEVELOPER") == "senior python developer"
        )

    def test_group_job_titles(self, client: TestClient):
        """Test job title grouping utility function"""
        from backend.routes.jobs import group_job_titles

        jobs = [
            {"title": "Python Developer"},
            {"title": "Python Developer"},
            {"title": "Java Developer"},
        ]

        grouped = group_job_titles(jobs)
        assert "Python Developer" in grouped
        assert grouped["Python Developer"] == 2
        assert grouped["Java Developer"] == 1

    def test_search_jobs_invalid_pagination(self, client: TestClient):
        """Test job search with invalid pagination parameters"""
        response = client.get("/api/v1/jobs/search?page=0&limit=0")
        assert response.status_code in [400, 422]

    def test_search_jobs_large_limit(self, client: TestClient):
        """Test job search with limit exceeding maximum"""
        response = client.get("/api/v1/jobs/search?limit=10000")
        assert response.status_code in [400, 422]

    def test_search_jobs_complex_filters(self, client: TestClient):
        """Test job search with multiple complex filters"""
        mock_jobs = [
            {
                "_id": str(ObjectId()),
                "title": "Senior Python Developer",
                "isRemote": True,
            }
        ]

        with patch("backend.routes.jobs.get_async_db") as mock_db:
            mock_db.return_value.jobs.find.return_value.skip.return_value.limit.return_value.to_list.return_value = (
                mock_jobs
            )
            mock_db.return_value.jobs.count_documents.return_value = 1

            response = client.get(
                "/api/v1/jobs/search?q=python&work_type=remote&experience=senior&job_type=full-time&salary_range=80000-120000"
            )

            assert response.status_code == 200
            data = response.json()
            assert len(data["jobs"]) == 1

    def test_search_jobs_date_range_filter(self, client: TestClient):
        """Test job search with date range filter"""
        mock_jobs = [
            {
                "_id": str(ObjectId()),
                "title": "Recent Job",
                "posted_date": datetime.now(),
            }
        ]

        with patch("backend.routes.jobs.get_async_db") as mock_db:
            mock_db.return_value.jobs.find.return_value.skip.return_value.limit.return_value.to_list.return_value = (
                mock_jobs
            )
            mock_db.return_value.jobs.count_documents.return_value = 1

            response = client.get("/api/v1/jobs/search?posted_age=7d")

            assert response.status_code == 200
            data = response.json()
            assert len(data["jobs"]) == 1

    def test_search_jobs_sorting(self, client: TestClient):
        """Test job search with different sorting options"""
        mock_jobs = [
            {"_id": str(ObjectId()), "title": "Job 1", "salary_max": 100000},
            {"_id": str(ObjectId()), "title": "Job 2", "salary_max": 80000},
        ]

        with patch("backend.routes.jobs.get_async_db") as mock_db:
            mock_db.return_value.jobs.find.return_value.skip.return_value.limit.return_value.to_list.return_value = (
                mock_jobs
            )
            mock_db.return_value.jobs.count_documents.return_value = 2

            # Test salary sorting
            response = client.get("/api/v1/jobs/search?sort_by=salary")
            assert response.status_code == 200

            # Test relevance sorting
            response = client.get("/api/v1/jobs/search?sort_by=relevance")
            assert response.status_code == 200

    def test_search_jobs_empty_results(self, client: TestClient):
        """Test job search with no results"""
        with patch("backend.routes.jobs.get_async_db") as mock_db:
            mock_db.return_value.jobs.find.return_value.skip.return_value.limit.return_value.to_list.return_value = (
                []
            )
            mock_db.return_value.jobs.count_documents.return_value = 0

            response = client.get("/api/v1/jobs/search?q=nonexistent")

            assert response.status_code == 200
            data = response.json()
            assert len(data["jobs"]) == 0
            assert data["total"] == 0

    def test_search_jobs_error_handling(self, client: TestClient):
        """Test job search error handling"""
        with patch("backend.routes.jobs.get_async_db") as mock_db:
            mock_db.return_value.jobs.find.side_effect = Exception("Database error")

            response = client.get("/api/v1/jobs/search?q=python")

            assert response.status_code == 500

    def test_job_application_form_scraping(self, client: TestClient, auth_headers):
        """Test job application form scraping"""
        job_id = str(ObjectId())
        form_data = {
            "url": "https://example.com/apply",
            "form_fields": ["name", "email", "resume"],
        }

        with patch("backend.routes.jobs.get_async_db") as mock_db, patch(
            "backend.routes.jobs.JobScrapingService"
        ) as mock_scraper:
            mock_db.return_value.jobs.find_one.return_value = {
                "_id": ObjectId(job_id),
                "title": "Test Job",
            }
            mock_scraper.return_value.scrape_application_form.return_value = {
                "fields": ["name", "email"],
                "form_data": {"name": "John Doe"},
            }

            response = client.post(
                f"/api/v1/jobs/{job_id}/scrape-form",
                json=form_data,
                headers=auth_headers,
            )

            assert response.status_code == 200

    def test_automated_job_application(self, client: TestClient, auth_headers):
        """Test automated job application submission"""
        job_id = str(ObjectId())
        application_data = {
            "resume": "base64_encoded_resume",
            "cover_letter": "Custom cover letter",
            "form_data": {"name": "John Doe", "email": "john@example.com"},
        }

        with patch("backend.routes.jobs.get_async_db") as mock_db, patch(
            "backend.routes.jobs.AutoApplicationService"
        ) as mock_auto_apply:
            mock_db.return_value.jobs.find_one.return_value = {
                "_id": ObjectId(job_id),
                "title": "Test Job",
                "application_url": "https://example.com/apply",
            }
            mock_auto_apply.return_value.submit_application.return_value = {
                "success": True,
                "application_id": "app123",
            }

            response = client.post(
                f"/api/v1/jobs/{job_id}/apply-automated",
                json=application_data,
                headers=auth_headers,
            )

            assert response.status_code == 200
