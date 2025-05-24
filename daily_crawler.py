#!/usr/bin/env python3
"""
Daily Job Crawler for Buzz2Remote
Crawls all 471 companies from distill export daily
"""

import sys
import os
import asyncio
import logging
from datetime import datetime
from distill_crawler import DistillCrawler

# Setup logging for production
def setup_logging():
    """Setup logging with both file and console output"""
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)
    
    log_filename = os.path.join(log_dir, f"crawler_{datetime.now().strftime('%Y%m%d')}.log")
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_filename),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    return logging.getLogger(__name__)

async def daily_crawl():
    """Run daily crawl of all companies"""
    logger = setup_logging()
    
    start_time = datetime.now()
    logger.info("🚀 Starting daily job crawl...")
    logger.info(f"⏰ Start time: {start_time}")
    
    try:
        # Initialize crawler
        crawler = DistillCrawler()
        
        # Crawl ALL companies (no limit)
        logger.info("🕷️ Crawling all companies from distill export...")
        jobs = await crawler.crawl_all_companies()  # No max_companies limit
        
        # Save to database
        if jobs:
            logger.info("💾 Saving jobs to database...")
            result = crawler.save_jobs_to_database(jobs)
            
            logger.info("✅ Daily crawl completed successfully!")
            logger.info(f"📊 Results: {result['new_jobs']} new, {result['updated_jobs']} updated")
            logger.info(f"📊 Total processed: {result['total_processed']}")
        else:
            logger.warning("⚠️ No jobs found during crawl")
        
        # Calculate duration
        end_time = datetime.now()
        duration = end_time - start_time
        logger.info(f"⏱️ Total duration: {duration}")
        
        return {
            "success": True,
            "jobs_found": len(jobs),
            "new_jobs": result.get('new_jobs', 0) if jobs else 0,
            "updated_jobs": result.get('updated_jobs', 0) if jobs else 0,
            "duration": str(duration),
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Daily crawl failed: {str(e)}")
        logger.exception("Full error traceback:")
        
        return {
            "success": False,
            "error": str(e),
            "start_time": start_time.isoformat(),
            "end_time": datetime.now().isoformat()
        }

def main():
    """Main entry point for daily crawler"""
    try:
        # Run async crawler
        result = asyncio.run(daily_crawl())
        
        # Exit codes for cron monitoring
        if result["success"]:
            print(f"\n🎉 Daily crawl completed successfully!")
            print(f"📊 New: {result['new_jobs']}, Updated: {result['updated_jobs']}")
            sys.exit(0)  # Success
        else:
            print(f"\n❌ Daily crawl failed: {result['error']}")
            sys.exit(1)  # Failure
            
    except KeyboardInterrupt:
        print("\n⏸️ Crawl interrupted by user")
        sys.exit(2)  # Interrupted
    except Exception as e:
        print(f"\n💥 Unexpected error: {str(e)}")
        sys.exit(3)  # Unexpected error

if __name__ == '__main__':
    main() 