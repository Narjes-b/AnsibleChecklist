"""GitLab archive/Git materialization through SourceSnapshot."""

from __future__ import annotations

from pathlib import Path
from contextlib import nullcontext
import shutil
import tempfile

from ..base import SourceProvider
from ..cache.base import CacheBackend
from ..cache.keys import SourceCacheKey
from ..errors import SourceError
from ..snapshot import (
    MaterializedSource,
    SourceCapabilities,
    SourceSnapshot,
    fingerprint_tree,
)
from ..github.archive import DEFAULT_MAX_ARCHIVE_BYTES, secure_extract_tar
from ..github.git import (
    find_lfs_pointers,
    materialize_git_checkout,
    verify_git_checkout,
)
from .auth import gitlab_git_auth_environment
from .client import GitLabClient
from .urls import GitLabTarget, parse_gitlab_target


class GitLabSource(SourceProvider):
    def __init__(
        self,
        target: str | GitLabTarget,
        *,
        ref=None,
        commit=None,
        host=None,
        acquisition="auto",
        history_required=False,
        include_submodules=False,
        include_lfs=False,
        client=None,
        cache: CacheBackend | None = None,
        max_archive_bytes=DEFAULT_MAX_ARCHIVE_BYTES,
    ):
        if ref and commit:
            raise SourceError("--ref and --commit are mutually exclusive")
        if acquisition not in {"auto", "archive", "git"}:
            raise SourceError("GitLab acquisition must be auto, archive, or git")
        self.target = (
            target
            if isinstance(target, GitLabTarget)
            else parse_gitlab_target(target, host=host)
        )
        self.ref = ref
        self.commit = commit
        self.acquisition = (
            "git"
            if acquisition == "auto" and history_required
            else ("archive" if acquisition == "auto" else acquisition)
        )
        self.include_submodules = include_submodules
        self.include_lfs = include_lfs
        self.client = client or GitLabClient(host=self.target.host)
        self.cache = cache
        self.max_archive_bytes = max_archive_bytes

    def _resolve(self):
        repository = self.target.full_name
        if self.commit:
            return self.client.resolve_ref(repository, self.commit), None, self.commit
        if self.ref:
            return self.client.resolve_ref(repository, self.ref), self.ref, None
        project = self.client.get_project(repository)
        default = str(project.get("default_branch") or "")
        if not default:
            raise SourceError("GitLab project has no resolvable default branch")
        return self.client.resolve_ref(repository, default), default, None

    def materialize(self):
        sha, requested_ref, requested_commit = self._resolve()
        repository = self.target.full_name
        key = SourceCacheKey(
            "gitlab",
            self.target.host,
            repository,
            sha,
            self.acquisition,
            self.include_submodules,
            self.include_lfs,
        )
        temporary_root = Path(tempfile.mkdtemp(prefix="ansibleguard-gitlab-"))
        tree = temporary_root / "repository"
        lock_context = self.cache.lock(key) if self.cache else nullcontext()
        try:
            lock_context.__enter__()
        except Exception:
            shutil.rmtree(temporary_root, ignore_errors=True)
            raise
        try:
            cached = self.cache.lookup(key) if self.cache else None
            if cached:
                self.cache.materialize(cached, tree)
                if self.acquisition == "git" and not verify_git_checkout(tree, sha):
                    self.cache.invalidate(key)
                    shutil.rmtree(tree, ignore_errors=True)
                    cached = None
            if cached:
                acquisition_metadata = dict((cached.metadata or {})["acquisition"])
                cache_status = "hit"
            elif self.acquisition == "archive":
                if self.include_submodules or self.include_lfs:
                    raise SourceError(
                        "submodule/LFS materialization requires Git acquisition"
                    )
                archive = temporary_root / "source.tar.gz"
                self.client.download_archive(
                    repository, sha, archive, max_bytes=self.max_archive_bytes
                )
                secure_extract_tar(archive, tree)
                archive.unlink(missing_ok=True)
                acquisition_metadata = {
                    "submodules": {
                        "present": (tree / ".gitmodules").is_file(),
                        "materialized": False,
                        "items": [],
                    },
                    "lfs": {
                        "pointers_detected": len(find_lfs_pointers(tree)),
                        "materialized": False,
                    },
                }
                cache_status = "miss"
            else:
                acquisition_metadata = materialize_git_checkout(
                    repository=repository,
                    host=self.target.host,
                    sha=sha,
                    destination=tree,
                    token=self.client.token,
                    include_submodules=self.include_submodules,
                    include_lfs=self.include_lfs,
                    auth_environment=gitlab_git_auth_environment(
                        self.client.token, self.target.host
                    ),
                )
                cache_status = "miss"
            tree_hash, entries = fingerprint_tree(tree)
            if not cached and self.cache:
                self.cache.store(
                    key, tree, tree_hash, metadata={"acquisition": acquisition_metadata}
                )
            capabilities = SourceCapabilities(
                working_tree=True,
                git_history=self.acquisition == "git",
                diff=self.acquisition == "git",
            )
            snapshot = SourceSnapshot(
                root=tree,
                provider="gitlab",
                repository=repository,
                requested_ref=requested_ref,
                resolved_sha=sha,
                acquisition=self.acquisition,
                tree_sha256=tree_hash,
                temporary=True,
                capabilities=capabilities,
                metadata={
                    "host": self.target.host,
                    "requested_commit": requested_commit,
                    "tree_entry_count": len(entries),
                    "submodules": acquisition_metadata["submodules"],
                    "lfs": acquisition_metadata["lfs"],
                    "cache": {"status": cache_status, "key": key.digest},
                },
            )
            return MaterializedSource.temporary_directory(snapshot, temporary_root)
        except Exception:
            shutil.rmtree(temporary_root, ignore_errors=True)
            raise
        finally:
            lock_context.__exit__(None, None, None)
