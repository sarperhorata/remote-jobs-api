#!/usr/bin/env python3

import pytest
from datetime import datetime
from bson import ObjectId

# Import the correct models
from models.profile import Profile  # SQLAlchemy model
from models.user import UserBase, UserCreate, UserUpdate, UserResponse, UserInDB  # Pydantic models
from models.job_multilang import (
    MultiLangText, JobMultiLang, TranslationService, JobMigrationService
)

class TestProfileModels:
    """Test profile SQLAlchemy model to boost coverage from 0% to 100%."""
    
    def test_profile_table_name(self):
        """Test Profile table name."""
        assert Profile.__tablename__ == "profiles"
    
    def test_profile_columns(self):
        """Test Profile has expected columns."""
        # Check if columns exist
        assert hasattr(Profile, 'id')
        assert hasattr(Profile, 'name')
        assert hasattr(Profile, 'email')
        assert hasattr(Profile, 'phone')
        assert hasattr(Profile, 'location')
        assert hasattr(Profile, 'job_type')
        assert hasattr(Profile, 'skills')
        assert hasattr(Profile, 'experience')
        assert hasattr(Profile, 'education')
        assert hasattr(Profile, 'languages')

class TestUserModels:
    """Test user Pydantic models to boost coverage from 0% to 100%."""
    
    def test_user_base_creation(self):
        """Test UserBase model creation."""
        user_data = {
            "email": "test@example.com",
            "full_name": "Test User",
            "is_active": True,
            "is_superuser": False
        }
        
        user = UserBase(**user_data)
        assert user.email == "test@example.com"
        assert user.full_name == "Test User"
        assert user.is_active is True
        assert user.is_superuser is False
    
    def test_user_create_model(self):
        """Test UserCreate model."""
        user_create_data = {
            "email": "new@example.com",
            "password": "securepassword123",
            "full_name": "New User"
        }
        
        user_create = UserCreate(**user_create_data)
        assert user_create.email == "new@example.com"
        assert user_create.password == "securepassword123"
        assert user_create.full_name == "New User"
    
    def test_user_update_model(self):
        """Test UserUpdate model with optional fields."""
        # Test with minimal data
        user_update = UserUpdate(full_name="Updated Name")
        assert user_update.full_name == "Updated Name"
        assert user_update.email is None
        
        # Test with multiple fields
        user_update_full = UserUpdate(
            email="updated@example.com",
            full_name="Updated Full Name",
            is_active=False,
            telegram_user_id=123456,
            company="TechCorp",
            skills=["Python", "FastAPI"]
        )
        assert user_update_full.email == "updated@example.com"
        assert user_update_full.is_active is False
        assert user_update_full.telegram_user_id == 123456
        assert user_update_full.company == "TechCorp"
        assert "Python" in user_update_full.skills
    
    def test_user_response_model(self):
        """Test UserResponse model."""
        user_response = UserResponse(
            email="response@example.com",
            full_name="Response User",
            company="TestCorp",
            location="Remote",
            bio="Software Engineer",
            skills=["Python", "MongoDB"],
            website="https://example.com",
            github="testuser",
            linkedin="testuser",
            twitter="testuser"
        )
        
        assert user_response.email == "response@example.com"
        assert user_response.company == "TestCorp"
        assert user_response.location == "Remote"
        assert user_response.bio == "Software Engineer"
        assert user_response.website == "https://example.com"
        assert user_response.github == "testuser"
    
    def test_user_in_db_model(self):
        """Test UserInDB model with hashed password."""
        user_in_db = UserInDB(
            email="db@example.com",
            full_name="DB User",
            hashed_password="$2b$12$hashed_password"
        )
        
        assert user_in_db.email == "db@example.com"
        assert user_in_db.hashed_password == "$2b$12$hashed_password"
        assert hasattr(user_in_db, 'created_at')
        assert hasattr(user_in_db, 'updated_at')
    
    def test_user_serialization(self):
        """Test User model serialization."""
        user = UserResponse(
            email="serialize@example.com",
            full_name="Serialize Test",
            position="Developer",
            telegram_username="testuser"
        )
        
        user_dict = user.model_dump()
        assert isinstance(user_dict, dict)
        assert user_dict["email"] == "serialize@example.com"
        assert user_dict["full_name"] == "Serialize Test"
        assert user_dict["position"] == "Developer"
        assert user_dict["telegram_username"] == "testuser"

class TestMultiLangModels:
    """Test multi-language models to boost coverage from 0% to 100%."""
    
    def test_multilang_text_creation(self):
        """Test MultiLangText creation and methods."""
        multilang = MultiLangText(
            original="Hello World",
            original_lang="en"
        )
        
        assert multilang.original == "Hello World"
        assert multilang.original_lang == "en"
        assert multilang.translations == {}
    
    def test_multilang_text_get_text(self):
        """Test MultiLangText get_text method."""
        multilang = MultiLangText(
            original="Hola Mundo",
            original_lang="es"
        )
        
        # Add translation
        multilang.add_translation("en", "Hello World")
        multilang.add_translation("tr", "Merhaba Dünya")
        
        # Test getting different languages
        assert multilang.get_text("es") == "Hola Mundo"  # Original
        assert multilang.get_text("en") == "Hello World"  # Translation
        assert multilang.get_text("tr") == "Merhaba Dünya"  # Translation
        assert multilang.get_text("fr") == "Hola Mundo"  # Fallback to original
    
    def test_multilang_text_add_translation(self):
        """Test MultiLangText add_translation method."""
        multilang = MultiLangText(
            original="Test",
            original_lang="en"
        )
        
        multilang.add_translation("es", "Prueba")
        multilang.add_translation("tr", "Test")
        
        assert multilang.translations["es"] == "Prueba"
        assert multilang.translations["tr"] == "Test"
        assert len(multilang.translations) == 2
    
    def test_job_multilang_creation(self):
        """Test JobMultiLang creation."""
        job_data = {
            "title": MultiLangText(original="Software Engineer", original_lang="en"),
            "description": MultiLangText(original="We are looking for...", original_lang="en"),
            "company": "TechCorp",
            "location": "Remote",
            "apply_url": "https://example.com/apply",
            "source": "company_website",
            "source_lang": "en"
        }
        
        job = JobMultiLang(**job_data)
        assert job.title.original == "Software Engineer"
        assert job.company == "TechCorp"
        assert job.source_lang == "en"
        assert job.is_active is True
    
    def test_job_multilang_get_localized_job(self):
        """Test JobMultiLang get_localized_job method."""
        job = JobMultiLang(
            title=MultiLangText(original="Python Developer", original_lang="en"),
            description=MultiLangText(original="Build amazing apps", original_lang="en"),
            company="TechCorp",
            location="Remote",
            apply_url="https://example.com/apply",
            source="company_website",
            source_lang="en"
        )
        
        # Add translations
        job.title.add_translation("es", "Desarrollador Python")
        job.description.add_translation("es", "Construye aplicaciones increíbles")
        job.auto_translated.append("es")
        
        # Get English version
        en_job = job.get_localized_job("en")
        assert en_job["title"] == "Python Developer"
        assert en_job["is_auto_translated"] is False
        assert "en" in en_job["available_languages"]
        
        # Get Spanish version
        es_job = job.get_localized_job("es")
        assert es_job["title"] == "Desarrollador Python"
        assert es_job["description"] == "Construye aplicaciones increíbles"
        assert es_job["is_auto_translated"] is True
        assert "es" in es_job["available_languages"]
    
    def test_translation_service_detect_language(self):
        """Test TranslationService detect_language method."""
        # This will return "en" as fallback since we don't have googletrans in tests
        detected = TranslationService.detect_language("Hello world")
        assert detected == "en"  # Fallback value
    
    @pytest.mark.asyncio
    async def test_translation_service_translate_job(self):
        """Test TranslationService translate_job method."""
        job = JobMultiLang(
            title=MultiLangText(original="Software Engineer", original_lang="en"),
            description=MultiLangText(original="We are hiring", original_lang="en"),
            company="TechCorp",
            location="Remote",
            apply_url="https://example.com/apply",
            source="company_website",
            source_lang="en"
        )
        
        # This will fail gracefully and return False since googletrans is not available
        result = await TranslationService.translate_job(job, "es")
        assert result is False  # Expected to fail without googletrans
        assert job.translation_status.get("es") == "failed"
    
    @pytest.mark.asyncio
    async def test_job_migration_service(self):
        """Test JobMigrationService migrate_existing_job method."""
        existing_job = {
            "_id": ObjectId(),
            "title": "Backend Developer",
            "description": "Join our team",
            "requirements": "Python, MongoDB",
            "company": "StartupXYZ",
            "location": "Remote",
            "salary_range": "80k-120k",
            "job_type": "Full-time",
            "apply_url": "https://startup.com/apply",
            "source": "direct",
            "is_active": True
        }
        
        migrated_job = await JobMigrationService.migrate_existing_job(existing_job)
        
        assert isinstance(migrated_job, JobMultiLang)
        assert migrated_job.title.original == "Backend Developer"
        assert migrated_job.description.original == "Join our team"
        assert migrated_job.company == "StartupXYZ"
        assert migrated_job.source_lang == "en"  # Detected language
    
    def test_job_multilang_with_requirements_and_benefits(self):
        """Test JobMultiLang with optional requirements and benefits."""
        job = JobMultiLang(
            title=MultiLangText(original="Full Stack Developer", original_lang="en"),
            description=MultiLangText(original="Exciting opportunity", original_lang="en"),
            requirements=MultiLangText(original="React, Node.js", original_lang="en"),
            benefits=MultiLangText(original="Health insurance, Remote work", original_lang="en"),
            company="WebCorp",
            location="Remote",
            apply_url="https://webcorp.com/apply",
            source="company_website",
            source_lang="en"
        )
        
        localized = job.get_localized_job("en")
        assert localized["requirements"] == "React, Node.js"
        assert localized["benefits"] == "Health insurance, Remote work"
    
    def test_job_multilang_without_optional_fields(self):
        """Test JobMultiLang without optional requirements and benefits."""
        job = JobMultiLang(
            title=MultiLangText(original="Designer", original_lang="en"),
            description=MultiLangText(original="Creative role", original_lang="en"),
            company="DesignCorp",
            location="Remote",
            apply_url="https://design.com/apply",
            source="company_website",
            source_lang="en"
        )
        
        localized = job.get_localized_job("en")
        assert localized["requirements"] is None
        assert localized["benefits"] is None 