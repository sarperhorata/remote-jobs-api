from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, EmailStr, Field, ConfigDict, field_validator
from bson import ObjectId
from .common import PyObjectId

class UserBase(BaseModel):
    email: EmailStr = Field(...)
    full_name: Optional[str] = None
    is_active: bool = True
    is_superuser: bool = False

class UserCreate(UserBase):
    password: str = Field(...)
    name: Optional[str] = None  # For backward compatibility

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    is_active: Optional[bool] = None

class User(UserBase):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    created_at: datetime = Field(default_factory=datetime.utcnow)

    model_config = ConfigDict(populate_by_name=True, arbitrary_types_allowed=True, json_encoders={ObjectId: str})

class UserInDB(User):
    hashed_password: str

# Onboarding için yeni schema'lar
class EmailOnlyRegister(BaseModel):
    email: EmailStr

class EmailVerification(BaseModel):
    token: str

class SetPassword(BaseModel):
    token: str
    password: str = Field(..., min_length=8, description="Password must be at least 8 characters long")
    confirm_password: str
    
    @field_validator('password')
    @classmethod
    def validate_password(cls, v):
        # En az 8 karakter
        if len(v) < 8:
            raise ValueError('Şifre en az 8 karakter olmalıdır')
        
        # En az bir büyük harf
        if not any(c.isupper() for c in v):
            raise ValueError('Şifre en az bir büyük harf içermelidir')
        
        # En az bir küçük harf
        if not any(c.islower() for c in v):
            raise ValueError('Şifre en az bir küçük harf içermelidir')
        
        # En az bir rakam
        if not any(c.isdigit() for c in v):
            raise ValueError('Şifre en az bir rakam içermelidir')
        
        # Özel karakterler (opsiyonel ama önerilen)
        import re
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
            # Uyarı ver ama hata verme
            pass
        
        return v
    
    @field_validator('confirm_password')
    @classmethod
    def validate_confirm_password(cls, v, values):
        # values parametresi artık info olarak geliyor
        if hasattr(values, 'data') and 'password' in values.data:
            password = values.data['password']
            if v != password:
                raise ValueError('Şifreler eşleşmiyor')
        return v

class LinkedInProfile(BaseModel):
    linkedin_id: str
    linkedin_data: Dict[str, Any]

class ProfileCompletion(BaseModel):
    name: Optional[str] = None
    bio: Optional[str] = None
    location: Optional[str] = None
    skills: Optional[List[str]] = None
    experience_years: Optional[int] = None
    job_preferences: Optional[Dict[str, Any]] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(UserBase):
    id: str = Field(alias="_id")
    is_active: bool
    is_superuser: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(populate_by_name=True, arbitrary_types_allowed=True)

    @classmethod
    def __get_pydantic_json_schema__(cls, core_schema, handler):
        json_schema = handler(core_schema)
        json_schema["properties"]["id"] = {"type": "string"}
        return json_schema

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None 