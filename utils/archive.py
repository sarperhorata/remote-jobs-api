from datetime import datetime, timedelta
import logging
from typing import List, Dict, Any
from ..models.job import Job
from ..database import get_database
from ..config import settings
from .sheets import sheets_archiver

logger = logging.getLogger(__name__)

async def archive_old_jobs() -> None:
    """
    Archive jobs that are older than 30 days to Google Sheets.
    """
    try:
        db = await get_database()
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        
        # Find old jobs
        old_jobs = await db.jobs.find({
            "created_at": {"$lt": thirty_days_ago},
            "archived": {"$ne": True}
        }).to_list(length=None)
        
        if not old_jobs:
            logger.info("No old jobs to archive")
            return
            
        # Archive to Google Sheets
        archived_count = 0
        for job in old_jobs:
            try:
                # Add to Google Sheets
                success = await sheets_archiver.archive_job(job)
                
                if success:
                    # Mark as archived in database
                    await db.jobs.update_one(
                        {"_id": job["_id"]},
                        {"$set": {"archived": True, "archived_at": datetime.utcnow()}}
                    )
                    archived_count += 1
                else:
                    logger.warning(f"Failed to archive job {job['_id']} to Google Sheets")
                
            except Exception as e:
                logger.error(f"Failed to archive job {job['_id']}: {str(e)}")
                continue
                
        logger.info(f"Successfully archived {archived_count} old jobs")
        
    except Exception as e:
        logger.error(f"Error in archive_old_jobs: {str(e)}")
        raise

async def add_to_sheets(job: Dict[str, Any]) -> None:
    """
    Add a job to Google Sheets archive.
    """
    try:
        # TODO: Implement Google Sheets integration
        # This will be implemented when we have the Google Sheets API credentials
        pass
        
    except Exception as e:
        logger.error(f"Error adding job to sheets: {str(e)}")
        raise 