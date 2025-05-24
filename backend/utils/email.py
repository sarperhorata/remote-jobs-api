import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from jose import jwt

# JWT settings
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def send_email(to_email: str, subject: str, body: str) -> bool:
    """
    E-posta gönderir.
    
    Args:
        to_email: Alıcı e-posta adresi
        subject: E-posta konusu
        body: E-posta içeriği
        
    Returns:
        bool: E-posta gönderildi mi?
    """
    try:
        # E-posta ayarları
        sender_email = os.getenv("EMAIL_USERNAME", "noreply@remotejobs.com")
        password = os.getenv("EMAIL_PASSWORD", "")
        
        # E-posta içeriği
        msg = MIMEMultipart()
        msg["From"] = sender_email
        msg["To"] = to_email
        msg["Subject"] = subject
        
        msg.attach(MIMEText(body, "html"))
        
        # E-posta gönder
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender_email, password)
        server.send_message(msg)
        server.quit()
        
        return True
    except Exception as e:
        print(f"E-posta gönderme hatası: {e}")
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
    try:
        msg = MIMEMultipart()
        msg['From'] = os.getenv("SMTP_USERNAME", "your-email@example.com")
        msg['To'] = email
        msg['Subject'] = "Verify your email address"

        body = f"""
        Hello,

        Please click the link below to verify your email address:
        {os.getenv("FRONTEND_URL", "http://localhost:3000")}/verify-email?token={token}

        If you did not request this verification, please ignore this email.

        Best regards,
        Your App Team
        """
        msg.attach(MIMEText(body, 'plain'))

        server = smtplib.SMTP(os.getenv("SMTP_HOST", "smtp.gmail.com"), int(os.getenv("SMTP_PORT", "587")))
        server.starttls()
        server.login(os.getenv("SMTP_USERNAME", "your-email@example.com"), os.getenv("SMTP_PASSWORD", "your-password"))
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        print(f"Error sending email: {str(e)}")
        return False

def send_password_reset_email(email: str, token: str) -> bool:
    try:
        msg = MIMEMultipart()
        msg['From'] = os.getenv("SMTP_USERNAME", "your-email@example.com")
        msg['To'] = email
        msg['Subject'] = "Reset your password"

        body = f"""
        Hello,

        Please click the link below to reset your password:
        {os.getenv("FRONTEND_URL", "http://localhost:3000")}/reset-password?token={token}

        If you did not request a password reset, please ignore this email.

        Best regards,
        Your App Team
        """
        msg.attach(MIMEText(body, 'plain'))

        server = smtplib.SMTP(os.getenv("SMTP_HOST", "smtp.gmail.com"), int(os.getenv("SMTP_PORT", "587")))
        server.starttls()
        server.login(os.getenv("SMTP_USERNAME", "your-email@example.com"), os.getenv("SMTP_PASSWORD", "your-password"))
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        print(f"Error sending email: {str(e)}")
        return False 