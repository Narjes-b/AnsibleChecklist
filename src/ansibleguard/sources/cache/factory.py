"""CLI/server cache construction without mandatory Redis dependencies."""

from __future__ import annotations

import os

from ..errors import SourceError
from .filesystem import FileSystemCache
from .redis import RedisCache


def create_cache_backend(*, backend="filesystem", cache_dir=None, redis_url=None):
    blobs = FileSystemCache(cache_dir)
    if backend == "filesystem":
        return blobs
    if backend != "redis":
        raise SourceError("cache backend must be filesystem or redis")
    url = redis_url or os.environ.get("ANSIBLEGUARD_REDIS_URL")
    if not url:
        raise SourceError("Redis cache requires ANSIBLEGUARD_REDIS_URL")
    try:
        import redis
    except ImportError as exc:
        raise SourceError("install ansibleguard[cache] to use Redis") from exc
    return RedisCache(redis.Redis.from_url(url), blobs)
