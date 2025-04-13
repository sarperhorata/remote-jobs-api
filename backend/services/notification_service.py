from fastapi import Depends
from typing import Dict, Any
import logging
from datetime import datetime

from notification.notification_manager import NotificationManager
from telegram_bot.bot import RemoteJobsBot

logger = logging.getLogger(__name__)

class NotificationService:
    """
    Service for handling different types of notifications
    """
    
    def __init__(self):
        self.notification_manager = NotificationManager()
        self.telegram_bot = RemoteJobsBot()
    
    async def send_deployment_notification(self, deployment_info: Dict[str, Any]) -> bool:
        """
        Send deployment notification to subscribed users
        
        Args:
            deployment_info (dict): Dictionary containing deployment information
                - environment: str (e.g. 'production', 'staging')
                - status: str (e.g. 'success', 'failed')
                - commit: str (commit hash)
                - message: str (deployment message)
                - timestamp: str (ISO format timestamp)
        """
        logger.info(f"Sending deployment notification: {deployment_info}")
        
        try:
            # Validate the required fields
            required_fields = ['environment', 'status', 'commit', 'message', 'timestamp']
            for field in required_fields:
                if field not in deployment_info:
                    logger.error(f"Missing required field in deployment info: {field}")
                    return False
            
            # Send notification via Telegram bot
            telegram_result = await self.telegram_bot.send_deployment_notification(deployment_info)
            
            # Also try to send via notification manager for other channels
            try:
                await self.notification_manager.send_deployment_notification(deployment_info)
            except Exception as e:
                logger.error(f"Error using notification manager: {str(e)}")
            
            return telegram_result
            
        except Exception as e:
            logger.error(f"Failed to send deployment notification: {str(e)}")
            return False 