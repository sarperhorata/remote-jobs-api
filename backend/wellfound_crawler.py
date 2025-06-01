import asyncio
import logging
from datetime import datetime
import json
from typing import List, Dict, Optional
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright
from fake_useragent import UserAgent
import aiohttp
import random
import time
import os
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WellfoundCrawler:
    def __init__(self):
        self.base_url = "https://wellfound.com"
        self.jobs_url = f"{self.base_url}/jobs"
        self.browser = None
        self.context = None
        self.page = None
        self.ua = UserAgent()
        self.email = os.getenv("WELLFOUND_EMAIL")
        self.password = os.getenv("WELLFOUND_PASSWORD")
        self.cookies_file = "wellfound_cookies.json"

    async def init_browser(self):
        """Initialize browser with custom settings"""
        playwright = await async_playwright().start()
        self.browser = await playwright.chromium.launch(
            headless=False,  # Set to True in production
            args=['--disable-blink-features=AutomationControlled']
        )
        
        # Create a new context with custom user agent
        self.context = await self.browser.new_context(
            user_agent=self.ua.random,
            viewport={'width': 1920, 'height': 1080},
            java_script_enabled=True,
            bypass_csp=True
        )
        
        # Add stealth scripts
        await self.context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
        """)
        
        self.page = await self.context.new_page()
        logger.info(f"Browser launched with user-agent: {self.ua.random}")

    async def load_cookies(self):
        """Load cookies from file"""
        try:
            if os.path.exists(self.cookies_file):
                with open(self.cookies_file, 'r') as f:
                    cookies = json.load(f)
                await self.context.add_cookies(cookies)
                logger.info("Cookies loaded successfully")
                return True
        except Exception as e:
            logger.error(f"Error loading cookies: {str(e)}")
        return False

    async def save_cookies(self):
        """Save current cookies to file"""
        try:
            cookies = await self.context.cookies()
            with open(self.cookies_file, 'w') as f:
                json.dump(cookies, f)
            logger.info("Cookies saved successfully")
        except Exception as e:
            logger.error(f"Error saving cookies: {str(e)}")

    async def login(self):
        """Login to Wellfound"""
        logger.info(f"Attempting to login to Wellfound with email: {self.email} and password: {'*' * len(self.password) if self.password else None}")
        
        # Try to load cookies first
        if await self.load_cookies():
            # Verify if we're logged in
            await self.page.goto(f"{self.base_url}/jobs", wait_until='domcontentloaded')
            await asyncio.sleep(5)  # Wait for any redirects
            
            # Check if we're redirected to login page
            if "/login" not in self.page.url:
                logger.info("Using existing cookies - already logged in")
                return True
        
        # If cookies didn't work, try manual login
        try:
            await self.page.goto(f"{self.base_url}/login", wait_until='domcontentloaded')
            await asyncio.sleep(5)  # Wait for any redirects
            
            # Wait for login form with increased timeout
            logger.info("Waiting for login form...")
            await self.page.wait_for_selector('form', timeout=90000)
            
            # Fill in credentials
            logger.info(f"Filling email: {self.email}")
            await self.page.fill('input[type="email"]', self.email or "")
            await asyncio.sleep(1)
            logger.info(f"Filling password: {'*' * len(self.password) if self.password else None}")
            await self.page.fill('input[type="password"]', self.password or "")
            await asyncio.sleep(1)
            
            # Click login button
            await self.page.click('button[type="submit"]')
            await asyncio.sleep(5)  # Wait for login to complete
            
            # Save cookies if login successful
            if "/login" not in self.page.url:
                await self.save_cookies()
                logger.info("Login successful")
                return True
            else:
                logger.error("Login failed - still on login page")
                return False
                
        except Exception as e:
            logger.error(f"Error during login: {str(e)}")
            # Save page content for debugging
            try:
                content = await self.page.content()
                with open("wellfound_login_debug.html", "w") as f:
                    f.write(content)
                logger.info("Saved login page HTML for debugging")
            except Exception as save_error:
                logger.error(f"Could not save login page HTML: {str(save_error)}")
            return False

    async def get_job_listings(self, max_pages=5):
        """Fetch job listings from the 'All Jobs' tab with pagination"""
        if not self.browser:
            await self.init_browser()
            await self.login()

        all_jobs = []
        page = 1
        
        # Go to jobs page and click 'All Jobs' tab if needed
        await self.page.goto(f"{self.base_url}/jobs", wait_until='domcontentloaded')
        await asyncio.sleep(5)
        try:
            # Try to click 'All Jobs' tab if it exists
            all_jobs_tab = await self.page.query_selector('a:has-text("All Jobs")')
            if all_jobs_tab:
                logger.info("Clicking 'All Jobs' tab...")
                await all_jobs_tab.click()
                await asyncio.sleep(3)
        except Exception as e:
            logger.warning(f"Could not click 'All Jobs' tab: {e}")
        
        while page <= max_pages:
            url = f"{self.jobs_url}?remote=true&page={page}"
            logger.info(f"Fetching page {page}: {url}")
            
            try:
                await self.page.goto(url, wait_until='domcontentloaded')
                await asyncio.sleep(5)  # Wait for any redirects
                
                # Wait for job cards with increased timeout
                await self.page.wait_for_selector('.styles_component__jobCard', timeout=90000)
                
                # Get page content
                content = await self.page.content()
                soup = BeautifulSoup(content, 'html.parser')
                
                # Find all job cards
                job_cards = soup.select('.styles_component__jobCard')
                logger.info(f"Found {len(job_cards)} jobs on page {page}")
                
                for card in job_cards:
                    job = await self._parse_job_card(card)
                    if job:
                        all_jobs.append(job)
                
                # Check for next page
                next_button = await self.page.query_selector('.styles_component__paginationNext:not([disabled])')
                if not next_button:
                    logger.info("No more pages available")
                    break
                    
                page += 1
                await asyncio.sleep(5)  # Increased delay between pages
                
            except Exception as e:
                logger.error(f"Error fetching page {page}: {str(e)}")
                break
        
        return all_jobs

    async def _parse_job_card(self, card):
        """Parse job card HTML"""
        try:
            title_elem = card.select_one('.styles_component__jobTitle')
            company_elem = card.select_one('.styles_component__companyName')
            location_elem = card.select_one('.styles_component__location')
            url_elem = card.select_one('a')
            
            if not all([title_elem, company_elem, url_elem]):
                return None
                
            return {
                'title': title_elem.text.strip(),
                'company': company_elem.text.strip(),
                'location': location_elem.text.strip() if location_elem else 'Remote',
                'url': f"{self.base_url}{url_elem['href']}" if url_elem else None
            }
        except Exception as e:
            logger.error(f"Error parsing job card: {str(e)}")
            return None

    async def get_job_details(self, job_url):
        """Get detailed job information"""
        try:
            await self.page.goto(job_url)
            await self.page.wait_for_load_state('networkidle')
            
            content = await self.page.content()
            soup = BeautifulSoup(content, 'html.parser')
            
            return {
                'description': self._get_text(soup, '.styles_component__jobDescription'),
                'requirements': self._get_text(soup, '.styles_component__requirements'),
                'salary': self._get_text(soup, '.styles_component__salary'),
                'posted_date': self._get_text(soup, '.styles_component__postedDate')
            }
        except Exception as e:
            logger.error(f"Error getting job details: {str(e)}")
            return None

    async def get_company_details(self, company_url):
        """Get company information"""
        try:
            await self.page.goto(company_url)
            await self.page.wait_for_load_state('networkidle')
            
            content = await self.page.content()
            soup = BeautifulSoup(content, 'html.parser')
            
            return {
                'name': self._get_text(soup, '.styles_component__companyName'),
                'description': self._get_text(soup, '.styles_component__companyDescription'),
                'website': self._get_text(soup, '.styles_component__companyWebsite'),
                'size': self._get_text(soup, '.styles_component__companySize'),
                'industry': self._get_text(soup, '.styles_component__companyIndustry'),
                'location': self._get_text(soup, '.styles_component__companyLocation')
            }
        except Exception as e:
            logger.error(f"Error getting company details: {str(e)}")
            return None

    def _get_text(self, soup, selector):
        """Helper method to get text from selector"""
        element = soup.select_one(selector)
        return element.text.strip() if element else None

    async def close(self):
        """Close browser and cleanup"""
        if self.browser:
            await self.browser.close()
            logger.info("Browser closed")

async def main():
    crawler = WellfoundCrawler()
    try:
        jobs = await crawler.get_job_listings(max_pages=2)
        print(f"\nFound {len(jobs)} jobs")
        for job in jobs:
            print(f"\nJob: {job['title']}")
            print(f"Company: {job['company']}")
            print(f"Location: {job['location']}")
            print(f"URL: {job['url']}")
    finally:
        await crawler.close()

if __name__ == "__main__":
    asyncio.run(main()) 