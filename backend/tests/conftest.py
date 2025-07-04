import pytest
import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from httpx import AsyncClient
from backend.main import app
from backend.database import get_async_db
import mongomock
from unittest.mock import patch, MagicMock, AsyncMock
from datetime import datetime
from backend.config import Settings
import pytest_asyncio
from bson import ObjectId
from fastapi.testclient import TestClient
import sys

# Set testing environment before importing the app
os.environ["TESTING"] = "true"

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
os.environ["BACKEND_CORS_ORIGINS"] = "http://localhost:3000,http://localhost:3001"
os.environ["ENVIRONMENT"] = "test"
os.environ["MONGODB_URI"] = "mongodb://localhost:27017/test_buzz2remote"

# Add project root to path to allow imports from backend
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.database.db import get_database

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for each test session."""
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="module")
def client():
    """
    Create a test client for the FastAPI app for each test module.
    This fixture is used for API-level tests.
    """
    with TestClient(app) as test_client:
        yield test_client

@pytest.fixture(scope="function")
async def db_mock():
    """
    Provides a mock of the database connection for function-scoped tests.
    This is ideal for unit tests of services or CRUD operations.
    """
    db = AsyncMock()
    
    # Create async mock collections
    db.users = AsyncMock()
    db.jobs = AsyncMock()
    db.companies = AsyncMock()
    db.user_activities = AsyncMock()
    db.user_sessions = AsyncMock()
    db.activity_summaries = AsyncMock()
    db.crawl_errors = AsyncMock()
    db.service_logs = AsyncMock()
    db.ads = AsyncMock()
    db.notifications = AsyncMock()
    db.test_collection = AsyncMock()
    db.test_concurrent = AsyncMock()
    
    # Default return values for common methods
    db.users.find_one.return_value = None
    db.jobs.find_one.return_value = None
    db.companies.find_one.return_value = None
    db.user_activities.find_one.return_value = None
    db.user_sessions.find_one.return_value = None
    
    # Mock collection methods
    for collection in [db.users, db.jobs, db.companies, db.user_activities, 
                      db.user_sessions, db.activity_summaries, db.crawl_errors,
                      db.service_logs, db.ads, db.notifications]:
        collection.insert_one = AsyncMock()
        collection.insert_many = AsyncMock()
        collection.update_one = AsyncMock()
        collection.update_many = AsyncMock()
        collection.delete_one = AsyncMock()
        collection.delete_many = AsyncMock()
        collection.find = AsyncMock()
        collection.find_one = AsyncMock()
        collection.count_documents = AsyncMock()
        collection.aggregate = AsyncMock()
        collection.create_index = AsyncMock()
        collection.drop = AsyncMock()
    
    return db

@pytest.fixture(autouse=True)
async def override_db(db_mock):
    """
    Automatically override the `get_database` dependency for all tests
    to use the mock database.
    """
    async def _override_get_db():
        return await db_mock

    app.dependency_overrides[get_database] = _override_get_db
    yield
    app.dependency_overrides.clear()

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

class MockCollection:
    """Mock collection that mimics MongoDB collection behavior."""
    
    def __init__(self):
        self._storage = {}
        # Create a mock for find that supports side_effect
        self.find = MagicMock(side_effect=self._find_implementation)
    
    def _find_implementation(self, query=None):
        """Internal find implementation."""
        return MockCursor(self._storage, query)
    
    async def count_documents(self, query=None):
        """Mock count_documents."""
        if not query:
            return len(self._storage)
        # Simple filtering for tests
        count = 0
        for doc in self._storage.values():
            if self._matches_query(doc, query):
                count += 1
        return count
    
    async def find_one(self, query):
        """Mock find_one."""
        if "_id" in query:
            target_id = query["_id"]
            if isinstance(target_id, ObjectId):
                target_id = str(target_id)
            return self._storage.get(target_id)
        return None
    
    async def insert_one(self, document):
        """Mock insert_one."""
        doc_id = document.get("_id", ObjectId())
        if isinstance(doc_id, ObjectId):
            doc_id = str(doc_id)
        document["_id"] = doc_id
        self._storage[doc_id] = document
        result = MagicMock()
        result.inserted_id = doc_id
        return result
    
    async def update_one(self, query, update):
        """Mock update_one."""
        result = MagicMock()
        result.modified_count = 0
        
        if "_id" in query:
            target_id = query["_id"]
            if isinstance(target_id, ObjectId):
                target_id = str(target_id)
            if target_id in self._storage:
                if "$set" in update:
                    self._storage[target_id].update(update["$set"])
                if "$inc" in update:
                    for key, value in update["$inc"].items():
                        self._storage[target_id][key] = self._storage[target_id].get(key, 0) + value
                result.modified_count = 1
        
        return result
    
    async def delete_one(self, query):
        """Mock delete_one."""
        result = MagicMock()
        result.deleted_count = 0
        
        if "_id" in query:
            target_id = query["_id"]
            if isinstance(target_id, ObjectId):
                target_id = str(target_id)
            if target_id in self._storage:
                del self._storage[target_id]
                result.deleted_count = 1
        
        return result
    
    def _matches_query(self, doc, query):
        """Simple query matching for tests."""
        if not query:
            return True
        for key, value in query.items():
            if key not in doc or doc[key] != value:
                return False
        return True

class MockCursor:
    """Mock cursor that mimics MongoDB cursor behavior."""
    
    def __init__(self, storage, query=None):
        self.storage = storage
        self.query = query or {}
        self._sort_spec = []
        self._skip_val = 0
        self._limit_val = None
    
    def sort(self, *args):
        """Mock sort."""
        if args:
            if isinstance(args[0], list):
                self._sort_spec = args[0]
            else:
                # Single sort spec
                self._sort_spec = [(args[0], args[1] if len(args) > 1 else 1)]
        return self
    
    def skip(self, count):
        """Mock skip."""
        self._skip_val = count
        return self
    
    def limit(self, count):
        """Mock limit."""
        self._limit_val = count
        return self
    
    async def to_list(self, length=None):
        """Mock to_list."""
        docs = []
        for doc in self.storage.values():
            if self._matches_query(doc, self.query):
                docs.append(doc)
        
        # Apply sorting
        if self._sort_spec:
            for sort_key, sort_dir in reversed(self._sort_spec):
                docs.sort(key=lambda x: x.get(sort_key, ""), reverse=(sort_dir == -1))
        
        # Apply skip and limit
        if self._skip_val:
            docs = docs[self._skip_val:]
        if self._limit_val:
            docs = docs[:self._limit_val]
        
        return docs
    
    def _matches_query(self, doc, query):
        """Simple query matching for tests."""
        if not query:
            return True
        for key, value in query.items():
            if key not in doc or doc[key] != value:
                return False
        return True

class MockDatabase:
    """Mock database that mimics MongoDB database behavior."""
    
    def __init__(self):
        self.ads = MockCollection()
        self.jobs = MockCollection()
        self.users = MockCollection()
        self.companies = MockCollection()
        self.crawl_errors = MockCollection()
        self.service_logs = MockCollection()
        self.test_collection = MockCollection()
        self.test_concurrent = MockCollection()
        # Add common database properties
        self.name = "test_database"
    
    def list_collection_names(self):
        """Mock list_collection_names method."""
        return ["ads", "jobs", "users", "companies", "crawl_errors", "service_logs"]

@pytest.fixture
def mock_database():
    """Mock database fixture for tests that expect mock_database parameter."""
    return MockDatabase()

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
        "apply_url": "https://example.com/apply",
        "url": "https://example.com/job",
        "source": "test"
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

@pytest_asyncio.fixture
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

def test_pytest_is_working():
    """A simple sanity check to ensure pytest runs."""
    assert 1 + 1 == 2

def test_can_import_fastapi_app():
    """Checks if the main FastAPI app instance can be imported without errors."""
    try:
        from backend.main import app
        assert app is not None
    except ImportError as e:
        pytest.fail(f"Failed to import the FastAPI app from backend.main: {e}") 