import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock
import os

import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from backend.main import app

client = TestClient(app)

@pytest.mark.asyncio
async def test_get_unknown_company_stats():
    """Test the endpoint for getting unknown company stats."""
    
    mock_db = {
        "jobs": MagicMock()
    }
    mock_db["jobs"].count_documents = AsyncMock(side_effect=[5, 2, 1, 0]) # unknown, empty, null, missing
    mock_db["jobs"].find.return_value.limit.return_value.to_list = AsyncMock(return_value=[
        {"_id": "1", "title": "Job 1", "url": "http://example.com/1", "company": "Unknown Company"},
        {"_id": "2", "title": "Job 2", "url": "http://example.com/2", "company": ""},
    ])

    with patch('backend.routes.admin_cleanup.get_db', new=AsyncMock(return_value=mock_db)):
        response = client.get("/api/v1/admin/stats/unknown-company")
        
    assert response.status_code == 200
    data = response.json()
    assert data["stats"]["total"] == 8
    assert data["stats"]["unknown_company"] == 5
    assert len(data["samples"]) == 2

@pytest.mark.asyncio
async def test_cleanup_unknown_company_endpoint():
    """Test the endpoint for cleaning up unknown company jobs."""
    
    mock_db = {
        "jobs": MagicMock()
    }
    mock_db["jobs"].count_documents = AsyncMock(return_value=1)
    mock_db["jobs"].find.return_value.limit.return_value.to_list = AsyncMock(return_value=[
        {"_id": "1", "title": "Software Engineer at Awesome Inc", "url": "http://greenhouse.io/boards/coolcompany", "company": "Unknown Company"}
    ])
    mock_db["jobs"].update_one = AsyncMock()

    with patch('backend.routes.admin_cleanup.get_db', new=AsyncMock(return_value=mock_db)):
        response = client.post("/api/v1/admin/cleanup/unknown-company")
        
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["updated"] == 1
    
    # Check that update was called with the correct new company name
    update_call_args = mock_db["jobs"].update_one.call_args
    assert update_call_args is not None
    assert update_call_args[0][1]["$set"]["company"] == "Coolcompany" # From greenhouse URL 