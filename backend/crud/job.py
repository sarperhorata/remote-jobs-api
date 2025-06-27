from typing import List, Optional, Dict, Any
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from backend.schemas.job import JobCreate, JobUpdate, JobResponse

async def create_job(db: AsyncIOMotorDatabase, job: JobCreate) -> str:
    """Create a new job in the database."""
    job_dict = job.dict()
    job_dict["created_at"] = datetime.utcnow()
    job_dict["updated_at"] = datetime.utcnow()
    job_dict["is_active"] = True
    job_dict["views_count"] = 0
    job_dict["applications_count"] = 0
    
    result = await db.jobs.insert_one(job_dict)
    return str(result.inserted_id)

async def get_job(db: AsyncIOMotorDatabase, job_id: str) -> Optional[JobResponse]:
    """Get a job by its ID."""
    if not ObjectId.is_valid(job_id):
        return None
        
    job = await db.jobs.find_one({"_id": ObjectId(job_id)})
    if job:
        job["_id"] = str(job["_id"])
        return JobResponse(**job)
    return None

async def get_jobs(
    db: AsyncIOMotorDatabase,
    skip: int = 0,
    limit: int = 10,
    company: Optional[str] = None,
    location: Optional[str] = None,
    sort_by: Optional[str] = None,
    sort_order: int = -1
) -> List[JobResponse]:
    """Get a list of jobs with optional filtering and sorting."""
    query = {}
    if company:
        query["company"] = company
    if location:
        query["location"] = location
        
    sort = {}
    if sort_by:
        sort[sort_by] = sort_order
        
    cursor = db.jobs.find(query).skip(skip).limit(limit)
    if sort:
        cursor = cursor.sort(list(sort.items()))
        
    jobs = await cursor.to_list(length=limit)
    return [JobResponse(**{**job, "_id": str(job["_id"])}) for job in jobs]

async def update_job(
    db: AsyncIOMotorDatabase,
    job_id: str,
    job: JobUpdate
) -> Optional[JobResponse]:
    """Update a job."""
    if not ObjectId.is_valid(job_id):
        return None
        
    update_data = job.dict(exclude_unset=True)
    update_data["updated_at"] = datetime.utcnow()
    
    result = await db.jobs.update_one(
        {"_id": ObjectId(job_id)},
        {"$set": update_data}
    )
    
    if result.modified_count:
        return await get_job(db, job_id)
    return None

async def delete_job(db: AsyncIOMotorDatabase, job_id: str) -> bool:
    """Delete a job."""
    if not ObjectId.is_valid(job_id):
        return False
        
    result = await db.jobs.delete_one({"_id": ObjectId(job_id)})
    return result.deleted_count > 0

async def search_jobs(
    db: AsyncIOMotorDatabase,
    query: str,
    skip: int = 0,
    limit: int = 10
) -> List[JobResponse]:
    """Search jobs by title or description."""
    search_filter = {
        "$or": [
            {"title": {"$regex": query, "$options": "i"}},
            {"description": {"$regex": query, "$options": "i"}}
        ]
    }
    
    cursor = db.jobs.find(search_filter).skip(skip).limit(limit)
    jobs = await cursor.to_list(length=limit)
    return [JobResponse(**{**job, "_id": str(job["_id"])}) for job in jobs]

async def get_job_statistics(db: AsyncIOMotorDatabase) -> Dict[str, Any]:
    """Get statistics about jobs."""
    total_jobs = await db.jobs.count_documents({})
    companies = await db.jobs.distinct("company")
    locations = await db.jobs.distinct("location")
    
    return {
        "total_jobs": total_jobs,
        "companies": companies,
        "locations": locations
    } 