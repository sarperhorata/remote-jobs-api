import logging
import os
import requests
import json
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
import time
from bs4 import BeautifulSoup
import re

from services.job_deduplication_service import JobDeduplicationService
from backend.crud.job import JobCRUD
from models.job import JobCreate

logger = logging.getLogger(__name__)

class LinkedInJobService:
    """
    LinkedIn iş ilanları için gelişmiş servis
    Hem API hem de web scraping kullanır
    """
    
    def __init__(self):
        self.client_id = os.getenv("LINKEDIN_CLIENT_ID")
        self.client_secret = os.getenv("LINKEDIN_CLIENT_SECRET")
        self.access_token = os.getenv("LINKEDIN_ACCESS_TOKEN")  # Company page access token
        self.deduplication_service = JobDeduplicationService()
        
        # Web scraping için session
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        })
    
    async def crawl_linkedin_jobs(self, keywords: str = "remote", location: str = "", limit: int = 100) -> Dict[str, Any]:
        """
        LinkedIn'den iş ilanlarını çek ve veritabanına kaydet
        """
        try:
            logger.info(f"Starting LinkedIn job crawl for keywords: {keywords}, location: {location}")
            
            # Web scraping ile iş ilanlarını çek
            jobs = await self._scrape_linkedin_jobs(keywords, location, limit)
            
            if not jobs:
                logger.warning("No jobs found from LinkedIn scraping")
                return {"total_found": 0, "new_jobs": 0, "duplicates": 0}
            
            logger.info(f"Found {len(jobs)} jobs from LinkedIn")
            
            # Deduplication kontrolü ve kaydetme
            new_jobs_count = 0
            duplicate_count = 0
            
            for job_data in jobs:
                try:
                    # Deduplication kontrolü
                    is_duplicate = await self.deduplication_service.check_duplicate(
                        title=job_data.get('title', ''),
                        company=job_data.get('company_name', ''),
                        location=job_data.get('location', ''),
                        source='linkedin'
                    )
                    
                    if is_duplicate:
                        duplicate_count += 1
                        logger.debug(f"Duplicate job found: {job_data.get('title')} at {job_data.get('company_name')}")
                        continue
                    
                    # Job modeli oluştur
                    job_create = JobCreate(
                        title=job_data.get('title', ''),
                        company=job_data.get('company_name', ''),
                        location=job_data.get('location', ''),
                        description=job_data.get('description', ''),
                        url=job_data.get('url', ''),
                        salary=job_data.get('salary'),
                        job_type=job_data.get('employment_type'),
                        posted_date=job_data.get('date_posted'),
                        source='linkedin',
                        external_id=job_data.get('id'),
                        is_remote=self._is_remote_job(job_data),
                        skills=self._extract_skills(job_data.get('description', '')),
                        experience_level=self._determine_experience_level(job_data),
                        created_at=datetime.utcnow(),
                        updated_at=datetime.utcnow()
                    )
                    
                    # Veritabanına kaydet
                    from backend.database.db import get_async_db
                    db = await get_async_db()
                    await JobCRUD.create_job(db, job_create)
                    new_jobs_count += 1
                    
                    logger.debug(f"Saved new job: {job_data.get('title')} at {job_data.get('company_name')}")
                    
                except Exception as e:
                    logger.error(f"Error processing LinkedIn job {job_data.get('id')}: {str(e)}")
                    continue
            
            result = {
                "total_found": len(jobs),
                "new_jobs": new_jobs_count,
                "duplicates": duplicate_count,
                "source": "linkedin",
                "keywords": keywords,
                "location": location,
                "crawl_time": datetime.utcnow().isoformat()
            }
            
            logger.info(f"LinkedIn crawl completed: {result}")
            return result
            
        except Exception as e:
            logger.error(f"Error in LinkedIn job crawl: {str(e)}")
            return {"error": str(e), "total_found": 0, "new_jobs": 0, "duplicates": 0}
    
    async def _scrape_linkedin_jobs(self, keywords: str, location: str, limit: int) -> List[Dict[str, Any]]:
        """
        LinkedIn'den web scraping ile iş ilanlarını çek
        """
        try:
            jobs = []
            start = 0
            page_size = 25
            
            while len(jobs) < limit:
                # LinkedIn jobs API endpoint
                url = "https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings"
                params = {
                    'keywords': keywords,
                    'location': location,
                    'start': start,
                    'count': min(page_size, limit - len(jobs))
                }
                
                response = self.session.get(url, params=params)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.text, 'html.parser')
                job_cards = soup.select('.job-search-card')
                
                if not job_cards:
                    break
                
                for job_card in job_cards:
                    try:
                        job_data = self._parse_job_card(job_card)
                        if job_data:
                            jobs.append(job_data)
                            
                            if len(jobs) >= limit:
                                break
                    except Exception as e:
                        logger.error(f"Error parsing job card: {str(e)}")
                        continue
                
                start += len(job_cards)
                
                # Rate limiting
                time.sleep(2)
                
                # Break if no more jobs
                if len(job_cards) < page_size:
                    break
            
            return jobs[:limit]
            
        except Exception as e:
            logger.error(f"Error scraping LinkedIn jobs: {str(e)}")
            return []
    
    def _parse_job_card(self, job_card) -> Optional[Dict[str, Any]]:
        """
        LinkedIn job card'ını parse et
        """
        try:
            # Extract basic info
            job_id = job_card.get('data-id') or job_card.get('data-job-id')
            title_elem = job_card.select_one('.base-search-card__title')
            company_elem = job_card.select_one('.base-search-card__subtitle')
            location_elem = job_card.select_one('.job-search-card__location')
            link_elem = job_card.select_one('a.base-card__full-link')
            date_elem = job_card.select_one('time.job-search-card__listdate')
            
            if not title_elem or not company_elem or not link_elem:
                return None
            
            # Extract job ID from URL if not available
            job_url = link_elem.get('href')
            if not job_id and job_url:
                job_id_match = re.search(r'/jobs/view/(\d+)', job_url)
                job_id = job_id_match.group(1) if job_id_match else None
            
            # Parse posted date
            posted_date = None
            if date_elem and 'datetime' in date_elem.attrs:
                posted_date = date_elem['datetime']
            else:
                posted_date = datetime.now().strftime('%Y-%m-%d')
            
            # Get detailed job info
            job_details = self._get_job_details(job_id) if job_id else {}
            
            job_data = {
                'id': job_id,
                'title': title_elem.text.strip(),
                'company_name': company_elem.text.strip(),
                'location': location_elem.text.strip() if location_elem else "Unknown",
                'url': job_url,
                'date_posted': posted_date,
                'source': 'linkedin',
                'description': job_details.get('description', ''),
                'salary': job_details.get('salary'),
                'employment_type': job_details.get('employment_type'),
                'industry': job_details.get('industry')
            }
            
            return job_data
            
        except Exception as e:
            logger.error(f"Error parsing job card: {str(e)}")
            return None
    
    def _get_job_details(self, job_id: str) -> Dict[str, Any]:
        """
        Belirli bir iş ilanının detaylarını çek
        """
        try:
            url = f"https://www.linkedin.com/jobs/view/{job_id}"
            response = self.session.get(url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract description
            description_elem = soup.select_one('.description__text')
            description = description_elem.get_text('\n').strip() if description_elem else ""
            
            # Extract JSON-LD data for additional info
            json_ld = None
            script_tags = soup.select('script[type="application/ld+json"]')
            for script in script_tags:
                try:
                    data = json.loads(script.string)
                    if data.get('@type') == 'JobPosting':
                        json_ld = data
                        break
                except:
                    pass
            
            details = {
                'description': description,
                'salary': json_ld.get('baseSalary') if json_ld else None,
                'employment_type': json_ld.get('employmentType') if json_ld else None,
                'industry': json_ld.get('industry') if json_ld else None
            }
            
            return details
            
        except Exception as e:
            logger.error(f"Error getting job details for {job_id}: {str(e)}")
            return {}
    
    def _is_remote_job(self, job_data: Dict[str, Any]) -> bool:
        """
        İş ilanının remote olup olmadığını belirle
        """
        title = job_data.get('title', '').lower()
        location = job_data.get('location', '').lower()
        description = job_data.get('description', '').lower()
        
        remote_keywords = ['remote', 'work from home', 'wfh', 'virtual', 'telecommute', 'distributed']
        
        for keyword in remote_keywords:
            if keyword in title or keyword in location or keyword in description:
                return True
        
        return False
    
    def _extract_skills(self, description: str) -> List[str]:
        """
        İş açıklamasından becerileri çıkar
        """
        # Basit keyword extraction - daha gelişmiş NLP kullanılabilir
        common_skills = [
            'python', 'javascript', 'react', 'node.js', 'java', 'c++', 'c#', 'php',
            'ruby', 'go', 'rust', 'swift', 'kotlin', 'typescript', 'angular', 'vue',
            'docker', 'kubernetes', 'aws', 'azure', 'gcp', 'sql', 'mongodb', 'redis',
            'git', 'agile', 'scrum', 'devops', 'ci/cd', 'microservices', 'api'
        ]
        
        description_lower = description.lower()
        found_skills = []
        
        for skill in common_skills:
            if skill in description_lower:
                found_skills.append(skill)
        
        return found_skills
    
    def _determine_experience_level(self, job_data: Dict[str, Any]) -> str:
        """
        İş deneyim seviyesini belirle
        """
        title = job_data.get('title', '').lower()
        description = job_data.get('description', '').lower()
        
        if any(word in title for word in ['senior', 'lead', 'principal', 'architect']):
            return 'senior'
        elif any(word in title for word in ['junior', 'entry', 'graduate', 'intern']):
            return 'junior'
        elif any(word in title for word in ['mid', 'intermediate']):
            return 'mid'
        else:
            return 'not_specified'
    
    async def get_linkedin_job_statistics(self) -> Dict[str, Any]:
        """
        LinkedIn iş ilanları istatistiklerini getir
        """
        try:
            # Son 30 günlük LinkedIn iş ilanları
            thirty_days_ago = datetime.utcnow() - timedelta(days=30)
            
            from backend.database.db import get_async_db
            db = await get_async_db()
            stats = await JobCRUD.get_job_statistics(db)
            
            return {
                "source": "linkedin",
                "period": "last_30_days",
                "total_jobs": stats.get('total_jobs', 0),
                "companies": len(stats.get('companies', [])),
                "locations": len(stats.get('locations', []))
            }
            
        except Exception as e:
            logger.error(f"Error getting LinkedIn job statistics: {str(e)}")
            return {"error": str(e)} 