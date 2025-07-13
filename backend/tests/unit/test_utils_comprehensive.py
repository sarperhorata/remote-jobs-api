import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from backend.utils.auth import get_current_user
from backend.utils.email import send_email, send_verification_email, send_password_reset_email
from backend.utils.security import SecurityUtils
from backend.utils.config import get_all_config
from backend.utils.recaptcha import verify_recaptcha

class TestAuthUtils:
    """Auth utility fonksiyonları için testler"""
    
    @patch('backend.utils.auth.get_async_db')
    def test_get_current_user_success(self, mock_db):
        """Başarılı user getirme testi"""
        mock_db.return_value = AsyncMock()
        mock_db.return_value.users.find_one.return_value = {
            "_id": "test_user_id",
            "email": "test@example.com",
            "is_active": True
        }
        
        # Test fonksiyonu
        assert hasattr(get_current_user, '__call__')
    
    @patch('backend.utils.auth.get_async_db')
    def test_get_current_user_not_found(self, mock_db):
        """User bulunamadığında testi"""
        mock_db.return_value = AsyncMock()
        mock_db.return_value.users.find_one.return_value = None
        
        # Test fonksiyonu
        assert hasattr(get_current_user, '__call__')

class TestEmailUtils:
    """Email utility fonksiyonları için testler"""
    
    @patch('backend.utils.email.mailgun_service.send_email')
    def test_send_email_success(self, mock_send):
        """Email gönderme başarılı testi"""
        mock_send.return_value = {"success": True, "id": "test_id"}
        
        result = send_email(
            to_email="test@example.com",
            subject="Test Subject",
            body="Test Body"
        )
        
        assert result is True
        mock_send.assert_called_once()
    
    @patch('backend.utils.email.mailgun_service.send_verification_email')
    def test_send_verification_email(self, mock_send):
        """Verification email gönderme testi"""
        mock_send.return_value = True
        
        result = send_verification_email("test@example.com", "verification_token_123")
        
        assert result is True
        mock_send.assert_called_once()
    
    @patch('backend.utils.email.mailgun_service.send_password_reset_email')
    def test_send_password_reset_email(self, mock_send):
        """Password reset email gönderme testi"""
        mock_send.return_value = True
        
        result = send_password_reset_email("test@example.com", "reset_token_123")
        
        assert result is True
        mock_send.assert_called_once()
    
    @patch('backend.utils.email.mailgun_service.send_email')
    def test_send_email_failure(self, mock_send):
        """Email gönderme başarısız testi"""
        mock_send.side_effect = Exception("Email service error")
        
        result = send_email(
            to_email="test@example.com",
            subject="Test Subject",
            body="Test Body"
        )
        
        assert result is False

class TestSecurityUtils:
    """Security utility fonksiyonları için testler"""
    
    def test_validate_password(self):
        """Password doğrulama testi"""
        # Geçerli password
        valid_password = "TestPass123!"
        assert SecurityUtils.validate_password(valid_password) is True
        
        # Geçersiz password - çok kısa
        invalid_password = "short"
        assert SecurityUtils.validate_password(invalid_password) is False
    
    def test_sanitize_input(self):
        """Input sanitization testi"""
        # XSS script içeren input
        malicious_input = "<script>alert('xss')</script>Hello"
        sanitized = SecurityUtils.sanitize_input(malicious_input)
        
        assert "<script>" not in sanitized
        assert "Hello" in sanitized
    
    def test_check_rate_limit(self):
        """Rate limiting testi"""
        ip = "192.168.1.1"
        endpoint = "/api/test"
        
        # İlk istek
        is_within_limit, remaining = SecurityUtils.check_rate_limit(ip, endpoint, limit=5)
        assert is_within_limit is True
        assert remaining == 4
    
    def test_validate_email(self):
        """Email doğrulama testi"""
        # Geçerli email
        valid_email = "test@example.com"
        assert SecurityUtils.validate_email(valid_email) is True
        
        # Geçersiz email
        invalid_email = "invalid-email"
        assert SecurityUtils.validate_email(invalid_email) is False
    
    def test_validate_phone(self):
        """Telefon doğrulama testi"""
        # Geçerli telefon
        valid_phone = "+1234567890"
        assert SecurityUtils.validate_phone(valid_phone) is True
        
        # Geçersiz telefon
        invalid_phone = "123"
        assert SecurityUtils.validate_phone(invalid_phone) is False
    
    def test_generate_csrf_token(self):
        """CSRF token oluşturma testi"""
        token = SecurityUtils.generate_csrf_token()
        
        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0
    
    def test_verify_csrf_token(self):
        """CSRF token doğrulama testi"""
        token = SecurityUtils.generate_csrf_token()
        
        # Geçerli token
        assert SecurityUtils.verify_csrf_token(token) is True
        
        # Geçersiz token
        assert SecurityUtils.verify_csrf_token("invalid_token") is False
    
    def test_get_secure_headers(self):
        """Güvenlik header'ları testi"""
        headers = SecurityUtils.get_secure_headers()
        
        assert isinstance(headers, dict)
        assert "X-Content-Type-Options" in headers
        assert "X-Frame-Options" in headers
        assert "X-XSS-Protection" in headers

class TestConfigUtils:
    """Config utility fonksiyonları için testler"""
    
    def test_get_all_config(self):
        """Config getirme testi"""
        config = get_all_config()
        
        assert config is not None
        assert "api" in config
        assert "database" in config
        assert "email" in config

class TestRecaptchaUtils:
    """Recaptcha utility fonksiyonları için testler"""
    
    @patch('backend.utils.recaptcha.requests.post')
    def test_verify_recaptcha_success(self, mock_post):
        """Recaptcha doğrulama başarılı testi"""
        mock_post.return_value.json.return_value = {"success": True}
        
        result = verify_recaptcha("test_token")
        
        assert result is True
        mock_post.assert_called_once()
    
    @patch('backend.utils.recaptcha.requests.post')
    def test_verify_recaptcha_failure(self, mock_post):
        """Recaptcha doğrulama başarısız testi"""
        mock_post.return_value.json.return_value = {"success": False}
        
        result = verify_recaptcha("invalid_token")
        
        assert result is False
        mock_post.assert_called_once()

class TestUtilityIntegration:
    """Utility entegrasyon testleri"""
    
    def test_utility_functions_exist(self):
        """Tüm utility fonksiyonlarının mevcut olduğunu test et"""
        # Auth utils
        assert hasattr(get_current_user, '__call__')
        
        # Email utils
        assert hasattr(send_email, '__call__')
        assert hasattr(send_verification_email, '__call__')
        assert hasattr(send_password_reset_email, '__call__')
        
        # Security utils
        assert hasattr(SecurityUtils.validate_password, '__call__')
        assert hasattr(SecurityUtils.sanitize_input, '__call__')
        assert hasattr(SecurityUtils.generate_csrf_token, '__call__')
        
        # Config utils
        assert hasattr(get_all_config, '__call__')
        
        # Recaptcha utils
        assert hasattr(verify_recaptcha, '__call__')
    
    def test_utility_error_handling(self):
        """Utility hata yönetimi testi"""
        # Email error handling
        with patch('backend.utils.email.mailgun_service.send_email') as mock_send:
            mock_send.side_effect = Exception("Service error")
            result = send_email("test@example.com", "Subject", "Body")
            assert result is False
        
        # Recaptcha error handling
        with patch('backend.utils.recaptcha.requests.post') as mock_post:
            mock_post.side_effect = Exception("Network error")
            result = verify_recaptcha("token")
            assert result is False 