"""Immutable source snapshot contracts and deterministic tree fingerprints."""

from __future__ import annotations

from dataclasses import dataclass, field
import hashlib
import json
import os
from pathlib import Path
import shutil
from typing import Callable

TREE_EXCLUDED_DIRECTORIES = frozenset(
    {
        ".git",
        ".ansibleguard-cache",
        "ansibleguard-output",
        "__pycache__",
    }
)


@dataclass(frozen=True)
class SourceCapabilities:
    """Operations that can be performed from a materialized source."""

    working_tree: bool = True
    git_history: bool = False
    diff: bool = False
    pull_requests: bool = False

    def as_dict(self) -> dict[str, bool]:
        return {
            "working_tree": self.working_tree,
            "git_history": self.git_history,
            "diff": self.diff,
            "pull_requests": self.pull_requests,
        }


@dataclass(frozen=True)
class SourceSnapshot:
    """A provider-neutral, immutable description of materialized source."""

    root: Path
    provider: str
    repository: str | None = None
    requested_ref: str | None = None
    resolved_sha: str | None = None
    acquisition: str = "filesystem"
    tree_sha256: str | None = None
    temporary: bool = False
    capabilities: SourceCapabilities = field(default_factory=SourceCapabilities)
    metadata: dict = field(default_factory=dict)

    def provenance(self) -> dict:
        return {
            "schema_version": 1,
            "provider": self.provider,
            "repository": self.repository,
            "requested_ref": self.requested_ref,
            "resolved_sha": self.resolved_sha,
            "acquisition": self.acquisition,
            "tree_sha256": self.tree_sha256,
            "temporary": self.temporary,
            "capabilities": self.capabilities.as_dict(),
            "metadata": dict(self.metadata),
        }


class MaterializedSource:
    """Context manager that guarantees provider cleanup."""

    def __init__(
        self,
        snapshot: SourceSnapshot,
        cleanup: Callable[[], None] | None = None,
    ) -> None:
        self.snapshot = snapshot
        self._cleanup = cleanup
        self._closed = False

    def __enter__(self) -> SourceSnapshot:
        return self.snapshot

    def __exit__(self, exc_type, exc, traceback) -> bool:
        self.close()
        return False

    def close(self) -> None:
        if self._closed:
            return
        self._closed = True
        if self._cleanup is not None:
            self._cleanup()

    @classmethod
    def temporary_directory(
        cls, snapshot: SourceSnapshot, temporary_root: Path
    ) -> "MaterializedSource":
        return cls(snapshot, lambda: shutil.rmtree(temporary_root, ignore_errors=True))


def _tree_entries(root: Path) -> list[dict[str, str]]:
    root = Path(root).resolve()
    if root.is_file():
        candidates = [root]
        base = root.parent
    else:
        candidates = []
        base = root
        for current, directories, filenames in os.walk(root, followlinks=False):
            directories[:] = sorted(
                name for name in directories if name not in TREE_EXCLUDED_DIRECTORIES
            )
            current_path = Path(current)
            candidates.extend(current_path / name for name in sorted(filenames))
            candidates.extend(
                current_path / name
                for name in directories
                if (current_path / name).is_symlink()
            )

    entries = []
    seen = set()
    for path in sorted(candidates, key=lambda value: value.as_posix()):
        relative = path.relative_to(base).as_posix()
        if relative in seen:
            continue
        seen.add(relative)
        if path.is_symlink():
            payload = os.readlink(path).encode("utf-8", errors="surrogateescape")
            kind = "symlink"
        elif path.is_file():
            payload = path.read_bytes()
            kind = "file"
        else:
            continue
        entries.append(
            {
                "path": relative,
                "kind": kind,
                "sha256": hashlib.sha256(payload).hexdigest(),
            }
        )
    return entries


def fingerprint_tree(root: Path) -> tuple[str, tuple[dict[str, str], ...]]:
    """Hash a stable manifest of paths, object kinds, and content hashes."""

    entries = tuple(_tree_entries(root))
    encoded = json.dumps(entries, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest(), entries
