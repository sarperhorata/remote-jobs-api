"""
Services Tests
Service fonksiyonları için testler
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from backend.services.cache_service import CacheService
from backend.services.mailgun_service import MailgunService
from backend.services.job_matching_service import JobMatchingService


class TestCacheService:
    """CacheService testleri"""
    
    def test_cache_service_creation(self):
        """CacheService oluşturma testi"""
        cache = CacheService()
        assert cache is not None
        
    def test_cache_set_get(self):
        """Cache set/get testi"""
        cache = CacheService()
        
        cache.set("test_key", "test_value", ttl=60)
        result = cache.get("test_key")
        
        assert result == "test_value"
        
    def test_cache_expiration(self):
        """Cache süre dolumu testi"""
        cache = CacheService()
        
        cache.set("test_key", "test_value", ttl=1)
        
        # 1 saniye bekle
        import time
        time.sleep(1.1)
        
        result = cache.get("test_key")
        assert result is None
        
    def test_cache_delete(self):
        """Cache silme testi"""
        cache = CacheService()
        
        cache.set("test_key", "test_value")
        cache.delete("test_key")
        
        result = cache.get("test_key")
        assert result is None
        
    def test_cache_clear(self):
        """Cache temizleme testi"""
        cache = CacheService()
        
        cache.set("key1", "value1")
        cache.set("key2", "value2")
        cache.clear()
        
        assert cache.get("key1") is None
        assert cache.get("key2") is None


class TestMailgunService:
    """MailgunService testleri"""
    
    def test_mailgun_service_creation(self):
        """MailgunService oluşturma testi"""
        service = MailgunService()
        assert service is not None
        
    @patch('backend.services.mailgun_service.requests.post')
    def test_send_email_success(self, mock_post):
        """Email gönderme başarı testi"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"id": "test_id"}
        mock_post.return_value = mock_response
        
        service = MailgunService()
        result = service.send_email("test@example.com", "Subject", "Body")
        
        assert result is True
        mock_post.assert_called_once()
        
    @patch('backend.services.mailgun_service.requests.post')
    def test_send_email_failure(self, mock_post):
        """Email gönderme başarısızlık testi"""
        mock_response = Mock()
        mock_response.status_code = 400
        mock_post.return_value = mock_response
        
        service = MailgunService()
        result = service.send_email("test@example.com", "Subject", "Body")
        
        assert result is False
        
    def test_send_verification_email(self):
        """Doğrulama emaili gönderme testi"""
        service = MailgunService()
        
        with patch.object(service, 'send_email') as mock_send:
            mock_send.return_value = True
            result = service.send_verification_email("test@example.com", "token123")
            
            assert result is True
            mock_send.assert_called_once()
            
    def test_send_password_reset_email(self):
        """Şifre sıfırlama emaili gönderme testi"""
        service = MailgunService()
        
        with patch.object(service, 'send_email') as mock_send:
            mock_send.return_value = True
            result = service.send_password_reset_email("test@example.com", "reset123")
            
            assert result is True
            mock_send.assert_called_once()


class TestJobMatchingService:
    """JobMatchingService testleri"""
    
    def test_job_matching_service_creation(self):
        """JobMatchingService oluşturma testi"""
        service = JobMatchingService()
        assert service is not None
        
    def test_calculate_job_match_score(self):
        """İş eşleştirme skoru hesaplama testi"""
        service = JobMatchingService()
        
        job = {
            "title": "Python Developer",
            "skills": ["Python", "Django", "PostgreSQL"],
            "experience_level": "Mid",
            "location": "Remote"
        }
        
        profile = {
            "skills": ["Python", "Django", "JavaScript"],
            "experience_level": "Mid",
            "preferred_location": "Remote"
        }
        
        score = service.calculate_match_score(job, profile)
        
        assert 0 <= score <= 100
        assert score > 50  # Yüksek eşleşme bekleniyor
        
    def test_calculate_job_match_score_no_match(self):
        """Eşleşme olmayan durum testi"""
        service = JobMatchingService()
        
        job = {
            "title": "Java Developer",
            "skills": ["Java", "Spring"],
            "experience_level": "Senior",
            "location": "On-site"
        }
        
        profile = {
            "skills": ["Python", "Django"],
            "experience_level": "Junior",
            "preferred_location": "Remote"
        }
        
        score = service.calculate_match_score(job, profile)
        
        assert 0 <= score <= 100
        assert score < 30  # Düşük eşleşme bekleniyor
        
    def test_get_recommended_jobs(self):
        """Önerilen işler testi"""
        service = JobMatchingService()
        
        jobs = [
            {
                "id": "1",
                "title": "Python Developer",
                "skills": ["Python", "Django"],
                "experience_level": "Mid",
                "location": "Remote"
            },
            {
                "id": "2", 
                "title": "Java Developer",
                "skills": ["Java", "Spring"],
                "experience_level": "Senior",
                "location": "On-site"
            }
        ]
        
        profile = {
            "skills": ["Python", "Django"],
            "experience_level": "Mid",
            "preferred_location": "Remote"
        }
        
        recommended = service.get_recommended_jobs(jobs, profile, limit=5)
        
        assert len(recommended) <= 5
        assert len(recommended) > 0
        assert recommended[0]["id"] == "1"  # Python job önce gelmeli 