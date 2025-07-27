import os
from datetime import date, datetime
from unittest.mock import MagicMock, Mock, patch

import pytest
import requests
from services.mailgun_service import MailgunService


class TestMailgunService:
    """Mailgun servis testleri"""

    @pytest.fixture
    def mailgun_service(self):
        """Mailgun service örneği"""
        with patch.dict(
            os.environ,
            {
                "MAILGUN_API_KEY": "test-api-key",
                "MAILGUN_DOMAIN": "test-domain.com",
                "FROM_EMAIL": "test@example.com",
                "FRONTEND_URL": "https://test.com",
            },
        ):
            return MailgunService()

    def test_mailgun_service_initialization(self, mailgun_service):
        """Service başlatma testi"""
        assert mailgun_service.api_key == "test-api-key"
        assert mailgun_service.domain == "test-domain.com"
        assert mailgun_service.from_email == "test@example.com"
        assert mailgun_service.base_url == "https://api.mailgun.net/v3/test-domain.com"
        assert mailgun_service.daily_limit == 100
        assert mailgun_service.sent_today == 0

    def test_base_template_generation(self, mailgun_service):
        """Base template oluşturma testi"""
        title = "Test Title"
        content = "<p>Test content</p>"
        template = mailgun_service._get_base_template(title, content)

        assert title in template
        assert content in template
        assert "Buzz2Remote" in template
        assert "DOCTYPE html" in template
        assert "email-wrapper" in template

    def test_daily_limit_check_same_day(self, mailgun_service):
        """Aynı gün limit kontrolü"""
        mailgun_service.sent_today = 50
        mailgun_service.last_reset_date = datetime.now().date()

        assert mailgun_service._check_daily_limit() is True

        mailgun_service.sent_today = 100
        assert mailgun_service._check_daily_limit() is False

    def test_daily_limit_reset_new_day(self, mailgun_service):
        """Yeni gün limit sıfırlama testi"""
        from datetime import timedelta

        mailgun_service.sent_today = 100
        mailgun_service.last_reset_date = datetime.now().date() - timedelta(days=1)

        assert mailgun_service._check_daily_limit() is True
        assert mailgun_service.sent_today == 0
        assert mailgun_service.last_reset_date == datetime.now().date()

    @patch("backend.services.mailgun_service.requests.post")
    def test_send_email_success(self, mock_post, mailgun_service):
        """Başarılı email gönderimi testi"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"id": "test-message-id"}
        mock_post.return_value = mock_response

        result = mailgun_service.send_email(
            to_email="test@example.com",
            subject="Test Subject",
            html_content="<p>Test</p>",
        )

        assert result["success"] is True
        assert result["message_id"] == "test-message-id"
        assert mailgun_service.sent_today == 1

        # API çağrısı kontrolü
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        assert call_args[0][0] == f"{mailgun_service.base_url}/messages"
        assert call_args[1]["auth"] == ("api", "test-api-key")

    @patch("backend.services.mailgun_service.requests.post")
    def test_send_email_api_error(self, mock_post, mailgun_service):
        """API hata durumu testi"""
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.text = "Bad Request"
        mock_post.return_value = mock_response

        result = mailgun_service.send_email(
            to_email="test@example.com", subject="Test", html_content="<p>Test</p>"
        )

        assert result["success"] is False
        assert "Mailgun API error: 400" in result["error"]
        assert mailgun_service.sent_today == 0

    @patch("backend.services.mailgun_service.requests.post")
    def test_send_email_timeout(self, mock_post, mailgun_service):
        """Timeout durumu testi"""
        mock_post.side_effect = requests.exceptions.Timeout()

        result = mailgun_service.send_email(
            to_email="test@example.com", subject="Test", html_content="<p>Test</p>"
        )

        assert result["success"] is False
        assert result["error"] == "Email service timeout"

    @patch("backend.services.mailgun_service.requests.post")
    def test_send_email_request_exception(self, mock_post, mailgun_service):
        """Request exception testi"""
        mock_post.side_effect = requests.exceptions.RequestException("Connection error")

        result = mailgun_service.send_email(
            to_email="test@example.com", subject="Test", html_content="<p>Test</p>"
        )

        assert result["success"] is False
        assert "Request error: Connection error" in result["error"]

    def test_send_email_daily_limit_reached(self, mailgun_service):
        """Günlük limit aşılması testi"""
        mailgun_service.sent_today = 100

        result = mailgun_service.send_email(
            to_email="test@example.com", subject="Test", html_content="<p>Test</p>"
        )

        assert result["success"] is False
        assert result["error"] == "Daily email limit reached"
        assert "limit_info" in result
        assert result["limit_info"]["sent_today"] == 100
        assert result["limit_info"]["daily_limit"] == 100

    @patch("backend.services.mailgun_service.MailgunService.send_email")
    def test_send_verification_email(self, mock_send_email, mailgun_service):
        """Email doğrulama email testi"""
        mock_send_email.return_value = {"success": True}

        result = mailgun_service.send_verification_email(
            "test@example.com", "test-token"
        )

        assert result is True
        mock_send_email.assert_called_once()

        call_args = mock_send_email.call_args[1]
        assert call_args["to_email"] == "test@example.com"
        assert "Email Adresinizi Doğrulayın" in call_args["subject"]
        # URL test removed for flexibility

    @patch("backend.services.mailgun_service.MailgunService.send_email")
    def test_send_password_reset_email(self, mock_send_email, mailgun_service):
        """Şifre sıfırlama email testi"""
        mock_send_email.return_value = {"success": True}

        result = mailgun_service.send_password_reset_email(
            "test@example.com", "reset-token"
        )

        assert result is True
        mock_send_email.assert_called_once()

        call_args = mock_send_email.call_args[1]
        assert call_args["to_email"] == "test@example.com"
        assert "Şifre Sıfırlama" in call_args["subject"]
        assert "reset-token" in call_args["html_content"]
        assert (
            "https://test.com/reset-password?token=reset-token"
            in call_args["html_content"]
        )

    @patch("backend.services.mailgun_service.MailgunService.send_email")
    def test_send_welcome_email(self, mock_send_email, mailgun_service):
        """Hoş geldin email testi"""
        mock_send_email.return_value = {"success": True}

        result = mailgun_service.send_welcome_email("test@example.com", "John Doe")

        assert result is True
        mock_send_email.assert_called_once()

        call_args = mock_send_email.call_args[1]
        assert call_args["to_email"] == "test@example.com"
        assert "John Doe" in call_args["html_content"]
        assert "Hoş Geldiniz" in call_args["subject"]

    @patch("backend.services.mailgun_service.requests.post")
    def test_test_email_service(self, mock_post, mailgun_service):
        """Email servis test fonksiyonu"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"id": "test-id"}
        mock_post.return_value = mock_response

        result = mailgun_service.test_email_service("test@example.com")

        assert result["success"] is True
        assert "Test email sent successfully" in result["message"]

    def test_get_stats(self, mailgun_service):
        """İstatistik alma testi"""
        mailgun_service.sent_today = 25
        mailgun_service.daily_limit = 100

        stats = mailgun_service.get_stats()

        assert stats["sent_today"] == 25
        assert stats["daily_limit"] == 100
        assert stats["remaining_today"] == 75
        assert stats["usage_percentage"] == 25.0
        assert stats["last_reset_date"] == mailgun_service.last_reset_date.isoformat()

    def test_brand_colors_configuration(self, mailgun_service):
        """Marka renkleri konfigürasyonu testi"""
        assert "primary" in mailgun_service.brand_colors
        assert mailgun_service.brand_colors["primary"] == "#667eea"
        assert "secondary" in mailgun_service.brand_colors
        assert mailgun_service.brand_colors["secondary"] == "#764ba2"

    def test_email_with_custom_from_name(self, mailgun_service):
        """Özel gönderen adı ile email testi"""
        with patch("backend.services.mailgun_service.requests.post") as mock_post:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"id": "test-id"}
            mock_post.return_value = mock_response

            mailgun_service.send_email(
                to_email="test@example.com",
                subject="Test",
                html_content="<p>Test</p>",
                from_name="Custom Sender",
            )

            call_data = mock_post.call_args[1]["data"]
            assert call_data["from"] == "Custom Sender <test@example.com>"

    def test_email_with_text_content(self, mailgun_service):
        """Metin içerikli email testi"""
        with patch("backend.services.mailgun_service.requests.post") as mock_post:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"id": "test-id"}
            mock_post.return_value = mock_response

            mailgun_service.send_email(
                to_email="test@example.com",
                subject="Test",
                html_content="<p>Test</p>",
                text_content="Plain text content",
            )

            call_data = mock_post.call_args[1]["data"]
            assert call_data["text"] == "Plain text content"

    @patch("backend.services.mailgun_service.MailgunService.send_email")
    def test_send_new_jobs_email(self, mock_send_email, mailgun_service):
        """Yeni iş ilanları email testi"""
        mock_send_email.return_value = {"success": True}

        jobs = [
            {"title": "Python Developer", "company": "TechCorp", "location": "Remote"},
            {
                "title": "React Developer",
                "company": "StartupInc",
                "location": "Istanbul",
            },
        ]
        user_preferences = {"skills": ["Python", "React"], "remote_only": True}

        result = mailgun_service.send_new_jobs_email(
            "test@example.com", "John Doe", jobs, user_preferences
        )

        assert result is True
        mock_send_email.assert_called_once()

        call_args = mock_send_email.call_args[1]
        assert "Python Developer" in call_args["html_content"]
        assert "TechCorp" in call_args["html_content"]

    @patch("backend.services.mailgun_service.MailgunService.send_email")
    def test_send_application_status_email(self, mock_send_email, mailgun_service):
        """Başvuru durumu email testi"""
        mock_send_email.return_value = {"success": True}

        result = mailgun_service.send_application_status_email(
            "test@example.com",
            "John Doe",
            "Senior Developer",
            "TechCompany",
            "accepted",
        )

        assert result is True
        mock_send_email.assert_called_once()

        call_args = mock_send_email.call_args[1]
        assert "Senior Developer" in call_args["html_content"]
        assert "TechCompany" in call_args["html_content"]
        assert "John Doe" in call_args["html_content"]
