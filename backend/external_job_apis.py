import asyncio
import json
import logging
import os
import time
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import requests

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class JobData:
    title: str
    company: str
    location: str
    description: str
    url: str
    salary: Optional[str]
    job_type: Optional[str]
    posted_date: Optional[str]
    source: str
    external_id: str


class RateLimiter:
    def __init__(self, max_requests: int, time_period_days: int = 1):
        self.max_requests = max_requests
        self.time_period_seconds = time_period_days * 24 * 3600
        self.requests = []

    def can_make_request(self) -> bool:
        now = time.time()
        # Remove old requests
        self.requests = [
            req_time
            for req_time in self.requests
            if now - req_time < self.time_period_seconds
        ]
        return len(self.requests) < self.max_requests

    def record_request(self):
        self.requests.append(time.time())

    def requests_remaining(self) -> int:
        now = time.time()
        self.requests = [
            req_time
            for req_time in self.requests
            if now - req_time < self.time_period_seconds
        ]
        return max(0, self.max_requests - len(self.requests))

    def next_reset_date(self) -> Optional[datetime]:
        if not self.requests:
            return None
        oldest_request = min(self.requests)
        return datetime.fromtimestamp(oldest_request + self.time_period_seconds)


class ServiceNotifier:
    """Enhanced notification service for Telegram integration"""

    def __init__(self):
        self.telegram_token = os.getenv("TELEGRAM_BOT_TOKEN")
        self.telegram_chat_id = os.getenv("TELEGRAM_CHAT_ID")
        self.enabled = bool(self.telegram_token and self.telegram_chat_id)

        if not self.enabled:
            logger.warning(
                "Telegram notifications disabled - missing TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID"
            )

    def _send_message(self, message: str):
        """Send message to Telegram with better error handling (DISABLED - only logs)"""
        # Log the message instead of sending to Telegram
        logger.info(f"TELEGRAM NOTIFICATION (DISABLED): {message}")
        return

        # Original code commented out to disable Telegram notifications
        # if not self.enabled:
        #     logger.info(f"Notification (disabled): {message}")
        #     return

        # try:
        #     url = f"https://api.telegram.org/bot{self.telegram_token}/sendMessage"
        #     payload = {
        #         "chat_id": self.telegram_chat_id,
        #         "text": message,
        #         "parse_mode": "HTML",
        #         "disable_web_page_preview": True,
        #     }

        #     response = requests.post(url, json=payload, timeout=10)

        #     if response.status_code == 200:
        #         logger.debug("✅ Telegram notification sent successfully")
        #     else:
        #         logger.error(
        #             f"❌ Telegram notification failed: {response.status_code} - {response.text}"
        #         )

        # except Exception as e:
        #     logger.error(f"❌ Error sending Telegram notification: {str(e)}")

    def send_crawler_summary(self, crawler_data: Dict[str, Any]):
        """Send comprehensive crawler summary"""
        try:
            # Import telegram bot
            from telegram_bot.bot_manager import bot_manager

            bot = bot_manager.bot_instance

            if bot and bot.enabled:
                # Use the new crawler notification method
                asyncio.create_task(bot.send_crawler_notification(crawler_data))
            else:
                # Fallback to direct message
                self._send_fallback_crawler_message(crawler_data)

        except Exception as e:
            logger.error(f"Error sending crawler summary: {str(e)}")
            # Fallback to direct message
            self._send_fallback_crawler_message(crawler_data)

    def _send_fallback_crawler_message(self, crawler_data: Dict[str, Any]):
        """Fallback crawler message when bot is not available"""
        status_emoji = (
            "✅"
            if crawler_data.get("status") == "success"
            else "⚠️" if crawler_data.get("status") == "warning" else "❌"
        )

        message = f"{status_emoji} <b>CRAWLER UPDATE</b>\n\n"
        message += f"<b>Service:</b> {crawler_data.get('service', 'Unknown')}\n"
        message += f"<b>Status:</b> {crawler_data.get('status', 'unknown').upper()}\n"

        if "companies_processed" in crawler_data:
            message += (
                f"<b>Companies Processed:</b> {crawler_data['companies_processed']}\n"
            )

        if "jobs_found" in crawler_data:
            message += f"<b>Jobs Found:</b> {crawler_data['jobs_found']}\n"

        if "new_jobs" in crawler_data:
            message += f"<b>New Jobs:</b> {crawler_data['new_jobs']}\n"

        if "disabled_endpoints" in crawler_data and crawler_data["disabled_endpoints"]:
            message += f"\n🚫 <b>Disabled Endpoints:</b> {len(crawler_data['disabled_endpoints'])}\n"
            for endpoint in crawler_data["disabled_endpoints"][:3]:  # Show max 3
                reason = endpoint.get("reason", "Unknown")
                message += f"• {reason}\n"

        message += f"\n🕐 <b>Time:</b> {crawler_data.get('timestamp', datetime.now().isoformat())}"

        self._send_message(message)


class APIErrorHandler:
    """Enhanced API error handler with better disabled endpoint management"""

    def __init__(self):
        self.disabled_endpoints_file = ".disabled_api_endpoints.json"
        self.quota_exceeded_file = ".quota_exceeded_apis.json"
        self.disabled_endpoints = self._load_disabled_endpoints()
        self.quota_exceeded = self._load_quota_exceeded()
        self.notifier = ServiceNotifier()

        # Enhanced error patterns
        self.disabled_patterns = [
            "permanently disabled",
            "endpoint does not exist",
            "endpoint is disabled for your subscription",
            "this endpoint is disabled",
            "access denied to this endpoint",
            "endpoint not available",
            "subscription does not include this endpoint",
        ]

        self.quota_patterns = [
            "you have exceeded monthly quota",
            "monthly quota exceeded",
            "quota limit reached",
            "rate limit exceeded",
            "too many requests",
            "quota exhausted",
            "monthly limit exceeded",
        ]

    def _load_disabled_endpoints(self) -> Dict[str, Dict]:
        """Load disabled endpoints from file"""
        try:
            if os.path.exists(self.disabled_endpoints_file):
                with open(self.disabled_endpoints_file, "r") as f:
                    return json.load(f)
            return {}
        except Exception as e:
            logger.error(f"Error loading disabled endpoints: {e}")
            return {}

    def _save_disabled_endpoints(self):
        """Save disabled endpoints to file"""
        try:
            with open(self.disabled_endpoints_file, "w") as f:
                json.dump(self.disabled_endpoints, f, indent=2)
        except Exception as e:
            logger.error(f"❌ Error saving disabled endpoints: {e}")

    def _load_quota_exceeded(self) -> Dict[str, Dict]:
        """Load quota exceeded APIs from file"""
        try:
            if os.path.exists(self.quota_exceeded_file):
                with open(self.quota_exceeded_file, "r") as f:
                    return json.load(f)
            return {}
        except Exception as e:
            logger.error(f"Error loading quota exceeded: {e}")
            return {}

    def _save_quota_exceeded(self):
        """Save quota exceeded APIs to file"""
        try:
            with open(self.quota_exceeded_file, "w") as f:
                json.dump(self.quota_exceeded, f, indent=2)
        except Exception as e:
            logger.error(f"❌ Error saving quota exceeded: {e}")

    def handle_api_error(
        self, api_name: str, endpoint: str, status_code: int, error_message: str
    ):
        """Enhanced API error handling"""
        error_lower = error_message.lower()

        # Check for permanently disabled endpoints
        if any(pattern in error_lower for pattern in self.disabled_patterns):
            self.disable_endpoint(api_name, endpoint, error_message)
            return

        # Check for quota exceeded errors
        if status_code == 429 or any(
            pattern in error_lower for pattern in self.quota_patterns
        ):
            self.mark_quota_exceeded(api_name, error_message)
            return

        # Check for 404 errors (endpoint not found)
        if status_code == 404:
            self.disable_endpoint(
                api_name, endpoint, f"Endpoint not found (404): {error_message}"
            )
            return

        # Check for 403 errors (access forbidden)
        if status_code == 403:
            self.disable_endpoint(
                api_name, endpoint, f"Access forbidden (403): {error_message}"
            )
            return

        # Check for other 4xx errors
        if 400 <= status_code < 500:
            self.notifier._send_message(
                f"""⚠️ <b>{api_name} - CLIENT ERROR</b>

🎯 <b>Endpoint:</b> {endpoint}
📊 <b>Status:</b> {status_code}
❌ <b>Error:</b> {error_message[:200]}

🔍 <b>Action:</b> Check API configuration"""
            )

        # Check for 5xx errors
        elif 500 <= status_code < 600:
            self.notifier._send_message(
                f"""🔥 <b>{api_name} - SERVER ERROR</b>

🎯 <b>Endpoint:</b> {endpoint}
📊 <b>Status:</b> {status_code}
❌ <b>Error:</b> {error_message[:200]}

⏳ <b>Action:</b> Will retry later"""
            )

    def disable_endpoint(self, api_name: str, endpoint: str, reason: str):
        """Permanently disable an endpoint with enhanced logging"""
        key = f"{api_name}_{endpoint}"

        if key not in self.disabled_endpoints:
            self.disabled_endpoints[key] = {
                "api_name": api_name,
                "endpoint": endpoint,
                "disabled_at": datetime.now().isoformat(),
                "reason": reason,
            }
            self._save_disabled_endpoints()

            self.notifier._send_message(
                f"""🚫 <b>{api_name} - ENDPOINT PERMANENTLY DISABLED</b>

🎯 <b>Endpoint:</b> {endpoint}
❌ <b>Reason:</b> {reason}
🕐 <b>Disabled at:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

⚠️ <b>This endpoint will not be used anymore until manually re-enabled!</b>

📋 <b>Total disabled endpoints:</b> {len(self.disabled_endpoints)}"""
            )

            logger.warning(
                f"🚫 Permanently disabled endpoint: {api_name}/{endpoint} - {reason}"
            )

    def mark_quota_exceeded(self, api_name: str, reason: str):
        """Mark API as quota exceeded for current month with enhanced tracking"""
        current_month = datetime.now().strftime("%Y-%m")

        if api_name not in self.quota_exceeded:
            self.quota_exceeded[api_name] = {}

        if current_month not in self.quota_exceeded[api_name]:
            self.quota_exceeded[api_name][current_month] = {
                "exceeded_at": datetime.now().isoformat(),
                "reason": reason,
            }
            self._save_quota_exceeded()

            # Calculate days until next month
            next_month = datetime.now().replace(
                day=1, hour=0, minute=0, second=0, microsecond=0
            )
            if next_month.month == 12:
                next_month = next_month.replace(year=next_month.year + 1, month=1)
            else:
                next_month = next_month.replace(month=next_month.month + 1)

            days_until_reset = (next_month - datetime.now()).days + 1

            self.notifier._send_message(
                f"""📛 <b>{api_name} - QUOTA EXCEEDED</b>

❌ <b>Reason:</b> {reason}
📅 <b>Month:</b> {current_month}
🕐 <b>Time:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
⏰ <b>Reset in:</b> {days_until_reset} days

⏸️ <b>This API will be paused until next month!</b>

📊 <b>Total APIs with quota issues:</b> {len(self.quota_exceeded)}"""
            )

            logger.warning(
                f"📛 API quota exceeded: {api_name} - will resume next month"
            )

    def is_endpoint_disabled(self, api_name: str, endpoint: str) -> bool:
        """Check if an endpoint is permanently disabled"""
        key = f"{api_name}_{endpoint}"
        return key in self.disabled_endpoints

    def is_quota_exceeded(self, api_name: str) -> bool:
        """Check if API quota is exceeded for current month"""
        current_month = datetime.now().strftime("%Y-%m")
        return (
            api_name in self.quota_exceeded
            and current_month in self.quota_exceeded[api_name]
        )

    def get_disabled_endpoints_summary(self) -> Dict[str, Any]:
        """Get summary of disabled endpoints for reporting"""
        disabled_list = []
        for key, endpoint_data in self.disabled_endpoints.items():
            disabled_list.append(
                {
                    "api_name": endpoint_data.get("api_name"),
                    "endpoint": endpoint_data.get("endpoint"),
                    "reason": endpoint_data.get("reason", "")[:100]
                    + ("..." if len(endpoint_data.get("reason", "")) > 100 else ""),
                    "disabled_at": endpoint_data.get("disabled_at"),
                }
            )

        return {"count": len(disabled_list), "endpoints": disabled_list}

    def clean_old_quota_records(self):
        """Clean old quota records from previous months"""
        current_month = datetime.now().strftime("%Y-%m")
        cleaned_apis = []

        for api_name in list(self.quota_exceeded.keys()):
            # Remove old month records
            old_records = []
            for month in list(self.quota_exceeded[api_name].keys()):
                if month < current_month:
                    old_records.append(month)
                    del self.quota_exceeded[api_name][month]

            if old_records:
                cleaned_apis.append(f"{api_name} ({len(old_records)} old records)")

            # Remove API if no records left
            if not self.quota_exceeded[api_name]:
                del self.quota_exceeded[api_name]

        if cleaned_apis:
            self._save_quota_exceeded()
            logger.info(f"🧹 Cleaned old quota records for: {', '.join(cleaned_apis)}")

    def get_status_summary(self) -> Dict[str, Any]:
        """Get comprehensive status summary"""
        current_month = datetime.now().strftime("%Y-%m")

        quota_exceeded_this_month = []
        for api_name, months in self.quota_exceeded.items():
            if current_month in months:
                quota_exceeded_this_month.append(api_name)

        return {
            "disabled_endpoints_count": len(self.disabled_endpoints),
            "quota_exceeded_apis": quota_exceeded_this_month,
            "quota_exceeded_count": len(quota_exceeded_this_month),
            "total_apis_affected": len(self.disabled_endpoints)
            + len(quota_exceeded_this_month),
            "last_updated": datetime.now().isoformat(),
        }
