import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from bson import ObjectId
from pymongo.errors import PyMongoError
from database.db import get_database_client

logger = logging.getLogger(__name__)

class JobRepository:
    """Repository class for job-related database operations"""
    
    def __init__(self):
        """Initialize the job repository with MongoDB collection"""
        self.db = get_database_client()
        self.collection = self.db.jobs
        
        # Ensure indexes for faster queries
        self._ensure_indexes()
    
    def _ensure_indexes(self):
        """Create necessary indexes for the jobs collection"""
        try:
            # Index for job source and external ID to check for duplicates
            self.collection.create_index([("source", 1), ("external_id", 1)], unique=True)
            
            # Index for search by company
            self.collection.create_index([("company", 1)])
            
            # Index for search by title
            self.collection.create_index([("title", "text"), ("description", "text")])
            
            # Index for date posted for sorting and filtering
            self.collection.create_index([("date_posted", -1)])
            
            # Index for location for filtering
            self.collection.create_index([("location", 1)])
            
            # Index for job type for filtering
            self.collection.create_index([("job_type", 1)])
            
            # Index for skills for filtering and similar job search
            self.collection.create_index([("skills", 1)])
            
            logger.info("Job collection indexes created successfully")
        except PyMongoError as e:
            logger.error(f"Error creating indexes: {e}")
    
    def save_job(self, job_data: Dict[str, Any]) -> str:
        """
        Save a job to the database. If the job already exists (based on source and external_id),
        update it; otherwise, insert a new job.
        
        Args:
            job_data (Dict[str, Any]): Job data to save
            
        Returns:
            str: ID of the saved job
            
        Raises:
            PyMongoError: If a database error occurs
        """
        try:
            # Ensure timestamps
            now = datetime.utcnow()
            if 'created_at' not in job_data:
                job_data['created_at'] = now
            job_data['updated_at'] = now
            
            # Check if job already exists
            query = {
                'source': job_data.get('source'),
                'external_id': job_data.get('external_id')
            }
            
            # Use update_one with upsert to either update an existing job or insert a new one
            result = self.collection.update_one(
                query,
                {'$set': job_data},
                upsert=True
            )
            
            if result.upserted_id:
                logger.info(f"New job inserted: {result.upserted_id}")
                return str(result.upserted_id)
            else:
                logger.info(f"Job updated: {job_data.get('external_id')}")
                # Get the ID of the updated document
                existing_job = self.collection.find_one(query)
                return str(existing_job['_id'])
                
        except PyMongoError as e:
            logger.error(f"Error saving job: {e}")
            raise
    
    def get_job_by_id(self, job_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a job by its ID
        
        Args:
            job_id (str): Job ID
            
        Returns:
            Optional[Dict[str, Any]]: Job data or None if not found
            
        Raises:
            PyMongoError: If a database error occurs
        """
        try:
            job = self.collection.find_one({'_id': ObjectId(job_id)})
            if job:
                job['_id'] = str(job['_id'])  # Convert ObjectId to string
            return job
        except PyMongoError as e:
            logger.error(f"Error getting job: {e}")
            raise
    
    def get_jobs(self, 
                 query: Dict[str, Any] = None, 
                 skip: int = 0, 
                 limit: int = 20,
                 sort_by: str = 'date_posted',
                 sort_order: int = -1) -> List[Dict[str, Any]]:
        """
        Get jobs with optional filtering, pagination, and sorting
        
        Args:
            query (Dict[str, Any], optional): Query filter. Defaults to None.
            skip (int, optional): Number of documents to skip. Defaults to 0.
            limit (int, optional): Number of documents to return. Defaults to 20.
            sort_by (str, optional): Field to sort by. Defaults to 'date_posted'.
            sort_order (int, optional): Sort order (1 for ascending, -1 for descending). Defaults to -1.
            
        Returns:
            List[Dict[str, Any]]: List of job documents
            
        Raises:
            PyMongoError: If a database error occurs
        """
        try:
            if query is None:
                query = {}
            
            cursor = self.collection.find(query) \
                                    .sort(sort_by, sort_order) \
                                    .skip(skip) \
                                    .limit(limit)
            
            # Convert ObjectId to string for each job
            jobs = []
            for job in cursor:
                job['_id'] = str(job['_id'])
                jobs.append(job)
            
            return jobs
        except PyMongoError as e:
            logger.error(f"Error getting jobs: {e}")
            raise
    
    def count_jobs(self, query: Dict[str, Any] = None) -> int:
        """
        Count jobs matching the given query
        
        Args:
            query (Dict[str, Any], optional): Query filter. Defaults to None.
            
        Returns:
            int: Count of matching jobs
            
        Raises:
            PyMongoError: If a database error occurs
        """
        try:
            if query is None:
                query = {}
            return self.collection.count_documents(query)
        except PyMongoError as e:
            logger.error(f"Error counting jobs: {e}")
            raise
    
    def delete_job(self, job_id: str) -> bool:
        """
        Delete a job by its ID
        
        Args:
            job_id (str): Job ID
            
        Returns:
            bool: True if deletion was successful, False otherwise
            
        Raises:
            PyMongoError: If a database error occurs
        """
        try:
            result = self.collection.delete_one({'_id': ObjectId(job_id)})
            if result.deleted_count:
                logger.info(f"Job deleted: {job_id}")
                return True
            logger.warning(f"Job not found for deletion: {job_id}")
            return False
        except PyMongoError as e:
            logger.error(f"Error deleting job: {e}")
            raise
    
    def get_similar_jobs(self, job_id: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Get similar jobs based on skills and job title
        
        Args:
            job_id (str): Reference job ID
            limit (int, optional): Number of similar jobs to return. Defaults to 5.
            
        Returns:
            List[Dict[str, Any]]: List of similar job documents
            
        Raises:
            PyMongoError: If a database error occurs
        """
        try:
            # Get the reference job
            job = self.get_job_by_id(job_id)
            if not job:
                logger.warning(f"Reference job not found: {job_id}")
                return []
            
            # Extract skills and title for matching
            skills = job.get('skills', [])
            title = job.get('title', '')
            
            # If no skills are available, match by title only
            if not skills:
                query = {
                    '_id': {'$ne': ObjectId(job_id)},
                    '$text': {'$search': title}
                }
                return self.get_jobs(query=query, limit=limit)
            
            # Match by skills (at least one skill must match)
            query = {
                '_id': {'$ne': ObjectId(job_id)},
                'skills': {'$in': skills}
            }
            
            return self.get_jobs(query=query, limit=limit)
        except PyMongoError as e:
            logger.error(f"Error getting similar jobs: {e}")
            raise
    
    def archive_old_jobs(self, days_threshold: int = 30) -> int:
        """
        Archive jobs older than the specified threshold
        
        Args:
            days_threshold (int, optional): Age threshold in days. Defaults to 30.
            
        Returns:
            int: Number of jobs archived
            
        Raises:
            PyMongoError: If a database error occurs
        """
        try:
            # Calculate the cutoff date
            cutoff_date = datetime.utcnow().replace(
                hour=0, minute=0, second=0, microsecond=0
            ) - timedelta(days=days_threshold)
            
            # Get jobs older than the cutoff date
            query = {
                'date_posted': {'$lt': cutoff_date},
                'archived': {'$ne': True}
            }
            
            # Update to mark as archived
            result = self.collection.update_many(
                query,
                {'$set': {'archived': True, 'updated_at': datetime.utcnow()}}
            )
            
            archived_count = result.modified_count
            logger.info(f"Archived {archived_count} jobs older than {days_threshold} days")
            
            return archived_count
        except PyMongoError as e:
            logger.error(f"Error archiving old jobs: {e}")
            raise 