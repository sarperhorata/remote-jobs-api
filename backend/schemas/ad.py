from pydantic import BaseModel, Field, validator
from typing import List, Optional
from datetime import datetime

class AdBase(BaseModel):
    title: str = Field(..., min_length=1, description="Title must not be empty")
    description: Optional[str] = None
    image_url: Optional[str] = None
    target_url: Optional[str] = None
    target_audience: Optional[List[str]] = []
    is_active: bool = True

class AdCreate(AdBase):
    @validator('title')
    def title_must_not_be_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('Title must not be empty')
        return v

class AdUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    image_url: Optional[str] = None
    target_url: Optional[str] = None
    target_audience: Optional[List[str]] = None
    is_active: Optional[bool] = None

class AdResponse(AdBase):
    id: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    views_count: int = 0
    clicks_count: int = 0
    # Additional fields that might be in test data
    company: Optional[str] = None
    position: Optional[str] = None
    status: Optional[str] = None
    clicks: Optional[int] = None
    impressions: Optional[int] = None

    class Config:
        from_attributes = True

class AdListResponse(BaseModel):
    items: List[AdResponse]
    total: int
    page: int
    per_page: int
    total_pages: int 