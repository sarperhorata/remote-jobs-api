"""
Security Utils Tests
Güvenlik fonksiyonları için testler
"""

import pytest
from unittest.mock import Mock, patch
from backend.utils.security import SecurityUtils


class TestSecurityUtils:
    """SecurityUtils sınıfı için testler"""
    
    def test_sanitize_input_basic(self):
        """Temel input sanitization testi"""
        result = SecurityUtils.sanitize_input("test<script>alert('xss')</script>")
        assert "<script>" not in result
        assert "alert" not in result
        
    def test_sanitize_input_sql_injection(self):
        """SQL injection koruması testi"""
        result = SecurityUtils.sanitize_input("'; DROP TABLE users; --")
        assert "DROP TABLE" not in result
        assert ";" not in result
        
    def test_sanitize_input_empty_string(self):
        """Boş string testi"""
        result = SecurityUtils.sanitize_input("")
        assert result == ""
        
    def test_sanitize_input_none(self):
        """None değeri testi"""
        result = SecurityUtils.sanitize_input(None)
        assert result == ""
        
    def test_sanitize_input_special_chars(self):
        """Özel karakterler testi"""
        result = SecurityUtils.sanitize_input("test&<>\"'")
        assert "&" in result  # HTML entities korunmalı
        assert "<" not in result
        assert ">" not in result
        
    def test_validate_email_valid(self):
        """Geçerli email testi"""
        assert SecurityUtils.validate_email("test@example.com") is True
        
    def test_validate_email_invalid(self):
        """Geçersiz email testi"""
        assert SecurityUtils.validate_email("invalid-email") is False
        
    def test_validate_email_empty(self):
        """Boş email testi"""
        assert SecurityUtils.validate_email("") is False
        
    def test_validate_url_valid(self):
        """Geçerli URL testi"""
        assert SecurityUtils.validate_url("https://example.com") is True
        
    def test_validate_url_invalid(self):
        """Geçersiz URL testi"""
        assert SecurityUtils.validate_url("not-a-url") is False
        
    def test_validate_url_empty(self):
        """Boş URL testi"""
        assert SecurityUtils.validate_url("") is False
        
    def test_generate_secure_token(self):
        """Güvenli token üretimi testi"""
        token1 = SecurityUtils.generate_secure_token()
        token2 = SecurityUtils.generate_secure_token()
        
        assert len(token1) == 32
        assert len(token2) == 32
        assert token1 != token2
        
    def test_hash_password(self):
        """Şifre hash'leme testi"""
        password = "testpassword"
        hashed = SecurityUtils.hash_password(password)
        
        assert hashed != password
        assert SecurityUtils.verify_password(password, hashed) is True
        
    def test_verify_password_incorrect(self):
        """Yanlış şifre doğrulama testi"""
        password = "testpassword"
        hashed = SecurityUtils.hash_password(password)
        
        assert SecurityUtils.verify_password("wrongpassword", hashed) is False
        
    def test_encrypt_decrypt_data(self):
        """Veri şifreleme/çözme testi"""
        data = "sensitive data"
        encrypted = SecurityUtils.encrypt_data(data)
        decrypted = SecurityUtils.decrypt_data(encrypted)
        
        assert encrypted != data
        assert decrypted == data
        
    def test_encrypt_decrypt_empty_data(self):
        """Boş veri şifreleme testi"""
        data = ""
        encrypted = SecurityUtils.encrypt_data(data)
        decrypted = SecurityUtils.decrypt_data(encrypted)
        
        assert decrypted == data 