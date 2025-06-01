"""
Base models module for the backend application.
This file contains common models and database configurations.
"""

from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os
import enum

# Database base class
Base = declarative_base()

# Enums for telegram bot compatibility
class WorkType(enum.Enum):
    REMOTE = "remote"
    OFFICE = "office"
    HYBRID = "hybrid"

class JobType(enum.Enum):
    FULL_TIME = "full_time"
    PART_TIME = "part_time"
    CONTRACT = "contract"
    FREELANCE = "freelance"

class WorkHours(enum.Enum):
    FLEXIBLE = "flexible"
    FIXED = "fixed"

# Basic User model for compatibility
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    full_name = Column(String)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# User profile models for telegram bot compatibility
class UserProfile(Base):
    __tablename__ = "user_profiles"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    telegram_id = Column(String, unique=True, index=True)
    preferred_work_type = Column(Enum(WorkType))
    preferred_job_type = Column(Enum(JobType))
    preferred_work_hours = Column(Enum(WorkHours))
    skills = Column(String)
    location = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# Pydantic models for API compatibility
class UserProfileCreate:
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

class UserProfileUpdate:
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

class UserNotificationPreference:
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

# Basic Job model for compatibility
class Job(Base):
    __tablename__ = "jobs"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    company = Column(String, index=True)
    location = Column(String)
    description = Column(String)
    requirements = Column(String)
    salary_range = Column(String)
    job_type = Column(String)
    experience_level = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# Database engine configuration - use SQLite for compatibility
def get_database_url():
    """Get appropriate database URL based on environment."""
    database_url = os.getenv("DATABASE_URL", "")
    # Convert MongoDB URLs to SQLite for SQLAlchemy compatibility
    if database_url.startswith("mongodb"):
        return "sqlite:///./test.db"
    if not database_url:
        return "sqlite:///./test.db"
    return database_url

# Only create engine if not in testing mode
engine = None
SessionLocal = None

def initialize_database():
    """Initialize database engine and session."""
    global engine, SessionLocal
    if engine is None:
        DATABASE_URL = get_database_url()
        engine = create_engine(DATABASE_URL)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create tables
def create_tables():
    """Create all tables in the database."""
    initialize_database()
    if engine:
        Base.metadata.create_all(bind=engine)

# Get database session
def get_db():
    """Get database session."""
    initialize_database()
    if SessionLocal is None:
        return None
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 