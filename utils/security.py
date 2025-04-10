import re
import logging
from fastapi import HTTPException, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional, Dict, Any
import time
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

# Rate limiting için basit bir in-memory store
rate_limit_store: Dict[str, Dict[str, Any]] = {}

class SecurityUtils:
    """Güvenlik yardımcı fonksiyonları"""
    
    @staticmethod
    def validate_password(password: str) -> bool:
        """
        Şifre güvenlik kurallarını kontrol eder.
        En az 8 karakter, 1 büyük harf, 1 küçük harf, 1 rakam ve 1 özel karakter içermelidir.
        """
        if len(password) < 8:
            return False
        
        if not re.search(r"[A-Z]", password):
            return False
        
        if not re.search(r"[a-z]", password):
            return False
        
        if not re.search(r"\d", password):
            return False
        
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
            return False
        
        return True
    
    @staticmethod
    def sanitize_input(input_str: str) -> str:
        """
        Kullanıcı girdilerini temizler ve XSS saldırılarına karşı korur.
        """
        # HTML etiketlerini kaldır
        sanitized = re.sub(r'<[^>]*>', '', input_str)
        # Özel karakterleri escape et
        sanitized = sanitized.replace('&', '&amp;')
        sanitized = sanitized.replace('<', '&lt;')
        sanitized = sanitized.replace('>', '&gt;')
        sanitized = sanitized.replace('"', '&quot;')
        sanitized = sanitized.replace("'", '&#x27;')
        return sanitized
    
    @staticmethod
    def check_rate_limit(ip: str, endpoint: str, limit: int = 100, window: int = 60) -> bool:
        """
        Rate limiting kontrolü yapar.
        
        Args:
            ip: İstemci IP adresi
            endpoint: İstek yapılan endpoint
            limit: Zaman penceresi içinde izin verilen maksimum istek sayısı
            window: Zaman penceresi (saniye)
            
        Returns:
            bool: Rate limit aşıldıysa False, aşılmadıysa True
        """
        key = f"{ip}:{endpoint}"
        now = time.time()
        
        if key not in rate_limit_store:
            rate_limit_store[key] = {
                "requests": [now],
                "last_reset": now
            }
            return True
        
        # Zaman penceresi dışındaki istekleri temizle
        rate_limit_store[key]["requests"] = [
            req_time for req_time in rate_limit_store[key]["requests"]
            if now - req_time < window
        ]
        
        # İstek sayısını kontrol et
        if len(rate_limit_store[key]["requests"]) >= limit:
            return False
        
        # Yeni isteği ekle
        rate_limit_store[key]["requests"].append(now)
        return True
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """
        E-posta adresinin geçerli olup olmadığını kontrol eder.
        """
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    @staticmethod
    def validate_phone(phone: str) -> bool:
        """
        Telefon numarasının geçerli olup olmadığını kontrol eder.
        """
        pattern = r'^\+?[1-9]\d{1,14}$'
        return bool(re.match(pattern, phone))
    
    @staticmethod
    def generate_csrf_token() -> str:
        """
        CSRF token oluşturur.
        """
        import secrets
        return secrets.token_urlsafe(32)
    
    @staticmethod
    def verify_csrf_token(token: str, stored_token: str) -> bool:
        """
        CSRF token'ı doğrular.
        """
        return token == stored_token 