from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
from .common import PyObjectId

class UserActivityBase(BaseModel):
    user_id: str
    activity_type: str
    details: Optional[Dict[str, Any]] = None

class UserActivityCreate(UserActivityBase):
    pass

class UserActivity(UserActivityBase):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {PyObjectId: str} 