import pytest
from pydantic import ValidationError
from datetime import datetime

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from backend.schemas.job import JobBase, JobCreate
from backend.schemas.company import CompanyBase
from backend.schemas.user import UserCreate

def test_job_base_schema_valid():
    """Tests that a valid JobBase schema can be created with required fields."""
    job_data = {
        "title": "Software Engineer",
        "company": "Innovate Inc.",
        "location": "Remote",
        "description": "A great opportunity for a skilled engineer.",
    }
    instance = JobBase(**job_data)
    assert instance.title == job_data["title"]
    assert instance.company == job_data["company"]

def test_job_create_schema_with_salary():
    """Tests creating a JobCreate schema with optional salary fields."""
    job_data = {
        "title": "Senior Engineer",
        "company": "TestCorp",
        "location": "Remote",
        "description": "A senior test job.",
        "salary_min": 100000,
        "salary_max": 150000,
        "currency": "USD"
    }
    instance = JobCreate(**job_data)
    assert instance.salary_min == 100000
    assert instance.currency == "USD"

def test_job_schema_missing_required_field_fails():
    """Tests that creating a JobBase instance without a required field raises a ValidationError."""
    with pytest.raises(ValidationError):
        JobBase(company="A Company", location="Remote", description="Missing title field.")

def test_company_base_schema_valid():
    """Tests that a valid CompanyBase schema can be created."""
    company_data = {
        "name": "Synergy Corp",
        "website": "https://synergy.com",
        "description": "Leading the industry in synergy."
    }
    instance = CompanyBase(**company_data)
    assert instance.name == company_data["name"]
    # Pydantic v2 automatically validates and converts the URL string
    assert str(instance.website) == company_data["website"] + "/"

def test_company_schema_invalid_website():
    """Tests that an invalid website URL raises a ValidationError."""
    with pytest.raises(ValidationError):
        CompanyBase(name="Invalid Site", website="not-a-url", description="...")

def test_user_create_schema_valid():
    """Tests that a valid UserCreate schema can be created."""
    user_data = {
        "email": "test.user@example.com",
        "password": "strongpassword123",
        "name": "Test User"
    }
    instance = UserCreate(**user_data)
    assert instance.email == user_data["email"]
    assert instance.name == user_data["name"]

def test_user_create_schema_invalid_email_fails():
    """Tests that an invalid email address raises a ValidationError."""
    with pytest.raises(ValidationError):
        UserCreate(email="not-a-valid-email", password="pw", name="User") 