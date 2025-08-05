"""
External Cronjob Endpoints
Cron-job.org için özel endpoint'ler (rate limiting olmadan)
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks, Request
from typing import Optional
import os
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/cron-external", tags=["cron-external"])

# Cron-job.org için özel API key
CRON_EXTERNAL_API_KEY = os.getenv("CRON_EXTERNAL_API_KEY", "buzz2remote-cron-2024")

def verify_cron_external_api_key(request: Request):
    """Cron-job.org için özel API key doğrulama"""
    # Query parameter'dan kontrol et
    api_key = request.query_params.get("api_key")
    if api_key == CRON_EXTERNAL_API_KEY:
        return api_key
    
    # Header'dan kontrol et
    auth_header = request.headers.get("authorization")
    if auth_header and auth_header.startswith("Bearer "):
        api_key = auth_header.split(" ")[1]
        if api_key == CRON_EXTERNAL_API_KEY:
            return api_key
    
    raise HTTPException(status_code=401, detail="Invalid API key")

@router.post("/health-check")
async def external_health_check(
    background_tasks: BackgroundTasks,
    request: Request
):
    """Cron-job.org için health check endpoint'i"""
    try:
        # API key doğrulama
        verify_cron_external_api_key(request)
        
        logger.info("External health check triggered")
        
        # Background task olarak çalıştır
        background_tasks.add_task(run_external_health_check)
        
        return {
            "status": "success", 
            "message": "Health check started",
            "job_id": "external_health_check"
        }
    except Exception as e:
        logger.error(f"External health check error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/external-apis")
async def external_api_crawler(
    background_tasks: BackgroundTasks,
    request: Request
):
    """Cron-job.org için external API crawler endpoint'i"""
    try:
        # API key doğrulama
        verify_cron_external_api_key(request)
        
        logger.info("External API crawler triggered")
        
        # Background task olarak çalıştır
        background_tasks.add_task(run_external_api_crawler)
        
        return {
            "status": "success", 
            "message": "External API crawler started",
            "job_id": "external_api_crawler"
        }
    except Exception as e:
        logger.error(f"External API crawler error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/database-cleanup")
async def external_database_cleanup(
    background_tasks: BackgroundTasks,
    request: Request
):
    """Cron-job.org için database cleanup endpoint'i"""
    try:
        # API key doğrulama
        verify_cron_external_api_key(request)
        
        logger.info("External database cleanup triggered")
        
        # Background task olarak çalıştır
        background_tasks.add_task(run_external_database_cleanup)
        
        return {
            "status": "success", 
            "message": "Database cleanup started",
            "job_id": "external_database_cleanup"
        }
    except Exception as e:
        logger.error(f"External database cleanup error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/job-statistics")
async def external_job_statistics(
    background_tasks: BackgroundTasks,
    request: Request
):
    """Cron-job.org için job statistics endpoint'i"""
    try:
        # API key doğrulama
        verify_cron_external_api_key(request)
        
        logger.info("External job statistics triggered")
        
        # Background task olarak çalıştır
        background_tasks.add_task(run_external_job_statistics)
        
        return {
            "status": "success", 
            "message": "Job statistics started",
            "job_id": "external_job_statistics"
        }
    except Exception as e:
        logger.error(f"External job statistics error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/distill-crawler")
async def external_distill_crawler(
    background_tasks: BackgroundTasks,
    request: Request
):
    """Cron-job.org için distill crawler endpoint'i"""
    try:
        # API key doğrulama
        verify_cron_external_api_key(request)
        
        logger.info("External distill crawler triggered")
        
        # Background task olarak çalıştır
        background_tasks.add_task(run_external_distill_crawler)
        
        return {
            "status": "success", 
            "message": "Distill crawler started",
            "job_id": "external_distill_crawler"
        }
    except Exception as e:
        logger.error(f"External distill crawler error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/status-monitor")
async def external_status_monitor(
    background_tasks: BackgroundTasks,
    request: Request
):
    """Cron-job.org için status monitor endpoint'i"""
    try:
        # API key doğrulama
        verify_cron_external_api_key(request)
        
        logger.info("External status monitor triggered")
        
        # Background task olarak çalıştır
        background_tasks.add_task(run_external_status_monitor)
        
        return {
            "status": "success", 
            "message": "Status monitor started",
            "job_id": "external_status_monitor"
        }
    except Exception as e:
        logger.error(f"External status monitor error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/test-timeout")
async def external_test_timeout(
    background_tasks: BackgroundTasks,
    request: Request
):
    """Cron-job.org için test timeout endpoint'i"""
    try:
        # API key doğrulama
        verify_cron_external_api_key(request)
        
        logger.info("External test timeout triggered")
        
        # Background task olarak çalıştır
        background_tasks.add_task(run_external_test_timeout)
        
        return {
            "status": "success", 
            "message": "Test timeout started",
            "job_id": "external_test_timeout"
        }
    except Exception as e:
        logger.error(f"External test timeout error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Background task fonksiyonları
async def run_external_health_check():
    """External health check'ı çalıştır"""
    try:
        # Health check logic burada
        logger.info("External health check completed")
        
    except Exception as e:
        logger.error(f"External health check failed: {str(e)}")

async def run_external_api_crawler():
    """External API crawler'ı çalıştır"""
    try:
        # External API crawler logic burada
        logger.info("External API crawler completed")
        
    except Exception as e:
        logger.error(f"External API crawler failed: {str(e)}")

async def run_external_database_cleanup():
    """External database cleanup'ı çalıştır"""
    try:
        # Database cleanup logic burada
        logger.info("External database cleanup completed")
        
    except Exception as e:
        logger.error(f"External database cleanup failed: {str(e)}")

async def run_external_job_statistics():
    """External job statistics'ı çalıştır"""
    try:
        # Job statistics logic burada
        logger.info("External job statistics completed")
        
    except Exception as e:
        logger.error(f"External job statistics failed: {str(e)}")

async def run_external_distill_crawler():
    """External distill crawler'ı çalıştır"""
    try:
        # Distill crawler logic burada
        logger.info("External distill crawler completed")
        
    except Exception as e:
        logger.error(f"External distill crawler failed: {str(e)}")

async def run_external_status_monitor():
    """External status monitor'ı çalıştır"""
    try:
        # Status monitor logic burada
        logger.info("External status monitor completed")
        
    except Exception as e:
        logger.error(f"External status monitor failed: {str(e)}")

async def run_external_test_timeout():
    """External test timeout monitor'ı çalıştır"""
    try:
        # Test timeout logic burada
        logger.info("External test timeout monitor completed")
        
    except Exception as e:
        logger.error(f"External test timeout monitor failed: {str(e)}") 