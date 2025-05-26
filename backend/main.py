from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
import sys
import os
import asyncio
from datetime import datetime

# Add admin panel to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from routes import auth, profile, jobs, ads, notification_routes
from database import get_db

# Import Telegram bot
try:
    from telegram_bot.bot import RemoteJobsBot
    TELEGRAM_BOT_AVAILABLE = True
except ImportError as e:
    logging.warning(f"Telegram bot not available: {e}")
    TELEGRAM_BOT_AVAILABLE = False

# Import admin panel
try:
    from admin_panel.routes import admin_router
    ADMIN_PANEL_AVAILABLE = True
except ImportError as e:
    logging.warning(f"Admin panel not available: {e}")
    ADMIN_PANEL_AVAILABLE = False

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Global bot instance
telegram_bot = None

# Create FastAPI app with custom docs URLs
app = FastAPI(
    title="Buzz2Remote API",
    description="API for Buzz2Remote - The Ultimate Remote Jobs Platform",
    version="2.0.0",
    docs_url="/docs",  # Swagger UI at /docs
    redoc_url="/redoc",  # ReDoc at /redoc
    openapi_url="/openapi.json"  # OpenAPI schema at /openapi.json
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
try:
    app.include_router(auth.router, prefix="/api", tags=["auth"])
    app.include_router(profile.router, prefix="/api", tags=["profile"])
    app.include_router(jobs.router, prefix="/api", tags=["jobs"])
    app.include_router(ads.router, prefix="/api", tags=["ads"])
    app.include_router(notification_routes.router, prefix="/api", tags=["notifications"])
    
    # Include admin panel if available
    if ADMIN_PANEL_AVAILABLE:
        app.include_router(admin_router, prefix="/admin")  # Admin panel at /admin/*
        logger.info("Admin panel included successfully")
    
    logger.info("All routers included successfully")
except Exception as e:
    logger.error(f"Error including routers: {str(e)}")
    raise e

@app.on_event("startup")
async def startup_db_client():
    global telegram_bot
    
    try:
        # Test database connection
        db = get_db()
        db.command('ismaster')
        logger.info("Connected to MongoDB successfully!")
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
                
                # Send startup notification
                startup_data = {
                    'environment': 'production' if os.getenv('ENVIRONMENT') == 'production' else 'development',
                    'status': 'success',
                    'commit': os.getenv('RENDER_GIT_COMMIT', 'unknown')[:8],
                    'message': 'Backend service started successfully',
                    'timestamp': datetime.now().isoformat()
                }
                await telegram_bot.send_deployment_notification(startup_data)
            else:
                logger.warning("Telegram bot is disabled")
        except Exception as e:
            logger.error(f"Failed to start Telegram bot: {str(e)}")
    else:
        logger.warning("Telegram bot not available")

@app.on_event("shutdown")
async def shutdown_event():
    global telegram_bot
    
    if telegram_bot and telegram_bot.enabled:
        try:
            await telegram_bot.stop()
            logger.info("Telegram bot stopped")
        except Exception as e:
            logger.error(f"Error stopping Telegram bot: {str(e)}")

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
            "Real-time Notifications"
        ],
        "documentation": "/docs",
        "admin_panel": "/admin",
        "github": "https://github.com/sarperhorata/remote-jobs-api"
    } 

@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring."""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

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