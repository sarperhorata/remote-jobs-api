import logging
from typing import List, Dict, Any, Optional
from concurrent.futures import ThreadPoolExecutor
import time
from datetime import datetime

# Import parsers
from .linkedin_parser import LinkedInParser
from .remotive_parser import RemotiveParser

# Configure logger
logger = logging.getLogger(__name__)

class JobBoardParser:
    """
    Unified parser for multiple job boards
    Handles fetching and aggregating jobs from different sources
    """
    
    def __init__(self):
        """Initialize parsers for different job sources"""
        self.parsers = {
            'linkedin': LinkedInParser(),
            'remotive': RemotiveParser()
        }
        logger.info(f"Initialized JobBoardParser with sources: {', '.join(self.parsers.keys())}")
    
    def get_jobs(self, sources: List[str] = None, keywords: str = "remote", 
                 location: str = "", limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get jobs from multiple sources
        
        Args:
            sources: List of sources to fetch from, defaults to all available sources
            keywords: Search keywords
            location: Job location
            limit: Maximum number of jobs to fetch per source
            
        Returns:
            List of job dictionaries from all sources
        """
        if sources is None:
            sources = list(self.parsers.keys())
        else:
            # Filter out any invalid sources
            sources = [s for s in sources if s in self.parsers]
            
        if not sources:
            logger.warning("No valid sources specified for job fetching")
            return []
            
        logger.info(f"Fetching jobs from sources: {sources} with keywords: '{keywords}', location: '{location}'")
        
        all_jobs = []
        
        # Use ThreadPoolExecutor to fetch jobs from multiple sources in parallel
        with ThreadPoolExecutor(max_workers=len(sources)) as executor:
            future_to_source = {
                executor.submit(self._fetch_jobs_from_source, source, keywords, location, limit): source
                for source in sources
            }
            
            for future in future_to_source:
                source = future_to_source[future]
                try:
                    jobs = future.result()
                    logger.info(f"Retrieved {len(jobs)} jobs from {source}")
                    all_jobs.extend(jobs)
                except Exception as e:
                    logger.error(f"Error retrieving jobs from {source}: {e}")
        
        logger.info(f"Retrieved a total of {len(all_jobs)} jobs from all sources")
        return all_jobs
    
    def _fetch_jobs_from_source(self, source: str, keywords: str, location: str, limit: int) -> List[Dict[str, Any]]:
        """Helper method to fetch jobs from a specific source"""
        try:
            parser = self.parsers.get(source)
            if not parser:
                logger.warning(f"Parser for source '{source}' not found")
                return []
                
            if source == 'linkedin':
                return parser.get_jobs(keywords=keywords, location=location, limit=limit)
            elif source == 'remotive':
                if keywords.lower() == "remote":
                    # For Remotive, use get_jobs_from_api for general remote jobs
                    return parser.get_jobs_from_api(limit=limit)
                else:
                    # Use search for specific keywords
                    return parser.search_jobs(keyword=keywords, limit=limit)
            else:
                logger.warning(f"Fetch method not defined for source '{source}'")
                return []
        except Exception as e:
            logger.error(f"Error in _fetch_jobs_from_source for {source}: {e}")
            return []
    
    def get_job_details(self, job_id: str, source: str) -> Dict[str, Any]:
        """
        Get detailed information for a specific job
        
        Args:
            job_id: ID of the job to fetch
            source: Source of the job (linkedin, remotive, etc.)
            
        Returns:
            Dictionary with job details
        """
        try:
            parser = self.parsers.get(source.lower())
            if not parser:
                logger.warning(f"Parser for source '{source}' not found")
                return {}
                
            logger.info(f"Fetching job details for job {job_id} from {source}")
            return parser.get_job_details(job_id)
        except Exception as e:
            logger.error(f"Error getting job details for job {job_id} from {source}: {e}")
            return {}
    
    def search_jobs(self, keyword: str, sources: List[str] = None, 
                   location: str = "", limit: int = 50) -> List[Dict[str, Any]]:
        """
        Search for jobs across multiple sources
        
        Args:
            keyword: Search keyword
            sources: List of sources to search, defaults to all available sources
            location: Job location
            limit: Maximum number of jobs to fetch per source
            
        Returns:
            List of job dictionaries matching the search criteria
        """
        # For search, we can reuse the get_jobs method with the keyword
        return self.get_jobs(sources=sources, keywords=keyword, location=location, limit=limit)
    
    def get_job_categories(self, sources: List[str] = None) -> Dict[str, List[str]]:
        """
        Get job categories from multiple sources
        
        Args:
            sources: List of sources to fetch categories from, defaults to all available
            
        Returns:
            Dictionary mapping source names to lists of categories
        """
        if sources is None:
            sources = list(self.parsers.keys())
        else:
            # Filter out any invalid sources
            sources = [s for s in sources if s in self.parsers]
            
        if not sources:
            logger.warning("No valid sources specified for category fetching")
            return {}
            
        logger.info(f"Fetching job categories from sources: {sources}")
        
        categories = {}
        
        for source in sources:
            try:
                parser = self.parsers.get(source)
                if not parser:
                    continue
                    
                source_categories = parser.get_job_categories()
                categories[source] = source_categories
                logger.info(f"Retrieved {len(source_categories)} categories from {source}")
            except Exception as e:
                logger.error(f"Error retrieving categories from {source}: {e}")
                categories[source] = []
        
        return categories
    
    def normalize_job_data(self, job: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize job data to a standard format
        
        Args:
            job: Job dictionary to normalize
            
        Returns:
            Normalized job dictionary
        """
        # Create a normalized job object with standard fields
        normalized = {
            'id': job.get('id'),
            'title': job.get('title'),
            'company_name': job.get('company_name'),
            'location': job.get('location', 'Remote'),
            'description': job.get('description', ''),
            'url': job.get('url', ''),
            'date_posted': job.get('date_posted'),
            'source': job.get('source'),
            'tags': job.get('tags', []),
            'salary': job.get('salary'),
            'employment_type': job.get('employment_type'),
            'date_retrieved': datetime.now().strftime('%Y-%m-%d')
        }
        
        # Ensure we have at least the required fields
        for field in ['id', 'title', 'company_name', 'source']:
            if not normalized.get(field):
                logger.warning(f"Missing required field '{field}' in job data")
                # Generate a unique ID if missing
                if field == 'id':
                    normalized['id'] = f"{normalized['source']}-{time.time()}"
                
        return normalized 