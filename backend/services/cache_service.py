# Redis caching implementation for Buzz2Remote
import redis
import json
import hashlib
from typing import Any, Optional
from datetime import timedelta
import logging

logger = logging.getLogger(__name__)

class CacheService:
    def __init__(self):
        self.redis_client = None
        try:
            self.redis_client = redis.Redis(
                host='localhost',
                port=6379,
                db=0,
                decode_responses=True
            )
            self.redis_client.ping()  # Test connection
            self.enabled = True
            logger.info("Redis cache enabled")
        except:
            self.enabled = False
            self.redis_client = None
            logger.warning("Redis not available, caching disabled")
    
    def _generate_key(self, prefix: str, params: dict) -> str:
        """Generate cache key from parameters"""
        params_str = json.dumps(params, sort_keys=True)
        params_hash = hashlib.md5(params_str.encode(), usedforsecurity=False).hexdigest()[:8]
        return f"buzz2remote:{prefix}:{params_hash}"
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        if not self.enabled:
            return None
        
        try:
            value = self.redis_client.get(key)
            return json.loads(value) if value else None
        except:
            return None
    
    async def set(self, key: str, value: Any, expire: int = 300) -> bool:
        """Set value in cache with expiration"""
        if not self.enabled:
            return False
        
        try:
            return self.redis_client.setex(
                key, 
                expire, 
                json.dumps(value, default=str)
            )
        except:
            return False
    
    async def get_jobs_cache(self, filters: dict, page: int, limit: int) -> Optional[dict]:
        """Get cached jobs query"""
        key = self._generate_key("jobs", {**filters, "page": page, "limit": limit})
        return await self.get(key)
    
    async def set_jobs_cache(self, filters: dict, page: int, limit: int, result: dict, expire: int = 300) -> bool:
        """Cache jobs query result"""
        key = self._generate_key("jobs", {**filters, "page": page, "limit": limit})
        return await self.set(key, result, expire=expire)
    
    async def get_user_cache(self, user_id: str, cache_type: str) -> Optional[Any]:
        """Get user-specific cache"""
        key = self._generate_key(f"user_{cache_type}", {"user_id": user_id})
        return await self.get(key)
    
    async def set_user_cache(self, user_id: str, cache_type: str, value: Any, expire: int = 600) -> bool:
        """Set user-specific cache"""
        key = self._generate_key(f"user_{cache_type}", {"user_id": user_id})
        return await self.set(key, value, expire=expire)
    
    async def delete(self, key: str) -> bool:
        """Delete cache key"""
        if not self.enabled:
            return False
        
        try:
            return bool(self.redis_client.delete(key))
        except:
            return False
    
    async def exists(self, key: str) -> bool:
        """Check if cache key exists"""
        if not self.enabled:
            return False
        
        try:
            return bool(self.redis_client.exists(key))
        except:
            return False
    
    async def clear_all_cache(self) -> bool:
        """Clear all cache"""
        if not self.enabled:
            return False
        
        try:
            keys = self.redis_client.keys("buzz2remote:*")
            if keys:
                return bool(self.redis_client.delete(*keys))
            return True
        except:
            return False
    
    async def clear_pattern_cache(self, pattern: str) -> bool:
        """Clear cache by pattern"""
        if not self.enabled:
            return False
        
        try:
            keys = self.redis_client.keys(pattern)
            if keys:
                return bool(self.redis_client.delete(*keys))
            return True
        except:
            return False

# Global cache instance
cache_service = CacheService() 