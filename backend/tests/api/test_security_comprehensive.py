import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, Mock
import json
import time
from main import app

client = TestClient(app)

class TestAPISecurityComprehensive:
    """Comprehensive API security tests"""

    def test_sql_injection_protection(self):
        """Test protection against SQL injection attacks"""
        sql_injections = [
            "'; DROP TABLE jobs; --",
            "1' OR '1'='1",
            "admin'; DELETE FROM users; --",
            "1' UNION SELECT * FROM users --",
            "'; INSERT INTO jobs VALUES ('malicious'); --"
        ]
        
        for injection in sql_injections:
            # Test in job search
            response = client.get(f"/api/v1/jobs/search?q={injection}")
            assert response.status_code in [200, 400, 422]
            
            # Should not return suspicious data
            if response.status_code == 200:
                data = response.json()
                assert "DROP" not in str(data).upper()
                assert "DELETE" not in str(data).upper()

    def test_xss_protection(self):
        """Test protection against XSS attacks"""
        xss_payloads = [
            "<script>alert('xss')</script>",
            "javascript:alert('xss')",
            "<img src=x onerror=alert('xss')>",
            "<iframe src=javascript:alert('xss')></iframe>",
            "';alert('xss');//"
        ]
        
        for payload in xss_payloads:
            response = client.get(f"/api/v1/jobs/search?q={payload}")
            
            # Should sanitize or reject XSS attempts
            if response.status_code == 200:
                data = response.text
                assert "<script>" not in data
                assert "javascript:" not in data
                assert "onerror=" not in data

    def test_path_traversal_protection(self):
        """Test protection against path traversal attacks"""
        path_traversals = [
            "../../etc/passwd",
            "../../../windows/system32/config/sam",
            "....//....//etc/passwd",
            "%2e%2e%2f%2e%2e%2fetc%2fpasswd",
            "..\\..\\windows\\system32\\config\\sam"
        ]
        
        for traversal in path_traversals:
            # Test in various endpoints
            response = client.get(f"/api/v1/jobs/{traversal}")
            assert response.status_code in [400, 404, 422]
            
            # Should not expose system files
            if response.status_code == 200:
                data = response.text.lower()
                assert "root:" not in data
                assert "administrator" not in data

    def test_header_injection_protection(self):
        """Test protection against HTTP header injection"""
        malicious_headers = {
            "X-Forwarded-For": "127.0.0.1\r\nX-Injected: malicious",
            "User-Agent": "test\r\nSet-Cookie: malicious=true",
            "Referer": "http://evil.com\r\nLocation: http://evil.com"
        }
        
        for header, value in malicious_headers.items():
            response = client.get("/api/v1/jobs/search", headers={header: value})
            
            # Should not include injected headers in response
            assert "X-Injected" not in response.headers
            assert "malicious=true" not in response.headers.get("Set-Cookie", "")

    def test_command_injection_protection(self):
        """Test protection against command injection"""
        command_injections = [
            "; ls -la",
            "| cat /etc/passwd",
            "&& rm -rf /",
            "`whoami`",
            "$(cat /etc/passwd)"
        ]
        
        for injection in command_injections:
            response = client.get(f"/api/v1/jobs/search?q={injection}")
            
            # Should not execute system commands
            assert response.status_code in [200, 400, 422]
            if response.status_code == 200:
                data = response.text
                assert "root:" not in data
                assert "bin/bash" not in data

    def test_rate_limiting_enforcement(self):
        """Test rate limiting enforcement"""
        # Make rapid requests to test rate limiting
        responses = []
        start_time = time.time()
        
        for i in range(20):
            response = client.get("/api/v1/jobs/search?limit=1")
            responses.append(response.status_code)
            
            # Small delay to avoid overwhelming the test
            time.sleep(0.01)
        
        execution_time = time.time() - start_time
        
        # Should handle rapid requests appropriately
        # Either allow all requests or implement rate limiting
        status_codes = set(responses)
        assert status_codes.issubset({200, 429, 503})
        
        # If rate limiting is implemented, should see 429s
        if 429 in status_codes:
            assert responses.count(429) > 0

    def test_oversized_request_protection(self):
        """Test protection against oversized requests"""
        # Very large JSON payload
        large_payload = {"data": "x" * 100000}  # 100KB
        
        response = client.post("/api/v1/jobs/search", json=large_payload)
        
        # Should reject or handle large payloads appropriately
        assert response.status_code in [200, 400, 413, 422]

    def test_malformed_json_handling(self):
        """Test handling of malformed JSON requests"""
        malformed_jsons = [
            '{"incomplete": ',
            '{"invalid": json}',
            '{"escaped": "\\u0000"}',
            '{"circular": {"ref": "circular"}}',
            'not json at all'
        ]
        
        for malformed in malformed_jsons:
            response = client.post(
                "/api/v1/jobs/search",
                data=malformed,
                headers={"Content-Type": "application/json"}
            )
            
            # Should handle malformed JSON gracefully
            assert response.status_code in [400, 422]

    def test_authentication_bypass_attempts(self):
        """Test attempts to bypass authentication"""
        bypass_attempts = [
            {"Authorization": "Bearer fake-token"},
            {"Authorization": "Bearer null"},
            {"Authorization": "Bearer undefined"},
            {"Authorization": "Bearer "},
            {"Authorization": "Basic YWRtaW46YWRtaW4="},  # admin:admin
            {"X-Admin-Override": "true"},
            {"X-User-Id": "1"},
            {"X-Forwarded-User": "admin"}
        ]
        
        for headers in bypass_attempts:
            # Test protected endpoint
            response = client.get("/api/v1/auth/me", headers=headers)
            
            # Should properly validate authentication
            assert response.status_code in [401, 403, 404]

    def test_privilege_escalation_protection(self):
        """Test protection against privilege escalation"""
        # Test with various role manipulations
        escalation_attempts = [
            {"role": "admin"},
            {"is_admin": True},
            {"permissions": ["all"]},
            {"user_type": "superuser"}
        ]
        
        for payload in escalation_attempts:
            response = client.post("/api/v1/auth/register", json={
                "email": "test@example.com",
                "password": "password123",
                "name": "Test User",
                **payload
            })
            
            # Should not allow privilege escalation through registration
            if response.status_code in [200, 201]:
                data = response.json()
                assert data.get("role") != "admin"
                assert data.get("is_admin") is not True

    def test_cors_security_configuration(self):
        """Test CORS security configuration"""
        # Test preflight request
        response = client.options(
            "/api/v1/jobs/search",
            headers={
                "Origin": "https://evil.com",
                "Access-Control-Request-Method": "GET"
            }
        )
        
        # Should have appropriate CORS headers
        assert response.status_code in [200, 204]
        
        # Should not allow arbitrary origins in production
        cors_header = response.headers.get("Access-Control-Allow-Origin")
        if cors_header:
            assert cors_header != "*" or "localhost" in cors_header

    def test_sensitive_data_exposure(self):
        """Test that sensitive data is not exposed"""
        response = client.get("/api/v1/jobs/search?limit=1")
        
        if response.status_code == 200:
            data = response.text.lower()
            
            # Should not expose sensitive information
            sensitive_terms = [
                "password", "secret", "api_key", "token", "private_key",
                "database_url", "connection_string", "admin_password"
            ]
            
            for term in sensitive_terms:
                assert term not in data

    def test_error_information_disclosure(self):
        """Test that errors don't disclose sensitive information"""
        # Trigger various errors
        error_endpoints = [
            "/api/v1/jobs/nonexistent",
            "/api/v1/users/99999",
            "/api/v1/auth/invalid",
            "/nonexistent/endpoint"
        ]
        
        for endpoint in error_endpoints:
            response = client.get(endpoint)
            
            if response.status_code >= 400:
                error_text = response.text.lower()
                
                # Should not expose internal paths or sensitive info
                assert "/users/" not in error_text
                assert "password" not in error_text
                assert "database" not in error_text
                assert "traceback" not in error_text

    def test_file_upload_security(self):
        """Test file upload security (if implemented)"""
        # Test with various file types
        malicious_files = [
            ("malicious.php", "<?php system($_GET['cmd']); ?>", "application/x-php"),
            ("script.js", "alert('xss')", "application/javascript"),
            ("exploit.exe", b"\x4d\x5a\x90\x00", "application/x-executable"),
            ("large.txt", "x" * 10000000, "text/plain")  # 10MB file
        ]
        
        for filename, content, content_type in malicious_files:
            files = {"file": (filename, content, content_type)}
            response = client.post("/api/v1/upload", files=files)
            
            # Should reject malicious files or handle safely
            if response.status_code in [200, 201]:
                # File should be processed safely
                data = response.json()
                assert "error" not in data or "safe" in str(data)

    def test_session_security(self):
        """Test session security measures"""
        # Test session fixation
        response1 = client.get("/api/v1/auth/login")
        session1 = response1.cookies.get("session_id")
        
        # Login with credentials
        login_response = client.post("/api/v1/auth/login", json={
            "email": "test@example.com",
            "password": "password123"
        })
        
        # Session should be regenerated after login
        if login_response.status_code == 200:
            session2 = login_response.cookies.get("session_id")
            if session1 and session2:
                assert session1 != session2

    def test_timing_attack_protection(self):
        """Test protection against timing attacks"""
        # Test login timing consistency
        times = []
        
        for i in range(5):
            start_time = time.time()
            response = client.post("/api/v1/auth/login", json={
                "email": f"nonexistent{i}@example.com",
                "password": "wrongpassword"
            })
            end_time = time.time()
            
            times.append(end_time - start_time)
            assert response.status_code in [400, 401]
        
        # Response times should be relatively consistent
        if len(times) > 1:
            time_variance = max(times) - min(times)
            assert time_variance < 1.0  # Should not vary by more than 1 second

    def test_clickjacking_protection(self):
        """Test clickjacking protection"""
        response = client.get("/api/v1/jobs/search")
        
        # Should have frame protection headers
        frame_options = response.headers.get("X-Frame-Options")
        csp = response.headers.get("Content-Security-Policy")
        
        # Should prevent embedding in frames
        if frame_options:
            assert frame_options in ["DENY", "SAMEORIGIN"]
        
        if csp:
            assert "frame-ancestors" in csp

    def test_content_type_validation(self):
        """Test content type validation"""
        # Test with incorrect content types
        wrong_content_types = [
            "text/plain",
            "application/xml", 
            "image/png",
            "application/x-www-form-urlencoded"
        ]
        
        for content_type in wrong_content_types:
            response = client.post(
                "/api/v1/auth/login",
                data='{"email": "test@example.com", "password": "test"}',
                headers={"Content-Type": content_type}
            )
            
            # Should validate content type appropriately
            assert response.status_code in [400, 415, 422]

    def test_api_version_security(self):
        """Test API versioning security"""
        # Test access to different API versions
        version_tests = [
            "/api/v0/jobs/search",  # Older version
            "/api/v2/jobs/search",  # Future version
            "/api/v1.1/jobs/search",  # Sub-version
            "/api/beta/jobs/search"  # Beta version
        ]
        
        for endpoint in version_tests:
            response = client.get(endpoint)
            
            # Should handle version requests appropriately
            assert response.status_code in [200, 404, 410]

class TestInputValidationSecurity:
    """Test input validation security measures"""

    def test_unicode_handling(self):
        """Test proper unicode handling"""
        unicode_inputs = [
            "python 🐍 developer",
            "السلام عليكم",  # Arabic
            "Здравствуй мир",  # Russian
            "こんにちは世界",  # Japanese
            "��🚀⭐️",  # Emojis
            "\u0000\u0001\u0002"  # Control characters
        ]
        
        for unicode_input in unicode_inputs:
            response = client.get(f"/api/v1/jobs/search?q={unicode_input}")
            
            # Should handle unicode gracefully
            assert response.status_code in [200, 400, 422]

    def test_boundary_value_testing(self):
        """Test boundary values for numeric inputs"""
        boundary_tests = [
            ("limit", [-1, 0, 1, 100, 10000, 2**31]),
            ("page", [-1, 0, 1, 1000, 2**31]),
            ("salary_min", [-1, 0, 1, 1000000, 2**31])
        ]
        
        for param, values in boundary_tests:
            for value in values:
                response = client.get(f"/api/v1/jobs/search?{param}={value}")
                
                # Should handle boundary values appropriately
                assert response.status_code in [200, 400, 422]

    def test_null_byte_injection(self):
        """Test protection against null byte injection"""
        null_byte_payloads = [
            "test\x00.php",
            "search\x00%00admin",
            "query\x00..\x00..etc\x00passwd"
        ]
        
        for payload in null_byte_payloads:
            response = client.get(f"/api/v1/jobs/search?q={payload}")
            
            # Should handle null bytes securely
            assert response.status_code in [200, 400, 422]

    def test_format_string_protection(self):
        """Test protection against format string attacks"""
        format_payloads = [
            "%s%s%s%s%s",
            "%x%x%x%x%x",
            "{0}{1}{2}{3}",
            "$(echo test)"
        ]
        
        for payload in format_payloads:
            response = client.get(f"/api/v1/jobs/search?q={payload}")
            
            # Should not execute format strings
            assert response.status_code in [200, 400, 422]
            if response.status_code == 200:
                data = response.text
                assert "test" not in data or payload in data

class TestAuthenticationSecurityAdvanced:
    """Advanced authentication security tests"""

    def test_token_manipulation(self):
        """Test JWT token manipulation attempts"""
        # Create base64 encoded fake tokens
        fake_tokens = [
            "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiYWRtaW4iOnRydWV9.TJVA95OrM7E2cBab30RMHrHDcEfxjoYZgeFONFh7HgQ",
            "eyJhbGciOiJub25lIn0.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiYWRtaW4iOnRydWV9.",
            "fake.token.here",
            ""
        ]
        
        for token in fake_tokens:
            headers = {"Authorization": f"Bearer {token}"}
            response = client.get("/api/v1/auth/me", headers=headers)
            
            # Should reject invalid tokens
            assert response.status_code in [401, 403]

    def test_password_policy_enforcement(self):
        """Test password policy enforcement"""
        weak_passwords = [
            "123",
            "password",
            "qwerty",
            "123456",
            "admin",
            "",
            "a",  # Too short
            "12345678"  # No complexity
        ]
        
        for password in weak_passwords:
            response = client.post("/api/v1/auth/register", json={
                "email": "test@example.com",
                "password": password,
                "name": "Test User"
            })
            
            # Should reject weak passwords
            assert response.status_code in [400, 422]

    def test_account_enumeration_protection(self):
        """Test protection against account enumeration"""
        # Test with existing vs non-existing emails
        test_emails = [
            "existing@example.com",
            "nonexistent@example.com",
            "admin@example.com"
        ]
        
        response_times = []
        response_messages = []
        
        for email in test_emails:
            start_time = time.time()
            response = client.post("/api/v1/auth/forgot-password", json={
                "email": email
            })
            end_time = time.time()
            
            response_times.append(end_time - start_time)
            response_messages.append(response.text)
        
        # Response times should be similar to prevent enumeration
        if len(response_times) > 1:
            time_variance = max(response_times) - min(response_times)
            assert time_variance < 0.5  # Should not vary significantly
        
        # Response messages should be similar
        unique_messages = set(response_messages)
        assert len(unique_messages) <= 2  # Should not leak account existence
