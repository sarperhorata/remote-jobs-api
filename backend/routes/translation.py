from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks, status
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase

from backend.database.db import get_async_db
from backend.services.translation_service import translation_service
from backend.models.models import (
    TranslationRequest, TranslationResponse, 
    JobTranslationResult, BatchTranslationRequest, BatchTranslationResponse
)
from backend.routes.auth import get_current_user_dependency

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/translation", tags=["translation"])

@router.post("/translate-text", response_model=TranslationResponse)
async def translate_text(
    request: TranslationRequest,
    current_user: dict = Depends(get_current_user_dependency)
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
    current_user: dict = Depends(get_current_user_dependency)
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
    return {
        "languages": translation_service.get_supported_languages(),
        "total_languages": len(translation_service.supported_languages)
    }

@router.post("/translate-job/{job_id}", response_model=JobTranslationResult)
async def translate_job(
    job_id: str,
    target_language: str = "en",
    db=Depends(get_async_db),
    current_user: dict = Depends(get_current_user_dependency)
):
    """
    Translate a specific job listing to target language
    """
    try:
        # Fetch job from database
        job = await db.jobs.find_one({"_id": ObjectId(job_id)})
        if not job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Job not found"
            )
        
        # Convert ObjectId to string for JSON serialization
        job["_id"] = str(job["_id"])
        
        # Translate the job
        translation_result = await translation_service.translate_job_listing(job)
        
        # Update job in database if translation was needed
        if translation_result['needs_translation']:
            translated_data = translation_result['translated_data']
            original_data = translation_result['original_data']
            translation_metadata = translation_result['translation_metadata']
            
            update_doc = {
                "$set": {
                    **translated_data,
                    "is_translated": True,
                    "original_language": translation_result['original_language'],
                    "original_data": original_data,
                    "translation_metadata": translation_metadata,
                    "updated_at": datetime.utcnow()
                }
            }
            
            await db.jobs.update_one(
                {"_id": ObjectId(job_id)},
                update_doc
            )
            
            logger.info(f"Job {job_id} translated from {translation_result['original_language']} to {target_language}")
        
        return JobTranslationResult(
            job_id=job_id,
            needs_translation=translation_result['needs_translation'],
            original_language=translation_result['original_language'],
            translated_data=translation_result.get('translated_data'),
            original_data=translation_result.get('original_data'),
            translation_metadata=translation_result.get('translation_metadata')
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error translating job {job_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Job translation failed: {str(e)}"
        )

@router.post("/batch-translate", response_model=BatchTranslationResponse)
async def batch_translate_jobs(
    request: BatchTranslationRequest,
    background_tasks: BackgroundTasks,
    db=Depends(get_async_db),
    current_user: dict = Depends(get_current_user_dependency)
):
    """
    Translate multiple job listings in batch
    """
    try:
        # Fetch jobs from database
        job_object_ids = [ObjectId(job_id) for job_id in request.job_ids]
        jobs_cursor = db.jobs.find({"_id": {"$in": job_object_ids}})
        jobs = []
        
        async for job in jobs_cursor:
            job["_id"] = str(job["_id"])  # Convert ObjectId to string
            jobs.append(job)
        
        if not jobs:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No jobs found with provided IDs"
            )
        
        # Translate jobs in batches
        translation_results = await translation_service.batch_translate_jobs(
            jobs, batch_size=request.batch_size
        )
        
        # Process results and update database
        results = []
        translated_count = 0
        failed_count = 0
        errors = []
        
        for i, result in enumerate(translation_results):
            job_id = jobs[i]["_id"]
            
            try:
                if result['needs_translation']:
                    # Update job in database
                    translated_data = result['translated_data']
                    original_data = result['original_data']
                    translation_metadata = result['translation_metadata']
                    
                    update_doc = {
                        "$set": {
                            **translated_data,
                            "is_translated": True,
                            "original_language": result['original_language'],
                            "original_data": original_data,
                            "translation_metadata": translation_metadata,
                            "updated_at": datetime.utcnow()
                        }
                    }
                    
                    await db.jobs.update_one(
                        {"_id": ObjectId(job_id)},
                        update_doc
                    )
                    
                    translated_count += 1
                    logger.info(f"Batch: Job {job_id} translated from {result['original_language']} to {request.target_language}")
                
                results.append(JobTranslationResult(
                    job_id=job_id,
                    needs_translation=result['needs_translation'],
                    original_language=result['original_language'],
                    translated_data=result.get('translated_data'),
                    original_data=result.get('original_data'),
                    translation_metadata=result.get('translation_metadata')
                ))
                
            except Exception as job_error:
                failed_count += 1
                error_msg = f"Failed to process job {job_id}: {str(job_error)}"
                errors.append(error_msg)
                logger.error(error_msg)
                
                # Add failed result
                results.append(JobTranslationResult(
                    job_id=job_id,
                    needs_translation=False,
                    original_language="unknown",
                    translation_metadata={"error": str(job_error)}
                ))
        
        return BatchTranslationResponse(
            total_jobs=len(jobs),
            translated_jobs=translated_count,
            failed_jobs=failed_count,
            results=results,
            errors=errors
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in batch translation: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Batch translation failed: {str(e)}"
        )

@router.get("/translation-stats")
async def get_translation_stats(
    db=Depends(get_async_db),
    current_user: dict = Depends(get_current_user_dependency)
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
async def setup_auto_translation(
    background_tasks: BackgroundTasks,
    enabled: bool = True,
    target_language: str = "en",
    current_user: dict = Depends(get_current_user_dependency)
):
    """
    Setup automatic translation for new job listings
    """
    try:
        # This would typically involve setting up a background task or webhook
        # For now, we'll create a simple flag in the database
        
        auto_translate_config = {
            "enabled": enabled,
            "target_language": target_language,
            "updated_at": datetime.utcnow(),
            "updated_by": current_user["_id"]
        }
        
        # Store configuration (you might want to use a separate collection for this)
        db = await get_async_db()
        await db.system_config.update_one(
            {"config_type": "auto_translation"},
            {"$set": auto_translate_config},
            upsert=True
        )
        
        if enabled:
            # Add background task to process untranslated jobs
            background_tasks.add_task(process_untranslated_jobs, target_language)
        
        return {
            "message": f"Auto-translation {'enabled' if enabled else 'disabled'}",
            "target_language": target_language,
            "config": auto_translate_config
        }
        
    except Exception as e:
        logger.error(f"Error setting up auto-translation: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to setup auto-translation: {str(e)}"
        )

@router.get("/job-translation-history/{job_id}")
async def get_job_translation_history(
    job_id: str,
    db=Depends(get_async_db),
    current_user: dict = Depends(get_current_user_dependency)
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

# Background task function
async def process_untranslated_jobs(target_language: str = "en"):
    """
    Background task to process untranslated jobs
    """
    try:
        db = await get_async_db()
        
        # Find jobs that need translation
        untranslated_jobs = []
        async for job in db.jobs.find({
            "$or": [
                {"is_translated": {"$ne": True}},
                {"is_translated": {"$exists": False}}
            ]
        }).limit(50):  # Process in batches
            job["_id"] = str(job["_id"])
            untranslated_jobs.append(job)
        
        if untranslated_jobs:
            logger.info(f"Processing {len(untranslated_jobs)} untranslated jobs")
            
            # Translate jobs
            translation_results = await translation_service.batch_translate_jobs(
                untranslated_jobs, batch_size=10
            )
            
            # Update database with results
            for i, result in enumerate(translation_results):
                if result['needs_translation']:
                    job_id = untranslated_jobs[i]["_id"]
                    
                    update_doc = {
                        "$set": {
                            **result['translated_data'],
                            "is_translated": True,
                            "original_language": result['original_language'],
                            "original_data": result['original_data'],
                            "translation_metadata": result['translation_metadata'],
                            "updated_at": datetime.utcnow()
                        }
                    }
                    
                    await db.jobs.update_one(
                        {"_id": ObjectId(job_id)},
                        update_doc
                    )
            
            logger.info(f"Completed processing {len(untranslated_jobs)} jobs")
        
    except Exception as e:
        logger.error(f"Error in background translation task: {str(e)}")

# Export router
__all__ = ['router'] 