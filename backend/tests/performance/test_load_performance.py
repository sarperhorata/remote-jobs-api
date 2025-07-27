import pytest
import asyncio
import time
import statistics
from concurrent.futures import ThreadPoolExecutor
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import psutil
import os
from main import app

class TestLoadPerformance:
    """Load testing and performance benchmarks"""
    
    @pytest.fixture
    def client(self):
        return TestClient(app)
    
    def test_single_request_performance(self, client):
        """Test single request response times"""
        endpoints = [
            "/health",
            "/api/v1/jobs/search?limit=10",
            "/api/v1/jobs/statistics",
            "/api/v1/jobs/recent"
        ]
        
        performance_results = {}
        
        for endpoint in endpoints:
            times = []
            for _ in range(10):  # 10 requests per endpoint
                start_time = time.time()
                response = client.get(endpoint)
                end_time = time.time()
                
                assert response.status_code in [200, 422, 404]
                times.append(end_time - start_time)
            
            avg_time = statistics.mean(times)
            max_time = max(times)
            min_time = min(times)
            
            performance_results[endpoint] = {
                "avg_response_time": avg_time,
                "max_response_time": max_time,
                "min_response_time": min_time,
                "std_dev": statistics.stdev(times) if len(times) > 1 else 0
            }
            
            # Performance assertions
            assert avg_time < 2.0, f"Average response time too slow for {endpoint}: {avg_time:.3f}s"
            assert max_time < 5.0, f"Max response time too slow for {endpoint}: {max_time:.3f}s"
        
        return performance_results
    
    def test_concurrent_requests(self, client):
        """Test system under concurrent load"""
        def make_request(endpoint):
            start_time = time.time()
            response = client.get(endpoint)
            end_time = time.time()
            return {
                "status_code": response.status_code,
                "response_time": end_time - start_time,
                "endpoint": endpoint
            }
        
        # Test concurrent requests
        endpoints = [
            "/api/v1/jobs/search?limit=5",
            "/api/v1/jobs/search?limit=10",
            "/api/v1/jobs/statistics",
            "/health"
        ]
        
        concurrent_requests = []
        for _ in range(5):  # 5 concurrent users
            concurrent_requests.extend(endpoints)
        
        start_time = time.time()
        with ThreadPoolExecutor(max_workers=10) as executor:
            results = list(executor.map(make_request, concurrent_requests))
        end_time = time.time()
        
        total_time = end_time - start_time
        avg_response_time = statistics.mean([r["response_time"] for r in results])
        
        # Performance assertions
        assert total_time < 10.0, f"Total concurrent test time too slow: {total_time:.3f}s"
        assert avg_response_time < 1.0, f"Average concurrent response time too slow: {avg_response_time:.3f}s"
        
        # Check all requests succeeded
        success_count = len([r for r in results if r["status_code"] in [200, 422]])
        success_rate = success_count / len(results)
        assert success_rate > 0.95, f"Success rate too low: {success_rate:.2%}"
        
        return {
            "total_requests": len(results),
            "total_time": total_time,
            "avg_response_time": avg_response_time,
            "success_rate": success_rate,
            "results": results
        }
    
    def test_memory_usage_under_load(self, client):
        """Test memory usage during load"""
        try:
            process = psutil.Process()
            initial_memory = process.memory_info().rss
            
            # Generate load
            for _ in range(50):
                client.get("/api/v1/jobs/search?limit=5")
            
            final_memory = process.memory_info().rss
            memory_increase = final_memory - initial_memory
            
            # Memory increase should be reasonable (< 100MB)
            assert memory_increase < 100 * 1024 * 1024, f"Memory increase too high: {memory_increase / 1024 / 1024:.2f}MB"
            
            return {
                "initial_memory_mb": initial_memory / 1024 / 1024,
                "final_memory_mb": final_memory / 1024 / 1024,
                "memory_increase_mb": memory_increase / 1024 / 1024
            }
            
        except ImportError:
            pytest.skip("psutil not available")
    
    def test_database_query_performance(self, client):
        """Test database query performance"""
        # Test different query complexities
        queries = [
            "/api/v1/jobs/search?q=python&limit=10",
            "/api/v1/jobs/search?q=python&work_type=remote&limit=20",
            "/api/v1/jobs/search?q=python&salary_range=50000-100000&limit=15",
            "/api/v1/jobs/search?q=python&experience=senior&job_type=full-time&limit=25"
        ]
        
        query_performance = {}
        
        for query in queries:
            times = []
            for _ in range(5):
                start_time = time.time()
                response = client.get(query)
                end_time = time.time()
                
                assert response.status_code in [200, 422]
                times.append(end_time - start_time)
            
            avg_time = statistics.mean(times)
            query_performance[query] = avg_time
            
            # Database queries should be reasonably fast
            assert avg_time < 3.0, f"Database query too slow for {query}: {avg_time:.3f}s"
        
        return query_performance
    
    def test_pagination_performance(self, client):
        """Test pagination performance with different page sizes"""
        page_sizes = [5, 10, 25, 50, 100]
        pagination_performance = {}
        
        for limit in page_sizes:
            times = []
            for page in range(1, 4):  # Test first 3 pages
                start_time = time.time()
                response = client.get(f"/api/v1/jobs/search?limit={limit}&page={page}")
                end_time = time.time()
                
                assert response.status_code in [200, 422]
                times.append(end_time - start_time)
            
            avg_time = statistics.mean(times)
            pagination_performance[f"limit_{limit}"] = avg_time
            
            # Larger page sizes should not be exponentially slower
            if limit <= 25:
                assert avg_time < 2.0, f"Pagination too slow for limit {limit}: {avg_time:.3f}s"
            else:
                assert avg_time < 3.0, f"Pagination too slow for limit {limit}: {avg_time:.3f}s"
        
        return pagination_performance
    
    def test_search_complexity_performance(self, client):
        """Test search performance with different complexity levels"""
        search_scenarios = [
            {"query": "python", "complexity": "simple"},
            {"query": "python developer remote", "complexity": "medium"},
            {"query": "python developer remote full-time senior 80000", "complexity": "complex"},
            {"query": "python developer remote full-time senior 80000-120000 san francisco", "complexity": "very_complex"}
        ]
        
        complexity_performance = {}
        
        for scenario in search_scenarios:
            times = []
            for _ in range(5):
                start_time = time.time()
                response = client.get(f"/api/v1/jobs/search?q={scenario['query']}&limit=10")
                end_time = time.time()
                
                assert response.status_code in [200, 422]
                times.append(end_time - start_time)
            
            avg_time = statistics.mean(times)
            complexity_performance[scenario["complexity"]] = avg_time
            
            # Complex searches should not be significantly slower
            if scenario["complexity"] in ["simple", "medium"]:
                assert avg_time < 2.0, f"Search too slow for {scenario['complexity']}: {avg_time:.3f}s"
            else:
                assert avg_time < 3.0, f"Search too slow for {scenario['complexity']}: {avg_time:.3f}s"
        
        return complexity_performance
    
    def test_error_handling_performance(self, client):
        """Test performance when handling errors"""
        error_scenarios = [
            "/api/v1/jobs/search?limit=invalid",
            "/api/v1/jobs/search?page=-1",
            "/api/v1/jobs/search?salary_range=invalid",
            "/api/v1/jobs/nonexistent-id"
        ]
        
        error_performance = {}
        
        for scenario in error_scenarios:
            times = []
            for _ in range(5):
                start_time = time.time()
                response = client.get(scenario)
                end_time = time.time()
                
                # Should handle errors gracefully
                assert response.status_code in [400, 404, 422]
                times.append(end_time - start_time)
            
            avg_time = statistics.mean(times)
            error_performance[scenario] = avg_time
            
            # Error handling should be fast
            assert avg_time < 1.0, f"Error handling too slow for {scenario}: {avg_time:.3f}s"
        
        return error_performance

class TestStressPerformance:
    """Stress testing for system limits"""
    
    @pytest.fixture
    def client(self):
        return TestClient(app)
    
    def test_rapid_fire_requests(self, client):
        """Test system under rapid fire requests"""
        def rapid_request():
            start_time = time.time()
            response = client.get("/api/v1/jobs/search?limit=1")
            end_time = time.time()
            return {
                "status_code": response.status_code,
                "response_time": end_time - start_time
            }
        
        # Make 100 rapid requests
        start_time = time.time()
        with ThreadPoolExecutor(max_workers=20) as executor:
            futures = [executor.submit(rapid_request) for _ in range(100)]
            results = [future.result() for future in futures]
        end_time = time.time()
        
        total_time = end_time - start_time
        response_times = [r["response_time"] for r in results]
        
        # Performance assertions
        assert total_time < 30.0, f"Rapid fire test too slow: {total_time:.3f}s"
        assert statistics.mean(response_times) < 2.0, f"Average rapid response time too slow: {statistics.mean(response_times):.3f}s"
        
        # Success rate should be high
        success_count = len([r for r in results if r["status_code"] in [200, 422]])
        success_rate = success_count / len(results)
        assert success_rate > 0.9, f"Success rate too low under stress: {success_rate:.2%}"
        
        return {
            "total_requests": len(results),
            "total_time": total_time,
            "avg_response_time": statistics.mean(response_times),
            "success_rate": success_rate,
            "max_response_time": max(response_times),
            "min_response_time": min(response_times)
        }
    
    def test_large_payload_handling(self, client):
        """Test handling of large payloads"""
        # Test with large search queries
        large_queries = [
            "a" * 1000,  # 1KB query
            "python developer " * 100,  # ~2KB query
            "remote full-time senior " * 200  # ~4KB query
        ]
        
        large_payload_performance = {}
        
        for query in large_queries:
            start_time = time.time()
            response = client.get(f"/api/v1/jobs/search?q={query}&limit=5")
            end_time = time.time()
            
            response_time = end_time - start_time
            
            # Should handle large payloads gracefully
            assert response.status_code in [200, 400, 413, 422]
            assert response_time < 5.0, f"Large payload handling too slow: {response_time:.3f}s"
            
            large_payload_performance[f"query_size_{len(query)}"] = response_time
        
        return large_payload_performance
    
    def test_sustained_load(self, client):
        """Test system under sustained load"""
        def sustained_request():
            return client.get("/api/v1/jobs/search?limit=10")
        
        # Sustained load for 30 seconds
        start_time = time.time()
        request_count = 0
        successful_requests = 0
        
        while time.time() - start_time < 30:  # 30 seconds
            response = sustained_request()
            request_count += 1
            
            if response.status_code in [200, 422]:
                successful_requests += 1
            
            time.sleep(0.1)  # Small delay to avoid overwhelming
        
        total_time = time.time() - start_time
        success_rate = successful_requests / request_count if request_count > 0 else 0
        
        # Performance assertions
        assert request_count > 100, f"Not enough requests made: {request_count}"
        assert success_rate > 0.95, f"Success rate too low under sustained load: {success_rate:.2%}"
        
        return {
            "total_requests": request_count,
            "successful_requests": successful_requests,
            "success_rate": success_rate,
            "total_time": total_time,
            "requests_per_second": request_count / total_time
        }