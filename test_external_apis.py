#!/usr/bin/env python3
"""
Test script for External API integrations
"""

from external_job_apis import ExternalJobAPIManager, FantasticJobsAPI, JobPostingFeedAPI, RemoteOKAPI, ArbeitnowFreeAPI
from datetime import datetime

def main():
    print("🧪 Testing External API Integrations")
    print("=" * 50)
    
    # Test individual APIs
    print("\n📊 Rate Limit Status:")
    
    # Fantastic Jobs
    fantastic = FantasticJobsAPI()
    print(f"• Fantastic Jobs: {fantastic.rate_limiter.requests_remaining()}/{fantastic.rate_limiter.max_requests}")
    
    # Job Posting Feed
    job_posting = JobPostingFeedAPI()
    print(f"• Job Posting Feed: {job_posting.rate_limiter.requests_remaining()}/{job_posting.rate_limiter.max_requests}")
    
    # RemoteOK
    remoteok = RemoteOKAPI()
    print(f"• RemoteOK: {remoteok.rate_limiter.requests_remaining()}/{remoteok.rate_limiter.max_requests}")
    
    # Arbeitnow Free
    arbeitnow = ArbeitnowFreeAPI()
    print(f"• Arbeitnow Free: {arbeitnow.rate_limiter.requests_remaining()}/{arbeitnow.rate_limiter.max_requests}")
    
    # Test manager
    print("\n🔧 Manager Configuration:")
    manager = ExternalJobAPIManager()
    print(f"Available APIs: {list(manager.apis.keys())}")
    
    # Check scheduling
    print("\n📅 Scheduling Check:")
    today = datetime.now()
    fantastic_days = [1, 3, 5, 7, 9, 11, 13, 15, 17, 19, 21, 23, 25, 27, 29]
    job_posting_days = [1, 8, 15, 22, 29]
    remoteok_daily = True  # Her gün
    arbeitnow_daily = True  # Her gün (süper cömert rate limit)
    
    print(f"Bugün: {today.strftime('%Y-%m-%d')} (gün: {today.day})")
    print(f"• Fantastic Jobs çalışsın mı: {today.day in fantastic_days}")
    print(f"• Job Posting Feed çalışsın mı: {today.day in job_posting_days}")
    print(f"• RemoteOK çalışsın mı: {remoteok_daily}")
    print(f"• Arbeitnow Free çalışsın mı: {arbeitnow_daily}")
    
    # Summary
    print(f"\n🎯 API Summary:")
    print(f"• Total APIs: 4")
    print(f"• Daily APIs: 2 (RemoteOK, Arbeitnow Free)")
    print(f"• Scheduled APIs: 2 (Fantastic Jobs, Job Posting Feed)")
    print(f"• Today's active APIs: {sum([today.day in fantastic_days, today.day in job_posting_days, remoteok_daily, arbeitnow_daily])}")
    
    # Only test if we have remaining requests
    print("\n🔬 API Tests:")
    
    if fantastic.rate_limiter.requests_remaining() > 0:
        print("⚠️ Fantastic Jobs has remaining requests - but skipping to save quota")
    else:
        print("❌ Fantastic Jobs - no requests remaining")
    
    if job_posting.rate_limiter.requests_remaining() > 0:
        print("⚠️ Job Posting Feed has remaining requests - but skipping to save quota")
    else:
        print("❌ Job Posting Feed - no requests remaining")
        
    if remoteok.rate_limiter.requests_remaining() > 0:
        print("⚠️ RemoteOK has remaining requests - but skipping to save quota")
    else:
        print("❌ RemoteOK - no requests remaining")
    
    if arbeitnow.rate_limiter.requests_remaining() > 0:
        print("⚠️ Arbeitnow Free has remaining requests - but skipping to save quota")
    else:
        print("❌ Arbeitnow Free - no requests remaining")
    
    print("\n✅ Test completed - No API calls made to preserve rate limits!")

if __name__ == "__main__":
    main() 