from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class AdBase(BaseModel):
    title: str
    description: str
    image_url: Optional[str] = None
    target_url: str
    target_audience: Optional[List[str]] = []
    is_active: bool = True

class AdCreate(AdBase):
    pass

class AdUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    image_url: Optional[str] = None
    target_url: Optional[str] = None
    target_audience: Optional[List[str]] = None
    is_active: Optional[bool] = None

class AdResponse(AdBase):
    id: str
    created_at: datetime
    updated_at: datetime
    views_count: int = 0
    clicks_count: int = 0

    class Config:
        from_attributes = True

class AdListResponse(BaseModel):
    items: List[AdResponse]
    total: int
    page: int
    per_page: int
    total_pages: int 