#!/usr/bin/env python3

import sys
sys.path.append('backend')
from database import get_db
from datetime import datetime

def check_jobs_database():
    try:
        db = get_db()
        jobs_col = db['jobs']
        
        # Total jobs count
        total_jobs = jobs_col.count_documents({})
        print(f'📊 Total jobs in database: {total_jobs}')
        
        # Active jobs
        active_jobs = jobs_col.count_documents({'is_active': True})
        print(f'✅ Active jobs: {active_jobs}')
        
        # Today's jobs
        today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        today_jobs = jobs_col.count_documents({
            'last_updated': {'$gte': today_start}
        })
        print(f'📅 Jobs updated today: {today_jobs}')
        
        # Jobs by source
        sources = list(jobs_col.aggregate([
            {'$group': {'_id': '$source_type', 'count': {'$sum': 1}}}
        ]))
        
        print('\n📋 Jobs by source:')
        for source in sources:
            source_name = source['_id'] or 'unknown'
            print(f'   {source_name}: {source["count"]} jobs')
        
        # Top companies
        top_companies = list(jobs_col.aggregate([
            {'$group': {'_id': '$company', 'count': {'$sum': 1}}},
            {'$sort': {'count': -1}},
            {'$limit': 5}
        ]))
        
        print('\n🏢 Top companies by job count:')
        for company in top_companies:
            print(f'   {company["_id"]}: {company["count"]} jobs')
        
        # Recent jobs sample
        recent_jobs = list(jobs_col.find({}).sort('last_updated', -1).limit(5))
        print('\n🔄 Most recent jobs:')
        for job in recent_jobs:
            last_updated = job.get('last_updated', 'unknown')
            if isinstance(last_updated, datetime):
                last_updated = last_updated.strftime('%Y-%m-%d %H:%M')
            print(f'   • {job.get("title", "N/A")} at {job.get("company", "N/A")} ({last_updated})')
        
        # Remote type distribution
        remote_types = list(jobs_col.aggregate([
            {'$group': {'_id': '$remote_type', 'count': {'$sum': 1}}}
        ]))
        
        print('\n🌍 Remote type distribution:')
        for remote_type in remote_types:
            print(f'   {remote_type["_id"]}: {remote_type["count"]} jobs')

    except Exception as e:
        print(f'❌ Database error: {str(e)}')
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    check_jobs_database() 