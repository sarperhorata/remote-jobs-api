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
import traceback

# Add backend to path
sys.path.append('backend')

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def send_telegram_notification(message: str, is_error: bool = False):
    """Send notification to @buzz2remote channel"""
    try:
        from backend.utils.telegram import TelegramNotifier
        notifier = TelegramNotifier()
        
        if is_error:
            await notifier.send_error_notification("Crawler Error", message, "Daily Crawler")
        else:
            await notifier.send_message(message)
            
    except Exception as e:
        logger.error(f"Failed to send Telegram notification: {str(e)}")

async def main():
    start_time = datetime.now()
    
    try:
        logger.info("🚀 Starting daily crawl...")
        
        # Send start notification
        await send_telegram_notification(
            f"🚀 <b>Daily Crawl Started</b>\n\n"
            f"<b>Time:</b> {start_time.strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"<b>Target:</b> 471 companies"
        )
        
        # Import and run crawler
        from distill_crawler import DistillCrawler
        
        crawler = DistillCrawler()
        
        # Crawl all companies
        logger.info("📊 Loading companies data...")
        crawler.load_companies_data()
        
        logger.info(f"🕷️ Crawling {len(crawler.companies_data)} companies...")
        jobs = await crawler.crawl_all_companies()
        
        # Save to database
        logger.info("💾 Saving jobs to database...")
        result = crawler.save_jobs_to_database(jobs)
        
        # Calculate duration
        end_time = datetime.now()
        duration = end_time - start_time
        
        # Send success notification
        success_message = (
            f"✅ <b>Daily Crawl Completed</b>\n\n"
            f"<b>📊 Results:</b>\n"
            f"• Total Jobs: {len(jobs):,}\n"
            f"• New Jobs: {result['new_jobs']:,}\n"
            f"• Updated Jobs: {result['updated_jobs']:,}\n"
            f"• Companies Crawled: {len(crawler.companies_data)}\n\n"
            f"<b>⏱️ Duration:</b> {str(duration).split('.')[0]}\n"
            f"<b>📅 Completed:</b> {end_time.strftime('%Y-%m-%d %H:%M:%S')}"
        )
        
        logger.info("✅ Daily crawl completed successfully!")
        logger.info(f"📊 Results: {result['new_jobs']} new, {result['updated_jobs']} updated")
        logger.info(f"📊 Total processed: {len(jobs)}")
        logger.info(f"⏱️ Total duration: {duration}")
        
        await send_telegram_notification(success_message)
        
        # Also send crawler status using the dedicated method
        try:
            from backend.utils.telegram import TelegramNotifier
            notifier = TelegramNotifier()
            await notifier.send_crawler_status(
                total_jobs=len(jobs),
                new_jobs=result['new_jobs'],
                updated_jobs=result['updated_jobs'],
                errors=0
            )
        except Exception as e:
            logger.error(f"Failed to send crawler status: {str(e)}")
        
        print(f"🎉 Daily crawl completed successfully!")
        print(f"📊 New: {result['new_jobs']}, Updated: {result['updated_jobs']}")
        
    except Exception as e:
        error_message = f"❌ Daily crawl failed: {str(e)}"
        logger.error(error_message)
        logger.error(traceback.format_exc())
        
        # Send error notification
        error_details = (
            f"❌ <b>Daily Crawl Failed</b>\n\n"
            f"<b>Error:</b> {str(e)}\n"
            f"<b>Time:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"<b>Duration:</b> {str(datetime.now() - start_time).split('.')[0]}"
        )
        
        await send_telegram_notification(error_details, is_error=True)
        
        print(f"❌ Daily crawl failed: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    # Set OpenAI API key if provided
    if len(sys.argv) > 1 and sys.argv[1].startswith('sk-'):
        os.environ['OPENAI_API_KEY'] = sys.argv[1]
        logger.info("OpenAI API key set from command line")
    
    asyncio.run(main()) 