from datetime import datetime, timedelta
from typing import Optional
from jose import jwt
from backend.config import get_settings

settings = get_settings()

ALGORITHM = getattr(settings, 'ALGORITHM', 'HS256')
SECRET_KEY = getattr(settings, 'SECRET_KEY', 'secret')


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt 