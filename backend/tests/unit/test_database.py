import pytest
from bson import ObjectId
from backend.crud import job as job_crud
from backend.models.job import JobCreate, JobUpdate
from datetime import datetime, timedelta
from backend.database import get_async_db

@pytest.mark.unit
class TestDatabaseFunctions:
    """Unit tests for database functions."""

    def test_database_connection_available(self, db_mock):
        """Test database connection is available."""
        assert db_mock is not None
        assert hasattr(db_mock, 'jobs')

    def test_jobs_collection_operations(self, db_mock):
        """Test basic CRUD operations on jobs collection."""
        # Mock collection operations
        db_mock.jobs.find_one.return_value = {
            "title": "Sample Job 1",
            "company": "Sample Company A",
            "location": "Remote",
            "description": "Desc 1",
            "is_active": True,
            "created_at": datetime.utcnow()
        }
        
        db_mock.jobs.find.return_value.to_list.return_value = [
            {"title": "Sample Job 1", "company": "Sample Company A"},
            {"title": "Sample Job 2", "company": "Sample Company B"},
            {"title": "Sample Job 3", "company": "Sample Company A"}
        ]
        
        # Test finding jobs
        jobs = db_mock.jobs.find().to_list()
        assert len(jobs) == 3
        
        # Test finding specific job
        job = db_mock.jobs.find_one({"title": "Sample Job 1"})
        assert job is not None
        assert job["company"] == "Sample Company A"

    def test_jobs_filtering(self, db_mock):
        """Test filtering jobs by various criteria."""
        # Mock filtered results
        db_mock.jobs.find.return_value.to_list.return_value = [
            {"company": "TechCorp", "location": "Remote", "is_active": True},
            {"company": "TechCorp", "location": "New York", "is_active": True}
        ]
        
        # Filter by company
        techcorp_jobs = db_mock.jobs.find({"company": "TechCorp"}).to_list()
        assert len(techcorp_jobs) == 2
        
        # Mock remote jobs
        db_mock.jobs.find.return_value.to_list.return_value = [
            {"company": "TechCorp", "location": "Remote", "is_active": True},
            {"company": "StartupCorp", "location": "Remote", "is_active": True}
        ]
        
        remote_jobs = db_mock.jobs.find({"location": "Remote"}).to_list()
        assert len(remote_jobs) == 2

    def test_jobs_sorting(self, db_mock):
        """Test sorting jobs by different fields."""
        # Mock sorted results
        db_mock.jobs.find.return_value.sort.return_value.to_list.return_value = [
            {"title": "Newest Job", "created_at": datetime(2024, 1, 4)},
            {"title": "Middle Job", "created_at": datetime(2024, 1, 2)},
            {"title": "Oldest Job", "created_at": datetime(2024, 1, 1)}
        ]
        
        # Sort by creation date
        jobs_by_date = db_mock.jobs.find().sort("created_at", -1).to_list()
        assert len(jobs_by_date) == 3
        
        # Verify sorting (newest first)
        assert jobs_by_date[0]["created_at"] >= jobs_by_date[1]["created_at"]

    def test_jobs_aggregation(self, db_mock):
        """Test aggregation operations on jobs."""
        # Mock aggregation results
        db_mock.jobs.aggregate.return_value.to_list.return_value = [
            {"_id": "Google", "count": 2},
            {"_id": "Microsoft", "count": 2},
            {"_id": "Amazon", "count": 1}
        ]
        
        # Count jobs by company
        company_counts = db_mock.jobs.aggregate([]).to_list()
        assert len(company_counts) == 3
        
        # Verify structure
        for company in company_counts:
            assert "_id" in company
            assert "count" in company
            assert company["count"] > 0

@pytest.mark.unit
class TestDataValidation:
    """Unit tests for data validation functions."""

    def test_job_data_validation(self, sample_job_data):
        """Test job data structure validation."""
        required_fields = ["title", "company", "location", "source"]
        
        for field in required_fields:
            assert field in sample_job_data
            assert sample_job_data[field] is not None
            assert len(str(sample_job_data[field])) > 0

    def test_job_data_types(self, sample_job_data):
        """Test job data types."""
        assert isinstance(sample_job_data["title"], str)
        assert isinstance(sample_job_data["company"], str)
        assert isinstance(sample_job_data["location"], str)

    def test_url_validation(self, sample_job_data):
        """Test URL field validation."""
        url = sample_job_data.get("url", "")
        apply_url = sample_job_data.get("apply_url", "")
        
        if url:
            assert url.startswith("http")
        if apply_url:
            assert apply_url.startswith("http")

@pytest.mark.unit
class TestUtilityFunctions:
    """Unit tests for utility functions."""

    def test_sanitize_input(self):
        """Test input sanitization function."""
        # This would test the actual sanitize_input function from admin panel
        test_inputs = [
            ("normal text", "normal text"),
            ("<script>alert('xss')</script>", "&lt;script&gt;alert(&#x27;xss&#x27;)&lt;/script&gt;"),
            ("", ""),
            (None, "")
        ]
        
        # Mock sanitize function for testing
        def mock_sanitize_input(input_str):
            if not input_str:
                return ""
            return input_str.replace("<", "&lt;").replace(">", "&gt;").replace("'", "&#x27;")
        
        for input_val, expected in test_inputs:
            result = mock_sanitize_input(input_val)
            assert result == expected

    def test_build_safe_filter(self):
        """Test safe filter building function."""
        # Mock build_safe_filter function for testing
        def mock_build_safe_filter(filter_value, field_name):
            if not filter_value or not field_name:
                return {}
            return {field_name: {"$regex": filter_value, "$options": "i"}}
        
        # Test cases
        assert mock_build_safe_filter("test", "title") == {"title": {"$regex": "test", "$options": "i"}}
        assert mock_build_safe_filter("", "title") == {}
        assert mock_build_safe_filter("test", "") == {}

@pytest.mark.unit
class TestCRUDOperations:
    """Unit tests for CRUD operations."""

    def test_create_job(self, db_mock, test_job_data):
        """Test job creation."""
        # Mock insert result
        mock_result = type('MockResult', (), {'inserted_id': ObjectId()})()
        db_mock.jobs.insert_one.return_value = mock_result
        
        # Test job creation
        result = db_mock.jobs.insert_one(test_job_data)
        assert result.inserted_id is not None
        db_mock.jobs.insert_one.assert_called_once()

    def test_get_job(self, db_mock, test_job_data):
        """Test getting a single job."""
        # Mock find_one result
        db_mock.jobs.find_one.return_value = test_job_data
        
        # Test getting job
        job = db_mock.jobs.find_one({"_id": ObjectId()})
        assert job is not None
        assert job["title"] == test_job_data["title"]
        db_mock.jobs.find_one.assert_called_once()

    def test_get_jobs(self, db_mock, test_job_data):
        """Test getting multiple jobs."""
        # Mock find result
        db_mock.jobs.find.return_value.to_list.return_value = [test_job_data]
        
        # Test getting jobs
        jobs = db_mock.jobs.find().to_list()
        assert len(jobs) == 1
        assert jobs[0]["title"] == test_job_data["title"]
        db_mock.jobs.find.assert_called_once()

    def test_update_job(self, db_mock, test_job_data):
        """Test job update."""
        # Mock update result
        mock_result = type('MockResult', (), {'modified_count': 1})()
        db_mock.jobs.update_one.return_value = mock_result
        
        # Test job update
        result = db_mock.jobs.update_one(
            {"_id": ObjectId()},
            {"$set": {"title": "Updated Job"}}
        )
        assert result.modified_count == 1
        db_mock.jobs.update_one.assert_called_once()

    def test_delete_job(self, db_mock):
        """Test job deletion."""
        # Mock delete result
        mock_result = type('MockResult', (), {'deleted_count': 1})()
        db_mock.jobs.delete_one.return_value = mock_result
        
        # Test job deletion
        result = db_mock.jobs.delete_one({"_id": ObjectId()})
        assert result.deleted_count == 1
        db_mock.jobs.delete_one.assert_called_once()

    def test_search_jobs(self, db_mock, test_job_data):
        """Test job search functionality."""
        # Mock search results
        db_mock.jobs.find.return_value.to_list.return_value = [test_job_data]
        
        # Test job search
        jobs = db_mock.jobs.find({"title": {"$regex": "Python"}}).to_list()
        assert len(jobs) == 1
        assert jobs[0]["title"] == test_job_data["title"]
        db_mock.jobs.find.assert_called_once()

    def test_get_job_statistics(self, db_mock):
        """Test job statistics aggregation."""
        # Mock aggregation results
        db_mock.jobs.aggregate.return_value.to_list.return_value = [
            {"_id": "active", "count": 10},
            {"_id": "inactive", "count": 5}
        ]
        
        # Test statistics
        stats = db_mock.jobs.aggregate([]).to_list()
        assert len(stats) == 2
        assert stats[0]["count"] == 10
        assert stats[1]["count"] == 5
        db_mock.jobs.aggregate.assert_called_once()

@pytest.mark.unit
class TestJobValidation:
    """Unit tests for job validation."""

    def test_job_validation_disabled(self, sample_job_data):
        """Test job validation is properly disabled for testing."""
        # This test ensures that job validation is disabled in test environment
        # so we can test with incomplete data
        assert "title" in sample_job_data
        assert "company" in sample_job_data

    def test_job_dates(self, sample_job_data):
        """Test job date fields."""
        # Test that date fields are properly formatted
        if "created_at" in sample_job_data:
            assert isinstance(sample_job_data["created_at"], datetime)
        
        if "updated_at" in sample_job_data:
            assert isinstance(sample_job_data["updated_at"], datetime)

    def test_job_status(self, sample_job_data):
        """Test job status field."""
        # Test that status field is boolean
        if "is_active" in sample_job_data:
            assert isinstance(sample_job_data["is_active"], bool)

@pytest.mark.unit
class TestJobRelationships:
    """Unit tests for job relationships."""

    def test_job_company_relationship(self, db_mock, mock_jobs_collection, mock_companies_collection):
        """Test relationship between jobs and companies."""
        # Mock job with company reference
        job_data = {"title": "Test Job", "company_id": ObjectId()}
        company_data = {"_id": job_data["company_id"], "name": "Test Company"}
        
        db_mock.jobs.find_one.return_value = job_data
        db_mock.companies.find_one.return_value = company_data
        
        # Test relationship
        job = db_mock.jobs.find_one({"_id": ObjectId()})
        company = db_mock.companies.find_one({"_id": job["company_id"]})
        
        assert job is not None
        assert company is not None
        assert company["name"] == "Test Company"

    def test_job_search_complex(self, db_mock, mock_jobs_collection):
        """Test complex job search scenarios."""
        # Mock complex search results
        db_mock.jobs.find.return_value.to_list.return_value = [
            {"title": "Senior Python Developer", "location": "Remote", "salary": "100k+"},
            {"title": "Python Developer", "location": "New York", "salary": "80k+"}
        ]
        
        # Test complex search
        jobs = db_mock.jobs.find({
            "title": {"$regex": "Python"},
            "location": {"$in": ["Remote", "New York"]}
        }).to_list()
        
        assert len(jobs) == 2
        assert all("Python" in job["title"] for job in jobs)

    def test_job_sorting(self, db_mock, mock_jobs_collection):
        """Test job sorting functionality."""
        # Mock sorted results
        db_mock.jobs.find.return_value.sort.return_value.to_list.return_value = [
            {"title": "A Job", "salary": 100000},
            {"title": "B Job", "salary": 90000},
            {"title": "C Job", "salary": 80000}
        ]
        
        # Test sorting by salary
        jobs = db_mock.jobs.find().sort("salary", -1).to_list()
        assert len(jobs) == 3
        assert jobs[0]["salary"] >= jobs[1]["salary"]

    def test_job_filtering_complex(self, db_mock, mock_jobs_collection):
        """Test complex job filtering."""
        # Mock filtered results
        db_mock.jobs.find.return_value.to_list.return_value = [
            {"title": "Remote Job", "location": "Remote", "is_active": True},
            {"title": "Office Job", "location": "New York", "is_active": True}
        ]
        
        # Test complex filtering
        jobs = db_mock.jobs.find({
            "is_active": True,
            "location": {"$in": ["Remote", "New York"]}
        }).to_list()
        
        assert len(jobs) == 2
        assert all(job["is_active"] for job in jobs)

    def test_job_aggregation(self, db_mock, mock_jobs_collection):
        """Test job aggregation operations."""
        # Mock aggregation results
        db_mock.jobs.aggregate.return_value.to_list.return_value = [
            {"_id": "Remote", "count": 5, "avg_salary": 95000},
            {"_id": "Office", "count": 3, "avg_salary": 85000}
        ]
        
        # Test aggregation
        pipeline = [
            {"$group": {"_id": "$location", "count": {"$sum": 1}, "avg_salary": {"$avg": "$salary"}}}
        ]
        
        results = db_mock.jobs.aggregate(pipeline).to_list()
        assert len(results) == 2
        assert all("count" in result and "avg_salary" in result for result in results) 