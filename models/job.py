from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

class JobBase(BaseModel):
    title: str
    company: str
    company_logo: Optional[str] = None
    location: str
    job_type: str
    salary: Optional[str] = None
    description: str
    responsibilities: Optional[List[str]] = None
    requirements: Optional[List[str]] = None
    benefits: Optional[List[str]] = None
    skills: Optional[List[str]] = None
    url: Optional[str] = None

class JobCreate(JobBase):
    pass

class JobUpdate(BaseModel):
    title: Optional[str] = None
    company: Optional[str] = None
    company_logo: Optional[str] = None
    location: Optional[str] = None
    job_type: Optional[str] = None
    salary: Optional[str] = None
    description: Optional[str] = None
    responsibilities: Optional[List[str]] = None
    requirements: Optional[List[str]] = None
    benefits: Optional[List[str]] = None
    skills: Optional[List[str]] = None
    url: Optional[str] = None

class JobResponse(JobBase):
    id: str = Field(..., alias="_id")
    posted_at: datetime
    is_archived: bool = False
    archived_at: Optional[datetime] = None

    class Config:
        allow_population_by_field_name = True

class JobListResponse(BaseModel):
    jobs: List[JobResponse]
    total: int
    page: int
    pages: int 