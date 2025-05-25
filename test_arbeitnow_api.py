#!/usr/bin/env python3
"""
Careful test for Arbeitnow Free API - single request
Bu test çok cömert rate limitler olmasına rağmen dikkatli kullanım için tasarlandı
"""

from external_job_apis import ArbeitnowFreeAPI
from datetime import datetime

def main():
    print("🧪 Arbeitnow Free API - Test")
    print("=" * 50)
    
    api = ArbeitnowFreeAPI()
    
    # Rate limit check
    remaining = api.rate_limiter.requests_remaining()
    print(f"📊 Rate limit remaining: {remaining:,}/500,000")
    print(f"🕐 Next reset: {api.rate_limiter.next_reset_date()}")
    
    print(f"\n🔧 API Configuration:")
    print(f"• Base URL: {api.base_url}")
    print(f"• Rate Limiter: {api.rate_limiter.max_requests:,} requests per {api.rate_limiter.time_period_days} day(s)")
    
    if remaining == 0:
        print("\n❌ No requests remaining! Skipping test.")
        return
    
    print(f"\n⚠️ WARNING: This will use 1 of your {api.rate_limiter.max_requests:,} monthly requests")
    print("⚠️ Proceeding with test...")
    
    # Test with minimal request
    try:
        jobs = api.fetch_remote_jobs(limit=10)  # Small limit for testing
        
        print(f"\n✅ API Test Results:")
        print(f"📊 Jobs fetched: {len(jobs)}")
        print(f"📊 Rate limit after test: {api.rate_limiter.requests_remaining():,}/500,000")
        
        if jobs:
            sample_job = jobs[0]
            print(f"\n📋 Sample Job:")
            print(f"• Title: {sample_job.title}")
            print(f"• Company: {sample_job.company}")
            print(f"• Location: {sample_job.location}")
            print(f"• Job Type: {sample_job.job_type}")
            print(f"• Source: {sample_job.source}")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        return
    
    print(f"\n🎉 Test completed successfully!")

if __name__ == "__main__":
    main() 