from fastapi import APIRouter, HTTPException, Query
from typing import Dict, Any
import sentry_sdk
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/sentry-test", tags=["Sentry Test"])

@router.post("/test-error")
async def test_sentry_error(
    error_type: str = Query("exception", description="Type of error to test: exception, http, logging")
) -> Dict[str, Any]:
    """
    Test Sentry error reporting
    """
    try:
        if error_type == "exception":
            # Test unhandled exception
            raise ValueError("Bu bir test hatasıdır - Sentry çalışıyor mu?")
        
        elif error_type == "http":
            # Test HTTP error
            raise HTTPException(
                status_code=500,
                detail="Test HTTP error for Sentry integration"
            )
        
        elif error_type == "logging":
            # Test logging error
            logger.error("Test error log for Sentry", extra={
                "test_data": {
                    "user_id": "test_user",
                    "action": "sentry_test",
                    "timestamp": "2024-12-21T12:00:00Z"
                }
            })
            
            return {
                "success": True,
                "message": "Error logged successfully - check Sentry dashboard"
            }
        
        else:
            return {
                "success": False,
                "error": "Invalid error type. Use: exception, http, logging"
            }
            
    except ValueError as e:
        # This should be caught by Sentry
        sentry_sdk.capture_exception(e)
        raise HTTPException(
            status_code=500,
            detail=f"Test exception caught and sent to Sentry: {str(e)}"
        )

@router.post("/test-message")
async def test_sentry_message(
    message: str = Query("Test message from Buzz2Remote API", description="Custom message to send to Sentry")
) -> Dict[str, Any]:
    """
    Test Sentry message capture
    """
    try:
        # Send custom message to Sentry
        sentry_sdk.capture_message(message, level="info")
        
        return {
            "success": True,
            "message": "Message sent to Sentry successfully",
            "sent_message": message
        }
        
    except Exception as e:
        logger.error(f"Error sending message to Sentry: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to send message to Sentry: {str(e)}"
        )

@router.get("/sentry-config")
async def get_sentry_config() -> Dict[str, Any]:
    """
    Get current Sentry configuration
    """
    try:
        hub = sentry_sdk.Hub.current
        client = hub.client
        
        if client:
            return {
                "success": True,
                "sentry_enabled": True,
                "dsn_configured": bool(client.dsn),
                "environment": client.options.get("environment"),
                "release": client.options.get("release"),
                "sample_rate": client.options.get("traces_sample_rate"),
                "integrations": [integration.__class__.__name__ for integration in client.integrations.values()]
            }
        else:
            return {
                "success": False,
                "sentry_enabled": False,
                "message": "Sentry client not initialized"
            }
            
    except Exception as e:
        logger.error(f"Error getting Sentry config: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        } 