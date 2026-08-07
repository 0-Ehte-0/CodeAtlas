# apps/api/routes/snapshots.py
import uuid
from fastapi import APIRouter, Depends, BackgroundTasks, HTTPException, status
from sqlalchemy.orm import Session

from database import get_db
from models import Repository, Snapshot, SnapshotStatus
from services.git_service import GitService

router = APIRouter(prefix="/api/v1/repositories", tags=["Snapshots"])

def process_clone_task(snapshot_id: uuid.UUID, repo_url: str, branch: str, db: Session):
    """Background task handling asynchronous git checkout."""
    snapshot = db.get(Snapshot, snapshot_id)
    if not snapshot:
        return

    target_path = GitService.get_snapshot_path(snapshot.repository_id, snapshot.id)
    snapshot.status = SnapshotStatus.CLONING
    db.commit()

    try:
        commit_sha = GitService.clone_repository(
            repo_url=repo_url,
            branch=branch,
            target_dir=target_path
        )
        snapshot.commit_sha = commit_sha
        snapshot.storage_path = str(target_path)
        snapshot.status = SnapshotStatus.READY
    except Exception as exc:
        snapshot.status = SnapshotStatus.FAILED
        snapshot.error_message = str(exc)
    finally:
        db.commit()

@router.post("/{repository_id}/clone", status_code=status.HTTP_202_ACCEPTED)
def trigger_repository_clone(
    repository_id: uuid.UUID,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Enqueues local storage acquisition for a repository."""
    repo = db.get(Repository, repository_id)
    if not repo:
        raise HTTPException(status_code=404, detail="Repository not found")

    snapshot = Snapshot(
        repository_id=repo.id,
        branch=repo.default_branch,
        status=SnapshotStatus.PENDING
    )
    db.add(snapshot)
    db.commit()
    db.refresh(snapshot)

    # Queue background task (will be migrated to Redis Queue in Phase 5)
    background_tasks.add_task(
        process_clone_task,
        snapshot_id=snapshot.id,
        repo_url=repo.url,
        branch=repo.default_branch,
        db=db
    )

    return {"snapshot_id": snapshot.id, "status": "CLONING_QUEUED"}