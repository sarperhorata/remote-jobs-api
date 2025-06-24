from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field

class APIServiceLog(BaseModel):
    """Model for API service logs"""
    service_name: str
    endpoint: str
    status: str  # success, error, warning
    response_time: float  # milliseconds
    quota_total: int
    quota_used: int
    quota_remaining: int
    error_message: Optional[str] = None
    meta: Optional[Dict[str, Any]] = None
    timestamp: datetime = Field(default_factory=datetime.now)

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        } 