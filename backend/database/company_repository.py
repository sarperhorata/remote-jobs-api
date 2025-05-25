import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from bson import ObjectId
from pymongo.errors import PyMongoError
from database.db import get_database_client

logger = logging.getLogger(__name__)

class CompanyRepository:
    """Repository class for company-related database operations"""
    
    def __init__(self):
        """Initialize the company repository with MongoDB collection"""
        self.db = get_database_client()
        self.collection = self.db.companies
        
        # Ensure indexes for faster queries
        self._ensure_indexes()
    
    def _ensure_indexes(self):
        """Create necessary indexes for the companies collection"""
        try:
            # Index for company name (unique)
            self.collection.create_index([("name", 1)], unique=True)
            
            # Index for company website
            self.collection.create_index([("website", 1)])
            
            # Index for industry
            self.collection.create_index([("industry", 1)])
            
            # Index for company size
            self.collection.create_index([("size", 1)])
            
            # Index for location
            self.collection.create_index([("location", 1)])
            
            # Text index for search
            self.collection.create_index([("name", "text"), ("description", "text")])
            
            logger.info("Company collection indexes created successfully")
        except PyMongoError as e:
            logger.error(f"Error creating company indexes: {e}")
    
    def save_company(self, company_data: Dict[str, Any]) -> str:
        """
        Save a company to the database. If the company already exists (based on name),
        update it; otherwise, insert a new company.
        
        Args:
            company_data (Dict[str, Any]): Company data to save
            
        Returns:
            str: ID of the saved company
            
        Raises:
            PyMongoError: If a database error occurs
        """
        try:
            # Ensure timestamps
            now = datetime.utcnow()
            if 'created_at' not in company_data:
                company_data['created_at'] = now
            company_data['updated_at'] = now
            
            # Check if company already exists
            query = {'name': company_data.get('name')}
            
            # Use update_one with upsert to either update an existing company or insert a new one
            result = self.collection.update_one(
                query,
                {'$set': company_data},
                upsert=True
            )
            
            if result.upserted_id:
                logger.info(f"New company inserted: {result.upserted_id}")
                return str(result.upserted_id)
            else:
                logger.info(f"Company updated: {company_data.get('name')}")
                # Get the ID of the updated document
                existing_company = self.collection.find_one(query)
                return str(existing_company['_id'])
                
        except PyMongoError as e:
            logger.error(f"Error saving company: {e}")
            raise
    
    def get_company_by_id(self, company_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a company by its ID
        
        Args:
            company_id (str): Company ID
            
        Returns:
            Optional[Dict[str, Any]]: Company data or None if not found
        """
        try:
            company = self.collection.find_one({'_id': ObjectId(company_id)})
            if company:
                company['_id'] = str(company['_id'])
            return company
        except PyMongoError as e:
            logger.error(f"Error getting company: {e}")
            raise
    
    def get_company_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Get a company by its name
        
        Args:
            name (str): Company name
            
        Returns:
            Optional[Dict[str, Any]]: Company data or None if not found
        """
        try:
            company = self.collection.find_one({'name': name})
            if company:
                company['_id'] = str(company['_id'])
            return company
        except PyMongoError as e:
            logger.error(f"Error getting company by name: {e}")
            raise
    
    def get_companies(self, 
                     query: Dict[str, Any] = None, 
                     skip: int = 0, 
                     limit: int = 20,
                     sort_by: str = 'name',
                     sort_order: int = 1) -> List[Dict[str, Any]]:
        """
        Get companies with optional filtering, pagination, and sorting
        
        Args:
            query (Dict[str, Any], optional): Query filter. Defaults to None.
            skip (int, optional): Number of documents to skip. Defaults to 0.
            limit (int, optional): Number of documents to return. Defaults to 20.
            sort_by (str, optional): Field to sort by. Defaults to 'name'.
            sort_order (int, optional): Sort order (1 for ascending, -1 for descending). Defaults to 1.
            
        Returns:
            List[Dict[str, Any]]: List of company documents
        """
        try:
            if query is None:
                query = {}
            
            cursor = self.collection.find(query) \
                                    .sort(sort_by, sort_order) \
                                    .skip(skip) \
                                    .limit(limit)
            
            # Convert ObjectId to string for each company
            companies = []
            for company in cursor:
                company['_id'] = str(company['_id'])
                companies.append(company)
            
            return companies
        except PyMongoError as e:
            logger.error(f"Error getting companies: {e}")
            raise
    
    def count_companies(self, query: Dict[str, Any] = None) -> int:
        """
        Count companies matching the given query
        
        Args:
            query (Dict[str, Any], optional): Query filter. Defaults to None.
            
        Returns:
            int: Count of matching companies
        """
        try:
            if query is None:
                query = {}
            return self.collection.count_documents(query)
        except PyMongoError as e:
            logger.error(f"Error counting companies: {e}")
            raise
    
    def update_company_stats(self, company_name: str) -> None:
        """
        Update company statistics (job count, etc.)
        
        Args:
            company_name (str): Company name
        """
        try:
            # Get job count for this company
            from database.job_repository import JobRepository
            job_repo = JobRepository()
            job_count = job_repo.count_jobs({'company': company_name})
            
            # Update company with job count
            self.collection.update_one(
                {'name': company_name},
                {
                    '$set': {
                        'job_count': job_count,
                        'updated_at': datetime.utcnow()
                    }
                }
            )
            
        except PyMongoError as e:
            logger.error(f"Error updating company stats: {e}")
            raise 