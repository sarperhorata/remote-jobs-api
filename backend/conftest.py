import sys
import os
import asyncio
import pytest
import pytest_asyncio
from typing import Generator, AsyncGenerator
from fastapi.testclient import TestClient
from motor.motor_asyncio import AsyncIOMotorClient
import mongomock

# Add parent directory to sys.path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app
from database import get_async_db, get_db

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
    """Create a mock MongoDB client for testing."""
    client = mongomock.MongoClient()
    return client

@pytest.fixture(scope="session")
def mock_db(mock_db_client):
    """Create a mock database for testing."""
    return mock_db_client.get_database("test_buzz2remote")

@pytest.fixture(scope="function")
async def async_db_override(mock_db):
    """Override async database dependency for testing."""
    # Create a mock async collection
    class MockAsyncCollection:
        def __init__(self, collection):
            self._collection = collection
            
        async def find_one(self, filter_dict=None):
            return self._collection.find_one(filter_dict)
            
        async def find(self, filter_dict=None):
            class AsyncCursor:
                def __init__(self, cursor):
                    self._cursor = cursor
                    
                async def to_list(self, length=None):
                    return list(self._cursor)
                    
                def sort(self, *args):
                    return AsyncCursor(self._cursor.sort(*args))
                    
                def skip(self, count):
                    return AsyncCursor(self._cursor.skip(count))
                    
                def limit(self, count):
                    return AsyncCursor(self._cursor.limit(count))
                    
            return AsyncCursor(self._collection.find(filter_dict))
            
        async def insert_one(self, document):
            return self._collection.insert_one(document)
            
        async def update_one(self, filter_dict, update):
            return self._collection.update_one(filter_dict, update)
            
        async def delete_one(self, filter_dict):
            return self._collection.delete_one(filter_dict)
            
        async def count_documents(self, filter_dict=None):
            return self._collection.count_documents(filter_dict or {})
            
        async def aggregate(self, pipeline):
            class AsyncAggCursor:
                def __init__(self, cursor):
                    self._cursor = list(cursor)
                    
                async def to_list(self, length=None):
                    return self._cursor[:length] if length else self._cursor
                    
            return AsyncAggCursor(mock_db.get_collection("jobs").aggregate(pipeline))
    
    class MockAsyncDB:
        def __init__(self, db):
            self._db = db
            
        def __getattr__(self, name):
            return MockAsyncCollection(self._db[name])
            
        def get_collection(self, name):
            return MockAsyncCollection(self._db[name])
    
    async_mock_db = MockAsyncDB(mock_db)
    return async_mock_db

@pytest.fixture(scope="function") 
def db_override(mock_db):
    """Override sync database dependency for testing."""
    return mock_db

@pytest.fixture(scope="function")
def client(async_db_override, db_override) -> Generator[TestClient, None, None]:
    """Create test client with database overrides."""
    
    async def get_async_db_override():
        yield async_db_override
        
    def get_db_override():
        return db_override
    
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
        "application_url": "https://example.com/apply"
    }

@pytest.fixture
def sample_user_data():
    """Sample user data for testing."""
    return {
        "email": "test@example.com",
        "password": "testpassword123",
        "name": "Test User"
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

# Database setup/teardown
@pytest.fixture(autouse=True)
def setup_test_db(mock_db):
    """Set up test database for each test."""
    # Clear collections before each test
    for collection_name in mock_db.list_collection_names():
        mock_db[collection_name].delete_many({})
    
    yield
    
    # Clean up after test
    for collection_name in mock_db.list_collection_names():
        mock_db[collection_name].delete_many({})

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
            "location": "San Francisco, CA"
        },
        {
            "name": "StartupXYZ", 
            "website": "https://startupxyz.com",
            "career_page": "https://startupxyz.com/jobs",
            "description": "Innovative startup",
            "industry": "SaaS",
            "size": "10-50",
            "location": "Austin, TX"
        }
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
            "application_url": "https://techcorp.com/apply/1"
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
            "application_url": "https://startupxyz.com/apply/1"
        }
    ]

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