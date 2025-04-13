import logging
import os
import json
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import sqlite3
import asyncio
from bson import ObjectId

# Düzgün modül yolunu kullanalım
from models.models import Job

logger = logging.getLogger(__name__)

# Arşiv dizini
ARCHIVE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "archive")

async def archive_old_jobs():
    """
    Archive jobs older than 30 days to Google Sheets and remove them from the database.
    """
    try:
        # Get jobs older than 30 days
        cutoff_date = datetime.utcnow() - timedelta(days=30)
        
        from utils.db import async_jobs, db
        
        # Basitleştirilmiş işlem: sadece eski jobları arşivlenmiş olarak işaretle
        try:
            # Eskiden MongoDB'de saklanan jobs'lar artık SQLite'ta
            old_jobs = db.fetch_all(
                "SELECT * FROM jobs WHERE created_at < ?", 
                [cutoff_date.isoformat()]
            )
            
            if not old_jobs:
                logger.info("No old jobs to archive")
                return
            
            # Basitleştirilmiş arşivleme
            for job in old_jobs:
                job_data = dict(job)
                job_data["is_archived"] = 1
                job_data["archived_at"] = datetime.utcnow().isoformat()
                db.update("jobs", 
                          {"is_archived": 1, "archived_at": job_data["archived_at"]}, 
                          "id = ?", [job_data["id"]])
            
            logger.info(f"Successfully archived {len(old_jobs)} old jobs")
            
        except Exception as e:
            logger.error(f"Error archiving old jobs in database: {e}")
            raise
        
    except Exception as e:
        logger.error(f"Error archiving old jobs: {str(e)}")

async def archive_to_sheets(jobs):
    """
    Archive jobs to Google Sheets.
    """
    try:
        # Get Google Sheets credentials from environment
        creds = Credentials.from_authorized_user_info({
            "client_id": os.getenv("GOOGLE_CLIENT_ID"),
            "client_secret": os.getenv("GOOGLE_CLIENT_SECRET"),
            "refresh_token": os.getenv("GOOGLE_REFRESH_TOKEN")
        })
        
        service = build('sheets', 'v4', credentials=creds)
        spreadsheet_id = os.getenv("GOOGLE_SHEETS_ID")
        
        # Prepare job data for sheets
        values = []
        for job in jobs:
            values.append([
                job.title,
                job.company,
                job.location,
                job.description,
                job.created_at.isoformat(),
                job.url
            ])
        
        # Append to sheets
        body = {
            'values': values
        }
        
        result = service.spreadsheets().values().append(
            spreadsheetId=spreadsheet_id,
            range='Archived Jobs!A:F',
            valueInputOption='RAW',
            insertDataOption='INSERT_ROWS',
            body=body
        ).execute()
        
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
        from utils.db import db
        
        query = "SELECT * FROM jobs WHERE is_archived = 1 ORDER BY archived_at DESC LIMIT ? OFFSET ?"
        rows = db.fetch_all(query, [limit, skip])
        
        # Sözlüğe dönüştür
        archived_jobs = [dict(job) for job in rows]
        
        return archived_jobs
    except Exception as e:
        logger.error(f"Error retrieving archived jobs: {str(e)}")
        return []

async def restore_job(job_id: int) -> bool:
    """
    Restores an archived job.
    """
    try:
        from utils.db import db
        
        result = db.update(
            "jobs",
            {"is_archived": 0, "archived_at": None},
            "id = ?", [job_id]
        )
        
        return result > 0
    except Exception as e:
        logger.error(f"Error restoring job {job_id}: {str(e)}")
        return False

async def get_job_count(include_archived: bool = False) -> int:
    """
    Gets the total count of jobs, optionally including archived ones.
    """
    try:
        from utils.db import db
        
        query = "SELECT COUNT(*) as count FROM jobs"
        if not include_archived:
            query += " WHERE is_archived = 0 OR is_archived IS NULL"
            
        result = db.fetch_one(query)
        return result["count"] if result else 0
    except Exception as e:
        logger.error(f"Error counting jobs: {str(e)}")
        return 0 