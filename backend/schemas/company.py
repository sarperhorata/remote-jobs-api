from datetime import datetime
from typing import List, Optional

from bson import ObjectId
from pydantic import BaseModel, ConfigDict, Field, HttpUrl

from .common import PyObjectId


class CompanyBase(BaseModel):
    name: str = Field(...)
    description: Optional[str] = None
    website: Optional[HttpUrl] = None
    logo_url: Optional[str] = None
    location: Optional[str] = None
    industry: Optional[str] = None
    size: Optional[str] = None
    founded_year: Optional[int] = None


class CompanyCreate(CompanyBase):
    pass


class CompanyUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    website: Optional[HttpUrl] = None
    logo_url: Optional[str] = None
    location: Optional[str] = None
    industry: Optional[str] = None
    size: Optional[str] = None
    founded_year: Optional[int] = None
    is_active: Optional[bool] = None


class Company(CompanyBase):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str},
    )


class CompanyResponse(CompanyBase):
    id: str
    created_at: datetime
    updated_at: datetime
    jobs_count: int = 0

    model_config = ConfigDict(from_attributes=True)


class CompanyListResponse(BaseModel):
    items: List[CompanyResponse]
    total: int
    page: int
    per_page: int
    total_pages: int
