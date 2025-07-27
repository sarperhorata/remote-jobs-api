"""
Security tests for the API
"""
import pytest
from fastapi.testclient import TestClient
from backend.main import app
from backend.middleware.input_validation import input_validator
from backend.middleware.rate_limiting import limiter, rate_limit_stats

client = TestClient(app)

class TestInputValidation:
    """Test input validation middleware"""
    
    def test_sql_injection_detection(self):
        """Test SQL injection detection"""
        # Test various SQL injection patterns
        malicious_inputs = [
            "'; DROP TABLE users; --",
            "1' OR '1'='1",
            "admin'--",
            "1; SELECT * FROM users",
            "1 UNION SELECT * FROM users",
            "1' AND 1=1--",
        ]
        
        for malicious_input in malicious_inputs:
            # This should raise an exception in the middleware
            with pytest.raises(Exception):
                input_validator._validate_string(malicious_input, "test")
    
    def test_xss_detection(self):
        """Test XSS detection"""
        malicious_inputs = [
            "<script>alert('xss')</script>",
            "<iframe src='javascript:alert(1)'></iframe>",
            "javascript:alert('xss')",
            "<img src=x onerror=alert(1)>",
            "<svg onload=alert(1)>",
        ]
        
        for malicious_input in malicious_inputs:
            with pytest.raises(Exception):
                input_validator._validate_string(malicious_input, "test")
    
    def test_path_traversal_detection(self):
        """Test path traversal detection"""
        malicious_inputs = [
            "../../../etc/passwd",
            "..\\..\\..\\windows\\system32\\config\\sam",
            "..%2f..%2f..%2fetc%2fpasswd",
            "..%252e%252e%252fetc%252fpasswd",
        ]
        
        for malicious_input in malicious_inputs:
            with pytest.raises(Exception):
                input_validator._validate_string(malicious_input, "test")
    
    def test_command_injection_detection(self):
        """Test command injection detection"""
        malicious_inputs = [
            "; rm -rf /",
            "| cat /etc/passwd",
            "`whoami`",
            "$(id)",
            "& ls -la",
        ]
        
        for malicious_input in malicious_inputs:
            with pytest.raises(Exception):
                input_validator._validate_string(malicious_input, "test")
    
    def test_email_validation(self):
        """Test email validation"""
        valid_emails = [
            "test@example.com",
            "user.name@domain.co.uk",
            "user+tag@example.org",
        ]
        
        invalid_emails = [
            "invalid-email",
            "@example.com",
            "user@",
            "user@.com",
            "user..name@example.com",
        ]
        
        for email in valid_emails:
            assert input_validator.validate_email(email) == True
        
        for email in invalid_emails:
            assert input_validator.validate_email(email) == False
    
    def test_password_strength_validation(self):
        """Test password strength validation"""
        # Test weak passwords
        weak_passwords = [
            "123",
            "password",
            "abc123",
        ]
        
        for password in weak_passwords:
            result = input_validator.validate_password_strength(password)
            assert result["valid"] == False
            assert len(result["errors"]) > 0
        
        # Test strong passwords
        strong_passwords = [
            "SecurePass123!",
            "MyP@ssw0rd2024",
            "Str0ng#Pass!",
        ]
        
        for password in strong_passwords:
            result = input_validator.validate_password_strength(password)
            assert result["valid"] == True
            assert len(result["errors"]) == 0
    
    def test_string_sanitization(self):
        """Test string sanitization"""
        malicious_strings = [
            ("<script>alert('xss')</script>", "alert('xss')"),
            ("<img src=x onerror=alert(1)>", "img src=x onerror=alert(1)"),
            ("javascript:alert('xss')", "alert('xss')"),
        ]
        
        for input_str, expected_output in malicious_strings:
            sanitized = input_validator.sanitize_string(input_str)
            assert "<script>" not in sanitized
            assert "javascript:" not in sanitized
            assert "onerror=" not in sanitized

class TestRateLimiting:
    """Test rate limiting middleware"""
    
    def test_rate_limiting_basic(self):
        """Test basic rate limiting"""
        # Make multiple requests to trigger rate limiting
        for i in range(10):
            response = client.get("/health")
            assert response.status_code in [200, 429]  # Either success or rate limited
    
    def test_rate_limit_stats(self):
        """Test rate limit statistics tracking"""
        # Make some requests to generate stats
        for i in range(5):
            client.get("/health")
        
        # Get stats
        stats = rate_limit_stats.get_stats()
        assert "requests_total" in stats
        assert stats["requests_total"] >= 5

class TestAuthenticationSecurity:
    """Test authentication security"""
    
    def test_login_brute_force_protection(self):
        """Test login brute force protection"""
        # Make multiple failed login attempts
        for i in range(6):
            response = client.post("/api/v1/auth/login", data={
                "username": "nonexistent@example.com",
                "password": "wrongpassword"
            })
            
            if i < 5:
                assert response.status_code == 401  # Unauthorized
            else:
                assert response.status_code == 429  # Too Many Requests
    
    def test_register_input_validation(self):
        """Test registration input validation"""
        # Test with invalid email
        response = client.post("/api/v1/auth/register", json={
            "email": "invalid-email",
            "password": "SecurePass123!",
            "name": "Test User"
        })
        assert response.status_code == 400
        assert "Invalid email format" in response.json()["detail"]
        
        # Test with weak password
        response = client.post("/api/v1/auth/register", json={
            "email": "test@example.com",
            "password": "123",
            "name": "Test User"
        })
        assert response.status_code == 400
        assert "Password validation failed" in response.json()["detail"]
        
        # Test with XSS in name
        response = client.post("/api/v1/auth/register", json={
            "email": "test@example.com",
            "password": "SecurePass123!",
            "name": "<script>alert('xss')</script>"
        })
        assert response.status_code == 400
        assert "Invalid input" in response.json()["detail"]

class TestAPISecurity:
    """Test API security"""
    
    def test_sql_injection_in_search(self):
        """Test SQL injection protection in search endpoints"""
        malicious_queries = [
            "'; DROP TABLE jobs; --",
            "1' OR '1'='1",
            "admin'--",
        ]
        
        for query in malicious_queries:
            response = client.get(f"/api/v1/jobs/search?q={query}")
            assert response.status_code == 400
            assert "Invalid input" in response.json()["detail"]
    
    def test_xss_in_search(self):
        """Test XSS protection in search endpoints"""
        malicious_queries = [
            "<script>alert('xss')</script>",
            "javascript:alert('xss')",
        ]
        
        for query in malicious_queries:
            response = client.get(f"/api/v1/jobs/search?q={query}")
            assert response.status_code == 400
            assert "Invalid input" in response.json()["detail"]
    
    def test_path_traversal_protection(self):
        """Test path traversal protection"""
        malicious_paths = [
            "../../../etc/passwd",
            "..\\..\\..\\windows\\system32\\config\\sam",
        ]
        
        for path in malicious_paths:
            response = client.get(f"/api/v1/jobs/{path}")
            assert response.status_code == 400
            assert "Invalid input" in response.json()["detail"]

class TestHeadersSecurity:
    """Test security headers"""
    
    def test_security_headers(self):
        """Test that security headers are present"""
        response = client.get("/health")
        
        # Check for security headers
        headers = response.headers
        
        # CORS headers should be present
        assert "access-control-allow-origin" in headers
        
        # Content-Type should be set
        assert "content-type" in headers
        assert "application/json" in headers["content-type"]

class TestEnvironmentSecurity:
    """Test environment security"""
    
    def test_no_hardcoded_secrets(self):
        """Test that no hardcoded secrets are exposed"""
        response = client.get("/health")
        
        # Check that no secrets are exposed in response
        response_data = response.json()
        
        # These fields should not contain hardcoded secrets
        sensitive_fields = ["secret", "password", "key", "token"]
        
        for field in sensitive_fields:
            # Check response content
            response_text = response.text.lower()
            assert f"your-{field}" not in response_text
            assert f"test_{field}" not in response_text
            assert f"fake_{field}" not in response_text

if __name__ == "__main__":
    pytest.main([__file__])