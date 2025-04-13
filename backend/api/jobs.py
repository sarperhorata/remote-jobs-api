from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional, Dict, Any
from models.models import Job
from utils.db import get_jobs, get_job, delete_job

router = APIRouter()

@router.get("/", response_model=List[Job])
async def get_all_jobs(
    company: Optional[str] = Query(None, description="Filter by company name (partial match)"),
    location: Optional[str] = Query(None, description="Filter by location (partial match)"),
    website_id: Optional[int] = Query(None, description="Filter by website ID"),
    is_remote: Optional[bool] = Query(None, description="Filter by remote status"),
    limit: int = Query(100, ge=1, le=1000, description="Limit the number of results"),
    offset: int = Query(0, ge=0, description="Offset for pagination")
):
    """
    Lists all job postings
    """
    filters = {}
    if company:
        filters["company"] = company
    if location:
        filters["location"] = location
    if website_id:
        filters["website_id"] = website_id
    if is_remote is not None:
        filters["is_remote"] = is_remote
    
    jobs = await get_jobs(filters=filters, limit=limit, offset=offset)
    return jobs

@router.get("/{job_id}", response_model=Job)
async def get_job_by_id(job_id: int):
    """
    Gets a specific job posting by ID
    """
    job = await get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail=f"Job with ID {job_id} not found")
    return job

@router.delete("/{job_id}")
async def delete_job_by_id(job_id: int):
    """
    Deletes a job posting
    """
    # First check if the job exists
    job = await get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail=f"Job with ID {job_id} not found")
    
    # Delete from database
    success = await delete_job(job_id)
    
    if not success:
        raise HTTPException(status_code=400, detail="Job deletion failed")
    
    return {"message": f"Job with ID {job_id} successfully deleted"}

@router.get("/search", response_model=List[Job])
async def search_jobs(
    q: str = Query(..., description="Search query (searches in title, company and description)"),
    limit: int = Query(100, ge=1, le=1000, description="Limit the number of results"),
    offset: int = Query(0, ge=0, description="Offset for pagination")
):
    """
    Searches job postings
    """
    # In this simple example, we don't fully model database operations for search,
    # we just filter previously retrieved job listings
    jobs = await get_jobs(limit=1000, offset=0)  # Get a larger dataset
    
    q = q.lower()
    filtered_jobs = []
    
    for job in jobs:
        title = job.title.lower() if job.title else ""
        company = job.company.lower() if job.company else ""
        description = job.description.lower() if job.description else ""
        
        if q in title or q in company or q in description:
            filtered_jobs.append(job)
    
    # Apply pagination
    start = offset
    end = offset + limit
    
    return filtered_jobs[start:end] 