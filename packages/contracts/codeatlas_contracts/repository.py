from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

class Repository(BaseModel):
    """
    Core representation of a code repository registered in CodeAtlas.
    """
    # Unique identifier for the repository (UUID string)
    id: str = Field(..., description="Unique repository ID")
    
    # Repository display name (e.g., 'facebook/react')
    name: str = Field(..., description="Repository full name or identifier")
    
    # Git clone URL (HTTPS or SSH)
    clone_url: str = Field(..., description="Git URL used for cloning the repository")
    
    # Default branch to analyze (e.g., 'main' or 'master')
    default_branch: str = Field(default="main", description="Target git branch")
    
    # Timestamp when the repository record was created
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Record creation timestamp")