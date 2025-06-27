import pytest
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from httpx import AsyncClient
from backend.main import app
from backend.database import get_async_db
import mongomock
from unittest.mock import patch, MagicMock
from datetime import datetime
from backend.config import Settings
import pytest_asyncio
from bson import ObjectId

# Simple MongoDB fixtures for testing
@pytest_asyncio.fixture(scope="function") 
async def mongodb_client():
    """Create a MongoDB client for testing.""" 
    client = AsyncIOMotorClient("mongodb://localhost:27017/")
    yield client
    try:
        await client.drop_database("test_db")
    except:
        pass  # Ignore errors during cleanup
    client.close()

@pytest_asyncio.fixture(scope="function")
async def mongodb(mongodb_client):
    """Create a MongoDB database for testing."""
    db = mongodb_client["test_db"] 
    yield db
    # Clean up after each test 
    try:
        collections = await db.list_collection_names()
        for collection_name in collections:
            await db[collection_name].delete_many({})
    except:
        pass  # Ignore cleanup errors

@pytest_asyncio.fixture
async def async_client():
    """Create an async client for testing API endpoints."""
    # Use simple in-memory database for testing instead of mocking get_async_db
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client

@pytest.fixture
def test_user_data():
    """Test user data for authentication."""
    return {
        "email": "test@example.com",
        "password": "testpassword123",
        "full_name": "Test User"
    }

@pytest.fixture
def test_job_data():
    """Test job data for job operations."""
    return {
        "title": "Test Job",
        "company": "Test Company",
        "location": "Remote",
        "description": "Test job description",
        "requirements": "Test requirements",
        "salary_range": "50000-70000",
        "job_type": "Full-time",
        "experience_level": "Mid-level",
        "apply_url": "https://example.com/apply"
    }

@pytest.fixture
def mock_jobs_collection():
    """Mock jobs collection with sample data."""
    # Return simple mock data instead of async operations
    return [
        {
            "_id": ObjectId(),
            "title": "Senior Python Developer",
            "company": "TechCorp",
            "location": "Remote",
            "description": "We are looking for a senior Python developer",
            "is_active": True,
            "created_at": datetime.utcnow()
        },
        {
            "_id": ObjectId(),
            "title": "Frontend Developer", 
            "company": "StartupXYZ",
            "location": "Remote",
            "description": "Join our growing team",
            "is_active": True,
            "created_at": datetime.utcnow()
        }
    ]

@pytest.fixture
def mock_users_collection():
    """Mock users collection with sample data."""
    return [
        {
            "_id": ObjectId(),
            "email": "test@example.com",
            "hashed_password": "hashed_password",
            "is_active": True,
            "created_at": datetime.utcnow()
        }
    ]

@pytest.fixture
def mock_companies_collection():
    """Mock companies collection with sample data."""
    return [
        {
            "_id": ObjectId(),
            "name": "TechCorp",
            "website": "https://techcorp.com",
            "careers_url": "https://techcorp.com/careers",
            "job_count": 15
        },
        {
            "_id": ObjectId(),
            "name": "StartupXYZ",
            "website": "https://startupxyz.com", 
            "careers_url": "https://startupxyz.com/careers",
            "job_count": 8
        }
    ]

@pytest.fixture
def mock_notifications_collection():
    """Mock notifications collection."""
    return []

@pytest.fixture 
def mock_ads_collection():
    """Mock ads collection."""
    return []

@pytest.fixture
def mock_token():
    """Mock JWT token for authentication."""
    return "mock.jwt.token"

@pytest.fixture
async def client_with_auth(async_client, mock_token):
    """Test client with authentication headers."""
    async_client.headers = {"Authorization": f"Bearer {mock_token}"}
    return async_client

@pytest.fixture
def mock_companies_data():
    """Sample companies data for testing."""
    return [
        {
            "name": "TechCorp",
            "website": "https://techcorp.com",
            "careers_url": "https://techcorp.com/careers",
            "job_count": 15
        },
        {
            "name": "StartupXYZ",
            "website": "https://startupxyz.com",
            "careers_url": "https://startupxyz.com/careers",
            "job_count": 8
        }
    ]

@pytest.fixture
def auth_headers():
    """Mock authentication headers for testing."""
    return {
        "Authorization": "Bearer test-token",
        "Content-Type": "application/json"
    }

@pytest.fixture
def sample_job_data():
    """Sample job data for testing."""
    return {
        "title": "Test Job Title",
        "company": "Test Company",
        "location": "Remote",
        "source": "test",
        "url": "https://test.com/job",
        "apply_url": "https://test.com/apply",
        "description": "This is a test job description",
        "requirements": "Python, FastAPI, MongoDB",
        "salary_range": "50000-80000",
        "job_type": "Full-time",
        "experience_level": "Mid-level",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }

@pytest.fixture
def mock_google_oauth():
    """Mock Google OAuth data."""
    return {
        "client_id": "mock_client_id",
        "client_secret": "mock_client_secret",
        "redirect_uri": "http://localhost:8000/auth/google/callback"
    }

@pytest.fixture
def mock_linkedin_oauth():
    """Mock LinkedIn OAuth data."""
    return {
        "client_id": "mock_linkedin_client_id",
        "client_secret": "mock_linkedin_client_secret"
    }

@pytest.fixture
def mock_cv_file():
    """Mock CV file for testing."""
    return {
        "filename": "test_cv.pdf",
        "content": b"Mock PDF content",
        "content_type": "application/pdf"
    }

@pytest.fixture(autouse=True)
def mock_external_services(monkeypatch):
    """Mock external services like Telegram bot, external APIs etc."""

    def mock_send_notification(*args, **kwargs):
        return True

    def mock_send_deployment_notification(*args, **kwargs):
        return True

    def mock_fetch_external_jobs(*args, **kwargs):
        return []

    # Mock telegram bot completely to avoid import issues
    import sys
    
    # Create mock modules to prevent import errors
    mock_models = MagicMock()
    mock_models.models = MagicMock()
    sys.modules['models'] = mock_models
    sys.modules['models.models'] = mock_models.models
    
    # Mock telegram modules
    mock_telegram_bot = MagicMock()
    mock_telegram_bot.bot = MagicMock()
    sys.modules['telegram_bot'] = mock_telegram_bot
    sys.modules['telegram_bot.bot'] = mock_telegram_bot.bot 