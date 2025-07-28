"""
Database Test Helper
Provides database testing utilities
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, UTC
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase

from backend.utils.objectid_helper import objectid_helper
from backend.utils.async_iterator_helper import async_iterator_helper

logger = logging.getLogger(__name__)


class DatabaseTestHelper:
    """Helper class for database testing"""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
    
    async def cleanup_collection(self, collection_name: str):
        """Clean up collection"""
        try:
            await self.db[collection_name].delete_many({})
            logger.info(f"Cleaned up collection: {collection_name}")
        except Exception as e:
            logger.error(f"Error cleaning up collection {collection_name}: {e}")
    
    async def cleanup_all_collections(self, collections: List[str]):
        """Clean up multiple collections"""
        for collection_name in collections:
            await self.cleanup_collection(collection_name)
    
    async def insert_test_data(self, collection_name: str, documents: List[Dict[str, Any]]) -> List[str]:
        """Insert test data into collection"""
        try:
            # Process documents
            processed_docs = []
            for doc in documents:
                if "_id" not in doc:
                    doc["_id"] = objectid_helper.create_objectid()
                elif isinstance(doc["_id"], str):
                    objectid = objectid_helper.to_objectid(doc["_id"])
                    if objectid:
                        doc["_id"] = objectid
                processed_docs.append(doc)
            
            result = await self.db[collection_name].insert_many(processed_docs)
            inserted_ids = [str(id) for id in result.inserted_ids]
            logger.info(f"Inserted {len(inserted_ids)} documents into {collection_name}")
            return inserted_ids
        except Exception as e:
            logger.error(f"Error inserting test data into {collection_name}: {e}")
            return []
    
    async def get_test_data(self, collection_name: str, query: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Get test data from collection"""
        try:
            if query is None:
                query = {}
            
            cursor = self.db[collection_name].find(query)
            documents = await async_iterator_helper.cursor_to_list(cursor)
            return objectid_helper.convert_list_objectids(documents)
        except Exception as e:
            logger.error(f"Error getting test data from {collection_name}: {e}")
            return []
    
    async def count_documents(self, collection_name: str, query: Dict[str, Any] = None) -> int:
        """Count documents in collection"""
        try:
            if query is None:
                query = {}
            
            return await self.db[collection_name].count_documents(query)
        except Exception as e:
            logger.error(f"Error counting documents in {collection_name}: {e}")
            return 0
    
    async def create_test_index(self, collection_name: str, keys: List[tuple], **kwargs) -> str:
        """Create test index"""
        try:
            return await self.db[collection_name].create_index(keys, **kwargs)
        except Exception as e:
            logger.error(f"Error creating index in {collection_name}: {e}")
            return ""
    
    async def drop_test_index(self, collection_name: str, index_name: str) -> bool:
        """Drop test index"""
        try:
            await self.db[collection_name].drop_index(index_name)
            return True
        except Exception as e:
            logger.error(f"Error dropping index in {collection_name}: {e}")
            return False


def get_test_job_data(job_id: str = None) -> Dict[str, Any]:
    """Get test job data"""
    return {
        "_id": job_id or str(objectid_helper.create_objectid()),
        "title": "Test Job",
        "company": "Test Company",
        "location": "Remote",
        "description": "Test job description",
        "salary_min": 50000,
        "salary_max": 80000,
        "job_type": "Full-time",
        "is_remote": True,
        "is_active": True,
        "created_at": datetime.now(UTC).isoformat(),
        "updated_at": datetime.now(UTC).isoformat()
    }


def get_test_user_data(user_id: str = None) -> Dict[str, Any]:
    """Get test user data"""
    return {
        "_id": user_id or str(objectid_helper.create_objectid()),
        "email": "test@example.com",
        "name": "Test User",
        "role": "user",
        "permissions": ["read", "write"],
        "is_active": True,
        "created_at": datetime.now(UTC).isoformat(),
        "updated_at": datetime.now(UTC).isoformat()
    }


def get_test_company_data(company_id: str = None) -> Dict[str, Any]:
    """Get test company data"""
    return {
        "_id": company_id or str(objectid_helper.create_objectid()),
        "name": "Test Company",
        "website": "https://testcompany.com",
        "description": "Test company description",
        "industry": "Technology",
        "size": "50-100",
        "is_active": True,
        "created_at": datetime.now(UTC).isoformat(),
        "updated_at": datetime.now(UTC).isoformat()
    }


def get_test_ad_data(ad_id: str = None) -> Dict[str, Any]:
    """Get test ad data"""
    return {
        "_id": ad_id or str(objectid_helper.create_objectid()),
        "title": "Test Advertisement",
        "description": "Test ad description",
        "company_id": str(objectid_helper.create_objectid()),
        "is_active": True,
        "start_date": datetime.now(UTC).isoformat(),
        "end_date": datetime.now(UTC).isoformat(),
        "created_at": datetime.now(UTC).isoformat(),
        "updated_at": datetime.now(UTC).isoformat()
    }


def get_multiple_test_jobs(count: int = 5) -> List[Dict[str, Any]]:
    """Get multiple test job data"""
    jobs = []
    for i in range(count):
        job = get_test_job_data()
        job["title"] = f"Test Job {i+1}"
        job["company"] = f"Test Company {i+1}"
        jobs.append(job)
    return jobs


def get_multiple_test_users(count: int = 3) -> List[Dict[str, Any]]:
    """Get multiple test user data"""
    users = []
    for i in range(count):
        user = get_test_user_data()
        user["email"] = f"test{i+1}@example.com"
        user["name"] = f"Test User {i+1}"
        users.append(user)
    return users


def get_multiple_test_companies(count: int = 3) -> List[Dict[str, Any]]:
    """Get multiple test company data"""
    companies = []
    for i in range(count):
        company = get_test_company_data()
        company["name"] = f"Test Company {i+1}"
        company["website"] = f"https://testcompany{i+1}.com"
        companies.append(company)
    return companies


async def setup_test_database(db: AsyncIOMotorDatabase):
    """Setup test database with sample data"""
    helper = DatabaseTestHelper(db)
    
    # Clean up existing data
    collections = ["jobs", "users", "companies", "ads", "applications"]
    await helper.cleanup_all_collections(collections)
    
    # Insert test data
    test_jobs = get_multiple_test_jobs(10)
    test_users = get_multiple_test_users(5)
    test_companies = get_multiple_test_companies(3)
    test_ads = [get_test_ad_data() for _ in range(5)]
    
    await helper.insert_test_data("jobs", test_jobs)
    await helper.insert_test_data("users", test_users)
    await helper.insert_test_data("companies", test_companies)
    await helper.insert_test_data("ads", test_ads)
    
    logger.info("Test database setup completed")


async def cleanup_test_database(db: AsyncIOMotorDatabase):
    """Clean up test database"""
    helper = DatabaseTestHelper(db)
    
    collections = ["jobs", "users", "companies", "ads", "applications"]
    await helper.cleanup_all_collections(collections)
    
    logger.info("Test database cleanup completed")


def assert_document_structure(document: Dict[str, Any], required_fields: List[str]):
    """Assert document has required fields"""
    for field in required_fields:
        assert field in document, f"Missing required field: {field}"


def assert_objectid_field(document: Dict[str, Any], field_name: str):
    """Assert field is valid ObjectId string"""
    assert field_name in document, f"Missing field: {field_name}"
    assert objectid_helper.is_valid_objectid(document[field_name]), f"Invalid ObjectId in field: {field_name}"


def assert_datetime_field(document: Dict[str, Any], field_name: str):
    """Assert field is valid datetime string"""
    assert field_name in document, f"Missing field: {field_name}"
    try:
        datetime.fromisoformat(document[field_name].replace('Z', '+00:00'))
    except ValueError:
        assert False, f"Invalid datetime in field: {field_name}"


def assert_pagination_response(response_data: Dict[str, Any]):
    """Assert pagination response structure"""
    required_fields = ["items", "total", "page", "size", "pages"]
    for field in required_fields:
        assert field in response_data, f"Missing pagination field: {field}"
    
    assert isinstance(response_data["items"], list), "Items should be a list"
    assert isinstance(response_data["total"], int), "Total should be an integer"
    assert isinstance(response_data["page"], int), "Page should be an integer"
    assert isinstance(response_data["size"], int), "Size should be an integer"
    assert isinstance(response_data["pages"], int), "Pages should be an integer" 