import os
import logging
import httpx
from typing import Optional

logger = logging.getLogger(__name__)

class TelegramNotifier:
    def __init__(self):
        self.bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        self.chat_id = os.getenv('TELEGRAM_CHAT_ID')
        self.base_url = f"https://api.telegram.org/bot{self.bot_token}"

    async def send_message(self, message: str, parse_mode: Optional[str] = "HTML") -> bool:
        """Send a message to the configured Telegram chat."""
        if not self.bot_token or not self.chat_id:
            logger.error("Telegram bot token or chat ID not configured")
            return False

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/sendMessage",
                    json={
                        "chat_id": self.chat_id,
                        "text": message,
                        "parse_mode": parse_mode
                    }
                )
                response.raise_for_status()
                return True
        except Exception as e:
            logger.error(f"Failed to send Telegram message: {str(e)}")
            return False

    async def send_deployment_status(self, platform: str, status: str, details: str) -> bool:
        """Send deployment status notification."""
        message = (
            f"🚀 <b>Deployment Update</b>\n\n"
            f"Platform: {platform}\n"
            f"Status: {status}\n"
            f"Details: {details}"
        )
        return await self.send_message(message)

telegram = TelegramNotifier() 