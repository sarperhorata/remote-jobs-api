import json
import logging
import os
from datetime import datetime
from typing import Any, Dict

from fastapi import APIRouter, BackgroundTasks, HTTPException, Request, status
from pydantic import BaseModel

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/webhooks", tags=["Webhooks"])


@router.post("/sentry")
async def sentry_webhook(
    request: Request, background_tasks: BackgroundTasks
) -> Dict[str, Any]:
    """
    Sentry webhook endpoint for receiving error notifications
    """
    try:
        # Get raw body
        body = await request.body()

        # Parse JSON
        try:
            data = json.loads(body.decode("utf-8"))
        except json.JSONDecodeError:
            logger.error("Invalid JSON in Sentry webhook")
            raise HTTPException(status_code=400, detail="Invalid JSON")

        # Process webhook in background
        background_tasks.add_task(process_sentry_webhook, data)

        return {"success": True, "message": "Webhook processed"}

    except Exception as e:
        logger.error(f"Error processing Sentry webhook: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


async def process_sentry_webhook(data: Dict[str, Any]):
    """Process Sentry webhook data and send to Telegram"""
    try:
        # Import telegram bot
        try:
            from telegram_bot.bot_manager import bot_manager

            bot = bot_manager.bot_instance

            if not bot or not bot.enabled:
                logger.warning("Telegram bot not available for Sentry notifications")
                return

        except ImportError:
            logger.error("Could not import Telegram bot for Sentry notifications")
            return

        # Extract event data
        event_data = extract_sentry_event_data(data)

        if not event_data:
            logger.warning("No valid event data in Sentry webhook")
            return

        # Check if event is critical enough to send notification
        if should_send_notification(event_data):
            await send_sentry_notification(bot, event_data)

    except Exception as e:
        logger.error(f"Error processing Sentry webhook: {str(e)}")


def extract_sentry_event_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """Extract relevant data from Sentry webhook"""
    try:
        # Handle different Sentry webhook formats
        if "data" in data and "event" in data["data"]:
            # Issue webhook format
            event = data["data"]["event"]
            issue = data["data"]["issue"]

            return {
                "type": "issue",
                "level": event.get("level", "unknown"),
                "title": issue.get("title", "Unknown error"),
                "message": event.get("message", ""),
                "culprit": event.get("culprit", ""),
                "environment": event.get("environment", "unknown"),
                "platform": event.get("platform", "unknown"),
                "url": issue.get("permalink", ""),
                "timestamp": event.get("timestamp", datetime.now().isoformat()),
                "user": event.get("user", {}),
                "tags": event.get("tags", {}),
                "fingerprint": event.get("fingerprint", []),
                "count": issue.get("count", 1),
                "first_seen": issue.get("first_seen", ""),
                "last_seen": issue.get("last_seen", ""),
                "status": issue.get("status", "unknown"),
            }

        elif "action" in data and "data" in data:
            # Action webhook format (issue state changes)
            action = data["action"]
            issue = data["data"]["issue"]

            return {
                "type": "action",
                "action": action,
                "level": "info",
                "title": issue.get("title", "Issue status changed"),
                "message": f"Issue {action}",
                "url": issue.get("permalink", ""),
                "timestamp": datetime.now().isoformat(),
                "count": issue.get("count", 1),
                "status": issue.get("status", "unknown"),
            }

        else:
            logger.warning(f"Unknown Sentry webhook format: {data.keys()}")
            return {}

    except Exception as e:
        logger.error(f"Error extracting Sentry event data: {str(e)}")
        return {}


def should_send_notification(event_data: Dict[str, Any]) -> bool:
    """Determine if the event is critical enough to send a notification"""

    # Always send for these levels
    critical_levels = ["fatal", "error"]
    if event_data.get("level") in critical_levels:
        return True

    # Send for high count errors
    if event_data.get("count", 0) > 10:
        return True

    # Send for production environment errors
    if event_data.get("environment") == "production" and event_data.get("level") in [
        "error",
        "warning",
    ]:
        return True

    # Send for specific action types
    if event_data.get("type") == "action" and event_data.get("action") in [
        "created",
        "reopened",
    ]:
        return True

    # Send for new issues
    if event_data.get("status") == "unresolved" and event_data.get(
        "first_seen"
    ) == event_data.get("last_seen"):
        return True

    return False


async def send_sentry_notification(bot, event_data: Dict[str, Any]):
    """Send Sentry notification to Telegram"""
    try:
        # Format notification message
        message = format_sentry_message(event_data)

        # Send to Telegram
        await bot.send_error_notification(message, event_data)

        logger.info(
            f"Sent Sentry notification to Telegram: {event_data.get('title', 'Unknown error')}"
        )

    except Exception as e:
        logger.error(f"Error sending Sentry notification to Telegram: {str(e)}")


def format_sentry_message(event_data: Dict[str, Any]) -> str:
    """Format Sentry event data into a readable message"""

    # Get level emoji
    level_emojis = {
        "fatal": "💀",
        "error": "🚨",
        "warning": "⚠️",
        "info": "ℹ️",
        "debug": "🐛",
    }

    level = event_data.get("level", "unknown")
    emoji = level_emojis.get(level, "🔍")

    # Format timestamp
    timestamp = event_data.get("timestamp", "")
    if timestamp:
        try:
            dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
            timestamp_str = dt.strftime("%Y-%m-%d %H:%M:%S UTC")
        except:
            timestamp_str = timestamp
    else:
        timestamp_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")

    # Build message
    if event_data.get("type") == "action":
        # Action notification
        action = event_data.get("action", "unknown")
        message = f"""
{emoji} **Sentry Issue {action.title()}**

**Title:** {event_data.get('title', 'Unknown')}
**Action:** {action}
**Status:** {event_data.get('status', 'unknown')}
**Count:** {event_data.get('count', 'unknown')}
**Time:** {timestamp_str}
"""
    else:
        # Error notification
        message = f"""
{emoji} **Sentry Alert - {level.upper()}**

**Error:** {event_data.get('title', 'Unknown error')}
**Environment:** {event_data.get('environment', 'unknown')}
**Platform:** {event_data.get('platform', 'unknown')}
**Count:** {event_data.get('count', 1)}
**Time:** {timestamp_str}
"""

        # Add message if available
        if event_data.get("message"):
            message += f"**Message:** {event_data.get('message')[:200]}...\n"

        # Add culprit if available
        if event_data.get("culprit"):
            message += f"**Culprit:** `{event_data.get('culprit')}`\n"

        # Add user info if available
        user = event_data.get("user", {})
        if user and user.get("email"):
            message += f"**User:** {user.get('email')}\n"

    # Add URL if available
    if event_data.get("url"):
        message += f"\n🔗 [View in Sentry]({event_data.get('url')})"

    return message.strip()


@router.get("/sentry/test")
async def test_sentry_webhook():
    """Test endpoint for Sentry webhook"""

    # Mock Sentry webhook data
    mock_data = {
        "data": {
            "event": {
                "level": "error",
                "message": "Test error from Buzz2Remote API",
                "culprit": "backend.routes.test",
                "environment": "development",
                "platform": "python",
                "timestamp": datetime.now().isoformat(),
                "user": {"email": "test@buzz2remote.com"},
                "tags": {"server_name": "buzz2remote-api"},
            },
            "issue": {
                "title": "Test Error: Something went wrong",
                "permalink": "https://sentry.io/organizations/buzz2remote/issues/12345/",
                "count": 5,
                "first_seen": datetime.now().isoformat(),
                "last_seen": datetime.now().isoformat(),
                "status": "unresolved",
            },
        }
    }

    # Process the mock webhook
    await process_sentry_webhook(mock_data)

    return {
        "success": True,
        "message": "Test Sentry webhook processed",
        "data": mock_data,
    }


import logging
import os
from typing import Dict, Any

from fastapi import APIRouter, HTTPException, Request, status
from pydantic import BaseModel

# Optional imports
try:
    from backend.services.notification_manager import NotificationManager
    NOTIFICATION_MANAGER_AVAILABLE = True
except ImportError:
    NOTIFICATION_MANAGER_AVAILABLE = False

try:
    from backend.telegram_bot.bot_manager import get_managed_bot
    TELEGRAM_BOT_AVAILABLE = True
except ImportError:
    TELEGRAM_BOT_AVAILABLE = False

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/webhook/sentry", tags=["Sentry Webhook"])

class SentryAlert(BaseModel):
    """Sentry alert payload model"""
    project_name: str
    project_slug: str
    url: str
    level: str
    message: str
    culprit: str
    event_id: str
    tags: Dict[str, str] = {}
    metadata: Dict[str, Any] = {}

@router.post("/alert")
async def sentry_alert_webhook(request: Request, alert: SentryAlert):
    """Handle Sentry alert webhooks"""
    
    # Verify webhook secret (optional but recommended)
    webhook_secret = os.getenv("SENTRY_WEBHOOK_SECRET")
    if webhook_secret:
        auth_header = request.headers.get("Authorization")
        if not auth_header or auth_header != f"Bearer {webhook_secret}":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid webhook secret"
            )
    
    try:
        # Log the alert
        logger.warning(f"Sentry Alert: {alert.level} - {alert.message}")
        
        # Only send notifications for critical errors to stay within free tier
        if alert.level in ["fatal", "error"]:
            await send_sentry_notification(alert)
        
        return {"status": "success", "message": "Alert processed"}
        
    except Exception as e:
        logger.error(f"Error processing Sentry alert: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error processing alert"
        )

async def send_sentry_notification(alert: SentryAlert):
    """Send Sentry alert notifications"""
    
    # Prepare notification message
    message = f"""
🚨 **Sentry Alert - {alert.project_name}**

**Level:** {alert.level.upper()}
**Message:** {alert.message}
**Culprit:** {alert.culprit}
**Event ID:** {alert.event_id}

**URL:** {alert.url}

**Tags:** {', '.join([f'{k}={v}' for k, v in alert.tags.items()])}
"""
    
    # Send to Telegram (if available)
    try:
        bot = get_managed_bot()
        if bot:
            chat_id = os.getenv("TELEGRAM_CHAT_ID")
            if chat_id:
                await bot.send_message(
                    chat_id=chat_id,
                    text=message,
                    parse_mode="Markdown"
                )
                logger.info(f"Sentry alert sent to Telegram: {alert.event_id}")
    except Exception as e:
        logger.error(f"Failed to send Sentry alert to Telegram: {e}")
    
    # Send to notification manager (if available)
    try:
        if NOTIFICATION_MANAGER_AVAILABLE:
            notification_manager = NotificationManager()
            await notification_manager.send_admin_notification(
                title=f"Sentry Alert: {alert.level.upper()}",
                message=alert.message,
                level=alert.level,
                metadata={
                    "event_id": alert.event_id,
                    "culprit": alert.culprit,
                    "url": alert.url,
                    "tags": alert.tags
                }
            )
            logger.info(f"Sentry alert sent to notification manager: {alert.event_id}")
    except Exception as e:
        logger.error(f"Failed to send Sentry alert to notification manager: {e}")

@router.get("/health")
async def sentry_webhook_health():
    """Health check for Sentry webhook"""
    return {
        "status": "healthy",
        "service": "sentry-webhook",
        "environment": os.getenv("ENVIRONMENT", "development")
    }
