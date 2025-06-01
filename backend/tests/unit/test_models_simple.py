#!/usr/bin/env python3

import pytest
from datetime import datetime
from bson import ObjectId

# Import the actual models that exist
from backend.models.job import JobBase, JobCreate, JobUpdate, JobResponse, JobListResponse, PyObjectId
from backend.models.company import Company
from backend.models.models import Job, User, Website, Monitor

class TestJobModels:
    """Test Job Pydantic models."""
    
    def test_job_base_creation(self):
        """Test creating a JobBase instance."""
        job_data = {
            "title": "Software Engineer",
            "company": "TechCorp",
            "location": "Remote",
            "description": "Build amazing software",
            "requirements": "Python, FastAPI",
            "salary_range": "80k-120k",
            "job_type": "Full-time",
            "experience_level": "mid",
            "apply_url": "https://example.com/apply"
        }
        
        job = JobBase(**job_data)
        assert job.title == "Software Engineer"
        assert job.company == "TechCorp"
        assert job.salary_range == "80k-120k"
        assert job.apply_url == "https://example.com/apply"
    
    def test_job_create_model(self):
        """Test JobCreate model."""
        job_data = {
            "title": "Backend Developer",
            "company": "StartupXYZ",
            "location": "New York",
            "description": "Work on backend systems",
            "requirements": "Node.js, MongoDB",
            "salary_range": "60k-90k",
            "job_type": "Full-time",
            "experience_level": "junior",
            "apply_url": "https://startup.com/apply"
        }
        
        job = JobCreate(**job_data)
        assert job.title == "Backend Developer"
        assert job.created_at is None  # Optional field
        assert job.updated_at is None  # Optional field
    
    def test_job_update_model(self):
        """Test JobUpdate model with optional fields."""
        # Test with minimal data
        job_update = JobUpdate(title="Updated Title")
        assert job_update.title == "Updated Title"
        assert job_update.company is None
        assert job_update.is_active is None
        
        # Test with multiple fields
        job_update_full = JobUpdate(
            title="Senior Developer",
            salary_range="100k-150k",
            is_active=True
        )
        assert job_update_full.title == "Senior Developer"
        assert job_update_full.salary_range == "100k-150k"
        assert job_update_full.is_active is True
    
    def test_job_response_model(self):
        """Test JobResponse model."""
        job_data = {
            "title": "Data Scientist",
            "company": "DataCorp",
            "location": "San Francisco",
            "description": "Analyze data",
            "requirements": "Python, ML",
            "salary_range": "120k-180k",
            "job_type": "Full-time",
            "experience_level": "senior",
            "apply_url": "https://datacorp.com/apply"
        }
        
        job = JobResponse(**job_data)
        assert job.title == "Data Scientist"
        assert job.is_active is True  # Default value
        assert job.views_count == 0  # Default value
        assert job.applications_count == 0  # Default value
        assert isinstance(job.created_at, datetime)
    
    def test_job_list_response_model(self):
        """Test JobListResponse model."""
        job_data = {
            "title": "Test Job",
            "company": "Test Corp",
            "location": "Remote",
            "description": "Test description",
            "requirements": "Test requirements",
            "salary_range": "50k-70k",
            "job_type": "Part-time",
            "experience_level": "entry",
            "apply_url": "https://test.com/apply"
        }
        
        job = JobResponse(**job_data)
        job_list = JobListResponse(
            items=[job],
            total=1,
            page=1,
            per_page=10,
            total_pages=1
        )
        
        assert len(job_list.items) == 1
        assert job_list.total == 1
        assert job_list.page == 1
        assert job_list.per_page == 10
        assert job_list.total_pages == 1

class TestPyObjectId:
    """Test PyObjectId custom type."""
    
    def test_py_object_id_creation(self):
        """Test PyObjectId creation."""
        obj_id = PyObjectId()
        assert isinstance(obj_id, ObjectId)
        assert ObjectId.is_valid(str(obj_id))
    
    def test_py_object_id_validation(self):
        """Test PyObjectId validation."""
        valid_id = "507f1f77bcf86cd799439011"
        obj_id = PyObjectId.validate(valid_id)
        assert isinstance(obj_id, ObjectId)
        assert str(obj_id) == valid_id
    
    def test_py_object_id_invalid(self):
        """Test PyObjectId with invalid input."""
        with pytest.raises(ValueError, match="Invalid ObjectId"):
            PyObjectId.validate("invalid_id")

class TestCompanyModel:
    """Test Company Pydantic model."""
    
    def test_company_creation(self):
        """Test creating a company instance."""
        company_data = {
            "_id": "507f1f77bcf86cd799439011",
            "name": "TechCorp",
            "website": "https://techcorp.com",
            "description": "A leading tech company",
            "industry": "Technology",
            "size": "1000-5000",
            "location": "San Francisco, CA"
        }
        
        company = Company(**company_data)
        assert company.name == "TechCorp"
        assert company.website == "https://techcorp.com"
        assert company.industry == "Technology"
        assert company.id == "507f1f77bcf86cd799439011"
    
    def test_company_minimal(self):
        """Test company with minimal required fields."""
        company = Company(_id="507f1f77bcf86cd799439012", name="Test Corp")
        assert company.name == "Test Corp"
        assert company.id == "507f1f77bcf86cd799439012"

class TestModelsFromMainFile:
    """Test models from models.py file."""
    
    def test_job_model_creation(self):
        """Test Job model from models.py."""
        job = Job(
            id=1,
            title="Test Job",
            company="Test Company",
            url="https://example.com/job",
            website_id=1,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        assert job.title == "Test Job"
        assert job.company == "Test Company"
        assert job.id == 1
        assert job.is_remote is True  # Default value
    
    def test_user_model_creation(self):
        """Test User model."""
        user = User(
            email="test@example.com",
            name="Test User"
        )
        assert user.email == "test@example.com"
        assert user.name == "Test User"
        assert user.is_active is True  # Default value
        assert user.is_superuser is False  # Default value
    
    def test_website_model_creation(self):
        """Test Website model."""
        website = Website(
            id=1,
            name="Test Website",
            url="https://example.com",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        assert website.name == "Test Website"
        assert str(website.url) == "https://example.com/"  # Pydantic normalizes URLs
        assert website.is_active is True  # Default value
    
    def test_monitor_model_creation(self):
        """Test Monitor model."""
        monitor = Monitor(
            id=1,
            name="Test Monitor",
            website_id=1,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        assert monitor.name == "Test Monitor"
        assert monitor.website_id == 1
        assert monitor.check_interval == 60  # Default value
        assert monitor.is_active is True  # Default value

class TestModelSerialization:
    """Test model serialization."""
    
    def test_job_base_serialization(self):
        """Test JobBase model serialization."""
        job = JobBase(
            title="Test Job",
            company="Test Company",
            location="Remote",
            description="Test description",
            requirements="Test requirements",
            salary_range="50k-80k",
            job_type="Full-time",
            experience_level="mid",
            apply_url="https://test.com/apply"
        )
        
        job_dict = job.model_dump()
        assert isinstance(job_dict, dict)
        assert job_dict["title"] == "Test Job"
        assert job_dict["company"] == "Test Company"
        assert job_dict["salary_range"] == "50k-80k"
    
    def test_company_serialization(self):
        """Test Company model serialization."""
        company = Company(
            _id="507f1f77bcf86cd799439013",
            name="Test Corp",
            website="https://test.com"
        )
        
        company_dict = company.model_dump()
        assert isinstance(company_dict, dict)
        assert company_dict["name"] == "Test Corp"
        assert company_dict["website"] == "https://test.com"
        assert company_dict["id"] == "507f1f77bcf86cd799439013"
    
    def test_user_serialization(self):
        """Test User model serialization."""
        user = User(
            email="test@example.com",
            name="Test User"
        )
        
        user_dict = user.model_dump()
        assert isinstance(user_dict, dict)
        assert user_dict["email"] == "test@example.com"
        assert user_dict["name"] == "Test User"
        assert user_dict["is_active"] is True 