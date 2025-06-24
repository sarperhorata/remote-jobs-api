import pytest
import asyncio
from httpx import AsyncClient
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime
from bson import ObjectId

from backend.main import app
from backend.database import get_async_db

class TestTranslationAPI:
    """Test suite for Translation API"""
    
    @pytest.fixture
    async def client(self):
        """Create test client"""
        async with AsyncClient(app=app, base_url="http://test") as ac:
            yield ac
    
    @pytest.fixture
    def mock_db(self):
        """Mock database"""
        db = AsyncMock()
        db.jobs = AsyncMock()
        db.system_config = AsyncMock()
        return db
    
    @pytest.fixture
    def mock_user(self):
        """Mock authenticated user"""
        return {
            "_id": "test_user_id",
            "email": "test@example.com",
            "name": "Test User"
        }
    
    @pytest.fixture
    def sample_turkish_job(self):
        """Sample Turkish job data"""
        return {
            "_id": ObjectId("507f1f77bcf86cd799439011"),
            "title": "Yazılım Geliştirici",
            "company": "Teknoloji Şirketi",
            "location": "İstanbul, Türkiye",
            "description": "Python ve Django ile web uygulamaları geliştiren yazılım geliştirici arıyoruz.",
            "requirements": "3+ yıl Python deneyimi",
            "benefits": "Sağlık sigortası, esnek çalışma",
            "jobType": "Tam zamanlı",
            "experienceLevel": "Orta seviye",
            "skills": ["Python", "Django", "PostgreSQL"],
            "isRemote": True,
            "original_language": "tr",
            "is_translated": False
        }
    
    @pytest.fixture
    def sample_english_job(self):
        """Sample English job data"""
        return {
            "_id": ObjectId("507f1f77bcf86cd799439012"),
            "title": "Software Developer",
            "company": "Tech Company",
            "location": "San Francisco, USA",
            "description": "We are looking for a software developer to build web applications using Python and Django.",
            "requirements": "3+ years Python experience",
            "benefits": "Health insurance, flexible work",
            "jobType": "Full-time",
            "experienceLevel": "Mid-level",
            "skills": ["Python", "Django", "PostgreSQL"],
            "isRemote": True,
            "original_language": "en",
            "is_translated": False
        }

    async def test_translate_text_success(self, client, mock_user):
        """Test successful text translation"""
        translation_request = {
            "text": "Merhaba dünya",
            "target_language": "en",
            "source_language": "tr"
        }
        
        # Mock translation service
        mock_result = {
            'translated_text': 'Hello world',
            'original_text': 'Merhaba dünya',
            'source_language': 'tr',
            'target_language': 'en',
            'translation_confidence': 0.85
        }
        
        with patch('backend.routes.translation.translation_service.translate_text', return_value=mock_result):
            with patch('backend.routes.translation.get_current_user_dependency', return_value=mock_user):
                response = await client.post("/api/translation/translate-text", json=translation_request)
        
        assert response.status_code == 200
        data = response.json()
        assert data["translated_text"] == "Hello world"
        assert data["original_text"] == "Merhaba dünya"
        assert data["source_language"] == "tr"
        assert data["target_language"] == "en"
        assert data["translation_confidence"] == 0.85

    async def test_translate_text_error(self, client, mock_user):
        """Test text translation error handling"""
        translation_request = {
            "text": "Test text",
            "target_language": "en"
        }
        
        with patch('backend.routes.translation.translation_service.translate_text', side_effect=Exception("Translation API error")):
            with patch('backend.routes.translation.get_current_user_dependency', return_value=mock_user):
                response = await client.post("/api/translation/translate-text", json=translation_request)
        
        assert response.status_code == 500
        data = response.json()
        assert "Translation failed" in data["detail"]

    async def test_detect_language_success(self, client, mock_user):
        """Test successful language detection"""
        with patch('backend.routes.translation.translation_service.detect_language', return_value=('tr', 0.9)):
            with patch('backend.routes.translation.get_current_user_dependency', return_value=mock_user):
                response = await client.post("/api/translation/detect-language", params={"text": "Merhaba dünya"})
        
        assert response.status_code == 200
        data = response.json()
        assert data["detected_language"] == "tr"
        assert data["confidence"] == 0.9
        assert "language_name" in data

    async def test_detect_language_error(self, client, mock_user):
        """Test language detection error handling"""
        with patch('backend.routes.translation.translation_service.detect_language', side_effect=Exception("Detection error")):
            with patch('backend.routes.translation.get_current_user_dependency', return_value=mock_user):
                response = await client.post("/api/translation/detect-language", params={"text": "Test text"})
        
        assert response.status_code == 500
        data = response.json()
        assert "Language detection failed" in data["detail"]

    async def test_get_supported_languages(self, client):
        """Test getting supported languages"""
        mock_languages = {
            'en': 'english',
            'tr': 'turkish',
            'es': 'spanish',
            'fr': 'french'
        }
        
        with patch('backend.routes.translation.translation_service.get_supported_languages', return_value=mock_languages):
            response = await client.get("/api/translation/supported-languages")
        
        assert response.status_code == 200
        data = response.json()
        assert "languages" in data
        assert "total_languages" in data
        assert data["total_languages"] == 4

    async def test_translate_job_success(self, client, mock_db, mock_user, sample_turkish_job):
        """Test successful job translation"""
        job_id = str(sample_turkish_job["_id"])
        
        # Mock database responses
        mock_db.jobs.find_one.return_value = sample_turkish_job
        mock_db.jobs.update_one.return_value = AsyncMock(modified_count=1)
        
        # Mock translation service
        mock_translation_result = {
            'needs_translation': True,
            'original_language': 'tr',
            'translated_data': {
                **sample_turkish_job,
                'title': 'Software Developer',
                'description': 'We are looking for a software developer...'
            },
            'original_data': sample_turkish_job,
            'translation_metadata': {
                'detected_language': 'tr',
                'translated_at': datetime.utcnow().isoformat(),
                'translation_required': True
            }
        }
        
        with patch('backend.routes.translation.get_async_db', return_value=mock_db):
            with patch('backend.routes.translation.translation_service.translate_job_listing', return_value=mock_translation_result):
                with patch('backend.routes.translation.get_current_user_dependency', return_value=mock_user):
                    response = await client.post(f"/api/translation/translate-job/{job_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["job_id"] == job_id
        assert data["needs_translation"] == True
        assert data["original_language"] == "tr"
        assert data["translated_data"] is not None
        assert data["original_data"] is not None
        
        # Verify database update was called
        mock_db.jobs.update_one.assert_called_once()

    async def test_translate_job_not_found(self, client, mock_db, mock_user):
        """Test job translation with non-existent job"""
        job_id = "507f1f77bcf86cd799439999"
        
        # Mock database to return None (job not found)
        mock_db.jobs.find_one.return_value = None
        
        with patch('backend.routes.translation.get_async_db', return_value=mock_db):
            with patch('backend.routes.translation.get_current_user_dependency', return_value=mock_user):
                response = await client.post(f"/api/translation/translate-job/{job_id}")
        
        assert response.status_code == 404
        data = response.json()
        assert "Job not found" in data["detail"]

    async def test_translate_job_no_translation_needed(self, client, mock_db, mock_user, sample_english_job):
        """Test job translation when no translation is needed"""
        job_id = str(sample_english_job["_id"])
        
        # Mock database responses
        mock_db.jobs.find_one.return_value = sample_english_job
        
        # Mock translation service to indicate no translation needed
        mock_translation_result = {
            'needs_translation': False,
            'original_language': 'en',
            'translated_data': sample_english_job,
            'original_data': sample_english_job,
            'translation_metadata': {
                'detected_language': 'en',
                'translation_required': False
            }
        }
        
        with patch('backend.routes.translation.get_async_db', return_value=mock_db):
            with patch('backend.routes.translation.translation_service.translate_job_listing', return_value=mock_translation_result):
                with patch('backend.routes.translation.get_current_user_dependency', return_value=mock_user):
                    response = await client.post(f"/api/translation/translate-job/{job_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["needs_translation"] == False
        assert data["original_language"] == "en"
        
        # Verify database update was NOT called
        mock_db.jobs.update_one.assert_not_called()

    async def test_batch_translate_jobs_success(self, client, mock_db, mock_user, sample_turkish_job, sample_english_job):
        """Test successful batch job translation"""
        job_ids = [str(sample_turkish_job["_id"]), str(sample_english_job["_id"])]
        batch_request = {
            "job_ids": job_ids,
            "target_language": "en",
            "batch_size": 2
        }
        
        # Mock database responses
        jobs_cursor = AsyncMock()
        jobs_cursor.__aiter__.return_value = iter([sample_turkish_job, sample_english_job])
        mock_db.jobs.find.return_value = jobs_cursor
        mock_db.jobs.update_one.return_value = AsyncMock(modified_count=1)
        
        # Mock translation service
        mock_translation_results = [
            {
                'needs_translation': True,
                'original_language': 'tr',
                'translated_data': {**sample_turkish_job, 'title': 'Software Developer'},
                'original_data': sample_turkish_job,
                'translation_metadata': {'detected_language': 'tr'}
            },
            {
                'needs_translation': False,
                'original_language': 'en',
                'translated_data': sample_english_job,
                'original_data': sample_english_job,
                'translation_metadata': {'detected_language': 'en'}
            }
        ]
        
        with patch('backend.routes.translation.get_async_db', return_value=mock_db):
            with patch('backend.routes.translation.translation_service.batch_translate_jobs', return_value=mock_translation_results):
                with patch('backend.routes.translation.get_current_user_dependency', return_value=mock_user):
                    response = await client.post("/api/translation/batch-translate", json=batch_request)
        
        assert response.status_code == 200
        data = response.json()
        assert data["total_jobs"] == 2
        assert data["translated_jobs"] == 1
        assert data["failed_jobs"] == 0
        assert len(data["results"]) == 2
        assert len(data["errors"]) == 0

    async def test_batch_translate_jobs_no_jobs_found(self, client, mock_db, mock_user):
        """Test batch translation with no jobs found"""
        batch_request = {
            "job_ids": ["507f1f77bcf86cd799439999"],
            "target_language": "en"
        }
        
        # Mock empty database response
        jobs_cursor = AsyncMock()
        jobs_cursor.__aiter__.return_value = iter([])
        mock_db.jobs.find.return_value = jobs_cursor
        
        with patch('backend.routes.translation.get_async_db', return_value=mock_db):
            with patch('backend.routes.translation.get_current_user_dependency', return_value=mock_user):
                response = await client.post("/api/translation/batch-translate", json=batch_request)
        
        assert response.status_code == 404
        data = response.json()
        assert "No jobs found" in data["detail"]

    async def test_batch_translate_with_errors(self, client, mock_db, mock_user, sample_turkish_job):
        """Test batch translation with some failures"""
        job_id = str(sample_turkish_job["_id"])
        batch_request = {
            "job_ids": [job_id],
            "target_language": "en"
        }
        
        # Mock database responses
        jobs_cursor = AsyncMock()
        jobs_cursor.__aiter__.return_value = iter([sample_turkish_job])
        mock_db.jobs.find.return_value = jobs_cursor
        mock_db.jobs.update_one.side_effect = Exception("Database error")
        
        # Mock translation service
        mock_translation_results = [
            {
                'needs_translation': True,
                'original_language': 'tr',
                'translated_data': {**sample_turkish_job, 'title': 'Software Developer'},
                'original_data': sample_turkish_job,
                'translation_metadata': {'detected_language': 'tr'}
            }
        ]
        
        with patch('backend.routes.translation.get_async_db', return_value=mock_db):
            with patch('backend.routes.translation.translation_service.batch_translate_jobs', return_value=mock_translation_results):
                with patch('backend.routes.translation.get_current_user_dependency', return_value=mock_user):
                    response = await client.post("/api/translation/batch-translate", json=batch_request)
        
        assert response.status_code == 200
        data = response.json()
        assert data["total_jobs"] == 1
        assert data["translated_jobs"] == 0
        assert data["failed_jobs"] == 1
        assert len(data["errors"]) == 1

    async def test_get_translation_stats(self, client, mock_db, mock_user):
        """Test getting translation statistics"""
        # Mock database aggregation responses
        mock_db.jobs.count_documents.side_effect = [1000, 600, 50]  # total, translated, failed
        
        # Mock aggregation pipeline for language stats
        mock_language_stats = [
            {"_id": "en", "count": 400},
            {"_id": "tr", "count": 300},
            {"_id": "es", "count": 200},
            {"_id": "fr", "count": 100}
        ]
        
        aggregation_cursor = AsyncMock()
        aggregation_cursor.__aiter__.return_value = iter(mock_language_stats)
        mock_db.jobs.aggregate.return_value = aggregation_cursor
        
        # Mock supported languages
        mock_languages = {
            'en': 'english',
            'tr': 'turkish',
            'es': 'spanish',
            'fr': 'french'
        }
        
        with patch('backend.routes.translation.get_async_db', return_value=mock_db):
            with patch('backend.routes.translation.translation_service.supported_languages', mock_languages):
                with patch('backend.routes.translation.get_current_user_dependency', return_value=mock_user):
                    response = await client.get("/api/translation/translation-stats")
        
        assert response.status_code == 200
        data = response.json()
        assert data["total_jobs"] == 1000
        assert data["translated_jobs"] == 600
        assert data["untranslated_jobs"] == 400
        assert data["translation_percentage"] == 60.0
        assert data["failed_translations"] == 50
        assert len(data["languages"]) == 4
        assert data["languages"][0]["language_code"] == "en"
        assert data["languages"][0]["job_count"] == 400

    async def test_setup_auto_translation(self, client, mock_db, mock_user):
        """Test setting up auto-translation"""
        # Mock database update
        mock_db.system_config.update_one.return_value = AsyncMock(modified_count=1)
        
        with patch('backend.routes.translation.get_async_db', return_value=mock_db):
            with patch('backend.routes.translation.get_current_user_dependency', return_value=mock_user):
                response = await client.post(
                    "/api/translation/auto-translate-new-jobs",
                    params={"enabled": True, "target_language": "en"}
                )
        
        assert response.status_code == 200
        data = response.json()
        assert "Auto-translation enabled" in data["message"]
        assert data["target_language"] == "en"
        assert "config" in data
        
        # Verify database update was called
        mock_db.system_config.update_one.assert_called_once()

    async def test_get_job_translation_history(self, client, mock_db, mock_user):
        """Test getting job translation history"""
        job_id = "507f1f77bcf86cd799439011"
        
        # Mock database response
        mock_job_data = {
            "_id": ObjectId(job_id),
            "is_translated": True,
            "original_language": "tr",
            "original_data": {
                "title": "Yazılım Geliştirici",
                "description": "Türkçe açıklama"
            },
            "translation_metadata": {
                "detected_language": "tr",
                "translated_at": "2024-01-15T10:00:00",
                "translation_required": True,
                "fields_translated": ["title", "description"]
            }
        }
        
        mock_db.jobs.find_one.return_value = mock_job_data
        
        with patch('backend.routes.translation.get_async_db', return_value=mock_db):
            with patch('backend.routes.translation.get_current_user_dependency', return_value=mock_user):
                response = await client.get(f"/api/translation/job-translation-history/{job_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["job_id"] == job_id
        assert data["is_translated"] == True
        assert data["original_language"] == "tr"
        assert data["has_original_data"] == True
        assert "translation_metadata" in data
        assert "original_data" in data

    async def test_get_job_translation_history_not_found(self, client, mock_db, mock_user):
        """Test getting translation history for non-existent job"""
        job_id = "507f1f77bcf86cd799439999"
        
        # Mock database to return None
        mock_db.jobs.find_one.return_value = None
        
        with patch('backend.routes.translation.get_async_db', return_value=mock_db):
            with patch('backend.routes.translation.get_current_user_dependency', return_value=mock_user):
                response = await client.get(f"/api/translation/job-translation-history/{job_id}")
        
        assert response.status_code == 404
        data = response.json()
        assert "Job not found" in data["detail"]

    async def test_translation_authentication_required(self, client):
        """Test that all translation endpoints require authentication"""
        endpoints = [
            ("POST", "/api/translation/translate-text", {"text": "test", "target_language": "en"}),
            ("POST", "/api/translation/detect-language", None),
            ("POST", "/api/translation/translate-job/test_id", None),
            ("POST", "/api/translation/batch-translate", {"job_ids": ["test"], "target_language": "en"}),
            ("GET", "/api/translation/translation-stats", None),
            ("POST", "/api/translation/auto-translate-new-jobs", None),
            ("GET", "/api/translation/job-translation-history/test_id", None)
        ]
        
        for method, endpoint, data in endpoints:
            if method == "POST":
                if data:
                    response = await client.post(endpoint, json=data)
                else:
                    response = await client.post(endpoint)
            else:
                response = await client.get(endpoint)
            
            # Should require authentication
            assert response.status_code in [401, 403, 422], f"Endpoint {endpoint} should require auth"

    async def test_invalid_job_id_format(self, client, mock_user):
        """Test handling of invalid job ID format"""
        invalid_job_id = "invalid_id"
        
        with patch('backend.routes.translation.get_current_user_dependency', return_value=mock_user):
            response = await client.post(f"/api/translation/translate-job/{invalid_job_id}")
        
        # Should handle ObjectId conversion error gracefully
        assert response.status_code in [400, 500]

    async def test_empty_batch_translation_request(self, client, mock_user):
        """Test batch translation with empty job list"""
        batch_request = {
            "job_ids": [],
            "target_language": "en"
        }
        
        with patch('backend.routes.translation.get_current_user_dependency', return_value=mock_user):
            response = await client.post("/api/translation/batch-translate", json=batch_request)
        
        # Should handle empty list gracefully
        assert response.status_code in [400, 404]

    async def test_translation_validation_errors(self, client, mock_user):
        """Test translation request validation"""
        # Missing required fields
        invalid_requests = [
            {},  # Empty request
            {"target_language": "en"},  # Missing text
            {"text": ""},  # Empty text
            {"text": "test", "target_language": "invalid_lang"}  # Invalid language code
        ]
        
        for invalid_request in invalid_requests:
            with patch('backend.routes.translation.get_current_user_dependency', return_value=mock_user):
                response = await client.post("/api/translation/translate-text", json=invalid_request)
            
            # Should return validation error
            assert response.status_code == 422

    async def test_concurrent_translation_requests(self, client, mock_user):
        """Test handling of concurrent translation requests"""
        translation_request = {
            "text": "Test concurrent translation",
            "target_language": "es"
        }
        
        mock_result = {
            'translated_text': 'Prueba de traducción concurrente',
            'original_text': 'Test concurrent translation',
            'source_language': 'en',
            'target_language': 'es',
            'translation_confidence': 0.85
        }
        
        with patch('backend.routes.translation.translation_service.translate_text', return_value=mock_result):
            with patch('backend.routes.translation.get_current_user_dependency', return_value=mock_user):
                # Send multiple concurrent requests
                tasks = [
                    client.post("/api/translation/translate-text", json=translation_request)
                    for _ in range(5)
                ]
                
                responses = await asyncio.gather(*tasks)
        
        # All requests should succeed
        for response in responses:
            assert response.status_code == 200
            data = response.json()
            assert data["translated_text"] == "Prueba de traducción concurrente"

# Integration tests
class TestTranslationIntegration:
    """Integration tests for complete translation workflow"""
    
    async def test_complete_job_translation_workflow(self, client):
        """Test complete job translation workflow from detection to storage"""
        # This would be a full integration test with real database
        # For now, we'll mock the entire flow
        
        mock_db = AsyncMock()
        mock_user = {"_id": "user1", "email": "test@example.com"}
        
        # Step 1: Detect non-English job
        job = {
            "_id": ObjectId("507f1f77bcf86cd799439011"),
            "title": "Desarrollador Full-Stack",
            "description": "Buscamos desarrollador con experiencia en React y Node.js"
        }
        
        # Step 2: Translate job
        mock_db.jobs.find_one.return_value = job
        mock_db.jobs.update_one.return_value = AsyncMock(modified_count=1)
        
        mock_translation_result = {
            'needs_translation': True,
            'original_language': 'es',
            'translated_data': {
                **job,
                'title': 'Full-Stack Developer',
                'description': 'We are looking for a developer with experience in React and Node.js'
            },
            'original_data': job,
            'translation_metadata': {
                'detected_language': 'es',
                'translated_at': datetime.utcnow().isoformat()
            }
        }
        
        with patch('backend.routes.translation.get_async_db', return_value=mock_db):
            with patch('backend.routes.translation.translation_service.translate_job_listing', return_value=mock_translation_result):
                with patch('backend.routes.translation.get_current_user_dependency', return_value=mock_user):
                    # Translate the job
                    response = await client.post("/api/translation/translate-job/507f1f77bcf86cd799439011")
                    
                    assert response.status_code == 200
                    data = response.json()
                    assert data["needs_translation"] == True
                    assert data["original_language"] == "es"
                    
                    # Verify translation was stored
                    mock_db.jobs.update_one.assert_called_once()
                    
                    # Get translation history
                    mock_db.jobs.find_one.return_value = {
                        **job,
                        "is_translated": True,
                        "original_language": "es",
                        "translation_metadata": mock_translation_result['translation_metadata']
                    }
                    
                    history_response = await client.get("/api/translation/job-translation-history/507f1f77bcf86cd799439011")
                    assert history_response.status_code == 200
                    history_data = history_response.json()
                    assert history_data["is_translated"] == True
                    assert history_data["original_language"] == "es"

if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 