#!/usr/bin/env python3
"""Discover native GitHub Ansible repositories with auditable metadata."""

from __future__ import annotations

import argparse
import csv
from datetime import datetime, timedelta, timezone
import hashlib
import json
import os
from pathlib import Path
import time

import requests


API_ROOT = "https://api.github.com"
API_VERSION = "2022-11-28"
DEFAULT_CACHE = Path("study/cache/github")
DEFAULT_OUTPUT = Path("study/manifests/github-candidates.csv")
DEFAULT_QUERIES = (
    "topic:ansible archived:false fork:false stars:0..9",
    "topic:ansible archived:false fork:false stars:10..99",
    "topic:ansible archived:false fork:false stars:100..999",
    "topic:ansible archived:false fork:false stars:>=1000",
    "topic:ansible-role archived:false fork:false",
    "topic:ansible-collection archived:false fork:false",
)
FIELDS = (
    "source_host",
    "project",
    "source_url",
    "clone_url",
    "html_url",
    "description",
    "topics",
    "default_branch",
    "created_at",
    "updated_at",
    "pushed_at",
    "archived",
    "disabled",
    "fork",
    "mirror_url",
    "license_spdx",
    "stars",
    "star_band",
    "forks",
    "subscribers",
    "repository_size_kb",
    "open_issues",
    "total_prs",
    "merged_prs",
    "merged_prs_last_24_months",
    "open_prs",
    "discovery_query",
    "discovered_at_utc",
    "selection_as_of_utc",
    "preclone_eligible",
    "preclone_reasons",
    "collect_for_screening",
    "selected",
    "exclusion_reason",
    "manual_review_note",
)


def _headers(token=None):
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "ansibleguard-multi-ecosystem-study/1",
        "X-GitHub-Api-Version": API_VERSION,
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers


def _cache_path(cache_dir, namespace, params):
    identity = json.dumps(params, sort_keys=True, separators=(",", ":"))
    digest = hashlib.sha256(identity.encode("utf-8")).hexdigest()[:20]
    return Path(cache_dir) / f"{namespace}-{digest}.json"


def _request_json(
    url,
    *,
    params,
    cache_path,
    token=None,
    offline=False,
    refresh_cache=False,
    retries=5,
    timeout=45,
):
    cache_path = Path(cache_path)
    if cache_path.is_file() and (offline or not refresh_cache):
        return json.loads(cache_path.read_text(encoding="utf-8"))
    if offline:
        if not cache_path.is_file():
            raise FileNotFoundError(f"Offline GitHub cache does not exist: {cache_path}")

    delay = 2
    for attempt in range(retries):
        try:
            response = requests.get(
                url,
                params=params,
                headers=_headers(token),
                timeout=timeout,
            )
        except requests.RequestException:
            if attempt == retries - 1:
                raise
            time.sleep(delay)
            delay = min(delay * 2, 60)
            continue
        if response.status_code in {403, 429, 500, 502, 503, 504}:
            if attempt == retries - 1:
                response.raise_for_status()
            retry_after = response.headers.get("Retry-After")
            if retry_after:
                wait = int(retry_after)
            elif response.headers.get("X-RateLimit-Remaining") == "0":
                reset = int(response.headers.get("X-RateLimit-Reset", "0"))
                wait = max(1, reset - int(time.time()))
            else:
                wait = delay
            time.sleep(min(wait, 60))
            delay = min(delay * 2, 60)
            continue
        response.raise_for_status()
        payload = response.json()
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        cache_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        return payload
    raise RuntimeError(f"Could not retrieve {url}")


def _star_band(stars):
    if stars < 10:
        return "0-9"
    if stars < 100:
        return "10-99"
    if stars < 1000:
        return "100-999"
    return "1000+"


def _preclone_eligibility(item, as_of, activity_months=24):
    reasons = []
    if item.get("private"):
        reasons.append("not-public")
    if item.get("archived"):
        reasons.append("archived")
    if item.get("disabled"):
        reasons.append("disabled")
    if item.get("fork"):
        reasons.append("fork")
    if item.get("mirror_url"):
        reasons.append("mirror")
    license_data = item.get("license") or {}
    if not license_data.get("spdx_id") or license_data.get("spdx_id") == "NOASSERTION":
        reasons.append("license-needs-review")
    pushed_at = item.get("pushed_at")
    try:
        pushed = datetime.fromisoformat(str(pushed_at).replace("Z", "+00:00"))
    except ValueError:
        reasons.append("missing-push-date")
    else:
        if pushed < as_of - timedelta(days=activity_months * 30):
            reasons.append("stale")
    return not reasons, reasons


def repository_row(item, query, discovered_at, as_of):
    eligible, reasons = _preclone_eligibility(item, as_of)
    license_data = item.get("license") or {}
    stars = int(item.get("stargazers_count") or 0)
    full_name = str(item.get("full_name") or "")
    return {
        "source_host": "github",
        "project": full_name,
        "source_url": item.get("html_url") or f"https://github.com/{full_name}",
        "clone_url": item.get("clone_url") or f"https://github.com/{full_name}.git",
        "html_url": item.get("html_url") or "",
        "description": item.get("description") or "",
        "topics": ";".join(sorted(item.get("topics") or [])),
        "default_branch": item.get("default_branch") or "",
        "created_at": item.get("created_at") or "",
        "updated_at": item.get("updated_at") or "",
        "pushed_at": item.get("pushed_at") or "",
        "archived": str(bool(item.get("archived"))).lower(),
        "disabled": str(bool(item.get("disabled"))).lower(),
        "fork": str(bool(item.get("fork"))).lower(),
        "mirror_url": item.get("mirror_url") or "",
        "license_spdx": license_data.get("spdx_id") or "",
        "stars": stars,
        "star_band": _star_band(stars),
        "forks": int(item.get("forks_count") or 0),
        "subscribers": item.get("subscribers_count") or "",
        "repository_size_kb": int(item.get("size") or 0),
        "open_issues": int(item.get("open_issues_count") or 0),
        "total_prs": "",
        "merged_prs": "",
        "merged_prs_last_24_months": "",
        "open_prs": "",
        "discovery_query": query,
        "discovered_at_utc": discovered_at,
        "selection_as_of_utc": as_of.isoformat(),
        "preclone_eligible": str(eligible).lower(),
        "preclone_reasons": ";".join(reasons),
        "collect_for_screening": "false",
        "selected": "false",
        "exclusion_reason": ";".join(reasons),
        "manual_review_note": "",
    }


def discover(
    queries,
    *,
    cache_dir=DEFAULT_CACHE,
    token=None,
    offline=False,
    refresh_cache=False,
    pages=2,
    per_page=100,
    as_of=None,
):
    as_of = as_of or datetime.now(timezone.utc)
    discovered_at = datetime.now(timezone.utc).isoformat()
    by_project = {}
    reasons = {}
    for query in queries:
        for page in range(1, pages + 1):
            params = {
                "q": query,
                "sort": "updated",
                "order": "desc",
                "per_page": per_page,
                "page": page,
            }
            payload = _request_json(
                f"{API_ROOT}/search/repositories",
                params=params,
                cache_path=_cache_path(cache_dir, "repositories", params),
                token=token,
                offline=offline,
                refresh_cache=refresh_cache,
            )
            items = payload.get("items", [])
            for item in items:
                project = str(item.get("full_name") or "")
                if not project:
                    continue
                by_project[project] = item
                reasons.setdefault(project, set()).add(query)
            if len(items) < per_page:
                break
    rows = []
    for project, item in by_project.items():
        row = repository_row(item, ";".join(sorted(reasons[project])), discovered_at, as_of)
        rows.append(row)
    return sorted(rows, key=lambda row: (-int(row["stars"]), row["project"]))


def _search_count(
    project, qualifier, *, cache_dir, token, offline, refresh_cache=False
):
    query = f"repo:{project} is:pr {qualifier}".strip()
    params = {"q": query, "per_page": 1, "page": 1}
    payload = _request_json(
        f"{API_ROOT}/search/issues",
        params=params,
        cache_path=_cache_path(cache_dir, "pulls", params),
        token=token,
        offline=offline,
        refresh_cache=refresh_cache,
    )
    return int(payload.get("total_count") or 0)


def enrich_pull_request_counts(
    rows,
    *,
    cache_dir,
    token=None,
    offline=False,
    refresh_cache=False,
    limit=50,
    projects=None,
    as_of=None,
):
    as_of = as_of or datetime.now(timezone.utc)
    cutoff = (as_of - timedelta(days=730)).date().isoformat()
    if projects:
        requested = list(dict.fromkeys(projects))
        by_project = {row["project"]: row for row in rows}
        missing = [project for project in requested if project not in by_project]
        if missing:
            raise ValueError(
                "PR enrichment projects are absent from discovery: "
                + ", ".join(missing)
            )
        population = [by_project[project] for project in requested]
    else:
        population = rows
    for row in population[:limit]:
        project = row["project"]
        row["total_prs"] = _search_count(
            project,
            "",
            cache_dir=cache_dir,
            token=token,
            offline=offline,
            refresh_cache=refresh_cache,
        )
        row["merged_prs"] = _search_count(
            project,
            "is:merged",
            cache_dir=cache_dir,
            token=token,
            offline=offline,
            refresh_cache=refresh_cache,
        )
        row["merged_prs_last_24_months"] = _search_count(
            project,
            f"is:merged merged:>={cutoff}",
            cache_dir=cache_dir,
            token=token,
            offline=offline,
            refresh_cache=refresh_cache,
        )
        row["open_prs"] = _search_count(
            project,
            "is:open",
            cache_dir=cache_dir,
            token=token,
            offline=offline,
            refresh_cache=refresh_cache,
        )
    return rows


def write_manifest(rows, path=DEFAULT_OUTPUT):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=FIELDS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    return path


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Discover native GitHub repositories containing Ansible code."
    )
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--cache-dir", type=Path, default=DEFAULT_CACHE)
    parser.add_argument("--query", action="append", dest="queries")
    parser.add_argument("--pages", type=int, default=2)
    parser.add_argument("--per-page", type=int, default=100)
    parser.add_argument("--offline", action="store_true")
    parser.add_argument(
        "--refresh-cache",
        action="store_true",
        help="Ignore cached responses and retrieve current GitHub data",
    )
    parser.add_argument("--enrich-prs", action="store_true")
    parser.add_argument("--enrich-limit", type=int, default=50)
    parser.add_argument(
        "--enrich-project",
        action="append",
        dest="enrich_projects",
        help="Enrich only this discovered owner/repository (repeatable)",
    )
    parser.add_argument(
        "--as-of",
        help="UTC eligibility cutoff used for activity gates (ISO-8601)",
    )
    args = parser.parse_args(argv)
    as_of = (
        datetime.fromisoformat(args.as_of.replace("Z", "+00:00"))
        if args.as_of
        else datetime.now(timezone.utc)
    )
    token = os.environ.get("GITHUB_TOKEN")
    rows = discover(
        args.queries or DEFAULT_QUERIES,
        cache_dir=args.cache_dir,
        token=token,
        offline=args.offline,
        refresh_cache=args.refresh_cache,
        pages=args.pages,
        per_page=args.per_page,
        as_of=as_of,
    )
    if args.enrich_prs:
        rows = enrich_pull_request_counts(
            rows,
            cache_dir=args.cache_dir,
            token=token,
            offline=args.offline,
            refresh_cache=args.refresh_cache,
            limit=args.enrich_limit,
            projects=args.enrich_projects,
            as_of=as_of,
        )
    output = write_manifest(rows, args.output)
    eligible = sum(row["preclone_eligible"] == "true" for row in rows)
    print(f"Wrote {len(rows)} GitHub candidates ({eligible} pre-clone eligible) to {output}")
    print(
        "Set collect_for_screening=true to calculate post-clone gates; "
        "set selected=true only after they pass."
    )


if __name__ == "__main__":
    main()
