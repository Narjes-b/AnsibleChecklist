"""Existing filesystem inputs exposed through the common source contract."""

from __future__ import annotations

from pathlib import Path
import subprocess

from .base import SourceProvider
from .errors import SourceError
from .snapshot import (
    MaterializedSource,
    SourceCapabilities,
    SourceSnapshot,
    fingerprint_tree,
)


def _git_text(root: Path, *arguments: str) -> str | None:
    location = root if root.is_dir() else root.parent
    try:
        completed = subprocess.run(
            ["git", "-C", str(location), *arguments],
            check=True,
            capture_output=True,
            text=True,
            timeout=10,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    return completed.stdout.strip() or None


class LocalSource(SourceProvider):
    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)

    def materialize(self) -> MaterializedSource:
        root = self.path.expanduser().resolve()
        if not root.exists():
            raise SourceError(f"local source path does not exist: {self.path}")
        tree_sha256, entries = fingerprint_tree(root)
        resolved_sha = _git_text(root, "rev-parse", "HEAD")
        status = _git_text(root, "status", "--porcelain", "--untracked-files=normal")
        snapshot = SourceSnapshot(
            root=root,
            provider="local",
            resolved_sha=resolved_sha,
            acquisition="filesystem",
            tree_sha256=tree_sha256,
            temporary=False,
            capabilities=SourceCapabilities(
                working_tree=True,
                git_history=resolved_sha is not None,
                diff=resolved_sha is not None,
                pull_requests=False,
            ),
            metadata={
                "tree_entry_count": len(entries),
                "git_dirty": bool(status),
            },
        )
        return MaterializedSource(snapshot)
