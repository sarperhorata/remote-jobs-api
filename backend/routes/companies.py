from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from backend.models.company import Company
from backend.database import get_async_db
from bson import ObjectId
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorDatabase
from backend.schemas.company import CompanyCreate, CompanyUpdate, CompanyResponse, CompanyListResponse
from backend.utils.auth import get_current_active_user, get_current_user, get_current_admin

router = APIRouter(tags=["companies"])

@router.post("/companies/", response_model=CompanyResponse)
async def create_company(
    company: CompanyCreate,
    db: AsyncIOMotorDatabase = Depends(get_async_db)
):
    """Create a new company."""
    company_dict = company.dict()
    company_dict["created_at"] = datetime.utcnow()
    company_dict["updated_at"] = datetime.utcnow()
    company_dict["is_active"] = True
    
    result = await db.companies.insert_one(company_dict)
    created_company = await db.companies.find_one({"_id": result.inserted_id})
    return created_company

@router.get("/companies/", response_model=CompanyListResponse)
async def get_companies(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    is_active: Optional[bool] = None,
    search: Optional[str] = None,
    db: AsyncIOMotorDatabase = Depends(get_async_db)
):
    """Get a list of companies with optional filtering."""
    query = {}
    if is_active is not None:
        query["is_active"] = is_active
    if search:
        query["$or"] = [
            {"name": {"$regex": search, "$options": "i"}},
            {"description": {"$regex": search, "$options": "i"}}
        ]
    
    # Get total count
    total = await db.companies.count_documents(query)
    
    # Get companies
    cursor = db.companies.find(query).sort("created_at", -1).skip(skip).limit(limit)
    companies = await cursor.to_list(length=limit)
    
    # Convert ObjectIds to strings for JSON serialization
    for company in companies:
        if "_id" in company and isinstance(company["_id"], ObjectId):
            company["id"] = str(company["_id"])
            company["_id"] = str(company["_id"])
        # Add jobs_count if not present
        if "jobs_count" not in company:
            company["jobs_count"] = await db.jobs.count_documents({"company": company["name"]})
    
    return {
        "items": companies,
        "total": total,
        "page": skip // limit + 1,
        "per_page": limit,
        "total_pages": (total + limit - 1) // limit
    }

@router.get("/companies/{company_id}", response_model=CompanyResponse)
async def get_company(
    company_id: str,
    db: AsyncIOMotorDatabase = Depends(get_async_db)
):
    """Get a specific company."""
    # Try to convert to ObjectId if it's a valid ObjectId string
    if ObjectId.is_valid(company_id):
        query = {"_id": ObjectId(company_id)}
    else:
        query = {"_id": company_id}
        
    company = await db.companies.find_one(query)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    
    # Convert ObjectId to string for JSON serialization
    if "_id" in company and isinstance(company["_id"], ObjectId):
        company["id"] = str(company["_id"])
        company["_id"] = str(company["_id"])
    
    # Add jobs_count if not present
    if "jobs_count" not in company:
        company["jobs_count"] = await db.jobs.count_documents({"company": company["name"]})
        
    return company

@router.put("/companies/{company_id}", response_model=CompanyResponse)
async def update_company(
    company_id: str,
    company: CompanyUpdate,
    db: AsyncIOMotorDatabase = Depends(get_async_db)
):
    """Update a company."""
    update_data = company.dict(exclude_unset=True)
    update_data["updated_at"] = datetime.utcnow()
    
    # Try to convert to ObjectId if it's a valid ObjectId string
    if ObjectId.is_valid(company_id):
        query = {"_id": ObjectId(company_id)}
    else:
        query = {"_id": company_id}
    
    result = await db.companies.update_one(query, {"$set": update_data})
    
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Company not found")
    
    updated_company = await db.companies.find_one(query)
    
    # Convert ObjectId to string for JSON serialization
    if "_id" in updated_company and isinstance(updated_company["_id"], ObjectId):
        updated_company["id"] = str(updated_company["_id"])
        updated_company["_id"] = str(updated_company["_id"])
        
    return updated_company

@router.delete("/companies/{company_id}", status_code=204)
async def delete_company(
    company_id: str,
    db: AsyncIOMotorDatabase = Depends(get_async_db)
):
    """Delete a company."""
    # Try to convert to ObjectId if it's a valid ObjectId string
    if ObjectId.is_valid(company_id):
        query = {"_id": ObjectId(company_id)}
    else:
        query = {"_id": company_id}
        
    result = await db.companies.delete_one(query)
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Company not found")

@router.get("/companies/{company_id}/jobs", response_model=dict)
async def get_company_jobs(
    company_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    is_active: Optional[bool] = None,
    db: AsyncIOMotorDatabase = Depends(get_async_db)
):
    """Get jobs for a specific company."""
    # First get the company to ensure it exists
    company = await db.companies.find_one({"_id": company_id})
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
        
    query = {"company": company["name"]}  # Use company name for job lookup
    if is_active is not None:
        query["is_active"] = is_active
    
    # Get total count
    total = await db.jobs.count_documents(query)
    
    # Get jobs
    cursor = db.jobs.find(query).sort("created_at", -1).skip(skip).limit(limit)
    jobs = await cursor.to_list(length=limit)
    
    # Convert ObjectIds to strings
    for job in jobs:
        if "_id" in job and isinstance(job["_id"], ObjectId):
            job["id"] = str(job["_id"])
            job["_id"] = str(job["_id"])
            
    return {
        "jobs": jobs,
        "total": total,
        "page": skip // limit + 1,
        "per_page": limit,
        "total_pages": (total + limit - 1) // limit
    } 