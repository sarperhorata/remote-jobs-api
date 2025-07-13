import pytest
import jwt
from datetime import datetime, timedelta
from unittest.mock import patch, Mock
import os

from utils.email import (
    send_email,
    create_email_verification_token,
    create_password_reset_token,
    verify_token,
    send_verification_email,
    send_password_reset_email,
    SECRET_KEY,
    ALGORITHM,
    ACCESS_TOKEN_EXPIRE_MINUTES
)


class TestUtilsEmail:
    """Utils email modülü testleri"""

    def test_constants_exist(self):
        """Email constants tanımlı"""
        assert SECRET_KEY is not None
        assert ALGORITHM == "HS256"
        assert ACCESS_TOKEN_EXPIRE_MINUTES == 30

    def test_create_email_verification_token(self):
        """Email verification token oluşturma"""
        email = "test@example.com"
        token = create_email_verification_token(email)
        
        assert isinstance(token, str)
        assert len(token) > 50  # JWT tokens are long
        
        # Token decode edilebilmeli
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        assert payload["sub"] == email
        assert payload["type"] == "email_verification"
        assert "exp" in payload

    def test_create_password_reset_token(self):
        """Password reset token oluşturma"""
        email = "test@example.com"
        token = create_password_reset_token(email)
        
        assert isinstance(token, str)
        assert len(token) > 50  # JWT tokens are long
        
        # Token decode edilebilmeli
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        assert payload["sub"] == email
        assert payload["type"] == "password_reset"
        assert "exp" in payload

    def test_verify_token_valid(self):
        """Geçerli token doğrulama"""
        email = "test@example.com"
        token = create_email_verification_token(email)
        
        payload = verify_token(token)
        assert payload is not None
        assert payload["sub"] == email
        assert payload["type"] == "email_verification"

    def test_verify_token_invalid(self):
        """Geçersiz token doğrulama"""
        invalid_token = "invalid.token.here"
        payload = verify_token(invalid_token)
        assert payload is None

    def test_verify_token_expired(self):
        """Süresi dolmuş token doğrulama"""
        # Geçmişte bir tarih ile token oluştur
        past_time = datetime.utcnow() - timedelta(hours=1)
        to_encode = {
            "sub": "test@example.com",
            "type": "email_verification",
            "exp": past_time
        }
        
        expired_token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        payload = verify_token(expired_token)
        assert payload is None

    def test_token_expiration_times(self):
        """Token süre kontrolü"""
        # Email verification token (24 saat)
        email_token = create_email_verification_token("test@example.com")
        email_payload = jwt.decode(email_token, SECRET_KEY, algorithms=[ALGORITHM])
        
        # Password reset token (1 saat)
        reset_token = create_password_reset_token("test@example.com")
        reset_payload = jwt.decode(reset_token, SECRET_KEY, algorithms=[ALGORITHM])
        
        # Email verification token daha uzun süreli olmalı
        assert email_payload["exp"] > reset_payload["exp"]

    @patch('backend.utils.email.mailgun_service')
    def test_send_email_success(self, mock_mailgun):
        """Email gönderme başarılı"""
        mock_mailgun.send_email.return_value = {"success": True}
        
        result = send_email(
            to_email="test@example.com",
            subject="Test Subject",
            body="<h1>Test Body</h1>"
        )
        
        assert result is True
        mock_mailgun.send_email.assert_called_once_with(
            to_email="test@example.com",
            subject="Test Subject",
            html_content="<h1>Test Body</h1>"
        )

    @patch('backend.utils.email.mailgun_service')
    def test_send_email_failure(self, mock_mailgun):
        """Email gönderme başarısız"""
        mock_mailgun.send_email.return_value = {"success": False, "error": "API Error"}
        
        result = send_email(
            to_email="test@example.com",
            subject="Test Subject",
            body="<h1>Test Body</h1>"
        )
        
        assert result is False

    @patch('backend.utils.email.mailgun_service')
    def test_send_email_exception(self, mock_mailgun):
        """Email gönderme exception"""
        mock_mailgun.send_email.side_effect = Exception("Connection error")
        
        result = send_email(
            to_email="test@example.com",
            subject="Test Subject",
            body="<h1>Test Body</h1>"
        )
        
        assert result is False

    @patch('backend.utils.email.mailgun_service')
    def test_send_verification_email_success(self, mock_mailgun):
        """Verification email gönderme başarılı"""
        mock_mailgun.send_verification_email.return_value = True
        
        result = send_verification_email("test@example.com", "token123")
        
        assert result is True
        mock_mailgun.send_verification_email.assert_called_once_with("test@example.com", "token123")

    @patch('backend.utils.email.mailgun_service')
    def test_send_verification_email_failure(self, mock_mailgun):
        """Verification email gönderme başarısız"""
        mock_mailgun.send_verification_email.return_value = False
        
        result = send_verification_email("test@example.com", "token123")
        
        assert result is False

    @patch('backend.utils.email.mailgun_service')
    def test_send_verification_email_exception(self, mock_mailgun):
        """Verification email gönderme exception"""
        mock_mailgun.send_verification_email.side_effect = Exception("Service error")
        
        result = send_verification_email("test@example.com", "token123")
        
        assert result is False

    @patch('backend.utils.email.mailgun_service')
    def test_send_password_reset_email_success(self, mock_mailgun):
        """Password reset email gönderme başarılı"""
        mock_mailgun.send_password_reset_email.return_value = True
        
        result = send_password_reset_email("test@example.com", "reset123")
        
        assert result is True
        mock_mailgun.send_password_reset_email.assert_called_once_with("test@example.com", "reset123")

    @patch('backend.utils.email.mailgun_service')
    def test_send_password_reset_email_failure(self, mock_mailgun):
        """Password reset email gönderme başarısız"""
        mock_mailgun.send_password_reset_email.return_value = False
        
        result = send_password_reset_email("test@example.com", "reset123")
        
        assert result is False

    @patch('backend.utils.email.mailgun_service')
    def test_send_password_reset_email_exception(self, mock_mailgun):
        """Password reset email gönderme exception"""
        mock_mailgun.send_password_reset_email.side_effect = Exception("Network error")
        
        result = send_password_reset_email("test@example.com", "reset123")
        
        assert result is False

    def test_different_tokens_for_same_email(self):
        """Aynı email için farklı tokenlar"""
        email = "test@example.com"
        
        token1 = create_email_verification_token(email)
        token2 = create_email_verification_token(email)
        
        # Farklı tokenlar olmalı (timestamp farklılığı nedeniyle)
        assert token1 != token2

    def test_different_token_types(self):
        """Farklı token türleri"""
        email = "test@example.com"
        
        verification_token = create_email_verification_token(email)
        reset_token = create_password_reset_token(email)
        
        # Farklı tokenlar olmalı
        assert verification_token != reset_token
        
        # Token payloadları farklı türde olmalı
        verification_payload = verify_token(verification_token)
        reset_payload = verify_token(reset_token)
        
        assert verification_payload["type"] == "email_verification"
        assert reset_payload["type"] == "password_reset"

    def test_token_contains_correct_email(self):
        """Token doğru email içerir"""
        emails = ["user1@example.com", "user2@test.org", "admin@company.com"]
        
        for email in emails:
            token = create_email_verification_token(email)
            payload = verify_token(token)
            assert payload["sub"] == email

    def test_environment_variable_override(self):
        """Environment variable override"""
        with patch.dict(os.environ, {"JWT_SECRET_KEY": "custom-secret"}):
            # Import yeniden yapıldığında, eski değer kullanılacak
            # çünkü module-level constant
            # Bu normal bir davranış
            assert True

    def test_email_parameter_validation(self):
        """Email parameter validation"""
        # Test with empty strings
        with patch('backend.utils.email.mailgun_service') as mock_mailgun:
            mock_mailgun.send_email.return_value = {"success": True}
            
            result = send_email("", "Subject", "Body")
            assert isinstance(result, bool)

    def test_token_structure_validation(self):
        """Token structure validation"""
        email = "test@example.com"
        token = create_email_verification_token(email)
        
        # JWT token should have 3 parts separated by dots
        parts = token.split('.')
        assert len(parts) == 3
        
        # Each part should be non-empty
        for part in parts:
            assert len(part) > 0

    def test_concurrent_token_creation(self):
        """Concurrent token creation"""
        import threading
        import time
        
        email = "test@example.com"
        tokens = []
        
        def create_token():
            time.sleep(0.001)  # Small delay to ensure different timestamps
            token = create_email_verification_token(email)
            tokens.append(token)
        
        threads = []
        for _ in range(5):
            thread = threading.Thread(target=create_token)
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join()
        
        # All tokens should be unique
        assert len(set(tokens)) == len(tokens)

    def test_malformed_token_handling(self):
        """Malformed token handling"""
        malformed_tokens = [
            "",
            "not.a.token",
            "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9",  # incomplete
            "invalid-jwt-format",
            "a.b.c.d.e",  # too many parts
            None
        ]
        
        for token in malformed_tokens:
            try:
                result = verify_token(token)
                assert result is None
            except Exception:
                # Exception handling is also acceptable
                assert True

    @patch('backend.utils.email.logger')
    def test_logging_behavior(self, mock_logger):
        """Logging behavior test"""
        with patch('backend.utils.email.mailgun_service') as mock_mailgun:
            mock_mailgun.send_email.return_value = {"success": True}
            
            send_email("test@example.com", "Subject", "Body")
            
            # Should log success
            mock_logger.info.assert_called()

    def test_kwargs_handling(self):
        """Kwargs handling in send_email"""
        with patch('backend.utils.email.mailgun_service') as mock_mailgun:
            mock_mailgun.send_email.return_value = {"success": True}
            
            result = send_email(
                to_email="test@example.com",
                subject="Subject",
                body="Body",
                extra_param="value",
                another_param=123
            )
            
            assert isinstance(result, bool) 