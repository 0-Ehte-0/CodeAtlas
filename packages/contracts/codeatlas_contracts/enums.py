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