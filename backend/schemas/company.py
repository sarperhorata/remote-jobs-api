from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class CompanyBase(BaseModel):
    name: str
    description: str
    website: Optional[str] = None
    logo_url: Optional[str] = None
    location: Optional[str] = None
    industry: Optional[str] = None
    size: Optional[str] = None
    founded_year: Optional[int] = None
    is_active: bool = True

class CompanyCreate(CompanyBase):
    pass

class CompanyUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    website: Optional[str] = None
    logo_url: Optional[str] = None
    location: Optional[str] = None
    industry: Optional[str] = None
    size: Optional[str] = None
    founded_year: Optional[int] = None
    is_active: Optional[bool] = None

class CompanyResponse(CompanyBase):
    id: str
    created_at: datetime
    updated_at: datetime
    jobs_count: int = 0

    class Config:
        from_attributes = True

class CompanyListResponse(BaseModel):
    items: List[CompanyResponse]
    total: int
    page: int
    per_page: int
    total_pages: int 