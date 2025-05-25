#!/usr/bin/env python3
"""
Careful test for Job Posting Feed API - single request only!
Bu test ayda sadece 5 isteğimiz olduğu için dikkatli kullanılmalı
"""

from external_job_apis import JobPostingFeedAPI
from datetime import datetime

def main():
    print("🧪 Job Posting Feed API - Careful Test")
    print("=" * 50)
    
    api = JobPostingFeedAPI()
    
    # Rate limit check
    remaining = api.rate_limiter.requests_remaining()
    print(f"📊 Rate limit remaining: {remaining}/5")
    
    if remaining == 0:
        print("❌ No requests remaining! Skipping test.")
        return
    
    print("\n⚠️ WARNING: This will use 1 of your 5 monthly requests!")
    print("⚠️ Proceeding with test...")
    
    # Test with minimal request
    try:
        jobs = api.fetch_remote_jobs(limit=10)  # Small limit for testing
        
        print(f"\n✅ Test completed!")
        print(f"📦 Jobs found: {len(jobs)}")
        print(f"📊 Rate limit remaining: {api.rate_limiter.requests_remaining()}/5")
        
        if jobs:
            print(f"\n📋 Sample job:")
            job = jobs[0]
            print(f"• Title: {job.title}")
            print(f"• Company: {job.company}")
            print(f"• Location: {job.location}")
            print(f"• Source: {job.source}")
            print(f"• URL: {job.url}")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main() 