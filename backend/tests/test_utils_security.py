import pytest
from utils.security import SecurityUtils

class TestPasswordSecurity:
    def test_validate_password_strong(self):
        assert SecurityUtils.validate_password("SecurePass123!") == True
    
    def test_validate_password_weak(self):
        assert SecurityUtils.validate_password("password") == False
        
class TestInputValidation:
    def test_email_validation(self):
        assert SecurityUtils.validate_email("test@example.com") is True
        assert SecurityUtils.validate_email("invalid") is False
        
    def test_sanitize_input(self):
        result = SecurityUtils.sanitize_input("<script>alert(1)</script>")
        assert "<script>" not in result
