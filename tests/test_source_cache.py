import json
import os
from pathlib import Path

import pytest

from ansibleguard.sources.cache.filesystem import FileSystemCache
from ansibleguard.sources.cache.keys import SourceCacheKey
from ansibleguard.sources.cache.redis import RedisCache
from ansibleguard.sources.errors import SourceError
from ansibleguard.sources.snapshot import fingerprint_tree


def _key(repository="owner/repo", commit="a" * 40):
    return SourceCacheKey(
        provider="github",
        host="github.com",
        repository=repository,
        commit=commit,
        acquisition="archive",
    )


def test_cache_key_uses_full_sha_repository_and_policy():
    first = _key("owner/one")
    second = _key("owner/two")
    third = SourceCacheKey(**{**first.canonical(), "include_lfs": True})
    assert len({first.digest, second.digest, third.digest}) == 3
    with pytest.raises(SourceError, match="full 40-character"):
        _key(commit="abc123")


def test_filesystem_cache_round_trip_verifies_tree_and_private_permissions(tmp_path):
    source = tmp_path / "source"
    source.mkdir()
    (source / "site.yml").write_text("- hosts: all\n", encoding="utf-8")
    tree_hash, _ = fingerprint_tree(source)
    cache = FileSystemCache(tmp_path / "cache")

    stored = cache.store(_key(), source, tree_hash, metadata={"private": True})
    found = cache.lookup(_key())
    destination = tmp_path / "materialized"
    cache.materialize(found, destination)

    assert stored.tree_sha256 == found.tree_sha256 == tree_hash
    assert (destination / "site.yml").read_text() == "- hosts: all\n"
    assert os.stat(cache.root).st_mode & 0o077 == 0
    assert os.stat(Path(found.storage_path) / "site.yml").st_mode & 0o077 == 0
    assert "token" not in json.dumps(found.as_dict()).lower()


def test_filesystem_cache_invalidates_corrupted_tree(tmp_path):
    source = tmp_path / "source"
    source.mkdir()
    (source / "site.yml").write_text("original\n", encoding="utf-8")
    tree_hash, _ = fingerprint_tree(source)
    cache = FileSystemCache(tmp_path / "cache")
    record = cache.store(_key(), source, tree_hash)
    (Path(record.storage_path) / "site.yml").write_text("corrupt\n", encoding="utf-8")

    assert cache.lookup(_key()) is None
    assert not Path(record.storage_path).exists()


class FakeRedis:
    def __init__(self):
        self.values = {}

    def get(self, key):
        return self.values.get(key)

    def set(self, key, value, nx=False, ex=None):
        if nx and key in self.values:
            return False
        self.values[key] = value
        return True

    def delete(self, key):
        self.values.pop(key, None)

    def eval(self, script, count, key, owner):
        if self.values.get(key) == owner:
            self.delete(key)
            return 1
        return 0


def test_redis_cache_stores_only_metadata_and_releases_lock(tmp_path):
    source = tmp_path / "source"
    source.mkdir()
    (source / "site.yml").write_text("content\n", encoding="utf-8")
    tree_hash, _ = fingerprint_tree(source)
    redis = FakeRedis()
    blobs = FileSystemCache(tmp_path / "blobs")
    cache = RedisCache(redis, blobs)

    record = cache.store(_key(), source, tree_hash)
    assert json.loads(redis.values[_key().redis_name])["tree_sha256"] == tree_hash
    assert "content" not in redis.values[_key().redis_name]
    assert cache.lookup(_key()).storage_path == record.storage_path

    lock_name = f"{_key().redis_name}:lock"
    with cache.lock(_key()):
        assert lock_name in redis.values
    assert lock_name not in redis.values


def test_cache_clean_preserves_pinned_entries_by_default(tmp_path):
    first = tmp_path / "first"
    second = tmp_path / "second"
    first.mkdir()
    second.mkdir()
    (first / "a.yml").write_text("a: 1\n")
    (second / "b.yml").write_text("b: 2\n")
    cache = FileSystemCache(tmp_path / "cache")
    first_hash, _ = fingerprint_tree(first)
    second_hash, _ = fingerprint_tree(second)
    cache.store(_key("owner/normal"), first, first_hash)
    cache.store(_key("owner/pinned"), second, second_hash, pinned=True)

    result = cache.clean()

    assert result["removed"] == 1
    assert cache.lookup(_key("owner/normal")) is None
    assert cache.lookup(_key("owner/pinned")) is not None


def test_redis_factory_requires_environment_url(tmp_path, monkeypatch):
    from ansibleguard.sources.cache.factory import create_cache_backend

    monkeypatch.delenv("ANSIBLEGUARD_REDIS_URL", raising=False)
    with pytest.raises(SourceError, match="ANSIBLEGUARD_REDIS_URL"):
        create_cache_backend(backend="redis", cache_dir=tmp_path / "cache")
