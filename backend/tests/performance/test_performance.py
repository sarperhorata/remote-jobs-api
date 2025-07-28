"""
Performance Tests
Tests for performance optimization
"""

import pytest
import asyncio
import time
from typing import List, Dict, Any
from unittest.mock import Mock, patch

from backend.tests.utils.performance_helper import (
    PerformanceTestHelper,
    performance_test,
    measure_time,
    measure_memory,
    DatabasePerformanceHelper,
    CachePerformanceHelper
)
from backend.utils.schema_validator import schema_validator, performance_monitor
from backend.utils.objectid_helper import objectid_helper
from backend.utils.async_iterator_helper import async_iterator_helper


@pytest.fixture
def performance_helper():
    """Create performance test helper"""
    return PerformanceTestHelper()


@pytest.fixture
def db_performance_helper():
    """Create database performance helper"""
    # Mock database for testing
    mock_db = Mock()
    return DatabasePerformanceHelper(mock_db)


@pytest.fixture
def cache_performance_helper():
    """Create cache performance helper"""
    return CachePerformanceHelper()


class TestSchemaValidationPerformance:
    """Test schema validation performance"""
    
    def test_schema_validation_speed(self, performance_helper):
        """Test schema validation speed"""
        from backend.utils.schema_validator import BaseSchema
        
        class TestSchema(BaseSchema):
            name: str
            email: str
            age: int
        
        # Test data
        test_data = {
            "name": "Test User",
            "email": "test@example.com",
            "age": 25
        }
        
        # Benchmark validation
        stats = performance_helper.benchmark_function(
            schema_validator.validate_with_cache,
            iterations=100,
            schema_class=TestSchema,
            data=test_data
        )
        
        # Assert performance
        performance_helper.assert_performance_threshold(stats, max_avg_time=0.01)
    
    def test_batch_validation_performance(self, performance_helper):
        """Test batch validation performance"""
        from backend.utils.schema_validator import BaseSchema
        
        class TestSchema(BaseSchema):
            name: str
            email: str
        
        # Test data
        test_data_list = [
            {"name": f"User {i}", "email": f"user{i}@example.com"}
            for i in range(100)
        ]
        
        # Benchmark batch validation
        stats = performance_helper.benchmark_function(
            schema_validator.validate_batch,
            iterations=10,
            schema_class=TestSchema,
            data_list=test_data_list
        )
        
        # Assert performance
        performance_helper.assert_performance_threshold(stats, max_avg_time=0.1)
    
    def test_validation_cache_performance(self, performance_helper):
        """Test validation cache performance"""
        from backend.utils.schema_validator import BaseSchema
        
        class TestSchema(BaseSchema):
            name: str
            email: str
        
        test_data = {"name": "Test", "email": "test@example.com"}
        
        # First validation (cache miss)
        start_time = time.time()
        schema_validator.validate_with_cache(TestSchema, test_data)
        first_time = time.time() - start_time
        
        # Second validation (cache hit)
        start_time = time.time()
        schema_validator.validate_with_cache(TestSchema, test_data)
        second_time = time.time() - start_time
        
        # Cache hit should be faster
        assert second_time < first_time, "Cache hit should be faster than cache miss"
        assert second_time < 0.001, "Cache hit should be very fast"


class TestObjectIdPerformance:
    """Test ObjectId operations performance"""
    
    def test_objectid_conversion_performance(self, performance_helper):
        """Test ObjectId conversion performance"""
        from bson import ObjectId
        
        # Test data
        objectid = ObjectId()
        objectid_str = str(objectid)
        
        # Benchmark conversion
        stats = performance_helper.benchmark_function(
            objectid_helper.to_objectid,
            iterations=1000,
            objectid_str=objectid_str
        )
        
        # Assert performance
        performance_helper.assert_performance_threshold(stats, max_avg_time=0.001)
    
    def test_objectid_validation_performance(self, performance_helper):
        """Test ObjectId validation performance"""
        from bson import ObjectId
        
        # Test data
        valid_id = str(ObjectId())
        invalid_id = "invalid_id"
        
        # Benchmark valid ID validation
        stats = performance_helper.benchmark_function(
            objectid_helper.is_valid_objectid,
            iterations=1000,
            objectid_str=valid_id
        )
        
        # Assert performance
        performance_helper.assert_performance_threshold(stats, max_avg_time=0.001)
    
    def test_dict_objectid_conversion_performance(self, performance_helper):
        """Test dictionary ObjectId conversion performance"""
        from bson import ObjectId
        
        # Test data with ObjectIds
        test_data = {
            "id": ObjectId(),
            "user_id": ObjectId(),
            "nested": {
                "item_id": ObjectId(),
                "list": [ObjectId(), ObjectId()]
            }
        }
        
        # Benchmark conversion
        stats = performance_helper.benchmark_function(
            objectid_helper.convert_dict_objectids,
            iterations=100,
            data=test_data
        )
        
        # Assert performance
        performance_helper.assert_performance_threshold(stats, max_avg_time=0.01)


class TestAsyncIteratorPerformance:
    """Test async iterator performance"""
    
    @pytest.mark.asyncio
    async def test_cursor_to_list_performance(self, performance_helper):
        """Test cursor to list conversion performance"""
        from motor.motor_asyncio import AsyncIOMotorCursor
        
        # Mock cursor
        mock_cursor = Mock(spec=AsyncIOMotorCursor)
        mock_cursor.to_list.return_value = [{"id": i} for i in range(100)]
        
        # Benchmark conversion
        stats = await performance_helper.benchmark_async_function(
            async_iterator_helper.cursor_to_list,
            iterations=50,
            cursor=mock_cursor
        )
        
        # Assert performance
        performance_helper.assert_performance_threshold(stats, max_avg_time=0.1)
    
    @pytest.mark.asyncio
    async def test_cursor_batch_performance(self, performance_helper):
        """Test cursor batch processing performance"""
        from motor.motor_asyncio import AsyncIOMotorCursor
        
        # Mock cursor with async iterator
        async def mock_cursor():
            for i in range(100):
                yield {"id": i}
        
        # Benchmark batch processing
        stats = await performance_helper.benchmark_async_function(
            async_iterator_helper.cursor_batch,
            iterations=10,
            cursor=mock_cursor(),
            batch_size=10
        )
        
        # Assert performance
        performance_helper.assert_performance_threshold(stats, max_avg_time=0.5)


class TestDatabasePerformance:
    """Test database performance"""
    
    @pytest.mark.asyncio
    async def test_query_performance(self, db_performance_helper):
        """Test database query performance"""
        # Mock query function
        async def mock_query():
            await asyncio.sleep(0.01)  # Simulate database delay
            return [{"id": i} for i in range(10)]
        
        # Benchmark query
        stats = await db_performance_helper.benchmark_query(
            "test_query",
            mock_query,
            iterations=10
        )
        
        # Assert performance
        db_performance_helper.assert_query_performance("test_query", max_avg_time=0.05)
    
    def test_slow_queries_detection(self, db_performance_helper):
        """Test slow queries detection"""
        # Add some test queries
        db_performance_helper.query_times = {
            "fast_query": {"avg_time": 0.01},
            "slow_query": {"avg_time": 2.0},
            "medium_query": {"avg_time": 0.5}
        }
        
        # Get slow queries
        slow_queries = db_performance_helper.get_slow_queries(threshold=1.0)
        
        # Should only return queries slower than 1 second
        assert len(slow_queries) == 1
        assert slow_queries[0]["query_name"] == "slow_query"


class TestCachePerformance:
    """Test cache performance"""
    
    def test_cache_performance_monitoring(self, cache_performance_helper):
        """Test cache performance monitoring"""
        # Record some cache accesses
        cache_performance_helper.record_cache_access("test_cache", True, 0.001)
        cache_performance_helper.record_cache_access("test_cache", False, 0.1)
        cache_performance_helper.record_cache_access("test_cache", True, 0.002)
        
        # Get stats
        stats = cache_performance_helper.get_cache_stats()
        
        # Check stats
        assert stats["hits"] == 2
        assert stats["misses"] == 1
        assert stats["total_accesses"] == 3
        assert stats["hit_rate"] == 2/3
    
    def test_cache_performance_assertions(self, cache_performance_helper):
        """Test cache performance assertions"""
        # Record good performance
        for i in range(10):
            cache_performance_helper.record_cache_access("test_cache", True, 0.001)
        
        # Should pass assertions
        cache_performance_helper.assert_cache_performance(min_hit_rate=0.8, max_avg_time=0.01)


class TestMemoryPerformance:
    """Test memory usage performance"""
    
    @measure_memory
    def test_memory_efficient_operations(self):
        """Test memory efficient operations"""
        # Create large data structure
        large_list = [{"id": i, "data": "x" * 100} for i in range(1000)]
        
        # Process data
        processed = [item["id"] for item in large_list]
        
        return len(processed)
    
    @measure_memory
    async def test_async_memory_usage(self):
        """Test async memory usage"""
        # Simulate async operation
        await asyncio.sleep(0.01)
        
        # Create some data
        data = [i for i in range(100)]
        
        return len(data)


class TestTimePerformance:
    """Test execution time performance"""
    
    @measure_time
    def test_fast_operation(self):
        """Test fast operation"""
        return sum(range(1000))
    
    @measure_time
    async def test_async_fast_operation(self):
        """Test async fast operation"""
        await asyncio.sleep(0.01)
        return "completed"


class TestPerformanceDecorators:
    """Test performance decorators"""
    
    @performance_test(max_time=0.1)
    async def test_performance_decorator(self):
        """Test performance decorator"""
        await asyncio.sleep(0.01)
        return "success"
    
    def test_performance_decorator_failure(self):
        """Test performance decorator with slow operation"""
        @performance_test(max_time=0.01)
        async def slow_operation():
            await asyncio.sleep(0.1)
            return "slow"
        
        # Should raise assertion error
        with pytest.raises(AssertionError):
            asyncio.run(slow_operation())


class TestPerformanceMonitoring:
    """Test performance monitoring"""
    
    def test_performance_monitor_metrics(self, performance_helper):
        """Test performance monitor metrics"""
        # Run some benchmarks
        performance_helper.benchmark_function(
            lambda: sum(range(100)),
            iterations=10
        )
        
        # Get slowest operations
        slowest = performance_helper.get_slowest_operations(limit=5)
        
        # Should have results
        assert len(slowest) > 0
        assert "avg_time" in slowest[0]
    
    def test_performance_report_generation(self, performance_helper):
        """Test performance report generation"""
        # Run some benchmarks
        performance_helper.benchmark_function(
            lambda: sum(range(100)),
            iterations=5
        )
        
        # Generate report
        report = performance_helper.generate_performance_report()
        
        # Check report content
        assert "Performance Test Report" in report
        assert "Summary" in report
        assert "Slowest Operations" in report


class TestPerformanceOptimizations:
    """Test performance optimizations"""
    
    def test_schema_cache_optimization(self):
        """Test schema cache optimization"""
        from backend.utils.schema_validator import BaseSchema
        
        class TestSchema(BaseSchema):
            name: str
            email: str
        
        test_data = {"name": "Test", "email": "test@example.com"}
        
        # Clear cache
        schema_validator.clear_cache()
        
        # First validation
        start_time = time.time()
        schema_validator.validate_with_cache(TestSchema, test_data)
        first_time = time.time() - start_time
        
        # Second validation (should use cache)
        start_time = time.time()
        schema_validator.validate_with_cache(TestSchema, test_data)
        second_time = time.time() - start_time
        
        # Cache should improve performance
        assert second_time < first_time * 0.5, "Cache should significantly improve performance"
    
    def test_batch_processing_optimization(self):
        """Test batch processing optimization"""
        # Test individual vs batch processing
        items = [{"id": i} for i in range(100)]
        
        # Individual processing
        start_time = time.time()
        for item in items:
            objectid_helper.convert_dict_objectids(item)
        individual_time = time.time() - start_time
        
        # Batch processing
        start_time = time.time()
        objectid_helper.convert_list_objectids(items)
        batch_time = time.time() - start_time
        
        # Batch should be more efficient
        assert batch_time < individual_time, "Batch processing should be more efficient"


class TestPerformanceThresholds:
    """Test performance thresholds"""
    
    def test_schema_validation_thresholds(self):
        """Test schema validation performance thresholds"""
        from backend.utils.schema_validator import BaseSchema
        
        class TestSchema(BaseSchema):
            name: str
            email: str
            age: int
        
        test_data = {"name": "Test", "email": "test@example.com", "age": 25}
        
        # Should complete within threshold
        start_time = time.time()
        schema_validator.validate_with_cache(TestSchema, test_data)
        validation_time = time.time() - start_time
        
        assert validation_time < 0.01, f"Schema validation took {validation_time:.3f}s, should be < 0.01s"
    
    def test_objectid_operations_thresholds(self):
        """Test ObjectId operations performance thresholds"""
        from bson import ObjectId
        
        objectid = ObjectId()
        objectid_str = str(objectid)
        
        # Should complete within threshold
        start_time = time.time()
        result = objectid_helper.to_objectid(objectid_str)
        operation_time = time.time() - start_time
        
        assert operation_time < 0.001, f"ObjectId conversion took {operation_time:.3f}s, should be < 0.001s"
        assert result == objectid 