import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
from bson import ObjectId
from pymongo.errors import PyMongoError
from database.company_repository import CompanyRepository


class TestCompanyRepository:
    """Company repository testleri"""
    
    @pytest.fixture
    def mock_db(self):
        """Mock database client"""
        mock_client = Mock()
        mock_collection = Mock()
        mock_client.companies = mock_collection
        return mock_client, mock_collection
    
    @pytest.fixture
    def company_repo(self, mock_db):
        """Company repository instance with mocked database"""
        mock_client, mock_collection = mock_db
        with patch('database.company_repository.get_database_client', return_value=mock_client):
            repo = CompanyRepository()
            return repo, mock_collection
    
    def test_init_creates_indexes(self, mock_db):
        """Repository initialization creates indexes"""
        mock_client, mock_collection = mock_db
        
        with patch('database.company_repository.get_database_client', return_value=mock_client):
            repo = CompanyRepository()
            
            # Verify indexes were created
            mock_collection.create_index.assert_called()
            assert mock_collection.create_index.call_count >= 6  # Multiple indexes
    
    def test_save_company_new(self, company_repo):
        """Test saving a new company"""
        repo, mock_collection = company_repo
        
        # Mock data
        company_data = {
            'name': 'Test Company',
            'website': 'https://test.com',
            'industry': 'Technology'
        }
        
        # Mock upsert result
        mock_result = Mock()
        mock_result.upserted_id = ObjectId('507f1f77bcf86cd799439011')
        mock_collection.update_one.return_value = mock_result
        
        # Mock find_one for getting existing company
        mock_collection.find_one.return_value = {
            '_id': ObjectId('507f1f77bcf86cd799439011'),
            'name': 'Test Company'
        }
        
        result = repo.save_company(company_data)
        
        # Verify update_one was called with upsert=True
        mock_collection.update_one.assert_called_once()
        call_args = mock_collection.update_one.call_args
        assert call_args[1]['upsert'] is True
        
        # Verify timestamps were added
        assert 'created_at' in company_data
        assert 'updated_at' in company_data
        
        assert result == '507f1f77bcf86cd799439011'
    
    def test_save_company_existing(self, company_repo):
        """Test updating an existing company"""
        repo, mock_collection = company_repo
        
        company_data = {
            'name': 'Existing Company',
            'website': 'https://existing.com'
        }
        
        # Mock upsert result (no upserted_id means existing company)
        mock_result = Mock()
        mock_result.upserted_id = None
        mock_collection.update_one.return_value = mock_result
        
        # Mock find_one for getting existing company
        mock_collection.find_one.return_value = {
            '_id': ObjectId('507f1f77bcf86cd799439012'),
            'name': 'Existing Company'
        }
        
        result = repo.save_company(company_data)
        
        assert result == '507f1f77bcf86cd799439012'
    
    def test_save_company_database_error(self, company_repo):
        """Test database error handling in save_company"""
        repo, mock_collection = company_repo
        
        company_data = {'name': 'Test Company'}
        mock_collection.update_one.side_effect = PyMongoError("Database error")
        
        with pytest.raises(PyMongoError):
            repo.save_company(company_data)
    
    def test_get_company_by_id_success(self, company_repo):
        """Test getting company by ID successfully"""
        repo, mock_collection = company_repo
        
        company_id = '507f1f77bcf86cd799439011'
        mock_company = {
            '_id': ObjectId(company_id),
            'name': 'Test Company',
            'website': 'https://test.com'
        }
        mock_collection.find_one.return_value = mock_company
        
        result = repo.get_company_by_id(company_id)
        
        mock_collection.find_one.assert_called_once_with({'_id': ObjectId(company_id)})
        assert result['_id'] == company_id
        assert result['name'] == 'Test Company'
    
    def test_get_company_by_id_not_found(self, company_repo):
        """Test getting company by ID when not found"""
        repo, mock_collection = company_repo
        
        company_id = '507f1f77bcf86cd799439011'
        mock_collection.find_one.return_value = None
        
        result = repo.get_company_by_id(company_id)
        
        assert result is None
    
    def test_get_company_by_id_database_error(self, company_repo):
        """Test database error handling in get_company_by_id"""
        repo, mock_collection = company_repo
        
        company_id = '507f1f77bcf86cd799439011'
        mock_collection.find_one.side_effect = PyMongoError("Database error")
        
        with pytest.raises(PyMongoError):
            repo.get_company_by_id(company_id)
    
    def test_get_company_by_name_success(self, company_repo):
        """Test getting company by name successfully"""
        repo, mock_collection = company_repo
        
        company_name = 'Test Company'
        mock_company = {
            '_id': ObjectId('507f1f77bcf86cd799439011'),
            'name': company_name,
            'website': 'https://test.com'
        }
        mock_collection.find_one.return_value = mock_company
        
        result = repo.get_company_by_name(company_name)
        
        mock_collection.find_one.assert_called_once_with({'name': company_name})
        assert result['name'] == company_name
        assert result['_id'] == '507f1f77bcf86cd799439011'
    
    def test_get_company_by_name_not_found(self, company_repo):
        """Test getting company by name when not found"""
        repo, mock_collection = company_repo
        
        company_name = 'Non-existent Company'
        mock_collection.find_one.return_value = None
        
        result = repo.get_company_by_name(company_name)
        
        assert result is None
    
    def test_get_companies_with_pagination(self, company_repo):
        """Test getting companies with pagination"""
        repo, mock_collection = company_repo
        
        # Mock cursor
        mock_cursor = Mock()
        mock_companies = [
            {'_id': ObjectId('507f1f77bcf86cd799439011'), 'name': 'Company 1'},
            {'_id': ObjectId('507f1f77bcf86cd799439012'), 'name': 'Company 2'}
        ]
        mock_cursor.__iter__ = Mock(return_value=iter(mock_companies))
        mock_collection.find.return_value = mock_cursor
        
        result = repo.get_companies(skip=10, limit=5, sort_by='name', sort_order=1)
        
        # Verify find was called with correct parameters
        mock_collection.find.assert_called_once_with({})
        mock_cursor.sort.assert_called_once_with('name', 1)
        mock_cursor.skip.assert_called_once_with(10)
        mock_cursor.limit.assert_called_once_with(5)
        
        # Verify ObjectId conversion
        assert len(result) == 2
        assert result[0]['_id'] == '507f1f77bcf86cd799439011'
        assert result[1]['_id'] == '507f1f77bcf86cd799439012'
    
    def test_get_companies_with_query(self, company_repo):
        """Test getting companies with query filter"""
        repo, mock_collection = company_repo
        
        query = {'industry': 'Technology'}
        mock_cursor = Mock()
        mock_cursor.__iter__ = Mock(return_value=iter([]))
        mock_collection.find.return_value = mock_cursor
        
        repo.get_companies(query=query)
        
        mock_collection.find.assert_called_once_with(query)
    
    def test_get_companies_database_error(self, company_repo):
        """Test database error handling in get_companies"""
        repo, mock_collection = company_repo
        
        mock_collection.find.side_effect = PyMongoError("Database error")
        
        with pytest.raises(PyMongoError):
            repo.get_companies()
    
    def test_count_companies_success(self, company_repo):
        """Test counting companies successfully"""
        repo, mock_collection = company_repo
        
        query = {'industry': 'Technology'}
        mock_collection.count_documents.return_value = 42
        
        result = repo.count_companies(query)
        
        mock_collection.count_documents.assert_called_once_with(query)
        assert result == 42
    
    def test_count_companies_no_query(self, company_repo):
        """Test counting companies without query"""
        repo, mock_collection = company_repo
        
        mock_collection.count_documents.return_value = 100
        
        result = repo.count_companies()
        
        mock_collection.count_documents.assert_called_once_with({})
        assert result == 100
    
    def test_count_companies_database_error(self, company_repo):
        """Test database error handling in count_companies"""
        repo, mock_collection = company_repo
        
        mock_collection.count_documents.side_effect = PyMongoError("Database error")
        
        with pytest.raises(PyMongoError):
            repo.count_companies()
    
    @patch('database.company_repository.JobRepository')
    def test_update_company_stats(self, mock_job_repo_class, company_repo):
        """Test updating company statistics"""
        repo, mock_collection = company_repo
        
        company_name = 'Test Company'
        
        # Mock job repository
        mock_job_repo = Mock()
        mock_job_repo.count_jobs.return_value = 15
        mock_job_repo_class.return_value = mock_job_repo
        
        # Mock update result
        mock_collection.update_one.return_value = Mock()
        
        repo.update_company_stats(company_name)
        
        # Verify job count was retrieved
        mock_job_repo.count_jobs.assert_called_once_with({'company': company_name})
        
        # Verify company was updated
        mock_collection.update_one.assert_called_once()
        call_args = mock_collection.update_one.call_args
        assert call_args[0][0] == {'name': company_name}
        assert '$set' in call_args[0][1]
    
    def test_update_company_stats_database_error(self, company_repo):
        """Test database error handling in update_company_stats"""
        repo, mock_collection = company_repo
        
        company_name = 'Test Company'
        mock_collection.update_one.side_effect = PyMongoError("Database error")
        
        with pytest.raises(PyMongoError):
            repo.update_company_stats(company_name)
    
    def test_ensure_indexes_error_handling(self, mock_db):
        """Test error handling in index creation"""
        mock_client, mock_collection = mock_db
        mock_collection.create_index.side_effect = PyMongoError("Index creation failed")
        
        with patch('database.company_repository.get_database_client', return_value=mock_client):
            # Should not raise exception, just log error
            repo = CompanyRepository()
            assert repo is not None 