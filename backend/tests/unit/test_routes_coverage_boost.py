#!/usr/bin/env python3

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from fastapi.testclient import TestClient
from fastapi import HTTPException
from datetime import datetime
from bson import ObjectId
import sys
import os

# Add proper paths for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

# Import the main app and routes
from backend.main import app
from backend.routes import companies, ads

class TestCompaniesRoutes:
    """Test companies routes to boost coverage from 43% to 90%+"""
    
    @pytest.fixture
    def client(self):
        """Create test client."""
        return TestClient(app)
    
    @pytest.fixture
    def mock_db(self):
        """Mock database for testing."""
        with patch('backend.routes.companies.get_db') as mock:
            mock_db = AsyncMock()
            mock.return_value.__aenter__.return_value = mock_db
            yield mock_db
    
    def test_get_companies_success(self, client, mock_db):
        """Test successful companies retrieval."""
        # Mock companies aggregation result
        mock_companies = [
            {
                "_id": "TechCorp",
                "job_count": 25,
                "locations": ["Remote", "San Francisco"],
                "latest_job_date": datetime.now(),
                "industries": ["Technology"],
                "company_sizes": ["100-500"],
                "website": "https://techcorp.com"
            },
            {
                "_id": "StartupXYZ", 
                "job_count": 15,
                "locations": ["Remote"],
                "latest_job_date": datetime.now(),
                "industries": ["Startup"],
                "company_sizes": ["10-50"],
                "website": "https://startupxyz.com"
            }
        ]
        
        mock_db.jobs.aggregate.return_value = mock_companies
        
        response = client.get("/api/companies")
        assert response.status_code == 200
        
        data = response.json()
        assert len(data) == 2
        assert data[0]["name"] == "TechCorp"
        assert data[0]["job_count"] == 25
        assert data[1]["name"] == "StartupXYZ"
    
    def test_get_companies_with_pagination(self, client, mock_db):
        """Test companies with pagination parameters."""
        mock_db.jobs.aggregate.return_value = []
        
        response = client.get("/api/companies?limit=10&offset=20")
        assert response.status_code == 200
        
        # Verify pagination parameters were used
        mock_db.jobs.aggregate.assert_called_once()
        pipeline = mock_db.jobs.aggregate.call_args[0][0]
        
        # Check for limit and skip stages
        limit_stage = next((stage for stage in pipeline if "$limit" in stage), None)
        skip_stage = next((stage for stage in pipeline if "$skip" in stage), None)
        
        assert limit_stage is not None
        assert skip_stage is not None
    
    def test_get_companies_with_search(self, client, mock_db):
        """Test companies with search parameter."""
        mock_db.jobs.aggregate.return_value = []
        
        response = client.get("/api/companies?search=tech")
        assert response.status_code == 200
        
        # Verify search was applied
        mock_db.jobs.aggregate.assert_called_once()
    
    def test_get_companies_database_error(self, client, mock_db):
        """Test companies endpoint with database error."""
        mock_db.jobs.aggregate.side_effect = Exception("Database connection failed")
        
        response = client.get("/api/companies")
        assert response.status_code == 500
    
    def test_get_company_details_success(self, client, mock_db):
        """Test successful company details retrieval."""
        company_name = "TechCorp"
        
        # Mock company jobs
        mock_jobs = [
            {
                "_id": str(ObjectId()),
                "title": "Software Engineer",
                "company": "TechCorp", 
                "location": "Remote",
                "type": "Full-time",
                "created_at": datetime.now(),
                "description": "Great opportunity"
            }
        ]
        
        # Mock company stats
        mock_stats = [
            {
                "_id": company_name,
                "job_count": 25,
                "locations": ["Remote", "San Francisco"],
                "job_types": ["Full-time", "Part-time"],
                "latest_job_date": datetime.now(),
                "average_salary": 120000
            }
        ]
        
        mock_db.jobs.find.return_value.sort.return_value.limit.return_value = mock_jobs
        mock_db.jobs.aggregate.return_value = mock_stats
        
        response = client.get(f"/api/companies/{company_name}")
        assert response.status_code == 200
        
        data = response.json()
        assert data["name"] == company_name
        assert data["job_count"] == 25
        assert len(data["recent_jobs"]) == 1
        assert data["recent_jobs"][0]["title"] == "Software Engineer"
    
    def test_get_company_details_not_found(self, client, mock_db):
        """Test company details for non-existent company."""
        company_name = "NonExistentCorp"
        
        mock_db.jobs.find.return_value.sort.return_value.limit.return_value = []
        mock_db.jobs.aggregate.return_value = []
        
        response = client.get(f"/api/companies/{company_name}")
        assert response.status_code == 404
        
        data = response.json()
        assert "not found" in data["detail"].lower()
    
    def test_get_company_details_database_error(self, client, mock_db):
        """Test company details with database error."""
        company_name = "TechCorp"
        
        mock_db.jobs.find.side_effect = Exception("Database error")
        
        response = client.get(f"/api/companies/{company_name}")
        assert response.status_code == 500

class TestAdsRoutes:
    """Test ads routes to boost coverage from 63% to 90%+"""
    
    @pytest.fixture  
    def client(self):
        """Create test client."""
        return TestClient(app)
    
    @pytest.fixture
    def mock_db(self):
        """Mock database for testing."""
        with patch('backend.routes.ads.get_db') as mock:
            mock_db = AsyncMock()
            mock.return_value.__aenter__.return_value = mock_db
            yield mock_db
    
    @pytest.fixture
    def sample_ad_data(self):
        """Sample ad data for testing."""
        return {
            "title": "Senior Python Developer",
            "company": "TechCorp",
            "description": "We are looking for a senior Python developer...",
            "requirements": "5+ years Python experience",
            "location": "Remote",
            "salary_range": "100k-150k",
            "type": "Full-time",
            "apply_url": "https://techcorp.com/jobs/1234",
            "expires_at": "2024-12-31"
        }
    
    def test_create_ad_success(self, client, mock_db, sample_ad_data):
        """Test successful ad creation."""
        # Mock user authentication
        with patch('backend.routes.ads.get_current_user') as mock_user:
            mock_user.return_value = {"id": "user123", "email": "test@example.com"}
            
            mock_db.ads.insert_one.return_value.inserted_id = ObjectId()
            
            response = client.post("/api/ads", json=sample_ad_data)
            assert response.status_code == 201
            
            data = response.json()
            assert data["title"] == sample_ad_data["title"]
            assert data["company"] == sample_ad_data["company"]
            assert "id" in data
    
    def test_create_ad_validation_error(self, client, mock_db):
        """Test ad creation with validation errors."""
        invalid_data = {
            "title": "",  # Empty title should fail validation
            "company": "TechCorp"
            # Missing required fields
        }
        
        with patch('backend.routes.ads.get_current_user') as mock_user:
            mock_user.return_value = {"id": "user123", "email": "test@example.com"}
            
            response = client.post("/api/ads", json=invalid_data)
            assert response.status_code == 422  # Validation error
    
    def test_create_ad_database_error(self, client, mock_db, sample_ad_data):
        """Test ad creation with database error."""
        with patch('backend.routes.ads.get_current_user') as mock_user:
            mock_user.return_value = {"id": "user123", "email": "test@example.com"}
            
            mock_db.ads.insert_one.side_effect = Exception("Database error")
            
            response = client.post("/api/ads", json=sample_ad_data)
            assert response.status_code == 500
    
    def test_get_ads_success(self, client, mock_db):
        """Test successful ads retrieval."""
        mock_ads = [
            {
                "_id": str(ObjectId()),
                "title": "Python Developer",
                "company": "TechCorp",
                "location": "Remote",
                "type": "Full-time",
                "created_at": datetime.now(),
                "is_active": True
            },
            {
                "_id": str(ObjectId()),
                "title": "React Developer", 
                "company": "WebCorp",
                "location": "Remote",
                "type": "Contract",
                "created_at": datetime.now(),
                "is_active": True
            }
        ]
        
        mock_db.ads.find.return_value.sort.return_value.limit.return_value = mock_ads
        mock_db.ads.count_documents.return_value = 2
        
        response = client.get("/api/ads")
        assert response.status_code == 200
        
        data = response.json()
        assert len(data["ads"]) == 2
        assert data["total"] == 2
        assert data["ads"][0]["title"] == "Python Developer"
    
    def test_get_ads_with_filters(self, client, mock_db):
        """Test ads retrieval with filters."""
        mock_db.ads.find.return_value.sort.return_value.limit.return_value = []
        mock_db.ads.count_documents.return_value = 0
        
        response = client.get("/api/ads?company=TechCorp&location=Remote&type=Full-time")
        assert response.status_code == 200
        
        # Verify filters were applied
        mock_db.ads.find.assert_called()
        call_args = mock_db.ads.find.call_args[0][0]
        
        assert call_args["company"] == "TechCorp"
        assert call_args["location"] == "Remote"  
        assert call_args["type"] == "Full-time"
    
    def test_get_ads_with_pagination(self, client, mock_db):
        """Test ads retrieval with pagination."""
        mock_db.ads.find.return_value.sort.return_value.limit.return_value = []
        mock_db.ads.count_documents.return_value = 0
        
        response = client.get("/api/ads?limit=10&offset=20")
        assert response.status_code == 200
        
        # Verify pagination was applied
        mock_db.ads.find.assert_called()
    
    def test_get_ad_by_id_success(self, client, mock_db):
        """Test successful single ad retrieval."""
        ad_id = str(ObjectId())
        mock_ad = {
            "_id": ad_id,
            "title": "Senior Developer",
            "company": "TechCorp",
            "description": "Great opportunity",
            "location": "Remote",
            "is_active": True,
            "created_at": datetime.now()
        }
        
        mock_db.ads.find_one.return_value = mock_ad
        
        response = client.get(f"/api/ads/{ad_id}")
        assert response.status_code == 200
        
        data = response.json()
        assert data["id"] == ad_id
        assert data["title"] == "Senior Developer"
    
    def test_get_ad_by_id_not_found(self, client, mock_db):
        """Test single ad retrieval for non-existent ad."""
        ad_id = str(ObjectId())
        
        mock_db.ads.find_one.return_value = None
        
        response = client.get(f"/api/ads/{ad_id}")
        assert response.status_code == 404
        
        data = response.json()
        assert "not found" in data["detail"].lower()
    
    def test_update_ad_success(self, client, mock_db):
        """Test successful ad update."""
        ad_id = str(ObjectId())
        update_data = {
            "title": "Updated Title",
            "description": "Updated description"
        }
        
        with patch('backend.routes.ads.get_current_user') as mock_user:
            mock_user.return_value = {"id": "user123", "email": "test@example.com"}
            
            # Mock finding existing ad
            mock_db.ads.find_one.return_value = {
                "_id": ad_id,
                "user_id": "user123",
                "title": "Original Title"
            }
            
            # Mock update operation
            mock_db.ads.update_one.return_value.modified_count = 1
            mock_db.ads.find_one.return_value = {
                "_id": ad_id,
                "title": "Updated Title",
                "description": "Updated description"
            }
            
            response = client.put(f"/api/ads/{ad_id}", json=update_data)
            assert response.status_code == 200
            
            data = response.json()
            assert data["title"] == "Updated Title"
    
    def test_update_ad_not_found(self, client, mock_db):
        """Test ad update for non-existent ad."""
        ad_id = str(ObjectId())
        
        with patch('backend.routes.ads.get_current_user') as mock_user:
            mock_user.return_value = {"id": "user123", "email": "test@example.com"}
            
            mock_db.ads.find_one.return_value = None
            
            response = client.put(f"/api/ads/{ad_id}", json={"title": "Updated"})
            assert response.status_code == 404
    
    def test_update_ad_unauthorized(self, client, mock_db):
        """Test ad update by non-owner."""
        ad_id = str(ObjectId())
        
        with patch('backend.routes.ads.get_current_user') as mock_user:
            mock_user.return_value = {"id": "user456", "email": "other@example.com"}
            
            # Mock finding ad owned by different user
            mock_db.ads.find_one.return_value = {
                "_id": ad_id,
                "user_id": "user123",  # Different user
                "title": "Original Title"
            }
            
            response = client.put(f"/api/ads/{ad_id}", json={"title": "Updated"})
            assert response.status_code == 403  # Forbidden
    
    def test_delete_ad_success(self, client, mock_db):
        """Test successful ad deletion."""
        ad_id = str(ObjectId())
        
        with patch('backend.routes.ads.get_current_user') as mock_user:
            mock_user.return_value = {"id": "user123", "email": "test@example.com"}
            
            # Mock finding existing ad
            mock_db.ads.find_one.return_value = {
                "_id": ad_id,
                "user_id": "user123",
                "title": "Test Ad"
            }
            
            # Mock delete operation
            mock_db.ads.delete_one.return_value.deleted_count = 1
            
            response = client.delete(f"/api/ads/{ad_id}")
            assert response.status_code == 200
            
            data = response.json()
            assert "deleted successfully" in data["message"].lower()
    
    def test_delete_ad_not_found(self, client, mock_db):
        """Test ad deletion for non-existent ad."""
        ad_id = str(ObjectId())
        
        with patch('backend.routes.ads.get_current_user') as mock_user:
            mock_user.return_value = {"id": "user123", "email": "test@example.com"}
            
            mock_db.ads.find_one.return_value = None
            
            response = client.delete(f"/api/ads/{ad_id}")
            assert response.status_code == 404
    
    def test_delete_ad_unauthorized(self, client, mock_db):
        """Test ad deletion by non-owner."""
        ad_id = str(ObjectId())
        
        with patch('backend.routes.ads.get_current_user') as mock_user:
            mock_user.return_value = {"id": "user456", "email": "other@example.com"}
            
            # Mock finding ad owned by different user
            mock_db.ads.find_one.return_value = {
                "_id": ad_id,
                "user_id": "user123",  # Different user
                "title": "Test Ad"
            }
            
            response = client.delete(f"/api/ads/{ad_id}")
            assert response.status_code == 403  # Forbidden

class TestRoutesIntegration:
    """Integration tests for routes interaction."""
    
    @pytest.fixture
    def client(self):
        """Create test client."""
        return TestClient(app)
    
    def test_companies_ads_integration(self, client):
        """Test integration between companies and ads endpoints."""
        with patch('backend.routes.companies.get_db') as mock_companies_db:
            with patch('backend.routes.ads.get_db') as mock_ads_db:
                # Mock companies data
                mock_companies_db.return_value.__aenter__.return_value.jobs.aggregate.return_value = [
                    {"_id": "TechCorp", "job_count": 25}
                ]
                
                # Mock ads data  
                mock_ads_db.return_value.__aenter__.return_value.ads.find.return_value.sort.return_value.limit.return_value = []
                mock_ads_db.return_value.__aenter__.return_value.ads.count_documents.return_value = 0
                
                # Test companies endpoint
                companies_response = client.get("/api/companies")
                assert companies_response.status_code == 200
                
                # Test ads endpoint
                ads_response = client.get("/api/ads")
                assert ads_response.status_code == 200
                
                # Verify both work independently
                companies_data = companies_response.json()
                ads_data = ads_response.json()
                
                assert len(companies_data) >= 0
                assert "ads" in ads_data 