"""
Bulk Apply API Tests
Toplu başvuru sistemi için test'ler
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from fastapi.testclient import TestClient
from datetime import datetime, timedelta

from ..routes.bulk_apply import router, bulk_apply_tasks
from ..models.user import UserResponse as User
from ..models.job import JobResponse as Job
from ..models.user_application import UserApplication as Application

# Test client - include the full app to get proper routing
from fastapi import FastAPI
from ..routes.bulk_apply import router

app = FastAPI()
app.include_router(router)
client = TestClient(app)

# Global auth headers for tests
auth_headers = {"Authorization": "Bearer test_token"}

# Mock user
mock_user = User(
    email="test@example.com",
    full_name="Test User",
    is_active=True,
    is_superuser=False
)

# Mock authentication
def mock_get_current_user():
    return mock_user

@pytest.fixture
def sample_jobs():
    return [
        {
            "id": "job_1",
            "title": "Senior React Developer",
            "company": "Tech Corp",
            "url": "https://example.com/job/1",
            "location": "New York, NY",
            "salary": "$100k - $150k"
        },
        {
            "id": "job_2",
            "title": "Frontend Engineer",
            "company": "Startup Inc",
            "url": "https://example.com/job/2",
            "location": "San Francisco, CA",
            "salary": "$90k - $130k"
        }
    ]

@pytest.fixture
def sample_form_config():
    return {
        "profile_data": {
            "firstName": "John",
            "lastName": "Doe",
            "email": "john.doe@example.com",
            "phone": "+1234567890",
            "experience": "5 years",
            "skills": ["React", "TypeScript", "Node.js"]
        },
        "auto_fill": True,
        "generate_cover_letter": True
    }

class TestFormAnalysis:
    """Form analizi endpoint test'leri"""
    
    @patch('backend.routes.bulk_apply.get_current_user', side_effect=mock_get_current_user)
    @patch('backend.routes.bulk_apply.check_rate_limit', new_callable=AsyncMock)
    @patch('backend.routes.bulk_apply.AIApplicationService')
    def test_analyze_form_success(self, mock_ai_service, mock_rate_limit, mock_auth):
        """Form analizi başarılı test"""
        # Mock AI service
        mock_ai_instance = Mock()
        mock_ai_instance.analyze_form = AsyncMock(return_value={
            "fields": [
                {"name": "firstName", "type": "text", "required": True},
                {"name": "email", "type": "email", "required": True}
            ],
            "form_type": "application",
            "confidence": 0.85,
            "estimated_time": 30
        })
        mock_ai_service.return_value = mock_ai_instance
        
        # Test request
        request_data = {
            "job_url": "https://example.com/job/123",
            "job_title": "Senior Developer",
            "company_name": "Tech Corp"
        }
        
        response = client.post("/api/v1/bulk-apply/analyze-form", json=request_data, headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "fields" in data
        assert "form_type" in data
        assert "confidence" in data
        assert "estimated_time" in data

class TestBulkApply:
    """Toplu başvuru endpoint test'leri"""
    
    @patch('backend.routes.bulk_apply.get_current_user', side_effect=mock_get_current_user)
    @patch('backend.routes.bulk_apply.check_rate_limit', new_callable=AsyncMock)
    def test_start_bulk_apply_success(self, mock_rate_limit, mock_auth, sample_jobs, sample_form_config):
        """Toplu başvuru başlatma başarılı test"""
        request_data = {
            "jobs": sample_jobs,
            "form_config": sample_form_config,
            "rate_limit": 1000,
            "max_retries": 3
        }
        
        response = client.post("/api/v1/bulk-apply/start-bulk-apply", json=request_data, headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "task_id" in data
        assert "status" in data

    @patch('backend.routes.bulk_apply.get_current_user', side_effect=mock_get_current_user)
    def test_get_bulk_apply_status(self, mock_auth):
        """Toplu başvuru durumu test"""
        # Test task oluştur
        task_id = "test_task_123"
        bulk_apply_tasks[task_id] = {
            "user_id": mock_user.email,
            "total_jobs": 2,
            "completed_jobs": 1,
            "successful_jobs": 1,
            "failed_jobs": 0,
            "in_progress_jobs": 0,
            "started_at": datetime.utcnow(),
            "status": "running"
        }
        
        response = client.get(f"/api/v1/bulk-apply/status/{task_id}", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["total_jobs"] == 2
        assert data["completed_jobs"] == 1
        assert data["status"] == "running"

    @patch('backend.routes.bulk_apply.get_current_user', side_effect=mock_get_current_user)
    def test_get_bulk_apply_status_not_found(self, mock_auth):
        """Bulunamayan task test"""
        response = client.get("/api/v1/bulk-apply/status/nonexistent_task", headers=auth_headers)
        
        assert response.status_code == 404

    @patch('backend.routes.bulk_apply.get_current_user', side_effect=mock_get_current_user)
    def test_get_bulk_apply_history(self, mock_auth):
        """Toplu başvuru geçmişi test"""
        # Test task'ları oluştur
        task_id_1 = "test_task_history_1"
        task_id_2 = "test_task_history_2"
        
        bulk_apply_tasks[task_id_1] = {
            "user_id": mock_user.email,
            "total_jobs": 2,
            "successful_jobs": 1,
            "started_at": datetime.utcnow() - timedelta(hours=1),
            "status": "completed"
        }
        
        bulk_apply_tasks[task_id_2] = {
            "user_id": mock_user.email,
            "total_jobs": 1,
            "successful_jobs": 1,
            "started_at": datetime.utcnow(),
            "status": "running"
        }
        
        response = client.get("/api/v1/bulk-apply/history", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "tasks" in data
        assert len(data["tasks"]) >= 2

class TestErrorHandling:
    """Hata yönetimi test'leri"""
    
    @patch('backend.routes.bulk_apply.get_current_user', side_effect=mock_get_current_user)
    def test_unauthorized_access(self, mock_auth):
        """Yetkisiz erişim test"""
        # Farklı kullanıcı için task oluştur
        task_id = "unauthorized_task"
        bulk_apply_tasks[task_id] = {
            "user_id": "different_user",
            "total_jobs": 2,
            "status": "running"
        }
        
        response = client.get(f"/api/v1/bulk-apply/status/{task_id}", headers=auth_headers)
        
        assert response.status_code == 403

class TestDataValidation:
    """Veri doğrulama test'leri"""
    
    @patch('backend.routes.bulk_apply.get_current_user', side_effect=mock_get_current_user)
    @patch('backend.routes.bulk_apply.check_rate_limit', new_callable=AsyncMock)
    def test_invalid_job_data(self, mock_rate_limit, mock_auth):
        """Geçersiz job verisi test"""
        request_data = {
            "jobs": [
                {
                    "id": "job_1",
                    "title": "",  # Boş title
                    "company": "Tech Corp",
                    "url": "https://example.com/job/1"
                }
            ],
            "form_config": {}
        }
        
        response = client.post("/api/v1/bulk-apply/start-bulk-apply", json=request_data, headers=auth_headers)
        
        assert response.status_code == 422

# Cleanup after tests
@pytest.fixture(autouse=True)
def cleanup_tasks():
    """Her test sonrası task'ları temizle"""
    yield
    bulk_apply_tasks.clear() 