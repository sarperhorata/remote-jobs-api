from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch

import pytest
from utils.email import (create_email_verification_token,
                         create_password_reset_token, send_email,
                         send_password_reset_email, send_verification_email,
                         verify_token)


class TestEmailTokenFunctions:
    """Test email token creation and verification"""

    def test_create_email_verification_token(self):
        """Test creating email verification token"""
        email = "test@example.com"
        token = create_email_verification_token(email)

        assert isinstance(token, str)
        assert len(token) > 0

    def test_create_password_reset_token(self):
        """Test creating password reset token"""
        email = "test@example.com"
        token = create_password_reset_token(email)

        assert isinstance(token, str)
        assert len(token) > 0

    def test_verify_token_valid_verification_token(self):
        """Test verifying valid email verification token"""
        email = "test@example.com"
        token = create_email_verification_token(email)

        payload = verify_token(token)

        assert payload is not None
        assert isinstance(payload, dict)
        assert payload["sub"] == email
        assert payload["type"] == "email_verification"
        assert "exp" in payload

    def test_verify_token_invalid_token(self):
        """Test verifying invalid token"""
        invalid_token = "invalid.token.here"

        result = verify_token(invalid_token)
        assert result is None


class TestEmailSendingFunctions:
    """Test email sending functions"""

    @patch("backend.services.mailgun_service.mailgun_service.send_email")
    def test_send_email_success(self, mock_mailgun):
        """Test successful email sending"""
        mock_mailgun.return_value = {"success": True}

        result = send_email(
            to_email="test@example.com", subject="Test Subject", body="Test message"
        )

        assert result is True
        mock_mailgun.assert_called_once()

    @patch("backend.services.mailgun_service.mailgun_service.send_email")
    def test_send_email_failure(self, mock_mailgun):
        """Test email sending failure"""
        mock_mailgun.return_value = {"success": False, "error": "Test error"}

        result = send_email(
            to_email="test@example.com", subject="Test Subject", body="Test message"
        )

        assert result is False

    @patch("backend.services.mailgun_service.mailgun_service.send_verification_email")
    def test_send_verification_email_success(self, mock_mailgun):
        """Test sending verification email"""
        mock_mailgun.return_value = True

        result = send_verification_email("test@example.com", "test_token")

        assert result is True
        mock_mailgun.assert_called_once()

    @patch("backend.services.mailgun_service.mailgun_service.send_verification_email")
    def test_send_verification_email_failure(self, mock_mailgun):
        """Test verification email sending failure"""
        mock_mailgun.side_effect = Exception("Mailgun Error")

        result = send_verification_email("test@example.com", "test_token")

        assert result is False


class TestEmailUtilityFunctions:
    """Test email utility functions"""

    def test_different_emails_create_different_tokens(self):
        """Test that different emails create different tokens"""
        email1 = "user1@example.com"
        email2 = "user2@example.com"

        token1 = create_email_verification_token(email1)
        token2 = create_email_verification_token(email2)

        assert token1 != token2

    def test_token_contains_required_fields(self):
        """Test that tokens contain all required fields"""
        email = "test@example.com"

        verification_token = create_email_verification_token(email)
        verification_payload = verify_token(verification_token)

        # Check required fields
        required_fields = ["sub", "type", "exp"]

        for field in required_fields:
            assert field in verification_payload

        # Check field types
        assert isinstance(verification_payload["sub"], str)
        assert isinstance(verification_payload["type"], str)
        assert isinstance(verification_payload["exp"], int)
