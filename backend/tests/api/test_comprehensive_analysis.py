import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch, AsyncMock
import json
from datetime import datetime

class TestComprehensiveAnalysisRoutes:
    """Test comprehensive analysis routes"""
    
    def test_comprehensive_analysis_endpoint_exists(self, client: TestClient):
        """Test that comprehensive analysis endpoint exists"""
        response = client.get("/api/v1/analysis/comprehensive")
        assert response.status_code in [405, 422]  # Method not allowed or validation error
    
    def test_job_market_analysis_endpoint_exists(self, client: TestClient):
        """Test that job market analysis endpoint exists"""
        response = client.get("/api/v1/analysis/job-market")
        assert response.status_code in [405, 422]  # Method not allowed or validation error
    
    def test_skill_analysis_endpoint_exists(self, client: TestClient):
        """Test that skill analysis endpoint exists"""
        response = client.get("/api/v1/analysis/skills")
        assert response.status_code in [405, 422]  # Method not allowed or validation error
    
    @patch('services.comprehensive_analysis_service.ComprehensiveAnalysisService.analyze_job_market')
    def test_job_market_analysis_success(self, mock_analyze, client: TestClient, auth_headers):
        """Test successful job market analysis"""
        mock_analyze.return_value = {
            "total_jobs": 1500,
            "remote_jobs_percentage": 65.5,
            "top_companies": [
                {"name": "TechCorp", "job_count": 45},
                {"name": "StartupX", "job_count": 32}
            ],
            "salary_trends": {
                "average_salary": 85000,
                "salary_range": {"min": 60000, "max": 120000}
            },
            "job_categories": [
                {"category": "Software Development", "count": 450},
                {"category": "Data Science", "count": 200}
            ],
            "analysis_date": datetime.now().isoformat()
        }
        
        response = client.post(
            "/api/v1/analysis/job-market",
            json={
                "filters": {
                    "location": "Remote",
                    "job_type": "Full-time",
                    "experience_level": "Mid-level"
                }
            },
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "total_jobs" in data["data"]
        assert "remote_jobs_percentage" in data["data"]
        assert "top_companies" in data["data"]
        assert "salary_trends" in data["data"]
    
    @patch('services.comprehensive_analysis_service.ComprehensiveAnalysisService.analyze_skills_demand')
    def test_skill_analysis_success(self, mock_analyze, client: TestClient, auth_headers):
        """Test successful skill analysis"""
        mock_analyze.return_value = {
            "most_demanded_skills": [
                {"skill": "Python", "demand_score": 0.95, "job_count": 320},
                {"skill": "JavaScript", "demand_score": 0.88, "job_count": 280},
                {"skill": "React", "demand_score": 0.82, "job_count": 200}
            ],
            "emerging_skills": [
                {"skill": "Rust", "growth_rate": 0.45, "job_count": 25},
                {"skill": "Go", "growth_rate": 0.38, "job_count": 40}
            ],
            "skill_categories": {
                "programming_languages": ["Python", "JavaScript", "Java"],
                "frameworks": ["React", "Django", "Flask"],
                "databases": ["PostgreSQL", "MongoDB", "Redis"]
            },
            "analysis_date": datetime.now().isoformat()
        }
        
        response = client.post(
            "/api/v1/analysis/skills",
            json={
                "filters": {
                    "job_type": "Full-time",
                    "experience_level": "All"
                }
            },
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "most_demanded_skills" in data["data"]
        assert "emerging_skills" in data["data"]
        assert "skill_categories" in data["data"]
    
    @patch('services.comprehensive_analysis_service.ComprehensiveAnalysisService.comprehensive_analysis')
    def test_comprehensive_analysis_success(self, mock_analyze, client: TestClient, auth_headers):
        """Test successful comprehensive analysis"""
        mock_analyze.return_value = {
            "resume_summary": {
                "total_skills": 15,
                "experience_years": 5,
                "skill_match_percentage": 78.5
            },
            "job_recommendations": [
                {
                    "job_id": "job_1",
                    "title": "Senior Python Developer",
                    "match_score": 0.92,
                    "company": "TechCorp",
                    "salary_range": "$80K - $120K"
                }
            ],
            "salary_insights": {
                "predicted_salary": 95000,
                "market_average": 85000,
                "percentile": 75
            },
            "market_analysis": {
                "total_jobs": 1200,
                "remote_opportunities": 65,
                "top_skills_demand": ["Python", "React", "AWS"]
            },
            "career_recommendations": [
                "Consider learning cloud technologies",
                "Focus on system design skills",
                "Network with remote-first companies"
            ],
            "analysis_date": datetime.now().isoformat()
        }
        
        response = client.post(
            "/api/v1/analysis/comprehensive",
            json={
                "resume_data": {
                    "skills": ["Python", "JavaScript", "React"],
                    "experience": "5 years",
                    "education": "Bachelor's in Computer Science"
                },
                "preferences": {
                    "location": "Remote",
                    "salary_min": 70000,
                    "job_type": "Full-time"
                }
            },
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "resume_summary" in data["data"]
        assert "job_recommendations" in data["data"]
        assert "salary_insights" in data["data"]
        assert "market_analysis" in data["data"]
        assert "career_recommendations" in data["data"]
    
    def test_comprehensive_analysis_missing_resume_data(self, client: TestClient, auth_headers):
        """Test comprehensive analysis with missing resume data"""
        response = client.post(
            "/api/v1/analysis/comprehensive",
            json={
                "preferences": {
                    "location": "Remote",
                    "salary_min": 70000
                }
            },
            headers=auth_headers
        )
        
        assert response.status_code == 400
        data = response.json()
        assert "Resume data is required" in data["detail"]
    
    def test_job_market_analysis_invalid_filters(self, client: TestClient, auth_headers):
        """Test job market analysis with invalid filters"""
        response = client.post(
            "/api/v1/analysis/job-market",
            json={
                "filters": {
                    "invalid_field": "invalid_value"
                }
            },
            headers=auth_headers
        )
        
        # Should still work as filters are optional
        assert response.status_code == 200
    
    @patch('services.comprehensive_analysis_service.ComprehensiveAnalysisService.analyze_job_market')
    def test_job_market_analysis_empty_results(self, mock_analyze, client: TestClient, auth_headers):
        """Test job market analysis with no results"""
        mock_analyze.return_value = {
            "total_jobs": 0,
            "remote_jobs_percentage": 0,
            "top_companies": [],
            "salary_trends": {"average_salary": 0, "salary_range": {"min": 0, "max": 0}},
            "job_categories": [],
            "analysis_date": datetime.now().isoformat()
        }
        
        response = client.post(
            "/api/v1/analysis/job-market",
            json={
                "filters": {
                    "location": "Non-existent location"
                }
            },
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["total_jobs"] == 0
    
    def test_comprehensive_analysis_authentication_required(self, client: TestClient):
        """Test that comprehensive analysis endpoints require authentication"""
        endpoints = [
            ("/api/v1/analysis/comprehensive", "POST"),
            ("/api/v1/analysis/job-market", "POST"),
            ("/api/v1/analysis/skills", "POST")
        ]
        
        for endpoint, method in endpoints:
            if method == "POST":
                response = client.post(endpoint, json={})
            else:
                response = client.get(endpoint)
            
            assert response.status_code in [401, 422]  # Unauthorized or validation error
    
    @patch('services.comprehensive_analysis_service.ComprehensiveAnalysisService.comprehensive_analysis')
    def test_comprehensive_analysis_error_handling(self, mock_analyze, client: TestClient, auth_headers):
        """Test error handling in comprehensive analysis"""
        mock_analyze.side_effect = Exception("Analysis service unavailable")
        
        response = client.post(
            "/api/v1/analysis/comprehensive",
            json={
                "resume_data": {"skills": ["Python"]},
                "preferences": {"location": "Remote"}
            },
            headers=auth_headers
        )
        
        assert response.status_code == 500
        data = response.json()
        assert "Analysis service unavailable" in data["detail"]
    
    def test_skill_analysis_with_specific_skills(self, client: TestClient, auth_headers):
        """Test skill analysis with specific skills filter"""
        response = client.post(
            "/api/v1/analysis/skills",
            json={
                "filters": {
                    "skills": ["Python", "React"],
                    "job_type": "Full-time"
                }
            },
            headers=auth_headers
        )
        
        # Should work with specific skills filter
        assert response.status_code == 200
    
    @patch('services.comprehensive_analysis_service.ComprehensiveAnalysisService.analyze_job_market')
    def test_job_market_analysis_with_date_range(self, mock_analyze, client: TestClient, auth_headers):
        """Test job market analysis with date range filter"""
        mock_analyze.return_value = {
            "total_jobs": 500,
            "remote_jobs_percentage": 70,
            "top_companies": [],
            "salary_trends": {"average_salary": 80000, "salary_range": {"min": 60000, "max": 100000}},
            "job_categories": [],
            "analysis_date": datetime.now().isoformat()
        }
        
        response = client.post(
            "/api/v1/analysis/job-market",
            json={
                "filters": {
                    "date_from": "2024-01-01",
                    "date_to": "2024-12-31",
                    "location": "Remote"
                }
            },
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True 