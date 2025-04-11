import asyncio
import logging
import os
from fastapi import FastAPI, HTTPException, Depends, Query, Request
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import threading
from apscheduler.schedulers.background import BackgroundScheduler
from utils.cronjob import wake_up_render
from middleware.security import SecurityMiddleware
from utils.db import test_connection
from utils.scheduler import setup_scheduler
from fastapi.responses import JSONResponse
from dotenv import load_dotenv

from api import monitors, notifications, websites, jobs
from crawler.monitor_manager import MonitorManager
from telegram_bot.bot import RemoteJobsBot
from utils.config import API_HOST, API_PORT, API_DEBUG, API_RELOAD, CORS_ORIGINS, CORS_ALLOW_CREDENTIALS

# Load environment variables
load_dotenv()

# Logging configuration
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Create FastAPI application
app = FastAPI(
    title="Remote Jobs Monitor API",
    description="API that monitors job listings and notifies about changes",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add security middleware
app.add_middleware(SecurityMiddleware)

# Add API routers
app.include_router(monitors.router, prefix="/api/monitors", tags=["Monitors"])
app.include_router(notifications.router, prefix="/api/notifications", tags=["Notifications"])
app.include_router(websites.router, prefix="/api/websites", tags=["Websites"])
app.include_router(jobs.router, prefix="/api/jobs", tags=["Jobs"])

# Monitor Manager instance
monitor_manager = MonitorManager()

# Telegram Bot instance
telegram_bot = RemoteJobsBot()
# Thread for running the Telegram bot
telegram_bot_thread = None

# Initialize scheduler
scheduler = BackgroundScheduler()
scheduler.add_job(wake_up_render, 'interval', minutes=10)
scheduler.start()

RENDER_URL = os.getenv('RENDER_URL', 'https://remote-jobs-62gn.onrender.com')

@app.on_event("startup")
async def startup_event():
    """
    Runs when the application starts
    """
    logger.info("Starting application...")
    
    # Create data directory
    os.makedirs("data", exist_ok=True)
    
    # Start Monitor Manager
    await monitor_manager.start()
    
    # Start Telegram bot in a separate thread
    global telegram_bot_thread
    telegram_bot_thread = threading.Thread(target=start_telegram_bot)
    telegram_bot_thread.daemon = True  # The thread will exit when the main thread exits
    telegram_bot_thread.start()
    logger.info("Telegram bot started in separate thread")

    # Test MongoDB connection
    if test_connection():
        logger.info("MongoDB connection successful")
    else:
        logger.error("MongoDB connection failed")

    # Set up scheduler
    scheduler = setup_scheduler()
    app.state.scheduler = scheduler
    logger.info("Application startup complete")

def start_telegram_bot():
    """
    Start the Telegram bot (this runs in a separate thread)
    """
    try:
        telegram_bot.run()
    except Exception as e:
        logger.error(f"Error running Telegram bot: {e}")

@app.on_event("shutdown")
async def shutdown_event():
    """
    Runs when the application shuts down
    """
    logger.info("Shutting down application...")
    
    # Stop Monitor Manager
    await monitor_manager.stop()
    
    # The Telegram bot will stop automatically when the main thread exits
    # since it's running as a daemon thread

    scheduler.shutdown()

    # Shutdown scheduler
    if hasattr(app.state, "scheduler"):
        app.state.scheduler.shutdown()
    logger.info("Application shutdown complete")

@app.get("/")
async def root():
    """
    Home page
    """
    return {
        "app": "Remote Jobs Monitor API",
        "version": "0.1.0",
        "endpoints": {
            "monitors": "/api/monitors",
            "notifications": "/api/notifications",
            "websites": "/api/websites",
            "jobs": "/api/jobs",
        },
        "telegram_bot": "Running" if telegram_bot_thread and telegram_bot_thread.is_alive() else "Not running"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# Error handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Global exception handler caught: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "An unexpected error occurred"},
    )

if __name__ == "__main__":
    uvicorn.run(
        "main:app", 
        host=API_HOST, 
        port=API_PORT,
        reload=API_RELOAD,
        log_level="info"
    ) 