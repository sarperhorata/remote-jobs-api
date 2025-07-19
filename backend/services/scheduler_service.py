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
        """External API crawler job - daily at 9 AM UTC"""
        try:
            await self._log_job_run("external_api_crawler", "started", "External API crawler job started")
            
            # Import external job APIs
            try:
                from external_job_apis import ExternalJobAPIManager
                manager = ExternalJobAPIManager()
                
                # Fetch jobs from external APIs
                results = manager.fetch_all_jobs(max_jobs_per_api=50)
                save_results = manager.save_jobs_to_database(results)
                
                total_jobs = sum(save_results.values())
                
                # Log success
                await self._log_job_run("external_api_crawler", "success", f"External API crawler completed successfully", {
                    "total_jobs": total_jobs,
                    "api_results": save_results
                })
                
                # Send Telegram notification if available
                try:
                    from backend.telegram_bot.bot_manager import bot_manager
                    if bot_manager.bot_instance and bot_manager.bot_instance.enabled:
                        await bot_manager.bot_instance.send_deployment_notification({
                            'type': 'external_api_crawl',
                            'status': 'success',
                            'total_jobs': total_jobs,
                            'api_results': save_results,
                            'timestamp': datetime.now().isoformat()
                        })
                except Exception as telegram_error:
                    logger.warning(f"Could not send Telegram notification: {telegram_error}")
                
            except ImportError as e:
                error_msg = f"External job APIs module not available: {e}"
                await self._log_job_run("external_api_crawler", "error", error_msg)
                logger.error(error_msg)
                
        except Exception as e:
            error_msg = f"External API crawler job failed: {e}"
            await self._log_job_run("external_api_crawler", "error", error_msg)
            logger.error(error_msg)
            
            # Send Telegram notification if available
            try:
                from backend.telegram_bot.bot_manager import bot_manager
                if bot_manager.bot_instance and bot_manager.bot_instance.enabled:
                    await bot_manager.bot_instance.send_deployment_notification({
                        'type': 'external_api_crawl',
                        'status': 'error',
                        'error': str(e),
                        'timestamp': datetime.now().isoformat()
                    })
            except Exception as telegram_error:
                logger.warning(f"Could not send Telegram notification: {telegram_error}")
    
    async def _distill_crawler_job(self):
        """Buzz2Remote-Companies distill crawler job - daily at 10 AM UTC"""
        try:
            await self._log_job_run("distill_crawler", "started", "Distill crawler job started")
            
            # Import distill crawler
            try:
                from distill_crawler import DistillCrawler
                crawler = DistillCrawler()
                
                # Run crawler
                results = await crawler.run_crawler()
                
                # Log success
                await self._log_job_run("distill_crawler", "success", f"Distill crawler completed successfully", {
                    "companies_found": len(results.get('companies', [])),
                    "jobs_found": len(results.get('jobs', [])),
                    "errors": results.get('errors', [])
                })
                
                # Send Telegram notification if available
                try:
                    from backend.telegram_bot.bot_manager import bot_manager
                    if bot_manager.bot_instance and bot_manager.bot_instance.enabled:
                        await bot_manager.bot_instance.send_deployment_notification({
                            'type': 'distill_crawl',
                            'status': 'success',
                            'companies_found': len(results.get('companies', [])),
                            'jobs_found': len(results.get('jobs', [])),
                            'timestamp': datetime.now().isoformat()
                        })
                except Exception as telegram_error:
                    logger.warning(f"Could not send Telegram notification: {telegram_error}")
                
            except ImportError as e:
                error_msg = f"Distill crawler module not available: {e}"
                await self._log_job_run("distill_crawler", "error", error_msg)
                logger.error(error_msg)
                
        except Exception as e:
            error_msg = f"Distill crawler job failed: {e}"
            await self._log_job_run("distill_crawler", "error", error_msg)
            logger.error(error_msg)
            
            # Send Telegram notification if available
            try:
                from backend.telegram_bot.bot_manager import bot_manager
                if bot_manager.bot_instance and bot_manager.bot_instance.enabled:
                    await bot_manager.bot_instance.send_deployment_notification({
                        'type': 'distill_crawl',
                        'status': 'error',
                        'error': str(e),
                        'timestamp': datetime.now().isoformat()
                    })
            except Exception as telegram_error:
                logger.warning(f"Could not send Telegram notification: {telegram_error}")
    
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
        """Daily job statistics job - daily at 8 AM UTC"""
        try:
            await self._log_job_run("job_statistics", "started", "Job statistics job started")
            
            # Import database
            try:
                from database.db import get_async_db
                db = await get_async_db()
                
                if db:
                    # Get job statistics
                    total_jobs = await db.jobs.count_documents({})
                    active_jobs = await db.jobs.count_documents({"status": "active"})
                    total_companies = await db.companies.count_documents({})
                    
                    # Get today's new jobs
                    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
                    new_jobs_today = await db.jobs.count_documents({"created_at": {"$gte": today}})
                    
                    # Get job sources distribution
                    pipeline = [
                        {"$group": {"_id": "$source", "count": {"$sum": 1}}},
                        {"$sort": {"count": -1}}
                    ]
                    source_stats = list(await db.jobs.aggregate(pipeline))
                    
                    # Log success
                    await self._log_job_run("job_statistics", "success", f"Job statistics collected successfully", {
                        "total_jobs": total_jobs,
                        "active_jobs": active_jobs,
                        "total_companies": total_companies,
                        "new_jobs_today": new_jobs_today,
                        "source_stats": source_stats
                    })
                    
                    # Send Telegram notification if available
                    try:
                        from backend.telegram_bot.bot_manager import bot_manager
                        if bot_manager.bot_instance and bot_manager.bot_instance.enabled:
                            await bot_manager.bot_instance.send_deployment_notification({
                                'type': 'daily_statistics',
                                'status': 'success',
                                'total_jobs': total_jobs,
                                'active_jobs': active_jobs,
                                'total_companies': total_companies,
                                'new_jobs_today': new_jobs_today,
                                'timestamp': datetime.now().isoformat()
                            })
                    except Exception as telegram_error:
                        logger.warning(f"Could not send Telegram notification: {telegram_error}")
                else:
                    error_msg = "Database connection not available"
                    await self._log_job_run("job_statistics", "error", error_msg)
                    logger.error(error_msg)
                
            except ImportError as e:
                error_msg = f"Database module not available: {e}"
                await self._log_job_run("job_statistics", "error", error_msg)
                logger.error(error_msg)
                
        except Exception as e:
            error_msg = f"Job statistics job failed: {e}"
            await self._log_job_run("job_statistics", "error", error_msg)
            logger.error(error_msg)
            
            # Send Telegram notification if available
            try:
                from backend.telegram_bot.bot_manager import bot_manager
                if bot_manager.bot_instance and bot_manager.bot_instance.enabled:
                    await bot_manager.bot_instance.send_deployment_notification({
                        'type': 'daily_statistics',
                        'status': 'error',
                        'error': str(e),
                        'timestamp': datetime.now().isoformat()
                    })
            except Exception as telegram_error:
                logger.warning(f"Could not send Telegram notification: {telegram_error}")
    
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