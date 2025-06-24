from fastapi import APIRouter, HTTPException, Depends, status, Query
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, timedelta
import uuid

from ..database import get_async_db
from ..routes.auth import get_current_user_dependency
from bson import ObjectId
import logging

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/applications", tags=["applications"])

# Pydantic models
class JobApplicationCreate(BaseModel):
    job_id: str
    application_type: str = "external"  # external, scraped, automated
    cover_letter: Optional[str] = None
    resume_url: Optional[str] = None
    additional_notes: Optional[str] = None
    form_data: Optional[dict] = None
    external_url: Optional[str] = None
    external_reference: Optional[str] = None

class JobApplicationUpdate(BaseModel):
    status: Optional[str] = None
    additional_notes: Optional[str] = None
    external_reference: Optional[str] = None
    company_response: Optional[str] = None

class JobApplicationResponse(BaseModel):
    id: str
    user_id: str
    job_id: str
    status: str
    application_type: str
    cover_letter: Optional[str] = None
    resume_url: Optional[str] = None
    additional_notes: Optional[str] = None
    form_data: Optional[dict] = None
    external_url: Optional[str] = None
    external_reference: Optional[str] = None
    applied_at: datetime
    updated_at: datetime
    viewed_by_company: bool = False
    company_response_date: Optional[datetime] = None
    company_response: Optional[str] = None

@router.post("/apply", response_model=dict)
async def apply_to_job(
    application_data: JobApplicationCreate,
    db=Depends(get_async_db),
    current_user: dict = Depends(get_current_user_dependency)
):
    """Apply to a job"""
    try:
        current_user_id = current_user["_id"]
        
        # Check if user already applied to this job
        existing_application = await db.job_applications.find_one({
            "user_id": current_user_id,
            "job_id": application_data.job_id
        })
        
        if existing_application:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You have already applied to this job"
            )
            
        # Verify job exists
        job = await db.jobs.find_one({"_id": ObjectId(application_data.job_id)})
        if not job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Job not found"
            )
            
        # Create new application
        application_id = str(uuid.uuid4())
        application_doc = {
            "_id": application_id,
            "user_id": current_user_id,
            "job_id": application_data.job_id,
            "application_type": application_data.application_type,
            "cover_letter": application_data.cover_letter,
            "resume_url": application_data.resume_url,
            "additional_notes": application_data.additional_notes,
            "form_data": application_data.form_data,
            "external_url": application_data.external_url,
            "external_reference": application_data.external_reference,
            "status": "applied",
            "applied_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "viewed_by_company": False,
            "company_response_date": None,
            "company_response": None
        }
        
        result = await db.job_applications.insert_one(application_doc)
        
        return {
            "message": "Application submitted successfully",
            "application_id": application_id,
            "status": "applied"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error applying to job: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to submit application"
        )

@router.get("/my-applications", response_model=dict)
async def get_my_applications(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    status_filter: Optional[str] = Query(None),
    db=Depends(get_async_db),
    current_user: dict = Depends(get_current_user_dependency)
):
    """Get current user's job applications"""
    try:
        current_user_id = current_user["_id"]
        
        # Build query
        query = {"user_id": current_user_id}
        
        if status_filter:
            query["status"] = status_filter
            
        # Get total count
        total = await db.job_applications.count_documents(query)
        
        # Apply pagination and ordering
        skip = (page - 1) * per_page
        applications_cursor = db.job_applications.find(query).sort("applied_at", -1).skip(skip).limit(per_page)
        
        applications = []
        async for app in applications_cursor:
            # Get job details
            job = await db.jobs.find_one({"_id": ObjectId(app["job_id"])})
            
            app_dict = {
                "id": app["_id"],
                "user_id": app["user_id"],
                "job_id": app["job_id"],
                "status": app["status"],
                "application_type": app["application_type"],
                "cover_letter": app.get("cover_letter"),
                "resume_url": app.get("resume_url"),
                "additional_notes": app.get("additional_notes"),
                "form_data": app.get("form_data"),
                "external_url": app.get("external_url"),
                "external_reference": app.get("external_reference"),
                "applied_at": app["applied_at"].isoformat(),
                "updated_at": app["updated_at"].isoformat(),
                "viewed_by_company": app.get("viewed_by_company", False),
                "company_response_date": app.get("company_response_date").isoformat() if app.get("company_response_date") else None,
                "company_response": app.get("company_response"),
                "job": {
                    "title": job.get("title", "Unknown"),
                    "company": job.get("company", "Unknown"),
                    "location": job.get("location", "Unknown"),
                    "jobType": job.get("jobType", "Unknown")
                } if job else None
            }
            applications.append(app_dict)
        
        return {
            "applications": applications,
            "total": total,
            "page": page,
            "per_page": per_page,
            "pages": (total + per_page - 1) // per_page
        }
        
    except Exception as e:
        logger.error(f"Error fetching user applications: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch applications"
        )

@router.get("/check-applied/{job_id}", response_model=dict)
async def check_if_applied(
    job_id: str,
    db=Depends(get_async_db),
    current_user: dict = Depends(get_current_user_dependency)
):
    """Check if user has applied to a specific job"""
    try:
        current_user_id = current_user["_id"]
        
        application = await db.job_applications.find_one({
            "user_id": current_user_id,
            "job_id": job_id
        })
        
        application_data = None
        if application:
            application_data = {
                "id": application["_id"],
                "status": application["status"],
                "applied_at": application["applied_at"].isoformat(),
                "application_type": application["application_type"]
            }
        
        return {
            "has_applied": application is not None,
            "application": application_data
        }
        
    except Exception as e:
        logger.error(f"Error checking application status: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to check application status"
        )

@router.get("/applied-jobs", response_model=dict)
async def get_applied_job_ids(
    db=Depends(get_async_db),
    current_user: dict = Depends(get_current_user_dependency)
):
    """Get list of job IDs user has applied to"""
    try:
        current_user_id = current_user["_id"]
        
        applications_cursor = db.job_applications.find(
            {"user_id": current_user_id},
            {"job_id": 1}
        )
        
        job_ids = []
        async for app in applications_cursor:
            job_ids.append(app["job_id"])
        
        return {
            "applied_job_ids": job_ids,
            "count": len(job_ids)
        }
        
    except Exception as e:
        logger.error(f"Error fetching applied job IDs: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch applied jobs"
        )

@router.get("/{application_id}", response_model=dict)
async def get_application(
    application_id: str,
    db=Depends(get_async_db),
    current_user: dict = Depends(get_current_user_dependency)
):
    """Get specific application details"""
    try:
        current_user_id = current_user["_id"]
        
        application = await db.job_applications.find_one({
            "_id": application_id,
            "user_id": current_user_id
        })
        
        if not application:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Application not found"
            )
        
        # Get job details
        job = await db.jobs.find_one({"_id": ObjectId(application["job_id"])})
        
        application_data = {
            "id": application["_id"],
            "user_id": application["user_id"],
            "job_id": application["job_id"],
            "status": application["status"],
            "application_type": application["application_type"],
            "cover_letter": application.get("cover_letter"),
            "resume_url": application.get("resume_url"),
            "additional_notes": application.get("additional_notes"),
            "form_data": application.get("form_data"),
            "external_url": application.get("external_url"),
            "external_reference": application.get("external_reference"),
            "applied_at": application["applied_at"].isoformat(),
            "updated_at": application["updated_at"].isoformat(),
            "viewed_by_company": application.get("viewed_by_company", False),
            "company_response_date": application.get("company_response_date").isoformat() if application.get("company_response_date") else None,
            "company_response": application.get("company_response"),
            "job": {
                "title": job.get("title", "Unknown"),
                "company": job.get("company", "Unknown"),
                "location": job.get("location", "Unknown"),
                "jobType": job.get("jobType", "Unknown")
            } if job else None
        }
        
        return {"application": application_data}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching application: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch application"
        )

@router.put("/{application_id}", response_model=dict)
async def update_application(
    application_id: str,
    update_data: JobApplicationUpdate,
    db=Depends(get_async_db),
    current_user: dict = Depends(get_current_user_dependency)
):
    """Update application status or details"""
    try:
        current_user_id = current_user["_id"]
        
        application = await db.job_applications.find_one({
            "_id": application_id,
            "user_id": current_user_id
        })
        
        if not application:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Application not found"
            )
        
        # Build update document
        update_doc = {"updated_at": datetime.utcnow()}
        
        if update_data.status is not None:
            update_doc["status"] = update_data.status
        if update_data.additional_notes is not None:
            update_doc["additional_notes"] = update_data.additional_notes
        if update_data.external_reference is not None:
            update_doc["external_reference"] = update_data.external_reference
        if update_data.company_response is not None:
            update_doc["company_response"] = update_data.company_response
            update_doc["company_response_date"] = datetime.utcnow()
        
        # Update the application
        result = await db.job_applications.update_one(
            {"_id": application_id, "user_id": current_user_id},
            {"$set": update_doc}
        )
        
        if result.modified_count == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No changes made to application"
            )
        
        return {
            "message": "Application updated successfully",
            "application_id": application_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating application: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update application"
        )

@router.delete("/{application_id}", response_model=dict)
async def withdraw_application(
    application_id: str,
    db=Depends(get_async_db),
    current_user: dict = Depends(get_current_user_dependency)
):
    """Withdraw/delete an application"""
    try:
        current_user_id = current_user["_id"]
        
        application = await db.job_applications.find_one({
            "_id": application_id,
            "user_id": current_user_id
        })
        
        if not application:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Application not found"
            )
        
        # Mark as withdrawn instead of deleting
        result = await db.job_applications.update_one(
            {"_id": application_id, "user_id": current_user_id},
            {"$set": {"status": "withdrawn", "updated_at": datetime.utcnow()}}
        )
        
        return {"message": "Application withdrawn successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error withdrawing application: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to withdraw application"
        )

@router.get("/stats", response_model=dict)
async def get_application_stats(
    db=Depends(get_async_db),
    current_user: dict = Depends(get_current_user_dependency)
):
    """Get user's application statistics"""
    try:
        current_user_id = current_user["_id"]
        
        # Total applications
        total_applications = await db.job_applications.count_documents({
            "user_id": current_user_id
        })
        
        # Applications by status
        status_counts = {}
        statuses = ['applied', 'viewed', 'rejected', 'hired', 'withdrawn']
        
        for app_status in statuses:
            count = await db.job_applications.count_documents({
                "user_id": current_user_id,
                "status": app_status
            })
            status_counts[app_status] = count
            
        # Applications by type
        type_counts = {}
        types = ['external', 'scraped', 'automated']
        
        for app_type in types:
            count = await db.job_applications.count_documents({
                "user_id": current_user_id,
                "application_type": app_type
            })
            type_counts[app_type] = count
            
        # Recent applications (last 7 days)
        week_ago = datetime.utcnow() - timedelta(days=7)
        recent_applications = await db.job_applications.count_documents({
            "user_id": current_user_id,
            "applied_at": {"$gte": week_ago}
        })
        
        # Response rate (applications with company response)
        responded_applications = await db.job_applications.count_documents({
            "user_id": current_user_id,
            "company_response": {"$ne": None}
        })
        
        response_rate = (responded_applications / total_applications * 100) if total_applications > 0 else 0
        
        return {
            "total_applications": total_applications,
            "status_breakdown": status_counts,
            "type_breakdown": type_counts,
            "recent_applications": recent_applications,
            "response_rate": round(response_rate, 2),
            "responded_applications": responded_applications
        }
        
    except Exception as e:
        logger.error(f"Error fetching application stats: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch application statistics"
        ) 