"""
Job Scraping Service

This service handles scraping job details from various sources
and extracting relevant information.
"""

import asyncio
import logging
import re
from datetime import datetime
from typing import Any, Dict, List, Optional

import aiohttp
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


class JobScrapingService:
    """Service for scraping job details from various sources"""

    def __init__(self, db=None):
        self.db = db
        self.session = None
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br",
            "DNT": "1",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
        }

    async def __aenter__(self):
        self.session = aiohttp.ClientSession(headers=self.headers)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    async def scrape_job_details(self, job_url: str) -> Dict[str, Any]:
        """Scrape job details from a given URL"""
        try:
            if not self.session:
                async with aiohttp.ClientSession(headers=self.headers) as session:
                    return await self._scrape_with_session(session, job_url)
            else:
                return await self._scrape_with_session(self.session, job_url)

        except Exception as e:
            logger.error(f"Error scraping job details from {job_url}: {e}")
            return {
                "success": False,
                "error": str(e),
                "url": job_url
            }

    async def _scrape_with_session(self, session: aiohttp.ClientSession, job_url: str) -> Dict[str, Any]:
        """Scrape job details using provided session"""
        try:
            async with session.get(job_url, timeout=30) as response:
                if response.status != 200:
                    return {
                        "success": False,
                        "error": f"HTTP {response.status}",
                        "url": job_url
                    }

                html_content = await response.text()
                soup = BeautifulSoup(html_content, "html.parser")

                # Extract job information
                job_data = {
                    "title": self._extract_job_title(soup),
                    "company": self._extract_company_name(soup),
                    "location": self._extract_location(soup),
                    "description": self._extract_description(soup),
                    "salary": self._extract_salary(soup),
                    "requirements": self._extract_requirements(soup),
                    "benefits": self._extract_benefits(soup),
                    "application_url": self._extract_application_url(soup, job_url),
                    "posted_date": self._extract_posted_date(soup),
                    "job_type": self._extract_job_type(soup),
                    "experience_level": self._extract_experience_level(soup),
                    "skills": self._extract_skills(soup),
                    "scraped_at": datetime.utcnow().isoformat(),
                    "source_url": job_url
                }

                return {
                    "success": True,
                    "job_data": job_data
                }

        except asyncio.TimeoutError:
            return {
                "success": False,
                "error": "Request timeout",
                "url": job_url
            }
        except Exception as e:
            logger.error(f"Error in _scrape_with_session: {e}")
            return {
                "success": False,
                "error": str(e),
                "url": job_url
            }

    async def scrape_multiple_jobs(self, job_urls: List[str]) -> List[Dict[str, Any]]:
        """Scrape multiple job URLs concurrently"""
        try:
            tasks = [self.scrape_job_details(url) for url in job_urls]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            processed_results = []
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    processed_results.append({
                        "success": False,
                        "error": str(result),
                        "url": job_urls[i]
                    })
                else:
                    processed_results.append(result)
            
            return processed_results

        except Exception as e:
            logger.error(f"Error scraping multiple jobs: {e}")
            return [{"success": False, "error": str(e)}]

    def _extract_job_title(self, soup: BeautifulSoup) -> str:
        """Extract job title from HTML"""
        # Common selectors for job titles
        selectors = [
            "h1",
            ".job-title",
            ".title",
            "[data-testid='job-title']",
            ".job-header h1",
            ".position-title"
        ]
        
        for selector in selectors:
            element = soup.select_one(selector)
            if element and element.get_text().strip():
                return element.get_text().strip()
        
        return ""

    def _extract_company_name(self, soup: BeautifulSoup) -> str:
        """Extract company name from HTML"""
        selectors = [
            ".company-name",
            ".employer",
            ".organization",
            "[data-testid='company-name']",
            ".job-company"
        ]
        
        for selector in selectors:
            element = soup.select_one(selector)
            if element and element.get_text().strip():
                return element.get_text().strip()
        
        return ""

    def _extract_location(self, soup: BeautifulSoup) -> str:
        """Extract job location from HTML"""
        selectors = [
            ".location",
            ".job-location",
            "[data-testid='location']",
            ".address"
        ]
        
        for selector in selectors:
            element = soup.select_one(selector)
            if element and element.get_text().strip():
                return element.get_text().strip()
        
        return ""

    def _extract_description(self, soup: BeautifulSoup) -> str:
        """Extract job description from HTML"""
        selectors = [
            ".job-description",
            ".description",
            ".job-details",
            "[data-testid='job-description']",
            ".content"
        ]
        
        for selector in selectors:
            element = soup.select_one(selector)
            if element and element.get_text().strip():
                return element.get_text().strip()
        
        return ""

    def _extract_salary(self, soup: BeautifulSoup) -> str:
        """Extract salary information from HTML"""
        selectors = [
            ".salary",
            ".compensation",
            ".pay",
            "[data-testid='salary']"
        ]
        
        for selector in selectors:
            element = soup.select_one(selector)
            if element and element.get_text().strip():
                return element.get_text().strip()
        
        return ""

    def _extract_requirements(self, soup: BeautifulSoup) -> List[str]:
        """Extract job requirements from HTML"""
        requirements = []
        
        # Look for requirements sections
        req_selectors = [
            ".requirements",
            ".qualifications",
            ".requirements-list",
            "ul:contains('Requirements')",
            "ul:contains('Qualifications')"
        ]
        
        for selector in req_selectors:
            elements = soup.select(selector)
            for element in elements:
                items = element.find_all("li")
                for item in items:
                    text = item.get_text().strip()
                    if text:
                        requirements.append(text)
        
        return requirements

    def _extract_benefits(self, soup: BeautifulSoup) -> List[str]:
        """Extract job benefits from HTML"""
        benefits = []
        
        # Look for benefits sections
        benefit_selectors = [
            ".benefits",
            ".perks",
            ".benefits-list",
            "ul:contains('Benefits')",
            "ul:contains('Perks')"
        ]
        
        for selector in benefit_selectors:
            elements = soup.select(selector)
            for element in elements:
                items = element.find_all("li")
                for item in items:
                    text = item.get_text().strip()
                    if text:
                        benefits.append(text)
        
        return benefits

    def _extract_application_url(self, soup: BeautifulSoup, base_url: str) -> str:
        """Extract application URL from HTML"""
        # Look for apply buttons/links
        apply_selectors = [
            "a[href*='apply']",
            "a[href*='application']",
            ".apply-button",
            ".apply-link",
            "button:contains('Apply')",
            "a:contains('Apply')"
        ]
        
        for selector in apply_selectors:
            element = soup.select_one(selector)
            if element:
                href = element.get("href")
                if href:
                    if href.startswith("http"):
                        return href
                    else:
                        return f"{base_url.rstrip('/')}/{href.lstrip('/')}"
        
        return base_url

    def _extract_posted_date(self, soup: BeautifulSoup) -> str:
        """Extract job posted date from HTML"""
        selectors = [
            ".posted-date",
            ".date-posted",
            "[data-testid='posted-date']",
            ".timestamp"
        ]
        
        for selector in selectors:
            element = soup.select_one(selector)
            if element and element.get_text().strip():
                return element.get_text().strip()
        
        return ""

    def _extract_job_type(self, soup: BeautifulSoup) -> str:
        """Extract job type (full-time, part-time, etc.) from HTML"""
        selectors = [
            ".job-type",
            ".employment-type",
            "[data-testid='job-type']"
        ]
        
        for selector in selectors:
            element = soup.select_one(selector)
            if element and element.get_text().strip():
                return element.get_text().strip()
        
        return ""

    def _extract_experience_level(self, soup: BeautifulSoup) -> str:
        """Extract experience level from HTML"""
        text = soup.get_text().lower()
        
        if "senior" in text:
            return "senior"
        elif "junior" in text or "entry" in text:
            return "junior"
        elif "mid" in text or "intermediate" in text:
            return "mid-level"
        else:
            return ""

    def _extract_skills(self, soup: BeautifulSoup) -> List[str]:
        """Extract required skills from HTML"""
        skills = []
        text = soup.get_text().lower()
        
        # Common programming languages and technologies
        common_skills = [
            "python", "javascript", "java", "c++", "c#", "php", "ruby", "go", "rust",
            "react", "angular", "vue", "node.js", "django", "flask", "spring",
            "docker", "kubernetes", "aws", "azure", "gcp", "sql", "mongodb",
            "redis", "elasticsearch", "git", "jenkins", "ci/cd"
        ]
        
        for skill in common_skills:
            if skill in text:
                skills.append(skill)
        
        return skills

    async def extract_job_information(self, job_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract and structure job information"""
        try:
            return {
                "title": job_data.get("title", ""),
                "company": job_data.get("company", ""),
                "location": job_data.get("location", ""),
                "description": job_data.get("description", ""),
                "salary_range": self._parse_salary(job_data.get("salary", "")),
                "requirements": job_data.get("requirements", []),
                "benefits": job_data.get("benefits", []),
                "skills": job_data.get("skills", []),
                "experience_level": job_data.get("experience_level", ""),
                "job_type": job_data.get("job_type", ""),
                "application_url": job_data.get("application_url", ""),
                "posted_date": job_data.get("posted_date", ""),
                "scraped_at": job_data.get("scraped_at", "")
            }
        except Exception as e:
            logger.error(f"Error extracting job information: {e}")
            return {}

    def _parse_salary(self, salary_text: str) -> Dict[str, Any]:
        """Parse salary information from text"""
        try:
            # Simple salary parsing
            numbers = re.findall(r'\$?(\d+(?:,\d{3})*(?:\.\d{2})?)', salary_text)
            if len(numbers) >= 2:
                return {
                    "min": float(numbers[0].replace(",", "")),
                    "max": float(numbers[1].replace(",", "")),
                    "currency": "USD"
                }
            elif len(numbers) == 1:
                return {
                    "amount": float(numbers[0].replace(",", "")),
                    "currency": "USD"
                }
            else:
                return {}
        except Exception:
            return {}

    async def parse_salary_information(self, salary_text: str) -> Dict[str, Any]:
        """Parse detailed salary information"""
        return self._parse_salary(salary_text)

    async def extract_skills_from_description(self, description: str) -> List[str]:
        """Extract skills from job description"""
        skills = []
        description_lower = description.lower()
        
        # Common skills to look for
        common_skills = [
            "python", "javascript", "java", "c++", "c#", "php", "ruby", "go", "rust",
            "react", "angular", "vue", "node.js", "django", "flask", "spring",
            "docker", "kubernetes", "aws", "azure", "gcp", "sql", "mongodb",
            "redis", "elasticsearch", "git", "jenkins", "ci/cd"
        ]
        
        for skill in common_skills:
            if skill in description_lower:
                skills.append(skill)
        
        return skills

    async def validate_job_data(self, job_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate scraped job data"""
        try:
            required_fields = ["title", "company", "description"]
            missing_fields = []
            
            for field in required_fields:
                if not job_data.get(field):
                    missing_fields.append(field)
            
            if missing_fields:
                return {
                    "valid": False,
                    "missing_fields": missing_fields
                }
            
            return {"valid": True}
            
        except Exception as e:
            logger.error(f"Error validating job data: {e}")
            return {"valid": False, "error": str(e)}

    async def clean_and_normalize_data(self, job_data: Dict[str, Any]) -> Dict[str, Any]:
        """Clean and normalize scraped job data"""
        try:
            cleaned_data = {}
            
            for key, value in job_data.items():
                if isinstance(value, str):
                    # Clean text fields
                    cleaned_value = value.strip()
                    if cleaned_value:
                        cleaned_data[key] = cleaned_value
                elif isinstance(value, list):
                    # Clean list fields
                    cleaned_list = [item.strip() for item in value if item and item.strip()]
                    if cleaned_list:
                        cleaned_data[key] = cleaned_list
                else:
                    cleaned_data[key] = value
            
            return cleaned_data
            
        except Exception as e:
            logger.error(f"Error cleaning job data: {e}")
            return job_data

    async def detect_job_source(self, url: str) -> str:
        """Detect the source of the job posting"""
        try:
            url_lower = url.lower()
            
            if "linkedin.com" in url_lower:
                return "linkedin"
            elif "indeed.com" in url_lower:
                return "indeed"
            elif "glassdoor.com" in url_lower:
                return "glassdoor"
            elif "monster.com" in url_lower:
                return "monster"
            elif "careerbuilder.com" in url_lower:
                return "careerbuilder"
            else:
                return "unknown"
                
        except Exception as e:
            logger.error(f"Error detecting job source: {e}")
            return "unknown"

    async def extract_application_deadline(self, soup: BeautifulSoup) -> str:
        """Extract application deadline from HTML"""
        selectors = [
            ".deadline",
            ".application-deadline",
            ".closing-date",
            "[data-testid='deadline']"
        ]
        
        for selector in selectors:
            element = soup.select_one(selector)
            if element and element.get_text().strip():
                return element.get_text().strip()
        
        return ""

    async def analyze_job_quality_score(self, job_data: Dict[str, Any]) -> float:
        """Analyze and score job quality based on available information"""
        try:
            score = 0.0
            
            # Score based on completeness
            if job_data.get("title"):
                score += 0.2
            if job_data.get("company"):
                score += 0.15
            if job_data.get("description"):
                score += 0.25
            if job_data.get("location"):
                score += 0.1
            if job_data.get("salary"):
                score += 0.1
            if job_data.get("requirements"):
                score += 0.1
            if job_data.get("application_url"):
                score += 0.1
            
            return min(score, 1.0)
            
        except Exception as e:
            logger.error(f"Error analyzing job quality: {e}")
            return 0.0
