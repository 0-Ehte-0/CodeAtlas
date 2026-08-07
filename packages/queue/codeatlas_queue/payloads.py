from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

class IndexJobPayload(BaseModel):
    """
    Data payload serialized to JSON and pushed to the Redis indexing queue.
    """
    # Matching job ID tracked in API storage
    job_id: str = Field(..., description="Unique job execution ID")
    
    # Repository ID to identify target metadata
    repository_id: str = Field(..., description="Target repository ID")
    
    # Git URL used by the worker to clone/pull the target repository
    clone_url: str = Field(..., description="Git clone URL")
    
    # Target commit SHA or branch name (optional, defaults to HEAD/default branch)
    ref: Optional[str] = Field(default=None, description="Specific branch, tag, or commit SHA")
    
    # Enqueue timestamp
    enqueued_at: datetime = Field(default_factory=datetime.utcnow, description="Time pushed to Redis")