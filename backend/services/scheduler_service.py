import asyncio
import logging
from datetime import datetime, timedelta
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
import os
import sys
import requests

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

logger = logging.getLogger(__name__)

class SchedulerService:
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.is_running = False
        
    async def start(self):
        """Start the scheduler service"""
        if self.is_running:
            return
            
        try:
            # Add jobs to scheduler
            await self._setup_jobs()
            
            # Start scheduler
            self.scheduler.start()
            self.is_running = True
            logger.info("Scheduler service started successfully")
            
        except Exception as e:
            logger.error(f"Failed to start scheduler service: {str(e)}")
            raise e
    
    async def stop(self):
        """Stop the scheduler service"""
        if not self.is_running:
            return
            
        try:
            self.scheduler.shutdown()
            self.is_running = False
            logger.info("Scheduler service stopped")
        except Exception as e:
            logger.error(f"Error stopping scheduler service: {str(e)}")
    
    async def _setup_jobs(self):
        """Setup all scheduled jobs"""
        
        # 1. Health check job - every 14 minutes to keep Render awake
        self.scheduler.add_job(
            self._health_check_job,
            trigger=IntervalTrigger(minutes=14),
            id='health_check',
            name='Health Check - Keep Render Awake',
            max_instances=1,
            coalesce=True
        )
        
        # 2. External API crawler - daily at 9 AM UTC
        self.scheduler.add_job(
            self._external_api_crawler_job,
            trigger=CronTrigger(hour=9, minute=0),
            id='external_api_crawler',
            name='External API Crawler',
            max_instances=1,
            coalesce=True
        )
        
        # 3. Buzz2Remote-Companies (Distill) crawler - daily at 10 AM UTC
        self.scheduler.add_job(
            self._distill_crawler_job,
            trigger=CronTrigger(hour=10, minute=0),
            id='distill_crawler',
            name='Buzz2Remote-Companies Distill Crawler',
            max_instances=1,
            coalesce=True
        )
        
        # 4. Database cleanup - weekly on Sunday at 2 AM UTC
        self.scheduler.add_job(
            self._database_cleanup_job,
            trigger=CronTrigger(day_of_week=6, hour=2, minute=0),
            id='database_cleanup',
            name='Database Cleanup',
            max_instances=1,
            coalesce=True
        )
        
        # 5. Job statistics - daily at 8 AM UTC
        self.scheduler.add_job(
            self._job_statistics_job,
            trigger=CronTrigger(hour=8, minute=0),
            id='job_statistics',
            name='Daily Job Statistics',
            max_instances=1,
            coalesce=True
        )
        
        logger.info("All scheduled jobs configured")
    
    async def _health_check_job(self):
        """Health check job to keep Render service awake"""
        try:
            render_url = os.getenv('RENDER_URL', 'https://buzz2remote-api.onrender.com')
            
            response = requests.get(f"{render_url}/health", timeout=10)
            
            if response.status_code == 200:
                logger.info(f"Health check successful at {datetime.now()}")
            else:
                logger.warning(f"Health check failed with status {response.status_code}")
                
        except Exception as e:
            logger.error(f"Health check error: {str(e)}")
    
    async def _external_api_crawler_job(self):
        """External API crawler job"""
        try:
            logger.info("Starting external API crawler job")
            
            # Import here to avoid circular imports
            try:
                from external_job_apis import ExternalJobAPIManager
                from service_notifications import ServiceNotifier
                
                manager = ExternalJobAPIManager()
                notifier = ServiceNotifier()
                
                # Send start notification
                notifier._send_message(f"""🚀 <b>SCHEDULED CRAWLER STARTED</b>

📅 <b>Time:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} UTC
🔄 <b>Starting external API crawling...</b>
🎯 <b>Target:</b> All available APIs""")
                
                # Run crawler
                results = manager.fetch_all_jobs(max_jobs_per_api=200)
                save_results = manager.save_jobs_to_database(results)
                
                # Calculate totals
                total_jobs = sum(save_results.values())
                
                # Send success notification
                results_text = []
                for api_name, count in save_results.items():
                    results_text.append(f"• {api_name}: {count} jobs")
                
                notifier._send_message(f"""✅ <b>SCHEDULED CRAWLER COMPLETED</b>

🎉 <b>Crawl successful!</b>
📊 <b>Total jobs:</b> {total_jobs}

🔧 <b>API Results:</b>
{chr(10).join(results_text)}

🕐 <b>Completed at:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} UTC""")
                
                logger.info(f"External API crawler completed successfully. Total jobs: {total_jobs}")
                
            except ImportError as e:
                logger.error(f"Failed to import external API modules: {str(e)}")
                
        except Exception as e:
            logger.error(f"External API crawler job error: {str(e)}")
            
            # Send error notification
            try:
                from service_notifications import ServiceNotifier
                notifier = ServiceNotifier()
                notifier._send_message(f"""❌ <b>SCHEDULED CRAWLER ERROR</b>

🚫 <b>Crawler failed</b>
❌ <b>Error:</b> {str(e)[:200]}...
🕐 <b>Time:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} UTC""")
            except:
                pass
    
    async def _distill_crawler_job(self):
        """Buzz2Remote-Companies (Distill) crawler job"""
        try:
            logger.info("Starting Buzz2Remote-Companies (Distill) crawler job")
            
            # Import here to avoid circular imports
            try:
                from distill_crawler import DistillCrawler
                from service_notifications import ServiceNotifier
                
                crawler = DistillCrawler()
                notifier = ServiceNotifier()
                
                # Send start notification
                notifier._send_message(f"""🏢 <b>BUZZ2REMOTE-COMPANIES CRAWLER STARTED</b>

📅 <b>Time:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} UTC
🔄 <b>Starting company websites crawling...</b>
🎯 <b>Target:</b> 500+ Company Career Pages
📋 <b>Source:</b> Distill.io Export Data""")
                
                # Load companies data
                crawler.load_companies_data()
                
                # Run crawler (limit to reasonable number for daily run)
                jobs = await crawler.crawl_all_companies(max_companies=100)
                
                # Save to database
                save_results = crawler.save_jobs_to_database(jobs)
                
                # Send success notification
                notifier._send_message(f"""✅ <b>BUZZ2REMOTE-COMPANIES COMPLETED</b>

🎉 <b>Company crawl successful!</b>
📊 <b>Total jobs found:</b> {len(jobs)}
💾 <b>New jobs:</b> {save_results.get('new_jobs', 0)}
🔄 <b>Updated jobs:</b> {save_results.get('updated_jobs', 0)}
🏢 <b>Companies crawled:</b> {min(100, len(crawler.companies_data))}

🕐 <b>Completed at:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} UTC
🌐 <b>Source:</b> Company Career Pages""")
                
                logger.info(f"Distill crawler completed successfully. Total jobs: {len(jobs)}")
                
            except ImportError as e:
                logger.error(f"Failed to import distill crawler modules: {str(e)}")
                
        except Exception as e:
            logger.error(f"Distill crawler job error: {str(e)}")
            
            # Send error notification
            try:
                from service_notifications import ServiceNotifier
                notifier = ServiceNotifier()
                notifier._send_message(f"""❌ <b>BUZZ2REMOTE-COMPANIES ERROR</b>

🚫 <b>Company crawler failed</b>
❌ <b>Error:</b> {str(e)[:200]}...
🕐 <b>Time:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} UTC
🏢 <b>Source:</b> Distill Company Data""")
            except:
                pass
    
    async def _database_cleanup_job(self):
        """Database cleanup job"""
        try:
            logger.info("Starting database cleanup job")
            
            from database import get_db
            
            db = get_db()
            
            # Remove old job postings (older than 90 days)
            cutoff_date = datetime.now() - timedelta(days=90)
            
            jobs_collection = db["jobs"]
            result = jobs_collection.delete_many({
                "posted_at": {"$lt": cutoff_date.isoformat()}
            })
            
            logger.info(f"Database cleanup completed. Removed {result.deleted_count} old jobs")
            
            # Send notification
            try:
                from service_notifications import ServiceNotifier
                notifier = ServiceNotifier()
                notifier._send_message(f"""🧹 <b>DATABASE CLEANUP COMPLETED</b>

✅ <b>Cleanup successful</b>
🗑️ <b>Removed jobs:</b> {result.deleted_count}
📅 <b>Cutoff date:</b> {cutoff_date.strftime('%Y-%m-%d')}
🕐 <b>Time:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} UTC""")
            except:
                pass
                
        except Exception as e:
            logger.error(f"Database cleanup job error: {str(e)}")
    
    async def _job_statistics_job(self):
        """Daily job statistics job"""
        try:
            logger.info("Starting job statistics job")
            
            from database import get_db
            
            db = get_db()
            jobs_collection = db["jobs"]
            
            # Get statistics
            total_jobs = jobs_collection.count_documents({})
            active_jobs = jobs_collection.count_documents({"is_active": True})
            
            # Jobs added in last 24 hours
            yesterday = datetime.now() - timedelta(days=1)
            new_jobs_24h = jobs_collection.count_documents({
                "created_at": {"$gte": yesterday.isoformat()}
            })
            
            logger.info(f"Job statistics: Total={total_jobs}, Active={active_jobs}, New(24h)={new_jobs_24h}")
            
            # Send notification
            try:
                from service_notifications import ServiceNotifier
                notifier = ServiceNotifier()
                notifier._send_message(f"""📊 <b>DAILY JOB STATISTICS</b>

📈 <b>Total jobs:</b> {total_jobs:,}
✅ <b>Active jobs:</b> {active_jobs:,}
🆕 <b>New jobs (24h):</b> {new_jobs_24h:,}

🕐 <b>Time:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} UTC
🌐 <b>Platform:</b> buzz2remote.com""")
            except:
                pass
                
        except Exception as e:
            logger.error(f"Job statistics job error: {str(e)}")
    
    def get_job_status(self):
        """Get status of all scheduled jobs"""
        if not self.is_running:
            return {"status": "stopped", "jobs": []}
        
        jobs = []
        for job in self.scheduler.get_jobs():
            jobs.append({
                "id": job.id,
                "name": job.name,
                "next_run": job.next_run_time.isoformat() if job.next_run_time else None,
                "trigger": str(job.trigger)
            })
        
        return {
            "status": "running",
            "jobs": jobs,
            "scheduler_state": self.scheduler.state
        }

# Global scheduler instance
scheduler_service = None

async def start_scheduler():
    """Start the global scheduler service"""
    global scheduler_service
    
    if scheduler_service is None:
        scheduler_service = SchedulerService()
    
    await scheduler_service.start()
    return scheduler_service

async def stop_scheduler():
    """Stop the global scheduler service"""
    global scheduler_service
    
    if scheduler_service:
        await scheduler_service.stop()

def get_scheduler():
    """Get the global scheduler service"""
    return scheduler_service 