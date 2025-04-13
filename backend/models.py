from pydantic import BaseModel, HttpUrl, EmailStr
from typing import Optional
from datetime import datetime

class Company(BaseModel):
    name: str
    url: HttpUrl
    selector: str

class JobPosting(BaseModel):
    company: str
    job_title: str
    link: str

class APIKey(BaseModel):
    key: str
    owner: str
    is_active: bool = True
    created_at: datetime = datetime.now()

class UserCreate(BaseModel):
    email: EmailStr
    username: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class User(BaseModel):
    id: str
    email: EmailStr
    username: str
    hashed_password: str
    is_active: bool = True
    created_at: datetime = datetime.now()

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer" 