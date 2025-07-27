from datetime import datetime
from typing import List, Optional

from bson import ObjectId
from pydantic import BaseModel, ConfigDict, Field, HttpUrl

from .common import PyObjectId


class JobBase(BaseModel):
    title: str = Field(...)
    company: str = Field(...)
    location: Optional[str] = None
    description: str = Field(...)
    apply_url: HttpUrl
    tags: Optional[List[str]] = []


class JobCreate(JobBase):
    pass


class JobUpdate(BaseModel):
    title: Optional[str] = None
    company: Optional[str] = None
    location: Optional[str] = None
    description: Optional[str] = None
    apply_url: Optional[HttpUrl] = None
    tags: Optional[List[str]] = None
    is_active: Optional[bool] = None


class Job(JobBase):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str},
    )


class JobListResponse(BaseModel):
    items: List[Job]
    total: int


class JobSearchQuery(BaseModel):
    """Search query schema for job filtering"""

    query: Optional[str] = None
    location: Optional[str] = None
    job_type: Optional[str] = None
    experience_level: Optional[str] = None
    company: Optional[str] = None
    skills: Optional[str] = None
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    remote_type: Optional[str] = None
    page: int = Field(default=1, ge=1)
    limit: int = Field(default=20, ge=1, le=100)
    sort_by: Optional[str] = Field(
        default="created_at", pattern="^(created_at|title|company|salary)$"
    )
    sort_order: Optional[str] = Field(default="desc", pattern="^(asc|desc)$")


class ApplicationCreate(BaseModel):
    """Schema for job application creation"""

    job_id: str
    cover_letter: Optional[str] = None
    application_type: str = Field(default="external", pattern="^(external|internal)$")
    additional_notes: Optional[str] = None


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
