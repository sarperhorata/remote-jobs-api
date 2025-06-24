import pytest
from httpx import AsyncClient
from unittest.mock import AsyncMock, patch

from backend.main import app

class TestSupportAPI:
    """Test suite for support API endpoints"""
    
    @pytest.fixture
    async def client(self):
        """Create test client"""
        async with AsyncClient(app=app, base_url="http://test") as ac:
            yield ac
    
    @pytest.fixture
    def mock_user(self):
        """Mock authenticated user"""
        return {
            "_id": "test_user_id",
            "email": "test@example.com",
            "name": "Test User"
        }
    
    async def test_create_support_ticket(self, client, mock_user):
        """Test creating a support ticket"""
        ticket_data = {
            "subject": "Cannot apply to jobs",
            "message": "I'm having trouble applying to jobs through the platform",
            "category": "technical",
            "priority": "medium"
        }
        
        with patch('backend.routes.support.get_current_user_dependency', return_value=mock_user):
            response = await client.post("/api/support/tickets", json=ticket_data)
        
        assert response.status_code == 201
        data = response.json()
        assert "ticket_id" in data
        assert data["message"] == "Support ticket created successfully"
        assert data["status"] == "open"
    
    async def test_create_support_ticket_validation(self, client, mock_user):
        """Test support ticket validation"""
        # Test missing required fields
        invalid_data = {
            "message": "Help me"
        }
        
        with patch('backend.routes.support.get_current_user_dependency', return_value=mock_user):
            response = await client.post("/api/support/tickets", json=invalid_data)
        
        assert response.status_code == 422  # Validation error
    
    async def test_get_user_support_tickets(self, client, mock_user):
        """Test getting user's support tickets"""
        with patch('backend.routes.support.get_current_user_dependency', return_value=mock_user):
            response = await client.get("/api/support/tickets")
        
        assert response.status_code == 200
        data = response.json()
        assert "tickets" in data
        assert "total" in data
        assert isinstance(data["tickets"], list)
    
    async def test_get_specific_support_ticket(self, client, mock_user):
        """Test getting a specific support ticket"""
        ticket_id = "ticket_123"
        
        with patch('backend.routes.support.get_current_user_dependency', return_value=mock_user):
            response = await client.get(f"/api/support/tickets/{ticket_id}")
        
        assert response.status_code in [200, 404]  # Depends on if ticket exists
    
    async def test_update_support_ticket(self, client, mock_user):
        """Test updating a support ticket"""
        ticket_id = "ticket_123"
        update_data = {
            "message": "Additional information: This happens every time I try to apply",
            "status": "pending"
        }
        
        with patch('backend.routes.support.get_current_user_dependency', return_value=mock_user):
            response = await client.put(f"/api/support/tickets/{ticket_id}", json=update_data)
        
        assert response.status_code in [200, 404]  # Depends on if ticket exists
    
    async def test_support_categories(self, client):
        """Test getting support categories"""
        response = await client.get("/api/support/categories")
        
        assert response.status_code == 200
        data = response.json()
        assert "categories" in data
        assert isinstance(data["categories"], list)
        
        # Check if common categories exist
        category_names = [cat["name"] for cat in data["categories"]]
        expected_categories = ["technical", "billing", "account", "general"]
        for category in expected_categories:
            assert category in category_names
    
    async def test_support_faq(self, client):
        """Test getting FAQ"""
        response = await client.get("/api/support/faq")
        
        assert response.status_code == 200
        data = response.json()
        assert "faqs" in data
        assert isinstance(data["faqs"], list)
        
        # Check FAQ structure
        if data["faqs"]:
            faq = data["faqs"][0]
            assert "question" in faq
            assert "answer" in faq
            assert "category" in faq
    
    async def test_support_contact_info(self, client):
        """Test getting contact information"""
        response = await client.get("/api/support/contact")
        
        assert response.status_code == 200
        data = response.json()
        assert "email" in data
        assert "response_time" in data
        assert "available_hours" in data
    
    async def test_support_ticket_unauthorized(self, client):
        """Test support ticket access without authentication"""
        response = await client.get("/api/support/tickets")
        
        assert response.status_code in [401, 403]
    
    async def test_support_ticket_priority_levels(self, client, mock_user):
        """Test different priority levels for support tickets"""
        priorities = ["low", "medium", "high", "urgent"]
        
        for priority in priorities:
            ticket_data = {
                "subject": f"Test ticket - {priority} priority",
                "message": "This is a test message",
                "category": "technical",
                "priority": priority
            }
            
            with patch('backend.routes.support.get_current_user_dependency', return_value=mock_user):
                response = await client.post("/api/support/tickets", json=ticket_data)
            
            assert response.status_code == 201
    
    async def test_support_ticket_file_attachment(self, client, mock_user):
        """Test support ticket with file attachment"""
        ticket_data = {
            "subject": "Bug report with screenshot",
            "message": "See attached screenshot of the error",
            "category": "technical",
            "priority": "medium",
            "attachments": ["screenshot.png", "error_log.txt"]
        }
        
        with patch('backend.routes.support.get_current_user_dependency', return_value=mock_user):
            response = await client.post("/api/support/tickets", json=ticket_data)
        
        assert response.status_code == 201
        data = response.json()
        if "attachments" in data:
            assert isinstance(data["attachments"], list)
    
    async def test_support_ticket_status_transitions(self, client, mock_user):
        """Test valid status transitions for support tickets"""
        valid_statuses = ["open", "pending", "resolved", "closed"]
        
        for status in valid_statuses:
            update_data = {"status": status}
            
            with patch('backend.routes.support.get_current_user_dependency', return_value=mock_user):
                response = await client.put("/api/support/tickets/test_id", json=update_data)
            
            # Should not fail validation (might return 404 if ticket doesn't exist)
            assert response.status_code in [200, 404]
    
    async def test_support_metrics(self, client):
        """Test support metrics endpoint"""
        response = await client.get("/api/support/metrics")
        
        assert response.status_code == 200
        data = response.json()
        
        expected_metrics = ["total_tickets", "open_tickets", "avg_response_time", "satisfaction_rating"]
        for metric in expected_metrics:
            assert metric in data
    
    async def test_bulk_support_actions(self, client, mock_user):
        """Test bulk actions on support tickets"""
        bulk_data = {
            "ticket_ids": ["ticket_1", "ticket_2", "ticket_3"],
            "action": "mark_resolved",
            "reason": "Bulk resolution for solved issues"
        }
        
        with patch('backend.routes.support.get_current_user_dependency', return_value=mock_user):
            response = await client.post("/api/support/tickets/bulk-action", json=bulk_data)
        
        assert response.status_code in [200, 400]  # Depends on implementation
    
    async def test_support_search(self, client, mock_user):
        """Test searching support tickets"""
        search_params = {
            "q": "cannot apply",
            "status": "open",
            "category": "technical",
            "priority": "high"
        }
        
        with patch('backend.routes.support.get_current_user_dependency', return_value=mock_user):
            response = await client.get("/api/support/tickets/search", params=search_params)
        
        assert response.status_code == 200
        data = response.json()
        assert "tickets" in data
        assert "total" in data
    
    async def test_support_ticket_comments(self, client, mock_user):
        """Test adding comments to support tickets"""
        ticket_id = "ticket_123"
        comment_data = {
            "message": "I've tried the suggested solution but it didn't work",
            "is_internal": False
        }
        
        with patch('backend.routes.support.get_current_user_dependency', return_value=mock_user):
            response = await client.post(f"/api/support/tickets/{ticket_id}/comments", json=comment_data)
        
        assert response.status_code in [201, 404]  # Depends on if ticket exists
    
    async def test_support_ticket_escalation(self, client, mock_user):
        """Test escalating a support ticket"""
        ticket_id = "ticket_123"
        escalation_data = {
            "reason": "Customer is frustrated and needs immediate attention",
            "escalate_to": "supervisor"
        }
        
        with patch('backend.routes.support.get_current_user_dependency', return_value=mock_user):
            response = await client.post(f"/api/support/tickets/{ticket_id}/escalate", json=escalation_data)
        
        assert response.status_code in [200, 404]  # Depends on if ticket exists
    
    async def test_support_satisfaction_survey(self, client, mock_user):
        """Test submitting satisfaction survey"""
        ticket_id = "ticket_123"
        survey_data = {
            "rating": 4,
            "feedback": "Good support, resolved my issue quickly",
            "would_recommend": True
        }
        
        with patch('backend.routes.support.get_current_user_dependency', return_value=mock_user):
            response = await client.post(f"/api/support/tickets/{ticket_id}/survey", json=survey_data)
        
        assert response.status_code in [200, 404]  # Depends on if ticket exists 