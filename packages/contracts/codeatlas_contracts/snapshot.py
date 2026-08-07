from datetime import datetime
from pydantic import BaseModel, Field

class RepositorySnapshot(BaseModel):
    """
    Represents an immutable point-in-time state of a repository commit.
    """
    # Unique snapshot identifier
    snapshot_id: str = Field(..., description="Unique snapshot ID")
    
    # Foreign key referencing the parent repository
    repository_id: str = Field(..., description="Parent repository ID")
    
    # Full Git commit SHA associated with this snapshot
    commit_hash: str = Field(..., description="Full git commit SHA processed")
    
    # Total source code files processed in this snapshot
    file_count: int = Field(default=0, ge=0, description="Total number of code files parsed")
    
    # Timestamp when indexing finished for this commit
    indexed_at: datetime = Field(default_factory=datetime.utcnow, description="Completion timestamp")