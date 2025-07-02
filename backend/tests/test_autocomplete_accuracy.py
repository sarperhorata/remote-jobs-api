"""
Test autocomplete API endpoint for accuracy of job counts and duplicate prevention.
"""
import pytest
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from routes.jobs import search_job_titles
from fastapi import Request
from unittest.mock import AsyncMock, MagicMock
import logging

# Test configuration
TEST_DB_URL = "mongodb://localhost:27017"
TEST_DB_NAME = "buzz2remote_test"

@pytest.fixture
async def test_db():
    """Create test database connection"""
    client = AsyncIOMotorClient(TEST_DB_URL)
    db = client[TEST_DB_NAME]
    
    # Clean up existing test data
    await db.jobs.delete_many({})
    
    # Insert test data with known duplicates and counts
    test_jobs = [
        {"title": "Software Engineer", "company": "Company A", "location": "Remote"},
        {"title": "Software Engineer", "company": "Company B", "location": "New York"},
        {"title": "software engineer", "company": "Company C", "location": "SF"},  # Duplicate with different case
        {"title": "Senior Software Engineer", "company": "Company D", "location": "Remote"},
        {"title": "Backend Developer", "company": "Company E", "location": "Remote"},
        {"title": "Backend Developer", "company": "Company F", "location": "Boston"},
        {"title": "Frontend Developer", "company": "Company G", "location": "Remote"},
        {"title": "Data Scientist", "company": "Company H", "location": "Remote"},
        {"title": "Data Scientist", "company": "Company I", "location": "Seattle"},
        {"title": "DevOps Engineer", "company": "Company J", "location": "Remote"},
    ]
    
    await db.jobs.insert_many(test_jobs)
    
    yield db
    
    # Cleanup
    await db.jobs.delete_many({})
    client.close()

@pytest.mark.asyncio
async def test_autocomplete_job_counts(test_db):
    """Test that autocomplete returns correct job counts"""
    
    # Test Software Engineer count (should be 3: Software Engineer + software engineer are same)
    results = await search_job_titles(q="software", limit=10, db=test_db)
    
    software_engineer_result = None
    for result in results:
        if result['title'].lower().replace(' ', '') == 'softwareengineer':
            software_engineer_result = result
            break
    
    assert software_engineer_result is not None, "Software Engineer should be found"
    assert software_engineer_result['count'] == 3, f"Expected 3 Software Engineer jobs, got {software_engineer_result['count']}"

@pytest.mark.asyncio
async def test_autocomplete_no_duplicates(test_db):
    """Test that autocomplete doesn't return duplicate titles"""
    
    results = await search_job_titles(q="developer", limit=10, db=test_db)
    
    # Extract normalized titles
    normalized_titles = []
    for result in results:
        normalized = ' '.join(result['title'].lower().strip().split())
        normalized_titles.append(normalized)
    
    # Check for duplicates
    unique_titles = set(normalized_titles)
    assert len(normalized_titles) == len(unique_titles), f"Found duplicate titles: {normalized_titles}"

@pytest.mark.asyncio
async def test_autocomplete_backend_developer_count(test_db):
    """Test Backend Developer count specifically"""
    
    results = await search_job_titles(q="backend", limit=10, db=test_db)
    
    backend_dev_result = None
    for result in results:
        if 'backend' in result['title'].lower() and 'developer' in result['title'].lower():
            backend_dev_result = result
            break
    
    assert backend_dev_result is not None, "Backend Developer should be found"
    assert backend_dev_result['count'] == 2, f"Expected 2 Backend Developer jobs, got {backend_dev_result['count']}"

@pytest.mark.asyncio
async def test_autocomplete_data_scientist_count(test_db):
    """Test Data Scientist count"""
    
    results = await search_job_titles(q="data", limit=10, db=test_db)
    
    data_scientist_result = None
    for result in results:
        if 'data scientist' in result['title'].lower():
            data_scientist_result = result
            break
    
    assert data_scientist_result is not None, "Data Scientist should be found"
    assert data_scientist_result['count'] == 2, f"Expected 2 Data Scientist jobs, got {data_scientist_result['count']}"

@pytest.mark.asyncio
async def test_autocomplete_case_insensitive_deduplication(test_db):
    """Test that different cases of same title are properly deduplicated"""
    
    results = await search_job_titles(q="software engineer", limit=10, db=test_db)
    
    # Should find only one "Software Engineer" entry, not separate entries for different cases
    software_engineer_results = [
        r for r in results 
        if 'software' in r['title'].lower() and 'engineer' in r['title'].lower() and 'senior' not in r['title'].lower()
    ]
    
    assert len(software_engineer_results) == 1, f"Expected 1 Software Engineer result, got {len(software_engineer_results)}"
    assert software_engineer_results[0]['count'] == 3, f"Expected count 3, got {software_engineer_results[0]['count']}"

if __name__ == "__main__":
    # Run tests manually for debugging
    async def run_tests():
        print("Running autocomplete accuracy tests...")
        
        # Setup test database
        client = AsyncIOMotorClient(TEST_DB_URL)
        db = client[TEST_DB_NAME]
        
        # Clean up existing test data
        await db.jobs.delete_many({})
        
        # Insert test data
        test_jobs = [
            {"title": "Software Engineer", "company": "Company A", "location": "Remote"},
            {"title": "Software Engineer", "company": "Company B", "location": "New York"},
            {"title": "software engineer", "company": "Company C", "location": "SF"},
            {"title": "Senior Software Engineer", "company": "Company D", "location": "Remote"},
            {"title": "Backend Developer", "company": "Company E", "location": "Remote"},
            {"title": "Backend Developer", "company": "Company F", "location": "Boston"},
            {"title": "Frontend Developer", "company": "Company G", "location": "Remote"},
            {"title": "Data Scientist", "company": "Company H", "location": "Remote"},
            {"title": "Data Scientist", "company": "Company I", "location": "Seattle"},
            {"title": "DevOps Engineer", "company": "Company J", "location": "Remote"},
        ]
        
        await db.jobs.insert_many(test_jobs)
        
        # Test autocomplete
        print("\n1. Testing Software Engineer count...")
        results = await search_job_titles(q="software", limit=10, db=db)
        print(f"Results for 'software': {results}")
        
        print("\n2. Testing Backend Developer count...")
        results = await search_job_titles(q="backend", limit=10, db=db)
        print(f"Results for 'backend': {results}")
        
        print("\n3. Testing no duplicates...")
        results = await search_job_titles(q="developer", limit=10, db=db)
        print(f"Results for 'developer': {results}")
        
        # Cleanup
        await db.jobs.delete_many({})
        client.close()
        
        print("\nTests completed!")
    
    asyncio.run(run_tests()) 