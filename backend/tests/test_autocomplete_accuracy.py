"""
Test autocomplete API endpoint for accuracy of job counts and duplicate prevention.
"""

import asyncio
import os
import sys
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from routes.jobs import search_job_titles


@pytest.mark.asyncio
async def test_autocomplete_basic_functionality():
    """Test basic autocomplete functionality with mock database"""

    # Mock database and collection
    mock_db = AsyncMock()
    mock_collection = AsyncMock()
    mock_db.jobs = mock_collection

    # Mock aggregation results
    mock_results = [
        {"title": "Software Engineer", "count": 3, "category": "Technology"},
        {"title": "Senior Software Engineer", "count": 1, "category": "Technology"},
        {"title": "Backend Developer", "count": 2, "category": "Technology"},
        {"title": "Frontend Developer", "count": 1, "category": "Technology"},
        {"title": "Data Scientist", "count": 2, "category": "Technology"},
    ]

    # Mock cursor
    mock_cursor = AsyncMock()
    mock_cursor.to_list.return_value = mock_results
    mock_collection.aggregate.return_value = mock_cursor

    # Test the function
    results = await search_job_titles(q="software", limit=10, db=mock_db)

    # Verify results
    assert len(results) > 0, "Should return some results"
    assert all(
        isinstance(r, dict) for r in results
    ), "All results should be dictionaries"
    assert all("title" in r for r in results), "All results should have title field"
    assert all("count" in r for r in results), "All results should have count field"


@pytest.mark.asyncio
async def test_autocomplete_no_duplicates():
    """Test that autocomplete doesn't return duplicate titles"""

    # Mock database
    mock_db = AsyncMock()
    mock_collection = AsyncMock()
    mock_db.jobs = mock_collection

    # Mock results with potential duplicates
    mock_results = [
        {"title": "Software Engineer", "count": 3, "category": "Technology"},
        {
            "title": "Software Engineer",
            "count": 2,
            "category": "Technology",
        },  # Duplicate
        {"title": "Backend Developer", "count": 2, "category": "Technology"},
        {"title": "Frontend Developer", "count": 1, "category": "Technology"},
    ]

    mock_cursor = AsyncMock()
    mock_cursor.to_list.return_value = mock_results
    mock_collection.aggregate.return_value = mock_cursor

    # Test the function
    results = await search_job_titles(q="developer", limit=10, db=mock_db)

    # Extract titles
    titles = [result["title"] for result in results]

    # Check for duplicates
    unique_titles = set(titles)
    assert len(titles) == len(unique_titles), f"Found duplicate titles: {titles}"


@pytest.mark.asyncio
async def test_autocomplete_empty_query():
    """Test autocomplete with empty query"""

    # Mock database
    mock_db = AsyncMock()
    mock_collection = AsyncMock()
    mock_db.jobs = mock_collection

    # Test with empty query
    results = await search_job_titles(q="", limit=10, db=mock_db)

    # Should return empty list for empty query
    assert results == [], "Empty query should return empty list"


@pytest.mark.asyncio
async def test_autocomplete_error_handling():
    """Test autocomplete error handling"""

    # Mock database that raises exception
    mock_db = AsyncMock()
    mock_collection = AsyncMock()
    mock_db.jobs = mock_collection

    # Mock collection to raise exception
    mock_collection.aggregate.side_effect = Exception("Database error")

    # Test the function - should handle error gracefully
    results = await search_job_titles(q="software", limit=10, db=mock_db)

    # Should return fallback results
    assert isinstance(results, list), "Should return list even on error"
    assert len(results) > 0, "Should return fallback results on error"


@pytest.mark.asyncio
async def test_autocomplete_limit_respect():
    """Test that autocomplete respects the limit parameter"""

    # Mock database
    mock_db = AsyncMock()
    mock_collection = AsyncMock()
    mock_db.jobs = mock_collection

    # Mock many results
    mock_results = [
        {"title": f"Job {i}", "count": 1, "category": "Technology"} for i in range(50)
    ]

    mock_cursor = AsyncMock()
    mock_cursor.to_list.return_value = mock_results
    mock_collection.aggregate.return_value = mock_cursor

    # Test with limit 5
    results = await search_job_titles(q="job", limit=5, db=mock_db)

    # Should respect limit
    assert len(results) <= 5, f"Should respect limit, got {len(results)} results"


if __name__ == "__main__":
    # Run tests manually for debugging
    async def run_tests():
        print("Running autocomplete accuracy tests...")

        # Test basic functionality
        print("\n1. Testing basic functionality...")
        await test_autocomplete_basic_functionality()
        print("✓ Basic functionality test passed")

        # Test no duplicates
        print("\n2. Testing no duplicates...")
        await test_autocomplete_no_duplicates()
        print("✓ No duplicates test passed")

        # Test empty query
        print("\n3. Testing empty query...")
        await test_autocomplete_empty_query()
        print("✓ Empty query test passed")

        # Test error handling
        print("\n4. Testing error handling...")
        await test_autocomplete_error_handling()
        print("✓ Error handling test passed")

        # Test limit respect
        print("\n5. Testing limit respect...")
        await test_autocomplete_limit_respect()
        print("✓ Limit respect test passed")

        print("\nAll tests completed successfully!")

    asyncio.run(run_tests())
