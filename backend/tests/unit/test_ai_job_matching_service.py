import pytest
import asyncio
from unittest.mock import AsyncMock, Mock, patch
from datetime import datetime, timedelta
from bson import ObjectId

from backend.services.ai_job_matching_service import AIJobMatchingService


class TestAIJobMatchingService:
    """Comprehensive tests for AI Job Matching Service"""
    
    @pytest.fixture
    def mock_db(self):
        """Create a mock database."""
        db = Mock()
        db.users = AsyncMock()
        db.user_skills = AsyncMock()
        db.user_experience = AsyncMock()
        db.user_preferences = AsyncMock()
        db.applications = AsyncMock()
        db.jobs = AsyncMock()
        db.recommendation_logs = AsyncMock()
        return db
    
    @pytest.fixture
    def ai_service(self, mock_db):
        """Create AI service instance with mock database."""
        return AIJobMatchingService(mock_db)
    
    @pytest.fixture
    def sample_user_profile(self):
        """Sample user profile for testing."""
        return {
            "user": {
                "_id": ObjectId(),
                "email": "test@example.com",
                "location": "San Francisco"
            },
            "skills": [
                {"name": "Python", "level": "expert"},
                {"name": "JavaScript", "level": "advanced"},
                {"name": "React", "level": "intermediate"}
            ],
            "experience": [
                {"company": "TechCorp", "years": 3, "position": "Backend Developer"},
                {"company": "StartupXYZ", "years": 2, "position": "Full Stack Developer"}
            ],
            "preferences": {
                "remote_work": True,
                "desired_salary": 100000,
                "job_type": "full-time",
                "company_size": "medium"
            },
            "application_history": []
        }
    
    @pytest.fixture
    def sample_job(self):
        """Sample job for testing."""
        return {
            "_id": ObjectId(),
            "title": "Senior Python Developer",
            "company": "RemoteTech Inc",
            "location": "Remote",
            "remote_type": "remote",
            "required_skills": ["Python", "Django", "PostgreSQL"],
            "experience_years": 4,
            "salary_min": 90000,
            "salary_max": 120000,
            "job_type": "full-time",
            "company_size": "medium",
            "status": "active",
            "description": "We are looking for a skilled Python developer."
        }
    
    @pytest.mark.asyncio
    async def test_get_job_recommendations_success(self, ai_service, mock_db, sample_user_profile, sample_job):
        """Test successful job recommendations."""
        user_id = str(ObjectId())
        
        # Mock database calls
        mock_db.users.find_one.return_value = sample_user_profile["user"]
        mock_db.user_skills.find.return_value.to_list.return_value = sample_user_profile["skills"]
        mock_db.user_experience.find.return_value.to_list.return_value = sample_user_profile["experience"]
        mock_db.user_preferences.find_one.return_value = sample_user_profile["preferences"]
        mock_db.applications.find.return_value.limit.return_value.to_list.return_value = []
        mock_db.jobs.find.return_value.limit.return_value.to_list.return_value = [sample_job]
        
        # Test
        recommendations = await ai_service.get_job_recommendations(user_id, limit=5)
        
        # Assertions
        assert len(recommendations) > 0
        assert recommendations[0]["title"] == "Senior Python Developer"
        assert "match_score" in recommendations[0]
        assert "match_reasons" in recommendations[0]
        assert 0.0 <= recommendations[0]["match_score"] <= 1.0
    
    @pytest.mark.asyncio
    async def test_get_job_recommendations_no_user_profile(self, ai_service, mock_db):
        """Test recommendations when user profile doesn't exist."""
        user_id = str(ObjectId())
        
        # Mock database calls
        mock_db.users.find_one.return_value = None
        
        # Test
        recommendations = await ai_service.get_job_recommendations(user_id)
        
        # Assertions
        assert recommendations == []
    
    @pytest.mark.asyncio
    async def test_calculate_match_score(self, ai_service, sample_user_profile, sample_job):
        """Test match score calculation."""
        score = await ai_service._calculate_match_score(sample_user_profile, sample_job)
        
        assert 0.0 <= score <= 1.0
        assert isinstance(score, float)
    
    @pytest.mark.asyncio
    async def test_match_skills_perfect_match(self, ai_service, sample_user_profile, sample_job):
        """Test perfect skills matching."""
        # Modify job to require exactly user's skills
        sample_job["required_skills"] = ["Python", "JavaScript"]
        
        score = await ai_service._match_skills(sample_user_profile, sample_job)
        
        assert score > 0.5  # Should be good match
    
    @pytest.mark.asyncio
    async def test_match_skills_no_match(self, ai_service, sample_user_profile, sample_job):
        """Test no skills matching."""
        # Modify job to require different skills
        sample_job["required_skills"] = ["Java", "C++", "Ruby"]
        
        score = await ai_service._match_skills(sample_user_profile, sample_job)
        
        assert score == 0.0  # No matching skills
    
    @pytest.mark.asyncio
    async def test_match_experience_sufficient(self, ai_service, sample_user_profile, sample_job):
        """Test experience matching when user has sufficient experience."""
        # User has 5 years total experience, job requires 4
        score = await ai_service._match_experience(sample_user_profile, sample_job)
        
        assert score >= 0.8  # Should be good match
    
    @pytest.mark.asyncio
    async def test_match_location_remote_preferred(self, ai_service, sample_user_profile, sample_job):
        """Test location matching for remote work preference."""
        sample_user_profile["preferences"]["remote_work"] = True
        sample_job["remote_type"] = "remote"
        
        score = await ai_service._match_location(sample_user_profile, sample_job)
        
        assert score == 1.0  # Perfect match for remote
    
    @pytest.mark.asyncio
    async def test_match_salary_perfect_match(self, ai_service, sample_user_profile, sample_job):
        """Test salary matching when user's expectation is met."""
        sample_user_profile["preferences"]["desired_salary"] = 100000
        sample_job["salary_max"] = 120000
        
        score = await ai_service._match_salary(sample_user_profile, sample_job)
        
        assert score == 1.0  # Perfect match
    
    @pytest.mark.asyncio
    async def test_get_match_analytics(self, ai_service, mock_db):
        """Test getting match analytics."""
        user_id = str(ObjectId())
        
        # Mock data
        mock_logs = [
            {"user_id": user_id, "total_matches": 5, "timestamp": datetime.utcnow()},
            {"user_id": user_id, "total_matches": 8, "timestamp": datetime.utcnow()}
        ]
        mock_applications = [
            {"user_id": user_id, "job_id": str(ObjectId()), "created_at": datetime.utcnow()}
        ]
        
        mock_db.recommendation_logs.find.return_value.sort.return_value.limit.return_value.to_list.return_value = mock_logs
        mock_db.applications.find.return_value.sort.return_value.limit.return_value.to_list.return_value = mock_applications
        
        analytics = await ai_service.get_match_analytics(user_id)
        
        assert analytics["total_recommendations_last_30"] == 2
        assert analytics["total_applications"] == 1
        assert 0.0 <= analytics["success_rate"] <= 1.0
    
    @pytest.mark.asyncio
    async def test_error_handling_get_recommendations(self, ai_service, mock_db):
        """Test error handling in get_job_recommendations."""
        user_id = str(ObjectId())
        
        # Mock database to raise exception
        mock_db.users.find_one.side_effect = Exception("Database error")
        
        recommendations = await ai_service.get_job_recommendations(user_id)
        
        assert recommendations == []
    
    def test_ai_service_initialization(self, mock_db):
        """Test AI service initialization."""
        service = AIJobMatchingService(mock_db)
        
        assert service.db == mock_db
        assert service.matching_cache == {}
        assert service.cache_ttl == 3600 