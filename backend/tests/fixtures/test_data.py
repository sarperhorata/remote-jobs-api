"""
Realistic Test Data Fixtures for Buzz2Remote
Bu dosya tüm testlerde kullanılacak gerçekçi test verilerini içerir.
"""

from datetime import datetime, timedelta
from typing import Dict, List, Any
from bson import ObjectId

# Gerçekçi şirket verileri
COMPANIES = [
    {
        "_id": ObjectId("507f1f77bcf86cd799439011"),
        "name": "TechCorp Solutions",
        "website": "https://techcorp.com",
        "size": "51-200",
        "industry": "Software Development",
        "location": "San Francisco, CA",
        "description": "Leading software development company",
        "is_verified": True,
        "job_count": 12,
        "created_at": datetime.utcnow() - timedelta(days=365),
        "updated_at": datetime.utcnow()
    },
    {
        "_id": ObjectId("507f1f77bcf86cd799439012"),
        "name": "StartupHub Inc",
        "website": "https://startuphub.io",
        "size": "11-50",
        "industry": "Technology",
        "location": "New York, NY",
        "description": "Fast-growing startup focused on AI",
        "is_verified": True,
        "job_count": 8,
        "created_at": datetime.utcnow() - timedelta(days=180),
        "updated_at": datetime.utcnow()
    }
]

# Gerçekçi iş ilanları
JOBS = [
    {
        "_id": ObjectId("507f1f77bcf86cd799439021"),
        "title": "Senior Python Developer",
        "company": "TechCorp Solutions",
        "company_id": ObjectId("507f1f77bcf86cd799439011"),
        "location": "San Francisco, CA",
        "work_type": "remote",
        "job_type": "full-time",
        "experience_level": "senior",
        "salary_min": 120000,
        "salary_max": 160000,
        "salary_currency": "USD",
        "description": "We are looking for a Senior Python Developer.",
        "requirements": ["5+ years Python experience"],
        "benefits": ["Health insurance", "Remote work"],
        "skills": ["Python", "Django", "FastAPI"],
        "posted_date": datetime.utcnow() - timedelta(days=5),
        "status": "active",
        "view_count": 245,
        "application_count": 12,
        "created_at": datetime.utcnow() - timedelta(days=5),
        "updated_at": datetime.utcnow()
    }
]

# Kullanıcı verileri
USERS = [
    {
        "_id": ObjectId("507f1f77bcf86cd799439031"),
        "email": "john.doe@example.com",
        "password_hash": "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewWOhQ7H4KOdJ3gm",
        "name": "John Doe",
        "first_name": "John",
        "last_name": "Doe",
        "is_verified": True,
        "is_active": True,
        "email_verified": True,
        "created_at": datetime.utcnow() - timedelta(days=120),
        "updated_at": datetime.utcnow()
    }
]

def get_test_company(index: int = 0) -> Dict[str, Any]:
    return COMPANIES[index].copy()

def get_test_job(index: int = 0) -> Dict[str, Any]:
    return JOBS[index].copy()

def get_test_user(index: int = 0) -> Dict[str, Any]:
    return USERS[index].copy()
