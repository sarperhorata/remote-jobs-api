import pytest
import asyncio
import time
from services.cache_service import CacheService

class TestCacheService:
    """In-memory Cache Service testleri"""
    
    @pytest.fixture
    def cache_service(self):
        """Cache service instance"""
        return CacheService(max_size=3, ttl_hours=1)  # Small cache for testing
    
    @pytest.mark.asyncio
    async def test_service_initialization(self, cache_service):
        """Service başlatma testi"""
        assert cache_service.max_size == 3
        assert cache_service.ttl_hours == 1
        assert cache_service.popular_ttl_hours == 72
        assert len(cache_service.cache) == 0
        assert len(cache_service.popular_cache) == 0
    
    @pytest.mark.asyncio
    async def test_set_and_get_normal_cache(self, cache_service):
        """Normal cache set/get testi"""
        # Set value
        result = await cache_service.set("test_key", {"data": "test_value"})
        assert result is True
        
        # Get value
        value = await cache_service.get("test_key")
        assert value == {"data": "test_value"}
    
    @pytest.mark.asyncio
    async def test_set_and_get_popular_cache(self, cache_service):
        """Popular keyword cache testi"""
        # Set popular keyword (should use popular cache)
        result = await cache_service.set("react developer", {"jobs": [1, 2, 3]})
        assert result is True
        
        # Should be in popular cache, not normal cache
        assert "react developer" in cache_service.popular_cache
        assert "react developer" not in cache_service.cache
        
        # Get value
        value = await cache_service.get("react developer")
        assert value == {"jobs": [1, 2, 3]}
    
    @pytest.mark.asyncio
    async def test_cache_miss(self, cache_service):
        """Cache miss testi"""
        value = await cache_service.get("nonexistent_key")
        assert value is None
    
    @pytest.mark.asyncio
    async def test_cache_ttl_expiry(self, cache_service):
        """TTL expiry testi"""
        # Set with very short TTL
        result = await cache_service.set("short_ttl_key", "test_value", ttl_hours=0.001)  # ~3.6 seconds
        assert result is True
        
        # Should exist immediately
        value = await cache_service.get("short_ttl_key")
        assert value == "test_value"
        
        # Wait for expiry (simulate)
        await asyncio.sleep(0.1)  # Wait a bit
        
        # Manually expire by setting past time
        cache_service.expiry_times["short_ttl_key"] = time.time() - 1
        
        # Should be expired now
        value = await cache_service.get("short_ttl_key")
        assert value is None
    
    @pytest.mark.asyncio
    async def test_lru_eviction(self, cache_service):
        """LRU eviction testi"""
        # Fill cache to max capacity (3 items)
        await cache_service.set("key1", "value1")
        await cache_service.set("key2", "value2")
        await cache_service.set("key3", "value3")
        
        assert len(cache_service.cache) == 3
        
        # Add one more item - should evict oldest (key1)
        await cache_service.set("key4", "value4")
        
        assert len(cache_service.cache) == 3
        assert await cache_service.get("key1") is None  # Evicted
        assert await cache_service.get("key2") == "value2"
        assert await cache_service.get("key3") == "value3"
        assert await cache_service.get("key4") == "value4"
    
    @pytest.mark.asyncio
    async def test_popular_keyword_detection(self, cache_service):
        """Popular keyword detection testi"""
        popular_keywords = [
            "react developer",
            "python engineer", 
            "javascript fullstack",
            "java backend",
            "node.js developer"
        ]
        
        for keyword in popular_keywords:
            is_popular = cache_service._is_popular_keyword(keyword)
            assert is_popular is True
            
        non_popular_keywords = [
            "unique_job_title_xyz",
            "very_specific_role_abc",
            "random_search_term"
        ]
        
        for keyword in non_popular_keywords:
            is_popular = cache_service._is_popular_keyword(keyword)
            assert is_popular is False
    
    @pytest.mark.asyncio
    async def test_delete_cache(self, cache_service):
        """Cache delete testi"""
        # Set value
        await cache_service.set("delete_test", "value_to_delete")
        assert await cache_service.get("delete_test") == "value_to_delete"
        
        # Delete value
        result = await cache_service.delete("delete_test")
        assert result is True
        
        # Should be None after delete
        assert await cache_service.get("delete_test") is None
    
    @pytest.mark.asyncio
    async def test_clear_cache(self, cache_service):
        """Cache clear testi"""
        # Set some values
        await cache_service.set("key1", "value1")
        await cache_service.set("react job", "popular_value")  # Popular cache
        
        assert len(cache_service.cache) == 1
        assert len(cache_service.popular_cache) == 1
        
        # Clear all cache
        result = await cache_service.clear()
        assert result is True
        
        # All caches should be empty
        assert len(cache_service.cache) == 0
        assert len(cache_service.popular_cache) == 0
        assert len(cache_service.access_times) == 0
        assert len(cache_service.popular_access_times) == 0
    
    @pytest.mark.asyncio
    async def test_cache_with_json_serializable_data(self, cache_service):
        """JSON serializable data testi"""
        test_data = {
            "jobs": [
                {"id": 1, "title": "Developer", "salary": 50000},
                {"id": 2, "title": "Designer", "salary": 45000}
            ],
            "metadata": {
                "total_count": 2,
                "search_query": "test search",
                "timestamp": "2024-01-15T10:00:00Z"
            }
        }
        
        await cache_service.set("complex_data", test_data)
        result = await cache_service.get("complex_data")
        
        assert result == test_data
        assert result["jobs"][0]["title"] == "Developer"
        assert result["metadata"]["total_count"] == 2
    
    @pytest.mark.asyncio
    async def test_cache_performance_stats(self, cache_service):
        """Cache performance istatistikleri"""
        # Get performance stats
        stats = await cache_service.get_stats()
        
        assert "regular_cache" in stats
        assert "popular_cache" in stats
        assert "total_entries" in stats
        assert stats["regular_cache"]["size"] == 0
        assert stats["popular_cache"]["size"] == 0
        
        # Add some data and check stats
        await cache_service.set("test1", "value1")
        await cache_service.set("react test", "popular_value")
        
        stats = await cache_service.get_stats()
        assert stats["regular_cache"]["size"] == 1
        assert stats["popular_cache"]["size"] == 1
        assert stats["total_entries"] == 2 