#!/usr/bin/env python3
"""
Job Statistics Cronjob
Generates daily job statistics and analytics
"""

import os
import sys
import json
import logging
from datetime import datetime, timedelta
from pymongo import MongoClient
from collections import defaultdict, Counter

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class JobStatistics:
    def __init__(self):
        """Initialize JobStatistics with database connection"""
        self.mongo_uri = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/buzz2remote')
        self.client = MongoClient(self.mongo_uri)
        self.db = self.client.buzz2remote
        self.jobs_collection = self.db.jobs
        self.companies_collection = self.db.companies
        self.stats_collection = self.db.job_statistics
        
    def generate_daily_stats(self):
        """Generate daily job statistics"""
        try:
            today = datetime.now().date()
            yesterday = today - timedelta(days=1)
            
            # Jobs added in last 24 hours
            yesterday_start = datetime.combine(yesterday, datetime.min.time())
            today_start = datetime.combine(today, datetime.min.time())
            
            new_jobs_count = self.jobs_collection.count_documents({
                'created_at': {'$gte': yesterday_start, '$lt': today_start}
            })
            
            # Total jobs
            total_jobs = self.jobs_collection.count_documents({})
            
            # Jobs by type
            job_types = list(self.jobs_collection.aggregate([
                {'$group': {'_id': '$job_type', 'count': {'$sum': 1}}},
                {'$sort': {'count': -1}}
            ]))
            
            # Jobs by location
            locations = list(self.jobs_collection.aggregate([
                {'$group': {'_id': '$location', 'count': {'$sum': 1}}},
                {'$sort': {'count': -1}},
                {'$limit': 10}
            ]))
            
            # Jobs by company
            companies = list(self.jobs_collection.aggregate([
                {'$group': {'_id': '$company', 'count': {'$sum': 1}}},
                {'$sort': {'count': -1}},
                {'$limit': 10}
            ]))
            
            # Remote vs On-site
            remote_count = self.jobs_collection.count_documents({
                '$or': [
                    {'location': {'$regex': 'remote', '$options': 'i'}},
                    {'job_type': {'$regex': 'remote', '$options': 'i'}}
                ]
            })
            
            # Salary statistics
            salary_stats = list(self.jobs_collection.aggregate([
                {'$match': {'salary_min': {'$exists': True, '$gt': 0}}},
                {'$group': {
                    '_id': None,
                    'avg_salary': {'$avg': '$salary_min'},
                    'min_salary': {'$min': '$salary_min'},
                    'max_salary': {'$max': '$salary_max'},
                    'count': {'$sum': 1}
                }}
            ]))
            
            # Technology stack analysis
            tech_skills = []
            skill_counter = Counter()
            
            for job in self.jobs_collection.find({'skills': {'$exists': True}}, {'skills': 1}):
                if job.get('skills'):
                    for skill in job['skills']:
                        skill_counter[skill.lower()] += 1
            
            top_skills = skill_counter.most_common(20)
            
            # Create statistics document
            stats_doc = {
                'date': today.isoformat(),
                'timestamp': datetime.now(),
                'daily_stats': {
                    'new_jobs_24h': new_jobs_count,
                    'total_jobs': total_jobs,
                    'remote_jobs': remote_count,
                    'onsite_jobs': total_jobs - remote_count
                },
                'job_distribution': {
                    'by_type': [{'type': item['_id'], 'count': item['count']} for item in job_types],
                    'by_location': [{'location': item['_id'], 'count': item['count']} for item in locations],
                    'by_company': [{'company': item['_id'], 'count': item['count']} for item in companies]
                },
                'salary_stats': salary_stats[0] if salary_stats else None,
                'top_skills': [{'skill': skill, 'count': count} for skill, count in top_skills],
                'generated_at': datetime.now()
            }
            
            # Save to database
            self.stats_collection.replace_one(
                {'date': today.isoformat()},
                stats_doc,
                upsert=True
            )
            
            logger.info(f"✅ Daily statistics generated successfully for {today}")
            logger.info(f"📊 Stats: {new_jobs_count} new jobs, {total_jobs} total jobs, {remote_count} remote jobs")
            
            return stats_doc
            
        except Exception as e:
            logger.error(f"❌ Error generating daily statistics: {e}")
            return None
    
    def generate_weekly_stats(self):
        """Generate weekly job statistics"""
        try:
            today = datetime.now().date()
            week_ago = today - timedelta(days=7)
            
            week_start = datetime.combine(week_ago, datetime.min.time())
            today_start = datetime.combine(today, datetime.min.time())
            
            # Weekly job trends
            weekly_jobs = list(self.jobs_collection.aggregate([
                {'$match': {'created_at': {'$gte': week_start, '$lt': today_start}}},
                {'$group': {
                    '_id': {
                        'year': {'$year': '$created_at'},
                        'month': {'$month': '$created_at'},
                        'day': {'$dayOfMonth': '$created_at'}
                    },
                    'count': {'$sum': 1}
                }},
                {'$sort': {'_id': 1}}
            ]))
            
            # Company growth
            company_growth = list(self.jobs_collection.aggregate([
                {'$match': {'created_at': {'$gte': week_start}}},
                {'$group': {'_id': '$company', 'count': {'$sum': 1}}},
                {'$sort': {'count': -1}},
                {'$limit': 20}
            ]))
            
            weekly_stats = {
                'week_ending': today.isoformat(),
                'weekly_trends': weekly_jobs,
                'top_hiring_companies': company_growth,
                'generated_at': datetime.now()
            }
            
            # Save weekly stats
            self.stats_collection.update_one(
                {'date': today.isoformat()},
                {'$set': {'weekly_stats': weekly_stats}},
                upsert=True
            )
            
            logger.info(f"✅ Weekly statistics generated successfully")
            return weekly_stats
            
        except Exception as e:
            logger.error(f"❌ Error generating weekly statistics: {e}")
            return None
    
    def cleanup_old_stats(self, days_to_keep=30):
        """Clean up old statistics older than specified days"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days_to_keep)
            
            result = self.stats_collection.delete_many({
                'timestamp': {'$lt': cutoff_date}
            })
            
            logger.info(f"🧹 Cleaned up {result.deleted_count} old statistics entries")
            return result.deleted_count
            
        except Exception as e:
            logger.error(f"❌ Error cleaning up old statistics: {e}")
            return 0
    
    def export_stats_to_file(self):
        """Export latest statistics to JSON file"""
        try:
            latest_stats = self.stats_collection.find_one(
                {},
                sort=[('timestamp', -1)]
            )
            
            if latest_stats:
                # Convert ObjectId to string for JSON serialization
                latest_stats['_id'] = str(latest_stats['_id'])
                
                filename = f"job_statistics_{datetime.now().strftime('%Y%m%d')}.json"
                filepath = os.path.join('data', filename)
                
                # Create data directory if it doesn't exist
                os.makedirs('data', exist_ok=True)
                
                with open(filepath, 'w') as f:
                    json.dump(latest_stats, f, indent=2, default=str)
                
                logger.info(f"📁 Statistics exported to {filepath}")
                return filepath
                
        except Exception as e:
            logger.error(f"❌ Error exporting statistics: {e}")
            return None
    
    def run_full_analytics(self):
        """Run complete analytics suite"""
        logger.info("🚀 Starting job statistics analytics...")
        
        # Generate daily stats
        daily_stats = self.generate_daily_stats()
        
        # Generate weekly stats (only on Sunday)
        if datetime.now().weekday() == 6:  # Sunday
            weekly_stats = self.generate_weekly_stats()
        
        # Cleanup old data
        self.cleanup_old_stats()
        
        # Export to file
        export_path = self.export_stats_to_file()
        
        logger.info("✅ Job statistics analytics completed")
        
        return {
            'daily_stats': daily_stats,
            'export_path': export_path,
            'timestamp': datetime.now()
        }

def main():
    """Main function for cronjob execution"""
    try:
        stats_generator = JobStatistics()
        result = stats_generator.run_full_analytics()
        
        print(f"✅ Job statistics cronjob completed successfully")
        print(f"📊 Generated at: {result['timestamp']}")
        
        if result.get('export_path'):
            print(f"📁 Exported to: {result['export_path']}")
        
        return 0
        
    except Exception as e:
        logger.error(f"❌ Job statistics cronjob failed: {e}")
        return 1

if __name__ == "__main__":
    exit(main()) 