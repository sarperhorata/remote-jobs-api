import logging
import re
from collections import Counter, defaultdict
from typing import Dict, List

from bson import ObjectId
from fastapi import APIRouter, Depends, Query
from motor.motor_asyncio import AsyncIOMotorDatabase

from backend.database import get_async_db

router = APIRouter(prefix="/jobs", tags=["job-analysis"])
logger = logging.getLogger(__name__)


def clean_job_title(title: str) -> str:
    """Clean and normalize job titles"""
    if not title:
        return ""

    # Remove company names and extra info that appears in some titles
    title = re.sub(
        r"^[A-Z][a-zA-Z\s]+[A-Z][a-zA-Z\s]*[A-Z][a-zA-Z\s]*", "", title
    )  # Remove names
    title = re.sub(r"Current Open Jobs", "", title, flags=re.IGNORECASE)
    title = re.sub(r"Open Applications", "", title, flags=re.IGNORECASE)
    title = re.sub(r"Customer Support", "", title, flags=re.IGNORECASE)

    # Remove extra whitespace and normalize
    title = re.sub(r"\s+", " ", title).strip()

    # Remove leading/trailing punctuation
    title = title.strip(".,;:-_|")

    return title


def normalize_job_title(title: str) -> str:
    """Normalize job titles for grouping"""
    cleaned = clean_job_title(title)
    if not cleaned:
        return ""

    # Convert to lowercase for comparison
    normalized = cleaned.lower()

    # Remove common prefixes/suffixes for grouping
    prefixes = [
        "senior",
        "sr",
        "junior",
        "jr",
        "lead",
        "principal",
        "staff",
        "associate",
        "assistant",
    ]
    suffixes = ["i", "ii", "iii", "iv", "1", "2", "3", "4", "5"]

    # Remove level indicators
    words = normalized.split()
    filtered_words = []

    for word in words:
        # Skip common level indicators
        if word not in prefixes and word not in suffixes:
            filtered_words.append(word)

    return " ".join(filtered_words)


def group_job_titles(jobs: list) -> dict:
    """Group jobs by normalized titles and return statistics"""
    title_groups = defaultdict(list)

    for job in jobs:
        original_title = job.get("title", "")
        normalized_title = normalize_job_title(original_title)

        if normalized_title:
            title_groups[normalized_title].append(
                {
                    "original_title": original_title,
                    "job_id": job.get("_id", job.get("id")),
                    "company": job.get("company", ""),
                }
            )

    # Convert to summary format
    grouped_results = {}
    for normalized_title, job_list in title_groups.items():
        original_titles = [job["original_title"] for job in job_list]
        title_counts = Counter(original_titles)

        grouped_results[normalized_title] = {
            "count": len(job_list),
            "variations": dict(title_counts),
            "most_common": (
                title_counts.most_common(1)[0][0] if title_counts else normalized_title
            ),
            "job_ids": [job["job_id"] for job in job_list],
        }

    return grouped_results


@router.get("/analyze-titles", response_model=dict)
async def analyze_job_titles(
    q: str = Query("", description="Search query"),
    limit: int = Query(5000, ge=1, le=5000, description="Number of results to analyze"),
    db: AsyncIOMotorDatabase = Depends(get_async_db),
):
    """Analyze and group job titles with statistics"""
    try:
        # Build query same as regular search
        query = {}

        # Search text query
        if q and q.strip():
            query["$or"] = [
                {"title": {"$regex": q, "$options": "i"}},
                {"description": {"$regex": q, "$options": "i"}},
                {"company": {"$regex": q, "$options": "i"}},
            ]

        # Get all matching jobs
        cursor = db.jobs.find(query).sort("created_at", -1).limit(limit)
        jobs = await cursor.to_list(length=limit)

        # Get total count
        total = await db.jobs.count_documents(query)

        # Convert ObjectIds to strings
        for job in jobs:
            if "_id" in job and isinstance(job["_id"], ObjectId):
                job["id"] = str(job["_id"])
                job["_id"] = str(job["_id"])

        # Group jobs by normalized titles
        grouped_titles = group_job_titles(jobs)

        # Sort by job count (most common titles first)
        sorted_groups = sorted(
            grouped_titles.items(), key=lambda x: x[1]["count"], reverse=True
        )

        # Create summary statistics
        title_stats = {
            "total_jobs_analyzed": len(jobs),
            "unique_normalized_titles": len(grouped_titles),
            "avg_jobs_per_title": (
                len(jobs) / len(grouped_titles) if grouped_titles else 0
            ),
            "top_5_titles": dict(sorted_groups[:5]),
        }

        return {
            "query": q,
            "total_jobs_in_db": total,
            "statistics": title_stats,
            "grouped_titles": dict(sorted_groups),
            "sample_raw_titles": [job.get("title", "") for job in jobs[:20]],
        }

    except Exception as e:
        logger.error(f"Error in job title analysis: {str(e)}")
        return {
            "query": q,
            "total_jobs_in_db": 0,
            "statistics": {},
            "grouped_titles": {},
            "sample_raw_titles": [],
            "error": str(e),
        }
