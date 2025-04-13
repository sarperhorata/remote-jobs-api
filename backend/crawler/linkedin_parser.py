import requests
import logging
from bs4 import BeautifulSoup
from typing import List, Dict, Optional, Any
from datetime import datetime
import time
import re
import json

# Configure logger
logger = logging.getLogger(__name__)

class LinkedInParser:
    """Parser for LinkedIn job listings"""
    
    def __init__(self):
        """Initialize the parser with necessary URLs and create a session"""
        self.base_url = "https://www.linkedin.com"
        self.jobs_url = "https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings"
        self.session = requests.Session()
        # Set user agent to avoid being blocked
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Referer': 'https://www.linkedin.com/jobs',
        })
    
    def get_jobs(self, keywords: str = "remote", location: str = "", start: int = 0, limit: int = 25) -> List[Dict[str, Any]]:
        """Get jobs based on keywords and location"""
        try:
            params = {
                'keywords': keywords,
                'location': location,
                'start': start,
                'count': min(limit, 100)  # LinkedIn typically limits to 100 per request
            }
            
            logger.info(f"Fetching LinkedIn jobs with params: {params}")
            response = self.session.get(self.jobs_url, params=params)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            job_cards = soup.select('.job-search-card')
            
            jobs = []
            for job_card in job_cards:
                try:
                    # Extract job details from card
                    job_id_elem = job_card.get('data-id') or job_card.get('data-job-id')
                    title_elem = job_card.select_one('.base-search-card__title')
                    company_elem = job_card.select_one('.base-search-card__subtitle')
                    location_elem = job_card.select_one('.job-search-card__location')
                    link_elem = job_card.select_one('a.base-card__full-link')
                    date_elem = job_card.select_one('time.job-search-card__listdate')
                    
                    # Skip if missing critical elements
                    if not title_elem or not company_elem or not link_elem:
                        continue
                    
                    job_url = link_elem['href'] if link_elem and 'href' in link_elem.attrs else None
                    
                    # Extract job ID from URL if not available directly
                    if not job_id_elem and job_url:
                        job_id_match = re.search(r'/jobs/view/(\d+)', job_url)
                        job_id_elem = job_id_match.group(1) if job_id_match else None
                    
                    # Parse posted date
                    posted_date = None
                    if date_elem and 'datetime' in date_elem.attrs:
                        posted_date = date_elem['datetime']
                    else:
                        posted_date = datetime.now().strftime('%Y-%m-%d')
                    
                    # Build job object
                    job = {
                        'id': job_id_elem,
                        'title': title_elem.text.strip(),
                        'company_name': company_elem.text.strip(),
                        'location': location_elem.text.strip() if location_elem else "Unknown",
                        'url': job_url,
                        'date_posted': posted_date,
                        'source': 'linkedin',
                    }
                    
                    jobs.append(job)
                except Exception as e:
                    logger.error(f"Error parsing LinkedIn job card: {e}")
                    continue
            
            logger.info(f"Found {len(jobs)} jobs from LinkedIn")
            return jobs
        except Exception as e:
            logger.error(f"Error getting LinkedIn jobs: {e}")
            return []
    
    def get_job_details(self, job_id: str) -> Dict[str, Any]:
        """Get detailed information for a specific job"""
        try:
            url = f"{self.base_url}/jobs/view/{job_id}"
            logger.info(f"Fetching LinkedIn job details from: {url}")
            
            response = self.session.get(url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract job details
            title_elem = soup.select_one('.top-card-layout__title')
            company_elem = soup.select_one('.topcard__org-name-link')
            location_elem = soup.select_one('.topcard__flavor--bullet')
            description_elem = soup.select_one('.description__text')
            
            if not title_elem or not description_elem:
                logger.warning(f"Missing critical elements for LinkedIn job {job_id}")
                return {}
            
            # Extract JSON-LD data if available (contains structured job data)
            json_ld = None
            script_tags = soup.select('script[type="application/ld+json"]')
            for script in script_tags:
                try:
                    data = json.loads(script.string)
                    if data.get('@type') == 'JobPosting':
                        json_ld = data
                        break
                except:
                    pass
            
            # Build detailed job object
            job_details = {
                'id': job_id,
                'title': title_elem.text.strip(),
                'company_name': company_elem.text.strip() if company_elem else "Unknown",
                'location': location_elem.text.strip() if location_elem else "Unknown",
                'description': description_elem.get_text('\n').strip() if description_elem else "",
                'url': url,
                'source': 'linkedin',
                'date_retrieved': datetime.now().strftime('%Y-%m-%d'),
            }
            
            # Add additional details from JSON-LD if available
            if json_ld:
                job_details.update({
                    'date_posted': json_ld.get('datePosted', job_details.get('date_retrieved')),
                    'valid_through': json_ld.get('validThrough'),
                    'employment_type': json_ld.get('employmentType'),
                    'industry': json_ld.get('industry'),
                    'salary': json_ld.get('baseSalary')
                })
            
            return job_details
        except Exception as e:
            logger.error(f"Error getting LinkedIn job details for job {job_id}: {e}")
            return {}
    
    def search_jobs(self, keyword: str, location: str = "", limit: int = 50) -> List[Dict[str, Any]]:
        """Search for jobs with the given keyword and location"""
        # For LinkedIn, search is functionally the same as get_jobs
        return self.get_jobs(keywords=keyword, location=location, limit=limit)
    
    def get_job_categories(self) -> List[str]:
        """Get list of job categories from LinkedIn"""
        try:
            url = f"{self.base_url}/jobs"
            logger.info(f"Fetching job categories from LinkedIn")
            
            response = self.session.get(url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            category_elements = soup.select('.jobs-search-box__category-card')
            
            categories = []
            for element in category_elements:
                category_text = element.text.strip()
                if category_text:
                    categories.append(category_text)
            
            logger.info(f"Found {len(categories)} job categories on LinkedIn")
            return categories
        except Exception as e:
            logger.error(f"Error getting LinkedIn job categories: {e}")
            return []
    
    def paginate_jobs(self, keywords: str = "remote", location: str = "", total_count: int = 100) -> List[Dict[str, Any]]:
        """Paginate through job listings to get a larger number"""
        all_jobs = []
        start = 0
        page_size = 25  # LinkedIn typically uses 25 per page
        
        while len(all_jobs) < total_count:
            jobs = self.get_jobs(keywords=keywords, location=location, start=start, limit=page_size)
            
            # Break if no more jobs found
            if not jobs:
                break
                
            all_jobs.extend(jobs)
            start += len(jobs)
            
            # Respect rate limits
            time.sleep(2)
            
            # Break if we got fewer jobs than requested (last page)
            if len(jobs) < page_size:
                break
        
        logger.info(f"Collected a total of {len(all_jobs)} LinkedIn jobs")
        return all_jobs[:total_count] 