import logging
import smtplib
import requests
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, Any, Optional, List
from datetime import datetime
import json

from models.models import Notification, NotificationType

logger = logging.getLogger(__name__)

class NotificationManager:
    """
    Class responsible for notification management
    """
    
    def __init__(self):
        # Email settings
        self.email_host = os.getenv("EMAIL_HOST", "smtp.gmail.com")
        self.email_port = int(os.getenv("EMAIL_PORT", "587"))
        self.email_user = os.getenv("EMAIL_USER", "")
        self.email_password = os.getenv("EMAIL_PASSWORD", "")
        self.email_from = os.getenv("EMAIL_FROM", "")
        
        # Telegram settings
        self.telegram_bot_token = os.getenv("TELEGRAM_BOT_TOKEN", "")
        
        # Request headers
        self.headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'Remote-Jobs-Monitor/1.0'
        }
    
    async def send_notification(self, notification: Notification, change_type: str, data: Dict[str, Any]) -> bool:
        """
        Sends a notification
        """
        logger.info(f"Sending notification of type {notification.notification_type}")
        
        try:
            if notification.notification_type == NotificationType.EMAIL:
                return await self._send_email_notification(notification, change_type, data)
            elif notification.notification_type == NotificationType.TELEGRAM:
                return await self._send_telegram_notification(notification, change_type, data)
            elif notification.notification_type == NotificationType.WEBHOOK:
                return await self._send_webhook_notification(notification, change_type, data)
            else:
                logger.error(f"Unsupported notification type: {notification.notification_type}")
                return False
        except Exception as e:
            logger.error(f"Error sending notification: {str(e)}")
            return False
    
    async def _send_email_notification(self, notification: Notification, change_type: str, data: Dict[str, Any]) -> bool:
        """
        Sends an email notification
        """
        if not self.email_user or not self.email_password:
            logger.error("Email credentials not configured")
            return False
        
        try:
            # Get recipient email from notification config
            to_email = notification.config.get("email")
            if not to_email:
                logger.error("No recipient email specified in notification config")
                return False
            
            # Create notification content
            subject, body = self._create_notification_content(change_type, data)
            
            # Send email
            msg = MIMEMultipart()
            msg['From'] = self.email_from or self.email_user
            msg['To'] = to_email
            msg['Subject'] = subject
            
            msg.attach(MIMEText(body, 'html'))
            
            server = smtplib.SMTP(self.email_host, self.email_port)
            server.starttls()
            server.login(self.email_user, self.email_password)
            server.send_message(msg)
            server.quit()
            
            logger.info(f"Email notification sent to {to_email}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email notification: {str(e)}")
            return False
    
    async def _send_telegram_notification(self, notification: Notification, change_type: str, data: Dict[str, Any]) -> bool:
        """
        Sends a Telegram notification
        """
        if not self.telegram_bot_token:
            logger.error("Telegram bot token not configured")
            return False
        
        try:
            # Get chat ID from notification config
            chat_id = notification.config.get("chat_id")
            if not chat_id:
                logger.error("No chat_id specified in notification config")
                return False
            
            # Create notification content
            _, text = self._create_notification_content(change_type, data, is_html=False)
            
            # Send request to Telegram API
            url = f"https://api.telegram.org/bot{self.telegram_bot_token}/sendMessage"
            payload = {
                "chat_id": chat_id,
                "text": text,
                "parse_mode": "Markdown"
            }
            
            response = requests.post(url, json=payload)
            response.raise_for_status()
            
            logger.info(f"Telegram notification sent to chat_id {chat_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send Telegram notification: {str(e)}")
            return False
    
    async def _send_webhook_notification(self, notification: Notification, change_type: str, data: Dict[str, Any]) -> bool:
        """
        Sends a webhook notification
        """
        try:
            # Get webhook URL from notification config
            webhook_url = notification.config.get("webhook_url")
            if not webhook_url:
                logger.error("No webhook_url specified in notification config")
                return False
            
            # Create webhook payload
            payload = {
                "notification_type": str(notification.notification_type),
                "notification_id": notification.id,
                "change_type": change_type,
                "data": data,
                "timestamp": datetime.now().isoformat()
            }
            
            # Send POST request to webhook
            response = requests.post(webhook_url, json=payload, headers=self.headers)
            response.raise_for_status()
            
            logger.info(f"Webhook notification sent to {webhook_url}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send webhook notification: {str(e)}")
            return False
    
    def _create_notification_content(self, change_type: str, data: Dict[str, Any], is_html: bool = True) -> tuple:
        """
        Creates notification content
        """
        title = data.get("title", "Unnamed job")
        company = data.get("company", "Unknown company")
        url = data.get("url", "#")
        location = data.get("location", "No location specified")
        
        if change_type == "new":
            subject = f"New Job: {title} at {company}"
            
            if is_html:
                body = f"""
                <h1>New Job Listing Found!</h1>
                <p><strong>Job Title:</strong> {title}</p>
                <p><strong>Company:</strong> {company}</p>
                <p><strong>Location:</strong> {location}</p>
                <p><a href="{url}" target="_blank">View Job Listing</a></p>
                """
            else:
                body = f"""
                *New Job Listing Found!*
                
                *Job Title:* {title}
                *Company:* {company}
                *Location:* {location}
                
                [View Job Listing]({url})
                """
        
        elif change_type == "updated":
            subject = f"Updated Job: {title} at {company}"
            
            if is_html:
                body = f"""
                <h1>Job Listing Updated!</h1>
                <p><strong>Job Title:</strong> {title}</p>
                <p><strong>Company:</strong> {company}</p>
                <p><strong>Location:</strong> {location}</p>
                <p><a href="{url}" target="_blank">View Updated Job Listing</a></p>
                """
            else:
                body = f"""
                *Job Listing Updated!*
                
                *Job Title:* {title}
                *Company:* {company}
                *Location:* {location}
                
                [View Updated Job Listing]({url})
                """
        
        elif change_type == "removed":
            subject = f"Removed Job: {title} at {company}"
            
            if is_html:
                body = f"""
                <h1>Job Listing Removed!</h1>
                <p><strong>Job Title:</strong> {title}</p>
                <p><strong>Company:</strong> {company}</p>
                <p><strong>URL:</strong> <a href="{url}" target="_blank">{url}</a></p>
                """
            else:
                body = f"""
                *Job Listing Removed!*
                
                *Job Title:* {title}
                *Company:* {company}
                *URL:* {url}
                """
        
        else:
            subject = f"Job Alert: {title} at {company}"
            
            if is_html:
                body = f"""
                <h1>Job Alert</h1>
                <p><strong>Job Title:</strong> {title}</p>
                <p><strong>Company:</strong> {company}</p>
                <p><strong>Location:</strong> {location}</p>
                <p><a href="{url}" target="_blank">View Job Listing</a></p>
                """
            else:
                body = f"""
                *Job Alert*
                
                *Job Title:* {title}
                *Company:* {company}
                *Location:* {location}
                
                [View Job Listing]({url})
                """
        
        return subject, body
    
    async def test_notification(self, notification: Notification) -> bool:
        """
        Sends a test notification
        """
        test_data = {
            "title": "Test Job Position",
            "company": "Test Company",
            "url": "https://example.com/job",
            "location": "Remote",
            "description": "This is a test notification from Remote Jobs Monitor."
        }
        
        return await self.send_notification(notification, "test", test_data) 