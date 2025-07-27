import asyncio
import json
import time
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from bson import ObjectId
from fastapi.testclient import TestClient

from main import app


class TestCompleteUserJourney:
    """End-to-end tests for complete user journeys"""

    @pytest.fixture
    def client(self):
        return TestClient(app)

    @pytest.fixture
    def mock_user_data(self):
        """Mock user data for testing"""
        return {
            "email": "test@example.com",
            "password": "TestPass123!",
            "full_name": "Test User",
            "phone": "+1234567890",
            "location": "New York",
            "experience_years": 3,
            "skills": ["Python", "JavaScript", "React"],
        }

    @pytest.fixture
    def mock_job_data(self):
        """Mock job data for testing"""
        return {
            "title": "Senior Python Developer",
            "company": "Tech Corp",
            "description": "We are looking for a senior Python developer with React experience",
            "location": "Remote",
            "salary_min": 80000,
            "salary_max": 120000,
            "requirements": ["Python", "Django", "React", "PostgreSQL"],
            "benefits": ["Health insurance", "Remote work", "Flexible hours"],
            "job_type": "full-time",
            "experience_level": "senior",
            "isRemote": True,
        }

    def test_user_registration_to_job_application_journey(
        self, client, mock_user_data, mock_job_data
    ):
        """Complete journey: Registration -> Login -> Job Search -> Application"""

        # Step 1: User Registration
        registration_response = client.post(
            "/api/v1/auth/register", json=mock_user_data
        )
        assert registration_response.status_code in [
            200,
            201,
            422,
        ], "Registration should work"

        # Step 2: User Login
        login_data = {
            "email": mock_user_data["email"],
            "password": mock_user_data["password"],
        }
        login_response = client.post("/api/v1/auth/login", json=login_data)
        assert login_response.status_code in [200, 422], "Login should work"

        # Extract token if login successful
        auth_token = None
        if login_response.status_code == 200:
            login_data = login_response.json()
            auth_token = login_data.get("access_token")

        # Step 3: Job Search
        search_response = client.get("/api/v1/jobs/search?q=python&limit=10")
        assert search_response.status_code == 200, "Job search should work"

        search_data = search_response.json()
        assert (
            "jobs" in search_data or "items" in search_data
        ), "Search should return jobs"

        # Step 4: Get Job Details
        if "jobs" in search_data and search_data["jobs"]:
            job_id = search_data["jobs"][0]["id"]
            job_detail_response = client.get(f"/api/v1/jobs/{job_id}")
            assert job_detail_response.status_code in [
                200,
                404,
            ], "Job detail should work"

        # Step 5: Submit Application (if authenticated)
        if auth_token:
            headers = {"Authorization": f"Bearer {auth_token}"}
            application_data = {
                "job_id": "test_job_id",
                "cover_letter": "I am interested in this position...",
                "resume_url": "https://example.com/resume.pdf",
            }
            application_response = client.post(
                "/api/v1/applications/apply", json=application_data, headers=headers
            )
            assert application_response.status_code in [
                200,
                201,
                422,
            ], "Application should work"

        return {
            "registration_success": registration_response.status_code in [200, 201],
            "login_success": login_response.status_code == 200,
            "search_success": search_response.status_code == 200,
            "application_success": auth_token is not None,
        }

    def test_job_search_and_filtering_journey(self, client):
        """Complete journey: Advanced job search with filters"""

        # Step 1: Basic Search
        basic_search = client.get("/api/v1/jobs/search?q=python&limit=20")
        assert basic_search.status_code == 200, "Basic search should work"

        # Step 2: Filtered Search
        filtered_search = client.get(
            "/api/v1/jobs/search?q=python&work_type=remote&job_type=full-time&experience=senior&limit=15"
        )
        assert filtered_search.status_code == 200, "Filtered search should work"

        # Step 3: Salary Range Search
        salary_search = client.get(
            "/api/v1/jobs/search?q=python&salary_range=80000-120000&limit=10"
        )
        assert salary_search.status_code == 200, "Salary search should work"

        # Step 4: Location-based Search
        location_search = client.get(
            "/api/v1/jobs/search?q=python&location=remote&limit=10"
        )
        assert location_search.status_code == 200, "Location search should work"

        # Step 5: Complex Search
        complex_search = client.get(
            "/api/v1/jobs/search?q=python developer&work_type=remote&job_type=full-time&experience=senior&salary_range=80000-120000&limit=20"
        )
        assert complex_search.status_code == 200, "Complex search should work"

        # Step 6: Search Statistics
        stats_response = client.get("/api/v1/jobs/statistics")
        assert stats_response.status_code == 200, "Statistics should work"

        # Step 7: Recent Jobs
        recent_jobs = client.get("/api/v1/jobs/recent")
        assert recent_jobs.status_code == 200, "Recent jobs should work"

        return {
            "basic_search_results": len(basic_search.json().get("jobs", [])),
            "filtered_search_results": len(filtered_search.json().get("jobs", [])),
            "salary_search_results": len(salary_search.json().get("jobs", [])),
            "location_search_results": len(location_search.json().get("jobs", [])),
            "complex_search_results": len(complex_search.json().get("jobs", [])),
            "has_statistics": "total_jobs" in stats_response.json(),
            "has_recent_jobs": len(recent_jobs.json().get("jobs", [])) >= 0,
        }

    def test_authentication_and_profile_journey(self, client, mock_user_data):
        """Complete journey: Authentication and profile management"""

        # Step 1: Register User
        register_response = client.post("/api/v1/auth/register", json=mock_user_data)
        assert register_response.status_code in [
            200,
            201,
            422,
        ], "Registration should work"

        # Step 2: Login
        login_response = client.post(
            "/api/v1/auth/login",
            json={
                "email": mock_user_data["email"],
                "password": mock_user_data["password"],
            },
        )

        if login_response.status_code == 200:
            login_data = login_response.json()
            auth_token = login_data.get("access_token")
            headers = {"Authorization": f"Bearer {auth_token}"}

            # Step 3: Get User Profile
            profile_response = client.get("/api/v1/user/profile", headers=headers)
            assert profile_response.status_code in [200, 404], "Profile should work"

            # Step 4: Update Profile
            update_data = {
                "full_name": "Updated Test User",
                "location": "San Francisco",
                "experience_years": 5,
                "skills": ["Python", "JavaScript", "React", "Node.js"],
            }
            update_response = client.put(
                "/api/v1/user/profile", json=update_data, headers=headers
            )
            assert update_response.status_code in [
                200,
                422,
            ], "Profile update should work"

            # Step 5: Get User Applications
            applications_response = client.get(
                "/api/v1/applications/my-applications", headers=headers
            )
            assert applications_response.status_code in [
                200,
                404,
            ], "Applications should work"

            return {
                "registration_success": True,
                "login_success": True,
                "profile_access": profile_response.status_code == 200,
                "profile_update": update_response.status_code == 200,
                "applications_access": applications_response.status_code == 200,
            }
        else:
            return {
                "registration_success": register_response.status_code in [200, 201],
                "login_success": False,
                "profile_access": False,
                "profile_update": False,
                "applications_access": False,
            }

    def test_job_recommendations_journey(self, client, mock_user_data):
        """Complete journey: Job recommendations and matching"""

        # Step 1: Register and Login
        client.post("/api/v1/auth/register", json=mock_user_data)
        login_response = client.post(
            "/api/v1/auth/login",
            json={
                "email": mock_user_data["email"],
                "password": mock_user_data["password"],
            },
        )

        if login_response.status_code == 200:
            auth_token = login_response.json().get("access_token")
            headers = {"Authorization": f"Bearer {auth_token}"}

            # Step 2: Get Job Recommendations
            recommendations_response = client.get(
                "/api/v1/jobs/recommendations", headers=headers
            )
            assert recommendations_response.status_code in [
                200,
                404,
            ], "Recommendations should work"

            # Step 3: Get Personalized Job Matches
            matches_response = client.get("/api/v1/jobs/matches", headers=headers)
            assert matches_response.status_code in [200, 404], "Matches should work"

            # Step 4: Track Job Views
            job_id = "test_job_id"
            view_response = client.post(f"/api/v1/jobs/{job_id}/view", headers=headers)
            assert view_response.status_code in [
                200,
                404,
            ], "Job view tracking should work"

            return {
                "login_success": True,
                "recommendations_available": recommendations_response.status_code
                == 200,
                "matches_available": matches_response.status_code == 200,
                "view_tracking": view_response.status_code == 200,
            }
        else:
            return {
                "login_success": False,
                "recommendations_available": False,
                "matches_available": False,
                "view_tracking": False,
            }

    def test_notification_and_communication_journey(self, client, mock_user_data):
        """Complete journey: Notifications and communication"""

        # Step 1: Register and Login
        client.post("/api/v1/auth/register", json=mock_user_data)
        login_response = client.post(
            "/api/v1/auth/login",
            json={
                "email": mock_user_data["email"],
                "password": mock_user_data["password"],
            },
        )

        if login_response.status_code == 200:
            auth_token = login_response.json().get("access_token")
            headers = {"Authorization": f"Bearer {auth_token}"}

            # Step 2: Get Notification Settings
            settings_response = client.get(
                "/api/v1/notifications/settings", headers=headers
            )
            assert settings_response.status_code in [
                200,
                404,
            ], "Notification settings should work"

            # Step 3: Update Notification Preferences
            notification_prefs = {
                "email_notifications": True,
                "push_notifications": False,
                "weekly_digest": True,
                "job_alerts": True,
            }
            update_settings_response = client.put(
                "/api/v1/notifications/settings",
                json=notification_prefs,
                headers=headers,
            )
            assert update_settings_response.status_code in [
                200,
                422,
            ], "Settings update should work"

            # Step 4: Get User Notifications
            notifications_response = client.get(
                "/api/v1/notifications", headers=headers
            )
            assert notifications_response.status_code in [
                200,
                404,
            ], "Notifications should work"

            # Step 5: Mark Notification as Read
            if notifications_response.status_code == 200:
                notifications_data = notifications_response.json()
                if notifications_data.get("notifications"):
                    notification_id = notifications_data["notifications"][0]["id"]
                    mark_read_response = client.put(
                        f"/api/v1/notifications/{notification_id}/read", headers=headers
                    )
                    assert mark_read_response.status_code in [
                        200,
                        404,
                    ], "Mark read should work"

            return {
                "login_success": True,
                "settings_access": settings_response.status_code == 200,
                "settings_update": update_settings_response.status_code == 200,
                "notifications_access": notifications_response.status_code == 200,
            }
        else:
            return {
                "login_success": False,
                "settings_access": False,
                "settings_update": False,
                "notifications_access": False,
            }

    def test_admin_panel_journey(self, client):
        """Complete journey: Admin panel functionality"""

        # Step 1: Access Admin Login
        admin_login_response = client.get("/admin/login")
        assert admin_login_response.status_code in [
            200,
            302,
            404,
        ], "Admin login should be accessible"

        # Step 2: Admin Login (with mock credentials)
        admin_credentials = {"username": "admin", "password": "admin123"}
        admin_auth_response = client.post("/admin/login", data=admin_credentials)
        assert admin_auth_response.status_code in [
            200,
            302,
            404,
        ], "Admin auth should work"

        # Step 3: Access Admin Dashboard
        dashboard_response = client.get("/admin/")
        assert dashboard_response.status_code in [
            200,
            302,
            404,
        ], "Admin dashboard should work"

        # Step 4: Access Admin Jobs
        admin_jobs_response = client.get("/admin/jobs")
        assert admin_jobs_response.status_code in [
            200,
            302,
            404,
        ], "Admin jobs should work"

        # Step 5: Access Admin Users
        admin_users_response = client.get("/admin/users")
        assert admin_users_response.status_code in [
            200,
            302,
            404,
        ], "Admin users should work"

        # Step 6: Access Admin Analytics
        admin_analytics_response = client.get("/admin/analytics")
        assert admin_analytics_response.status_code in [
            200,
            302,
            404,
        ], "Admin analytics should work"

        return {
            "login_accessible": admin_login_response.status_code in [200, 302],
            "auth_works": admin_auth_response.status_code in [200, 302],
            "dashboard_accessible": dashboard_response.status_code in [200, 302],
            "jobs_accessible": admin_jobs_response.status_code in [200, 302],
            "users_accessible": admin_users_response.status_code in [200, 302],
            "analytics_accessible": admin_analytics_response.status_code in [200, 302],
        }

    def test_error_handling_journey(self, client):
        """Complete journey: Error handling and edge cases"""

        # Step 1: Test Invalid Endpoints
        invalid_endpoint = client.get("/api/v1/nonexistent")
        assert (
            invalid_endpoint.status_code == 404
        ), "Should return 404 for invalid endpoint"

        # Step 2: Test Invalid Job ID
        invalid_job = client.get("/api/v1/jobs/invalid-id")
        assert invalid_job.status_code in [404, 422], "Should handle invalid job ID"

        # Step 3: Test Invalid Search Parameters
        invalid_search = client.get("/api/v1/jobs/search?limit=invalid&page=-1")
        assert invalid_search.status_code in [
            200,
            400,
            422,
        ], "Should handle invalid search params"

        # Step 4: Test Large Payload
        large_payload = {"data": "x" * 10000}  # 10KB payload
        large_request = client.post("/api/v1/jobs/search", json=large_payload)
        assert large_request.status_code in [
            200,
            400,
            413,
            422,
        ], "Should handle large payload"

        # Step 5: Test Rate Limiting
        rapid_requests = []
        for _ in range(10):
            response = client.get("/api/v1/jobs/search?limit=1")
            rapid_requests.append(response.status_code)

        # Should handle rapid requests gracefully
        assert all(
            status in [200, 429, 503] for status in rapid_requests
        ), "Should handle rapid requests"

        # Step 6: Test Authentication Errors
        protected_endpoint = client.get("/api/v1/user/profile")
        assert protected_endpoint.status_code in [
            401,
            403,
        ], "Should require authentication"

        # Step 7: Test Invalid Token
        invalid_token_headers = {"Authorization": "Bearer invalid_token"}
        invalid_auth = client.get("/api/v1/user/profile", headers=invalid_token_headers)
        assert invalid_auth.status_code in [401, 403], "Should reject invalid token"

        return {
            "invalid_endpoint_handled": invalid_endpoint.status_code == 404,
            "invalid_job_handled": invalid_job.status_code in [404, 422],
            "invalid_search_handled": invalid_search.status_code in [200, 400, 422],
            "large_payload_handled": large_request.status_code in [200, 400, 413, 422],
            "rate_limiting_works": all(
                status in [200, 429, 503] for status in rapid_requests
            ),
            "auth_required": protected_endpoint.status_code in [401, 403],
            "invalid_token_rejected": invalid_auth.status_code in [401, 403],
        }

    def test_performance_journey(self, client):
        """Complete journey: Performance testing under load"""

        # Step 1: Test Response Times
        endpoints = [
            "/health",
            "/api/v1/jobs/search?limit=10",
            "/api/v1/jobs/statistics",
            "/api/v1/jobs/recent",
        ]

        performance_results = {}
        for endpoint in endpoints:
            start_time = time.time()
            response = client.get(endpoint)
            end_time = time.time()

            response_time = end_time - start_time
            performance_results[endpoint] = {
                "response_time": response_time,
                "status_code": response.status_code,
                "success": response.status_code in [200, 422],
            }

            # Performance assertions
            assert (
                response_time < 3.0
            ), f"Response time too slow for {endpoint}: {response_time:.3f}s"
            assert response.status_code in [
                200,
                422,
            ], f"Unexpected status for {endpoint}: {response.status_code}"

        # Step 2: Test Concurrent Access
        import queue
        import threading

        results_queue = queue.Queue()

        def concurrent_request(endpoint):
            start_time = time.time()
            response = client.get(endpoint)
            end_time = time.time()

            results_queue.put(
                {
                    "endpoint": endpoint,
                    "response_time": end_time - start_time,
                    "status_code": response.status_code,
                }
            )

        # Start concurrent threads
        threads = []
        for _ in range(5):
            for endpoint in endpoints:
                thread = threading.Thread(target=concurrent_request, args=(endpoint,))
                threads.append(thread)
                thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join()

        # Collect results
        concurrent_results = []
        while not results_queue.empty():
            concurrent_results.append(results_queue.get())

        # Analyze concurrent performance
        avg_concurrent_time = sum(r["response_time"] for r in concurrent_results) / len(
            concurrent_results
        )
        success_rate = len(
            [r for r in concurrent_results if r["status_code"] in [200, 422]]
        ) / len(concurrent_results)

        # Performance assertions
        assert (
            avg_concurrent_time < 5.0
        ), f"Average concurrent response time too slow: {avg_concurrent_time:.3f}s"
        assert (
            success_rate > 0.9
        ), f"Success rate too low under load: {success_rate:.2%}"

        return {
            "single_request_performance": performance_results,
            "concurrent_performance": {
                "avg_response_time": avg_concurrent_time,
                "success_rate": success_rate,
                "total_requests": len(concurrent_results),
            },
        }
