from fastapi import APIRouter, HTTPException, Depends, UploadFile, File
from typing import List, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from backend.database import get_async_db
from backend.utils.auth import get_current_active_user
import os
import shutil
from datetime import datetime
from bson import ObjectId
from backend.schemas.profile import ProfileCreate, ProfileResponse

router = APIRouter()

UPLOAD_DIR = "uploads"

@router.post("/profiles/upload-photo")
async def upload_profile_photo(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_active_user)
):
    db = get_async_db()
    profiles = db["profiles"]
    if not os.path.exists(UPLOAD_DIR):
        os.makedirs(UPLOAD_DIR)
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as buffer:
        buffer.write(await file.read())
    profiles.update_one({"_id": ObjectId(current_user["_id"])}, {"$set": {"profile_photo_url": f"/uploads/{file.filename}"}})
    return {"message": "Profile photo uploaded successfully"}

@router.post("/profiles/")
def create_profile(profile: dict):
    db = get_async_db()
    profiles = db["profiles"]
    result = profiles.insert_one(profile)
    created_profile = profiles.find_one({"_id": result.inserted_id})
    created_profile["_id"] = str(created_profile["_id"])
    return created_profile

@router.get("/profiles/{profile_id}")
def get_profile(profile_id: str):
    db = get_async_db()
    profiles = db["profiles"]
    profile = profiles.find_one({"_id": ObjectId(profile_id)})
    if profile is None:
        raise HTTPException(status_code=404, detail="Profile not found")
    profile["_id"] = str(profile["_id"])
    return profile

@router.put("/profiles/{profile_id}")
def update_profile(profile_id: str, profile: dict):
    db = get_async_db()
    profiles = db["profiles"]
    existing_profile = profiles.find_one({"_id": ObjectId(profile_id)})
    if existing_profile is None:
        raise HTTPException(status_code=404, detail="Profile not found")
    update_data = {k: v for k, v in profile.items() if v is not None}
    profiles.update_one({"_id": ObjectId(profile_id)}, {"$set": update_data})
    updated_profile = profiles.find_one({"_id": ObjectId(profile_id)})
    updated_profile["_id"] = str(updated_profile["_id"])
    return updated_profile

@router.put("/profile")
async def update_profile(
    profile: dict,
    current_user: dict = Depends(get_current_active_user)
):
    db = get_async_db()
    profiles = db["profiles"]
    update_data = {k: v for k, v in profile.items() if k not in ["password", "password_confirm"]}
    update_data["updated_at"] = datetime.utcnow()
    profiles.update_one({"_id": ObjectId(current_user["_id"])}, {"$set": update_data})
    return {"message": "Profile updated successfully"}

@router.post("/profile/photo")
async def upload_profile_photo(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_active_user)
):
    db = get_async_db()
    profiles = db["profiles"]
    if not os.path.exists(UPLOAD_DIR):
        os.makedirs(UPLOAD_DIR)
    file_location = f"{UPLOAD_DIR}/{current_user['_id']}_{file.filename}"
    with open(file_location, "wb+") as file_object:
        shutil.copyfileobj(file.file, file_object)
    profiles.update_one({"_id": ObjectId(current_user["_id"])}, {"$set": {"profile_photo_url": file_location, "updated_at": datetime.utcnow()}})
    return {"message": "Profile photo uploaded successfully"} 