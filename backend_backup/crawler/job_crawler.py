import requests
from bs4 import BeautifulSoup
import time
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
import re

from models.models import Job, Website, WebsiteType, SelectorBase

logger = logging.getLogger(__name__)

class JobCrawler:
    """
    Crawler class used to extract job listings.
    """
    
    def __init__(self):
        # Set User-Agent to mimic a real browser
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
    
    async def get_jobs_from_website(self, website: Website, keywords: Optional[List[str]] = None, exclude_keywords: Optional[List[str]] = None) -> List[Job]:
        """
        Extracts job listings from the given website
        """
        logger.info(f"Crawling jobs from {website.name}: {website.url}")
        
        if website.website_type == WebsiteType.REMOTE_OK:
            return await self._crawl_remote_ok(website)
        elif website.website_type == WebsiteType.WE_WORK_REMOTELY:
            return await self._crawl_we_work_remotely(website)
        elif website.website_type == WebsiteType.REMOTE_CO:
            return await self._crawl_remote_co(website)
        elif website.website_type == WebsiteType.JOBS_FROM_SPACE:
            return await self._crawl_jobs_from_space(website)
        elif website.website_type == WebsiteType.REMOTIVE:
            return await self._crawl_remotive(website)
        elif website.website_type == WebsiteType.CUSTOM:
            return await self._crawl_custom_website(website)
        else:
            logger.error(f"Unsupported website type: {website.website_type}")
            return []
    
    async def _crawl_remote_ok(self, website: Website) -> List[Job]:
        """
        Extracts job listings from RemoteOK sites
        """
        jobs = []
        try:
            response = self.session.get(website.url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            job_listings = soup.select('tr.job')
            
            for job in job_listings:
                try:
                    title_elem = job.select_one('.company_and_position h2')
                    company_elem = job.select_one('.company_and_position h3')
                    link_elem = job.select_one('a.preventLink')
                    tags_elems = job.select('.tags .tag')
                    
                    if not title_elem or not link_elem:
                        continue
                    
                    title = title_elem.text.strip()
                    company = company_elem.text.strip() if company_elem else "Unknown"
                    url = "https://remoteok.com" + link_elem.get('href', '')
                    tags = [tag.text.strip() for tag in tags_elems] if tags_elems else []
                    
                    job_data = {
                        "title": title,
                        "company": company,
                        "url": url,
                        "tags": tags,
                        "is_remote": True,
                        "website_id": website.id,
                        "posted_date": datetime.now(),  # Remote OK doesn't show clear posting dates
                    }
                    
                    jobs.append(job_data)
                except Exception as e:
                    logger.error(f"Error parsing job from RemoteOK: {e}")
            
            logger.info(f"Found {len(jobs)} jobs on RemoteOK")
            return jobs
            
        except Exception as e:
            logger.error(f"Error crawling RemoteOK: {e}")
            return []
    
    async def _crawl_we_work_remotely(self, website: Website) -> List[Job]:
        """
        Extracts job listings from WeWorkRemotely sites
        """
        jobs = []
        try:
            response = self.session.get(website.url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            job_listings = soup.select('li.feature')
            
            for job in job_listings:
                try:
                    title_elem = job.select_one('.title')
                    company_elem = job.select_one('.company')
                    link_elem = job.select_one('a')
                    location_elem = job.select_one('.region')
                    
                    if not title_elem or not link_elem:
                        continue
                    
                    title = title_elem.text.strip()
                    company = company_elem.text.strip() if company_elem else "Unknown"
                    url = "https://weworkremotely.com" + link_elem.get('href', '')
                    location = location_elem.text.strip() if location_elem else None
                    
                    job_data = {
                        "title": title,
                        "company": company,
                        "url": url,
                        "location": location,
                        "is_remote": True,
                        "website_id": website.id,
                        "posted_date": datetime.now(),  # WWR doesn't show clear posting dates on list page
                    }
                    
                    jobs.append(job_data)
                except Exception as e:
                    logger.error(f"Error parsing job from WeWorkRemotely: {e}")
            
            logger.info(f"Found {len(jobs)} jobs on WeWorkRemotely")
            return jobs
            
        except Exception as e:
            logger.error(f"Error crawling WeWorkRemotely: {e}")
            return []
    
    async def _crawl_remote_co(self, website: Website) -> List[Job]:
        """
        Extracts job listings from Remote.co sites
        """
        jobs = []
        try:
            response = self.session.get(website.url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            job_cards = soup.select('.card-body.p-0')
            
            for job in job_cards:
                try:
                    title_elem = job.select_one('.font-weight-bold.larger')
                    company_elem = job.select_one('p.m-0:nth-child(2)')
                    link_elem = job.select_one('a.stretched-link')
                    
                    if not title_elem or not link_elem:
                        continue
                    
                    title = title_elem.text.strip()
                    company = company_elem.text.strip() if company_elem else "Unknown"
                    url = link_elem.get('href', '')
                    if not url.startswith('http'):
                        url = "https://remote.co" + url
                    
                    job_data = {
                        "title": title,
                        "company": company,
                        "url": url,
                        "is_remote": True,
                        "website_id": website.id,
                        "posted_date": datetime.now(),  # Assume current date for simplicity
                    }
                    
                    jobs.append(job_data)
                except Exception as e:
                    logger.error(f"Error parsing job from Remote.co: {e}")
            
            logger.info(f"Found {len(jobs)} jobs on Remote.co")
            return jobs
            
        except Exception as e:
            logger.error(f"Error crawling Remote.co: {e}")
            return []
    
    async def _crawl_jobs_from_space(self, website: Website) -> List[Job]:
        """
        Extracts job listings from JobsFromSpace
        """
        jobs = []
        try:
            response = self.session.get(website.url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Try to find job listings container
            job_listings_container = soup.find('div', class_='job-listings') or soup.find('div', {'id': 'job-list'})
            
            # If container not found with specific classes, try more general approach
            if not job_listings_container:
                job_listings = soup.find_all('div', class_=lambda c: c and ('job-card' in c.lower() or 'job-listing' in c.lower()))
            else:
                job_listings = job_listings_container.find_all('div', class_=lambda c: c and ('job' in c.lower()))
            
            for job in job_listings:
                try:
                    # Extract job title
                    title_elem = job.find('h2') or job.find('h3') or job.find('a', class_=lambda c: c and ('title' in c.lower()))
                    
                    # Extract company name
                    company_elem = job.find('span', class_=lambda c: c and ('company' in c.lower())) or \
                                  job.find('div', class_=lambda c: c and ('company' in c.lower()))
                    
                    # Extract job URL
                    link_elem = job.find('a', href=True)
                    
                    # Extract location
                    location_elem = job.find('span', class_=lambda c: c and ('location' in c.lower())) or \
                                   job.find('div', class_=lambda c: c and ('location' in c.lower()))
                    
                    # Extract tags/skills
                    tags_container = job.find('div', class_=lambda c: c and ('tags' in c.lower() or 'skills' in c.lower()))
                    tags = []
                    if tags_container:
                        tag_elements = tags_container.find_all('span') or tags_container.find_all('a')
                        tags = [tag.text.strip() for tag in tag_elements]
                    
                    # Continue only if we have the essential information
                    if not title_elem or not link_elem:
                        continue
                    
                    title = title_elem.text.strip()
                    company = company_elem.text.strip() if company_elem else "Unknown"
                    
                    # Format URL properly
                    url = link_elem['href']
                    if not url.startswith(('http://', 'https://')):
                        url = f"https://www.jobsfromspace.com{url}" if not url.startswith('/') else f"https://www.jobsfromspace.com{url}"
                    
                    location = location_elem.text.strip() if location_elem else None
                    
                    # Create job data
                    job_data = {
                        "title": title,
                        "company": company,
                        "url": url,
                        "location": location,
                        "tags": tags,
                        "is_remote": True,  # Assuming all jobs from JobsFromSpace are remote
                        "website_id": website.id,
                        "posted_date": datetime.now(),
                    }
                    
                    jobs.append(job_data)
                except Exception as e:
                    logger.error(f"Error parsing job from JobsFromSpace: {e}")
            
            logger.info(f"Found {len(jobs)} jobs on JobsFromSpace")
            return jobs
            
        except Exception as e:
            logger.error(f"Error crawling JobsFromSpace: {e}")
            return []
    
    async def _crawl_custom_website(self, website: Website) -> List[Job]:
        """
        Extracts job listings from custom websites using defined selectors
        """
        if not website.selectors or len(website.selectors) == 0:
            logger.error(f"No selectors defined for custom website: {website.name}")
            return []
        
        jobs = []
        try:
            response = self.session.get(website.url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Use defined selectors
            job_container_selector = next((s for s in website.selectors if s.name == "job_container"), None)
            title_selector = next((s for s in website.selectors if s.name == "title"), None)
            company_selector = next((s for s in website.selectors if s.name == "company"), None)
            url_selector = next((s for s in website.selectors if s.name == "url"), None)
            location_selector = next((s for s in website.selectors if s.name == "location"), None)
            
            if not job_container_selector or not title_selector:
                logger.error(f"Missing required selectors for {website.name}")
                return []
            
            # Check selector type and process
            if job_container_selector.selector_type == "css":
                job_elements = soup.select(job_container_selector.value)
            else:  # xpath
                # Beautiful Soup XPath desteklemez, bu nedenle lxml kullanmak gerekir
                # Bu basit implementasyonda sadece CSS selektörlerini destekliyoruz
                logger.error("XPath selectors are not supported in this implementation")
                return []
            
            for job_element in job_elements:
                try:
                    # Extract data using selectors
                    title = self._extract_with_selector(job_element, title_selector)
                    company = self._extract_with_selector(job_element, company_selector) if company_selector else "Unknown"
                    
                    # Extract URL
                    url = ""
                    if url_selector:
                        url_elem = self._select_element(job_element, url_selector)
                        if url_elem and hasattr(url_elem, 'get'):
                            url = url_elem.get('href', '')
                    
                    # Convert URL to full URL
                    if url and not url.startswith(('http://', 'https://')):
                        from urllib.parse import urljoin
                        url = urljoin(str(website.url), url)
                    
                    # Extract location
                    location = self._extract_with_selector(job_element, location_selector) if location_selector else None
                    
                    if title and url:
                        job_data = {
                            "title": title,
                            "company": company,
                            "url": url,
                            "location": location,
                            "is_remote": True,  # Default to remote
                            "website_id": website.id,
                            "posted_date": datetime.now(),  # Default to current date
                        }
                        
                        jobs.append(job_data)
                except Exception as e:
                    logger.error(f"Error parsing job from custom website {website.name}: {e}")
            
            logger.info(f"Found {len(jobs)} jobs on {website.name}")
            return jobs
            
        except Exception as e:
            logger.error(f"Error crawling custom website {website.name}: {e}")
            return []
    
    def _select_element(self, parent, selector: SelectorBase):
        """
        Selects element based on given selector information
        """
        if selector.selector_type == "css":
            return parent.select_one(selector.value)
        else:
            logger.error("XPath selectors are not supported")
            return None
    
    def _extract_with_selector(self, parent, selector: SelectorBase) -> str:
        """
        Extracts content based on given selector information
        """
        element = self._select_element(parent, selector)
        if not element:
            return ""
        
        if selector.attribute:
            return element.get(selector.attribute, "").strip()
        else:
            return element.text.strip()
    
    def filter_jobs_by_keywords(self, jobs: List[Dict[str, Any]], keywords: List[str], exclude_keywords: List[str]) -> List[Dict[str, Any]]:
        """
        Filters job listings based on keywords
        """
        if not keywords and not exclude_keywords:
            return jobs
        
        filtered_jobs = []
        for job in jobs:
            # Combine all text
            job_text = f"{job.get('title', '')} {job.get('company', '')} {job.get('description', '')}"
            job_text = job_text.lower()
            
            # Include keyword check
            include_match = True
            if keywords:
                include_match = any(keyword.lower() in job_text for keyword in keywords)
            
            # Exclude keyword check
            exclude_match = False
            if exclude_keywords:
                exclude_match = any(keyword.lower() in job_text for keyword in exclude_keywords)
            
            # Filtering criteria
            if include_match and not exclude_match:
                filtered_jobs.append(job)
        
        return filtered_jobs
    
    async def get_job_details(self, job_url: str) -> Dict[str, Any]:
        """
        Extracts job details from the given job URL
        """
        try:
            response = self.session.get(job_url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Job details are usually specific to the page structure,
            # for a simple example, let's extract the main content area
            job_description = soup.select_one('main') or soup.select_one('.job-description') or soup.select_one('.description')
            
            if job_description:
                description = job_description.get_text(strip=True)
            else:
                description = ""
            
            # Extract salary if available (simple example with regex)
            salary_pattern = r'\$\d+[kK][-–]\$\d+[kK]|\$\d+[kK][-–]\d+[kK]|\$\d+,\d+[-–]\$\d+,\d+|\$\d+[-–]\$\d+|\d+[kK][-–]\d+[kK]'
            salary_matches = re.findall(salary_pattern, response.text)
            salary = salary_matches[0] if salary_matches else None
            
            return {
                "description": description,
                "salary": salary,
                "raw_data": str(soup)
            }
            
        except Exception as e:
            logger.error(f"Error fetching job details for {job_url}: {e}")
            return {
                "description": "",
                "salary": None,
                "raw_data": None
            }
    
    async def _crawl_remotive(self, website: Website) -> List[Job]:
        """
        Extracts job listings from Remotive.io
        """
        from .remotive_parser import RemotiveParser
        
        jobs = []
        try:
            # Initialize parser
            parser = RemotiveParser()
            logger.info(f"Using Remotive API to get jobs from {website.url}")
            
            # Use API to get jobs
            raw_jobs = parser.get_jobs_from_api(limit=100)
            
            for job in raw_jobs:
                try:
                    # Map API response to our Job model
                    job_data = {
                        "title": job.get("title", ""),
                        "company": job.get("company_name", "Unknown"),
                        "url": job.get("url", ""),
                        "description": job.get("description", ""),
                        "location": job.get("candidate_required_location", "Remote"),
                        "tags": job.get("tags", []),
                        "is_remote": True,  # Remotive is all remote jobs
                        "website_id": website.id,
                        "salary": job.get("salary", ""),
                        "posted_date": datetime.fromisoformat(job.get("publication_date", datetime.now().isoformat())),
                        "raw_data": job
                    }
                    
                    jobs.append(job_data)
                except Exception as e:
                    logger.error(f"Error parsing Remotive job: {e}")
                    continue
            
            logger.info(f"Found {len(jobs)} Remotive jobs")
            return jobs
        except Exception as e:
            logger.error(f"Error crawling Remotive: {e}")
            return [] 