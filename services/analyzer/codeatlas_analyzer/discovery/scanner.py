# services/analyzer/codeatlas_analyzer/discovery/scanner.py
import os
from pathlib import Path
from typing import List, Dict
from codeatlas_analyzer.discovery.models import DiscoveredFile

# Supported extensions mapping to normalized language identifiers
SUPPORTED_EXTENSIONS: Dict[str, str] = {
    ".py": "python",
    ".pyi": "python",
    ".ts": "typescript",
    ".tsx": "typescript",
    ".js": "javascript",
    ".jsx": "javascript",
    ".mjs": "javascript",
    ".cjs": "javascript",
}

# Ignored directory names across Python, Node, Git, and build artifacts
IGNORED_DIRECTORIES = {
    ".git",
    "node_modules",
    ".venv",
    "venv",
    "env",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    "dist",
    "build",
    ".next",
    ".turbo",
    "target",
    "coverage",
    ".idea",
    ".vscode",
}

def discover_source_files(root_dir: str | Path) -> List[DiscoveredFile]:
    root_path = Path(root_dir).resolve()
    if not root_path.exists() or not root_path.is_dir():
        raise ValueError(f"Invalid directory path: {root_dir}")

    discovered: List[DiscoveredFile] = []

    for current_root, dirs, files in os.walk(root_path, topdown=True):
        # Prune ignored directories in-place
        dirs[:] = [d for d in dirs if d not in IGNORED_DIRECTORIES and not d.startswith(".")]

        for file_name in files:
            file_path = Path(current_root) / file_name
            ext = file_path.suffix.lower()

            if ext in SUPPORTED_EXTENSIONS:
                try:
                    stat = file_path.stat()
                    relative_path = file_path.relative_to(root_path).as_posix()
                    discovered.append(
                        DiscoveredFile(
                            relative_path=relative_path,
                            absolute_path=str(file_path.resolve()),
                            extension=ext,
                            size_bytes=stat.st_size,
                            language=SUPPORTED_EXTENSIONS[ext],
                        )
                    )
                except (OSError, PermissionError):
                    continue

    return discovered