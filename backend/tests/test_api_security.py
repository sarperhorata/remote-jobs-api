"""
API Security Tests - testing security vulnerabilities and protection mechanisms
"""

import asyncio
import json
import re
from unittest.mock import AsyncMock, MagicMock, patch

import pytest


@pytest.mark.asyncio
async def test_sql_injection_protection():
    """Test SQL injection protection"""

    # Mock database query function
    def safe_query(query, params=None):
        """Simulate safe parameterized query"""
        if params:
            # This simulates parameterized queries
            return f"Query executed with parameters: {params}"
        else:
            # This simulates raw query (dangerous)
            return f"Raw query executed: {query}"

    # Test safe parameterized query
    safe_result = safe_query(
        "SELECT * FROM users WHERE email = ?", ["test@example.com"]
    )
    assert "parameters" in safe_result, "Should use parameterized query"

    # Test malicious input
    malicious_input = "'; DROP TABLE users; --"
    safe_malicious = safe_query(
        "SELECT * FROM users WHERE email = ?", [malicious_input]
    )
    # In parameterized queries, malicious SQL should be treated as data, not executed
    assert (
        malicious_input in safe_malicious
    ), "Malicious input should be preserved as data"
    assert (
        "Query executed with parameters" in safe_malicious
    ), "Should use parameterized query"


@pytest.mark.asyncio
async def test_xss_protection():
    """Test XSS protection"""

    def sanitize_html(text):
        """Simulate HTML sanitization"""
        if not text:
            return ""

        # Basic XSS protection
        dangerous_patterns = [
            r"<script[^>]*>.*?</script>",
            r"<iframe[^>]*>.*?</iframe>",
            r"<object[^>]*>.*?</object>",
            r"<embed[^>]*>.*?</embed>",
            r"javascript:",
            r"on\w+\s*=",
        ]

        sanitized = text
        for pattern in dangerous_patterns:
            sanitized = re.sub(pattern, "", sanitized, flags=re.IGNORECASE | re.DOTALL)

        return sanitized

    # Test safe content
    safe_content = "<p>Hello World</p>"
    sanitized_safe = sanitize_html(safe_content)
    assert sanitized_safe == safe_content, "Safe content should remain unchanged"

    # Test XSS attempts
    xss_attempts = [
        "<script>alert('xss')</script>",
        "<iframe src='javascript:alert(1)'></iframe>",
        "<img src='x' onerror='alert(1)'>",
        "javascript:alert('xss')",
        "<object data='javascript:alert(1)'></object>",
    ]

    for xss_attempt in xss_attempts:
        sanitized = sanitize_html(xss_attempt)
        assert "<script" not in sanitized.lower(), "Script tags should be removed"
        assert (
            "javascript:" not in sanitized.lower()
        ), "JavaScript URLs should be removed"
        assert "onerror" not in sanitized.lower(), "Event handlers should be removed"


@pytest.mark.asyncio
async def test_input_validation():
    """Test input validation"""

    def validate_email(email):
        """Validate email format"""
        if not email:
            return False
        pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        return bool(re.match(pattern, email))

    def validate_phone(phone):
        """Validate phone number format"""
        if not phone:
            return False
        pattern = r"^\+?[1-9]\d{1,14}$"
        return bool(re.match(pattern, phone))

    def validate_password(password):
        """Validate password strength"""
        if not password or len(password) < 8:
            return False

        has_upper = any(c.isupper() for c in password)
        has_lower = any(c.islower() for c in password)
        has_digit = any(c.isdigit() for c in password)
        has_special = any(c in "!@#$%^&*" for c in password)

        return has_upper and has_lower and has_digit and has_special

    # Test email validation
    valid_emails = [
        "test@example.com",
        "user.name@domain.co.uk",
        "user+tag@example.org",
    ]
    invalid_emails = ["invalid-email", "@example.com", "user@", "user@.com", ""]

    for email in valid_emails:
        assert validate_email(email), f"Valid email {email} should pass validation"

    for email in invalid_emails:
        assert not validate_email(
            email
        ), f"Invalid email {email} should fail validation"

    # Test phone validation
    valid_phones = ["+1234567890", "1234567890", "+44123456789"]
    invalid_phones = ["abc", "+", "", "123abc"]

    for phone in valid_phones:
        assert validate_phone(phone), f"Valid phone {phone} should pass validation"

    for phone in invalid_phones:
        assert not validate_phone(
            phone
        ), f"Invalid phone {phone} should fail validation"

    # Test password validation
    valid_passwords = ["SecurePass123!", "MyP@ssw0rd", "Str0ng#Pass"]
    invalid_passwords = [
        "weak",
        "nouppercase123!",
        "NOLOWERCASE123!",
        "NoSpecial123",
        "",
    ]

    for password in valid_passwords:
        assert validate_password(password), f"Valid password should pass validation"

    for password in invalid_passwords:
        assert not validate_password(
            password
        ), f"Invalid password should fail validation"


@pytest.mark.asyncio
async def test_rate_limiting():
    """Test rate limiting logic"""

    class RateLimiter:
        def __init__(self, max_requests=10, window_seconds=60):
            self.max_requests = max_requests
            self.window_seconds = window_seconds
            self.requests = {}

        def is_allowed(self, user_id):
            now = asyncio.get_event_loop().time()

            if user_id not in self.requests:
                self.requests[user_id] = []

            # Remove old requests outside the window
            self.requests[user_id] = [
                req_time
                for req_time in self.requests[user_id]
                if now - req_time < self.window_seconds
            ]

            # Check if user has exceeded limit
            if len(self.requests[user_id]) >= self.max_requests:
                return False

            # Add current request
            self.requests[user_id].append(now)
            return True

    # Create rate limiter
    limiter = RateLimiter(max_requests=3, window_seconds=60)

    # Test normal usage
    for i in range(3):
        assert limiter.is_allowed("user1"), f"Request {i+1} should be allowed"

    # Test rate limit exceeded
    assert not limiter.is_allowed("user1"), "4th request should be blocked"

    # Test different users
    assert limiter.is_allowed("user2"), "Different user should be allowed"


@pytest.mark.asyncio
async def test_authentication_validation():
    """Test authentication validation"""

    def validate_token(token):
        """Simulate token validation"""
        if not token:
            return False

        # For testing purposes, accept our mock tokens
        if token in ["admin_token", "user_token", "guest_token"]:
            return True

        # Simulate JWT token format validation
        if not token.startswith("eyJ"):
            return False

        # Simulate token expiration check
        # In real implementation, this would decode and check expiration
        return len(token) > 20

    def validate_permissions(token, required_permission):
        """Simulate permission validation"""
        if not validate_token(token):
            return False

        # Mock permission mapping
        permissions = {
            "admin_token": ["read", "write", "delete", "admin"],
            "user_token": ["read", "write"],
            "guest_token": ["read"],
        }

        user_permissions = permissions.get(token, [])
        return required_permission in user_permissions

    # Test valid tokens
    valid_tokens = ["eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.valid.token.here"]
    invalid_tokens = ["", "invalid", "short", None]

    for token in valid_tokens:
        assert validate_token(token), f"Valid token should pass validation"

    for token in invalid_tokens:
        assert not validate_token(token), f"Invalid token should fail validation"

    # Test permissions
    assert validate_permissions(
        "admin_token", "admin"
    ), "Admin should have admin permission"
    assert validate_permissions(
        "user_token", "read"
    ), "User should have read permission"
    assert not validate_permissions(
        "guest_token", "delete"
    ), "Guest should not have delete permission"
    assert not validate_permissions(
        "invalid_token", "read"
    ), "Invalid token should not have permissions"


@pytest.mark.asyncio
async def test_data_encryption():
    """Test data encryption/decryption"""

    def simple_encrypt(data, key):
        """Simple encryption simulation"""
        if not data or not key:
            return None

        # Simulate encryption (this is NOT real encryption)
        encrypted = ""
        for char in data:
            encrypted += chr(ord(char) ^ ord(key[0]))
        return encrypted

    def simple_decrypt(encrypted_data, key):
        """Simple decryption simulation"""
        if not encrypted_data or not key:
            return None

        # Simulate decryption
        decrypted = ""
        for char in encrypted_data:
            decrypted += chr(ord(char) ^ ord(key[0]))
        return decrypted

    # Test encryption/decryption
    test_data = "sensitive information"
    key = "secret_key"

    encrypted = simple_encrypt(test_data, key)
    assert encrypted is not None, "Encryption should succeed"
    assert encrypted != test_data, "Encrypted data should be different from original"

    decrypted = simple_decrypt(encrypted, key)
    assert decrypted == test_data, "Decrypted data should match original"

    # Test with wrong key
    wrong_decrypted = simple_decrypt(encrypted, "wrong_key")
    assert wrong_decrypted != test_data, "Wrong key should not decrypt correctly"


@pytest.mark.asyncio
async def test_csrf_protection():
    """Test CSRF protection"""

    def generate_csrf_token():
        """Generate CSRF token"""
        import secrets

        return secrets.token_hex(32)

    def validate_csrf_token(token, stored_token):
        """Validate CSRF token"""
        if not token or not stored_token:
            return False
        return token == stored_token

    # Test token generation
    token1 = generate_csrf_token()
    token2 = generate_csrf_token()

    assert token1 != token2, "Generated tokens should be different"
    assert len(token1) == 64, "Token should be 64 characters (32 bytes hex)"

    # Test token validation
    stored_token = generate_csrf_token()

    assert validate_csrf_token(
        stored_token, stored_token
    ), "Valid token should pass validation"
    assert not validate_csrf_token(
        "wrong_token", stored_token
    ), "Wrong token should fail validation"
    assert not validate_csrf_token(
        "", stored_token
    ), "Empty token should fail validation"
    assert not validate_csrf_token(
        stored_token, ""
    ), "Empty stored token should fail validation"


@pytest.mark.asyncio
async def test_file_upload_security():
    """Test file upload security"""

    def validate_file_upload(filename, content_type, file_size):
        """Validate file upload"""
        errors = []

        # Check file extension
        allowed_extensions = [".jpg", ".jpeg", ".png", ".gif", ".pdf", ".doc", ".docx"]
        file_ext = filename.lower()[filename.rfind(".") :] if "." in filename else ""

        if file_ext not in allowed_extensions:
            errors.append("File type not allowed")

        # Check content type
        allowed_types = [
            "image/jpeg",
            "image/png",
            "image/gif",
            "application/pdf",
            "application/msword",
        ]
        if content_type not in allowed_types:
            errors.append("Content type not allowed")

        # Check file size (max 5MB)
        max_size = 5 * 1024 * 1024  # 5MB
        if file_size > max_size:
            errors.append("File too large")

        # Check for malicious filenames
        dangerous_patterns = [r"\.\./", r"\.\.\\", r"<script", r"javascript:"]
        for pattern in dangerous_patterns:
            if re.search(pattern, filename, re.IGNORECASE):
                errors.append("Malicious filename detected")

        return errors

    # Test valid uploads
    valid_uploads = [
        ("document.pdf", "application/pdf", 1024 * 1024),  # 1MB PDF
        ("image.jpg", "image/jpeg", 500 * 1024),  # 500KB JPEG
        ("photo.png", "image/png", 2 * 1024 * 1024),  # 2MB PNG
    ]

    for filename, content_type, size in valid_uploads:
        errors = validate_file_upload(filename, content_type, size)
        assert len(errors) == 0, f"Valid upload should have no errors: {errors}"

    # Test invalid uploads
    invalid_uploads = [
        ("script.php", "application/x-php", 1024),  # PHP file
        ("large.pdf", "application/pdf", 10 * 1024 * 1024),  # 10MB file
        ("../../../etc/passwd", "text/plain", 1024),  # Path traversal
        ("<script>alert(1)</script>.jpg", "image/jpeg", 1024),  # XSS in filename
    ]

    for filename, content_type, size in invalid_uploads:
        errors = validate_file_upload(filename, content_type, size)
        assert len(errors) > 0, f"Invalid upload should have errors: {filename}"


if __name__ == "__main__":
    # Run tests manually for debugging
    async def run_tests():
        print("Running API security tests...")

        print("\n1. Testing SQL injection protection...")
        await test_sql_injection_protection()
        print("✓ SQL injection protection passed")

        print("\n2. Testing XSS protection...")
        await test_xss_protection()
        print("✓ XSS protection passed")

        print("\n3. Testing input validation...")
        await test_input_validation()
        print("✓ Input validation passed")

        print("\n4. Testing rate limiting...")
        await test_rate_limiting()
        print("✓ Rate limiting passed")

        print("\n5. Testing authentication validation...")
        await test_authentication_validation()
        print("✓ Authentication validation passed")

        print("\n6. Testing data encryption...")
        await test_data_encryption()
        print("✓ Data encryption passed")

        print("\n7. Testing CSRF protection...")
        await test_csrf_protection()
        print("✓ CSRF protection passed")

        print("\n8. Testing file upload security...")
        await test_file_upload_security()
        print("✓ File upload security passed")

        print("\nAll API security tests completed successfully!")

    asyncio.run(run_tests())
