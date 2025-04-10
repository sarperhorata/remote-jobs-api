import asyncio
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import time

from models.models import Monitor, Website, Job, ChangeLog
from crawler.job_crawler import JobCrawler
from notification.notification_manager import NotificationManager

logger = logging.getLogger(__name__)

class MonitorManager:
    """
    Class that manages job listing monitors.
    """
    
    def __init__(self):
        self.job_crawler = JobCrawler()
        self.notification_manager = NotificationManager()
        self.running = False
        self.monitors = {}  # monitor_id -> Monitor
        self.monitor_tasks = {}  # monitor_id -> asyncio.Task
    
    async def start(self):
        """
        Starts all monitors
        """
        logger.info("Starting monitor manager")
        self.running = True
        await self._load_monitors()
        await self._start_monitors()
    
    async def stop(self):
        """
        Stops all monitors
        """
        logger.info("Stopping monitor manager")
        self.running = False
        for monitor_id, task in self.monitor_tasks.items():
            if not task.done():
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    logger.info(f"Monitor task {monitor_id} cancelled")
        self.monitor_tasks = {}
    
    async def _load_monitors(self):
        """
        Loads all active monitors from the database
        """
        # Database operations will be done here
        # For now, we'll create example monitors
        self.monitors = {}
        # TODO: Fetch monitors from the database
    
    async def _start_monitors(self):
        """
        Starts all monitors
        """
        for monitor_id, monitor in self.monitors.items():
            if monitor.is_active:
                self._start_monitor(monitor_id)
    
    def _start_monitor(self, monitor_id: int):
        """
        Starts a specific monitor
        """
        if monitor_id in self.monitor_tasks and not self.monitor_tasks[monitor_id].done():
            logger.warning(f"Monitor {monitor_id} already running")
            return
        
        monitor = self.monitors.get(monitor_id)
        if not monitor:
            logger.error(f"Monitor {monitor_id} not found")
            return
        
        logger.info(f"Starting monitor {monitor_id}: {monitor.name}")
        task = asyncio.create_task(self._monitor_loop(monitor))
        self.monitor_tasks[monitor_id] = task
    
    def stop_monitor(self, monitor_id: int):
        """
        Stops a specific monitor
        """
        if monitor_id not in self.monitor_tasks:
            logger.warning(f"Monitor {monitor_id} not running")
            return
        
        task = self.monitor_tasks[monitor_id]
        if not task.done():
            task.cancel()
        
        logger.info(f"Stopped monitor {monitor_id}")
        if monitor_id in self.monitor_tasks:
            del self.monitor_tasks[monitor_id]
    
    async def add_monitor(self, monitor: Monitor):
        """
        Adds a new monitor and starts it
        """
        # Save to database and get ID
        # This is a sample:
        monitor_id = 1  # This ID is actually assigned by the database
        
        self.monitors[monitor_id] = monitor
        if monitor.is_active:
            self._start_monitor(monitor_id)
        
        return monitor_id
    
    async def update_monitor(self, monitor_id: int, updates: Dict[str, Any]) -> bool:
        """
        Updates a monitor
        """
        if monitor_id not in self.monitors:
            logger.error(f"Monitor {monitor_id} not found")
            return False
        
        # First, stop the monitor
        self.stop_monitor(monitor_id)
        
        # Update the monitor
        monitor = self.monitors[monitor_id]
        for key, value in updates.items():
            setattr(monitor, key, value)
        
        # Save to database
        # TODO: Add database update code
        
        # If the monitor is active, start it again
        if monitor.is_active:
            self._start_monitor(monitor_id)
        
        return True
    
    async def delete_monitor(self, monitor_id: int) -> bool:
        """
        Deletes a monitor
        """
        if monitor_id not in self.monitors:
            logger.error(f"Monitor {monitor_id} not found")
            return False
        
        # Stop the monitor
        self.stop_monitor(monitor_id)
        
        # Delete the monitor
        del self.monitors[monitor_id]
        
        # Delete from database
        # TODO: Add database delete code
        
        return True
    
    async def _monitor_loop(self, monitor: Monitor):
        """
        Monitor loop
        """
        logger.info(f"Monitor loop started for {monitor.name}")
        
        while self.running and monitor.is_active:
            try:
                # Is control time due?
                now = datetime.now()
                if monitor.last_check:
                    next_check = monitor.last_check + timedelta(minutes=monitor.check_interval)
                    if next_check > now:
                        # Wait until next control
                        wait_seconds = (next_check - now).total_seconds()
                        logger.debug(f"Monitor {monitor.name} waiting for {wait_seconds} seconds")
                        await asyncio.sleep(wait_seconds)
                
                # Check the website
                await self._check_monitor(monitor)
                
                # Update last control time
                monitor.last_check = datetime.now()
                # TODO: Update in database
                
            except asyncio.CancelledError:
                logger.info(f"Monitor {monitor.name} cancelled")
                break
            except Exception as e:
                logger.error(f"Error in monitor loop for {monitor.name}: {e}")
                await asyncio.sleep(60)  # Wait 1 minute if there's an error
    
    async def _check_monitor(self, monitor: Monitor):
        """
        Checks the website of the monitor
        """
        logger.info(f"Checking monitor {monitor.name}")
        
        try:
            # Get the website
            website = await self._get_website(monitor.website_id)
            if not website:
                logger.error(f"Website {monitor.website_id} not found for monitor {monitor.name}")
                return
            
            # Get job listings
            jobs = await self.job_crawler.get_jobs_from_website(
                website,
                keywords=monitor.keywords,
                exclude_keywords=monitor.exclude_keywords
            )
            
            # Compare and update jobs
            await self._compare_and_update_jobs(monitor, jobs)
            
        except Exception as e:
            logger.error(f"Error checking monitor {monitor.name}: {e}")
    
    async def _get_website(self, website_id: int) -> Optional[Website]:
        """
        Gets the website from the database
        """
        # TODO: Fetch the website from the database
        # This is a sample:
        return None
    
    async def _compare_and_update_jobs(self, monitor: Monitor, new_jobs: List[Dict[str, Any]]):
        """
        Compares new job listings with existing listings and updates them
        """
        # Get existing job listings
        existing_jobs = await self._get_existing_jobs(monitor.id)
        
        # Find new and updated listings
        new_job_urls = {job.get('url') for job in new_jobs}
        existing_job_urls = {job.url for job in existing_jobs}
        
        # New listings
        new_job_urls_set = new_job_urls - existing_job_urls
        
        # Removed listings
        removed_job_urls = existing_job_urls - new_job_urls
        
        # Save new listings
        for job_data in new_jobs:
            if job_data.get('url') in new_job_urls_set:
                await self._add_new_job(monitor, job_data)
        
        # Mark removed listings
        for job in existing_jobs:
            if job.url in removed_job_urls:
                await self._mark_job_removed(monitor, job)
    
    async def _get_existing_jobs(self, monitor_id: int) -> List[Job]:
        """
        Gets existing job listings from the database
        """
        # TODO: Fetch job listings for the monitor from the database
        # This is a sample:
        return []
    
    async def _add_new_job(self, monitor: Monitor, job_data: Dict[str, Any]):
        """
        Adds a new job and sends a notification
        """
        # Get job details
        details = await self.job_crawler.get_job_details(job_data.get('url', ''))
        job_data.update(details)
        
        # Save to database
        # TODO: Save to database and get job_id
        job_id = 1  # Sample ID
        
        # Create change log
        change_log = {
            'monitor_id': monitor.id,
            'job_id': job_id,
            'change_type': 'new',
            'new_data': job_data,
            'is_notified': False
        }
        
        # Save change log to database
        # TODO: Save change log to database
        
        # Send notification
        if monitor.notify_on_change:
            await self._send_notification(monitor, 'new', job_data)
    
    async def _mark_job_removed(self, monitor: Monitor, job: Job):
        """
        Marks the job as removed
        """
        # Update in database
        # TODO: Update in database
        
        # Create change log
        change_log = {
            'monitor_id': monitor.id,
            'job_id': job.id,
            'change_type': 'removed',
            'old_data': {
                'title': job.title,
                'company': job.company,
                'url': job.url
            },
            'is_notified': False
        }
        
        # Save change log to database
        # TODO: Save change log to database
        
        # Send notification
        if monitor.notify_on_change:
            await self._send_notification(monitor, 'removed', {
                'title': job.title,
                'company': job.company,
                'url': job.url
            })
    
    async def _send_notification(self, monitor: Monitor, change_type: str, job_data: Dict[str, Any]):
        """
        Sends a change notification
        """
        # Get notifications for the monitor
        notifications = await self._get_monitor_notifications(monitor.id)
        
        # Send to each notification channel
        for notification in notifications:
            await self.notification_manager.send_notification(
                notification,
                change_type,
                job_data
            )
    
    async def _get_monitor_notifications(self, monitor_id: int) -> List[Any]:
        """
        Gets notifications for the monitor from the database
        """
        # TODO: Fetch notifications for the monitor from the database
        # This is a sample:
        return []
    
    async def check_monitor_now(self, monitor_id: int):
        """
        Checks a specific monitor immediately
        """
        monitor = self.monitors.get(monitor_id)
        if not monitor:
            logger.error(f"Monitor {monitor_id} not found")
            return False
        
        await self._check_monitor(monitor)
        monitor.last_check = datetime.now()
        # TODO: Update in database
        
        return True 