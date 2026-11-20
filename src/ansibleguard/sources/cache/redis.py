"""Optional Redis metadata/locking over a separate blob backend."""

from __future__ import annotations

from contextlib import contextmanager
import json
import secrets
import time

from ..errors import SourceError
from .base import CacheBackend, CacheRecord
from .keys import SourceCacheKey


class RedisCache(CacheBackend):
    """Redis indexes records and coordinates workers; blobs stay elsewhere."""

    def __init__(self, redis_client, blob_backend: CacheBackend, *, lock_ttl=600):
        self.redis = redis_client
        self.blobs = blob_backend
        self.lock_ttl = int(lock_ttl)

    def lookup(self, key: SourceCacheKey) -> CacheRecord | None:
        encoded = self.redis.get(key.redis_name)
        if not encoded:
            return None
        record = self.blobs.lookup(key)
        if record is None:
            self.redis.delete(key.redis_name)
            return None
        return record

    def store(self, key, source_root, tree_sha256, *, metadata=None, pinned=False):
        record = self.blobs.store(
            key,
            source_root,
            tree_sha256,
            metadata=metadata,
            pinned=pinned,
        )
        self.redis.set(key.redis_name, json.dumps(record.as_dict()))
        return record

    def materialize(self, record, destination):
        return self.blobs.materialize(record, destination)

    def invalidate(self, key):
        self.redis.delete(key.redis_name)
        self.blobs.invalidate(key)

    @contextmanager
    def lock(self, key: SourceCacheKey, *, wait_seconds=60):
        name = f"{key.redis_name}:lock"
        owner = secrets.token_hex(16)
        deadline = time.monotonic() + wait_seconds
        while not self.redis.set(name, owner, nx=True, ex=self.lock_ttl):
            if time.monotonic() >= deadline:
                raise SourceError("timed out waiting for the source cache lock")
            time.sleep(0.1)
        try:
            yield
        finally:
            script = (
                "if redis.call('get', KEYS[1]) == ARGV[1] then "
                "return redis.call('del', KEYS[1]) else return 0 end"
            )
            self.redis.eval(script, 1, name, owner)
