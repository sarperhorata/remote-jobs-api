import pytest
import time
import asyncio
import statistics
from unittest.mock import AsyncMock, MagicMock
from fastapi.testclient import TestClient

class TestPerformanceBenchmarks:
    """Performance benchmarking testleri"""
    
    def test_api_response_time_benchmark(self, client):
        """API yanıt sürelerinin benchmark'ını test eder"""
        endpoints = [
            "/health",
            "/",
            "/docs",
            "/api/v1/jobs/",
            "/api/v1/companies/",
            "/api/v1/users/"
        ]
        
        results = {}
        
        for endpoint in endpoints:
            times = []
            for _ in range(10):  # 10 test
                start_time = time.time()
                response = client.get(endpoint)
                end_time = time.time()
                
                if response.status_code in [200, 404]:  # Geçerli yanıtlar
                    times.append(end_time - start_time)
            
            if times:
                results[endpoint] = {
                    'avg_time': statistics.mean(times),
                    'min_time': min(times),
                    'max_time': max(times),
                    'median_time': statistics.median(times),
                    'std_dev': statistics.stdev(times) if len(times) > 1 else 0
                }
        
        # Benchmark kriterleri
        for endpoint, metrics in results.items():
            assert metrics['avg_time'] < 5.0, f"{endpoint} average response time too slow: {metrics['avg_time']:.3f}s"
            assert metrics['max_time'] < 10.0, f"{endpoint} max response time too slow: {metrics['max_time']:.3f}s"
    
    def test_concurrent_requests_benchmark(self, client):
        """Eşzamanlı isteklerin benchmark'ını test eder"""
        import concurrent.futures
        
        def make_request():
            return client.get("/health")
        
        # Farklı eşzamanlı istek sayıları ile test
        concurrent_levels = [5, 10, 20]
        
        for level in concurrent_levels:
            start_time = time.time()
            
            with concurrent.futures.ThreadPoolExecutor(max_workers=level) as executor:
                futures = [executor.submit(make_request) for _ in range(level)]
                responses = [future.result() for future in futures]
            
            end_time = time.time()
            total_time = end_time - start_time
            
            # Tüm istekler başarılı olmalı
            success_count = sum(1 for r in responses if r.status_code == 200)
            assert success_count == level, f"Only {success_count}/{level} requests succeeded"
            
            # Eşzamanlı istekler makul sürede tamamlanmalı
            assert total_time < 15.0, f"Concurrent requests too slow: {total_time:.3f}s for {level} requests"
    
    def test_memory_usage_benchmark(self, client):
        """Bellek kullanımının benchmark'ını test eder"""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss
        
        # 50 istek gönder
        for _ in range(50):
            response = client.get("/health")
            assert response.status_code == 200
        
        final_memory = process.memory_info().rss
        memory_increase = final_memory - initial_memory
        
        # Bellek artışı 100MB'dan az olmalı
        assert memory_increase < 100 * 1024 * 1024, f"Memory increase too high: {memory_increase / 1024 / 1024:.2f}MB"
    
    def test_database_query_performance_benchmark(self, client):
        """Veritabanı sorgu performansının benchmark'ını test eder"""
        queries = [
            "/api/v1/jobs/?limit=10",
            "/api/v1/jobs/?limit=50",
            "/api/v1/jobs/?limit=100",
            "/api/v1/companies/?limit=10",
            "/api/v1/users/?limit=10"
        ]
        
        for query in queries:
            times = []
            for _ in range(5):  # 5 test
                start_time = time.time()
                response = client.get(query)
                end_time = time.time()
                
                if response.status_code in [200, 404]:
                    times.append(end_time - start_time)
            
            if times:
                avg_time = statistics.mean(times)
                assert avg_time < 8.0, f"Database query too slow: {query} took {avg_time:.3f}s"
    
    def test_search_performance_benchmark(self, client):
        """Arama performansının benchmark'ını test eder"""
        search_queries = [
            "python",
            "developer",
            "remote",
            "senior",
            "full-stack"
        ]
        
        for query in search_queries:
            times = []
            for _ in range(3):  # 3 test
                start_time = time.time()
                response = client.get(f"/api/v1/jobs/search?q={query}")
                end_time = time.time()
                
                if response.status_code in [200, 404]:
                    times.append(end_time - start_time)
            
            if times:
                avg_time = statistics.mean(times)
                assert avg_time < 10.0, f"Search too slow: '{query}' took {avg_time:.3f}s"
    
    def test_file_upload_performance_benchmark(self, client):
        """Dosya yükleme performansının benchmark'ını test eder"""
        file_sizes = [1024, 10240, 102400]  # 1KB, 10KB, 100KB
        
        for size in file_sizes:
            test_file_content = b"Test file content" * (size // 16)
            
            times = []
            for _ in range(3):  # 3 test
                start_time = time.time()
                response = client.post(
                    "/api/v1/upload/cv",
                    files={"file": ("test.pdf", test_file_content, "application/pdf")}
                )
                end_time = time.time()
                
                if response.status_code in [200, 400, 401, 422]:
                    times.append(end_time - start_time)
            
            if times:
                avg_time = statistics.mean(times)
                # Dosya boyutuna göre kabul edilebilir süre
                max_time = min(5.0 + (size / 1024 / 1024) * 2, 15.0)  # 5s + 2s per MB, max 15s
                assert avg_time < max_time, f"File upload too slow: {size} bytes took {avg_time:.3f}s"
    
    def test_authentication_performance_benchmark(self, client):
        """Kimlik doğrulama performansının benchmark'ını test eder"""
        auth_operations = [
            ("/api/v1/auth/login", {"email": "test@example.com", "password": "testpass"}),
            ("/api/v1/auth/register", {"email": "new@example.com", "password": "newpass", "first_name": "Test", "last_name": "User"}),
        ]
        
        for endpoint, data in auth_operations:
            times = []
            for _ in range(5):  # 5 test
                start_time = time.time()
                response = client.post(endpoint, json=data)
                end_time = time.time()
                
                if response.status_code in [200, 201, 400, 401, 422]:
                    times.append(end_time - start_time)
            
            if times:
                avg_time = statistics.mean(times)
                assert avg_time < 5.0, f"Authentication too slow: {endpoint} took {avg_time:.3f}s"
    
    def test_error_handling_performance_benchmark(self, client):
        """Hata işleme performansının benchmark'ını test eder"""
        error_endpoints = [
            "/api/v1/nonexistent/",
            "/api/v1/jobs/invalid-id",
            "/api/v1/users/invalid-id"
        ]
        
        for endpoint in error_endpoints:
            times = []
            for _ in range(10):  # 10 test
                start_time = time.time()
                response = client.get(endpoint)
                end_time = time.time()
                
                if response.status_code in [404, 400, 422]:
                    times.append(end_time - start_time)
            
            if times:
                avg_time = statistics.mean(times)
                assert avg_time < 2.0, f"Error handling too slow: {endpoint} took {avg_time:.3f}s"
    
    def test_pagination_performance_benchmark(self, client):
        """Sayfalama performansının benchmark'ını test eder"""
        page_sizes = [5, 10, 20, 50]
        
        for page_size in page_sizes:
            times = []
            for page in range(1, 4):  # 3 sayfa
                start_time = time.time()
                response = client.get(f"/api/v1/jobs/?limit={page_size}&page={page}")
                end_time = time.time()
                
                if response.status_code in [200, 404]:
                    times.append(end_time - start_time)
            
            if times:
                avg_time = statistics.mean(times)
                assert avg_time < 5.0, f"Pagination too slow: page_size={page_size} took {avg_time:.3f}s"
    
    def test_cache_performance_benchmark(self, client):
        """Cache performansının benchmark'ını test eder"""
        cacheable_endpoints = [
            "/api/v1/jobs/",
            "/api/v1/companies/",
            "/health"
        ]
        
        for endpoint in cacheable_endpoints:
            # İlk istek (cache miss)
            start_time = time.time()
            response1 = client.get(endpoint)
            first_time = time.time() - start_time
            
            # İkinci istek (cache hit)
            start_time = time.time()
            response2 = client.get(endpoint)
            second_time = time.time() - start_time
            
            # Cache etkisi kontrol et
            if response1.status_code == response2.status_code:
                # İkinci istek daha hızlı olmalı (cache etkisi)
                assert second_time <= first_time + 1.0, f"Cache not working: {endpoint}"
    
    def test_overall_system_performance_benchmark(self, client):
        """Genel sistem performansının benchmark'ını test eder"""
        # Karmaşık senaryo: birden fazla endpoint'e istek
        endpoints = [
            "/health",
            "/api/v1/jobs/?limit=10",
            "/api/v1/companies/?limit=5",
            "/docs"
        ]
        
        start_time = time.time()
        
        for _ in range(5):  # 5 tur
            for endpoint in endpoints:
                response = client.get(endpoint)
                assert response.status_code in [200, 404]
        
        total_time = time.time() - start_time
        
        # 20 istek (5 tur × 4 endpoint) 30 saniyede tamamlanmalı
        assert total_time < 30.0, f"Overall system performance too slow: {total_time:.3f}s for 20 requests"