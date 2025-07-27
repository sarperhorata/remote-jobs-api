from datetime import datetime

import pytest
from bson import ObjectId
from models.job import (JobBase, JobCreate, JobListResponse, JobResponse,
                        JobUpdate, PyObjectId)
from pydantic import ValidationError


class TestPyObjectId:
    """PyObjectId wrapper testleri"""

    def test_valid_objectid_string(self):
        """Geçerli ObjectId string testi"""
        valid_id = "507f1f77bcf86cd799439011"
        py_obj_id = PyObjectId.validate(valid_id)
        assert isinstance(py_obj_id, ObjectId)
        assert str(py_obj_id) == valid_id

    def test_invalid_objectid_string(self):
        """Geçersiz ObjectId string testi"""
        invalid_id = "invalid_objectid"
        with pytest.raises(ValueError, match="Invalid ObjectId"):
            PyObjectId.validate(invalid_id)

    def test_objectid_instance(self):
        """ObjectId instance testi"""
        obj_id = ObjectId()
        py_obj_id = PyObjectId.validate(str(obj_id))
        assert isinstance(py_obj_id, ObjectId)

    def test_serialization(self):
        """Serialization testi"""
        obj_id = ObjectId()
        py_obj_id = PyObjectId(obj_id)
        assert str(py_obj_id) == str(obj_id)


class TestJobBase:
    """JobBase model testleri"""

    @pytest.fixture
    def valid_job_data(self):
        """Geçerli job verisi"""
        return {
            "title": "Python Developer",
            "company": "TechCorp",
            "location": "San Francisco, CA",
            "description": "Looking for a Python developer",
            "requirements": "Python, Django, PostgreSQL",
            "salary_range": "$80,000 - $120,000",
            "job_type": "Full-time",
            "experience_level": "Mid-level",
            "apply_url": "https://example.com/apply",
        }

    def test_job_base_creation(self, valid_job_data):
        """JobBase oluşturma testi"""
        job = JobBase(**valid_job_data)

        assert job.title == "Python Developer"
        assert job.company == "TechCorp"
        assert job.location == "San Francisco, CA"
        assert job.job_type == "Full-time"
        assert job.apply_url == "https://example.com/apply"

    def test_job_base_with_optional_fields(self, valid_job_data):
        """Opsiyonel alanlarla JobBase testi"""
        job_data = valid_job_data.copy()
        job_data.update(
            {
                "remote_type": "Remote",
                "benefits": ["Health Insurance", "401k"],
                "skills": ["Python", "Django", "PostgreSQL"],
                "application_deadline": datetime(2025, 12, 31),
            }
        )

        job = JobBase(**job_data)

        assert job.remote_type == "Remote"
        assert job.benefits == ["Health Insurance", "401k"]
        assert job.skills == ["Python", "Django", "PostgreSQL"]
        assert job.application_deadline == datetime(2025, 12, 31)

    def test_job_base_missing_required_field(self, valid_job_data):
        """Zorunlu alan eksik testi"""
        del valid_job_data["title"]

        with pytest.raises(ValidationError) as exc_info:
            JobBase(**valid_job_data)

        assert "title" in str(exc_info.value)

    def test_job_base_serialization(self, valid_job_data):
        """Serialization testi"""
        job = JobBase(**valid_job_data)
        serialized = job.model_dump()

        assert isinstance(serialized, dict)
        assert serialized["title"] == "Python Developer"
        assert serialized["company"] == "TechCorp"


class TestJobCreate:
    """JobCreate model testleri"""

    def test_job_create_without_timestamps(self):
        """Timestamp olmadan JobCreate testi"""
        job_data = {
            "title": "Backend Developer",
            "company": "StartupInc",
            "location": "Remote",
            "description": "Backend role",
            "requirements": "Python, FastAPI",
            "salary_range": "$70,000 - $100,000",
            "job_type": "Full-time",
            "experience_level": "Senior",
            "apply_url": "https://startup.com/apply",
        }

        job = JobCreate(**job_data)

        assert job.created_at is None
        assert job.updated_at is None
        assert job.title == "Backend Developer"

    def test_job_create_with_timestamps(self):
        """Timestamp ile JobCreate testi"""
        now = datetime.utcnow()
        job_data = {
            "title": "Frontend Developer",
            "company": "WebCorp",
            "location": "New York",
            "description": "React developer needed",
            "requirements": "React, TypeScript",
            "salary_range": "$60,000 - $90,000",
            "job_type": "Contract",
            "experience_level": "Junior",
            "apply_url": "https://webcorp.com/jobs",
            "created_at": now,
            "updated_at": now,
        }

        job = JobCreate(**job_data)

        assert job.created_at == now
        assert job.updated_at == now


class TestJobUpdate:
    """JobUpdate model testleri"""

    def test_job_update_partial(self):
        """Kısmi güncelleme testi"""
        update_data = {
            "title": "Senior Python Developer",
            "salary_range": "$100,000 - $150,000",
            "is_active": False,
        }

        job_update = JobUpdate(**update_data)

        assert job_update.title == "Senior Python Developer"
        assert job_update.salary_range == "$100,000 - $150,000"
        assert job_update.is_active is False
        # Diğer alanlar None olmalı
        assert job_update.company is None
        assert job_update.location is None

    def test_job_update_empty(self):
        """Boş güncelleme testi"""
        job_update = JobUpdate()

        # Tüm alanlar None olmalı
        assert job_update.title is None
        assert job_update.company is None
        assert job_update.is_active is None

    def test_job_update_with_lists(self):
        """Liste alanları ile güncelleme testi"""
        update_data = {
            "benefits": ["Remote Work", "Flexible Hours"],
            "skills": ["Python", "FastAPI", "MongoDB"],
            "remote_type": "Hybrid",
        }

        job_update = JobUpdate(**update_data)

        assert job_update.benefits == ["Remote Work", "Flexible Hours"]
        assert job_update.skills == ["Python", "FastAPI", "MongoDB"]
        assert job_update.remote_type == "Hybrid"


class TestJobResponse:
    """JobResponse model testleri"""

    @pytest.fixture
    def job_response_data(self):
        """JobResponse test verisi"""
        return {
            "title": "DevOps Engineer",
            "company": "CloudTech",
            "location": "Austin, TX",
            "description": "DevOps role with AWS",
            "requirements": "AWS, Docker, Kubernetes",
            "salary_range": "$90,000 - $130,000",
            "job_type": "Full-time",
            "experience_level": "Senior",
            "apply_url": "https://cloudtech.com/careers",
        }

    def test_job_response_creation(self, job_response_data):
        """JobResponse oluşturma testi"""
        job = JobResponse(**job_response_data)

        assert job.title == "DevOps Engineer"
        assert job.is_active is True  # Default value
        assert job.views_count == 0  # Default value
        assert job.applications_count == 0  # Default value
        assert isinstance(job.created_at, datetime)
        assert isinstance(job.updated_at, datetime)
        assert hasattr(job, "id")  # PyObjectId field

    def test_job_response_with_custom_values(self, job_response_data):
        """Özel değerlerle JobResponse testi"""
        custom_id = ObjectId()
        now = datetime.utcnow()

        job_response_data.update(
            {
                "_id": custom_id,
                "is_active": False,
                "created_at": now,
                "updated_at": now,
                "views_count": 100,
                "applications_count": 25,
            }
        )

        job = JobResponse(**job_response_data)

        assert str(job.id) == str(custom_id)
        assert job.is_active is False
        assert job.views_count == 100
        assert job.applications_count == 25
        assert job.created_at == now

    def test_job_response_serialization(self, job_response_data):
        """JobResponse serialization testi"""
        job = JobResponse(**job_response_data)
        serialized = job.model_dump()

        assert isinstance(serialized, dict)
        assert "id" in serialized
        assert isinstance(serialized["created_at"], datetime)
        assert serialized["is_active"] is True

    def test_job_response_json_schema(self, job_response_data):
        """JSON schema testi"""
        job = JobResponse(**job_response_data)
        schema = job.model_json_schema()

        assert isinstance(schema, dict)
        assert "properties" in schema
        assert "title" in schema["properties"]
        assert "id" in schema["properties"]


class TestJobListResponse:
    """JobListResponse model testleri"""

    @pytest.fixture
    def job_items(self):
        """Test için job listesi"""
        jobs_data = [
            {
                "title": f"Developer {i}",
                "company": f"Company {i}",
                "location": "Remote",
                "description": f"Job description {i}",
                "requirements": "Programming skills",
                "salary_range": f"${50000 + i*10000} - ${70000 + i*10000}",
                "job_type": "Full-time",
                "experience_level": "Mid-level",
                "apply_url": f"https://company{i}.com/apply",
            }
            for i in range(3)
        ]
        return [JobResponse(**job_data) for job_data in jobs_data]

    def test_job_list_response_creation(self, job_items):
        """JobListResponse oluşturma testi"""
        job_list = JobListResponse(
            items=job_items, total=25, page=1, per_page=10, total_pages=3
        )

        assert len(job_list.items) == 3
        assert job_list.total == 25
        assert job_list.page == 1
        assert job_list.per_page == 10
        assert job_list.total_pages == 3
        assert all(isinstance(job, JobResponse) for job in job_list.items)

    def test_job_list_response_empty(self):
        """Boş JobListResponse testi"""
        job_list = JobListResponse(
            items=[], total=0, page=1, per_page=10, total_pages=0
        )

        assert len(job_list.items) == 0
        assert job_list.total == 0
        assert job_list.total_pages == 0

    def test_job_list_response_serialization(self, job_items):
        """JobListResponse serialization testi"""
        job_list = JobListResponse(
            items=job_items[:2],  # İlk 2 item
            total=2,
            page=1,
            per_page=2,
            total_pages=1,
        )

        serialized = job_list.model_dump()

        assert isinstance(serialized, dict)
        assert "items" in serialized
        assert len(serialized["items"]) == 2
        assert serialized["total"] == 2
        assert all(isinstance(item, dict) for item in serialized["items"])


class TestModelIntegration:
    """Model entegrasyonu testleri"""

    def test_job_lifecycle(self):
        """Job yaşam döngüsü testi"""
        # 1. Job oluşturma
        create_data = {
            "title": "Full Stack Developer",
            "company": "TechStartup",
            "location": "Silicon Valley",
            "description": "Full stack development role",
            "requirements": "React, Node.js, MongoDB",
            "salary_range": "$80,000 - $120,000",
            "job_type": "Full-time",
            "experience_level": "Senior",
            "apply_url": "https://techstartup.com/jobs",
        }

        job_create = JobCreate(**create_data)
        assert job_create.title == "Full Stack Developer"

        # 2. Job response'a dönüştürme
        job_response = JobResponse(**create_data)
        assert isinstance(job_response.id, PyObjectId)
        assert job_response.is_active is True

        # 3. Job güncelleme
        job_update = JobUpdate(salary_range="$90,000 - $140,000", is_active=False)
        assert job_update.salary_range == "$90,000 - $140,000"
        assert job_update.is_active is False

    def test_validation_errors(self):
        """Validation hataları testi"""
        # Eksik zorunlu alanlar
        incomplete_data = {
            "title": "Test Job",
            "company": "Test Company",
            # Diğer zorunlu alanlar eksik
        }

        with pytest.raises(ValidationError):
            JobBase(**incomplete_data)

        with pytest.raises(ValidationError):
            JobResponse(**incomplete_data)

    def test_datetime_handling(self):
        """Datetime işleme testi"""
        job_data = {
            "title": "Data Scientist",
            "company": "DataCorp",
            "location": "Boston",
            "description": "Machine learning role",
            "requirements": "Python, scikit-learn",
            "salary_range": "$100,000 - $150,000",
            "job_type": "Full-time",
            "experience_level": "Senior",
            "apply_url": "https://datacorp.com/apply",
            "application_deadline": datetime(2025, 6, 30),
        }

        job = JobResponse(**job_data)
        assert isinstance(job.application_deadline, datetime)
        assert isinstance(job.created_at, datetime)
        assert isinstance(job.updated_at, datetime)


class TestJobApplicationMongo:
    """Test JobApplicationMongo model"""

    def test_job_application_mongo_to_dict(self):
        """Test to_dict method"""
        from datetime import datetime

        from models.models import JobApplicationMongo

        # Create instance
        app = JobApplicationMongo(
            user_id="user123",
            job_id="job456",
            application_type="external",
            cover_letter="I'm interested",
            status="applied",
        )

        # Test to_dict
        result = app.to_dict()

        assert isinstance(result, dict)
        assert result["user_id"] == "user123"
        assert result["job_id"] == "job456"
        assert result["application_type"] == "external"
        assert result["cover_letter"] == "I'm interested"
        assert result["status"] == "applied"
        assert "applied_at" in result
        assert "updated_at" in result
        assert result["viewed_by_company"] is False

    def test_job_application_mongo_with_datetime_fields(self):
        """Test to_dict with datetime fields"""
        from datetime import datetime

        from models.models import JobApplicationMongo

        response_date = datetime.utcnow()
        app = JobApplicationMongo(
            user_id="user123",
            job_id="job456",
            application_type="external",
            company_response_date=response_date,
            company_response="We received your application",
        )

        result = app.to_dict()
        assert result["company_response_date"] is not None
        assert result["company_response"] == "We received your application"


class TestJobApplicationMongo:
    """Test JobApplicationMongo model"""

    def test_job_application_mongo_to_dict(self):
        """Test to_dict method"""
        from models.models import JobApplicationMongo

        # Create instance
        app = JobApplicationMongo(
            user_id="user123",
            job_id="job456",
            application_type="external",
            cover_letter="I am interested",
            status="applied",
        )

        # Test to_dict
        result = app.to_dict()

        assert isinstance(result, dict)
        assert result["user_id"] == "user123"
        assert result["job_id"] == "job456"
        assert result["application_type"] == "external"
        assert result["cover_letter"] == "I am interested"
        assert result["status"] == "applied"
        assert "applied_at" in result
        assert "updated_at" in result
        assert result["viewed_by_company"] is False
