from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
from routes import auth, profile, jobs, ads, notification_routes
from database import get_db

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = FastAPI(title="Buzz2Remote API")

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
    logger.info("All routers included successfully")
except Exception as e:
    logger.error(f"Error including routers: {str(e)}")
    raise e

@app.on_event("startup")
async def startup_db_client():
    try:
        # Test database connection
        db = get_db()
        db.command('ismaster')
        logger.info("Connected to MongoDB successfully!")
    except Exception as e:
        logger.error(f"Could not connect to MongoDB: {str(e)}")
        raise e

@app.get("/")
async def root():
    return {"message": "Welcome to Buzz2Remote API"} 