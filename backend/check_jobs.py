#!/usr/bin/env python3

import os
import sys
from datetime import datetime

from pymongo import MongoClient

# MongoDB connection
try:
    MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017/buzz2remote")
    client = MongoClient(MONGODB_URL)
    db = client.get_database("buzz2remote")
    jobs_collection = db.jobs

    # Get stats
    total_jobs = jobs_collection.count_documents({})
    active_jobs = jobs_collection.count_documents({"is_active": True})

    print(f"📊 Job Statistics:")
    print(f"Total jobs: {total_jobs}")
    print(f"Active jobs: {active_jobs}")

    # Get sample jobs
    print(f"\n📝 Sample Jobs:")
    sample_jobs = list(jobs_collection.find().limit(10))

    for i, job in enumerate(sample_jobs, 1):
        title = job.get("title", "N/A")
        company = job.get("company", "N/A")
        location = job.get("location", "N/A")
        source = job.get("source", "N/A")

        print(f"{i}. {title} at {company} ({location}) - Source: {source}")

    # Check for test jobs
    test_jobs = jobs_collection.count_documents(
        {
            "$or": [
                {"title": {"$regex": "test", "$options": "i"}},
                {"company": {"$regex": "test", "$options": "i"}},
            ]
        }
    )

    print(f"\n🧪 Test Jobs Found: {test_jobs}")

    # Get companies
    companies = jobs_collection.distinct("company")
    print(f"\n🏢 Total Companies: {len(companies)}")
    print(f"Sample companies: {companies[:10]}")

except Exception as e:
    print(f"❌ Error connecting to database: {e}")
    sys.exit(1)
