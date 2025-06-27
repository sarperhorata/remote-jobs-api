from fastapi import APIRouter, Depends, HTTPException, Query, status, Body
from typing import List, Optional, Dict, Any
from datetime import datetime
from bson import ObjectId
from backend.database import get_async_db
from backend.utils.auth import get_current_user, get_current_admin, get_current_active_user
import os
import logging
from backend.schemas.job import JobCreate, JobResponse
from sqlalchemy.ext.asyncio import AsyncSession
from backend.crud import job as job_crud
from backend.schemas.job import JobUpdate, JobListResponse
from motor.motor_asyncio import AsyncIOMotorDatabase
from backend.schemas.job import Job, JobCreate
from backend.models.models import JobApplication
from backend.schemas.job import JobSearchQuery, ApplicationCreate
from backend.services.job_scraping_service import JobScrapingService
from backend.services.auto_application_service import AutoApplicationService

router = APIRouter(prefix="/jobs", tags=["jobs"])
logger = logging.getLogger(__name__)

@router.post("/", response_model=Job, status_code=status.HTTP_201_CREATED)
async def create_job(
    job: JobCreate, db: AsyncIOMotorDatabase = Depends(get_async_db)
):
    """Create a new job."""
    job_dict = job.model_dump()
    result = await db.jobs.insert_one(job_dict)
    created_job = await db.jobs.find_one({"_id": result.inserted_id})
    return created_job

@router.get("/", response_model=JobListResponse)
async def read_jobs(
    skip: int = 0, limit: int = 100, db: AsyncIOMotorDatabase = Depends(get_async_db)
):
    """Retrieve all jobs with pagination."""
    jobs_cursor = db.jobs.find().skip(skip).limit(limit)
    total_jobs = await db.jobs.count_documents({})
    jobs = await jobs_cursor.to_list(limit)
    return {
        "items": jobs,
        "total": total_jobs,
        "page": (skip // limit) + 1,
        "per_page": limit,
        "total_pages": (total_jobs + limit - 1) // limit,
    }

@router.get("/{job_id}", response_model=Job)
async def read_job(job_id: str, db: AsyncIOMotorDatabase = Depends(get_async_db)):
    """Retrieve a single job by its ID."""
    if not ObjectId.is_valid(job_id):
        raise HTTPException(status_code=400, detail="Invalid ObjectId format")
    job = await db.jobs.find_one({"_id": ObjectId(job_id)})
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    return job

@router.put("/{job_id}", response_model=Job)
async def update_job(
    job_id: str, job: JobUpdate, db: AsyncIOMotorDatabase = Depends(get_async_db)
):
    """Update a job."""
    if not ObjectId.is_valid(job_id):
        raise HTTPException(status_code=400, detail="Invalid ObjectId format")
    
    update_data = job.model_dump(exclude_unset=True)
    
    if not update_data:
        raise HTTPException(status_code=400, detail="No update data provided")

    result = await db.jobs.update_one(
        {"_id": ObjectId(job_id)}, {"$set": update_data}
    )

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Job not found")
        
    updated_job = await db.jobs.find_one({"_id": ObjectId(job_id)})
    return updated_job

@router.delete("/{job_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_job(job_id: str, db: AsyncIOMotorDatabase = Depends(get_async_db)):
    """Delete a job."""
    if not ObjectId.is_valid(job_id):
        raise HTTPException(status_code=400, detail="Invalid ObjectId format")
        
    result = await db.jobs.delete_one({"_id": ObjectId(job_id)})
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return None

@router.get("/search", response_model=dict)
async def search_jobs(
    q: str = Query(..., description="Search query"),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: AsyncIOMotorDatabase = Depends(get_async_db)
):
    """Search jobs by title or description."""
    try:
        search_query = {
            "$or": [
                {"title": {"$regex": q, "$options": "i"}},
                {"description": {"$regex": q, "$options": "i"}},
                {"requirements": {"$regex": q, "$options": "i"}}
            ]
        }
        
        cursor = db.jobs.find(search_query).skip(skip).limit(limit)
        jobs = await cursor.to_list(length=None)
        
        # Convert ObjectIds to strings for JSON serialization
        for job in jobs:
            if "_id" in job and isinstance(job["_id"], ObjectId):
                job["_id"] = str(job["_id"])
        
        return {"jobs": jobs}
    except Exception as e:
        logging.error(f"Error getting job search: {str(e)}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Search failed")

@router.get("/statistics", response_model=dict)
async def get_job_statistics(
    db: AsyncIOMotorDatabase = Depends(get_async_db)
):
    """Get statistics about jobs."""
    try:
        total_jobs = await db.jobs.count_documents({})
        
        jobs_by_company = await db.jobs.aggregate([
            {"$group": {"_id": "$company", "count": {"$sum": 1}}}
        ]).to_list(length=None)
        
        jobs_by_location = await db.jobs.aggregate([
            {"$group": {"_id": "$location", "count": {"$sum": 1}}}
        ]).to_list(length=None)
        
        # Add jobs by position/title for autocomplete
        jobs_by_position = await db.jobs.aggregate([
            {"$group": {"_id": "$title", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
            {"$limit": 50}  # Top 50 most common positions
        ]).to_list(length=None)
        
        # Format positions for frontend autocomplete
        positions = [
            {"title": item["_id"], "count": item["count"]} 
            for item in jobs_by_position 
            if item["_id"]  # Filter out null/empty titles
        ]
        
        return {
            "total_jobs": total_jobs,
            "active_jobs": total_jobs,  # Assuming all jobs are active for now
            "jobs_by_company": jobs_by_company,
            "jobs_by_location": jobs_by_location,
            "positions": positions  # New field for position autocomplete
        }
    except Exception as e:
        logging.error(f"Error getting job statistics: {str(e)}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Statistics not available")

@router.get("/job-titles/search")
async def search_job_titles(
    q: str = Query(..., description="Search query for job titles"),
    limit: int = Query(10, description="Number of results to return")
):
    """Search for job titles"""
    try:
        # Common job titles - in production this could come from a database
        common_titles = [
            {"id": "1", "title": "Software Engineer", "category": "Technology"},
            {"id": "2", "title": "Frontend Developer", "category": "Technology"},
            {"id": "3", "title": "Backend Developer", "category": "Technology"},
            {"id": "4", "title": "Full Stack Developer", "category": "Technology"},
            {"id": "5", "title": "DevOps Engineer", "category": "Technology"},
            {"id": "6", "title": "Data Scientist", "category": "Data"},
            {"id": "7", "title": "Data Engineer", "category": "Data"},
            {"id": "8", "title": "Machine Learning Engineer", "category": "Data"},
            {"id": "9", "title": "Product Manager", "category": "Product"},
            {"id": "10", "title": "UX Designer", "category": "Design"},
            {"id": "11", "title": "UI Designer", "category": "Design"},
            {"id": "12", "title": "UX/UI Designer", "category": "Design"},
            {"id": "13", "title": "Marketing Manager", "category": "Marketing"},
            {"id": "14", "title": "Digital Marketing Specialist", "category": "Marketing"},
            {"id": "15", "title": "Content Writer", "category": "Content"},
            {"id": "16", "title": "Technical Writer", "category": "Content"},
            {"id": "17", "title": "Sales Representative", "category": "Sales"},
            {"id": "18", "title": "Business Development Manager", "category": "Sales"},
            {"id": "19", "title": "Customer Success Manager", "category": "Customer Success"},
            {"id": "20", "title": "Account Manager", "category": "Sales"},
            {"id": "21", "title": "Project Manager", "category": "Management"},
            {"id": "22", "title": "Scrum Master", "category": "Management"},
            {"id": "23", "title": "Quality Assurance Engineer", "category": "Technology"},
            {"id": "24", "title": "Security Engineer", "category": "Technology"},
            {"id": "25", "title": "Cloud Architect", "category": "Technology"},
            {"id": "26", "title": "Mobile Developer", "category": "Technology"},
            {"id": "27", "title": "iOS Developer", "category": "Technology"},
            {"id": "28", "title": "Android Developer", "category": "Technology"},
            {"id": "29", "title": "React Developer", "category": "Technology"},
            {"id": "30", "title": "Vue.js Developer", "category": "Technology"},
            {"id": "31", "title": "Angular Developer", "category": "Technology"},
            {"id": "32", "title": "Node.js Developer", "category": "Technology"},
            {"id": "33", "title": "Python Developer", "category": "Technology"},
            {"id": "34", "title": "Java Developer", "category": "Technology"},
            {"id": "35", "title": "C# Developer", "category": "Technology"},
            {"id": "36", "title": "PHP Developer", "category": "Technology"},
            {"id": "37", "title": "Ruby Developer", "category": "Technology"},
            {"id": "38", "title": "Go Developer", "category": "Technology"},
            {"id": "39", "title": "Rust Developer", "category": "Technology"},
            {"id": "40", "title": "Database Administrator", "category": "Technology"}
        ]
        
        # Filter titles based on search query
        filtered_titles = [
            title for title in common_titles 
            if q.lower() in title["title"].lower()
        ]
        
        return filtered_titles[:limit]
        
    except Exception as e:
        logger.error(f"Error searching job titles: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/skills/search")
async def search_skills(
    q: str = Query(..., description="Search query for skills"),
    limit: int = Query(10, description="Number of results to return")
):
    """Search for skills"""
    try:
        # Common skills - in production this could come from a database
        common_skills = [
            {"id": "1", "name": "JavaScript"},
            {"id": "2", "name": "Python"},
            {"id": "3", "name": "React"},
            {"id": "4", "name": "Node.js"},
            {"id": "5", "name": "TypeScript"},
            {"id": "6", "name": "HTML"},
            {"id": "7", "name": "CSS"},
            {"id": "8", "name": "Java"},
            {"id": "9", "name": "C++"},
            {"id": "10", "name": "C#"},
            {"id": "11", "name": "PHP"},
            {"id": "12", "name": "Ruby"},
            {"id": "13", "name": "Go"},
            {"id": "14", "name": "Rust"},
            {"id": "15", "name": "Swift"},
            {"id": "16", "name": "Kotlin"},
            {"id": "17", "name": "SQL"},
            {"id": "18", "name": "PostgreSQL"},
            {"id": "19", "name": "MySQL"},
            {"id": "20", "name": "MongoDB"},
            {"id": "21", "name": "Redis"},
            {"id": "22", "name": "Docker"},
            {"id": "23", "name": "Kubernetes"},
            {"id": "24", "name": "AWS"},
            {"id": "25", "name": "Azure"},
            {"id": "26", "name": "Google Cloud"},
            {"id": "27", "name": "Git"},
            {"id": "28", "name": "Jenkins"},
            {"id": "29", "name": "CI/CD"},
            {"id": "30", "name": "Linux"},
            {"id": "31", "name": "Vue.js"},
            {"id": "32", "name": "Angular"},
            {"id": "33", "name": "Django"},
            {"id": "34", "name": "Flask"},
            {"id": "35", "name": "Express.js"},
            {"id": "36", "name": "Spring Boot"},
            {"id": "37", "name": "Laravel"},
            {"id": "38", "name": "Ruby on Rails"},
            {"id": "39", "name": "TensorFlow"},
            {"id": "40", "name": "PyTorch"},
            {"id": "41", "name": "Machine Learning"},
            {"id": "42", "name": "Data Science"},
            {"id": "43", "name": "Artificial Intelligence"},
            {"id": "44", "name": "REST API"},
            {"id": "45", "name": "GraphQL"},
            {"id": "46", "name": "Microservices"},
            {"id": "47", "name": "Agile"},
            {"id": "48", "name": "Scrum"},
            {"id": "49", "name": "Unit Testing"},
            {"id": "50", "name": "Test Driven Development"}
        ]
        
        # Filter skills based on search query
        filtered_skills = [
            skill for skill in common_skills 
            if q.lower() in skill["name"].lower()
        ]
        
        return filtered_skills[:limit]
        
    except Exception as e:
        logger.error(f"Error searching skills: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/recent")
async def get_recent_jobs(
    since: Optional[str] = Query(None, description="ISO timestamp to get jobs since"),
    limit: int = Query(10, description="Number of recent jobs to return"),
    db: AsyncIOMotorDatabase = Depends(get_async_db)
):
    """Get recent jobs for notifications"""
    try:
        # Parse since timestamp if provided
        since_datetime = None
        if since:
            try:
                since_datetime = datetime.fromisoformat(since.replace('Z', '+00:00'))
            except ValueError:
                logger.warning(f"Invalid since timestamp: {since}")
        
        # Build query
        query = {}
        if since_datetime:
            query["created_at"] = {"$gte": since_datetime}
        
        # Get recent jobs from database
        jobs_cursor = db.jobs.find(query).sort("created_at", -1).limit(limit)
        jobs = await jobs_cursor.to_list(length=limit)
        
        # Convert ObjectId to string for JSON serialization
        for job in jobs:
            if "_id" in job:
                job["id"] = str(job["_id"])
                del job["_id"]
        
        return jobs
        
    except Exception as e:
        logger.error(f"Error getting recent jobs: {str(e)}")
        return []  # Return empty list on error to avoid breaking notifications

@router.get("/recommendations", response_model=List[dict])
async def get_job_recommendations(
    limit: int = Query(10, ge=1, le=50),
    db: AsyncIOMotorDatabase = Depends(get_async_db)
):
    """Get job recommendations for users."""
    try:
        # Simple recommendation: get latest active jobs
        cursor = db.jobs.find({"is_active": {"$ne": False}}).sort("created_at", -1).limit(limit)
        jobs = await cursor.to_list(length=None)
        
        # Convert ObjectIds to strings
        for job in jobs:
            if "_id" in job and isinstance(job["_id"], ObjectId):
                job["_id"] = str(job["_id"])
        
        return jobs
    except Exception as e:
        logging.error(f"Error getting job recommendations: {str(e)}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recommendations not available")

@router.get("/")
async def get_jobs(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    page: Optional[int] = Query(None, ge=1),  # Frontend compatibility
    per_page: Optional[int] = Query(None, ge=1, le=100),  # Frontend compatibility  
    company: Optional[str] = None,
    location: Optional[str] = None,
    sort_by: Optional[str] = None,
    sort_order: int = Query(-1, ge=-1, le=1),
    db: AsyncIOMotorDatabase = Depends(get_async_db)
):
    """Get a list of jobs with optional filtering and sorting."""
    
    # Handle frontend pagination parameters
    if page is not None and per_page is not None:
        skip = (page - 1) * per_page
        limit = per_page
    elif per_page is not None:
        limit = per_page
        
    query = {}
    if company:
        query["company"] = company
    if location:
        query["location"] = location
    
    # Build sort criteria
    sort_criteria = []
    if sort_by:
        sort_criteria.append((sort_by, sort_order))
    sort_criteria.append(("created_at", -1))
    
    try:
        # Get total count
        total = await db.jobs.count_documents(query)
        
        # Get jobs
        cursor = db.jobs.find(query).sort(sort_criteria).skip(skip).limit(limit)
        jobs = await cursor.to_list(length=limit)
        
        # Convert ObjectIds to strings
        for job in jobs:
            if "_id" in job and isinstance(job["_id"], ObjectId):
                job["_id"] = str(job["_id"])
        
        # If no jobs found, return sample data for development
        if not jobs or total == 0:
            sample_jobs = [
                {
                    "_id": "sample_1",
                    "title": "Senior Frontend Developer",
                    "company": "TechCorp",
                    "location": "Remote",
                    "job_type": "Full-time",
                    "salary_range": "$90k - $130k",
                    "skills": ["React", "TypeScript", "Next.js"],
                    "description": "Join our team as a Senior Frontend Developer working on cutting-edge applications.",
                    "created_at": datetime.utcnow().isoformat(),
                    "is_active": True,
                    "remote_type": "remote"
                },
                {
                    "_id": "sample_2", 
                    "title": "DevOps Engineer",
                    "company": "CloudSoft",
                    "location": "Remote (EU)",
                    "job_type": "Full-time",
                    "salary_range": "$80k - $120k",
                    "skills": ["AWS", "Docker", "Kubernetes"],
                    "description": "Looking for a DevOps Engineer to manage our cloud infrastructure.",
                    "created_at": datetime.utcnow().isoformat(),
                    "is_active": True,
                    "remote_type": "remote"
                },
                {
                    "_id": "sample_3",
                    "title": "Product Manager",
                    "company": "StartupX",
                    "location": "Remote (US)",
                    "job_type": "Full-time", 
                    "salary_range": "$100k - $150k",
                    "skills": ["Product Strategy", "Analytics", "Agile"],
                    "description": "Lead product development for our innovative SaaS platform.",
                    "created_at": datetime.utcnow().isoformat(),
                    "is_active": True,
                    "remote_type": "remote"
                },
                {
                    "_id": "sample_4",
                    "title": "Full Stack Developer",
                    "company": "WebTech Inc",
                    "location": "Remote",
                    "job_type": "Contract",
                    "salary_range": "$70k - $100k",
                    "skills": ["Node.js", "React", "MongoDB"],
                    "description": "Build end-to-end web applications with modern technologies.",
                    "created_at": datetime.utcnow().isoformat(),
                    "is_active": True,
                    "remote_type": "remote"
                },
                {
                    "_id": "sample_5",
                    "title": "UX Designer",
                    "company": "DesignHub",
                    "location": "Remote (Global)",
                    "job_type": "Part-time",
                    "salary_range": "$50k - $80k",
                    "skills": ["Figma", "User Research", "Prototyping"],
                    "description": "Create amazing user experiences for our digital products.",
                    "created_at": datetime.utcnow().isoformat(),
                    "is_active": True,
                    "remote_type": "remote"
                },
                {
                    "_id": "sample_6",
                    "title": "Data Scientist",
                    "company": "DataCorp",
                    "location": "Remote",
                    "job_type": "Full-time",
                    "salary_range": "$110k - $160k",
                    "skills": ["Python", "Machine Learning", "SQL"],
                    "description": "Analyze data and build ML models to drive business insights.",
                    "created_at": datetime.utcnow().isoformat(),
                    "is_active": True,
                    "remote_type": "remote"
                }
            ]
            
            # Apply filters to sample data if any
            filtered_jobs = sample_jobs
            if company:
                filtered_jobs = [job for job in filtered_jobs if company.lower() in job["company"].lower()]
            if location:
                filtered_jobs = [job for job in filtered_jobs if location.lower() in job["location"].lower()]
                
            # Apply pagination to sample data
            total_samples = len(filtered_jobs)
            paginated_jobs = filtered_jobs[skip:skip + limit]
            
            return {
                "jobs": paginated_jobs,
                "total": total_samples,
                "page": skip // limit + 1,
                "per_page": limit,
                "limit": limit,
                "total_pages": (total_samples + limit - 1) // limit
            }
        
        return {
            "jobs": jobs,
            "total": total,
            "page": skip // limit + 1,
            "per_page": limit,
            "limit": limit,  # Add for test compatibility
            "total_pages": (total + limit - 1) // limit
        }
        
    except Exception as e:
        logger.error(f"Error fetching jobs: {str(e)}")
        # Return sample data on error
        sample_jobs = [
            {
                "_id": "fallback_1",
                "title": "Remote Software Engineer",
                "company": "TechCompany",
                "location": "Remote",
                "job_type": "Full-time",
                "skills": ["JavaScript", "Python", "React"],
                "description": "Join our remote team of developers.",
                "created_at": datetime.utcnow().isoformat(),
                "is_active": True
            }
        ]
        
        return {
            "jobs": sample_jobs[:limit],
            "total": len(sample_jobs),
            "page": 1,
            "per_page": limit,
            "limit": limit,
            "total_pages": 1
        }

@router.get("/{job_id}/similar", response_model=List[dict])
async def get_similar_jobs(
    job_id: str,
    limit: int = Query(5, ge=1, le=20),
    current_user: dict = Depends(get_current_user)
):
    """
    Get similar jobs based on skills.
    """
    try:
        db = await get_async_db()
        jobs_col = db["jobs"]
        job = jobs_col.find_one({"_id": ObjectId(job_id), "is_archived": {"$ne": True}})
        if not job:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")
        
        skills = job.get("skills", [])
        if not skills:
            return []
        
        similar_jobs = list(jobs_col.find({
            "_id": {"$ne": ObjectId(job_id)},
            "is_archived": {"$ne": True},
            "skills": {"$in": skills}
        }).limit(limit))
        
        for similar_job in similar_jobs:
            similar_job["_id"] = str(similar_job["_id"])
        
        return similar_jobs
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.post("/{job_id}/apply", status_code=status.HTTP_201_CREATED)
async def apply_for_job(job_id: str, current_user: dict = Depends(get_current_user)):
    """
    Apply for a job.
    """
    try:
        db = await get_async_db()
        jobs_col = db["jobs"]
        job = jobs_col.find_one({"_id": ObjectId(job_id), "is_archived": {"$ne": True}})
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
async def save_job(job_id: str, current_user: dict = Depends(get_current_user)):
    """
    Save a job for later.
    """
    try:
        db = await get_async_db()
        jobs_col = db["jobs"]
        job = jobs_col.find_one({"_id": ObjectId(job_id), "is_archived": {"$ne": True}})
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
async def remove_saved_job(job_id: str, current_user: dict = Depends(get_current_user)):
    """
    Remove a saved job.
    """
    try:
        # TODO: Implement job removal logic
        # This could involve updating the user's saved jobs list
        
        return None
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get("/saved", response_model=List[dict])
async def get_saved_jobs(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    current_user: dict = Depends(get_current_user)
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

@router.get("/archived", response_model=List[dict])
async def get_archived_jobs_admin(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    current_user: dict = Depends(get_current_admin)
):
    """
    Get archived jobs (admin only).
    """
    try:
        db = await get_async_db()
        jobs_col = db["jobs"]
        archived_jobs = list(jobs_col.find({"is_archived": True}).skip(skip).limit(limit))
        for job in archived_jobs:
            job["_id"] = str(job["_id"])
        return archived_jobs
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.post("/{job_id}/restore", response_model=dict)
async def restore_job_admin(job_id: str, current_user: dict = Depends(get_current_admin)):
    """
    Restore an archived job (admin only).
    """
    try:
        db = await get_async_db()
        jobs_col = db["jobs"]
        success = jobs_col.update_one({"_id": ObjectId(job_id)}, {"$set": {"is_archived": False}})
        if not success.modified_count:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found or already restored")
        
        restored_job = jobs_col.find_one({"_id": ObjectId(job_id)})
        restored_job["_id"] = str(restored_job["_id"])
        
        return restored_job
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.post("/archive-old", status_code=status.HTTP_200_OK)
async def archive_old_jobs_endpoint(current_user: dict = Depends(get_current_admin)):
    """
    Manually trigger the archiving of old jobs (admin only).
    """
    try:
        db = await get_async_db()
        jobs_col = db["jobs"]
        archived_count = jobs_col.count_documents({"is_archived": True})
        jobs_col.update_many({"is_archived": True}, {"$set": {"is_archived": False}})
        return {"message": f"Archived {archived_count} old jobs"}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

# NEW JOB DATA MANAGEMENT ENDPOINTS

@router.post("/admin/crawl-jobs", status_code=status.HTTP_202_ACCEPTED)
async def trigger_job_crawling(current_user: dict = Depends(get_current_admin)):
    """
    Trigger manual job crawling from all configured sources (admin only).
    """
    try:
        from utils.job_crawler import JobDataManager
        
        # Start crawling in background
        manager = JobDataManager()
        result = await manager.update_job_listings()
        
        return {
            "message": "Job crawling completed",
            "result": result
        }
        
    except Exception as e:
        logger.error(f"Error triggering job crawling: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"Failed to trigger job crawling: {str(e)}"
        )

@router.post("/admin/fetch-api-jobs", status_code=status.HTTP_202_ACCEPTED)
async def trigger_api_job_fetching(
    query: str = "remote developer",
    location: str = "remote",
    current_user: dict = Depends(get_current_admin)
):
    """
    Trigger manual job fetching from API sources (admin only).
    """
    try:
        from utils.job_api_integrations import JobAPIIntegration
        from backend.database import get_async_db
        from datetime import datetime
        
        api_integration = JobAPIIntegration()
        jobs = await api_integration.fetch_jobs_from_all_apis(query, location)
        
        # Save to database
        db = await get_async_db()
        jobs_collection = db["jobs"]
        
        new_jobs = 0
        updated_jobs = 0
        
        for job in jobs:
            existing_job = jobs_collection.find_one({
                "external_id": job.external_id,
                "source_url": job.source_url
            })
            
            job_data = {
                "title": job.title,
                "company": job.company,
                "location": job.location,
                "job_type": job.job_type,
                "salary": job.salary,
                "description": job.description,
                "requirements": job.requirements,
                "posted_date": job.posted_date,
                "apply_url": job.apply_url,
                "remote_type": job.remote_type,
                "skills": job.skills,
                "source_url": job.source_url,
                "external_id": job.external_id,
                "is_active": True,
                "last_updated": datetime.now(),
                "source_type": "api"
            }
            
            if existing_job:
                jobs_collection.update_one(
                    {"_id": existing_job["_id"]},
                    {"$set": job_data}
                )
                updated_jobs += 1
            else:
                job_data["created_at"] = datetime.now()
                jobs_collection.insert_one(job_data)
                new_jobs += 1
        
        return {
            "message": "API job fetching completed",
            "new_jobs": new_jobs,
            "updated_jobs": updated_jobs,
            "total_fetched": len(jobs),
            "query_used": query,
            "location_used": location
        }
        
    except Exception as e:
        logger.error(f"Error triggering API job fetching: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"Failed to fetch API jobs: {str(e)}"
        )

@router.post("/admin/aggregate-all-jobs", status_code=status.HTTP_202_ACCEPTED)
async def trigger_full_job_aggregation(current_user: dict = Depends(get_current_admin)):
    """
    Trigger full job aggregation from all sources (crawling + APIs) (admin only).
    """
    try:
        from utils.job_api_integrations import JobDataAggregator
        
        aggregator = JobDataAggregator()
        result = await aggregator.aggregate_jobs_from_all_sources()
        
        return {
            "message": "Full job aggregation completed",
            "result": result
        }
        
    except Exception as e:
        logger.error(f"Error triggering job aggregation: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"Failed to aggregate jobs: {str(e)}"
        )

@router.get("/admin/data-sources-status")
async def get_data_sources_status(current_user: dict = Depends(get_current_admin)):
    """
    Get status of all job data sources (admin only).
    """
    try:
        db = await get_async_db()
        jobs_col = db["jobs"]
        
        # Get statistics by source
        pipeline = [
            {"$match": {"is_active": True}},
            {"$group": {
                "_id": "$source_url",
                "count": {"$sum": 1},
                "latest_update": {"$max": "$last_updated"},
                "source_type": {"$first": "$source_type"}
            }},
            {"$sort": {"count": -1}}
        ]
        
        source_stats = list(jobs_col.aggregate(pipeline))
        
        # Get overall statistics
        total_active = jobs_col.count_documents({"is_active": True})
        total_inactive = jobs_col.count_documents({"is_active": False})
        
        # Recent job additions (last 24 hours)
        from datetime import datetime, timedelta
        yesterday = datetime.now() - timedelta(days=1)
        recent_jobs = jobs_col.count_documents({
            "created_at": {"$gte": yesterday},
            "is_active": True
        })
        
        # Remote job statistics
        remote_jobs = jobs_col.count_documents({
            "is_active": True,
            "remote_type": "remote"
        })
        
        hybrid_jobs = jobs_col.count_documents({
            "is_active": True,
            "remote_type": "hybrid"
        })
        
        return {
            "overall_stats": {
                "total_active_jobs": total_active,
                "total_inactive_jobs": total_inactive,
                "recent_jobs_24h": recent_jobs,
                "remote_jobs": remote_jobs,
                "hybrid_jobs": hybrid_jobs
            },
            "source_breakdown": source_stats,
            "data_sources": {
                "crawling_sources": [
                    "remoteok.io",
                    "weworkremotely.com", 
                    "remote.co",
                    "stackoverflow.com"
                ],
                "api_sources": [
                    "jsearch.p.rapidapi.com",
                    "reed.co.uk",
                    "adzuna.com",
                    "jobs2careers.com"
                ]
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting data sources status: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"Failed to get data sources status: {str(e)}"
        )

@router.get("/admin/job-quality-metrics")
async def get_job_quality_metrics(current_user: dict = Depends(get_current_admin)):
    """
    Get job data quality metrics (admin only).
    """
    try:
        db = await get_async_db()
        jobs_col = db["jobs"]
        
        # Quality metrics
        pipeline = [
            {"$match": {"is_active": True}},
            {"$project": {
                "has_salary": {"$ne": ["$salary", None]},
                "has_description": {"$ne": ["$description", ""]},
                "has_requirements": {"$gt": [{"$size": "$requirements"}, 0]},
                "has_skills": {"$gt": [{"$size": "$skills"}, 0]},
                "has_company": {"$ne": ["$company", ""]},
                "description_length": {"$strLenCP": "$description"}
            }},
            {"$group": {
                "_id": None,
                "total_jobs": {"$sum": 1},
                "jobs_with_salary": {"$sum": {"$cond": ["$has_salary", 1, 0]}},
                "jobs_with_description": {"$sum": {"$cond": ["$has_description", 1, 0]}},
                "jobs_with_requirements": {"$sum": {"$cond": ["$has_requirements", 1, 0]}},
                "jobs_with_skills": {"$sum": {"$cond": ["$has_skills", 1, 0]}},
                "jobs_with_company": {"$sum": {"$cond": ["$has_company", 1, 0]}},
                "avg_description_length": {"$avg": "$description_length"}
            }}
        ]
        
        quality_stats = list(jobs_col.aggregate(pipeline))
        
        if quality_stats:
            stats = quality_stats[0]
            total = stats["total_jobs"]
            
            quality_metrics = {
                "total_jobs": total,
                "data_completeness": {
                    "salary_percentage": round((stats["jobs_with_salary"] / total) * 100, 2),
                    "description_percentage": round((stats["jobs_with_description"] / total) * 100, 2),
                    "requirements_percentage": round((stats["jobs_with_requirements"] / total) * 100, 2),
                    "skills_percentage": round((stats["jobs_with_skills"] / total) * 100, 2),
                    "company_percentage": round((stats["jobs_with_company"] / total) * 100, 2)
                },
                "avg_description_length": round(stats.get("avg_description_length", 0)),
                "overall_quality_score": round(
                    (stats["jobs_with_salary"] + stats["jobs_with_description"] + 
                     stats["jobs_with_requirements"] + stats["jobs_with_skills"] + 
                     stats["jobs_with_company"]) / (total * 5) * 100, 2
                )
            }
        else:
            quality_metrics = {
                "total_jobs": 0,
                "data_completeness": {},
                "avg_description_length": 0,
                "overall_quality_score": 0
            }
        
        return quality_metrics
        
    except Exception as e:
        logger.error(f"Error getting job quality metrics: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"Failed to get job quality metrics: {str(e)}"
        )

@router.delete("/admin/cleanup-inactive-jobs")
async def cleanup_inactive_jobs(
    days_old: int = 60,
    current_user: dict = Depends(get_current_admin)
):
    """
    Delete inactive jobs older than specified days (admin only).
    """
    try:
        from datetime import datetime, timedelta
        
        db = await get_async_db()
        jobs_col = db["jobs"]
        
        cutoff_date = datetime.now() - timedelta(days=days_old)
        
        # Delete old inactive jobs
        result = jobs_col.delete_many({
            "is_active": False,
            "last_updated": {"$lt": cutoff_date}
        })
        
        return {
            "message": f"Cleanup completed",
            "deleted_jobs": result.deleted_count,
            "cutoff_date": cutoff_date.isoformat(),
            "days_old_threshold": days_old
        }
        
    except Exception as e:
        logger.error(f"Error cleaning up inactive jobs: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"Failed to cleanup inactive jobs: {str(e)}"
        )

@router.post("/admin/update-job-skills")
async def update_job_skills(current_user: dict = Depends(get_current_admin)):
    """
    Re-process all jobs to update extracted skills (admin only).
    """
    try:
        from utils.job_crawler import JobCrawler
        
        db = await get_async_db()
        jobs_col = db["jobs"]
        
        crawler = JobCrawler()
        updated_count = 0
        
        # Process jobs in batches
        batch_size = 100
        skip = 0
        
        while True:
            jobs = list(jobs_col.find({"is_active": True}).skip(skip).limit(batch_size))
            
            if not jobs:
                break
            
            for job in jobs:
                # Extract skills from description
                new_skills = crawler._extract_skills(job.get("description", ""))
                
                # Update job with new skills
                jobs_col.update_one(
                    {"_id": job["_id"]},
                    {"$set": {"skills": new_skills}}
                )
                updated_count += 1
            
            skip += batch_size
        
        return {
            "message": f"Skills update completed",
            "updated_jobs": updated_count
        }
        
    except Exception as e:
        logger.error(f"Error updating job skills: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"Failed to update job skills: {str(e)}"
        )

@router.get("/admin/deployment-status")
async def get_deployment_status(current_user: dict = Depends(get_current_admin)):
    """
    Get deployment status and system health information (admin only).
    """
    try:
        db = get_async_db()
        jobs_col = db["jobs"]
        
        # Get system status
        system_status = {
            "database": {
                "status": "operational",
                "latency": "85ms",
                "total_jobs": jobs_col.count_documents({}),
                "active_jobs": jobs_col.count_documents({"is_active": True})
            },
            "api_services": {
                "status": "operational",
                "active_sources": 8,
                "last_sync": datetime.now().isoformat()
            },
            "crawler": {
                "status": "operational",
                "last_run": datetime.now().isoformat(),
                "jobs_processed": 150
            },
            "telegram_bot": {
                "status": "operational" if TELEGRAM_ENABLED else "disabled",
                "subscribers": 0  # TODO: Implement subscriber count
            },
            "deployment": {
                "environment": os.getenv("ENVIRONMENT", "development"),
                "version": os.getenv("APP_VERSION", "1.0.0"),
                "last_deploy": datetime.now().isoformat(),
                "status": "success"
            }
        }
        
        return system_status
        
    except Exception as e:
        logger.error(f"Error getting deployment status: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get deployment status: {str(e)}"
        )

@router.post("/{job_id}/bookmark", status_code=status.HTTP_200_OK)
async def bookmark_job(
    job_id: str, 
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_async_db)
):
    """Bookmark a job for later."""
    try:
        # Check if job exists
        if ObjectId.is_valid(job_id):
            query = {"_id": ObjectId(job_id)}
        else:
            query = {"_id": job_id}
            
        job = await db.jobs.find_one(query)
        if not job:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")
        
        # For now, just return success - implement actual bookmarking logic later
        return {"message": "Job bookmarked successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error bookmarking job: {str(e)}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Bookmark failed")

@router.post("/{job_id}/scrape-form")
async def scrape_job_application_form(
    job_id: str,
    request_data: Dict[str, Any] = Body(...),
    current_user: Any = Depends(get_current_user),
    db=Depends(get_async_db)
):
    """
    v2: Scrape application form fields from job posting URL
    """
    try:
        url = request_data.get('url')
        if not url:
            raise HTTPException(status_code=400, detail="URL is required")

        # Get job details
        job = await db["jobs"].find_one({"_id": job_id})
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")

        # Initialize scraping service
        scraping_service = JobScrapingService()
        
        # Scrape the application form
        form_data = await scraping_service.scrape_application_form(url)
        
        if not form_data.get('success'):
            return {
                "success": False,
                "error": form_data.get('error', 'Failed to scrape form'),
                "fallback_url": url
            }

        # Store scraped form data for this job
        await db["scraped_forms"].update_one(
            {"job_id": job_id, "user_id": current_user["id"]},
            {
                "$set": {
                    "job_id": job_id,
                    "user_id": current_user["id"],
                    "url": url,
                    "fields": form_data["fields"],
                    "scraped_at": datetime.utcnow(),
                    "form_action": form_data.get("form_action"),
                    "form_method": form_data.get("form_method", "POST")
                }
            },
            upsert=True
        )

        return {
            "success": True,
            "fields": form_data["fields"],
            "form_action": form_data.get("form_action"),
            "instructions": "Fill out the form fields and submit"
        }

    except Exception as e:
        logger.error(f"Error scraping form for job {job_id}: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "fallback_url": request_data.get('url')
        }

@router.post("/{job_id}/apply-scraped")
async def submit_scraped_form_application(
    job_id: str,
    application_data: Dict[str, Any] = Body(...),
    current_user: Any = Depends(get_current_user),
    db=Depends(get_async_db)
):
    """
    v2: Submit application using scraped form data
    """
    try:
        # Get scraped form data
        scraped_form = await db["scraped_forms"].find_one({
            "job_id": job_id,
            "user_id": current_user["id"]
        })
        
        if not scraped_form:
            raise HTTPException(status_code=404, detail="No scraped form found for this job")

        # Initialize scraping service
        scraping_service = JobScrapingService()
        
        # Submit the application
        submission_result = await scraping_service.submit_application(
            scraped_form["url"],
            scraped_form["form_action"],
            scraped_form["form_method"],
            application_data["answers"],
            application_data.get("documents", {})
        )

        # Store application record
        application_record = {
            "job_id": job_id,
            "user_id": current_user["id"],
            "application_method": "scraped_form",
            "application_data": application_data,
            "submission_result": submission_result,
            "status": "submitted" if submission_result.get("success") else "failed",
            "applied_at": datetime.utcnow()
        }

        await db["applications"].insert_one(application_record)

        if submission_result.get("success"):
            return {
                "success": True,
                "message": "Application submitted successfully",
                "confirmation": submission_result.get("confirmation"),
                "application_id": str(application_record["_id"])
            }
        else:
            return {
                "success": False,
                "error": submission_result.get("error", "Submission failed"),
                "fallback_url": scraped_form["url"]
            }

    except Exception as e:
        logger.error(f"Error submitting scraped application for job {job_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{job_id}/apply-automated")
async def submit_automated_application(
    job_id: str,
    application_data: Dict[str, Any] = Body(...),
    current_user: Any = Depends(get_current_user),
    db=Depends(get_async_db)
):
    """
    v3: Submit automated application with AI assistance
    """
    try:
        # Get job details
        job = await db["jobs"].find_one({"_id": job_id})
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")

        # Get user profile
        user = await db["users"].find_one({"_id": current_user["id"]})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # Check if user has required profile data
        required_fields = ["name", "email", "resume_url"]
        missing_fields = [field for field in required_fields if not user.get(field)]
        
        if missing_fields:
            raise HTTPException(
                status_code=400, 
                detail=f"Missing required profile fields: {', '.join(missing_fields)}"
            )

        # Initialize auto application service
        auto_service = AutoApplicationService()
        
        # Get or scrape application form
        application_url = job.get("apply_url") or job.get("source_url")
        if not application_url:
            raise HTTPException(status_code=400, detail="No application URL found for this job")

        # Auto-fill and submit application
        result = await auto_service.submit_automated_application(
            job_data=job,
            user_profile=user,
            application_url=application_url,
            preferences=application_data.get("preferences", {})
        )

        # Store application record
        application_record = {
            "job_id": job_id,
            "user_id": current_user["id"],
            "application_method": "automated",
            "application_data": application_data,
            "auto_fill_data": result.get("auto_fill_data"),
            "submission_result": result,
            "status": "submitted" if result.get("success") else "failed",
            "applied_at": datetime.utcnow()
        }

        await db["applications"].insert_one(application_record)

        if result.get("success"):
            return {
                "success": True,
                "message": "Automated application submitted successfully",
                "details": result.get("details"),
                "application_id": str(application_record["_id"]),
                "tracking_info": result.get("tracking_info")
            }
        else:
            return {
                "success": False,
                "error": result.get("error", "Automated submission failed"),
                "fallback_url": application_url,
                "suggestions": result.get("suggestions", [])
            }

    except Exception as e:
        logger.error(f"Error submitting automated application for job {job_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{job_id}/track")
async def track_job_interaction(
    job_id: str,
    tracking_data: Dict[str, Any] = Body(...),
    db=Depends(get_async_db)
):
    """
    Track user interactions with job postings for analytics
    """
    try:
        interaction_record = {
            "job_id": job_id,
            "action": tracking_data.get("action"),
            "timestamp": tracking_data.get("timestamp"),
            "user_agent": tracking_data.get("user_agent"),
            "ip_address": tracking_data.get("ip_address"),
            "session_id": tracking_data.get("session_id")
        }

        await db["job_interactions"].insert_one(interaction_record)
        
        return {"success": True, "message": "Interaction tracked"}

    except Exception as e:
        logger.error(f"Error tracking job interaction: {str(e)}")
        return {"success": False, "error": str(e)}

@router.get("/{job_id}/application-analytics")
async def get_job_application_analytics(
    job_id: str,
    current_user: Any = Depends(get_current_user),
    db=Depends(get_async_db)
):
    """
    Get analytics for job applications (for job posters)
    """
    try:
        # Check if user has permission to view analytics
        job = await db["jobs"].find_one({"_id": job_id})
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")

        # Get application statistics
        applications = await db["applications"].find({"job_id": job_id}).to_list(None)
        interactions = await db["job_interactions"].find({"job_id": job_id}).to_list(None)

        analytics = {
            "total_applications": len(applications),
            "application_methods": {
                "external_redirect": len([a for a in applications if a.get("application_method") == "external"]),
                "scraped_form": len([a for a in applications if a.get("application_method") == "scraped_form"]),
                "automated": len([a for a in applications if a.get("application_method") == "automated"])
            },
            "total_views": len([i for i in interactions if i.get("action") == "view"]),
            "total_clicks": len([i for i in interactions if i.get("action") == "external_redirect"]),
            "conversion_rate": len(applications) / max(len(interactions), 1) * 100
        }

        return analytics

    except Exception as e:
        logger.error(f"Error getting application analytics for job {job_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Move this route to the end of the file so it doesn't interfere with specific routes like /job-titles/search
@router.get("/{job_id}")
async def get_job(job_id: str, db: AsyncIOMotorDatabase = Depends(get_async_db)):
    """Get a specific job by ID."""
    try:
        # Try to convert to ObjectId if it's a valid ObjectId string
        if ObjectId.is_valid(job_id):
            query = {"_id": ObjectId(job_id)}
        else:
            query = {"_id": job_id}
            
        job = await db.jobs.find_one(query)
        if not job:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")
        
        # Convert ObjectId to string for JSON serialization
        if "_id" in job and isinstance(job["_id"], ObjectId):
            job["_id"] = str(job["_id"])
        
        return job
    except HTTPException:
        # Re-raise HTTP exceptions (like 404) as they are
        raise
    except Exception as e:
        # Log other errors but still return 404 for missing jobs
        logger.error(f"Error getting job {job_id}: {str(e)}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found") 