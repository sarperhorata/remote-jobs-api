"""
Schema Validation Helper
Performance optimized schema validation utilities
"""

import logging
import time
from typing import Dict, List, Any, Optional, Union, Type
from datetime import datetime, UTC
from pydantic import BaseModel, ValidationError, validator, root_validator
from pydantic.fields import Field
import functools

logger = logging.getLogger(__name__)


class SchemaValidator:
    """Performance optimized schema validator"""
    
    def __init__(self):
        self.validation_cache = {}
        self.error_cache = {}
    
    def validate_with_cache(self, schema_class: Type[BaseModel], data: Dict[str, Any]) -> Union[BaseModel, Dict[str, Any]]:
        """Validate data with caching for performance"""
        cache_key = f"{schema_class.__name__}_{hash(str(data))}"
        
        if cache_key in self.validation_cache:
            return self.validation_cache[cache_key]
        
        try:
            start_time = time.time()
            validated_data = schema_class(**data)
            validation_time = time.time() - start_time
            
            # Cache successful validation
            self.validation_cache[cache_key] = validated_data
            
            if validation_time > 0.1:  # Log slow validations
                logger.warning(f"Slow validation for {schema_class.__name__}: {validation_time:.3f}s")
            
            return validated_data
            
        except ValidationError as e:
            # Cache error for repeated invalid data
            error_key = f"error_{cache_key}"
            self.error_cache[error_key] = e.errors()
            raise
    
    def validate_batch(self, schema_class: Type[BaseModel], data_list: List[Dict[str, Any]]) -> List[Union[BaseModel, Dict[str, Any]]]:
        """Validate multiple items with optimized batch processing"""
        results = []
        errors = []
        
        for i, data in enumerate(data_list):
            try:
                validated = self.validate_with_cache(schema_class, data)
                results.append(validated)
            except ValidationError as e:
                errors.append({"index": i, "errors": e.errors(), "data": data})
        
        if errors:
            raise ValidationError(errors, model=schema_class)
        
        return results
    
    def validate_partial(self, schema_class: Type[BaseModel], data: Dict[str, Any], required_fields: List[str] = None) -> Dict[str, Any]:
        """Validate partial data (for updates)"""
        if required_fields:
            # Check required fields
            missing_fields = [field for field in required_fields if field not in data]
            if missing_fields:
                raise ValidationError(f"Missing required fields: {missing_fields}", model=schema_class)
        
        # Create partial schema
        partial_data = {k: v for k, v in data.items() if v is not None}
        
        try:
            return schema_class(**partial_data)
        except ValidationError as e:
            raise
    
    def clear_cache(self):
        """Clear validation cache"""
        self.validation_cache.clear()
        self.error_cache.clear()
        logger.info("Schema validation cache cleared")


# Global validator instance
schema_validator = SchemaValidator()


def validate_schema(schema_class: Type[BaseModel]):
    """Decorator for schema validation with performance monitoring"""
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            
            try:
                # Extract data from kwargs or args
                data = kwargs.get('data') or (args[0] if args else {})
                
                if isinstance(data, dict):
                    validated_data = schema_validator.validate_with_cache(schema_class, data)
                    kwargs['data'] = validated_data
                
                result = await func(*args, **kwargs)
                
                validation_time = time.time() - start_time
                if validation_time > 0.05:  # Log slow operations
                    logger.info(f"Schema validation in {func.__name__}: {validation_time:.3f}s")
                
                return result
                
            except ValidationError as e:
                logger.error(f"Schema validation failed in {func.__name__}: {e}")
                raise
            
        return wrapper
    return decorator


def validate_response_schema(schema_class: Type[BaseModel]):
    """Decorator for response schema validation"""
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            result = await func(*args, **kwargs)
            
            if isinstance(result, dict):
                try:
                    validated_result = schema_validator.validate_with_cache(schema_class, result)
                    return validated_result.dict()
                except ValidationError as e:
                    logger.error(f"Response validation failed in {func.__name__}: {e}")
                    return result
            
            return result
        
        return wrapper
    return decorator


class BaseSchema(BaseModel):
    """Base schema with performance optimizations"""
    
    class Config:
        # Performance optimizations
        validate_assignment = False  # Disable validation on assignment
        extra = "ignore"  # Ignore extra fields
        use_enum_values = True  # Use enum values directly
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }
    
    @validator('*', pre=True)
    def empty_str_to_none(cls, v):
        """Convert empty strings to None for better performance"""
        if v == "":
            return None
        return v
    
    @root_validator(pre=True)
    def remove_none_values(cls, values):
        """Remove None values for cleaner data"""
        return {k: v for k, v in values.items() if v is not None}


class PaginationSchema(BaseSchema):
    """Pagination schema with performance optimizations"""
    page: int = Field(default=1, ge=1, description="Page number")
    size: int = Field(default=20, ge=1, le=100, description="Page size")
    
    @validator('page', 'size', pre=True)
    def convert_to_int(cls, v):
        """Convert to int with error handling"""
        try:
            return int(v) if v is not None else v
        except (ValueError, TypeError):
            return v


class SearchSchema(BaseSchema):
    """Search schema with performance optimizations"""
    query: Optional[str] = Field(default=None, max_length=200, description="Search query")
    filters: Optional[Dict[str, Any]] = Field(default=None, description="Search filters")
    sort_by: Optional[str] = Field(default=None, description="Sort field")
    sort_order: Optional[str] = Field(default="desc", pattern="^(asc|desc)$", description="Sort order")
    
    @validator('query', pre=True)
    def clean_query(cls, v):
        """Clean search query"""
        if isinstance(v, str):
            return v.strip()[:200]  # Limit length
        return v
    
    @validator('sort_order', pre=True)
    def normalize_sort_order(cls, v):
        """Normalize sort order"""
        if isinstance(v, str):
            return v.lower()
        return v


class ErrorResponseSchema(BaseSchema):
    """Error response schema"""
    error: str = Field(description="Error message")
    message: Optional[str] = Field(default=None, description="Detailed error message")
    timestamp: str = Field(default_factory=lambda: datetime.now(UTC).isoformat(), description="Error timestamp")
    code: Optional[str] = Field(default=None, description="Error code")


class SuccessResponseSchema(BaseSchema):
    """Success response schema"""
    success: bool = Field(default=True, description="Success status")
    data: Optional[Any] = Field(default=None, description="Response data")
    message: Optional[str] = Field(default=None, description="Success message")
    timestamp: str = Field(default_factory=lambda: datetime.now(UTC).isoformat(), description="Response timestamp")


class ValidationErrorSchema(BaseSchema):
    """Validation error schema"""
    field: str = Field(description="Field name")
    message: str = Field(description="Validation message")
    value: Optional[Any] = Field(default=None, description="Invalid value")
    type: str = Field(default="validation_error", description="Error type")


def create_validation_error_response(field: str, message: str, value: Any = None) -> Dict[str, Any]:
    """Create standardized validation error response"""
    return ValidationErrorSchema(
        field=field,
        message=message,
        value=value,
        type="validation_error"
    ).dict()


def validate_and_transform_data(data: Dict[str, Any], transformations: Dict[str, callable] = None) -> Dict[str, Any]:
    """Validate and transform data with performance optimizations"""
    if transformations is None:
        transformations = {}
    
    transformed_data = {}
    
    for key, value in data.items():
        if key in transformations:
            try:
                transformed_value = transformations[key](value)
                transformed_data[key] = transformed_value
            except Exception as e:
                logger.warning(f"Transformation failed for field {key}: {e}")
                transformed_data[key] = value
        else:
            transformed_data[key] = value
    
    return transformed_data


def validate_required_fields(data: Dict[str, Any], required_fields: List[str]) -> List[str]:
    """Validate required fields with performance optimization"""
    missing_fields = []
    
    for field in required_fields:
        if field not in data or data[field] is None:
            missing_fields.append(field)
    
    return missing_fields


def sanitize_data(data: Dict[str, Any], allowed_fields: List[str] = None) -> Dict[str, Any]:
    """Sanitize data by removing unwanted fields"""
    if allowed_fields is None:
        return data
    
    return {k: v for k, v in data.items() if k in allowed_fields}


# Performance monitoring
class SchemaPerformanceMonitor:
    """Monitor schema validation performance"""
    
    def __init__(self):
        self.validation_times = {}
        self.error_counts = {}
        self.total_validations = 0
    
    def record_validation(self, schema_name: str, validation_time: float, success: bool):
        """Record validation performance"""
        if schema_name not in self.validation_times:
            self.validation_times[schema_name] = []
            self.error_counts[schema_name] = 0
        
        self.validation_times[schema_name].append(validation_time)
        self.total_validations += 1
        
        if not success:
            self.error_counts[schema_name] += 1
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get performance statistics"""
        stats = {}
        
        for schema_name, times in self.validation_times.items():
            if times:
                stats[schema_name] = {
                    "avg_time": sum(times) / len(times),
                    "max_time": max(times),
                    "min_time": min(times),
                    "total_validations": len(times),
                    "error_count": self.error_counts.get(schema_name, 0),
                    "error_rate": self.error_counts.get(schema_name, 0) / len(times) if times else 0
                }
        
        return stats
    
    def reset(self):
        """Reset performance monitor"""
        self.validation_times.clear()
        self.error_counts.clear()
        self.total_validations = 0


# Global performance monitor
performance_monitor = SchemaPerformanceMonitor() 