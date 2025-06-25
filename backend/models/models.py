from pydantic import BaseModel, HttpUrl, Field, EmailStr
from typing import List, Optional, Dict, Any, Union
from enum import Enum
from datetime import datetime
from sqlalchemy import Column, Integer, BigInteger, String, Boolean, DateTime, Text, JSON, ForeignKey, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

# SQLAlchemy Base for database models
Base = declarative_base()

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

class User(BaseModel):
    id: Optional[str] = None
    email: EmailStr
    name: Optional[str] = None  # İlk kayıtta opsiyonel
    password: Optional[str] = None  # Email doğrulandıktan sonra set edilecek
    is_active: bool = True
    is_superuser: bool = False
    email_verified: bool = False  # Email doğrulama durumu
    onboarding_completed: bool = False  # Onboarding tamamlandı mı?
    onboarding_step: int = 0  # Hangi adımda (0: email, 1: password, 2: profile, 3: completed)
    linkedin_id: Optional[str] = None  # LinkedIn ID
    linkedin_profile: Optional[dict] = None  # LinkedIn profil bilgileri
    profile_picture_url: Optional[str] = None
    resume_url: Optional[str] = None  # CV dosya URL'i
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()
    stripe_customer_id: Optional[str] = None
    stripe_subscription_id: Optional[str] = None
    subscription_status: Optional[str] = None
    subscription_plan: Optional[str] = None
    subscription_end_date: Optional[datetime] = None

    class Config:
        from_attributes = True

# Enhanced Job Model for MongoDB with Translation Support
class EnhancedJob(BaseModel):
    id: Optional[str] = None
    title: str
    company: str
    location: Optional[str] = None
    description: Optional[str] = None
    requirements: Optional[str] = None
    benefits: Optional[str] = None
    salary: Optional[Union[str, Dict[str, Any]]] = None
    jobType: Optional[str] = None  # Full-time, Part-time, Contract, etc.
    experienceLevel: Optional[str] = None  # Entry, Mid, Senior, Executive
    skills: Optional[List[str]] = None
    isRemote: bool = False
    url: Optional[str] = None
    companyUrl: Optional[str] = None
    
    # Translation fields
    original_language: str = 'en'  # ISO language code (tr, de, fr, etc.)
    is_translated: bool = False
    original_data: Optional[Dict[str, Any]] = None  # Store original non-English data
    translation_metadata: Optional[Dict[str, Any]] = None  # Store translation details
    
    # Additional metadata
    source: Optional[str] = None  # Source website/platform
    posted_date: Optional[datetime] = None
    applicant_count: Optional[int] = None
    views: int = 0
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        from_attributes = True

# Translation Models
class TranslationRequest(BaseModel):
    text: str
    source_language: Optional[str] = None
    target_language: str = 'en'

class TranslationResponse(BaseModel):
    translated_text: str
    original_text: str
    source_language: str
    target_language: str
    translation_confidence: float
    error: Optional[str] = None

class JobTranslation(BaseModel):
    """Translation data for a job listing"""
    job_id: str
    original_language: str
    target_language: str
    translated_fields: Dict[str, str]  # field_name -> translated_text
    translation_metadata: Optional[Dict[str, Any]] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

class CompanyTranslation(BaseModel):
    """Translation data for company information"""
    company_id: str
    original_language: str
    target_language: str
    translated_fields: Dict[str, str]  # field_name -> translated_text
    translation_metadata: Optional[Dict[str, Any]] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

class JobTranslationResult(BaseModel):
    job_id: str
    needs_translation: bool
    original_language: str
    translated_data: Optional[Dict[str, Any]] = None
    original_data: Optional[Dict[str, Any]] = None
    translation_metadata: Optional[Dict[str, Any]] = None

class BatchTranslationRequest(BaseModel):
    job_ids: List[str]
    target_language: str = 'en'
    batch_size: int = 10

class BatchTranslationResponse(BaseModel):
    total_jobs: int
    translated_jobs: int
    failed_jobs: int
    results: List[JobTranslationResult]
    errors: List[str] = []

class JobApplication(Base):
    __tablename__ = 'job_applications'
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey('users.id'), nullable=False)
    job_id = Column(String(36), ForeignKey('jobs.id'), nullable=False)
    
    # Application status
    status = Column(String(50), default='applied')  # applied, viewed, rejected, hired, withdrawn
    application_type = Column(String(20), nullable=False)  # external, scraped, automated
    
    # Application data
    cover_letter = Column(Text)
    resume_url = Column(String(500))
    additional_notes = Column(Text)
    form_data = Column(JSON)  # Store scraped form responses
    
    # External tracking
    external_url = Column(String(1000))  # Company application URL
    external_reference = Column(String(200))  # Company reference/confirmation number
    
    # Metadata
    applied_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Response tracking
    viewed_by_company = Column(Boolean, default=False)
    company_response_date = Column(DateTime)
    company_response = Column(Text)
    
    # Relationships
    user = relationship('User', backref='job_applications')
    job = relationship('Job', backref='applications')
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_user_job', 'user_id', 'job_id'),
        Index('idx_user_applied_at', 'user_id', 'applied_at'),
        Index('idx_job_applied_at', 'job_id', 'applied_at'),
        Index('idx_status', 'status'),
    )
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'job_id': self.job_id,
            'status': self.status,
            'application_type': self.application_type,
            'cover_letter': self.cover_letter,
            'resume_url': self.resume_url,
            'additional_notes': self.additional_notes,
            'form_data': self.form_data,
            'external_url': self.external_url,
            'external_reference': self.external_reference,
            'applied_at': self.applied_at.isoformat() if self.applied_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'viewed_by_company': self.viewed_by_company,
            'company_response_date': self.company_response_date.isoformat() if self.company_response_date else None,
            'company_response': self.company_response,
            'job': self.job.to_dict() if self.job else None
        } 