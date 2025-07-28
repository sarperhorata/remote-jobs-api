"""
Async Iterator Helper
Handles async iterator operations and cursor management
"""

import logging
from typing import AsyncIterator, List, Dict, Any, Optional
from motor.motor_asyncio import AsyncIOMotorCursor

logger = logging.getLogger(__name__)


class AsyncIteratorHelper:
    """Helper class for async iterator operations"""
    
    @staticmethod
    async def cursor_to_list(cursor: AsyncIOMotorCursor, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Convert cursor to list with optional limit"""
        try:
            if limit:
                cursor = cursor.limit(limit)
            
            result = await cursor.to_list(length=None)
            return result
        except Exception as e:
            logger.error(f"Error converting cursor to list: {e}")
            return []
    
    @staticmethod
    async def cursor_to_list_with_skip(cursor: AsyncIOMotorCursor, skip: int = 0, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Convert cursor to list with skip and limit"""
        try:
            if skip:
                cursor = cursor.skip(skip)
            if limit:
                cursor = cursor.limit(limit)
            
            result = await cursor.to_list(length=None)
            return result
        except Exception as e:
            logger.error(f"Error converting cursor to list with skip: {e}")
            return []
    
    @staticmethod
    async def cursor_count(cursor: AsyncIOMotorCursor) -> int:
        """Get count from cursor"""
        try:
            return await cursor.count_documents({})
        except Exception as e:
            logger.error(f"Error counting cursor: {e}")
            return 0
    
    @staticmethod
    async def cursor_exists(cursor: AsyncIOMotorCursor) -> bool:
        """Check if cursor has any documents"""
        try:
            return await cursor.count_documents({}) > 0
        except Exception as e:
            logger.error(f"Error checking cursor existence: {e}")
            return False
    
    @staticmethod
    async def cursor_first(cursor: AsyncIOMotorCursor) -> Optional[Dict[str, Any]]:
        """Get first document from cursor"""
        try:
            cursor = cursor.limit(1)
            result = await cursor.to_list(length=1)
            return result[0] if result else None
        except Exception as e:
            logger.error(f"Error getting first document: {e}")
            return None
    
    @staticmethod
    async def cursor_batch(cursor: AsyncIOMotorCursor, batch_size: int = 100) -> AsyncIterator[List[Dict[str, Any]]]:
        """Process cursor in batches"""
        try:
            batch = []
            async for document in cursor:
                batch.append(document)
                if len(batch) >= batch_size:
                    yield batch
                    batch = []
            
            # Yield remaining documents
            if batch:
                yield batch
        except Exception as e:
            logger.error(f"Error processing cursor in batches: {e}")
            yield []
    
    @staticmethod
    async def cursor_map(cursor: AsyncIOMotorCursor, transform_func) -> List[Any]:
        """Apply transform function to cursor documents"""
        try:
            result = []
            async for document in cursor:
                transformed = transform_func(document)
                result.append(transformed)
            return result
        except Exception as e:
            logger.error(f"Error mapping cursor: {e}")
            return []
    
    @staticmethod
    async def cursor_filter(cursor: AsyncIOMotorCursor, filter_func) -> List[Dict[str, Any]]:
        """Filter cursor documents"""
        try:
            result = []
            async for document in cursor:
                if filter_func(document):
                    result.append(document)
            return result
        except Exception as e:
            logger.error(f"Error filtering cursor: {e}")
            return []
    
    @staticmethod
    async def cursor_reduce(cursor: AsyncIOMotorCursor, reduce_func, initial_value=None):
        """Reduce cursor documents"""
        try:
            result = initial_value
            async for document in cursor:
                result = reduce_func(result, document)
            return result
        except Exception as e:
            logger.error(f"Error reducing cursor: {e}")
            return initial_value
    
    @staticmethod
    async def cursor_group_by(cursor: AsyncIOMotorCursor, key_func) -> Dict[str, List[Dict[str, Any]]]:
        """Group cursor documents by key"""
        try:
            groups = {}
            async for document in cursor:
                key = key_func(document)
                if key not in groups:
                    groups[key] = []
                groups[key].append(document)
            return groups
        except Exception as e:
            logger.error(f"Error grouping cursor: {e}")
            return {}
    
    @staticmethod
    async def cursor_sort(cursor: AsyncIOMotorCursor, sort_key, reverse: bool = False) -> List[Dict[str, Any]]:
        """Sort cursor documents in memory"""
        try:
            documents = await cursor.to_list(length=None)
            return sorted(documents, key=lambda x: x.get(sort_key), reverse=reverse)
        except Exception as e:
            logger.error(f"Error sorting cursor: {e}")
            return []
    
    @staticmethod
    async def cursor_unique(cursor: AsyncIOMotorCursor, key_func) -> List[Dict[str, Any]]:
        """Get unique documents from cursor based on key"""
        try:
            seen = set()
            unique_docs = []
            async for document in cursor:
                key = key_func(document)
                if key not in seen:
                    seen.add(key)
                    unique_docs.append(document)
            return unique_docs
        except Exception as e:
            logger.error(f"Error getting unique documents: {e}")
            return []
    
    @staticmethod
    async def cursor_chunk(cursor: AsyncIOMotorCursor, chunk_size: int = 1000) -> AsyncIterator[List[Dict[str, Any]]]:
        """Process cursor in large chunks"""
        try:
            chunk = []
            async for document in cursor:
                chunk.append(document)
                if len(chunk) >= chunk_size:
                    yield chunk
                    chunk = []
            
            # Yield remaining documents
            if chunk:
                yield chunk
        except Exception as e:
            logger.error(f"Error processing cursor in chunks: {e}")
            yield []


# Global helper instance
async_iterator_helper = AsyncIteratorHelper()


def safe_cursor_operation(func):
    """Decorator to safely handle cursor operations"""
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            logger.error(f"Cursor operation failed in {func.__name__}: {e}")
            return []
    return wrapper


def cursor_timeout(timeout_seconds: int = 30):
    """Decorator to add timeout to cursor operations"""
    import asyncio
    
    def decorator(func):
        async def wrapper(*args, **kwargs):
            try:
                return await asyncio.wait_for(func(*args, **kwargs), timeout=timeout_seconds)
            except asyncio.TimeoutError:
                logger.error(f"Cursor operation timed out in {func.__name__}")
                return []
            except Exception as e:
                logger.error(f"Cursor operation failed in {func.__name__}: {e}")
                return []
        return wrapper
    return decorator 