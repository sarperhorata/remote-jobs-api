import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, MagicMock
import time
import json

class TestPerformanceAPI:
    """Performance API endpoint'leri için kapsamlı testler"""
    
    def test_api_response_time_under_threshold(self, client):
        """API yanıt süresinin belirlenen eşiğin altında olduğunu test eder"""
        start_time = time.time()
        response = client.get("/api/v1/health")
        end_time = time.time()
        
        response_time = end_time - start_time
        assert response.status_code == 200
        assert response_time < 1.0  # 1 saniye altında olmalı
    
    def test_concurrent_requests_handling(self, client):
        """Eşzamanlı isteklerin düzgün işlendiğini test eder"""
        import threading
        import concurrent.futures
        
        def make_request():
            return client.get("/api/v1/health")
        
        # 10 eşzamanlı istek gönder
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(make_request) for _ in range(10)]
            responses = [future.result() for future in futures]
        
        # Tüm istekler başarılı olmalı
        for response in responses:
            assert response.status_code == 200
    
    def test_memory_usage_stable(self, client):
        """Bellek kullanımının kararlı olduğunu test eder"""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss
        
        # 100 istek gönder
        for _ in range(100):
            response = client.get("/api/v1/health")
            assert response.status_code == 200
        
        final_memory = process.memory_info().rss
        memory_increase = final_memory - initial_memory
        
        # Bellek artışı 10MB'dan az olmalı
        assert memory_increase < 10 * 1024 * 1024
    
    def test_large_payload_handling(self, client):
        """Büyük payload'ların düzgün işlendiğini test eder"""
        # Büyük bir JSON payload oluştur
        large_payload = {
            "data": "x" * 10000,  # 10KB veri
            "items": [{"id": i, "content": "test"} for i in range(1000)]
        }
        
        start_time = time.time()
        response = client.post("/api/v1/jobs/search", json=large_payload)
        end_time = time.time()
        
        # Büyük payload'lar da 5 saniye içinde işlenmeli
        assert end_time - start_time < 5.0
        assert response.status_code in [200, 400, 422]  # Geçerli bir yanıt
    
    def test_database_query_performance(self, client):
        """Veritabanı sorgularının performansını test eder"""
        # Job arama sorgusu
        start_time = time.time()
        response = client.get("/api/v1/jobs/?limit=100")
        end_time = time.time()
        
        query_time = end_time - start_time
        assert response.status_code in [200, 404]
        assert query_time < 2.0  # 2 saniye altında olmalı
    
    def test_cache_performance(self, client):
        """Cache performansını test eder"""
        # İlk istek
        start_time = time.time()
        response1 = client.get("/api/v1/jobs/")
        first_request_time = time.time() - start_time
        
        # İkinci istek (cache'den gelmeli)
        start_time = time.time()
        response2 = client.get("/api/v1/jobs/")
        second_request_time = time.time() - start_time
        
        # İkinci istek daha hızlı olmalı (cache etkisi)
        assert second_request_time <= first_request_time
        assert response1.status_code == response2.status_code
    
    def test_error_handling_performance(self, client):
        """Hata işleme performansını test eder"""
        # Geçersiz endpoint'e istek
        start_time = time.time()
        response = client.get("/api/v1/nonexistent/")
        end_time = time.time()
        
        error_handling_time = end_time - start_time
        assert response.status_code == 404
        assert error_handling_time < 0.5  # Hata işleme hızlı olmalı
    
    def test_authentication_performance(self, client):
        """Kimlik doğrulama performansını test eder"""
        # Login isteği
        login_data = {
            "email": "test@example.com",
            "password": "testpassword"
        }
        
        start_time = time.time()
        response = client.post("/api/v1/auth/login", json=login_data)
        end_time = time.time()
        
        auth_time = end_time - start_time
        assert response.status_code in [200, 401, 422]
        assert auth_time < 1.0  # Kimlik doğrulama 1 saniye altında olmalı
    
    def test_file_upload_performance(self, client):
        """Dosya yükleme performansını test eder"""
        # Küçük bir dosya oluştur
        test_file_content = b"Test file content" * 1000  # ~16KB
        
        start_time = time.time()
        response = client.post(
            "/api/v1/upload/cv",
            files={"file": ("test.pdf", test_file_content, "application/pdf")}
        )
        end_time = time.time()
        
        upload_time = end_time - start_time
        assert response.status_code in [200, 400, 401, 422]
        assert upload_time < 3.0  # Dosya yükleme 3 saniye altında olmalı
    
    def test_search_performance(self, client):
        """Arama performansını test eder"""
        # Job arama
        start_time = time.time()
        response = client.get("/api/v1/jobs/search?q=python&location=remote")
        end_time = time.time()
        
        search_time = end_time - start_time
        assert response.status_code in [200, 404]
        assert search_time < 2.0  # Arama 2 saniye altında olmalı
    
    def test_pagination_performance(self, client):
        """Sayfalama performansını test eder"""
        # Farklı sayfa boyutları ile test
        page_sizes = [10, 50, 100]
        
        for page_size in page_sizes:
            start_time = time.time()
            response = client.get(f"/api/v1/jobs/?limit={page_size}&page=1")
            end_time = time.time()
            
            pagination_time = end_time - start_time
            assert response.status_code in [200, 404]
            assert pagination_time < 1.5  # Sayfalama 1.5 saniye altında olmalı