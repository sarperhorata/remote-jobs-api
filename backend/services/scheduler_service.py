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
        
        # 3. BUZZ2REMOTE-COMPANIES crawler - daily at 10 AM UTC
        self.scheduler.add_job(
            self._distill_crawler_job,
            trigger=CronTrigger(hour=10, minute=0),
            id='distill_crawler',
            name='BUZZ2REMOTE-COMPANIES Crawler',
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
            # Use different URLs based on environment
            if os.getenv('ENVIRONMENT') == 'production':
                render_url = os.getenv('RENDER_URL', 'https://buzz2remote-api.onrender.com')
                health_endpoint = f"{render_url}/health"
            else:
                # For local development, use localhost with correct port
                health_endpoint = "http://localhost:5001/health"
            
            response = requests.get(health_endpoint, timeout=10)
            
            if response.status_code == 200:
                logger.info(f"Health check successful at {datetime.now()}")
            else:
                logger.warning(f"Health check failed with status {response.status_code}")
                
        except Exception as e:
            logger.warning(f"Health check failed: {str(e)}")
    
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
        """BUZZ2REMOTE-COMPANIES crawler job"""
        crawler = None
        notifier = None
        
        try:
            logger.info("Starting BUZZ2REMOTE-COMPANIES crawler job")
            
            # Import here to avoid circular imports
            try:
                from distill_crawler import DistillCrawler
                from service_notifications import ServiceNotifier
                
                crawler = DistillCrawler()
                notifier = ServiceNotifier()
                
            except ImportError as e:
                logger.error(f"Failed to import BUZZ2REMOTE-COMPANIES crawler modules: {str(e)}")
                # This is a critical error - can't proceed without modules
                raise e
            
            # Send start notification
            notifier._send_message(f"""🏢 <b>BUZZ2REMOTE-COMPANIES CRAWLER STARTED</b>

📅 <b>Time:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} UTC
🔄 <b>Starting company websites crawling...</b>
🎯 <b>Target:</b> All Company Career Pages
📋 <b>Source:</b> Distill.io Export Data""")
            
            # Load companies data
            try:
                crawler.load_companies_data()
                total_companies = len(crawler.companies_data)
                logger.info(f"Loaded {total_companies} companies for crawling")
                
            except Exception as e:
                logger.error(f"Failed to load companies data: {str(e)}")
                # This is a critical error - can't proceed without data
                raise e
            
            # Run crawler for all companies
            try:
                jobs = await crawler.crawl_all_companies()
                
                # Save to database
                save_results = crawler.save_jobs_to_database(jobs)
                
                # Calculate success metrics
                total_companies = len(crawler.companies_data)
                total_jobs_found = len(jobs)
                new_jobs = save_results.get('new_jobs', 0)
                updated_jobs = save_results.get('updated_jobs', 0)
                
                # Send success notification with detailed stats
                summary = getattr(crawler, 'last_crawl_summary', {})
                total_companies = summary.get('total_companies', len(crawler.companies_data))
                successful_companies = summary.get('successful_companies', 0)
                companies_with_jobs = summary.get('companies_with_jobs', 0)
                failed_companies = summary.get('failed_companies', 0)
                top_companies = summary.get('top_companies', {})
                
                # Build top companies text
                top_companies_text = ""
                if top_companies:
                    top_list = list(top_companies.items())[:3]  # Top 3
                    top_companies_text = f"\n\n🏆 <b>Top Performers:</b>\n"
                    for company, count in top_list:
                        top_companies_text += f"• {company}: {count} jobs\n"
                
                notifier._send_message(f"""✅ <b>BUZZ2REMOTE-COMPANIES COMPLETED</b>

🎉 <b>Company crawl successful!</b>
📊 <b>Total jobs found:</b> {total_jobs_found}
💾 <b>New jobs:</b> {new_jobs}
🔄 <b>Updated jobs:</b> {updated_jobs}

📈 <b>Company Breakdown:</b>
🏢 <b>Total companies:</b> {total_companies}
✅ <b>Successfully processed:</b> {successful_companies}
🎯 <b>Companies with jobs:</b> {companies_with_jobs}
❌ <b>Failed companies:</b> {failed_companies}{top_companies_text}

🕐 <b>Completed at:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} UTC
🌐 <b>Source:</b> Company Career Pages

ℹ️ <i>Individual company failures are logged separately and don't affect overall success</i>""")
                
                logger.info(f"BUZZ2REMOTE-COMPANIES crawler completed successfully. Total jobs: {total_jobs_found} from {total_companies} companies")
                
            except Exception as e:
                logger.error(f"Error during crawling execution: {str(e)}")
                # Even if crawling fails partially, don't send error if we loaded companies
                # Check if it's a total failure or partial failure
                
                if "load_companies_data" in str(e) or not hasattr(crawler, 'companies_data'):
                    # Critical failure - couldn't start
                    raise e
                else:
                    # Partial failure - still report what we got
                    notifier._send_message(f"""⚠️ <b>BUZZ2REMOTE-COMPANIES PARTIAL FAILURE</b>

🚫 <b>Crawling encountered issues</b>
❌ <b>Error:</b> {str(e)[:200]}...
🏢 <b>Companies loaded:</b> {len(crawler.companies_data) if hasattr(crawler, 'companies_data') else 0}
🕐 <b>Time:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} UTC

ℹ️ <i>This may be due to individual company site issues, not a system failure</i>""")
                    
                    # Don't raise the exception - this is not a critical scheduler failure
                    return
                
        except Exception as e:
            logger.error(f"BUZZ2REMOTE-COMPANIES crawler job error: {str(e)}")
            
            # Send error notification only for critical failures
            try:
                if notifier:
                    notifier._send_message(f"""❌ <b>BUZZ2REMOTE-COMPANIES CRITICAL ERROR</b>

🚫 <b>Crawler failed to start or load data</b>
❌ <b>Error:</b> {str(e)[:200]}...
🕐 <b>Time:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} UTC
🏢 <b>Source:</b> Distill Company Data

⚠️ <i>This is a system-level failure requiring attention</i>""")
                else:
                    # Fallback notification without notifier
                    logger.critical(f"CRITICAL: BUZZ2REMOTE-COMPANIES crawler failed to start: {str(e)}")
            except Exception as notification_error:
                logger.error(f"Failed to send error notification: {notification_error}")
            
            # Only re-raise critical errors that prevent scheduler from continuing
            if "ImportError" in str(type(e)) or "Failed to load companies data" in str(e):
                raise e
            # For other errors, just log them but don't crash the scheduler
    
    async def _database_cleanup_job(self):
        """Database cleanup job"""
        try:
            logger.info("Starting database cleanup job")
            
            from backend.database import get_async_db
            
            db = await get_async_db()
            
            # Remove old job postings (older than 90 days)
            cutoff_date = datetime.now() - timedelta(days=90)
            
            jobs_collection = db["jobs"]
            result = await jobs_collection.delete_many({
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
            
            from backend.database import get_async_db
            
            db = await get_async_db()
            jobs_collection = db["jobs"]
            
            # Get statistics
            total_jobs = await jobs_collection.count_documents({})
            active_jobs = await jobs_collection.count_documents({"is_active": True})
            
            # Jobs added in last 24 hours
            yesterday = datetime.now() - timedelta(days=1)
            new_jobs_24h = await jobs_collection.count_documents({
                "last_updated": {"$gte": yesterday.isoformat()}
            })
            
            logger.info(f"Job statistics: Total={total_jobs}, Active={active_jobs}, New(24h)={new_jobs_24h}")
            
            # Send notification
            try:
                from service_notifications import ServiceNotifier
                notifier = ServiceNotifier()
                notifier._send_message(f"""📊 <b>DAILY JOB STATISTICS</b>

�� <b>Total jobs:</b> {total_jobs:,}
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