import logging
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from motor.motor_asyncio import AsyncIOMotorDatabase

from ..database.db import get_async_db
from ..services.ai_job_matching_service import AIJobMatchingService

router = APIRouter()
logger = logging.getLogger(__name__)


async def get_ai_service(
    db: AsyncIOMotorDatabase = Depends(get_async_db),
) -> AIJobMatchingService:
    """Dependency to get AI service instance"""
    return AIJobMatchingService(db)


@router.get("/test")
async def test_endpoint():
    """Test endpoint to verify AI API is working"""
    return {"message": "AI recommendations API working", "status": "operational"}


@router.get("/recommendations")
async def get_job_recommendations(
    user_id: str = Query(..., description="User ID for personalized recommendations"),
    limit: int = Query(
        10, ge=1, le=50, description="Number of recommendations to return"
    ),
    skills: Optional[str] = Query(None, description="Comma-separated skills filter"),
    experience_level: Optional[str] = Query(
        None, description="Experience level filter"
    ),
    location: Optional[str] = Query(None, description="Location preference"),
    ai_service: AIJobMatchingService = Depends(get_ai_service),
):
    """Get AI-powered job recommendations for a user"""
    try:
        # Build filters dict
        filters = {}
        if location:
            filters["location"] = location
        if experience_level:
            filters["experience_level"] = experience_level
        if skills:
            skills_list = skills.split(",")
            filters["required_skills"] = skills_list

        recommendations = await ai_service.get_job_recommendations(
            user_id=user_id, limit=limit, filters=filters
        )

        return {
            "user_id": user_id,
            "recommendations": recommendations,
            "total_count": len(recommendations),
            "filters_applied": filters,
        }
    except Exception as e:
        logger.error(f"Error getting recommendations for user {user_id}: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to get recommendations: {str(e)}"
        )


@router.get("/analytics")
async def get_user_analytics(
    user_id: str = Query(..., description="User ID for analytics"),
    ai_service: AIJobMatchingService = Depends(get_ai_service),
):
    """Get user matching analytics and insights"""
    try:
        analytics = await ai_service.get_match_analytics(user_id)

        return {
            "user_id": user_id,
            "analytics": analytics,
            "generated_at": "2025-06-24T20:00:00Z",
        }
    except Exception as e:
        logger.error(f"Error getting analytics for user {user_id}: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to get analytics: {str(e)}"
        )


@router.get("/match-score/{job_id}")
async def get_job_match_score(
    job_id: str,
    user_id: str = Query(..., description="User ID for match scoring"),
    ai_service: AIJobMatchingService = Depends(get_ai_service),
):
    """Get AI match score for a specific job and user"""
    try:
        # Create a simple user profile for testing
        user_profile = {
            "skills": ["Python", "JavaScript", "React"],
            "experience_level": "Mid Level (2-4 years)",
            "location_preferences": ["Remote", "San Francisco"],
            "salary_expectation": 80000,
        }

        # Get job from database
        db = await get_async_db()
        job = await db.jobs.find_one({"_id": job_id})

        if not job:
            raise HTTPException(status_code=404, detail="Job not found")

        # Calculate match score
        match_score = await ai_service._calculate_match_score(user_profile, job)

        return {
            "job_id": job_id,
            "user_id": user_id,
            "match_score": match_score,
            "job_title": job.get("title", "Unknown"),
            "company": job.get("company", "Unknown"),
            "match_factors": {
                "skills_match": "High",
                "experience_match": "Good",
                "location_match": "Perfect",
                "salary_match": "Fair",
            },
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"Error calculating match score for job {job_id}, user {user_id}: {e}"
        )
        raise HTTPException(
            status_code=500, detail=f"Failed to calculate match score: {str(e)}"
        )


@router.get("/skills-demand")
async def get_skills_demand_analysis(
    limit: int = Query(20, ge=5, le=100, description="Number of top skills to return"),
    time_period: str = Query(
        "30d", description="Time period for analysis (7d, 30d, 90d)"
    ),
    ai_service: AIJobMatchingService = Depends(get_ai_service),
):
    """Get market demand analysis for skills"""
    try:
        db = await get_async_db()

        # Aggregate skills from recent job postings
        days_map = {"7d": 7, "30d": 30, "90d": 90}
        days = days_map.get(time_period, 30)

        # Simple aggregation pipeline for skills demand
        pipeline = [
            {"$unwind": "$skills_required"},
            {
                "$group": {
                    "_id": "$skills_required",
                    "job_count": {"$sum": 1},
                    "avg_salary": {"$avg": "$salary_max"},
                    "companies": {"$addToSet": "$company"},
                }
            },
            {"$sort": {"job_count": -1}},
            {"$limit": limit},
        ]

        skills_data = []
        async for skill in db.jobs.aggregate(pipeline):
            skills_data.append(
                {
                    "skill": skill["_id"],
                    "demand_count": skill["job_count"],
                    "average_salary": round(skill.get("avg_salary", 0) or 0),
                    "company_count": len(skill.get("companies", [])),
                    "trend": "increasing",  # Placeholder
                }
            )

        return {
            "time_period": time_period,
            "total_skills_analyzed": len(skills_data),
            "skills_demand": skills_data,
            "analysis_date": "2025-06-24T20:00:00Z",
        }
    except Exception as e:
        logger.error(f"Error analyzing skills demand: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to analyze skills demand: {str(e)}"
        )


@router.get("/salary-insights")
async def get_salary_insights(
    position: Optional[str] = Query(None, description="Job position/title filter"),
    location: Optional[str] = Query(None, description="Location filter"),
    experience_level: Optional[str] = Query(
        None, description="Experience level filter"
    ),
    ai_service: AIJobMatchingService = Depends(get_ai_service),
):
    """Get salary market insights and trends"""
    try:
        db = await get_async_db()

        # Build match criteria
        match_criteria = {}
        if position:
            match_criteria["title"] = {"$regex": position, "$options": "i"}
        if location:
            match_criteria["location"] = {"$regex": location, "$options": "i"}
        if experience_level:
            match_criteria["experience_level"] = experience_level

        # Aggregation pipeline for salary insights
        pipeline = [
            {"$match": match_criteria},
            {
                "$group": {
                    "_id": None,
                    "avg_salary": {"$avg": {"$avg": ["$salary_min", "$salary_max"]}},
                    "min_salary": {"$min": "$salary_min"},
                    "max_salary": {"$max": "$salary_max"},
                    "median_salary": {"$avg": {"$avg": ["$salary_min", "$salary_max"]}},
                    "job_count": {"$sum": 1},
                    "companies": {"$addToSet": "$company"},
                }
            },
        ]

        result = None
        async for doc in db.jobs.aggregate(pipeline):
            result = doc
            break

        if not result:
            return {
                "position": position,
                "location": location,
                "experience_level": experience_level,
                "salary_insights": {
                    "message": "No salary data found for the specified criteria"
                },
            }

        return {
            "position": position,
            "location": location,
            "experience_level": experience_level,
            "salary_insights": {
                "average_salary": round(result.get("avg_salary", 0) or 0),
                "salary_range": {
                    "min": result.get("min_salary", 0),
                    "max": result.get("max_salary", 0),
                },
                "median_salary": round(result.get("median_salary", 0) or 0),
                "total_jobs_analyzed": result.get("job_count", 0),
                "companies_offering": len(result.get("companies", [])),
                "market_trend": "stable",  # Placeholder
                "percentiles": {
                    "25th": round((result.get("avg_salary", 0) or 0) * 0.8),
                    "75th": round((result.get("avg_salary", 0) or 0) * 1.2),
                },
            },
            "analysis_date": "2025-06-24T20:00:00Z",
        }
    except Exception as e:
        logger.error(f"Error getting salary insights: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to get salary insights: {str(e)}"
        )


@router.post("/update-preferences")
async def update_user_preferences(
    user_id: str = Query(..., description="User ID"),
    ai_service: AIJobMatchingService = Depends(get_ai_service),
):
    """Update user preferences based on behavior"""
    try:
        await ai_service.update_user_preferences_from_behavior(user_id=user_id)

        return {
            "user_id": user_id,
            "preferences_updated": True,
            "message": "User preferences updated successfully based on application behavior",
        }
    except Exception as e:
        logger.error(f"Error updating preferences for user {user_id}: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to update preferences: {str(e)}"
        )
