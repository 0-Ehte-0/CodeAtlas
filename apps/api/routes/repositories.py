# apps/api/routes/repositories.py
import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select
from redis_client import redis_client

from database import get_db
from models import Repository, IndexJob
from schemas import RepositoryCreate, RepositoryResponse, IndexJobCreateRequest, IndexJobResponse
from codeatlas_contracts.enums import IndexStatus
from codeatlas_queue.constants import INDEXING_QUEUE_NAME
from codeatlas_queue.payloads import IndexJobPayload
from codeatlas_observability import get_logger

logger = get_logger("codeatlas.api")
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

@router.post("/{repository_id}/index", response_model=IndexJobResponse, status_code=status.HTTP_202_ACCEPTED)
def create_indexing_job(
    repository_id: uuid.UUID,
    payload_in: IndexJobCreateRequest = None,
    db: Session = Depends(get_db)
):
    repository = db.scalar(select(Repository).where(Repository.id == repository_id))
    if not repository:
        raise HTTPException(status_code=404, detail="Repository not found")

    job_id = str(uuid.uuid4())
    ref = payload_in.ref if payload_in else repository.default_branch

    # 1. Record job in PostgreSQL
    new_job = IndexJob(
        job_id=job_id,
        repository_id=repository.id,
        status=IndexStatus.QUEUED
    )
    db.add(new_job)
    db.commit()
    db.refresh(new_job)

    # 2. Enqueue payload into Redis
    queue_payload = IndexJobPayload(
        job_id=job_id,
        repository_id=str(repository.id),
        clone_url=repository.url,
        ref=ref
    )
    redis_client.lpush(INDEXING_QUEUE_NAME, queue_payload.model_dump_json())
    logger.info(f"Enqueued indexing job {job_id} for repository {repository_id}")

    return new_job