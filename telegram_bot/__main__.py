#!/usr/bin/env python
"""
Main entry point for the Telegram bot.
Run with `python -m telegram_bot` from the backend directory.
"""
import logging
import sys
import os

# Append the parent directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from telegram_bot.bot import RemoteJobsBot
from utils.config import logger

if __name__ == "__main__":
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