import logging
import asyncio
from datetime import datetime
from typing import List, Dict, Any
import json
import os
from database import get_db
from utils.config import logger

class CompanyCrawler:
    def __init__(self):
        self.db = get_db()
        self.companies_col = self.db["companies"]
        self.jobs_col = self.db["jobs"]
        self.error_log_col = self.db["crawl_errors"]
        
    async def crawl_all_companies(self):
        """Crawl all companies in the database without any limit"""
        try:
            # Get all active companies without any limit
            companies = list(self.companies_col.find({"is_active": True}))
            total_companies = len(companies)
            logger.info(f"Starting to crawl all {total_companies} companies")
            
            # Initialize counters
            total_jobs = 0
            new_jobs = 0
            updated_jobs = 0
            error_count = 0
            error_logs = []
            
            # Process each company
            for company in companies:
                try:
                    company_name = company.get("name")
                    career_page = company.get("career_page")
                    
                    if not career_page:
                        error_logs.append({
                            "company": company_name,
                            "error": "No career page URL found",
                            "timestamp": datetime.now()
                        })
                        error_count += 1
                        continue
                    
                    # Crawl company jobs
                    jobs = await self._crawl_company_jobs(company)
                    
                    # Update counters
                    total_jobs += len(jobs)
                    new_jobs += len([j for j in jobs if j.get("is_new", False)])
                    updated_jobs += len([j for j in jobs if not j.get("is_new", False)])
                    
                except Exception as e:
                    error_logs.append({
                        "company": company.get("name", "Unknown"),
                        "error": str(e),
                        "timestamp": datetime.now()
                    })
                    error_count += 1
                    logger.error(f"Error crawling company {company.get('name')}: {str(e)}")
            
            # Save error logs
            if error_logs:
                self.error_log_col.insert_many(error_logs)
            
            # Send notification
            await self._send_notification(
                total_jobs=total_jobs,
                new_jobs=new_jobs,
                updated_jobs=updated_jobs,
                companies_crawled=total_companies,
                error_count=error_count
            )
            
            return {
                "total_jobs": total_jobs,
                "new_jobs": new_jobs,
                "updated_jobs": updated_jobs,
                "companies_crawled": total_companies,
                "error_count": error_count
            }
            
        except Exception as e:
            logger.error(f"Error in company crawler: {str(e)}")
            raise
    
    async def _crawl_company_jobs(self, company: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Crawl jobs from a single company"""
        # Implementation of company-specific crawling logic
        # This is a placeholder - implement actual crawling logic here
        return []
    
    async def _send_notification(self, **stats):
        """Send notification about crawl results"""
        try:
            from telegram_bot.bot import RemoteJobsBot
            bot = RemoteJobsBot()
            
            message = f"""✅ BUZZ2REMOTE-COMPANIES COMPLETED
🎉 Company crawl successful!
📊 Total jobs found: {stats['total_jobs']}
💾 New jobs: {stats['new_jobs']}
🔄 Updated jobs: {stats['updated_jobs']}
🏢 Companies crawled: {stats['companies_crawled']}
❌ Errors: {stats['error_count']}
🕐 Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} UTC
🌐 Source: Company Career Pages"""

            await bot.send_deployment_notification({
                "environment": "production",
                "status": "success",
                "message": message,
                "timestamp": datetime.now().isoformat(),
                "services": ["company-crawler"],
                "features": ["error-logging"]
            })
            
        except Exception as e:
            logger.error(f"Error sending notification: {str(e)}")

# Run the crawler
if __name__ == "__main__":
    crawler = CompanyCrawler()
    asyncio.run(crawler.crawl_all_companies()) 