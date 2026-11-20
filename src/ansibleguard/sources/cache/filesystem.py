"""Secure filesystem blob/cache backend for desktop and server workers."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
import json
import os
from pathlib import Path
import shutil

from ..errors import SourceError
from ..snapshot import fingerprint_tree
from .base import CacheBackend, CacheRecord
from .keys import SourceCacheKey


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _tree_size(root: Path) -> int:
    total = 0
    for current, _, files in os.walk(root, followlinks=False):
        for name in files:
            try:
                total += (Path(current) / name).lstat().st_size
            except OSError:
                pass
    return total


def _restrict_permissions(root: Path) -> None:
    os.chmod(root, 0o700)
    for current, directories, filenames in os.walk(root, followlinks=False):
        for name in directories:
            path = Path(current) / name
            if not path.is_symlink():
                os.chmod(path, 0o700)
        for name in filenames:
            path = Path(current) / name
            if path.is_symlink():
                continue
            mode = path.stat().st_mode
            os.chmod(path, 0o700 if mode & 0o111 else 0o600)


class FileSystemCache(CacheBackend):
    def __init__(self, root: str | Path | None = None) -> None:
        self.root = Path(root or Path.home() / ".cache" / "ansibleguard" / "sources")
        self.root.mkdir(parents=True, exist_ok=True, mode=0o700)
        os.chmod(self.root, 0o700)

    def _entry(self, key: SourceCacheKey) -> Path:
        return self.root / key.provider.lower() / key.digest

    @staticmethod
    def _record(path: Path, payload: dict) -> CacheRecord:
        key = SourceCacheKey(**payload["key"])
        return CacheRecord(
            key=key,
            tree_sha256=payload["tree_sha256"],
            storage_path=str(path / "tree"),
            created_at=payload["created_at"],
            last_accessed_at=payload["last_accessed_at"],
            verified=bool(payload.get("verified")),
            pinned=bool(payload.get("pinned")),
            size_bytes=int(payload.get("size_bytes") or 0),
            metadata=payload.get("metadata") or {},
        )

    def lookup(self, key: SourceCacheKey) -> CacheRecord | None:
        entry = self._entry(key)
        metadata_path = entry / "metadata.json"
        tree = entry / "tree"
        if not metadata_path.is_file() or not tree.is_dir():
            return None
        try:
            payload = json.loads(metadata_path.read_text(encoding="utf-8"))
            record = self._record(entry, payload)
        except (OSError, ValueError, KeyError, TypeError):
            self.invalidate(key)
            return None
        if record.key.digest != key.digest:
            self.invalidate(key)
            return None
        actual, _ = fingerprint_tree(tree)
        if actual != record.tree_sha256:
            self.invalidate(key)
            return None
        payload["last_accessed_at"] = _utc_now()
        metadata_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        os.chmod(metadata_path, 0o600)
        return self._record(entry, payload)

    def store(
        self,
        key: SourceCacheKey,
        source_root: Path,
        tree_sha256: str,
        *,
        metadata: dict | None = None,
        pinned: bool = False,
    ) -> CacheRecord:
        actual, _ = fingerprint_tree(source_root)
        if actual != tree_sha256:
            raise SourceError("refusing to cache a tree with a mismatched fingerprint")
        entry = self._entry(key)
        temporary = entry.with_name(entry.name + ".partial")
        if temporary.exists():
            shutil.rmtree(temporary)
        temporary.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
        temporary.mkdir(mode=0o700)
        try:
            shutil.copytree(source_root, temporary / "tree", symlinks=True)
            _restrict_permissions(temporary / "tree")
            now = _utc_now()
            payload = {
                "schema_version": 1,
                "key": key.canonical(),
                "tree_sha256": tree_sha256,
                "created_at": now,
                "last_accessed_at": now,
                "verified": True,
                "pinned": bool(pinned),
                "size_bytes": _tree_size(temporary / "tree"),
                "metadata": metadata or {},
            }
            metadata_path = temporary / "metadata.json"
            metadata_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
            os.chmod(metadata_path, 0o600)
            if entry.exists():
                shutil.rmtree(entry)
            temporary.replace(entry)
        except Exception:
            shutil.rmtree(temporary, ignore_errors=True)
            raise
        return self._record(entry, payload)

    def materialize(self, record: CacheRecord, destination: Path) -> Path:
        source = Path(record.storage_path)
        if not source.is_dir():
            raise SourceError("cached source blob is missing")
        destination = Path(destination)
        shutil.copytree(source, destination, symlinks=True)
        return destination

    def invalidate(self, key: SourceCacheKey) -> None:
        entry = self._entry(key)
        if entry.exists():
            shutil.rmtree(entry)

    def info(self) -> dict:
        records = list(self.root.glob("*/*/metadata.json"))
        return {
            "backend": "filesystem",
            "root": str(self.root),
            "entries": len(records),
            "size_bytes": sum(
                int(json.loads(path.read_text()).get("size_bytes") or 0)
                for path in records
            ),
        }

    def clean(self, *, older_than_days=None, include_pinned=False) -> dict:
        cutoff = (
            _utc_now()
            if older_than_days is None
            else (
                datetime.now(timezone.utc) - timedelta(days=older_than_days)
            ).isoformat()
        )
        removed = 0
        freed = 0
        for metadata_path in list(self.root.glob("*/*/metadata.json")):
            try:
                payload = json.loads(metadata_path.read_text(encoding="utf-8"))
            except (OSError, ValueError):
                continue
            if payload.get("pinned") and not include_pinned:
                continue
            if str(payload.get("last_accessed_at") or "") > cutoff:
                continue
            freed += int(payload.get("size_bytes") or 0)
            shutil.rmtree(metadata_path.parent)
            removed += 1
        return {"removed": removed, "freed_bytes": freed}
