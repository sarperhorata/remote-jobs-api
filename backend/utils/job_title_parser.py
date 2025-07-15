import re
import logging
from typing import Dict, Optional, Tuple
from enum import Enum

logger = logging.getLogger(__name__)

class RemoteType(Enum):
    FULL_REMOTE = "Full Remote"
    REMOTE_SPECIFIC = "Remote - Specific Location"
    HYBRID = "Hybrid"
    ON_SITE = "On-Site"
    NOT_SPECIFIED = "Not Specified"

class JobTitleParser:
    """
    Job title'ları parse eden ve düzgün field'lara ayıran utility class
    """
    
    def __init__(self):
        # Common company suffixes that might be concatenated to titles
        self.company_patterns = [
            r'[A-Z][a-z]+(?:[A-Z][a-z]+)*$',  # CamelCase company names
            r'[A-Z]{2,}$',  # All caps company names
        ]
        
        # Remote work indicators
        self.remote_patterns = [
            r'Remote:?\s*(\w+)',  # Remote:AU, Remote AU, etc.
            r'Remote\s*[-–]\s*([A-Z]{2,3}(?:\s+only)?)',  # Remote - AU only
            r'Remote\s*\(([^)]+)\)',  # Remote (AU only)
            r'Work\s*from\s*home',
            r'WFH',
            r'Fully\s*Remote',
            r'100%\s*Remote',
        ]
        
        # Location patterns
        self.location_patterns = [
            r'([A-Z]{2,3})\s*only',  # AU only, USA only
            r'([A-Z]{2,3})\s*timezone',  # AU timezone
            r'([A-Z]{2,3})\s*based',  # AU based
        ]

    def parse_job_title(self, raw_title: str) -> Dict[str, Optional[str]]:
        """
        Parse a concatenated job title into separate components
        
        Args:
            raw_title: Raw job title like "Product ManagerBugcrowdRemote:Au"
            
        Returns:
            Dictionary with parsed components:
            {
                'title': 'Product Manager',
                'company': 'Bugcrowd', 
                'remote_info': 'Remote: AU',
                'is_remote': True,
                'location_restriction': 'AU',
                'cleaned_title': 'Product Manager'
            }
        """
        if not raw_title or not raw_title.strip():
            return self._empty_result()
        
        title = raw_title.strip()
        
        try:
            # Extract remote information first
            remote_info = self._extract_remote_info(title)
            if remote_info['text']:
                title = title.replace(remote_info['text'], '').strip()
            
            # Split title and company
            title_company = self._split_title_company(title)
            
            # Clean the title
            cleaned_title = self._clean_title(title_company['title'])
            
            result = {
                'title': cleaned_title,
                'company': title_company['company'],
                'remote_info': remote_info['text'],
                'is_remote': remote_info['is_remote'],
                'location_restriction': remote_info['location'],
                'remote_type': remote_info['type'],
                'cleaned_title': cleaned_title,
                'original_title': raw_title
            }
            
            logger.debug(f"Parsed '{raw_title}' -> {result}")
            return result
            
        except Exception as e:
            logger.error(f"Error parsing job title '{raw_title}': {str(e)}")
            return self._fallback_result(raw_title)

    def _extract_remote_info(self, text: str) -> Dict:
        """Extract remote work information from text"""
        result = {
            'text': '',
            'is_remote': False,
            'location': None,
            'type': RemoteType.NOT_SPECIFIED
        }
        
        text_lower = text.lower()
        
        # Check for remote patterns
        for pattern in self.remote_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                result['text'] = match.group(0)
                result['is_remote'] = True
                
                # Extract location if present
                if len(match.groups()) > 0:
                    location = match.group(1).strip()
                    if location:
                        result['location'] = location.upper()
                        result['type'] = RemoteType.REMOTE_SPECIFIC
                else:
                    result['type'] = RemoteType.FULL_REMOTE
                break
        
        # Check for location restrictions
        if not result['location']:
            for pattern in self.location_patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    result['location'] = match.group(1).upper()
                    if not result['is_remote']:
                        result['type'] = RemoteType.ON_SITE
                    break
        
        return result

    def _split_title_company(self, text: str) -> Dict[str, Optional[str]]:
        """Split text into title and company parts"""
        # Look for CamelCase pattern which often indicates company name
        # Example: "Product ManagerBugcrowd" -> title="Product Manager", company="Bugcrowd"
        
        # Pattern to find where title ends and company begins
        # Look for lowercase followed by uppercase (indicating word boundary)
        pattern = r'([a-z])([A-Z][a-z]+(?:[A-Z][a-z]+)*?)$'
        match = re.search(pattern, text)
        
        if match:
            split_pos = match.start(2)
            title = text[:split_pos].strip()
            company = text[split_pos:].strip()
            
            # Validate that we have reasonable splits
            if len(title) >= 3 and len(company) >= 2:
                return {'title': title, 'company': company}
        
        # Fallback: try to split on common patterns
        # Look for patterns like "ManagerAt", "DeveloperFor", etc.
        fallback_patterns = [
            r'(.*?)(At[A-Z][a-z]+)',
            r'(.*?)(For[A-Z][a-z]+)', 
            r'(.*?)([A-Z][a-z]+(?:[A-Z][a-z]+)+)$'
        ]
        
        for pattern in fallback_patterns:
            match = re.search(pattern, text)
            if match and len(match.groups()) >= 2:
                title = match.group(1).strip()
                company = match.group(2).strip()
                
                # Remove connecting words
                company = re.sub(r'^(At|For)', '', company)
                
                if len(title) >= 3 and len(company) >= 2:
                    return {'title': title, 'company': company}
        
        # If no clear split found, return the whole text as title
        return {'title': text, 'company': None}

    def _clean_title(self, title: str) -> str:
        """Clean and normalize job title"""
        if not title:
            return ""
        
        # Remove extra whitespace
        title = re.sub(r'\s+', ' ', title).strip()
        
        # Remove leading/trailing punctuation
        title = title.strip('.,;:-_|')
        
        # Fix common concatenation issues
        # Add space before capital letters when needed
        title = re.sub(r'([a-z])([A-Z])', r'\1 \2', title)
        
        # Remove duplicate words
        words = title.split()
        unique_words = []
        for word in words:
            if word not in unique_words:
                unique_words.append(word)
        
        return ' '.join(unique_words)

    def _empty_result(self) -> Dict[str, Optional[str]]:
        """Return empty result structure"""
        return {
            'title': None,
            'company': None,
            'remote_info': None,
            'is_remote': False,
            'location_restriction': None,
            'remote_type': RemoteType.NOT_SPECIFIED,
            'cleaned_title': None,
            'original_title': None
        }

    def _fallback_result(self, raw_title: str) -> Dict[str, Optional[str]]:
        """Return fallback result when parsing fails"""
        return {
            'title': raw_title,
            'company': None,
            'remote_info': None,
            'is_remote': False,
            'location_restriction': None,
            'remote_type': RemoteType.NOT_SPECIFIED,
            'cleaned_title': raw_title,
            'original_title': raw_title
        }

# Global instance
job_title_parser = JobTitleParser()

def parse_job_title(raw_title: str) -> Dict[str, Optional[str]]:
    """
    Convenience function to parse job title
    
    Args:
        raw_title: Raw job title string
        
    Returns:
        Dictionary with parsed components
    """
    return job_title_parser.parse_job_title(raw_title)

def clean_and_extract_job_info(job_data: Dict) -> Dict:
    """
    Clean job data and extract parsed information
    
    Args:
        job_data: Job data dictionary
        
    Returns:
        Updated job data with parsed fields
    """
    raw_title = job_data.get('title', '')
    parsed = parse_job_title(raw_title)
    
    # Update job data with parsed information
    if parsed['title']:
        job_data['title'] = parsed['title']
    
    if parsed['company'] and not job_data.get('company'):
        job_data['company'] = parsed['company']
    
    # Add remote information
    if parsed['is_remote']:
        job_data['is_remote'] = True
        job_data['remote_type'] = parsed['remote_type'].value
        
        if parsed['location_restriction']:
            job_data['location_restriction'] = parsed['location_restriction']
            job_data['location'] = f"Remote ({parsed['location_restriction']})"
        else:
            job_data['location'] = "Remote"
    
    # Store original title for reference
    job_data['original_title'] = raw_title
    
    return job_data 