import pytest
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime
from bson import ObjectId
from backend.services.user_application_service import UserApplicationService
from backend.models.user_application import (
    UserApplicationCreate,
    UserApplicationUpdate,
    UserApplicationResponse
)

class TestUserApplicationService:
    """User Application Service testleri"""
    
    @pytest.fixture
    def mock_db(self):
        """Mock database"""
        db = Mock()
        db.user_applications = Mock()
        return db
    
    @pytest.fixture
    def service(self, mock_db):
        """User application service instance"""
        service = UserApplicationService()
        service.db = mock_db
        service.collection = mock_db.user_applications
        return service
    
    @pytest.fixture
    def sample_application_data(self):
        """Sample application data"""
        return {
            "user_id": "user123",
            "job_id": "job456",
            "application_type": "manual",
            "auto_apply_used": False,
            "status": "applied",
            "notes": "Test application",
            "applied_at": datetime.utcnow()
        }
    
    @pytest.fixture
    def sample_application_create(self, sample_application_data):
        """Sample UserApplicationCreate object"""
        return UserApplicationCreate(**sample_application_data)
    
    @pytest.fixture
    def sample_application_response(self, sample_application_data):
        """Sample UserApplicationResponse object"""
        return UserApplicationResponse(
            id=str(ObjectId()),
            **sample_application_data
        )
    
    def test_service_initialization(self, service):
        """Service başlatma testi"""
        assert service is not None
        assert hasattr(service, 'db')
        assert hasattr(service, 'collection')
        assert hasattr(service, '_get_collection')
    
    @pytest.mark.asyncio
    async def test_get_collection(self, service, mock_db):
        """Collection get testi"""
        collection = await service._get_collection()
        
        assert collection == mock_db.user_applications
        assert service.collection == mock_db.user_applications
    
    @pytest.mark.asyncio
    async def test_create_application_success(self, service, sample_application_create, sample_application_response):
        """Başarılı application oluşturma testi"""
        # Mock collection operations
        mock_insert_result = Mock()
        mock_insert_result.inserted_id = ObjectId()
        service.collection.insert_one = AsyncMock(return_value=mock_insert_result)
        
        service.collection.find_one = AsyncMock(return_value=sample_application_response.model_dump())
        
        result = await service.create_application(sample_application_create)
        
        assert isinstance(result, UserApplicationResponse)
        assert result.user_id == sample_application_create.user_id
        assert result.job_id == sample_application_create.job_id
        assert result.application_type == sample_application_create.application_type
        
        service.collection.insert_one.assert_called_once()
        service.collection.find_one.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_create_application_database_error(self, service, sample_application_create):
        """Database error ile application oluşturma testi"""
        service.collection.insert_one = AsyncMock(side_effect=Exception("Database error"))
        
        with pytest.raises(Exception, match="Database error"):
            await service.create_application(sample_application_create)
    
    @pytest.mark.asyncio
    async def test_create_application_retrieve_error(self, service, sample_application_create):
        """Retrieve error ile application oluşturma testi"""
        mock_insert_result = Mock()
        mock_insert_result.inserted_id = ObjectId()
        service.collection.insert_one = AsyncMock(return_value=mock_insert_result)
        
        service.collection.find_one = AsyncMock(return_value=None)
        
        with pytest.raises(Exception, match="Failed to retrieve created application"):
            await service.create_application(sample_application_create)
    
    @pytest.mark.asyncio
    async def test_get_application_by_id_success(self, service, sample_application_response):
        """Başarılı application get testi"""
        service.collection.find_one = AsyncMock(return_value=sample_application_response.model_dump())
        
        result = await service.get_application_by_id("app123")
        
        assert isinstance(result, UserApplicationResponse)
        assert result.user_id == sample_application_response.user_id
        service.collection.find_one.assert_called_once_with({"_id": "app123"})
    
    @pytest.mark.asyncio
    async def test_get_application_by_id_not_found(self, service):
        """Application bulunamadığında test"""
        service.collection.find_one = AsyncMock(return_value=None)
        
        result = await service.get_application_by_id("nonexistent")
        
        assert result is None
    
    @pytest.mark.asyncio
    async def test_get_user_applications_success(self, service, sample_application_response):
        """Başarılı user applications get testi"""
        mock_cursor = Mock()
        mock_cursor.sort = Mock(return_value=mock_cursor)
        mock_cursor.skip = Mock(return_value=mock_cursor)
        mock_cursor.limit = Mock(return_value=mock_cursor)
        mock_cursor.to_list = AsyncMock(return_value=[sample_application_response.model_dump()])
        
        service.collection.find = Mock(return_value=mock_cursor)
        
        result = await service.get_user_applications("user123", skip=0, limit=10)
        
        assert len(result) == 1
        assert isinstance(result[0], UserApplicationResponse)
        service.collection.find.assert_called_once_with({"user_id": "user123"})
    
    @pytest.mark.asyncio
    async def test_get_user_applications_empty(self, service):
        """Boş user applications test"""
        mock_cursor = Mock()
        mock_cursor.sort = Mock(return_value=mock_cursor)
        mock_cursor.skip = Mock(return_value=mock_cursor)
        mock_cursor.limit = Mock(return_value=mock_cursor)
        mock_cursor.to_list = AsyncMock(return_value=[])
        
        service.collection.find = Mock(return_value=mock_cursor)
        
        result = await service.get_user_applications("user123")
        
        assert result == []
    
    @pytest.mark.asyncio
    async def test_update_application_success(self, service, sample_application_response):
        """Başarılı application update testi"""
        update_data = UserApplicationUpdate(status="interviewed", notes="Updated notes")
        
        service.collection.update_one = AsyncMock(return_value=Mock(modified_count=1))
        service.collection.find_one = AsyncMock(return_value=sample_application_response.model_dump())
        
        result = await service.update_application("app123", update_data)
        
        assert isinstance(result, UserApplicationResponse)
        service.collection.update_one.assert_called_once()
        service.collection.find_one.assert_called_once_with({"_id": "app123"})
    
    @pytest.mark.asyncio
    async def test_update_application_not_found(self, service):
        """Application bulunamadığında update test"""
        update_data = UserApplicationUpdate(status="interviewed")
        
        service.collection.update_one = AsyncMock(return_value=Mock(modified_count=0))
        
        result = await service.update_application("nonexistent", update_data)
        
        assert result is None
    
    @pytest.mark.asyncio
    async def test_delete_application_success(self, service):
        """Başarılı application delete testi"""
        service.collection.delete_one = AsyncMock(return_value=Mock(deleted_count=1))
        
        result = await service.delete_application("app123")
        
        assert result is True
        service.collection.delete_one.assert_called_once_with({"_id": "app123"})
    
    @pytest.mark.asyncio
    async def test_delete_application_not_found(self, service):
        """Application bulunamadığında delete test"""
        service.collection.delete_one = AsyncMock(return_value=Mock(deleted_count=0))
        
        result = await service.delete_application("nonexistent")
        
        assert result is False
    
    @pytest.mark.asyncio
    async def test_get_application_stats(self, service):
        """Application stats testi"""
        mock_cursor = Mock()
        mock_cursor.to_list = AsyncMock(return_value=[
            {"status": "applied", "count": 5},
            {"status": "interviewed", "count": 2},
            {"status": "rejected", "count": 1}
        ])
        
        service.collection.aggregate = Mock(return_value=mock_cursor)
        
        result = await service.get_application_stats("user123")
        
        assert isinstance(result, dict)
        assert "total_applications" in result
        assert "status_breakdown" in result
        service.collection.aggregate.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_search_applications(self, service, sample_application_response):
        """Application search testi"""
        mock_cursor = Mock()
        mock_cursor.sort = Mock(return_value=mock_cursor)
        mock_cursor.skip = Mock(return_value=mock_cursor)
        mock_cursor.limit = Mock(return_value=mock_cursor)
        mock_cursor.to_list = AsyncMock(return_value=[sample_application_response.model_dump()])
        
        service.collection.find = Mock(return_value=mock_cursor)
        
        search_filters = {
            "status": "applied",
            "application_type": "manual",
            "date_from": datetime(2023, 1, 1),
            "date_to": datetime(2023, 12, 31)
        }
        
        result = await service.search_applications("user123", search_filters, skip=0, limit=10)
        
        assert len(result) == 1
        assert isinstance(result[0], UserApplicationResponse)
        service.collection.find.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_recent_applications(self, service, sample_application_response):
        """Recent applications testi"""
        mock_cursor = Mock()
        mock_cursor.sort = Mock(return_value=mock_cursor)
        mock_cursor.limit = Mock(return_value=mock_cursor)
        mock_cursor.to_list = AsyncMock(return_value=[sample_application_response.model_dump()])
        
        service.collection.find = Mock(return_value=mock_cursor)
        
        result = await service.get_recent_applications("user123", limit=5)
        
        assert len(result) == 1
        assert isinstance(result[0], UserApplicationResponse)
        service.collection.find.assert_called_once_with({"user_id": "user123"})
    
    @pytest.mark.asyncio
    async def test_get_applications_by_job(self, service, sample_application_response):
        """Job'a göre applications testi"""
        mock_cursor = Mock()
        mock_cursor.sort = Mock(return_value=mock_cursor)
        mock_cursor.skip = Mock(return_value=mock_cursor)
        mock_cursor.limit = Mock(return_value=mock_cursor)
        mock_cursor.to_list = AsyncMock(return_value=[sample_application_response.model_dump()])
        
        service.collection.find = Mock(return_value=mock_cursor)
        
        result = await service.get_applications_by_job("job456", skip=0, limit=10)
        
        assert len(result) == 1
        assert isinstance(result[0], UserApplicationResponse)
        service.collection.find.assert_called_once_with({"job_id": "job456"})
    
    @pytest.mark.asyncio
    async def test_get_applications_by_status(self, service, sample_application_response):
        """Status'a göre applications testi"""
        mock_cursor = Mock()
        mock_cursor.sort = Mock(return_value=mock_cursor)
        mock_cursor.skip = Mock(return_value=mock_cursor)
        mock_cursor.limit = Mock(return_value=mock_cursor)
        mock_cursor.to_list = AsyncMock(return_value=[sample_application_response.model_dump()])
        
        service.collection.find = Mock(return_value=mock_cursor)
        
        result = await service.get_applications_by_status("user123", "applied", skip=0, limit=10)
        
        assert len(result) == 1
        assert isinstance(result[0], UserApplicationResponse)
        service.collection.find.assert_called_once_with({"user_id": "user123", "status": "applied"})
    
    def test_service_methods_exist(self, service):
        """Service metodlarının varlığını test et"""
        required_methods = [
            '_get_collection',
            'create_application',
            'get_application_by_id',
            'get_user_applications',
            'update_application',
            'delete_application',
            'get_application_stats',
            'search_applications',
            'get_recent_applications',
            'get_applications_by_job',
            'get_applications_by_status'
        ]
        
        for method in required_methods:
            assert hasattr(service, method)
            assert callable(getattr(service, method))
    
    @pytest.mark.asyncio
    async def test_service_integration(self, service, sample_application_create, sample_application_response):
        """Service integration testi"""
        # Test full CRUD cycle
        
        # Create
        mock_insert_result = Mock()
        mock_insert_result.inserted_id = ObjectId()
        service.collection.insert_one = AsyncMock(return_value=mock_insert_result)
        service.collection.find_one = AsyncMock(return_value=sample_application_response.model_dump())
        
        created = await service.create_application(sample_application_create)
        assert created is not None
        
        # Read
        service.collection.find_one = AsyncMock(return_value=sample_application_response.model_dump())
        retrieved = await service.get_application_by_id(str(created.id))
        assert retrieved is not None
        
        # Update
        update_data = UserApplicationUpdate(status="interviewed")
        service.collection.update_one = AsyncMock(return_value=Mock(modified_count=1))
        service.collection.find_one = AsyncMock(return_value=sample_application_response.model_dump())
        
        updated = await service.update_application(str(created.id), update_data)
        assert updated is not None
        
        # Delete
        service.collection.delete_one = AsyncMock(return_value=Mock(deleted_count=1))
        deleted = await service.delete_application(str(created.id))
        assert deleted is True 