from typing import List, Optional, Dict, Any
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from backend.schemas.job import JobCreate, JobUpdate, JobResponse
from backend.services.job_deduplication_service import deduplication_service

class JobCRUD:
    """CRUD operations for jobs"""
    
    @staticmethod
    async def create_job(db: AsyncIOMotorDatabase, job: JobCreate) -> str:
        """Create a new job in the database with deduplication check."""
        job_dict = job.dict()
        job_dict["created_at"] = datetime.utcnow()
        job_dict["updated_at"] = datetime.utcnow()
        job_dict["is_active"] = True
        job_dict["views_count"] = 0
        job_dict["applications_count"] = 0
        
        # Use deduplication service to save job
        job_id, dedup_result = await deduplication_service.save_job_with_deduplication(job_dict)
        
        if dedup_result.is_duplicate:
            # Log duplicate detection
            from backend.utils.logger import logger
            logger.info(f"Duplicate job detected: {dedup_result.duplicate_reason} (confidence: {dedup_result.confidence_level})")
        
        return job_id

    @staticmethod
    async def create_job_batch(db: AsyncIOMotorDatabase, jobs: List[JobCreate]) -> Dict[str, Any]:
        """Create multiple jobs with deduplication check."""
        results = {
            "total": len(jobs),
            "created": 0,
            "updated": 0,
            "duplicates": 0,
            "errors": 0
        }
        
        for job in jobs:
            try:
                job_dict = job.dict()
                job_dict["created_at"] = datetime.utcnow()
                job_dict["updated_at"] = datetime.utcnow()
                job_dict["is_active"] = True
                job_dict["views_count"] = 0
                job_dict["applications_count"] = 0
                
                # Use deduplication service
                job_id, dedup_result = await deduplication_service.save_job_with_deduplication(job_dict)
                
                if dedup_result.is_duplicate:
                    results["duplicates"] += 1
                else:
                    results["created"] += 1
            except Exception as e:
                results["errors"] += 1
                from backend.utils.logger import logger
                logger.error(f"Error creating job: {str(e)}")
        
        return results

    @staticmethod
    async def get_job(db: AsyncIOMotorDatabase, job_id: str) -> Optional[JobResponse]:
        """Get a job by ID."""
        try:
            job_doc = await db.jobs.find_one({"_id": ObjectId(job_id)})
            if job_doc:
                job_doc["id"] = str(job_doc["_id"])
                del job_doc["_id"]
                return JobResponse(**job_doc)
            return None
        except Exception:
            return None

    @staticmethod
    async def get_jobs(
        db: AsyncIOMotorDatabase,
        skip: int = 0,
        limit: int = 10,
        company: Optional[str] = None,
        location: Optional[str] = None,
        sort_by: Optional[str] = None,
        sort_order: int = -1
    ) -> List[JobResponse]:
        """Get jobs with optional filtering."""
        query = {"is_active": True}
        
        if company:
            query["company"] = {"$regex": company, "$options": "i"}
        if location:
            query["location"] = {"$regex": location, "$options": "i"}
        
        sort_field = sort_by or "created_at"
        cursor = db.jobs.find(query).sort(sort_field, sort_order).skip(skip).limit(limit)
        
        jobs = []
        async for job_doc in cursor:
            job_doc["id"] = str(job_doc["_id"])
            del job_doc["_id"]
            jobs.append(JobResponse(**job_doc))
        
        return jobs

    @staticmethod
    async def update_job(
        db: AsyncIOMotorDatabase,
        job_id: str,
        job: JobUpdate
    ) -> Optional[JobResponse]:
        """Update a job."""
        try:
            update_data = job.dict(exclude_unset=True)
            update_data["updated_at"] = datetime.utcnow()
            
            result = await db.jobs.update_one(
                {"_id": ObjectId(job_id)},
                {"$set": update_data}
            )
            
            if result.modified_count:
                return await JobCRUD.get_job(db, job_id)
            return None
        except Exception:
            return None

    @staticmethod
    async def delete_job(db: AsyncIOMotorDatabase, job_id: str) -> bool:
        """Delete a job."""
        try:
            result = await db.jobs.delete_one({"_id": ObjectId(job_id)})
            return result.deleted_count > 0
        except Exception:
            return False

    @staticmethod
    async def search_jobs(
        db: AsyncIOMotorDatabase,
        query: str,
        skip: int = 0,
        limit: int = 10
    ) -> List[JobResponse]:
        """Search jobs by text."""
        search_query = {
            "$or": [
                {"title": {"$regex": query, "$options": "i"}},
                {"description": {"$regex": query, "$options": "i"}},
                {"company": {"$regex": query, "$options": "i"}},
                {"location": {"$regex": query, "$options": "i"}}
            ],
            "is_active": True
        }
        
        cursor = db.jobs.find(search_query).skip(skip).limit(limit)
        jobs = []
        async for job_doc in cursor:
            job_doc["id"] = str(job_doc["_id"])
            del job_doc["_id"]
            jobs.append(JobResponse(**job_doc))
        
        return jobs

    @staticmethod
    async def get_job_statistics(db: AsyncIOMotorDatabase) -> Dict[str, Any]:
        """Get job statistics."""
        total_jobs = await db.jobs.count_documents({"is_active": True})
        companies_count = len(await db.jobs.distinct("company", {"is_active": True}))
        
        return {
            "total_jobs": total_jobs,
            "total_companies": companies_count
        }

# Backward compatibility - keep original functions
create_job = JobCRUD.create_job
create_job_batch = JobCRUD.create_job_batch
get_job = JobCRUD.get_job
get_jobs = JobCRUD.get_jobs
update_job = JobCRUD.update_job
delete_job = JobCRUD.delete_job
search_jobs = JobCRUD.search_jobs
get_job_statistics = JobCRUD.get_job_statistics 