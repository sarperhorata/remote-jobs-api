import asyncio
import json
import logging
import time
from collections import OrderedDict
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class CacheService:
    """
    In-memory cache service for storing popular job search results.
    Implements LRU (Least Recently Used) eviction policy.
    """

    def __init__(self, max_size: int = 100, ttl_hours: int = 24):
        self.max_size = max_size
        self.ttl_hours = ttl_hours
        self.cache: OrderedDict = OrderedDict()
        self.access_times: Dict[str, float] = {}
        self.expiry_times: Dict[str, float] = {}

        # Popular keywords cache with longer TTL
        self.popular_cache: OrderedDict = OrderedDict()
        self.popular_access_times: Dict[str, float] = {}
        self.popular_expiry_times: Dict[str, float] = {}
        self.popular_ttl_hours = 72  # 3 days for popular searches

        logger.info(
            f"✅ Cache service initialized with max_size={max_size}, ttl={ttl_hours}h, popular_ttl={self.popular_ttl_hours}h"
        )

    def _is_popular_keyword(self, keyword: str) -> bool:
        """Check if keyword is in top 10 popular searches."""
        popular_keywords = [
            "react",
            "python",
            "javascript",
            "java",
            "node",
            "frontend",
            "backend",
            "fullstack",
            "devops",
            "data",
        ]
        keyword_lower = keyword.lower().strip()
        return any(
            pop_kw in keyword_lower or keyword_lower in pop_kw
            for pop_kw in popular_keywords
        )

    def _cleanup_expired(
        self, cache_dict: OrderedDict, expiry_dict: Dict[str, float]
    ) -> None:
        """Remove expired entries from cache."""
        current_time = time.time()
        expired_keys = [
            key
            for key, expiry_time in expiry_dict.items()
            if current_time > expiry_time
        ]

        for key in expired_keys:
            if key in cache_dict:
                del cache_dict[key]
            if key in expiry_dict:
                del expiry_dict[key]
            logger.debug(f"🗑️ Removed expired cache entry: {key}")

    def _update_access_time(self, key: str, is_popular: bool = False) -> None:
        """Update access time for LRU tracking."""
        current_time = time.time()
        if is_popular:
            self.popular_access_times[key] = current_time
            # Move to end (most recently used)
            if key in self.popular_cache:
                self.popular_cache.move_to_end(key)
        else:
            self.access_times[key] = current_time
            # Move to end (most recently used)
            if key in self.cache:
                self.cache.move_to_end(key)

    def _evict_lru(self, is_popular: bool = False) -> None:
        """Evict least recently used entry if cache is full."""
        if is_popular:
            if len(self.popular_cache) >= self.max_size:
                # Remove oldest entry (first in OrderedDict)
                oldest_key = next(iter(self.popular_cache))
                del self.popular_cache[oldest_key]
                if oldest_key in self.popular_access_times:
                    del self.popular_access_times[oldest_key]
                if oldest_key in self.popular_expiry_times:
                    del self.popular_expiry_times[oldest_key]
                logger.debug(f"🗑️ Evicted LRU popular cache entry: {oldest_key}")
        else:
            if len(self.cache) >= self.max_size:
                # Remove oldest entry (first in OrderedDict)
                oldest_key = next(iter(self.cache))
                del self.cache[oldest_key]
                if oldest_key in self.access_times:
                    del self.access_times[oldest_key]
                if oldest_key in self.expiry_times:
                    del self.expiry_times[oldest_key]
                logger.debug(f"🗑️ Evicted LRU cache entry: {oldest_key}")

    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        try:
            is_popular = self._is_popular_keyword(key)

            # Cleanup expired entries first
            if is_popular:
                self._cleanup_expired(self.popular_cache, self.popular_expiry_times)
                cache_dict = self.popular_cache
                expiry_dict = self.popular_expiry_times
            else:
                self._cleanup_expired(self.cache, self.expiry_times)
                cache_dict = self.cache
                expiry_dict = self.expiry_times

            if key in cache_dict:
                # Check if expired
                if key in expiry_dict and time.time() > expiry_dict[key]:
                    # Remove expired entry
                    del cache_dict[key]
                    del expiry_dict[key]
                    logger.debug(f"🗑️ Removed expired cache entry: {key}")
                    return None

                # Update access time for LRU
                self._update_access_time(key, is_popular)

                value = cache_dict[key]
                logger.debug(f"✅ Cache hit for key: {key} (popular: {is_popular})")
                return value

            logger.debug(f"❌ Cache miss for key: {key} (popular: {is_popular})")
            return None

        except Exception as e:
            logger.error(f"Error getting from cache: {e}")
            return None

    async def set(self, key: str, value: Any, ttl_hours: Optional[int] = None) -> bool:
        """Set value in cache with TTL."""
        try:
            is_popular = self._is_popular_keyword(key)

            # Use appropriate TTL
            if ttl_hours is None:
                ttl_hours = self.popular_ttl_hours if is_popular else self.ttl_hours

            # Cleanup expired entries first
            if is_popular:
                self._cleanup_expired(self.popular_cache, self.popular_expiry_times)
                cache_dict = self.popular_cache
                expiry_dict = self.popular_expiry_times
            else:
                self._cleanup_expired(self.cache, self.expiry_times)
                cache_dict = self.cache
                expiry_dict = self.expiry_times

            # Evict LRU if cache is full
            self._evict_lru(is_popular)

            # Set value and expiry time
            current_time = time.time()
            expiry_time = current_time + (ttl_hours * 3600)

            cache_dict[key] = value
            expiry_dict[key] = expiry_time
            self._update_access_time(key, is_popular)

            logger.debug(
                f"💾 Cached key: {key} (popular: {is_popular}, ttl: {ttl_hours}h)"
            )
            return True

        except Exception as e:
            logger.error(f"Error setting cache: {e}")
            return False

    async def delete(self, key: str) -> bool:
        """Delete key from cache."""
        try:
            is_popular = self._is_popular_keyword(key)

            if is_popular:
                if key in self.popular_cache:
                    del self.popular_cache[key]
                if key in self.popular_access_times:
                    del self.popular_access_times[key]
                if key in self.popular_expiry_times:
                    del self.popular_expiry_times[key]
            else:
                if key in self.cache:
                    del self.cache[key]
                if key in self.access_times:
                    del self.access_times[key]
                if key in self.expiry_times:
                    del self.expiry_times[key]

            logger.debug(f"🗑️ Deleted cache key: {key}")
            return True

        except Exception as e:
            logger.error(f"Error deleting from cache: {e}")
            return False

    async def clear(self) -> bool:
        """Clear all cache."""
        try:
            self.cache.clear()
            self.access_times.clear()
            self.expiry_times.clear()
            self.popular_cache.clear()
            self.popular_access_times.clear()
            self.popular_expiry_times.clear()

            logger.info("🧹 All cache cleared")
            return True

        except Exception as e:
            logger.error(f"Error clearing cache: {e}")
            return False

    async def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        try:
            # Cleanup expired entries first
            self._cleanup_expired(self.cache, self.expiry_times)
            self._cleanup_expired(self.popular_cache, self.popular_expiry_times)

            return {
                "regular_cache": {
                    "size": len(self.cache),
                    "max_size": self.max_size,
                    "ttl_hours": self.ttl_hours,
                },
                "popular_cache": {
                    "size": len(self.popular_cache),
                    "max_size": self.max_size,
                    "ttl_hours": self.popular_ttl_hours,
                },
                "total_entries": len(self.cache) + len(self.popular_cache),
                "total_max_size": self.max_size * 2,
            }

        except Exception as e:
            logger.error(f"Error getting cache stats: {e}")
            return {}

    async def get_popular_keywords(self) -> List[str]:
        """Get list of popular keywords."""
        return [
            "react",
            "python",
            "javascript",
            "java",
            "node",
            "frontend",
            "backend",
            "fullstack",
            "devops",
            "data",
        ]


# Global cache instance
_cache_service: Optional[CacheService] = None


def get_cache_service() -> CacheService:
    """Get global cache service instance."""
    global _cache_service
    if _cache_service is None:
        _cache_service = CacheService()
    return _cache_service


async def init_cache_service(max_size: int = 100, ttl_hours: int = 24) -> CacheService:
    """Initialize global cache service."""
    global _cache_service
    _cache_service = CacheService(max_size=max_size, ttl_hours=ttl_hours)
    return _cache_service
