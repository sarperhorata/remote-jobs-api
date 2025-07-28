"""
Base Repository Pattern
Provides common database operations with ObjectId and async iterator handling
"""

import logging
from typing import Dict, List, Any, Optional, Union
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorCollection, AsyncIOMotorDatabase

from backend.utils.objectid_helper import objectid_helper
from backend.utils.async_iterator_helper import async_iterator_helper

logger = logging.getLogger(__name__)


class BaseRepository:
    """Base repository with common database operations"""
    
    def __init__(self, collection: AsyncIOMotorCollection):
        self.collection = collection
        self.db = collection.database
    
    async def find_one(self, query: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Find one document"""
        try:
            # Convert ObjectIds in query
            converted_query = objectid_helper.convert_query_objectids(query)
            
            document = await self.collection.find_one(converted_query)
            if document:
                return objectid_helper.convert_dict_objectids(document)
            return None
        except Exception as e:
            logger.error(f"Error in find_one: {e}")
            return None
    
    async def find_by_id(self, document_id: str) -> Optional[Dict[str, Any]]:
        """Find document by ID"""
        try:
            if not objectid_helper.is_valid_objectid(document_id):
                return None
            
            objectid = objectid_helper.to_objectid(document_id)
            document = await self.collection.find_one({"_id": objectid})
            
            if document:
                return objectid_helper.convert_dict_objectids(document)
            return None
        except Exception as e:
            logger.error(f"Error in find_by_id: {e}")
            return None
    
    async def find_many(self, query: Dict[str, Any], limit: Optional[int] = None, skip: int = 0) -> List[Dict[str, Any]]:
        """Find many documents"""
        try:
            # Convert ObjectIds in query
            converted_query = objectid_helper.convert_query_objectids(query)
            
            cursor = self.collection.find(converted_query)
            
            if skip:
                cursor = cursor.skip(skip)
            if limit:
                cursor = cursor.limit(limit)
            
            documents = await async_iterator_helper.cursor_to_list(cursor)
            return objectid_helper.convert_list_objectids(documents)
        except Exception as e:
            logger.error(f"Error in find_many: {e}")
            return []
    
    async def find_all(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Find all documents"""
        try:
            cursor = self.collection.find({})
            
            if limit:
                cursor = cursor.limit(limit)
            
            documents = await async_iterator_helper.cursor_to_list(cursor)
            return objectid_helper.convert_list_objectids(documents)
        except Exception as e:
            logger.error(f"Error in find_all: {e}")
            return []
    
    async def insert_one(self, document: Dict[str, Any]) -> Optional[str]:
        """Insert one document"""
        try:
            # Ensure _id is ObjectId if not provided
            if "_id" not in document:
                document["_id"] = objectid_helper.create_objectid()
            elif isinstance(document["_id"], str):
                objectid = objectid_helper.to_objectid(document["_id"])
                if objectid:
                    document["_id"] = objectid
            
            result = await self.collection.insert_one(document)
            return str(result.inserted_id)
        except Exception as e:
            logger.error(f"Error in insert_one: {e}")
            return None
    
    async def insert_many(self, documents: List[Dict[str, Any]]) -> List[str]:
        """Insert many documents"""
        try:
            # Process documents
            processed_docs = []
            for doc in documents:
                if "_id" not in doc:
                    doc["_id"] = objectid_helper.create_objectid()
                elif isinstance(doc["_id"], str):
                    objectid = objectid_helper.to_objectid(doc["_id"])
                    if objectid:
                        doc["_id"] = objectid
                processed_docs.append(doc)
            
            result = await self.collection.insert_many(processed_docs)
            return [str(id) for id in result.inserted_ids]
        except Exception as e:
            logger.error(f"Error in insert_many: {e}")
            return []
    
    async def update_one(self, query: Dict[str, Any], update: Dict[str, Any]) -> bool:
        """Update one document"""
        try:
            # Convert ObjectIds in query
            converted_query = objectid_helper.convert_query_objectids(query)
            
            result = await self.collection.update_one(converted_query, update)
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"Error in update_one: {e}")
            return False
    
    async def update_by_id(self, document_id: str, update: Dict[str, Any]) -> bool:
        """Update document by ID"""
        try:
            if not objectid_helper.is_valid_objectid(document_id):
                return False
            
            objectid = objectid_helper.to_objectid(document_id)
            result = await self.collection.update_one({"_id": objectid}, update)
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"Error in update_by_id: {e}")
            return False
    
    async def update_many(self, query: Dict[str, Any], update: Dict[str, Any]) -> int:
        """Update many documents"""
        try:
            # Convert ObjectIds in query
            converted_query = objectid_helper.convert_query_objectids(query)
            
            result = await self.collection.update_many(converted_query, update)
            return result.modified_count
        except Exception as e:
            logger.error(f"Error in update_many: {e}")
            return 0
    
    async def delete_one(self, query: Dict[str, Any]) -> bool:
        """Delete one document"""
        try:
            # Convert ObjectIds in query
            converted_query = objectid_helper.convert_query_objectids(query)
            
            result = await self.collection.delete_one(converted_query)
            return result.deleted_count > 0
        except Exception as e:
            logger.error(f"Error in delete_one: {e}")
            return False
    
    async def delete_by_id(self, document_id: str) -> bool:
        """Delete document by ID"""
        try:
            if not objectid_helper.is_valid_objectid(document_id):
                return False
            
            objectid = objectid_helper.to_objectid(document_id)
            result = await self.collection.delete_one({"_id": objectid})
            return result.deleted_count > 0
        except Exception as e:
            logger.error(f"Error in delete_by_id: {e}")
            return False
    
    async def delete_many(self, query: Dict[str, Any]) -> int:
        """Delete many documents"""
        try:
            # Convert ObjectIds in query
            converted_query = objectid_helper.convert_query_objectids(query)
            
            result = await self.collection.delete_many(converted_query)
            return result.deleted_count
        except Exception as e:
            logger.error(f"Error in delete_many: {e}")
            return 0
    
    async def count(self, query: Dict[str, Any] = None) -> int:
        """Count documents"""
        try:
            if query is None:
                query = {}
            
            # Convert ObjectIds in query
            converted_query = objectid_helper.convert_query_objectids(query)
            
            return await self.collection.count_documents(converted_query)
        except Exception as e:
            logger.error(f"Error in count: {e}")
            return 0
    
    async def exists(self, query: Dict[str, Any]) -> bool:
        """Check if document exists"""
        try:
            # Convert ObjectIds in query
            converted_query = objectid_helper.convert_query_objectids(query)
            
            cursor = self.collection.find(converted_query).limit(1)
            return await async_iterator_helper.cursor_exists(cursor)
        except Exception as e:
            logger.error(f"Error in exists: {e}")
            return False
    
    async def aggregate(self, pipeline: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Aggregate documents"""
        try:
            cursor = self.collection.aggregate(pipeline)
            documents = await async_iterator_helper.cursor_to_list(cursor)
            return objectid_helper.convert_list_objectids(documents)
        except Exception as e:
            logger.error(f"Error in aggregate: {e}")
            return []
    
    async def distinct(self, field: str, query: Dict[str, Any] = None) -> List[Any]:
        """Get distinct values"""
        try:
            if query is None:
                query = {}
            
            # Convert ObjectIds in query
            converted_query = objectid_helper.convert_query_objectids(query)
            
            return await self.collection.distinct(field, converted_query)
        except Exception as e:
            logger.error(f"Error in distinct: {e}")
            return []
    
    async def create_index(self, keys: List[tuple], **kwargs) -> str:
        """Create index"""
        try:
            return await self.collection.create_index(keys, **kwargs)
        except Exception as e:
            logger.error(f"Error in create_index: {e}")
            return ""
    
    async def drop_index(self, index_name: str) -> bool:
        """Drop index"""
        try:
            await self.collection.drop_index(index_name)
            return True
        except Exception as e:
            logger.error(f"Error in drop_index: {e}")
            return False
    
    async def list_indexes(self) -> List[Dict[str, Any]]:
        """List indexes"""
        try:
            cursor = self.collection.list_indexes()
            return await async_iterator_helper.cursor_to_list(cursor)
        except Exception as e:
            logger.error(f"Error in list_indexes: {e}")
            return [] 