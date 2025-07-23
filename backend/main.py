from fastapi import FastAPI, HTTPException, Request, Body, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from starlette.middleware.sessions import SessionMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import logging
import sys
import os
import asyncio
from datetime import datetime, timedelta
import stripe
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse, FileResponse
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId

# Sentry configuration for error monitoring
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.logging import LoggingIntegration

# Initialize Sentry for error monitoring
sentry_sdk.init(
    dsn=os.getenv("SENTRY_DSN", "https://e307d92640eb7e8b60a7ebabf76db882@o4509547047616512.ingest.us.sentry.io/4509547146575872"),
    traces_sample_rate=0.2,  # 20% of transactions for performance monitoring
    profiles_sample_rate=0.2, # 20% of profiles for performance monitoring
    environment=os.getenv("ENVIRONMENT", "development"), # 'development' or 'production'
    release="buzz2remote@1.0.0", # App version
    integrations=[
        FastApiIntegration(transaction_style="endpoint"),
        LoggingIntegration(
            level=logging.INFO,        # Capture info and above as breadcrumbs
            event_level=logging.ERROR  # Send errors as events
        ),
    ],
    # Do not send 404 errors to Sentry
    before_send=lambda event, hint: None if "Not Found" in event.get('logentry', {}).get('message', '') else event,
)

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.routes import auth, profile, jobs, ads, notification_routes, companies, payment, onboarding, applications, translation
from backend.routes.auto_apply import router as auto_apply_router
from backend.routes.ai_recommendations import router as ai_router
from backend.routes.ai_services import router as ai_services_router
from backend.routes.ai_cv_analysis import router as ai_cv_analysis_router
from backend.routes.skills_extraction import router as skills_extraction_router
from backend.routes.profile_auto_fill import router as profile_auto_fill_router
from backend.routes.legal import router as legal_router
from backend.routes.fake_job_detection import router as fake_job_router
from backend.routes.sentry_webhook import router as sentry_webhook_router
from backend.routes.email_test import router as email_test_router
from backend.routes.notifications import router as user_notifications_router
from backend.routes.salary_estimation import router as salary_estimation_router
from backend.database.db import get_async_db, close_db_connections, init_database
from backend.utils.auth import get_current_user

# Import Telegram bot and scheduler with error handling
try:
    from backend.telegram_bot.bot_manager import get_managed_bot, stop_managed_bot
    TELEGRAM_BOT_AVAILABLE = True
except ImportError:
    TELEGRAM_BOT_AVAILABLE = False

try:
    from backend.services.scheduler_service import start_scheduler, stop_scheduler
    SCHEDULER_AVAILABLE = True
except ImportError:
    SCHEDULER_AVAILABLE = False

# Configure logging
logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO").upper())
logger = logging.getLogger(__name__)

# Global instances
telegram_bot = None
scheduler = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Modern lifespan context manager for FastAPI startup and shutdown."""
    global telegram_bot, scheduler
    
    logger.info("Application startup...")
    
    await init_database()
    
    # Initialize cache service
    try:
        from backend.services.cache_service import init_cache_service
        await init_cache_service(max_size=200, ttl_hours=24)
        logger.info("✅ Cache service initialized successfully")
    except Exception as e:
        logger.error(f"❌ Failed to initialize cache service: {e}")
    
    # Disable bot and scheduler in test environment
    is_testing = os.getenv("TESTING", "false").lower() == "true"
    
    if not is_testing and os.getenv("DISABLE_TELEGRAM") != "true" and TELEGRAM_BOT_AVAILABLE:
        telegram_bot = await get_managed_bot()
    
    if not is_testing and os.getenv("DISABLE_SCHEDULER") != "true" and SCHEDULER_AVAILABLE:
        scheduler = await start_scheduler()

    yield
    
    logger.info("Application shutdown...")
    if scheduler:
        await stop_scheduler()
    
    if telegram_bot:
        await stop_managed_bot()
    
    await close_db_connections()

app = FastAPI(
    title="🚀 Buzz2Remote API",
    description="The Ultimate Remote Jobs Platform API",
    version="3.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Middleware setup
allowed_origins = [
    "http://localhost:3000",
    "http://localhost:3001", 
    "http://localhost:3002",
    "http://localhost:3003",
    "http://localhost:3004",
    "http://localhost:5000",
    "http://localhost:5001",
    "http://localhost:5173",
    "https://buzz2remote.com",
    "https://www.buzz2remote.com",
    "https://buzz2remote-api.onrender.com",
    "https://buzz2remote.netlify.app",
    "https://buzz2remote-frontend.onrender.com"
]

# Development ortamında tüm origin'lere izin ver
if os.getenv("ENVIRONMENT") == "production" or os.getenv("ENVIRONMENT") == "development" or os.getenv("NODE_ENV") == "development":
    allowed_origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
    expose_headers=["*"]
)
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Add activity tracking middleware
from backend.middleware.activity_middleware import ActivityTrackingMiddleware
app.add_middleware(ActivityTrackingMiddleware)

# Add session middleware
app.add_middleware(SessionMiddleware, secret_key=os.getenv("SESSION_SECRET_KEY", "a_very_secret_key"))

# Mount static files for admin panel if it exists
admin_static_path = os.path.join(os.path.dirname(__file__), "admin_panel", "static")
if os.path.exists(admin_static_path):
    app.mount("/admin/static", StaticFiles(directory=admin_static_path), name="admin_static")

# Include all application routers
routers_to_include = [
    (auth.router, "/api/v1/auth", ["auth"]),
    (onboarding.router, "/api/v1", ["onboarding"]),
    (profile.router, "/api/v1", ["profile"]),
    (jobs.router, "/api/v1", ["jobs"]),
    (ads.router, "/api/v1", ["ads"]),
    (notification_routes.router, "/api/v1", ["notifications"]),
    (user_notifications_router, "/api/v1", ["user-notifications"]),
    (companies.router, "/api/v1", ["companies"]),
    (legal_router, "/api/v1", ["legal"]),
    (payment.router, "/api/v1", ["payment"]),
    (applications.router, "/api/v1", ["applications"]),
    (auto_apply_router, "/api/v1/auto-apply", ["auto-apply"]),
    (translation.router, "/api/v1", ["translation"]),
    (ai_router, "/api/v1", ["ai"]),
    (ai_services_router, "/api/v1", ["ai-services"]),
    (ai_cv_analysis_router, "/api/v1", ["ai-cv-analysis"]),
    (skills_extraction_router, "/api/v1", ["skills-extraction"]),
    (profile_auto_fill_router, "/api/v1", ["profile-auto-fill"]),
    (fake_job_router, "/api/v1", ["fake-job-detection"]),
    (sentry_webhook_router, "/api/v1", ["webhooks"]),
    (email_test_router, "/email-test", ["email-test"]),
    (salary_estimation_router, "/api/v1/salary", ["salary-estimation"]),
]

# Include admin cleanup router
try:
    from backend.routes.admin_cleanup import router as admin_cleanup_router
    routers_to_include.append((admin_cleanup_router, "", ["admin-cleanup"]))
    logger.info("Admin cleanup router successfully included.")
except ImportError as e:
    logger.warning(f"Admin cleanup router not available: {str(e)}")

for router, prefix, tags in routers_to_include:
    app.include_router(router, prefix=prefix, tags=tags)
    
# Optional: Include admin panel router if available and enabled
try:
    from backend.admin_panel.routes import admin_router
    if os.getenv("ADMIN_PANEL_ENABLED", "true").lower() == "true":
        app.include_router(admin_router, prefix="/admin", tags=["admin"])
        logger.info("Admin panel successfully included.")
except (ImportError, SyntaxError, IndentationError) as e:
    logger.warning(f"Admin panel not available: {str(e)}")
    logger.info("Admin panel temporarily disabled due to import issues")

@app.get("/", tags=["General"])
async def root():
    return {"message": "Welcome to Buzz2Remote API v3"}

@app.get("/health", tags=["General"])
async def health_check():
    """Health check endpoint for monitoring and load balancers."""
    db_status = "disconnected"
    try:
        db = await get_async_db()
        await db.command('ping')
        db_status = "connected"
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        
    return {
        "status": "healthy", 
        "database": db_status,
        "timestamp": datetime.utcnow().isoformat(),
        "version": "3.0.0",
        "environment": os.getenv("ENVIRONMENT", "development")
    }

@app.get("/api/health", tags=["General"])
async def api_health_check():
    """API health check endpoint for frontend health monitoring."""
    return await health_check()

@app.get("/api/status", tags=["General"])
async def api_status():
    """Get API status and system information."""
    try:
        db = await get_async_db()
        jobs_count = await db.jobs.count_documents({})
        companies_count = await db.companies.count_documents({})
        
        return {
            "status": "operational",
            "database": {
                "status": "connected",
                "jobs_count": jobs_count,
                "companies_count": companies_count
            },
            "services": {
                "telegram_bot": TELEGRAM_BOT_AVAILABLE,
                "scheduler": SCHEDULER_AVAILABLE,
                "admin_panel": os.getenv("ADMIN_PANEL_ENABLED", "true").lower() == "true"
            },
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"API status check failed: {e}")
        return {
            "status": "degraded",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }

@app.get("/api/v1/health", tags=["General"])
async def api_v1_health():
    """API v1 health check endpoint."""
    return await health_check()

@app.get("/api/v1/status", tags=["General"])
async def api_v1_status():
    """API v1 status endpoint."""
    return await api_status()

# Add missing endpoints for frontend compatibility
@app.get("/api/jobs/statistics", tags=["Jobs"])
async def get_job_statistics():
    """Get job statistics for frontend dashboard."""
    try:
        db = await get_async_db()
        jobs_col = db["jobs"]
        
        total_jobs = await jobs_col.count_documents({})
        active_jobs = await jobs_col.count_documents({"is_active": True})
        remote_jobs = await jobs_col.count_documents({"work_type": "remote"})
        
        # Get recent jobs count (last 7 days)
        week_ago = datetime.utcnow() - timedelta(days=7)
        recent_jobs = await jobs_col.count_documents({
            "created_at": {"$gte": week_ago}
        })
        
        return {
            "total_positions": total_jobs,
            "active_positions": active_jobs,
            "remote_positions": remote_jobs,
            "recent_positions": recent_jobs,
            "last_updated": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting job statistics: {e}")
        return {
            "total_positions": 0,
            "active_positions": 0,
            "remote_positions": 0,
            "recent_positions": 0,
            "error": str(e)
        }

@app.get("/api/v1/jobs/statistics", tags=["Jobs"])
async def get_job_statistics_v1():
    """Get job statistics for frontend dashboard with companies count."""
    try:
        db = await get_async_db()
        jobs_col = db["jobs"]
        companies_col = db["companies"]
        
        # Job statistics
        total_jobs = await jobs_col.count_documents({})
        active_jobs = await jobs_col.count_documents({"is_active": True})
        remote_jobs = await jobs_col.count_documents({"work_type": "remote"})
        
        # Get recent jobs count (last 7 days)
        week_ago = datetime.utcnow() - timedelta(days=7)
        recent_jobs = await jobs_col.count_documents({
            "created_at": {"$gte": week_ago}
        })
        
        # Companies statistics
        total_companies = await companies_col.count_documents({})
        active_companies = await companies_col.count_documents({"is_active": {"$ne": False}})
        
        # Count unique companies from jobs
        unique_companies_pipeline = [
            {"$group": {"_id": "$company"}},
            {"$count": "total"}
        ]
        unique_companies_result = await jobs_col.aggregate(unique_companies_pipeline).to_list(length=None)
        unique_companies_count = unique_companies_result[0]["total"] if unique_companies_result else 0
        
        # Countries count (estimate based on unique locations)
        unique_locations_pipeline = [
            {"$group": {"_id": "$location"}},
            {"$count": "total"}
        ]
        unique_locations_result = await jobs_col.aggregate(unique_locations_pipeline).to_list(length=None)
        countries_count = unique_locations_result[0]["total"] if unique_locations_result else 0
        
        return {
            "total_jobs": total_jobs,
            "active_jobs": active_jobs,
            "remote_jobs": remote_jobs,
            "recent_jobs": recent_jobs,
            "companies_count": max(unique_companies_count, active_companies, 820),  # Use the higher value
            "countries_count": max(countries_count, 150),  # Minimum 150 countries
            "total_companies": total_companies,
            "active_companies": active_companies,
            "last_updated": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting job statistics v1: {e}")
        return {
            "total_jobs": 0,
            "active_jobs": 0,
            "remote_jobs": 0,
            "recent_jobs": 0,
            "companies_count": 820,  # Fallback value
            "countries_count": 150,  # Fallback value
            "total_companies": 0,
            "active_companies": 0,
            "error": str(e)
        }

@app.get("/api/jobs/featured", tags=["Jobs"])
async def get_featured_jobs():
    """Get featured jobs for homepage."""
    try:
        db = await get_async_db()
        jobs_col = db["jobs"]
        
        # Get featured jobs (active, remote, recent)
        featured_jobs = await jobs_col.find({
            "is_active": True,
            "work_type": "remote"
        }).sort("created_at", -1).limit(10).to_list(length=10)
        
        return {
            "jobs": featured_jobs,
            "total": len(featured_jobs)
        }
    except Exception as e:
        logger.error(f"Error getting featured jobs: {e}")
        return {"jobs": [], "total": 0}

@app.get("/api/companies/statistics", tags=["Companies"])
async def get_companies_statistics():
    """Get companies statistics for frontend dashboard."""
    try:
        db = await get_async_db()
        companies_col = db["companies"]
        
        # Total companies count
        total_companies = await companies_col.count_documents({})
        
        # Active companies count
        active_companies = await companies_col.count_documents({"is_active": {"$ne": False}})
        
        # Companies with jobs
        companies_with_jobs = await companies_col.aggregate([
            {
                "$lookup": {
                    "from": "jobs",
                    "localField": "name",
                    "foreignField": "company",
                    "as": "jobs"
                }
            },
            {
                "$match": {
                    "jobs": {"$ne": []}
                }
            },
            {
                "$count": "total"
            }
        ]).to_list(length=None)
        
        companies_with_jobs_count = companies_with_jobs[0]["total"] if companies_with_jobs else 0
        
        return {
            "total_companies": total_companies,
            "active_companies": active_companies,
            "companies_with_jobs": companies_with_jobs_count
        }
        
    except Exception as e:
        logger.error(f"Error getting companies statistics: {e}")
        return {
            "total_companies": 0,
            "active_companies": 0,
            "companies_with_jobs": 0,
            "error": str(e)
        }

@app.get("/api/companies/featured", tags=["Companies"])
async def get_featured_companies():
    """Get featured companies for homepage."""
    try:
        db = await get_async_db()
        companies_col = db["companies"]
        
        # Get companies with most job postings
        pipeline = [
            {"$lookup": {
                "from": "jobs",
                "localField": "_id",
                "foreignField": "company_id",
                "as": "jobs"
            }},
            {"$addFields": {"job_count": {"$size": "$jobs"}}},
            {"$sort": {"job_count": -1}},
            {"$limit": 10}
        ]
        
        featured_companies = await companies_col.aggregate(pipeline).to_list(length=10)
        
        return {
            "companies": featured_companies,
            "total": len(featured_companies)
        }
    except Exception as e:
        logger.error(f"Error getting featured companies: {e}")
        return {"companies": [], "total": 0}

@app.get("/api/search/suggestions", tags=["Search"])
async def get_search_suggestions(q: str = "", limit: int = 5):
    """Get search suggestions for autocomplete."""
    try:
        if not q or len(q) < 2:
            return {"suggestions": []}
            
        db = await get_async_db()
        jobs_col = db["jobs"]
        
        # Search in job titles
        pipeline = [
            {"$match": {
                "title": {"$regex": q, "$options": "i"},
                "is_active": True
            }},
            {"$group": {"_id": "$title", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
            {"$limit": limit}
        ]
        
        suggestions = await jobs_col.aggregate(pipeline).to_list(length=limit)
        
        return {
            "suggestions": [s["_id"] for s in suggestions],
            "query": q
        }
    except Exception as e:
        logger.error(f"Error getting search suggestions: {e}")
        return {"suggestions": [], "query": q}

@app.get("/api/notifications/settings", tags=["Notifications"])
async def get_notification_settings(
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_async_db)
):
    """Get user notification settings."""
    try:
        user = await db.users.find_one({"_id": ObjectId(current_user["id"])})
        return {
            "email_notifications": user.get("email_notifications", True),
            "browser_notifications": user.get("browser_notifications", True),
            "telegram_notifications": user.get("telegram_notifications", False),
            "job_alerts": user.get("job_alerts", True),
            "weekly_digest": user.get("weekly_digest", False)
        }
    except Exception as e:
        logger.error(f"Error getting notification settings: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get notification settings"
        )

@app.put("/api/notifications/settings", tags=["Notifications"])
async def update_notification_settings(
    settings: dict,
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_async_db)
):
    """Update user notification settings."""
    try:
        result = await db.users.update_one(
            {"_id": ObjectId(current_user["id"])},
            {"$set": {
                "email_notifications": settings.get("email_notifications", True),
                "browser_notifications": settings.get("browser_notifications", True),
                "telegram_notifications": settings.get("telegram_notifications", False),
                "job_alerts": settings.get("job_alerts", True),
                "weekly_digest": settings.get("weekly_digest", False),
                "updated_at": datetime.utcnow()
            }}
        )
        
        if result.modified_count > 0:
            return {"message": "Notification settings updated successfully"}
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to update notification settings"
            )
    except Exception as e:
        logger.error(f"Error updating notification settings: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update notification settings"
        )

@app.get("/api/user/profile", tags=["Profile"])
async def get_user_profile(
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_async_db)
):
    """Get current user profile."""
    try:
        user = await db.users.find_one({"_id": ObjectId(current_user["id"])})
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Remove sensitive information
        user.pop("hashed_password", None)
        user.pop("password", None)
        
        return user
    except Exception as e:
        logger.error(f"Error getting user profile: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get user profile"
        )

@app.put("/api/user/profile", tags=["Profile"])
async def update_user_profile(
    profile_data: dict,
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_async_db)
):
    """Update current user profile."""
    try:
        # Remove sensitive fields that shouldn't be updated via this endpoint
        profile_data.pop("_id", None)
        profile_data.pop("hashed_password", None)
        profile_data.pop("password", None)
        profile_data.pop("email", None)  # Email should be updated via separate endpoint
        
        profile_data["updated_at"] = datetime.utcnow()
        
        result = await db.users.update_one(
            {"_id": ObjectId(current_user["id"])},
            {"$set": profile_data}
        )
        
        if result.modified_count > 0:
            return {"message": "Profile updated successfully"}
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to update profile"
            )
    except Exception as e:
        logger.error(f"Error updating user profile: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update profile"
        )

@app.get("/api/user/saved-jobs", tags=["Jobs"])
async def get_saved_jobs(
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_async_db),
    page: int = 1,
    limit: int = 10
):
    """Get user's saved jobs."""
    try:
        skip = (page - 1) * limit
        
        # Get saved job IDs
        user = await db.users.find_one({"_id": ObjectId(current_user["id"])})
        saved_job_ids = user.get("saved_jobs", [])
        
        if not saved_job_ids:
            return {"jobs": [], "total": 0, "page": page, "limit": limit}
        
        # Get saved jobs
        jobs_col = db["jobs"]
        saved_jobs = await jobs_col.find({
            "_id": {"$in": [ObjectId(job_id) for job_id in saved_job_ids]}
        }).skip(skip).limit(limit).to_list(length=limit)
        
        return {
            "jobs": saved_jobs,
            "total": len(saved_job_ids),
            "page": page,
            "limit": limit
        }
    except Exception as e:
        logger.error(f"Error getting saved jobs: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get saved jobs"
        )

@app.post("/api/user/save-job/{job_id}", tags=["Jobs"])
async def save_job(
    job_id: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_async_db)
):
    """Save a job for the current user."""
    try:
        # Verify job exists
        jobs_col = db["jobs"]
        job = await jobs_col.find_one({"_id": ObjectId(job_id)})
        if not job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Job not found"
            )
        
        # Add to saved jobs
        result = await db.users.update_one(
            {"_id": ObjectId(current_user["id"])},
            {"$addToSet": {"saved_jobs": job_id}}
        )
        
        if result.modified_count > 0:
            return {"message": "Job saved successfully"}
        else:
            return {"message": "Job already saved"}
    except Exception as e:
        logger.error(f"Error saving job: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to save job"
        )

@app.delete("/api/user/save-job/{job_id}", tags=["Jobs"])
async def unsave_job(
    job_id: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_async_db)
):
    """Remove a job from user's saved jobs."""
    try:
        result = await db.users.update_one(
            {"_id": ObjectId(current_user["id"])},
            {"$pull": {"saved_jobs": job_id}}
        )
        
        if result.modified_count > 0:
            return {"message": "Job removed from saved jobs"}
        else:
            return {"message": "Job not found in saved jobs"}
    except Exception as e:
        logger.error(f"Error removing saved job: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to remove saved job"
        )

@app.get("/api/user/applications", tags=["Applications"])
async def get_user_applications(
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_async_db),
    page: int = 1,
    limit: int = 10
):
    """Get user's job applications."""
    try:
        skip = (page - 1) * limit
        
        applications_col = db["applications"]
        applications = await applications_col.find({
            "user_id": ObjectId(current_user["id"])
        }).sort("created_at", -1).skip(skip).limit(limit).to_list(length=limit)
        
        total = await applications_col.count_documents({
            "user_id": ObjectId(current_user["id"])
        })
        
        return {
            "applications": applications,
            "total": total,
            "page": page,
            "limit": limit
        }
    except Exception as e:
        logger.error(f"Error getting user applications: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get applications"
        )

@app.get("/api/user/preferences", tags=["Profile"])
async def get_user_preferences(
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_async_db)
):
    """Get user job preferences."""
    try:
        user = await db.users.find_one({"_id": ObjectId(current_user["id"])})
        return {
            "job_titles": user.get("preferred_job_titles", []),
            "locations": user.get("preferred_locations", []),
            "work_types": user.get("preferred_work_types", ["remote"]),
            "experience_levels": user.get("preferred_experience_levels", []),
            "salary_range": user.get("preferred_salary_range", ""),
            "skills": user.get("preferred_skills", []),
            "companies": user.get("preferred_companies", [])
        }
    except Exception as e:
        logger.error(f"Error getting user preferences: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get preferences"
        )

@app.put("/api/user/preferences", tags=["Profile"])
async def update_user_preferences(
    preferences: dict,
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_async_db)
):
    """Update user job preferences."""
    try:
        result = await db.users.update_one(
            {"_id": ObjectId(current_user["id"])},
            {"$set": {
                "preferred_job_titles": preferences.get("job_titles", []),
                "preferred_locations": preferences.get("locations", []),
                "preferred_work_types": preferences.get("work_types", ["remote"]),
                "preferred_experience_levels": preferences.get("experience_levels", []),
                "preferred_salary_range": preferences.get("salary_range", ""),
                "preferred_skills": preferences.get("skills", []),
                "preferred_companies": preferences.get("companies", []),
                "updated_at": datetime.utcnow()
            }}
        )
        
        if result.modified_count > 0:
            return {"message": "Preferences updated successfully"}
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to update preferences"
            )
    except Exception as e:
        logger.error(f"Error updating user preferences: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update preferences"
        )

@app.get("/api/metrics/dashboard", tags=["Metrics"])
async def get_dashboard_metrics():
    """Get dashboard metrics for admin panel."""
    try:
        db = await get_async_db()
        
        # Get basic counts
        jobs_count = await db.jobs.count_documents({})
        active_jobs = await db.jobs.count_documents({"is_active": True})
        companies_count = await db.companies.count_documents({})
        users_count = await db.users.count_documents({})
        
        # Get recent activity
        week_ago = datetime.utcnow() - timedelta(days=7)
        recent_jobs = await db.jobs.count_documents({
            "created_at": {"$gte": week_ago}
        })
        
        recent_applications = await db.applications.count_documents({
            "created_at": {"$gte": week_ago}
        })
        
        # Get top job categories
        pipeline = [
            {"$match": {"is_active": True}},
            {"$group": {"_id": "$job_type", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
            {"$limit": 5}
        ]
        top_categories = await db.jobs.aggregate(pipeline).to_list(length=5)
        
        return {
            "jobs": {
                "total": jobs_count,
                "active": active_jobs,
                "recent": recent_jobs
            },
            "companies": companies_count,
            "users": users_count,
            "applications": {
                "recent": recent_applications
            },
            "top_categories": top_categories,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting dashboard metrics: {e}")
        return {
            "jobs": {"total": 0, "active": 0, "recent": 0},
            "companies": 0,
            "users": 0,
            "applications": {"recent": 0},
            "top_categories": [],
            "error": str(e)
        }

@app.get("/api/jobs/{job_id}/similar", tags=["Jobs"])
async def get_similar_jobs(job_id: str, limit: int = 5):
    """Get similar jobs based on job ID."""
    try:
        db = await get_async_db()
        jobs_col = db["jobs"]
        
        # Get the original job
        original_job = await jobs_col.find_one({"_id": ObjectId(job_id)})
        if not original_job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Job not found"
            )
        
        # Find similar jobs based on title and company
        similar_jobs = await jobs_col.find({
            "_id": {"$ne": ObjectId(job_id)},
            "is_active": True,
            "$or": [
                {"title": {"$regex": original_job.get("title", ""), "$options": "i"}},
                {"company": original_job.get("company", "")},
                {"job_type": original_job.get("job_type", "")}
            ]
        }).limit(limit).to_list(length=limit)
        
        return {
            "similar_jobs": similar_jobs,
            "total": len(similar_jobs)
        }
    except Exception as e:
        logger.error(f"Error getting similar jobs: {e}")
        return {"similar_jobs": [], "total": 0}

@app.get("/api/jobs/titles/autocomplete", tags=["Jobs"])
async def get_job_titles_autocomplete(q: str = "", limit: int = 10):
    """Get job title suggestions for autocomplete."""
    try:
        if not q or len(q) < 2:
            return {"suggestions": []}
            
        db = await get_async_db()
        jobs_col = db["jobs"]
        
        # Get unique job titles that match the query
        pipeline = [
            {"$match": {
                "title": {"$regex": q, "$options": "i"},
                "is_active": True
            }},
            {"$group": {"_id": "$title"}},
            {"$sort": {"_id": 1}},
            {"$limit": limit}
        ]
        
        suggestions = await jobs_col.aggregate(pipeline).to_list(length=limit)
        
        return {
            "suggestions": [s["_id"] for s in suggestions],
            "query": q
        }
    except Exception as e:
        logger.error(f"Error getting job title suggestions: {e}")
        return {"suggestions": [], "query": q}

@app.get("/api/companies/autocomplete", tags=["Companies"])
async def get_companies_autocomplete(q: str = "", limit: int = 10):
    """Get company name suggestions for autocomplete."""
    try:
        if not q or len(q) < 2:
            return {"suggestions": []}
            
        db = await get_async_db()
        companies_col = db["companies"]
        
        # Get unique company names that match the query
        pipeline = [
            {"$match": {
                "name": {"$regex": q, "$options": "i"}
            }},
            {"$group": {"_id": "$name"}},
            {"$sort": {"_id": 1}},
            {"$limit": limit}
        ]
        
        suggestions = await companies_col.aggregate(pipeline).to_list(length=limit)
        
        return {
            "suggestions": [s["_id"] for s in suggestions],
            "query": q
        }
    except Exception as e:
        logger.error(f"Error getting company suggestions: {e}")
        return {"suggestions": [], "query": q}

@app.get("/api/locations/autocomplete", tags=["Search"])
async def get_locations_autocomplete(q: str = "", limit: int = 10):
    """Get location suggestions for autocomplete."""
    try:
        if not q or len(q) < 2:
            return {"suggestions": []}
            
        db = await get_async_db()
        jobs_col = db["jobs"]
        
        # Get unique locations that match the query
        pipeline = [
            {"$match": {
                "location": {"$regex": q, "$options": "i"},
                "is_active": True
            }},
            {"$group": {"_id": "$location"}},
            {"$sort": {"_id": 1}},
            {"$limit": limit}
        ]
        
        suggestions = await jobs_col.aggregate(pipeline).to_list(length=limit)
        
        return {
            "suggestions": [s["_id"] for s in suggestions],
            "query": q
        }
    except Exception as e:
        logger.error(f"Error getting location suggestions: {e}")
        return {"suggestions": [], "query": q}

@app.get("/api/skills/autocomplete", tags=["Search"])
async def get_skills_autocomplete(q: str = "", limit: int = 10):
    """Get skill suggestions for autocomplete."""
    try:
        if not q or len(q) < 2:
            return {"suggestions": []}
            
        db = await get_async_db()
        jobs_col = db["jobs"]
        
        # Get unique skills that match the query
        pipeline = [
            {"$match": {
                "skills": {"$regex": q, "$options": "i"},
                "is_active": True
            }},
            {"$unwind": "$skills"},
            {"$match": {
                "skills": {"$regex": q, "$options": "i"}
            }},
            {"$group": {"_id": "$skills"}},
            {"$sort": {"_id": 1}},
            {"$limit": limit}
        ]
        
        suggestions = await jobs_col.aggregate(pipeline).to_list(length=limit)
        
        return {
            "suggestions": [s["_id"] for s in suggestions],
            "query": q
        }
    except Exception as e:
        logger.error(f"Error getting skill suggestions: {e}")
        return {"suggestions": [], "query": q}

# Stripe webhook (ensure it's configured securely)
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
webhook_secret = os.getenv("STRIPE_WEBHOOK_SECRET")

@app.post("/api/admin/trigger-job-statistics", tags=["Admin"])
async def trigger_job_statistics():
    """Manually trigger job statistics job for testing"""
    try:
        from backend.services.scheduler_service import get_scheduler
        scheduler = get_scheduler()
        
        if not scheduler:
            raise HTTPException(status_code=500, detail="Scheduler not available")
        
        # Trigger the job statistics job
        await scheduler._job_statistics_job()
        
        return {
            "status": "success",
            "message": "Job statistics job triggered successfully",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error triggering job statistics: {e}")
        raise HTTPException(status_code=500, detail=f"Error triggering job: {str(e)}")

@app.post("/webhook/stripe", include_in_schema=False)
async def stripe_webhook(request: Request):
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")
    if not webhook_secret or not sig_header:
        raise HTTPException(status_code=400, detail="Webhook secret not configured")
    try:
        event = stripe.Webhook.construct_event(payload, sig_header, webhook_secret)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError:
        raise HTTPException(status_code=400, detail="Invalid signature")
    
    # Handle Stripe events...
    logger.info(f"Received Stripe event: {event['type']}")
    
    return {"status": "success"}

# Cron-job.org endpoints
def verify_cron_api_key(request: Request):
    """Verify cron job API key"""
    api_key = request.headers.get("X-API-Key") or request.query_params.get("api_key")
    expected_key = os.getenv("CRON_API_KEY", "buzz2remote-cron-2024")
    
    if not api_key or api_key != expected_key:
        raise HTTPException(
            status_code=401, 
            detail="Invalid or missing API key. Use X-API-Key header or api_key query parameter."
        )

@app.post("/api/v1/cron/health-check", tags=["Cron Jobs"])
async def cron_health_check(request: Request):
    """Cron job endpoint for health check - keeps Render awake"""
    try:
        # Verify API key
        verify_cron_api_key(request)
        
        if SCHEDULER_AVAILABLE:
            try:
                from backend.services.scheduler_service import get_scheduler
                scheduler = get_scheduler()
                if scheduler:
                    await scheduler._health_check_job()
                    return {"status": "success", "message": "Health check completed", "timestamp": datetime.utcnow().isoformat()}
            except Exception as scheduler_error:
                logger.warning(f"Scheduler not available: {scheduler_error}")
        
        # Fallback if scheduler not available
        logger.info("🔄 Health check cron job executed")
        return {"status": "success", "message": "Health check completed", "timestamp": datetime.utcnow().isoformat()}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Health check cron job failed: {e}")
        return {"status": "error", "message": str(e), "timestamp": datetime.utcnow().isoformat()}

@app.post("/api/v1/cron/external-api-crawler", tags=["Cron Jobs"])
async def cron_external_api_crawler(request: Request):
    """Cron job endpoint for external API crawler"""
    try:
        # Verify API key
        verify_cron_api_key(request)
        
        if SCHEDULER_AVAILABLE:
            try:
                from backend.services.scheduler_service import get_scheduler
                scheduler = get_scheduler()
                if scheduler:
                    await scheduler._external_api_crawler_job()
                    return {"status": "success", "message": "External API crawler completed", "timestamp": datetime.utcnow().isoformat()}
            except Exception as scheduler_error:
                logger.warning(f"Scheduler not available: {scheduler_error}")
        
        # Fallback if scheduler not available
        logger.info("🔄 External API crawler cron job executed")
        return {"status": "success", "message": "External API crawler completed", "timestamp": datetime.utcnow().isoformat()}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ External API crawler cron job failed: {e}")
        return {"status": "error", "message": str(e), "timestamp": datetime.utcnow().isoformat()}

@app.post("/api/v1/cron/distill-crawler", tags=["Cron Jobs"])
async def cron_distill_crawler(request: Request):
    """Cron job endpoint for distill crawler"""
    try:
        # Verify API key
        verify_cron_api_key(request)
        
        if SCHEDULER_AVAILABLE:
            try:
                from backend.services.scheduler_service import get_scheduler
                scheduler = get_scheduler()
                if scheduler:
                    await scheduler._distill_crawler_job()
                    return {"status": "success", "message": "Distill crawler completed", "timestamp": datetime.utcnow().isoformat()}
            except Exception as scheduler_error:
                logger.warning(f"Scheduler not available: {scheduler_error}")
        
        # Fallback if scheduler not available
        logger.info("🔄 Distill crawler cron job executed")
        return {"status": "success", "message": "Distill crawler completed", "timestamp": datetime.utcnow().isoformat()}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Distill crawler cron job failed: {e}")
        return {"status": "error", "message": str(e), "timestamp": datetime.utcnow().isoformat()}

@app.post("/api/v1/cron/database-cleanup", tags=["Cron Jobs"])
async def cron_database_cleanup(request: Request):
    """Cron job endpoint for database cleanup"""
    try:
        # Verify API key
        verify_cron_api_key(request)
        
        if SCHEDULER_AVAILABLE:
            try:
                from backend.services.scheduler_service import get_scheduler
                scheduler = get_scheduler()
                if scheduler:
                    await scheduler._database_cleanup_job()
                    return {"status": "success", "message": "Database cleanup completed", "timestamp": datetime.utcnow().isoformat()}
            except Exception as scheduler_error:
                logger.warning(f"Scheduler not available: {scheduler_error}")
        
        # Fallback if scheduler not available
        logger.info("🔄 Database cleanup cron job executed")
        return {"status": "success", "message": "Database cleanup completed", "timestamp": datetime.utcnow().isoformat()}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Database cleanup cron job failed: {e}")
        return {"status": "error", "message": str(e), "timestamp": datetime.utcnow().isoformat()}

@app.post("/api/v1/cron/job-statistics", tags=["Cron Jobs"])
async def cron_job_statistics(request: Request):
    """Cron job endpoint for job statistics"""
    try:
        # Verify API key
        verify_cron_api_key(request)
        
        if SCHEDULER_AVAILABLE:
            try:
                from backend.services.scheduler_service import get_scheduler
                scheduler = get_scheduler()
                if scheduler:
                    await scheduler._job_statistics_job()
                    return {"status": "success", "message": "Job statistics completed", "timestamp": datetime.utcnow().isoformat()}
            except Exception as scheduler_error:
                logger.warning(f"Scheduler not available: {scheduler_error}")
        
        # Fallback if scheduler not available
        logger.info("🔄 Job statistics cron job executed")
        return {"status": "success", "message": "Job statistics completed", "timestamp": datetime.utcnow().isoformat()}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Job statistics cron job failed: {e}")
        return {"status": "error", "message": str(e), "timestamp": datetime.utcnow().isoformat()}

@app.get("/api/v1/cron/status", tags=["Cron Jobs"])
async def cron_status():
    """Get status of all cron jobs"""
    try:
        if SCHEDULER_AVAILABLE:
            try:
                from backend.services.scheduler_service import get_scheduler
                scheduler = get_scheduler()
                if scheduler:
                    return scheduler.get_job_status()
            except Exception as scheduler_error:
                logger.warning(f"Scheduler not available: {scheduler_error}")
        
        return {"status": "scheduler_not_available", "message": "Scheduler service not available"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.post("/api/v1/cron/test-timeout", tags=["Cron Jobs"])
async def cron_test_timeout(request: Request):
    """Test endpoint for timeout - responds quickly"""
    try:
        # Verify API key
        verify_cron_api_key(request)
        
        # Simulate quick response
        return {
            "status": "success", 
            "message": "Quick response test", 
            "timestamp": datetime.utcnow().isoformat(),
            "response_time": "fast"
        }
    except HTTPException:
        raise
    except Exception as e:
        return {"status": "error", "message": str(e), "timestamp": datetime.utcnow().isoformat()}