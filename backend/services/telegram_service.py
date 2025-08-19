import logging
import os

import psutil
from telegram import Bot
from telegram.ext import CommandHandler, Updater
from telegram.error import TelegramError

logger = logging.getLogger(__name__)


class TelegramService:
    _instance = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(TelegramService, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if not self._initialized:
            self.bot = None
            self.updater = None
            self.enabled = False
            self._initialized = True

            # Check for existing instances
            current_process = psutil.Process()
            for proc in psutil.process_iter(["pid", "name", "cmdline"]):
                try:
                    if (
                        proc.info["name"] == "python"
                        and "telegram_service.py" in " ".join(proc.info["cmdline"])
                        and proc.pid != current_process.pid
                    ):
                        logger.warning(
                            f"Found existing telegram service instance with PID {proc.pid}"
                        )
                        proc.terminate()
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass

    async def start(self):
        """Start the telegram service"""
        if self.enabled:
            logger.warning("Telegram service is already running")
            return

        try:
            token = os.getenv("TELEGRAM_BOT_TOKEN")
            if not token:
                logger.warning("TELEGRAM_BOT_TOKEN not found in environment variables")
                return

            self.bot = Bot(token=token)
            self.updater = Updater(bot=self.bot)

            # Add handlers
            self.updater.dispatcher.add_handler(
                CommandHandler("start", self._start_command)
            )
            self.updater.dispatcher.add_handler(
                CommandHandler("help", self._help_command)
            )

            # Start polling
            self.updater.start_polling()
            self.enabled = True
            logger.info("Telegram service started successfully")

        except Exception as e:
            logger.error(f"Failed to start telegram service: {str(e)}")
            raise e

    async def stop(self):
        """Stop the telegram service"""
        if not self.enabled:
            logger.warning("Telegram service is not running")
            return

        try:
            if self.updater:
                self.updater.stop()
            self.enabled = False
            logger.info("Telegram service stopped")
        except Exception as e:
            logger.error(f"Error stopping telegram service: {str(e)}")
            raise e

    async def send_message(self, message: str):
        """Send message to Telegram chat (DISABLED - only logs)"""
        # Log the message instead of sending to Telegram
        logger.info(f"TELEGRAM NOTIFICATION (DISABLED): {message}")
        return
        
        # Original code commented out to disable Telegram notifications
        # try:
        #     if not self.bot:
        #         token = os.getenv("TELEGRAM_BOT_TOKEN")
        #         if not token:
        #         logger.warning("TELEGRAM_BOT_TOKEN not found")
        #         return
        #         self.bot = Bot(token=token)

        #     chat_id = os.getenv("TELEGRAM_CHAT_ID")
        #     if not chat_id:
        #         logger.warning("TELEGRAM_CHAT_ID not found")
        #         return

        #     await self.bot.send_message(chat_id=chat_id, text=message)
        #     logger.info(f"Telegram message sent: {message[:50]}...")
            
        # except Exception as e:
        #     logger.error(f"Failed to send Telegram message: {str(e)}")

    def _start_command(self, update, context):
        """Handle /start command"""
        update.message.reply_text("Hello! I'm the Buzz2Remote bot.")

    def _help_command(self, update, context):
        """Handle /help command"""
        help_text = """
Available commands:
/start - Start the bot
/help - Show this help message
        """
        update.message.reply_text(help_text)
