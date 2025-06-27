from fastapi import APIRouter, HTTPException, Depends
from backend.database import get_db, DATABASE_AVAILABLE
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/admin/cleanup/unknown-company")
async def cleanup_unknown_company():
    """Clean up jobs with 'Unknown Company' or empty company names"""
    try:
        db = await get_db()
        if not DATABASE_AVAILABLE or db is None:
            raise HTTPException(status_code=503, detail="Database not available")
        
        # Count jobs with unknown/empty company
        unknown_query = {
            "$or": [
                {"company": "Unknown Company"},
                {"company": ""},
                {"company": None},
                {"company": {"$exists": False}}
            ]
        }
        
        unknown_count = await db.jobs.count_documents(unknown_query)
        
        if unknown_count == 0:
            return {
                "status": "success",
                "message": "No unknown company jobs found",
                "cleaned": 0
            }
        
        # Option 1: Delete them
        # result = await db.jobs.delete_many(unknown_query)
        
        # Option 2: Update them to extract company from URL or description
        jobs_cursor = db.jobs.find(unknown_query).limit(100)  # Process in batches
        jobs = await jobs_cursor.to_list(100)
        
        updated_count = 0
        for job in jobs:
            new_company = None
            
            # Try to extract company from URL
            if job.get("url"):
                url = job["url"]
                if "greenhouse.io" in url:
                    parts = url.split("/")
                    for i, part in enumerate(parts):
                        if part == "boards" and i > 0:
                            new_company = parts[i-1].replace("-", " ").title()
                            break
                elif "lever.co" in url:
                    parts = url.split("/")
                    if len(parts) > 2:
                        new_company = parts[2].replace("-", " ").title()
            
            # If still no company, try from title
            if not new_company and job.get("title"):
                title = job["title"]
                if " at " in title:
                    new_company = title.split(" at ")[-1].strip()
            
            # Update if we found a company
            if new_company:
                await db.jobs.update_one(
                    {"_id": job["_id"]},
                    {"$set": {"company": new_company}}
                )
                updated_count += 1
        
        return {
            "status": "success",
            "message": f"Processed {len(jobs)} unknown company jobs",
            "updated": updated_count,
            "remaining": unknown_count - updated_count
        }
        
    except Exception as e:
        logger.error(f"Error cleaning unknown companies: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/admin/stats/unknown-company")
async def get_unknown_company_stats():
    """Get statistics about unknown company jobs"""
    try:
        db = await get_db()
        if not DATABASE_AVAILABLE or db is None:
            raise HTTPException(status_code=503, detail="Database not available")
        
        # Count different variations
        stats = {
            "unknown_company": await db.jobs.count_documents({"company": "Unknown Company"}),
            "empty_string": await db.jobs.count_documents({"company": ""}),
            "null_value": await db.jobs.count_documents({"company": None}),
            "missing_field": await db.jobs.count_documents({"company": {"$exists": False}})
        }
        
        stats["total"] = sum(stats.values())
        
        # Get sample jobs
        sample_cursor = db.jobs.find({
            "$or": [
                {"company": "Unknown Company"},
                {"company": ""},
                {"company": None},
                {"company": {"$exists": False}}
            ]
        }).limit(5)
        
        samples = []
        async for job in sample_cursor:
            samples.append({
                "id": str(job["_id"]),
                "title": job.get("title", "N/A"),
                "url": job.get("url", "N/A"),
                "company": job.get("company", "MISSING")
            })
        
        return {
            "stats": stats,
            "samples": samples
        }
        
    except Exception as e:
        logger.error(f"Error getting unknown company stats: {e}")
        raise HTTPException(status_code=500, detail=str(e)) 