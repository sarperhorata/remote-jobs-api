import logging
from datetime import datetime
from typing import List, Optional

from bson import ObjectId

from backend.database.db import get_db
from backend.models.user_application import (UserApplication,
                                             UserApplicationCreate,
                                             UserApplicationResponse,
                                             UserApplicationUpdate)

logger = logging.getLogger(__name__)


class UserApplicationService:
    """Service for managing user job applications"""

    def __init__(self):
        self.db = None
        self.collection = None

    async def _get_collection(self):
        """Get the user applications collection"""
        if self.collection is None:
            self.db = await get_db()
            self.collection = self.db.user_applications
        return self.collection

    async def create_application(
        self, application_data: UserApplicationCreate
    ) -> UserApplicationResponse:
        """Create a new job application"""
        try:
            collection = await self._get_collection()

            # Create application document
            application = UserApplication(**application_data.model_dump())
            application_dict = application.model_dump()

            # Insert into database
            result = await collection.insert_one(application_dict)

            # Fetch and return the created application
            created_application = await collection.find_one({"_id": result.inserted_id})
            if not created_application:
                raise Exception("Failed to retrieve created application")

            return UserApplicationResponse(**created_application)

        except Exception as e:
            logger.error(f"Error creating application: {str(e)}")
            raise

    async def get_user_application(
        self, user_id: str, job_id: str
    ) -> Optional[UserApplicationResponse]:
        """Get user's application for a specific job"""
        try:
            collection = await self._get_collection()

            application = await collection.find_one(
                {"user_id": user_id, "job_id": job_id}
            )

            if application:
                return UserApplicationResponse(**application)
            return None

        except Exception as e:
            logger.error(f"Error fetching user application: {str(e)}")
            raise

    async def get_user_applications(
        self,
        user_id: str,
        skip: int = 0,
        limit: int = 100,
        status_filter: Optional[str] = None,
    ) -> List[UserApplicationResponse]:
        """Get all applications for a user"""
        try:
            collection = await self._get_collection()

            query = {"user_id": user_id}

            if status_filter:
                query["status"] = status_filter

            cursor = (
                collection.find(query).sort("applied_at", -1).skip(skip).limit(limit)
            )
            applications = []

            async for app in cursor:
                applications.append(UserApplicationResponse(**app))

            return applications

        except Exception as e:
            logger.error(f"Error fetching user applications: {str(e)}")
            raise

    async def get_applied_job_ids(self, user_id: str) -> List[str]:
        """Get list of job IDs that user has applied to"""
        try:
            collection = await self._get_collection()

            cursor = collection.find({"user_id": user_id}, {"job_id": 1, "_id": 0})

            job_ids = []
            async for app in cursor:
                job_ids.append(app["job_id"])

            return job_ids

        except Exception as e:
            logger.error(f"Error fetching applied job IDs: {str(e)}")
            raise

    async def get_application_by_id(
        self, application_id: str
    ) -> Optional[UserApplicationResponse]:
        """Get application by ID"""
        try:
            collection = await self._get_collection()

            application = await collection.find_one({"_id": ObjectId(application_id)})

            if application:
                return UserApplicationResponse(**application)
            return None

        except Exception as e:
            logger.error(f"Error fetching application by ID: {str(e)}")
            raise

    async def update_application(
        self, application_id: str, update_data: UserApplicationUpdate
    ) -> UserApplicationResponse:
        """Update an application"""
        try:
            collection = await self._get_collection()

            # Build update document
            update_dict = {}
            for field, value in update_data.model_dump(exclude_none=True).items():
                update_dict[field] = value

            if update_dict:
                update_dict["updated_at"] = datetime.utcnow()

                result = await collection.update_one(
                    {"_id": ObjectId(application_id)}, {"$set": update_dict}
                )

                if result.modified_count == 0:
                    raise Exception("No application was updated")

            # Fetch and return updated application
            updated_application = await collection.find_one(
                {"_id": ObjectId(application_id)}
            )
            if not updated_application:
                raise Exception("Failed to retrieve updated application")

            return UserApplicationResponse(**updated_application)

        except Exception as e:
            logger.error(f"Error updating application: {str(e)}")
            raise

    async def delete_application(self, application_id: str) -> bool:
        """Delete an application"""
        try:
            collection = await self._get_collection()

            result = await collection.delete_one({"_id": ObjectId(application_id)})
            return result.deleted_count > 0

        except Exception as e:
            logger.error(f"Error deleting application: {str(e)}")
            raise

    async def mark_as_auto_applied(self, user_id: str, job_id: str) -> bool:
        """Mark an application as auto-applied"""
        try:
            collection = await self._get_collection()

            result = await collection.update_one(
                {"user_id": user_id, "job_id": job_id},
                {"$set": {"auto_apply_used": True, "updated_at": datetime.utcnow()}},
            )
            return result.modified_count > 0

        except Exception as e:
            logger.error(f"Error marking application as auto-applied: {str(e)}")
            raise

    async def get_application_stats(self, user_id: str) -> dict:
        """Get user's application statistics"""
        try:
            collection = await self._get_collection()

            pipeline = [
                {"$match": {"user_id": user_id}},
                {"$group": {"_id": "$status", "count": {"$sum": 1}}},
            ]

            cursor = collection.aggregate(pipeline)
            stats = {"total": 0}

            async for stat in cursor:
                stats[stat["_id"]] = stat["count"]
                stats["total"] += stat["count"]

            return stats

        except Exception as e:
            logger.error(f"Error fetching application stats: {str(e)}")
            raise


# Lazy initialization function
_user_application_service = None


def get_user_application_service() -> UserApplicationService:
    """Get or create user application service instance"""
    global _user_application_service
    if _user_application_service is None:
        _user_application_service = UserApplicationService()
    return _user_application_service
