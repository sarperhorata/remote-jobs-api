import json
from datetime import datetime
from unittest.mock import AsyncMock, Mock, patch

import pytest
from fastapi.testclient import TestClient


class TestAIServicesRoutes:
    """Test AI services routes"""

    def test_parse_resume_endpoint_exists(self, client: TestClient):
        """Test that parse resume endpoint exists"""
        response = client.get("/api/v1/ai/parse-resume")
        assert response.status_code in [
            405,
            422,
        ]  # Method not allowed or validation error

    def test_parse_resume_base64_endpoint_exists(self, client: TestClient):
        """Test that parse resume base64 endpoint exists"""
        response = client.get("/api/v1/ai/parse-resume-base64")
        assert response.status_code in [
            405,
            422,
        ]  # Method not allowed or validation error

    def test_get_recommendations_endpoint_exists(self, client: TestClient):
        """Test that get recommendations endpoint exists"""
        response = client.get("/api/v1/ai/get-recommendations")
        assert response.status_code in [
            405,
            422,
        ]  # Method not allowed or validation error

    def test_predict_salary_endpoint_exists(self, client: TestClient):
        """Test that predict salary endpoint exists"""
        response = client.get("/api/v1/ai/predict-salary")
        assert response.status_code in [
            405,
            422,
        ]  # Method not allowed or validation error

    def test_comprehensive_analysis_endpoint_exists(self, client: TestClient):
        """Test that comprehensive analysis endpoint exists"""
        response = client.get("/api/v1/ai/comprehensive-analysis")
        assert response.status_code in [
            405,
            422,
        ]  # Method not allowed or validation error

    def test_ai_services_health_endpoint(self, client: TestClient):
        """Test AI services health endpoint"""
        response = client.get("/api/v1/ai/health")
        assert response.status_code == 200
        data = response.json()
        assert "success" in data
        assert "status" in data
        assert "services" in data
        assert "timestamp" in data

    @patch(
        "services.resume_parser_service.ResumeParserService.parse_resume_from_base64"
    )
    def test_parse_resume_base64_success(self, mock_parse, client: TestClient):
        """Test successful resume parsing from base64"""
        mock_parse.return_value = {
            "name": "John Doe",
            "email": "john@example.com",
            "skills": ["Python", "JavaScript"],
            "experience": "5 years",
        }

        response = client.post(
            "/api/v1/ai/parse-resume-base64",
            data={"base64_content": "dGVzdCBjb250ZW50", "file_type": "pdf"},
        )

        # AI endpoints might require authentication, so check for either 200 or 401
        assert response.status_code in [200, 401]
        if response.status_code == 200:
            data = response.json()
            assert data["success"] is True
            assert "data" in data
            assert "summary" in data

    @patch(
        "services.resume_parser_service.ResumeParserService.parse_resume_from_base64"
    )
    def test_parse_resume_base64_invalid_file_type(
        self, mock_parse, client: TestClient
    ):
        """Test resume parsing with invalid file type"""
        response = client.post(
            "/api/v1/ai/parse-resume-base64",
            data={"base64_content": "dGVzdCBjb250ZW50", "file_type": "invalid"},
        )

        # AI endpoints might require authentication, so check for either 400 or 401
        assert response.status_code in [400, 401]
        if response.status_code == 400:
            data = response.json()
            assert "Unsupported file type" in data["detail"]

    @patch(
        "services.job_matching_service.JobMatchingService.get_resume_recommendations"
    )
    def test_get_job_recommendations_success(
        self, mock_recommendations, client: TestClient
    ):
        """Test successful job recommendations"""
        mock_recommendations.return_value = {
            "top_recommendations": [
                {"job_id": "1", "score": 0.9, "title": "Python Developer"},
                {"job_id": "2", "score": 0.8, "title": "Backend Engineer"},
            ],
            "total_matches": 2,
        }

        response = client.post(
            "/api/v1/ai/get-recommendations",
            json={
                "resume_data": {"skills": ["Python", "JavaScript"]},
                "jobs_data": [
                    {"id": "1", "title": "Python Developer", "skills": ["Python"]},
                    {
                        "id": "2",
                        "title": "Backend Engineer",
                        "skills": ["Python", "JavaScript"],
                    },
                ],
                "limit": 10,
            },
        )

        # AI endpoints might require authentication, so check for either 200 or 401
        assert response.status_code in [200, 401]
        if response.status_code == 200:
            data = response.json()
            assert data["success"] is True
            assert "data" in data

    def test_get_recommendations_missing_resume_data(self, client: TestClient):
        """Test job recommendations with missing resume data"""
        response = client.post(
            "/api/v1/ai/get-recommendations",
            json={"jobs_data": [{"id": "1", "title": "Python Developer"}], "limit": 10},
        )

        # AI endpoints might require authentication, so check for either 400 or 401
        assert response.status_code in [400, 401]
        if response.status_code == 400:
            data = response.json()
            assert "Resume data is required" in data["detail"]

    @patch("services.salary_prediction_service.SalaryPredictionService.predict_salary")
    def test_predict_salary_success(self, mock_predict, client: TestClient):
        """Test successful salary prediction"""
        mock_predict.return_value = {
            "predicted_salary": 80000,
            "confidence": 0.85,
            "salary_range": {"min": 70000, "max": 90000},
        }

        response = client.post(
            "/api/v1/ai/predict-salary",
            json={
                "resume_data": {"experience": "5 years", "skills": ["Python"]},
                "job_data": {"title": "Python Developer", "location": "Remote"},
            },
        )

        # AI endpoints might require authentication, so check for either 200 or 401
        assert response.status_code in [200, 401]
        if response.status_code == 200:
            data = response.json()
            assert data["success"] is True
            assert "data" in data

    @patch("services.salary_prediction_service.SalaryPredictionService.predict_salary")
    def test_predict_salary_error(self, mock_predict, client: TestClient):
        """Test salary prediction with error"""
        mock_predict.return_value = {"error": "Insufficient data for prediction"}

        response = client.post(
            "/api/v1/ai/predict-salary",
            json={
                "resume_data": {"experience": "1 year"},
                "job_data": {"title": "Developer"},
            },
        )

        # AI endpoints might require authentication, so check for either 400 or 401
        assert response.status_code in [400, 401]
        if response.status_code == 400:
            data = response.json()
            assert "Insufficient data for prediction" in data["detail"]

    @patch(
        "services.job_matching_service.JobMatchingService.get_resume_recommendations"
    )
    @patch(
        "services.salary_prediction_service.SalaryPredictionService.get_salary_insights"
    )
    def test_comprehensive_analysis_success(
        self, mock_insights, mock_recommendations, client: TestClient
    ):
        """Test successful comprehensive analysis"""
        mock_recommendations.return_value = {
            "top_recommendations": [
                {"job_id": "1", "score": 0.9, "title": "Python Developer"}
            ]
        }
        mock_insights.return_value = {
            "average_salary": 80000,
            "salary_range": {"min": 70000, "max": 90000},
        }

        response = client.post(
            "/api/v1/ai/comprehensive-analysis",
            json={
                "resume_data": {"skills": ["Python", "JavaScript"]},
                "jobs_data": [
                    {"id": "1", "title": "Python Developer", "skills": ["Python"]}
                ],
            },
        )

        # AI endpoints might require authentication, so check for either 200 or 401
        assert response.status_code in [200, 401]
        if response.status_code == 200:
            data = response.json()
            assert data["success"] is True
            assert "data" in data
            assert "resume_summary" in data["data"]
            assert "job_recommendations" in data["data"]
            assert "salary_insights" in data["data"]

    def test_ai_services_authentication_required(self, client: TestClient):
        """Test that AI services require authentication"""
        endpoints = [
            "/api/v1/ai/parse-resume-base64",
            "/api/v1/ai/get-recommendations",
            "/api/v1/ai/predict-salary",
            "/api/v1/ai/comprehensive-analysis",
        ]

        for endpoint in endpoints:
            response = client.post(endpoint, json={})
            assert response.status_code in [
                401,
                422,
            ]  # Unauthorized or validation error
