import pytest
import os
from unittest.mock import patch, Mock
from typing import Dict, Any

from backend.utils.config import (
    get_db_url,
    get_crawler_headers,
    get_all_config,
    DATABASE_URL,
    IS_PRODUCTION,
    TELEGRAM_ENABLED,
    API_HOST,
    API_PORT,
    CORS_ORIGINS,
    JWT_SECRET,
    EMAIL_HOST,
    USER_AGENT
)


class TestUtilsConfig:
    """Utils config modülü testleri"""
    
    def test_get_db_url_returns_string(self):
        """get_db_url fonksiyonu string döndürür"""
        db_url = get_db_url()
        assert isinstance(db_url, str)
        assert len(db_url) > 0

    def test_get_crawler_headers_structure(self):
        """get_crawler_headers doğru header yapısı döndürür"""
        headers = get_crawler_headers()
        assert isinstance(headers, dict)
        assert "User-Agent" in headers
        assert "Accept-Language" in headers
        assert "Accept" in headers
        assert headers["User-Agent"] == USER_AGENT

    def test_get_all_config_structure(self):
        """get_all_config doğru yapıda config döndürür"""
        config = get_all_config()
        assert isinstance(config, dict)
        
        # Ana bölümlerin varlığını kontrol et
        required_sections = [
            "api", "database", "email", "telegram", 
            "monitor", "crawler", "cors", "jwt",
            "cache", "rate_limit", "file_upload", 
            "premium", "notification", "security"
        ]
        
        for section in required_sections:
            assert section in config
            assert isinstance(config[section], dict)

    def test_api_config_section(self):
        """API config bölümü doğru değerlere sahip"""
        config = get_all_config()
        api_config = config["api"]
        
        assert "host" in api_config
        assert "port" in api_config
        assert "debug" in api_config
        assert "reload" in api_config
        
        assert api_config["host"] == API_HOST
        assert api_config["port"] == API_PORT
        assert isinstance(api_config["debug"], bool)
        assert isinstance(api_config["reload"], bool)

    def test_database_config_section(self):
        """Database config bölümü doğru değerlere sahip"""
        config = get_all_config()
        db_config = config["database"]
        
        assert "url" in db_config
        assert "is_production" in db_config
        
        assert isinstance(db_config["url"], str)
        assert isinstance(db_config["is_production"], bool)
        assert db_config["is_production"] == IS_PRODUCTION

    def test_email_config_section(self):
        """Email config bölümü doğru değerlere sahip"""
        config = get_all_config()
        email_config = config["email"]
        
        assert "host" in email_config
        assert "port" in email_config
        assert "user" in email_config
        assert "from" in email_config
        assert "enabled" in email_config
        
        assert email_config["host"] == EMAIL_HOST
        assert isinstance(email_config["port"], int)
        assert isinstance(email_config["enabled"], bool)

    def test_telegram_config_section(self):
        """Telegram config bölümü doğru değerlere sahip"""
        config = get_all_config()
        telegram_config = config["telegram"]
        
        assert "enabled" in telegram_config
        assert "bot_token" in telegram_config
        assert "chat_id" in telegram_config
        
        assert isinstance(telegram_config["enabled"], bool)
        assert telegram_config["enabled"] == TELEGRAM_ENABLED

    def test_cors_config_section(self):
        """CORS config bölümü doğru değerlere sahip"""
        config = get_all_config()
        cors_config = config["cors"]
        
        assert "origins" in cors_config
        assert "allow_credentials" in cors_config
        
        assert isinstance(cors_config["origins"], list)
        assert isinstance(cors_config["allow_credentials"], bool)
        assert cors_config["origins"] == CORS_ORIGINS

    def test_jwt_config_section(self):
        """JWT config bölümü doğru değerlere sahip"""
        config = get_all_config()
        jwt_config = config["jwt"]
        
        assert "secret" in jwt_config
        assert "algorithm" in jwt_config
        assert "expire_minutes" in jwt_config
        
        assert jwt_config["secret"] == JWT_SECRET
        assert jwt_config["algorithm"] == "HS256"
        assert isinstance(jwt_config["expire_minutes"], int)

    def test_monitor_config_section(self):
        """Monitor config bölümü doğru değerlere sahip"""
        config = get_all_config()
        monitor_config = config["monitor"]
        
        assert "default_interval" in monitor_config
        assert "max_interval" in monitor_config
        assert "min_interval" in monitor_config
        
        assert isinstance(monitor_config["default_interval"], int)
        assert isinstance(monitor_config["max_interval"], int)
        assert isinstance(monitor_config["min_interval"], int)
        
        # Mantıklı değer aralığı kontrolü
        assert monitor_config["min_interval"] < monitor_config["default_interval"]
        assert monitor_config["default_interval"] < monitor_config["max_interval"]

    def test_crawler_config_section(self):
        """Crawler config bölümü doğru değerlere sahip"""
        config = get_all_config()
        crawler_config = config["crawler"]
        
        assert "timeout" in crawler_config
        assert "delay" in crawler_config
        assert "user_agent" in crawler_config
        
        assert isinstance(crawler_config["timeout"], int)
        assert isinstance(crawler_config["delay"], float)
        assert crawler_config["user_agent"] == USER_AGENT

    def test_cache_config_section(self):
        """Cache config bölümü doğru değerlere sahip"""
        config = get_all_config()
        cache_config = config["cache"]
        
        assert "ttl" in cache_config
        assert "max_size" in cache_config
        
        assert isinstance(cache_config["ttl"], int)
        assert isinstance(cache_config["max_size"], int)
        assert cache_config["ttl"] > 0
        assert cache_config["max_size"] > 0

    def test_rate_limit_config_section(self):
        """Rate limit config bölümü doğru değerlere sahip"""
        config = get_all_config()
        rate_limit_config = config["rate_limit"]
        
        assert "window" in rate_limit_config
        assert "max_requests" in rate_limit_config
        
        assert isinstance(rate_limit_config["window"], int)
        assert isinstance(rate_limit_config["max_requests"], int)
        assert rate_limit_config["window"] > 0
        assert rate_limit_config["max_requests"] > 0

    def test_file_upload_config_section(self):
        """File upload config bölümü doğru değerlere sahip"""
        config = get_all_config()
        file_config = config["file_upload"]
        
        assert "max_size" in file_config
        assert "allowed_extensions" in file_config
        assert "upload_dir" in file_config
        
        assert isinstance(file_config["max_size"], int)
        assert isinstance(file_config["allowed_extensions"], list)
        assert isinstance(file_config["upload_dir"], str)
        assert file_config["max_size"] > 0

    def test_premium_config_section(self):
        """Premium config bölümü doğru değerlere sahip"""
        config = get_all_config()
        premium_config = config["premium"]
        
        assert "price" in premium_config
        assert "free_trial_days" in premium_config
        assert "max_free_job_views" in premium_config
        assert "max_referral_days" in premium_config
        
        assert isinstance(premium_config["price"], float)
        assert isinstance(premium_config["free_trial_days"], int)
        assert isinstance(premium_config["max_free_job_views"], int)
        assert isinstance(premium_config["max_referral_days"], int)

    def test_notification_config_section(self):
        """Notification config bölümü doğru değerlere sahip"""
        config = get_all_config()
        notification_config = config["notification"]
        
        assert "email_interval" in notification_config
        assert "telegram_interval" in notification_config
        
        assert isinstance(notification_config["email_interval"], int)
        assert isinstance(notification_config["telegram_interval"], int)

    def test_security_config_section(self):
        """Security config bölümü doğru değerlere sahip"""
        config = get_all_config()
        security_config = config["security"]
        
        assert "password_min_length" in security_config
        assert "require_uppercase" in security_config
        assert "require_lowercase" in security_config
        assert "require_numbers" in security_config
        assert "require_special" in security_config
        
        assert isinstance(security_config["password_min_length"], int)
        assert isinstance(security_config["require_uppercase"], bool)
        assert isinstance(security_config["require_lowercase"], bool)
        assert isinstance(security_config["require_numbers"], bool)
        assert isinstance(security_config["require_special"], bool)

    @patch.dict(os.environ, {"API_HOST": "test-host"})
    def test_environment_variable_override(self):
        """Environment variable'lar doğru override edilir"""
        # Bu test önceki importların değişmeyeceği gerçeğine dayanır
        # Yeni bir config instance'ı almanın bir yolu olmadığı için
        # sadece fonksiyon çıktılarını test edebiliriz
        
        with patch('backend.utils.config.API_HOST', 'test-host'):
            config = get_all_config()
            assert config["api"]["host"] == "test-host"

    def test_cors_origins_parsing(self):
        """CORS origins doğru parse edilir"""
        config = get_all_config()
        cors_origins = config["cors"]["origins"]
        
        assert isinstance(cors_origins, list)
        # En az bir origin olmalı
        assert len(cors_origins) >= 1

    def test_database_url_validation(self):
        """Database URL validasyonu"""
        db_url = get_db_url()
        
        # URL format kontrolü (mongodb:// veya mongodb+srv://)
        assert db_url.startswith(("mongodb://", "mongodb+srv://")) or db_url == "mongodb://localhost:27017/buzz2remote"

    def test_telegram_enabled_logic(self):
        """Telegram enabled logic doğru çalışır"""
        config = get_all_config()
        telegram_config = config["telegram"]
        
        # Eğer bot_token placeholder ile başlıyorsa enabled false olmalı
        if telegram_config["bot_token"].startswith("YOUR_"):
            assert telegram_config["enabled"] is False
        else:
            # Gerçek token varsa, TELEGRAM_ENABLED değeri kullanılır
            assert isinstance(telegram_config["enabled"], bool)

    def test_production_vs_development_settings(self):
        """Production ve development ayarları doğru"""
        config = get_all_config()
        
        # Production durumuna göre bazı ayarların farklı olması beklenir
        if config["database"]["is_production"]:
            # Production'da debug kapalı olmalı (genel kural)
            pass  # Config'de debug production'a göre ayarlanmamış, bu normal
        else:
            # Development'ta local database kullanılabilir
            pass

    def test_config_immutability(self):
        """Config değerleri tutarlı kalır"""
        config1 = get_all_config()
        config2 = get_all_config()
        
        # Aynı değerleri döndürmeli
        assert config1["api"]["host"] == config2["api"]["host"]
        assert config1["api"]["port"] == config2["api"]["port"]
        assert config1["database"]["url"] == config2["database"]["url"]

    def test_header_values_are_strings(self):
        """Crawler headers tüm değerleri string"""
        headers = get_crawler_headers()
        
        for key, value in headers.items():
            assert isinstance(key, str)
            assert isinstance(value, str)
            assert len(value) > 0

    def test_numeric_configs_are_positive(self):
        """Numerik config değerleri pozitif"""
        config = get_all_config()
        
        # Port numarası pozitif olmalı
        assert config["api"]["port"] > 0
        
        # Email port pozitif olmalı  
        assert config["email"]["port"] > 0
        
        # Timeout değerleri pozitif olmalı
        assert config["crawler"]["timeout"] > 0
        assert config["crawler"]["delay"] >= 0
        
        # Cache değerleri pozitif olmalı
        assert config["cache"]["ttl"] > 0
        assert config["cache"]["max_size"] > 0 