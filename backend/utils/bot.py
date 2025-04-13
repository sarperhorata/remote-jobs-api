import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get TELEGRAM_BOT_TOKEN from environment variable
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_ENABLED = TELEGRAM_BOT_TOKEN is not None

# Log warning if token is missing but don't crash
if not TELEGRAM_ENABLED:
    logger.warning("TELEGRAM_BOT_TOKEN environment variable is not set. Telegram bot features will be disabled.")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a message when the command /start is issued."""
    await update.message.reply_text('Hi! I am your Remote Jobs bot. Use /help to see available commands.')

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a message when the command /help is issued."""
    help_text = """
Available commands:
/start - Start the bot
/help - Show this help message
/jobs - List latest job postings
    """
    await update.message.reply_text(help_text)

def setup_bot():
    """Set up and start the bot."""
    # Skip if Telegram bot is disabled
    if not TELEGRAM_ENABLED:
        logger.info("Telegram bot is disabled. Skipping setup.")
        return None
        
    try:
        application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
        
        # Add command handlers
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("help", help_command))
        
        # Start the bot (non-blocking)
        # Use run_polling(close_loop=False) to run in background
        application.run_polling(close_loop=False)
        return application
    except Exception as e:
        logger.error(f"Error setting up bot: {str(e)}")
        return None 