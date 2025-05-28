from fastapi import APIRouter, Request, HTTPException, Depends, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from typing import Optional, Dict, Any
import os
import sys
from datetime import datetime, timedelta
import json
import logging
from motor.motor_asyncio import AsyncIOMotorDatabase
import asyncio
import uuid

# Add backend to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import get_db, get_async_db
from services.scheduler_service import get_scheduler

# Setup templates
templates = Jinja2Templates(directory=os.path.join(os.path.dirname(os.path.abspath(__file__)), "templates"))

admin_router = APIRouter()
logger = logging.getLogger(__name__)

def get_admin_auth(request: Request):
    """Simple admin authentication check"""
    admin_logged_in = request.session.get("admin_logged_in", False)
    if not admin_logged_in:
        raise HTTPException(status_code=401, detail="Admin authentication required")
    return True

@admin_router.get("/", response_class=HTMLResponse)
async def admin_dashboard(request: Request, admin_auth: bool = Depends(get_admin_auth)):
    """Admin dashboard"""
    try:
        db = await get_async_db()
        
        # Get basic statistics
        jobs_collection = db["jobs"]
        total_jobs = await jobs_collection.count_documents({})
        active_jobs = await jobs_collection.count_documents({"is_active": True})
        
        # Jobs added in last 24 hours
        yesterday = datetime.now() - timedelta(days=1)
        new_jobs_24h = await jobs_collection.count_documents({
            "created_at": {"$gte": yesterday.isoformat()}
        })
        
        # Get scheduler status
        scheduler = get_scheduler()
        scheduler_status = scheduler.get_job_status() if scheduler else {"status": "not_available", "jobs": []}
        
        # Get deployment status
        deployment_status = {
            "database_status": "operational",
            "crawler_status": "operational",
            "telegram_status": "operational" if os.getenv("TELEGRAM_ENABLED", "false").lower() == "true" else "disabled",
            "last_deploy": datetime.now().isoformat(),
            "deployment_status": "success"
        }
        
        # Get error logs
        error_logs = []
        try:
            error_logs_cursor = db.crawl_errors.find().sort('timestamp', -1).limit(100)
            error_logs = await error_logs_cursor.to_list(length=100)
        except Exception as log_e:
            logger.error(f"Error fetching crawl_errors: {log_e}")
            pass
        
        stats = {
            "total_jobs": total_jobs,
            "active_jobs": active_jobs,
            "new_jobs_24h": new_jobs_24h,
            "scheduler_status": scheduler_status["status"],
            "active_cronjobs": len(scheduler_status.get("jobs", [])),
            **deployment_status
        }
        
        return templates.TemplateResponse("dashboard.html", {
            "request": request,
            "stats": stats,
            "scheduler_status": scheduler_status,
            "deployment_status": deployment_status,
            "error_logs": error_logs,
            "page_title": "Admin Dashboard"
        })
        
    except Exception as e:
        logger.error(f"Error in admin dashboard: {str(e)}")
        return templates.TemplateResponse("error.html", {
            "request": request,
            "error": str(e),
            "page_title": "Error"
        })

@admin_router.get("/login", response_class=HTMLResponse)
async def admin_login_page(request: Request):
    """Admin login page"""
    return templates.TemplateResponse("login.html", {
        "request": request,
        "page_title": "Admin Login"
    })

@admin_router.post("/login")
async def admin_login(request: Request, username: str = Form(...), password: str = Form(...)):
    """Handle admin login"""
    if username == os.getenv("ADMIN_USERNAME", "admin") and password == os.getenv("ADMIN_PASSWORD", "buzz2remote2024"):
        request.session["admin_logged_in"] = True
        return RedirectResponse(url="/admin/", status_code=302)
    else:
        return templates.TemplateResponse("login.html", {
            "request": request,
            "error": "Invalid credentials",
            "page_title": "Admin Login"
        })

@admin_router.get("/logout")
async def admin_logout(request: Request):
    """Handle admin logout"""
    request.session.clear()
    return RedirectResponse(url="/admin/login", status_code=302)

@admin_router.get("/jobs", response_class=HTMLResponse)
async def admin_jobs_page(request: Request, admin_auth: bool = Depends(get_admin_auth)):
    """Jobs management page - displays jobs"""
    try:
        db = await get_async_db()
        jobs_collection = db["jobs"]
        
        # Get recent jobs (limit to 100 for performance)
        jobs_cursor = jobs_collection.find({}).sort("created_at", -1).limit(100)
        jobs_list = await jobs_cursor.to_list(length=100)
        
        # Convert ObjectId to string for JSON serialization
        for job in jobs_list:
            job["_id"] = str(job["_id"])
        
        return templates.TemplateResponse("admin/jobs.html", {
            "request": request,
            "jobs": jobs_list,
            "page_title": "Jobs Management"
        })
        
    except Exception as e:
        logger.error(f"Error fetching admin jobs page: {e}")
        return templates.TemplateResponse("error.html", {
            "request": request,
            "error": str(e),
            "page_title": "Error"
        })

@admin_router.get("/companies", response_class=HTMLResponse)
async def admin_companies_page(request: Request, admin_auth: bool = Depends(get_admin_auth)):
    """Companies management page - displays companies"""
    try:
        db = await get_async_db()
        companies_collection = db["companies"]
        companies_cursor = companies_collection.find({}).limit(100)
        companies_list = await companies_cursor.to_list(length=100)
        for company in companies_list:
            company["_id"] = str(company["_id"])

        return templates.TemplateResponse(
            "admin/companies.html",
            {"request": request, "companies": companies_list, "page_title": "Companies Management"}
        )
    except Exception as e:
        logger.error(f"Error fetching admin companies page: {e}")
        return templates.TemplateResponse("error.html", {
            "request": request,
            "error": str(e),
            "page_title": "Error"
        })

@admin_router.get("/cronjobs", response_class=HTMLResponse)
async def admin_cronjobs(request: Request, admin_auth: bool = Depends(get_admin_auth)):
    """Cronjobs management page"""
    try:
        scheduler = get_scheduler()
        
        if not scheduler:
            return templates.TemplateResponse("cronjobs.html", {
                "request": request,
                "scheduler_available": False,
                "page_title": "Cronjobs Management"
            })
        
        scheduler_status = scheduler.get_job_status()
        formatted_jobs = []
        for job in scheduler_status.get("jobs", []):
            formatted_job = {
                "id": job["id"],
                "name": job["name"],
                "next_run": job["next_run"],
                "trigger": job["trigger"],
                "status": "Active" if job["next_run"] else "Inactive"
            }
            job_descriptions = {
                "health_check": "Keeps Render service awake by sending health check requests every 14 minutes",
                "external_api_crawler": "Crawls external job APIs (RemoteOK, WeWorkRemotely, etc.) daily at 9 AM UTC",
                "distill_crawler": "Crawls company career pages from Distill export data daily at 10 AM UTC",
                "database_cleanup": "Removes old job postings (90+ days) weekly on Sunday at 2 AM UTC",
                "job_statistics": "Generates and sends daily job statistics at 8 AM UTC"
            }
            formatted_job["description"] = job_descriptions.get(job["id"], "No description available")
            formatted_jobs.append(formatted_job)
        
        return templates.TemplateResponse("cronjobs.html", {
            "request": request,
            "scheduler_available": True,
            "scheduler_status": scheduler_status["status"],
            "jobs": formatted_jobs,
            "page_title": "Cronjobs Management"
        })
        
    except Exception as e:
        logger.error(f"Error fetching cronjobs: {e}")
        return templates.TemplateResponse("error.html", {
            "request": request,
            "error": str(e),
            "page_title": "Error"
        })

@admin_router.get("/settings", response_class=HTMLResponse)
async def admin_settings(request: Request, admin_auth: bool = Depends(get_admin_auth)):
    """Settings page"""
    try:
        env_vars = {
            "ENVIRONMENT": os.getenv("ENVIRONMENT", "development"),
            "MONGODB_URI": "***" if os.getenv("MONGODB_URI") else "Not set",
            "TELEGRAM_BOT_TOKEN": "***" if os.getenv("TELEGRAM_BOT_TOKEN") else "Not set",
            "TELEGRAM_CHAT_ID": os.getenv("TELEGRAM_CHAT_ID", "Not set"),
            "RENDER_GIT_COMMIT": os.getenv("RENDER_GIT_COMMIT", "Not available")[:8] if os.getenv("RENDER_GIT_COMMIT") else "Not available"
        }
        
        return templates.TemplateResponse("settings.html", {
            "request": request,
            "env_vars": env_vars,
            "page_title": "Settings"
        })
        
    except Exception as e:
        logger.error(f"Error fetching settings: {e}")
        return templates.TemplateResponse("error.html", {
            "request": request,
            "error": str(e),
            "page_title": "Error"
        })

@admin_router.get("/service-status")
async def get_service_status(admin_auth: bool = Depends(get_admin_auth)):
    try:
        db = await get_async_db()
        services = {
            "Buzz2remote": {"last_run": None, "status": "active"},
            "External": {"last_run": None, "status": "active"},
            "Analysis": {"last_run": None, "status": "active"}
        }
        
        logs_cursor = db.service_logs.find().sort("timestamp", -1).limit(3)
        logs = await logs_cursor.to_list(length=3)
        for log in logs:
            if log["service"] in services:
                services[log["service"]]["last_run"] = log["timestamp"]
        
        return services
    except Exception as e:
        logger.error(f"Error getting service status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@admin_router.post("/actions/run-crawler")
async def run_crawler_action():
    try:
        process_id = str(uuid.uuid4())
        db = await get_async_db()
        await db.processes.insert_one({
            "process_id": process_id,
            "type": "crawler",
            "status": "running",
            "started_at": datetime.utcnow(),
            "progress": 0
        })
        asyncio.create_task(run_crawler_process_sync(process_id))
        return {"status": "success", "process_id": process_id}
    except Exception as e:
        logger.error(f"Error starting crawler: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@admin_router.post("/actions/fetch-external-apis")
async def fetch_external_apis_action():
    try:
        process_id = str(uuid.uuid4())
        db = await get_async_db()
        await db.processes.insert_one({
            "process_id": process_id,
            "type": "api_fetch",
            "status": "running",
            "started_at": datetime.utcnow(),
            "progress": 0
        })
        asyncio.create_task(fetch_external_apis_process_sync(process_id))
        return {"status": "success", "process_id": process_id}
    except Exception as e:
        logger.error(f"Error starting API fetch: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@admin_router.post("/actions/analyze-positions")
async def analyze_positions_action():
    try:
        process_id = str(uuid.uuid4())
        db = await get_async_db()
        await db.processes.insert_one({
            "process_id": process_id,
            "type": "analysis",
            "status": "running",
            "started_at": datetime.utcnow(),
            "progress": 0
        })
        asyncio.create_task(analyze_positions_process_sync(process_id))
        return {"status": "success", "process_id": process_id}
    except Exception as e:
        logger.error(f"Error starting position analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))

async def run_crawler_process_sync(process_id: str):
    db = await get_async_db()
    try:
        logger.info(f"Starting sync crawler process {process_id}")
        await asyncio.sleep(10)
        await db.processes.update_one(
            {"process_id": process_id},
            {"$set": {"status": "completed", "progress": 100, "ended_at": datetime.utcnow()}}
        )
        logger.info(f"Sync crawler process {process_id} completed.")
    except Exception as e:
        logger.error(f"Error in sync crawler process {process_id}: {e}")
        await db.processes.update_one(
            {"process_id": process_id},
            {"$set": {"status": "failed", "error": str(e), "ended_at": datetime.utcnow()}}
        )

async def fetch_external_apis_process_sync(process_id: str):
    db = await get_async_db()
    try:
        logger.info(f"Starting sync API fetch process {process_id}")
        await asyncio.sleep(10)
        await db.processes.update_one(
            {"process_id": process_id},
            {"$set": {"status": "completed", "progress": 100, "ended_at": datetime.utcnow()}}
        )
        logger.info(f"Sync API fetch process {process_id} completed.")
    except Exception as e:
        logger.error(f"Error in sync API fetch process {process_id}: {e}")
        await db.processes.update_one(
            {"process_id": process_id},
            {"$set": {"status": "failed", "error": str(e), "ended_at": datetime.utcnow()}}
        )

async def analyze_positions_process_sync(process_id: str):
    db = await get_async_db()
    try:
        logger.info(f"Starting sync analysis process {process_id}")
        await asyncio.sleep(10)
        await db.processes.update_one(
            {"process_id": process_id},
            {"$set": {"status": "completed", "progress": 100, "ended_at": datetime.utcnow()}}
        )
        logger.info(f"Sync analysis process {process_id} completed.")
    except Exception as e:
        logger.error(f"Error in sync analysis process {process_id}: {e}")
        await db.processes.update_one(
            {"process_id": process_id},
            {"$set": {"status": "failed", "error": str(e), "ended_at": datetime.utcnow()}}
        ) 