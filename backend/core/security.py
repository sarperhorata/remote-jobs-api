import os
from datetime import datetime, timedelta
from typing import Optional

import jwt
from fastapi import Depends, Header, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jwt import InvalidTokenError as JWTError
from passlib.context import CryptContext

from backend.utils.config import get_settings

settings = get_settings()

ALGORITHM = getattr(settings, "ALGORITHM", "HS256")
SECRET_KEY = getattr(settings, "SECRET_KEY", "secret")

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Password context for hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password using bcrypt."""
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def require_api_key(x_api_key: str = Header(..., alias="X-API-Key")) -> str:
    """Validate API key for internal service endpoints"""
    expected_api_key = os.getenv("API_KEY", "buzz2remote-secure-api-key-2025")

    if x_api_key != expected_api_key:
        raise HTTPException(status_code=401, detail="Invalid API key")

    return x_api_key


async def get_current_user(token: str = Depends(oauth2_scheme)) -> Optional[dict]:
    """Get current user from JWT token"""
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    # Get user from database
    from backend.database.db import get_database

    db = get_database()
    user = await db.users.find_one({"_id": user_id})
    if user is None:
        raise credentials_exception
    return user
