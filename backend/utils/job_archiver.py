import logging
import os
from datetime import datetime, timedelta
from typing import Any, Dict, List

from bson import ObjectId
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from models.job import Job
from utils.db import async_jobs

from database.db import get_async_db

logger = logging.getLogger(__name__)


async def archive_old_jobs():
    """
    Archive jobs older than 30 days to Google Sheets and remove them from the database.
    """
    try:
        # Get jobs older than 30 days
        cutoff_date = datetime.utcnow() - timedelta(days=30)
        db = await get_async_db()
        old_jobs_cursor = db.jobs.find({"created_at": {"$lt": cutoff_date}})
        old_jobs = await old_jobs_cursor.to_list(length=None)

        if not old_jobs:
            logger.info("No old jobs to archive")
            return

        # Archive to Google Sheets
        archived_count = await archive_to_sheets(old_jobs)

        # Delete archived jobs from database
        job_ids = [job["_id"] for job in old_jobs]
        await db.jobs.delete_many({"_id": {"$in": job_ids}})

        logger.info(f"Successfully archived {archived_count} old jobs")

    except Exception as e:
        logger.error(f"Error archiving old jobs: {str(e)}")
        raise


async def archive_to_sheets(jobs):
    """
    Archive jobs to Google Sheets.
    """
    try:
        # Get Google Sheets credentials from environment
        creds = Credentials.from_authorized_user_info(
            {
                "client_id": os.getenv("GOOGLE_CLIENT_ID"),
                "client_secret": os.getenv("GOOGLE_CLIENT_SECRET"),
                "refresh_token": os.getenv("GOOGLE_REFRESH_TOKEN"),
            }
        )

        service = build("sheets", "v4", credentials=creds)
        spreadsheet_id = os.getenv("GOOGLE_SHEETS_ID")

        # Prepare job data for sheets
        values = []
        for job in jobs:
            values.append(
                [
                    job.get("title", ""),
                    job.get("company", ""),
                    job.get("location", ""),
                    job.get("description", ""),
                    job.get("created_at", datetime.utcnow()).isoformat(),
                    job.get("url", ""),
                ]
            )

        # Append to sheets
        body = {"values": values}

        result = (
            service.spreadsheets()
            .values()
            .append(
                spreadsheetId=spreadsheet_id,
                range="Archived Jobs!A:F",
                valueInputOption="RAW",
                insertDataOption="INSERT_ROWS",
                body=body,
            )
            .execute()
        )

        return len(values)

    except HttpError as e:
        logger.error(f"Google Sheets API error: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Error archiving to Google Sheets: {str(e)}")
        raise


async def get_archived_jobs(skip: int = 0, limit: int = 10) -> List[Dict[str, Any]]:
    """
    Retrieves archived jobs with pagination.
    """
    try:
        cursor = (
            async_jobs.find({"is_archived": True})
            .sort("archived_at", -1)
            .skip(skip)
            .limit(limit)
        )
        archived_jobs = await cursor.to_list(length=limit)

        # Convert ObjectId to string for JSON serialization
        for job in archived_jobs:
            job["_id"] = str(job["_id"])

        return archived_jobs
    except Exception as e:
        logger.error(f"Error retrieving archived jobs: {str(e)}")
        return []


async def restore_job(job_id: str) -> bool:
    """
    Restores an archived job.
    """
    try:
        result = await async_jobs.update_one(
            {"_id": ObjectId(job_id)},
            {"$set": {"is_archived": False, "archived_at": None}},
        )

        return result.modified_count > 0
    except Exception as e:
        logger.error(f"Error restoring job {job_id}: {str(e)}")
        return False


async def get_job_count(include_archived: bool = False) -> int:
    """
    Gets the total count of jobs, optionally including archived ones.
    """
    try:
        query = {} if include_archived else {"is_archived": {"$ne": True}}
        return await async_jobs.count_documents(query)
    except Exception as e:
        logger.error(f"Error counting jobs: {str(e)}")
        return 0
