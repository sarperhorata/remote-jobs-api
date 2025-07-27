import logging
import math
import re
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


class JobMatchingService:
    """
    Job matching service that calculates compatibility scores between resumes and job postings
    """

    def __init__(self):
        # Skill matching weights
        self.skill_weights = {
            "programming": 0.25,
            "frameworks": 0.20,
            "databases": 0.15,
            "cloud": 0.15,
            "tools": 0.10,
            "languages": 0.05,
            "additional": 0.10,
        }

        # Experience level weights
        self.experience_weights = {
            "entry": 0.1,
            "junior": 0.2,
            "mid": 0.3,
            "senior": 0.4,
            "lead": 0.5,
            "manager": 0.6,
            "director": 0.7,
            "executive": 0.8,
        }

        # Job level keywords
        self.level_keywords = {
            "entry": ["entry", "junior", "graduate", "intern", "trainee", "0-1", "0-2"],
            "junior": ["junior", "entry", "1-2", "1-3", "2-3"],
            "mid": ["mid", "middle", "intermediate", "3-5", "4-6", "5-7"],
            "senior": ["senior", "5+", "6+", "7+", "8+"],
            "lead": ["lead", "team lead", "technical lead", "senior"],
            "manager": ["manager", "management", "team manager"],
            "director": ["director", "head of", "vp"],
            "executive": ["executive", "ceo", "cto", "cfo", "president"],
        }

    def calculate_matching_score(
        self, resume_data: Dict[str, Any], job_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Calculate comprehensive matching score between resume and job

        Args:
            resume_data: Parsed resume data
            job_data: Job posting data

        Returns:
            Dictionary containing matching scores and details
        """
        try:
            # Calculate individual scores
            skill_score = self._calculate_skill_matching(resume_data, job_data)
            experience_score = self._calculate_experience_matching(
                resume_data, job_data
            )
            location_score = self._calculate_location_matching(resume_data, job_data)
            salary_score = self._calculate_salary_matching(resume_data, job_data)
            education_score = self._calculate_education_matching(resume_data, job_data)

            # Calculate weighted overall score
            overall_score = self._calculate_overall_score(
                {
                    "skill": skill_score,
                    "experience": experience_score,
                    "location": location_score,
                    "salary": salary_score,
                    "education": education_score,
                }
            )

            return {
                "overall_score": overall_score,
                "skill_score": skill_score,
                "experience_score": experience_score,
                "location_score": location_score,
                "salary_score": salary_score,
                "education_score": education_score,
                "matching_details": self._get_matching_details(resume_data, job_data),
                "calculated_at": datetime.now().isoformat(),
            }

        except Exception as e:
            logger.error(f"Error calculating matching score: {str(e)}")
            return {
                "overall_score": 0,
                "error": str(e),
                "calculated_at": datetime.now().isoformat(),
            }

    def _calculate_skill_matching(
        self, resume_data: Dict[str, Any], job_data: Dict[str, Any]
    ) -> float:
        """Calculate skill matching score"""
        resume_skills = resume_data.get("skills", {})
        job_requirements = self._extract_job_requirements(job_data)

        if not job_requirements:
            return 0.5  # Neutral score if no requirements found

        total_score = 0
        total_weight = 0

        for category, weight in self.skill_weights.items():
            resume_category_skills = set(resume_skills.get(category, []))
            job_category_requirements = set(job_requirements.get(category, []))

            if job_category_requirements:
                # Calculate intersection
                matching_skills = resume_category_skills.intersection(
                    job_category_requirements
                )

                # Calculate score based on matching percentage
                if job_category_requirements:
                    category_score = len(matching_skills) / len(
                        job_category_requirements
                    )
                    total_score += category_score * weight
                    total_weight += weight

        return total_score / total_weight if total_weight > 0 else 0

    def _extract_job_requirements(
        self, job_data: Dict[str, Any]
    ) -> Dict[str, List[str]]:
        """Extract skill requirements from job data"""
        requirements = {}

        # Extract from job description
        description = job_data.get("description", "").lower()
        title = job_data.get("title", "").lower()

        # Define skill categories and their keywords
        skill_categories = {
            "programming": [
                "python",
                "javascript",
                "java",
                "c++",
                "c#",
                "php",
                "ruby",
                "go",
                "rust",
                "swift",
                "kotlin",
            ],
            "frameworks": [
                "react",
                "angular",
                "vue",
                "django",
                "flask",
                "spring",
                "express",
                "laravel",
                "rails",
            ],
            "databases": [
                "mysql",
                "postgresql",
                "mongodb",
                "redis",
                "elasticsearch",
                "sqlite",
                "oracle",
            ],
            "cloud": [
                "aws",
                "azure",
                "gcp",
                "docker",
                "kubernetes",
                "terraform",
                "jenkins",
            ],
            "tools": [
                "git",
                "jira",
                "confluence",
                "slack",
                "figma",
                "adobe",
                "photoshop",
            ],
            "languages": [
                "english",
                "turkish",
                "german",
                "french",
                "spanish",
                "italian",
                "russian",
                "chinese",
            ],
        }

        # Extract skills from description and title
        for category, keywords in skill_categories.items():
            found_skills = []
            for skill in keywords:
                if skill in description or skill in title:
                    found_skills.append(skill)
            if found_skills:
                requirements[category] = found_skills

        # Extract additional skills using regex patterns
        additional_skills = []
        skill_patterns = [
            r"experience with ([^.\n,]+)",
            r"knowledge of ([^.\n,]+)",
            r"proficient in ([^.\n,]+)",
            r"familiar with ([^.\n,]+)",
            r"required skills?[:\s]+([^.\n]+)",
            r"qualifications?[:\s]+([^.\n]+)",
        ]

        for pattern in skill_patterns:
            matches = re.findall(pattern, description, re.IGNORECASE)
            for match in matches:
                skills_list = [s.strip() for s in match.split(",")]
                additional_skills.extend(skills_list)

        if additional_skills:
            requirements["additional"] = list(set(additional_skills))

        return requirements

    def _calculate_experience_matching(
        self, resume_data: Dict[str, Any], job_data: Dict[str, Any]
    ) -> float:
        """Calculate experience level matching score"""
        resume_experience = resume_data.get("experience", [])
        job_level = self._extract_job_level(job_data)

        if not resume_experience:
            return 0.1  # Very low score for no experience

        # Calculate total years of experience
        total_years = self._calculate_total_experience_years(resume_experience)

        # Map experience years to levels
        experience_level = self._map_years_to_level(total_years)

        # Calculate matching score
        if job_level in self.experience_weights:
            expected_weight = self.experience_weights[job_level]
            actual_weight = self.experience_weights.get(experience_level, 0.3)

            # Calculate score based on how close the levels are
            score = 1 - abs(expected_weight - actual_weight)
            return max(0, min(1, score))

        return 0.5  # Neutral score if level not found

    def _extract_job_level(self, job_data: Dict[str, Any]) -> str:
        """Extract job level from job data"""
        title = job_data.get("title", "").lower()
        description = job_data.get("description", "").lower()

        # Check for level keywords in title and description
        for level, keywords in self.level_keywords.items():
            for keyword in keywords:
                if keyword in title or keyword in description:
                    return level

        # Default to mid-level if no clear indication
        return "mid"

    def _calculate_total_experience_years(
        self, experience: List[Dict[str, str]]
    ) -> float:
        """Calculate total years of experience"""
        total_years = 0

        for exp in experience:
            start_date = exp.get("start_date")
            end_date = exp.get("end_date")
            duration = exp.get("duration")

            if duration:
                # Extract years from duration string
                duration_match = re.search(r"(\d+)", duration)
                if duration_match:
                    total_years += float(duration_match.group(1))
            elif start_date and end_date:
                try:
                    start_year = int(start_date)
                    if end_date.lower() in ["present", "current", "now"]:
                        end_year = datetime.now().year
                    else:
                        end_year = int(end_date)
                    total_years += end_year - start_year
                except (ValueError, TypeError):
                    continue

        return total_years

    def _map_years_to_level(self, years: float) -> str:
        """Map years of experience to level"""
        if years < 1:
            return "entry"
        elif years < 3:
            return "junior"
        elif years < 5:
            return "mid"
        elif years < 8:
            return "senior"
        elif years < 12:
            return "lead"
        else:
            return "manager"

    def _calculate_location_matching(
        self, resume_data: Dict[str, Any], job_data: Dict[str, Any]
    ) -> float:
        """Calculate location matching score"""
        resume_location = (
            resume_data.get("personal_info", {}).get("location", "").lower()
        )
        job_location = job_data.get("location", "").lower()

        if not resume_location or not job_location:
            return 0.5  # Neutral score if location info missing

        # Check for exact match
        if resume_location == job_location:
            return 1.0

        # Check for partial match (city, country)
        resume_parts = resume_location.split(",")
        job_parts = job_location.split(",")

        for resume_part in resume_parts:
            for job_part in job_parts:
                if resume_part.strip() == job_part.strip():
                    return 0.8

        # Check for remote work compatibility
        if "remote" in job_location or "work from home" in job_location:
            return 0.7  # Good score for remote jobs

        return 0.2  # Low score for different locations

    def _calculate_salary_matching(
        self, resume_data: Dict[str, Any], job_data: Dict[str, Any]
    ) -> float:
        """Calculate salary expectation matching score"""
        # This is a simplified version - in real implementation, you'd need salary data
        # For now, return a neutral score
        return 0.5

    def _calculate_education_matching(
        self, resume_data: Dict[str, Any], job_data: Dict[str, Any]
    ) -> float:
        """Calculate education matching score"""
        resume_education = resume_data.get("education", [])
        job_description = job_data.get("description", "").lower()

        if not resume_education:
            return 0.3  # Low score for no education info

        # Check for degree requirements in job description
        degree_requirements = []
        degree_keywords = ["bachelor", "master", "phd", "degree", "diploma"]

        for keyword in degree_keywords:
            if keyword in job_description:
                degree_requirements.append(keyword)

        if not degree_requirements:
            return 0.7  # Good score if no specific requirements

        # Check if resume has any of the required degrees
        resume_degrees = []
        for edu in resume_education:
            degree = edu.get("degree", "").lower()
            if degree:
                resume_degrees.append(degree)

        for requirement in degree_requirements:
            for degree in resume_degrees:
                if requirement in degree or degree in requirement:
                    return 1.0

        return 0.4  # Moderate score if no matching degrees

    def _calculate_overall_score(self, scores: Dict[str, float]) -> float:
        """Calculate weighted overall score"""
        weights = {
            "skill": 0.35,
            "experience": 0.25,
            "location": 0.15,
            "salary": 0.10,
            "education": 0.15,
        }

        total_score = 0
        total_weight = 0

        for component, score in scores.items():
            weight = weights.get(component, 0)
            total_score += score * weight
            total_weight += weight

        return total_score / total_weight if total_weight > 0 else 0

    def _get_matching_details(
        self, resume_data: Dict[str, Any], job_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Get detailed matching information"""
        resume_skills = resume_data.get("skills", {})
        job_requirements = self._extract_job_requirements(job_data)

        matching_skills = {}
        missing_skills = {}

        for category in job_requirements:
            resume_category_skills = set(resume_skills.get(category, []))
            job_category_requirements = set(job_requirements.get(category, []))

            matching = resume_category_skills.intersection(job_category_requirements)
            missing = job_category_requirements - resume_category_skills

            if matching:
                matching_skills[category] = list(matching)
            if missing:
                missing_skills[category] = list(missing)

        return {
            "matching_skills": matching_skills,
            "missing_skills": missing_skills,
            "skill_coverage": (
                len(matching_skills) / len(job_requirements) if job_requirements else 0
            ),
        }

    def get_top_matches(
        self,
        resume_data: Dict[str, Any],
        jobs_data: List[Dict[str, Any]],
        limit: int = 10,
        min_score: float = 0.3,
    ) -> List[Dict[str, Any]]:
        """
        Get top matching jobs for a resume

        Args:
            resume_data: Parsed resume data
            jobs_data: List of job postings
            limit: Maximum number of matches to return
            min_score: Minimum score threshold

        Returns:
            List of top matching jobs with scores
        """
        matches = []

        for job in jobs_data:
            score_data = self.calculate_matching_score(resume_data, job)
            overall_score = score_data.get("overall_score", 0)

            if overall_score >= min_score:
                matches.append(
                    {
                        "job_id": job.get("id"),
                        "job_title": job.get("title"),
                        "company": job.get("company"),
                        "location": job.get("location"),
                        "overall_score": overall_score,
                        "skill_score": score_data.get("skill_score", 0),
                        "experience_score": score_data.get("experience_score", 0),
                        "matching_details": score_data.get("matching_details", {}),
                    }
                )

        # Sort by overall score (descending)
        matches.sort(key=lambda x: x["overall_score"], reverse=True)

        return matches[:limit]

    def get_resume_recommendations(
        self,
        resume_data: Dict[str, Any],
        jobs_data: List[Dict[str, Any]],
        limit: int = 10,
    ) -> Dict[str, Any]:
        """
        Get personalized job recommendations for a resume

        Args:
            resume_data: Parsed resume data
            jobs_data: List of job postings
            limit: Maximum number of recommendations

        Returns:
            Dictionary containing recommendations and insights
        """
        top_matches = self.get_top_matches(resume_data, jobs_data, limit=limit)

        # Analyze skill gaps
        skill_gaps = self._analyze_skill_gaps(resume_data, jobs_data)

        # Get industry insights
        industry_insights = self._get_industry_insights(resume_data, jobs_data)

        return {
            "top_recommendations": top_matches,
            "skill_gaps": skill_gaps,
            "industry_insights": industry_insights,
            "total_jobs_analyzed": len(jobs_data),
            "recommendations_generated_at": datetime.now().isoformat(),
        }

    def _analyze_skill_gaps(
        self, resume_data: Dict[str, Any], jobs_data: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Analyze skill gaps between resume and job market"""
        resume_skills = resume_data.get("skills", {})
        all_job_requirements = {}

        # Collect all job requirements
        for job in jobs_data:
            requirements = self._extract_job_requirements(job)
            for category, skills in requirements.items():
                if category not in all_job_requirements:
                    all_job_requirements[category] = set()
                all_job_requirements[category].update(skills)

        # Find missing skills
        skill_gaps = {}
        for category, job_skills in all_job_requirements.items():
            resume_category_skills = set(resume_skills.get(category, []))
            missing = job_skills - resume_category_skills
            if missing:
                skill_gaps[category] = list(missing)

        return {
            "missing_skills": skill_gaps,
            "skill_gap_count": sum(len(skills) for skills in skill_gaps.values()),
            "most_demanded_skills": self._get_most_demanded_skills(jobs_data),
        }

    def _get_most_demanded_skills(
        self, jobs_data: List[Dict[str, Any]]
    ) -> Dict[str, int]:
        """Get most demanded skills across all jobs"""
        skill_counts = {}

        for job in jobs_data:
            requirements = self._extract_job_requirements(job)
            for category, skills in requirements.items():
                for skill in skills:
                    skill_counts[skill] = skill_counts.get(skill, 0) + 1

        # Sort by frequency
        sorted_skills = sorted(skill_counts.items(), key=lambda x: x[1], reverse=True)
        return dict(sorted_skills[:20])  # Top 20 skills

    def _get_industry_insights(
        self, resume_data: Dict[str, Any], jobs_data: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Get industry insights and trends"""
        # This is a simplified version - in real implementation, you'd analyze industry trends
        return {
            "total_jobs": len(jobs_data),
            "remote_jobs_percentage": self._calculate_remote_percentage(jobs_data),
            "salary_ranges": self._get_salary_ranges(jobs_data),
            "top_companies": self._get_top_companies(jobs_data),
        }

    def _calculate_remote_percentage(self, jobs_data: List[Dict[str, Any]]) -> float:
        """Calculate percentage of remote jobs"""
        remote_count = 0
        for job in jobs_data:
            location = job.get("location", "").lower()
            if "remote" in location or "work from home" in location:
                remote_count += 1

        return (remote_count / len(jobs_data)) * 100 if jobs_data else 0

    def _get_salary_ranges(self, jobs_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Get salary range insights"""
        # Simplified - in real implementation, you'd extract and analyze salary data
        return {"average_salary": "Not available", "salary_range": "Not available"}

    def _get_top_companies(self, jobs_data: List[Dict[str, Any]]) -> List[str]:
        """Get top companies hiring"""
        company_counts = {}
        for job in jobs_data:
            company = job.get("company", "")
            if company:
                company_counts[company] = company_counts.get(company, 0) + 1

        sorted_companies = sorted(
            company_counts.items(), key=lambda x: x[1], reverse=True
        )
        return [company for company, count in sorted_companies[:10]]
