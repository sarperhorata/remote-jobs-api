from fastapi import FastAPI, HTTPException, Request, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from starlette.middleware.sessions import SessionMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import logging
import sys
import os
import asyncio
from datetime import datetime
import stripe
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse, FileResponse

# Sentry configuration for error monitoring
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.logging import LoggingIntegration

# Initialize Sentry for error monitoring
sentry_sdk.init(
    dsn=os.getenv("SENTRY_DSN"),
    integrations=[
        FastApiIntegration(
            failed_request_status_codes={400, 401, 403, 404, 422, 500, 501, 502, 503}
        ),
        LoggingIntegration(
            level=logging.INFO,
            event_level=logging.ERROR
        ),
    ],
    traces_sample_rate=0.1,
    profiles_sample_rate=0.1,
    environment=os.getenv("ENVIRONMENT", "development"),
    release=os.getenv("RENDER_GIT_COMMIT", "unknown"),
    send_default_pii=True,
    max_breadcrumbs=50,
    before_send=lambda event, hint: event if event.get('level') != 'debug' else None,
)

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.routes import auth, profile, jobs, ads, notification_routes, companies, payment, onboarding, applications, translation
from backend.routes.ai_recommendations import router as ai_router
from backend.routes.legal import router as legal_router
from backend.routes.fake_job_detection import router as fake_job_router
from backend.routes.sentry_webhook import router as sentry_webhook_router
from backend.database.db import get_async_db, close_db_connections, init_database

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
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, restrict this to your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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
    (auth.router, "/api", ["auth"]),
    (onboarding.router, "/api", ["onboarding"]),
    (profile.router, "/api", ["profile"]),
    (jobs.router, "/api", ["jobs"]),
    (ads.router, "/api", ["ads"]),
    (notification_routes.router, "/api", ["notifications"]),
    (companies.router, "/api", ["companies"]),
    (legal_router, "/api", ["legal"]),
    (payment.router, "/api", ["payment"]),
    (applications.router, "/api", ["applications"]),
    (translation.router, "/api", ["translation"]),
    (ai_router, "/api", ["ai"]),
    (fake_job_router, "/api", ["fake-job-detection"]),
    (sentry_webhook_router, "/api", ["webhooks"])
]

for router, prefix, tags in routers_to_include:
    app.include_router(router, prefix=prefix, tags=tags)
    
# Optional: Include admin panel router if available and enabled
try:
    from backend.admin_panel.routes import admin_router
    if os.getenv("ADMIN_PANEL_ENABLED", "true").lower() == "true":
        app.include_router(admin_router, prefix="/admin", tags=["admin"])
        logger.info("Admin panel successfully included.")
except ImportError:
    logger.warning("Admin panel not found, skipping.")

@app.get("/", tags=["General"])
async def root():
    return {"message": "Welcome to Buzz2Remote API v3"}

@app.get("/health", tags=["General"])
async def health_check():
    db_status = "disconnected"
    try:
        db = await get_async_db()
        await db.command('ping')
        db_status = "connected"
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        
    return {"status": "healthy", "database": db_status}

# Stripe webhook (ensure it's configured securely)
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
webhook_secret = os.getenv("STRIPE_WEBHOOK_SECRET")

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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8001, reload=True) 