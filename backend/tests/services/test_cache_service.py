import pytest
from unittest.mock import Mock, patch, AsyncMock
import json
import hashlib
from services.cache_service import CacheService

class TestCacheService:
    """Cache Service testleri"""
    
    @pytest.fixture
    def mock_redis(self):
        """Mock Redis client"""
        mock_redis = Mock()
        mock_redis.ping.return_value = True
        mock_redis.get.return_value = None
        mock_redis.setex.return_value = True
        mock_redis.delete.return_value = 1
        mock_redis.exists.return_value = 1
        return mock_redis
    
    @pytest.fixture
    def cache_service_with_redis(self, mock_redis):
        """Redis ile cache service instance"""
        with patch('services.cache_service.redis.Redis', return_value=mock_redis):
            service = CacheService()
            return service, mock_redis
    
    @pytest.fixture
    def cache_service_without_redis(self):
        """Redis olmadan cache service instance"""
        with patch('services.cache_service.redis.Redis', side_effect=Exception("Redis connection failed")):
            service = CacheService()
            return service
    
    def test_service_initialization_with_redis(self, cache_service_with_redis):
        """Redis ile service başlatma testi"""
        service, mock_redis = cache_service_with_redis
        
        assert service.enabled is True
        assert service.redis_client is not None
        mock_redis.ping.assert_called_once()
    
    def test_service_initialization_without_redis(self, cache_service_without_redis):
        """Redis olmadan service başlatma testi"""
        service = cache_service_without_redis
        
        assert service.enabled is False
        assert service.redis_client is None
    
    def test_generate_key(self, cache_service_with_redis):
        """Cache key generation testi"""
        service, _ = cache_service_with_redis
        
        params = {"query": "python", "location": "remote"}
        key = service._generate_key("jobs", params)
        
        assert key.startswith("buzz2remote:jobs:")
        assert len(key.split(":")[-1]) == 8  # MD5 hash length
    
    def test_generate_key_consistent(self, cache_service_with_redis):
        """Cache key consistency testi"""
        service, _ = cache_service_with_redis
        
        params = {"query": "python", "location": "remote"}
        key1 = service._generate_key("jobs", params)
        key2 = service._generate_key("jobs", params)
        
        assert key1 == key2  # Same params should generate same key
    
    @pytest.mark.asyncio
    async def test_get_with_redis(self, cache_service_with_redis):
        """Redis ile get testi"""
        service, mock_redis = cache_service_with_redis
        
        # Mock successful get
        mock_redis.get.return_value = json.dumps({"data": "test"})
        
        result = await service.get("test_key")
        
        assert result == {"data": "test"}
        mock_redis.get.assert_called_once_with("test_key")
    
    @pytest.mark.asyncio
    async def test_get_without_redis(self, cache_service_without_redis):
        """Redis olmadan get testi"""
        service = cache_service_without_redis
        
        result = await service.get("test_key")
        
        assert result is None
    
    @pytest.mark.asyncio
    async def test_get_invalid_json(self, cache_service_with_redis):
        """Invalid JSON get testi"""
        service, mock_redis = cache_service_with_redis
        
        # Mock invalid JSON
        mock_redis.get.return_value = "invalid json"
        
        result = await service.get("test_key")
        
        assert result is None
    
    @pytest.mark.asyncio
    async def test_set_with_redis(self, cache_service_with_redis):
        """Redis ile set testi"""
        service, mock_redis = cache_service_with_redis
        
        data = {"test": "data"}
        result = await service.set("test_key", data, expire=300)
        
        assert result is True
        mock_redis.setex.assert_called_once_with("test_key", 300, json.dumps(data, default=str))
    
    @pytest.mark.asyncio
    async def test_set_without_redis(self, cache_service_without_redis):
        """Redis olmadan set testi"""
        service = cache_service_without_redis
        
        result = await service.set("test_key", {"test": "data"})
        
        assert result is False
    
    @pytest.mark.asyncio
    async def test_get_jobs_cache(self, cache_service_with_redis):
        """Jobs cache get testi"""
        service, mock_redis = cache_service_with_redis
        
        filters = {"query": "python", "location": "remote"}
        page = 1
        limit = 10
        
        # Mock successful get
        cached_data = {"jobs": [{"id": "1", "title": "Python Developer"}]}
        mock_redis.get.return_value = json.dumps(cached_data)
        
        result = await service.get_jobs_cache(filters, page, limit)
        
        assert result == cached_data
        
        # Verify key generation
        expected_key = service._generate_key("jobs", {**filters, "page": page, "limit": limit})
        mock_redis.get.assert_called_once_with(expected_key)
    
    @pytest.mark.asyncio
    async def test_set_jobs_cache(self, cache_service_with_redis):
        """Jobs cache set testi"""
        service, mock_redis = cache_service_with_redis
        
        filters = {"query": "python", "location": "remote"}
        page = 1
        limit = 10
        data = {"jobs": [{"id": "1", "title": "Python Developer"}]}
        expire = 600
        
        result = await service.set_jobs_cache(filters, page, limit, data, expire)
        
        assert result is True
        
        # Verify key generation and set
        expected_key = service._generate_key("jobs", {**filters, "page": page, "limit": limit})
        mock_redis.setex.assert_called_once_with(expected_key, expire, json.dumps(data, default=str))
    
    @pytest.mark.asyncio
    async def test_get_user_cache(self, cache_service_with_redis):
        """User cache get testi"""
        service, mock_redis = cache_service_with_redis
        
        user_id = "user123"
        cache_type = "preferences"
        
        # Mock successful get
        cached_data = {"theme": "dark", "notifications": True}
        mock_redis.get.return_value = json.dumps(cached_data)
        
        result = await service.get_user_cache(user_id, cache_type)
        
        assert result == cached_data
        
        # Verify key generation
        expected_key = service._generate_key(f"user_{cache_type}", {"user_id": user_id})
        mock_redis.get.assert_called_once_with(expected_key)
    
    @pytest.mark.asyncio
    async def test_set_user_cache(self, cache_service_with_redis):
        """User cache set testi"""
        service, mock_redis = cache_service_with_redis
        
        user_id = "user123"
        cache_type = "preferences"
        data = {"theme": "dark", "notifications": True}
        expire = 3600
        
        result = await service.set_user_cache(user_id, cache_type, data, expire)
        
        assert result is True
        
        # Verify key generation and set
        expected_key = service._generate_key(f"user_{cache_type}", {"user_id": user_id})
        mock_redis.setex.assert_called_once_with(expected_key, expire, json.dumps(data, default=str))
    
    @pytest.mark.asyncio
    async def test_delete_cache(self, cache_service_with_redis):
        """Cache delete testi"""
        service, mock_redis = cache_service_with_redis
        
        result = await service.delete("test_key")
        
        assert result is True
        mock_redis.delete.assert_called_once_with("test_key")
    
    @pytest.mark.asyncio
    async def test_exists_cache(self, cache_service_with_redis):
        """Cache exists testi"""
        service, mock_redis = cache_service_with_redis
        
        result = await service.exists("test_key")
        
        assert result is True
        mock_redis.exists.assert_called_once_with("test_key")
    
    @pytest.mark.asyncio
    async def test_clear_all_cache(self, cache_service_with_redis):
        """Clear all cache testi"""
        service, mock_redis = cache_service_with_redis
        
        # Mock keys pattern
        mock_redis.keys.return_value = ["buzz2remote:jobs:12345678", "buzz2remote:user_preferences:87654321"]
        
        result = await service.clear_all_cache()
        
        assert result is True
        mock_redis.keys.assert_called_once_with("buzz2remote:*")
        assert mock_redis.delete.call_count == 2
    
    @pytest.mark.asyncio
    async def test_clear_pattern_cache(self, cache_service_with_redis):
        """Clear pattern cache testi"""
        service, mock_redis = cache_service_with_redis
        
        pattern = "buzz2remote:jobs:*"
        mock_redis.keys.return_value = ["buzz2remote:jobs:12345678", "buzz2remote:jobs:87654321"]
        
        result = await service.clear_pattern_cache(pattern)
        
        assert result is True
        mock_redis.keys.assert_called_once_with(pattern)
        assert mock_redis.delete.call_count == 2
    
    def test_cache_key_uniqueness(self, cache_service_with_redis):
        """Cache key uniqueness testi"""
        service, _ = cache_service_with_redis
        
        # Different params should generate different keys
        key1 = service._generate_key("jobs", {"query": "python"})
        key2 = service._generate_key("jobs", {"query": "javascript"})
        
        assert key1 != key2
        
        # Same params should generate same key
        key3 = service._generate_key("jobs", {"query": "python"})
        assert key1 == key3
    
    @pytest.mark.asyncio
    async def test_cache_service_integration(self, cache_service_with_redis):
        """Cache service integration testi"""
        service, mock_redis = cache_service_with_redis
        
        # Test full cache cycle
        test_data = {"test": "data", "number": 123}
        
        # Set data
        mock_redis.setex.return_value = True
        set_result = await service.set("test_key", test_data, expire=300)
        assert set_result is True
        
        # Get data
        mock_redis.get.return_value = json.dumps(test_data)
        get_result = await service.get("test_key")
        assert get_result == test_data
        
        # Check exists
        mock_redis.exists.return_value = 1
        exists_result = await service.exists("test_key")
        assert exists_result is True
        
        # Delete data
        mock_redis.delete.return_value = 1
        delete_result = await service.delete("test_key")
        assert delete_result is True
    
    def test_cache_service_methods_exist(self, cache_service_with_redis):
        """Cache service metodlarının varlığını test et"""
        service, _ = cache_service_with_redis
        
        required_methods = [
            '_generate_key',
            'get',
            'set',
            'get_jobs_cache',
            'set_jobs_cache',
            'get_user_cache',
            'set_user_cache',
            'delete',
            'exists',
            'clear_all_cache',
            'clear_pattern_cache'
        ]
        
        for method in required_methods:
            assert hasattr(service, method)
            assert callable(getattr(service, method)) 