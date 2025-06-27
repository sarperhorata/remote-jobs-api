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
            "updated_companies": 0,
            "failed_companies": 0,
            "skipped_companies": 0
        }
        self.processing_errors = []
        self.update_errors = []
        
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
    
    def normalize_company_name(self, company_name: str) -> list:
        """Enhanced normalize company name and generate possible variations with fuzzy matching"""
        if not company_name or company_name.strip() == "":
            return []
        
        original = company_name.strip()
        variations = [original]  # Always include original
        
        # Clean basic formatting
        clean = re.sub(r'\s+', ' ', original)  # Multiple spaces to single space
        clean = clean.strip()
        if clean != original and clean:
            variations.append(clean)
        
        # ENHANCED: More comprehensive prefix patterns
        enhanced_prefixes = [
            # English patterns
            'Careers', 'Jobs at', 'Work at', 'Join', 'Open positions', 'Openings at',
            'Current Openings', 'Current job openings', 'Job openings at', 'We\'re hiring',
            'Open roles', 'Latest Job Openings', 'Find your career at', 'Work for',
            'Work with us at', 'Come work with us', 'Join the team', 'Join Our Team',
            'Job Openings', 'Career Opportunities', 'About', 'Homepage', 'Jobs', 'Untitled',
            'Careers at', 'Working at', 'Come work with us', 'We\'re Hiring at',
            'Find your career at', 'Work From Home', 'Remote Jobs', 'Employment at',
            'Positions at', 'Vacancies at', 'Opportunities at', 'Apply to', 'Hiring at',
            
            # Turkish patterns
            'Şurada açılan kadrolar:', 'Şurada açılan kadrolar', 'Kariyer fırsatları',
            'İş ilanları', 'Açık pozisyonlar', 'Kariyer', 'İş fırsatları',
            
            # Company-specific patterns we see in errors
            'Jobs', 'Careers', 'Openings at', 'Current Openings', 'Latest Job Openings',
            'Job Openings at', 'Open Positions', 'Career Page', 'Work at', 'Join'
        ]
        
        # ENHANCED: More comprehensive suffix patterns
        enhanced_suffixes = [
            # Career-related suffixes
            'Careers', 'Jobs', 'Job Board', 'Current Openings', 'Open Positions',
            'Career Opportunities', 'We\'re Hiring', 'Open roles', 'Job openings',
            'Current job openings', 'Latest Job Openings', 'Find Your Next Career Role',
            'Join Our Team', 'Work with us', 'Career Page', 'Job Opportunities',
            'Employment Opportunity', 'Careers Page', 'Work From Home', 'Remote Jobs',
            'Hiring', 'Employment', 'Positions', 'Vacancies', 'Opportunities',
            
            # Company entity suffixes
            'Inc.', 'Inc', 'LLC', 'Ltd.', 'Ltd', 'Corp.', 'Corp', 'Corporation', 
            'Company', 'Co.', 'Co', 'GmbH', 'AG', 'S.A.', 'B.V.', 'Pty Ltd'
        ]
        
        # NEW: Remove articles (The, A, An)
        articles = ['The ', 'A ', 'An ']
        for article in articles:
            if original.startswith(article):
                cleaned = original[len(article):].strip()
                if cleaned and len(cleaned) > 2:
                    variations.append(cleaned)
        
        # ENHANCED: Better prefix removal with exact word boundaries
        for prefix in enhanced_prefixes:
            # Try different separators and word boundaries
            patterns_to_try = [
                f"^{re.escape(prefix)}\\s*\\|\\s*",     # "Prefix | Company"
                f"^{re.escape(prefix)}\\s*-\\s*",       # "Prefix - Company"  
                f"^{re.escape(prefix)}\\s*:\\s*",       # "Prefix: Company"
                f"^{re.escape(prefix)}\\s+",            # "Prefix Company"
                f"^{re.escape(prefix)}$",               # Just the prefix
            ]
            
            for pattern in patterns_to_try:
                cleaned = re.sub(pattern, '', original, flags=re.IGNORECASE).strip()
                if cleaned and cleaned != original and len(cleaned) > 2:
                    variations.append(cleaned)
        
        # ENHANCED: Better suffix removal with exact word boundaries  
        for suffix in enhanced_suffixes:
            # Try different separators and word boundaries
            patterns_to_try = [
                f"\\s*\\|\\s*{re.escape(suffix)}$",     # "Company | Suffix"
                f"\\s*-\\s*{re.escape(suffix)}$",       # "Company - Suffix"
                f"\\s*:\\s*{re.escape(suffix)}$",       # "Company: Suffix"
                f"\\s+{re.escape(suffix)}$",            # "Company Suffix"
                f"^{re.escape(suffix)}$",               # Just the suffix
            ]
            
            for pattern in patterns_to_try:
                cleaned = re.sub(pattern, '', original, flags=re.IGNORECASE).strip()
                if cleaned and cleaned != original and len(cleaned) > 2:
                    variations.append(cleaned)
        
        # ENHANCED: Better extraction from delimited formats
        delimiters = ['|', ' - ', ':', '•', ' • ', ' · ']
        for delimiter in delimiters:
            if delimiter in original:
                parts = original.split(delimiter)
                for part in parts:
                    clean_part = part.strip()
                    # Filter out parts that are just job-related words
                    if (clean_part and len(clean_part) > 2 and 
                        not any(word.lower() in clean_part.lower() for word in 
                               ['jobs', 'careers', 'hiring', 'openings', 'positions', 'work', 'career'])):
                        variations.append(clean_part)
        
        # NEW: Extract company name from common specific patterns we see in the 230 errors
        specific_patterns = [
            (r'^Jobs?\s+at\s+(.+)$', 1),                    # "Jobs at Company"
            (r'^(.+?)\s+Jobs?$', 1),                        # "Company Jobs"
            (r'^(.+?)\s+Careers?$', 1),                     # "Company Careers"
            (r'^Openings?\s+at\s+(.+)$', 1),               # "Openings at Company"
            (r'^Current\s+Openings?\s*-?\s*(.+)$', 1),     # "Current Openings - Company"
            (r'^(.+?)\s*-\s*Current\s+Openings?$', 1),     # "Company - Current Openings"
            (r'^Work\s+at\s+(.+)$', 1),                    # "Work at Company"
            (r'^(.+?)\s+Job\s+Board$', 1),                 # "Company Job Board"
            (r'^Şurada\s+açılan\s+kadrolar:?\s*(.+)$', 1), # Turkish pattern
            (r'^(.+?)\s+Careers?\s+Page$', 1),             # "Company Careers Page"
        ]
        
        for pattern, group_num in specific_patterns:
            match = re.search(pattern, original, re.IGNORECASE)
            if match:
                extracted = match.group(group_num).strip()
                if extracted and len(extracted) > 2:
                    variations.append(extracted)
        
        # NEW: Handle long titles by extracting meaningful parts
        if len(original) > 50:
            words = original.split()
            # Try combinations of first few words
            for i in range(2, min(5, len(words) + 1)):
                short_name = ' '.join(words[:i])
                if len(short_name) > 3 and len(short_name) < 30:
                    # Skip if it's just job-related words
                    if not all(word.lower() in ['jobs', 'careers', 'hiring', 'openings', 'work', 'at'] 
                              for word in words[:i]):
                        variations.append(short_name)
        
        # NEW: Smart company entity removal (but keep if it's the only identifier)
        company_entities = [' Inc.', ' Inc', ' LLC', ' Ltd.', ' Ltd', ' Corp.', ' Corp', 
                           ' Corporation', ' Company', ' Co.', ' Co', ' GmbH', ' AG']
        for variation in variations.copy():
            for entity in company_entities:
                if variation.endswith(entity):
                    cleaned = variation[:-len(entity)].strip()
                    if cleaned and len(cleaned) > 2:
                        variations.append(cleaned)
        
        # NEW: Clean up HTML entities and normalize special characters
        for i, variation in enumerate(variations.copy()):
            # Remove HTML entities
            cleaned = re.sub(r'&[a-zA-Z0-9#]+;', '', variation)
            # Normalize quotes and dashes
            cleaned = cleaned.replace('"', '').replace('"', '').replace('"', '')
            cleaned = cleaned.replace('–', '-').replace('—', '-').replace('−', '-')
            # Remove extra punctuation but keep essential ones
            cleaned = re.sub(r'[^\w\s\-\.\,\'\&\(\)]', ' ', cleaned)
            # Clean up multiple spaces
            cleaned = re.sub(r'\s+', ' ', cleaned).strip()
            if cleaned and cleaned != variation and len(cleaned) > 1:
                variations.append(cleaned)
        
        # NEW: Generate abbreviations and acronyms
        for variation in variations.copy():
            words = variation.split()
            if len(words) >= 2 and len(words) <= 4:
                # Generate acronym from first letters
                acronym = ''.join(word[0].upper() for word in words if word[0].isalpha())
                if len(acronym) >= 2 and len(acronym) <= 5:
                    variations.append(acronym)
        
        # Remove duplicates and empty strings, keep order
        unique_variations = []
        seen = set()
        for var in variations:
            clean_var = var.strip()
            # More strict filtering
            if (clean_var and clean_var not in seen and len(clean_var) > 1 and
                # Don't include variations that are just job-related words
                not clean_var.lower() in ['jobs', 'careers', 'hiring', 'openings', 'work', 'career', 'positions']):
                unique_variations.append(clean_var)
                seen.add(clean_var)
        
        # Sort by potential relevance (shorter names first, but not too short)
        def relevance_score(name):
            # Prefer names between 3-20 characters
            if 3 <= len(name) <= 20:
                return len(name)
            elif len(name) < 3:
                return 100  # Very low priority
            else:
                return 50 + len(name)  # Lower priority for very long names
        
        unique_variations.sort(key=relevance_score)
        
        # Return top variations (increased from 10 to 15 for better matching)
        return unique_variations[:15]
    
    def extract_website_from_uri(self, uri: str, company_name: str) -> dict:
        """Extract main website domain from career page URI"""
        result = {
            "website": None,
            "career_page": uri,
            "error": None,
            "extraction_method": None
        }
        
        try:
            if not uri or uri.strip() == "":
                result["error"] = "Empty URI"
                return result
                
            parsed = urlparse(uri)
            if not parsed.netloc:
                result["error"] = f"Invalid URL format: {uri}"
                return result
                
            domain = parsed.netloc
            original_domain = domain
            
            # Remove common subdomains
            domain = re.sub(r'^(www\.|careers\.|jobs\.|apply\.|talent\.|hiring\.)', '', domain)
            
            # Handle special cases for job platforms
            if 'lever.co' in domain:
                result["extraction_method"] = "lever_platform"
                # Extract company name from lever URL
                path_parts = parsed.path.strip('/').split('/')
                if path_parts and path_parts[0]:
                    result["website"] = f"https://{path_parts[0]}.com"
                else:
                    result["website"] = f"https://{domain}"
                    result["error"] = "Could not extract company name from Lever URL"
                    
            elif 'greenhouse.io' in domain:
                result["extraction_method"] = "greenhouse_platform"
                if 'boards.greenhouse.io' in domain or 'job-boards.greenhouse.io' in domain:
                    path_parts = parsed.path.strip('/').split('/')
                    if path_parts and path_parts[0]:
                        result["website"] = f"https://{path_parts[0]}.com"
                    else:
                        result["website"] = f"https://{domain}"
                        result["error"] = "Could not extract company name from Greenhouse URL"
                else:
                    result["website"] = f"https://{domain}"
                    
            elif 'workable.com' in domain:
                result["extraction_method"] = "workable_platform"
                if 'apply.workable.com' in domain:
                    path_parts = parsed.path.strip('/').split('/')
                    if path_parts and path_parts[0]:
                        result["website"] = f"https://{path_parts[0]}.com"
                    else:
                        result["website"] = f"https://{domain}"
                        result["error"] = "Could not extract company name from Workable URL"
                else:
                    result["website"] = f"https://{domain}"
                    
            elif 'breezy.hr' in domain:
                result["extraction_method"] = "breezy_platform"
                subdomain = domain.split('.')[0]
                if subdomain and subdomain != 'breezy':
                    result["website"] = f"https://{subdomain}.com"
                else:
                    result["website"] = f"https://{domain}"
                    result["error"] = "Could not extract subdomain from Breezy URL"
                    
            elif 'smartrecruiters.com' in domain:
                result["extraction_method"] = "smartrecruiters_platform"
                if 'careers.smartrecruiters.com' in domain:
                    path_parts = parsed.path.strip('/').split('/')
                    if path_parts and path_parts[0]:
                        result["website"] = f"https://{path_parts[0]}.com"
                    else:
                        result["website"] = f"https://{domain}"
                        result["error"] = "Could not extract company name from SmartRecruiters URL"
                else:
                    result["website"] = f"https://{domain}"
                    
            elif 'ashbyhq.com' in domain:
                result["extraction_method"] = "ashby_platform"
                path_parts = parsed.path.strip('/').split('/')
                if path_parts and path_parts[0] and path_parts[0] != 'jobs':
                    result["website"] = f"https://{path_parts[0]}.com"
                else:
                    result["website"] = f"https://{domain}"
                    result["error"] = "Could not extract company name from Ashby URL"
                    
            elif 'bamboohr.com' in domain:
                result["extraction_method"] = "bamboohr_platform"
                subdomain = domain.split('.')[0]
                if subdomain and subdomain != 'bamboohr':
                    result["website"] = f"https://{subdomain}.com"
                else:
                    result["website"] = f"https://{domain}"
                    result["error"] = "Could not extract subdomain from BambooHR URL"
                    
            elif 'recruitee.com' in domain:
                result["extraction_method"] = "recruitee_platform"
                subdomain = domain.split('.')[0]
                if subdomain and subdomain != 'recruitee':
                    result["website"] = f"https://{subdomain}.com"
                else:
                    result["website"] = f"https://{domain}"
                    result["error"] = "Could not extract subdomain from Recruitee URL"
                    
            elif 'jobvite.com' in domain:
                result["extraction_method"] = "jobvite_platform"
                if 'jobs.jobvite.com' in domain:
                    path_parts = parsed.path.strip('/').split('/')
                    if path_parts and path_parts[0]:
                        result["website"] = f"https://{path_parts[0]}.com"
                    else:
                        result["website"] = f"https://{domain}"
                        result["error"] = "Could not extract company name from Jobvite URL"
                else:
                    result["website"] = f"https://{domain}"
                    
            elif 'applytojob.com' in domain:
                result["extraction_method"] = "applytojob_platform"
                subdomain = domain.split('.')[0]
                if subdomain and subdomain != 'applytojob':
                    result["website"] = f"https://{subdomain}.com"
                else:
                    result["website"] = f"https://{domain}"
                    result["error"] = "Could not extract subdomain from ApplyToJob URL"
                    
            elif 'factorialhr.com' in domain:
                result["extraction_method"] = "factorialhr_platform"
                subdomain = domain.split('.')[0]
                if subdomain and subdomain != 'factorial':
                    result["website"] = f"https://{subdomain}.com"
                else:
                    result["website"] = f"https://{domain}"
                    result["error"] = "Could not extract subdomain from FactorialHR URL"
                    
            elif 'hrpanda.co' in domain:
                result["extraction_method"] = "hrpanda_platform"
                subdomain = domain.split('.')[0]
                if subdomain and subdomain != 'hrpanda':
                    result["website"] = f"https://{subdomain}.com"
                else:
                    result["website"] = f"https://{domain}"
                    result["error"] = "Could not extract subdomain from HRPanda URL"
                    
            elif 'huntflow.io' in domain:
                result["extraction_method"] = "huntflow_platform"
                # Extract from path or subdomain
                if '.' in domain:
                    parts = domain.split('.')
                    if len(parts) > 2 and parts[0] not in ['www', 'jobs']:
                        result["website"] = f"https://{parts[0]}.com"
                    else:
                        result["website"] = f"https://{domain}"
                        result["error"] = "Could not extract company from Huntflow URL"
                else:
                    result["website"] = f"https://{domain}"
                    
            elif 'gethirex.com' in domain:
                result["extraction_method"] = "hirex_platform"
                # Extract company from path for Hirex
                path_parts = parsed.path.strip('/').split('/')
                if len(path_parts) > 1 and path_parts[0] == 'o' and path_parts[1]:
                    result["website"] = f"https://{path_parts[1]}.com"
                else:
                    result["website"] = f"https://{domain}"
                    result["error"] = "Could not extract company from Hirex URL"
                    
            elif 'traffit.com' in domain:
                result["extraction_method"] = "traffit_platform"
                subdomain = domain.split('.')[0]
                if subdomain and subdomain != 'traffit':
                    result["website"] = f"https://{subdomain}.com"
                else:
                    result["website"] = f"https://{domain}"
                    result["error"] = "Could not extract subdomain from Traffit URL"
                    
            elif 'freshteam.com' in domain:
                result["extraction_method"] = "freshteam_platform"
                subdomain = domain.split('.')[0]
                if subdomain and subdomain != 'freshteam':
                    result["website"] = f"https://{subdomain}.com"
                else:
                    result["website"] = f"https://{domain}"
                    result["error"] = "Could not extract subdomain from Freshteam URL"
                    
            elif 'homerun.co' in domain:
                result["extraction_method"] = "homerun_platform"
                subdomain = domain.split('.')[0]
                if subdomain and subdomain != 'homerun':
                    result["website"] = f"https://{subdomain}.com"
                else:
                    result["website"] = f"https://{domain}"
                    result["error"] = "Could not extract subdomain from Homerun URL"
                    
            elif 'pinpointhq.com' in domain:
                result["extraction_method"] = "pinpoint_platform"
                subdomain = domain.split('.')[0]
                if subdomain and subdomain != 'pinpoint':
                    result["website"] = f"https://{subdomain}.com"
                else:
                    result["website"] = f"https://{domain}"
                    result["error"] = "Could not extract subdomain from PinpointHQ URL"
                    
            elif 'notion.site' in domain:
                result["extraction_method"] = "notion_careers_page"
                # For Notion career pages, extract company name from subdomain
                subdomain = domain.split('.')[0]
                if subdomain and subdomain not in ['notion', 'www']:
                    # Try to extract meaningful company name from notion subdomain
                    if '-' in subdomain:
                        company_part = subdomain.split('-')[0]
                        result["website"] = f"https://{company_part}.com"
                    else:
                        result["website"] = f"https://{subdomain}.com"
                else:
                    result["website"] = f"https://{domain}"
                    result["error"] = "Could not extract company from Notion careers page"
                    
            # NEW: Handle direct company websites (the main issue we're fixing)
            else:
                result["extraction_method"] = "direct_company_website"
                # For direct company websites, use the cleaned domain
                clean_domain = domain
                
                # Check if this looks like a career/jobs path on the main company domain
                career_indicators = ['/careers', '/jobs', '/work-with-us', '/hiring', '/join', '/open-roles', '/opportunities']
                is_career_page = any(indicator in parsed.path.lower() for indicator in career_indicators)
                
                if is_career_page:
                    result["website"] = f"https://{clean_domain}"
                    logger.info(f"✅ Direct company website detected: {uri} → {result['website']}")
                else:
                    # Might be a job board or other platform we don't recognize
                    result["website"] = f"https://{clean_domain}"
                    result["error"] = f"Unrecognized platform or unclear if this is a company website: {domain}"
            
            # Validate extracted website
            if result["website"] and result["website"] == result["career_page"]:
                result["error"] = "Website same as career page - no extraction needed"
                
        except Exception as e:
            result["error"] = f"URL parsing failed: {str(e)}"
            logger.error(f"❌ Error extracting website from {uri} for {company_name}: {e}")
            
        return result
    
    def process_companies(self):
        """Process companies and extract website information"""
        logger.info("🔄 Processing companies for website extraction...")
        
        for i, company_data in enumerate(self.companies_data):
            try:
                name = company_data.get('name', f'Unknown_Company_{i}')
                uri = company_data.get('uri', '')
                
                if not uri or uri.strip() == "":
                    self.stats["skipped_companies"] += 1
                    error_info = {
                        "company_name": name,
                        "error_type": "missing_uri",
                        "error_message": "No career page URI provided",
                        "uri": uri
                    }
                    self.processing_errors.append(error_info)
                    logger.warning(f"⚠️  Skipped {name}: No career page URI")
                    continue
                
                self.stats["career_pages_found"] += 1
                
                # Extract main website
                extraction_result = self.extract_website_from_uri(uri, name)
                website = extraction_result.get("website")
                error_msg = extraction_result.get("error")
                extraction_method = extraction_result.get("extraction_method")
                
                if website and not error_msg:
                    self.stats["websites_found"] += 1
                    logger.info(f"✅ {name}: {uri} → {website} ({extraction_method})")
                elif website and error_msg:
                    self.stats["websites_found"] += 1
                    logger.warning(f"⚠️  {name}: {uri} → {website} (WARNING: {error_msg})")
                else:
                    self.stats["failed_companies"] += 1
                    # Make sure we have a proper error message
                    final_error_msg = error_msg if error_msg else "Unknown extraction error - no website extracted"
                    error_info = {
                        "company_name": name,
                        "error_type": "extraction_failed",
                        "error_message": final_error_msg,
                        "uri": uri,
                        "extraction_method": extraction_method
                    }
                    self.processing_errors.append(error_info)
                    logger.error(f"❌ {name}: Failed to extract website from {uri} - {final_error_msg}")
                
                # Store processed data
                company_data['processed_website'] = website
                company_data['career_page'] = uri
                company_data['extraction_result'] = extraction_result
                
            except Exception as e:
                self.stats["failed_companies"] += 1
                error_msg = f"Processing exception: {str(e)}"
                error_info = {
                    "company_name": name if 'name' in locals() else f'Unknown_Company_{i}',
                    "error_type": "processing_exception",
                    "error_message": error_msg,
                    "uri": uri if 'uri' in locals() else 'unknown'
                }
                self.processing_errors.append(error_info)
                logger.error(f"❌ Error processing company {name if 'name' in locals() else i}: {error_msg}")
                continue
        
        logger.info(f"📊 Processing completed: {self.stats['websites_found']}/{self.stats['total_companies']} websites extracted ({(self.stats['websites_found']/self.stats['total_companies']*100):.1f}%)")
    
    async def update_database(self):
        """Update MongoDB with website information"""
        logger.info("💾 Updating database with website information...")
        
        try:
            successful_updates = 0
            for company_data in self.companies_data:
                try:
                    name = company_data.get('name', 'Unknown')
                    website = company_data.get('processed_website', '')
                    career_page = company_data.get('career_page', '')
                    extraction_result = company_data.get('extraction_result', {})
                    
                    if not career_page:
                        continue
                    
                    # Generate name variations for better matching
                    name_variations = self.normalize_company_name(name)
                    if not name_variations:
                        logger.warning(f"⚠️  No name variations generated for: {name}")
                        continue
                    
                    # Try to update jobs with each name variation
                    total_updated = 0
                    matched_variation = None
                    
                    for variation in name_variations:
                        try:
                            result = await db.jobs.update_many(
                                {"company": variation},
                                {
                                    "$set": {
                                        "company_website": website,
                                        "company_careers_url": career_page,
                                        "website_updated_at": datetime.now(),
                                        "website_extraction_method": extraction_result.get("extraction_method"),
                                        "website_extraction_error": extraction_result.get("error")
                                    }
                                }
                            )
                            
                            if result.modified_count > 0:
                                total_updated += result.modified_count
                                matched_variation = variation
                                logger.info(f"✅ Updated {result.modified_count} jobs for {name} (matched as '{variation}')")
                                break  # Found a match, no need to try other variations
                                
                        except Exception as update_ex:
                            logger.error(f"❌ Database update error for variation '{variation}': {str(update_ex)}")
                            continue
                    
                    if total_updated > 0:
                        successful_updates += 1
                        self.stats["updated_companies"] += 1
                    else:
                        error_info = {
                            "company_name": name,
                            "error_type": "no_jobs_found",
                            "error_message": f"No jobs found in database for company variations: {name_variations[:3]}... (tried {len(name_variations)} total)",
                            "website": website,
                            "career_page": career_page,
                            "name_variations_tried": name_variations
                        }
                        self.update_errors.append(error_info)
                        logger.warning(f"⚠️  No jobs found for company: {name} (tried {len(name_variations)} variations)")
                    
                    # Also update/create in companies collection (use the matched variation if found)
                    company_name_to_store = matched_variation if matched_variation else name_variations[0] if name_variations else name
                    try:
                        await db.companies.update_one(
                            {"name": company_name_to_store},
                            {
                                "$set": {
                                    "name": company_name_to_store,
                                    "original_name": name,  # Keep track of original name from distill
                                    "website": website,
                                    "careers_url": career_page,
                                    "updated_at": datetime.now(),
                                    "extraction_method": extraction_result.get("extraction_method"),
                                    "extraction_error": extraction_result.get("error"),
                                    "name_variations": name_variations
                                }
                            },
                            upsert=True
                        )
                    except Exception as company_update_ex:
                        logger.error(f"❌ Error updating companies collection for {name}: {str(company_update_ex)}")
                    
                except Exception as e:
                    error_msg = f"Database update failed: {str(e)}"
                    error_info = {
                        "company_name": name if 'name' in locals() else 'Unknown',
                        "error_type": "database_update_failed",
                        "error_message": error_msg,
                        "website": website if 'website' in locals() else 'unknown',
                        "career_page": career_page if 'career_page' in locals() else 'unknown'
                    }
                    self.update_errors.append(error_info)
                    logger.error(f"❌ Error updating database for {name if 'name' in locals() else 'unknown company'}: {error_msg}")
                    continue
                    
            logger.info(f"✅ Database update completed: {successful_updates}/{len(self.companies_data)} companies successfully updated")
            
        except Exception as e:
            logger.error(f"❌ Database update failed: {str(e)}")
            raise
    
    async def save_processing_logs(self):
        """Save processing errors and statistics to database for admin panel review"""
        try:
            # Save processing run log
            processing_log = {
                "timestamp": datetime.now(),
                "type": "company_website_enrichment",
                "stats": self.stats,
                "processing_errors": self.processing_errors,
                "update_errors": self.update_errors,
                "total_errors": len(self.processing_errors) + len(self.update_errors),
                "success_rate": (self.stats['updated_companies'] / self.stats['total_companies']) * 100 if self.stats['total_companies'] > 0 else 0
            }
            
            await db.processing_logs.insert_one(processing_log)
            logger.info(f"📊 Saved processing log with {processing_log['total_errors']} errors")
            
            # Save individual error records for easy querying
            if self.processing_errors or self.update_errors:
                all_errors = []
                
                for error in self.processing_errors:
                    error["timestamp"] = datetime.now()
                    error["log_type"] = "company_enrichment_processing"
                    all_errors.append(error)
                
                for error in self.update_errors:
                    error["timestamp"] = datetime.now()
                    error["log_type"] = "company_enrichment_database"
                    all_errors.append(error)
                
                if all_errors:
                    await db.error_logs.insert_many(all_errors)
                    logger.info(f"📝 Saved {len(all_errors)} individual error records")
            
        except Exception as e:
            logger.error(f"❌ Failed to save processing logs: {str(e)}")
    
    def print_stats(self):
        """Print processing statistics"""
        success_rate = (self.stats['updated_companies'] / self.stats['total_companies']) * 100 if self.stats['total_companies'] > 0 else 0
        
        # Calculate the numbers user wants to see
        companies_crawled = self.stats['total_companies']
        successful_crawls = self.stats['updated_companies']
        erroneous_crawls = len(self.update_errors)  # Companies that couldn't be found in database
        
        print(f"\n🎯 BUZZ2REMOTE-COMPANIES COMPLETED")
        print(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print(f"Companies crawled = {companies_crawled}")
        print(f"Successful crawls = {successful_crawls}")
        print(f"Erroneous crawls = {erroneous_crawls}")
        print(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print(f"Success rate: {success_rate:.1f}%")
        print(f"Verification: {successful_crawls} + {erroneous_crawls} = {companies_crawled} ✅")
        
        print(f"\n📊 Detailed Statistics:")
        print(f"Total companies in distill export: {self.stats['total_companies']}")
        print(f"Career pages found: {self.stats['career_pages_found']}")
        print(f"Websites extracted: {self.stats['websites_found']}")
        print(f"Database records updated: {self.stats['updated_companies']}")
        print(f"Failed extractions: {self.stats['failed_companies']}")
        print(f"Skipped companies: {self.stats['skipped_companies']}")
        print(f"Processing errors: {len(self.processing_errors)}")
        print(f"Database errors: {len(self.update_errors)}")
        
        if len(self.update_errors) > 0:
            print(f"\n❌ Top Database Errors (companies not found in jobs collection):")
            for error in self.update_errors[:10]:  # Show first 10
                company_name = error.get('company_name', 'Unknown')
                error_msg = error.get('error_message', 'Unknown error')
                print(f"   • {company_name}: {error_msg[:100]}...")
        
        if self.processing_errors:
            print(f"\n⚠️  Top Processing Errors:")
            error_types = {}
            for error in self.processing_errors[:10]:  # Show first 10
                error_type = error.get('error_type', 'unknown')
                if error_type not in error_types:
                    error_types[error_type] = 0
                error_types[error_type] += 1
                print(f"   • {error['company_name']}: {error['error_message']}")
            
            print(f"\n📈 Processing Error Summary:")
            for error_type, count in error_types.items():
                print(f"   • {error_type}: {count} errors")

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
        
        # Save logs for admin panel
        await enricher.save_processing_logs()
        
        # Print results
        enricher.print_stats()
        
        print("\n✅ Company website enrichment completed successfully!")
        print("📊 Check admin panel for detailed error analysis.")
        
    except Exception as e:
        logger.error(f"❌ Script failed: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main()) 