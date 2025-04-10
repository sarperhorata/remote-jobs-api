from pydantic import BaseModel, EmailStr, constr
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    email: EmailStr
    name: Optional[str] = None
    phone: Optional[constr(regex=r'^\+?1?\d{9,15}$')] = None
    title: Optional[str] = None
    linkedin_url: Optional[str] = None
    github_url: Optional[str] = None
    twitter_url: Optional[str] = None
    google_url: Optional[str] = None
    profile_photo_url: Optional[str] = None
    experience: Optional[str] = None
    education: Optional[str] = None
    skills: Optional[str] = None

class UserCreate(UserBase):
    password: constr(min_length=8)
    confirm_password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    phone: Optional[constr(regex=r'^\+?1?\d{9,15}$')] = None
    linkedin_url: Optional[str] = None
    current_password: Optional[str] = None
    new_password: Optional[constr(min_length=8)] = None

class UserResponse(UserBase):
    id: int
    is_active: bool
    is_verified: bool
    is_phone_verified: bool
    subscription_type: str
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None 