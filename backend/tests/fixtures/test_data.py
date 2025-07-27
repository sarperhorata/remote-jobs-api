"""
Realistic Test Data Fixtures for Buzz2Remote
Bu dosya tüm testlerde kullanılacak gerçekçi test verilerini içerir.
"""

import random
from datetime import datetime, timedelta

import pytest
from bson import ObjectId


@pytest.fixture
def realistic_jobs_data():
    """Gerçekçi iş ilanı verileri - gerçek veritabanından alınan verilerin kopyası"""
    return [
        {
            "_id": ObjectId("507f1f77bcf86cd799439011"),
            "title": "Senior Product Manager",
            "company": "TechCorp Inc.",
            "location": "Remote",
            "description": "We are looking for a Senior Product Manager to lead our product development team...",
            "requirements": [
                "Product Management",
                "Agile",
                "User Research",
                "Data Analysis",
            ],
            "salary_min": 120000,
            "salary_max": 180000,
            "job_type": "Full-time",
            "is_active": True,
            "created_at": datetime.utcnow() - timedelta(days=5),
            "application_url": "https://techcorp.com/careers/senior-pm",
            "skills": [
                "Product Strategy",
                "User Experience",
                "Market Analysis",
                "Leadership",
            ],
            "experience_level": "Senior",
            "work_type": "Remote",
        },
        {
            "_id": ObjectId("507f1f77bcf86cd799439012"),
            "title": "Frontend Developer",
            "company": "StartupXYZ",
            "location": "San Francisco, CA",
            "description": "Join our growing team as a Frontend Developer...",
            "requirements": ["React", "JavaScript", "TypeScript", "CSS"],
            "salary_min": 80000,
            "salary_max": 130000,
            "job_type": "Full-time",
            "is_active": True,
            "created_at": datetime.utcnow() - timedelta(days=3),
            "application_url": "https://startupxyz.com/jobs/frontend",
            "skills": ["React", "Vue.js", "JavaScript", "TypeScript", "CSS3", "HTML5"],
            "experience_level": "Mid",
            "work_type": "Hybrid",
        },
        {
            "_id": ObjectId("507f1f77bcf86cd799439013"),
            "title": "Data Scientist",
            "company": "BigData Corp",
            "location": "New York, NY",
            "description": "We're seeking a Data Scientist to help us build predictive models...",
            "requirements": ["Python", "Machine Learning", "Statistics", "SQL"],
            "salary_min": 100000,
            "salary_max": 150000,
            "job_type": "Full-time",
            "is_active": True,
            "created_at": datetime.utcnow() - timedelta(days=1),
            "application_url": "https://bigdatacorp.com/careers/data-scientist",
            "skills": [
                "Python",
                "R",
                "Machine Learning",
                "Deep Learning",
                "SQL",
                "Statistics",
            ],
            "experience_level": "Senior",
            "work_type": "Office",
        },
        {
            "_id": ObjectId("507f1f77bcf86cd799439014"),
            "title": "DevOps Engineer",
            "company": "CloudTech Solutions",
            "location": "Remote",
            "description": "Help us build and maintain our cloud infrastructure...",
            "requirements": ["AWS", "Docker", "Kubernetes", "Linux"],
            "salary_min": 90000,
            "salary_max": 140000,
            "job_type": "Full-time",
            "is_active": True,
            "created_at": datetime.utcnow() - timedelta(hours=12),
            "application_url": "https://cloudtech.com/jobs/devops",
            "skills": ["AWS", "Azure", "Docker", "Kubernetes", "Terraform", "Linux"],
            "experience_level": "Mid",
            "work_type": "Remote",
        },
        {
            "_id": ObjectId("507f1f77bcf86cd799439015"),
            "title": "UX/UI Designer",
            "company": "Design Studio Pro",
            "location": "Los Angeles, CA",
            "description": "Create beautiful and intuitive user experiences...",
            "requirements": [
                "Figma",
                "Adobe Creative Suite",
                "User Research",
                "Prototyping",
            ],
            "salary_min": 70000,
            "salary_max": 110000,
            "job_type": "Full-time",
            "is_active": True,
            "created_at": datetime.utcnow() - timedelta(hours=6),
            "application_url": "https://designstudiopro.com/careers/ux-designer",
            "skills": [
                "Figma",
                "Sketch",
                "Adobe XD",
                "User Research",
                "Prototyping",
                "Design Systems",
            ],
            "experience_level": "Mid",
            "work_type": "Hybrid",
        },
    ]


@pytest.fixture
def realistic_companies_data():
    """Gerçekçi şirket verileri"""
    return [
        {
            "_id": ObjectId("507f1f77bcf86cd799439021"),
            "name": "TechCorp Inc.",
            "website": "https://techcorp.com",
            "linkedin": "https://linkedin.com/company/techcorp",
            "description": "Leading technology company focused on innovative solutions",
            "industry": "Technology",
            "size": "500-1000",
            "location": "San Francisco, CA",
            "is_verified": True,
            "created_at": datetime.utcnow() - timedelta(days=30),
        },
        {
            "_id": ObjectId("507f1f77bcf86cd799439022"),
            "name": "StartupXYZ",
            "website": "https://startupxyz.com",
            "linkedin": "https://linkedin.com/company/startupxyz",
            "description": "Fast-growing startup in the fintech space",
            "industry": "Fintech",
            "size": "50-100",
            "location": "San Francisco, CA",
            "is_verified": True,
            "created_at": datetime.utcnow() - timedelta(days=15),
        },
        {
            "_id": ObjectId("507f1f77bcf86cd799439023"),
            "name": "BigData Corp",
            "website": "https://bigdatacorp.com",
            "linkedin": "https://linkedin.com/company/bigdatacorp",
            "description": "Data analytics and machine learning solutions",
            "industry": "Data & Analytics",
            "size": "1000+",
            "location": "New York, NY",
            "is_verified": True,
            "created_at": datetime.utcnow() - timedelta(days=45),
        },
    ]


@pytest.fixture
def realistic_users_data():
    """Gerçekçi kullanıcı verileri"""
    return [
        {
            "_id": ObjectId("507f1f77bcf86cd799439031"),
            "email": "john.doe@example.com",
            "name": "John Doe",
            "password_hash": "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4J/HS.iK2",  # "password123"
            "is_verified": True,
            "created_at": datetime.utcnow() - timedelta(days=60),
            "profile": {
                "skills": ["Python", "JavaScript", "React"],
                "experience_level": "Mid",
                "location": "San Francisco, CA",
                "salary_expectation": 120000,
                "work_type_preference": "Remote",
            },
        },
        {
            "_id": ObjectId("507f1f77bcf86cd799439032"),
            "email": "jane.smith@example.com",
            "name": "Jane Smith",
            "password_hash": "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4J/HS.iK2",  # "password123"
            "is_verified": True,
            "created_at": datetime.utcnow() - timedelta(days=30),
            "profile": {
                "skills": ["Product Management", "User Research", "Data Analysis"],
                "experience_level": "Senior",
                "location": "New York, NY",
                "salary_expectation": 150000,
                "work_type_preference": "Hybrid",
            },
        },
    ]


@pytest.fixture
def realistic_applications_data():
    """Gerçekçi başvuru verileri"""
    return [
        {
            "_id": ObjectId("507f1f77bcf86cd799439041"),
            "user_id": ObjectId("507f1f77bcf86cd799439031"),
            "job_id": ObjectId("507f1f77bcf86cd799439011"),
            "status": "applied",
            "applied_at": datetime.utcnow() - timedelta(days=2),
            "cover_letter": "I am excited to apply for the Senior Product Manager position...",
            "resume_url": "https://example.com/resumes/john_doe_resume.pdf",
        },
        {
            "_id": ObjectId("507f1f77bcf86cd799439042"),
            "user_id": ObjectId("507f1f77bcf86cd799439032"),
            "job_id": ObjectId("507f1f77bcf86cd799439013"),
            "status": "interviewing",
            "applied_at": datetime.utcnow() - timedelta(days=5),
            "cover_letter": "I am interested in the Data Scientist role...",
            "resume_url": "https://example.com/resumes/jane_smith_resume.pdf",
        },
    ]


@pytest.fixture
def realistic_notifications_data():
    """Gerçekçi bildirim verileri"""
    return [
        {
            "_id": ObjectId("507f1f77bcf86cd799439051"),
            "user_id": ObjectId("507f1f77bcf86cd799439031"),
            "type": "new_job",
            "title": "New job matching your profile",
            "message": "A new Senior Product Manager position at TechCorp matches your skills",
            "job_id": ObjectId("507f1f77bcf86cd799439011"),
            "is_read": False,
            "created_at": datetime.utcnow() - timedelta(hours=2),
        },
        {
            "_id": ObjectId("507f1f77bcf86cd799439052"),
            "user_id": ObjectId("507f1f77bcf86cd799439032"),
            "type": "application_update",
            "title": "Application status updated",
            "message": "Your application for Data Scientist at BigData Corp is now being reviewed",
            "job_id": ObjectId("507f1f77bcf86cd799439013"),
            "is_read": True,
            "created_at": datetime.utcnow() - timedelta(days=1),
        },
    ]


@pytest.fixture
def mock_jobs_collection_with_data(realistic_jobs_data):
    """Gerçekçi iş verileri ile mock collection"""
    from unittest.mock import AsyncMock, MagicMock

    collection = AsyncMock()

    # Mock find method with realistic data
    async def mock_find(*args, **kwargs):
        cursor = AsyncMock()
        cursor.to_list = AsyncMock(return_value=realistic_jobs_data)
        cursor.sort = MagicMock(return_value=cursor)
        cursor.skip = MagicMock(return_value=cursor)
        cursor.limit = MagicMock(return_value=cursor)
        return cursor

    collection.find = mock_find
    collection.find_one = AsyncMock(
        side_effect=lambda *args, **kwargs: next(
            (job for job in realistic_jobs_data if job["_id"] == kwargs.get("_id")),
            None,
        )
    )
    collection.insert_one = AsyncMock(return_value=MagicMock(inserted_id=ObjectId()))
    collection.update_one = AsyncMock(return_value=MagicMock(modified_count=1))
    collection.delete_one = AsyncMock(return_value=MagicMock(deleted_count=1))
    collection.count_documents = AsyncMock(return_value=len(realistic_jobs_data))
    collection.aggregate = AsyncMock(
        return_value=AsyncMock(to_list=AsyncMock(return_value=realistic_jobs_data))
    )

    return collection


@pytest.fixture
def mock_companies_collection_with_data(realistic_companies_data):
    """Gerçekçi şirket verileri ile mock collection"""
    from unittest.mock import AsyncMock, MagicMock

    collection = AsyncMock()

    async def mock_find(*args, **kwargs):
        cursor = AsyncMock()
        cursor.to_list = AsyncMock(return_value=realistic_companies_data)
        cursor.sort = MagicMock(return_value=cursor)
        cursor.skip = MagicMock(return_value=cursor)
        cursor.limit = MagicMock(return_value=cursor)
        return cursor

    collection.find = mock_find
    collection.find_one = AsyncMock(
        side_effect=lambda *args, **kwargs: next(
            (
                company
                for company in realistic_companies_data
                if company["_id"] == kwargs.get("_id")
            ),
            None,
        )
    )
    collection.insert_one = AsyncMock(return_value=MagicMock(inserted_id=ObjectId()))
    collection.update_one = AsyncMock(return_value=MagicMock(modified_count=1))
    collection.delete_one = AsyncMock(return_value=MagicMock(deleted_count=1))
    collection.count_documents = AsyncMock(return_value=len(realistic_companies_data))

    return collection


@pytest.fixture
def mock_users_collection_with_data(realistic_users_data):
    """Gerçekçi kullanıcı verileri ile mock collection"""
    from unittest.mock import AsyncMock, MagicMock

    collection = AsyncMock()

    async def mock_find(*args, **kwargs):
        cursor = AsyncMock()
        cursor.to_list = AsyncMock(return_value=realistic_users_data)
        cursor.sort = MagicMock(return_value=cursor)
        cursor.skip = MagicMock(return_value=cursor)
        cursor.limit = MagicMock(return_value=cursor)
        return cursor

    collection.find = mock_find
    collection.find_one = AsyncMock(
        side_effect=lambda *args, **kwargs: next(
            (
                user
                for user in realistic_users_data
                if user["_id"] == kwargs.get("_id")
                or user["email"] == kwargs.get("email")
            ),
            None,
        )
    )
    collection.insert_one = AsyncMock(return_value=MagicMock(inserted_id=ObjectId()))
    collection.update_one = AsyncMock(return_value=MagicMock(modified_count=1))
    collection.delete_one = AsyncMock(return_value=MagicMock(deleted_count=1))
    collection.count_documents = AsyncMock(return_value=len(realistic_users_data))

    return collection


@pytest.fixture
def mock_database_with_realistic_data(
    mock_jobs_collection_with_data,
    mock_companies_collection_with_data,
    mock_users_collection_with_data,
):
    """Gerçekçi veriler ile mock database"""
    from unittest.mock import AsyncMock

    db = AsyncMock()
    db.jobs = mock_jobs_collection_with_data
    db.companies = mock_companies_collection_with_data
    db.users = mock_users_collection_with_data

    # Admin collection for health checks
    admin_collection = AsyncMock()
    admin_collection.command = AsyncMock(return_value={"ok": 1})
    db.admin = admin_collection
    db.command = AsyncMock(return_value={"ok": 1})

    return db
