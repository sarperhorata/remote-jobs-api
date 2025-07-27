import uuid
from datetime import datetime, UTC
from typing import List, Optional

from pydantic import BaseModel, EmailStr, Field


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
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    model_config = {"from_attributes": True}
