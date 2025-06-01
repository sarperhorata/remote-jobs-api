from fastapi import FastAPI, HTTPException, Request, Body
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from fastapi.staticfiles import StaticFiles
import logging
import sys
import os
import asyncio
from datetime import datetime
import stripe

# Add admin panel to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.routes import auth, profile, jobs, ads, notification_routes, companies, payment
from backend.routes.legal import router as legal_router
from backend.database import get_async_db, ensure_indexes

# Import Telegram bot
# try:
#     from telegram_bot.bot import RemoteJobsBot
#     TELEGRAM_BOT_AVAILABLE = True
# except ImportError as e:
#     logging.warning(f"Telegram bot not available: {e}")
#     TELEGRAM_BOT_AVAILABLE = False
TELEGRAM_BOT_AVAILABLE = False  # Temporarily disabled due to conflicts

# Import scheduler service
# try:
#     from services.scheduler_service import start_scheduler, stop_scheduler, get_scheduler
#     SCHEDULER_AVAILABLE = True
# except ImportError as e:
#     logging.warning(f"Scheduler service not available: {e}")
#     SCHEDULER_AVAILABLE = False
SCHEDULER_AVAILABLE = False  # Temporarily disabled

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
    title="🚀 Buzz2Remote API",
    description="""
    **The Ultimate Remote Jobs Platform API**
    
    Welcome to Buzz2Remote API - Your gateway to remote opportunities worldwide!
    
    ## 🌟 Key Features
    
    * **36,000+ Active Remote Jobs** from 375+ companies worldwide
    * **AI-Enhanced CV Parsing** with intelligent skill extraction
    * **Real-time Job Crawling** from top company career pages
    * **Advanced Search & Filtering** with location, skills, and salary filters
    * **LinkedIn OAuth Integration** for seamless user experience
    * **Real-time Notifications** via Telegram bot integration
    * **Cloud-based Cronjobs** for automated data updates
    * **Admin Panel** for comprehensive job management
    
    ## 🔧 API Endpoints
    
    ### 🔑 Authentication
    - Login/Register with email or LinkedIn OAuth
    - JWT-based secure authentication
    - Profile management and preferences
    
    ### 💼 Jobs
    - Search and filter remote jobs
    - Get job recommendations based on profile
    - Save favorite jobs and track applications
    - Advanced search with AI-powered matching
    
    ### 🏢 Companies  
    - Browse 375+ remote-friendly companies
    - Get company profiles and job listings
    - Follow companies for updates
    
    ### 📊 Analytics
    - Job market statistics and trends
    - Salary insights and location data
    - Skill demand analytics
    
    ### 🔔 Notifications
    - Real-time job alerts
    - Telegram bot integration
    - Custom notification preferences
    
    ## 🛡️ Security & Performance
    
    - **Rate Limited** for fair usage
    - **Input Validated** for security
    - **Cached Results** for optimal performance
    - **MongoDB Atlas** for reliable data storage
    - **Cloud Infrastructure** on Render.com
    
    ## 📞 Support
    
    - **GitHub**: [github.com/sarperhorata/remote-jobs-api](https://github.com/sarperhorata/remote-jobs-api)
    - **Admin Panel**: [/admin](/admin)
    - **Status Page**: [/health](/health)
    
    ---
    *Built with ❤️ for the remote work community*
    """,
    version="2.1.0",
    docs_url="/docs",  # Swagger UI at /docs
    redoc_url="/redoc",  # ReDoc at /redoc
    openapi_url="/openapi.json",  # OpenAPI schema at /openapi.json
    contact={
        "name": "Buzz2Remote Team",
        "url": "https://github.com/sarperhorata/remote-jobs-api",
        "email": "support@buzz2remote.com"
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT"
    },
    servers=[
        {
            "url": "https://buzz2remote-api.onrender.com",
            "description": "Production server"
        },
        {
            "url": "http://localhost:8000",
            "description": "Development server"
        }
    ]
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
    app.include_router(legal_router, prefix="/api", tags=["legal"])
    app.include_router(payment.router, prefix="/api", tags=["payment"])
    
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

# Initialize Stripe
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
webhook_secret = os.getenv("STRIPE_WEBHOOK_SECRET")

@app.on_event("startup")
async def startup_db_client():
    global telegram_bot, scheduler
    
    try:
        # Initialize database connection pool - use db directly instead of the generator
        from backend.database import db
        await db.command('ping')
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
        from backend.database import close_db_connections
        close_db_connections()
        logger.info("Database connections closed")
    except Exception as e:
        logger.error(f"Error closing database connections: {str(e)}")

@app.get("/", 
    summary="🏠 API Welcome & Information",
    description="""
    **Welcome to Buzz2Remote API!**
    
    This endpoint provides basic information about the API, current status, and available features.
    Perfect for health checks and getting started with our platform.
    
    ### Response includes:
    - API version and status
    - Available features overview  
    - Links to documentation and admin panel
    - GitHub repository information
    - Current service statistics
    """,
    response_description="Welcome message with comprehensive API information and status",
    tags=["General"],
    responses={
        200: {
            "description": "API information retrieved successfully",
            "content": {
                "application/json": {
                    "example": {
                        "message": "Welcome to Buzz2Remote API",
                        "version": "2.1.0",
                        "status": "active",
                        "features": [
                            "AI-Enhanced CV Parsing",
                            "375+ Company Job Crawling",
                            "LinkedIn OAuth Integration",
                            "Advanced Job Search & Matching"
                        ]
                    }
                }
            }
        }
    }
)
async def root():
    """
    🎯 **API Root Endpoint**
    
    Returns comprehensive information about the Buzz2Remote API including:
    - Current service status and version
    - Complete feature list and capabilities  
    - Documentation and admin panel links
    - Real-time service statistics
    
    This endpoint is perfect for:
    - ✅ Health checks and monitoring
    - 📖 Getting API overview for new developers  
    - 🔗 Finding links to documentation and tools
    - 📊 Quick service status verification
    """
    return {
        "message": "Welcome to Buzz2Remote API", 
        "version": "2.1.0",
        "status": "active",
        "description": "The Ultimate Remote Jobs Platform API",
        "features": [
            "🤖 AI-Enhanced CV Parsing",
            "🏢 375+ Company Job Crawling", 
            "🔗 LinkedIn OAuth Integration",
            "🔍 Advanced Job Search & Matching",
            "📊 Real-time Job Analytics",
            "🔔 Telegram Notifications",
            "☁️ Cloud-based Cronjobs",
            "🛡️ Automated Health Checks"
        ],
        "statistics": {
            "total_jobs": "36,000+",
            "total_companies": "375+",
            "active_apis": 8,
            "daily_updates": "1,000+"
        },
        "documentation": {
            "swagger_ui": "/docs",
            "redoc": "/redoc", 
            "openapi_schema": "/openapi.json"
        },
        "admin_panel": "/admin",
        "health_check": "/health",
        "github": "https://github.com/sarperhorata/remote-jobs-api",
        "contact": "support@buzz2remote.com"
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

@app.post("/webhook/stripe")
async def stripe_webhook(request: Request):
    """Handle Stripe webhook events"""
    try:
        payload = await request.body()
        sig_header = request.headers.get("stripe-signature")

        if not sig_header:
            raise HTTPException(status_code=400, detail="No Stripe signature found")

        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, webhook_secret
            )
        except ValueError as e:
            raise HTTPException(status_code=400, detail="Invalid payload")
        except stripe.error.SignatureVerificationError as e:
            raise HTTPException(status_code=400, detail="Invalid signature")

        # Handle the event
        if event.type == "checkout.session.completed":
            session = event.data.object
            # Handle successful payment
            # Update user's subscription status
            # Send confirmation email
            logger.info(f"Payment successful for session {session.id}")
            
        elif event.type == "customer.subscription.updated":
            subscription = event.data.object
            # Handle subscription update
            # Update user's subscription status
            logger.info(f"Subscription updated: {subscription.id}")
            
        elif event.type == "customer.subscription.deleted":
            subscription = event.data.object
            # Handle subscription cancellation
            # Update user's subscription status
            logger.info(f"Subscription cancelled: {subscription.id}")

        return {"status": "success"}

    except Exception as e:
        logger.error(f"Error processing webhook: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    import os
    
    # Get configuration from environment variables
    host = os.getenv('API_HOST', '0.0.0.0')
    port = int(os.getenv('API_PORT', 5001))
    
    uvicorn.run(app, host=host, port=port) 