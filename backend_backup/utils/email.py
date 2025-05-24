import os
import smtplib
import jwt
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

# JWT ayarları
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
    E-posta doğrulama token'ı oluşturur.
    
    Args:
        email: E-posta adresi
        
    Returns:
        str: Doğrulama token'ı
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
    Şifre sıfırlama token'ı oluşturur.
    
    Args:
        email: E-posta adresi
        
    Returns:
        str: Şifre sıfırlama token'ı
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
    Token'ı doğrular.
    
    Args:
        token: Doğrulanacak token
        
    Returns:
        Optional[Dict[str, Any]]: Token içeriği
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.JWTError:
        return None

def send_verification_email(email: str, token: str) -> bool:
    """
    E-posta doğrulama e-postası gönderir.
    
    Args:
        email: E-posta adresi
        token: Doğrulama token'ı
        
    Returns:
        bool: E-posta gönderildi mi?
    """
    verification_url = f"{os.getenv('FRONTEND_URL', 'http://localhost:3000')}/verify-email?token={token}"
    
    subject = "E-posta Adresinizi Doğrulayın"
    body = f"""
    <html>
        <body>
            <h1>E-posta Doğrulama</h1>
            <p>Merhaba,</p>
            <p>E-posta adresinizi doğrulamak için aşağıdaki bağlantıya tıklayın:</p>
            <p><a href="{verification_url}">E-posta Adresimi Doğrula</a></p>
            <p>Bu bağlantı 24 saat boyunca geçerlidir.</p>
            <p>Eğer bu işlemi siz yapmadıysanız, bu e-postayı görmezden gelebilirsiniz.</p>
            <p>Saygılarımızla,<br>Remote Jobs Ekibi</p>
        </body>
    </html>
    """
    
    return send_email(email, subject, body)

def send_password_reset_email(email: str, token: str) -> bool:
    """
    Şifre sıfırlama e-postası gönderir.
    
    Args:
        email: E-posta adresi
        token: Şifre sıfırlama token'ı
        
    Returns:
        bool: E-posta gönderildi mi?
    """
    reset_url = f"{os.getenv('FRONTEND_URL', 'http://localhost:3000')}/reset-password?token={token}"
    
    subject = "Şifre Sıfırlama"
    body = f"""
    <html>
        <body>
            <h1>Şifre Sıfırlama</h1>
            <p>Merhaba,</p>
            <p>Şifrenizi sıfırlamak için aşağıdaki bağlantıya tıklayın:</p>
            <p><a href="{reset_url}">Şifremi Sıfırla</a></p>
            <p>Bu bağlantı 1 saat boyunca geçerlidir.</p>
            <p>Eğer bu işlemi siz yapmadıysanız, bu e-postayı görmezden gelebilirsiniz.</p>
            <p>Saygılarımızla,<br>Remote Jobs Ekibi</p>
        </body>
    </html>
    """
    
    return send_email(email, subject, body) 