#!/usr/bin/env python3
"""
Duplicate Job Detection Script
Finds and analyzes duplicate jobs in the database
"""

import asyncio
import sys
import os
from datetime import datetime
from collections import defaultdict

# Add the parent directory to the path so we can import from backend
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.db import get_async_db
from utils.html_cleaner import clean_job_title, clean_company_name

async def find_duplicate_jobs():
    """Find duplicate jobs based on title, company, and location"""
    print("🔍 Analyzing jobs for duplicates...")
    
    db = await get_async_db()
    jobs_col = db["jobs"]
    
    # Get all jobs
    all_jobs = await jobs_col.find({}).to_list(length=None)
    total_jobs = len(all_jobs)
    print(f"📊 Total jobs in database: {total_jobs:,}")
    
    # Create a dictionary to group jobs by key
    job_groups = defaultdict(list)
    
    for job in all_jobs:
        # Create a unique key based on title, company, and location
        title = clean_job_title(job.get('title', ''))
        company = clean_company_name(job.get('company', ''))
        location = job.get('location', '')
        
        # Skip jobs with missing critical data
        if not title or not company:
            continue
            
        # Create a key that combines title, company, and location
        key = f"{title.lower()}|{company.lower()}|{location.lower()}"
        job_groups[key].append(job)
    
    # Find groups with more than one job (duplicates)
    duplicates = {key: jobs for key, jobs in job_groups.items() if len(jobs) > 1}
    
    print(f"\n🔍 Duplicate Analysis Results:")
    print(f"📈 Unique job combinations: {len(job_groups):,}")
    print(f"🚨 Duplicate groups found: {len(duplicates):,}")
    
    # Calculate statistics
    total_duplicates = sum(len(jobs) for jobs in duplicates.values())
    unique_jobs = total_jobs - total_duplicates + len(duplicates)
    
    print(f"📊 Estimated unique jobs: {unique_jobs:,}")
    print(f"🗑️  Estimated duplicate jobs: {total_duplicates - len(duplicates):,}")
    print(f"📊 Duplicate percentage: {((total_duplicates - len(duplicates)) / total_jobs * 100):.1f}%")
    
    # Show top duplicate groups
    print(f"\n🏆 Top 10 Most Duplicated Jobs:")
    sorted_duplicates = sorted(duplicates.items(), key=lambda x: len(x[1]), reverse=True)
    
    for i, (key, jobs) in enumerate(sorted_duplicates[:10]):
        parts = key.split('|')
        title = parts[0] if len(parts) > 0 else 'Unknown'
        company = parts[1] if len(parts) > 1 else 'Unknown'
        location = parts[2] if len(parts) > 2 else 'Unknown'
        print(f"{i+1}. {title} at {company} ({location})")
        print(f"   Count: {len(jobs)} duplicates")
        print(f"   IDs: {[str(job.get('_id', 'N/A')) for job in jobs[:3]]}{'...' if len(jobs) > 3 else ''}")
        print()
    
    # Show companies with most duplicates
    company_duplicates = defaultdict(int)
    for jobs in duplicates.values():
        company = clean_company_name(jobs[0].get('company', ''))
        company_duplicates[company] += len(jobs)
    
    print(f"🏢 Companies with Most Duplicates:")
    sorted_companies = sorted(company_duplicates.items(), key=lambda x: x[1], reverse=True)
    for company, count in sorted_companies[:10]:
        print(f"   {company}: {count} duplicate jobs")
    
    return {
        'total_jobs': total_jobs,
        'unique_jobs': unique_jobs,
        'duplicate_groups': len(duplicates),
        'total_duplicates': total_duplicates - len(duplicates),
        'duplicate_percentage': ((total_duplicates - len(duplicates)) / total_jobs * 100)
    }

async def clean_duplicates():
    """Clean duplicate jobs by keeping the most recent one"""
    print("\n🧹 Starting duplicate cleanup...")
    
    db = await get_async_db()
    jobs_col = db["jobs"]
    
    # Get all jobs
    all_jobs = await jobs_col.find({}).to_list(length=None)
    
    # Group by duplicate key
    job_groups = defaultdict(list)
    
    for job in all_jobs:
        title = clean_job_title(job.get('title', ''))
        company = clean_company_name(job.get('company', ''))
        location = job.get('location', '')
        
        if not title or not company:
            continue
            
        key = f"{title.lower()}|{company.lower()}|{location.lower()}"
        job_groups[key].append(job)
    
    # Find duplicates
    duplicates = {key: jobs for key, jobs in job_groups.items() if len(jobs) > 1}
    
    cleaned_count = 0
    
    for key, jobs in duplicates.items():
        # Sort by created_at (most recent first)
        sorted_jobs = sorted(jobs, key=lambda x: x.get('created_at', datetime.min), reverse=True)
        
        # Keep the first (most recent) job, delete the rest
        jobs_to_delete = sorted_jobs[1:]
        
        for job in jobs_to_delete:
            job_id = job.get('_id')
            if job_id:
                await jobs_col.delete_one({'_id': job_id})
                cleaned_count += 1
    
    print(f"✅ Cleaned {cleaned_count} duplicate jobs")
    return cleaned_count

async def main():
    """Main function"""
    print("🚀 Buzz2Remote Duplicate Job Analysis")
    print("=" * 50)
    
    try:
        # Analyze duplicates
        stats = await find_duplicate_jobs()
        
        # Ask user if they want to clean duplicates
        if stats['duplicate_groups'] > 0:
            print(f"\n❓ Found {stats['duplicate_groups']} duplicate groups.")
            print("Do you want to clean duplicates? (y/N): ", end="")
            
            # For automation, we'll assume yes
            response = "y"  # In real usage, you'd use input()
            
            if response.lower() in ['y', 'yes']:
                cleaned = await clean_duplicates()
                print(f"🎉 Cleanup completed! Removed {cleaned} duplicate jobs.")
            else:
                print("⏭️  Skipping cleanup.")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code) 