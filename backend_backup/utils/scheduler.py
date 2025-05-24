import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from datetime import datetime, timedelta
from .job_archiver import archive_old_jobs
from .cronjob import wake_up_render

logger = logging.getLogger(__name__)

def setup_scheduler():
    """
    Set up the scheduler with jobs for archiving old jobs and keeping the service alive.
    """
    scheduler = AsyncIOScheduler()
    
    # Schedule job archiving to run daily at midnight
    scheduler.add_job(
        archive_old_jobs,
        CronTrigger(hour=0, minute=0),
        id='archive_old_jobs',
        name='Archive old jobs daily at midnight',
        replace_existing=True
    )
    
    # Schedule wake-up job to run every 14 minutes
    scheduler.add_job(
        wake_up_render,
        IntervalTrigger(minutes=14),
        id='wake_up_render',
        name='Wake up Render service every 14 minutes',
        replace_existing=True
    )
    
    scheduler.start()
    logger.info("Scheduler started with jobs: archive_old_jobs (daily at midnight) and wake_up_render (every 14 minutes)")
    
    return scheduler 