import re
import logging
import time
import secrets
import hashlib
from typing import Dict, Tuple, Set, List, Optional
import os
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

logger = logging.getLogger(__name__)

# Rate limiting configuration
rate_limit_data = {
    # Structure: {ip: {endpoint: [(timestamp, count)]}}
    "ip_endpoint_counters": {},
    # Count of IP violations: {ip: violation_count}
    "ip_violations": {},
    # Keep track of recent CSRF tokens: {token: expiry_timestamp}
    "csrf_tokens": {},
}

# OAuth2 scheme for token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")

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
        
        # Check for uppercase, lowercase, digit, and special character
        has_uppercase = re.search(r'[A-Z]', password) is not None
        has_lowercase = re.search(r'[a-z]', password) is not None
        has_digit = re.search(r'\d', password) is not None
        has_special = re.search(r'[!@#$%^&*(),.?":{}|<>]', password) is not None
        
        return has_uppercase and has_lowercase and has_digit and has_special
    
    @staticmethod
    def sanitize_input(input_str: str) -> str:
        """
        Kullanıcı girdilerini temizler ve XSS saldırılarına karşı korur.
        """
        if not input_str:
            return ""
            
        # Replace potentially dangerous characters
        sanitized = input_str
        sanitized = re.sub(r'<script.*?>.*?</script>', '', sanitized, flags=re.DOTALL)
        sanitized = re.sub(r'<.*?javascript:.*?>', '', sanitized)
        sanitized = re.sub(r'<.*?\s+on\w+\s*=.*?>', '', sanitized)
        
        return sanitized
    
    @staticmethod
    def check_rate_limit(ip: str, endpoint: str, limit: int = 30) -> Tuple[bool, int]:
        """
        Check if the current request is within rate limit
        Returns a tuple (is_within_limit, remaining_requests)
        """
        # Default window: 60 seconds (1 minute)
        window = 60  
        current_time = time.time()
        
        # Initialize data structures if not exists
        if ip not in rate_limit_data["ip_endpoint_counters"]:
            rate_limit_data["ip_endpoint_counters"][ip] = {}
            
        if endpoint not in rate_limit_data["ip_endpoint_counters"][ip]:
            rate_limit_data["ip_endpoint_counters"][ip][endpoint] = []
        
        # Get request history for this IP and endpoint
        requests = rate_limit_data["ip_endpoint_counters"][ip][endpoint]
        
        # Remove old requests outside the time window
        requests = [req for req in requests if current_time - req < window]
        rate_limit_data["ip_endpoint_counters"][ip][endpoint] = requests
        
        # Check if limit is reached
        remaining = limit - len(requests)
        is_within_limit = len(requests) < limit
        
        # If within limit, add the current request timestamp
        if is_within_limit:
            requests.append(current_time)
        else:
            # Record violation for potential IP blocking
            if ip not in rate_limit_data["ip_violations"]:
                rate_limit_data["ip_violations"][ip] = 0
            rate_limit_data["ip_violations"][ip] += 1
        
        # Clean up old violation records periodically
        if current_time % 3600 < 10:  # Roughly every hour
            SecurityUtils._cleanup_old_data()
            
        return is_within_limit, remaining
    
    @staticmethod
    def get_rate_violations(ip: str) -> int:
        """Get the number of rate limit violations for an IP"""
        return rate_limit_data["ip_violations"].get(ip, 0)
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """
        E-posta adresinin geçerli olup olmadığını kontrol eder.
        """
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    @staticmethod
    def validate_phone(phone: str) -> bool:
        """
        Telefon numarasının geçerli olup olmadığını kontrol eder.
        """
        # Match international format with optional country code
        pattern = r'^\+?[0-9]{8,15}$'
        return re.match(pattern, phone) is not None
    
    @staticmethod
    def generate_csrf_token() -> str:
        """
        CSRF token oluşturur.
        """
        token = secrets.token_hex(32)
        expiry = time.time() + 3600  # 1 hour expiry
        
        # Store token with expiry
        rate_limit_data["csrf_tokens"][token] = expiry
        return token
    
    @staticmethod
    def verify_csrf_token(token: str) -> bool:
        """
        CSRF token'ı doğrular.
        """
        if not token:
            return False
            
        # Check if token exists and is not expired
        expiry = rate_limit_data["csrf_tokens"].get(token)
        if not expiry:
            return False
            
        is_valid = time.time() < expiry
        
        # Remove the token after use (one-time use)
        if token in rate_limit_data["csrf_tokens"]:
            del rate_limit_data["csrf_tokens"][token]
            
        return is_valid
    
    @staticmethod
    def get_secure_headers() -> Dict[str, str]:
        """Return a dictionary of security headers for responses"""
        return {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            "Referrer-Policy": "strict-origin-when-cross-origin",
            "Content-Security-Policy": "default-src 'self'; script-src 'self' https://www.google.com/recaptcha/ https://www.gstatic.com/recaptcha/; frame-src 'self' https://www.google.com/recaptcha/ https://hcaptcha.com; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; connect-src 'self' https://api.example.com"
        }
    
    @staticmethod
    def _cleanup_old_data() -> None:
        """Clean up old rate limit and CSRF data"""
        current_time = time.time()
        
        # Clean old CSRF tokens
        expired_tokens = [token for token, expiry in rate_limit_data["csrf_tokens"].items() 
                         if current_time > expiry]
        for token in expired_tokens:
            del rate_limit_data["csrf_tokens"][token]
        
        # Clean old IP violations (older than 24 hours)
        for ip in list(rate_limit_data["ip_violations"].keys()):
            # Reset violation count if IP hasn't had recent violations
            if ip in rate_limit_data["ip_endpoint_counters"]:
                has_recent = False
                for endpoint, timestamps in rate_limit_data["ip_endpoint_counters"][ip].items():
                    if any(current_time - ts < 86400 for ts in timestamps):  # 24 hours
                        has_recent = True
                        break
                
                if not has_recent:
                    del rate_limit_data["ip_violations"][ip]
        
        logger.info(f"Cleaned up security data. Active IPs: {len(rate_limit_data['ip_endpoint_counters'])}, "
                   f"CSRF tokens: {len(rate_limit_data['csrf_tokens'])}")
    
    @staticmethod
    async def get_current_user(token: str = Depends(oauth2_scheme)):
        """Dependency for getting the current authenticated user"""
        from utils.jwt import decode_token  # Import here to avoid circular imports
        
        try:
            payload = decode_token(token)
            if payload is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid authentication credentials",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            return payload
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            ) 