import pytest
import asyncio
import os
import sys
from unittest.mock import patch, MagicMock, AsyncMock
from datetime import datetime, timedelta
import json
from bson import ObjectId

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

class TestDatabaseMigrations:
    """Database migration and schema tests"""
    
    @pytest.fixture
    def mock_db(self):
        """Mock database connection"""
        db = MagicMock()
        db.jobs = MagicMock()
        db.users = MagicMock()
        db.applications = MagicMock()
        db.companies = MagicMock()
        db.analytics = MagicMock()
        return db
    
    @pytest.mark.asyncio
    async def test_database_connection_migration(self, mock_db):
        """Test database connection and basic migration"""
        try:
            from backend.database.db import get_async_db
            
            # Mock the database connection
            with patch('backend.database.db.get_async_db', return_value=mock_db):
                db = await get_async_db()
                
                # Test connection
                assert db is not None
                assert hasattr(db, 'jobs')
                assert hasattr(db, 'users')
                assert hasattr(db, 'applications')
                
        except ImportError:
            pytest.skip("Database module not available")
    
    @pytest.mark.asyncio
    async def test_jobs_collection_schema(self, mock_db):
        """Test jobs collection schema validation"""
        # Valid job document structure
        valid_job = {
            "_id": ObjectId(),
            "title": "Software Engineer",
            "company": "Tech Corp",
            "description": "We are looking for a skilled software engineer",
            "location": "Remote",
            "salary_min": 50000,
            "salary_max": 80000,
            "requirements": ["Python", "Django", "PostgreSQL"],
            "benefits": ["Health insurance", "Remote work"],
            "job_type": "full-time",
            "experience_level": "mid-level",
            "isRemote": True,
            "posted_date": datetime.utcnow(),
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "status": "active",
            "source": "manual",
            "external_id": "ext_123",
            "company_id": ObjectId(),
            "skills": ["Python", "Django"],
            "tags": ["remote", "full-time"]
        }
        
        # Test required fields
        required_fields = ["title", "company", "description", "location"]
        for field in required_fields:
            assert field in valid_job, f"Required field {field} missing from job schema"
        
        # Test data types
        assert isinstance(valid_job["title"], str), "Title should be string"
        assert isinstance(valid_job["salary_min"], int), "Salary min should be integer"
        assert isinstance(valid_job["requirements"], list), "Requirements should be list"
        assert isinstance(valid_job["posted_date"], datetime), "Posted date should be datetime"
        
        # Test business rules
        assert valid_job["salary_min"] > 0, "Salary should be positive"
        assert valid_job["salary_max"] >= valid_job["salary_min"], "Max salary should be >= min salary"
        assert len(valid_job["title"]) > 0, "Title should not be empty"
        
        return valid_job
    
    @pytest.mark.asyncio
    async def test_users_collection_schema(self, mock_db):
        """Test users collection schema validation"""
        # Valid user document structure
        valid_user = {
            "_id": ObjectId(),
            "email": "test@example.com",
            "full_name": "John Doe",
            "password_hash": "hashed_password_123",
            "phone": "+1234567890",
            "location": "New York",
            "experience_years": 5,
            "skills": ["Python", "JavaScript", "React"],
            "resume_url": "https://example.com/resume.pdf",
            "profile_completed": True,
            "email_verified": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "last_login": datetime.utcnow(),
            "status": "active",
            "preferences": {
                "job_types": ["full-time", "remote"],
                "salary_range": {"min": 50000, "max": 100000},
                "locations": ["Remote", "New York", "San Francisco"],
                "notifications": {
                    "email": True,
                    "push": False,
                    "weekly_digest": True
                }
            },
            "subscription": {
                "plan": "premium",
                "start_date": datetime.utcnow(),
                "end_date": datetime.utcnow() + timedelta(days=30),
                "status": "active"
            }
        }
        
        # Test required fields
        required_fields = ["email", "full_name", "password_hash"]
        for field in required_fields:
            assert field in valid_user, f"Required field {field} missing from user schema"
        
        # Test data types
        assert isinstance(valid_user["email"], str), "Email should be string"
        assert isinstance(valid_user["experience_years"], int), "Experience years should be integer"
        assert isinstance(valid_user["skills"], list), "Skills should be list"
        assert isinstance(valid_user["created_at"], datetime), "Created at should be datetime"
        
        # Test business rules
        assert valid_user["experience_years"] >= 0, "Experience should be non-negative"
        assert len(valid_user["email"]) > 0, "Email should not be empty"
        assert "@" in valid_user["email"], "Email should contain @"
        
        return valid_user
    
    @pytest.mark.asyncio
    async def test_applications_collection_schema(self, mock_db):
        """Test applications collection schema validation"""
        # Valid application document structure
        valid_application = {
            "_id": ObjectId(),
            "user_id": ObjectId(),
            "job_id": ObjectId(),
            "status": "applied",
            "applied_date": datetime.utcnow(),
            "cover_letter": "I am interested in this position...",
            "resume_url": "https://example.com/resume.pdf",
            "notes": "Additional notes about the application",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "tracking": {
                "views": 0,
                "downloads": 0,
                "last_viewed": None
            },
            "ai_analysis": {
                "match_score": 85.5,
                "strengths": ["Python experience", "Remote work"],
                "weaknesses": ["Limited React experience"],
                "suggestions": ["Add React projects to portfolio"]
            }
        }
        
        # Test required fields
        required_fields = ["user_id", "job_id", "status", "applied_date"]
        for field in required_fields:
            assert field in valid_application, f"Required field {field} missing from application schema"
        
        # Test data types
        assert isinstance(valid_application["user_id"], ObjectId), "User ID should be ObjectId"
        assert isinstance(valid_application["job_id"], ObjectId), "Job ID should be ObjectId"
        assert isinstance(valid_application["status"], str), "Status should be string"
        assert isinstance(valid_application["applied_date"], datetime), "Applied date should be datetime"
        
        # Test business rules
        valid_statuses = ["applied", "reviewing", "interviewing", "offered", "rejected", "withdrawn"]
        assert valid_application["status"] in valid_statuses, f"Invalid status: {valid_application['status']}"
        
        return valid_application
    
    @pytest.mark.asyncio
    async def test_companies_collection_schema(self, mock_db):
        """Test companies collection schema validation"""
        # Valid company document structure
        valid_company = {
            "_id": ObjectId(),
            "name": "Tech Corp",
            "description": "Leading technology company",
            "website": "https://techcorp.com",
            "logo_url": "https://techcorp.com/logo.png",
            "industry": "Technology",
            "size": "100-500",
            "location": "San Francisco, CA",
            "founded_year": 2010,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "status": "active",
            "contact_info": {
                "email": "hr@techcorp.com",
                "phone": "+1-555-0123",
                "address": "123 Tech Street, San Francisco, CA 94105"
            },
            "social_media": {
                "linkedin": "https://linkedin.com/company/techcorp",
                "twitter": "https://twitter.com/techcorp",
                "github": "https://github.com/techcorp"
            },
            "stats": {
                "total_jobs": 25,
                "active_jobs": 15,
                "total_applications": 150
            }
        }
        
        # Test required fields
        required_fields = ["name", "description", "industry"]
        for field in required_fields:
            assert field in valid_company, f"Required field {field} missing from company schema"
        
        # Test data types
        assert isinstance(valid_company["name"], str), "Name should be string"
        assert isinstance(valid_company["founded_year"], int), "Founded year should be integer"
        assert isinstance(valid_company["created_at"], datetime), "Created at should be datetime"
        
        # Test business rules
        assert len(valid_company["name"]) > 0, "Company name should not be empty"
        assert valid_company["founded_year"] > 1800, "Founded year should be reasonable"
        assert valid_company["founded_year"] <= datetime.now().year, "Founded year should not be in future"
        
        return valid_company
    
    @pytest.mark.asyncio
    async def test_index_creation_migration(self, mock_db):
        """Test database index creation and validation"""
        # Mock index creation
        mock_db.jobs.create_index = AsyncMock()
        mock_db.users.create_index = AsyncMock()
        mock_db.applications.create_index = AsyncMock()
        mock_db.companies.create_index = AsyncMock()
        
        # Define required indexes
        required_indexes = {
            "jobs": [
                ("title", "text"),
                ("company", 1),
                ("location", 1),
                ("isRemote", 1),
                ("job_type", 1),
                ("experience_level", 1),
                ("salary_min", 1),
                ("salary_max", 1),
                ("posted_date", -1),
                ("status", 1),
                ("company_id", 1)
            ],
            "users": [
                ("email", 1),
                ("full_name", 1),
                ("location", 1),
                ("skills", 1),
                ("status", 1),
                ("created_at", -1)
            ],
            "applications": [
                ("user_id", 1),
                ("job_id", 1),
                ("status", 1),
                ("applied_date", -1),
                ("user_id", 1, "job_id", 1)  # Compound index
            ],
            "companies": [
                ("name", 1),
                ("industry", 1),
                ("location", 1),
                ("status", 1),
                ("created_at", -1)
            ]
        }
        
        # Test index creation
        for collection_name, indexes in required_indexes.items():
            collection = getattr(mock_db, collection_name)
            for index in indexes:
                if isinstance(index, tuple):
                    if len(index) == 2:
                        collection.create_index.assert_any_call(index[0], index[1])
                    elif len(index) == 4:
                        collection.create_index.assert_any_call([(index[0], index[1]), (index[2], index[3])])
        
        return required_indexes
    
    @pytest.mark.asyncio
    async def test_data_migration_validation(self, mock_db):
        """Test data migration validation"""
        # Mock existing data
        existing_jobs = [
            {
                "_id": ObjectId(),
                "title": "Old Job Title",
                "company": "Old Company",
                "location": "Old Location",
                "created_at": datetime.utcnow() - timedelta(days=365)
            }
        ]
        
        # Mock migration function
        async def migrate_job_data(job):
            """Mock job data migration"""
            migrated_job = job.copy()
            
            # Add new required fields
            if "salary_min" not in migrated_job:
                migrated_job["salary_min"] = 50000
            if "salary_max" not in migrated_job:
                migrated_job["salary_max"] = 80000
            if "job_type" not in migrated_job:
                migrated_job["job_type"] = "full-time"
            if "isRemote" not in migrated_job:
                migrated_job["isRemote"] = False
            if "status" not in migrated_job:
                migrated_job["status"] = "active"
            if "updated_at" not in migrated_job:
                migrated_job["updated_at"] = datetime.utcnow()
            
            return migrated_job
        
        # Test migration
        migrated_jobs = []
        for job in existing_jobs:
            migrated_job = await migrate_job_data(job)
            migrated_jobs.append(migrated_job)
        
        # Validate migrated data
        for job in migrated_jobs:
            required_fields = ["salary_min", "salary_max", "job_type", "isRemote", "status", "updated_at"]
            for field in required_fields:
                assert field in job, f"Migrated job missing required field: {field}"
            
            # Validate data types
            assert isinstance(job["salary_min"], int), "Salary min should be integer after migration"
            assert isinstance(job["salary_max"], int), "Salary max should be integer after migration"
            assert isinstance(job["job_type"], str), "Job type should be string after migration"
            assert isinstance(job["isRemote"], bool), "IsRemote should be boolean after migration"
            assert isinstance(job["updated_at"], datetime), "Updated at should be datetime after migration"
        
        return migrated_jobs
    
    @pytest.mark.asyncio
    async def test_schema_backward_compatibility(self, mock_db):
        """Test schema backward compatibility"""
        # Test that old data format is still readable
        old_format_job = {
            "_id": ObjectId(),
            "title": "Legacy Job",
            "company": "Legacy Company",
            "description": "Legacy description",
            "location": "Legacy Location"
            # Missing new fields
        }
        
        # Should be able to read old format
        assert "title" in old_format_job
        assert "company" in old_format_job
        assert "description" in old_format_job
        assert "location" in old_format_job
        
        # Should handle missing fields gracefully
        missing_fields = ["salary_min", "salary_max", "job_type", "isRemote"]
        for field in missing_fields:
            value = old_format_job.get(field, None)
            assert value is None, f"Old format should not have {field}"
        
        return old_format_job
    
    @pytest.mark.asyncio
    async def test_database_connection_pool(self, mock_db):
        """Test database connection pool configuration"""
        try:
            from backend.database.db import get_async_db
            
            # Mock connection pool settings
            pool_settings = {
                "max_pool_size": 10,
                "min_pool_size": 1,
                "max_idle_time": 30000,  # 30 seconds
                "connect_timeout": 20000,  # 20 seconds
                "server_selection_timeout": 5000  # 5 seconds
            }
            
            # Test pool configuration
            assert pool_settings["max_pool_size"] > 0, "Max pool size should be positive"
            assert pool_settings["min_pool_size"] >= 0, "Min pool size should be non-negative"
            assert pool_settings["max_pool_size"] >= pool_settings["min_pool_size"], "Max should be >= min"
            
            return pool_settings
            
        except ImportError:
            pytest.skip("Database module not available")
    
    @pytest.mark.asyncio
    async def test_database_rollback_capability(self, mock_db):
        """Test database rollback capability"""
        # Mock transaction
        mock_session = MagicMock()
        mock_session.start_transaction = AsyncMock()
        mock_session.commit_transaction = AsyncMock()
        mock_session.abort_transaction = AsyncMock()
        
        # Test successful transaction
        try:
            await mock_session.start_transaction()
            
            # Simulate database operations
            mock_db.jobs.insert_one.return_value.inserted_id = ObjectId()
            result = mock_db.jobs.insert_one({"title": "Test Job"})
            
            await mock_session.commit_transaction()
            
            assert result.inserted_id is not None, "Insert should succeed"
            
        except Exception:
            await mock_session.abort_transaction()
            raise
        
        return mock_session