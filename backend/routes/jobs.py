from fastapi import APIRouter, Depends, HTTPException, Query, status
from typing import List, Optional, Dict, Any
from datetime import datetime
from bson import ObjectId

from models.job import Job, JobCreate, JobUpdate, JobResponse, JobListResponse
from models.user import User
from utils.auth import get_current_user, get_current_admin
from utils.db import async_jobs
from utils.job_archiver import archive_old_jobs, get_archived_jobs, restore_job, get_job_count

router = APIRouter(prefix="/jobs", tags=["jobs"])

@router.get("", response_model=JobListResponse)
async def get_jobs(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    search: Optional[str] = None,
    location: Optional[str] = None,
    job_type: Optional[str] = None,
    skills: Optional[List[str]] = None,
    min_salary: Optional[int] = None,
    max_salary: Optional[int] = None,
    sort_by: Optional[str] = "posted_at",
    sort_order: Optional[str] = "desc",
    current_user: User = Depends(get_current_user)
):
    """
    Get a list of active (non-archived) jobs with optional filtering.
    """
    # Build the query
    query = {"is_archived": {"$ne": True}}
    
    if search:
        query["$or"] = [
            {"title": {"$regex": search, "$options": "i"}},
            {"company": {"$regex": search, "$options": "i"}},
            {"description": {"$regex": search, "$options": "i"}}
        ]
    
    if location:
        query["location"] = {"$regex": location, "$options": "i"}
    
    if job_type:
        query["job_type"] = job_type
    
    if skills:
        query["skills"] = {"$in": skills}
    
    if min_salary is not None or max_salary is not None:
        query["salary"] = {}
        if min_salary is not None:
            query["salary"]["$gte"] = min_salary
        if max_salary is not None:
            query["salary"]["$lte"] = max_salary
    
    # Determine sort direction
    sort_direction = -1 if sort_order == "desc" else 1
    
    # Get total count for pagination
    total = await async_jobs.count_documents(query)
    
    # Execute the query with sorting and pagination
    cursor = async_jobs.find(query).sort(sort_by, sort_direction).skip(skip).limit(limit)
    jobs = await cursor.to_list(length=limit)
    
    # Convert ObjectId to string for JSON serialization
    for job in jobs:
        job["_id"] = str(job["_id"])
    
    return {
        "jobs": jobs,
        "total": total,
        "page": skip // limit + 1,
        "pages": (total + limit - 1) // limit
    }

@router.get("/{job_id}", response_model=JobResponse)
async def get_job(job_id: str, current_user: User = Depends(get_current_user)):
    """
    Get a specific job by ID.
    """
    try:
        job = await async_jobs.find_one({"_id": ObjectId(job_id), "is_archived": {"$ne": True}})
        
        if not job:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")
        
        # Convert ObjectId to string for JSON serialization
        job["_id"] = str(job["_id"])
        
        return job
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.post("", response_model=JobResponse, status_code=status.HTTP_201_CREATED)
async def create_job(job: JobCreate, current_user: User = Depends(get_current_admin)):
    """
    Create a new job (admin only).
    """
    try:
        job_data = job.dict()
        job_data["posted_at"] = datetime.now()
        job_data["is_archived"] = False
        
        result = await async_jobs.insert_one(job_data)
        
        # Get the created job
        created_job = await async_jobs.find_one({"_id": result.inserted_id})
        created_job["_id"] = str(created_job["_id"])
        
        return created_job
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.put("/{job_id}", response_model=JobResponse)
async def update_job(job_id: str, job: JobUpdate, current_user: User = Depends(get_current_admin)):
    """
    Update a job (admin only).
    """
    try:
        # Check if job exists
        existing_job = await async_jobs.find_one({"_id": ObjectId(job_id)})
        if not existing_job:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")
        
        # Update the job
        update_data = {k: v for k, v in job.dict(exclude_unset=True).items()}
        
        result = await async_jobs.update_one(
            {"_id": ObjectId(job_id)},
            {"$set": update_data}
        )
        
        if result.modified_count == 0:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No changes made")
        
        # Get the updated job
        updated_job = await async_jobs.find_one({"_id": ObjectId(job_id)})
        updated_job["_id"] = str(updated_job["_id"])
        
        return updated_job
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.delete("/{job_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_job(job_id: str, current_user: User = Depends(get_current_admin)):
    """
    Soft delete a job (admin only).
    """
    try:
        # Check if job exists
        existing_job = await async_jobs.find_one({"_id": ObjectId(job_id)})
        if not existing_job:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")
        
        # Soft delete by setting is_archived to True
        result = await async_jobs.update_one(
            {"_id": ObjectId(job_id)},
            {"$set": {"is_archived": True, "archived_at": datetime.now()}}
        )
        
        if result.modified_count == 0:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Failed to delete job")
        
        return None
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get("/{job_id}/similar", response_model=List[JobResponse])
async def get_similar_jobs(
    job_id: str,
    limit: int = Query(5, ge=1, le=20),
    current_user: User = Depends(get_current_user)
):
    """
    Get similar jobs based on skills.
    """
    try:
        # Get the job
        job = await async_jobs.find_one({"_id": ObjectId(job_id), "is_archived": {"$ne": True}})
        if not job:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")
        
        # Get similar jobs based on skills
        skills = job.get("skills", [])
        if not skills:
            return []
        
        similar_jobs = await async_jobs.find({
            "_id": {"$ne": ObjectId(job_id)},
            "is_archived": {"$ne": True},
            "skills": {"$in": skills}
        }).limit(limit).to_list(length=limit)
        
        # Convert ObjectId to string for JSON serialization
        for similar_job in similar_jobs:
            similar_job["_id"] = str(similar_job["_id"])
        
        return similar_jobs
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.post("/{job_id}/apply", status_code=status.HTTP_201_CREATED)
async def apply_for_job(job_id: str, current_user: User = Depends(get_current_user)):
    """
    Apply for a job.
    """
    try:
        # Check if job exists and is not archived
        job = await async_jobs.find_one({"_id": ObjectId(job_id), "is_archived": {"$ne": True}})
        if not job:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")
        
        # TODO: Implement job application logic
        # This could involve creating a new collection for applications
        # and storing the user's application data
        
        return {"message": "Application submitted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.post("/{job_id}/save", status_code=status.HTTP_201_CREATED)
async def save_job(job_id: str, current_user: User = Depends(get_current_user)):
    """
    Save a job for later.
    """
    try:
        # Check if job exists and is not archived
        job = await async_jobs.find_one({"_id": ObjectId(job_id), "is_archived": {"$ne": True}})
        if not job:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")
        
        # TODO: Implement job saving logic
        # This could involve updating the user's saved jobs list
        
        return {"message": "Job saved successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.delete("/{job_id}/save", status_code=status.HTTP_204_NO_CONTENT)
async def remove_saved_job(job_id: str, current_user: User = Depends(get_current_user)):
    """
    Remove a saved job.
    """
    try:
        # TODO: Implement job removal logic
        # This could involve updating the user's saved jobs list
        
        return None
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get("/saved", response_model=List[JobResponse])
async def get_saved_jobs(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    current_user: User = Depends(get_current_user)
):
    """
    Get saved jobs.
    """
    try:
        # TODO: Implement saved jobs retrieval logic
        # This could involve querying the user's saved jobs list
        
        return []
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get("/archived", response_model=List[JobResponse])
async def get_archived_jobs_admin(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    current_user: User = Depends(get_current_admin)
):
    """
    Get archived jobs (admin only).
    """
    try:
        archived_jobs = await get_archived_jobs(skip, limit)
        return archived_jobs
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.post("/{job_id}/restore", response_model=JobResponse)
async def restore_job_admin(job_id: str, current_user: User = Depends(get_current_admin)):
    """
    Restore an archived job (admin only).
    """
    try:
        success = await restore_job(job_id)
        if not success:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found or already restored")
        
        # Get the restored job
        restored_job = await async_jobs.find_one({"_id": ObjectId(job_id)})
        restored_job["_id"] = str(restored_job["_id"])
        
        return restored_job
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.post("/archive-old", status_code=status.HTTP_200_OK)
async def archive_old_jobs_endpoint(current_user: User = Depends(get_current_admin)):
    """
    Manually trigger the archiving of old jobs (admin only).
    """
    try:
        archived_count = await archive_old_jobs()
        return {"message": f"Archived {archived_count} old jobs"}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)) 