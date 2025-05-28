from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from fastapi.staticfiles import StaticFiles
import logging
import sys
import os
import asyncio
from datetime import datetime

# Add admin panel to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from routes import auth, profile, jobs, ads, notification_routes, companies
from database import get_db, get_async_db, ensure_indexes

# Import Telegram bot
try:
    from telegram_bot.bot import RemoteJobsBot
    TELEGRAM_BOT_AVAILABLE = True
except ImportError as e:
    logging.warning(f"Telegram bot not available: {e}")
    TELEGRAM_BOT_AVAILABLE = False

# Import scheduler service
try:
    from services.scheduler_service import start_scheduler, stop_scheduler, get_scheduler
    SCHEDULER_AVAILABLE = True
except ImportError as e:
    logging.warning(f"Scheduler service not available: {e}")
    SCHEDULER_AVAILABLE = False

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Import admin panel
try:
    # Use the root admin panel instead of backend admin panel
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from admin_panel.routes import admin_router
    ADMIN_PANEL_AVAILABLE = True
    logger.info("Admin panel imported successfully")
except ImportError as e:
    logging.warning(f"Admin panel not available: {e}")
    ADMIN_PANEL_AVAILABLE = False

# Global instances
telegram_bot = None
scheduler = None

# Create FastAPI app with custom docs URLs
app = FastAPI(
    title="Buzz2Remote API",
    description="API for Buzz2Remote - The Ultimate Remote Jobs Platform",
    version="2.0.0",
    docs_url="/docs",  # Swagger UI at /docs
    redoc_url="/redoc",  # ReDoc at /redoc
    openapi_url="/openapi.json"  # OpenAPI schema at /openapi.json
)

# Add session middleware for admin panel
app.add_middleware(
    SessionMiddleware,
    secret_key=os.getenv("SESSION_SECRET_KEY", "buzz2remote-secret-key-change-in-production")
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],  # Only allow frontend in development
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# Mount static files for admin panel
# Use root admin panel static files
admin_static_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "admin_panel", "static")
if os.path.exists(admin_static_path):
    app.mount("/admin/static", StaticFiles(directory=admin_static_path), name="admin_static")

# Include routers
try:
    app.include_router(auth.router, prefix="/api", tags=["auth"])
    app.include_router(profile.router, prefix="/api", tags=["profile"])
    app.include_router(jobs.router, prefix="/api", tags=["jobs"])
    app.include_router(ads.router, prefix="/api", tags=["ads"])
    app.include_router(notification_routes.router, prefix="/api", tags=["notifications"])
    app.include_router(companies.router, prefix="/api", tags=["companies"])
    
    # Include admin panel if available
    if ADMIN_PANEL_AVAILABLE:
        # Include admin router (no prefix needed as it's already defined in the router)
        app.include_router(admin_router, tags=["admin"])
        logger.info("Admin panel included successfully")
        logger.info(f"Admin routes: {[route.path for route in admin_router.routes]}")
    else:
        logger.warning("Admin panel not available - skipping inclusion")
    
    logger.info("All routers included successfully")
except Exception as e:
    logger.error(f"Error including routers: {str(e)}")
    raise e

@app.on_event("startup")
async def startup_db_client():
    global telegram_bot, scheduler
    
    try:
        # Initialize database connection pool
        db = get_db()
        db.command('ismaster')
        logger.info("Connected to MongoDB successfully!")
        
        # Pre-initialize async connection for better performance
        async_db = await get_async_db()
        await async_db.command('ping')
        logger.info("Async MongoDB connection pool initialized!")
        
        # Ensure indexes
        await ensure_indexes()
    except Exception as e:
        logger.error(f"Could not connect to MongoDB: {str(e)}")
        raise e
    
    # Initialize Telegram bot
    if TELEGRAM_BOT_AVAILABLE:
        try:
            telegram_bot = RemoteJobsBot()
            if telegram_bot.enabled:
                # Start bot in background
                asyncio.create_task(telegram_bot.run_async())
                logger.info("Telegram bot started successfully!")
                
                # Send comprehensive startup notification
                startup_data = {
                    'environment': 'production' if os.getenv('ENVIRONMENT') == 'production' else 'development',
                    'status': 'success',
                    'commit': os.getenv('RENDER_GIT_COMMIT', 'unknown')[:8],
                    'message': 'Backend service started successfully',
                    'timestamp': datetime.now().isoformat(),
                    'services': ['MongoDB Atlas', 'FastAPI', 'Telegram Bot', 'Scheduler Service'],
                    'endpoints': ['/docs', '/admin', '/api/jobs', '/scheduler/status'],
                    'features': ['External API Crawler', 'Buzz2Remote-Companies Crawler', 'Cloud Cronjobs']
                }
                await telegram_bot.send_deployment_notification(startup_data)
            else:
                logger.warning("Telegram bot is disabled")
        except Exception as e:
            logger.error(f"Failed to start Telegram bot: {str(e)}")
    else:
        logger.warning("Telegram bot not available")
    
    # Initialize scheduler service
    if SCHEDULER_AVAILABLE:
        try:
            scheduler = await start_scheduler()
            logger.info("Scheduler service started successfully!")
            
            # Send detailed scheduler startup notification
            if telegram_bot and telegram_bot.enabled:
                scheduler_data = {
                    'environment': 'production' if os.getenv('ENVIRONMENT') == 'production' else 'development',
                    'status': 'success',
                    'commit': os.getenv('RENDER_GIT_COMMIT', 'unknown')[:8],
                    'message': 'All cloud cronjobs are now active and running',
                    'timestamp': datetime.now().isoformat(),
                    'cronjobs': [
                        'Health Check (every 14 min)',
                        'External API Crawler (daily 9 AM UTC)',
                        'Buzz2Remote-Companies (daily 10 AM UTC)',
                        'Database Cleanup (weekly Sunday 2 AM UTC)',
                        'Job Statistics (daily 8 AM UTC)'
                    ]
                }
                await telegram_bot.send_deployment_notification(scheduler_data)
                
        except Exception as e:
            logger.error(f"Failed to start scheduler service: {str(e)}")
    else:
        logger.warning("Scheduler service not available")

@app.on_event("shutdown")
async def shutdown_event():
    global telegram_bot, scheduler
    
    # Stop scheduler
    if scheduler:
        try:
            await stop_scheduler()
            logger.info("Scheduler service stopped")
        except Exception as e:
            logger.error(f"Error stopping scheduler service: {str(e)}")
    
    # Stop Telegram bot
    if telegram_bot and telegram_bot.enabled:
        try:
            await telegram_bot.stop()
            logger.info("Telegram bot stopped")
        except Exception as e:
            logger.error(f"Error stopping Telegram bot: {str(e)}")
    
    # Close database connections
    try:
        from database import close_db_connections
        close_db_connections()
        logger.info("Database connections closed")
    except Exception as e:
        logger.error(f"Error closing database connections: {str(e)}")

@app.get("/", 
    summary="🏠 API Welcome Message",
    description="Welcome to Buzz2Remote API!",
    response_description="Welcome message with API status",
    tags=["General"]
)
async def root():
    """
    API Root Endpoint
    Returns welcome message and basic API information.
    """
    return {
        "message": "Welcome to Buzz2Remote API", 
        "version": "2.0.0",
        "status": "active",
        "features": [
            "AI-Enhanced CV Parsing",
            "471+ Company Job Crawling", 
            "LinkedIn OAuth Integration",
            "Advanced Job Search & Matching",
            "Real-time Notifications",
            "Cloud-based Cronjobs",
            "Automated Health Checks"
        ],
        "documentation": "/docs",
        "admin_panel": "/admin",
        "github": "https://github.com/sarperhorata/remote-jobs-api"
    } 

@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring."""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.get("/scheduler/status")
async def scheduler_status():
    """Get scheduler status and job information."""
    if scheduler:
        return scheduler.get_job_status()
    else:
        return {"status": "not_available", "message": "Scheduler service not initialized"}

# Add deployment notification endpoint
@app.post("/webhook/deployment")
async def deployment_webhook(deployment_data: dict):
    """Webhook endpoint for deployment notifications"""
    global telegram_bot
    
    if telegram_bot and telegram_bot.enabled:
        try:
            await telegram_bot.send_deployment_notification(deployment_data)
            return {"message": "Deployment notification sent successfully"}
        except Exception as e:
            logger.error(f"Failed to send deployment notification: {str(e)}")
            return {"error": str(e)}, 500
    else:
        return {"error": "Telegram bot not available"}, 503

if __name__ == "__main__":
    import uvicorn
    import os
    
    # Get configuration from environment variables
    host = os.getenv('API_HOST', '0.0.0.0')
    port = int(os.getenv('API_PORT', 5001))
    
    uvicorn.run(app, host=host, port=port) 