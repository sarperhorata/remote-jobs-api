"""
Cronjob API Routes
Cronjob tetikleme endpoint'leri
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
import os
import logging

# API key doğrulama fonksiyonu burada tanımlanacak
# from ..services.telegram_service import TelegramService
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/cron", tags=["cron"])
security = HTTPBearer()

# API Key doğrulama
def verify_cron_api_key(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Cronjob API key doğrulama"""
    api_key = credentials.credentials
    expected_key = os.getenv("API_KEY", "default_cron_key")
    
    if api_key != expected_key:
        raise HTTPException(status_code=401, detail="Invalid API key")
    
    return api_key

@router.post("/external-apis")
async def trigger_external_apis(
    background_tasks: BackgroundTasks,
    api_key: str = Depends(verify_cron_api_key)
):
    """External API crawler'ı tetikle"""
    try:
        logger.info("External API crawler triggered")
        
        # Background task olarak çalıştır
        background_tasks.add_task(run_external_api_crawler)
        
        return {
            "status": "success", 
            "message": "External API crawler started",
            "job_id": "external_apis"
        }
    except Exception as e:
        logger.error(f"External API crawler error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/database-cleanup")
async def trigger_database_cleanup(
    background_tasks: BackgroundTasks,
    api_key: str = Depends(verify_cron_api_key)
):
    """Database cleanup'ı tetikle"""
    try:
        logger.info("Database cleanup triggered")
        
        # Background task olarak çalıştır
        background_tasks.add_task(run_database_cleanup)
        
        return {
            "status": "success", 
            "message": "Database cleanup started",
            "job_id": "database_cleanup"
        }
    except Exception as e:
        logger.error(f"Database cleanup error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/job-statistics")
async def trigger_job_statistics(
    background_tasks: BackgroundTasks,
    api_key: str = Depends(verify_cron_api_key)
):
    """Job statistics'ı tetikle"""
    try:
        logger.info("Job statistics triggered")
        
        # Background task olarak çalıştır
        background_tasks.add_task(run_job_statistics)
        
        return {
            "status": "success", 
            "message": "Job statistics started",
            "job_id": "job_statistics"
        }
    except Exception as e:
        logger.error(f"Job statistics error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/distill-crawler")
async def trigger_distill_crawler(
    background_tasks: BackgroundTasks,
    api_key: str = Depends(verify_cron_api_key)
):
    """Distill crawler'ı tetikle"""
    try:
        logger.info("Distill crawler triggered")
        
        # Background task olarak çalıştır
        background_tasks.add_task(run_distill_crawler)
        
        return {
            "status": "success", 
            "message": "Distill crawler started",
            "job_id": "distill_crawler"
        }
    except Exception as e:
        logger.error(f"Distill crawler error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/status-monitor")
async def trigger_status_monitor(
    background_tasks: BackgroundTasks,
    api_key: str = Depends(verify_cron_api_key)
):
    """Status monitor'ı tetikle"""
    try:
        logger.info("Status monitor triggered")
        
        # Background task olarak çalıştır
        background_tasks.add_task(run_status_monitor)
        
        return {
            "status": "success", 
            "message": "Status monitor started",
            "job_id": "status_monitor"
        }
    except Exception as e:
        logger.error(f"Status monitor error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/test-timeout")
async def trigger_test_timeout(
    background_tasks: BackgroundTasks,
    api_key: str = Depends(verify_cron_api_key)
):
    """Test timeout monitor'ı tetikle"""
    try:
        logger.info("Test timeout monitor triggered")
        
        # Background task olarak çalıştır
        background_tasks.add_task(run_test_timeout)
        
        return {
            "status": "success", 
            "message": "Test timeout monitor started",
            "job_id": "test_timeout"
        }
    except Exception as e:
        logger.error(f"Test timeout monitor error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Background task fonksiyonları
async def run_external_api_crawler():
    """External API crawler'ı çalıştır"""
    try:
        # External API crawler logic burada
        logger.info("External API crawler completed")
        
        # Telegram bildirimi gönder
        # telegram = TelegramService()
        # await telegram.send_message("✅ External API crawler completed successfully")
        
    except Exception as e:
        logger.error(f"External API crawler failed: {str(e)}")
        # telegram = TelegramService()
        # await telegram.send_message(f"❌ External API crawler failed: {str(e)}")

async def run_database_cleanup():
    """Database cleanup'ı çalıştır"""
    try:
        # Database cleanup logic burada
        logger.info("Database cleanup completed")
        
        # Telegram bildirimi gönder
        # telegram = TelegramService()
        # await telegram.send_message("✅ Database cleanup completed successfully")
        
    except Exception as e:
        logger.error(f"Database cleanup failed: {str(e)}")
        # telegram = TelegramService()
        # await telegram.send_message(f"❌ Database cleanup failed: {str(e)}")

async def run_job_statistics():
    """Job statistics'ı çalıştır"""
    try:
        # Job statistics logic burada
        logger.info("Job statistics completed")
        
        # Telegram bildirimi gönder
        # telegram = TelegramService()
        # await telegram.send_message("✅ Job statistics completed successfully")
        
    except Exception as e:
        logger.error(f"Job statistics failed: {str(e)}")
        # telegram = TelegramService()
        # await telegram.send_message(f"❌ Job statistics failed: {str(e)}")

async def run_distill_crawler():
    """Distill crawler'ı çalıştır"""
    try:
        # Distill crawler logic burada
        logger.info("Distill crawler completed")
        
        # Telegram bildirimi gönder
        # telegram = TelegramService()
        # await telegram.send_message("✅ Distill crawler completed successfully")
        
    except Exception as e:
        logger.error(f"Distill crawler failed: {str(e)}")
        # telegram = TelegramService()
        # await telegram.send_message(f"❌ Distill crawler failed: {str(e)}")

async def run_status_monitor():
    """Status monitor'ı çalıştır"""
    try:
        # Status monitor logic burada
        logger.info("Status monitor completed")
        
        # Telegram bildirimi gönder
        # telegram = TelegramService()
        # await telegram.send_message("✅ Status monitor completed successfully")
        
    except Exception as e:
        logger.error(f"Status monitor failed: {str(e)}")
        # telegram = TelegramService()
        # await telegram.send_message(f"❌ Status monitor failed: {str(e)}")

async def run_test_timeout():
    """Test timeout monitor'ı çalıştır"""
    try:
        # Test timeout logic burada
        logger.info("Test timeout monitor completed")
        
        # Telegram bildirimi gönder
        # telegram = TelegramService()
        # await telegram.send_message("✅ Test timeout monitor completed successfully")
        
    except Exception as e:
        logger.error(f"Test timeout monitor failed: {str(e)}")
        # telegram = TelegramService()
        # await telegram.send_message(f"❌ Test timeout monitor failed: {str(e)}") 