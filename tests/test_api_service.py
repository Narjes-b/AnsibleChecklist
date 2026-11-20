import json

import pytest

from ansibleguard.api.jobs import RedisJobStore
from ansibleguard.api.service import AnalysisRequest, AnalysisService
from ansibleguard.sources.errors import SourceError


def test_local_api_job_uses_normal_analyzer_and_exposes_findings(tmp_path):
    repository = tmp_path / "repositories" / "role"
    repository.mkdir(parents=True)
    (repository / "site.yml").write_text("- hosts: all\n", encoding="utf-8")
    service = AnalysisService(
        tmp_path / "outputs",
        allow_local=True,
        local_roots=[tmp_path / "repositories"],
    )
    job_id = service.submit(
        AnalysisRequest(
            provider="local",
            repository=str(repository),
            profile="developer-fast",
        )
    )

    completed = service.execute(job_id)

    assert completed["status"] == "completed"
    assert isinstance(service.findings(job_id), list)
    metadata = json.loads(
        (tmp_path / "outputs" / job_id / "run_metadata.json").read_text()
    )
    assert metadata["source"]["provider"] == "local"


def test_server_local_source_is_disabled_and_confined_by_default(tmp_path):
    repository = tmp_path / "repository"
    repository.mkdir()
    service = AnalysisService(tmp_path / "outputs")
    job_id = service.submit(AnalysisRequest("local", str(repository)))
    with pytest.raises(SourceError, match="disabled"):
        service.execute(job_id)
    assert service.get(job_id)["status"] == "failed"

    confined = AnalysisService(
        tmp_path / "confined",
        allow_local=True,
        local_roots=[tmp_path / "allowed"],
    )
    job_id = confined.submit(AnalysisRequest("local", str(repository)))
    with pytest.raises(SourceError, match="outside"):
        confined.execute(job_id)


def test_analysis_request_rejects_unknown_provider(tmp_path):
    service = AnalysisService(tmp_path / "outputs")
    with pytest.raises(SourceError, match="unsupported"):
        service.submit(AnalysisRequest("unknown", "owner/repo"))
    with pytest.raises(SourceError, match="positive pull request"):
        service.submit(AnalysisRequest("github-pr", "owner/repo"))


class Redis:
    def __init__(self):
        self.values = {}

    def set(self, key, value, ex=None):
        self.values[key] = value

    def get(self, key):
        return self.values.get(key)


def test_redis_job_store_contains_state_not_analysis_artifacts():
    redis = Redis()
    store = RedisJobStore(redis)
    store.put("job", {"status": "queued", "output": "/blob/job"})
    assert store.get("job") == {"status": "queued", "output": "/blob/job"}
    assert "findings" not in next(iter(redis.values.values()))
