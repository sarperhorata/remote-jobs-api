#!/usr/bin/env python3
"""
External Job APIs Integration for Buzz2Remote
3rd party job API'lerini entegre edip job ve company mapping yapar
"""

import os
import requests
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from service_notifications import ServiceNotifier
import hashlib

@dataclass
class JobData:
    """Standard job data structure"""
    title: str
    company: str
    location: str
    description: str
    url: str
    salary: Optional[str] = None
    job_type: Optional[str] = None
    posted_date: Optional[str] = None
    source: str = "external_api"
    external_id: str = ""

@dataclass
class CompanyData:
    """Standard company data structure"""
    name: str
    description: Optional[str] = None
    website: Optional[str] = None
    industry: Optional[str] = None
    size: Optional[str] = None
    location: Optional[str] = None

class RateLimiter:
    """Rate limiting for API calls"""
    
    def __init__(self, max_requests: int, time_period_days: int):
        self.max_requests = max_requests
        self.time_period_days = time_period_days
        self.requests_file = f".api_requests_{max_requests}_{time_period_days}.json"
        self.requests_history = self._load_history()
    
    def _load_history(self) -> List[str]:
        """Load request history from file"""
        try:
            if os.path.exists(self.requests_file):
                with open(self.requests_file, 'r') as f:
                    return json.load(f)
            return []
        except:
            return []
    
    def _save_history(self):
        """Save request history to file"""
        try:
            with open(self.requests_file, 'w') as f:
                json.dump(self.requests_history, f)
        except Exception as e:
            print(f"❌ Error saving rate limit history: {e}")
    
    def _clean_old_requests(self):
        """Remove old requests outside time window"""
        cutoff_date = datetime.now() - timedelta(days=self.time_period_days)
        cutoff_str = cutoff_date.isoformat()
        self.requests_history = [req for req in self.requests_history if req > cutoff_str]
    
    def can_make_request(self) -> bool:
        """Check if we can make a request"""
        self._clean_old_requests()
        return len(self.requests_history) < self.max_requests
    
    def record_request(self):
        """Record a new request"""
        self.requests_history.append(datetime.now().isoformat())
        self._save_history()
    
    def requests_remaining(self) -> int:
        """Get remaining requests"""
        self._clean_old_requests()
        return max(0, self.max_requests - len(self.requests_history))
    
    def next_reset_date(self) -> Optional[datetime]:
        """Get next reset date"""
        if not self.requests_history:
            return None
        oldest_request = min(self.requests_history)
        return datetime.fromisoformat(oldest_request) + timedelta(days=self.time_period_days)

class FantasticJobsAPI:
    """Fantastic Jobs API integration"""
    
    def __init__(self):
        self.base_url = "https://active-jobs-db.p.rapidapi.com"
        self.api_key = os.getenv('RAPIDAPI_KEY', '9c58f51d0dmsh97f8afac642c5f1p1fd8a9jsn2aae92a07f7a')
        self.headers = {
            'x-rapidapi-host': 'active-jobs-db.p.rapidapi.com',
            'x-rapidapi-key': self.api_key
        }
        # 15 requests per month = 30 days
        self.rate_limiter = RateLimiter(max_requests=15, time_period_days=30)
        self.notifier = ServiceNotifier()
        
    def _make_request(self, endpoint: str, params: Dict) -> Optional[Dict]:
        """Make API request with rate limiting"""
        
        if not self.rate_limiter.can_make_request():
            remaining = self.rate_limiter.requests_remaining()
            next_reset = self.rate_limiter.next_reset_date()
            
            self.notifier._send_message(f"""⚠️ <b>FANTASTIC JOBS API - RATE LIMIT</b>

❌ <b>Rate limit exceeded</b>
📊 <b>Remaining requests:</b> {remaining}/15
🕐 <b>Next reset:</b> {next_reset.strftime('%Y-%m-%d %H:%M') if next_reset else 'N/A'}

⏳ <b>Waiting for rate limit reset...</b>""")
            return None
        
        try:
            url = f"{self.base_url}/{endpoint}"
            response = requests.get(url, headers=self.headers, params=params, timeout=30)
            
            self.rate_limiter.record_request()
            
            if response.status_code == 200:
                data = response.json()
                
                self.notifier._send_message(f"""✅ <b>FANTASTIC JOBS API - SUCCESS</b>

🎯 <b>Endpoint:</b> {endpoint}
📊 <b>Status:</b> {response.status_code}
📦 <b>Jobs found:</b> {len(data.get('jobs', []))}
⚡ <b>Remaining requests:</b> {self.rate_limiter.requests_remaining()}/15

🕐 <b>Time:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}""")
                
                return data
            else:
                error_msg = f"HTTP {response.status_code}: {response.text[:200]}"
                self.notifier._send_message(f"""❌ <b>FANTASTIC JOBS API - ERROR</b>

🎯 <b>Endpoint:</b> {endpoint}
📊 <b>Status:</b> {response.status_code}
❌ <b>Error:</b> {error_msg}
⚡ <b>Remaining requests:</b> {self.rate_limiter.requests_remaining()}/15""")
                return None
                
        except Exception as e:
            self.notifier._send_message(f"""❌ <b>FANTASTIC JOBS API - EXCEPTION</b>

🎯 <b>Endpoint:</b> {endpoint}
❌ <b>Error:</b> {str(e)[:200]}
⚡ <b>Remaining requests:</b> {self.rate_limiter.requests_remaining()}/15""")
            return None
    
    def fetch_remote_jobs(self, limit: int = 100) -> List[JobData]:
        """Fetch remote jobs from Fantastic Jobs API"""
        
        # Try different endpoints that might be available
        endpoints_to_try = [
            ("active-ats-1h", {
                "offset": 0,
                "title_filter": '"remote"',
                "location_filter": '"United States" OR "United Kingdom" OR "Canada" OR "remote"',
                "description_type": "text"
            }),
            ("jobs", {
                "q": "remote",
                "location": "remote",
                "limit": min(limit, 100)
            }),
            ("search", {
                "query": "remote work",
                "limit": min(limit, 100)
            })
        ]
        
        jobs = []
        
        for endpoint, params in endpoints_to_try:
            data = self._make_request(endpoint, params)
            
            if data and 'jobs' in data:
                for job_data in data['jobs'][:limit]:
                    job = self._parse_job_data(job_data)
                    if job:
                        jobs.append(job)
                break  # Success, don't try other endpoints
        
        return jobs[:limit]  # Respect limit
    
    def _parse_job_data(self, job_data: Dict) -> Optional[JobData]:
        """Parse job data from API response"""
        try:
            # Try different possible field names
            title = job_data.get('title') or job_data.get('job_title') or job_data.get('name', '')
            company = job_data.get('company') or job_data.get('company_name') or job_data.get('employer', '')
            location = job_data.get('location') or job_data.get('job_location') or job_data.get('city', '')
            description = job_data.get('description') or job_data.get('job_description') or ''
            url = job_data.get('url') or job_data.get('job_url') or job_data.get('apply_url', '')
            
            # Generate external ID
            external_id = job_data.get('id') or hashlib.md5(f"{title}{company}{location}".encode()).hexdigest()[:16]
            
            if title and company:
                return JobData(
                    title=title,
                    company=company,
                    location=location,
                    description=description,
                    url=url,
                    salary=job_data.get('salary'),
                    job_type=job_data.get('job_type', 'Remote'),
                    posted_date=job_data.get('posted_date') or job_data.get('created_at'),
                    source="fantastic_jobs_api",
                    external_id=external_id
                )
        except Exception as e:
            print(f"❌ Error parsing job data: {e}")
        
        return None

class ExternalJobAPIManager:
    """Manage all external job API integrations"""
    
    def __init__(self):
        self.apis = {
            'fantastic_jobs': FantasticJobsAPI()
        }
        self.notifier = ServiceNotifier()
    
    def fetch_all_jobs(self, max_jobs_per_api: int = 100) -> Dict[str, List[JobData]]:
        """Fetch jobs from all available APIs"""
        
        all_jobs = {}
        total_jobs = 0
        
        for api_name, api_instance in self.apis.items():
            try:
                print(f"🔄 Fetching jobs from {api_name}...")
                jobs = api_instance.fetch_remote_jobs(limit=max_jobs_per_api)
                all_jobs[api_name] = jobs
                total_jobs += len(jobs)
                
                print(f"✅ {api_name}: {len(jobs)} jobs fetched")
                
            except Exception as e:
                print(f"❌ Error fetching from {api_name}: {e}")
                all_jobs[api_name] = []
        
        # Send summary notification
        self.notifier._send_message(f"""📦 <b>EXTERNAL APIS - BATCH COMPLETE</b>

✅ <b>Total Jobs Fetched:</b> {total_jobs}

🔧 <b>API Results:</b>
• Fantastic Jobs: {len(all_jobs.get('fantastic_jobs', []))} jobs

🕐 <b>Time:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
🎯 <b>System:</b> buzz2remote.com""")
        
        return all_jobs
    
    def save_jobs_to_database(self, jobs_data: Dict[str, List[JobData]]) -> Dict[str, int]:
        """Save fetched jobs to database"""
        
        # This would integrate with your existing database
        # For now, let's save to JSON for testing
        
        results = {}
        
        for api_name, jobs in jobs_data.items():
            saved_count = 0
            
            # Save to JSON file for testing
            filename = f"external_jobs_{api_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            
            jobs_json = []
            for job in jobs:
                jobs_json.append({
                    'title': job.title,
                    'company': job.company,
                    'location': job.location,
                    'description': job.description[:500] + "..." if len(job.description) > 500 else job.description,
                    'url': job.url,
                    'salary': job.salary,
                    'job_type': job.job_type,
                    'posted_date': job.posted_date,
                    'source': job.source,
                    'external_id': job.external_id,
                    'fetched_at': datetime.now().isoformat()
                })
            
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(jobs_json, f, indent=2, ensure_ascii=False)
                saved_count = len(jobs)
                print(f"✅ Saved {saved_count} jobs from {api_name} to {filename}")
            except Exception as e:
                print(f"❌ Error saving {api_name} jobs: {e}")
            
            results[api_name] = saved_count
        
        return results

def run_external_api_crawler():
    """Main function to run external API crawler"""
    
    print("🚀 Starting External Job API Crawler")
    print("=" * 50)
    
    manager = ExternalJobAPIManager()
    
    # Fetch jobs from all APIs
    jobs_data = manager.fetch_all_jobs(max_jobs_per_api=100)
    
    # Save to database
    results = manager.save_jobs_to_database(jobs_data)
    
    # Print summary
    total_saved = sum(results.values())
    print(f"\n📊 SUMMARY:")
    print(f"✅ Total Jobs Saved: {total_saved}")
    for api_name, count in results.items():
        print(f"• {api_name}: {count} jobs")
    
    return results

if __name__ == "__main__":
    # Test the system
    run_external_api_crawler() 