# tests/test_git_service.py
import pytest
from pathlib import Path
from apps.api.services.git_service import GitService

# Sample repos for validation
PYTHON_TEST_REPO = "https://github.com/psf/requests.git"
TYPESCRIPT_TEST_REPO = "https://github.com/sindresorhus/is-plain-obj.git"

@pytest.fixture
def tmp_clone_dir(tmp_path):
    """Provides isolated temporary paths for testing clone instances."""
    return tmp_path / "test_clones"

def test_clone_python_repository(tmp_clone_dir):
    """Validates cloning a small Python repository."""
    target_dir = tmp_clone_dir / "python_repo"
    
    commit_sha = GitService.clone_repository(
        repo_url=PYTHON_TEST_REPO,
        branch="main",
        target_dir=target_dir
    )

    # Assertions
    assert target_dir.exists()
    assert (target_dir / "pyproject.toml").exists() or (target_dir / "setup.py").exists()
    assert len(commit_sha) == 40

    # Cleanup
    GitService.cleanup_directory(tmp_clone_dir)
    assert not target_dir.exists()

def test_clone_typescript_repository(tmp_clone_dir):
    """Validates cloning a small TypeScript repository."""
    target_dir = tmp_clone_dir / "ts_repo"
    
    commit_sha = GitService.clone_repository(
        repo_url=TYPESCRIPT_TEST_REPO,
        branch="main",
        target_dir=target_dir
    )

    # Assertions
    assert target_dir.exists()
    assert (target_dir / "package.json").exists()
    assert len(commit_sha) == 40

    # Cleanup
    GitService.cleanup_directory(tmp_clone_dir)
    assert not target_dir.exists()