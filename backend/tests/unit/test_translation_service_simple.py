import pytest
from backend.services.translation_service import TranslationService, translation_service

class TestTranslationServiceSimple:
    """Simple translation service tests"""
    
    def test_service_exists(self):
        """Test translation service exists"""
        assert translation_service is not None
        
    def test_service_is_instance(self):
        """Test service is TranslationService instance"""
        assert isinstance(translation_service, TranslationService)
        
    def test_service_has_methods(self):
        """Test service has required methods"""
        assert hasattr(translation_service, "translate_text")
        assert hasattr(translation_service, "detect_language")
        assert hasattr(translation_service, "translate_job_listing")
        
    def test_service_initialization(self):
        """Test service initializes without error"""
        service = TranslationService()
        assert service is not None
