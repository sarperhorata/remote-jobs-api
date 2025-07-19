#!/usr/bin/env python3
"""
Import external job data into MongoDB
"""

import json
import asyncio
from datetime import datetime
from pathlib import Path
from motor.motor_asyncio import AsyncIOMotorClient
import sys
import os
from utils.html_cleaner import clean_job_data

# Add backend to path
sys.path.append('/Users/sarperhorata/buzz2remote/backend')

async def import_jobs():
    """Import jobs from external_jobs directory"""
    
    # Connect to MongoDB
    client = AsyncIOMotorClient("mongodb://localhost:27017/")
    db = client["buzz2remote"]
    jobs_collection = db["jobs"]
    
    # Get job files
    data_dir = Path("/Users/sarperhorata/buzz2remote/data/external_jobs")
    
    # Import the largest files first
    job_files = [
        "external_jobs_remotive_20250525_221440.json",
        "external_jobs_arbeitnow_free_20250525_221440.json", 
        "external_jobs_job_posting_feed_20250525_221440.json",
        "external_jobs_jobicy_20250525_221440.json"
    ]
    
    total_imported = 0
    
    for filename in job_files:
        file_path = data_dir / filename
        if not file_path.exists():
            print(f"File not found: {filename}")
            continue
            
        print(f"Processing {filename}...")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                if not content or content == "[]":
                    print(f"Empty file: {filename}")
                    continue
                    
                jobs_data = json.loads(content)
                
            if not jobs_data:
                print(f"No jobs in {filename}")
                continue
                
            # Process and insert jobs
            imported_count = 0
            for job_data in jobs_data:
                # Clean and normalize job data
                raw_job_data = {
                    "title": job_data.get("title", ""),
                    "company": job_data.get("company", ""),
                    "location": job_data.get("location", "Remote"),
                    "description": job_data.get("description", ""),
                    "requirements": job_data.get("requirements", ""),
                    "benefits": job_data.get("benefits", "")
                }
                
                # Clean HTML tags from job data
                cleaned_data = clean_job_data(raw_job_data)
                
                clean_job = {
                    "title": cleaned_data["title"],
                    "company": cleaned_data["company"],
                    "location": cleaned_data["location"],
                    "description": cleaned_data["description"][:2000],  # Limit description
                    "url": job_data.get("url", ""),
                    "apply_url": job_data.get("url", ""),  # Use URL as apply URL if not specified
                    "job_type": job_data.get("job_type", "Full-time"),
                    "salary": job_data.get("salary"),
                    "posted_date": job_data.get("posted_date"),
                    "source": job_data.get("source", filename.split("_")[2]),
                    "external_id": job_data.get("external_id", ""),
                    "is_active": True,
                    "created_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow(),
                    "views_count": 0,
                    "applications_count": 0
                }
                
                # Skip if missing required fields
                if not clean_job["title"] or not clean_job["company"]:
                    continue
                    
                # Check if job already exists
                existing = await jobs_collection.find_one({
                    "title": clean_job["title"],
                    "company": clean_job["company"],
                    "url": clean_job["url"]
                })
                
                if not existing:
                    await jobs_collection.insert_one(clean_job)
                    imported_count += 1
                    
            print(f"Imported {imported_count} jobs from {filename}")
            total_imported += imported_count
            
        except Exception as e:
            print(f"Error processing {filename}: {str(e)}")
            continue
    
    print(f"\nTotal jobs imported: {total_imported}")
    
    # Show final count
    total_count = await jobs_collection.count_documents({})
    print(f"Total jobs in database: {total_count}")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(import_jobs()) 