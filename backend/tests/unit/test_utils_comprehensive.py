import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from backend.utils.auth import create_access_token, verify_password, get_password_hash
from backend.utils.email import send_email, send_verification_email
from backend.utils.config import get_settings, Settings
from backend.utils.html_cleaner import clean_html_tags, clean_job_data
from backend.utils.security import SecurityUtils
from datetime import datetime, timedelta
import os

class TestAuthUtils:
    """Test authentication utilities."""
    
    def test_create_access_token(self):
        """Test access token creation."""
        data = {"sub": "test@example.com"}
        token = create_access_token(data=data)
        
        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0
    
    def test_create_access_token_with_expires(self):
        """Test access token creation with custom expiration."""
        data = {"sub": "test@example.com"}
        expires_delta = timedelta(minutes=30)
        token = create_access_token(data=data, expires_delta=expires_delta)
        
        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0
    
    def test_verify_password(self):
        """Test password verification."""
        password = "testpassword123"
        hashed = get_password_hash(password)
        
        assert verify_password(password, hashed) is True
        assert verify_password("wrongpassword", hashed) is False
    
    def test_get_password_hash(self):
        """Test password hashing."""
        password = "testpassword123"
        hashed = get_password_hash(password)
        
        assert hashed is not None
        assert isinstance(hashed, str)
        assert hashed != password
        assert len(hashed) > len(password)

class TestEmailUtils:
    """Test email utilities."""
    
    @patch('backend.utils.email.mailgun_service.send_email')
    def test_send_email(self, mock_send):
        """Test email sending."""
        mock_send.return_value = {"success": True, "id": "test_id"}
        
        result = send_email(
            to_email="test@example.com",
            subject="Test Subject",
            body="Test Body"
        )
        
        assert result is True
        mock_send.assert_called_once()
    
    @patch('backend.utils.email.send_email')
    def test_send_verification_email(self, mock_send_email):
        """Test verification email sending."""
        mock_send_email.return_value = True
        
        result = send_verification_email("test@example.com", "verification_token_123")
        
        assert result is True
        mock_send_email.assert_called_once()
    
    def test_send_email_with_invalid_data(self):
        """Test email sending with invalid data."""
        result = send_email(
            to_email="",
            subject="",
            body=""
        )
        
        assert result is False
    
    @patch('backend.utils.email.mailgun_service.send_email')
    def test_send_email_service_error(self, mock_send):
        """Test email sending with service error."""
        mock_send.side_effect = Exception("Service Error")
        
        result = send_email(
            to_email="test@example.com",
            subject="Test Subject",
            body="Test Body"
        )
        
        assert result is False

class TestConfigUtils:
    """Test configuration utilities."""
    
    def test_get_settings(self):
        """Test settings retrieval."""
        settings = get_settings()
        
        assert settings is not None
        assert isinstance(settings, Settings)
        assert hasattr(settings, 'DATABASE_URL')
        assert hasattr(settings, 'SECRET_KEY')
    
    def test_settings_environment_variables(self):
        """Test settings environment variable handling."""
        # Test with environment variables
        os.environ["TEST_VAR"] = "test_value"
        
        settings = get_settings()
        
        assert settings is not None
        # Clean up
        del os.environ["TEST_VAR"]
    
    def test_settings_default_values(self):
        """Test settings default values."""
        settings = get_settings()
        
        # Test that required fields have default values
        assert settings.DATABASE_URL is not None
        assert settings.SECRET_KEY is not None
        assert settings.ALGORITHM is not None
        assert settings.ACCESS_TOKEN_EXPIRE_MINUTES is not None

class TestHtmlCleanerUtils:
    """Test HTML cleaning utilities."""
    
    def test_clean_html_tags(self):
        """Test HTML tag cleaning."""
        dirty_html = "<p>Test <script>alert('xss')</script> content</p>"
        cleaned = clean_html_tags(dirty_html)
        
        assert cleaned is not None
        assert isinstance(cleaned, str)
        assert "<script>" not in cleaned
        assert "Test" in cleaned
        assert "content" in cleaned
    
    def test_clean_html_tags_with_complex_html(self):
        """Test HTML tag cleaning with complex HTML."""
        dirty_html = "<p>Test <b>bold</b> <i>italic</i> content</p>"
        cleaned = clean_html_tags(dirty_html)
        
        assert cleaned is not None
        assert "<b>" not in cleaned
        assert "<i>" not in cleaned
        assert "Test" in cleaned
        assert "bold" in cleaned
        assert "italic" in cleaned
    
    def test_clean_html_tags_empty_input(self):
        """Test HTML tag cleaning with empty input."""
        cleaned = clean_html_tags("")
        
        assert cleaned is not None
        assert cleaned == ""
    
    def test_clean_html_tags_none_input(self):
        """Test HTML tag cleaning with None input."""
        cleaned = clean_html_tags(None)
        
        assert cleaned is not None
        assert cleaned == ""
    
    def test_clean_job_data(self):
        """Test job data cleaning."""
        job_data = {
            "title": "<script>alert('xss')</script>Test Job",
            "description": "<p>Test description</p>",
            "requirements": "<b>Python</b> <script>malicious</script>"
        }
        
        cleaned = clean_job_data(job_data)
        
        assert cleaned is not None
        assert isinstance(cleaned, dict)
        assert "<script>" not in cleaned["title"]
        assert "Test Job" in cleaned["title"]
        assert "<script>" not in cleaned["requirements"]
        assert "Python" in cleaned["requirements"]
    
    def test_clean_job_data_nested(self):
        """Test job data cleaning with nested structures."""
        job_data = {
            "title": "Test Job",
            "details": {
                "description": "<script>alert('xss')</script>Description",
                "requirements": ["<b>Python</b>", "<script>malicious</script>JavaScript"]
            }
        }
        
        cleaned = clean_job_data(job_data)
        
        assert cleaned is not None
        assert "<script>" not in cleaned["details"]["description"]
        assert "<script>" not in str(cleaned["details"]["requirements"])

class TestSecurityUtils:
    """Test security utilities."""
    
    def test_validate_password(self):
        """Test password validation."""
        # Test strong password
        strong_password = "StrongPass123!"
        result = SecurityUtils.validate_password(strong_password)
        assert result is True
        
        # Test weak password
        weak_password = "123"
        result = SecurityUtils.validate_password(weak_password)
        assert result is False
    
    def test_validate_password_edge_cases(self):
        """Test password validation edge cases."""
        # Test empty password
        result = SecurityUtils.validate_password("")
        assert result is False
        
        # Test None password
        result = SecurityUtils.validate_password(None)
        assert result is False
        
        # Test very long password
        long_password = "a" * 1000 + "A1!"
        result = SecurityUtils.validate_password(long_password)
        assert result is True
    
    def test_sanitize_input(self):
        """Test input sanitization."""
        # Test SQL injection attempt
        malicious_input = "'; DROP TABLE users; --"
        sanitized = SecurityUtils.sanitize_input(malicious_input)
        
        assert sanitized is not None
        assert isinstance(sanitized, str)
        assert "DROP TABLE" not in sanitized
        
        # Test XSS attempt
        xss_input = "<script>alert('xss')</script>"
        sanitized = SecurityUtils.sanitize_input(xss_input)
        
        assert "<script>" not in sanitized
    
    def test_sanitize_input_edge_cases(self):
        """Test input sanitization edge cases."""
        # Test empty input
        sanitized = SecurityUtils.sanitize_input("")
        assert sanitized == ""
        
        # Test None input
        sanitized = SecurityUtils.sanitize_input(None)
        assert sanitized == ""
        
        # Test normal input
        normal_input = "This is normal text"
        sanitized = SecurityUtils.sanitize_input(normal_input)
        assert sanitized == normal_input
    
    def test_sanitize_input_special_characters(self):
        """Test input sanitization with special characters."""
        special_input = "Test & < > \" ' characters"
        sanitized = SecurityUtils.sanitize_input(special_input)
        
        assert sanitized is not None
        assert isinstance(sanitized, str)
        # Should preserve safe characters
        assert "Test" in sanitized
        assert "characters" in sanitized
    
    def test_validate_email(self):
        """Test email validation."""
        # Test valid email
        valid_email = "test@example.com"
        result = SecurityUtils.validate_email(valid_email)
        assert result is True
        
        # Test invalid email
        invalid_email = "invalid-email"
        result = SecurityUtils.validate_email(invalid_email)
        assert result is False
    
    def test_validate_phone(self):
        """Test phone validation."""
        # Test valid phone
        valid_phone = "+1234567890"
        result = SecurityUtils.validate_phone(valid_phone)
        assert result is True
        
        # Test invalid phone
        invalid_phone = "123"
        result = SecurityUtils.validate_phone(invalid_phone)
        assert result is False
    
    def test_generate_csrf_token(self):
        """Test CSRF token generation."""
        token = SecurityUtils.generate_csrf_token()
        
        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0
    
    def test_verify_csrf_token(self):
        """Test CSRF token verification."""
        token = SecurityUtils.generate_csrf_token()
        
        # Test valid token
        result = SecurityUtils.verify_csrf_token(token)
        assert result is True
        
        # Test invalid token
        result = SecurityUtils.verify_csrf_token("invalid_token")
        assert result is False
    
    def test_get_secure_headers(self):
        """Test secure headers generation."""
        headers = SecurityUtils.get_secure_headers()
        
        assert isinstance(headers, dict)
        assert "X-Content-Type-Options" in headers
        assert "X-Frame-Options" in headers
        assert "X-XSS-Protection" in headers
    
    def test_check_rate_limit(self):
        """Test rate limiting."""
        ip = "192.168.1.1"
        endpoint = "/api/test"
        
        # Test first request
        is_within_limit, remaining = SecurityUtils.check_rate_limit(ip, endpoint, limit=5)
        assert is_within_limit is True
        assert remaining == 4
        
        # Test multiple requests
        for i in range(4):
            is_within_limit, remaining = SecurityUtils.check_rate_limit(ip, endpoint, limit=5)
            assert is_within_limit is True
        
        # Test limit exceeded
        is_within_limit, remaining = SecurityUtils.check_rate_limit(ip, endpoint, limit=5)
        assert is_within_limit is False
        assert remaining == 0

class TestIntegrationUtils:
    """Test utility integration scenarios."""
    
    def test_auth_email_integration(self):
        """Test authentication and email integration."""
        # Create user data
        email = "test@example.com"
        password = "StrongPass123!"
        
        # Test password hashing and verification
        hashed = get_password_hash(password)
        assert verify_password(password, hashed) is True
        
        # Test token creation
        token = create_access_token(data={"sub": email})
        assert token is not None
        
        # Test email sending (mocked)
        with patch('backend.utils.email.mailgun_service.send_email') as mock_send:
            mock_send.return_value = {"success": True}
            result = send_email(email, "Welcome", "Welcome to our platform!")
            assert result is True
    
    def test_security_html_integration(self):
        """Test security and HTML cleaning integration."""
        # Test malicious input through HTML cleaning
        malicious_data = {
            "title": "<script>alert('xss')</script>Job Title",
            "description": "'; DROP TABLE jobs; -- Description"
        }
        
        # Clean the data
        cleaned = clean_job_data(malicious_data)
        
        # Validate the cleaned data
        assert "<script>" not in cleaned["title"]
        assert "DROP TABLE" not in cleaned["description"]
        assert "Job Title" in cleaned["title"]
        assert "Description" in cleaned["description"]
        
        # Test password validation for the same user
        password = "WeakPass"
        strength = SecurityUtils.validate_password(password)
        assert strength is False
    
    def test_config_security_integration(self):
        """Test configuration and security integration."""
        # Get settings
        settings = get_settings()
        
        # Test that security settings are properly configured
        assert settings.SECRET_KEY is not None
        assert len(settings.SECRET_KEY) >= 32
        assert settings.ALGORITHM is not None
        
        # Test password validation with configured settings
        password = "TestPassword123!"
        strength = SecurityUtils.validate_password(password)
        assert strength is True
        
        # Test token creation with settings
        token = create_access_token(
            data={"sub": "test@example.com"},
            expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        assert token is not None 