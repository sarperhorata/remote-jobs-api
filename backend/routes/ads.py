from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorDatabase
from backend.database import get_async_db
from backend.schemas.ad import AdCreate, AdUpdate, AdResponse, AdListResponse

router = APIRouter()

@router.post("/ads", response_model=AdResponse)
async def create_ad(
    ad: AdCreate,
    db: AsyncIOMotorDatabase = Depends(get_async_db)
):
    """Create a new advertisement."""
    ad_dict = ad.dict()
    ad_dict["created_at"] = datetime.utcnow()
    ad_dict["updated_at"] = datetime.utcnow()
    ad_dict["is_active"] = True
    ad_dict["views_count"] = 0
    ad_dict["clicks_count"] = 0
    
    result = await db.ads.insert_one(ad_dict)
    created_ad = await db.ads.find_one({"_id": result.inserted_id})
    return created_ad

@router.get("/ads", response_model=AdListResponse)
async def get_ads(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    is_active: Optional[bool] = None,
    db: AsyncIOMotorDatabase = Depends(get_async_db)
):
    """Get a list of advertisements with optional filtering."""
    query = {}
    if is_active is not None:
        query["is_active"] = is_active
    
    # Get total count
    total = await db.ads.count_documents(query)
    
    # Get ads
    cursor = db.ads.find(query).sort("created_at", -1).skip(skip).limit(limit)
    ads = await cursor.to_list(length=limit)
    
    return {
        "items": ads,
        "total": total,
        "page": skip // limit + 1,
        "per_page": limit,
        "total_pages": (total + limit - 1) // limit
    }

@router.get("/ads/{ad_id}", response_model=AdResponse)
async def get_ad(
    ad_id: str,
    db: AsyncIOMotorDatabase = Depends(get_async_db)
):
    """Get a specific advertisement."""
    ad = await db.ads.find_one({"_id": ad_id})
    if not ad:
        raise HTTPException(status_code=404, detail="Advertisement not found")
    return ad

@router.put("/ads/{ad_id}", response_model=AdResponse)
async def update_ad(
    ad_id: str,
    ad: AdUpdate,
    db: AsyncIOMotorDatabase = Depends(get_async_db)
):
    """Update an advertisement."""
    update_data = ad.dict(exclude_unset=True)
    update_data["updated_at"] = datetime.utcnow()
    
    result = await db.ads.update_one(
        {"_id": ad_id},
        {"$set": update_data}
    )
    
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Advertisement not found")
    
    updated_ad = await db.ads.find_one({"_id": ad_id})
    return updated_ad

@router.delete("/ads/{ad_id}", status_code=204)
async def delete_ad(
    ad_id: str,
    db: AsyncIOMotorDatabase = Depends(get_async_db)
):
    """Delete an advertisement."""
    result = await db.ads.delete_one({"_id": ad_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Advertisement not found")

@router.post("/ads/{ad_id}/view")
async def record_ad_view(
    ad_id: str,
    db: AsyncIOMotorDatabase = Depends(get_async_db)
):
    """Record a view for an advertisement."""
    result = await db.ads.update_one(
        {"_id": ad_id},
        {"$inc": {"views_count": 1}}
    )
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Advertisement not found")
    return {"message": "View recorded successfully"}

@router.post("/ads/{ad_id}/click")
async def record_ad_click(
    ad_id: str,
    db: AsyncIOMotorDatabase = Depends(get_async_db)
):
    """Record a click for an advertisement."""
    result = await db.ads.update_one(
        {"_id": ad_id},
        {"$inc": {"clicks_count": 1}}
    )
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Advertisement not found")
    return {"message": "Click recorded successfully"} 