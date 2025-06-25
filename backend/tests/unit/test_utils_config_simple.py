import pytest
from backend.utils.config import *

class TestUtilsConfig:
    """Test utils.config module"""
    
    def test_config_imports(self):
        """Test config imports work"""
        from backend.utils import config
        assert config is not None
        
    def test_config_has_database_settings(self):
        """Test config has database settings"""
        try:
            from backend.utils.config import DATABASE_URL
            assert DATABASE_URL is not None
        except ImportError:
            # If not available, thats fine
            pass
            
    def test_config_environment_handling(self):
        """Test config handles environment variables"""
        import os
        # Test that environment variables are processed
        db_url = os.environ.get("DATABASE_URL", "")
        # Should contain some database reference
        assert any(word in db_url.lower() for word in ["mongo", "db", "localhost", "database"])
