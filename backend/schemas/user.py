from pydantic import BaseModel, EmailStr, constr
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    email: EmailStr
    name: Optional[str] = None
    phone: Optional[str] = None
    linkedin_url: Optional[str] = None
    title: Optional[str] = None
    profile_photo_url: Optional[str] = None
    experience: Optional[str] = None
    education: Optional[str] = None
    skills: Optional[str] = None

class UserCreate(UserBase):
    password: str
    recaptcha_response: Optional[str] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    phone: Optional[constr(pattern=r'^\+?1?\d{9,15}$')] = None
    linkedin_url: Optional[str] = None
    current_password: Optional[str] = None
    new_password: Optional[constr(min_length=8)] = None

class UserResponse(UserBase):
    id: str
    is_email_verified: bool
    subscription_type: str

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None 