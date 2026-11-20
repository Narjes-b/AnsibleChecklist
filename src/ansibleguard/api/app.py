"""Optional FastAPI surface over AnalysisService."""

from __future__ import annotations

from .service import AnalysisRequest, AnalysisService
from ..sources.errors import SourceError
from .. import __version__


def create_app(service: AnalysisService):
    try:
        from fastapi import BackgroundTasks, FastAPI, HTTPException
    except ImportError as exc:
        raise RuntimeError("install ansibleguard[server] to use the web API") from exc

    app = FastAPI(title="AnsibleGuard API", version=__version__)

    def submit(provider, payload, background_tasks):
        try:
            request = AnalysisRequest(provider=provider, **payload)
            job_id = service.submit(request)
        except (SourceError, TypeError, ValueError) as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        background_tasks.add_task(service.execute, job_id)
        return {"id": job_id, "status": "queued"}

    @app.post("/api/v1/analysis/github")
    def github(payload: dict, background_tasks: BackgroundTasks):
        return submit("github", payload, background_tasks)

    @app.post("/api/v1/analysis/gitlab")
    def gitlab(payload: dict, background_tasks: BackgroundTasks):
        return submit("gitlab", payload, background_tasks)

    @app.post("/api/v1/analysis/pr")
    def pull_request(payload: dict, background_tasks: BackgroundTasks):
        return submit("github-pr", payload, background_tasks)

    @app.post("/api/v1/analysis/local")
    def local(payload: dict, background_tasks: BackgroundTasks):
        return submit("local", payload, background_tasks)

    @app.get("/api/v1/analysis/{job_id}")
    def status(job_id: str):
        try:
            return service.get(job_id)
        except SourceError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc

    @app.get("/api/v1/analysis/{job_id}/findings")
    def findings(job_id: str):
        try:
            return {"items": service.findings(job_id)}
        except SourceError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc

    return app
