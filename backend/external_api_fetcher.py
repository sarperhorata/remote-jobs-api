import asyncio
import logging
from datetime import datetime
from typing import Any, Dict, List

import aiohttp
from motor.motor_asyncio import AsyncIOMotorClient

from config import MONGODB_URL

logger = logging.getLogger(__name__)


class ExternalAPIFetcher:
    def __init__(self):
        self.client = AsyncIOMotorClient(MONGODB_URL)
        self.db = self.client.buzz2remote
        self.jobs_collection = self.db.jobs
        self.companies_collection = self.db.companies

        # Configure external APIs
        self.apis = {
            "remoteok": "https://remoteok.com/api/v1/jobs",
            "weworkremotely": "https://weworkremotely.com/api/v1/jobs",
            "github": "https://jobs.github.com/positions.json",
        }

    async def fetch_all_apis(self):
        """Fetch jobs from all configured external APIs"""
        tasks = []
        for api_name, api_url in self.apis.items():
            tasks.append(self.fetch_api(api_name, api_url))

        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Log results
        for api_name, result in zip(self.apis.keys(), results):
            if isinstance(result, Exception):
                logger.error(f"Error fetching {api_name}: {str(result)}")
            else:
                logger.info(f"Successfully fetched {result} jobs from {api_name}")

    async def fetch_api(self, api_name: str, api_url: str) -> int:
        """Fetch jobs from a specific API"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(api_url) as response:
                    if response.status != 200:
                        raise Exception(f"API returned status {response.status}")

                    jobs = await response.json()
                    processed_jobs = await self.process_jobs(api_name, jobs)
                    return len(processed_jobs)
        except Exception as e:
            logger.error(f"Error fetching {api_name}: {str(e)}")
            raise

    async def process_jobs(
        self, api_name: str, jobs: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Process and store jobs from an API"""
        processed_jobs = []

        for job in jobs:
            try:
                # Transform job data to our format
                processed_job = self.transform_job(api_name, job)

                # Check if job already exists
                existing_job = await self.jobs_collection.find_one(
                    {"source": api_name, "source_id": processed_job["source_id"]}
                )

                if existing_job:
                    # Update existing job
                    await self.jobs_collection.update_one(
                        {"_id": existing_job["_id"]}, {"$set": processed_job}
                    )
                else:
                    # Insert new job
                    await self.jobs_collection.insert_one(processed_job)

                processed_jobs.append(processed_job)
            except Exception as e:
                logger.error(f"Error processing job from {api_name}: {str(e)}")
                continue

        return processed_jobs

    def transform_job(self, api_name: str, job: Dict[str, Any]) -> Dict[str, Any]:
        """Transform job data from API format to our format"""
        # Base job structure
        transformed_job = {
            "title": job.get("title", ""),
            "company": job.get("company", ""),
            "location": job.get("location", "Remote"),
            "description": job.get("description", ""),
            "url": job.get("url", ""),
            "source": api_name,
            "source_id": str(job.get("id", "")),
            "posted_at": job.get("posted_at", datetime.utcnow()),
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "status": "active",
        }

        # API-specific transformations
        if api_name == "remoteok":
            transformed_job.update(
                {
                    "salary": job.get("salary", ""),
                    "tags": job.get("tags", []),
                    "company_logo": job.get("company_logo", ""),
                }
            )
        elif api_name == "weworkremotely":
            transformed_job.update(
                {
                    "category": job.get("category", ""),
                    "company_logo": job.get("company_logo", ""),
                }
            )
        elif api_name == "github":
            transformed_job.update(
                {
                    "company_logo": job.get("company_logo", ""),
                    "type": job.get("type", ""),
                    "how_to_apply": job.get("how_to_apply", ""),
                }
            )

        return transformed_job


if __name__ == "__main__":
    # Set up logging
    logging.basicConfig(level=logging.INFO)

    # Run the fetcher
    fetcher = ExternalAPIFetcher()
    asyncio.run(fetcher.fetch_all_apis())
