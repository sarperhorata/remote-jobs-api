#!/usr/bin/env python3
"""
Run Buzz2Remote crawler
"""

import sys
import os
import asyncio
import logging
from datetime import datetime

# Setup paths
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))
sys.path.insert(0, os.path.dirname(__file__))

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def run_crawler():
    """Run the distill crawler"""
    print("🚀 STARTING BUZZ2REMOTE CRAWLER")
    print("=" * 50)
    
    try:
        # Import crawler
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))
        from distill_crawler import DistillCrawler
        
        crawler = DistillCrawler()
        print("✅ Crawler imported successfully")
        
        # Load companies
        crawler.load_companies_data()
        total_companies = len(crawler.companies_data)
        print(f"📊 Loaded {total_companies} companies for crawling")
        
        if total_companies == 0:
            print("❌ No companies data found!")
            return
        
        # Start crawling
        print(f"🚀 Starting to crawl ALL {total_companies} companies (NO LIMIT)...")
        start_time = datetime.now()
        
        jobs = await crawler.crawl_all_companies()
        
        end_time = datetime.now()
        duration = end_time - start_time
        
        # Calculate results
        total_jobs = len(jobs) if jobs else 0
        successful_companies = len(set([job.company for job in jobs])) if jobs else 0
        failed_companies = total_companies - successful_companies
        
        print(f"\n🎯 FINAL CRAWLER RESULTS:")
        print(f"📊 Total companies processed: {total_companies}")
        print(f"✅ Successful companies: {successful_companies}")
        print(f"❌ Failed companies: {failed_companies}")
        print(f"🎯 Total jobs found: {total_jobs}")
        print(f"⏱️ Duration: {duration}")
        
        # Save to database if we have jobs
        if jobs:
            print(f"\n💾 Saving {total_jobs} jobs to database...")
            db_result = crawler.save_jobs_to_database(jobs)
            print(f"💾 Database save result:")
            print(f"   📝 New jobs: {db_result.get('new_jobs', 0)}")
            print(f"   🔄 Updated jobs: {db_result.get('updated_jobs', 0)}")
            print(f"   🏢 New companies: {db_result.get('new_companies', 0)}")
            print(f"   🔄 Updated companies: {db_result.get('updated_companies', 0)}")
        
        # Try to send Telegram notification
        try:
            from external_job_apis import ServiceNotifier
            notifier = ServiceNotifier()
            
            notification_data = {
                'service': 'BUZZ2REMOTE-COMPANIES',
                'status': 'success' if total_jobs > 0 else 'warning',
                'companies_processed': total_companies,
                'successful_companies': successful_companies,
                'failed_companies': failed_companies,
                'jobs_found': total_jobs,
                'new_jobs': db_result.get('new_jobs', 0) if jobs else 0,
                'duration': str(duration),
                'timestamp': datetime.now().isoformat()
            }
            
            notifier.send_crawler_summary(notification_data)
            print("📱 Telegram notification sent!")
            
        except Exception as telegram_error:
            print(f"⚠️ Telegram notification failed: {telegram_error}")
        
        return {
            'total_companies': total_companies,
            'successful_companies': successful_companies,
            'failed_companies': failed_companies,
            'total_jobs': total_jobs,
            'duration': duration
        }
        
    except Exception as e:
        print(f"❌ Crawler failed: {e}")
        logger.error(f"Crawler error: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == '__main__':
    asyncio.run(run_crawler()) 