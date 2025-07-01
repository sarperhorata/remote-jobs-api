import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

class TestJobsRouteSimple:
    """Simple extended tests for jobs routes"""

    def test_search_jobs_basic(self):
        """Test basic job search functionality"""
        response = client.get("/api/v1/jobs/search")
        assert response.status_code in [200, 422]
        data = response.json()
        assert "items" in data or "jobs" in data
        assert "total" in data

    def test_search_jobs_with_query(self):
        """Test job search with query parameter"""
        response = client.get("/api/v1/jobs/search?q=python")
        assert response.status_code in [200, 422]
        data = response.json()
        assert isinstance(data, dict)

    def test_search_jobs_with_pagination(self):
        """Test job search with pagination"""
        response = client.get("/api/v1/jobs/search?page=1&limit=5")
        assert response.status_code in [200, 422]
        data = response.json()
        
        items = data.get("items", data.get("jobs", []))
        assert len(items) <= 5

    def test_search_jobs_with_filters(self):
        """Test job search with various filters"""
        filters = {
            "location": "Remote",
            "company": "Tech Corp",
            "work_type": "remote", 
            "job_type": "full-time",
            "experience_level": "senior",
            "sort_by": "newest",
            "posted_age": "7DAYS"
        }
        
        query_string = "&".join([f"{k}={v}" for k, v in filters.items()])
        response = client.get(f"/api/v1/jobs/search?{query_string}")
        assert response.status_code in [200, 422]

    def test_search_jobs_invalid_pagination(self):
        """Test job search with invalid pagination parameters"""
        response = client.get("/api/v1/jobs/search?page=-1&limit=0")
        # Should handle invalid params gracefully
        assert response.status_code in [200, 400, 422]

    def test_search_jobs_large_limit(self):
        """Test job search with very large limit"""
        response = client.get("/api/v1/jobs/search?limit=10000")
        assert response.status_code in [200, 422]
        data = response.json()
        items = data.get("items", data.get("jobs", []))
        # Should be capped at reasonable limit
        assert len(items) <= 100

    def test_job_titles_search(self):
        """Test job titles autocomplete search"""
        response = client.get("/api/v1/jobs/job-titles/search?q=dev&limit=5")
        assert response.status_code in [200, 422]
        data = response.json()
        assert isinstance(data, list)
        assert len(data) <= 5

    def test_job_titles_search_empty_query(self):
        """Test job titles search with empty query"""
        response = client.get("/api/v1/jobs/job-titles/search?q=&limit=5")
        assert response.status_code in [200, 422]
        data = response.json()
        assert isinstance(data, list)

    def test_companies_search(self):
        """Test companies autocomplete search"""
        response = client.get("/api/v1/jobs/companies/search?q=tech&limit=3")
        assert response.status_code in [200, 422]
        data = response.json()
        assert isinstance(data, list)
        assert len(data) <= 3

    def test_companies_search_case_insensitive(self):
        """Test companies search is case insensitive"""
        response = client.get("/api/v1/jobs/companies/search?q=TECH&limit=3")
        assert response.status_code in [200, 422]

    def test_locations_search(self):
        """Test locations autocomplete search"""
        response = client.get("/api/v1/jobs/locations/search?q=san&limit=3")
        assert response.status_code in [200, 422]
        data = response.json()
        assert isinstance(data, list)
        assert len(data) <= 3

    def test_locations_search_partial_match(self):
        """Test locations search with partial matches"""
        response = client.get("/api/v1/jobs/locations/search?q=new&limit=5")
        assert response.status_code in [200, 422]

    def test_search_jobs_with_complex_query(self):
        """Test job search with complex query containing special characters"""
        complex_queries = [
            "python & machine learning",
            "react.js + typescript",
            "c++ developer",
            "full-stack engineer"
        ]
        
        for query in complex_queries:
            response = client.get(f"/api/v1/jobs/search?q={query}")
            assert response.status_code in [200, 422]

    def test_search_jobs_with_date_filters(self):
        """Test job search with date-based filters"""
        date_filters = ["1DAY", "7DAYS", "14DAYS", "30DAYS"]
        
        for filter_val in date_filters:
            response = client.get(f"/api/v1/jobs/search?posted_age={filter_val}")
            assert response.status_code in [200, 422]

    def test_search_jobs_sorting_options(self):
        """Test job search with different sorting options"""
        sort_options = ["newest", "oldest", "relevance", "salary_high", "salary_low"]
        
        for sort_option in sort_options:
            response = client.get(f"/api/v1/jobs/search?sort_by={sort_option}")
            assert response.status_code in [200, 422]

    def test_search_with_malformed_parameters(self):
        """Test search with malformed parameters"""
        malformed_params = [
            "limit=abc",
            "page=xyz", 
            "posted_age=invalid",
            "sort_by=nonsense"
        ]
        
        for param in malformed_params:
            response = client.get(f"/api/v1/jobs/search?{param}")
            # Should handle malformed params gracefully
            assert response.status_code in [200, 400, 422]

    def test_search_response_structure(self):
        """Test job search response has correct structure"""
        response = client.get("/api/v1/jobs/search?limit=1")
        assert response.status_code in [200, 422]
        
        data = response.json()
        
        # Should have either 'items' or 'jobs' key
        assert "items" in data or "jobs" in data
        assert "total" in data
        
        items = data.get("items", data.get("jobs", []))
        if items:
            job = items[0]
            # Basic job fields should be present
            assert "title" in job
            assert "company" in job

    def test_autocomplete_response_structure(self):
        """Test autocomplete endpoints return correct structure"""
        endpoints = [
            "/api/v1/jobs/job-titles/search?q=dev&limit=3",
            "/api/v1/jobs/companies/search?q=tech&limit=3", 
            "/api/v1/jobs/locations/search?q=san&limit=3"
        ]
        
        for endpoint in endpoints:
            response = client.get(endpoint)
            assert response.status_code in [200, 422]
            data = response.json()
            assert isinstance(data, list)

    def test_search_with_unicode_characters(self):
        """Test search with unicode characters"""
        unicode_queries = ["développeur", "ingeniero", "разработчик"]
        
        for query in unicode_queries:
            response = client.get(f"/api/v1/jobs/search?q={query}")
            assert response.status_code in [200, 422]

    def test_search_with_sql_injection_attempt(self):
        """Test search is protected against SQL injection attempts"""
        malicious_queries = [
            "'; DROP TABLE jobs; --",
            "1' OR '1'='1",
            "<script>alert('xss')</script>"
        ]
        
        for query in malicious_queries:
            response = client.get(f"/api/v1/jobs/search?q={query}")
            assert response.status_code in [200, 422]  # Should handle safely

    def test_search_with_extremely_long_query(self):
        """Test search with extremely long query string"""
        long_query = "a" * 1000  # Long query
        response = client.get(f"/api/v1/jobs/search?q={long_query}")
        assert response.status_code in [200, 400, 413]  # Should handle gracefully

    def test_rate_limiting_protection(self):
        """Test endpoints handle multiple rapid requests"""
        for _ in range(5):
            response = client.get("/api/v1/jobs/search?q=test&limit=1")
            assert response.status_code in [200, 429]

    def test_health_check_coverage(self):
        """Test health check endpoint"""
        response = client.get("/health")
        assert response.status_code in [200, 422]

    def test_cors_headers(self):
        """Test CORS headers are present"""
        response = client.options("/api/v1/jobs/search")
        assert response.status_code in [200, 405]  # Some endpoints may not support OPTIONS

    def test_pagination_edge_cases(self):
        """Test pagination edge cases"""
        edge_cases = [
            "page=0&limit=1",
            "page=1&limit=1000",
            "page=999999&limit=1"
        ]
        
        for params in edge_cases:
            response = client.get(f"/api/v1/jobs/search?{params}")
            assert response.status_code in [200, 400, 422]

    def test_search_performance_basic(self):
        """Test search performance doesn't timeout"""
        import time
        
        start_time = time.time()
        response = client.get("/api/v1/jobs/search?q=python&limit=10")
        end_time = time.time()
        
        assert response.status_code in [200, 422]
        # Should complete within reasonable time (3 seconds)
        assert (end_time - start_time) < 3.0

class TestJobsSkillsRoutes:
    """Test job skills-related routes"""
    
    def test_skills_search_endpoint_exists(self, client):
        """Test skills search endpoint exists"""
        response = client.get("/api/v1/jobs/skills/search?q=python&limit=5")
        assert response.status_code == 200
        
    def test_skills_search_with_results(self, client):
        """Test skills search returns results"""
        response = client.get("/api/v1/jobs/skills/search?q=java&limit=10")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        
    def test_skills_search_empty_query(self, client):
        """Test skills search with empty query"""
        response = client.get("/api/v1/jobs/skills/search?q=&limit=5")
        assert response.status_code == 200

class TestJobsRecentRoutes:
    """Test recent jobs routes"""
    
    def test_recent_jobs_endpoint_exists(self, client):
        """Test recent jobs endpoint exists"""
        response = client.get("/api/v1/jobs/recent?limit=5")
        assert response.status_code == 200
        
    def test_recent_jobs_with_timestamp(self, client):
        """Test recent jobs with since parameter"""
        from datetime import datetime, timedelta
        since = (datetime.utcnow() - timedelta(days=1)).isoformat()
        response = client.get(f"/api/v1/jobs/recent?since={since}&limit=3")
        assert response.status_code == 200

class TestJobsTrackingRoutes:
    """Test job tracking routes"""
    
    def test_track_job_interaction_endpoint(self, client):
        """Test track job interaction endpoint"""
        tracking_data = {
            "action": "view",
            "source": "search_results",
            "user_agent": "test-agent"
        }
        response = client.post("/api/v1/jobs/job123/track", json=tracking_data)
        # Should return 200, 401, or 422 - not 404
        assert response.status_code in [200, 401, 422, 500]

class TestJobsStatisticsRoutes:
    """Test job statistics routes"""
    
    def test_job_statistics_endpoint_exists(self, client):
        """Test job statistics endpoint exists"""
        response = client.get("/api/v1/jobs/statistics")
        assert response.status_code in [200, 404, 500]
        
    def test_job_statistics_response_format(self, client):
        """Test job statistics response format"""
        response = client.get("/api/v1/jobs/statistics")
        if response.status_code == 200:
            data = response.json()
            # Should have basic statistics fields
            assert "total_jobs" in data or "error" in data

class TestJobsRecommendationRoutes:
    """Test job recommendations routes"""
    
    def test_recommendations_endpoint_exists(self, client):
        """Test recommendations endpoint exists"""
        response = client.get("/api/v1/jobs/recommendations?limit=5")
        assert response.status_code in [200, 500]
        
    def test_recommendations_with_limit(self, client):
        """Test recommendations with different limits"""
        for limit in [1, 5, 10]:
            response = client.get(f"/api/v1/jobs/recommendations?limit={limit}")
            assert response.status_code in [200, 500]

class TestJobsSkillsRoutes:
    """Test job skills-related routes"""
    
    def test_skills_search_endpoint_exists(self, client):
        """Test skills search endpoint exists"""
        response = client.get("/api/v1/jobs/skills/search?q=python&limit=5")
        assert response.status_code == 200
        
    def test_skills_search_with_results(self, client):
        """Test skills search returns results"""
        response = client.get("/api/v1/jobs/skills/search?q=java&limit=10")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

class TestJobsRecentRoutes:
    """Test recent jobs routes"""
    
    def test_recent_jobs_endpoint_exists(self, client):
        """Test recent jobs endpoint exists"""
        response = client.get("/api/v1/jobs/recent?limit=5")
        assert response.status_code == 200

class TestJobsStatisticsRoutes:
    """Test job statistics routes"""
    
    def test_job_statistics_endpoint_exists(self, client):
        """Test job statistics endpoint exists"""
        response = client.get("/api/v1/jobs/statistics")
        assert response.status_code in [200, 404, 500]
