#!/usr/bin/env python3
"""
Cleanup Duplicate Jobs Script
Bu script veritabanındaki duplicate iş ilanlarını temizler.
"""

import asyncio
import logging
from datetime import datetime
from database.db import get_database_client
from collections import defaultdict

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def cleanup_duplicates():
    """Clean up duplicate jobs from the database"""
    client = await get_database_client()
    db = client.buzz2remote
    jobs_collection = db.jobs
    
    print('🧹 DUPLICATE İŞ İLANLARI TEMİZLİĞİ')
    print('=' * 60)
    
    # Get all jobs
    all_jobs = await jobs_collection.find().to_list(length=None)
    total_jobs = len(all_jobs)
    print(f'📊 Toplam iş ilanı: {total_jobs:,}')
    
    # Group by duplicate criteria
    title_company_source_url_groups = defaultdict(list)
    title_company_location_groups = defaultdict(list)
    
    for job in all_jobs:
        title = job.get('title', '').strip().lower()
        company = job.get('company', '').strip().lower()
        source_url = job.get('source_url', '').strip()
        location = job.get('location', '').strip().lower()
        
        # Group by title + company + source_url
        if title and company and source_url:
            key = f'{title}|{company}|{source_url}'
            title_company_source_url_groups[key].append(job)
        
        # Group by title + company + location
        if title and company and location:
            key = f'{title}|{company}|{location}'
            title_company_location_groups[key].append(job)
    
    # Find duplicates
    duplicates_by_source_url = {k: v for k, v in title_company_source_url_groups.items() if len(v) > 1}
    duplicates_by_location = {k: v for k, v in title_company_location_groups.items() if len(v) > 1}
    
    print(f'🔄 Title+Company+SourceURL duplicate grupları: {len(duplicates_by_source_url)}')
    print(f'🔄 Title+Company+Location duplicate grupları: {len(duplicates_by_location)}')
    
    # Clean up duplicates by source_url (priority)
    deleted_count = 0
    updated_count = 0
    
    print('\n🧹 SOURCE_URL DUPLICATE\'LARI TEMİZLENİYOR...')
    for key, jobs in duplicates_by_source_url.items():
        if len(jobs) > 1:
            # Keep the first job, delete the rest
            jobs_to_keep = jobs[0]
            jobs_to_delete = jobs[1:]
            
            # Delete duplicate jobs
            for job in jobs_to_delete:
                job_id = job['_id']
                result = await jobs_collection.delete_one({'_id': job_id})
                if result.deleted_count > 0:
                    deleted_count += 1
            
            # Update the kept job with latest data (excluding _id)
            latest_job = max(jobs, key=lambda x: x.get('created_at', datetime.min))
            if latest_job != jobs_to_keep:
                # Remove _id from update data
                update_data = {k: v for k, v in latest_job.items() if k != '_id'}
                result = await jobs_collection.update_one(
                    {'_id': jobs_to_keep['_id']},
                    {'$set': update_data}
                )
                if result.modified_count > 0:
                    updated_count += 1
    
    print(f'✅ {deleted_count} duplicate silindi')
    print(f'✅ {updated_count} ilan güncellendi')
    
    # Clean up remaining duplicates by location
    print('\n🧹 LOCATION DUPLICATE\'LARI TEMİZLENİYOR...')
    location_deleted = 0
    location_updated = 0
    
    for key, jobs in duplicates_by_location.items():
        if len(jobs) > 1:
            # Keep the first job, delete the rest
            jobs_to_keep = jobs[0]
            jobs_to_delete = jobs[1:]
            
            # Delete duplicate jobs
            for job in jobs_to_delete:
                job_id = job['_id']
                result = await jobs_collection.delete_one({'_id': job_id})
                if result.deleted_count > 0:
                    location_deleted += 1
            
            # Update the kept job with latest data
            latest_job = max(jobs, key=lambda x: x.get('created_at', datetime.min))
            if latest_job != jobs_to_keep:
                result = await jobs_collection.update_one(
                    {'_id': jobs_to_keep['_id']},
                    {'$set': latest_job}
                )
                if result.modified_count > 0:
                    location_updated += 1
    
    print(f'✅ {location_deleted} location duplicate silindi')
    print(f'✅ {location_updated} location ilan güncellendi')
    
    # Final statistics
    remaining_jobs = await jobs_collection.count_documents({})
    total_deleted = deleted_count + location_deleted
    total_updated = updated_count + location_updated
    
    print(f'\n📊 TEMİZLİK SONUÇLARI:')
    print(f'   Başlangıç: {total_jobs:,} ilan')
    print(f'   Silinen: {total_deleted:,} duplicate')
    print(f'   Güncellenen: {total_updated:,} ilan')
    print(f'   Kalan: {remaining_jobs:,} ilan')
    print(f'   Temizlik oranı: {(total_deleted/total_jobs*100):.1f}%')
    
    return {
        'initial_count': total_jobs,
        'deleted_count': total_deleted,
        'updated_count': total_updated,
        'final_count': remaining_jobs,
        'cleanup_ratio': total_deleted/total_jobs*100
    }

async def test_duplicate_detection():
    """Test the new duplicate detection system"""
    client = await get_database_client()
    db = client.buzz2remote
    jobs_collection = db.jobs
    
    print('\n🧪 DUPLICATE DETECTION TEST')
    print('=' * 40)
    
    # Test with a known duplicate
    test_job = {
        'title': 'Product Manager - Ad Tech',
        'company': 'MonetizeMore - Career Page',
        'source_url': 'https://monetizem.applytojob.com/apply',
        'location': 'Remote',
        'job_type': 'Full-time',
        'source': 'distill_crawler',
        'external_id': 'test_duplicate_detection_123',
        'description': 'Test job for duplicate detection'
    }
    
    # Try to save the same job twice
    from database.job_repository import JobRepository
    repo = JobRepository()
    
    # First save
    job_id_1 = repo.save_job(test_job.copy())
    print(f'İlk kayıt: {job_id_1}')
    
    # Second save (should be detected as duplicate)
    job_id_2 = repo.save_job(test_job.copy())
    print(f'İkinci kayıt: {job_id_2}')
    
    if job_id_1 == job_id_2:
        print('✅ Duplicate detection çalışıyor!')
    else:
        print('❌ Duplicate detection çalışmıyor!')

if __name__ == "__main__":
    async def main():
        # Run cleanup
        results = await cleanup_duplicates()
        
        # Test duplicate detection
        await test_duplicate_detection()
        
        print(f'\n🎉 Temizlik tamamlandı!')
        print(f'   {results["deleted_count"]:,} duplicate silindi')
        print(f'   {results["cleanup_ratio"]:.1f}% temizlik oranı')
    
    asyncio.run(main()) 