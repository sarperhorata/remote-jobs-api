from datetime import datetime
from typing import Annotated, List, Optional

from bson import ObjectId
from pydantic import (BaseModel, ConfigDict, Field, GetCoreSchemaHandler,
                      GetJsonSchemaHandler)
from pydantic.json_schema import JsonSchemaValue
from pydantic_core import CoreSchema


class PyObjectId(ObjectId):
    @classmethod
    def __get_pydantic_core_schema__(
        cls, source_type, handler: GetCoreSchemaHandler
    ) -> CoreSchema:
        from pydantic_core import core_schema

        return core_schema.json_or_python_schema(
            json_schema=core_schema.str_schema(),
            python_schema=core_schema.union_schema(
                [
                    core_schema.is_instance_schema(ObjectId),
                    core_schema.chain_schema(
                        [
                            core_schema.str_schema(),
                            core_schema.no_info_plain_validator_function(cls.validate),
                        ]
                    ),
                ]
            ),
            serialization=core_schema.plain_serializer_function_ser_schema(
                str, return_schema=core_schema.str_schema()
            ),
        )

    @classmethod
    def __get_pydantic_json_schema__(
        cls, core_schema: CoreSchema, handler: GetJsonSchemaHandler
    ) -> JsonSchemaValue:
        json_schema = handler(core_schema)
        json_schema.update(type="string")
        return json_schema

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)


class JobBase(BaseModel):
    title: str
    company: str
    location: str
    description: str
    requirements: str
    salary_range: str
    job_type: str
    experience_level: str
    apply_url: str
    remote_type: Optional[str] = None
    benefits: Optional[List[str]] = None
    skills: Optional[List[str]] = None
    application_deadline: Optional[datetime] = None


class JobCreate(JobBase):
    """Model for creating a job - datetime fields are set automatically by the API"""

    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class JobUpdate(BaseModel):
    title: Optional[str] = None
    company: Optional[str] = None
    location: Optional[str] = None
    description: Optional[str] = None
    requirements: Optional[str] = None
    salary_range: Optional[str] = None
    job_type: Optional[str] = None
    experience_level: Optional[str] = None
    apply_url: Optional[str] = None
    remote_type: Optional[str] = None
    benefits: Optional[List[str]] = None
    skills: Optional[List[str]] = None
    application_deadline: Optional[datetime] = None
    is_active: Optional[bool] = None


class JobResponse(JobBase):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    views_count: int = 0
    applications_count: int = 0

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str, datetime: lambda dt: dt.isoformat()},
        json_schema_serialization_defaults_required=True,
    )


class JobListResponse(BaseModel):
    items: List[JobResponse]
    total: int
    page: int
    per_page: int
    total_pages: int
