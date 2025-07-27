"""
Job Notification Service

This service handles job matching and notification creation for users
when new jobs match their saved search criteria.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase

from backend.models.models import UserNotificationCreate
from backend.services.ai_job_matching_service import AIJobMatchingService

logger = logging.getLogger(__name__)


class JobNotificationService:
    """
    Service for creating job notifications when new jobs match user preferences
    """

    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.ai_matching_service = AIJobMatchingService(db)

    async def process_new_jobs_for_notifications(
        self, new_jobs: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Process new jobs and create notifications for matching users

        Args:
            new_jobs: List of newly added jobs

        Returns:
            Dictionary with notification statistics
        """
        try:
            logger.info(f"Processing {len(new_jobs)} new jobs for notifications")

            total_notifications = 0
            matched_users = set()

            for job in new_jobs:
                # Find users who might be interested in this job
                matching_users = await self._find_matching_users(job)

                for user_id in matching_users:
                    # Check if user has notification preferences enabled
                    if await self._should_send_notification(user_id, job):
                        # Create notification
                        notification_created = await self._create_job_notification(
                            user_id, job
                        )
                        if notification_created:
                            total_notifications += 1
                            matched_users.add(user_id)

                        # Send desktop notification if user is online
                        await self._send_desktop_notification(user_id, job)

            logger.info(
                f"Created {total_notifications} notifications for {len(matched_users)} users"
            )

            return {
                "total_jobs_processed": len(new_jobs),
                "total_notifications_created": total_notifications,
                "unique_users_notified": len(matched_users),
                "processed_at": datetime.utcnow().isoformat(),
            }

        except Exception as e:
            logger.error(f"Error processing new jobs for notifications: {str(e)}")
            return {
                "error": str(e),
                "total_jobs_processed": 0,
                "total_notifications_created": 0,
                "unique_users_notified": 0,
            }

    async def _find_matching_users(self, job: Dict[str, Any]) -> List[str]:
        """
        Find users whose preferences match the job

        Args:
            job: Job data

        Returns:
            List of user IDs that match the job
        """
        try:
            matching_users = []

            # Get all active users with job preferences
            users_cursor = self.db.users.find(
                {
                    "is_active": True,
                    "$or": [
                        {"preferred_job_titles": {"$exists": True, "$ne": []}},
                        {"preferred_skills": {"$exists": True, "$ne": []}},
                        {"preferred_locations": {"$exists": True, "$ne": []}},
                        {"preferred_companies": {"$exists": True, "$ne": []}},
                    ],
                }
            )

            async for user in users_cursor:
                user_id = str(user["_id"])

                # Check if job matches user preferences
                if await self._job_matches_user_preferences(job, user):
                    matching_users.append(user_id)

            return matching_users

        except Exception as e:
            logger.error(f"Error finding matching users: {str(e)}")
            return []

    async def _job_matches_user_preferences(
        self, job: Dict[str, Any], user: Dict[str, Any]
    ) -> bool:
        """
        Check if a job matches user preferences

        Args:
            job: Job data
            user: User data with preferences

        Returns:
            True if job matches user preferences
        """
        try:
            # Check job title preferences
            preferred_titles = user.get("preferred_job_titles", [])
            if preferred_titles:
                job_title = job.get("title", "").lower()
                title_match = any(
                    title.lower() in job_title for title in preferred_titles
                )
                if not title_match:
                    return False

            # Check location preferences
            preferred_locations = user.get("preferred_locations", [])
            if preferred_locations:
                job_location = job.get("location", "").lower()
                location_match = any(
                    loc.lower() in job_location for loc in preferred_locations
                )
                if not location_match and job.get("remote_type", "").lower() not in [
                    "remote",
                    "hybrid",
                ]:
                    return False

            # Check company preferences
            preferred_companies = user.get("preferred_companies", [])
            if preferred_companies:
                job_company = job.get("company", "").lower()
                company_match = any(
                    company.lower() in job_company for company in preferred_companies
                )
                if not company_match:
                    return False

            # Check skills preferences
            preferred_skills = user.get("preferred_skills", [])
            if preferred_skills:
                job_description = job.get("description", "").lower()
                skills_match = any(
                    skill.lower() in job_description for skill in preferred_skills
                )
                if not skills_match:
                    return False

            # Check work type preferences
            preferred_work_types = user.get("preferred_work_types", ["remote"])
            job_work_type = job.get("remote_type", "").lower()
            work_type_match = any(
                work_type.lower() in job_work_type for work_type in preferred_work_types
            )
            if not work_type_match:
                return False

            return True

        except Exception as e:
            logger.error(f"Error checking job preferences match: {str(e)}")
            return False

    async def _should_send_notification(
        self, user_id: str, job: Dict[str, Any]
    ) -> bool:
        """
        Check if notification should be sent to user

        Args:
            user_id: User ID
            job: Job data

        Returns:
            True if notification should be sent
        """
        try:
            # Check if user has notification settings
            user = await self.db.users.find_one({"_id": ObjectId(user_id)})
            if not user:
                return False

            # Check if notifications are enabled
            notification_settings = user.get("notification_settings", {})
            if not notification_settings.get("job_alerts", True):
                return False

            # Check if user has already been notified about this job recently
            recent_notification = await self.db.user_notifications.find_one(
                {
                    "user_id": user_id,
                    "metadata.job_id": str(job["_id"]),
                    "created_at": {"$gte": datetime.utcnow() - timedelta(hours=24)},
                }
            )

            if recent_notification:
                return False

            return True

        except Exception as e:
            logger.error(f"Error checking notification settings: {str(e)}")
            return False

    async def _create_job_notification(self, user_id: str, job: Dict[str, Any]) -> bool:
        """
        Create a job notification for user

        Args:
            user_id: User ID
            job: Job data

        Returns:
            True if notification was created successfully
        """
        try:
            # Create notification data
            notification_data = UserNotificationCreate(
                user_id=user_id,
                title=f"New Job: {job.get('title', 'Unknown Position')}",
                message=f"A new {job.get('remote_type', 'remote')} position at {job.get('company', 'Unknown Company')} matches your preferences.",
                notification_type="info",
                category="job",
                action_url=f"/jobs/{job['_id']}",
                action_text="View Job",
                metadata={
                    "job_id": str(job["_id"]),
                    "job_title": job.get("title"),
                    "company": job.get("company"),
                    "location": job.get("location"),
                    "remote_type": job.get("remote_type"),
                },
            )

            # Insert notification
            notifications_col = self.db["user_notifications"]
            notification_dict = notification_data.model_dump()
            notification_dict["created_at"] = datetime.utcnow()

            result = await notifications_col.insert_one(notification_dict)

            if result.inserted_id:
                logger.info(
                    f"Created job notification for user {user_id}, job {job['_id']}"
                )
                return True
            else:
                logger.error(f"Failed to create notification for user {user_id}")
                return False

        except Exception as e:
            logger.error(f"Error creating job notification: {str(e)}")
            return False

    async def _send_desktop_notification(
        self, user_id: str, job: Dict[str, Any]
    ) -> bool:
        """
        Send desktop notification to user (if they're online)

        Args:
            user_id: User ID
            job: Job data

        Returns:
            True if notification was sent
        """
        try:
            # This would integrate with WebSocket or Server-Sent Events
            # For now, we'll just log the intent
            logger.info(
                f"Would send desktop notification to user {user_id} for job {job['_id']}"
            )

            # TODO: Implement WebSocket notification
            # await websocket_manager.send_to_user(user_id, {
            #     "type": "job_notification",
            #     "data": {
            #         "title": f"New Job: {job.get('title')}",
            #         "body": f"New position at {job.get('company')}",
            #         "job_id": str(job["_id"])
            #     }
            # })

            return True

        except Exception as e:
            logger.error(f"Error sending desktop notification: {str(e)}")
            return False

    async def get_user_notification_stats(self, user_id: str) -> Dict[str, Any]:
        """
        Get notification statistics for a user

        Args:
            user_id: User ID

        Returns:
            Dictionary with notification statistics
        """
        try:
            notifications_col = self.db["user_notifications"]

            # Get total notifications
            total_notifications = await notifications_col.count_documents(
                {"user_id": user_id}
            )

            # Get unread notifications
            unread_notifications = await notifications_col.count_documents(
                {"user_id": user_id, "is_read": False}
            )

            # Get job notifications count
            job_notifications = await notifications_col.count_documents(
                {"user_id": user_id, "category": "job"}
            )

            # Get recent notifications (last 7 days)
            week_ago = datetime.utcnow() - timedelta(days=7)
            recent_notifications = await notifications_col.count_documents(
                {"user_id": user_id, "created_at": {"$gte": week_ago}}
            )

            return {
                "total_notifications": total_notifications,
                "unread_notifications": unread_notifications,
                "job_notifications": job_notifications,
                "recent_notifications": recent_notifications,
            }

        except Exception as e:
            logger.error(f"Error getting notification stats: {str(e)}")
            return {
                "total_notifications": 0,
                "unread_notifications": 0,
                "job_notifications": 0,
                "recent_notifications": 0,
            }
