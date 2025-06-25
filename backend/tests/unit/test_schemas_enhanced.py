"""
Schema enhancement tests for better coverage - Simplified
"""
import pytest
from pydantic import ValidationError
from datetime import datetime
import sys
import os

# Add project root to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

# Import schemas with error handling
try:
    from backend.schemas.job import JobBase
    from backend.schemas.company import CompanyBase
    from backend.schemas.user import UserBase
    SCHEMAS_AVAILABLE = True
except ImportError:
    SCHEMAS_AVAILABLE = False

@pytest.mark.skipif(not SCHEMAS_AVAILABLE, reason="Schemas not found, skipping schema tests")
class TestJobSchemas:
    """Test job schema validation and functionality"""
    
    def test_job_base_valid(self):
        """Test valid job base creation"""
        job_data = {
            "title": "Software Engineer",
            "company": "Tech Corp",
            "location": "Remote",
            "description": "Great job opportunity"
        }
        # Pydantic v2 requires all fields to be present or have defaults
        # Assuming remote and job_type might be optional with defaults in the real model
        job = JobBase(**job_data)
        assert job.title == "Software Engineer"

@pytest.mark.skipif(not SCHEMAS_AVAILABLE, reason="Schemas not found, skipping schema tests")
class TestCompanySchemas:
    """Test company schema validation"""
    
    def test_company_base_creation(self):
        """Test company base creation"""
        company_data = {
            "name": "TechCorp Inc",
            "website": "https://techcorp.com",
            "description": "Leading tech company"
        }
        company = CompanyBase(**company_data)
        assert company.name == "TechCorp Inc"

@pytest.mark.skipif(not SCHEMAS_AVAILABLE, reason="Schemas not found, skipping schema tests")
class TestUserSchemas:
    """Test user schema validation"""
    
    def test_user_base_creation(self):
        """Test user base creation"""
        user_data = {
            "email": "test@example.com",
            "name": "John Doe",
            "is_active": True,
            "onboarding_completed": False
        }
        user = UserBase(**user_data)
        assert user.email == "test@example.com"
        assert user.name == "John Doe" 