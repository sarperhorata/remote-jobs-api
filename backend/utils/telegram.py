import logging
import os
from typing import Optional

import httpx

logger = logging.getLogger(__name__)


class TelegramNotifier:
    def __init__(self):
        self.bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
        self.chat_id = os.getenv("TELEGRAM_CHAT_ID")
        self.channel = os.getenv("TELEGRAM_CHANNEL", "@buzz2remote")
        self.base_url = f"https://api.telegram.org/bot{self.bot_token}"

    async def send_message(
        self, message: str, parse_mode: Optional[str] = "HTML"
    ) -> bool:
        """Send a message to the configured Telegram chat/channel."""
        if not self.bot_token:
            logger.error("Telegram bot token not configured")
            return False

        # Use channel username if chat_id is not properly set
        target_chat = self.chat_id
        if not target_chat or target_chat == "455797523":  # Old personal chat ID
            target_chat = self.channel
            logger.info(f"Using channel username: {target_chat}")

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/sendMessage",
                    json={
                        "chat_id": target_chat,
                        "text": message,
                        "parse_mode": parse_mode,
                    },
                )
                response.raise_for_status()

                result = response.json()
                if result.get("ok"):
                    logger.info(f"Message sent successfully to {target_chat}")
                    return True
                else:
                    logger.error(f"Telegram API error: {result.get('description')}")
                    return False

        except Exception as e:
            logger.error(f"Failed to send Telegram message: {str(e)}")
            logger.error(
                f"Target chat: {target_chat}, Bot token: {self.bot_token[:20]}..."
            )
            return False

    async def send_deployment_status(
        self, platform: str, status: str, details: str
    ) -> bool:
        """Send deployment status notification."""
        status_emoji = "✅" if status.lower() in ["success", "successful"] else "❌"

        message = (
            f"{status_emoji} <b>Buzz2Remote Deployment</b>\n\n"
            f"<b>Platform:</b> {platform}\n"
            f"<b>Status:</b> {status}\n"
            f"<b>Details:</b> {details}\n"
            f"<b>Time:</b> {self._get_current_time()}"
        )
        return await self.send_message(message)

    async def send_error_notification(
        self, error_type: str, error_message: str, component: str = "System"
    ) -> bool:
        """Send error notification."""
        message = (
            f"🚨 <b>Buzz2Remote Error Alert</b>\n\n"
            f"<b>Component:</b> {component}\n"
            f"<b>Type:</b> {error_type}\n"
            f"<b>Message:</b> {error_message}\n"
            f"<b>Time:</b> {self._get_current_time()}"
        )
        return await self.send_message(message)

    async def send_crawler_status(
        self, total_jobs: int, new_jobs: int, updated_jobs: int, errors: int = 0
    ) -> bool:
        """Send crawler status notification."""
        status_emoji = "✅" if errors == 0 else "⚠️"

        message = (
            f"{status_emoji} <b>Daily Crawler Report</b>\n\n"
            f"<b>Total Jobs:</b> {total_jobs:,}\n"
            f"<b>New Jobs:</b> {new_jobs:,}\n"
            f"<b>Updated Jobs:</b> {updated_jobs:,}\n"
            f"<b>Errors:</b> {errors}\n"
            f"<b>Time:</b> {self._get_current_time()}"
        )
        return await self.send_message(message)

    def _get_current_time(self) -> str:
        """Get current time in readable format."""
        from datetime import datetime

        return datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")

    async def test_connection(self) -> bool:
        """Test Telegram connection."""
        test_message = f"🧪 Test message from Buzz2Remote\n\nConnection test at {self._get_current_time()}"
        return await self.send_message(test_message)


telegram = TelegramNotifier()
