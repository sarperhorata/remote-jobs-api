import pytest
from backend.models.models import User, TranslationRequest

class TestUserModel:
    def test_user_creation(self):
        user = User(email="test@example.com")
        assert user.email == "test@example.com"
        assert user.is_active is True
        
    def test_user_defaults(self):
        user = User(email="test@example.com")
        assert user.onboarding_step == 0
        assert user.email_verified is False

class TestTranslationModels:
    def test_translation_request(self):
        request = TranslationRequest(text="Hello world")
        assert request.text == "Hello world"
        assert request.target_language == "en"
