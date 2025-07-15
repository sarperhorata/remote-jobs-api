#!/usr/bin/env python3
"""
Job Title Fixing Script
Bu script mevcut veritabanındaki bozuk job title'ları temizler ve düzgün field'lara ayırır.
"""

import asyncio
import sys
import os
import logging
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from utils.job_title_parser import parse_job_title
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class JobTitleFixer:
    def __init__(self):
        self.mongo_url = os.getenv("MONGODB_URL", "mongodb://localhost:27017/buzz2remote")
        self.client = None
        self.db = None
        
    async def connect(self):
        """Connect to MongoDB"""
        try:
            self.client = AsyncIOMotorClient(self.mongo_url)
            self.db = self.client.buzz2remote  # Use specific database name
            logger.info("Connected to MongoDB")
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise

    async def disconnect(self):
        """Disconnect from MongoDB"""
        if self.client:
            self.client.close()
            logger.info("Disconnected from MongoDB")

    async def analyze_job_titles(self):
        """Analyze job titles to identify problematic ones"""
        logger.info("Analyzing job titles...")
        
        # Find jobs with potentially problematic titles
        # Look for titles that contain company names or remote info
        pipeline = [
            {
                "$match": {
                    "$or": [
                        {"title": {"$regex": "[a-z][A-Z]", "$options": "i"}},  # CamelCase
                        {"title": {"$regex": "Remote", "$options": "i"}},      # Contains Remote
                        {"title": {"$regex": "[A-Z]{2,}", "$options": "i"}},   # Multiple capitals
                    ]
                }
            },
            {
                "$project": {
                    "title": 1,
                    "company": 1,
                    "location": 1
                }
            },
            {"$limit": 100}  # Sample for analysis
        ]
        
        cursor = self.db.jobs.aggregate(pipeline)
        problematic_jobs = await cursor.to_list(length=100)
        
        logger.info(f"Found {len(problematic_jobs)} potentially problematic job titles")
        
        examples = []
        for job in problematic_jobs[:10]:  # Show first 10 examples
            parsed = parse_job_title(job.get('title', ''))
            examples.append({
                'original': job.get('title'),
                'parsed_title': parsed['title'],
                'parsed_company': parsed['company'],
                'current_company': job.get('company'),
                'is_remote': parsed['is_remote'],
                'location_restriction': parsed['location_restriction']
            })
            
        logger.info("Examples of problematic titles:")
        for i, example in enumerate(examples, 1):
            logger.info(f"{i}. '{example['original']}' -> Title: '{example['parsed_title']}', Company: '{example['parsed_company']}'")
            
        return len(problematic_jobs)

    async def fix_job_titles(self, dry_run=True, limit=None):
        """Fix job titles in the database"""
        logger.info(f"Starting job title fix (dry_run={dry_run})")
        
        # Find all jobs that need fixing
        query = {
            "$or": [
                {"title": {"$regex": "[a-z][A-Z]"}},  # CamelCase
                {"title": {"$regex": "Remote", "$options": "i"}},  # Contains Remote
                {"title": {"$regex": "^.*[A-Z]{2,}.*$"}},  # Multiple capitals
            ]
        }
        
        # Get total count
        total_count = await self.db.jobs.count_documents(query)
        logger.info(f"Found {total_count} jobs that need title fixing")
        
        if limit:
            logger.info(f"Processing only first {limit} jobs")
        
        # Process jobs in batches
        batch_size = 100
        processed = 0
        updated = 0
        errors = 0
        
        cursor = self.db.jobs.find(query)
        if limit:
            cursor = cursor.limit(limit)
            
        async for job in cursor:
            try:
                original_title = job.get('title', '')
                if not original_title:
                    continue
                    
                # Parse the title
                parsed = parse_job_title(original_title)
                
                # Prepare update document
                update_doc = {
                    "updated_at": datetime.utcnow(),
                    "title_parsed": True,  # Mark as processed
                }
                
                # Update title if it changed
                if parsed['title'] and parsed['title'] != original_title:
                    update_doc['title'] = parsed['title']
                    update_doc['original_title'] = original_title
                    
                # Update company if parsed and not already set
                if parsed['company'] and (not job.get('company') or job.get('company') == parsed['company']):
                    update_doc['company'] = parsed['company']
                    
                # Update remote information
                if parsed['is_remote']:
                    update_doc['is_remote'] = True
                    update_doc['remote_type'] = parsed['remote_type'].value if hasattr(parsed['remote_type'], 'value') else str(parsed['remote_type'])
                    
                    if parsed['location_restriction']:
                        update_doc['location_restriction'] = parsed['location_restriction']
                        # Update location if it's currently just "Remote"
                        if job.get('location') in ['Remote', '', None]:
                            update_doc['location'] = f"Remote ({parsed['location_restriction']})"
                    elif job.get('location') in ['', None]:
                        update_doc['location'] = "Remote"
                
                # Only update if we have changes
                if len(update_doc) > 2:  # More than just updated_at and title_parsed
                    if not dry_run:
                        await self.db.jobs.update_one(
                            {"_id": job["_id"]},
                            {"$set": update_doc}
                        )
                        updated += 1
                    else:
                        logger.info(f"Would update: '{original_title}' -> '{parsed['title']}'")
                        if parsed['company']:
                            logger.info(f"  Company: {parsed['company']}")
                        if parsed['is_remote']:
                            logger.info(f"  Remote: {parsed['remote_type']}")
                        updated += 1
                
                processed += 1
                
                if processed % batch_size == 0:
                    logger.info(f"Processed {processed}/{total_count if not limit else min(limit, total_count)} jobs, updated {updated}")
                    
            except Exception as e:
                logger.error(f"Error processing job {job.get('_id')}: {e}")
                errors += 1
                continue
        
        logger.info(f"Job title fixing completed:")
        logger.info(f"  Total processed: {processed}")
        logger.info(f"  Total updated: {updated}")
        logger.info(f"  Errors: {errors}")
        
        return processed, updated, errors

    async def create_indexes(self):
        """Create indexes for better performance"""
        logger.info("Creating indexes...")
        
        indexes = [
            ("title", 1),
            ("company", 1),
            ("is_remote", 1),
            ("location_restriction", 1),
            ("title_parsed", 1),
            ("original_title", 1)
        ]
        
        for field, direction in indexes:
            try:
                await self.db.jobs.create_index([(field, direction)])
                logger.info(f"Created index on {field}")
            except Exception as e:
                logger.warning(f"Index creation failed for {field}: {e}")

async def main():
    """Main function"""
    fixer = JobTitleFixer()
    
    try:
        await fixer.connect()
        
        # Create indexes first
        await fixer.create_indexes()
        
        # Analyze current state
        problematic_count = await fixer.analyze_job_titles()
        
        if problematic_count == 0:
            logger.info("No problematic job titles found!")
            return
        
        # Ask user for confirmation
        print(f"\nFound {problematic_count} jobs with potentially problematic titles.")
        
        # Run dry run first
        print("\n=== DRY RUN ===")
        await fixer.fix_job_titles(dry_run=True, limit=10)
        
        # Ask for confirmation to proceed
        response = input("\nDo you want to proceed with the actual fix? (y/N): ")
        if response.lower() != 'y':
            logger.info("Operation cancelled by user")
            return
        
        # Proceed with actual fix
        print("\n=== ACTUAL FIX ===")
        processed, updated, errors = await fixer.fix_job_titles(dry_run=False)
        
        logger.info("Job title fixing completed successfully!")
        
    except Exception as e:
        logger.error(f"Error during job title fixing: {e}")
        raise
    finally:
        await fixer.disconnect()

if __name__ == "__main__":
    asyncio.run(main()) 