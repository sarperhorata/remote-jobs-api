import requests
from bs4 import BeautifulSoup
import json
import re
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
import os

# Logger setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class JobsFromSpaceParser:
    """
    Parser for the JobsFromSpace website to extract job listings and analyze site structure.
    """
    
    def __init__(self, base_url="https://www.jobsfromspace.com"):
        self.base_url = base_url
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
    
    def analyze_site(self):
        """Analyze the site structure to identify API endpoints and data sources"""
        try:
            logger.info(f"Analyzing {self.base_url}...")
            response = self.session.get(self.base_url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Look for script tags that might contain data
            scripts = soup.find_all('script')
            api_endpoints = []
            data_objects = []
            
            for script in scripts:
                # Look for API endpoints
                if script.string:
                    api_matches = re.findall(r'https?://[^"\'\s]+api[^"\'\s]*', script.string)
                    if api_matches:
                        api_endpoints.extend(api_matches)
                    
                    # Look for data objects
                    data_matches = re.findall(r'window\.[A-Za-z0-9_]+ = ({.+?});', script.string, re.DOTALL)
                    if data_matches:
                        data_objects.extend(data_matches)
            
            # Look for links to job listings
            job_links = []
            for a in soup.find_all('a', href=True):
                if '/job/' in a['href'] or '/jobs/' in a['href']:
                    job_links.append(a['href'])
            
            return {
                'api_endpoints': api_endpoints,
                'data_objects': data_objects,
                'job_links': job_links[:10],  # Limit to first 10 for analysis
                'structure': {
                    'title': soup.title.string if soup.title else None,
                    'meta_description': soup.find('meta', {'name': 'description'})['content'] if soup.find('meta', {'name': 'description'}) else None,
                }
            }
        except Exception as e:
            logger.error(f"Error analyzing site: {e}")
            return None
    
    def get_company_list(self):
        """Extract the list of companies that have job listings on the site"""
        try:
            logger.info(f"Getting company list from {self.base_url}...")
            response = self.session.get(f"{self.base_url}/companies")
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            companies = []
            
            # Look for company cards or listings
            company_elements = soup.select('.company-card, .company-listing, .company-item')
            
            if not company_elements:
                # Try alternative selectors if specific ones don't work
                company_elements = soup.find_all('div', class_=lambda c: c and ('company' in c.lower() or 'employer' in c.lower()))
            
            for company in company_elements:
                company_name = company.find('h3') or company.find('h2') or company.find('h4')
                company_link = company.find('a', href=True)
                
                if company_name and company_link:
                    companies.append({
                        'name': company_name.text.strip(),
                        'url': company_link['href'] if company_link['href'].startswith('http') else f"{self.base_url}{company_link['href']}"
                    })
            
            return companies
        except Exception as e:
            logger.error(f"Error getting company list: {e}")
            return []
    
    def get_jobs(self, max_pages=1):
        """Extract job listings from the site"""
        all_jobs = []
        
        try:
            for page in range(1, max_pages + 1):
                logger.info(f"Getting jobs from page {page}...")
                
                url = f"{self.base_url}/jobs"
                if page > 1:
                    url = f"{url}?page={page}"
                
                response = self.session.get(url)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Look for job cards or listings
                job_elements = soup.select('.job-card, .job-listing, .job-item, .list-item')
                
                if not job_elements:
                    # Try alternative selectors if specific ones don't work
                    job_elements = soup.find_all('div', class_=lambda c: c and ('job' in c.lower() or 'listing' in c.lower()))
                
                for job in job_elements:
                    try:
                        # Extract job details
                        title_elem = job.find('h2') or job.find('h3') or job.find('h4')
                        company_elem = job.find(class_=lambda c: c and ('company' in c.lower()))
                        link_elem = job.find('a', href=True)
                        
                        if not title_elem or not link_elem:
                            continue
                        
                        title = title_elem.text.strip()
                        company = company_elem.text.strip() if company_elem else "Unknown"
                        url = link_elem['href'] if link_elem['href'].startswith('http') else f"{self.base_url}{link_elem['href']}"
                        
                        # Extract additional details if available
                        location = None
                        location_elem = job.find(class_=lambda c: c and ('location' in c.lower()))
                        if location_elem:
                            location = location_elem.text.strip()
                        
                        tags = []
                        tags_elem = job.find('div', class_=lambda c: c and ('tags' in c.lower() or 'skills' in c.lower()))
                        if tags_elem:
                            tag_items = tags_elem.find_all('span') or tags_elem.find_all('a')
                            tags = [tag.text.strip() for tag in tag_items]
                        
                        job_data = {
                            "title": title,
                            "company": company,
                            "url": url,
                            "location": location,
                            "tags": tags,
                            "is_remote": "remote" in title.lower() or "remote" in " ".join(tags).lower(),
                            "source": "JobsFromSpace",
                            "posted_date": datetime.now().isoformat(),
                        }
                        
                        all_jobs.append(job_data)
                    except Exception as e:
                        logger.error(f"Error parsing job: {e}")
                
                logger.info(f"Found {len(job_elements)} jobs on page {page}")
                
                # Check if there's a next page
                next_page = soup.find('a', string='Next') or soup.find('a', class_=lambda c: c and ('next' in c.lower()))
                if not next_page:
                    break
        
        except Exception as e:
            logger.error(f"Error getting jobs: {e}")
        
        return all_jobs
    
    def check_api_endpoints(self):
        """
        Look for potential API endpoints by checking common paths
        """
        common_endpoints = [
            '/api/jobs',
            '/api/jobs/search',
            '/api/companies',
            '/graphql',
            '/jobs/data.json',
        ]
        
        working_endpoints = []
        
        for endpoint in common_endpoints:
            try:
                url = f"{self.base_url}{endpoint}"
                response = self.session.get(url)
                
                if response.status_code == 200:
                    try:
                        data = response.json()
                        working_endpoints.append({
                            'url': url,
                            'status': response.status_code,
                            'content_type': response.headers.get('Content-Type', ''),
                            'sample_data': str(data)[:500] + '...' if len(str(data)) > 500 else str(data)
                        })
                    except:
                        working_endpoints.append({
                            'url': url,
                            'status': response.status_code,
                            'content_type': response.headers.get('Content-Type', ''),
                            'sample_data': response.text[:500] + '...' if len(response.text) > 500 else response.text
                        })
            except Exception as e:
                logger.error(f"Error checking endpoint {endpoint}: {e}")
        
        return working_endpoints

# Run analysis if executed directly
if __name__ == "__main__":
    parser = JobsFromSpaceParser()
    
    # Analyze site structure
    site_analysis = parser.analyze_site()
    print("\n=== Site Analysis ===")
    print(f"Title: {site_analysis['structure']['title']}")
    print(f"Description: {site_analysis['structure']['meta_description']}")
    print(f"API Endpoints: {site_analysis['api_endpoints']}")
    print(f"Example Job Links: {site_analysis['job_links'][:5]}")
    
    # Check for API endpoints
    print("\n=== Checking API Endpoints ===")
    api_endpoints = parser.check_api_endpoints()
    for endpoint in api_endpoints:
        print(f"Endpoint: {endpoint['url']}")
        print(f"Status: {endpoint['status']}")
        print(f"Content Type: {endpoint['content_type']}")
        print(f"Sample Data: {endpoint['sample_data'][:200]}...")
    
    # Get company list
    companies = parser.get_company_list()
    print(f"\n=== Found {len(companies)} Companies ===")
    for i, company in enumerate(companies[:10]):
        print(f"{i+1}. {company['name']} - {company['url']}")
    
    # Get jobs
    jobs = parser.get_jobs(max_pages=1)
    print(f"\n=== Found {len(jobs)} Jobs ===")
    for i, job in enumerate(jobs[:10]):
        print(f"{i+1}. {job['title']} at {job['company']} - {job['url']}")
    
    # Save results
    os.makedirs('data', exist_ok=True)
    
    with open('data/jobsfromspace_analysis.json', 'w') as f:
        json.dump(site_analysis, f, indent=2)
    
    with open('data/jobsfromspace_companies.json', 'w') as f:
        json.dump(companies, f, indent=2)
    
    with open('data/jobsfromspace_jobs.json', 'w') as f:
        json.dump(jobs, f, indent=2) 