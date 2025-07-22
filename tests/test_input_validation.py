import pytest
from unittest.mock import MagicMock, AsyncMock
from fastapi import Request, HTTPException
from backend.middleware.input_validation import InputValidationMiddleware

pytestmark = pytest.mark.asyncio

class TestInputValidation:
    """Test input validation middleware"""
    
    def test_validate_email_success(self):
        """Test successful email validation"""
        middleware = InputValidationMiddleware()
        
        valid_emails = [
            "test@example.com",
            "user.name@domain.co.uk",
            "user+tag@example.org",
            "123@test.com"
        ]
        
        for email in valid_emails:
            result = middleware.validate_email(email)
            assert result is True, f"Email {email} should be valid"
    
    def test_validate_email_failure(self):
        """Test failed email validation"""
        middleware = InputValidationMiddleware()
        
        invalid_emails = [
            "invalid-email",
            "@example.com",
            "test@",
            "",
            "test@.com"
        ]
        
        for email in invalid_emails:
            result = middleware.validate_email(email)
            assert result is False, f"Email {email} should be invalid"
    
    def test_validate_password_strength_success(self):
        """Test successful password strength validation"""
        middleware = InputValidationMiddleware()
        
        strong_passwords = [
            "StrongPass123!",
            "MySecureP@ssw0rd",
            "Complex#Password2024",
            "Test123!@#"
        ]
        
        for password in strong_passwords:
            result = middleware.validate_password_strength(password)
            assert result["valid"] is True, f"Password should be strong: {password}"
            assert len(result["errors"]) == 0
    
    def test_validate_password_strength_failure(self):
        """Test failed password strength validation"""
        middleware = InputValidationMiddleware()
        
        weak_passwords = [
            "weak",  # too short
            "onlylowercase",  # no uppercase, numbers, special chars
            "ONLYUPPERCASE",  # no lowercase, numbers, special chars
            "12345678",  # only numbers
            "!@#$%^&*",  # only special chars
            ""  # empty
        ]
        
        for password in weak_passwords:
            result = middleware.validate_password_strength(password)
            assert result["valid"] is False, f"Password should be weak: {password}"
            assert len(result["errors"]) > 0
    
    def test_sanitize_string_success(self):
        """Test successful string sanitization"""
        middleware = InputValidationMiddleware()
        
        test_cases = [
            ("<script>alert('xss')</script>", "alert('xss')"),
            ("Hello World", "Hello World"),
            ("Test & More", "Test & More"),
            ("", ""),
            ("   whitespace   ", "whitespace"),
            ("\n\t\r", ""),
            ("<b>bold</b>", "bold"),
            ("javascript:alert('xss')", "alert('xss')")
        ]
        
        for input_str, expected in test_cases:
            result = middleware.sanitize_string(input_str)
            assert result == expected, f"Input: '{input_str}' -> Expected: '{expected}', Got: '{result}'"
    
    def test_validate_url_success(self):
        """Test successful URL validation"""
        middleware = InputValidationMiddleware()
        
        valid_urls = [
            "https://example.com",
            "http://test.org",
            "https://api.example.com/v1",
            "http://localhost:3000",
            "https://www.google.com/search?q=test"
        ]
        
        for url in valid_urls:
            result = middleware.validate_url(url)
            assert result is True, f"URL should be valid: {url}"
    
    def test_validate_url_failure(self):
        """Test failed URL validation"""
        middleware = InputValidationMiddleware()
        
        invalid_urls = [
            "not-a-url",
            "ftp://example.com",
            "javascript:alert('xss')",
            "data:text/html,<script>alert('xss')</script>",
            "",
            "http://",
            "https://"
        ]
        
        for url in invalid_urls:
            result = middleware.validate_url(url)
            assert result is False, f"URL should be invalid: {url}"
    
    def test_validate_phone_success(self):
        """Test successful phone validation"""
        middleware = InputValidationMiddleware()
        
        valid_phones = [
            "+1234567890",
            "123-456-7890",
            "(123) 456-7890",
            "123.456.7890",
            "+1 234 567 8900"
        ]
        
        for phone in valid_phones:
            result = middleware.validate_phone(phone)
            assert result is True, f"Phone should be valid: {phone}"
    
    def test_validate_phone_failure(self):
        """Test failed phone validation"""
        middleware = InputValidationMiddleware()
        
        invalid_phones = [
            "not-a-phone",
            "123",
            "abc-def-ghij",
            "",
            "12345678901234567890"  # too long
        ]
        
        for phone in invalid_phones:
            result = middleware.validate_phone(phone)
            assert result is False, f"Phone should be invalid: {phone}"
    
    def test_calculate_password_strength(self):
        """Test password strength calculation"""
        middleware = InputValidationMiddleware()
        
        test_cases = [
            ("weak", "weak"),
            ("StrongPass123!", "very_strong"),
            ("MySecureP@ssw0rd", "very_strong"),
            ("12345678", "medium"),
            ("abcdefgh", "medium")
        ]
        
        for password, expected_strength in test_cases:
            result = middleware._calculate_password_strength(password)
            assert result == expected_strength, f"Password '{password}' should be {expected_strength}"
    
    async def test_middleware_call_next_success(self):
        """Test middleware successfully calls next"""
        middleware = InputValidationMiddleware()
        
        # Mock request
        mock_request = MagicMock()
        mock_request.method = "GET"
        mock_request.url.path = "/api/test"
        mock_request.query_params = {}
        mock_request.headers = {}
        
        # Mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        
        # Mock call_next
        mock_call_next = AsyncMock(return_value=mock_response)
        
        # Test middleware
        response = await middleware(mock_request, mock_call_next)
        
        assert response == mock_response
        mock_call_next.assert_called_once_with(mock_request)
    
    async def test_middleware_validation_error(self):
        """Test middleware raises validation error for dangerous input"""
        middleware = InputValidationMiddleware()
        
        # Mock request with dangerous input
        mock_request = MagicMock()
        mock_request.method = "POST"
        mock_request.url.path = "/api/test"
        mock_request.query_params = {"input": "<script>alert('xss')</script>"}
        mock_request.headers = {}
        
        # Mock call_next
        mock_call_next = AsyncMock()
        
        # Test middleware should raise HTTPException
        with pytest.raises(HTTPException) as exc_info:
            await middleware(mock_request, mock_call_next)
        
        assert exc_info.value.status_code == 400
        assert "Invalid input" in str(exc_info.value.detail)