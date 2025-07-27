import asyncio
import json
import logging
import os
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import aiohttp
import requests
from utils.job_crawler import JobListing

logger = logging.getLogger(__name__)


class JobAPIIntegration:
    def __init__(self):
        self.apis = {
            "jsearch": {
                "base_url": "https://jsearch.p.rapidapi.com",
                "api_key": os.getenv("JSEARCH_API_KEY"),
                "rate_limit": 1,  # requests per second
                "endpoints": {"search": "/search", "details": "/job-details"},
            },
            "reed": {
                "base_url": "https://www.reed.co.uk/api/1.0",
                "api_key": os.getenv("REED_API_KEY"),
                "rate_limit": 0.5,
                "endpoints": {"search": "/search"},
            },
            "adzuna": {
                "base_url": "https://api.adzuna.com/v1/api",
                "app_id": os.getenv("ADZUNA_APP_ID"),
                "app_key": os.getenv("ADZUNA_APP_KEY"),
                "rate_limit": 0.5,
                "endpoints": {"search": "/jobs/us/search"},
            },
            "jobs2careers": {
                "base_url": "https://api.jobs2careers.com/api",
                "publisher_id": os.getenv("JOBS2CAREERS_PUBLISHER_ID"),
                "rate_limit": 1,
                "endpoints": {"search": "/search.php"},
            },
        }

    async def fetch_jobs_from_all_apis(
        self,
        query: str = "remote developer",
        location: str = "remote",
        limit_per_api: int = 50,
    ) -> List[JobListing]:
        """
        Fetch jobs from all configured APIs
        """
        all_jobs = []

        for api_name, config in self.apis.items():
            try:
                logger.info(f"Fetching jobs from {api_name} API...")

                if api_name == "jsearch":
                    jobs = await self._fetch_jsearch_jobs(
                        query, location, limit_per_api
                    )
                elif api_name == "reed":
                    jobs = await self._fetch_reed_jobs(query, location, limit_per_api)
                elif api_name == "adzuna":
                    jobs = await self._fetch_adzuna_jobs(query, location, limit_per_api)
                elif api_name == "jobs2careers":
                    jobs = await self._fetch_jobs2careers_jobs(
                        query, location, limit_per_api
                    )
                else:
                    continue

                all_jobs.extend(jobs)
                logger.info(f"Fetched {len(jobs)} jobs from {api_name}")

                # Rate limiting
                await asyncio.sleep(1 / config["rate_limit"])

            except Exception as e:
                logger.error(f"Error fetching from {api_name}: {str(e)}")
                continue

        return all_jobs

    async def _fetch_jsearch_jobs(
        self, query: str, location: str, limit: int
    ) -> List[JobListing]:
        """
        Fetch jobs from JSearch API (RapidAPI)
        """
        jobs = []
        config = self.apis["jsearch"]

        if not config["api_key"]:
            logger.warning("JSearch API key not configured")
            return jobs

        try:
            headers = {
                "X-RapidAPI-Key": config["api_key"],
                "X-RapidAPI-Host": "jsearch.p.rapidapi.com",
            }

            params = {
                "query": f"{query} {location}",
                "page": "1",
                "num_pages": "1",
                "date_posted": "all",
                "remote_jobs_only": "true" if "remote" in location.lower() else "false",
            }

            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{config['base_url']}{config['endpoints']['search']}",
                    headers=headers,
                    params=params,
                ) as response:
                    if response.status == 200:
                        data = await response.json()

                        for job_data in data.get("data", [])[:limit]:
                            job = self._parse_jsearch_job(job_data)
                            if job:
                                jobs.append(job)
                    else:
                        logger.error(f"JSearch API error: {response.status}")

        except Exception as e:
            logger.error(f"Error fetching JSearch jobs: {str(e)}")

        return jobs

    def _parse_jsearch_job(self, job_data: Dict) -> Optional[JobListing]:
        """
        Parse JSearch API response to JobListing
        """
        try:
            return JobListing(
                title=job_data.get("job_title", ""),
                company=job_data.get("employer_name", ""),
                location=job_data.get("job_city", "")
                + ", "
                + job_data.get("job_state", ""),
                job_type=job_data.get("job_employment_type", "Full-time"),
                salary=self._format_salary(
                    job_data.get("job_min_salary"), job_data.get("job_max_salary")
                ),
                description=job_data.get("job_description", ""),
                requirements=self._extract_requirements_from_description(
                    job_data.get("job_description", "")
                ),
                posted_date=self._parse_date(
                    job_data.get("job_posted_at_datetime_utc")
                ),
                apply_url=job_data.get("job_apply_link", ""),
                remote_type=self._determine_remote_type_from_data(job_data),
                skills=self._extract_skills_from_description(
                    job_data.get("job_description", "")
                ),
                source_url="jsearch.p.rapidapi.com",
                external_id=f"jsearch_{job_data.get('job_id', '')}",
            )
        except Exception as e:
            logger.error(f"Error parsing JSearch job: {str(e)}")
            return None

    async def _fetch_reed_jobs(
        self, query: str, location: str, limit: int
    ) -> List[JobListing]:
        """
        Fetch jobs from Reed API
        """
        jobs = []
        config = self.apis["reed"]

        if not config["api_key"]:
            logger.warning("Reed API key not configured")
            return jobs

        try:
            auth = aiohttp.BasicAuth(config["api_key"], "")

            params = {
                "keywords": query,
                "locationName": location,
                "resultsToTake": min(limit, 100),  # Reed max is 100
                "distanceFromLocation": 15,
            }

            async with aiohttp.ClientSession(auth=auth) as session:
                async with session.get(
                    f"{config['base_url']}{config['endpoints']['search']}",
                    params=params,
                ) as response:
                    if response.status == 200:
                        data = await response.json()

                        for job_data in data.get("results", []):
                            job = self._parse_reed_job(job_data)
                            if job:
                                jobs.append(job)
                    else:
                        logger.error(f"Reed API error: {response.status}")

        except Exception as e:
            logger.error(f"Error fetching Reed jobs: {str(e)}")

        return jobs

    def _parse_reed_job(self, job_data: Dict) -> Optional[JobListing]:
        """
        Parse Reed API response to JobListing
        """
        try:
            return JobListing(
                title=job_data.get("jobTitle", ""),
                company=job_data.get("employerName", ""),
                location=job_data.get("locationName", ""),
                job_type=job_data.get("jobType", "Full-time"),
                salary=self._format_salary(
                    job_data.get("minimumSalary"), job_data.get("maximumSalary")
                ),
                description=job_data.get("jobDescription", ""),
                requirements=self._extract_requirements_from_description(
                    job_data.get("jobDescription", "")
                ),
                posted_date=self._parse_date(job_data.get("date")),
                apply_url=job_data.get("jobUrl", ""),
                remote_type=self._determine_remote_type_from_location(
                    job_data.get("locationName", "")
                ),
                skills=self._extract_skills_from_description(
                    job_data.get("jobDescription", "")
                ),
                source_url="reed.co.uk",
                external_id=f"reed_{job_data.get('jobId', '')}",
            )
        except Exception as e:
            logger.error(f"Error parsing Reed job: {str(e)}")
            return None

    async def _fetch_adzuna_jobs(
        self, query: str, location: str, limit: int
    ) -> List[JobListing]:
        """
        Fetch jobs from Adzuna API
        """
        jobs = []
        config = self.apis["adzuna"]

        if not (config["app_id"] and config["app_key"]):
            logger.warning("Adzuna API credentials not configured")
            return jobs

        try:
            params = {
                "app_id": config["app_id"],
                "app_key": config["app_key"],
                "results_per_page": min(limit, 50),  # Adzuna max is 50
                "what": query,
                "where": location,
                "content-type": "application/json",
            }

            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{config['base_url']}{config['endpoints']['search']}/1",
                    params=params,
                ) as response:
                    if response.status == 200:
                        data = await response.json()

                        for job_data in data.get("results", []):
                            job = self._parse_adzuna_job(job_data)
                            if job:
                                jobs.append(job)
                    else:
                        logger.error(f"Adzuna API error: {response.status}")

        except Exception as e:
            logger.error(f"Error fetching Adzuna jobs: {str(e)}")

        return jobs

    def _parse_adzuna_job(self, job_data: Dict) -> Optional[JobListing]:
        """
        Parse Adzuna API response to JobListing
        """
        try:
            return JobListing(
                title=job_data.get("title", ""),
                company=job_data.get("company", {}).get("display_name", ""),
                location=job_data.get("location", {}).get("display_name", ""),
                job_type="Full-time",  # Adzuna doesn't provide this
                salary=self._format_salary(
                    job_data.get("salary_min"), job_data.get("salary_max")
                ),
                description=job_data.get("description", ""),
                requirements=self._extract_requirements_from_description(
                    job_data.get("description", "")
                ),
                posted_date=self._parse_date(job_data.get("created")),
                apply_url=job_data.get("redirect_url", ""),
                remote_type=self._determine_remote_type_from_location(
                    job_data.get("location", {}).get("display_name", "")
                ),
                skills=self._extract_skills_from_description(
                    job_data.get("description", "")
                ),
                source_url="adzuna.com",
                external_id=f"adzuna_{job_data.get('id', '')}",
            )
        except Exception as e:
            logger.error(f"Error parsing Adzuna job: {str(e)}")
            return None

    async def _fetch_jobs2careers_jobs(
        self, query: str, location: str, limit: int
    ) -> List[JobListing]:
        """
        Fetch jobs from Jobs2Careers API
        """
        jobs = []
        config = self.apis["jobs2careers"]

        if not config["publisher_id"]:
            logger.warning("Jobs2Careers publisher ID not configured")
            return jobs

        try:
            params = {
                "publisher": config["publisher_id"],
                "q": query,
                "l": location,
                "limit": min(limit, 50),
                "format": "json",
            }

            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{config['base_url']}{config['endpoints']['search']}",
                    params=params,
                ) as response:
                    if response.status == 200:
                        data = await response.json()

                        for job_data in data.get("jobs", []):
                            job = self._parse_jobs2careers_job(job_data)
                            if job:
                                jobs.append(job)
                    else:
                        logger.error(f"Jobs2Careers API error: {response.status}")

        except Exception as e:
            logger.error(f"Error fetching Jobs2Careers jobs: {str(e)}")

        return jobs

    def _parse_jobs2careers_job(self, job_data: Dict) -> Optional[JobListing]:
        """
        Parse Jobs2Careers API response to JobListing
        """
        try:
            return JobListing(
                title=job_data.get("title", ""),
                company=job_data.get("company", ""),
                location=job_data.get("location", ""),
                job_type=job_data.get("type", "Full-time"),
                salary=job_data.get("salary", ""),
                description=job_data.get("description", ""),
                requirements=self._extract_requirements_from_description(
                    job_data.get("description", "")
                ),
                posted_date=self._parse_date(job_data.get("date")),
                apply_url=job_data.get("url", ""),
                remote_type=self._determine_remote_type_from_location(
                    job_data.get("location", "")
                ),
                skills=self._extract_skills_from_description(
                    job_data.get("description", "")
                ),
                source_url="jobs2careers.com",
                external_id=f"jobs2careers_{job_data.get('id', '')}",
            )
        except Exception as e:
            logger.error(f"Error parsing Jobs2Careers job: {str(e)}")
            return None

    # Helper methods
    def _format_salary(
        self, min_salary: Optional[float], max_salary: Optional[float]
    ) -> Optional[str]:
        """
        Format salary range from min/max values
        """
        if min_salary and max_salary:
            return f"${int(min_salary):,} - ${int(max_salary):,}"
        elif min_salary:
            return f"${int(min_salary):,}+"
        elif max_salary:
            return f"Up to ${int(max_salary):,}"
        return None

    def _parse_date(self, date_str: Optional[str]) -> Optional[datetime]:
        """
        Parse date string to datetime object
        """
        if not date_str:
            return None

        try:
            # Try different date formats
            date_formats = [
                "%Y-%m-%dT%H:%M:%S.%fZ",
                "%Y-%m-%dT%H:%M:%SZ",
                "%Y-%m-%d",
                "%d/%m/%Y",
                "%m/%d/%Y",
            ]

            for fmt in date_formats:
                try:
                    return datetime.strptime(date_str, fmt)
                except ValueError:
                    continue

        except Exception as e:
            logger.error(f"Error parsing date {date_str}: {str(e)}")

        return None

    def _determine_remote_type_from_data(self, job_data: Dict) -> str:
        """
        Determine remote type from job data
        """
        location = job_data.get("job_city", "") + " " + job_data.get("job_state", "")
        remote_allowed = job_data.get("job_is_remote", False)

        if remote_allowed or "remote" in location.lower():
            return "remote"
        elif "hybrid" in location.lower():
            return "hybrid"
        else:
            return "onsite"

    def _determine_remote_type_from_location(self, location: str) -> str:
        """
        Determine remote type from location string
        """
        location_lower = location.lower()

        if any(
            word in location_lower
            for word in ["remote", "anywhere", "worldwide", "work from home"]
        ):
            return "remote"
        elif any(word in location_lower for word in ["hybrid", "flexible"]):
            return "hybrid"
        else:
            return "onsite"

    def _extract_requirements_from_description(self, description: str) -> List[str]:
        """
        Extract requirements from job description
        """
        import re

        requirements = []

        # Look for requirement patterns
        requirement_patterns = [
            r"(?:requirements?|qualifications?|must have|essential).*?(?:\n\n|\n(?=[A-Z])|$)",
            r"(?:experience with|knowledge of|proficient in).*?(?:\n|\.|,)",
            r"(?:\d+\+?\s*years?\s*(?:of\s*)?experience)",
        ]

        for pattern in requirement_patterns:
            matches = re.findall(pattern, description, re.IGNORECASE | re.DOTALL)
            requirements.extend(matches)

        return [req.strip() for req in requirements if len(req.strip()) > 10][
            :5
        ]  # Limit to 5

    def _extract_skills_from_description(self, description: str) -> List[str]:
        """
        Extract skills from job description
        """
        common_skills = [
            "Python",
            "JavaScript",
            "Java",
            "C++",
            "C#",
            "PHP",
            "Ruby",
            "Go",
            "Rust",
            "React",
            "Vue",
            "Angular",
            "Node.js",
            "Django",
            "Flask",
            "Laravel",
            "AWS",
            "Azure",
            "GCP",
            "Docker",
            "Kubernetes",
            "Jenkins",
            "SQL",
            "MongoDB",
            "PostgreSQL",
            "Redis",
            "Elasticsearch",
            "Git",
            "Linux",
            "API",
            "REST",
            "GraphQL",
            "Microservices",
        ]

        found_skills = []
        description_lower = description.lower()

        for skill in common_skills:
            if skill.lower() in description_lower:
                found_skills.append(skill)

        return found_skills[:10]  # Limit to 10 skills


class JobDataAggregator:
    def __init__(self):
        self.api_integration = JobAPIIntegration()

    async def aggregate_jobs_from_all_sources(self) -> Dict[str, Any]:
        """
        Aggregate jobs from both crawling and API sources
        """
        try:
            from utils.job_crawler import JobDataManager

            from database import get_db

            # Get jobs from crawling
            crawler_manager = JobDataManager()
            crawl_result = await crawler_manager.update_job_listings()

            # Get jobs from APIs
            api_jobs = await self.api_integration.fetch_jobs_from_all_apis()

            # Save API jobs to database
            db = get_db()
            jobs_collection = db["jobs"]

            api_new_jobs = 0
            api_updated_jobs = 0

            for job in api_jobs:
                # Check if job already exists
                existing_job = jobs_collection.find_one(
                    {"external_id": job.external_id, "source_url": job.source_url}
                )

                job_data = {
                    "title": job.title,
                    "company": job.company,
                    "location": job.location,
                    "job_type": job.job_type,
                    "salary": job.salary,
                    "description": job.description,
                    "requirements": job.requirements,
                    "posted_date": job.posted_date,
                    "apply_url": job.apply_url,
                    "remote_type": job.remote_type,
                    "skills": job.skills,
                    "source_url": job.source_url,
                    "external_id": job.external_id,
                    "is_active": True,
                    "last_updated": datetime.now(),
                    "source_type": "api",
                }

                if existing_job:
                    jobs_collection.update_one(
                        {"_id": existing_job["_id"]}, {"$set": job_data}
                    )
                    api_updated_jobs += 1
                else:
                    job_data["created_at"] = datetime.now()
                    jobs_collection.insert_one(job_data)
                    api_new_jobs += 1

            return {
                "status": "success",
                "crawl_result": crawl_result,
                "api_result": {
                    "new_jobs": api_new_jobs,
                    "updated_jobs": api_updated_jobs,
                    "total_fetched": len(api_jobs),
                },
                "total_new_jobs": crawl_result.get("new_jobs", 0) + api_new_jobs,
                "total_updated_jobs": crawl_result.get("updated_jobs", 0)
                + api_updated_jobs,
            }

        except Exception as e:
            logger.error(f"Error aggregating jobs: {str(e)}")
            return {"status": "error", "message": str(e)}
