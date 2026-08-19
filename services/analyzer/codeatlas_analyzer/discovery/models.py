# services/analyzer/codeatlas_analyzer/discovery/models.py
from pydantic import BaseModel

class DiscoveredFile(BaseModel):
    relative_path: str
    absolute_path: str
    extension: str
    size_bytes: int
    language: str