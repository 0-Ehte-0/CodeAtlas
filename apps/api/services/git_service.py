# apps/api/services/git_service.py
import os
import stat
import shutil
import logging
from pathlib import Path
from git import Repo, GitCommandError

logger = logging.getLogger(__name__)

BASE_STORAGE_PATH = Path(os.getenv("STORAGE_PATH", "./storage/repositories")).resolve()

class GitService:
    """Service responsible for local disk management and Git checkout operations."""

    @staticmethod
    def _remove_readonly(func, path, exc_info):
        """
        Error handler for shutil.rmtree to handle read-only files on Windows.
        Clears the read-only flag and re-attempts the deletion.
        """
        os.chmod(path, stat.S_IWRITE)
        func(path)

    @staticmethod
    def get_snapshot_path(repo_id: str, snapshot_id: str) -> Path:
        """Generates predictable local filesystem directory for snapshot clones."""
        path = BASE_STORAGE_PATH / str(repo_id) / str(snapshot_id) / "source_code"
        path.mkdir(parents=True, exist_ok=True)
        return path

    @classmethod
    def clone_repository(
        cls, 
        repo_url: str, 
        branch: str, 
        target_dir: Path
    ) -> str:
        """
        Clones a Git repository to disk and returns the active HEAD commit SHA.
        """
        logger.info(f"Cloning {repo_url} (branch: {branch}) into {target_dir}")
        cloned_repo = None
        try:
            cloned_repo = Repo.clone_from(
                url=repo_url,
                to_path=target_dir,
                branch=branch,
                depth=1
            )
            commit_sha = cloned_repo.head.commit.hexsha
            logger.info(f"Successfully cloned repository. HEAD SHA: {commit_sha}")
            return commit_sha

        except GitCommandError as e:
            logger.error(f"Failed to clone repository: {str(e)}")
            cls.cleanup_directory(target_dir.parent)
            raise RuntimeError(f"Git clone operation failed: {e.stderr.strip()}")
        finally:
            # Explicitly close repo object to release Windows file locks
            if cloned_repo:
                cloned_repo.close()

    @classmethod
    def cleanup_directory(cls, path: Path) -> None:
        """Removes local directory subtree when snapshots are deleted or fail."""
        if path.exists() and path.is_dir():
            try:
                # Pass the permission error handler to force-delete read-only .git pack files
                shutil.rmtree(path, onerror=cls._remove_readonly)
                logger.info(f"Cleaned up directory: {path}")
            except Exception as e:
                logger.error(f"Error cleaning up directory {path}: {str(e)}")