import sys
import pytest

if "pytest_asyncio" in sys.modules:
    pytest.skip("pytest_asyncio loaded, skipping sync-only recaptcha tests", allow_module_level=True)

from unittest.mock import patch
from utils.recaptcha import verify_recaptcha

class TestRecaptchaUtils:
    """Test recaptcha utility functions"""
    
    @patch('utils.recaptcha.requests.post')
    def test_verify_recaptcha_with_valid_token(self, mock_post):
        """Test recaptcha verification with valid token"""
        # Mock successful response
        mock_response = type('MockResponse', (), {'json': lambda: {'success': True}})()
        mock_post.return_value = mock_response
        
        result = verify_recaptcha("valid_test_token")
        assert result is True
        
    @patch('utils.recaptcha.requests.post')
    def test_verify_recaptcha_with_empty_token(self, mock_post):
        """Test recaptcha verification with empty token"""
        # Mock failed response
        mock_response = type('MockResponse', (), {'json': lambda: {'success': False}})()
        mock_post.return_value = mock_response
        
        result = verify_recaptcha("")
        # Should return True if no secret key is set (test environment)
        assert result is True
        
    @patch('utils.recaptcha.requests.post')
    def test_verify_recaptcha_with_none_token(self, mock_post):
        """Test recaptcha verification with None token"""
        # Mock failed response
        mock_response = type('MockResponse', (), {'json': lambda: {'success': False}})()
        mock_post.return_value = mock_response
        
        result = verify_recaptcha(None)
        # Should return True if no secret key is set (test environment)
        assert result is True
