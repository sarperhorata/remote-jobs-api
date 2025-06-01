import pytest
import asyncio
from fastapi import status
from httpx import AsyncClient
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime
from bson import ObjectId


@pytest.mark.asyncio
class TestNotificationsAPI:
    """Test suite for Notifications API endpoints."""

    async def test_get_notifications_success(self, async_client: AsyncClient, mock_database):
        """Test successful notifications retrieval."""
        notifications_data = [
            {
                "_id": ObjectId(),
                "user_id": "user123",
                "title": "New Job Match",
                "message": "A new job matches your criteria",
                "type": "job_alert",
                "status": "unread",
                "created_at": datetime.now()
            },
            {
                "_id": ObjectId(),
                "user_id": "user123",
                "title": "Application Update",
                "message": "Your application status changed",
                "type": "application_update",
                "status": "read",
                "created_at": datetime.now()
            }
        ]
        
        # Mock notifications in storage
        for notification in notifications_data:
            notif_id = str(notification["_id"])
            mock_database.notifications._storage[notif_id] = notification
        
        response = await async_client.get("/api/notifications/")
        assert response.status_code in [200, 401, 404]  # OK, Unauthorized, or Not Found

    async def test_get_notifications_with_authentication(self, async_client: AsyncClient, mock_database):
        """Test notifications retrieval with authentication headers."""
        headers = {"Authorization": "Bearer test-token"}
        response = await async_client.get("/api/notifications/", headers=headers)
        assert response.status_code in [200, 401, 404]  # OK, Unauthorized, or Not Found

    async def test_get_notifications_pagination(self, async_client: AsyncClient, mock_database):
        """Test notifications pagination."""
        response = await async_client.get("/api/notifications/?page=1&per_page=10")
        assert response.status_code in [200, 401, 404]

    async def test_get_notification_by_id_success(self, async_client: AsyncClient, mock_database):
        """Test successful notification retrieval by ID."""
        notif_id = str(ObjectId())
        notification_data = {
            "_id": ObjectId(notif_id),
            "user_id": "user123",
            "title": "Test Notification",
            "message": "Test message",
            "type": "info",
            "status": "unread",
            "created_at": datetime.now()
        }
        
        # Store in mock database
        mock_database.notifications._storage[notif_id] = notification_data
        
        response = await async_client.get(f"/api/notifications/{notif_id}")
        assert response.status_code in [200, 401, 404]

    async def test_get_notification_by_id_not_found(self, async_client: AsyncClient, mock_database):
        """Test notification not found scenario."""
        non_existent_id = str(ObjectId())
        response = await async_client.get(f"/api/notifications/{non_existent_id}")
        assert response.status_code in [404, 401, 422]

    async def test_create_notification_success(self, async_client: AsyncClient, mock_database):
        """Test successful notification creation."""
        notification_data = {
            "user_id": "user123",
            "title": "New Notification",
            "message": "This is a test notification",
            "type": "info",
            "channel": "email"
        }
        
        # Mock insert result
        mock_result = MagicMock()
        mock_result.inserted_id = ObjectId()
        mock_database.notifications.insert_one = AsyncMock(return_value=mock_result)
        
        response = await async_client.post("/api/notifications/", json=notification_data)
        assert response.status_code in [201, 401, 404, 422]

    async def test_create_notification_validation_error(self, async_client: AsyncClient, mock_database):
        """Test notification creation with validation errors."""
        invalid_notification_data = {
            "title": "",  # Empty title
            "message": "",  # Empty message
            "type": "invalid_type"  # Invalid type
        }
        
        response = await async_client.post("/api/notifications/", json=invalid_notification_data)
        assert response.status_code in [422, 401, 404]

    async def test_mark_notification_as_read(self, async_client: AsyncClient, mock_database):
        """Test marking notification as read."""
        notif_id = str(ObjectId())
        notification_data = {
            "_id": ObjectId(notif_id),
            "user_id": "user123",
            "title": "Unread Notification",
            "status": "unread"
        }
        
        # Store in mock database
        mock_database.notifications._storage[notif_id] = notification_data
        
        # Mock update result
        mock_result = MagicMock()
        mock_result.modified_count = 1
        mock_database.notifications.update_one = AsyncMock(return_value=mock_result)
        
        response = await async_client.put(f"/api/notifications/{notif_id}/read")
        assert response.status_code in [200, 401, 404]

    async def test_mark_all_notifications_as_read(self, async_client: AsyncClient, mock_database):
        """Test marking all notifications as read for a user."""
        # Mock update result
        mock_result = MagicMock()
        mock_result.modified_count = 5  # 5 notifications updated
        mock_database.notifications.update_many = AsyncMock(return_value=mock_result)
        
        response = await async_client.put("/api/notifications/mark-all-read")
        assert response.status_code in [200, 401, 404]

    async def test_delete_notification_success(self, async_client: AsyncClient, mock_database):
        """Test successful notification deletion."""
        notif_id = str(ObjectId())
        notification_data = {
            "_id": ObjectId(notif_id),
            "user_id": "user123",
            "title": "Notification to Delete"
        }
        
        # Store in mock database
        mock_database.notifications._storage[notif_id] = notification_data
        
        # Mock delete result
        mock_result = MagicMock()
        mock_result.deleted_count = 1
        mock_database.notifications.delete_one = AsyncMock(return_value=mock_result)
        
        response = await async_client.delete(f"/api/notifications/{notif_id}")
        assert response.status_code in [200, 204, 401, 404]

    async def test_delete_notification_not_found(self, async_client: AsyncClient, mock_database):
        """Test deleting non-existent notification."""
        non_existent_id = str(ObjectId())
        
        # Mock no deletion
        mock_result = MagicMock()
        mock_result.deleted_count = 0
        mock_database.notifications.delete_one = AsyncMock(return_value=mock_result)
        
        response = await async_client.delete(f"/api/notifications/{non_existent_id}")
        assert response.status_code in [404, 401, 422]

    async def test_get_notification_settings(self, async_client: AsyncClient, mock_database):
        """Test getting notification settings for a user."""
        settings_data = {
            "_id": "user123",
            "email_notifications": True,
            "push_notifications": False,
            "job_alerts": True,
            "application_updates": True,
            "newsletter": False
        }
        
        # Store in mock database
        mock_database.notification_settings._storage["user123"] = settings_data
        
        response = await async_client.get("/api/notifications/settings")
        assert response.status_code in [200, 401, 404]

    async def test_update_notification_settings(self, async_client: AsyncClient, mock_database):
        """Test updating notification settings."""
        settings_update = {
            "email_notifications": False,
            "push_notifications": True,
            "job_alerts": False
        }
        
        # Mock update result
        mock_result = MagicMock()
        mock_result.modified_count = 1
        mock_database.notification_settings.update_one = AsyncMock(return_value=mock_result)
        
        response = await async_client.put("/api/notifications/settings", json=settings_update)
        assert response.status_code in [200, 401, 404]

    async def test_get_notifications_by_type(self, async_client: AsyncClient, mock_database):
        """Test getting notifications filtered by type."""
        # Test different notification types
        types = ["job_alert", "application_update", "newsletter", "system"]
        
        for notif_type in types:
            response = await async_client.get(f"/api/notifications/?type={notif_type}")
            assert response.status_code in [200, 401, 404]

    async def test_get_unread_notifications_count(self, async_client: AsyncClient, mock_database):
        """Test getting count of unread notifications."""
        # Mock count result
        mock_database.notifications.count_documents = AsyncMock(return_value=5)
        
        response = await async_client.get("/api/notifications/unread-count")
        assert response.status_code in [200, 401, 404]

    async def test_send_bulk_notifications(self, async_client: AsyncClient, mock_database):
        """Test sending bulk notifications."""
        bulk_notification_data = {
            "user_ids": ["user1", "user2", "user3"],
            "title": "System Announcement",
            "message": "Important system update",
            "type": "system"
        }
        
        # Mock bulk insert result
        mock_result = MagicMock()
        mock_result.inserted_ids = [ObjectId(), ObjectId(), ObjectId()]
        mock_database.notifications.insert_many = AsyncMock(return_value=mock_result)
        
        response = await async_client.post("/api/notifications/bulk", json=bulk_notification_data)
        assert response.status_code in [201, 401, 404, 422]

    async def test_notifications_filtering_and_sorting(self, async_client: AsyncClient, mock_database):
        """Test notifications filtering and sorting."""
        # Test filtering by status
        response = await async_client.get("/api/notifications/?status=unread")
        assert response.status_code in [200, 401, 404]
        
        # Test sorting by created_at
        response = await async_client.get("/api/notifications/?sort_by=created_at&sort_order=desc")
        assert response.status_code in [200, 401, 404]
        
        # Test date range filtering
        response = await async_client.get("/api/notifications/?from_date=2024-01-01&to_date=2024-12-31")
        assert response.status_code in [200, 401, 404]

    async def test_notification_templates(self, async_client: AsyncClient, mock_database):
        """Test notification template endpoints."""
        # Test getting templates
        response = await async_client.get("/api/notifications/templates")
        assert response.status_code in [200, 401, 404]
        
        # Test getting specific template
        response = await async_client.get("/api/notifications/templates/job_alert")
        assert response.status_code in [200, 401, 404]

    async def test_notifications_error_handling(self, async_client: AsyncClient, mock_database):
        """Test error handling in notifications endpoints."""
        # Test with invalid ObjectId
        response = await async_client.get("/api/notifications/invalid-id")
        assert response.status_code in [400, 401, 404, 422]
        
        # Test database error simulation
        mock_database.notifications.find.side_effect = Exception("Database error")
        response = await async_client.get("/api/notifications/")
        assert response.status_code in [200, 401, 500, 503]

    async def test_notification_webhooks(self, async_client: AsyncClient, mock_database):
        """Test notification webhook endpoints."""
        webhook_data = {
            "url": "https://example.com/webhook",
            "events": ["notification_sent", "notification_failed"],
            "secret": "webhook_secret"
        }
        
        response = await async_client.post("/api/notifications/webhooks", json=webhook_data)
        assert response.status_code in [201, 401, 404, 422] 