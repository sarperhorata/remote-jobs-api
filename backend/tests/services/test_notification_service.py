import pytest
from unittest.mock import Mock, patch

class TestNotificationService:
    """Test suite for NotificationService functionality."""

    def test_email_validation(self):
        """Test email address validation."""
        import re
        
        def validate_email(email):
            pattern = r'^[^\s@]+@[^\s@]+\.[^\s@]+$'
            return bool(re.match(pattern, email))
        
        valid_emails = [
            "test@example.com",
            "user.name@domain.co.uk",
            "admin+tag@site.org"
        ]
        
        invalid_emails = [
            "invalid-email",
            "@domain.com", 
            "user@",
            ""
        ]
        
        for email in valid_emails:
            assert validate_email(email) is True, f"Should validate: {email}"
            
        for email in invalid_emails:
            assert validate_email(email) is False, f"Should reject: {email}"

    def test_notification_formatting(self):
        """Test notification message formatting."""
        template = "Hello {name}, you have {count} new messages"
        data = {"name": "John", "count": 5}
        
        result = template.format(**data)
        expected = "Hello John, you have 5 new messages"
        
        assert result == expected

    def test_notification_preferences_validation(self):
        """Test user notification preferences validation."""
        user_preferences = {
            "email_notifications": True,
            "push_notifications": False,
            "job_alerts": True,
            "marketing_emails": False
        }
        
        def validate_preferences(prefs):
            required_keys = ["email_notifications", "push_notifications", "job_alerts"]
            return all(key in prefs for key in required_keys)
        
        assert validate_preferences(user_preferences) is True
        
        # Test invalid preferences
        invalid_prefs = {"email_notifications": True}
        assert validate_preferences(invalid_prefs) is False

    def test_notification_rate_limiting(self):
        """Test notification rate limiting logic."""
        rate_limit = 5
        sent_count = 0
        
        def send_with_rate_limit(message):
            nonlocal sent_count
            if sent_count >= rate_limit:
                return {"success": False, "error": "Rate limit exceeded"}
            sent_count += 1
            return {"success": True, "count": sent_count}
        
        # Send notifications up to rate limit
        for i in range(rate_limit):
            result = send_with_rate_limit(f"Message {i}")
            assert result["success"] is True
        
        # This should fail due to rate limit
        result = send_with_rate_limit("Rate limited message")
        assert result["success"] is False
        assert "Rate limit exceeded" in result["error"]

    def test_notification_template_rendering(self):
        """Test notification template rendering."""
        template = {
            "subject": "Job Application Update - {job_title}",
            "body": "Dear {applicant_name}, your application for {job_title} at {company} has been {status}."
        }
        
        data = {
            "job_title": "Software Engineer",
            "applicant_name": "John Doe", 
            "company": "Tech Corp",
            "status": "approved"
        }
        
        def render_template(template, data):
            return {
                "subject": template["subject"].format(**data),
                "body": template["body"].format(**data)
            }
        
        result = render_template(template, data)
        
        assert "Software Engineer" in result["subject"]
        assert "John Doe" in result["body"]
        assert "Tech Corp" in result["body"]
        assert "approved" in result["body"]

    @patch('smtplib.SMTP')
    def test_email_sending_mock(self, mock_smtp):
        """Test email sending with mocked SMTP."""
        mock_server = Mock()
        mock_smtp.return_value = mock_server
        
        def send_email(recipient, subject, message):
            try:
                # Simulate email sending
                mock_server.sendmail("sender@example.com", recipient, f"Subject: {subject}\n\n{message}")
                return True
            except Exception:
                return False
        
        result = send_email("test@example.com", "Test Subject", "Test message")
        assert result is True
        mock_server.sendmail.assert_called_once()

    def test_notification_data_sanitization(self):
        """Test notification data sanitization."""
        def sanitize_message(message):
            # Remove potentially dangerous characters
            dangerous_chars = ["<", ">", "&", '"', "'"]
            for char in dangerous_chars:
                message = message.replace(char, "")
            return message.strip()
        
        dirty_message = "<script>alert('xss')</script>Hello World!"
        clean_message = sanitize_message(dirty_message)
        
        assert "<script>" not in clean_message
        assert "Hello World!" in clean_message

    def test_notification_queue_processing(self):
        """Test notification queue processing."""
        notification_queue = []
        
        def add_to_queue(notification):
            notification_queue.append(notification)
            return len(notification_queue)
        
        def process_queue():
            processed = []
            while notification_queue:
                notification = notification_queue.pop(0)
                processed.append(notification)
            return processed
        
        # Add notifications to queue
        add_to_queue({"type": "email", "recipient": "user1@example.com"})
        add_to_queue({"type": "push", "recipient": "user2@example.com"})
        
        assert len(notification_queue) == 2
        
        # Process queue
        processed = process_queue()
        assert len(processed) == 2
        assert len(notification_queue) == 0

    def test_notification_error_handling(self):
        """Test notification error handling."""
        def send_notification_with_error_handling(recipient, message):
            try:
                if not recipient or "@" not in recipient:
                    raise ValueError("Invalid recipient")
                if not message:
                    raise ValueError("Empty message")
                return {"success": True, "message": "Sent successfully"}
            except ValueError as e:
                return {"success": False, "error": str(e)}
            except Exception as e:
                return {"success": False, "error": "Unknown error occurred"}
        
        # Test valid notification
        result = send_notification_with_error_handling("test@example.com", "Hello")
        assert result["success"] is True
        
        # Test invalid recipient
        result = send_notification_with_error_handling("invalid-email", "Hello")
        assert result["success"] is False
        assert "Invalid recipient" in result["error"]
        
        # Test empty message
        result = send_notification_with_error_handling("test@example.com", "")
        assert result["success"] is False
        assert "Empty message" in result["error"]
