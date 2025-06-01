import sys
import os
import asyncio
import pytest
import pytest_asyncio
from typing import Generator, AsyncGenerator
from fastapi.testclient import TestClient
from motor.motor_asyncio import AsyncIOMotorClient
import mongomock
from unittest.mock import MagicMock, patch, AsyncMock
from httpx import AsyncClient
from bson import ObjectId

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
    # Create a comprehensive mock async collection
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
            
        async def insert_many(self, documents):
            return self._collection.insert_many(documents)
            
        async def update_one(self, filter_dict, update):
            return self._collection.update_one(filter_dict, update)
            
        async def update_many(self, filter_dict, update):
            return self._collection.update_many(filter_dict, update)
            
        async def delete_one(self, filter_dict):
            return self._collection.delete_one(filter_dict)
            
        async def delete_many(self, filter_dict):
            return self._collection.delete_many(filter_dict)
            
        async def count_documents(self, filter_dict=None):
            return self._collection.count_documents(filter_dict or {})
            
        async def aggregate(self, pipeline):
            class AsyncAggCursor:
                def __init__(self, cursor):
                    self._cursor = list(cursor)
                    
                async def to_list(self, length=None):
                    return self._cursor[:length] if length else self._cursor
                    
            return AsyncAggCursor(mock_db.get_collection("jobs").aggregate(pipeline))
            
        def distinct(self, field):
            return AsyncMock(return_value=[])
    
    class MockAsyncDB:
        def __init__(self, db):
            self._db = db
            
        def __getattr__(self, name):
            return MockAsyncCollection(self._db[name])
            
        def get_collection(self, name):
            return MockAsyncCollection(self._db[name])
            
        async def command(self, command):
            """Mock MongoDB command like ping"""
            return {"ok": 1}
    
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

@pytest.fixture
def test_user_data():
    """Test user data for auth testing."""
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

# Create comprehensive async mock database
@pytest.fixture
def mock_database():
    """Provide a comprehensive async mock database for testing."""
    mock_db = AsyncMock()
    
    # In-memory storage for test data
    _storage = {
        "jobs": {},
        "users": {},
        "companies": {}
    }
    
    # Create a proper async cursor mock that supports method chaining
    class MockAsyncCursor:
        def __init__(self, data=None, collection_storage=None):
            self._data = data or []
            self._storage = collection_storage or {}
            
        def skip(self, count):
            return MockAsyncCursor(self._data[count:], self._storage)
            
        def limit(self, count):
            return MockAsyncCursor(self._data[:count] if count else self._data, self._storage)
            
        def sort(self, *args):
            return MockAsyncCursor(self._data, self._storage)
            
        async def to_list(self, length=None):
            return self._data[:length] if length else self._data
            
        def __aiter__(self):
            return self
            
        async def __anext__(self):
            if self._data:
                return self._data.pop(0)
            raise StopAsyncIteration
    
    # Mock collection class with persistence
    class MockCollection:
        def __init__(self, storage_dict):
            self._storage = storage_dict
            
        async def find_one(self, filter_dict=None):
            if not filter_dict:
                return None
            
            for doc_id, doc in self._storage.items():
                # Check all filter conditions
                match = True
                for key, value in filter_dict.items():
                    if key == "_id":
                        if str(doc.get("_id")) != str(value):
                            match = False
                            break
                    else:
                        if doc.get(key) != value:
                            match = False
                            break
                
                if match:
                    return doc
            
            return None
            
        def find(self, filter_dict=None):
            data = list(self._storage.values())
            return MockAsyncCursor(data, self._storage)
            
        async def insert_one(self, document):
            doc_id = ObjectId()
            document["_id"] = doc_id
            self._storage[str(doc_id)] = document
            
            result = MagicMock()
            result.inserted_id = doc_id
            return result
            
        async def update_one(self, filter_dict, update_dict):
            result = MagicMock()
            if "_id" in filter_dict:
                doc_id = str(filter_dict["_id"])
                if doc_id in self._storage:
                    if "$set" in update_dict:
                        self._storage[doc_id].update(update_dict["$set"])
                    result.modified_count = 1
                    return result
            result.modified_count = 0
            return result
            
        async def delete_one(self, filter_dict):
            result = MagicMock()
            if "_id" in filter_dict:
                doc_id = str(filter_dict["_id"])
                if doc_id in self._storage:
                    del self._storage[doc_id]
                    result.deleted_count = 1
                    return result
            result.deleted_count = 0
            return result
            
        async def count_documents(self, filter_dict=None):
            return len(self._storage)
            
        def aggregate(self, pipeline):
            # Simple aggregation simulation for statistics
            if not self._storage:
                return MockAsyncCursor([], self._storage)
                
            # Simulate common aggregation patterns
            jobs = list(self._storage.values())
            
            # Check for group by company aggregation
            for stage in pipeline:
                if "$group" in stage:
                    group_stage = stage["$group"]
                    if group_stage.get("_id") == "$company":
                        # Group by company
                        company_stats = {}
                        for job in jobs:
                            company = job.get("company", "Unknown")
                            if company not in company_stats:
                                company_stats[company] = {"_id": company, "count": 0}
                            company_stats[company]["count"] += 1
                        return MockAsyncCursor(list(company_stats.values()), self._storage)
                    
                    elif group_stage.get("_id") == "$location":
                        # Group by location
                        location_stats = {}
                        for job in jobs:
                            location = job.get("location", "Unknown")
                            if location not in location_stats:
                                location_stats[location] = {"_id": location, "count": 0}
                            location_stats[location]["count"] += 1
                        return MockAsyncCursor(list(location_stats.values()), self._storage)
            
            return MockAsyncCursor([], self._storage)
    
    # Jobs collection
    mock_db.jobs = MockCollection(_storage["jobs"])
    
    # Users collection
    mock_db.users = MockCollection(_storage["users"])
    
    # Companies collection
    mock_db.companies = MockCollection(_storage["companies"])
    
    # Database commands
    mock_db.command = AsyncMock(return_value={"ok": 1})
    
    return mock_db

# Database setup/teardown with proper async mocking
@pytest.fixture(autouse=True)
def setup_test_db(mock_database):
    """Mock the database for all tests with proper async support."""
    with patch('backend.database.get_db', return_value=mock_database):
        with patch('database.get_db', return_value=mock_database):
            with patch('backend.database.db', mock_database):
                with patch('database.db', mock_database):
                    # Also patch the async database getter
                    async def mock_get_async_db():
                        yield mock_database
                    
                    with patch('backend.database.get_async_db', mock_get_async_db):
                        with patch('database.get_async_db', mock_get_async_db):
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
            "created_at": "2024-01-01T00:00:00Z"
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
    mock_database.jobs.insert_one = AsyncMock(return_value=MagicMock(inserted_id="new_id"))
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
            "website": "https://techcorp.com"
        }
    ]
    
    # Create proper mock aggregation cursor
    mock_agg_cursor = AsyncMock()
    mock_agg_cursor.to_list = AsyncMock(return_value=sample_companies)
    
    # Set up companies collection mock
    mock_database.companies.aggregate = MagicMock(return_value=mock_agg_cursor)
    mock_database.companies.find = MagicMock(return_value=AsyncMock(to_list=AsyncMock(return_value=sample_companies)))
    mock_database.companies.count_documents = AsyncMock(return_value=len(sample_companies))
    
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
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client

@pytest.fixture
def mock_cv_file():
    """Mock CV file for testing file uploads."""
    return {
        "filename": "test_cv.pdf",
        "content": b"mock pdf content",
        "content_type": "application/pdf"
    }

# MongoDB collection fixtures for specific testing scenarios
@pytest.fixture
def mongodb(mock_database):
    """Provide mock MongoDB instance."""
    return {"jobs": mock_database.jobs, "users": mock_database.users, "companies": mock_database.companies}

@pytest.fixture
def mock_token():
    return "mock.jwt.token"

@pytest.fixture
def client_with_auth_header(client, mock_token):
    """Create a client with authentication headers."""
    client.headers.update({"Authorization": f"Bearer {mock_token}"})
    return client 