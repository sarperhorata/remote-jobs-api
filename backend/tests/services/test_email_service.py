import pytest
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, Any
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

class TestEmailService:
    """Test suite for Email Service functionality."""

    def test_email_validation(self):
        """Test email validation functionality."""
        import re
        
        def validate_email(email: str) -> bool:
            """Validate email format using regex."""
            pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            return bool(re.match(pattern, email))

        # Test valid emails
        assert validate_email("user@example.com") == True
        assert validate_email("test.user+tag@domain.co.uk") == True
        assert validate_email("user_123@sub.domain.com") == True

        # Test invalid emails
        assert validate_email("invalid-email") == False
        assert validate_email("@domain.com") == False
        assert validate_email("user@") == False
        assert validate_email("user@domain") == False
        assert validate_email("") == False

    def test_email_template_rendering(self):
        """Test email template rendering."""
        def render_email_template(template_name: str, context: Dict[str, Any]) -> str:
            """Render email template with context variables."""
            templates = {
                "welcome": "Welcome {user_name}! Your account has been created.",
                "job_alert": "New job posted: {job_title} at {company_name}",
                "password_reset": "Click here to reset your password: {reset_link}",
                "application_status": "Your application for {job_title} is now {status}"
            }
            
            if template_name not in templates:
                raise ValueError(f"Template '{template_name}' not found")
            
            template = templates[template_name]
            return template.format(**context)

        # Test welcome email
        result = render_email_template("welcome", {"user_name": "John Doe"})
        assert "Welcome John Doe!" in result

        # Test job alert email
        result = render_email_template("job_alert", {
            "job_title": "Software Engineer",
            "company_name": "Tech Corp"
        })
        assert "Software Engineer" in result
        assert "Tech Corp" in result

        # Test template not found
        with pytest.raises(ValueError):
            render_email_template("nonexistent", {})

    @patch('smtplib.SMTP')
    def test_email_sending(self, mock_smtp):
        """Test email sending functionality."""
        # Mock SMTP instance
        mock_server = MagicMock()
        mock_smtp.return_value = mock_server

        def send_email(to_email: str, subject: str, body: str, smtp_config: Dict = None):
            """Send email using SMTP."""
            if not smtp_config:
                smtp_config = {
                    "host": "smtp.gmail.com",
                    "port": 587,
                    "username": "test@example.com",
                    "password": "password"
                }

            # Create message
            msg = MIMEMultipart()
            msg['From'] = smtp_config["username"]
            msg['To'] = to_email
            msg['Subject'] = subject
            msg.attach(MIMEText(body, 'plain'))

            # Connect and send
            server = smtplib.SMTP(smtp_config["host"], smtp_config["port"])
            server.starttls()
            server.login(smtp_config["username"], smtp_config["password"])
            server.send_message(msg)
            server.quit()

            return {"status": "sent", "message_id": "test123"}

        # Test successful send
        result = send_email("user@example.com", "Test Subject", "Test Body")
        assert result["status"] == "sent"

        # Verify SMTP calls
        mock_smtp.assert_called_once_with("smtp.gmail.com", 587)
        mock_server.starttls.assert_called_once()
        mock_server.login.assert_called_once()
        mock_server.send_message.assert_called_once()
        mock_server.quit.assert_called_once()

    def test_bulk_email_sending(self):
        """Test bulk email sending with rate limiting."""
        import time
        
        def send_bulk_emails(recipients: list, subject: str, body: str, rate_limit: int = 5):
            """Send emails to multiple recipients with rate limiting."""
            sent_emails = []
            failed_emails = []
            
            for i, recipient in enumerate(recipients):
                try:
                    # Simulate sending
                    if "@invalid" in recipient:
                        raise Exception("Invalid email address")
                    
                    # Rate limiting - wait between sends
                    if i > 0 and i % rate_limit == 0:
                        time.sleep(0.1)  # Reduced for testing
                    
                    sent_emails.append({
                        "recipient": recipient,
                        "status": "sent",
                        "timestamp": time.time()
                    })
                    
                except Exception as e:
                    failed_emails.append({
                        "recipient": recipient,
                        "error": str(e),
                        "timestamp": time.time()
                    })
            
            return {
                "sent": sent_emails,
                "failed": failed_emails,
                "total_sent": len(sent_emails),
                "total_failed": len(failed_emails)
            }

        recipients = [
            "user1@example.com",
            "user2@example.com", 
            "user3@invalid.com",
            "user4@example.com"
        ]

        result = send_bulk_emails(recipients, "Test Subject", "Test Body")
        
        assert result["total_sent"] == 3
        assert result["total_failed"] == 1
        assert "user3@invalid.com" in [f["recipient"] for f in result["failed"]]

    def test_email_queue_processing(self):
        """Test email queue processing."""
        import queue
        
        def process_email_queue(email_queue: queue.Queue, max_retries: int = 3):
            """Process emails from queue with retry logic."""
            processed = []
            
            while not email_queue.empty():
                try:
                    email_data = email_queue.get_nowait()
                    
                    # Simulate sending
                    if email_data.get("fail", False):
                        # Retry logic
                        retries = email_data.get("retries", 0)
                        if retries < max_retries:
                            email_data["retries"] = retries + 1
                            email_queue.put(email_data)  # Re-queue for retry
                            continue
                        else:
                            processed.append({"status": "failed", "email": email_data})
                    else:
                        processed.append({"status": "sent", "email": email_data})
                    
                except queue.Empty:
                    break
            
            return processed

        # Create test queue
        test_queue = queue.Queue()
        test_queue.put({"to": "user1@example.com", "subject": "Test 1"})
        test_queue.put({"to": "user2@example.com", "subject": "Test 2", "fail": True})
        test_queue.put({"to": "user3@example.com", "subject": "Test 3"})

        result = process_email_queue(test_queue)
        
        # Should have processed 2 successful emails and 1 failed after retries
        sent_count = len([r for r in result if r["status"] == "sent"])
        failed_count = len([r for r in result if r["status"] == "failed"])
        
        assert sent_count == 2
        assert failed_count == 1

    def test_email_unsubscribe_handling(self):
        """Test email unsubscribe functionality."""
        def handle_unsubscribe(email: str, unsubscribe_token: str, user_preferences: Dict):
            """Handle user unsubscribe requests."""
            # Verify token (simplified)
            expected_token = f"unsub_{email.replace('@', '_at_').replace('.', '_dot_')}"
            
            if unsubscribe_token != expected_token:
                return {"status": "error", "message": "Invalid unsubscribe token"}
            
            # Update preferences
            if email not in user_preferences:
                user_preferences[email] = {}
            
            user_preferences[email]["email_notifications"] = False
            user_preferences[email]["unsubscribed_at"] = "2023-12-01T10:00:00Z"
            
            return {
                "status": "success", 
                "message": "Successfully unsubscribed",
                "email": email
            }

        user_prefs = {}
        
        # Test valid unsubscribe
        token = "unsub_user_at_example_dot_com"
        result = handle_unsubscribe("user@example.com", token, user_prefs)
        
        assert result["status"] == "success"
        assert user_prefs["user@example.com"]["email_notifications"] == False

        # Test invalid token
        result = handle_unsubscribe("user@example.com", "invalid_token", user_prefs)
        assert result["status"] == "error"
