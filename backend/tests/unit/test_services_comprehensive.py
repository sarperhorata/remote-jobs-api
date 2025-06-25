import pytest
from backend.services.translation_service import translation_service

class TestTranslationService:
    def test_service_exists(self):
        assert translation_service is not None
        
    def test_supported_languages(self):
        assert hasattr(translation_service, "supported_languages")
        
    def test_service_methods_exist(self):
        assert hasattr(translation_service, "translate_text")
