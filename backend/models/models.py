from pydantic import BaseModel, HttpUrl, Field, EmailStr
from typing import List, Optional, Dict, Any, Union
from enum import Enum
from datetime import datetime
from sqlalchemy import Column, Integer, BigInteger, String, Boolean, DateTime

class WebsiteType(str, Enum):
    REMOTE_OK = "remote_ok"
    WE_WORK_REMOTELY = "we_work_remotely"
    REMOTE_CO = "remote_co"
    JOBS_FROM_SPACE = "jobs_from_space"
    REMOTIVE = "remotive"
    CUSTOM = "custom"

class NotificationType(str, Enum):
    EMAIL = "email"
    TELEGRAM = "telegram"
    WEBHOOK = "webhook"

class WorkType(str, Enum):
    REMOTE = "remote"
    HYBRID = "hybrid"
    OFFICE = "office"
    ANY = "any"

class JobType(str, Enum):
    FULL_TIME = "full_time"
    PART_TIME = "part_time"
    CONTRACT = "contract"
    FREELANCE = "freelance"
    INTERNSHIP = "internship"
    ANY = "any"

class TravelRequirement(str, Enum):
    NO = "no"
    LIMITED = "limited"
    YES = "yes"
    ANY = "any"

class WorkHours(str, Enum):
    REGULAR = "regular"  # 9-5
    FLEXIBLE = "flexible"
    ANY = "any"

class MeetingFrequency(str, Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    BIWEEKLY = "biweekly"
    MONTHLY = "monthly"
    RARELY = "rarely"
    ANY = "any"

class SkillLevel(str, Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"

class LanguageLevel(str, Enum):
    ELEMENTARY = "elementary"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    NATIVE = "native"

class SelectorBase(BaseModel):
    name: str
    selector_type: str = "css"  # css, xpath
    value: str
    attribute: Optional[str] = None

class SelectorCreate(SelectorBase):
    pass

class Selector(SelectorBase):
    id: int
    website_id: int
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

class WebsiteBase(BaseModel):
    name: str
    url: HttpUrl
    website_type: WebsiteType = WebsiteType.CUSTOM
    is_active: bool = True
    selectors: Optional[List[SelectorBase]] = None
    headers: Optional[Dict[str, str]] = None
    params: Optional[Dict[str, str]] = None

class WebsiteCreate(WebsiteBase):
    selectors: List[SelectorCreate]

class Website(WebsiteBase):
    id: int
    selectors: List[Selector] = []
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

class MonitorBase(BaseModel):
    name: str
    website_id: int
    check_interval: int = 60  # Default check interval in minutes
    keywords: Optional[List[str]] = None
    exclude_keywords: Optional[List[str]] = None
    is_active: bool = True
    notify_on_change: bool = True

class MonitorCreate(MonitorBase):
    pass

class Monitor(MonitorBase):
    id: int
    created_at: datetime
    updated_at: datetime

class NotificationBase(BaseModel):
    name: str
    notification_type: NotificationType
    config: Dict[str, Any]  # Configuration for the notification type
    is_active: bool = True

class Notification(NotificationBase):
    id: int
    created_at: datetime
    updated_at: datetime

class NotificationCreate(NotificationBase):
    pass

class JobBase(BaseModel):
    title: str
    company: str
    url: HttpUrl
    description: Optional[str] = None
    location: Optional[str] = None
    salary: Optional[str] = None
    tags: Optional[List[str]] = None
    posted_date: Optional[datetime] = None
    is_remote: bool = True
    website_id: int
    raw_data: Optional[Dict[str, Any]] = None

class JobCreate(JobBase):
    monitor_id: int

class Job(JobBase):
    id: int
    created_at: datetime
    updated_at: datetime

class ChangeLogBase(BaseModel):
    monitor_id: int
    job_id: int
    change_type: str  # 'new', 'updated', 'removed'
    old_data: Optional[Dict[str, Any]] = None
    new_data: Optional[Dict[str, Any]] = None
    is_notified: bool = False

class ChangeLogCreate(ChangeLogBase):
    pass

class ChangeLog(ChangeLogBase):
    id: int
    created_at: datetime
    updated_at: datetime

# User Profile Models
class Skill(BaseModel):
    name: str
    level: SkillLevel
    years_experience: Optional[int] = None

class Language(BaseModel):
    name: str
    level: LanguageLevel

class Education(BaseModel):
    institution: str
    degree: str
    field_of_study: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    current: bool = False
    description: Optional[str] = None

class WorkExperience(BaseModel):
    title: str
    company: str
    location: Optional[str] = None
    start_date: datetime
    end_date: Optional[datetime] = None
    current: bool = False
    description: Optional[str] = None

class Certificate(BaseModel):
    name: str
    issuing_organization: str
    issue_date: Optional[datetime] = None
    expiration_date: Optional[datetime] = None
    credential_id: Optional[str] = None
    credential_url: Optional[HttpUrl] = None

class SalaryExpectation(BaseModel):
    amount: float
    currency: str = "USD"
    period: str = "year"  # year, month, hour

class WorkPreferences(BaseModel):
    work_type: WorkType = WorkType.ANY
    job_type: JobType = JobType.ANY
    travel_requirement: TravelRequirement = TravelRequirement.ANY
    work_hours: WorkHours = WorkHours.ANY
    timezone: Optional[str] = None
    meeting_frequency: MeetingFrequency = MeetingFrequency.ANY
    min_salary: Optional[SalaryExpectation] = None
    willing_to_relocate: bool = False
    preferred_locations: Optional[List[str]] = None
    
class UserProfileBase(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    phone: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None
    bio: Optional[str] = None
    profile_picture_url: Optional[HttpUrl] = None
    resume_url: Optional[HttpUrl] = None
    linkedin_url: Optional[HttpUrl] = None
    github_url: Optional[HttpUrl] = None
    portfolio_url: Optional[HttpUrl] = None
    skills: Optional[List[Skill]] = None
    languages: Optional[List[Language]] = None
    education: Optional[List[Education]] = None
    work_experience: Optional[List[WorkExperience]] = None
    certificates: Optional[List[Certificate]] = None
    work_preferences: Optional[WorkPreferences] = None
    is_active: bool = True
    is_premium: bool = False
    subscription_type: Optional[str] = None  # "free", "basic", "pro", "enterprise"
    subscription_expires: Optional[datetime] = None

class UserProfile(UserProfileBase):
    id: int
    telegram_chat_id: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    last_login: Optional[datetime] = None

class UserProfileCreate(UserProfileBase):
    password: str = Field(..., min_length=8)
    
class UserProfileUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None
    bio: Optional[str] = None
    profile_picture_url: Optional[HttpUrl] = None
    resume_url: Optional[HttpUrl] = None
    linkedin_url: Optional[HttpUrl] = None
    github_url: Optional[HttpUrl] = None
    portfolio_url: Optional[HttpUrl] = None
    skills: Optional[List[Skill]] = None
    languages: Optional[List[Language]] = None
    education: Optional[List[Education]] = None
    work_experience: Optional[List[WorkExperience]] = None
    certificates: Optional[List[Certificate]] = None
    work_preferences: Optional[WorkPreferences] = None
    is_active: Optional[bool] = None
    is_premium: Optional[bool] = None
    subscription_type: Optional[str] = None
    subscription_expires: Optional[datetime] = None
    telegram_chat_id: Optional[int] = None
    
# Job Application Models
class JobApplication(BaseModel):
    id: int
    user_id: int
    job_id: int
    status: str  # "applied", "in_progress", "rejected", "offer", "accepted"
    applied_date: datetime
    cover_letter: Optional[str] = None
    resume_url: Optional[HttpUrl] = None
    notes: Optional[str] = None
    match_score: Optional[float] = None  # 0-100% match between user and job
    updated_at: Optional[datetime] = None
    
class JobApplicationCreate(BaseModel):
    job_id: int
    cover_letter: Optional[str] = None
    resume_url: Optional[HttpUrl] = None
    notes: Optional[str] = None

class UserNotificationPreference(Base):
    """Model for storing user notification preferences"""
    __tablename__ = 'user_notification_preferences'

    id = Column(Integer, primary_key=True)
    user_id = Column(BigInteger, nullable=False, unique=True)
    telegram_chat_id = Column(BigInteger, nullable=True)
    email = Column(String, nullable=True)
    notify_on_deployment = Column(Boolean, default=True)
    notify_on_error = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<UserNotificationPreference(user_id={self.user_id})>" 