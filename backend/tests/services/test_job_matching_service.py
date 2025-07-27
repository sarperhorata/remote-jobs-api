from unittest.mock import AsyncMock, Mock

import pytest
from services.ai_job_matching_service import AIJobMatchingService


class TestJobMatchingService:
    @pytest.fixture
    def mock_db(self):
        db = Mock()
        db.users = Mock()
        db.jobs = Mock()
        db.user_skills = Mock()
        db.user_experience = Mock()
        db.user_preferences = Mock()
        db.applications = Mock()
        db.recommendation_logs = Mock()
        return db

    @pytest.fixture
    def service(self, mock_db):
        return AIJobMatchingService(mock_db)

    @pytest.mark.asyncio
    async def test_service_initialization(self, service):
        assert service is not None
        assert hasattr(service, "db")
        assert hasattr(service, "matching_cache")
        assert hasattr(service, "cache_ttl")

    @pytest.mark.asyncio
    async def test_get_job_recommendations_no_profile(self, service, mock_db):
        """Test recommendations when user profile doesn't exist"""
        mock_db.users.find_one.return_value = AsyncMock(return_value=None)

        result = await service.get_job_recommendations("nonexistent_user")
        assert result == []

    @pytest.mark.asyncio
    async def test_get_job_recommendations_empty_jobs(self, service, mock_db):
        """Test recommendations when no jobs available"""
        # Mock user profile
        mock_db.users.find_one.return_value = AsyncMock(return_value={"_id": "user123"})
        mock_db.user_skills.find.return_value.to_list.return_value = AsyncMock(
            return_value=[]
        )
        mock_db.user_experience.find.return_value.to_list.return_value = AsyncMock(
            return_value=[]
        )
        mock_db.user_preferences.find_one.return_value = AsyncMock(return_value={})
        mock_db.applications.find.return_value.limit.return_value.to_list.return_value = AsyncMock(
            return_value=[]
        )

        # Mock empty jobs
        mock_db.jobs.find.return_value.limit.return_value.to_list.return_value = (
            AsyncMock(return_value=[])
        )

        result = await service.get_job_recommendations("user123")
        assert result == []

    @pytest.mark.asyncio
    async def test_match_analytics_empty_data(self, service, mock_db):
        """Test match analytics with no data"""
        mock_db.recommendation_logs.find.return_value.sort.return_value.limit.return_value.to_list.return_value = AsyncMock(
            return_value=[]
        )
        mock_db.applications.find.return_value.sort.return_value.limit.return_value.to_list.return_value = AsyncMock(
            return_value=[]
        )

        result = await service.get_match_analytics("user123")
        assert isinstance(result, dict)
        assert result["total_recommendations_last_30"] == 0
        assert result["total_applications"] == 0
