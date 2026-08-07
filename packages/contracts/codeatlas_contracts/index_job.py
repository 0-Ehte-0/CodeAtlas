from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from codeatlas_contracts.enums import IndexStatus

class IndexJob(BaseModel):
    """
    Tracks the execution progress and state of an indexing operation.
    """
    # Unique identifier for this specific job execution
    job_id: str = Field(..., description="Unique job execution ID")
    
    # Associated repository ID
    repository_id: str = Field(..., description="Target repository ID being indexed")
    
    # Current status of the job execution
    status: IndexStatus = Field(default=IndexStatus.PENDING, description="Current lifecycle state")
    
    # Optional error message populated if status becomes FAILED
    error_message: Optional[str] = Field(default=None, description="Detailed error description if failed")
    
    # Creation and update tracking
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Job creation time")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Last status update time")