from beanie import Document
from fastapi_users.db import BeanieBaseUser, BeanieUserDatabase
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
from enum import Enum

class UserRole(str, Enum):
    ADMIN = "admin"
    MANAGER = "manager"
    VIEWER = "viewer"

class User(BeanieBaseUser, Document):
    """User model for admin panel authentication"""
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    role: UserRole = UserRole.VIEWER
    created_at: datetime = datetime.utcnow()
    last_login: Optional[datetime] = None
    is_active: bool = True
    
    class Settings:
        name = "admin_users"

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    role: UserRole = UserRole.VIEWER
    is_active: bool = True
    is_superuser: bool = False
    is_verified: bool = False

class UserUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None

class UserRead(BaseModel):
    id: str
    email: EmailStr
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    role: UserRole
    is_active: bool
    is_superuser: bool
    is_verified: bool
    created_at: datetime
    last_login: Optional[datetime] = None

async def get_user_db():
    yield BeanieUserDatabase(User) 