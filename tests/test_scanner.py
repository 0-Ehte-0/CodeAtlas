# tests/test_scanner.py
from pathlib import Path
import pytest
from codeatlas_analyzer.discovery.scanner import discover_source_files

def test_discover_source_files(tmp_path: Path):
    # Setup mock Python & TypeScript files
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "index.ts").write_text("console.log('hello');")
    (tmp_path / "src" / "app.tsx").write_text("export const App = () => null;")
    (tmp_path / "main.py").write_text("print('hello')")

    # Setup ignored directories
    (tmp_path / "node_modules").mkdir()
    (tmp_path / "node_modules" / "bad.js").write_text("throw error;")
    (tmp_path / ".git").mkdir()
    (tmp_path / ".git" / "config.py").write_text("secret=1")
    (tmp_path / ".venv").mkdir()
    (tmp_path / ".venv" / "lib.py").write_text("import sys")

    files = discover_source_files(tmp_path)
    relative_paths = {f.relative_path for f in files}

    assert "main.py" in relative_paths
    assert "src/index.ts" in relative_paths
    assert "src/app.tsx" in relative_paths
    assert not any("node_modules" in p for p in relative_paths)
    assert not any(".git" in p for p in relative_paths)
    assert not any(".venv" in p for p in relative_paths)