from fastapi import APIRouter, Request, HTTPException, Depends, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from typing import Optional, Dict, Any
import os
import sys
from datetime import datetime, timedelta
import json
import logging

# Add backend to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import get_db
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
async def admin_dashboard(request: Request):
    """Admin dashboard"""
    try:
        db = get_db()
        
        # Get basic statistics
        jobs_collection = db["jobs"]
        total_jobs = jobs_collection.count_documents({})
        active_jobs = jobs_collection.count_documents({"is_active": True})
        
        # Jobs added in last 24 hours
        yesterday = datetime.now() - timedelta(days=1)
        new_jobs_24h = jobs_collection.count_documents({
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
        error_logs = list(db.crawl_errors.find().sort('timestamp', -1).limit(100))
        except:
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
    if username == "admin" and password == "buzz2remote2024":
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
async def admin_jobs(request: Request, admin_auth: bool = Depends(get_admin_auth)):
    """Jobs management page"""
    try:
        db = get_db()
        jobs_collection = db["jobs"]
        
        # Get recent jobs (limit to 100 for performance)
        jobs = list(jobs_collection.find({}).sort("created_at", -1).limit(100))
        
        # Convert ObjectId to string for JSON serialization
        for job in jobs:
            job["_id"] = str(job["_id"])
        
        return templates.TemplateResponse("jobs.html", {
            "request": request,
            "jobs": jobs,
            "page_title": "Jobs Management"
        })
        
    except Exception as e:
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
        
        # Get scheduler status and job details
        scheduler_status = scheduler.get_job_status()
        
        # Format job information for display
        formatted_jobs = []
        for job in scheduler_status.get("jobs", []):
            formatted_job = {
                "id": job["id"],
                "name": job["name"],
                "next_run": job["next_run"],
                "trigger": job["trigger"],
                "status": "Active" if job["next_run"] else "Inactive"
            }
            
            # Add description based on job ID
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
        return templates.TemplateResponse("error.html", {
            "request": request,
            "error": str(e),
            "page_title": "Error"
        })

@admin_router.get("/settings", response_class=HTMLResponse)
async def admin_settings(request: Request, admin_auth: bool = Depends(get_admin_auth)):
    """Settings page"""
    try:
        # Get environment variables and system info
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
        return templates.TemplateResponse("error.html", {
            "request": request,
            "error": str(e),
            "page_title": "Error"
        })

@admin_router.get("/service-status")
async def get_service_status():
    try:
        # Get last run times from database
        db = get_db()
        services = {
            "Buzz2remote": {"last_run": None, "status": "active"},
            "External": {"last_run": None, "status": "active"},
            "Analysis": {"last_run": None, "status": "active"}
        }
        
        # Get last run times from service_logs collection
        logs = db.service_logs.find().sort("timestamp", -1).limit(3)
        for log in logs:
            if log["service"] in services:
                services[log["service"]]["last_run"] = log["timestamp"]
        
        return services
    except Exception as e:
        logger.error(f"Error getting service status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@admin_router.post("/run-buzz2remote")
async def run_buzz2remote():
    try:
        # Run the company crawler
        from buzz2remote_companies_crawler import CompanyCrawler
        crawler = CompanyCrawler()
        await crawler.crawl_all_companies()
        
        # Log the run
        db = get_db()
        db.service_logs.insert_one({
            "service": "Buzz2remote",
            "timestamp": datetime.utcnow(),
            "status": "success"
        })
        
        return {"success": True, "message": "Company crawler completed successfully", "timestamp": datetime.utcnow().isoformat()}
    except Exception as e:
        logger.error(f"Error running company crawler: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@admin_router.post("/run-external")
async def run_external():
    try:
        # Run external API fetcher
        from external_api_fetcher import ExternalAPIFetcher
        fetcher = ExternalAPIFetcher()
        await fetcher.fetch_all_apis()
        
        # Log the run
        db = get_db()
        db.service_logs.insert_one({
            "service": "External",
            "timestamp": datetime.utcnow(),
            "status": "success"
        })
        
        return {"success": True, "message": "External API fetch completed successfully", "timestamp": datetime.utcnow().isoformat()}
    except Exception as e:
        logger.error(f"Error running external API fetcher: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@admin_router.post("/run-analysis")
async def run_analysis():
    try:
        # Run job analysis
        from job_analyzer import JobAnalyzer
        analyzer = JobAnalyzer()
        await analyzer.analyze_all_jobs()
        
        # Log the run
        db = get_db()
        db.service_logs.insert_one({
            "service": "Analysis",
            "timestamp": datetime.utcnow(),
            "status": "success"
        })
        
        return {"success": True, "message": "Job analysis completed successfully", "timestamp": datetime.utcnow().isoformat()}
    except Exception as e:
        logger.error(f"Error running job analysis: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e)) 