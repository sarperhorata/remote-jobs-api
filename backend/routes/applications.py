from fastapi import APIRouter, HTTPException, Depends, status, Query
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
import uuid
from fastapi.security import HTTPBearer

from ..database.db import get_async_db
from ..routes.auth import get_current_user_dependency
from bson import ObjectId
import logging

from ..models.user_application import (
    UserApplicationCreate, 
    UserApplicationUpdate, 
    UserApplicationResponse
)
from ..services.user_application_service import get_user_application_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/applications", tags=["applications"])
security = HTTPBearer()

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

@router.post("/apply", 
    response_model=UserApplicationResponse,
    summary="Apply to a job",
    description="Submit a job application for the authenticated user",
    responses={
        200: {
            "description": "Application submitted successfully",
            "content": {
                "application/json": {
                    "example": {
                        "id": "app_123",
                        "user_id": "user_456", 
                        "job_id": "job_789",
                        "status": "applied",
                        "application_type": "external",
                        "applied_at": "2024-01-15T10:30:00Z"
                    }
                }
            }
        },
        400: {"description": "Already applied to this job or invalid data"},
        401: {"description": "Authentication required"},
        404: {"description": "Job not found"},
        500: {"description": "Server error"}
    }
)
async def apply_to_job(
    application_data: UserApplicationCreate,
    current_user: dict = Depends(get_current_user_dependency)
):
    """
    Apply to a job posting
    
    This endpoint allows authenticated users to submit job applications.
    
    **Requirements:**
    - User must be authenticated
    - Job must exist
    - User cannot apply to the same job twice
    
    **Application Types:**
    - `external`: Direct application through company website
    - `scraped`: Application through scraped form data
    - `automated`: Automated application using AI
    """
    try:
        # Set user_id from current user
        application_data.user_id = current_user["_id"]
        
        # Get service instance
        service = get_user_application_service()
        
        # Check if already applied
        existing = await service.get_user_application(
            user_id=current_user["_id"],
            job_id=application_data.job_id
        )
        
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You have already applied to this job"
            )
        
        application = await service.create_application(application_data)
        logger.info(f"User {current_user['_id']} applied to job {application_data.job_id}")
        
        return application
        
    except Exception as e:
        logger.error(f"Error applying to job: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to apply to job"
        )

@router.get("/my-applications", 
    response_model=List[UserApplicationResponse],
    summary="Get user's applications",
    description="Retrieve all job applications submitted by the authenticated user",
    responses={
        200: {
            "description": "List of user applications",
            "content": {
                "application/json": {
                    "example": [
                        {
                            "id": "app_123",
                            "user_id": "user_456",
                            "job_id": "job_789", 
                            "status": "applied",
                            "application_type": "external",
                            "applied_at": "2024-01-15T10:30:00Z"
                        }
                    ]
                }
            }
        },
        401: {"description": "Authentication required"},
        500: {"description": "Server error"}
    }
)
async def get_my_applications(
    current_user: dict = Depends(get_current_user_dependency),
    skip: int = Query(0, description="Number of applications to skip for pagination"),
    limit: int = Query(100, description="Maximum number of applications to return"),
    status_filter: Optional[str] = Query(None, description="Filter by application status (applied, viewed, rejected, hired, withdrawn)")
):
    """
    Get current user's job applications
    
    Returns a paginated list of job applications submitted by the authenticated user.
    
    **Query Parameters:**
    - `skip`: Number of records to skip (for pagination)
    - `limit`: Maximum number of records to return (default: 100)
    - `status_filter`: Filter applications by status
    
    **Status Values:**
    - `applied`: Application submitted
    - `viewed`: Application viewed by company
    - `rejected`: Application rejected
    - `hired`: Application successful
    - `withdrawn`: Application withdrawn by user
    """
    try:
        service = get_user_application_service()
        applications = await service.get_user_applications(
            user_id=current_user["_id"],
            skip=skip,
            limit=limit,
            status_filter=status_filter
        )
        return applications
        
    except Exception as e:
        logger.error(f"Error fetching user applications: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch applications"
        )

@router.get("/applied-jobs", 
    response_model=List[str],
    summary="Get applied job IDs",
    description="Get list of job IDs that the user has applied to",
    responses={
        200: {
            "description": "List of job IDs",
            "content": {
                "application/json": {
                    "example": ["job_123", "job_456", "job_789"]
                }
            }
        },
        401: {"description": "Authentication required"},
        500: {"description": "Server error"}
    }
)
async def get_applied_job_ids(
    current_user: dict = Depends(get_current_user_dependency)
):
    """
    Get list of job IDs that current user has applied to
    
    This endpoint returns a simple list of job IDs that the authenticated user
    has submitted applications for. Useful for checking application status
    in job listings.
    """
    try:
        service = get_user_application_service()
        job_ids = await service.get_applied_job_ids(
            user_id=current_user["_id"]
        )
        return job_ids
        
    except Exception as e:
        logger.error(f"Error fetching applied job IDs: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch applied jobs"
        )

@router.get("/check-applied/{job_id}",
    summary="Check application status",
    description="Check if user has applied to a specific job",
    responses={
        200: {
            "description": "Application status information",
            "content": {
                "application/json": {
                    "example": {
                        "applied": True,
                        "application_id": "app_123",
                        "applied_at": "2024-01-15T10:30:00Z",
                        "status": "applied"
                    }
                }
            }
        },
        401: {"description": "Authentication required"},
        500: {"description": "Server error"}
    }
)
async def check_if_applied(
    job_id: str,
    current_user: dict = Depends(get_current_user_dependency)
):
    """
    Check if user has already applied to a specific job
    
    Returns application status information for a specific job:
    - Whether the user has applied
    - Application ID if exists
    - Application date if exists  
    - Current application status if exists
    """
    try:
        service = get_user_application_service()
        application = await service.get_user_application(
            user_id=current_user["_id"],
            job_id=job_id
        )
        
        return {
            "applied": application is not None,
            "application_id": str(application.id) if application else None,
            "applied_at": application.applied_at if application else None,
            "status": application.status if application else None
        }
        
    except Exception as e:
        logger.error(f"Error checking application status: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to check application status"
        )

@router.get("/{application_id}", 
    response_model=dict,
    summary="Get application details",
    description="Get detailed information about a specific application",
    responses={
        200: {
            "description": "Application details with job information",
            "content": {
                "application/json": {
                    "example": {
                        "application": {
                            "id": "app_123",
                            "user_id": "user_456",
                            "job_id": "job_789",
                            "status": "applied",
                            "application_type": "external",
                            "cover_letter": "Dear hiring manager...",
                            "applied_at": "2024-01-15T10:30:00Z",
                            "job": {
                                "title": "Senior Developer",
                                "company": "Tech Corp",
                                "location": "Remote"
                            }
                        }
                    }
                }
            }
        },
        401: {"description": "Authentication required"},
        404: {"description": "Application not found"},
        500: {"description": "Server error"}
    }
)
async def get_application(
    application_id: str,
    db=Depends(get_async_db),
    current_user: dict = Depends(get_current_user_dependency)
):
    """
    Get specific application details
    
    Returns detailed information about a specific job application including:
    - Complete application data
    - Associated job information
    - Company response information if available
    
    **Note:** Users can only access their own applications.
    """
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

@router.get("/stats",
    response_model=dict,
    summary="Get application statistics",
    description="Get comprehensive statistics about user's job applications",
    responses={
        200: {
            "description": "Application statistics",
            "content": {
                "application/json": {
                    "example": {
                        "total_applications": 25,
                        "status_breakdown": {
                            "applied": 15,
                            "viewed": 8,
                            "rejected": 2,
                            "hired": 0,
                            "withdrawn": 0
                        },
                        "type_breakdown": {
                            "external": 20,
                            "scraped": 3,
                            "automated": 2
                        },
                        "recent_applications": 5,
                        "response_rate": 40.0,
                        "responded_applications": 10
                    }
                }
            }
        },
        401: {"description": "Authentication required"},
        500: {"description": "Server error"}
    }
)
async def get_application_stats(
    db=Depends(get_async_db),
    current_user: dict = Depends(get_current_user_dependency)
):
    """
    Get user's application statistics
    
    Returns comprehensive statistics about the user's job applications including:
    
    **Metrics:**
    - `total_applications`: Total number of applications submitted
    - `status_breakdown`: Count of applications by status
    - `type_breakdown`: Count of applications by type 
    - `recent_applications`: Applications submitted in last 7 days
    - `response_rate`: Percentage of applications with company responses
    - `responded_applications`: Number of applications with company responses
    
    **Status Categories:**
    - `applied`: Newly submitted applications
    - `viewed`: Applications viewed by companies
    - `rejected`: Rejected applications
    - `hired`: Successful applications
    - `withdrawn`: User-withdrawn applications
    
    **Application Types:**
    - `external`: Manual applications through company websites
    - `scraped`: Applications using scraped form data
    - `automated`: AI-assisted automated applications
    """
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

@router.put("/applications/{application_id}", response_model=UserApplicationResponse)
async def update_application(
    application_id: str,
    update_data: UserApplicationUpdate,
    current_user: dict = Depends(get_current_user_dependency)
):
    """Update a job application"""
    try:
        # Verify application belongs to user
        service = get_user_application_service()
        application = await service.get_application_by_id(application_id)
        if not application or application.user_id != current_user["_id"]:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Application not found"
            )
        
        updated_application = await service.update_application(
            application_id, update_data
        )
        return updated_application
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating application: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update application"
        )

@router.delete("/applications/{application_id}")
async def delete_application(
    application_id: str,
    current_user: dict = Depends(get_current_user_dependency)
):
    """Delete a job application"""
    try:
        # Verify application belongs to user
        service = get_user_application_service()
        application = await service.get_application_by_id(application_id)
        if not application or application.user_id != current_user["_id"]:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Application not found"
            )
        
        await service.delete_application(application_id)
        return {"message": "Application deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting application: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete application"
        ) 