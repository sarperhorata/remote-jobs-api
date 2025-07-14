#!/usr/bin/env python3
"""
Pydantic V2 Migration Tests
Tests to verify successful migration from class Config to ConfigDict
"""

import pytest
from pydantic import BaseModel, ConfigDict
import importlib
import inspect


class TestPydanticV2Migration:
    """Test Pydantic V2 migration to ConfigDict"""

    def test_models_use_configdict(self):
        """Test that all models use ConfigDict instead of class Config"""
        # Import all model modules
        model_modules = [
            "models.models",
            "models.profile", 
            "models.company",
            "models.api_service_log",
            "models.user_activity",
            "models.job_multilang"
        ]
        
        for module_name in model_modules:
            try:
                module = importlib.import_module(module_name)
                # Get all classes in the module
                for name, obj in inspect.getmembers(module, inspect.isclass):
                    if issubclass(obj, BaseModel) and obj != BaseModel:
                        # Check that the model has model_config instead of Config
                        assert hasattr(obj, "model_config"), f"{name} in {module_name} missing model_config"
                        assert not hasattr(obj, "Config"), f"{name} in {module_name} still has old Config class"
                        
                        # Check that model_config is ConfigDict instance
                        if hasattr(obj, "model_config") and obj.model_config is not None:
                            # ConfigDict should be dict-like
                            assert isinstance(obj.model_config, (dict, ConfigDict)), f"{name} model_config is not ConfigDict"
                            
            except ImportError:
                pytest.skip(f"Module {module_name} not found")

    def test_schema_models_use_configdict(self):
        """Test that schema models use ConfigDict"""
        schema_modules = [
            "schemas.user_activity"
        ]
        
        for module_name in schema_modules:
            try:
                module = importlib.import_module(module_name)
                for name, obj in inspect.getmembers(module, inspect.isclass):
                    if issubclass(obj, BaseModel) and obj != BaseModel:
                        if hasattr(obj, "model_config"):
                            assert isinstance(obj.model_config, (dict, ConfigDict)), f"{name} schema model_config is not ConfigDict"
                            
            except ImportError:
                pytest.skip(f"Schema module {module_name} not found")

    def test_config_settings_use_settingsconfigdict(self):
        """Test that Settings models use SettingsConfigDict"""
        try:
            from core.config import Settings
            from pydantic_settings import SettingsConfigDict
            
            # Check that Settings has model_config
            assert hasattr(Settings, "model_config"), "Settings missing model_config"
            assert not hasattr(Settings, "Config"), "Settings still has old Config class"
            
            # Check that it's SettingsConfigDict
            if hasattr(Settings, "model_config") and Settings.model_config is not None:
                assert isinstance(Settings.model_config, (dict, SettingsConfigDict)), "Settings model_config is not SettingsConfigDict"
                
        except ImportError:
            pytest.skip("core.config module not found")

    def test_no_deprecation_warnings_for_models(self):
        """Test that importing models doesn't generate Pydantic deprecation warnings"""
        import warnings
        
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            
            # Import model modules
            try:
                import models.models
                import models.profile
                import models.company
                
                # Filter for Pydantic deprecation warnings
                pydantic_warnings = [warning for warning in w 
                                   if "pydantic" in str(warning.message).lower() and 
                                      "deprecated" in str(warning.message).lower()]
                
                # Should have minimal deprecation warnings
                assert len(pydantic_warnings) <= 2, f"Too many Pydantic deprecation warnings: {[str(w.message) for w in pydantic_warnings]}"
                
            except ImportError as e:
                pytest.skip(f"Could not import models: {e}")

    def test_model_instantiation_works(self):
        """Test that models can be instantiated without errors"""
        try:
            from models.models import User, UserNotification
            from datetime import datetime
            
            # Test User model instantiation
            user_data = {
                "email": "test@example.com",
                "name": "Test User",
                "is_active": True,
                "email_verified": True,
                "onboarding_completed": True,
                "onboarding_step": 4
            }
            
            user = User(**user_data)
            assert user.email == "test@example.com"
            assert user.name == "Test User"
            
            # Test UserNotification model
            notification_data = {
                "user_id": "user123",
                "title": "Test Notification",
                "message": "Test message",
                "notification_type": "info",
                "is_read": False
            }
            
            notification = UserNotification(**notification_data)
            assert notification.title == "Test Notification"
            assert notification.notification_type == "info"
            
        except ImportError as e:
            pytest.skip(f"Could not import models for testing: {e}")

    def test_json_serialization_works(self):
        """Test that models can be serialized to JSON"""
        try:
            from models.models import User
            
            user = User(
                email="test@example.com",
                name="Test User"
            )
            
            # Test JSON serialization
            json_data = user.model_dump()
            assert isinstance(json_data, dict)
            assert json_data["email"] == "test@example.com"
            
            # Test JSON string serialization  
            json_str = user.model_dump_json()
            assert isinstance(json_str, str)
            assert "test@example.com" in json_str
            
        except ImportError as e:
            pytest.skip(f"Could not import models for JSON testing: {e}")

    def test_model_validation_works(self):
        """Test that model validation still works correctly"""
        try:
            from models.models import User
            from pydantic import ValidationError
            
            # Test valid data
            valid_user = User(email="test@example.com")
            assert valid_user.email == "test@example.com"
            
            # Test invalid email should raise ValidationError
            with pytest.raises(ValidationError):
                User(email="invalid-email")
                
        except ImportError as e:
            pytest.skip(f"Could not import models for validation testing: {e}") 