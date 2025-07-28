"""
Performance Test Helper
Utilities for performance testing and optimization
"""

import time
import asyncio
import logging
import statistics
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime, UTC
from functools import wraps
import tracemalloc

logger = logging.getLogger(__name__)


class PerformanceMonitor:
    """Monitor performance metrics"""
    
    def __init__(self):
        self.metrics = {}
        self.start_time = None
        self.memory_snapshot = None
    
    def start_monitoring(self, operation_name: str):
        """Start monitoring an operation"""
        self.start_time = time.time()
        self.memory_snapshot = tracemalloc.take_snapshot()
        logger.info(f"Started monitoring: {operation_name}")
    
    def stop_monitoring(self, operation_name: str) -> Dict[str, Any]:
        """Stop monitoring and return metrics"""
        if self.start_time is None:
            return {}
        
        end_time = time.time()
        duration = end_time - self.start_time
        
        # Memory usage
        current_snapshot = tracemalloc.take_snapshot()
        memory_diff = current_snapshot.compare_to(self.memory_snapshot, 'lineno')
        memory_usage = sum(stat.size_diff for stat in memory_diff)
        
        metrics = {
            "duration": duration,
            "memory_usage": memory_usage,
            "timestamp": datetime.now(UTC).isoformat()
        }
        
        self.metrics[operation_name] = metrics
        logger.info(f"Operation {operation_name} completed in {duration:.3f}s, memory: {memory_usage} bytes")
        
        return metrics
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get all metrics"""
        return self.metrics
    
    def reset(self):
        """Reset metrics"""
        self.metrics.clear()
        self.start_time = None
        self.memory_snapshot = None


class PerformanceTestHelper:
    """Helper for performance testing"""
    
    def __init__(self):
        self.monitor = PerformanceMonitor()
        self.benchmarks = {}
    
    def benchmark_function(self, func: Callable, iterations: int = 100, *args, **kwargs) -> Dict[str, Any]:
        """Benchmark a function"""
        times = []
        memory_usage = []
        
        for i in range(iterations):
            self.monitor.start_monitoring(f"benchmark_{func.__name__}_{i}")
            
            # Run function
            result = func(*args, **kwargs)
            
            metrics = self.monitor.stop_monitoring(f"benchmark_{func.__name__}_{i}")
            times.append(metrics["duration"])
            memory_usage.append(metrics["memory_usage"])
        
        # Calculate statistics
        stats = {
            "function_name": func.__name__,
            "iterations": iterations,
            "avg_time": statistics.mean(times),
            "min_time": min(times),
            "max_time": max(times),
            "median_time": statistics.median(times),
            "std_dev_time": statistics.stdev(times) if len(times) > 1 else 0,
            "avg_memory": statistics.mean(memory_usage),
            "total_time": sum(times),
            "times": times
        }
        
        self.benchmarks[func.__name__] = stats
        return stats
    
    async def benchmark_async_function(self, func: Callable, iterations: int = 100, *args, **kwargs) -> Dict[str, Any]:
        """Benchmark an async function"""
        times = []
        memory_usage = []
        
        for i in range(iterations):
            self.monitor.start_monitoring(f"benchmark_{func.__name__}_{i}")
            
            # Run async function
            result = await func(*args, **kwargs)
            
            metrics = self.monitor.stop_monitoring(f"benchmark_{func.__name__}_{i}")
            times.append(metrics["duration"])
            memory_usage.append(metrics["memory_usage"])
        
        # Calculate statistics
        stats = {
            "function_name": func.__name__,
            "iterations": iterations,
            "avg_time": statistics.mean(times),
            "min_time": min(times),
            "max_time": max(times),
            "median_time": statistics.median(times),
            "std_dev_time": statistics.stdev(times) if len(times) > 1 else 0,
            "avg_memory": statistics.mean(memory_usage),
            "total_time": sum(times),
            "times": times
        }
        
        self.benchmarks[func.__name__] = stats
        return stats
    
    def assert_performance_threshold(self, stats: Dict[str, Any], max_avg_time: float, max_memory: int = None):
        """Assert performance meets thresholds"""
        assert stats["avg_time"] <= max_avg_time, f"Average time {stats['avg_time']:.3f}s exceeds threshold {max_avg_time}s"
        
        if max_memory:
            assert stats["avg_memory"] <= max_memory, f"Average memory {stats['avg_memory']} bytes exceeds threshold {max_memory} bytes"
    
    def get_slowest_operations(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get slowest operations"""
        sorted_benchmarks = sorted(
            self.benchmarks.values(),
            key=lambda x: x["avg_time"],
            reverse=True
        )
        return sorted_benchmarks[:limit]
    
    def generate_performance_report(self) -> str:
        """Generate performance report"""
        report = ["# Performance Test Report", ""]
        
        if not self.benchmarks:
            report.append("No benchmarks recorded.")
            return "\n".join(report)
        
        # Summary
        total_operations = len(self.benchmarks)
        total_time = sum(b["total_time"] for b in self.benchmarks.values())
        avg_time = total_time / total_operations
        
        report.extend([
            f"## Summary",
            f"- Total operations: {total_operations}",
            f"- Total time: {total_time:.3f}s",
            f"- Average time per operation: {avg_time:.3f}s",
            ""
        ])
        
        # Slowest operations
        report.append("## Slowest Operations")
        slowest = self.get_slowest_operations(5)
        for i, benchmark in enumerate(slowest, 1):
            report.extend([
                f"### {i}. {benchmark['function_name']}",
                f"- Average time: {benchmark['avg_time']:.3f}s",
                f"- Min time: {benchmark['min_time']:.3f}s",
                f"- Max time: {benchmark['max_time']:.3f}s",
                f"- Iterations: {benchmark['iterations']}",
                ""
            ])
        
        return "\n".join(report)


def performance_test(max_time: float = 1.0, max_memory: int = None):
    """Decorator for performance testing"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            helper = PerformanceTestHelper()
            
            # Run benchmark
            stats = await helper.benchmark_async_function(func, iterations=10, *args, **kwargs)
            
            # Assert performance
            helper.assert_performance_threshold(stats, max_time, max_memory)
            
            return await func(*args, **kwargs)
        
        return wrapper
    return decorator


def measure_time(func: Callable) -> Callable:
    """Decorator to measure function execution time"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        
        duration = end_time - start_time
        logger.info(f"{func.__name__} executed in {duration:.3f}s")
        
        return result
    
    @wraps(func)
    async def async_wrapper(*args, **kwargs):
        start_time = time.time()
        result = await func(*args, **kwargs)
        end_time = time.time()
        
        duration = end_time - start_time
        logger.info(f"{func.__name__} executed in {duration:.3f}s")
        
        return result
    
    if asyncio.iscoroutinefunction(func):
        return async_wrapper
    else:
        return wrapper


def measure_memory(func: Callable) -> Callable:
    """Decorator to measure memory usage"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        tracemalloc.start()
        snapshot1 = tracemalloc.take_snapshot()
        
        result = func(*args, **kwargs)
        
        snapshot2 = tracemalloc.take_snapshot()
        tracemalloc.stop()
        
        memory_diff = snapshot2.compare_to(snapshot1, 'lineno')
        memory_usage = sum(stat.size_diff for stat in memory_diff)
        
        logger.info(f"{func.__name__} used {memory_usage} bytes")
        
        return result
    
    @wraps(func)
    async def async_wrapper(*args, **kwargs):
        tracemalloc.start()
        snapshot1 = tracemalloc.take_snapshot()
        
        result = await func(*args, **kwargs)
        
        snapshot2 = tracemalloc.take_snapshot()
        tracemalloc.stop()
        
        memory_diff = snapshot2.compare_to(snapshot1, 'lineno')
        memory_usage = sum(stat.size_diff for stat in memory_diff)
        
        logger.info(f"{func.__name__} used {memory_usage} bytes")
        
        return result
    
    if asyncio.iscoroutinefunction(func):
        return async_wrapper
    else:
        return wrapper


class DatabasePerformanceHelper:
    """Helper for database performance testing"""
    
    def __init__(self, db):
        self.db = db
        self.query_times = {}
    
    async def benchmark_query(self, query_name: str, query_func: Callable, iterations: int = 10) -> Dict[str, Any]:
        """Benchmark a database query"""
        times = []
        
        for i in range(iterations):
            start_time = time.time()
            result = await query_func()
            end_time = time.time()
            
            duration = end_time - start_time
            times.append(duration)
        
        stats = {
            "query_name": query_name,
            "iterations": iterations,
            "avg_time": statistics.mean(times),
            "min_time": min(times),
            "max_time": max(times),
            "median_time": statistics.median(times),
            "total_time": sum(times)
        }
        
        self.query_times[query_name] = stats
        return stats
    
    def assert_query_performance(self, query_name: str, max_avg_time: float):
        """Assert query performance meets threshold"""
        if query_name not in self.query_times:
            raise ValueError(f"Query {query_name} not benchmarked")
        
        stats = self.query_times[query_name]
        assert stats["avg_time"] <= max_avg_time, f"Query {query_name} average time {stats['avg_time']:.3f}s exceeds threshold {max_avg_time}s"
    
    def get_slow_queries(self, threshold: float = 1.0) -> List[Dict[str, Any]]:
        """Get queries slower than threshold"""
        slow_queries = []
        
        for query_name, stats in self.query_times.items():
            if stats["avg_time"] > threshold:
                slow_queries.append(stats)
        
        return sorted(slow_queries, key=lambda x: x["avg_time"], reverse=True)


class CachePerformanceHelper:
    """Helper for cache performance testing"""
    
    def __init__(self):
        self.cache_hits = 0
        self.cache_misses = 0
        self.cache_times = {}
    
    def record_cache_access(self, cache_name: str, hit: bool, access_time: float):
        """Record cache access"""
        if hit:
            self.cache_hits += 1
        else:
            self.cache_misses += 1
        
        if cache_name not in self.cache_times:
            self.cache_times[cache_name] = []
        
        self.cache_times[cache_name].append(access_time)
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        total_accesses = self.cache_hits + self.cache_misses
        hit_rate = self.cache_hits / total_accesses if total_accesses > 0 else 0
        
        return {
            "hits": self.cache_hits,
            "misses": self.cache_misses,
            "total_accesses": total_accesses,
            "hit_rate": hit_rate,
            "cache_times": self.cache_times
        }
    
    def assert_cache_performance(self, min_hit_rate: float = 0.8, max_avg_time: float = 0.01):
        """Assert cache performance meets thresholds"""
        stats = self.get_cache_stats()
        
        assert stats["hit_rate"] >= min_hit_rate, f"Cache hit rate {stats['hit_rate']:.2%} below threshold {min_hit_rate:.2%}"
        
        for cache_name, times in self.cache_times.items():
            avg_time = statistics.mean(times)
            assert avg_time <= max_avg_time, f"Cache {cache_name} average time {avg_time:.3f}s exceeds threshold {max_avg_time}s"


# Global helpers
performance_helper = PerformanceTestHelper() 