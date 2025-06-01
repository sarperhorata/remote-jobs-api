#!/usr/bin/env python3

import sys
import os
import json
import asyncio
import logging
from datetime import datetime
from urllib.parse import urlparse
import re

# Add backend to path
sys.path.append('backend')
from database import db

# Setup logging
logging.basicConfig(
    level=logging.INFO, 
    format='%(levelname)s:%(name)s:%(message)s'
)
logger = logging.getLogger(__name__)

class CompanyWebsiteEnricher:
    def __init__(self):
        self.companies_data = []
        self.stats = {
            "total_companies": 0,
            "websites_found": 0,
            "career_pages_found": 0,
            "updated_companies": 0
        }
        
    def load_distill_data(self):
        """Load companies data from distill export"""
        try:
            with open('distill-export/Distill export - 01-18_2025-05-25.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self.companies_data = data['data']
            self.stats["total_companies"] = len(self.companies_data)
            logger.info(f"✅ Loaded {len(self.companies_data)} companies from distill export")
            
        except Exception as e:
            logger.error(f"❌ Error loading companies data: {str(e)}")
            raise
    
    def extract_website_from_uri(self, uri: str) -> str:
        """Extract main website domain from career page URI"""
        try:
            parsed = urlparse(uri)
            domain = parsed.netloc
            
            # Remove common subdomains
            domain = re.sub(r'^(www\.|careers\.|jobs\.|apply\.|talent\.)', '', domain)
            
            # Handle special cases for job platforms
            if 'lever.co' in domain:
                # Extract company name from lever URL
                path_parts = parsed.path.strip('/').split('/')
                if path_parts and path_parts[0]:
                    return f"https://{path_parts[0]}.com"
                return f"https://{domain}"
            elif 'greenhouse.io' in domain:
                # Extract company from greenhouse URL
                if 'boards.greenhouse.io' in domain:
                    path_parts = parsed.path.strip('/').split('/')
                    if path_parts and path_parts[0]:
                        return f"https://{path_parts[0]}.com"
                return f"https://{domain}"
            elif 'workable.com' in domain:
                # Extract company from workable URL
                if 'apply.workable.com' in domain:
                    path_parts = parsed.path.strip('/').split('/')
                    if path_parts and path_parts[0]:
                        return f"https://{path_parts[0]}.com"
                return f"https://{domain}"
            elif 'breezy.hr' in domain:
                # Extract company from breezy URL
                subdomain = domain.split('.')[0]
                if subdomain and subdomain != 'breezy':
                    return f"https://{subdomain}.com"
                return f"https://{domain}"
            elif 'smartrecruiters.com' in domain:
                # Extract company from smartrecruiters URL  
                if 'careers.smartrecruiters.com' in domain:
                    path_parts = parsed.path.strip('/').split('/')
                    if path_parts and path_parts[0]:
                        return f"https://{path_parts[0]}.com"
                return f"https://{domain}"
            else:
                # For direct company career pages, this is already the main domain
                return f"https://{domain}"
                
        except Exception as e:
            logger.debug(f"Could not extract website from {uri}: {e}")
            return uri
    
    def process_companies(self):
        """Process companies and extract website information"""
        for company_data in self.companies_data:
            try:
                name = company_data.get('name', 'Unknown')
                uri = company_data.get('uri', '')
                
                if uri:
                    self.stats["career_pages_found"] += 1
                    
                    # Extract main website
                    website = self.extract_website_from_uri(uri)
                    if website and website != uri:
                        self.stats["websites_found"] += 1
                    
                    # Store processed data
                    company_data['processed_website'] = website
                    company_data['career_page'] = uri
                    
            except Exception as e:
                logger.error(f"Error processing company {name}: {e}")
                continue
    
    async def update_database(self):
        """Update MongoDB with website information"""
        try:
            for company_data in self.companies_data:
                try:
                    name = company_data.get('name', 'Unknown')
                    website = company_data.get('processed_website', '')
                    career_page = company_data.get('career_page', '')
                    
                    if not career_page:
                        continue
                    
                    # Update jobs collection with company website info
                    result = await db.jobs.update_many(
                        {"company": name},
                        {
                            "$set": {
                                "company_website": website,
                                "company_careers_url": career_page,
                                "website_updated_at": datetime.now()
                            }
                        }
                    )
                    
                    if result.modified_count > 0:
                        self.stats["updated_companies"] += 1
                        logger.info(f"✅ Updated {result.modified_count} jobs for {name}")
                    
                    # Also update/create in companies collection
                    await db.companies.update_one(
                        {"name": name},
                        {
                            "$set": {
                                "name": name,
                                "website": website,
                                "careers_url": career_page,
                                "updated_at": datetime.now()
                            }
                        },
                        upsert=True
                    )
                    
                except Exception as e:
                    logger.error(f"Error updating database for {name}: {e}")
                    continue
                    
            logger.info(f"✅ Database update completed: {self.stats['updated_companies']} companies updated")
            
        except Exception as e:
            logger.error(f"❌ Database update failed: {str(e)}")
            raise
    
    def print_stats(self):
        """Print processing statistics"""
        print(f"\n📊 Company Website Enrichment Results:")
        print(f"Total companies processed: {self.stats['total_companies']}")
        print(f"Career pages found: {self.stats['career_pages_found']}")
        print(f"Websites extracted: {self.stats['websites_found']}")
        print(f"Database records updated: {self.stats['updated_companies']}")
        print(f"Success rate: {(self.stats['updated_companies']/self.stats['total_companies'])*100:.1f}%")

async def main():
    """Main function"""
    enricher = CompanyWebsiteEnricher()
    
    try:
        # Load data
        enricher.load_distill_data()
        
        # Process companies
        enricher.process_companies()
        
        # Update database
        await enricher.update_database()
        
        # Print results
        enricher.print_stats()
        
        print("\n✅ Company website enrichment completed successfully!")
        
    except Exception as e:
        logger.error(f"❌ Script failed: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main()) 