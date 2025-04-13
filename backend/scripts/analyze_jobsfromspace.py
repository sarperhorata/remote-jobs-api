#!/usr/bin/env python3
import os
import sys
import json
import logging
from pathlib import Path

# Add the parent directory to the path to import modules from backend
script_dir = Path(__file__).resolve().parent
backend_dir = script_dir.parent
sys.path.append(str(backend_dir.parent))

from backend.crawler.jobs_from_space_parser import JobsFromSpaceParser
from backend.models.models import WebsiteType, Website, SelectorBase

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

def main():
    """
    Analyze and crawl JobsFromSpace website for job listings
    """
    logger.info("Starting JobsFromSpace analysis")
    
    # Initialize parser
    parser = JobsFromSpaceParser()
    
    # Create data directory if it doesn't exist
    data_dir = script_dir / "data"
    data_dir.mkdir(exist_ok=True)
    
    # Analyze site structure
    logger.info("Analyzing site structure...")
    site_analysis = parser.analyze_site()
    
    if site_analysis:
        logger.info(f"Site title: {site_analysis['structure']['title']}")
        logger.info(f"API endpoints found: {len(site_analysis['api_endpoints'])}")
        logger.info(f"Job links found: {len(site_analysis['job_links'])}")
        
        # Save analysis
        with open(data_dir / "jobsfromspace_analysis.json", 'w') as f:
            json.dump(site_analysis, f, indent=2)
    
    # Check potential API endpoints
    logger.info("Checking API endpoints...")
    api_endpoints = parser.check_api_endpoints()
    logger.info(f"Working API endpoints: {len(api_endpoints)}")
    
    for endpoint in api_endpoints:
        logger.info(f"Found working endpoint: {endpoint['url']}")
    
    # Get company list
    logger.info("Retrieving company list...")
    companies = parser.get_company_list()
    logger.info(f"Found {len(companies)} companies")
    
    if companies:
        # Save company list
        with open(data_dir / "jobsfromspace_companies.json", 'w') as f:
            json.dump(companies, f, indent=2)
    
    # Get jobs
    logger.info("Retrieving jobs...")
    jobs = parser.get_jobs(max_pages=3)  # Limit to 3 pages for initial test
    logger.info(f"Found {len(jobs)} job listings")
    
    if jobs:
        # Save jobs
        with open(data_dir / "jobsfromspace_jobs.json", 'w') as f:
            json.dump(jobs, f, indent=2)
        
        # Print sample jobs
        logger.info("Sample jobs:")
        for i, job in enumerate(jobs[:5]):
            logger.info(f"{i+1}. {job['title']} at {job['company']}")
    
    # Suggest selectors for custom crawling
    logger.info("Generating selector suggestions for custom crawler...")
    selectors = [
        {"name": "job_container", "selector_type": "css", "value": ".job-card, .job-listing, .job-item"},
        {"name": "title", "selector_type": "css", "value": "h2, h3, .job-title"},
        {"name": "company", "selector_type": "css", "value": ".company, .company-name"},
        {"name": "url", "selector_type": "css", "value": "a"},
        {"name": "location", "selector_type": "css", "value": ".location, .job-location"},
        {"name": "tags", "selector_type": "css", "value": ".tags span, .skills span"},
    ]
    
    # Create a fake website object for testing
    website = {
        "name": "JobsFromSpace",
        "url": "https://www.jobsfromspace.com/jobs",
        "website_type": WebsiteType.JOBS_FROM_SPACE.value,
        "is_active": True,
        "selectors": selectors
    }
    
    with open(data_dir / "jobsfromspace_website.json", 'w') as f:
        json.dump(website, f, indent=2)
    
    logger.info("Analysis completed! Results saved to data directory.")
    logger.info(f"Found {len(jobs)} jobs from {len(companies)} companies.")

if __name__ == "__main__":
    main() 