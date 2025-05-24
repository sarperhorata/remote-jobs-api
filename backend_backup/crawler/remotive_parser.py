import requests
import logging
from bs4 import BeautifulSoup
from typing import List, Dict, Optional, Any
from datetime import datetime
import time
import re

# Configure logger
logger = logging.getLogger(__name__)

class RemotiveParser:
    """Parser for Remotive.io job listings"""
    
    def __init__(self):
        """Initialize the parser with necessary URLs and create a session"""
        self.base_url = "https://remotive.io"
        self.api_url = "https://remotive.io/api/remote-jobs"
        self.session = requests.Session()
        # Set user agent to avoid being blocked
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
    
    def get_job_categories(self) -> List[str]:
        """Get list of job categories from Remotive"""
        try:
            logger.info("Fetching job categories from Remotive")
            response = self.session.get(f"{self.base_url}/remote-jobs")
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            categories = []
            
            # Find category elements in the page
            category_elements = soup.select('.job-category')
            for element in category_elements:
                category_text = element.text.strip()
                if category_text:
                    categories.append(category_text)
            
            logger.info(f"Found {len(categories)} job categories")
            return categories
        except Exception as e:
            logger.error(f"Error getting job categories: {e}")
            return []
    
    def get_jobs_from_api(self, category: Optional[str] = None, limit: int = 50) -> List[Dict[str, Any]]:
        """Get jobs from Remotive API"""
        try:
            url = self.api_url
            if category:
                url = f"{url}/category/{category}"
            
            logger.info(f"Fetching jobs from Remotive API: {url}")
            response = self.session.get(url)
            response.raise_for_status()
            
            data = response.json()
            jobs = data.get('jobs', [])
            
            # Validate and clean job data
            validated_jobs = []
            for job in jobs:
                if not job.get('title') or not job.get('company_name'):
                    logger.warning(f"Skipping job without required fields: {job.get('id')}")
                    continue
                    
                # Ensure all required fields exist
                job['title'] = job.get('title', '').strip()
                job['company_name'] = job.get('company_name', 'Unknown').strip()
                job['url'] = job.get('url', '').strip()
                if not job['url']:
                    job['url'] = f"{self.base_url}/remote-jobs/{job.get('id', '')}"
                
                validated_jobs.append(job)
            
            # Limit the number of jobs if specified
            if limit and limit < len(validated_jobs):
                validated_jobs = validated_jobs[:limit]
            
            logger.info(f"Found {len(validated_jobs)} valid jobs from Remotive API")
            return validated_jobs
        except Exception as e:
            logger.error(f"Error getting jobs from API: {e}")
            return []
            
    def get_jobs_from_page(self, page: int = 1, limit: int = 20) -> List[Dict[str, Any]]:
        """Get jobs by scraping website pages"""
        try:
            url = f"{self.base_url}/remote-jobs?page={page}"
            logger.info(f"Fetching jobs from page: {url}")
            
            response = self.session.get(url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            job_elements = soup.select('.job-list-item')
            
            jobs = []
            for job_element in job_elements[:limit]:
                try:
                    # Extract basic job information
                    title_element = job_element.select_one('.position')
                    company_element = job_element.select_one('.company')
                    link_element = job_element.select_one('a')
                    tags_elements = job_element.select('.job-tag')
                    
                    if not title_element or not company_element or not link_element:
                        continue
                        
                    job_url = f"{self.base_url}{link_element['href']}" if link_element['href'].startswith('/') else link_element['href']
                    
                    # Extract job ID from URL
                    job_id_match = re.search(r'/remote-jobs/(\d+)', job_url)
                    job_id = job_id_match.group(1) if job_id_match else None
                    
                    # Build job object
                    job = {
                        'id': job_id,
                        'title': title_element.text.strip(),
                        'company_name': company_element.text.strip(),
                        'url': job_url,
                        'tags': [tag.text.strip() for tag in tags_elements],
                        'source': 'remotive',
                        'date_posted': datetime.now().strftime('%Y-%m-%d'),
                    }
                    
                    jobs.append(job)
                except Exception as e:
                    logger.error(f"Error parsing job element: {e}")
                    continue
            
            logger.info(f"Found {len(jobs)} jobs from page {page}")
            return jobs
        except Exception as e:
            logger.error(f"Error getting jobs from page: {e}")
            return []
    
    def get_job_details(self, job_id: str) -> Dict[str, Any]:
        """Get detailed information for a specific job"""
        try:
            url = f"{self.base_url}/remote-jobs/{job_id}"
            logger.info(f"Fetching job details from: {url}")
            
            response = self.session.get(url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract job details
            title_element = soup.select_one('h1.job-details-title')
            company_element = soup.select_one('.job-details-company-name')
            description_element = soup.select_one('.job-description')
            apply_url_element = soup.select_one('.job-details-apply-button-top')
            
            if not title_element or not description_element:
                logger.warning(f"Missing critical elements for job {job_id}")
                return {}
            
            # Build detailed job object
            job_details = {
                'id': job_id,
                'title': title_element.text.strip(),
                'company_name': company_element.text.strip() if company_element else "Unknown",
                'description': description_element.get_text('\n').strip(),
                'apply_url': apply_url_element['href'] if apply_url_element and 'href' in apply_url_element.attrs else None,
                'source': 'remotive',
                'url': url,
                'date_retrieved': datetime.now().strftime('%Y-%m-%d'),
            }
            
            return job_details
        except Exception as e:
            logger.error(f"Error getting job details for job {job_id}: {e}")
            return {}
    
    def search_jobs(self, keyword: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Search for jobs with the given keyword"""
        try:
            url = f"{self.api_url}?search={keyword}"
            logger.info(f"Searching jobs with keyword '{keyword}' from: {url}")
            
            response = self.session.get(url)
            response.raise_for_status()
            
            data = response.json()
            jobs = data.get('jobs', [])
            
            # Process and filter jobs
            filtered_jobs = []
            for job in jobs[:limit]:
                if not job.get('title') or not job.get('company_name'):
                    continue
                
                # Add source information
                job['source'] = 'remotive'
                filtered_jobs.append(job)
            
            logger.info(f"Found {len(filtered_jobs)} jobs matching keyword '{keyword}'")
            return filtered_jobs
        except Exception as e:
            logger.error(f"Error searching jobs with keyword '{keyword}': {e}")
            return []
    
    def get_companies(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get list of companies that post jobs on Remotive"""
        try:
            url = f"{self.base_url}/remote-companies"
            logger.info(f"Fetching companies from: {url}")
            
            response = self.session.get(url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            company_elements = soup.select('.company-card')
            
            companies = []
            for company_element in company_elements[:limit]:
                try:
                    name_element = company_element.select_one('.company-name')
                    link_element = company_element.select_one('a')
                    
                    if not name_element or not link_element:
                        continue
                    
                    company_url = f"{self.base_url}{link_element['href']}" if link_element['href'].startswith('/') else link_element['href']
                    
                    company = {
                        'name': name_element.text.strip(),
                        'url': company_url,
                    }
                    
                    companies.append(company)
                except Exception as e:
                    logger.error(f"Error parsing company element: {e}")
                    continue
            
            logger.info(f"Found {len(companies)} companies")
            return companies
        except Exception as e:
            logger.error(f"Error getting companies: {e}")
            return []