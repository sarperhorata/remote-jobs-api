from fastapi import APIRouter, HTTPException, Depends
from typing import List
from database import get_db
from utils.auth import get_current_active_user
from datetime import datetime
from bson import ObjectId

router = APIRouter()

@router.post("/notifications/")
def create_notification(notification: dict):
    db = get_db()
    notifications = db["notifications"]
    notification["created_at"] = datetime.utcnow()
    result = notifications.insert_one(notification)
    created_notification = notifications.find_one({"_id": result.inserted_id})
    created_notification["_id"] = str(created_notification["_id"])
    return created_notification

@router.get("/notifications/", response_model=List[dict])
def get_notifications(
    skip: int = 0,
    limit: int = 100,
    current_user: dict = Depends(get_current_active_user)
):
    db = get_db()
    notifications = db["notifications"]
    user_notifications = list(notifications.find(
        {"user_id": current_user["_id"]}
    ).skip(skip).limit(limit))
    for notification in user_notifications:
        notification["_id"] = str(notification["_id"])
    return user_notifications

@router.get("/notifications/{notification_id}")
def get_notification(
    notification_id: str,
    current_user: dict = Depends(get_current_active_user)
):
    db = get_db()
    notifications = db["notifications"]
    notification = notifications.find_one({
        "_id": ObjectId(notification_id),
        "user_id": current_user["_id"]
    })
    if notification is None:
        raise HTTPException(status_code=404, detail="Notification not found")
    notification["_id"] = str(notification["_id"])
    return notification

@router.put("/notifications/{notification_id}")
def update_notification(
    notification_id: str,
    notification: dict,
    current_user: dict = Depends(get_current_active_user)
):
    db = get_db()
    notifications = db["notifications"]
    existing_notification = notifications.find_one({
        "_id": ObjectId(notification_id),
        "user_id": current_user["_id"]
    })
    if existing_notification is None:
        raise HTTPException(status_code=404, detail="Notification not found")
    
    update_data = {k: v for k, v in notification.items() if v is not None}
    update_data["updated_at"] = datetime.utcnow()
    
    notifications.update_one(
        {"_id": ObjectId(notification_id)},
        {"$set": update_data}
    )
    
    updated_notification = notifications.find_one({"_id": ObjectId(notification_id)})
    updated_notification["_id"] = str(updated_notification["_id"])
    return updated_notification

@router.delete("/notifications/{notification_id}")
def delete_notification(
    notification_id: str,
    current_user: dict = Depends(get_current_active_user)
):
    db = get_db()
    notifications = db["notifications"]
    result = notifications.delete_one({
        "_id": ObjectId(notification_id),
        "user_id": current_user["_id"]
    })
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Notification not found")
    return {"message": "Notification deleted successfully"}