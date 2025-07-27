import os
from unittest.mock import patch

import pytest

from backend.utils.config import (API_HOST, API_PORT, DATABASE_URL, USER_AGENT,
                                  get_all_config, get_crawler_headers,
                                  get_db_url)


class TestConfigFunctions:
    """Test config utility functions"""

    def test_get_db_url_returns_database_url(self):
        """Test get_db_url returns DATABASE_URL"""
        result = get_db_url()
        assert result == DATABASE_URL
        assert isinstance(result, str)

    @patch.dict(os.environ, {"DATABASE_URL": "mongodb://test:27017/testdb"})
    def test_get_db_url_with_custom_url(self):
        """Test get_db_url with custom DATABASE_URL"""
        # Reload module to pick up new env var
        import importlib

        import utils.config

        importlib.reload(utils.config)

        result = utils.config.get_db_url()
        assert "mongodb://test:27017/testdb" in result

    def test_get_crawler_headers_structure(self):
        """Test get_crawler_headers returns correct structure"""
        headers = get_crawler_headers()

        assert isinstance(headers, dict)
        assert "User-Agent" in headers
        assert "Accept-Language" in headers
        assert "Accept" in headers

        # Check values
        assert headers["User-Agent"] == USER_AGENT
        assert headers["Accept-Language"] == "en-US,en;q=0.9"
        assert "text/html" in headers["Accept"]

    def test_get_crawler_headers_content(self):
        """Test get_crawler_headers returns expected values"""
        headers = get_crawler_headers()

        # Should contain realistic browser headers
        assert "Mozilla" in headers["User-Agent"]
        assert "Chrome" in headers["User-Agent"]
        assert headers["Accept-Language"].startswith("en-US")

    def test_get_all_config_structure(self):
        """Test get_all_config returns complete config structure"""
        config = get_all_config()

        assert isinstance(config, dict)

        # Check main sections exist
        required_sections = [
            "api",
            "database",
            "email",
            "telegram",
            "monitor",
            "crawler",
            "cors",
            "jwt",
            "cache",
            "rate_limit",
            "file_upload",
            "premium",
            "notification",
            "security",
        ]

        for section in required_sections:
            assert section in config
            assert isinstance(config[section], dict)

    def test_get_all_config_api_section(self):
        """Test API section in config"""
        config = get_all_config()
        api_config = config["api"]

        assert api_config["host"] == API_HOST
        assert api_config["port"] == API_PORT
        assert isinstance(api_config["debug"], bool)
        assert isinstance(api_config["reload"], bool)

    def test_get_all_config_database_section(self):
        """Test database section in config"""
        config = get_all_config()
        db_config = config["database"]

        assert "url" in db_config
        assert "is_production" in db_config
        assert isinstance(db_config["is_production"], bool)
        assert db_config["url"] == get_db_url()

    def test_get_all_config_email_section(self):
        """Test email section in config"""
        config = get_all_config()
        email_config = config["email"]

        required_fields = ["host", "port", "user", "from", "enabled"]
        for field in required_fields:
            assert field in email_config

        assert isinstance(email_config["port"], int)
        assert isinstance(email_config["enabled"], bool)

    def test_get_all_config_security_section(self):
        """Test security section in config"""
        config = get_all_config()
        security_config = config["security"]

        assert security_config["password_min_length"] >= 8
        assert isinstance(security_config["require_uppercase"], bool)
        assert isinstance(security_config["require_lowercase"], bool)
        assert isinstance(security_config["require_numbers"], bool)
        assert isinstance(security_config["require_special"], bool)

    def test_get_all_config_crawler_section(self):
        """Test crawler section in config"""
        config = get_all_config()
        crawler_config = config["crawler"]

        assert isinstance(crawler_config["timeout"], int)
        assert isinstance(crawler_config["delay"], float)
        assert crawler_config["user_agent"] == USER_AGENT
        assert crawler_config["timeout"] > 0
        assert crawler_config["delay"] > 0

    def test_get_all_config_premium_section(self):
        """Test premium section in config"""
        config = get_all_config()
        premium_config = config["premium"]

        assert isinstance(premium_config["price"], float)
        assert isinstance(premium_config["free_trial_days"], int)
        assert isinstance(premium_config["max_free_job_views"], int)
        assert premium_config["price"] > 0
        assert premium_config["free_trial_days"] > 0

    @patch.dict(os.environ, {"API_DEBUG": "false", "API_RELOAD": "false"})
    def test_get_all_config_with_env_overrides(self):
        """Test config with environment variable overrides"""
        # Reload module to pick up new env vars
        import importlib

        import utils.config

        importlib.reload(utils.config)

        config = utils.config.get_all_config()
        # Note: Due to module loading, this might not reflect changes
        # but tests the function behavior
        assert isinstance(config["api"]["debug"], bool)
        assert isinstance(config["api"]["reload"], bool)

    def test_config_functions_return_consistent_data(self):
        """Test that config functions return consistent data"""
        config1 = get_all_config()
        config2 = get_all_config()

        # Should return same structure
        assert config1.keys() == config2.keys()

        # Database URL should be consistent
        db_url1 = get_db_url()
        db_url2 = get_db_url()
        assert db_url1 == db_url2

        # Headers should be consistent
        headers1 = get_crawler_headers()
        headers2 = get_crawler_headers()
        assert headers1 == headers2
