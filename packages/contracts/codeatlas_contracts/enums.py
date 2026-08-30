from enum import Enum

class IndexStatus(str, Enum):
    """
    Represents the lifecycle state of a repository indexing job.
    """
    PENDING = "PENDING"        # Job created, not yet sent to Redis queue
    QUEUED = "QUEUED"          # Job published to Redis queue
    PROCESSING = "PROCESSING"  # Analyzer has picked up the job and is parsing
    COMPLETED = "COMPLETED"    # Graph and vectors successfully stored
    FAILED = "FAILED"          # Processing encountered an error

class SupportedLanguage(str, Enum):
    PYTHON = "python"
    TYPESCRIPT = "typescript"
    JAVASCRIPT = "javascript"
    HTML = "html"
    CSS = "css"
    UNKNOWN = "unknown"

    @classmethod
    def from_extension(cls, extension: str) -> "SupportedLanguage":
        """Maps file extensions (with or without leading dot) to SupportedLanguage."""
        ext = extension.lower().lstrip(".")
        mapping = {
            "py": cls.PYTHON,
            "pyi": cls.PYTHON,
            "ts": cls.TYPESCRIPT,
            "tsx": cls.TYPESCRIPT,
            "mts": cls.TYPESCRIPT,
            "cts": cls.TYPESCRIPT,
            "js": cls.JAVASCRIPT,
            "jsx": cls.JAVASCRIPT,
            "mjs": cls.JAVASCRIPT,
            "cjs": cls.JAVASCRIPT,
            "html": cls.HTML, 
            "htm": cls.HTML,
            "css": cls.CSS,
        }
        return mapping.get(ext, cls.UNKNOWN)