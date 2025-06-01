import pytest
from httpx import AsyncClient
from backend.models.job import JobCreate
from bson import ObjectId

@pytest.mark.asyncio
async def test_create_job(async_client: AsyncClient, test_job_data: dict, mongodb):
    """Test creating a job via API."""
    await mongodb["jobs"].delete_many({})

    response = await async_client.post("/api/jobs/", json=test_job_data)
    assert response.status_code == 201
    data = response.json()
    assert "_id" in data
    assert data["title"] == test_job_data["title"]
    assert data["company"] == test_job_data["company"]

@pytest.mark.asyncio
async def test_get_jobs(async_client: AsyncClient, test_job_data: dict, mongodb):
    """Test getting a list of jobs via API."""
    await mongodb["jobs"].delete_many({})
    job = JobCreate(**test_job_data)
    await async_client.post("/api/jobs/", json=job.model_dump())
    
    response = await async_client.get("/api/jobs/")
    assert response.status_code == 200
    data = response.json()
    assert "jobs" in data
    assert "total" in data
    assert "page" in data
    assert "per_page" in data
    assert "total_pages" in data
    assert len(data["jobs"]) > 0
    assert "_id" in data["jobs"][0]

@pytest.mark.asyncio
async def test_get_job(async_client: AsyncClient, test_job_data: dict, mongodb):
    """Test getting a specific job via API."""
    await mongodb["jobs"].delete_many({})
    job = JobCreate(**test_job_data)
    create_response = await async_client.post("/api/jobs/", json=job.model_dump())
    job_id = create_response.json()["_id"]
    
    response = await async_client.get(f"/api/jobs/{job_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["_id"] == job_id
    assert data["title"] == test_job_data["title"]
    assert data["company"] == test_job_data["company"]

@pytest.mark.asyncio
async def test_update_job(async_client: AsyncClient, test_job_data: dict, mongodb):
    """Test updating a job via API."""
    await mongodb["jobs"].delete_many({})
    job = JobCreate(**test_job_data)
    create_response = await async_client.post("/api/jobs/", json=job.model_dump())
    job_id = create_response.json()["_id"]
    
    update_data = {"title": "Updated Job Title"}
    response = await async_client.put(f"/api/jobs/{job_id}", json=update_data)
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Updated Job Title"
    assert data["_id"] == job_id

@pytest.mark.asyncio
async def test_delete_job(async_client: AsyncClient, test_job_data: dict, mongodb):
    """Test deleting a job via API."""
    await mongodb["jobs"].delete_many({})
    job = JobCreate(**test_job_data)
    create_response = await async_client.post("/api/jobs/", json=job.model_dump())
    job_id = create_response.json()["_id"]
    
    response = await async_client.delete(f"/api/jobs/{job_id}")
    assert response.status_code == 204
    
    get_response = await async_client.get(f"/api/jobs/{job_id}")
    assert get_response.status_code == 404

@pytest.mark.asyncio
async def test_search_jobs(async_client: AsyncClient, test_job_data: dict, mongodb):
    """Test searching jobs via API."""
    await mongodb["jobs"].delete_many({})
    job = JobCreate(**test_job_data)
    await async_client.post("/api/jobs/", json=job.model_dump())
    
    response = await async_client.get("/api/jobs/search", params={"q": "Test"})
    assert response.status_code == 200
    data = response.json()
    assert "jobs" in data
    assert len(data["jobs"]) > 0
    assert any("Test" in job["title"] for job in data["jobs"])
    assert "_id" in data["jobs"][0]

@pytest.mark.asyncio
async def test_get_job_statistics(async_client: AsyncClient, test_job_data: dict, mongodb):
    """Test getting job statistics via API."""
    await mongodb["jobs"].delete_many({})
    companies = ["Company A", "Company B", "Company C"]
    locations = ["Remote", "New York", "London"]
    
    for company in companies:
        for location in locations:
            job_data = test_job_data.copy()
            job_data["company"] = company
            job_data["location"] = location
            job = JobCreate(**job_data)
            await async_client.post("/api/jobs/", json=job.model_dump())
    
    response = await async_client.get("/api/jobs/statistics")
    assert response.status_code == 200
    data = response.json()
    assert "total_jobs" in data
    assert "jobs_by_company" in data
    assert "jobs_by_location" in data
    assert len(data["jobs_by_company"]) >= len(companies)
    assert len(data["jobs_by_location"]) >= len(locations) 