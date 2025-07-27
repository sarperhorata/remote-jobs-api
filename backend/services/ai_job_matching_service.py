"""
AI Job Matching Service

This service provides intelligent job recommendations using machine learning
algorithms and user behavior analysis to match job seekers with suitable positions.
"""

import asyncio
import json
import logging
import os
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase

# Setup logging
logger = logging.getLogger(__name__)


class AIJobMatchingService:
    """
    Advanced AI-powered job matching service that provides intelligent
    job recommendations based on user profile, skills, experience, and preferences.
    """

    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.matching_cache = {}
        self.cache_ttl = 3600  # 1 hour cache

    async def get_job_recommendations(
        self, user_id: str, limit: int = 10, filters: Optional[Dict] = None
    ) -> List[Dict[str, Any]]:
        """
        Get AI-powered job recommendations for a user.

        Args:
            user_id: User ID to get recommendations for
            limit: Maximum number of recommendations
            filters: Optional filters to apply

        Returns:
            List of recommended jobs with match scores
        """
        try:
            # Get user profile
            user_profile = await self._get_user_profile(user_id)
            if not user_profile:
                logger.warning(f"No profile found for user {user_id}")
                return []

            # Get available jobs
            jobs = await self._get_available_jobs(filters)

            # Calculate match scores
            scored_jobs = []
            for job in jobs:
                match_score = await self._calculate_match_score(user_profile, job)
                if match_score > 0.3:  # Minimum match threshold
                    job["match_score"] = match_score
                    job["match_reasons"] = await self._get_match_reasons(
                        user_profile, job
                    )
                    scored_jobs.append(job)

            # Sort by match score and return top results
            scored_jobs.sort(key=lambda x: x["match_score"], reverse=True)

            # Log recommendation activity
            await self._log_recommendations(user_id, len(scored_jobs), limit)

            return scored_jobs[:limit]

        except Exception as e:
            logger.error(
                f"Error getting job recommendations for user {user_id}: {str(e)}"
            )
            return []

    async def _get_user_profile(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get comprehensive user profile for matching."""
        try:
            # Get user basic info
            user = await self.db.users.find_one({"_id": ObjectId(user_id)})
            if not user:
                return None

            # Get user skills
            skills = await self.db.user_skills.find({"user_id": user_id}).to_list(None)

            # Get user experience
            experience = await self.db.user_experience.find(
                {"user_id": user_id}
            ).to_list(None)

            # Get user preferences
            preferences = (
                await self.db.user_preferences.find_one({"user_id": user_id}) or {}
            )

            # Get application history for learning
            applications = (
                await self.db.applications.find({"user_id": user_id})
                .limit(50)
                .to_list(None)
            )

            return {
                "user": user,
                "skills": skills,
                "experience": experience,
                "preferences": preferences,
                "application_history": applications,
            }

        except Exception as e:
            logger.error(f"Error getting user profile {user_id}: {str(e)}")
            return None

    async def _get_available_jobs(
        self, filters: Optional[Dict] = None
    ) -> List[Dict[str, Any]]:
        """Get available jobs for matching."""
        try:
            query = {"status": "active"}

            # Apply filters
            if filters:
                if filters.get("location"):
                    query["location"] = {"$regex": filters["location"], "$options": "i"}
                if filters.get("remote"):
                    query["remote_type"] = {"$in": ["remote", "hybrid"]}
                if filters.get("salary_min"):
                    query["salary_min"] = {"$gte": filters["salary_min"]}
                if filters.get("job_type"):
                    query["job_type"] = filters["job_type"]

            # Get recent active jobs
            jobs = await self.db.jobs.find(query).limit(1000).to_list(None)

            # Convert ObjectId to string for JSON serialization
            for job in jobs:
                job["_id"] = str(job["_id"])

            return jobs

        except Exception as e:
            logger.error(f"Error getting available jobs: {str(e)}")
            return []

    async def _calculate_match_score(
        self, user_profile: Dict[str, Any], job: Dict[str, Any]
    ) -> float:
        """
        Calculate AI match score between user and job.

        Returns a score between 0.0 and 1.0 where:
        - 0.0-0.3: Poor match
        - 0.3-0.6: Fair match
        - 0.6-0.8: Good match
        - 0.8-1.0: Excellent match
        """
        try:
            total_score = 0.0
            weights = {
                "skills": 0.35,
                "experience": 0.25,
                "location": 0.15,
                "salary": 0.10,
                "job_type": 0.10,
                "company_size": 0.05,
            }

            # Skills matching
            skills_score = await self._match_skills(user_profile, job)
            total_score += skills_score * weights["skills"]

            # Experience matching
            experience_score = await self._match_experience(user_profile, job)
            total_score += experience_score * weights["experience"]

            # Location matching
            location_score = await self._match_location(user_profile, job)
            total_score += location_score * weights["location"]

            # Salary matching
            salary_score = await self._match_salary(user_profile, job)
            total_score += salary_score * weights["salary"]

            # Job type matching
            job_type_score = await self._match_job_type(user_profile, job)
            total_score += job_type_score * weights["job_type"]

            # Company size matching
            company_score = await self._match_company_size(user_profile, job)
            total_score += company_score * weights["company_size"]

            return min(total_score, 1.0)

        except Exception as e:
            logger.error(f"Error calculating match score: {str(e)}")
            return 0.0

    async def _match_skills(self, user_profile: Dict, job: Dict) -> float:
        """Calculate skills match score."""
        try:
            user_skills = set()
            for skill in user_profile.get("skills", []):
                user_skills.add(skill.get("name", "").lower())

            job_skills = set()
            if job.get("required_skills"):
                job_skills.update([skill.lower() for skill in job["required_skills"]])
            if job.get("description"):
                # Simple skill extraction from job description
                description_lower = job["description"].lower()
                common_skills = [
                    "python",
                    "javascript",
                    "react",
                    "node",
                    "aws",
                    "docker",
                    "kubernetes",
                    "sql",
                    "mongodb",
                    "postgresql",
                    "git",
                    "html",
                    "css",
                    "typescript",
                    "vue",
                    "angular",
                    "django",
                    "flask",
                    "fastapi",
                    "redis",
                    "elasticsearch",
                    "java",
                    "golang",
                    "rust",
                    "c++",
                    "machine learning",
                    "ai",
                    "data science",
                    "devops",
                    "ci/cd",
                    "terraform",
                ]
                for skill in common_skills:
                    if skill in description_lower:
                        job_skills.add(skill)

            if not job_skills:
                return 0.5  # Neutral score if no skills specified

            matching_skills = user_skills.intersection(job_skills)
            if not user_skills:
                return 0.0

            return len(matching_skills) / len(job_skills)

        except Exception:
            return 0.0

    async def _match_experience(self, user_profile: Dict, job: Dict) -> float:
        """Calculate experience match score."""
        try:
            user_experience_years = 0
            for exp in user_profile.get("experience", []):
                if exp.get("years"):
                    user_experience_years += exp["years"]

            required_years = job.get("experience_years", 0)
            if required_years == 0:
                return 0.8  # Good score if no experience requirement

            if user_experience_years >= required_years:
                # Bonus for more experience but not too much
                bonus = min((user_experience_years - required_years) * 0.1, 0.2)
                return min(1.0, 0.8 + bonus)
            else:
                # Penalty for less experience
                ratio = user_experience_years / required_years
                return max(0.0, ratio * 0.8)

        except Exception:
            return 0.5

    async def _match_location(self, user_profile: Dict, job: Dict) -> float:
        """Calculate location match score."""
        try:
            user_location = user_profile.get("user", {}).get("location", "").lower()
            preferred_remote = user_profile.get("preferences", {}).get(
                "remote_work", False
            )

            job_location = job.get("location", "").lower()
            job_remote = job.get("remote_type", "").lower() in ["remote", "hybrid"]

            if job_remote and preferred_remote:
                return 1.0  # Perfect match for remote work

            if job_remote and not preferred_remote:
                return 0.8  # Good match, remote is flexible

            if not job_remote and preferred_remote:
                return 0.3  # Poor match if user wants remote but job isn't

            # Location matching for non-remote jobs
            if user_location and job_location:
                if user_location in job_location or job_location in user_location:
                    return 1.0
                else:
                    return 0.4  # Different locations

            return 0.6  # Neutral if location info is missing

        except Exception:
            return 0.5

    async def _match_salary(self, user_profile: Dict, job: Dict) -> float:
        """Calculate salary match score."""
        try:
            desired_salary = user_profile.get("preferences", {}).get("desired_salary")
            job_salary_min = job.get("salary_min")
            job_salary_max = job.get("salary_max")

            if not desired_salary:
                return 0.7  # Neutral if no preference

            if not job_salary_min and not job_salary_max:
                return 0.6  # Neutral if no salary info

            if job_salary_max and desired_salary <= job_salary_max:
                return 1.0  # Perfect match

            if job_salary_min and desired_salary >= job_salary_min:
                return 0.8  # Good match

            return 0.3  # Poor match

        except Exception:
            return 0.5

    async def _match_job_type(self, user_profile: Dict, job: Dict) -> float:
        """Calculate job type match score."""
        try:
            preferred_type = (
                user_profile.get("preferences", {}).get("job_type", "").lower()
            )
            job_type = job.get("job_type", "").lower()

            if not preferred_type:
                return 0.7  # Neutral if no preference

            if preferred_type == job_type:
                return 1.0  # Perfect match

            # Partial matches
            if "full" in preferred_type and "full" in job_type:
                return 0.9
            if "part" in preferred_type and "part" in job_type:
                return 0.9
            if "contract" in preferred_type and "contract" in job_type:
                return 0.9

            return 0.4  # Different types

        except Exception:
            return 0.5

    async def _match_company_size(self, user_profile: Dict, job: Dict) -> float:
        """Calculate company size match score."""
        try:
            preferred_size = (
                user_profile.get("preferences", {}).get("company_size", "").lower()
            )
            company_size = job.get("company_size", "").lower()

            if not preferred_size or not company_size:
                return 0.7  # Neutral if no data

            if preferred_size == company_size:
                return 1.0

            # Partial matches
            size_categories = {
                "startup": ["startup", "small"],
                "small": ["startup", "small", "medium"],
                "medium": ["small", "medium", "large"],
                "large": ["medium", "large", "enterprise"],
                "enterprise": ["large", "enterprise"],
            }

            if preferred_size in size_categories:
                if company_size in size_categories[preferred_size]:
                    return 0.8

            return 0.4

        except Exception:
            return 0.5

    async def _get_match_reasons(self, user_profile: Dict, job: Dict) -> List[str]:
        """Get human-readable reasons for the match."""
        reasons = []

        try:
            # Skills match
            user_skills = {
                skill.get("name", "").lower()
                for skill in user_profile.get("skills", [])
            }
            job_skills = set()
            if job.get("required_skills"):
                job_skills.update([skill.lower() for skill in job["required_skills"]])

            matching_skills = user_skills.intersection(job_skills)
            if matching_skills:
                reasons.append(f"Skills match: {', '.join(list(matching_skills)[:3])}")

            # Experience match
            user_exp = sum(
                exp.get("years", 0) for exp in user_profile.get("experience", [])
            )
            required_exp = job.get("experience_years", 0)
            if user_exp >= required_exp:
                reasons.append(f"Experience requirement met ({user_exp}+ years)")

            # Location match
            if job.get("remote_type", "").lower() in ["remote", "hybrid"]:
                reasons.append("Remote work available")

            # Salary match
            desired_salary = user_profile.get("preferences", {}).get("desired_salary")
            job_salary_max = job.get("salary_max")
            if desired_salary and job_salary_max and desired_salary <= job_salary_max:
                reasons.append("Salary range matches expectations")

            return reasons[:5]  # Limit to top 5 reasons

        except Exception:
            return ["AI analysis suggests this is a good match"]

    async def _log_recommendations(self, user_id: str, total_matches: int, limit: int):
        """Log recommendation activity for analytics."""
        try:
            log_entry = {
                "user_id": user_id,
                "timestamp": datetime.utcnow(),
                "total_matches": total_matches,
                "requested_limit": limit,
                "service": "ai_job_matching",
            }
            await self.db.recommendation_logs.insert_one(log_entry)
        except Exception as e:
            logger.error(f"Error logging recommendations: {str(e)}")

    async def get_match_analytics(self, user_id: str) -> Dict[str, Any]:
        """Get analytics about user's job matching patterns."""
        try:
            # Get recent recommendations
            logs = (
                await self.db.recommendation_logs.find({"user_id": user_id})
                .sort("timestamp", -1)
                .limit(30)
                .to_list(None)
            )

            # Get user applications
            applications = (
                await self.db.applications.find({"user_id": user_id})
                .sort("created_at", -1)
                .limit(50)
                .to_list(None)
            )

            analytics = {
                "total_recommendations_last_30": len(logs),
                "total_applications": len(applications),
                "avg_recommendations_per_session": 0,
                "most_common_skills": [],
                "preferred_locations": [],
                "success_rate": 0.0,
            }

            if logs:
                analytics["avg_recommendations_per_session"] = sum(
                    log.get("total_matches", 0) for log in logs
                ) / len(logs)

            # Calculate success rate (applications / recommendations)
            if logs and applications:
                total_recommendations = sum(log.get("total_matches", 0) for log in logs)
                if total_recommendations > 0:
                    analytics["success_rate"] = (
                        len(applications) / total_recommendations
                    )

            return analytics

        except Exception as e:
            logger.error(f"Error getting match analytics: {str(e)}")
            return {}

    async def update_user_preferences_from_behavior(self, user_id: str):
        """
        Update user preferences based on their application behavior.
        Machine learning-like approach to improve recommendations.
        """
        try:
            # Get user's recent applications
            applications = (
                await self.db.applications.find({"user_id": user_id})
                .sort("created_at", -1)
                .limit(20)
                .to_list(None)
            )

            if not applications:
                return

            # Analyze patterns
            location_patterns = {}
            salary_patterns = []
            company_size_patterns = {}
            job_type_patterns = {}

            for app in applications:
                job = await self.db.jobs.find_one({"_id": ObjectId(app["job_id"])})
                if not job:
                    continue

                # Location patterns
                location = job.get("location", "")
                if location:
                    location_patterns[location] = location_patterns.get(location, 0) + 1

                # Salary patterns
                if job.get("salary_max"):
                    salary_patterns.append(job["salary_max"])

                # Company size patterns
                company_size = job.get("company_size", "")
                if company_size:
                    company_size_patterns[company_size] = (
                        company_size_patterns.get(company_size, 0) + 1
                    )

                # Job type patterns
                job_type = job.get("job_type", "")
                if job_type:
                    job_type_patterns[job_type] = job_type_patterns.get(job_type, 0) + 1

            # Update preferences based on patterns
            preferences_update = {}

            # Most common location
            if location_patterns:
                preferred_location = max(location_patterns, key=location_patterns.get)
                preferences_update["preferred_location"] = preferred_location

            # Average desired salary
            if salary_patterns:
                avg_salary = sum(salary_patterns) / len(salary_patterns)
                preferences_update["desired_salary"] = int(avg_salary)

            # Most common company size
            if company_size_patterns:
                preferred_size = max(
                    company_size_patterns, key=company_size_patterns.get
                )
                preferences_update["company_size"] = preferred_size

            # Most common job type
            if job_type_patterns:
                preferred_type = max(job_type_patterns, key=job_type_patterns.get)
                preferences_update["job_type"] = preferred_type

            # Update user preferences
            if preferences_update:
                preferences_update["updated_at"] = datetime.utcnow()
                preferences_update["auto_updated"] = True

                await self.db.user_preferences.update_one(
                    {"user_id": user_id}, {"$set": preferences_update}, upsert=True
                )

                logger.info(f"Updated preferences for user {user_id} based on behavior")

        except Exception as e:
            logger.error(f"Error updating user preferences: {str(e)}")
