#!/usr/bin/env python3
"""
Test script for Mailgun and Sentry integrations
"""

import sys
import os
import asyncio
from datetime import datetime

# Add backend to path
sys.path.insert(0, 'backend')
sys.path.insert(0, '.')

def test_mailgun():
    """Test Mailgun email service"""
    print("🧪 Testing Mailgun integration...")
    
    try:
        from backend.services.mailgun_service import mailgun_service
        print("✅ Mailgun service imported successfully")
        
        # Get stats first
        stats = mailgun_service.get_stats()
        print(f"📊 Mailgun stats: {stats}")
        
        # Send test email to sarperhorata@gmail.com
        print("📧 Sending test email to sarperhorata@gmail.com...")
        result = mailgun_service.send_test_email('sarperhorata@gmail.com')
        print(f"📧 Mailgun test result: {result}")
        
        if result.get('success'):
            print("✅ TEST EMAIL SENT SUCCESSFULLY to sarperhorata@gmail.com!")
            print(f"📨 Message ID: {result.get('message_id')}")
        else:
            print(f"❌ Email failed: {result.get('error')}")
            print(f"🔍 Details: {result}")
            
        return result.get('success', False)
        
    except Exception as e:
        print(f"❌ Mailgun test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_sentry():
    """Test Sentry error reporting"""
    print("\n🧪 Testing Sentry integration...")
    
    try:
        import sentry_sdk
        print("✅ Sentry SDK imported successfully")
        
        # Send test error to Sentry
        print("🚨 Sending test error to Sentry...")
        sentry_sdk.capture_message(
            '🧪 TEST ERROR from Buzz2Remote - Integration test successful!', 
            level='error'
        )
        
        # Send test exception
        try:
            raise ValueError("🧪 Test exception for Sentry integration - this is expected!")
        except Exception as e:
            sentry_sdk.capture_exception(e)
        
        print("✅ TEST ERROR SENT TO SENTRY!")
        print("📱 Check your Telegram for Sentry notifications")
        return True
        
    except Exception as e:
        print(f"❌ Sentry test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_telegram_bot():
    """Test Telegram bot functionality"""
    print("\n🧪 Testing Telegram Bot integration...")
    
    try:
        from backend.telegram_bot.bot import RemoteJobsBot
        bot = RemoteJobsBot()
        print(f"✅ Telegram bot imported, enabled: {bot.enabled}")
        
        if bot.enabled:
            print("🤖 Telegram bot is configured and ready")
            return True
        else:
            print("⚠️ Telegram bot is disabled - check environment variables")
            return False
            
    except Exception as e:
        print(f"❌ Telegram bot test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_crawler():
    """Test Buzz2Remote crawler"""
    print("\n🏢 Testing Buzz2Remote Crawler...")
    
    try:
        from backend.distill_crawler import DistillCrawler
        from backend.external_job_apis import ServiceNotifier
        
        crawler = DistillCrawler()
        notifier = ServiceNotifier()
        
        print("✅ Crawler imported successfully")
        
        # Load companies data
        crawler.load_companies_data()
        total_companies = len(crawler.companies_data)
        print(f"📊 Loaded {total_companies} companies for crawling")
        
        if total_companies == 0:
            print("❌ No companies loaded!")
            return False
        
        # Send start notification
        start_notification = {
            'service': 'BUZZ2REMOTE-COMPANIES',
            'status': 'starting',
            'companies_total': total_companies,
            'timestamp': datetime.now().isoformat()
        }
        notifier.send_crawler_summary(start_notification)
        print("📱 Start notification sent to Telegram")
        
        print(f"🚀 Starting to crawl {total_companies} companies...")
        
        # Run crawler
        start_time = datetime.now()
        jobs = await crawler.crawl_all_companies()
        end_time = datetime.now()
        duration = end_time - start_time
        
        # Get results
        total_jobs = len(jobs)
        successful_companies = len(set([job.company for job in jobs]))
        failed_companies = total_companies - successful_companies
        
        print(f"\n🎯 CRAWLER RESULTS:")
        print(f"📊 Total companies: {total_companies}")
        print(f"✅ Successful companies: {successful_companies}")
        print(f"❌ Failed companies: {failed_companies}")
        print(f"🎯 Total jobs found: {total_jobs}")
        print(f"⏱️ Duration: {duration}")
        
        # Save results to database
        if jobs:
            print("💾 Saving jobs to database...")
            db_result = crawler.save_jobs_to_database(jobs)
            print(f"💾 Database save result: {db_result}")
        
        # Send completion notification
        completion_notification = {
            'service': 'BUZZ2REMOTE-COMPANIES',
            'status': 'success' if total_jobs > 0 else 'warning',
            'companies_processed': total_companies,
            'companies_successful': successful_companies,
            'companies_failed': failed_companies,
            'jobs_found': total_jobs,
            'new_jobs': db_result.get('new_jobs', 0) if jobs else 0,
            'duration': str(duration),
            'timestamp': datetime.now().isoformat()
        }
        notifier.send_crawler_summary(completion_notification)
        print("📱 Completion notification sent to Telegram")
        
        return True
        
    except Exception as e:
        print(f"❌ Crawler test failed: {e}")
        import traceback
        traceback.print_exc()
        
        # Send error notification
        try:
            error_notification = {
                'service': 'BUZZ2REMOTE-COMPANIES',
                'status': 'error',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
            notifier.send_crawler_summary(error_notification)
        except:
            pass
        
        return False

async def main():
    """Run all tests"""
    print("🚀 BUZZ2REMOTE INTEGRATION TESTS")
    print("=" * 50)
    
    results = {
        'mailgun': False,
        'sentry': False,
        'telegram': False,
        'crawler': False
    }
    
    # Test 1: Mailgun
    results['mailgun'] = test_mailgun()
    
    # Test 2: Sentry
    results['sentry'] = test_sentry()
    
    # Test 3: Telegram Bot
    results['telegram'] = test_telegram_bot()
    
    # Test 4: Crawler
    results['crawler'] = await test_crawler()
    
    # Summary
    print("\n" + "=" * 50)
    print("📋 TEST SUMMARY:")
    print("=" * 50)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name.upper()}: {status}")
    
    total_passed = sum(results.values())
    total_tests = len(results)
    
    print(f"\n🎯 Overall: {total_passed}/{total_tests} tests passed")
    
    if total_passed == total_tests:
        print("🎉 ALL TESTS PASSED!")
    else:
        print("⚠️ Some tests failed - check logs above")

if __name__ == '__main__':
    asyncio.run(main()) 