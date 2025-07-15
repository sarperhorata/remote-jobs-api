#!/usr/bin/env python3
"""
Script to clean up jobs older than 2 months from the database.
"""

import asyncio
import os
import sys
from datetime import datetime, timedelta
from motor.motor_asyncio import AsyncIOMotorClient

# Get database URL directly
DATABASE_URL = os.getenv("DATABASE_URL", "mongodb://localhost:27017/buzz2remote")

async def cleanup_old_jobs():
    """Remove jobs older than 2 months from the database."""
    print("Starting cleanup of old jobs...")
    
    # Connect to MongoDB
    client = AsyncIOMotorClient(DATABASE_URL)
    db = client.get_default_database()
    
    # Calculate cutoff date (2 months ago)
    two_months_ago = datetime.utcnow() - timedelta(days=60)
    print(f"Removing jobs older than: {two_months_ago}")
    
    # Build query to find old jobs
    old_jobs_query = {
        "$and": [
            {
                "$or": [
                    {"created_at": {"$lt": two_months_ago}},
                    {"posted_date": {"$lt": two_months_ago.isoformat()}},
                    {"date_posted": {"$lt": two_months_ago.isoformat()}}
                ]
            },
            {
                # Don't delete jobs that have no date (might be recent imports)
                "$or": [
                    {"created_at": {"$exists": True}},
                    {"posted_date": {"$exists": True}},
                    {"date_posted": {"$exists": True}}
                ]
            }
        ]
    }
    
    try:
        # First, count how many jobs will be deleted
        count = await db.jobs.count_documents(old_jobs_query)
        print(f"Found {count} old jobs to delete")
        
        if count > 0:
            # Delete old jobs
            result = await db.jobs.delete_many(old_jobs_query)
            print(f"Successfully deleted {result.deleted_count} old jobs")
            
            # Get remaining job count
            remaining = await db.jobs.count_documents({})
            print(f"Remaining jobs in database: {remaining}")
        else:
            print("No old jobs found to delete")
            
    except Exception as e:
        print(f"Error during cleanup: {e}")
    finally:
        # Close the connection
        client.close()
        print("Cleanup completed")

if __name__ == "__main__":
    asyncio.run(cleanup_old_jobs()) 