from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks, status, Query
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase

from ..database.db import get_async_db
from ..services.translation_service import translation_service
from ..utils.auth import get_current_user
from ..schemas.user import User
from ..database.db import get_db

# Translation schemas - defined inline for now
class TranslationRequest(BaseModel):
    text: str
    target_language: str = "en"
    source_language: Optional[str] = None

class TranslationResponse(BaseModel):
    translated_text: str
    original_text: str
    source_language: str
    target_language: str
    translation_confidence: float

class JobTranslationResult(BaseModel):
    job_id: str
    needs_translation: bool
    original_language: str
    translated_data: Optional[Dict[str, Any]] = None
    original_data: Optional[Dict[str, Any]] = None
    translation_metadata: Optional[Dict[str, Any]] = None

class BatchTranslationRequest(BaseModel):
    job_ids: List[str]
    target_language: str = "en"
    batch_size: int = 10

class BatchTranslationResponse(BaseModel):
    total_jobs: int
    translated_jobs: int
    failed_jobs: int
    results: List[JobTranslationResult]
    errors: List[str]

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/translation", tags=["translation"])

@router.post("/translate-text", response_model=TranslationResponse)
async def translate_text(
    request: TranslationRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Translate individual text to target language
    """
    try:
        result = await translation_service.translate_text(
            text=request.text,
            target_lang=request.target_language,
            source_lang=request.source_language
        )
        
        return TranslationResponse(**result)
        
    except Exception as e:
        logger.error(f"Error translating text: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Translation failed: {str(e)}"
        )

@router.post("/detect-language")
async def detect_language(
    text: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Detect the language of given text
    """
    try:
        language, confidence = await translation_service.detect_language(text)
        
        return {
            "detected_language": language,
            "confidence": confidence,
            "language_name": translation_service.supported_languages.get(language, "Unknown")
        }
        
    except Exception as e:
        logger.error(f"Error detecting language: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Language detection failed: {str(e)}"
        )

@router.get("/supported-languages")
async def get_supported_languages():
    """
    Get list of supported languages for translation
    """
    try:
        languages = translation_service.get_supported_languages()
        
        return {
            "success": True,
            "supported_languages": languages,
            "total_languages": len(languages)
        }
        
    except Exception as e:
        logger.error(f"Error fetching supported languages: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch supported languages"
        )

@router.post("/translate-job/{job_id}", response_model=JobTranslationResult)
async def translate_job_listing(
    job_id: str,
    target_language: str = "en",
    current_user: User = Depends(get_current_user)
):
    """Translate a specific job listing"""
    try:
        db = get_db()
        
        # Fetch job from database
        job = await db.jobs.find_one({"_id": ObjectId(job_id)})
        if not job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Job not found"
            )
        
        # Check if job already has translation
        if job.get("translated_data") and job.get("original_language"):
            return {
                "success": True,
                "job_id": job_id,
                "already_translated": True,
                "original_language": job.get("original_language"),
                "translated_data": job.get("translated_data"),
                "original_data": job.get("original_data")
            }
        
        # Translate the job
        translation_result = await translation_service.translate_job_listing(job)
        
        if translation_result["needs_translation"]:
            # Update job in database with translation
            update_doc = {
                "translated_data": translation_result["translated_data"],
                "original_data": translation_result["original_data"],
                "original_language": translation_result["original_language"],
                "translation_metadata": translation_result["translation_metadata"],
                "updated_at": translation_result["translation_metadata"]["translated_at"]
            }
            
            await db.jobs.update_one(
                {"_id": ObjectId(job_id)},
                {"$set": update_doc}
            )
            
            return {
                "success": True,
                "job_id": job_id,
                "translated": True,
                "original_language": translation_result["original_language"],
                "translated_data": translation_result["translated_data"],
                "translation_metadata": translation_result["translation_metadata"]
            }
        else:
            return {
                "success": True,
                "job_id": job_id,
                "translated": False,
                "message": "Job is already in English, no translation needed",
                "original_language": translation_result["original_language"]
            }
        
    except Exception as e:
        logger.error(f"Error translating job {job_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to translate job listing"
        )

@router.post("/batch-translate", response_model=BatchTranslationResponse)
async def batch_translate_jobs(
    job_ids: List[str],
    target_language: str = "en",
    batch_size: int = 10,
    current_user: User = Depends(get_current_user)
):
    """Translate multiple job listings in batch"""
    try:
        if len(job_ids) > 50:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Maximum 50 jobs can be translated at once"
            )
        
        db = get_db()
        
        # Fetch jobs from database
        jobs_cursor = db.jobs.find({"_id": {"$in": [ObjectId(jid) for jid in job_ids]}})
        jobs = []
        async for job in jobs_cursor:
            jobs.append(job)
        
        if not jobs:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No jobs found"
            )
        
        # Filter jobs that need translation
        jobs_to_translate = []
        already_translated = []
        
        for job in jobs:
            if job.get("translated_data") and job.get("original_language"):
                already_translated.append({
                    "job_id": str(job["_id"]),
                    "original_language": job["original_language"],
                    "status": "already_translated"
                })
            else:
                jobs_to_translate.append(job)
        
        # Translate jobs in batches
        translation_results = await translation_service.batch_translate_jobs(
            jobs_to_translate, 
            batch_size=batch_size
        )
        
        # Update database with translations
        translated_jobs = []
        for i, result in enumerate(translation_results):
            job = jobs_to_translate[i]
            job_id = str(job["_id"])
            
            if result.get("needs_translation"):
                # Update job in database
                update_doc = {
                    "translated_data": result["translated_data"],
                    "original_data": result["original_data"],
                    "original_language": result["original_language"],
                    "translation_metadata": result["translation_metadata"],
                    "updated_at": result["translation_metadata"]["translated_at"]
                }
                
                await db.jobs.update_one(
                    {"_id": ObjectId(job_id)},
                    {"$set": update_doc}
                )
                
                translated_jobs.append({
                    "job_id": job_id,
                    "original_language": result["original_language"],
                    "status": "translated",
                    "translation_quality": result["translation_metadata"].get("quality_score", 0)
                })
            else:
                translated_jobs.append({
                    "job_id": job_id,
                    "original_language": result["original_language"],
                    "status": "no_translation_needed"
                })
        
        return {
            "success": True,
            "total_jobs": len(job_ids),
            "jobs_found": len(jobs),
            "already_translated": len(already_translated),
            "newly_translated": len([j for j in translated_jobs if j["status"] == "translated"]),
            "no_translation_needed": len([j for j in translated_jobs if j["status"] == "no_translation_needed"]),
            "results": translated_jobs + already_translated
        }
        
    except Exception as e:
        logger.error(f"Error in batch translation: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to batch translate jobs"
        )

@router.get("/translation-stats")
async def get_translation_stats(
    db=Depends(get_async_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Get translation statistics for the platform
    """
    try:
        # Total jobs
        total_jobs = await db.jobs.count_documents({})
        
        # Translated jobs
        translated_jobs = await db.jobs.count_documents({"is_translated": True})
        
        # Jobs by original language
        pipeline = [
            {"$group": {
                "_id": "$original_language",
                "count": {"$sum": 1}
            }},
            {"$sort": {"count": -1}}
        ]
        
        language_stats = []
        async for result in db.jobs.aggregate(pipeline):
            language_name = translation_service.supported_languages.get(
                result["_id"], result["_id"]
            )
            language_stats.append({
                "language_code": result["_id"],
                "language_name": language_name,
                "job_count": result["count"]
            })
        
        # Translation success rate
        failed_translations = await db.jobs.count_documents({
            "translation_metadata.error": {"$exists": True}
        })
        
        success_rate = 0
        if translated_jobs > 0:
            success_rate = ((translated_jobs - failed_translations) / translated_jobs) * 100
        
        return {
            "total_jobs": total_jobs,
            "translated_jobs": translated_jobs,
            "untranslated_jobs": total_jobs - translated_jobs,
            "translation_percentage": (translated_jobs / total_jobs * 100) if total_jobs > 0 else 0,
            "success_rate": round(success_rate, 2),
            "failed_translations": failed_translations,
            "languages": language_stats,
            "supported_languages_count": len(translation_service.supported_languages)
        }
        
    except Exception as e:
        logger.error(f"Error fetching translation stats: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch translation statistics: {str(e)}"
        )

@router.post("/auto-translate-new-jobs")
async def auto_translate_new_jobs(
    max_jobs: int = Query(20, le=100, description="Maximum number of jobs to translate"),
    current_user: User = Depends(get_current_user)
):
    """Automatically detect and translate recently added non-English jobs"""
    try:
        db = get_db()
        
        # Find recent jobs without translation
        from datetime import datetime, timedelta
        recent_date = datetime.utcnow() - timedelta(days=7)  # Last 7 days
        
        query = {
            "created_at": {"$gte": recent_date},
            "translated_data": {"$exists": False}
        }
        
        jobs_cursor = db.jobs.find(query).limit(max_jobs)
        jobs = []
        async for job in jobs_cursor:
            jobs.append(job)
        
        if not jobs:
            return {
                "success": True,
                "message": "No new jobs requiring translation found",
                "processed": 0
            }
        
        # Translate jobs
        translation_results = await translation_service.batch_translate_jobs(jobs, batch_size=10)
        
        # Update database
        translated_count = 0
        for i, result in enumerate(translation_results):
            job = jobs[i]
            
            if result.get("needs_translation"):
                update_doc = {
                    "translated_data": result["translated_data"],
                    "original_data": result["original_data"], 
                    "original_language": result["original_language"],
                    "translation_metadata": result["translation_metadata"],
                    "updated_at": result["translation_metadata"]["translated_at"]
                }
                
                await db.jobs.update_one(
                    {"_id": job["_id"]},
                    {"$set": update_doc}
                )
                translated_count += 1
        
        return {
            "success": True,
            "message": f"Auto-translation completed for {translated_count} jobs",
            "total_processed": len(jobs),
            "translated": translated_count,
            "already_english": len(jobs) - translated_count
        }
        
    except Exception as e:
        logger.error(f"Error in auto-translate: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to auto-translate jobs"
        )

@router.get("/job-translation-history/{job_id}")
async def get_job_translation_history(
    job_id: str,
    db=Depends(get_async_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Get translation history and metadata for a specific job
    """
    try:
        job = await db.jobs.find_one(
            {"_id": ObjectId(job_id)},
            {"translation_metadata": 1, "original_data": 1, "is_translated": 1, "original_language": 1}
        )
        
        if not job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Job not found"
            )
        
        return {
            "job_id": job_id,
            "is_translated": job.get("is_translated", False),
            "original_language": job.get("original_language", "en"),
            "has_original_data": job.get("original_data") is not None,
            "translation_metadata": job.get("translation_metadata", {}),
            "original_data": job.get("original_data") if job.get("original_data") else None
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching translation history for job {job_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch translation history: {str(e)}"
        )

@router.get("/jobs-requiring-translation")
async def get_jobs_requiring_translation(
    limit: int = Query(50, le=100),
    skip: int = Query(0, ge=0),
    language_filter: Optional[str] = Query(None, description="Filter by detected language"),
    current_user: User = Depends(get_current_user)
):
    """Get jobs that might need translation (non-English content)"""
    try:
        db = get_db()
        
        # Query for jobs without translation data
        query = {
            "$or": [
                {"translated_data": {"$exists": False}},
                {"original_language": {"$exists": False}}
            ]
        }
        
        if language_filter:
            query["original_language"] = language_filter
        
        # Get total count
        total = await db.jobs.count_documents(query)
        
        # Fetch jobs
        jobs_cursor = db.jobs.find(query).skip(skip).limit(limit)
        jobs = []
        
        async for job in jobs_cursor:
            # Quick language detection on title
            title_language, confidence = await translation_service.detect_language(job.get("title", ""))
            
            job_info = {
                "job_id": str(job["_id"]),
                "title": job.get("title", ""),
                "company": job.get("company", ""),
                "detected_language": title_language,
                "confidence": confidence,
                "needs_translation": title_language != "en" and confidence > 0.7,
                "created_at": job.get("created_at")
            }
            jobs.append(job_info)
        
        return {
            "success": True,
            "total_jobs": total,
            "jobs": jobs,
            "page_info": {
                "skip": skip,
                "limit": limit,
                "has_more": skip + limit < total
            }
        }
        
    except Exception as e:
        logger.error(f"Error fetching jobs requiring translation: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch jobs requiring translation"
        )

# Export router
__all__ = ['router'] 