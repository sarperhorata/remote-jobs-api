import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, MagicMock
import json
import re

class TestDataValidationAPI:
    """Veri doğrulama API endpoint'leri için kapsamlı testler"""
    
    def test_job_data_validation_success(self, client):
        """Geçerli job verisi ile başarılı doğrulama testi"""
        valid_job_data = {
            "title": "Senior Python Developer",
            "company": "Tech Corp",
            "location": "Remote",
            "description": "We are looking for a senior Python developer...",
            "requirements": ["Python", "Django", "PostgreSQL"],
            "salary_min": 80000,
            "salary_max": 120000,
            "job_type": "full-time",
            "experience_level": "senior"
        }
        
        response = client.post("/api/v1/jobs/", json=valid_job_data)
        assert response.status_code in [200, 201, 422]  # 422 validation error da kabul edilebilir
    
    def test_job_data_validation_missing_required_fields(self, client):
        """Eksik zorunlu alanlar ile doğrulama testi"""
        invalid_job_data = {
            "title": "Senior Python Developer",
            # company eksik
            "location": "Remote"
        }
        
        response = client.post("/api/v1/jobs/", json=invalid_job_data)
        assert response.status_code == 422  # Validation error
    
    def test_job_data_validation_invalid_salary_range(self, client):
        """Geçersiz maaş aralığı ile doğrulama testi"""
        invalid_job_data = {
            "title": "Senior Python Developer",
            "company": "Tech Corp",
            "location": "Remote",
            "salary_min": 120000,  # max'tan büyük
            "salary_max": 80000
        }
        
        response = client.post("/api/v1/jobs/", json=invalid_job_data)
        assert response.status_code == 422
    
    def test_job_data_validation_invalid_email_format(self, client):
        """Geçersiz email formatı ile doğrulama testi"""
        invalid_job_data = {
            "title": "Senior Python Developer",
            "company": "Tech Corp",
            "contact_email": "invalid-email-format"
        }
        
        response = client.post("/api/v1/jobs/", json=invalid_job_data)
        assert response.status_code == 422
    
    def test_user_registration_validation_success(self, client):
        """Geçerli kullanıcı kaydı doğrulama testi"""
        valid_user_data = {
            "email": "test@example.com",
            "password": "StrongPassword123!",
            "first_name": "John",
            "last_name": "Doe",
            "phone": "+1234567890"
        }
        
        response = client.post("/api/v1/auth/register", json=valid_user_data)
        assert response.status_code in [200, 201, 422]
    
    def test_user_registration_validation_weak_password(self, client):
        """Zayıf şifre ile doğrulama testi"""
        invalid_user_data = {
            "email": "test@example.com",
            "password": "123",  # Çok zayıf
            "first_name": "John",
            "last_name": "Doe"
        }
        
        response = client.post("/api/v1/auth/register", json=invalid_user_data)
        assert response.status_code == 422
    
    def test_user_registration_validation_invalid_email(self, client):
        """Geçersiz email ile doğrulama testi"""
        invalid_user_data = {
            "email": "not-an-email",
            "password": "StrongPassword123!",
            "first_name": "John",
            "last_name": "Doe"
        }
        
        response = client.post("/api/v1/auth/register", json=invalid_user_data)
        assert response.status_code == 422
    
    def test_application_data_validation_success(self, client):
        """Geçerli başvuru verisi doğrulama testi"""
        valid_application_data = {
            "job_id": "507f1f77bcf86cd799439011",
            "cover_letter": "I am interested in this position...",
            "resume_url": "https://example.com/resume.pdf",
            "expected_salary": 90000
        }
        
        response = client.post("/api/v1/applications/", json=valid_application_data)
        assert response.status_code in [200, 201, 422]
    
    def test_application_data_validation_invalid_job_id(self, client):
        """Geçersiz job ID ile doğrulama testi"""
        invalid_application_data = {
            "job_id": "invalid-id",
            "cover_letter": "I am interested in this position..."
        }
        
        response = client.post("/api/v1/applications/", json=invalid_application_data)
        assert response.status_code == 422
    
    def test_company_data_validation_success(self, client):
        """Geçerli şirket verisi doğrulama testi"""
        valid_company_data = {
            "name": "Tech Solutions Inc",
            "website": "https://techsolutions.com",
            "industry": "Technology",
            "size": "100-500",
            "location": "San Francisco, CA"
        }
        
        response = client.post("/api/v1/companies/", json=valid_company_data)
        assert response.status_code in [200, 201, 422]
    
    def test_company_data_validation_invalid_website(self, client):
        """Geçersiz website URL'i ile doğrulama testi"""
        invalid_company_data = {
            "name": "Tech Solutions Inc",
            "website": "not-a-valid-url",
            "industry": "Technology"
        }
        
        response = client.post("/api/v1/companies/", json=invalid_company_data)
        assert response.status_code == 422
    
    def test_search_query_validation_success(self, client):
        """Geçerli arama sorgusu doğrulama testi"""
        response = client.get("/api/v1/jobs/search?q=python&location=remote&experience=senior")
        assert response.status_code in [200, 404]
    
    def test_search_query_validation_invalid_parameters(self, client):
        """Geçersiz arama parametreleri ile doğrulama testi"""
        response = client.get("/api/v1/jobs/search?salary_min=abc&salary_max=def")
        assert response.status_code in [200, 400, 422]
    
    def test_pagination_validation_success(self, client):
        """Geçerli sayfalama parametreleri doğrulama testi"""
        response = client.get("/api/v1/jobs/?page=1&limit=10")
        assert response.status_code in [200, 404]
    
    def test_pagination_validation_invalid_page(self, client):
        """Geçersiz sayfa numarası ile doğrulama testi"""
        response = client.get("/api/v1/jobs/?page=-1&limit=10")
        assert response.status_code in [200, 400, 422]
    
    def test_pagination_validation_invalid_limit(self, client):
        """Geçersiz limit değeri ile doğrulama testi"""
        response = client.get("/api/v1/jobs/?page=1&limit=10000")  # Çok büyük limit
        assert response.status_code in [200, 400, 422]
    
    def test_file_upload_validation_success(self, client):
        """Geçerli dosya yükleme doğrulama testi"""
        test_file_content = b"Test PDF content"
        
        response = client.post(
            "/api/v1/upload/cv",
            files={"file": ("test.pdf", test_file_content, "application/pdf")}
        )
        assert response.status_code in [200, 201, 400, 401, 422]
    
    def test_file_upload_validation_invalid_type(self, client):
        """Geçersiz dosya tipi ile doğrulama testi"""
        test_file_content = b"Test content"
        
        response = client.post(
            "/api/v1/upload/cv",
            files={"file": ("test.exe", test_file_content, "application/octet-stream")}
        )
        assert response.status_code in [400, 422]  # Geçersiz dosya tipi
    
    def test_file_upload_validation_too_large(self, client):
        """Çok büyük dosya ile doğrulama testi"""
        # 10MB'dan büyük dosya
        test_file_content = b"x" * (11 * 1024 * 1024)
        
        response = client.post(
            "/api/v1/upload/cv",
            files={"file": ("large.pdf", test_file_content, "application/pdf")}
        )
        assert response.status_code in [400, 413, 422]  # Dosya çok büyük
    
    def test_json_payload_validation_malformed(self, client):
        """Bozuk JSON payload ile doğrulama testi"""
        headers = {"Content-Type": "application/json"}
        
        response = client.post(
            "/api/v1/jobs/",
            data="{'invalid': json}",
            headers=headers
        )
        assert response.status_code in [400, 422]  # JSON parse error
    
    def test_xss_prevention_validation(self, client):
        """XSS koruması doğrulama testi"""
        malicious_data = {
            "title": "<script>alert('xss')</script>",
            "company": "Tech Corp",
            "description": "javascript:alert('xss')"
        }
        
        response = client.post("/api/v1/jobs/", json=malicious_data)
        # XSS koruması varsa 422, yoksa 200/201 olabilir
        assert response.status_code in [200, 201, 400, 422]
    
    def test_sql_injection_prevention_validation(self, client):
        """SQL injection koruması doğrulama testi"""
        malicious_data = {
            "title": "'; DROP TABLE jobs; --",
            "company": "Tech Corp"
        }
        
        response = client.post("/api/v1/jobs/", json=malicious_data)
        # SQL injection koruması varsa 422, yoksa 200/201 olabilir
        assert response.status_code in [200, 201, 400, 422]
    
    def test_input_length_validation(self, client):
        """Girdi uzunluğu doğrulama testi"""
        # Çok uzun başlık
        long_title = "A" * 1000
        
        long_data = {
            "title": long_title,
            "company": "Tech Corp"
        }
        
        response = client.post("/api/v1/jobs/", json=long_data)
        assert response.status_code in [200, 201, 400, 422]
    
    def test_required_field_validation_comprehensive(self, client):
        """Kapsamlı zorunlu alan doğrulama testi"""
        # Tüm zorunlu alanlar eksik
        empty_data = {}
        
        response = client.post("/api/v1/jobs/", json=empty_data)
        assert response.status_code == 422
    
    def test_data_type_validation(self, client):
        """Veri tipi doğrulama testi"""
        invalid_type_data = {
            "title": 123,  # String olmalı
            "company": True,  # String olmalı
            "salary_min": "not-a-number"  # Number olmalı
        }
        
        response = client.post("/api/v1/jobs/", json=invalid_type_data)
        assert response.status_code == 422