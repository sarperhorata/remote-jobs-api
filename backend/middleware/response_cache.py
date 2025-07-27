"""
Response Caching Middleware
Implements intelligent caching for API responses to improve performance
"""

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
import json
import hashlib
import time
import os
import logging
from typing import Dict, Optional, Any, List
from datetime import datetime, timedelta
import asyncio

logger = logging.getLogger(__name__)

class InMemoryCache:
    """In-memory cache implementation with TTL support"""
    
    def __init__(self, max_size: int = 1000, default_ttl: int = 300):
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.max_size = max_size
        self.default_ttl = default_ttl
        self.access_times: Dict[str, float] = {}
        self.hit_count = 0
        self.miss_count = 0
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        if key in self.cache:
            entry = self.cache[key]
            
            # Check if expired
            if time.time() > entry['expires_at']:
                await self.delete(key)
                self.miss_count += 1
                return None
            
            # Update access time for LRU
            self.access_times[key] = time.time()
            self.hit_count += 1
            return entry['data']
        
        self.miss_count += 1
        return None
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in cache with TTL"""
        try:
            # Clean up if at max size
            if len(self.cache) >= self.max_size:
                await self._evict_lru()
            
            expires_at = time.time() + (ttl or self.default_ttl)
            
            self.cache[key] = {
                'data': value,
                'expires_at': expires_at,
                'created_at': time.time()
            }
            self.access_times[key] = time.time()
            return True
            
        except Exception as e:
            logger.error(f"Cache set error: {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        """Delete key from cache"""
        if key in self.cache:
            del self.cache[key]
            if key in self.access_times:
                del self.access_times[key]
            return True
        return False
    
    async def clear(self) -> bool:
        """Clear all cache entries"""
        self.cache.clear()
        self.access_times.clear()
        return True
    
    async def _evict_lru(self):
        """Evict least recently used item"""
        if not self.access_times:
            return
        
        # Find least recently used key
        lru_key = min(self.access_times.keys(), key=lambda k: self.access_times[k])
        await self.delete(lru_key)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        total_requests = self.hit_count + self.miss_count
        hit_rate = (self.hit_count / total_requests * 100) if total_requests > 0 else 0
        
        return {
            'type': 'in_memory',
            'size': len(self.cache),
            'max_size': self.max_size,
            'hit_count': self.hit_count,
            'miss_count': self.miss_count,
            'hit_rate': round(hit_rate, 2),
            'total_requests': total_requests
        }

class ResponseCacheMiddleware(BaseHTTPMiddleware):
    """Response caching middleware with intelligent cache strategy"""
    
    def __init__(self, app):
        super().__init__(app)
        self.cache = InMemoryCache(max_size=500, default_ttl=300)  # 5 minutes default
        
        # Cache configuration for different endpoints
        self.cache_config = {
            '/api/v1/jobs/': {
                'ttl': 180,  # 3 minutes
                'vary_by': ['page', 'limit'],
                'enabled': True
            },
            '/api/v1/jobs/search': {
                'ttl': 300,  # 5 minutes  
                'vary_by': ['q', 'page', 'limit', 'sort_by', 'location'],
                'enabled': True
            },
            '/api/v1/companies/': {
                'ttl': 600,  # 10 minutes
                'vary_by': ['page', 'limit'],
                'enabled': True
            },
            '/api/companies/statistics': {
                'ttl': 1800,  # 30 minutes
                'vary_by': [],
                'enabled': True
            },
            '/api/v1/jobs/statistics': {
                'ttl': 900,  # 15 minutes
                'vary_by': [],
                'enabled': True
            }
        }
        
        # Methods that should be cached
        self.cacheable_methods = {'GET'}
        
        # Headers to exclude from cache key
        self.exclude_headers = {
            'authorization', 'cookie', 'user-agent', 
            'accept-encoding', 'connection', 'host'
        }
    
    async def dispatch(self, request: Request, call_next):
        """Process request with caching logic"""
        try:
            # Check if request should be cached
            if not await self._should_cache(request):
                return await call_next(request)
            
            # Generate cache key
            cache_key = await self._generate_cache_key(request)
            
            # Try to get from cache
            cached_response = await self.cache.get(cache_key)
            if cached_response:
                return await self._create_cached_response(cached_response, request)
            
            # Process request
            response = await call_next(request)
            
            # Cache successful responses
            if await self._should_cache_response(response):
                await self._cache_response(cache_key, response, request)
            
            # Add cache headers
            await self._add_cache_headers(response, request, cached=False)
            
            return response
            
        except Exception as e:
            logger.error(f"Cache middleware error: {e}")
            return await call_next(request)
    
    async def _should_cache(self, request: Request) -> bool:
        """Determine if request should be cached"""
        # Check method
        if request.method not in self.cacheable_methods:
            return False
        
        # Check if endpoint is configured for caching
        path = request.url.path
        config = self._get_cache_config(path)
        
        return config and config.get('enabled', False)
    
    async def _should_cache_response(self, response: Response) -> bool:
        """Determine if response should be cached"""
        # Only cache successful responses
        if response.status_code != 200:
            return False
        
        # Check content type
        content_type = response.headers.get('content-type', '')
        if 'application/json' not in content_type:
            return False
        
        return True
    
    def _get_cache_config(self, path: str) -> Optional[Dict[str, Any]]:
        """Get cache configuration for path"""
        # Exact match first
        if path in self.cache_config:
            return self.cache_config[path]
        
        # Pattern matching for dynamic paths
        for pattern, config in self.cache_config.items():
            if pattern in path:
                return config
        
        return None
    
    async def _generate_cache_key(self, request: Request) -> str:
        """Generate unique cache key for request"""
        path = request.url.path
        config = self._get_cache_config(path)
        
        # Start with path
        key_parts = [path]
        
        # Add query parameters based on config
        if config and 'vary_by' in config:
            for param in config['vary_by']:
                value = request.query_params.get(param)
                if value:
                    key_parts.append(f"{param}={value}")
        
        # Add user context if authenticated
        user_id = getattr(request.state, 'user_id', None)
        if user_id:
            key_parts.append(f"user={user_id}")
        
        # Create hash
        key_string = '|'.join(key_parts)
        return hashlib.md5(key_string.encode()).hexdigest()
    
    async def _cache_response(self, cache_key: str, response: Response, request: Request):
        """Cache response data"""
        try:
            path = request.url.path
            config = self._get_cache_config(path)
            ttl = config.get('ttl', 300) if config else 300
            
            # Read response body
            body = b""
            async for chunk in response.body_iterator:
                body += chunk
            
            # Parse JSON if possible
            try:
                data = json.loads(body.decode())
            except:
                data = body.decode()
            
            # Store in cache
            cache_data = {
                'data': data,
                'headers': dict(response.headers),
                'status_code': response.status_code,
                'cached_at': datetime.utcnow().isoformat()
            }
            
            await self.cache.set(cache_key, cache_data, ttl)
            
            # Recreate response with body
            response.body_iterator = self._iter_body(body)
            
        except Exception as e:
            logger.error(f"Cache store error: {e}")
    
    def _iter_body(self, body: bytes):
        """Create body iterator from bytes"""
        yield body
    
    async def _create_cached_response(self, cached_data: Dict[str, Any], request: Request) -> Response:
        """Create response from cached data"""
        try:
            headers = cached_data.get('headers', {})
            
            # Add cache hit headers
            headers['X-Cache'] = 'HIT'
            headers['X-Cache-Date'] = cached_data.get('cached_at', '')
            
            # Create JSON response
            return JSONResponse(
                content=cached_data['data'],
                status_code=cached_data.get('status_code', 200),
                headers=headers
            )
            
        except Exception as e:
            logger.error(f"Cache response creation error: {e}")
            # Return None to force fresh request
            return None
    
    async def _add_cache_headers(self, response: Response, request: Request, cached: bool = False):
        """Add cache-related headers to response"""
        try:
            path = request.url.path
            config = self._get_cache_config(path)
            
            if not cached:
                response.headers['X-Cache'] = 'MISS'
                
            if config:
                ttl = config.get('ttl', 300)
                response.headers['Cache-Control'] = f'public, max-age={ttl}'
                response.headers['X-Cache-TTL'] = str(ttl)
            
        except Exception as e:
            logger.error(f"Cache headers error: {e}")

# Cache management utilities
class CacheManager:
    """Cache management utilities"""
    
    def __init__(self, cache_middleware: ResponseCacheMiddleware):
        self.middleware = cache_middleware
        self.cache = cache_middleware.cache
    
    async def clear_all(self) -> bool:
        """Clear all cache entries"""
        return await self.cache.clear()
    
    async def clear_pattern(self, pattern: str) -> int:
        """Clear cache entries matching pattern"""
        cleared = 0
        keys_to_delete = []
        
        for key in self.cache.cache.keys():
            if pattern in key:
                keys_to_delete.append(key)
        
        for key in keys_to_delete:
            if await self.cache.delete(key):
                cleared += 1
        
        return cleared
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        base_stats = self.cache.get_stats()
        
        # Add additional stats
        cache_entries = []
        for key, entry in self.cache.cache.items():
            cache_entries.append({
                'key': key[:20] + '...' if len(key) > 20 else key,
                'created_at': entry.get('created_at', 0),
                'expires_at': entry.get('expires_at', 0),
                'age_seconds': time.time() - entry.get('created_at', 0)
            })
        
        base_stats['entries'] = cache_entries[:10]  # Show first 10
        base_stats['config'] = self.middleware.cache_config
        
        return base_stats
    
    async def warm_cache(self, urls: List[str]) -> Dict[str, bool]:
        """Pre-warm cache with popular URLs"""
        results = {}
        
        for url in urls:
            try:
                # This would require making internal requests
                # Implementation depends on FastAPI app setup
                results[url] = True
            except Exception as e:
                logger.error(f"Cache warm error for {url}: {e}")
                results[url] = False
        
        return results

# Global cache instance
response_cache_middleware = None
cache_manager = None

def get_cache_manager() -> Optional[CacheManager]:
    """Get global cache manager instance"""
    return cache_manager

def initialize_cache_middleware(app) -> ResponseCacheMiddleware:
    """Initialize and return cache middleware instance"""
    global response_cache_middleware, cache_manager
    
    response_cache_middleware = ResponseCacheMiddleware(app)
    cache_manager = CacheManager(response_cache_middleware)
    
    return response_cache_middleware 