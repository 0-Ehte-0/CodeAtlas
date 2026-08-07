# apps/api/utils/validators.py
import re
from fastapi import HTTPException, status

GIT_URL_REGEX = re.compile(
    r'^(https?://|git@|ssh://)([\w\.\@\-]+)[:/]([\w,\-,\_]+)/([\w,\-,\_]+)(\.git)?$'
)

def validate_git_url(url: str) -> None:
    """Validates if the provided string follows standard Git repository URL structures."""
    if not GIT_URL_REGEX.match(url):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Invalid Git repository URL. Must be a HTTP(S) or SSH Git endpoint."
        )