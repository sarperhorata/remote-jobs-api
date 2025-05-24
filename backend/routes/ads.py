from fastapi import APIRouter, HTTPException, Depends
from typing import List
from database import get_db
from utils.auth import get_current_active_user
from datetime import datetime
from bson import ObjectId

router = APIRouter()

@router.post("/ads/")
def create_ad(ad: dict):
    db = get_db()
    ads = db["ads"]
    ad["created_at"] = datetime.utcnow()
    result = ads.insert_one(ad)
    created_ad = ads.find_one({"_id": result.inserted_id})
    created_ad["_id"] = str(created_ad["_id"])
    return created_ad

@router.get("/ads/", response_model=List[dict])
def get_ads(
    skip: int = 0,
    limit: int = 100,
    current_user: dict = Depends(get_current_active_user)
):
    db = get_db()
    ads = db["ads"]
    user_ads = list(ads.find(
        {"user_id": current_user["_id"]}
    ).skip(skip).limit(limit))
    for ad in user_ads:
        ad["_id"] = str(ad["_id"])
    return user_ads

@router.get("/ads/{ad_id}")
def get_ad(
    ad_id: str,
    current_user: dict = Depends(get_current_active_user)
):
    db = get_db()
    ads = db["ads"]
    ad = ads.find_one({
        "_id": ObjectId(ad_id),
        "user_id": current_user["_id"]
    })
    if ad is None:
        raise HTTPException(status_code=404, detail="Ad not found")
    ad["_id"] = str(ad["_id"])
    return ad

@router.put("/ads/{ad_id}")
def update_ad(
    ad_id: str,
    ad: dict,
    current_user: dict = Depends(get_current_active_user)
):
    db = get_db()
    ads = db["ads"]
    existing_ad = ads.find_one({
        "_id": ObjectId(ad_id),
        "user_id": current_user["_id"]
    })
    if existing_ad is None:
        raise HTTPException(status_code=404, detail="Ad not found")
    
    update_data = {k: v for k, v in ad.items() if v is not None}
    update_data["updated_at"] = datetime.utcnow()
    
    ads.update_one(
        {"_id": ObjectId(ad_id)},
        {"$set": update_data}
    )
    
    updated_ad = ads.find_one({"_id": ObjectId(ad_id)})
    updated_ad["_id"] = str(updated_ad["_id"])
    return updated_ad

@router.delete("/ads/{ad_id}")
def delete_ad(
    ad_id: str,
    current_user: dict = Depends(get_current_active_user)
):
    db = get_db()
    ads = db["ads"]
    result = ads.delete_one({
        "_id": ObjectId(ad_id),
        "user_id": current_user["_id"]
    })
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Ad not found")
    return {"message": "Ad deleted successfully"} 