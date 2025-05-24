from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any
from notification.notification_manager import NotificationManager
from telegram_bot.bot import RemoteJobsBot

router = APIRouter()
notification_manager = NotificationManager()
telegram_bot = RemoteJobsBot()

@router.post("/deployment")
async def send_deployment_notification(deployment_info: Dict[str, Any]):
    """
    Send a notification about a deployment
    
    deployment_info should contain:
    - environment: str (e.g., 'production', 'staging')
    - status: str (e.g., 'success', 'failed')
    - commit: str (commit hash)
    - message: str (deployment message)
    - timestamp: datetime (when the deployment occurred)
    """
    try:
        # Notifikasyon sisteminden bildirim gönder
        result = await notification_manager.send_notification(
            notification_type="deployment",
            data=deployment_info
        )
        
        # Telegram botundan da bildirim gönder (başarılı olsa da olmasa da)
        try:
            await telegram_bot.send_deployment_notification(deployment_info)
        except Exception as e:
            print(f"Telegram bildirimi gönderilirken hata oluştu: {str(e)}")
        
        return {"message": "Deployment notification sent successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send deployment notification: {str(e)}")