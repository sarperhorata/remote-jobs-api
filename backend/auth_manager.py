from datetime import datetime
import redis
from typing import Optional
import secrets  # Güvenli random key üretimi için
from models import APIKey

class AuthManager:
    def __init__(self):
        self.redis_client = redis.Redis(host='localhost', port=6379, db=1)  # farklı db kullanıyoruz
        
    def validate_api_key(self, api_key: str) -> bool:
        key_data = self.redis_client.get(f"api_key:{api_key}")
        if not key_data:
            return False
            
        key_info = APIKey.parse_raw(key_data)
        return key_info.is_active
        
    def create_api_key(self, owner: str) -> str:
        # Güvenli random key oluştur
        api_key = secrets.token_urlsafe(32)
        
        # Key bilgilerini kaydet
        key_info = APIKey(
            key=api_key,
            owner=owner,
            created_at=datetime.now()
        )
        
        self.redis_client.set(
            f"api_key:{api_key}",
            key_info.json()
        )
        
        return api_key
        
    def revoke_api_key(self, api_key: str) -> bool:
        key_data = self.redis_client.get(f"api_key:{api_key}")
        if not key_data:
            return False
            
        key_info = APIKey.parse_raw(key_data)
        key_info.is_active = False
        
        self.redis_client.set(
            f"api_key:{api_key}",
            key_info.json()
        )
        
        return True 