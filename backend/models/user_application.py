from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict
from bson import ObjectId
from .common import PyObjectId

class UserApplicationBase(BaseModel):
    user_id: str = Field(...)
    job_id: str = Field(...)
    applied_at: datetime = Field(default_factory=datetime.utcnow)
    application_type: str = Field(default="external")  # external, internal, auto
    status: str = Field(default="applied")  # applied, viewed, responded, rejected, accepted
    cover_letter: Optional[str] = None
    auto_apply_used: bool = Field(default=False)
    response_received: Optional[datetime] = None
    notes: Optional[str] = None

class UserApplicationCreate(UserApplicationBase):
    pass

class UserApplicationUpdate(BaseModel):
    status: Optional[str] = None
    response_received: Optional[datetime] = None
    notes: Optional[str] = None

class UserApplication(UserApplicationBase):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    
    model_config = ConfigDict(
        populate_by_name=True, 
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str}
    )

class UserApplicationResponse(BaseModel):
    id: str = Field(alias="_id")
    user_id: str
    job_id: str
    applied_at: datetime
    application_type: str
    status: str
    cover_letter: Optional[str] = None
    auto_apply_used: bool
    response_received: Optional[datetime] = None
    notes: Optional[str] = None
    
    model_config = ConfigDict(populate_by_name=True) 