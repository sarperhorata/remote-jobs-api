import logging
from typing import List, Dict, Any, Optional, Tuple, Set
from datetime import datetime, timedelta
from difflib import SequenceMatcher
import hashlib
import re
from dataclasses import dataclass
from motor.motor_asyncio import AsyncIOMotorDatabase
from database import get_async_db

logger = logging.getLogger(__name__)

@dataclass
class DeduplicationResult:
    """Result of deduplication check"""
    is_duplicate: bool
    duplicate_job_id: Optional[str] = None
    similarity_score: float = 0.0
    duplicate_reason: Optional[str] = None
    confidence_level: str = "low"  # low, medium, high

@dataclass
class DeduplicationStats:
    """Statistics for deduplication process"""
    total_checked: int = 0
    duplicates_found: int = 0
    new_jobs: int = 0
    updated_jobs: int = 0
    removed_duplicates: int = 0
    processing_time: float = 0.0

class JobDeduplicationService:
    """
    Merkezi Job Deduplication Servisi
    
    Bu servis tüm job ekleme işlemlerinde kullanılır ve duplikasyonları tespit eder.
    Farklı stratejiler kullanarak yüksek doğrulukla duplikasyon tespiti yapar.
    """
    
    def __init__(self):
        self.db: Optional[AsyncIOMotorDatabase] = None
        self.collection = None
        
        # Deduplication stratejileri ve ağırlıkları
        self.strategies = {
            'exact_match': {
                'weight': 1.0,
                'fields': ['external_id', 'source_url', 'url']
            },
            'title_company_match': {
                'weight': 0.9,
                'fields': ['title', 'company']
            },
            'fuzzy_title_match': {
                'weight': 0.8,
                'fields': ['title']
            },
            'content_similarity': {
                'weight': 0.7,
                'fields': ['description', 'requirements']
            },
            'hash_match': {
                'weight': 0.95,
                'fields': ['title', 'company', 'description']
            }
        }
        
        # Minimum similarity threshold
        self.min_similarity_threshold = 0.85
        self.high_confidence_threshold = 0.95
        
    async def _get_collection(self):
        """Get the jobs collection"""
        if self.collection is None:
            self.db = await get_async_db()
            self.collection = self.db.jobs
        return self.collection
    
    def _normalize_text(self, text: str) -> str:
        """Normalize text for comparison"""
        if not text:
            return ""
        
        # Convert to lowercase
        text = text.lower()
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Remove special characters but keep alphanumeric and spaces
        text = re.sub(r'[^\w\s]', '', text)
        
        return text
    
    def _calculate_text_similarity(self, text1: str, text2: str) -> float:
        """Calculate similarity between two text strings"""
        if not text1 or not text2:
            return 0.0
        
        normalized1 = self._normalize_text(text1)
        normalized2 = self._normalize_text(text2)
        
        if not normalized1 or not normalized2:
            return 0.0
        
        # Use SequenceMatcher for similarity
        similarity = SequenceMatcher(None, normalized1, normalized2).ratio()
        return similarity
    
    def _generate_job_hash(self, job_data: Dict[str, Any]) -> str:
        """Generate a hash for job data"""
        # Create a normalized string for hashing
        hash_string = f"{job_data.get('title', '')}|{job_data.get('company', '')}|{job_data.get('description', '')}"
        normalized = self._normalize_text(hash_string)
        
        # Generate SHA-256 hash
        return hashlib.sha256(normalized.encode('utf-8')).hexdigest()
    
    async def check_duplicate(self, job_data: Dict[str, Any]) -> DeduplicationResult:
        """
        Check if a job is a duplicate of existing jobs
        
        Args:
            job_data: Job data to check
            
        Returns:
            DeduplicationResult with duplicate information
        """
        collection = await self._get_collection()
        
        # Strategy 1: Exact match on external_id and source_url
        if job_data.get('external_id') and job_data.get('source_url'):
            existing = await collection.find_one({
                'external_id': job_data['external_id'],
                'source_url': job_data['source_url']
            })
            if existing:
                return DeduplicationResult(
                    is_duplicate=True,
                    duplicate_job_id=str(existing['_id']),
                    similarity_score=1.0,
                    duplicate_reason="exact_external_id_match",
                    confidence_level="high"
                )
        
        # Strategy 2: Exact match on URL
        if job_data.get('url'):
            existing = await collection.find_one({'url': job_data['url']})
            if existing:
                return DeduplicationResult(
                    is_duplicate=True,
                    duplicate_job_id=str(existing['_id']),
                    similarity_score=1.0,
                    duplicate_reason="exact_url_match",
                    confidence_level="high"
                )
        
        # Strategy 3: Title + Company exact match
        if job_data.get('title') and job_data.get('company'):
            normalized_title = self._normalize_text(job_data['title'])
            normalized_company = self._normalize_text(job_data['company'])
            
            existing = await collection.find_one({
                'title_normalized': normalized_title,
                'company_normalized': normalized_company
            })
            if existing:
                return DeduplicationResult(
                    is_duplicate=True,
                    duplicate_job_id=str(existing['_id']),
                    similarity_score=0.95,
                    duplicate_reason="title_company_exact_match",
                    confidence_level="high"
                )
        
        # Strategy 4: Hash match
        job_hash = self._generate_job_hash(job_data)
        existing = await collection.find_one({'job_hash': job_hash})
        if existing:
            return DeduplicationResult(
                is_duplicate=True,
                duplicate_job_id=str(existing['_id']),
                similarity_score=0.95,
                duplicate_reason="content_hash_match",
                confidence_level="high"
            )
        
        # Strategy 5: Fuzzy matching for similar jobs
        if job_data.get('title') and job_data.get('company'):
            # Find jobs with similar title and same company
            similar_jobs = await collection.find({
                'company': {'$regex': job_data['company'], '$options': 'i'}
            }).limit(10).to_list(length=10)
            
            best_match = None
            best_score = 0.0
            
            for existing_job in similar_jobs:
                # Calculate title similarity
                title_similarity = self._calculate_text_similarity(
                    job_data['title'], 
                    existing_job.get('title', '')
                )
                
                # Calculate description similarity if available
                desc_similarity = 0.0
                if job_data.get('description') and existing_job.get('description'):
                    desc_similarity = self._calculate_text_similarity(
                        job_data['description'],
                        existing_job.get('description', '')
                    )
                
                # Combined score
                combined_score = (title_similarity * 0.7) + (desc_similarity * 0.3)
                
                if combined_score > best_score and combined_score >= self.min_similarity_threshold:
                    best_score = combined_score
                    best_match = existing_job
            
            if best_match:
                confidence = "high" if best_score >= self.high_confidence_threshold else "medium"
                return DeduplicationResult(
                    is_duplicate=True,
                    duplicate_job_id=str(best_match['_id']),
                    similarity_score=best_score,
                    duplicate_reason="fuzzy_content_match",
                    confidence_level=confidence
                )
        
        # No duplicate found
        return DeduplicationResult(is_duplicate=False)
    
    async def save_job_with_deduplication(self, job_data: Dict[str, Any]) -> Tuple[str, DeduplicationResult]:
        """
        Save job with deduplication check
        
        Args:
            job_data: Job data to save
            
        Returns:
            Tuple of (job_id, deduplication_result)
        """
        collection = await self._get_collection()
        
        # Check for duplicates
        duplicate_result = await self.check_duplicate(job_data)
        
        if duplicate_result.is_duplicate:
            # Update existing job if it's a duplicate
            if duplicate_result.confidence_level in ["high", "medium"]:
                # Update the existing job with new information
                update_data = {
                    'updated_at': datetime.utcnow(),
                    'last_updated': datetime.utcnow()
                }
                
                # Update fields that might have changed
                for field in ['description', 'requirements', 'salary', 'apply_url', 'source_url']:
                    if field in job_data:
                        update_data[field] = job_data[field]
                
                await collection.update_one(
                    {'_id': duplicate_result.duplicate_job_id},
                    {'$set': update_data}
                )
                
                logger.info(f"Updated duplicate job: {duplicate_result.duplicate_job_id}")
                return duplicate_result.duplicate_job_id, duplicate_result
            else:
                # Low confidence duplicate - log but don't update
                logger.warning(f"Low confidence duplicate detected: {duplicate_result.duplicate_reason}")
                return duplicate_result.duplicate_job_id, duplicate_result
        
        # No duplicate found - save as new job
        # Add normalized fields and hash
        job_data['title_normalized'] = self._normalize_text(job_data.get('title', ''))
        job_data['company_normalized'] = self._normalize_text(job_data.get('company', ''))
        job_data['job_hash'] = self._generate_job_hash(job_data)
        job_data['created_at'] = datetime.utcnow()
        job_data['updated_at'] = datetime.utcnow()
        
        result = await collection.insert_one(job_data)
        job_id = str(result.inserted_id)
        
        logger.info(f"Saved new job: {job_id}")
        return job_id, duplicate_result
    
    async def find_and_remove_duplicates(self, batch_size: int = 100) -> DeduplicationStats:
        """
        Find and remove duplicate jobs from the database
        
        Args:
            batch_size: Number of jobs to process in each batch
            
        Returns:
            DeduplicationStats with processing results
        """
        collection = await self._get_collection()
        stats = DeduplicationStats()
        start_time = datetime.now()
        
        # Get all jobs
        all_jobs = await collection.find({}).to_list(length=None)
        stats.total_checked = len(all_jobs)
        
        # Group jobs by company for efficient processing
        jobs_by_company = {}
        for job in all_jobs:
            company = job.get('company', '').lower()
            if company not in jobs_by_company:
                jobs_by_company[company] = []
            jobs_by_company[company].append(job)
        
        # Process each company's jobs
        for company, company_jobs in jobs_by_company.items():
            if len(company_jobs) <= 1:
                continue
            
            # Sort by creation date (oldest first)
            company_jobs.sort(key=lambda x: x.get('created_at', datetime.min))
            
            # Find duplicates within company
            duplicates_to_remove = []
            processed_jobs = []
            
            for job in company_jobs:
                is_duplicate = False
                
                for processed_job in processed_jobs:
                    # Check for duplicates
                    duplicate_result = await self.check_duplicate({
                        'title': job.get('title'),
                        'company': job.get('company'),
                        'description': job.get('description'),
                        'external_id': job.get('external_id'),
                        'source_url': job.get('source_url'),
                        'url': job.get('url')
                    })
                    
                    if duplicate_result.is_duplicate and duplicate_result.confidence_level in ["high", "medium"]:
                        # Keep the older job, mark newer one for removal
                        if job.get('created_at', datetime.min) > processed_job.get('created_at', datetime.min):
                            duplicates_to_remove.append(job['_id'])
                        else:
                            duplicates_to_remove.append(processed_job['_id'])
                            processed_jobs.remove(processed_job)
                            processed_jobs.append(job)
                        is_duplicate = True
                        stats.duplicates_found += 1
                        break
                
                if not is_duplicate:
                    processed_jobs.append(job)
            
            # Remove duplicates
            if duplicates_to_remove:
                result = await collection.delete_many({'_id': {'$in': duplicates_to_remove}})
                stats.removed_duplicates += result.deleted_count
                logger.info(f"Removed {result.deleted_count} duplicates for company: {company}")
        
        stats.processing_time = (datetime.now() - start_time).total_seconds()
        logger.info(f"Deduplication completed: {stats.removed_duplicates} duplicates removed in {stats.processing_time:.2f}s")
        
        return stats
    
    async def get_duplicate_report(self) -> Dict[str, Any]:
        """
        Generate a report of potential duplicates in the database
        
        Returns:
            Dictionary with duplicate analysis
        """
        collection = await self._get_collection()
        
        # Get all jobs
        all_jobs = await collection.find({}).to_list(length=None)
        
        # Group by company
        jobs_by_company = {}
        for job in all_jobs:
            company = job.get('company', '').lower()
            if company not in jobs_by_company:
                jobs_by_company[company] = []
            jobs_by_company[company].append(job)
        
        duplicate_groups = []
        total_duplicates = 0
        
        for company, company_jobs in jobs_by_company.items():
            if len(company_jobs) <= 1:
                continue
            
            # Find similar jobs within company
            similar_groups = []
            processed_indices = set()
            
            for i, job1 in enumerate(company_jobs):
                if i in processed_indices:
                    continue
                
                similar_jobs = [job1]
                processed_indices.add(i)
                
                for j, job2 in enumerate(company_jobs[i+1:], i+1):
                    if j in processed_indices:
                        continue
                    
                    # Check similarity
                    duplicate_result = await self.check_duplicate({
                        'title': job2.get('title'),
                        'company': job2.get('company'),
                        'description': job2.get('description'),
                        'external_id': job2.get('external_id'),
                        'source_url': job2.get('source_url'),
                        'url': job2.get('url')
                    })
                    
                    if duplicate_result.is_duplicate:
                        similar_jobs.append(job2)
                        processed_indices.add(j)
                
                if len(similar_jobs) > 1:
                    similar_groups.append(similar_jobs)
                    total_duplicates += len(similar_jobs) - 1
            
            if similar_groups:
                duplicate_groups.append({
                    'company': company,
                    'groups': similar_groups,
                    'total_jobs': len(company_jobs),
                    'duplicate_count': sum(len(group) - 1 for group in similar_groups)
                })
        
        return {
            'total_jobs': len(all_jobs),
            'total_duplicates': total_duplicates,
            'companies_with_duplicates': len(duplicate_groups),
            'duplicate_groups': duplicate_groups,
            'generated_at': datetime.utcnow().isoformat()
        }

# Global instance
deduplication_service = JobDeduplicationService() 