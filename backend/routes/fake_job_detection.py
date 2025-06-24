from fastapi import APIRouter, HTTPException, Depends, Query, status
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
import logging

from backend.services.fake_job_detector import fake_job_detector, FakeJobRiskLevel
from backend.database import get_async_db
from backend.utils.auth import get_current_admin

router = APIRouter(prefix="/fake-job-detection", tags=["fake-job-detection"])
logger = logging.getLogger(__name__)

class JobAnalysisRequest(BaseModel):
    """Request model for job analysis"""
    job_id: str

class BatchJobAnalysisRequest(BaseModel):
    """Request model for batch job analysis"""
    job_ids: List[str]
    max_jobs: int = 50

class FakeJobAnalysisResponse(BaseModel):
    """Response model for fake job analysis"""
    job_id: str
    risk_level: str
    confidence_score: float
    red_flags: List[str]
    suspicious_patterns: List[str]
    ai_analysis: Optional[str]
    recommendation: str
    analyzed_at: str

@router.post("/analyze-job", response_model=FakeJobAnalysisResponse)
async def analyze_single_job(
    request: JobAnalysisRequest,
    db=Depends(get_async_db),
    admin=Depends(get_current_admin)
):
    """
    Analyze a single job posting for fake indicators.
    
    This endpoint uses AI and rule-based analysis to detect potentially 
    fraudulent job postings.
    """
    try:
        # Get job data from database
        job = await db.jobs.find_one({"_id": request.job_id})
        if not job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Job not found"
            )
        
        # Convert ObjectId to string for analysis
        if "_id" in job:
            job["_id"] = str(job["_id"])
        
        # Analyze the job
        analysis = await fake_job_detector.analyze_job(job)
        
        return FakeJobAnalysisResponse(
            job_id=analysis.job_id,
            risk_level=analysis.risk_level.value,
            confidence_score=analysis.confidence_score,
            red_flags=analysis.red_flags,
            suspicious_patterns=analysis.suspicious_patterns,
            ai_analysis=analysis.ai_analysis,
            recommendation=analysis.recommendation,
            analyzed_at=analysis.analyzed_at.isoformat()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error analyzing job {request.job_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Analysis failed: {str(e)}"
        )

@router.post("/analyze-batch", response_model=Dict[str, Any])
async def analyze_batch_jobs(
    request: BatchJobAnalysisRequest,
    db=Depends(get_async_db),
    admin=Depends(get_current_admin)
):
    """
    Analyze multiple job postings in batch for fake indicators.
    
    Useful for processing large numbers of jobs efficiently.
    Maximum 50 jobs per request to prevent timeouts.
    """
    try:
        # Validate batch size
        if len(request.job_ids) > request.max_jobs:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Too many jobs requested. Maximum {request.max_jobs} allowed."
            )
        
        # Get jobs from database
        jobs_cursor = db.jobs.find({"_id": {"$in": request.job_ids}})
        jobs = await jobs_cursor.to_list(length=None)
        
        if not jobs:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No jobs found with provided IDs"
            )
        
        # Convert ObjectIds to strings
        for job in jobs:
            if "_id" in job:
                job["_id"] = str(job["_id"])
        
        # Analyze jobs in batch
        analyses = await fake_job_detector.batch_analyze_jobs(jobs)
        
        # Format results
        results = []
        risk_summary = {"low": 0, "medium": 0, "high": 0, "critical": 0}
        
        for analysis in analyses:
            results.append({
                "job_id": analysis.job_id,
                "risk_level": analysis.risk_level.value,
                "confidence_score": analysis.confidence_score,
                "red_flags_count": len(analysis.red_flags),
                "recommendation": analysis.recommendation
            })
            risk_summary[analysis.risk_level.value] += 1
        
        return {
            "total_analyzed": len(analyses),
            "results": results,
            "risk_summary": risk_summary,
            "recommendations": {
                "high_risk_jobs": len([a for a in analyses if a.risk_level in [FakeJobRiskLevel.HIGH, FakeJobRiskLevel.CRITICAL]]),
                "requires_review": len([a for a in analyses if "REVIEW" in a.recommendation]),
                "should_reject": len([a for a in analyses if "REJECT" in a.recommendation])
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in batch analysis: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Batch analysis failed: {str(e)}"
        )

@router.get("/analysis-history/{job_id}", response_model=List[FakeJobAnalysisResponse])
async def get_job_analysis_history(
    job_id: str,
    admin=Depends(get_current_admin),
    db=Depends(get_async_db)
):
    """
    Get analysis history for a specific job.
    
    Returns all previous analyses performed on this job.
    """
    try:
        # Get analysis history from database
        analyses_cursor = db.fake_job_analyses.find(
            {"job_id": job_id}
        ).sort("analyzed_at", -1)
        
        analyses = await analyses_cursor.to_list(length=None)
        
        if not analyses:
            return []
        
        # Format results
        results = []
        for analysis in analyses:
            results.append(FakeJobAnalysisResponse(
                job_id=analysis["job_id"],
                risk_level=analysis["risk_level"],
                confidence_score=analysis["confidence_score"],
                red_flags=analysis["red_flags"],
                suspicious_patterns=analysis["suspicious_patterns"],
                ai_analysis=analysis.get("ai_analysis"),
                recommendation=analysis["recommendation"],
                analyzed_at=analysis["analyzed_at"]
            ))
        
        return results
        
    except Exception as e:
        logger.error(f"Error getting analysis history for job {job_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get analysis history: {str(e)}"
        )

@router.get("/statistics", response_model=Dict[str, Any])
async def get_fake_job_statistics(
    days: int = Query(30, ge=1, le=365, description="Number of days to analyze"),
    admin=Depends(get_current_admin)
):
    """
    Get fake job detection statistics.
    
    Returns statistics about fake job detection over the specified period.
    """
    try:
        stats = await fake_job_detector.get_analysis_statistics(days)
        
        if not stats:
            return {
                "total_analyzed": 0,
                "risk_distribution": {},
                "avg_confidence_by_risk": {},
                "period_days": days,
                "message": "No analysis data available for the specified period"
            }
        
        return stats
        
    except Exception as e:
        logger.error(f"Error getting fake job statistics: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get statistics: {str(e)}"
        )

@router.get("/high-risk-jobs", response_model=Dict[str, Any])
async def get_high_risk_jobs(
    risk_level: Optional[str] = Query(None, description="Filter by risk level"),
    limit: int = Query(50, ge=1, le=100),
    skip: int = Query(0, ge=0),
    admin=Depends(get_current_admin),
    db=Depends(get_async_db)
):
    """
    Get jobs flagged as high risk.
    
    Returns a list of jobs that have been identified as potentially fake
    or suspicious by the detection system.
    """
    try:
        # Build query
        query = {}
        if risk_level:
            if risk_level.lower() not in ["low", "medium", "high", "critical"]:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid risk level. Must be one of: low, medium, high, critical"
                )
            query["risk_level"] = risk_level.lower()
        else:
            # Default to high and critical risk
            query["risk_level"] = {"$in": ["high", "critical"]}
        
        # Get high-risk analyses
        total = await db.fake_job_analyses.count_documents(query)
        
        analyses_cursor = db.fake_job_analyses.find(query).sort("analyzed_at", -1).skip(skip).limit(limit)
        analyses = await analyses_cursor.to_list(length=None)
        
        # Get corresponding job data
        job_ids = [analysis["job_id"] for analysis in analyses]
        jobs_cursor = db.jobs.find({"_id": {"$in": job_ids}})
        jobs = await jobs_cursor.to_list(length=None)
        
        # Create job lookup
        jobs_dict = {str(job["_id"]): job for job in jobs}
        
        # Format results
        results = []
        for analysis in analyses:
            job_data = jobs_dict.get(analysis["job_id"])
            if job_data:
                results.append({
                    "job_id": analysis["job_id"],
                    "job_title": job_data.get("title", "Unknown"),
                    "company": job_data.get("company", "Unknown"),
                    "risk_level": analysis["risk_level"],
                    "confidence_score": analysis["confidence_score"],
                    "red_flags_count": len(analysis["red_flags"]),
                    "recommendation": analysis["recommendation"],
                    "analyzed_at": analysis["analyzed_at"],
                    "job_url": job_data.get("url")
                })
        
        return {
            "total": total,
            "results": results,
            "pagination": {
                "limit": limit,
                "skip": skip,
                "has_more": skip + len(results) < total
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting high-risk jobs: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get high-risk jobs: {str(e)}"
        )

@router.post("/bulk-action", response_model=Dict[str, Any])
async def bulk_action_on_jobs(
    job_ids: List[str],
    action: str = Query(..., description="Action to perform: analyze, approve, reject, flag"),
    admin=Depends(get_current_admin),
    db=Depends(get_async_db)
):
    """
    Perform bulk actions on jobs based on fake detection results.
    
    Allows admins to take action on multiple jobs at once.
    """
    try:
        if action not in ["analyze", "approve", "reject", "flag"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid action. Must be one of: analyze, approve, reject, flag"
            )
        
        if len(job_ids) > 100:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Too many jobs. Maximum 100 allowed per bulk action."
            )
        
        results = {"success": 0, "failed": 0, "errors": []}
        
        if action == "analyze":
            # Perform batch analysis
            jobs_cursor = db.jobs.find({"_id": {"$in": job_ids}})
            jobs = await jobs_cursor.to_list(length=None)
            
            for job in jobs:
                try:
                    job["_id"] = str(job["_id"])
                    await fake_job_detector.analyze_job(job)
                    results["success"] += 1
                except Exception as e:
                    results["failed"] += 1
                    results["errors"].append(f"Job {job.get('_id', 'unknown')}: {str(e)}")
        
        elif action == "approve":
            # Mark jobs as approved
            update_result = await db.jobs.update_many(
                {"_id": {"$in": job_ids}},
                {"$set": {"fake_detection_status": "approved", "is_active": True}}
            )
            results["success"] = update_result.modified_count
        
        elif action == "reject":
            # Mark jobs as rejected (hide from users)
            update_result = await db.jobs.update_many(
                {"_id": {"$in": job_ids}},
                {"$set": {"fake_detection_status": "rejected", "is_active": False}}
            )
            results["success"] = update_result.modified_count
        
        elif action == "flag":
            # Flag jobs for manual review
            update_result = await db.jobs.update_many(
                {"_id": {"$in": job_ids}},
                {"$set": {"fake_detection_status": "flagged", "requires_review": True}}
            )
            results["success"] = update_result.modified_count
        
        return {
            "action": action,
            "total_jobs": len(job_ids),
            "successful": results["success"],
            "failed": results["failed"],
            "errors": results["errors"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in bulk action {action}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Bulk action failed: {str(e)}"
        ) 