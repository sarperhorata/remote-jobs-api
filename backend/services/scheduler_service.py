import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import os
import sys
import requests

# APScheduler imports
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

logger = logging.getLogger(__name__)

# Global scheduler service instance
_scheduler_service = None

class SchedulerService:
    """
    Scheduler service for managing background jobs
    """
    
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.is_running = False
        self.job_logs = {}  # Store last 1 week of logs per job
        
    async def start(self):
        """Start the scheduler service"""
        # Check if scheduler should be disabled
        if os.getenv('DISABLE_SCHEDULER', 'false').lower() == 'true':
            logger.info("⏸️ Scheduler service is disabled via DISABLE_SCHEDULER environment variable")
            return False
            
        try:
            if not self.is_running:
                # Configure scheduler with timezone
                self.scheduler.configure(timezone='UTC')
                await self._setup_jobs()
                self.scheduler.start()
                self.is_running = True
                logger.info("✅ Scheduler service started successfully")
                
                # Send startup notification
                await self._log_job_run("scheduler_startup", "success", "Scheduler service started", {
                    "jobs_count": len(self.scheduler.get_jobs()),
                    "status": "running"
                })
                
            return True
        except Exception as e:
            logger.error(f"❌ Failed to start scheduler service: {e}")
            # Try to start without timezone configuration
            try:
                if not self.is_running:
                    await self._setup_jobs()
                    self.scheduler.start()
                    self.is_running = True
                    logger.info("✅ Scheduler service started successfully (without timezone)")
                    return True
            except Exception as e2:
                logger.error(f"❌ Failed to start scheduler service (fallback): {e2}")
            return False
    
    async def stop(self):
        """Stop the scheduler service"""
        try:
            if self.is_running:
                self.scheduler.shutdown()
                self.is_running = False
                logger.info("🛑 Scheduler service stopped")
        except Exception as e:
            logger.error(f"Error stopping scheduler service: {e}")
    
    async def _setup_jobs(self):
        """Setup all scheduled jobs"""
        try:
            # Health check job - every 14 minutes to keep Render awake
            self.scheduler.add_job(
                self._health_check_job,
                IntervalTrigger(minutes=14),
                id="health_check",
                name="Health Check - Keep Render Awake",
                replace_existing=True
            )
            
            # External API crawler - daily at 9 AM UTC
            self.scheduler.add_job(
                self._external_api_crawler_job,
                CronTrigger(hour=9, minute=0),
                id="external_api_crawler", 
                name="External API Crawler",
                replace_existing=True
            )
            
            # Buzz2Remote-Companies distill crawler - daily at 10 AM UTC
            self.scheduler.add_job(
                self._distill_crawler_job,
                CronTrigger(hour=10, minute=0),
                id="distill_crawler",
                name="Buzz2Remote-Companies Distill Crawler", 
                replace_existing=True
            )
            
            # Database cleanup - weekly on Sunday at 2 AM UTC
            self.scheduler.add_job(
                self._database_cleanup_job,
                CronTrigger(day_of_week=6, hour=2, minute=0),
                id="database_cleanup",
                name="Database Cleanup",
                replace_existing=True
            )
            
            # Daily job statistics - daily at 8 AM UTC
            self.scheduler.add_job(
                self._job_statistics_job,
                CronTrigger(hour=8, minute=0),
                id="job_statistics",
                name="Daily Job Statistics",
                replace_existing=True
            )
            
            logger.info("✅ All scheduled jobs configured")
            
        except Exception as e:
            logger.error(f"❌ Error setting up jobs: {str(e)}")
            raise e
    
    async def _log_job_run(self, job_id: str, status: str, message: str, data: Dict[str, Any] = None):
        """Log job run with 1-week retention"""
        try:
            # Initialize job logs if not exists
            if job_id not in self.job_logs:
                self.job_logs[job_id] = []
            
            # Create log entry
            log_entry = {
                "timestamp": datetime.now(),
                "status": status,
                "message": message,
                "data": data or {}
            }
            
            # Add to job logs
            self.job_logs[job_id].append(log_entry)
            
            # Clean old logs (keep only last 7 days)
            week_ago = datetime.now() - timedelta(days=7)
            self.job_logs[job_id] = [
                log for log in self.job_logs[job_id] 
                if log["timestamp"] > week_ago
            ]
            
            # Send to database if available
            try:
                from database.db import get_async_db
                db = await get_async_db()
                if db:
                    await db.scheduler_logs.insert_one({
                        "job_id": job_id,
                        "timestamp": datetime.now(),
                        "status": status,
                        "message": message,
                        "data": data or {}
                    })
                    
                    # Clean old database logs too (7 days retention)
                    await db.scheduler_logs.delete_many({
                        "timestamp": {"$lt": week_ago}
                    })
                    
            except Exception as db_error:
                logger.warning(f"Could not save job log to database: {db_error}")
                
        except Exception as e:
            logger.error(f"Error logging job run: {e}")
    
    async def _health_check_job(self):
        """Health check job to keep Render service awake"""
        try:
            import httpx
            
            # Check if we're running on Render
            if os.getenv('RENDER'):
                try:
                    async with httpx.AsyncClient() as client:
                        response = await client.get("https://buzz2remote-api.onrender.com/health", timeout=30)
                        if response.status_code == 200:
                            await self._log_job_run("health_check", "success", "Health check successful", {
                                "response_time": response.elapsed.total_seconds(),
                                "status_code": response.status_code
                            })
                        else:
                            await self._log_job_run("health_check", "warning", f"Health check returned {response.status_code}")
                            
                except Exception as e:
                    await self._log_job_run("health_check", "error", f"Health check failed: {str(e)}")
            else:
                await self._log_job_run("health_check", "skipped", "Not running on Render, health check skipped")
                
        except Exception as e:
            logger.error(f"Health check job error: {str(e)}")
            await self._log_job_run("health_check", "error", f"Health check job error: {str(e)}")
    
    async def _external_api_crawler_job(self):
        """External API crawler job"""
        try:
            logger.info("🚀 Starting external API crawler job")
            await self._log_job_run("external_api_crawler", "started", "External API crawler started")
            
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
                
                # Log success
                await self._log_job_run("external_api_crawler", "success", f"Crawled {total_jobs} jobs from external APIs", {
                    "total_jobs": total_jobs,
                    "results": save_results
                })
                
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
                
                logger.info(f"✅ External API crawler completed successfully. Total jobs: {total_jobs}")
                
            except ImportError as e:
                logger.error(f"Failed to import external API modules: {str(e)}")
                await self._log_job_run("external_api_crawler", "error", f"Import error: {str(e)}")
                
        except Exception as e:
            logger.error(f"External API crawler job error: {str(e)}")
            await self._log_job_run("external_api_crawler", "error", f"Crawler job error: {str(e)}")
            
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
            logger.info("🏢 Starting BUZZ2REMOTE-COMPANIES crawler job")
            await self._log_job_run("distill_crawler", "started", "Buzz2Remote companies crawler started")
            
            # Import here to avoid circular imports
            try:
                from distill_crawler import DistillCrawler
                from service_notifications import ServiceNotifier
                
                crawler = DistillCrawler()
                notifier = ServiceNotifier()
                
            except ImportError as e:
                logger.error(f"Failed to import BUZZ2REMOTE-COMPANIES crawler modules: {str(e)}")
                await self._log_job_run("distill_crawler", "error", f"Import error: {str(e)}")
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
                await self._log_job_run("distill_crawler", "error", f"Failed to load companies data: {str(e)}")
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
                
                # Log success
                await self._log_job_run("distill_crawler", "success", f"Crawled {total_jobs_found} jobs from {total_companies} companies", {
                    "total_companies": total_companies,
                    "total_jobs": total_jobs_found,
                    "new_jobs": new_jobs,
                    "updated_jobs": updated_jobs
                })
                
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
                
                notifier._send_message(f"""✅ <b>BUZZ2REMOTE-COMPANIES CRAWL COMPLETED</b>

🎉 <b>Crawl successful!</b>
📊 <b>Total jobs found:</b> {total_jobs_found:,}
🆕 <b>New jobs:</b> {new_jobs:,}
🔄 <b>Updated jobs:</b> {updated_jobs:,}

🏢 <b>Company Stats:</b>
• Total companies: {total_companies}
• Successfully crawled: {successful_companies}
• Companies with jobs: {companies_with_jobs}
• Failed companies: {failed_companies}{top_companies_text}

🕐 <b>Completed at:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} UTC
📋 <b>Source:</b> Distill Company Export Data""")
                
                logger.info(f"✅ BUZZ2REMOTE-COMPANIES crawler completed successfully.")
                logger.info(f"📊 Companies: {total_companies}, Jobs: {total_jobs_found}, New: {new_jobs}, Updated: {updated_jobs}")
                
            except Exception as e:
                logger.error(f"BUZZ2REMOTE-COMPANIES crawler execution error: {str(e)}")
                await self._log_job_run("distill_crawler", "error", f"Crawler execution error: {str(e)}")
                
                # Send error notification for execution failures
                if notifier:
                    notifier._send_message(f"""⚠️ <b>BUZZ2REMOTE-COMPANIES CRAWL ERROR</b>

⚠️ <b>Crawler encountered errors during execution</b>
❌ <b>Error:</b> {str(e)[:200]}...
🕐 <b>Time:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} UTC
🏢 <b>Source:</b> Distill Company Data

💡 <i>This may be a temporary issue. Check logs for details.</i>""")
                
        except Exception as e:
            logger.error(f"BUZZ2REMOTE-COMPANIES crawler job error: {str(e)}")
            await self._log_job_run("distill_crawler", "error", f"Critical crawler job error: {str(e)}")
            
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
            logger.info("🧹 Starting database cleanup job")
            await self._log_job_run("database_cleanup", "started", "Database cleanup started")
            
            from database import get_async_db
            
            db = await get_async_db()
            
            # Remove old job postings (older than 90 days)
            cutoff_date = datetime.now() - timedelta(days=90)
            
            jobs_collection = db["jobs"]
            result = await jobs_collection.delete_many({
                "posted_at": {"$lt": cutoff_date.isoformat()}
            })
            
            logger.info(f"✅ Database cleanup completed. Removed {result.deleted_count} old jobs")
            await self._log_job_run("database_cleanup", "success", f"Removed {result.deleted_count} old jobs", {
                "deleted_count": result.deleted_count,
                "cutoff_date": cutoff_date.isoformat()
            })
            
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
            await self._log_job_run("database_cleanup", "error", f"Database cleanup error: {str(e)}")
    
    async def _job_statistics_job(self):
        """Daily job statistics job"""
        try:
            logger.info("📊 Starting job statistics job")
            await self._log_job_run("job_statistics", "started", "Job statistics job started")
            
            from database import get_async_db
            
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
            
            logger.info(f"📊 Job statistics: Total={total_jobs}, Active={active_jobs}, New(24h)={new_jobs_24h}")
            await self._log_job_run("job_statistics", "success", f"Generated daily statistics", {
                "total_jobs": total_jobs,
                "active_jobs": active_jobs,
                "new_jobs_24h": new_jobs_24h
            })
            
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
            await self._log_job_run("job_statistics", "error", f"Job statistics error: {str(e)}")
    
    def get_job_status(self):
        """Get status of all scheduled jobs with next run times"""
        if not self.is_running:
            return {"status": "stopped", "jobs": []}
        
        jobs = []
        for job in self.scheduler.get_jobs():
            jobs.append({
                "id": job.id,
                "name": job.name,
                "next_run": job.next_run_time.isoformat() if job.next_run_time else None,
                "trigger": str(job.trigger),
                "last_logs": self.job_logs.get(job.id, [])[-5:]  # Last 5 logs
            })
        
        return {
            "status": "running",
            "jobs": jobs,
            "scheduler_state": self.scheduler.state,
            "total_logs": sum(len(logs) for logs in self.job_logs.values())
        }
    
    def get_job_logs(self, job_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Get logs for a specific job"""
        if job_id not in self.job_logs:
            return []
        
        # Return most recent logs first
        logs = self.job_logs[job_id][-limit:]
        return sorted(logs, key=lambda x: x["timestamp"], reverse=True)


def get_scheduler() -> Optional[SchedulerService]:
    """Get the global scheduler service instance"""
    global _scheduler_service
    return _scheduler_service

async def start_scheduler():
    """Start the global scheduler service"""
    global _scheduler_service
    
    if _scheduler_service is None:
        _scheduler_service = SchedulerService()
    
    return await _scheduler_service.start()

async def stop_scheduler():
    """Stop the global scheduler service"""
    global _scheduler_service
    
    if _scheduler_service:
        await _scheduler_service.stop() 