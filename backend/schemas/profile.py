from pydantic import BaseModel, EmailStr, ConfigDict
from typing import List, Optional

class ProfileBase(BaseModel):
    name: str
    email: EmailStr
    phone: Optional[str] = None
    location: Optional[str] = None
    job_type: Optional[str] = None
    skills: List[str] = []
    experience: Optional[str] = None
    education: Optional[str] = None
    languages: List[str] = []

class ProfileCreate(ProfileBase):
    pass

class ProfileUpdate(ProfileBase):
    name: Optional[str] = None
    email: Optional[EmailStr] = None

class ProfileResponse(ProfileBase):
    id: int

    model_config = ConfigDict(from_attributes=True) 