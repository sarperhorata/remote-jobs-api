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
import xml.etree.ElementTree as ET

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

class APIErrorHandler:
    """Handle API errors and manage disabled endpoints"""
    
    def __init__(self):
        self.disabled_endpoints_file = ".disabled_api_endpoints.json"
        self.quota_exceeded_file = ".quota_exceeded_apis.json"
        self.disabled_endpoints = self._load_disabled_endpoints()
        self.quota_exceeded = self._load_quota_exceeded()
        self.notifier = ServiceNotifier()
    
    def _load_disabled_endpoints(self) -> Dict[str, Dict]:
        """Load disabled endpoints from file"""
        try:
            if os.path.exists(self.disabled_endpoints_file):
                with open(self.disabled_endpoints_file, 'r') as f:
                    return json.load(f)
            return {}
        except:
            return {}
    
    def _save_disabled_endpoints(self):
        """Save disabled endpoints to file"""
        try:
            with open(self.disabled_endpoints_file, 'w') as f:
                json.dump(self.disabled_endpoints, f, indent=2)
        except Exception as e:
            print(f"❌ Error saving disabled endpoints: {e}")
    
    def _load_quota_exceeded(self) -> Dict[str, Dict]:
        """Load quota exceeded APIs from file"""
        try:
            if os.path.exists(self.quota_exceeded_file):
                with open(self.quota_exceeded_file, 'r') as f:
                    return json.load(f)
            return {}
        except:
            return {}
    
    def _save_quota_exceeded(self):
        """Save quota exceeded APIs to file"""
        try:
            with open(self.quota_exceeded_file, 'w') as f:
                json.dump(self.quota_exceeded, f, indent=2)
        except Exception as e:
            print(f"❌ Error saving quota exceeded: {e}")
    
    def handle_api_error(self, api_name: str, endpoint: str, status_code: int, error_message: str):
        """Handle API errors based on status code and message"""
        
        # Check for disabled endpoint error
        if "This endpoint is disabled for your subscription" in error_message:
            self.disable_endpoint(api_name, endpoint, error_message)
            return
        
        # Check for quota exceeded error
        if "You have exceeded monthly quota" in error_message or status_code == 429:
            self.mark_quota_exceeded(api_name, error_message)
            return
        
        # Check for other 4xx errors
        if 400 <= status_code < 500:
            self.notifier._send_message(f"""⚠️ <b>{api_name} - CLIENT ERROR</b>

🎯 <b>Endpoint:</b> {endpoint}
📊 <b>Status:</b> {status_code}
❌ <b>Error:</b> {error_message[:200]}

🔍 <b>Action:</b> Check API configuration""")
        
        # Check for 5xx errors
        elif 500 <= status_code < 600:
            self.notifier._send_message(f"""🔥 <b>{api_name} - SERVER ERROR</b>

🎯 <b>Endpoint:</b> {endpoint}
📊 <b>Status:</b> {status_code}
❌ <b>Error:</b> {error_message[:200]}

⏳ <b>Action:</b> Will retry later""")
    
    def disable_endpoint(self, api_name: str, endpoint: str, reason: str):
        """Disable an endpoint permanently"""
        key = f"{api_name}_{endpoint}"
        
        if key not in self.disabled_endpoints:
            self.disabled_endpoints[key] = {
                "api_name": api_name,
                "endpoint": endpoint,
                "disabled_at": datetime.now().isoformat(),
                "reason": reason
            }
            self._save_disabled_endpoints()
            
            self.notifier._send_message(f"""🚫 <b>{api_name} - ENDPOINT DISABLED</b>

🎯 <b>Endpoint:</b> {endpoint}
❌ <b>Reason:</b> {reason}
🕐 <b>Disabled at:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

⚠️ <b>This endpoint will not be used anymore!</b>""")
    
    def mark_quota_exceeded(self, api_name: str, reason: str):
        """Mark API as quota exceeded for current month"""
        current_month = datetime.now().strftime('%Y-%m')
        
        if api_name not in self.quota_exceeded:
            self.quota_exceeded[api_name] = {}
        
        if current_month not in self.quota_exceeded[api_name]:
            self.quota_exceeded[api_name][current_month] = {
                "exceeded_at": datetime.now().isoformat(),
                "reason": reason
            }
            self._save_quota_exceeded()
            
            self.notifier._send_message(f"""📛 <b>{api_name} - QUOTA EXCEEDED</b>

❌ <b>Reason:</b> {reason}
📅 <b>Month:</b> {current_month}
🕐 <b>Time:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

⏸️ <b>This API will be paused until next month!</b>""")
    
    def is_endpoint_disabled(self, api_name: str, endpoint: str) -> bool:
        """Check if an endpoint is disabled"""
        key = f"{api_name}_{endpoint}"
        return key in self.disabled_endpoints
    
    def is_quota_exceeded(self, api_name: str) -> bool:
        """Check if API quota is exceeded for current month"""
        current_month = datetime.now().strftime('%Y-%m')
        return api_name in self.quota_exceeded and current_month in self.quota_exceeded[api_name]
    
    def clean_old_quota_records(self):
        """Clean old quota records from previous months"""
        current_month = datetime.now().strftime('%Y-%m')
        
        for api_name in list(self.quota_exceeded.keys()):
            # Remove old month records
            for month in list(self.quota_exceeded[api_name].keys()):
                if month < current_month:
                    del self.quota_exceeded[api_name][month]
            
            # Remove API if no records left
            if not self.quota_exceeded[api_name]:
                del self.quota_exceeded[api_name]
        
        self._save_quota_exceeded()

class FantasticJobsAPI:
    """Fantastic Jobs API integration"""
    
    def __init__(self):
        self.base_url = "https://active-jobs-db.p.rapidapi.com"
        self.api_key = os.getenv('RAPIDAPI_KEY')
        self.headers = {
            "X-RapidAPI-Key": self.api_key,
            "X-RapidAPI-Host": self.base_url.replace("https://", "")
        }
        # 15 requests per month = 30 days
        self.rate_limiter = RateLimiter(max_requests=15, time_period_days=30)
        self.notifier = ServiceNotifier()
        self.error_handler = APIErrorHandler()
        
    def _make_request(self, endpoint: str, params: Dict) -> Optional[Dict]:
        """Make API request with rate limiting"""
        
        # Check if quota is exceeded
        if self.error_handler.is_quota_exceeded("FANTASTIC_JOBS"):
            self.notifier._send_message(f"""⏸️ <b>FANTASTIC JOBS API - PAUSED</b>

📛 <b>Status:</b> Quota exceeded for this month
⏳ <b>Will resume:</b> Next month

Skipping API call...""")
            return None
        
        # Check if endpoint is disabled
        if self.error_handler.is_endpoint_disabled("FANTASTIC_JOBS", endpoint):
            self.notifier._send_message(f"""🚫 <b>FANTASTIC JOBS API - ENDPOINT DISABLED</b>

🎯 <b>Endpoint:</b> {endpoint}
❌ <b>Status:</b> Permanently disabled

Skipping API call...""")
            return None
        
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
                
                # Handle API errors
                self.error_handler.handle_api_error("FANTASTIC_JOBS", endpoint, response.status_code, response.text)
                
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
            
            # Generate external ID using secure hash
            external_id = job_data.get('id') or hashlib.sha256(f"{title}{company}{location}".encode()).hexdigest()[:16]
            
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

class JobPostingFeedAPI:
    """Job Posting Feed API integration - 5 requests/month, up to 500 jobs per request"""
    
    def __init__(self):
        self.base_url = "https://job-posting-feed-api.p.rapidapi.com"
        self.api_key = os.getenv('RAPIDAPI_KEY')
        self.headers = {
            "X-RapidAPI-Key": self.api_key,
            "X-RapidAPI-Host": self.base_url.replace("https://", "")
        }
        # 5 requests per month = 30 days
        self.rate_limiter = RateLimiter(max_requests=5, time_period_days=30)
        self.notifier = ServiceNotifier()
        
    def _make_request(self, endpoint: str, params: Dict) -> Optional[Dict]:
        """Make API request with rate limiting"""
        
        if not self.rate_limiter.can_make_request():
            remaining = self.rate_limiter.requests_remaining()
            next_reset = self.rate_limiter.next_reset_date()
            
            self.notifier._send_message(f"""⚠️ <b>JOB POSTING FEED API - RATE LIMIT</b>

❌ <b>Rate limit exceeded</b>
📊 <b>Remaining requests:</b> {remaining}/5
🕐 <b>Next reset:</b> {next_reset.strftime('%Y-%m-%d %H:%M') if next_reset else 'N/A'}

⏳ <b>Bu API çok sınırlı (5/month)!</b>""")
            return None
        
        try:
            url = f"{self.base_url}/{endpoint}"
            response = requests.get(url, headers=self.headers, params=params, timeout=30)
            
            self.rate_limiter.record_request()
            
            if response.status_code == 200:
                data = response.json()
                job_count = len(data) if isinstance(data, list) else len(data.get('jobs', []))
                
                self.notifier._send_message(f"""✅ <b>JOB POSTING FEED API - SUCCESS</b>

🎯 <b>Endpoint:</b> {endpoint}
📊 <b>Status:</b> {response.status_code}
📦 <b>Jobs found:</b> {job_count}
⚡ <b>Remaining requests:</b> {self.rate_limiter.requests_remaining()}/5

🕐 <b>Time:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}""")
                
                return data
            else:
                error_msg = f"HTTP {response.status_code}: {response.text[:200]}"
                self.notifier._send_message(f"""❌ <b>JOB POSTING FEED API - ERROR</b>

🎯 <b>Endpoint:</b> {endpoint}
📊 <b>Status:</b> {response.status_code}
❌ <b>Error:</b> {error_msg}
⚡ <b>Remaining requests:</b> {self.rate_limiter.requests_remaining()}/5""")
                return None
                
        except Exception as e:
            self.notifier._send_message(f"""❌ <b>JOB POSTING FEED API - EXCEPTION</b>

🎯 <b>Endpoint:</b> {endpoint}
❌ <b>Error:</b> {str(e)[:200]}
⚡ <b>Remaining requests:</b> {self.rate_limiter.requests_remaining()}/5""")
            return None
    
    def fetch_remote_jobs(self, limit: int = 500) -> List[JobData]:
        """Fetch remote jobs from Job Posting Feed API"""
        
        # Bu API'nin bilinen endpoints'leri
        endpoints_to_try = [
            ("active-ats-6m", {
                "description_type": "text"
            }),
            ("active-ats-1h", {
                "description_type": "text"
            })
        ]
        
        jobs = []
        
        for endpoint, params in endpoints_to_try:
            data = self._make_request(endpoint, params)
            
            if data:
                # Response direkt liste olabilir veya jobs key'i içerebilir
                jobs_list = data if isinstance(data, list) else data.get('jobs', [])
                
                for job_data in jobs_list[:limit]:
                    job = self._parse_job_data(job_data)
                    if job:
                        jobs.append(job)
                        
                        # Remote job'ları filtrele
                        if not self._is_remote_job(job):
                            jobs.remove(job)
                
                break  # Başarılı olunca diğer endpoint'leri deneme
        
        return jobs[:limit]
    
    def _is_remote_job(self, job: JobData) -> bool:
        """Check if job is remote based on title, location, or description"""
        remote_keywords = ['remote', 'work from home', 'telecommute', 'distributed', 'virtual']
        
        # Title check
        if any(keyword in job.title.lower() for keyword in remote_keywords):
            return True
        
        # Location check
        if any(keyword in job.location.lower() for keyword in remote_keywords):
            return True
        
        # Description check (first 500 chars for performance)
        description_start = job.description[:500].lower()
        if any(keyword in description_start for keyword in remote_keywords):
            return True
        
        return False
    
    def _parse_job_data(self, job_data: Dict) -> Optional[JobData]:
        """Parse job data from API response"""
        try:
            # Job Posting Feed API format
            title = job_data.get('title', '')
            company = job_data.get('organization', '')
            
            # Location parsing - can be complex nested structure
            location = self._parse_location(job_data.get('locations_raw', []))
            
            description = job_data.get('description_text', '')
            url = job_data.get('url', '')
            
            # Salary parsing
            salary = self._parse_salary(job_data.get('salary_raw'))
            
            # Job type
            employment_type = job_data.get('employment_type')
            job_type = self._parse_employment_type(employment_type)
            
            # Posted date
            posted_date = job_data.get('date_posted') or job_data.get('date_created')
            
            # External ID
            external_id = job_data.get('id', '') or hashlib.md5(f"{title}{company}".encode()).hexdigest()[:16]
            
            if title and company:
                return JobData(
                    title=title,
                    company=company,
                    location=location,
                    description=description,
                    url=url,
                    salary=salary,
                    job_type=job_type,
                    posted_date=posted_date,
                    source="job_posting_feed_api",
                    external_id=external_id
                )
        except Exception as e:
            print(f"❌ Error parsing job data: {e}")
        
        return None
    
    def _parse_location(self, locations_raw: List) -> str:
        """Parse complex location structure"""
        if not locations_raw:
            return "Remote"
        
        location_parts = []
        for loc in locations_raw[:1]:  # Take first location
            if isinstance(loc, dict):
                address = loc.get('address', {})
                if isinstance(address, dict):
                    city = address.get('addressLocality', '')
                    state = address.get('addressRegion', '')
                    country = address.get('addressCountry', '')
                    
                    if city:
                        location_parts.append(city)
                    if state:
                        location_parts.append(state)
                    if country and country != 'US':
                        location_parts.append(country)
        
        return ', '.join(location_parts) if location_parts else "Remote"
    
    def _parse_salary(self, salary_raw) -> Optional[str]:
        """Parse salary information"""
        if not salary_raw:
            return None
        
        if isinstance(salary_raw, dict):
            min_val = salary_raw.get('value', {}).get('minValue')
            max_val = salary_raw.get('value', {}).get('maxValue')
            currency = salary_raw.get('currency', 'USD')
            unit = salary_raw.get('value', {}).get('unitText', 'YEAR')
            
            if min_val and max_val:
                return f"${min_val}-${max_val} {currency}/{unit}"
            elif min_val:
                return f"${min_val}+ {currency}/{unit}"
        
        return str(salary_raw) if salary_raw else None
    
    def _parse_employment_type(self, employment_type) -> str:
        """Parse employment type"""
        if isinstance(employment_type, list) and employment_type:
            return employment_type[0]
        elif isinstance(employment_type, str):
            return employment_type
        return "Full-time"

class RemoteOKAPI:
    """RemoteOK API integration - 24 requests/day"""
    
    def __init__(self):
        self.base_url = "https://jobs-from-remoteok.p.rapidapi.com"
        self.api_key = os.getenv('RAPIDAPI_KEY')
        self.headers = {
            'x-rapidapi-host': 'jobs-from-remoteok.p.rapidapi.com',
            'x-rapidapi-key': self.api_key
        }
        # 24 requests per day = 1 day period
        self.rate_limiter = RateLimiter(max_requests=24, time_period_days=1)
        self.notifier = ServiceNotifier()
        
    def _make_request(self, endpoint: str = "", params: Dict = None) -> Optional[Dict]:
        """Make API request with rate limiting"""
        
        if not self.rate_limiter.can_make_request():
            remaining = self.rate_limiter.requests_remaining()
            next_reset = self.rate_limiter.next_reset_date()
            
            self.notifier._send_message(f"""⚠️ <b>REMOTEOK API - RATE LIMIT</b>

❌ <b>Rate limit exceeded</b>
📊 <b>Remaining requests:</b> {remaining}/24
🕐 <b>Next reset:</b> {next_reset.strftime('%Y-%m-%d %H:%M') if next_reset else 'N/A'}

⏳ <b>Günlük limit doldu!</b>""")
            return None
        
        try:
            url = f"{self.base_url}/{endpoint}" if endpoint else self.base_url
            response = requests.get(url, headers=self.headers, params=params or {}, timeout=30)
            
            self.rate_limiter.record_request()
            
            if response.status_code == 200:
                data = response.json()
                job_count = len(data) if isinstance(data, list) else len(data.get('jobs', []))
                
                self.notifier._send_message(f"""✅ <b>REMOTEOK API - SUCCESS</b>

🎯 <b>Endpoint:</b> {endpoint or 'root'}
📊 <b>Status:</b> {response.status_code}
📦 <b>Jobs found:</b> {job_count}
⚡ <b>Remaining requests:</b> {self.rate_limiter.requests_remaining()}/24

🕐 <b>Time:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}""")
                
                return data
            else:
                error_msg = f"HTTP {response.status_code}: {response.text[:200]}"
                self.notifier._send_message(f"""❌ <b>REMOTEOK API - ERROR</b>

🎯 <b>Endpoint:</b> {endpoint or 'root'}
📊 <b>Status:</b> {response.status_code}
❌ <b>Error:</b> {error_msg}
⚡ <b>Remaining requests:</b> {self.rate_limiter.requests_remaining()}/24""")
                return None
                
        except Exception as e:
            self.notifier._send_message(f"""❌ <b>REMOTEOK API - EXCEPTION</b>

🎯 <b>Endpoint:</b> {endpoint or 'root'}
❌ <b>Error:</b> {str(e)[:200]}
⚡ <b>Remaining requests:</b> {self.rate_limiter.requests_remaining()}/24""")
            return None
    
    def fetch_remote_jobs(self, limit: int = 100) -> List[JobData]:
        """Fetch remote jobs from RemoteOK API"""
        
        jobs = []
        
        # RemoteOK API genellikle root endpoint'te tüm job'ları döndürür
        data = self._make_request()
        
        if data:
            # Response direkt liste olabilir veya jobs key'i içerebilir
            jobs_list = data if isinstance(data, list) else data.get('jobs', [])
            
            for job_data in jobs_list[:limit]:
                job = self._parse_job_data(job_data)
                if job:
                    jobs.append(job)
        
        return jobs[:limit]
    
    def _parse_job_data(self, job_data: Dict) -> Optional[JobData]:
        """Parse job data from RemoteOK API response"""
        try:
            # RemoteOK API format - RemoteOK'den gelen standart format
            title = job_data.get('position', '') or job_data.get('title', '')
            company = job_data.get('company', '')
            
            # Location - remote job'lar için genellikle "Remote" veya "Worldwide"
            location = job_data.get('location', 'Remote')
            if not location or location.lower() in ['', 'null', 'none']:
                location = "Remote"
            
            # Description 
            description = job_data.get('description', '') or job_data.get('text', '')
            
            # URL - RemoteOK'de genellikle slug veya id kullanılır
            job_id = job_data.get('id', '') or job_data.get('slug', '')
            url = f"https://remoteok.io/remote-jobs/{job_id}" if job_id else job_data.get('url', '')
            
            # Salary parsing
            salary = self._parse_salary(job_data)
            
            # Job type - RemoteOK'de genellikle tags'te var
            job_type = self._parse_job_type(job_data)
            
            # Posted date
            posted_date = self._parse_date(job_data.get('date', '')) or job_data.get('epoch', '')
            
            # External ID
            external_id = str(job_id) or hashlib.md5(f"{title}{company}".encode()).hexdigest()[:16]
            
            if title and company:
                return JobData(
                    title=title,
                    company=company,
                    location=location,
                    description=description,
                    url=url,
                    salary=salary,
                    job_type=job_type,
                    posted_date=posted_date,
                    source="remoteok_api",
                    external_id=external_id
                )
        except Exception as e:
            print(f"❌ Error parsing RemoteOK job data: {e}")
        
        return None
    
    def _parse_salary(self, job_data: Dict) -> Optional[str]:
        """Parse salary information from RemoteOK data"""
        # RemoteOK'de salary genellikle min/max olarak geliyor
        salary_min = job_data.get('salary_min')
        salary_max = job_data.get('salary_max')
        
        if salary_min and salary_max:
            return f"${salary_min:,}-${salary_max:,}"
        elif salary_min:
            return f"${salary_min:,}+"
        elif salary_max:
            return f"Up to ${salary_max:,}"
        
        # Tags'te salary bilgisi olabilir
        tags = job_data.get('tags', [])
        if isinstance(tags, list):
            for tag in tags:
                if isinstance(tag, str) and ('$' in tag or 'k' in tag.lower()):
                    return tag
        
        return None
    
    def _parse_job_type(self, job_data: Dict) -> str:
        """Parse job type from RemoteOK data"""
        # Tags'ten job type bilgisini çıkarmaya çalış
        tags = job_data.get('tags', [])
        if isinstance(tags, list):
            for tag in tags:
                if isinstance(tag, str):
                    tag_lower = tag.lower()
                    if tag_lower in ['fulltime', 'full-time', 'full time']:
                        return 'Full-time'
                    elif tag_lower in ['parttime', 'part-time', 'part time']:
                        return 'Part-time'
                    elif tag_lower in ['contract', 'contractor']:
                        return 'Contract'
                    elif tag_lower in ['internship', 'intern']:
                        return 'Internship'
        
        return 'Full-time'  # Default
    
    def _parse_date(self, date_str: str) -> Optional[str]:
        """Parse date from RemoteOK format"""
        if not date_str:
            return None
        
        try:
            # RemoteOK genellikle ISO format kullanır
            if isinstance(date_str, str):
                return date_str
            elif isinstance(date_str, (int, float)):
                # Epoch timestamp ise
                return datetime.fromtimestamp(date_str).isoformat()
        except:
            pass
        
        return str(date_str) if date_str else None

class ArbeitnowFreeAPI:
    """Arbeitnow Free Job Board API - 500,000 requests/month, 1000/hour"""
    
    def __init__(self):
        self.base_url = "https://arbeitnow-free-job-board.p.rapidapi.com"
        self.api_key = os.getenv('RAPIDAPI_KEY')
        self.headers = {
            'Content-Type': 'application/json',
            'x-rapidapi-host': 'arbeitnow-free-job-board.p.rapidapi.com',
            'x-rapidapi-key': self.api_key
        }
        # 500,000 requests per month = 30 days
        self.rate_limiter = RateLimiter(max_requests=500000, time_period_days=30)
        self.notifier = ServiceNotifier()
        
    def _make_request(self, endpoint: str = "api/job-board-api", params: Dict = None) -> Optional[Dict]:
        """Make API request with rate limiting"""
        
        if not self.rate_limiter.can_make_request():
            remaining = self.rate_limiter.requests_remaining()
            next_reset = self.rate_limiter.next_reset_date()
            self.notifier.send_notification(
                f"⚠️ Arbeitnow Free API rate limit reached!\n"
                f"📊 Requests remaining: {remaining}/500000\n"
                f"🕐 Next reset: {next_reset}"
            )
            return None
            
        url = f"{self.base_url}/{endpoint}"
        
        try:
            response = requests.get(url, headers=self.headers, params=params or {}, timeout=30)
            self.rate_limiter.record_request()
            
            if response.status_code == 200:
                data = response.json()
                self.notifier.send_notification(
                    f"✅ Arbeitnow Free API success!\n"
                    f"📊 Jobs fetched: {len(data.get('data', []))}\n"
                    f"📊 Rate limit: {self.rate_limiter.requests_remaining()}/500000"
                )
                return data
            else:
                self.notifier.send_notification(
                    f"❌ Arbeitnow Free API error!\n"
                    f"🔢 Status: {response.status_code}\n"
                    f"📝 Response: {response.text[:200]}"
                )
                return None
                
        except Exception as e:
            self.notifier.send_notification(
                f"❌ Arbeitnow Free API exception!\n"
                f"🐛 Error: {str(e)}"
            )
            return None
    
    def fetch_remote_jobs(self, page: int = 1, limit: int = 100) -> List[JobData]:
        """Fetch remote jobs from Arbeitnow Free API"""
        
        params = {'page': page}
        
        data = self._make_request(params=params)
        if not data:
            return []
            
        jobs = []
        job_items = data.get('data', [])
        
        for item in job_items:
            try:
                # Convert Arbeitnow data to our standardized format
                job = JobData(
                    title=item.get('title', ''),
                    company=item.get('company_name', ''),
                    location=item.get('location', ''),
                    description=item.get('description', ''),
                    url=item.get('url', ''),
                    salary=None,  # Arbeitnow doesn't provide salary info in this format
                    job_type=', '.join(item.get('job_types', [])) or ('Remote' if item.get('remote') else 'On-site'),
                    posted_date=item.get('created_at', ''),
                    source="ArbeitnowFree",
                    external_id=item.get('slug', '')
                )
                jobs.append(job)
                
            except Exception as e:
                print(f"Error processing Arbeitnow job: {e}")
                continue
        
        return jobs[:limit]  # Respect limit parameter

class JobicyAPI:
    """Jobicy API integration - 500,000 requests/month, 1000/hour"""
    
    def __init__(self):
        self.base_url = "https://jobicy.p.rapidapi.com/api/v2"
        self.api_key = os.getenv('RAPIDAPI_KEY')
        self.headers = {
            'x-rapidapi-host': 'jobicy.p.rapidapi.com',
            'x-rapidapi-key': self.api_key
        }
        # 500,000 requests per month = 30 days
        self.rate_limiter = RateLimiter(max_requests=500000, time_period_days=30)
        self.notifier = ServiceNotifier()
        
    def _make_request(self, endpoint: str = "remote-jobs", params: Dict = None) -> Optional[Dict]:
        """Make API request with rate limiting"""
        
        if not self.rate_limiter.can_make_request():
            remaining = self.rate_limiter.requests_remaining()
            next_reset = self.rate_limiter.next_reset_date()
            
            self.notifier._send_message(f"""⚠️ <b>JOBIcy API - RATE LIMIT</b>

❌ <b>Rate limit exceeded</b>
📊 <b>Remaining requests:</b> {remaining:,}/500,000
🕐 <b>Next reset:</b> {next_reset.strftime('%Y-%m-%d %H:%M') if next_reset else 'N/A'}

⏳ <b>Waiting for rate limit reset...</b>""")
            return None
        
        try:
            url = f"{self.base_url}/{endpoint}"
            response = requests.get(url, headers=self.headers, params=params or {}, timeout=30)
            
            self.rate_limiter.record_request()
            
            if response.status_code == 200:
                data = response.json()
                job_count = len(data) if isinstance(data, list) else len(data.get('jobs', []))
                
                self.notifier._send_message(f"""✅ <b>JOBIcy API - SUCCESS</b>

🎯 <b>Endpoint:</b> {endpoint}
📊 <b>Status:</b> {response.status_code}
📦 <b>Jobs found:</b> {job_count}
⚡ <b>Remaining requests:</b> {self.rate_limiter.requests_remaining():,}/500,000

🕐 <b>Time:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}""")
                
                return data
            else:
                error_msg = f"HTTP {response.status_code}: {response.text[:200]}"
                self.notifier._send_message(f"""❌ <b>JOBIcy API - ERROR</b>

🎯 <b>Endpoint:</b> {endpoint}
📊 <b>Status:</b> {response.status_code}
❌ <b>Error:</b> {error_msg}
⚡ <b>Remaining requests:</b> {self.rate_limiter.requests_remaining():,}/500,000""")
                return None
                
        except Exception as e:
            self.notifier._send_message(f"""❌ <b>JOBIcy API - EXCEPTION</b>

🎯 <b>Endpoint:</b> {endpoint}
❌ <b>Error:</b> {str(e)[:200]}
⚡ <b>Remaining requests:</b> {self.rate_limiter.requests_remaining():,}/500,000""")
            return None
    
    def fetch_remote_jobs(self, limit: int = 100) -> List[JobData]:
        """Fetch remote jobs from Jobicy API"""
        
        data = self._make_request()
        if not data:
            return []
            
        jobs = []
        job_items = data if isinstance(data, list) else data.get('jobs', [])
        
        for item in job_items[:limit]:
            try:
                # Convert Jobicy data to our standardized format
                job = JobData(
                    title=item.get('title', ''),
                    company=item.get('company', ''),
                    location=item.get('location', 'Remote'),
                    description=item.get('description', ''),
                    url=item.get('url', ''),
                    salary=item.get('salary'),
                    job_type=item.get('job_type', 'Remote'),
                    posted_date=item.get('date_posted', ''),
                    source="jobicy_api",
                    external_id=item.get('id', '') or hashlib.md5(f"{item.get('title', '')}{item.get('company', '')}".encode()).hexdigest()[:16]
                )
                jobs.append(job)
                
            except Exception as e:
                print(f"Error processing Jobicy job: {e}")
                continue
        
        return jobs[:limit]  # Respect limit parameter

class RemoteJobsPlansAPI:
    """Remote Jobs Plans API integration - 20 requests/month, 100 jobs per request"""
    
    def __init__(self):
        self.base_url = "https://remote-jobs1.p.rapidapi.com"
        self.api_key = os.getenv('RAPIDAPI_KEY')
        self.headers = {
            'x-rapidapi-host': 'remote-jobs1.p.rapidapi.com',
            'x-rapidapi-key': self.api_key
        }
        # 20 requests per month = 30 days
        self.rate_limiter = RateLimiter(max_requests=20, time_period_days=30)
        self.notifier = ServiceNotifier()
        
    def _make_request(self, endpoint: str = "jobs", params: Dict = None) -> Optional[Dict]:
        """Make API request with rate limiting"""
        
        if not self.rate_limiter.can_make_request():
            remaining = self.rate_limiter.requests_remaining()
            next_reset = self.rate_limiter.next_reset_date()
            
            self.notifier._send_message(f"""⚠️ <b>REMOTE JOBS PLANS API - RATE LIMIT</b>

❌ <b>Rate limit exceeded</b>
📊 <b>Remaining requests:</b> {remaining}/20
🕐 <b>Next reset:</b> {next_reset.strftime('%Y-%m-%d %H:%M') if next_reset else 'N/A'}

⏳ <b>Bu API çok sınırlı (20/month)!</b>""")
            return None
        
        try:
            url = f"{self.base_url}/{endpoint}"
            response = requests.get(url, headers=self.headers, params=params or {}, timeout=30)
            
            self.rate_limiter.record_request()
            
            if response.status_code == 200:
                data = response.json()
                job_count = len(data) if isinstance(data, list) else len(data.get('jobs', []))
                
                self.notifier._send_message(f"""✅ <b>REMOTE JOBS PLANS API - SUCCESS</b>

🎯 <b>Endpoint:</b> {endpoint}
📊 <b>Status:</b> {response.status_code}
📦 <b>Jobs found:</b> {job_count}
⚡ <b>Remaining requests:</b> {self.rate_limiter.requests_remaining()}/20

🕐 <b>Time:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}""")
                
                return data
            else:
                error_msg = f"HTTP {response.status_code}: {response.text[:200]}"
                self.notifier._send_message(f"""❌ <b>REMOTE JOBS PLANS API - ERROR</b>

🎯 <b>Endpoint:</b> {endpoint}
📊 <b>Status:</b> {response.status_code}
❌ <b>Error:</b> {error_msg}
⚡ <b>Remaining requests:</b> {self.rate_limiter.requests_remaining()}/20""")
                return None
                
        except Exception as e:
            self.notifier._send_message(f"""❌ <b>REMOTE JOBS PLANS API - EXCEPTION</b>

🎯 <b>Endpoint:</b> {endpoint}
❌ <b>Error:</b> {str(e)[:200]}
⚡ <b>Remaining requests:</b> {self.rate_limiter.requests_remaining()}/20""")
            return None
    
    def fetch_remote_jobs(self, limit: int = 100) -> List[JobData]:
        """Fetch remote jobs from Remote Jobs Plans API"""
        
        # Default params for remote jobs
        params = {
            'offset': 0,
            'country': 'us',
            'employmentType': 'fulltime'
        }
        
        data = self._make_request(params=params)
        if not data:
            return []
            
        jobs = []
        job_items = data if isinstance(data, list) else data.get('jobs', [])
        
        for item in job_items[:limit]:
            try:
                # Convert Remote Jobs Plans data to our standardized format
                job = JobData(
                    title=item.get('title', ''),
                    company=item.get('company', ''),
                    location=item.get('location', 'Remote'),
                    description=item.get('description', ''),
                    url=item.get('url', ''),
                    salary=item.get('salary'),
                    job_type=item.get('employment_type', 'Full-time'),
                    posted_date=item.get('date_posted', ''),
                    source="remote_jobs_plans_api",
                    external_id=item.get('id', '') or hashlib.md5(f"{item.get('title', '')}{item.get('company', '')}".encode()).hexdigest()[:16]
                )
                jobs.append(job)
                
            except Exception as e:
                print(f"Error processing Remote Jobs Plans job: {e}")
                continue
        
        return jobs[:limit]  # Respect limit parameter

class JobPostingsRSSAPI:
    """Job Postings RSS API integration - 31 requests/month, 10 jobs per request, up to 300 jobs free"""
    def __init__(self):
        self.base_url = "https://job-postings-rss-feed.p.rapidapi.com/api/rss/v1/jobs_full"
        self.api_key = os.getenv('RAPIDAPI_KEY')
        self.headers = {
            'x-rapidapi-host': 'job-postings-rss-feed.p.rapidapi.com',
            'x-rapidapi-key': self.api_key
        }
        # 31 requests per month = 30 days
        self.rate_limiter = RateLimiter(max_requests=31, time_period_days=30)
        self.notifier = ServiceNotifier()

    def _make_request(self, page: int = 1) -> Optional[str]:
        if not self.rate_limiter.can_make_request():
            remaining = self.rate_limiter.requests_remaining()
            next_reset = self.rate_limiter.next_reset_date()
            self.notifier._send_message(f"""⚠️ <b>Job Postings RSS API - RATE LIMIT</b>\n\n❌ <b>Rate limit exceeded</b>\n📊 <b>Remaining requests:</b> {remaining}/31\n🕐 <b>Next reset:</b> {next_reset.strftime('%Y-%m-%d %H:%M') if next_reset else 'N/A'}\n\n⏳ <b>Waiting for rate limit reset...</b>""")
            return None
        params = {
            'page': page,
            'countryCode': 'us',
            'hasSalary': 'true'
        }
        try:
            response = requests.get(self.base_url, headers=self.headers, params=params, timeout=30)
            self.rate_limiter.record_request()
            if response.status_code == 200:
                return response.text
            else:
                self.notifier._send_message(f"❌ <b>Job Postings RSS API - ERROR</b>\nStatus: {response.status_code}\n{response.text[:200]}")
                return None
        except Exception as e:
            self.notifier._send_message(f"❌ <b>Job Postings RSS API - EXCEPTION</b>\nError: {str(e)[:200]}")
            return None

    def fetch_remote_jobs(self, limit: int = 10) -> List[JobData]:
        jobs = []
        page = 1
        fetched = 0
        while fetched < limit:
            xml_data = self._make_request(page=page)
            if not xml_data:
                break
            root = ET.fromstring(xml_data)
            channel = root.find('channel')
            if channel is None:
                break
            items = channel.findall('item')
            for item in items:
                if fetched >= limit:
                    break
                try:
                    job = JobData(
                        title=item.findtext('title', ''),
                        company=item.findtext('company', ''),
                        location=item.findtext('location', ''),
                        description=item.findtext('description', ''),
                        url=item.findtext('link', ''),
                        salary=item.findtext('salary'),
                        job_type=item.findtext('workType'),
                        posted_date=item.findtext('pubDate'),
                        source="job_postings_rss_api",
                        external_id=item.findtext('guid', '')
                    )
                    jobs.append(job)
                    fetched += 1
                except Exception as e:
                    print(f"Error parsing Job Postings RSS job: {e}")
                    continue
            if len(items) < 10:
                break  # No more pages
            page += 1
        return jobs[:limit]

class RemotiveAPI:
    """Remotive API integration - Max 4 requests/day, no rate limit but respectful usage"""
    
    def __init__(self):
        self.base_url = "https://remotive.com/api/remote-jobs"
        # No API key required for Remotive
        self.headers = {
            'User-Agent': 'buzz2remote-job-aggregator/1.0'
        }
        # 4 requests per day = 1 day period
        self.rate_limiter = RateLimiter(max_requests=4, time_period_days=1)
        self.notifier = ServiceNotifier()
        
    def _make_request(self, params: Dict = None) -> Optional[Dict]:
        """Make API request with rate limiting"""
        
        if not self.rate_limiter.can_make_request():
            remaining = self.rate_limiter.requests_remaining()
            next_reset = self.rate_limiter.next_reset_date()
            
            self.notifier._send_message(f"""⚠️ <b>REMOTIVE API - RATE LIMIT</b>

❌ <b>Rate limit exceeded</b>
📊 <b>Remaining requests:</b> {remaining}/4
🕐 <b>Next reset:</b> {next_reset.strftime('%Y-%m-%d %H:%M') if next_reset else 'N/A'}

⏳ <b>Günlük limit doldu (4/gün)!</b>""")
            return None
        
        try:
            response = requests.get(self.base_url, headers=self.headers, params=params or {}, timeout=30)
            
            self.rate_limiter.record_request()
            
            if response.status_code == 200:
                data = response.json()
                job_count = data.get('job-count', 0)
                total_count = data.get('total-job-count', 0)
                
                self.notifier._send_message(f"""✅ <b>REMOTIVE API - SUCCESS</b>

📊 <b>Status:</b> {response.status_code}
📦 <b>Jobs found:</b> {job_count}
📈 <b>Total available:</b> {total_count:,}
⚡ <b>Remaining requests:</b> {self.rate_limiter.requests_remaining()}/4

🕐 <b>Time:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}""")
                
                return data
            else:
                error_msg = f"HTTP {response.status_code}: {response.text[:200]}"
                self.notifier._send_message(f"""❌ <b>REMOTIVE API - ERROR</b>

📊 <b>Status:</b> {response.status_code}
❌ <b>Error:</b> {error_msg}
⚡ <b>Remaining requests:</b> {self.rate_limiter.requests_remaining()}/4""")
                return None
                
        except Exception as e:
            self.notifier._send_message(f"""❌ <b>REMOTIVE API - EXCEPTION</b>

❌ <b>Error:</b> {str(e)[:200]}
⚡ <b>Remaining requests:</b> {self.rate_limiter.requests_remaining()}/4""")
            return None
    
    def fetch_remote_jobs(self, limit: int = 100) -> List[JobData]:
        """Fetch remote jobs from Remotive API"""
        
        # Remotive API parametreleri
        params = {
            'limit': min(limit, 100),  # Max 100 per request
            'category': 'software-dev'  # Focus on software development jobs
        }
        
        data = self._make_request(params=params)
        if not data:
            return []
            
        jobs = []
        job_items = data.get('jobs', [])
        
        for item in job_items[:limit]:
            try:
                # Convert Remotive data to our standardized format
                job = JobData(
                    title=item.get('title', ''),
                    company=item.get('company_name', ''),
                    location=item.get('candidate_required_location', 'Remote'),
                    description=self._clean_html_description(item.get('description', '')),
                    url=item.get('url', ''),
                    salary=item.get('salary'),
                    job_type=self._parse_job_type(item.get('job_type', '')),
                    posted_date=item.get('publication_date', ''),
                    source="remotive_api",
                    external_id=str(item.get('id', ''))
                )
                jobs.append(job)
                
            except Exception as e:
                print(f"Error processing Remotive job: {e}")
                continue
        
        return jobs[:limit]
    
    def _clean_html_description(self, description: str) -> str:
        """Clean HTML from job description"""
        if not description:
            return ""
        
        # Remove HTML tags
        import re
        clean_desc = re.sub(r'<[^>]+>', '', description)
        
        # Remove extra whitespace
        clean_desc = re.sub(r'\s+', ' ', clean_desc).strip()
        
        # Limit length
        if len(clean_desc) > 1000:
            clean_desc = clean_desc[:1000] + "..."
        
        return clean_desc
    
    def _parse_job_type(self, job_type: str) -> str:
        """Parse job type from Remotive format"""
        if not job_type:
            return "Full-time"
        
        type_mapping = {
            'full_time': 'Full-time',
            'part_time': 'Part-time',
            'contract': 'Contract',
            'freelance': 'Freelance',
            'internship': 'Internship'
        }
        
        return type_mapping.get(job_type.lower(), job_type.title())

class HimalayasAPI:
    """Himalayas API integration - Respectful usage, no official rate limit but abuse prevention"""
    
    def __init__(self):
        self.base_url = "https://himalayas.app/api/jobs"
        # No API key required for Himalayas
        self.headers = {
            'User-Agent': 'buzz2remote-job-aggregator/1.0',
            'Accept': 'application/json',
            'Accept-Language': 'en-US,en;q=0.9'
        }
        # Conservative rate limiting: 2 requests per day to avoid abuse
        self.rate_limiter = RateLimiter(max_requests=2, time_period_days=1)
        self.notifier = ServiceNotifier()
        
    def _make_request(self, params: Dict = None) -> Optional[Dict]:
        """Make API request with rate limiting"""
        
        if not self.rate_limiter.can_make_request():
            remaining = self.rate_limiter.requests_remaining()
            next_reset = self.rate_limiter.next_reset_date()
            
            self.notifier._send_message(f"""⚠️ <b>HIMALAYAS API - RATE LIMIT</b>

❌ <b>Rate limit exceeded</b>
📊 <b>Remaining requests:</b> {remaining}/2
🕐 <b>Next reset:</b> {next_reset.strftime('%Y-%m-%d %H:%M') if next_reset else 'N/A'}

⏳ <b>Günlük limit doldu (2/gün - abuse prevention)!</b>""")
            return None
        
        try:
            response = requests.get(self.base_url, headers=self.headers, params=params or {}, timeout=30)
            
            self.rate_limiter.record_request()
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    job_count = len(data) if isinstance(data, list) else len(data.get('jobs', []))
                    
                    self.notifier._send_message(f"""✅ <b>HIMALAYAS API - SUCCESS</b>

📊 <b>Status:</b> {response.status_code}
📦 <b>Jobs found:</b> {job_count}
⚡ <b>Remaining requests:</b> {self.rate_limiter.requests_remaining()}/2

🕐 <b>Time:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}""")
                    
                    return data
                except json.JSONDecodeError:
                    # Might be HTML (Cloudflare protection)
                    if "cloudflare" in response.text.lower() or "challenge" in response.text.lower():
                        self.notifier._send_message(f"""⚠️ <b>HIMALAYAS API - CLOUDFLARE PROTECTION</b>

🛡️ <b>Cloudflare challenge detected</b>
📊 <b>Status:</b> {response.status_code}
⚡ <b>Remaining requests:</b> {self.rate_limiter.requests_remaining()}/2

💡 <b>API might be protected by Cloudflare</b>""")
                    else:
                        self.notifier._send_message(f"""❌ <b>HIMALAYAS API - JSON ERROR</b>

📊 <b>Status:</b> {response.status_code}
❌ <b>Error:</b> Invalid JSON response
⚡ <b>Remaining requests:</b> {self.rate_limiter.requests_remaining()}/2""")
                    return None
            else:
                error_msg = f"HTTP {response.status_code}: {response.text[:200]}"
                self.notifier._send_message(f"""❌ <b>HIMALAYAS API - ERROR</b>

📊 <b>Status:</b> {response.status_code}
❌ <b>Error:</b> {error_msg}
⚡ <b>Remaining requests:</b> {self.rate_limiter.requests_remaining()}/2""")
                return None
                
        except Exception as e:
            self.notifier._send_message(f"""❌ <b>HIMALAYAS API - EXCEPTION</b>

❌ <b>Error:</b> {str(e)[:200]}
⚡ <b>Remaining requests:</b> {self.rate_limiter.requests_remaining()}/2""")
            return None
    
    def fetch_remote_jobs(self, limit: int = 50) -> List[JobData]:
        """Fetch remote jobs from Himalayas API"""
        
        # Himalayas API parametreleri
        params = {
            'limit': min(limit, 100),  # Conservative limit
            'remote': 'true',  # Only remote jobs
            'sort': 'recent'  # Most recent first
        }
        
        data = self._make_request(params=params)
        if not data:
            return []
            
        jobs = []
        
        # Handle different response formats
        if isinstance(data, list):
            job_items = data
        elif isinstance(data, dict):
            job_items = data.get('jobs', data.get('data', []))
        else:
            return []
        
        for item in job_items[:limit]:
            try:
                # Convert Himalayas data to our standardized format
                job = JobData(
                    title=item.get('title', ''),
                    company=self._extract_company_name(item),
                    location=item.get('location', 'Remote'),
                    description=self._clean_description(item.get('description', '')),
                    url=item.get('url', '') or item.get('apply_url', ''),
                    salary=self._parse_salary(item),
                    job_type=self._parse_job_type(item),
                    posted_date=item.get('published_at', '') or item.get('created_at', ''),
                    source="himalayas_api",
                    external_id=str(item.get('id', '')) or hashlib.md5(f"{item.get('title', '')}{item.get('company', '')}".encode()).hexdigest()[:16]
                )
                jobs.append(job)
                
            except Exception as e:
                print(f"Error processing Himalayas job: {e}")
                continue
        
        return jobs[:limit]
    
    def _extract_company_name(self, item: Dict) -> str:
        """Extract company name from different possible fields"""
        company = item.get('company', '')
        if isinstance(company, dict):
            return company.get('name', '')
        elif isinstance(company, str):
            return company
        
        # Try alternative fields
        return item.get('company_name', '') or item.get('employer', '')
    
    def _parse_salary(self, item: Dict) -> Optional[str]:
        """Parse salary information"""
        salary = item.get('salary')
        if not salary:
            return None
        
        if isinstance(salary, dict):
            min_sal = salary.get('min')
            max_sal = salary.get('max')
            currency = salary.get('currency', 'USD')
            
            if min_sal and max_sal:
                return f"${min_sal:,}-${max_sal:,} {currency}"
            elif min_sal:
                return f"${min_sal:,}+ {currency}"
        
        return str(salary) if salary else None
    
    def _parse_job_type(self, item: Dict) -> str:
        """Parse job type"""
        job_type = item.get('employment_type', '') or item.get('type', '')
        
        if not job_type:
            return "Full-time"
        
        type_mapping = {
            'full_time': 'Full-time',
            'part_time': 'Part-time',
            'contract': 'Contract',
            'freelance': 'Freelance',
            'internship': 'Internship'
        }
        
        return type_mapping.get(job_type.lower(), job_type.title())
    
    def _clean_description(self, description: str) -> str:
        """Clean job description"""
        if not description:
            return ""
        
        # Remove HTML tags if present
        import re
        clean_desc = re.sub(r'<[^>]+>', '', description)
        
        # Remove extra whitespace
        clean_desc = re.sub(r'\s+', ' ', clean_desc).strip()
        
        # Limit length
        if len(clean_desc) > 1000:
            clean_desc = clean_desc[:1000] + "..."
        
        return clean_desc

class ExternalJobAPIManager:
    """Manage all external job API integrations"""
    
    def __init__(self):
        self.apis = {
            'fantastic_jobs': FantasticJobsAPI(),
            'job_posting_feed': JobPostingFeedAPI(),
            'remoteok': RemoteOKAPI(),
            'arbeitnow_free': ArbeitnowFreeAPI(),
            'jobicy': JobicyAPI(),
            'remote_jobs_plans': RemoteJobsPlansAPI(),
            'job_postings_rss': JobPostingsRSSAPI(),
            'remotive': RemotiveAPI(),
            'himalayas': HimalayasAPI()
        }
        self.notifier = ServiceNotifier()
    
    def fetch_all_jobs(self, max_jobs_per_api: int = 100) -> Dict[str, List[JobData]]:
        """Fetch jobs from all available APIs"""
        
        all_jobs = {}
        total_jobs = 0
        
        for api_name, api_instance in self.apis.items():
            try:
                print(f"🔄 Fetching jobs from {api_name}...")
                
                # API-specific limits
                if api_name == 'job_posting_feed':
                    api_limit = 500  # Max 500 per request
                elif api_name == 'remoteok':
                    api_limit = max_jobs_per_api  # No specific limit mentioned
                elif api_name == 'arbeitnow_free':
                    api_limit = max_jobs_per_api  # No specific limit mentioned
                elif api_name == 'jobicy':
                    api_limit = max_jobs_per_api  # No specific limit mentioned
                elif api_name == 'remote_jobs_plans':
                    api_limit = 100  # Max 100 per request
                else:
                    api_limit = max_jobs_per_api
                    
                jobs = api_instance.fetch_remote_jobs(limit=api_limit)
                
                all_jobs[api_name] = jobs
                total_jobs += len(jobs)
                
                print(f"✅ {api_name}: {len(jobs)} jobs fetched")
                
            except Exception as e:
                print(f"❌ Error fetching from {api_name}: {e}")
                all_jobs[api_name] = []
        
        # Send summary notification
        self.notifier._send_message(f"""📦 <b>EXTERNAL APIS - BATCH COMPLETE</b>\n\n✅ <b>Total Jobs Fetched:</b> {total_jobs}\n\n🔧 <b>API Results:</b>\n• Fantastic Jobs: {len(all_jobs.get('fantastic_jobs', []))} jobs\n• Job Posting Feed: {len(all_jobs.get('job_posting_feed', []))} jobs\n• RemoteOK: {len(all_jobs.get('remoteok', []))} jobs\n• Arbeitnow Free: {len(all_jobs.get('arbeitnow_free', []))} jobs\n• Jobicy: {len(all_jobs.get('jobicy', []))} jobs\n• Remote Jobs Plans: {len(all_jobs.get('remote_jobs_plans', []))} jobs\n• Job Postings RSS: {len(all_jobs.get('job_postings_rss', []))} jobs\n• Remotive: {len(all_jobs.get('remotive', []))} jobs\n• Himalayas: {len(all_jobs.get('himalayas', []))} jobs\n\n🕐 <b>Time:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n🎯 <b>System:</b> buzz2remote.com""")
        
        return all_jobs
    
    def save_jobs_to_database(self, jobs_data: Dict[str, List[JobData]]) -> Dict[str, int]:
        """Save fetched jobs to database - REAL DATABASE INTEGRATION"""
        
        results = {}
        total_new = 0
        total_updated = 0
        
        try:
            # Import database connection - REAL DB
            import sys
            import os
            sys.path.append('/Users/sarperhorata/buzz2remote/backend')
            
            from database import get_async_db
            import asyncio
            
            async def save_to_mongodb():
                nonlocal total_new, total_updated
                
                db = await get_async_db()
                jobs_collection = db.jobs
                
                for api_name, jobs in jobs_data.items():
                    new_count = 0
                    updated_count = 0
                    
                    for job in jobs:
                        try:
                            # Create job document
                            job_doc = {
                                'title': job.title,
                                'company': job.company,
                                'location': job.location,
                                'description': job.description,
                                'url': job.url,
                                'salary': job.salary,
                                'job_type': job.job_type,
                                'employment_type': job.job_type,  # Legacy field
                                'posted_date': job.posted_date,
                                'source': job.source,
                                'source_type': api_name,
                                'external_id': job.external_id,
                                'is_active': True,
                                'created_at': datetime.now(),
                                'last_updated': datetime.now().isoformat(),
                                'fetched_at': datetime.now().isoformat()
                            }
                            
                            # Check if job already exists
                            existing = await jobs_collection.find_one({
                                'external_id': job.external_id,
                                'source_type': api_name
                            })
                            
                            if existing:
                                # Update existing job
                                await jobs_collection.update_one(
                                    {'_id': existing['_id']},
                                    {'$set': job_doc}
                                )
                                updated_count += 1
                                total_updated += 1
                            else:
                                # Insert new job
                                await jobs_collection.insert_one(job_doc)
                                new_count += 1
                                total_new += 1
                                
                        except Exception as e:
                            print(f"❌ Error saving job {job.title}: {e}")
                            continue
                    
                    results[api_name] = new_count
                    print(f"✅ {api_name}: {new_count} new, {updated_count} updated")
                
                return results
            
            # Run async database operation
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # If already in async context, create new task
                results = asyncio.run_coroutine_threadsafe(save_to_mongodb(), loop).result()
            else:
                # If not in async context, run normally
                results = asyncio.run(save_to_mongodb())
            
            # Send REAL results notification
            self.notifier._send_message(f"""💾 <b>DATABASE SAVE COMPLETE - REAL DATA</b>

✅ <b>Total NEW jobs:</b> {total_new}
🔄 <b>Total UPDATED jobs:</b> {total_updated}
📊 <b>Total processed:</b> {total_new + total_updated}

🔧 <b>API Breakdown (NEW jobs only):</b>
• Fantastic Jobs: {results.get('fantastic_jobs', 0)} new
• Job Posting Feed: {results.get('job_posting_feed', 0)} new
• RemoteOK: {results.get('remoteok', 0)} new
• Arbeitnow Free: {results.get('arbeitnow_free', 0)} new
• Jobicy: {results.get('jobicy', 0)} new
• Remote Jobs Plans: {results.get('remote_jobs_plans', 0)} new
• Job Postings RSS: {results.get('job_postings_rss', 0)} new
• Remotive: {results.get('remotive', 0)} new
• Himalayas: {results.get('himalayas', 0)} new

🕐 <b>Time:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
💾 <b>Database:</b> MongoDB Atlas (buzz2remote)""")
            
        except Exception as e:
            print(f"❌ Database error: {e}")
            # Fallback to JSON for debugging
            for api_name, jobs in jobs_data.items():
                filename = f"external_jobs_{api_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                try:
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
                    
                    with open(filename, 'w', encoding='utf-8') as f:
                        json.dump(jobs_json, f, indent=2, ensure_ascii=False)
                    results[api_name] = len(jobs)
                    print(f"⚠️ Fallback: Saved {len(jobs)} jobs from {api_name} to {filename}")
                except Exception as fe:
                    print(f"❌ Fallback error for {api_name}: {fe}")
                    results[api_name] = 0
        
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