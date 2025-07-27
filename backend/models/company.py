from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class Company(BaseModel):
    id: str = Field(alias="_id")
    name: str
    description: Optional[str] = None
    website: Optional[str] = None
    careerPage: Optional[str] = None
    logo: Optional[str] = None
    location: Optional[str] = None
    size: Optional[str] = None
    industry: Optional[str] = None
    founded: Optional[int] = None
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    jobs_count: Optional[int] = 0
    benefits: Optional[List[str]] = []
    tech_stack: Optional[List[str]] = []
    social_links: Optional[dict] = {}
    remote_policy: Optional[str] = None

    class Config:
        populate_by_name = True
        json_encoders = {datetime: lambda v: v.isoformat()}
