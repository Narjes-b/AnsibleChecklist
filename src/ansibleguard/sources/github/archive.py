"""Bounded, traversal-safe GitHub tar archive extraction."""

from __future__ import annotations

import os
from pathlib import Path, PurePosixPath
import shutil
import tarfile

from ..errors import SourceError

DEFAULT_MAX_ARCHIVE_BYTES = 250 * 1024 * 1024
DEFAULT_MAX_UNCOMPRESSED_BYTES = 2 * 1024 * 1024 * 1024
DEFAULT_MAX_FILES = 200_000


def _safe_parts(name: str) -> tuple[str, ...]:
    path = PurePosixPath(name)
    if path.is_absolute() or ".." in path.parts:
        raise SourceError("archive contains an unsafe path")
    parts = tuple(part for part in path.parts if part not in {"", "."})
    if not parts:
        raise SourceError("archive contains an empty path")
    return parts


def _inside(root: Path, candidate: Path) -> bool:
    try:
        candidate.resolve(strict=False).relative_to(root.resolve())
    except ValueError:
        return False
    return True


def secure_extract_tar(
    archive: Path,
    destination: Path,
    *,
    max_files: int = DEFAULT_MAX_FILES,
    max_uncompressed_bytes: int = DEFAULT_MAX_UNCOMPRESSED_BYTES,
) -> Path:
    """Extract one GitHub-style top-level tree without using extractall()."""

    archive = Path(archive)
    destination = Path(destination)
    destination.mkdir(parents=True, exist_ok=False)
    try:
        with tarfile.open(archive, mode="r:*") as source:
            members = source.getmembers()
            if len(members) > max_files:
                raise SourceError("archive exceeds the configured file-count limit")
            total = sum(member.size for member in members if member.isfile())
            if total > max_uncompressed_bytes:
                raise SourceError(
                    "archive exceeds the configured uncompressed-size limit"
                )
            parsed = [(member, _safe_parts(member.name)) for member in members]
            roots = {parts[0] for _, parts in parsed}
            if len(roots) != 1:
                raise SourceError(
                    "archive must contain exactly one top-level directory"
                )

            for member, parts in parsed:
                relative_parts = parts[1:]
                if not relative_parts:
                    continue
                target = destination.joinpath(*relative_parts)
                if not _inside(destination, target):
                    raise SourceError("archive path escapes the extraction directory")
                if member.isdir():
                    target.mkdir(parents=True, exist_ok=True)
                    continue
                target.parent.mkdir(parents=True, exist_ok=True)
                if member.isfile():
                    extracted = source.extractfile(member)
                    if extracted is None:
                        raise SourceError("archive regular file has no payload")
                    with extracted, target.open("wb") as output:
                        shutil.copyfileobj(extracted, output, length=1024 * 1024)
                    os.chmod(target, 0o755 if member.mode & 0o111 else 0o644)
                    continue
                if member.issym():
                    link = PurePosixPath(member.linkname)
                    if link.is_absolute():
                        raise SourceError("archive contains an absolute symlink")
                    resolved_link = target.parent.joinpath(*link.parts)
                    if not _inside(destination, resolved_link):
                        raise SourceError(
                            "archive symlink escapes the extraction directory"
                        )
                    target.symlink_to(member.linkname)
                    continue
                # Hard links can create non-obvious cross-member aliases. GitHub
                # source archives do not need them, so reject them with all
                # devices, sockets, and FIFOs.
                raise SourceError("archive contains an unsupported special entry")
    except Exception:
        shutil.rmtree(destination, ignore_errors=True)
        raise
    return destination
