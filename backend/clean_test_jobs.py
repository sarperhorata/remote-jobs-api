#!/usr/bin/env python3

import os
import sys
from pymongo import MongoClient
from datetime import datetime

# MongoDB connection
try:
    MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017/buzz2remote")
    client = MongoClient(MONGODB_URL)
    db = client.get_database("buzz2remote")
    jobs_collection = db.jobs
    
    print("🧹 Cleaning Test Jobs from Database...")
    
    # Find test jobs
    test_query = {
        "$or": [
            {"title": {"$regex": "test", "$options": "i"}},
            {"company": {"$regex": "test", "$options": "i"}},
            {"title": {"$regex": "sample", "$options": "i"}},
            {"company": {"$regex": "sample", "$options": "i"}},
            {"title": {"$regex": "demo", "$options": "i"}},
            {"company": {"$regex": "demo", "$options": "i"}},
            {"company": "TechCorp"},
            {"company": "StartupXYZ"},
            {"company": "Demo Company"},
            {"title": "Software Engineer"},
            {"title": "Senior Python Developer"},
            {"title": "Frontend Developer"}
        ]
    }
    
    # Count test jobs before deletion
    test_jobs_count = jobs_collection.count_documents(test_query)
    print(f"Found {test_jobs_count} test jobs to delete")
    
    if test_jobs_count > 0:
        # Show some examples
        print("\n📋 Examples of jobs to be deleted:")
        sample_test_jobs = list(jobs_collection.find(test_query).limit(5))
        for i, job in enumerate(sample_test_jobs, 1):
            title = job.get("title", "N/A")
            company = job.get("company", "N/A")
            print(f"{i}. {title} at {company}")
        
        # Ask for confirmation
        confirm = input(f"\n❓ Do you want to delete {test_jobs_count} test jobs? (y/N): ")
        
        if confirm.lower() == 'y':
            # Delete test jobs
            result = jobs_collection.delete_many(test_query)
            print(f"✅ Deleted {result.deleted_count} test jobs")
            
            # Show updated stats
            remaining_jobs = jobs_collection.count_documents({})
            print(f"📊 Remaining jobs: {remaining_jobs}")
        else:
            print("❌ Operation cancelled")
    else:
        print("✅ No test jobs found!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    sys.exit(1) 