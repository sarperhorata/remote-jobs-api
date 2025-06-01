from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorDatabase
from backend.database import get_async_db
from backend.schemas.notification import NotificationCreate, NotificationResponse, NotificationListResponse

router = APIRouter()

@router.post("/notifications", response_model=NotificationResponse)
async def create_notification(
    notification: NotificationCreate,
    db: AsyncIOMotorDatabase = Depends(get_async_db)
):
    """Create a new notification."""
    notification_dict = notification.dict()
    notification_dict["created_at"] = datetime.utcnow()
    notification_dict["is_read"] = False
    
    result = await db.notifications.insert_one(notification_dict)
    created_notification = await db.notifications.find_one({"_id": result.inserted_id})
    return created_notification

@router.get("/notifications", response_model=NotificationListResponse)
async def get_notifications(
    user_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    is_read: Optional[bool] = None,
    db: AsyncIOMotorDatabase = Depends(get_async_db)
):
    """Get a list of notifications for a user."""
    query = {"user_id": user_id}
    if is_read is not None:
        query["is_read"] = is_read
    
    # Get total count
    total = await db.notifications.count_documents(query)
    
    # Get notifications
    cursor = db.notifications.find(query).sort("created_at", -1).skip(skip).limit(limit)
    notifications = await cursor.to_list(length=limit)
    
    return {
        "items": notifications,
        "total": total,
        "page": skip // limit + 1,
        "per_page": limit,
        "total_pages": (total + limit - 1) // limit
    }

@router.get("/notifications/{notification_id}", response_model=NotificationResponse)
async def get_notification(
    notification_id: str,
    db: AsyncIOMotorDatabase = Depends(get_async_db)
):
    """Get a specific notification."""
    notification = await db.notifications.find_one({"_id": notification_id})
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    return notification

@router.put("/notifications/{notification_id}/read", response_model=NotificationResponse)
async def mark_notification_as_read(
    notification_id: str,
    db: AsyncIOMotorDatabase = Depends(get_async_db)
):
    """Mark a notification as read."""
    result = await db.notifications.update_one(
        {"_id": notification_id},
        {"$set": {"is_read": True, "read_at": datetime.utcnow()}}
    )
    
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Notification not found")
    
    updated_notification = await db.notifications.find_one({"_id": notification_id})
    return updated_notification

@router.delete("/notifications/{notification_id}", status_code=204)
async def delete_notification(
    notification_id: str,
    db: AsyncIOMotorDatabase = Depends(get_async_db)
):
    """Delete a notification."""
    result = await db.notifications.delete_one({"_id": notification_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Notification not found")

@router.put("/notifications/read-all", response_model=dict)
async def mark_all_notifications_as_read(
    user_id: str,
    db: AsyncIOMotorDatabase = Depends(get_async_db)
):
    """Mark all notifications as read for a user."""
    result = await db.notifications.update_many(
        {"user_id": user_id, "is_read": False},
        {"$set": {"is_read": True, "read_at": datetime.utcnow()}}
    )
    
    return {
        "message": "All notifications marked as read",
        "modified_count": result.modified_count
    }