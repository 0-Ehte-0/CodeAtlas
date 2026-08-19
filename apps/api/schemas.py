# apps/api/schemas.py
import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, HttpUrl, Field, ConfigDict
from codeatlas_contracts.enums import IndexStatus

class RepositoryBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255, example="CodeAtlas API")
    url: str = Field(..., example="https://github.com/organization/repository.git")
    default_branch: str = Field(default="main", example="main")
    description: Optional[str] = Field(default=None)

class RepositoryCreate(RepositoryBase):
    """Payload required to create a new repository."""
    pass

class RepositoryResponse(RepositoryBase):
    """Serialized repository data returned to clients."""
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class IndexJobCreateRequest(BaseModel):
    ref: Optional[str] = None

class IndexJobResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    job_id: str
    repository_id: uuid.UUID
    status: IndexStatus
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: datetime