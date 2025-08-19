"""
Bulk Apply API Routes
Toplu başvuru sistemi için API endpoint'leri
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from fastapi.responses import JSONResponse
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, HttpUrl
import asyncio
import time
import logging
from datetime import datetime, timedelta

from ..models.user import UserResponse as User
from ..models.job import JobResponse as Job
from ..models.user_application import UserApplication as Application
from ..middleware.auth_middleware import get_current_user
from ..services.ai_application_service import AIApplicationService
from ..middleware.rate_limiter import RateLimiter
from ..database.base_repository import BaseRepository
from ..middleware.input_validation import validate_url
from ..utils.security import SecurityUtils
from ..utils.rate_limiting import check_rate_limit

# Logging
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/bulk-apply", tags=["Bulk Apply"])

# Rate limiter instance
rate_limiter = RateLimiter()

# Pydantic models
class JobSelection(BaseModel):
    id: str
    title: str
    company: str
    url: HttpUrl
    location: Optional[str] = None
    salary: Optional[str] = None

class FormAnalysisRequest(BaseModel):
    job_url: HttpUrl
    job_title: str
    company_name: str

class FormAnalysisResponse(BaseModel):
    fields: List[Dict[str, Any]]
    form_type: str
    confidence: float
    estimated_time: int

class FormFillRequest(BaseModel):
    job_url: HttpUrl
    form_data: Dict[str, Any]
    profile_data: Dict[str, Any]

class FormFillResponse(BaseModel):
    success: bool
    filled_fields: Dict[str, Any]
    missing_fields: List[str]
    confidence: float

class FormSubmitRequest(BaseModel):
    job_url: HttpUrl
    form_data: Dict[str, Any]

class FormSubmitResponse(BaseModel):
    success: bool
    application_id: Optional[str] = None
    message: str
    timestamp: datetime

class BulkApplyRequest(BaseModel):
    jobs: List[JobSelection]
    form_config: Dict[str, Any]
    rate_limit: Optional[int] = 1000  # milliseconds
    max_retries: Optional[int] = 3

class BulkApplyResponse(BaseModel):
    job_id: str
    status: str
    success: bool
    application_id: Optional[str] = None
    error_message: Optional[str] = None
    retry_count: int = 0
    timestamp: datetime

class BulkApplyStatus(BaseModel):
    total_jobs: int
    completed_jobs: int
    successful_jobs: int
    failed_jobs: int
    in_progress_jobs: int
    estimated_completion: Optional[datetime] = None
    overall_progress: float

# Background task storage
bulk_apply_tasks: Dict[str, Dict[str, Any]] = {}

@router.post("/analyze-form", response_model=FormAnalysisResponse)
async def analyze_form(
    request: FormAnalysisRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Form analizi yapar ve tespit edilen alanları döner
    """
    try:
        # Rate limiting
        await check_rate_limit(current_user.id, "form_analysis", 5, 60)
        
        # URL validation
        if not validate_url(str(request.job_url)):
            raise HTTPException(status_code=400, detail="Invalid job URL")
        
        # Form analizi
        ai_service = AIApplicationService()
        analysis_result = await ai_service.analyze_form(
            job_url=str(request.job_url),
            job_title=request.job_title,
            company_name=request.company_name
        )
        
        logger.info(f"Form analysis completed for {request.job_url}")
        
        return FormAnalysisResponse(
            fields=analysis_result.get("fields", []),
            form_type=analysis_result.get("form_type", "unknown"),
            confidence=analysis_result.get("confidence", 0.0),
            estimated_time=analysis_result.get("estimated_time", 30)
        )
        
    except Exception as e:
        logger.error(f"Form analysis error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Form analysis failed: {str(e)}")

@router.post("/fill-form", response_model=FormFillResponse)
async def fill_form(
    request: FormFillRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Form alanlarını kullanıcı profili ile doldurur
    """
    try:
        # Rate limiting
        await check_rate_limit(current_user.id, "form_fill", 10, 60)
        
        # Input sanitization
        sanitized_data = {
                            key: SecurityUtils.sanitize_input(value) 
            for key, value in request.form_data.items()
        }
        
        # Form doldurma
        ai_service = AIApplicationService()
        fill_result = await ai_service.fill_form(
            job_url=str(request.job_url),
            form_data=sanitized_data,
            profile_data=request.profile_data
        )
        
        logger.info(f"Form filling completed for {request.job_url}")
        
        return FormFillResponse(
            success=fill_result.get("success", False),
            filled_fields=fill_result.get("filled_fields", {}),
            missing_fields=fill_result.get("missing_fields", []),
            confidence=fill_result.get("confidence", 0.0)
        )
        
    except Exception as e:
        logger.error(f"Form filling error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Form filling failed: {str(e)}")

@router.post("/submit-form", response_model=FormSubmitResponse)
async def submit_form(
    request: FormSubmitRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Doldurulmuş formu gönderir
    """
    try:
        # Rate limiting
        await check_rate_limit(current_user.id, "form_submit", 5, 60)
        
        # Form gönderme
        ai_service = AIApplicationService()
        submit_result = await ai_service.submit_form(
            job_url=str(request.job_url),
            form_data=request.form_data
        )
        
        # Başvuru kaydını veritabanına ekle
        if submit_result.get("success"):
            application = Application(
                user_id=current_user.id,
                job_url=str(request.job_url),
                application_id=submit_result.get("application_id"),
                status="submitted",
                submitted_at=datetime.utcnow(),
                metadata=submit_result.get("metadata", {})
            )
            
            # Veritabanına kaydet
            repo = BaseRepository()
            await repo.create(application)
        
        logger.info(f"Form submission completed for {request.job_url}")
        
        return FormSubmitResponse(
            success=submit_result.get("success", False),
            application_id=submit_result.get("application_id"),
            message=submit_result.get("message", "Form submitted successfully"),
            timestamp=datetime.utcnow()
        )
        
    except Exception as e:
        logger.error(f"Form submission error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Form submission failed: {str(e)}")

@router.post("/start-bulk-apply")
async def start_bulk_apply(
    request: BulkApplyRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user)
):
    """
    Toplu başvuru işlemini başlatır
    """
    try:
        # Rate limiting
        await check_rate_limit(current_user.id, "bulk_apply", 1, 300)  # 5 dakikada 1
        
        # Job sayısı kontrolü
        if len(request.jobs) > 50:
            raise HTTPException(status_code=400, detail="Maximum 50 jobs allowed per bulk apply")
        
        # Task ID oluştur
        task_id = f"bulk_apply_{current_user.id}_{int(time.time())}"
        
        # Task durumunu başlat
        bulk_apply_tasks[task_id] = {
            "user_id": current_user.id,
            "total_jobs": len(request.jobs),
            "completed_jobs": 0,
            "successful_jobs": 0,
            "failed_jobs": 0,
            "in_progress_jobs": 0,
            "jobs": request.jobs,
            "form_config": request.form_config,
            "rate_limit": request.rate_limit,
            "max_retries": request.max_retries,
            "started_at": datetime.utcnow(),
            "status": "running",
            "results": []
        }
        
        # Background task'ı başlat
        background_tasks.add_task(
            process_bulk_apply,
            task_id,
            current_user.id,
            request.jobs,
            request.form_config,
            request.rate_limit,
            request.max_retries
        )
        
        logger.info(f"Bulk apply started: {task_id} for user {current_user.id}")
        
        return {
            "task_id": task_id,
            "status": "started",
            "total_jobs": len(request.jobs),
            "estimated_completion": datetime.utcnow() + timedelta(
                seconds=len(request.jobs) * (request.rate_limit / 1000)
            )
        }
        
    except Exception as e:
        logger.error(f"Bulk apply start error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Bulk apply failed to start: {str(e)}")

@router.get("/status/{task_id}", response_model=BulkApplyStatus)
async def get_bulk_apply_status(
    task_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Toplu başvuru durumunu kontrol eder
    """
    try:
        if task_id not in bulk_apply_tasks:
            raise HTTPException(status_code=404, detail="Task not found")
        
        task = bulk_apply_tasks[task_id]
        
        # Kullanıcı kontrolü
        if task["user_id"] != current_user.id:
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Progress hesapla
        total = task["total_jobs"]
        completed = task["completed_jobs"]
        progress = (completed / total * 100) if total > 0 else 0
        
        # Tahmini tamamlanma zamanı
        estimated_completion = None
        if task["status"] == "running" and completed > 0:
            elapsed = datetime.utcnow() - task["started_at"]
            rate = completed / elapsed.total_seconds()
            remaining = (total - completed) / rate if rate > 0 else 0
            estimated_completion = datetime.utcnow() + timedelta(seconds=remaining)
        
        return BulkApplyStatus(
            total_jobs=total,
            completed_jobs=completed,
            successful_jobs=task["successful_jobs"],
            failed_jobs=task["failed_jobs"],
            in_progress_jobs=task["in_progress_jobs"],
            estimated_completion=estimated_completion,
            overall_progress=progress
        )
        
    except Exception as e:
        logger.error(f"Bulk apply status error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Status check failed: {str(e)}")

@router.get("/results/{task_id}")
async def get_bulk_apply_results(
    task_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Toplu başvuru sonuçlarını döner
    """
    try:
        if task_id not in bulk_apply_tasks:
            raise HTTPException(status_code=404, detail="Task not found")
        
        task = bulk_apply_tasks[task_id]
        
        # Kullanıcı kontrolü
        if task["user_id"] != current_user.id:
            raise HTTPException(status_code=403, detail="Access denied")
        
        return {
            "task_id": task_id,
            "status": task["status"],
            "started_at": task["started_at"],
            "completed_at": task.get("completed_at"),
            "results": task["results"],
            "summary": {
                "total_jobs": task["total_jobs"],
                "successful_jobs": task["successful_jobs"],
                "failed_jobs": task["failed_jobs"],
                "success_rate": (task["successful_jobs"] / task["total_jobs"] * 100) if task["total_jobs"] > 0 else 0
            }
        }
        
    except Exception as e:
        logger.error(f"Bulk apply results error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Results retrieval failed: {str(e)}")

@router.post("/cancel/{task_id}")
async def cancel_bulk_apply(
    task_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Toplu başvuru işlemini iptal eder
    """
    try:
        if task_id not in bulk_apply_tasks:
            raise HTTPException(status_code=404, detail="Task not found")
        
        task = bulk_apply_tasks[task_id]
        
        # Kullanıcı kontrolü
        if task["user_id"] != current_user.id:
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Task'ı iptal et
        task["status"] = "cancelled"
        task["cancelled_at"] = datetime.utcnow()
        
        logger.info(f"Bulk apply cancelled: {task_id}")
        
        return {
            "task_id": task_id,
            "status": "cancelled",
            "message": "Bulk apply cancelled successfully"
        }
        
    except Exception as e:
        logger.error(f"Bulk apply cancel error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Cancel failed: {str(e)}")

@router.get("/history")
async def get_bulk_apply_history(
    current_user: User = Depends(get_current_user),
    limit: int = 10,
    offset: int = 0
):
    """
    Kullanıcının toplu başvuru geçmişini döner
    """
    try:
        # Kullanıcının task'larını filtrele
        user_tasks = [
            task for task in bulk_apply_tasks.values()
            if task["user_id"] == current_user.id
        ]
        
        # Sırala ve sayfalama yap
        sorted_tasks = sorted(user_tasks, key=lambda x: x["started_at"], reverse=True)
        paginated_tasks = sorted_tasks[offset:offset + limit]
        
        return {
            "tasks": [
                {
                    "task_id": task_id,
                    "status": task["status"],
                    "total_jobs": task["total_jobs"],
                    "successful_jobs": task["successful_jobs"],
                    "started_at": task["started_at"],
                    "completed_at": task.get("completed_at")
                }
                for task_id, task in enumerate(paginated_tasks)
            ],
            "total": len(user_tasks),
            "limit": limit,
            "offset": offset
        }
        
    except Exception as e:
        logger.error(f"Bulk apply history error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"History retrieval failed: {str(e)}")

async def process_bulk_apply(
    task_id: str,
    user_id: str,
    jobs: List[JobSelection],
    form_config: Dict[str, Any],
    rate_limit: int,
    max_retries: int
):
    """
    Background task: Toplu başvuru işlemini gerçekleştirir
    """
    try:
        task = bulk_apply_tasks[task_id]
        ai_service = AIApplicationService()
        
        for i, job in enumerate(jobs):
            if task["status"] == "cancelled":
                break
            
            task["in_progress_jobs"] += 1
            
            # Rate limiting
            if i > 0:
                await asyncio.sleep(rate_limit / 1000)
            
            # Job'ı işle
            result = await process_single_job(
                job, form_config, ai_service, max_retries
            )
            
            # Sonucu kaydet
            task["results"].append(result)
            task["completed_jobs"] += 1
            task["in_progress_jobs"] -= 1
            
            if result["success"]:
                task["successful_jobs"] += 1
            else:
                task["failed_jobs"] += 1
            
            logger.info(f"Job {i+1}/{len(jobs)} completed: {result['status']}")
        
        # Task'ı tamamla
        task["status"] = "completed"
        task["completed_at"] = datetime.utcnow()
        
        logger.info(f"Bulk apply completed: {task_id}")
        
    except Exception as e:
        logger.error(f"Bulk apply processing error: {str(e)}")
        task["status"] = "failed"
        task["error"] = str(e)

async def process_single_job(
    job: JobSelection,
    form_config: Dict[str, Any],
    ai_service: AIApplicationService,
    max_retries: int
) -> Dict[str, Any]:
    """
    Tek bir job'ı işler
    """
    retry_count = 0
    
    while retry_count <= max_retries:
        try:
            # Form analizi
            analysis = await ai_service.analyze_form(
                job_url=str(job.url),
                job_title=job.title,
                company_name=job.company
            )
            
            # Form doldurma
            fill_result = await ai_service.fill_form(
                job_url=str(job.url),
                form_data=analysis.get("fields", {}),
                profile_data=form_config.get("profile_data", {})
            )
            
            # Form gönderme
            submit_result = await ai_service.submit_form(
                job_url=str(job.url),
                form_data=fill_result.get("filled_fields", {})
            )
            
            return {
                "job_id": job.id,
                "status": "completed",
                "success": submit_result.get("success", False),
                "application_id": submit_result.get("application_id"),
                "retry_count": retry_count,
                "timestamp": datetime.utcnow()
            }
            
        except Exception as e:
            retry_count += 1
            logger.warning(f"Job {job.id} failed (attempt {retry_count}): {str(e)}")
            
            if retry_count > max_retries:
                return {
                    "job_id": job.id,
                    "status": "failed",
                    "success": False,
                    "error_message": str(e),
                    "retry_count": retry_count,
                    "timestamp": datetime.utcnow()
                }
            
            # Retry delay
            await asyncio.sleep(2 ** retry_count)  # Exponential backoff

@router.delete("/cleanup")
async def cleanup_old_tasks(
    current_user: User = Depends(get_current_user)
):
    """
    Eski task'ları temizler (admin only)
    """
    try:
        # Admin kontrolü
        if not current_user.is_admin:
            raise HTTPException(status_code=403, detail="Admin access required")
        
        cutoff_time = datetime.utcnow() - timedelta(days=7)
        cleaned_count = 0
        
        for task_id, task in list(bulk_apply_tasks.items()):
            if task["started_at"] < cutoff_time:
                del bulk_apply_tasks[task_id]
                cleaned_count += 1
        
        logger.info(f"Cleaned up {cleaned_count} old bulk apply tasks")
        
        return {
            "message": f"Cleaned up {cleaned_count} old tasks",
            "remaining_tasks": len(bulk_apply_tasks)
        }
        
    except Exception as e:
        logger.error(f"Cleanup error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Cleanup failed: {str(e)}") 