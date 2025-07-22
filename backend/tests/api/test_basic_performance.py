import pytest
from fastapi.testclient import TestClient
import time

class TestBasicPerformance:
    """Temel performans testleri - MongoDB bağımsız"""
    
    def test_health_endpoint_fast_response(self, client):
        """Health endpoint'inin hızlı yanıt verdiğini test eder"""
        start_time = time.time()
        response = client.get("/health")
        end_time = time.time()
        
        response_time = end_time - start_time
        assert response.status_code == 200
        assert response_time < 2.0  # 2 saniye altında olmalı
    
    def test_root_endpoint_fast_response(self, client):
        """Root endpoint'inin hızlı yanıt verdiğini test eder"""
        start_time = time.time()
        response = client.get("/")
        end_time = time.time()
        
        response_time = end_time - start_time
        assert response.status_code == 200
        assert response_time < 2.0  # 2 saniye altında olmalı
    
    def test_docs_endpoint_fast_response(self, client):
        """Docs endpoint'inin hızlı yanıt verdiğini test eder"""
        start_time = time.time()
        response = client.get("/docs")
        end_time = time.time()
        
        response_time = end_time - start_time
        assert response.status_code == 200
        assert response_time < 3.0  # 3 saniye altında olmalı
    
    def test_concurrent_health_requests(self, client):
        """Eşzamanlı health isteklerinin düzgün işlendiğini test eder"""
        import concurrent.futures
        
        def make_request():
            return client.get("/health")
        
        # 3 eşzamanlı istek gönder
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            futures = [executor.submit(make_request) for _ in range(3)]
            responses = [future.result() for future in futures]
        
        # Tüm istekler başarılı olmalı
        for response in responses:
            assert response.status_code == 200
    
    def test_error_endpoint_fast_response(self, client):
        """Hata endpoint'inin hızlı yanıt verdiğini test eder"""
        start_time = time.time()
        response = client.get("/nonexistent-endpoint")
        end_time = time.time()
        
        response_time = end_time - start_time
        assert response.status_code == 404
        assert response_time < 1.0  # Hata işleme 1 saniye altında olmalı
    
    def test_json_response_structure(self, client):
        """JSON yanıt yapısının doğru olduğunu test eder"""
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        
        # Health endpoint'inin beklenen yapıda olduğunu kontrol et
        assert "status" in data
        assert "timestamp" in data
        assert data["status"] == "healthy"
    
    def test_response_headers_correct(self, client):
        """Yanıt header'larının doğru olduğunu test eder"""
        response = client.get("/health")
        
        assert response.status_code == 200
        assert "content-type" in response.headers
        assert "application/json" in response.headers["content-type"]
    
    def test_multiple_requests_consistency(self, client):
        """Çoklu isteklerin tutarlı olduğunu test eder"""
        responses = []
        
        for _ in range(5):
            response = client.get("/health")
            responses.append(response)
        
        # Tüm yanıtlar aynı status code'a sahip olmalı
        status_codes = [r.status_code for r in responses]
        assert all(code == 200 for code in status_codes)
        
        # Tüm yanıtlar aynı yapıda olmalı
        for response in responses:
            data = response.json()
            assert "status" in data
            assert "timestamp" in data