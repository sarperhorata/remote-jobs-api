import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch, AsyncMock
import json
from datetime import datetime

class TestFakeJobDetectionRoutes:
    """Test fake job detection routes"""
    
    def test_analyze_job_endpoint_exists(self, client: TestClient):
        """Test that analyze job endpoint exists"""
        response = client.get("/api/v1/fake-job-detection/analyze-job")
        assert response.status_code in [405, 422]  # Method not allowed or validation error
    
    def test_batch_analyze_jobs_endpoint_exists(self, client: TestClient):
        """Test that batch analyze jobs endpoint exists"""
        response = client.get("/api/v1/fake-job-detection/batch-analyze")
        assert response.status_code in [405, 422]  # Method not allowed or validation error
    
    def test_get_analysis_history_endpoint_exists(self, client: TestClient):
        """Test that get analysis history endpoint exists"""
        response = client.get("/api/v1/fake-job-detection/history")
        assert response.status_code in [405, 422]  # Method not allowed or validation error
    
    @patch('services.fake_job_detector.FakeJobDetector.analyze_job')
    def test_analyze_single_job_success(self, mock_analyze, client: TestClient, admin_headers):
        """Test successful single job analysis"""
        mock_analysis = Mock()
        mock_analysis.job_id = "test_job_123"
        mock_analysis.risk_level.value = "medium"
        mock_analysis.confidence_score = 0.75
        mock_analysis.red_flags = ["Suspicious email domain"]
        mock_analysis.suspicious_patterns = ["Generic job description"]
        mock_analysis.ai_analysis = "AI analysis result"
        mock_analysis.recommendation = "Proceed with caution"
        mock_analysis.analyzed_at = datetime.now()
        
        mock_analyze.return_value = mock_analysis
        
        response = client.post(
            "/api/v1/fake-job-detection/analyze-job",
            json={"job_id": "test_job_123"},
            headers=admin_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["job_id"] == "test_job_123"
        assert data["risk_level"] == "medium"
        assert data["confidence_score"] == 0.75
        assert "red_flags" in data
        assert "suspicious_patterns" in data
        assert "ai_analysis" in data
        assert "recommendation" in data
    
    def test_analyze_job_not_found(self, client: TestClient, admin_headers):
        """Test job analysis with non-existent job"""
        response = client.post(
            "/api/v1/fake-job-detection/analyze-job",
            json={"job_id": "non_existent_job"},
            headers=admin_headers
        )
        
        assert response.status_code == 404
        data = response.json()
        assert "Job not found" in data["detail"]
    
    @patch('services.fake_job_detector.FakeJobDetector.batch_analyze_jobs')
    def test_batch_analyze_jobs_success(self, mock_batch_analyze, client: TestClient, admin_headers):
        """Test successful batch job analysis"""
        mock_results = [
            {
                "job_id": "job_1",
                "risk_level": "low",
                "confidence_score": 0.9,
                "red_flags": [],
                "suspicious_patterns": [],
                "ai_analysis": "Legitimate job posting",
                "recommendation": "Safe to proceed",
                "analyzed_at": datetime.now().isoformat()
            },
            {
                "job_id": "job_2",
                "risk_level": "high",
                "confidence_score": 0.8,
                "red_flags": ["Suspicious domain", "No company info"],
                "suspicious_patterns": ["Generic description"],
                "ai_analysis": "Multiple red flags detected",
                "recommendation": "Avoid this posting",
                "analyzed_at": datetime.now().isoformat()
            }
        ]
        
        mock_batch_analyze.return_value = mock_results
        
        response = client.post(
            "/api/v1/fake-job-detection/batch-analyze",
            json={
                "job_ids": ["job_1", "job_2"],
                "batch_size": 10
            },
            headers=admin_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "results" in data
        assert len(data["results"]) == 2
        assert data["total_analyzed"] == 2
        assert "summary" in data
    
    def test_batch_analyze_invalid_request(self, client: TestClient, admin_headers):
        """Test batch analysis with invalid request"""
        response = client.post(
            "/api/v1/fake-job-detection/batch-analyze",
            json={"job_ids": []},  # Empty job list
            headers=admin_headers
        )
        
        assert response.status_code == 400
        data = response.json()
        assert "Job IDs list cannot be empty" in data["detail"]
    
    def test_get_analysis_history_success(self, client: TestClient, admin_headers):
        """Test successful analysis history retrieval"""
        response = client.get(
            "/api/v1/fake-job-detection/history",
            params={"limit": 10, "offset": 0},
            headers=admin_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "analyses" in data
        assert "total_count" in data
        assert "pagination" in data
    
    def test_fake_job_detection_admin_only(self, client: TestClient):
        """Test that fake job detection endpoints require admin access"""
        endpoints = [
            ("/api/v1/fake-job-detection/analyze-job", "POST"),
            ("/api/v1/fake-job-detection/batch-analyze", "POST"),
            ("/api/v1/fake-job-detection/history", "GET")
        ]
        
        for endpoint, method in endpoints:
            if method == "POST":
                response = client.post(endpoint, json={})
            else:
                response = client.get(endpoint)
            
            assert response.status_code in [401, 403, 422]  # Unauthorized, Forbidden, or validation error
    
    @patch('services.fake_job_detector.FakeJobDetector.analyze_job')
    def test_analyze_job_error_handling(self, mock_analyze, client: TestClient, admin_headers):
        """Test error handling in job analysis"""
        mock_analyze.side_effect = Exception("Analysis failed")
        
        response = client.post(
            "/api/v1/fake-job-detection/analyze-job",
            json={"job_id": "test_job_123"},
            headers=admin_headers
        )
        
        assert response.status_code == 500
        data = response.json()
        assert "Analysis failed" in data["detail"]
    
    def test_analyze_job_invalid_job_id(self, client: TestClient, admin_headers):
        """Test job analysis with invalid job ID format"""
        response = client.post(
            "/api/v1/fake-job-detection/analyze-job",
            json={"job_id": ""},  # Empty job ID
            headers=admin_headers
        )
        
        assert response.status_code == 422  # Validation error
    
    @patch('services.fake_job_detector.FakeJobDetector.batch_analyze_jobs')
    def test_batch_analyze_large_batch(self, mock_batch_analyze, client: TestClient, admin_headers):
        """Test batch analysis with large batch size"""
        # Create a large list of job IDs
        large_job_list = [f"job_{i}" for i in range(100)]
        
        mock_batch_analyze.return_value = []
        
        response = client.post(
            "/api/v1/fake-job-detection/batch-analyze",
            json={
                "job_ids": large_job_list,
                "batch_size": 50
            },
            headers=admin_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "results" in data
        assert "total_analyzed" in data 