import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch, AsyncMock
import json
from datetime import datetime

class TestTranslationRoutes:
    """Test translation routes"""
    
    def test_translate_job_endpoint_exists(self, client: TestClient):
        """Test that translate job endpoint exists"""
        response = client.get("/api/v1/translation/translate-job")
        assert response.status_code in [405, 422]  # Method not allowed or validation error
    
    def test_auto_translate_new_jobs_endpoint_exists(self, client: TestClient):
        """Test that auto translate new jobs endpoint exists"""
        response = client.get("/api/v1/translation/auto-translate-new-jobs")
        assert response.status_code in [405, 422]  # Method not allowed or validation error
    
    @patch('services.translation_service.TranslationService.translate_job')
    def test_translate_job_success(self, mock_translate, client: TestClient, auth_headers):
        """Test successful job translation"""
        mock_translate.return_value = {
            "needs_translation": True,
            "translated_data": {
                "title": "Software Developer",
                "description": "We are looking for a skilled software developer",
                "requirements": "Python, JavaScript experience required"
            },
            "original_data": {
                "title": "Développeur de logiciels",
                "description": "Nous recherchons un développeur de logiciels qualifié",
                "requirements": "Expérience Python, JavaScript requise"
            },
            "original_language": "fr",
            "translation_metadata": {
                "translated_at": datetime.now().isoformat(),
                "source_language": "fr",
                "target_language": "en"
            }
        }
        
        response = client.post(
            "/api/v1/translation/translate-job",
            json={"job_id": "test_job_123"},
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "translated_data" in data["data"]
        assert "original_data" in data["data"]
        assert "original_language" in data["data"]
    
    def test_translate_job_not_found(self, client: TestClient, auth_headers):
        """Test job translation with non-existent job"""
        response = client.post(
            "/api/v1/translation/translate-job",
            json={"job_id": "non_existent_job"},
            headers=auth_headers
        )
        
        assert response.status_code == 404
        data = response.json()
        assert "Job not found" in data["detail"]
    
    @patch('services.translation_service.TranslationService.batch_translate_jobs')
    def test_auto_translate_new_jobs_success(self, mock_batch_translate, client: TestClient, auth_headers):
        """Test successful auto translation of new jobs"""
        mock_batch_translate.return_value = [
            {
                "job_id": "job_1",
                "needs_translation": True,
                "translated_data": {
                    "title": "Python Developer",
                    "description": "Remote Python developer position"
                },
                "original_data": {
                    "title": "Développeur Python",
                    "description": "Poste de développeur Python à distance"
                },
                "original_language": "fr",
                "translation_metadata": {
                    "translated_at": datetime.now().isoformat(),
                    "source_language": "fr",
                    "target_language": "en"
                }
            },
            {
                "job_id": "job_2",
                "needs_translation": False,
                "translated_data": None,
                "original_data": None,
                "original_language": "en",
                "translation_metadata": None
            }
        ]
        
        response = client.post(
            "/api/v1/translation/auto-translate-new-jobs",
            params={"max_jobs": 20},
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "processed" in data
        assert "translated" in data
    
    def test_auto_translate_no_new_jobs(self, client: TestClient, auth_headers):
        """Test auto translation when no new jobs need translation"""
        response = client.post(
            "/api/v1/translation/auto-translate-new-jobs",
            params={"max_jobs": 10},
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "No new jobs requiring translation found" in data["message"]
    
    def test_translate_job_missing_job_id(self, client: TestClient, auth_headers):
        """Test job translation with missing job ID"""
        response = client.post(
            "/api/v1/translation/translate-job",
            json={},  # Empty request
            headers=auth_headers
        )
        
        assert response.status_code == 422  # Validation error
    
    def test_auto_translate_invalid_max_jobs(self, client: TestClient, auth_headers):
        """Test auto translation with invalid max_jobs parameter"""
        response = client.post(
            "/api/v1/translation/auto-translate-new-jobs",
            params={"max_jobs": 150},  # Exceeds limit
            headers=auth_headers
        )
        
        assert response.status_code == 422  # Validation error
    
    @patch('services.translation_service.TranslationService.translate_job')
    def test_translate_job_already_translated(self, mock_translate, client: TestClient, auth_headers):
        """Test translation of already translated job"""
        mock_translate.return_value = {
            "needs_translation": False,
            "translated_data": None,
            "original_data": None,
            "original_language": "en",
            "translation_metadata": None
        }
        
        response = client.post(
            "/api/v1/translation/translate-job",
            json={"job_id": "already_translated_job"},
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["needs_translation"] is False
    
    def test_translation_authentication_required(self, client: TestClient):
        """Test that translation endpoints require authentication"""
        endpoints = [
            ("/api/v1/translation/translate-job", "POST"),
            ("/api/v1/translation/auto-translate-new-jobs", "POST")
        ]
        
        for endpoint, method in endpoints:
            if method == "POST":
                response = client.post(endpoint, json={})
            else:
                response = client.get(endpoint)
            
            assert response.status_code in [401, 422]  # Unauthorized or validation error
    
    @patch('services.translation_service.TranslationService.translate_job')
    def test_translate_job_error_handling(self, mock_translate, client: TestClient, auth_headers):
        """Test error handling in job translation"""
        mock_translate.side_effect = Exception("Translation service unavailable")
        
        response = client.post(
            "/api/v1/translation/translate-job",
            json={"job_id": "test_job_123"},
            headers=auth_headers
        )
        
        assert response.status_code == 500
        data = response.json()
        assert "Translation service unavailable" in data["detail"]
    
    def test_translate_job_invalid_job_id_format(self, client: TestClient, auth_headers):
        """Test job translation with invalid job ID format"""
        response = client.post(
            "/api/v1/translation/translate-job",
            json={"job_id": ""},  # Empty job ID
            headers=auth_headers
        )
        
        assert response.status_code == 422  # Validation error
    
    @patch('services.translation_service.TranslationService.batch_translate_jobs')
    def test_auto_translate_batch_processing(self, mock_batch_translate, client: TestClient, auth_headers):
        """Test batch processing in auto translation"""
        # Mock multiple job translations
        mock_results = []
        for i in range(5):
            mock_results.append({
                "job_id": f"job_{i}",
                "needs_translation": True,
                "translated_data": {"title": f"Translated Job {i}"},
                "original_data": {"title": f"Original Job {i}"},
                "original_language": "fr",
                "translation_metadata": {
                    "translated_at": datetime.now().isoformat(),
                    "source_language": "fr",
                    "target_language": "en"
                }
            })
        
        mock_batch_translate.return_value = mock_results
        
        response = client.post(
            "/api/v1/translation/auto-translate-new-jobs",
            params={"max_jobs": 5},
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["processed"] == 5
        assert data["translated"] == 5 