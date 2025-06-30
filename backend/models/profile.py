from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional
from datetime import datetime
import uuid

class Profile(BaseModel):
    """MongoDB Profile model using Pydantic"""
    
    id: Optional[str] = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    email: EmailStr
    phone: Optional[str] = None
    location: Optional[str] = None
    job_type: Optional[str] = None
    skills: List[str] = Field(default_factory=list)
    experience: Optional[str] = None
    education: Optional[str] = None
    languages: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        from_attributes = True 