"""
ObjectId Helper
Handles ObjectId conversion and validation
"""

import logging
from typing import Any, Dict, List, Optional, Union
from bson import ObjectId
from bson.errors import InvalidId

logger = logging.getLogger(__name__)


class ObjectIdHelper:
    """Helper class for ObjectId operations"""
    
    @staticmethod
    def is_valid_objectid(objectid_str: str) -> bool:
        """Check if string is a valid ObjectId"""
        try:
            ObjectId(objectid_str)
            return True
        except (InvalidId, TypeError):
            return False
    
    @staticmethod
    def to_objectid(objectid_str: str) -> Optional[ObjectId]:
        """Convert string to ObjectId"""
        try:
            return ObjectId(objectid_str)
        except (InvalidId, TypeError) as e:
            logger.warning(f"Invalid ObjectId: {objectid_str}, error: {e}")
            return None
    
    @staticmethod
    def to_string(objectid: ObjectId) -> str:
        """Convert ObjectId to string"""
        return str(objectid)
    
    @staticmethod
    def convert_dict_objectids(data: Dict[str, Any]) -> Dict[str, Any]:
        """Convert ObjectIds in dictionary to strings"""
        converted = {}
        for key, value in data.items():
            if isinstance(value, ObjectId):
                converted[key] = str(value)
            elif isinstance(value, dict):
                converted[key] = ObjectIdHelper.convert_dict_objectids(value)
            elif isinstance(value, list):
                converted[key] = ObjectIdHelper.convert_list_objectids(value)
            else:
                converted[key] = value
        return converted
    
    @staticmethod
    def convert_list_objectids(data: List[Any]) -> List[Any]:
        """Convert ObjectIds in list to strings"""
        converted = []
        for item in data:
            if isinstance(item, ObjectId):
                converted.append(str(item))
            elif isinstance(item, dict):
                converted.append(ObjectIdHelper.convert_dict_objectids(item))
            elif isinstance(item, list):
                converted.append(ObjectIdHelper.convert_list_objectids(item))
            else:
                converted.append(item)
        return converted
    
    @staticmethod
    def convert_query_objectids(query: Dict[str, Any]) -> Dict[str, Any]:
        """Convert string ObjectIds in query to ObjectId objects"""
        converted = {}
        for key, value in query.items():
            if key == "_id" and isinstance(value, str):
                objectid = ObjectIdHelper.to_objectid(value)
                if objectid:
                    converted[key] = objectid
                else:
                    converted[key] = value
            elif key == "_id" and isinstance(value, dict):
                # Handle $in, $nin operators
                converted[key] = {}
                for operator, values in value.items():
                    if operator in ["$in", "$nin"] and isinstance(values, list):
                        converted[key][operator] = [
                            ObjectIdHelper.to_objectid(v) if isinstance(v, str) else v
                            for v in values
                        ]
                    else:
                        converted[key][operator] = values
            elif isinstance(value, dict):
                converted[key] = ObjectIdHelper.convert_query_objectids(value)
            elif isinstance(value, list):
                converted[key] = [
                    ObjectIdHelper.to_objectid(v) if isinstance(v, str) else v
                    for v in value
                ]
            else:
                converted[key] = value
        return converted
    
    @staticmethod
    def create_objectid() -> ObjectId:
        """Create new ObjectId"""
        return ObjectId()
    
    @staticmethod
    def from_datetime(datetime_obj) -> ObjectId:
        """Create ObjectId from datetime"""
        return ObjectId.from_datetime(datetime_obj)
    
    @staticmethod
    def get_datetime(objectid: ObjectId):
        """Get datetime from ObjectId"""
        return objectid.generation_time


# Global helper instance
objectid_helper = ObjectIdHelper()


def safe_objectid_conversion(func):
    """Decorator to safely convert ObjectIds in function results"""
    async def wrapper(*args, **kwargs):
        result = await func(*args, **kwargs)
        
        if isinstance(result, dict):
            return objectid_helper.convert_dict_objectids(result)
        elif isinstance(result, list):
            return objectid_helper.convert_list_objectids(result)
        else:
            return result
    
    return wrapper


def validate_objectid_param(param_name: str = "id"):
    """Decorator to validate ObjectId parameter"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # Get the parameter value
            param_value = kwargs.get(param_name)
            if param_value and not objectid_helper.is_valid_objectid(param_value):
                raise ValueError(f"Invalid {param_name}: {param_value}")
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator


def convert_objectid_fields(fields: List[str]):
    """Decorator to convert specific fields to ObjectId in query"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # Convert query parameters
            if "query" in kwargs:
                query = kwargs["query"]
                for field in fields:
                    if field in query and isinstance(query[field], str):
                        objectid = objectid_helper.to_objectid(query[field])
                        if objectid:
                            query[field] = objectid
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator 