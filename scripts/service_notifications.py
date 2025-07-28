#!/usr/bin/env python3
"""
Service Notifications for Buzz2Remote
Handles Telegram notifications for cronjob status
"""

import os
import requests
import logging
from datetime import datetime
from typing import Dict, Any, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ServiceNotifier:
    def __init__(self):
        """Initialize Service Notifier with Telegram credentials"""
        self.bot_token = os.getenv('TELEGRAM_BOT_TOKEN', '8116251711:AAFhGxXtOJu2eCqCORoDr46XWq7ejqMeYnY')
        self.chat_id = os.getenv('TELEGRAM_CHAT_ID', '-1002424698891')
        self.base_url = f"https://api.telegram.org/bot{self.bot_token}"
        
    def send_telegram_message(self, message: str, parse_mode: str = "HTML") -> bool:
        """Send message to Telegram"""
        try:
            url = f"{self.base_url}/sendMessage"
            payload = {
                'chat_id': self.chat_id,
                'text': message,
                'parse_mode': parse_mode
            }
            
            response = requests.post(url, json=payload, timeout=10)
            
            if response.status_code == 200:
                logger.info("Telegram message sent successfully")
                return True
            else:
                logger.error(f"Failed to send Telegram message: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Error sending Telegram message: {e}")
            return False
    
    def notify_cronjob_success(self, job_name: str, details: Dict[str, Any] = None) -> bool:
        """Send success notification for cronjob"""
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            message = f"✅ <b>Cronjob Success</b>\n\n"
            message += f"🔧 <b>Job</b>: {job_name}\n"
            message += f"⏰ <b>Time</b>: {timestamp}\n"
            
            if details:
                message += f"\n📊 <b>Details</b>:\n"
                for key, value in details.items():
                    message += f"• {key}: {value}\n"
            
            message += f"\n🚀 <b>Buzz2Remote System</b>"
            
            return self.send_telegram_message(message)
            
        except Exception as e:
            logger.error(f"Error sending success notification: {e}")
            return False
    
    def notify_cronjob_failure(self, job_name: str, error: str, details: Dict[str, Any] = None) -> bool:
        """Send failure notification for cronjob"""
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            message = f"❌ *Cronjob Failed*\n\n"
            message += f"🔧 *Job*: {job_name}\n"
            message += f"⏰ *Time*: {timestamp}\n"
            message += f"🚨 *Error*: {error}\n"
            
            if details:
                message += f"\n📊 *Details*:\n"
                for key, value in details.items():
                    message += f"• {key}: {value}\n"
            
            message += f"\n🔧 *Action Required* - Check logs and restart if needed"
            message += f"\n🚀 *Buzz2Remote System*"
            
            return self.send_telegram_message(message)
            
        except Exception as e:
            logger.error(f"Error sending failure notification: {e}")
            return False
    
    def notify_external_api_results(self, results: Dict[str, Any]) -> bool:
        """Send External API crawler results"""
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            message = f"🕷️ *External API Crawler Results*\n\n"
            message += f"⏰ *Time*: {timestamp}\n"
            
            if results.get('success', False):
                message += f"✅ *Status*: Success\n"
                total_jobs = results.get('total_new_jobs', 0)
                message += f"📋 *New Jobs*: {total_jobs}\n"
                
                # API breakdown
                if results.get('api_results'):
                    message += f"\n📊 *API Breakdown*:\n"
                    for api_name, result in results['api_results'].items():
                        jobs_count = result.get('new_jobs', 0)
                        status = "✅" if result.get('success') else "❌"
                        message += f"• {status} {api_name}: {jobs_count} jobs\n"
            else:
                message += f"❌ *Status*: Failed\n"
                message += f"🚨 *Error*: {results.get('error', 'Unknown error')}\n"
            
            message += f"\n🚀 *Buzz2Remote System*"
            
            return self.send_telegram_message(message)
            
        except Exception as e:
            logger.error(f"Error sending API results notification: {e}")
            return False
    
    def notify_system_health(self, health_data: Dict[str, Any]) -> bool:
        """Send system health notification"""
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            message = f"🏥 *System Health Check*\n\n"
            message += f"⏰ *Time*: {timestamp}\n"
            
            # Overall status
            if health_data.get('healthy', True):
                message += f"✅ *Status*: Healthy\n"
            else:
                message += f"❌ *Status*: Issues Detected\n"
            
            # Database
            db_status = health_data.get('database', {})
            db_icon = "✅" if db_status.get('healthy') else "❌"
            message += f"{db_icon} *Database*: {db_status.get('status', 'Unknown')}\n"
            
            # Server resources
            resources = health_data.get('resources', {})
            if resources:
                cpu = resources.get('cpu_percent', 0)
                memory = resources.get('memory_percent', 0)
                disk = resources.get('disk_percent', 0)
                
                message += f"\n📊 *Resources*:\n"
                message += f"• CPU: {cpu}%\n"
                message += f"• Memory: {memory}%\n"
                message += f"• Disk: {disk}%\n"
            
            # Active cronjobs
            active_jobs = health_data.get('active_cronjobs', 0)
            total_jobs = health_data.get('total_cronjobs', 0)
            message += f"\n🔧 *Cronjobs*: {active_jobs}/{total_jobs} active\n"
            
            # Warnings or errors
            if health_data.get('warnings'):
                message += f"\n⚠️ *Warnings*:\n"
                for warning in health_data['warnings'][:3]:  # Limit to 3
                    message += f"• {warning}\n"
            
            message += f"\n🚀 *Buzz2Remote System*"
            
            return self.send_telegram_message(message)
            
        except Exception as e:
            logger.error(f"Error sending health notification: {e}")
            return False
    
    def notify_critical_alert(self, alert_type: str, message_text: str, details: Dict[str, Any] = None) -> bool:
        """Send critical system alert"""
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            message = f"🚨 *CRITICAL ALERT*\n\n"
            message += f"⚠️ *Type*: {alert_type}\n"
            message += f"⏰ *Time*: {timestamp}\n"
            message += f"📝 *Message*: {message_text}\n"
            
            if details:
                message += f"\n📊 *Details*:\n"
                for key, value in details.items():
                    message += f"• {key}: {value}\n"
            
            message += f"\n🚨 *IMMEDIATE ACTION REQUIRED*"
            message += f"\n🚀 *Buzz2Remote System*"
            
            return self.send_telegram_message(message)
            
        except Exception as e:
            logger.error(f"Error sending critical alert: {e}")
            return False
    
    def test_connection(self) -> bool:
        """Test Telegram connection"""
        try:
            test_message = f"🧪 <b>Test Message</b>\n\n"
            test_message += f"⏰ Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            test_message += f"✅ Telegram connection is working!\n"
            test_message += f"🚀 <b>Buzz2Remote System</b>"
            
            return self.send_telegram_message(test_message)
            
        except Exception as e:
            logger.error(f"Error testing Telegram connection: {e}")
            return False

def main():
    """Test the notification system"""
    notifier = ServiceNotifier()
    
    print("🧪 Testing Telegram notification system...")
    
    # Test connection
    if notifier.test_connection():
        print("✅ Telegram connection test successful!")
    else:
        print("❌ Telegram connection test failed!")
        return
    
    # Test success notification
    success_result = notifier.notify_cronjob_success(
        "test_job",
        {"new_jobs": 5, "processed_apis": 3, "duration": "45 seconds"}
    )
    
    if success_result:
        print("✅ Success notification sent!")
    else:
        print("❌ Success notification failed!")

if __name__ == "__main__":
    main() 