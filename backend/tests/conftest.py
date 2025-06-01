import pytest
import asyncio
import os
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

# Set test environment variables
os.environ.setdefault("EMAIL_HOST", "smtp.gmail.com")
os.environ.setdefault("EMAIL_USERNAME", "test@example.com")
os.environ.setdefault("EMAIL_PASSWORD", "test_password")
os.environ.setdefault("EMAIL_FROM", "test@example.com")
os.environ.setdefault("GOOGLE_CLIENT_ID", "test_google_client_id")
os.environ.setdefault("GOOGLE_CLIENT_SECRET", "test_google_client_secret")
os.environ.setdefault("GOOGLE_REDIRECT_URI", "http://localhost:3000/auth/callback")
os.environ.setdefault("STRIPE_SECRET_KEY", "sk_test_fake")
os.environ.setdefault("STRIPE_WEBHOOK_SECRET", "whsec_test_secret")
os.environ.setdefault("OPENAI_API_KEY", "test_openai_key")
os.environ.setdefault("TELEGRAM_BOT_TOKEN", "test_telegram_token")
os.environ.setdefault("TELEGRAM_CHAT_ID", "123456789")

# Configure asyncio mode for pytest-asyncio
pytest_plugins = ['pytest_asyncio']

@pytest_asyncio.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()

@pytest_asyncio.fixture(scope="session")
async def mongodb_client():
    """Create a MongoDB client for testing."""
    try:
        client = AsyncIOMotorClient("mongodb://localhost:27017/")
        yield client
        await client.drop_database("test_db")
        client.close()
    except Exception:
        # If MongoDB is not available, use mongomock
        import mongomock_motor
        client = mongomock_motor.AsyncMongoMockClient()
        yield client

@pytest_asyncio.fixture(scope="function")
async def mongodb(mongodb_client):
    """Create a MongoDB database for testing."""
    db = mongodb_client["test_db"]
    # Clean up before each test
    try:
        await db.drop_collection("jobs")
        await db.drop_collection("users")
        await db.drop_collection("companies")
    except Exception:
        pass
    yield db

@pytest_asyncio.fixture
async def async_client(mongodb):
    """Create an async client for testing API endpoints."""
    with patch("backend.database.get_async_db", autospec=True) as mock_get_async_db:
        async def async_db_mock():
            yield mongodb
        mock_get_async_db.side_effect = async_db_mock
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
        "salary_range": "$50,000 - $70,000",
        "job_type": "Full-time",
        "experience_level": "Mid-level",
        "apply_url": "https://example.com/apply"
    }

@pytest.fixture
def mock_jobs_collection(mongodb):
    """Mock jobs collection with sample data."""
    collection = mongodb["jobs"]
    collection.insert_many([
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
    ])
    return collection

@pytest.fixture
def mock_users_collection(mongodb):
    """Mock users collection with sample data."""
    collection = mongodb["users"]
    collection.insert_many([
        {
            "_id": ObjectId(),
            "email": "test@example.com",
            "hashed_password": "hashed_password",
            "is_active": True,
            "created_at": datetime.utcnow()
        }
    ])
    return collection

@pytest.fixture
def mock_companies_collection(mongodb):
    """Mock companies collection with sample data."""
    collection = mongodb["companies"]
    collection.insert_many([
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
    ])
    return collection

@pytest.fixture
def mock_notifications_collection(mongodb):
    """Mock notifications collection."""
    return mongodb["notifications"]

@pytest.fixture
def mock_ads_collection(mongodb):
    """Mock ads collection."""
    return mongodb["ads"]

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
        "salary_range": "$50,000 - $80,000",
        "job_type": "Full-time",
        "experience_level": "Mid-level"
    }

@pytest.fixture
def mock_google_oauth():
    """Mock Google OAuth data."""
    return {
        "code": "mock_auth_code",
        "state": "mock_state"
    }

@pytest.fixture
def mock_linkedin_oauth():
    """Mock LinkedIn OAuth data."""
    return {
        "code": "mock_linkedin_code",
        "state": "mock_state"
    }

@pytest.fixture
def mock_cv_file():
    """Mock CV file for testing."""
    return {
        "filename": "test_cv.pdf",
        "content": b"Mock CV content",
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
    
    try:
        monkeypatch.setattr("external_job_apis.fetch_jobs", mock_fetch_external_jobs)
    except AttributeError:
        pass 