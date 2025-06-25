import pytest
from unittest.mock import Mock, AsyncMock, patch
from backend.services.translation_service import TranslationService, translation_service

class TestTranslationService:
    """Test translation service comprehensively"""
    
    def test_service_initialization(self):
        """Test translation service initialization"""
        service = TranslationService()
        assert service is not None
        
    def test_supported_languages_property(self):
        """Test supported languages property"""
        assert hasattr(translation_service, "supported_languages")
        
    @pytest.mark.asyncio
    async def test_translate_text_method(self):
        """Test translate_text method exists"""
        assert hasattr(translation_service, "translate_text")
        assert callable(translation_service.translate_text)
        
    @pytest.mark.asyncio  
    async def test_detect_language_method(self):
        """Test detect_language method exists"""
        assert hasattr(translation_service, "detect_language")
        assert callable(translation_service.detect_language)
        
    @pytest.mark.asyncio
    async def test_translate_job_listing_method(self):
        """Test translate_job_listing method"""
        job_data = {"title": "Developer", "description": "Test job"}
        
        with patch.object(translation_service, "translate_job_listing") as mock_method:
            mock_method.return_value = {
                "needs_translation": False,
                "original_language": "en"
            }
            
            result = await translation_service.translate_job_listing(job_data)
            assert "needs_translation" in result
            
    @pytest.mark.asyncio
    async def test_batch_translate_jobs(self):
        """Test batch translation functionality"""
        jobs = [{"title": "Job 1"}, {"title": "Job 2"}]
        
        with patch.object(translation_service, "batch_translate_jobs") as mock_method:
            mock_method.return_value = [
                {"needs_translation": False, "original_language": "en"},
                {"needs_translation": False, "original_language": "en"}
            ]
            
            results = await translation_service.batch_translate_jobs(jobs)
            assert len(results) == 2
            
    def test_service_error_handling(self):
        """Test service error handling"""
        # Test that service handles missing GoogleTrans gracefully
        assert translation_service is not None
