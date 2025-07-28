#!/usr/bin/env python3
"""
Distill Crawler Cronjob for Buzz2Remote-Companies
Monitors company job postings and collects new listings
"""

import os
import sys
import json
import logging
import requests
from datetime import datetime, timedelta
from pymongo import MongoClient
from urllib.parse import urljoin, urlparse
import time
import hashlib

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DistillCrawler:
    def __init__(self):
        """Initialize Distill Crawler"""
        self.mongo_uri = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/buzz2remote')
        self.client = MongoClient(self.mongo_uri)
        self.db = self.client.buzz2remote
        self.companies_collection = self.db.companies
        self.jobs_collection = self.db.jobs
        self.crawl_logs_collection = self.db.crawl_logs
        
        # Distill.io webhook URL (if using Distill.io service)
        self.distill_webhook_url = os.getenv('DISTILL_WEBHOOK_URL')
        
        # Company monitoring URLs
        self.company_urls = [
            {
                'name': 'Remote.co',
                'url': 'https://remote.co/remote-jobs/',
                'type': 'job_board',
                'selector': '.job_board_job',
                'frequency': 'hourly'
            },
            {
                'name': 'AngelList',
                'url': 'https://angel.co/jobs',
                'type': 'job_board', 
                'selector': '[data-test="JobSearchResultJobTitle"]',
                'frequency': 'daily'
            },
            {
                'name': 'FlexJobs',
                'url': 'https://www.flexjobs.com/search',
                'type': 'job_board',
                'selector': '.job',
                'frequency': 'daily'
            },
            {
                'name': 'Stack Overflow Jobs',
                'url': 'https://stackoverflow.com/jobs',
                'type': 'job_board',
                'selector': '[data-jobid]',
                'frequency': 'daily'
            },
            {
                'name': 'Dice',
                'url': 'https://www.dice.com/jobs',
                'type': 'job_board',
                'selector': '.card-title-link',
                'frequency': 'daily'
            }
        ]
        
    def fetch_page_content(self, url, timeout=30):
        """Fetch page content with error handling"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=timeout)
            response.raise_for_status()
            
            return {
                'content': response.text,
                'status_code': response.status_code,
                'content_length': len(response.text),
                'timestamp': datetime.now()
            }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Error fetching {url}: {e}")
            return None
    
    def generate_content_hash(self, content):
        """Generate SHA256 hash of content for change detection"""
        return hashlib.sha256(content.encode('utf-8')).hexdigest()
    
    def detect_changes(self, company_name, current_content):
        """Detect if content has changed since last crawl"""
        try:
            current_hash = self.generate_content_hash(current_content)
            
            # Get last crawl data
            last_crawl = self.crawl_logs_collection.find_one(
                {'company_name': company_name},
                sort=[('timestamp', -1)]
            )
            
            if not last_crawl:
                logger.info(f"🆕 First crawl for {company_name}")
                return True, current_hash
            
            last_hash = last_crawl.get('content_hash', '')
            
            if current_hash != last_hash:
                logger.info(f"🔄 Content changed for {company_name}")
                return True, current_hash
            else:
                logger.info(f"✅ No changes detected for {company_name}")
                return False, current_hash
                
        except Exception as e:
            logger.error(f"❌ Error detecting changes for {company_name}: {e}")
            return True, None  # Assume changes on error
    
    def parse_job_listings(self, content, company_config):
        """Parse job listings from HTML content"""
        try:
            from bs4 import BeautifulSoup
            
            soup = BeautifulSoup(content, 'html.parser')
            job_elements = soup.select(company_config['selector'])
            
            jobs = []
            for element in job_elements:
                try:
                    # Extract job information based on common patterns
                    title_elem = element.find(['h1', 'h2', 'h3', 'a']) or element
                    title = title_elem.get_text(strip=True) if title_elem else 'Unknown Title'
                    
                    # Try to find link
                    link_elem = element.find('a') or element
                    link = link_elem.get('href', '') if link_elem else ''
                    
                    # Make relative URLs absolute
                    if link and not link.startswith('http'):
                        base_url = f"{urlparse(company_config['url']).scheme}://{urlparse(company_config['url']).netloc}"
                        link = urljoin(base_url, link)
                    
                    # Extract company name from parent elements
                    company_elem = element.find_parent()
                    company = company_config['name']
                    
                    # Try to extract location
                    location_indicators = ['location', 'city', 'remote', 'place']
                    location = 'Not specified'
                    
                    for indicator in location_indicators:
                        loc_elem = element.find(attrs={'class': lambda x: x and indicator in x.lower()})
                        if loc_elem:
                            location = loc_elem.get_text(strip=True)
                            break
                    
                    job = {
                        'title': title,
                        'company': company,
                        'location': location,
                        'link': link,
                        'source': 'distill_crawler',
                        'source_url': company_config['url'],
                        'crawled_at': datetime.now(),
                        'job_id': hashlib.md5(f"{title}{company}{link}".encode()).hexdigest()
                    }
                    
                    jobs.append(job)
                    
                except Exception as e:
                    logger.warning(f"⚠️ Error parsing job element: {e}")
                    continue
            
            logger.info(f"📋 Parsed {len(jobs)} jobs from {company_config['name']}")
            return jobs
            
        except ImportError:
            logger.error("❌ BeautifulSoup not installed. Install with: pip install beautifulsoup4")
            return []
        except Exception as e:
            logger.error(f"❌ Error parsing job listings: {e}")
            return []
    
    def save_jobs_to_database(self, jobs):
        """Save new jobs to database"""
        try:
            new_jobs_count = 0
            updated_jobs_count = 0
            
            for job in jobs:
                # Check if job already exists
                existing_job = self.jobs_collection.find_one({
                    'job_id': job['job_id']
                })
                
                if existing_job:
                    # Update existing job
                    self.jobs_collection.update_one(
                        {'job_id': job['job_id']},
                        {'$set': {
                            'last_seen': datetime.now(),
                            'crawled_at': job['crawled_at']
                        }}
                    )
                    updated_jobs_count += 1
                else:
                    # Insert new job
                    job['created_at'] = datetime.now()
                    job['status'] = 'active'
                    job['job_type'] = 'Full-time'  # Default
                    job['skills'] = []  # Will be filled by skill extraction
                    
                    self.jobs_collection.insert_one(job)
                    new_jobs_count += 1
            
            logger.info(f"💾 Saved {new_jobs_count} new jobs, updated {updated_jobs_count} existing jobs")
            
            return {
                'new_jobs': new_jobs_count,
                'updated_jobs': updated_jobs_count,
                'total_processed': len(jobs)
            }
            
        except Exception as e:
            logger.error(f"❌ Error saving jobs to database: {e}")
            return {'new_jobs': 0, 'updated_jobs': 0, 'total_processed': 0}
    
    def log_crawl_activity(self, company_name, url, content_hash, job_count, status='success'):
        """Log crawl activity to database"""
        try:
            log_entry = {
                'company_name': company_name,
                'url': url,
                'content_hash': content_hash,
                'job_count': job_count,
                'status': status,
                'timestamp': datetime.now(),
                'crawler_type': 'distill'
            }
            
            self.crawl_logs_collection.insert_one(log_entry)
            
        except Exception as e:
            logger.error(f"❌ Error logging crawl activity: {e}")
    
    def should_crawl_company(self, company_config):
        """Determine if company should be crawled based on frequency"""
        try:
            frequency = company_config.get('frequency', 'daily')
            last_crawl = self.crawl_logs_collection.find_one(
                {'company_name': company_config['name']},
                sort=[('timestamp', -1)]
            )
            
            if not last_crawl:
                return True  # First crawl
            
            last_crawl_time = last_crawl['timestamp']
            now = datetime.now()
            
            if frequency == 'hourly':
                return (now - last_crawl_time) >= timedelta(hours=1)
            elif frequency == 'daily':
                return (now - last_crawl_time) >= timedelta(days=1)
            elif frequency == 'weekly':
                return (now - last_crawl_time) >= timedelta(days=7)
            else:
                return True  # Default to crawl
                
        except Exception as e:
            logger.warning(f"⚠️ Error checking crawl frequency: {e}")
            return True  # Default to crawl on error
    
    def crawl_company(self, company_config):
        """Crawl a single company's job board"""
        company_name = company_config['name']
        url = company_config['url']
        
        logger.info(f"🕷️ Starting crawl for {company_name} at {url}")
        
        try:
            # Check if we should crawl based on frequency
            if not self.should_crawl_company(company_config):
                logger.info(f"⏭️ Skipping {company_name} - not time to crawl yet")
                return {'status': 'skipped', 'reason': 'frequency_limit'}
            
            # Fetch page content
            page_data = self.fetch_page_content(url)
            
            if not page_data:
                self.log_crawl_activity(company_name, url, None, 0, 'failed')
                return {'status': 'failed', 'reason': 'fetch_error'}
            
            # Detect changes
            content_changed, content_hash = self.detect_changes(company_name, page_data['content'])
            
            if not content_changed:
                self.log_crawl_activity(company_name, url, content_hash, 0, 'no_changes')
                return {'status': 'no_changes', 'content_hash': content_hash}
            
            # Parse job listings
            jobs = self.parse_job_listings(page_data['content'], company_config)
            
            # Save jobs to database
            save_result = self.save_jobs_to_database(jobs)
            
            # Log activity
            self.log_crawl_activity(company_name, url, content_hash, len(jobs), 'success')
            
            logger.info(f"✅ Completed crawl for {company_name}: {save_result['new_jobs']} new jobs")
            
            return {
                'status': 'success',
                'company': company_name,
                'jobs_found': len(jobs),
                'new_jobs': save_result['new_jobs'],
                'updated_jobs': save_result['updated_jobs'],
                'content_hash': content_hash
            }
            
        except Exception as e:
            logger.error(f"❌ Error crawling {company_name}: {e}")
            self.log_crawl_activity(company_name, url, None, 0, 'error')
            return {'status': 'error', 'reason': str(e)}
    
    def run_full_crawl(self):
        """Run full crawl across all configured companies"""
        logger.info("🚀 Starting Distill crawler for Buzz2Remote-Companies")
        
        results = []
        total_new_jobs = 0
        total_updated_jobs = 0
        
        for company_config in self.company_urls:
            try:
                result = self.crawl_company(company_config)
                results.append(result)
                
                if result['status'] == 'success':
                    total_new_jobs += result.get('new_jobs', 0)
                    total_updated_jobs += result.get('updated_jobs', 0)
                
                # Delay between requests to be respectful
                time.sleep(2)
                
            except Exception as e:
                logger.error(f"❌ Error in full crawl for {company_config['name']}: {e}")
                results.append({
                    'status': 'error',
                    'company': company_config['name'],
                    'reason': str(e)
                })
        
        # Generate summary
        summary = {
            'timestamp': datetime.now(),
            'companies_crawled': len([r for r in results if r['status'] in ['success', 'no_changes']]),
            'companies_failed': len([r for r in results if r['status'] in ['failed', 'error']]),
            'companies_skipped': len([r for r in results if r['status'] == 'skipped']),
            'total_new_jobs': total_new_jobs,
            'total_updated_jobs': total_updated_jobs,
            'results': results
        }
        
        logger.info(f"✅ Distill crawl completed: {total_new_jobs} new jobs, {total_updated_jobs} updated")
        
        return summary
    
    def cleanup_old_logs(self, days_to_keep=7):
        """Clean up old crawl logs"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days_to_keep)
            
            result = self.crawl_logs_collection.delete_many({
                'timestamp': {'$lt': cutoff_date}
            })
            
            logger.info(f"🧹 Cleaned up {result.deleted_count} old crawl logs")
            return result.deleted_count
            
        except Exception as e:
            logger.error(f"❌ Error cleaning up crawl logs: {e}")
            return 0

def main():
    """Main function for cronjob execution"""
    try:
        crawler = DistillCrawler()
        
        # Run full crawl
        summary = crawler.run_full_crawl()
        
        # Cleanup old logs
        crawler.cleanup_old_logs()
        
        print(f"✅ Distill crawler completed successfully")
        print(f"🏢 Companies crawled: {summary['companies_crawled']}")
        print(f"📋 New jobs found: {summary['total_new_jobs']}")
        print(f"🔄 Jobs updated: {summary['total_updated_jobs']}")
        
        return 0
        
    except Exception as e:
        logger.error(f"❌ Distill crawler failed: {e}")
        return 1

if __name__ == "__main__":
    exit(main()) 