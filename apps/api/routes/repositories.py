# apps/api/routes/repositories.py
import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select

from database import get_db
from models import Repository
from schemas import RepositoryCreate, RepositoryResponse

router = APIRouter(prefix="/api/v1/repositories", tags=["Repositories"])

@router.post("", response_model=RepositoryResponse, status_code=status.HTTP_201_CREATED)
def create_repository(
    payload: RepositoryCreate, 
    db: Session = Depends(get_db)
):
    """Registers a new repository in PostgreSQL."""
    # Check if repository URL already exists
    existing = db.execute(
        select(Repository).where(Repository.url == payload.url)
    ).scalar_one_or_none()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Repository with URL '{payload.url}' already exists."
        )

    repo = Repository(
        name=payload.name,
        url=payload.url,
        default_branch=payload.default_branch,
        description=payload.description
    )
    db.add(repo)
    db.commit()
    db.refresh(repo)
    return repo

@router.get("", response_model=List[RepositoryResponse])
def list_repositories(
    skip: int = 0, 
    limit: int = 50, 
    db: Session = Depends(get_db)
):
    """Retrieves a paginated list of registered repositories."""
    stmt = select(Repository).offset(skip).limit(limit).order_by(Repository.created_at.desc())
    repositories = db.scalars(stmt).all()
    return repositories

@router.get("/{repository_id}", response_model=RepositoryResponse)
def get_repository_detail(
    repository_id: uuid.UUID, 
    db: Session = Depends(get_db)
):
    """Retrieves repository metadata by ID."""
    repo = db.get(Repository, repository_id)
    if not repo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Repository with ID '{repository_id}' not found."
        )
    return repo