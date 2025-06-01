from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
from datetime import datetime
from bson import ObjectId

class JobBase(BaseModel):
    title: str
    company: str
    location: str
    description: str
    requirements: Optional[str] = None
    salary_range: Optional[str] = None
    job_type: str
    experience_level: Optional[str] = None
    apply_url: str
    remote_type: Optional[str] = None
    benefits: Optional[str] = None
    skills: Optional[str] = None
    application_deadline: Optional[datetime] = None

class JobCreate(JobBase):
    pass

class JobUpdate(BaseModel):
    title: Optional[str] = None
    company: Optional[str] = None
    location: Optional[str] = None
    description: Optional[str] = None
    requirements: Optional[str] = None
    salary_range: Optional[str] = None
    job_type: Optional[str] = None
    experience_level: Optional[str] = None
    apply_url: Optional[str] = None
    remote_type: Optional[str] = None
    benefits: Optional[str] = None
    skills: Optional[str] = None
    application_deadline: Optional[datetime] = None
    is_active: Optional[bool] = None

class JobResponse(JobBase):
    id: str = Field(alias="_id")
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    views_count: int
    applications_count: int

    model_config = ConfigDict(populate_by_name=True, arbitrary_types_allowed=True)
    
    @classmethod
    def __get_pydantic_json_schema__(cls, core_schema, handler):
        json_schema = handler(core_schema)
        json_schema["properties"]["id"] = {"type": "string"}
        return json_schema

class JobListResponse(BaseModel):
    jobs: List[JobResponse]
    total: int
    page: int
    per_page: int
    limit: int
    total_pages: int 