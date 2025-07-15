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
from backend.services.job_deduplication_service import deduplication_service

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
    """Job crawler with deduplication support"""
    
    def __init__(self):
        self.session = None
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession(headers=self.headers)
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def crawl_jobs(self, urls: List[str]) -> List[Dict[str, Any]]:
        """Crawl jobs from multiple URLs with deduplication"""
        jobs = []
        
        for url in urls:
            try:
                page_jobs = await self.crawl_single_page(url)
                jobs.extend(page_jobs)
                await asyncio.sleep(1)  # Rate limiting
            except Exception as e:
                logger.error(f"Error crawling {url}: {str(e)}")
                continue
        
        return jobs
    
    async def crawl_single_page(self, url: str) -> List[Dict[str, Any]]:
        """Crawl jobs from a single page"""
        if not self.session:
            self.session = aiohttp.ClientSession(headers=self.headers)
        
        try:
            async with self.session.get(url) as response:
                if response.status != 200:
                    logger.warning(f"Failed to fetch {url}: {response.status}")
                    return []
                
                html = await response.text()
                return self.parse_jobs(html, url)
                
        except Exception as e:
            logger.error(f"Error fetching {url}: {str(e)}")
            return []
    
    def parse_jobs(self, html: str, source_url: str) -> List[Dict[str, Any]]:
        """Parse jobs from HTML content"""
        soup = BeautifulSoup(html, 'html.parser')
        jobs = []
        
        # Generic job parsing logic
        job_elements = soup.find_all(['div', 'article', 'li'], class_=re.compile(r'job|position|listing', re.I))
        
        for element in job_elements:
            try:
                job_data = self.extract_job_data(element, source_url)
                if job_data:
                    jobs.append(job_data)
            except Exception as e:
                logger.error(f"Error parsing job element: {str(e)}")
                continue
        
        return jobs
    
    def extract_job_data(self, element, source_url: str) -> Optional[Dict[str, Any]]:
        """Extract job data from HTML element"""
        try:
            # Extract title
            title_elem = element.find(['h1', 'h2', 'h3', 'h4'], class_=re.compile(r'title|position', re.I))
            title = title_elem.get_text().strip() if title_elem else None
            
            # Extract company
            company_elem = element.find(['span', 'div'], class_=re.compile(r'company|employer', re.I))
            company = company_elem.get_text().strip() if company_elem else None
            
            # Extract description
            desc_elem = element.find(['div', 'p'], class_=re.compile(r'description|summary', re.I))
            description = desc_elem.get_text().strip() if desc_elem else None
            
            # Extract location
            location_elem = element.find(['span', 'div'], class_=re.compile(r'location|place', re.I))
            location = location_elem.get_text().strip() if location_elem else "Remote"
            
            # Extract apply URL
            apply_link = element.find('a', href=True, text=re.compile(r'apply|application', re.I))
            apply_url = urljoin(source_url, apply_link['href']) if apply_link else None
            
            # Generate external ID
            external_id = f"{title}_{company}_{source_url}" if title and company else None
            
            if not title or not company:
                return None
            
            return {
                'title': title,
                'company': company,
                'description': description,
                'location': location,
                'apply_url': apply_url,
                'source_url': source_url,
                'external_id': external_id,
                'crawled_at': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error extracting job data: {str(e)}")
            return None

class JobDataManager:
    def __init__(self):
        self.crawler = JobCrawler()
        
    async def update_job_listings(self) -> Dict[str, Any]:
        """
        Update job listings from all sources with deduplication
        """
        try:
            from database import get_db
            
            # Crawl all jobs
            crawled_jobs = await self.crawler.crawl_all_companies()
            
            # Save to database with deduplication
            new_jobs = 0
            updated_jobs = 0
            duplicates = 0
            
            for job in crawled_jobs:
                try:
                    # Use deduplication service
                    job_id, dedup_result = await deduplication_service.save_job_with_deduplication(job)
                    
                    if dedup_result.is_duplicate:
                        duplicates += 1
                        if dedup_result.confidence_level in ["high", "medium"]:
                            updated_jobs += 1
                    else:
                        new_jobs += 1
                        
                except Exception as e:
                    logger.error(f"Error saving job {job.get('title', 'Unknown')}: {str(e)}")
                    continue
            
            logger.info(f"💾 Database save completed: {new_jobs} new, {updated_jobs} updated, {duplicates} duplicates")
            
            return {
                "new_jobs": new_jobs,
                "updated_jobs": updated_jobs,
                "duplicates": duplicates,
                "total_processed": len(crawled_jobs)
            }
            
        except Exception as e:
            logger.error(f"❌ Error updating job listings: {str(e)}")
            raise
    
    async def save_jobs_with_deduplication(self, jobs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Save jobs to database with deduplication
        """
        try:
            new_jobs = 0
            updated_jobs = 0
            duplicates = 0
            
            for job in jobs:
                try:
                    # Use deduplication service
                    job_id, dedup_result = await deduplication_service.save_job_with_deduplication(job)
                    
                    if dedup_result.is_duplicate:
                        duplicates += 1
                        if dedup_result.confidence_level in ["high", "medium"]:
                            updated_jobs += 1
                    else:
                        new_jobs += 1
                        
                except Exception as e:
                    logger.error(f"Error saving job {job.get('title', 'Unknown')}: {str(e)}")
                    continue
            
            logger.info(f"💾 Database save completed: {new_jobs} new, {updated_jobs} updated, {duplicates} duplicates")
            
            return {
                "new_jobs": new_jobs,
                "updated_jobs": updated_jobs,
                "duplicates": duplicates,
                "total_processed": len(jobs)
            }
            
        except Exception as e:
            logger.error(f"❌ Error saving to database: {str(e)}")
            raise 