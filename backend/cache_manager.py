from datetime import datetime, timedelta
import json
from typing import Dict, Optional
import logging
from fastapi import Request
import redis

class CacheManager:
    def __init__(self, cache_duration_hours: int = 24):
        self.redis_client = redis.Redis(host='localhost', port=6379, db=0)
        self.cache_duration = timedelta(hours=cache_duration_hours)
        self.rate_limit_duration = timedelta(hours=24)
        self.requests_per_period = 3
        self.logger = logging.getLogger(__name__)

    async def get_client_ip(self, request: Request) -> str:
        """Request'ten IP adresini al"""
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0]
        return request.client.host

    def get_rate_limit_key(self, ip: str) -> str:
        """IP için rate limit key'ini oluştur"""
        return f"rate_limit:{ip}"

    def get_cache_key(self, endpoint: str, params: Dict = None) -> str:
        """Cache key'i oluştur"""
        if params:
            param_str = json.dumps(params, sort_keys=True)
            return f"cache:{endpoint}:{param_str}"
        return f"cache:{endpoint}"

    async def check_rate_limit(self, request: Request) -> bool:
        """IP bazlı rate limit kontrolü"""
        try:
            ip = await self.get_client_ip(request)
            key = self.get_rate_limit_key(ip)
            
            # Pipeline kullanarak atomic işlem yap
            pipe = self.redis_client.pipeline()
            
            # Mevcut istek sayısını al
            current = self.redis_client.get(key)
            if not current:
                pipe.setex(key, int(self.rate_limit_duration.total_seconds()), 1)
                pipe.execute()
                return True
            
            current = int(current)
            if current >= self.requests_per_period:
                return False
            
            pipe.incr(key)
            pipe.execute()
            return True
            
        except Exception as e:
            self.logger.error(f"Rate limit check error: {str(e)}")
            return True  # Hata durumunda izin ver

    def get_cached_data(self, key: str) -> Optional[Dict]:
        """Cache'den veri al"""
        try:
            data = self.redis_client.get(key)
            if data:
                return json.loads(data)
            return None
        except Exception as e:
            self.logger.error(f"Cache get error: {str(e)}")
            return None

    def set_cached_data(self, key: str, data: Dict):
        """Veriyi cache'e kaydet"""
        try:
            self.redis_client.setex(
                key,
                int(self.cache_duration.total_seconds()),
                json.dumps(data)
            )
        except Exception as e:
            self.logger.error(f"Cache set error: {str(e)}") 