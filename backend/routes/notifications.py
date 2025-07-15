from fastapi import APIRouter, HTTPException, Depends, Query, status
from fastapi.responses import StreamingResponse
from typing import List, Optional
from datetime import datetime
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase
import asyncio
import json

from backend.database import get_async_db
from backend.utils.auth import get_current_user
from backend.models.models import UserNotification, UserNotificationCreate, UserNotificationUpdate
import logging

router = APIRouter(prefix="/notifications", tags=["notifications"])
logger = logging.getLogger(__name__)

# Store active SSE connections
active_connections: dict = {}

@router.get("/stream")
async def notification_stream(
    token: str = Query(..., description="Authentication token"),
    db: AsyncIOMotorDatabase = Depends(get_async_db)
):
    """
    Server-Sent Events endpoint for real-time notifications
    """
    try:
        # Verify token and get user (simplified version)
        from backend.utils.auth import verify_token
        try:
            payload = verify_token(token)
            user_id = payload.get("sub")
            if not user_id:
                raise HTTPException(status_code=401, detail="Invalid token")
        except Exception:
            raise HTTPException(status_code=401, detail="Invalid token")

        async def event_generator():
            connection_id = f"{user_id}_{datetime.utcnow().timestamp()}"
            active_connections[connection_id] = True
            
            try:
                # Send initial unread count
                initial_count = await get_unread_count_for_user(user_id, db)
                yield f"data: {json.dumps({'type': 'unread_count', 'count': initial_count})}\n\n"

                # Keep connection alive and listen for updates
                while active_connections.get(connection_id, False):
                    await asyncio.sleep(5)  # Send keepalive every 5 seconds
                    yield f"data: {json.dumps({'type': 'keepalive', 'timestamp': datetime.utcnow().isoformat()})}\n\n"
                    
            except asyncio.CancelledError:
                logger.info(f"SSE connection cancelled for user {user_id}")
            except Exception as e:
                logger.error(f"SSE error for user {user_id}: {str(e)}")
            finally:
                # Clean up connection
                if connection_id in active_connections:
                    del active_connections[connection_id]

        return StreamingResponse(
            event_generator(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "Cache-Control"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error starting notification stream: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to start notification stream"
        )

async def get_unread_count_for_user(user_id: str, db: AsyncIOMotorDatabase) -> int:
    """Helper function to get unread count for a user"""
    try:
        notifications_col = db["user_notifications"]
        count = await notifications_col.count_documents({
            "user_id": user_id,
            "is_read": False,
            "is_active": True
        })
        return count
    except Exception as e:
        logger.error(f"Error getting unread count for user {user_id}: {str(e)}")
        return 0

async def notify_user_count_change(user_id: str, new_count: int):
    """Notify a specific user about unread count change"""
    message = json.dumps({
        'type': 'unread_count', 
        'count': new_count,
        'timestamp': datetime.utcnow().isoformat()
    })
    
    # Send to all active connections for this user
    connections_to_remove = []
    for connection_id in list(active_connections.keys()):
        if connection_id.startswith(f"{user_id}_"):
            try:
                # In a real implementation, you'd have a way to send to specific connections
                # For now, we'll just log it
                logger.info(f"Would send count update to {connection_id}: {message}")
            except Exception as e:
                logger.error(f"Failed to send to connection {connection_id}: {str(e)}")
                connections_to_remove.append(connection_id)
    
    # Clean up failed connections
    for connection_id in connections_to_remove:
        if connection_id in active_connections:
            del active_connections[connection_id]

@router.get("/", response_model=List[UserNotification])
async def get_user_notifications(
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_async_db),
    is_read: Optional[bool] = Query(None, description="Filter by read status"),
    category: Optional[str] = Query(None, description="Filter by category"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    """
    Get user notifications with optional filters and pagination
    """
    try:
        user_id = str(current_user["_id"])
        
        # Build filter
        filter_query = {"user_id": user_id, "is_active": True}
        
        if is_read is not None:
            filter_query["is_read"] = is_read
            
        if category:
            filter_query["category"] = category
        
        # Get notifications
        notifications_col = db["user_notifications"]
        cursor = notifications_col.find(filter_query).sort("created_at", -1).skip(offset).limit(limit)
        notifications = await cursor.to_list(length=limit)
        
        # Convert ObjectId to string
        for notification in notifications:
            if "_id" in notification:
                notification["_id"] = str(notification["_id"])
        
        return notifications
        
    except Exception as e:
        logger.error(f"Error getting user notifications: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get notifications"
        )

@router.get("/unread-count")
async def get_unread_count(
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_async_db)
):
    """
    Get count of unread notifications
    """
    try:
        user_id = str(current_user["_id"])
        count = await get_unread_count_for_user(user_id, db)
        return {"unread_count": count}
        
    except Exception as e:
        logger.error(f"Error getting unread count: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get unread count"
        )

@router.post("/", response_model=UserNotification)
async def create_notification(
    notification: UserNotificationCreate,
    db: AsyncIOMotorDatabase = Depends(get_async_db)
):
    """
    Create a new notification
    """
    try:
        notifications_col = db["user_notifications"]
        
        notification_dict = notification.model_dump()
        notification_dict["created_at"] = datetime.utcnow()
        
        result = await notifications_col.insert_one(notification_dict)
        
        # Get the created notification
        created_notification = await notifications_col.find_one({"_id": result.inserted_id})
        created_notification["_id"] = str(created_notification["_id"])
        
        # Notify user about new notification via SSE
        user_id = notification_dict["user_id"]
        new_count = await get_unread_count_for_user(user_id, db)
        await notify_user_count_change(user_id, new_count)
        
        return created_notification
        
    except Exception as e:
        logger.error(f"Error creating notification: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create notification"
        )

@router.put("/{notification_id}/read")
async def mark_as_read(
    notification_id: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_async_db)
):
    """
    Mark a notification as read
    """
    try:
        user_id = str(current_user["_id"])
        notifications_col = db["user_notifications"]
        
        # Verify notification belongs to user
        notification = await notifications_col.find_one({
            "_id": ObjectId(notification_id),
            "user_id": user_id
        })
        
        if not notification:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Notification not found"
            )
        
        # Update notification
        await notifications_col.update_one(
            {"_id": ObjectId(notification_id)},
            {
                "$set": {
                    "is_read": True,
                    "read_at": datetime.utcnow()
                }
            }
        )
        
        # Update unread count via SSE
        new_count = await get_unread_count_for_user(user_id, db)
        await notify_user_count_change(user_id, new_count)
        
        return {"message": "Notification marked as read"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error marking notification as read: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to mark notification as read"
        )

@router.put("/mark-all-read")
async def mark_all_as_read(
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_async_db)
):
    """
    Mark all user notifications as read
    """
    try:
        user_id = str(current_user["_id"])
        notifications_col = db["user_notifications"]
        
        result = await notifications_col.update_many(
            {
                "user_id": user_id,
                "is_read": False,
                "is_active": True
            },
            {
                "$set": {
                    "is_read": True,
                    "read_at": datetime.utcnow()
                }
            }
        )
        
        # Update unread count via SSE (should be 0 now)
        await notify_user_count_change(user_id, 0)
        
        return {
            "message": f"Marked {result.modified_count} notifications as read",
            "modified_count": result.modified_count
        }
        
    except Exception as e:
        logger.error(f"Error marking all notifications as read: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to mark notifications as read"
        )

@router.delete("/{notification_id}")
async def delete_notification(
    notification_id: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_async_db)
):
    """
    Delete a notification (soft delete by setting is_active to False)
    """
    try:
        user_id = str(current_user["_id"])
        notifications_col = db["user_notifications"]
        
        # Verify notification belongs to user
        notification = await notifications_col.find_one({
            "_id": ObjectId(notification_id),
            "user_id": user_id
        })
        
        if not notification:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Notification not found"
            )
        
        # Soft delete
        await notifications_col.update_one(
            {"_id": ObjectId(notification_id)},
            {"$set": {"is_active": False}}
        )
        
        # Update unread count via SSE
        new_count = await get_unread_count_for_user(user_id, db)
        await notify_user_count_change(user_id, new_count)
        
        return {"message": "Notification deleted"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting notification: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete notification"
        )

@router.delete("/clear-all")
async def clear_all_notifications(
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_async_db)
):
    """
    Clear all user notifications (soft delete)
    """
    try:
        user_id = str(current_user["_id"])
        notifications_col = db["user_notifications"]
        
        result = await notifications_col.update_many(
            {
                "user_id": user_id,
                "is_active": True
            },
            {"$set": {"is_active": False}}
        )
        
        # Update unread count via SSE (should be 0 now)
        await notify_user_count_change(user_id, 0)
        
        return {
            "message": f"Cleared {result.modified_count} notifications",
            "cleared_count": result.modified_count
        }
        
    except Exception as e:
        logger.error(f"Error clearing all notifications: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to clear notifications"
        )

@router.post("/test/create")
async def create_test_notification(
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_async_db)
):
    """
    Create a test notification for the current user
    """
    try:
        user_id = str(current_user["_id"])
        notifications_col = db["user_notifications"]
        
        # Create test notification
        test_notification = {
            "user_id": user_id,
            "title": "Test Notification",
            "message": "This is a test notification to verify the notification system is working properly.",
            "notification_type": "info",
            "category": "system",
            "is_read": False,
            "is_active": True,
            "action_url": "https://buzz2remote.com",
            "action_text": "Visit Website",
            "created_at": datetime.utcnow()
        }
        
        result = await notifications_col.insert_one(test_notification)
        
        # Get the created notification
        created_notification = await notifications_col.find_one({"_id": result.inserted_id})
        created_notification["_id"] = str(created_notification["_id"])
        
        # Notify user about new notification via SSE
        new_count = await get_unread_count_for_user(user_id, db)
        await notify_user_count_change(user_id, new_count)
        
        return {
            "message": "Test notification created successfully",
            "notification": created_notification
        }
        
    except Exception as e:
        logger.error(f"Error creating test notification: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create test notification"
        ) 