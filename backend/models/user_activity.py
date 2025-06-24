from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum
import uuid

class ActivityType(str, Enum):
    """User activity types"""
    LOGIN = "login"
    LOGOUT = "logout"
    REGISTER = "register"
    PASSWORD_RESET = "password_reset"
    PROFILE_UPDATE = "profile_update"
    JOB_SEARCH = "job_search"
    JOB_VIEW = "job_view"
    JOB_APPLY = "job_apply"
    JOB_SAVE = "job_save"
    JOB_UNSAVE = "job_unsave"
    COMPANY_VIEW = "company_view"
    COMPANY_FOLLOW = "company_follow"
    CV_UPLOAD = "cv_upload"
    CV_PARSE = "cv_parse"
    ONBOARDING_STEP = "onboarding_step"
    SUBSCRIPTION_CHANGE = "subscription_change"
    NOTIFICATION_SETTINGS = "notification_settings"
    API_CALL = "api_call"
    ERROR_OCCURRED = "error_occurred"
    PAYMENT_INITIATED = "payment_initiated"
    PAYMENT_COMPLETED = "payment_completed"
    ADMIN_ACTION = "admin_action"
    EMAIL_VERIFICATION = "email_verification"
    LINKEDIN_CONNECT = "linkedin_connect"
    SESSION_START = "session_start"
    SESSION_END = "session_end"

class UserActivity(BaseModel):
    """User activity tracking model"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    activity_type: ActivityType
    
    # Request information
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    referer: Optional[str] = None
    
    # Activity details
    endpoint: Optional[str] = None
    method: Optional[str] = None
    status_code: Optional[int] = None
    response_time_ms: Optional[float] = None
    
    # Business logic data
    activity_data: Optional[Dict[str, Any]] = None
    
    # Location and device info
    country: Optional[str] = None
    city: Optional[str] = None
    device_type: Optional[str] = None  # mobile, desktop, tablet
    browser: Optional[str] = None
    os: Optional[str] = None
    
    # Timing
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    duration_seconds: Optional[float] = None
    
    # Error tracking
    error_message: Optional[str] = None
    error_type: Optional[str] = None
    stack_trace: Optional[str] = None
    
    # Additional metadata
    is_success: bool = True
    metadata: Optional[Dict[str, Any]] = None
    
    class Config:
        from_attributes = True

class UserSession(BaseModel):
    """User session tracking"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    session_token: str
    
    # Session details
    started_at: datetime = Field(default_factory=datetime.utcnow)
    last_activity: datetime = Field(default_factory=datetime.utcnow)
    ended_at: Optional[datetime] = None
    is_active: bool = True
    
    # Device and location
    ip_address: str
    user_agent: str
    device_fingerprint: Optional[str] = None
    country: Optional[str] = None
    city: Optional[str] = None
    
    # Activity summary
    total_requests: int = 0
    total_errors: int = 0
    pages_visited: List[str] = Field(default_factory=list)
    features_used: List[str] = Field(default_factory=list)
    
    # Performance metrics
    avg_response_time: Optional[float] = None
    total_session_time: Optional[float] = None
    
    class Config:
        from_attributes = True

class ActivitySummary(BaseModel):
    """Daily/weekly activity summary"""
    user_id: str
    date: datetime
    period_type: str  # daily, weekly, monthly
    
    # Activity counts
    total_activities: int = 0
    login_count: int = 0
    job_searches: int = 0
    job_views: int = 0
    job_applications: int = 0
    profile_updates: int = 0
    
    # Performance metrics
    avg_session_duration: Optional[float] = None
    total_time_spent: Optional[float] = None
    error_rate: Optional[float] = None
    
    # Feature usage
    features_used: List[str] = Field(default_factory=list)
    most_used_feature: Optional[str] = None
    
    class Config:
        from_attributes = True 