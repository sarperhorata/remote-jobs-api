#!/usr/bin/env python3

import sys
import os
import json
import asyncio
import aiohttp
import time
import logging
from datetime import datetime
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
import re
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

# Import from current backend directory
from backend.database import get_db

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class JobListing:
    title: str
    company: str
    location: str
    description: str
    apply_url: str
    source_url: str
    external_id: str
    posted_date: Optional[datetime] = None
    job_type: str = "Full-time"
    salary: Optional[str] = None
    requirements: List[str] = None
    skills: List[str] = None
    remote_type: str = "remote"

class DistillCrawler:
    def __init__(self):
        self.session = None
        self.companies_data = []
        self.crawled_jobs = []
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        
    def load_companies_data(self):
        """Load companies data from distill export"""
        try:
            # Get the project root directory (parent of backend)
            project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            distill_file_path = os.path.join(project_root, 'distill-export', 'Distill export - 01-18_2025-05-25.json')
            
            with open(distill_file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self.companies_data = data['data']
            logger.info(f"✅ Loaded {len(self.companies_data)} companies from distill export")
            
            # Remove duplicates
            unique_companies = {}
            for company in self.companies_data:
                uri = company.get('uri')
                if uri not in unique_companies:
                    unique_companies[uri] = company
                else:
                    logger.warning(f"🔄 Skipping duplicate: {company.get('name')} - {uri}")
            
            self.companies_data = list(unique_companies.values())
            logger.info(f"✅ After removing duplicates: {len(self.companies_data)} unique companies")
            
        except Exception as e:
            logger.error(f"❌ Error loading companies data: {str(e)}")
            raise
    
    async def crawl_company(self, company_data: Dict) -> List[JobListing]:
        """Crawl a single company using distill configuration"""
        jobs = []
        
        try:
            company_name = company_data.get('name', 'Unknown Company')
            uri = company_data.get('uri', '')
            config = company_data.get('config', {})
            
            if not uri:
                logger.warning(f"⚠️ No URI found for company: {company_name}")
                return []  # Return empty instead of raising exception
            
            logger.info(f"🔍 Crawling {company_name} at {uri}")
            
            # Parse distill config
            selectors_config = config.get('selectors', [])
            
            if self._is_job_platform(uri):
                jobs = await self._crawl_job_platform(company_name, uri, config)
            else:
                jobs = await self._crawl_custom_site(company_name, uri, config)
            
            logger.info(f"✅ Found {len(jobs)} jobs for {company_name}")
            return jobs
            
        except asyncio.TimeoutError:
            logger.warning(f"⏰ Timeout crawling {company_name} ({uri}) - skipping")
            return []  # Return empty instead of raising exception
            
        except aiohttp.ClientError as e:
            logger.warning(f"🌐 Network error for {company_name} ({uri}): {str(e)} - skipping")
            return []  # Return empty instead of raising exception
            
        except Exception as e:
            logger.warning(f"⚠️ Error crawling {company_name} ({uri}): {str(e)} - skipping")
            return []  # Return empty instead of raising exception
    
    def _is_job_platform(self, uri: str) -> bool:
        """Check if URI is a known job platform"""
        job_platforms = [
            'jobs.lever.co', 'greenhouse.io', 'workable.com', 'breezy.hr',
            'smartrecruiters.com', 'ashbyhq.com', 'freshteam.com'
        ]
        
        return any(platform in uri for platform in job_platforms)
    
    async def _crawl_job_platform(self, company_name: str, uri: str, config: Dict) -> List[JobListing]:
        """Crawl known job platforms with optimized selectors"""
        jobs = []
        
        try:
            async with self.session.get(uri, timeout=30) as response:
                if response.status != 200:
                    logger.warning(f"⚠️ HTTP {response.status} for {company_name}")
                    return jobs
                
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')
                
                # Platform-specific job extraction
                if 'lever.co' in uri:
                    jobs = self._extract_lever_jobs(company_name, uri, soup)
                elif 'greenhouse.io' in uri:
                    jobs = self._extract_greenhouse_jobs(company_name, uri, soup)
                elif 'workable.com' in uri:
                    jobs = self._extract_workable_jobs(company_name, uri, soup)
                elif 'breezy.hr' in uri:
                    jobs = self._extract_breezy_jobs(company_name, uri, soup)
                elif 'smartrecruiters.com' in uri:
                    jobs = self._extract_smartrecruiters_jobs(company_name, uri, soup)
                elif 'ashbyhq.com' in uri:
                    jobs = self._extract_ashby_jobs(company_name, uri, soup)
                elif 'freshteam.com' in uri:
                    jobs = self._extract_freshteam_jobs(company_name, uri, soup)
                
        except Exception as e:
            logger.error(f"❌ Error crawling job platform {company_name}: {str(e)}")
        
        return jobs
    
    async def _crawl_custom_site(self, company_name: str, uri: str, config: Dict) -> List[JobListing]:
        """Crawl custom company sites using distill selectors"""
        jobs = []
        
        try:
            # Extract selectors from distill config
            selections = config.get('selections', [])
            if not selections:
                logger.warning(f"⚠️ No selectors configured for {company_name}")
                return jobs
            
            async with self.session.get(uri, timeout=30) as response:
                if response.status != 200:
                    logger.warning(f"⚠️ HTTP {response.status} for {company_name}")
                    return jobs
                
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')
                
                # Process each selection from distill config
                for selection in selections:
                    frames = selection.get('frames', [])
                    for frame in frames:
                        includes = frame.get('includes', [])
                        for include in includes:
                            # Check if it's CSS or XPath
                            selector_type = include.get('type', 'xpath')
                            expr = include.get('expr')
                            
                            if not expr:
                                continue
                                
                            try:
                                if selector_type == 'css':
                                    # Direct CSS selector - use as is
                                    container_elements = soup.select(expr)
                                    logger.debug(f"✅ CSS selector '{expr}' found {len(container_elements)} container elements")
                                    
                                    # Check if we found containers or individual jobs
                                    job_elements = []
                                    for container in container_elements:
                                        # Look for individual job elements within the container
                                        individual_jobs = self._find_individual_jobs_in_container(container)
                                        if individual_jobs:
                                            job_elements.extend(individual_jobs)
                                            logger.debug(f"✅ Found {len(individual_jobs)} individual jobs in container")
                                        else:
                                            # If no individual jobs found, treat container as single job
                                            job_elements.append(container)
                                else:
                                    # XPath - convert to CSS
                                    css_selector = self._xpath_to_css(expr)
                                    if css_selector:
                                        try:
                                            job_elements = soup.select(css_selector)
                                            logger.debug(f"✅ XPath->CSS '{css_selector}' found {len(job_elements)} elements")
                                        except Exception as css_error:
                                            logger.debug(f"❌ CSS selector '{css_selector}' failed: {css_error}")
                                            job_elements = []
                                    else:
                                        # Fallback to generic selectors when XPath conversion fails
                                        logger.debug(f"⚠️ XPath conversion failed for '{expr}', using fallback")
                                        try:
                                            fallback_selector = self._get_fallback_selectors()
                                            job_elements = soup.select(fallback_selector)
                                            logger.debug(f"✅ Fallback selectors found {len(job_elements)} elements")
                                        except Exception as fallback_error:
                                            logger.debug(f"❌ Fallback selectors also failed: {fallback_error}")
                                            job_elements = []
                                
                                # Extract jobs from found elements
                                for element in job_elements:
                                    job = self._extract_job_from_element(company_name, uri, element)
                                    if job:
                                        jobs.append(job)
                                        
                            except Exception as e:
                                logger.debug(f"❌ Selector error for {company_name}: {str(e)} - skipping")
                                # Try fallback approach
                                try:
                                    fallback_elements = soup.select(self._get_fallback_selectors())
                                    for element in fallback_elements:
                                        job = self._extract_job_from_element(company_name, uri, element)
                                        if job:
                                            jobs.append(job)
                                except Exception as fallback_error:
                                    logger.debug(f"❌ Fallback also failed: {fallback_error} - skipping")
                
        except Exception as e:
            logger.error(f"❌ Error crawling custom site {company_name}: {str(e)}")
        
        return jobs
    
    def _xpath_to_css(self, xpath: str) -> Optional[str]:
        """Enhanced XPath to CSS selector conversion with better error handling"""
        try:
            # Clean the xpath first
            xpath = xpath.strip()
            
            # Handle empty or invalid xpath
            if not xpath or xpath in ['', '//', '/', '.']:
                logger.debug(f"Empty or invalid XPath: '{xpath}'")
                return None
            
            # Problematic patterns that can't be easily converted
            problematic_patterns = [
                r'contains\s*\(',           # contains() functions
                r'text\s*\(\)',             # text() functions  
                r'position\s*\(\)',         # position() functions
                r'last\s*\(\)',             # last() functions
                r'@\w+\s*=\s*[\'"][^\'"]*[\'"]',  # attribute equals with quotes
                r'\[\s*\d+\s*\]',           # numeric index selectors
                r'\|\|',                    # OR operators
                r'ancestor:',               # ancestor axis
                r'following:',              # following axis
                r'preceding:',              # preceding axis
            ]
            
            # If XPath contains problematic patterns, use fallback
            for pattern in problematic_patterns:
                if re.search(pattern, xpath, re.IGNORECASE):
                    logger.debug(f"Complex XPath pattern detected: {pattern} in {xpath}")
                    return None
            
            # Start conversion
            css = xpath
            
            # Remove leading // and /
            css = re.sub(r'^/+', '', css)
            
            # Convert descendant selectors
            css = re.sub(r'//', ' ', css)
            css = re.sub(r'/', ' > ', css)
            
            # Convert simple attribute selectors
            css = re.sub(r'\[@([^=\]]+)=([\'"])([^\]]*)\2\]', r'[\1="\3"]', css)
            css = re.sub(r'\[@([^=\]]+)\]', r'[\1]', css)
            
            # Remove problematic characters that would cause CSS errors
            css = re.sub(r'[\(\)]', '', css)  # Remove parentheses
            css = re.sub(r'\s+', ' ', css).strip()  # Clean whitespace
            
            # Validate the result doesn't start with combinators
            if css.startswith(('>', '+', '~', ' >')):
                logger.debug(f"CSS starts with combinator: {css}")
                return None
            
            # Basic validation - check for remaining problematic characters
            if any(char in css for char in ['(', ')', '[', ']']) and not re.match(r'^[\w\s\-\[\]="\.:>#\+~]+$', css):
                logger.debug(f"CSS contains problematic characters: {css}")
                return None
            
            return css if css and len(css) > 0 else None
            
        except Exception as e:
            logger.debug(f"XPath conversion failed for '{xpath}': {e}")
            return None
    
    def _get_fallback_selectors(self) -> str:
        """Return safe fallback CSS selectors with error handling"""
        # Return selectors that are guaranteed to work
        return "h1, h2, h3, h4, h5, a, div, p, span, li"
    
    def _extract_lever_jobs(self, company_name: str, uri: str, soup: BeautifulSoup) -> List[JobListing]:
        """Extract jobs from Lever platform"""
        jobs = []
        
        # Common Lever selectors
        job_elements = soup.select('.posting, .postings-group .posting, [data-qa="posting"]')
        
        for element in job_elements:
            try:
                title_elem = element.select_one('.posting-title, h5, .posting-name, [data-qa="posting-name"]')
                title = title_elem.get_text(strip=True) if title_elem else ''
                
                location_elem = element.select_one('.posting-categories .location, .location, [data-qa="posting-location"]')
                location = location_elem.get_text(strip=True) if location_elem else 'Remote'
                
                link_elem = element.select_one('a')
                apply_url = self._safe_get_href(link_elem, uri) if link_elem else uri
                
                if title:
                    job = JobListing(
                        title=title,
                        company=company_name,
                        location=location,
                        description='',
                        apply_url=apply_url,
                        source_url=uri,
                        external_id=f"lever_{hash(apply_url)}",
                        remote_type=self._determine_remote_type(location)
                    )
                    jobs.append(job)
                    
            except Exception as e:
                logger.debug(f"Error parsing Lever job element: {e}")
                continue
        
        return jobs
    
    def _extract_greenhouse_jobs(self, company_name: str, uri: str, soup: BeautifulSoup) -> List[JobListing]:
        """Extract jobs from Greenhouse platform"""
        jobs = []
        
        job_elements = soup.select('.opening, .job, [data-mapped="job"]')
        
        for element in job_elements:
            try:
                title_elem = element.select_one('a, .opening-title, h3')
                title = title_elem.get_text(strip=True) if title_elem else ''
                
                location_elem = element.select_one('.location, [data-mapped="location"]')
                location = location_elem.get_text(strip=True) if location_elem else 'Remote'
                
                link_elem = element.select_one('a')
                apply_url = self._safe_get_href(link_elem, uri) if link_elem else uri
                
                if title:
                    job = JobListing(
                        title=title,
                        company=company_name,
                        location=location,
                        description='',
                        apply_url=apply_url,
                        source_url=uri,
                        external_id=f"greenhouse_{hash(apply_url)}",
                        remote_type=self._determine_remote_type(location)
                    )
                    jobs.append(job)
                    
            except Exception as e:
                logger.debug(f"Error parsing Greenhouse job element: {e}")
                continue
        
        return jobs
    
    def _extract_workable_jobs(self, company_name: str, uri: str, soup: BeautifulSoup) -> List[JobListing]:
        """Extract jobs from Workable platform"""
        jobs = []
        
        job_elements = soup.select('[data-ui="job"], .job-post, li[role="listitem"]')
        
        for element in job_elements:
            try:
                title_elem = element.select_one('h3, .job-title, [data-ui="job-title"]')
                title = title_elem.get_text(strip=True) if title_elem else ''
                
                location_elem = element.select_one('.location, [data-ui="job-location"]')
                location = location_elem.get_text(strip=True) if location_elem else 'Remote'
                
                link_elem = element.select_one('a')
                apply_url = self._safe_get_href(link_elem, uri) if link_elem else uri
                
                if title:
                    job = JobListing(
                        title=title,
                        company=company_name,
                        location=location,
                        description='',
                        apply_url=apply_url,
                        source_url=uri,
                        external_id=f"workable_{hash(apply_url)}",
                        remote_type=self._determine_remote_type(location)
                    )
                    jobs.append(job)
                    
            except Exception as e:
                logger.debug(f"Error parsing Workable job element: {e}")
                continue
        
        return jobs
    
    def _extract_breezy_jobs(self, company_name: str, uri: str, soup: BeautifulSoup) -> List[JobListing]:
        """Extract jobs from Breezy platform"""
        jobs = []
        
        job_elements = soup.select('.position, .job-listing, li.position')
        
        for element in job_elements:
            try:
                title_elem = element.select_one('h3, .position-title, .job-title')
                title = title_elem.get_text(strip=True) if title_elem else ''
                
                location_elem = element.select_one('.location, .position-location')
                location = location_elem.get_text(strip=True) if location_elem else 'Remote'
                
                link_elem = element.select_one('a')
                apply_url = self._safe_get_href(link_elem, uri) if link_elem else uri
                
                if title:
                    job = JobListing(
                        title=title,
                        company=company_name,
                        location=location,
                        description='',
                        apply_url=apply_url,
                        source_url=uri,
                        external_id=f"breezy_{hash(apply_url)}",
                        remote_type=self._determine_remote_type(location)
                    )
                    jobs.append(job)
                    
            except Exception as e:
                logger.debug(f"Error parsing Breezy job element: {e}")
                continue
        
        return jobs
    
    def _extract_smartrecruiters_jobs(self, company_name: str, uri: str, soup: BeautifulSoup) -> List[JobListing]:
        """Extract jobs from SmartRecruiters platform"""
        jobs = []
        
        job_elements = soup.select('.opening-job, .job-item, li[class*="opening"]')
        
        for element in job_elements:
            try:
                title_elem = element.select_one('h4, .job-title, .opening-job-title')
                title = title_elem.get_text(strip=True) if title_elem else ''
                
                location_elem = element.select_one('.job-location, .opening-job-location')
                location = location_elem.get_text(strip=True) if location_elem else 'Remote'
                
                link_elem = element.select_one('a')
                apply_url = self._safe_get_href(link_elem, uri) if link_elem else uri
                
                if title:
                    job = JobListing(
                        title=title,
                        company=company_name,
                        location=location,
                        description='',
                        apply_url=apply_url,
                        source_url=uri,
                        external_id=f"smartrecruiters_{hash(apply_url)}",
                        remote_type=self._determine_remote_type(location)
                    )
                    jobs.append(job)
                    
            except Exception as e:
                logger.debug(f"Error parsing SmartRecruiters job element: {e}")
                continue
        
        return jobs
    
    def _extract_ashby_jobs(self, company_name: str, uri: str, soup: BeautifulSoup) -> List[JobListing]:
        """Extract jobs from Ashby platform"""
        jobs = []
        
        job_elements = soup.select('[data-testid*="job"], .job-listing, .opening')
        
        for element in job_elements:
            try:
                title_elem = element.select_one('h3, .job-title, [data-testid*="title"]')
                title = title_elem.get_text(strip=True) if title_elem else ''
                
                location_elem = element.select_one('.location, [data-testid*="location"]')
                location = location_elem.get_text(strip=True) if location_elem else 'Remote'
                
                link_elem = element.select_one('a')
                apply_url = self._safe_get_href(link_elem, uri) if link_elem else uri
                
                if title:
                    job = JobListing(
                        title=title,
                        company=company_name,
                        location=location,
                        description='',
                        apply_url=apply_url,
                        source_url=uri,
                        external_id=f"ashby_{hash(apply_url)}",
                        remote_type=self._determine_remote_type(location)
                    )
                    jobs.append(job)
                    
            except Exception as e:
                logger.debug(f"Error parsing Ashby job element: {e}")
                continue
        
        return jobs
    
    def _extract_freshteam_jobs(self, company_name: str, uri: str, soup: BeautifulSoup) -> List[JobListing]:
        """Extract jobs from Freshteam platform"""
        jobs = []
        
        job_elements = soup.select('.job-list, .job-card, .job-item')
        
        for element in job_elements:
            try:
                title_elem = element.select_one('.heading, .job-title, h3')
                title = title_elem.get_text(strip=True) if title_elem else ''
                
                location_elem = element.select_one('.location, .job-location')
                location = location_elem.get_text(strip=True) if location_elem else 'Remote'
                
                link_elem = element.select_one('a')
                apply_url = self._safe_get_href(link_elem, uri) if link_elem else uri
                
                if title:
                    job = JobListing(
                        title=title,
                        company=company_name,
                        location=location,
                        description='',
                        apply_url=apply_url,
                        source_url=uri,
                        external_id=f"freshteam_{hash(apply_url)}",
                        remote_type=self._determine_remote_type(location)
                    )
                    jobs.append(job)
                    
            except Exception as e:
                logger.debug(f"Error parsing Freshteam job element: {e}")
                continue
        
        return jobs
    
    def _extract_job_from_element(self, company_name: str, uri: str, element) -> Optional[JobListing]:
        """Extract job from generic element with improved detection"""
        try:
            # Get all text content
            text = element.get_text(strip=True)
            
            # Skip very short or very long text (likely not job titles)
            if len(text) < 5 or len(text) > 500:
                return None
            
            # Skip CSS, JavaScript, and style content
            if any(indicator in text.lower() for indicator in [
                'css', 'javascript', 'font-size', 'color:', 'display:', 'px;', 'margin:', 'padding:'
            ]):
                return None
            
            # Enhanced job title detection patterns
            job_patterns = [
                # Technical roles
                r'\b(senior|sr\.?|junior|jr\.?|lead|principal|staff)\s+(software|backend|frontend|full[- ]?stack|devops|data|ml|ai)\s+(engineer|developer|scientist|analyst)',
                r'\b(software|backend|frontend|full[- ]?stack|web|mobile|ios|android)\s+(engineer|developer)',
                r'\b(data|machine learning|ai|ml)\s+(engineer|scientist|analyst)',
                r'\b(product|program|project)\s+manager',
                r'\b(designer|ux|ui|graphic)\b',
                r'\b(marketing|sales|business)\s+(manager|specialist|analyst|coordinator)',
                r'\b(customer|client)\s+(success|support|service)',
                r'\b(operations|hr|finance|accounting)\s+(manager|specialist|analyst)',
                r'\b(cto|ceo|cfo|vp|director|head of)',
                
                # General patterns
                r'\b\w+\s+(engineer|developer|manager|analyst|specialist|coordinator|director|lead)\b',
                r'\b(intern|internship|graduate|entry.level)\b',
            ]
            
            # Check if text matches job patterns
            text_lower = text.lower()
            is_job_title = any(re.search(pattern, text_lower) for pattern in job_patterns)
            
            # Also check for common job-related keywords
            job_keywords = [
                'engineer', 'developer', 'manager', 'analyst', 'designer', 'consultant',
                'specialist', 'coordinator', 'director', 'lead', 'scientist', 'architect',
                'intern', 'associate', 'executive', 'officer', 'representative'
            ]
            
            has_job_keyword = any(keyword in text_lower for keyword in job_keywords)
            
            # Must have job keyword and reasonable length
            if not has_job_keyword or not (10 <= len(text) <= 200):
                return None
            
            # Extract job information
            job_title = text.strip()
            
            # Try to find associated link
            link_elem = element.find('a') or element.find_parent('a')
            if link_elem:
                apply_url = self._safe_get_href(link_elem, uri)
            else:
                apply_url = uri
            
            # Try to extract location (common patterns)
            location = 'Remote'  # Default
            location_patterns = [
                r'\b(remote|worldwide|anywhere|work from home)\b',
                r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*),\s*([A-Z]{2}|[A-Z][a-z]+)\b',  # City, State/Country
                r'\b(london|paris|berlin|madrid|amsterdam|toronto|vancouver|sydney|tokyo|singapore)\b'
            ]
            
            # Look in nearby elements for location
            parent = element.find_parent()
            if parent:
                parent_text = parent.get_text()
                for pattern in location_patterns:
                    match = re.search(pattern, parent_text, re.IGNORECASE)
                    if match:
                        location = match.group(0)
                        break
            
            # Create job listing
            job = JobListing(
                title=job_title,
                company=company_name,
                location=location,
                description='',
                apply_url=apply_url,
                source_url=uri,
                external_id=f"distill_{hash(apply_url)}_{hash(job_title)}",
                remote_type=self._determine_remote_type(location)
            )
            
            return job
            
        except Exception as e:
            logger.debug(f"Error extracting job from element: {e}")
            return None
    
    def _determine_remote_type(self, location: str) -> str:
        """Determine if job is remote, hybrid, or onsite"""
        location_lower = location.lower()
        
        if any(word in location_lower for word in ['remote', 'anywhere', 'worldwide', 'work from home']):
            return 'remote'
        elif any(word in location_lower for word in ['hybrid', 'flexible']):
            return 'hybrid'
        else:
            return 'onsite'
    
    async def crawl_all_companies(self) -> List[JobListing]:
        """Crawl ALL companies from distill export - no limit"""
        all_jobs = []
        failed_companies = []
        successful_companies = 0
        
        if not self.companies_data:
            self.load_companies_data()
        
        companies_to_crawl = self.companies_data
        total_companies = len(companies_to_crawl)
        
        logger.info(f"🚀 Starting to crawl ALL {total_companies} companies...")
        
        connector = aiohttp.TCPConnector(limit=10, ttl_dns_cache=300)
        timeout = aiohttp.ClientTimeout(total=60)
        
        async with aiohttp.ClientSession(
            headers=self.headers,
            connector=connector,
            timeout=timeout
        ) as session:
            self.session = session
            
            # Process companies in batches
            batch_size = 5
            for i in range(0, total_companies, batch_size):
                batch = companies_to_crawl[i:i + batch_size]
                
                logger.info(f"📦 Processing batch {i//batch_size + 1} ({len(batch)} companies)")
                
                # Process batch concurrently
                tasks = [self.crawl_company(company) for company in batch]
                
                try:
                    batch_results = await asyncio.gather(*tasks, return_exceptions=True)
                except Exception as e:
                    logger.error(f"Batch processing error: {e}")
                    # If batch fails entirely, process companies individually
                    batch_results = []
                    for company in batch:
                        try:
                            result = await self.crawl_company(company)
                            batch_results.append(result)
                        except Exception as individual_error:
                            batch_results.append(individual_error)
                
                # Collect results safely
                for idx, result in enumerate(batch_results):
                    if idx >= len(batch):  # Safety check
                        logger.warning(f"Result index {idx} exceeds batch size {len(batch)}")
                        continue
                        
                    company = batch[idx]
                    company_name = company.get('name', 'Unknown')
                    
                    try:
                        if isinstance(result, list):
                            all_jobs.extend(result)
                            if result:  # Has jobs
                                successful_companies += 1
                            logger.debug(f"✅ {company_name}: {len(result)} jobs")
                        elif isinstance(result, Exception):
                            failed_companies.append({
                                'name': company_name,
                                'error': str(result)
                            })
                            logger.debug(f"⚠️ {company_name}: {str(result)}")
                        else:
                            # Handle unexpected result types
                            failed_companies.append({
                                'name': company_name,
                                'error': f'Unexpected result type: {type(result)}'
                            })
                            logger.debug(f"⚠️ {company_name}: Unexpected result type {type(result)}")
                    except Exception as processing_error:
                        failed_companies.append({
                            'name': company_name,
                            'error': f'Result processing error: {str(processing_error)}'
                        })
                        logger.debug(f"⚠️ {company_name}: Processing error {str(processing_error)}")
                
                # Rate limiting between batches
                await asyncio.sleep(2)
                
                # Progress update
                processed = min(i + batch_size, total_companies)
                logger.info(f"📊 Progress: {processed}/{total_companies} companies processed ({len(all_jobs)} jobs found so far)")
        
        # Log final statistics
        failed_count = len(failed_companies)
        success_count = total_companies - failed_count
        successful_job_count = len([job for job in all_jobs if job])
        
        logger.info(f"🏁 Crawling completed!")
        logger.info(f"📈 Successfully processed: {success_count}/{total_companies} companies")
        logger.info(f"📈 Companies with jobs: {successful_companies}/{total_companies}")
        logger.info(f"📉 Failed companies: {failed_count}")
        logger.info(f"🎯 Total jobs found: {len(all_jobs)}")
        
        # Log detailed success breakdown
        if successful_companies > 0:
            logger.info(f"🎉 Top performing companies by job count:")
            # Count jobs by company
            company_job_counts = {}
            for job in all_jobs:
                company = job.company
                company_job_counts[company] = company_job_counts.get(company, 0) + 1
            
            # Sort and show top 5
            top_companies = sorted(company_job_counts.items(), key=lambda x: x[1], reverse=True)[:5]
            for company, job_count in top_companies:
                logger.info(f"   📊 {company}: {job_count} jobs")
        
        # Log some failed companies for debugging (but don't spam)
        if failed_companies:
            sample_failures = failed_companies[:5]  # Show only first 5
            logger.info(f"⚠️ Sample failures (first {len(sample_failures)} of {failed_count}):")
            for failure in sample_failures:
                logger.info(f"   ❌ {failure['name']}: {failure['error'][:100]}...")
            
            if failed_count > 5:
                logger.info(f"   ... and {failed_count - 5} more companies had issues")
        
        # Create summary for scheduler
        self.last_crawl_summary = {
            'total_companies': total_companies,
            'successful_companies': success_count,
            'companies_with_jobs': successful_companies, 
            'failed_companies': failed_count,
            'total_jobs': len(all_jobs),
            'top_companies': dict(sorted(company_job_counts.items(), key=lambda x: x[1], reverse=True)[:10]) if 'company_job_counts' in locals() else {},
            'sample_failures': [{'name': f['name'], 'error': f['error'][:100]} for f in failed_companies[:10]]
        }
        
        return all_jobs
    
    def save_jobs_to_database(self, jobs: List[JobListing]):
        """Save jobs and company information to MongoDB database"""
        try:
            db = get_db()
            jobs_collection = db["jobs"]
            companies_collection = db["companies"]
            
            new_jobs = 0
            updated_jobs = 0
            new_companies = 0
            updated_companies = 0
            
            # Track processed companies to avoid duplicates
            processed_companies = set()
            
            for job in jobs:
                # Save job
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
                    "requirements": job.requirements or [],
                    "posted_date": job.posted_date,
                    "apply_url": job.apply_url,
                    "remote_type": job.remote_type,
                    "skills": job.skills or [],
                    "source_url": job.source_url,
                    "external_id": job.external_id,
                    "is_active": True,
                    "last_updated": datetime.now(),
                    "source_type": "distill_crawler"
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
                
                # Save company if not already processed
                if job.company not in processed_companies:
                    # Find company in companies_data
                    company_data = next(
                        (c for c in self.companies_data if c.get('name') == job.company),
                        None
                    )
                    
                    if company_data:
                        company_doc = {
                            "name": job.company,
                            "website": company_data.get('uri', ''),  # Use URI as website
                            "careerPage": job.source_url,  # Use job source URL as career page
                            "description": company_data.get('description', ''),
                            "location": "Remote",  # Default to Remote
                            "size": "Unknown",  # Default size
                            "industry": "Technology",  # Default industry
                            "is_active": True,
                            "created_at": datetime.now(),
                            "updated_at": datetime.now(),
                            "jobs_count": 1,  # Will be updated later
                            "remote_policy": "Remote-first"  # Default policy
                        }
                        
                        # Check if company exists
                        existing_company = companies_collection.find_one({"name": job.company})
                        
                        if existing_company:
                            # Update company
                            companies_collection.update_one(
                                {"_id": existing_company["_id"]},
                                {
                                    "$set": {
                                        "website": company_doc["website"],
                                        "careerPage": company_doc["careerPage"],
                                        "updated_at": datetime.now()
                                    },
                                    "$inc": {"jobs_count": 1}
                                }
                            )
                            updated_companies += 1
                        else:
                            # Insert new company
                            companies_collection.insert_one(company_doc)
                            new_companies += 1
                        
                        processed_companies.add(job.company)
            
            logger.info(f"💾 Database save completed: {new_jobs} new jobs, {updated_jobs} updated jobs, {new_companies} new companies, {updated_companies} updated companies")
            
            return {
                "new_jobs": new_jobs,
                "updated_jobs": updated_jobs,
                "new_companies": new_companies,
                "updated_companies": updated_companies,
                "total_processed": len(jobs)
            }
            
        except Exception as e:
            logger.error(f"❌ Error saving to database: {str(e)}")
            raise

    def _find_individual_jobs_in_container(self, container) -> List:
        """Find individual job elements within a container"""
        job_elements = []
        
        # Common patterns for individual job listings
        job_selectors = [
            # Most common job listing patterns
            '.job-listing', '.job-item', '.job-card', '.job',
            '.position', '.opening', '.role', '.vacancy',
            '[class*="job"]', '[class*="position"]', '[class*="role"]',
            '[data-testid*="job"]', '[data-qa*="job"]',
            '.posting', '.listing', '.opportunity',
            
            # Generic patterns that often contain jobs
            'li', 'article', '.card', '.item',
            'tr', 'div[class*="row"]',
            
            # Link-based patterns
            'a[href*="job"]', 'a[href*="career"]', 'a[href*="position"]',
            'a[href*="apply"]', 'a[href*="opening"]'
        ]
        
        for selector in job_selectors:
            try:
                elements = container.select(selector)
                if elements:
                    # Filter elements that look like actual job listings
                    filtered_jobs = []
                    for elem in elements:
                        text = elem.get_text(strip=True)
                        
                        # Skip very short or very long content
                        if not (10 <= len(text) <= 500):
                            continue
                            
                        # Skip navigation, filter, and UI elements
                        skip_patterns = [
                            'show filters', 'all departments', 'clear filters',
                            'sort by', 'page', 'next', 'previous', 'load more',
                            'contact', 'about', 'home', 'menu', 'search',
                            'css', 'javascript', 'px;', 'color:', 'font-size:'
                        ]
                        
                        text_lower = text.lower()
                        if any(pattern in text_lower for pattern in skip_patterns):
                            continue
                            
                        # Look for job-related keywords
                        job_keywords = [
                            'engineer', 'developer', 'manager', 'analyst', 'designer',
                            'specialist', 'coordinator', 'director', 'lead', 'scientist',
                            'architect', 'consultant', 'associate', 'intern', 'executive'
                        ]
                        
                        if any(keyword in text_lower for keyword in job_keywords):
                            filtered_jobs.append(elem)
                    
                    # If we found good job elements, return them
                    if filtered_jobs:
                        logger.debug(f"Found {len(filtered_jobs)} jobs with selector '{selector}'")
                        job_elements.extend(filtered_jobs)
                        break  # Stop at first successful selector
                        
            except Exception as e:
                logger.debug(f"Error with selector '{selector}': {e}")
                continue
        
        # If still no jobs found, try a more aggressive approach
        if not job_elements:
            # Look for any elements that contain job-related text
            all_elements = container.find_all(['div', 'li', 'article', 'a', 'span', 'p'])
            for elem in all_elements:
                text = elem.get_text(strip=True)
                if 20 <= len(text) <= 200:  # Reasonable job title length
                    text_lower = text.lower()
                    job_indicators = [
                        'engineer', 'developer', 'manager', 'analyst', 'designer',
                        'remote', 'full-time', 'part-time', 'contract'
                    ]
                    if any(indicator in text_lower for indicator in job_indicators):
                        job_elements.append(elem)
                        if len(job_elements) >= 50:  # Limit to prevent too many false positives
                            break
        
        return job_elements

    def _safe_get_href(self, link_elem, uri):
        """Safely extract href from elements"""
        if link_elem:
            href = link_elem.get('href', '')
            return urljoin(uri, href) if href else uri
        else:
            return uri

async def main():
    """Main function for testing"""
    crawler = DistillCrawler()
    
    # Test with first 10 companies
    jobs = await crawler.crawl_all_companies()
    
    print(f"\n🎯 Crawling Results:")
    print(f"Total jobs found: {len(jobs)}")
    
    # Show sample jobs
    for i, job in enumerate(jobs[:5]):
        print(f"\n{i+1}. {job.title} at {job.company}")
        print(f"   Location: {job.location}")
        print(f"   Apply: {job.apply_url}")
    
    # Save to database
    if jobs:
        result = crawler.save_jobs_to_database(jobs)
        print(f"\n💾 Saved to database: {result}")

if __name__ == '__main__':
    asyncio.run(main()) 