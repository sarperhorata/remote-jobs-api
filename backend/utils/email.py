import os
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from jose import jwt
from backend.services.mailgun_service import mailgun_service

logger = logging.getLogger(__name__)

# JWT settings
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def send_email(to_email: str, subject: str, body: str, **kwargs) -> bool:
    """
    E-posta gönderir (Mailgun üzerinden).
    
    Args:
        to_email: Alıcı e-posta adresi
        subject: E-posta konusu
        body: E-posta içeriği (HTML)
        
    Returns:
        bool: E-posta gönderildi mi?
    """
    try:
        result = mailgun_service.send_email(
            to_email=to_email,
            subject=subject,
            html_content=body
        )
        
        if result.get("success"):
            logger.info(f"Email sent successfully to {to_email}")
            return True
        else:
            logger.error(f"Failed to send email: {result.get('error')}")
            return False
            
    except Exception as e:
        logger.error(f"E-posta gönderme hatası: {e}")
        return False

def create_email_verification_token(email: str) -> str:
    """
    Create email verification token.
    
    Args:
        email: Email address
        
    Returns:
        str: Verification token
    """
    expires_delta = timedelta(hours=24)
    expire = datetime.utcnow() + expires_delta
    
    to_encode = {
        "sub": email,
        "type": "email_verification",
        "exp": expire
    }
    
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def create_password_reset_token(email: str) -> str:
    """
    Create password reset token.
    
    Args:
        email: Email address
        
    Returns:
        str: Password reset token
    """
    expires_delta = timedelta(hours=1)
    expire = datetime.utcnow() + expires_delta
    
    to_encode = {
        "sub": email,
        "type": "password_reset",
        "exp": expire
    }
    
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Verify token.
    
    Args:
        token: Token to verify
        
    Returns:
        Optional[Dict[str, Any]]: Token payload
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.JWTError:
        return None

def send_verification_email(email: str, token: str) -> bool:
    """Send email verification using Mailgun service"""
    try:
        return mailgun_service.send_verification_email(email, token)
    except Exception as e:
        logger.error(f"Error sending verification email: {str(e)}")
        return False

def send_password_reset_email(email: str, token: str) -> bool:
    """Send password reset email using Mailgun service"""
    try:
        return mailgun_service.send_password_reset_email(email, token)
    except Exception as e:
        logger.error(f"Error sending password reset email: {str(e)}")
        return False 