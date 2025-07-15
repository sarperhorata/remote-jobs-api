from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from typing import Dict, Any, Optional
import logging
from datetime import datetime

from services.linkedin_job_service import LinkedInJobService
from database.db import get_async_db
import crud.job as job_crud

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/linkedin", tags=["LinkedIn Jobs"])

@router.post("/jobs/crawl")
async def crawl_linkedin_jobs(
    keywords: str = "remote",
    location: str = "",
    limit: int = 100,
    background_tasks: BackgroundTasks = None
):
    """
    LinkedIn'den iş ilanlarını çek ve veritabanına kaydet
    """
    try:
        linkedin_service = LinkedInJobService()
        
        # Background task olarak çalıştır
        if background_tasks:
            background_tasks.add_task(
                linkedin_service.crawl_linkedin_jobs,
                keywords=keywords,
                location=location,
                limit=limit
            )
            return {
                "message": "LinkedIn job crawling started in background",
                "status": "started",
                "keywords": keywords,
                "location": location,
                "limit": limit
            }
        else:
            # Direkt çalıştır
            result = await linkedin_service.crawl_linkedin_jobs(
                keywords=keywords,
                location=location,
                limit=limit
            )
            return result
            
    except Exception as e:
        logger.error(f"LinkedIn job crawling error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/jobs/status")
async def get_linkedin_job_status():
    """
    LinkedIn iş ilanlarının durumunu getir
    """
    try:
        linkedin_service = LinkedInJobService()
        stats = await linkedin_service.get_linkedin_job_statistics()
        
        return {
            "status": "active",
            "last_updated": datetime.utcnow().isoformat(),
            "statistics": stats
        }
        
    except Exception as e:
        logger.error(f"LinkedIn job status error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/jobs/search")
async def search_linkedin_jobs(
    query: str = "",
    location: str = "",
    job_type: str = "",
    experience_level: str = "",
    limit: int = 20,
    offset: int = 0,
    db = Depends(get_async_db)
):
    """
    LinkedIn iş ilanlarında arama yap
    """
    try:
        # Database'den LinkedIn kaynaklı iş ilanlarını getir
        filters = {
            "source": "linkedin",
            "is_active": True
        }
        
        if query:
            filters["$or"] = [
                {"title": {"$regex": query, "$options": "i"}},
                {"description": {"$regex": query, "$options": "i"}},
                {"company": {"$regex": query, "$options": "i"}}
            ]
            
        if location:
            filters["location"] = {"$regex": location, "$options": "i"}
            
        if job_type:
            filters["job_type"] = job_type
            
        if experience_level:
            filters["experience_level"] = experience_level
        
        jobs = await job_crud.get_jobs_with_filters(
            db=db, 
            filters=filters,
            limit=limit,
            offset=offset
        )
        
        return {
            "jobs": jobs,
            "total": len(jobs),
            "filters_applied": filters,
            "pagination": {
                "limit": limit,
                "offset": offset
            }
        }
        
    except Exception as e:
        logger.error(f"LinkedIn job search error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/companies")
async def get_linkedin_companies(
    limit: int = 50,
    db = Depends(get_async_db)
):
    """
    LinkedIn'den çekilen şirketleri listele
    """
    try:
        companies = await job_crud.get_companies_by_source(
            db=db,
            source="linkedin",
            limit=limit
        )
        
        return {
            "companies": companies,
            "total": len(companies),
            "source": "linkedin"
        }
        
    except Exception as e:
        logger.error(f"LinkedIn companies error: {e}")
        raise HTTPException(status_code=500, detail=str(e)) 