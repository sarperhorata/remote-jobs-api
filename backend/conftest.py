import asyncio
import os
import sys
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Generator
from unittest.mock import AsyncMock, MagicMock, patch

import mongomock
import pytest
import pytest_asyncio
from bson import ObjectId
from fastapi.testclient import TestClient
from httpx import AsyncClient
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

# Add parent directory to sys.path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Add the current backend directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backend.database import get_async_db, get_db
from main import app


# Set up test event loop
@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


# Mock database for testing
@pytest.fixture(scope="session")
def mock_db_client():
    """Create a mock database client."""
    mock_client = MagicMock()
    return mock_client


@pytest.fixture(scope="session")
def mock_db():
    """Create a mock database instance."""
    mock_db = AsyncMock(spec=AsyncIOMotorDatabase)

    # Create mock collections
    mock_collections = {
        "companies": AsyncMock(),
        "jobs": AsyncMock(),
        "users": AsyncMock(),
        "notifications": AsyncMock(),
        "admin": AsyncMock(),
        "ads": AsyncMock(),
        "notification_settings": AsyncMock(),
    }

    # Set up mock collections with common operations
    for collection in mock_collections.values():
        collection.find = AsyncMock()
        collection.find_one = AsyncMock()
        collection.insert_one = AsyncMock()
        collection.update_one = AsyncMock()
        collection.delete_one = AsyncMock()
        collection.count_documents = AsyncMock()

        # Set up cursor mock
        mock_cursor = AsyncMock()
        mock_cursor.to_list = AsyncMock(return_value=[])
        mock_cursor.sort = MagicMock(return_value=mock_cursor)
        mock_cursor.skip = MagicMock(return_value=mock_cursor)
        mock_cursor.limit = MagicMock(return_value=mock_cursor)
        collection.find.return_value = mock_cursor
        collection.aggregate = AsyncMock(return_value=mock_cursor)

    # Attach collections to database mock
    for name, collection in mock_collections.items():
        setattr(mock_db, name, collection)

    return mock_db


@pytest.fixture
async def async_db_override(mock_db):
    """Override the database dependency for testing."""

    async def get_async_db_override():
        return mock_db

    return get_async_db_override


@pytest.fixture(scope="function")
def db_override(mock_db):
    """Override sync database dependency for testing."""
    return mock_db


@pytest.fixture(scope="function")
def client(async_db_override, db_override) -> Generator[TestClient, None, None]:
    """Create test client with database overrides."""

    def get_db_override():
        return db_override

    app.dependency_overrides[get_async_db] = async_db_override
    app.dependency_overrides[get_db] = get_db_override

    with TestClient(app) as test_client:
        yield test_client

    # Clean up overrides
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def client_with_realistic_data(
    mock_database_with_realistic_data,
) -> Generator[TestClient, None, None]:
    """Create test client with realistic test data."""

    async def get_async_db_override():
        return mock_database_with_realistic_data

    def get_db_override():
        return mock_database_with_realistic_data

    app.dependency_overrides[get_async_db] = get_async_db_override
    app.dependency_overrides[get_db] = get_db_override

    with TestClient(app) as test_client:
        yield test_client

    # Clean up overrides
    app.dependency_overrides.clear()


@pytest.fixture
def sample_job_data():
    """Sample job data for testing."""
    return {
        "title": "Software Engineer",
        "company": "TechCorp",
        "location": "Remote",
        "description": "Build amazing software",
        "requirements": "Python, FastAPI",
        "salary_min": 80000,
        "salary_max": 120000,
        "job_type": "Full-time",
        "is_active": True,
        "created_at": "2024-01-01T00:00:00Z",
        "application_url": "https://example.com/apply",
    }


@pytest.fixture
def sample_user_data():
    """Sample user data for testing."""
    return {
        "email": "test@example.com",
        "password": "testpassword123",
        "name": "Test User",
    }


@pytest.fixture
def test_user_data():
    """Test user data for auth testing."""
    return {
        "email": "test@example.com",
        "password": "testpassword123",
        "name": "Test User",
    }


# Authentication fixtures
@pytest.fixture
def auth_headers():
    """Mock authentication headers."""
    return {"Authorization": "Bearer test-token"}


@pytest.fixture
def client_with_auth(client, auth_headers) -> TestClient:
    """Test client with authentication headers."""
    client.headers.update(auth_headers)
    return client


# Create comprehensive async mock database
@pytest.fixture(scope="session")
def mock_collection():
    """Create a mock collection with common operations."""
    collection = AsyncMock()
    collection.find = AsyncMock()
    collection.find_one = AsyncMock()
    collection.insert_one = AsyncMock()
    collection.update_one = AsyncMock()
    collection.delete_one = AsyncMock()
    collection.count_documents = AsyncMock()

    # Set up cursor mock
    mock_cursor = AsyncMock()
    mock_cursor.to_list = AsyncMock(return_value=[])
    mock_cursor.sort = MagicMock(return_value=mock_cursor)
    mock_cursor.skip = MagicMock(return_value=mock_cursor)
    mock_cursor.limit = MagicMock(return_value=mock_cursor)
    collection.find.return_value = mock_cursor
    collection.aggregate = AsyncMock(return_value=mock_cursor)

    return collection


@pytest.fixture(scope="session")
def mock_database(mock_collection):
    """Create a mock database with collections."""
    db = AsyncMock(spec=AsyncIOMotorDatabase)
    db.companies = mock_collection
    db.jobs = mock_collection
    db.users = mock_collection
    db.notifications = mock_collection
    db.notification_settings = mock_collection

    # Create admin collection with command method for health checks
    admin_collection = AsyncMock()
    admin_collection.command = AsyncMock(return_value={"ok": 1})
    db.admin = admin_collection

    # Add command method to database itself for health checks
    db.command = AsyncMock(return_value={"ok": 1})

    return db


@pytest.fixture(scope="session")
def mock_database_with_realistic_data(
    realistic_jobs_data, realistic_companies_data, realistic_users_data
):
    """Create a mock database with realistic test data."""

    db = AsyncMock(spec=AsyncIOMotorDatabase)

    # Mock jobs collection with realistic data
    jobs_collection = AsyncMock()

    async def mock_jobs_find(*args, **kwargs):
        cursor = AsyncMock()
        cursor.to_list = AsyncMock(return_value=realistic_jobs_data)
        cursor.sort = MagicMock(return_value=cursor)
        cursor.skip = MagicMock(return_value=cursor)
        cursor.limit = MagicMock(return_value=cursor)
        return cursor

    jobs_collection.find = mock_jobs_find
    jobs_collection.find_one = AsyncMock(
        side_effect=lambda *args, **kwargs: next(
            (job for job in realistic_jobs_data if job["_id"] == kwargs.get("_id")),
            None,
        )
    )
    jobs_collection.count_documents = AsyncMock(return_value=len(realistic_jobs_data))
    jobs_collection.aggregate = AsyncMock(
        return_value=AsyncMock(to_list=AsyncMock(return_value=realistic_jobs_data))
    )
    db.jobs = jobs_collection

    # Mock companies collection with realistic data
    companies_collection = AsyncMock()

    async def mock_companies_find(*args, **kwargs):
        cursor = AsyncMock()
        cursor.to_list = AsyncMock(return_value=realistic_companies_data)
        cursor.sort = MagicMock(return_value=cursor)
        cursor.skip = MagicMock(return_value=cursor)
        cursor.limit = MagicMock(return_value=cursor)
        return cursor

    companies_collection.find = mock_companies_find
    companies_collection.find_one = AsyncMock(
        side_effect=lambda *args, **kwargs: next(
            (
                company
                for company in realistic_companies_data
                if company["_id"] == kwargs.get("_id")
            ),
            None,
        )
    )
    companies_collection.count_documents = AsyncMock(
        return_value=len(realistic_companies_data)
    )
    db.companies = companies_collection

    # Mock users collection with realistic data
    users_collection = AsyncMock()

    async def mock_users_find(*args, **kwargs):
        cursor = AsyncMock()
        cursor.to_list = AsyncMock(return_value=realistic_users_data)
        cursor.sort = MagicMock(return_value=cursor)
        cursor.skip = MagicMock(return_value=cursor)
        cursor.limit = MagicMock(return_value=cursor)
        return cursor

    users_collection.find = mock_users_find
    users_collection.find_one = AsyncMock(
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
    users_collection.count_documents = AsyncMock(return_value=len(realistic_users_data))
    db.users = users_collection

    # Create admin collection with command method for health checks
    admin_collection = AsyncMock()
    admin_collection.command = AsyncMock(return_value={"ok": 1})
    db.admin = admin_collection

    # Add command method to database itself for health checks
    db.command = AsyncMock(return_value={"ok": 1})

    return db


# Database setup/teardown with proper async mocking
@pytest.fixture(autouse=True)
def setup_test_db(mock_database):
    """Mock the database for all tests with proper async support."""
    with patch("backend.database.get_db", return_value=mock_database):
        with patch("database.get_db", return_value=mock_database):
            with patch("backend.database.db", mock_database):
                with patch("database.db", mock_database):
                    # Also patch the async database getter
                    async def mock_get_async_db():
                        return mock_database

                    with patch("backend.database.get_async_db", mock_get_async_db):
                        with patch("database.get_async_db", mock_get_async_db):
                            with patch(
                                "backend.database.get_database",
                                return_value=mock_database,
                            ):
                                yield mock_database


# Test data fixtures
@pytest.fixture
def sample_companies():
    """Sample company data for testing."""
    return [
        {
            "name": "TechCorp",
            "website": "https://techcorp.com",
            "career_page": "https://techcorp.com/careers",
            "description": "Leading tech company",
            "industry": "Technology",
            "size": "1000-5000",
            "location": "San Francisco, CA",
        },
        {
            "name": "StartupXYZ",
            "website": "https://startupxyz.com",
            "career_page": "https://startupxyz.com/jobs",
            "description": "Innovative startup",
            "industry": "SaaS",
            "size": "10-50",
            "location": "Austin, TX",
        },
    ]


@pytest.fixture
def sample_jobs():
    """Sample job data for testing."""
    return [
        {
            "title": "Senior Python Developer",
            "company": "TechCorp",
            "location": "Remote",
            "description": "We are looking for a Senior Python Developer",
            "requirements": "5+ years Python experience",
            "salary_min": 100000,
            "salary_max": 150000,
            "job_type": "Full-time",
            "is_active": True,
            "application_url": "https://techcorp.com/apply/1",
        },
        {
            "title": "Frontend Developer",
            "company": "StartupXYZ",
            "location": "Austin, TX",
            "description": "Join our frontend team",
            "requirements": "React, TypeScript",
            "salary_min": 80000,
            "salary_max": 120000,
            "job_type": "Full-time",
            "is_active": True,
            "application_url": "https://startupxyz.com/apply/1",
        },
    ]


# Mock specific collections for complex scenarios
@pytest.fixture
def mock_jobs_collection(mock_database):
    """Mock jobs collection with sample data."""
    sample_jobs = [
        {
            "_id": "507f1f77bcf86cd799439011",
            "title": "Senior Python Developer",
            "company": "TechCorp",
            "location": "Remote",
            "source": "direct",
            "created_at": "2024-01-01T00:00:00Z",
        }
    ]

    # Create proper mock cursor
    mock_cursor = AsyncMock()
    mock_cursor.to_list = AsyncMock(return_value=sample_jobs)
    mock_cursor.sort = MagicMock(return_value=mock_cursor)
    mock_cursor.skip = MagicMock(return_value=mock_cursor)
    mock_cursor.limit = MagicMock(return_value=mock_cursor)

    # Set up the database mock properly
    mock_database.jobs.find = MagicMock(return_value=mock_cursor)
    mock_database.jobs.count_documents = AsyncMock(return_value=len(sample_jobs))
    mock_database.jobs.find_one = AsyncMock(return_value=sample_jobs[0])
    mock_database.jobs.insert_one = AsyncMock(
        return_value=MagicMock(inserted_id="new_id")
    )
    mock_database.jobs.update_one = AsyncMock(return_value=MagicMock(modified_count=1))
    mock_database.jobs.delete_one = AsyncMock(return_value=MagicMock(deleted_count=1))

    return mock_database.jobs


@pytest.fixture
def mock_companies_collection(mock_database):
    """Mock companies collection with sample data."""
    sample_companies = [
        {
            "_id": "TechCorp",
            "job_count": 5,
            "latest_job": "2024-01-01T00:00:00Z",
            "website": "https://techcorp.com",
        }
    ]

    # Create proper mock aggregation cursor
    mock_agg_cursor = AsyncMock()
    mock_agg_cursor.to_list = AsyncMock(return_value=sample_companies)

    # Set up companies collection mock
    mock_database.companies.aggregate = MagicMock(return_value=mock_agg_cursor)
    mock_database.companies.find = MagicMock(
        return_value=AsyncMock(to_list=AsyncMock(return_value=sample_companies))
    )
    mock_database.companies.count_documents = AsyncMock(
        return_value=len(sample_companies)
    )

    return mock_database.companies


# Skip slow tests by default
def pytest_configure(config):
    config.addinivalue_line("markers", "slow: marks tests as slow")
    config.addinivalue_line("markers", "integration: marks tests as integration tests")
    config.addinivalue_line("markers", "unit: marks tests as unit tests")
    config.addinivalue_line("markers", "api: marks tests as API tests")
    config.addinivalue_line("markers", "syntax: marks tests as syntax tests")


def pytest_collection_modifyitems(config, items):
    # Run all tests by default, including slow ones
    pass


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.fixture
async def async_client(mock_database):
    """Create an async test client."""
    from main import app

    # Set up database dependency overrides
    async def mock_get_async_db():
        return mock_database

    def mock_get_db():
        return mock_database

    app.dependency_overrides[get_async_db] = mock_get_async_db
    app.dependency_overrides[get_db] = mock_get_db

    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client

    # Clean up overrides
    app.dependency_overrides.clear()


@pytest.fixture
async def async_client_with_realistic_data(mock_database_with_realistic_data):
    """Create async test client with realistic test data."""
    from main import app

    # Set up database dependency overrides
    async def mock_get_async_db():
        return mock_database_with_realistic_data

    def mock_get_db():
        return mock_database_with_realistic_data

    app.dependency_overrides[get_async_db] = mock_get_async_db
    app.dependency_overrides[get_db] = mock_get_db

    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client

    # Clean up overrides
    app.dependency_overrides.clear()


@pytest.fixture
def mock_cv_file():
    """Mock CV file for testing file uploads."""
    return {
        "filename": "test_cv.pdf",
        "content": b"mock pdf content",
        "content_type": "application/pdf",
    }


# MongoDB collection fixtures for specific testing scenarios
@pytest.fixture
def mongodb(mock_database):
    """Provide mock MongoDB instance."""
    return {
        "jobs": mock_database.jobs,
        "users": mock_database.users,
        "companies": mock_database.companies,
    }


@pytest.fixture
def mock_token():
    return "mock.jwt.token"


@pytest.fixture
def client_with_auth_header(client, mock_token):
    """Create a client with authentication headers."""
    client.headers.update({"Authorization": f"Bearer {mock_token}"})
    return client


@pytest.fixture
def mock_auth():
    """Create mock authentication."""
    return {"username": "test_admin", "password": "test_password", "is_admin": True}


@pytest.fixture
def mock_session():
    """Create mock session data."""
    return {"user": {"username": "test_admin", "is_admin": True}}
