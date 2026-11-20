"""Job state backends; analysis artifacts remain on disk/object storage."""

from __future__ import annotations

from copy import deepcopy
import json
from threading import Lock


class InMemoryJobStore:
    def __init__(self):
        self._jobs = {}
        self._lock = Lock()

    def put(self, job_id: str, payload: dict) -> None:
        with self._lock:
            self._jobs[job_id] = deepcopy(payload)

    def get(self, job_id: str) -> dict | None:
        with self._lock:
            value = self._jobs.get(job_id)
            return deepcopy(value) if value is not None else None


class RedisJobStore:
    def __init__(self, redis_client, *, prefix="ansibleguard:job", ttl=86400):
        self.redis = redis_client
        self.prefix = prefix
        self.ttl = int(ttl)

    def _key(self, job_id):
        return f"{self.prefix}:{job_id}"

    def put(self, job_id, payload):
        self.redis.set(self._key(job_id), json.dumps(payload), ex=self.ttl)

    def get(self, job_id):
        value = self.redis.get(self._key(job_id))
        if value is None:
            return None
        if isinstance(value, bytes):
            value = value.decode("utf-8")
        return json.loads(value)
