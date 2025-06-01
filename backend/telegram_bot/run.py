#!/usr/bin/env python
import logging
import sys
import os
import signal

# Append the parent directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from telegram_bot.bot import RemoteJobsBot
from utils.config import logger

def signal_handler(signum, frame):
    """Handle termination signals"""
    logger.info(f"Received signal {signum}")
    sys.exit(0)

if __name__ == "__main__":
    # Register signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    logger.info("Starting Telegram bot")
    bot = RemoteJobsBot()
    
    try:
        bot.run()
    except KeyboardInterrupt:
        logger.info("Bot stopping due to keyboard interrupt")
    except Exception as e:
        logger.error(f"Error running bot: {str(e)}")
        raise
    finally:
        logger.info("Bot stopped") 