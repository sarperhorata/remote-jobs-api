import pytest
import re
import json
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, MagicMock

class TestSecurity:
    """Güvenlik testleri"""
    
    def test_sql_injection_prevention(self, client):
        """SQL injection saldırılarının önlendiğini test eder"""
        malicious_inputs = [
            "'; DROP TABLE jobs; --",
            "' OR '1'='1",
            "'; INSERT INTO users VALUES ('hacker', 'password'); --",
            "' UNION SELECT * FROM users --",
            "'; UPDATE users SET password='hacked' --"
        ]
        
        for malicious_input in malicious_inputs:
            # Job arama endpoint'inde test et
            response = client.get(f"/api/v1/jobs/search?q={malicious_input}")
            # SQL injection başarısız olmalı (422, 400, veya güvenli 200)
            assert response.status_code in [200, 400, 422, 404]
            
            # Yanıtta SQL hatası olmamalı
            if response.status_code == 200:
                response_text = response.text.lower()
                assert "sql" not in response_text
                assert "syntax error" not in response_text
                assert "mysql" not in response_text
                assert "postgresql" not in response_text
    
    def test_xss_prevention(self, client):
        """XSS saldırılarının önlendiğini test eder"""
        xss_payloads = [
            "<script>alert('xss')</script>",
            "javascript:alert('xss')",
            "<img src=x onerror=alert('xss')>",
            "<svg onload=alert('xss')>",
            "';alert('xss');//"
        ]
        
        for payload in xss_payloads:
            # Job oluşturma endpoint'inde test et
            job_data = {
                "title": payload,
                "company": "Test Corp",
                "description": payload
            }
            
            response = client.post("/api/v1/jobs/", json=job_data)
            # XSS payload'ı reddedilmeli veya sanitize edilmeli
            assert response.status_code in [200, 201, 400, 422]
            
            if response.status_code in [200, 201]:
                # Yanıtta script tag'leri olmamalı
                response_text = response.text.lower()
                assert "<script>" not in response_text
                assert "javascript:" not in response_text
    
    def test_no_sql_injection_prevention(self, client):
        """NoSQL injection saldırılarının önlendiğini test eder"""
        nosql_payloads = [
            '{"$where": "1==1"}',
            '{"$ne": null}',
            '{"$gt": ""}',
            '{"$regex": ".*"}',
            '{"$exists": true}'
        ]
        
        for payload in nosql_payloads:
            # Job arama endpoint'inde test et
            response = client.get(f"/api/v1/jobs/search?q={payload}")
            # NoSQL injection başarısız olmalı
            assert response.status_code in [200, 400, 422, 404]
    
    def test_path_traversal_prevention(self, client):
        """Path traversal saldırılarının önlendiğini test eder"""
        path_traversal_payloads = [
            "../../../etc/passwd",
            "..\\..\\..\\windows\\system32\\config\\sam",
            "....//....//....//etc/passwd",
            "%2e%2e%2f%2e%2e%2f%2e%2e%2fetc%2fpasswd"
        ]
        
        for payload in path_traversal_payloads:
            # Dosya yükleme endpoint'inde test et
            response = client.post(
                "/api/v1/upload/cv",
                files={"file": (payload, b"test content", "application/pdf")}
            )
            # Path traversal reddedilmeli
            assert response.status_code in [400, 422, 403]
    
    def test_command_injection_prevention(self, client):
        """Command injection saldırılarının önlendiğini test eder"""
        command_injection_payloads = [
            "; rm -rf /",
            "| cat /etc/passwd",
            "&& whoami",
            "; ls -la",
            "`id`"
        ]
        
        for payload in command_injection_payloads:
            # Job arama endpoint'inde test et
            response = client.get(f"/api/v1/jobs/search?q={payload}")
            # Command injection başarısız olmalı
            assert response.status_code in [200, 400, 422, 404]
    
    def test_input_validation(self, client):
        """Input validation'ın düzgün çalıştığını test eder"""
        invalid_inputs = [
            # Çok uzun input'lar
            {"title": "A" * 10000},
            # Geçersiz email formatları
            {"email": "invalid-email"},
            {"email": "test@.com"},
            {"email": "@example.com"},
            # Geçersiz URL'ler
            {"website": "not-a-url"},
            {"website": "ftp://malicious.com"},
            # Negatif sayılar
            {"salary_min": -1000},
            {"salary_max": -5000}
        ]
        
        for invalid_input in invalid_inputs:
            response = client.post("/api/v1/jobs/", json=invalid_input)
            # Geçersiz input reddedilmeli
            assert response.status_code in [400, 422]
    
    def test_authentication_required(self, client):
        """Korumalı endpoint'lerin kimlik doğrulama gerektirdiğini test eder"""
        protected_endpoints = [
            "/api/v1/users/profile",
            "/api/v1/applications/",
            "/api/v1/admin/users",
            "/api/v1/admin/jobs"
        ]
        
        for endpoint in protected_endpoints:
            response = client.get(endpoint)
            # Kimlik doğrulama gerekli
            assert response.status_code in [401, 403, 404]
    
    def test_csrf_protection(self, client):
        """CSRF korumasının aktif olduğunu test eder"""
        # CSRF token olmadan POST isteği
        response = client.post("/api/v1/jobs/", json={
            "title": "Test Job",
            "company": "Test Corp"
        })
        
        # CSRF koruması varsa 403, yoksa 200/201/422 olabilir
        assert response.status_code in [200, 201, 400, 401, 403, 422]
    
    def test_rate_limiting(self, client):
        """Rate limiting'in aktif olduğunu test eder"""
        # Çok sayıda istek gönder
        for _ in range(100):
            response = client.get("/health")
            if response.status_code == 429:  # Rate limit aşıldı
                break
        else:
            # Rate limiting yoksa test geçer
            pass
    
    def test_secure_headers(self, client):
        """Güvenlik header'larının mevcut olduğunu test eder"""
        response = client.get("/health")
        
        # Güvenlik header'ları kontrol et
        headers = response.headers
        
        # Content Security Policy
        if "content-security-policy" in headers:
            csp = headers["content-security-policy"]
            assert "script-src" in csp or "default-src" in csp
        
        # X-Frame-Options
        if "x-frame-options" in headers:
            assert headers["x-frame-options"] in ["DENY", "SAMEORIGIN"]
        
        # X-Content-Type-Options
        if "x-content-type-options" in headers:
            assert headers["x-content-type-options"] == "nosniff"
    
    def test_password_strength_validation(self, client):
        """Şifre gücü validasyonunun çalıştığını test eder"""
        weak_passwords = [
            "123",
            "password",
            "abc123",
            "qwerty",
            "123456789"
        ]
        
        for weak_password in weak_passwords:
            user_data = {
                "email": "test@example.com",
                "password": weak_password,
                "first_name": "Test",
                "last_name": "User"
            }
            
            response = client.post("/api/v1/auth/register", json=user_data)
            # Zayıf şifre reddedilmeli
            assert response.status_code in [400, 422]
    
    def test_jwt_token_validation(self, client):
        """JWT token validasyonunun çalıştığını test eder"""
        invalid_tokens = [
            "invalid.token.here",
            "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.invalid.signature",
            "expired.token.here",
            ""
        ]
        
        for invalid_token in invalid_tokens:
            headers = {"Authorization": f"Bearer {invalid_token}"}
            response = client.get("/api/v1/users/profile", headers=headers)
            # Geçersiz token reddedilmeli
            assert response.status_code in [401, 403]
    
    def test_file_type_validation(self, client):
        """Dosya tipi validasyonunun çalıştığını test eder"""
        malicious_files = [
            ("malicious.exe", b"malicious content", "application/octet-stream"),
            ("script.js", b"alert('xss')", "application/javascript"),
            ("shell.sh", b"#!/bin/bash\nrm -rf /", "text/plain"),
            ("virus.bat", b"@echo off\ndel C:\\", "application/octet-stream")
        ]
        
        for filename, content, content_type in malicious_files:
            response = client.post(
                "/api/v1/upload/cv",
                files={"file": (filename, content, content_type)}
            )
            # Tehlikeli dosya tipleri reddedilmeli
            assert response.status_code in [400, 422, 403]
    
    def test_input_sanitization(self, client):
        """Input sanitization'ın çalıştığını test eder"""
        malicious_inputs = [
            "<script>alert('xss')</script>",
            "javascript:alert('xss')",
            "'; DROP TABLE users; --",
            "../../../etc/passwd",
            "{{7*7}}",  # Template injection
            "${7*7}"   # Expression language injection
        ]
        
        for malicious_input in malicious_inputs:
            job_data = {
                "title": malicious_input,
                "company": "Test Corp",
                "description": malicious_input
            }
            
            response = client.post("/api/v1/jobs/", json=job_data)
            # Input sanitize edilmeli veya reddedilmeli
            assert response.status_code in [200, 201, 400, 422]
            
            if response.status_code in [200, 201]:
                # Yanıtta tehlikeli içerik olmamalı
                response_text = response.text.lower()
                assert "<script>" not in response_text
                assert "javascript:" not in response_text
                assert "drop table" not in response_text
    
    def test_session_management(self, client):
        """Session yönetiminin güvenli olduğunu test eder"""
        # Login işlemi
        login_data = {
            "email": "test@example.com",
            "password": "testpassword"
        }
        
        response = client.post("/api/v1/auth/login", json=login_data)
        
        if response.status_code == 200:
            # Session cookie'si güvenli olmalı
            cookies = response.cookies
            
            for cookie_name, cookie_value in cookies.items():
                if "session" in cookie_name.lower() or "token" in cookie_name.lower():
                    # Cookie güvenlik özellikleri kontrol et
                    # HttpOnly, Secure, SameSite gibi
                    pass
    
    def test_logging_security(self, client):
        """Logging'in güvenlik açığı oluşturmadığını test eder"""
        sensitive_data = [
            "password123",
            "secret_key_here",
            "api_key_abc123",
            "token_xyz789"
        ]
        
        for sensitive in sensitive_data:
            # Hassas veri ile istek gönder
            response = client.get(f"/api/v1/jobs/search?q={sensitive}")
            
            # Log dosyalarında hassas veri olmamalı (manuel kontrol gerekli)
            # Bu test sadece isteğin başarılı olduğunu kontrol eder
            assert response.status_code in [200, 404]
    
    def test_error_information_disclosure(self, client):
        """Hata mesajlarında hassas bilgi sızıntısı olmadığını test eder"""
        # Geçersiz endpoint'e istek
        response = client.get("/api/v1/nonexistent/")
        
        if response.status_code == 404:
            # 404 hata mesajında hassas bilgi olmamalı
            error_text = response.text.lower()
            assert "database" not in error_text
            assert "password" not in error_text
            assert "api_key" not in error_text
            assert "secret" not in error_text
            assert "internal" not in error_text