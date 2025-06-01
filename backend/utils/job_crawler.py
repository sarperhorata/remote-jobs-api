import requests
import logging
import asyncio
import aiohttp
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import re
import json
from urllib.parse import urljoin, urlparse
from dataclasses import dataclass
import time

logger = logging.getLogger(__name__)

@dataclass
class JobListing:
    title: str
    company: str
    location: str
    job_type: str
    salary: Optional[str]
    description: str
    requirements: List[str]
    posted_date: Optional[datetime]
    apply_url: str
    remote_type: str  # "remote", "hybrid", "onsite"
    skills: List[str]
    source_url: str
    external_id: str

class JobCrawler:
    def __init__(self):
        self.session = None
        self.crawl_config = self._load_crawl_config()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
    def _load_crawl_config(self) -> Dict:
        """
        Load crawling configuration for different company websites
        """
        return {
            "companies": {
                "remote_ok": {
                    "base_url": "https://remoteok.io/api",
                    "type": "api",
                    "rate_limit": 1,  # requests per second
                    "selectors": {}
                },
                "we_work_remotely": {
                    "base_url": "https://weworkremotely.com",
                    "type": "scrape",
                    "rate_limit": 0.5,
                    "job_list_path": "/remote-jobs",
                    "selectors": {
                        "job_item": "section.jobs li",
                        "title": ".title",
                        "company": ".company",
                        "location": ".region",
                        "job_link": "a"
                    }
                },
                "remote_co": {
                    "base_url": "https://remote.co",
                    "type": "scrape",
                    "rate_limit": 0.5,
                    "job_list_path": "/remote-jobs",
                    "selectors": {
                        "job_item": ".job_board_list .card",
                        "title": ".card-title",
                        "company": ".card-text .company",
                        "location": ".card-text .location",
                        "job_link": "a"
                    }
                },
                "angel_co": {
                    "base_url": "https://angel.co",
                    "type": "api",
                    "rate_limit": 0.5,
                    "api_endpoint": "/api/jobs",
                    "selectors": {}
                },
                "stackoverflow_jobs": {
                    "base_url": "https://stackoverflow.com",
                    "type": "scrape",
                    "rate_limit": 0.5,
                    "job_list_path": "/jobs/remote-developer-jobs",
                    "selectors": {
                        "job_item": ".js-job-link",
                        "title": ".fc-black-900",
                        "company": ".fc-black-700",
                        "location": ".fc-black-500",
                        "job_link": "a"
                    }
                }
            }
        }
    
    async def crawl_all_companies(self) -> List[JobListing]:
        """
        Crawl all configured companies for job listings
        """
        all_jobs = []
        
        async with aiohttp.ClientSession(headers=self.headers) as session:
            self.session = session
            
            for company_name, config in self.crawl_config["companies"].items():
                try:
                    logger.info(f"Crawling {company_name}...")
                    
                    if config["type"] == "api":
                        jobs = await self._crawl_api_jobs(company_name, config)
                    else:
                        jobs = await self._crawl_website_jobs(company_name, config)
                    
                    all_jobs.extend(jobs)
                    logger.info(f"Found {len(jobs)} jobs from {company_name}")
                    
                    # Rate limiting
                    await asyncio.sleep(1 / config["rate_limit"])
                    
                except Exception as e:
                    logger.error(f"Error crawling {company_name}: {str(e)}")
                    continue
        
        return all_jobs
    
    async def _crawl_api_jobs(self, company_name: str, config: Dict) -> List[JobListing]:
        """
        Crawl jobs from API endpoints
        """
        jobs = []
        
        try:
            if company_name == "remote_ok":
                jobs = await self._crawl_remote_ok_api(config)
            elif company_name == "angel_co":
                jobs = await self._crawl_angel_co_api(config)
            
        except Exception as e:
            logger.error(f"Error crawling API for {company_name}: {str(e)}")
        
        return jobs
    
    async def _crawl_remote_ok_api(self, config: Dict) -> List[JobListing]:
        """
        Crawl RemoteOK API
        """
        jobs = []
        
        try:
            async with self.session.get(f"{config['base_url']}") as response:
                if response.status == 200:
                    data = await response.json()
                    
                    for job_data in data[1:]:  # Skip first item (metadata)
                        try:
                            job = JobListing(
                                title=job_data.get("position", ""),
                                company=job_data.get("company", ""),
                                location=job_data.get("location", "Remote"),
                                job_type="Full-time",
                                salary=self._extract_salary(job_data.get("description", "")),
                                description=job_data.get("description", ""),
                                requirements=self._extract_requirements(job_data.get("description", "")),
                                posted_date=datetime.fromtimestamp(job_data.get("date", 0)) if job_data.get("date") else None,
                                apply_url=job_data.get("url", ""),
                                remote_type="remote",
                                skills=job_data.get("tags", []),
                                source_url="https://remoteok.io",
                                external_id=str(job_data.get("id", ""))
                            )
                            jobs.append(job)
                        except Exception as e:
                            logger.error(f"Error parsing RemoteOK job: {str(e)}")
                            continue
                            
        except Exception as e:
            logger.error(f"Error fetching RemoteOK API: {str(e)}")
        
        return jobs
    
    async def _crawl_website_jobs(self, company_name: str, config: Dict) -> List[JobListing]:
        """
        Crawl jobs from website HTML
        """
        jobs = []
        
        try:
            url = f"{config['base_url']}{config['job_list_path']}"
            
            async with self.session.get(url) as response:
                if response.status == 200:
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')
                    
                    job_elements = soup.select(config["selectors"]["job_item"])
                    
                    for job_element in job_elements:
                        try:
                            job = await self._parse_job_element(job_element, config, company_name)
                            if job:
                                jobs.append(job)
                        except Exception as e:
                            logger.error(f"Error parsing job element from {company_name}: {str(e)}")
                            continue
                            
        except Exception as e:
            logger.error(f"Error crawling website {company_name}: {str(e)}")
        
        return jobs
    
    async def _parse_job_element(self, job_element, config: Dict, company_name: str) -> Optional[JobListing]:
        """
        Parse individual job element from HTML
        """
        try:
            selectors = config["selectors"]
            
            title_elem = job_element.select_one(selectors.get("title", ""))
            company_elem = job_element.select_one(selectors.get("company", ""))
            location_elem = job_element.select_one(selectors.get("location", ""))
            link_elem = job_element.select_one(selectors.get("job_link", "a"))
            
            if not (title_elem and link_elem):
                return None
            
            title = title_elem.get_text(strip=True)
            company = company_elem.get_text(strip=True) if company_elem else ""
            location = location_elem.get_text(strip=True) if location_elem else "Remote"
            
            job_url = link_elem.get('href', '')
            if job_url and not job_url.startswith('http'):
                job_url = urljoin(config["base_url"], job_url)
            
            # Get job details from individual job page
            job_details = await self._get_job_details(job_url)
            
            return JobListing(
                title=title,
                company=company,
                location=location,
                job_type="Full-time",
                salary=job_details.get("salary"),
                description=job_details.get("description", ""),
                requirements=job_details.get("requirements", []),
                posted_date=job_details.get("posted_date"),
                apply_url=job_url,
                remote_type=self._determine_remote_type(location),
                skills=job_details.get("skills", []),
                source_url=config["base_url"],
                external_id=self._generate_external_id(job_url)
            )
            
        except Exception as e:
            logger.error(f"Error parsing job element: {str(e)}")
            return None
    
    async def _get_job_details(self, job_url: str) -> Dict:
        """
        Get detailed job information from individual job page
        """
        details = {
            "description": "",
            "requirements": [],
            "salary": None,
            "posted_date": None,
            "skills": []
        }
        
        try:
            async with self.session.get(job_url) as response:
                if response.status == 200:
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')
                    
                    # Extract description
                    description_selectors = [
                        '.job-description',
                        '.description',
                        '.job-content',
                        '[class*="description"]'
                    ]
                    
                    for selector in description_selectors:
                        desc_elem = soup.select_one(selector)
                        if desc_elem:
                            details["description"] = desc_elem.get_text(strip=True)
                            break
                    
                    # Extract requirements
                    details["requirements"] = self._extract_requirements(details["description"])
                    
                    # Extract salary
                    details["salary"] = self._extract_salary(details["description"])
                    
                    # Extract skills
                    details["skills"] = self._extract_skills(details["description"])
                    
        except Exception as e:
            logger.error(f"Error getting job details from {job_url}: {str(e)}")
        
        return details
    
    def _extract_salary(self, text: str) -> Optional[str]:
        """
        Extract salary information from job text
        """
        salary_patterns = [
            r'\$[\d,]+\s*-\s*\$[\d,]+',
            r'\$[\d,]+k?\s*-\s*\$[\d,]+k?',
            r'[\d,]+\s*-\s*[\d,]+\s*USD',
            r'€[\d,]+\s*-\s*€[\d,]+',
            r'£[\d,]+\s*-\s*£[\d,]+'
        ]
        
        for pattern in salary_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(0)
        
        return None
    
    def _extract_requirements(self, text: str) -> List[str]:
        """
        Extract job requirements from description
        """
        requirements = []
        
        # Look for common requirement patterns
        requirement_patterns = [
            r'(?:requirements?|qualifications?|must have).*?(?:\n\n|\n(?=[A-Z])|$)',
            r'(?:experience with|knowledge of|proficient in).*?(?:\n|\.|,)',
            r'(?:\d+\+?\s*years?\s*(?:of\s*)?experience)',
        ]
        
        for pattern in requirement_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE | re.DOTALL)
            requirements.extend(matches)
        
        return [req.strip() for req in requirements if len(req.strip()) > 10]
    
    def _extract_skills(self, text: str) -> List[str]:
        """
        Extract technical skills from job description
        """
        common_skills = [
            'Python', 'JavaScript', 'Java', 'C++', 'C#', 'PHP', 'Ruby', 'Go', 'Rust',
            'React', 'Vue', 'Angular', 'Node.js', 'Django', 'Flask', 'Laravel',
            'AWS', 'Azure', 'GCP', 'Docker', 'Kubernetes', 'Jenkins',
            'SQL', 'MongoDB', 'PostgreSQL', 'Redis', 'Elasticsearch',
            'Git', 'Linux', 'API', 'REST', 'GraphQL', 'Microservices'
        ]
        
        found_skills = []
        text_lower = text.lower()
        
        for skill in common_skills:
            if skill.lower() in text_lower:
                found_skills.append(skill)
        
        return found_skills
    
    def _determine_remote_type(self, location: str) -> str:
        """
        Determine if job is remote, hybrid, or onsite
        """
        location_lower = location.lower()
        
        if any(word in location_lower for word in ['remote', 'anywhere', 'worldwide']):
            return 'remote'
        elif any(word in location_lower for word in ['hybrid', 'flexible']):
            return 'hybrid'
        else:
            return 'onsite'
    
    def _generate_external_id(self, url: str) -> str:
        """
        Generate external ID from job URL
        """
        return f"{urlparse(url).netloc}_{hash(url)}"

class JobDataManager:
    def __init__(self):
        self.crawler = JobCrawler()
        
    async def update_job_listings(self) -> Dict[str, Any]:
        """
        Update job listings from all sources
        """
        try:
            from database import get_db
            
            # Crawl all jobs
            crawled_jobs = await self.crawler.crawl_all_companies()
            
            # Save to database
            db = get_db()
            jobs_collection = db["jobs"]
            
            new_jobs = 0
            updated_jobs = 0
            
            for job in crawled_jobs:
                # Check if job already exists
                existing_job = jobs_collection.find_one({
                    "external_id": job.external_id,
                    "source_url": job.source_url
                })
                
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
                    "last_updated": datetime.now()
                }
                
                if existing_job:
                    jobs_collection.update_one(
                        {"_id": existing_job["_id"]},
                        {"$set": job_data}
                    )
                    updated_jobs += 1
                else:
                    job_data["created_at"] = datetime.now()
                    jobs_collection.insert_one(job_data)
                    new_jobs += 1
            
            # Deactivate old jobs
            cutoff_date = datetime.now() - timedelta(days=30)
            deactivated = jobs_collection.update_many(
                {"last_updated": {"$lt": cutoff_date}},
                {"$set": {"is_active": False}}
            )
            
            return {
                "status": "success",
                "new_jobs": new_jobs,
                "updated_jobs": updated_jobs,
                "deactivated_jobs": deactivated.modified_count,
                "total_crawled": len(crawled_jobs)
            }
            
        except Exception as e:
            logger.error(f"Error updating job listings: {str(e)}")
            return {
                "status": "error",
                "message": str(e)
            }

    async def save_jobs_to_database(self, jobs: List[JobListing]):
        """Save jobs to MongoDB database"""
        try:
            db = get_db()
            jobs_collection = db["jobs"]
            
            new_jobs = 0
            updated_jobs = 0
            
            for job in jobs:
                # Check if job already exists using title and company
                existing_job = jobs_collection.find_one({
                    "title": job.title,
                    "company": job.company
                })
                
                job_data = {
                    "title": job.title,
                    "company": job.company,
                    "location": job.location,
                    "job_type": job.job_type,
                    "salary": job.salary,
                    "description": job.description,
                    "requirements": job.requirements or [],
                    "posted_date": job.posted_date,
                    "remote_type": job.remote_type,
                    "skills": job.skills or [],
                    "source_url": job.source_url,
                    "external_id": job.external_id,
                    "is_active": True,
                    "last_updated": datetime.now(),
                    "source_type": "distill_crawler"
                }
                
                if existing_job:
                    # Update application URLs array
                    application_urls = existing_job.get("application_urls", [])
                    if job.apply_url not in application_urls:
                        application_urls.append({
                            "url": job.apply_url,
                            "source": job.source_url,
                            "added_at": datetime.now()
                        })
                    
                    # Update job data with new application URLs
                    job_data["application_urls"] = application_urls
                    
                    # Update only if there are changes
                    if any(job_data[key] != existing_job.get(key) for key in job_data.keys()):
                        jobs_collection.update_one(
                            {"_id": existing_job["_id"]},
                            {"$set": job_data}
                        )
                        updated_jobs += 1
                else:
                    # Create new job with initial application URL
                    job_data["application_urls"] = [{
                        "url": job.apply_url,
                        "source": job.source_url,
                        "added_at": datetime.now()
                    }]
                    job_data["created_at"] = datetime.now()
                    jobs_collection.insert_one(job_data)
                    new_jobs += 1
            
            logger.info(f"💾 Database save completed: {new_jobs} new, {updated_jobs} updated")
            
            return {
                "new_jobs": new_jobs,
                "updated_jobs": updated_jobs,
                "total_processed": len(jobs)
            }
            
        except Exception as e:
            logger.error(f"❌ Error saving to database: {str(e)}")
            raise 