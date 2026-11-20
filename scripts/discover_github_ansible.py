#!/usr/bin/env python3
"""Discover native GitHub Ansible repositories with auditable metadata."""

from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import csv
import math
from datetime import datetime, timedelta, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import time

import requests


API_ROOT = "https://api.github.com"
API_VERSION = "2022-11-28"
DEFAULT_CACHE = Path("study/cache/github")
DEFAULT_OUTPUT = Path("study/manifests/github-candidates.csv")
DEFAULT_QUERIES = (
    # Discovery is intentionally inclusive. Fork/archive/mirror/recency gates
    # are applied later so their attrition remains measurable. Every query
    # below widens *candidate diversity*, not quality: none loosens or
    # tightens any downstream threshold.

    # --- Original topic/text queries -----------------------------------
    "topic:ansible fork:true",
    "topic:ansible-role fork:true",
    "topic:ansible-collection fork:true",
    "ansible in:name,description,topics fork:true",

    # --- Ecosystem queries: adjacent topics that co-occur with real
    # Ansible usage but aren't captured by the "ansible" topic alone
    # (e.g. an IaC repo tagged "configuration-management" that only
    # mentions Ansible in its description). -----------------------------
    "ansible topic:infrastructure-as-code fork:true",
    "ansible topic:configuration-management fork:true",
    "ansible topic:devops fork:true",
    "ansible topic:automation fork:true",
    "ansible topic:iac fork:true",
    "ansible topic:provisioning fork:true",

    # --- Ansible collection queries: galaxy.yml-based collections often
    # carry namespace-style names (namespace.collection) or a
    # "galaxy"/"ansible-galaxy" topic rather than "ansible-collection". --
    "topic:ansible-galaxy fork:true",
    "ansible-collection in:name fork:true",

    # --- Organization queries: known high-volume Ansible-content
    # organizations whose repositories may not carry the "ansible" topic
    # at all (many predate GitHub topics or rely on org membership as
    # their only Ansible signal). -----------------------------------------
    "org:ansible-collections fork:true",
    "org:geerlingguy ansible fork:true",
    "org:redhat-cop ansible fork:true",
    "org:debops fork:true",
    "org:oasis-roles fork:true",

    # --- Infrastructure/automation repositories: broader repos that use
    # Ansible as one part of a larger infrastructure-automation stack,
    # which "topic:ansible" alone tends to miss since Ansible may be a
    # secondary rather than primary topic tag. ---------------------------
    "ansible-playbook in:name,description fork:true",
    "ansible-role in:name fork:true",
    "\"infrastructure as code\" ansible fork:true",
)
FIELDS = (
    "selection_protocol_version",
    "source_host",
    "repository_id",
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
    "private",
    "archived",
    "disabled",
    "fork",
    "mirror_url",
    "is_template",
    "generated_repository_match",
    "license_spdx",
    "stars",
    "star_band",
    "stars_used_for_selection",
    "forks",
    "subscribers",
    "repository_size_kb",
    "open_issues",
    "total_prs",
    "total_commits",
    "total_commits_source",
    "commit_count_status",
    "merged_prs",
    "merged_prs_last_24_months",
    "open_prs",
    "merged_ansible_changing_prs",
    "ansible_pr_scan_status",
    "pass_public",
    "pass_not_disabled",
    "pass_not_fork",
    "pass_not_archived",
    "pass_not_mirror",
    "pass_not_template",
    "pass_not_generated",
    "pass_last_commit_within_6_years",
    "pass_total_prs_gt_50",
    "pass_commits_ge_1000",
    "pass_merged_ansible_prs_ge_50",
    "metadata_eligible",
    "metadata_exclusion_reasons",
    "discovery_sources",
    "discovery_methods",
    "discovery_coverage_scope",
    "discovery_coverage_warning",
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


def _token_pool(token, tokens):
    """Normalize token/tokens into a non-empty list, tokens taking precedence."""
    if tokens:
        pool = [item for item in tokens if item]
        if pool:
            return pool
    return [token]


def _rate_limit_backoff(response, delay):
    """Decide how long to wait before retrying a 403/429 GitHub response.

    Returns (wait_seconds, reason) for a genuine rate-limit condition, or
    None if the response is some other 403/429 that should just raise.
    GitHub's "secondary" (abuse-detection) limit is not represented by
    X-RateLimit-* headers or /rate_limit and can trigger from request
    concurrency/burstiness even while primary quota is nonzero -- shared by
    every caller here rather than duplicated, since both the search/repo
    JSON path and the raw commit-count path can hit either kind.
    """
    retry_after = response.headers.get("Retry-After")
    remaining = response.headers.get("X-RateLimit-Remaining")
    try:
        message = str(response.json().get("message", "")).lower()
    except (ValueError, AttributeError):
        message = response.text.lower()
    secondary = (
        response.status_code == 429
        or retry_after is not None
        or "secondary rate limit" in message
        or "abuse detection" in message
    )
    primary = remaining == "0"
    if not primary and not secondary:
        return None
    if retry_after:
        try:
            wait = max(1, int(retry_after))
        except ValueError:
            wait = 60
        return wait, "GitHub Retry-After"
    if primary:
        reset = int(response.headers.get("X-RateLimit-Reset", "0"))
        wait = max(1, reset - int(time.time()) + 1)
        return wait, "GitHub primary rate limit"
    # Secondary limits can persist while the core quota is still nonzero.
    # Back off much more slowly than an ordinary transient server failure.
    return min(max(60, delay), 300), "GitHub secondary rate limit"


def _request_json(
    url,
    *,
    params,
    cache_path,
    token=None,
    tokens=None,
    start_index=0,
    offline=False,
    refresh_cache=False,
    retries=20,
    timeout=45,
):
    cache_path = Path(cache_path)
    if cache_path.is_file() and (offline or not refresh_cache):
        return json.loads(cache_path.read_text(encoding="utf-8"))
    if offline:
        if not cache_path.is_file():
            raise FileNotFoundError(f"Offline GitHub cache does not exist: {cache_path}")

    pool = _token_pool(token, tokens)
    delay = 2
    consecutive_limited = 0
    for attempt in range(retries):
        chosen_token = pool[(start_index + attempt) % len(pool)]
        try:
            response = requests.get(
                url,
                params=params,
                headers=_headers(chosen_token),
                timeout=timeout,
            )
        except requests.RequestException:
            if attempt == retries - 1:
                raise
            time.sleep(delay)
            delay = min(delay * 2, 60)
            continue
        if response.status_code in {403, 429}:
            backoff = _rate_limit_backoff(response, delay)
            if backoff is None:
                response.raise_for_status()
            consecutive_limited += 1
            if consecutive_limited < len(pool):
                # Another token in the pool may still have quota -- try it
                # on the very next attempt instead of sleeping. A rate limit
                # is a property of the token, not of the request.
                continue
            if attempt == retries - 1:
                response.raise_for_status()
            wait, reason = backoff
            print(
                f"{reason}; waiting {wait}s before retrying {url} "
                f"(all {len(pool)} token(s) limited)"
            )
            time.sleep(wait)
            delay = min(delay * 2, 300)
            consecutive_limited = 0
            continue
        consecutive_limited = 0
        if response.status_code in {500, 502, 503, 504}:
            if attempt == retries - 1:
                response.raise_for_status()
            print(
                f"GitHub returned HTTP {response.status_code}; "
                f"waiting {delay}s before retrying {url}"
            )
            time.sleep(delay)
            delay = min(delay * 2, 60)
            continue
        response.raise_for_status()
        payload = response.json()
        if isinstance(payload, dict) and payload.get("incomplete_results"):
            # GitHub search timed out server-side and returned a partial
            # result set with HTTP 200 -- not an error status, so it would
            # otherwise sail past every check above and get cached as if it
            # were the true, complete answer. A caller that later raises on
            # incomplete_results would then keep replaying this same
            # incomplete response from cache forever, never actually
            # retrying against GitHub. Treat it as transient instead.
            if attempt == retries - 1:
                raise RuntimeError(
                    f"GitHub returned incomplete_results for {url} after "
                    f"{retries} attempts (params={params})"
                )
            print(f"GitHub returned incomplete_results; waiting {delay}s before retrying {url}")
            time.sleep(delay)
            delay = min(delay * 2, 60)
            continue
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


def _bool(value):
    return "true" if value else "false"


GENERATED_REPOSITORY_PATTERN = re.compile(
    r"[-_]generated\b|[-_]auto[-_]|[-_]bot[-_]|\btemplate[-_]repo\b|\bcookiecutter\b",
    re.IGNORECASE,
)


def _looks_generated(item):
    """Heuristic match for scaffold/bot-authored repositories.

    GitHub has no API flag for "generated" the way it does for
    is_template, so this is a name/description regex rather than a
    metadata field -- it deliberately only matches repositories that
    advertise their own generated/templated nature (e.g. a name ending
    in "-generated" or a cookiecutter-produced repo), not repositories
    that merely use code generation internally.
    """
    haystack = (
        f"{item.get('name') or ''} {item.get('full_name') or ''} "
        f"{item.get('description') or ''}"
    )
    return bool(GENERATED_REPOSITORY_PATTERN.search(haystack))


def _preclone_eligibility(item, as_of, recency_years=6):
    """Return the supervisor-approved metadata gates and all failure reasons."""
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
    if item.get("is_template"):
        reasons.append("template")
    if _looks_generated(item):
        reasons.append("generated")
    pushed_at = item.get("pushed_at")
    try:
        pushed = datetime.fromisoformat(str(pushed_at).replace("Z", "+00:00"))
    except ValueError:
        reasons.append("missing-push-date")
    else:
        if pushed < as_of - timedelta(days=recency_years * 365):
            reasons.append("last-commit-older-than-6-years")
    return not reasons, reasons


def repository_row(item, query, discovered_at, as_of):
    eligible, reasons = _preclone_eligibility(item, as_of)
    license_data = item.get("license") or {}
    stars = int(item.get("stargazers_count") or 0)
    full_name = str(item.get("full_name") or "")
    methods = []
    if "topic:" in query:
        methods.append("github-topic-search")
    if "in:name,description,topics" in query:
        methods.append("github-metadata-text-search")
    return {
        "selection_protocol_version": "2",
        "source_host": "github",
        "repository_id": item.get("id") or "",
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
        "private": _bool(bool(item.get("private"))),
        "archived": str(bool(item.get("archived"))).lower(),
        "disabled": str(bool(item.get("disabled"))).lower(),
        "fork": str(bool(item.get("fork"))).lower(),
        "mirror_url": item.get("mirror_url") or "",
        "is_template": str(bool(item.get("is_template"))).lower(),
        "generated_repository_match": str(_looks_generated(item)).lower(),
        "license_spdx": license_data.get("spdx_id") or "",
        "stars": stars,
        "star_band": _star_band(stars),
        "stars_used_for_selection": "false",
        "forks": int(item.get("forks_count") or 0),
        "subscribers": item.get("subscribers_count") or "",
        "repository_size_kb": int(item.get("size") or 0),
        "open_issues": int(item.get("open_issues_count") or 0),
        "total_prs": "",
        "total_commits": "",
        "total_commits_source": "",
        "commit_count_status": "not-evaluated",
        "merged_prs": "",
        "merged_prs_last_24_months": "",
        "open_prs": "",
        "merged_ansible_changing_prs": "",
        "ansible_pr_scan_status": "not-evaluated",
        "pass_public": _bool(not item.get("private")),
        "pass_not_disabled": _bool(not item.get("disabled")),
        "pass_not_fork": _bool(not item.get("fork")),
        "pass_not_archived": _bool(not item.get("archived")),
        "pass_not_mirror": _bool(not item.get("mirror_url")),
        "pass_not_template": _bool(not item.get("is_template")),
        "pass_not_generated": _bool(not _looks_generated(item)),
        "pass_last_commit_within_6_years": _bool(
            "last-commit-older-than-6-years" not in reasons
            and "missing-push-date" not in reasons
        ),
        "pass_total_prs_gt_50": "not-evaluated",
        "pass_commits_ge_1000": "not-evaluated",
        "pass_merged_ansible_prs_ge_50": "not-evaluated",
        "metadata_eligible": _bool(eligible),
        "metadata_exclusion_reasons": ";".join(reasons),
        "discovery_sources": "github",
        "discovery_methods": ";".join(methods),
        "discovery_coverage_scope": "union-of-configured-github-searches",
        "discovery_coverage_warning": (
            "not-all-ansible-repositories;repositories-without-matching-topics-or-metadata-may-be-missed"
        ),
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
    pages=None,
    per_page=100,
    as_of=None,
):
    as_of = as_of or datetime.now(timezone.utc)
    discovered_at = datetime.now(timezone.utc).isoformat()
    by_project = {}
    reasons = {}
    for query in queries:
        if pages is None:
            query_items = _discover_complete_query(
                query,
                cache_dir=cache_dir,
                token=token,
                offline=offline,
                refresh_cache=refresh_cache,
                per_page=per_page,
                start=datetime(2008, 1, 1, tzinfo=timezone.utc),
                end=as_of,
            )
        else:
            query_items = []
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
                query_items.extend(items)
                if len(items) < per_page:
                    break
        for item in query_items:
            project = str(item.get("full_name") or "")
            if not project:
                continue
            by_project[project] = item
            reasons.setdefault(project, set()).add(query)
    rows = []
    for project, item in by_project.items():
        row = repository_row(item, ";".join(sorted(reasons[project])), discovered_at, as_of)
        rows.append(row)
    return sorted(rows, key=lambda row: row["project"].lower())


def _discover_complete_query(
    query,
    *,
    cache_dir,
    token,
    offline,
    refresh_cache,
    per_page,
    start,
    end,
):
    """Recursively partition by creation time so no search slice exceeds 1,000."""
    created = f"created:{start.isoformat()}..{end.isoformat()}"
    partition_query = f"{query} {created}"
    first_params = {
        "q": partition_query,
        "sort": "updated",
        "order": "desc",
        "per_page": per_page,
        "page": 1,
    }
    first = _request_json(
        f"{API_ROOT}/search/repositories",
        params=first_params,
        cache_path=_cache_path(cache_dir, "repositories", first_params),
        token=token,
        offline=offline,
        refresh_cache=refresh_cache,
    )
    if first.get("incomplete_results"):
        raise RuntimeError(f"GitHub returned incomplete results for {partition_query}")
    total = int(first.get("total_count", len(first.get("items", []))))
    if total > 1000:
        span = end - start
        if span.total_seconds() <= 1:
            raise RuntimeError(
                "A one-second GitHub creation partition exceeds 1,000 results: "
                + partition_query
            )
        midpoint = start + span / 2
        return [
            *_discover_complete_query(
                query, cache_dir=cache_dir, token=token, offline=offline,
                refresh_cache=refresh_cache, per_page=per_page,
                start=start, end=midpoint,
            ),
            *_discover_complete_query(
                query, cache_dir=cache_dir, token=token, offline=offline,
                refresh_cache=refresh_cache, per_page=per_page,
                start=midpoint, end=end,
            ),
        ]
    items = list(first.get("items", []))
    pages = math.ceil(total / per_page) if total else 0
    for page in range(2, pages + 1):
        params = {**first_params, "page": page}
        payload = _request_json(
            f"{API_ROOT}/search/repositories",
            params=params,
            cache_path=_cache_path(cache_dir, "repositories", params),
            token=token,
            offline=offline,
            refresh_cache=refresh_cache,
        )
        if payload.get("incomplete_results"):
            raise RuntimeError(f"GitHub returned incomplete results for {partition_query}")
        items.extend(payload.get("items", []))
    return items


def _search_count(
    project, qualifier, *, cache_dir, token=None, tokens=None, start_index=0,
    offline, refresh_cache=False
):
    """Return the PR count for project, or None if it cannot be searched.

    GitHub returns HTTP 422 for `repo:owner/name` search qualifiers when the
    repository was renamed, transferred, or deleted between discovery and
    enrichment time (confirmed in practice: the repo API 301-redirects to a
    new owner/name, but search has no such fallback). This is not transient
    -- retrying the same stale name will never succeed -- so it is reported
    to the caller rather than raised, keeping one renamed repository from
    aborting enrichment for the rest of the population.
    """
    query = f"repo:{project} is:pr {qualifier}".strip()
    params = {"q": query, "per_page": 1, "page": 1}
    try:
        payload = _request_json(
            f"{API_ROOT}/search/issues",
            params=params,
            cache_path=_cache_path(cache_dir, "pulls", params),
            token=token,
            tokens=tokens,
            start_index=start_index,
            offline=offline,
            refresh_cache=refresh_cache,
        )
    except requests.HTTPError as exc:
        if exc.response is not None and exc.response.status_code == 422:
            return None
        raise
    return int(payload.get("total_count") or 0)


def _commit_count(
    project, branch, *, cache_dir, token=None, tokens=None, start_index=0,
    offline, refresh_cache=False, retries=20, timeout=45,
):
    """Count commits reachable from the default branch using one paginated request."""
    params = {"sha": branch, "per_page": 1, "page": 1}
    cache_path = _cache_path(
        cache_dir, "commit-count", {"project": project, **params}
    )
    if cache_path.is_file() and (offline or not refresh_cache):
        cached = json.loads(cache_path.read_text(encoding="utf-8"))
        if cached.get("status") == "unavailable-http-404":
            return None
        return int(cached["count"])
    if offline:
        raise FileNotFoundError(f"Offline GitHub cache does not exist: {cache_path}")
    url = f"{API_ROOT}/repos/{project}/commits"
    pool = _token_pool(token, tokens)
    delay = 2
    consecutive_limited = 0
    for attempt in range(retries):
        chosen_token = pool[(start_index + attempt) % len(pool)]
        try:
            response = requests.get(
                url, params=params, headers=_headers(chosen_token), timeout=timeout
            )
        except requests.RequestException:
            if attempt == retries - 1:
                raise
            time.sleep(delay)
            delay = min(delay * 2, 60)
            continue
        if response.status_code == 409:  # empty repository
            count = 0
            break
        if response.status_code == 404:
            # Repositories can be deleted, made private, or lose/change their
            # recorded default branch between discovery and enrichment. Keep
            # the candidate in the ledger, cache the outcome, and continue.
            cache_path.parent.mkdir(parents=True, exist_ok=True)
            cache_path.write_text(
                json.dumps(
                    {
                        "count": None,
                        "project": project,
                        "branch": branch,
                        "status": "unavailable-http-404",
                    },
                    indent=2,
                ),
                encoding="utf-8",
            )
            return None
        if response.status_code in {403, 429}:
            backoff = _rate_limit_backoff(response, delay)
            if backoff is None:
                response.raise_for_status()
            consecutive_limited += 1
            if consecutive_limited < len(pool):
                # Another token in the pool may still have quota -- try it
                # on the very next attempt instead of sleeping.
                continue
            if attempt == retries - 1:
                response.raise_for_status()
            wait, reason = backoff
            print(
                f"{reason}; waiting {wait}s before retrying {url} "
                f"(all {len(pool)} token(s) limited)"
            )
            time.sleep(wait)
            delay = min(delay * 2, 300)
            consecutive_limited = 0
            continue
        consecutive_limited = 0
        if response.status_code in {500, 502, 503, 504}:
            if attempt == retries - 1:
                response.raise_for_status()
            print(
                f"GitHub returned HTTP {response.status_code}; "
                f"waiting {delay}s before retrying {url}"
            )
            time.sleep(delay)
            delay = min(delay * 2, 60)
            continue
        response.raise_for_status()
        payload = response.json()
        last = re.search(r"[?&]page=(\d+)[^>]*>; rel=\"last\"", response.headers.get("Link", ""))
        count = int(last.group(1)) if last else len(payload)
        break
    else:
        raise RuntimeError(f"Could not count commits for {project}")
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    cache_path.write_text(
        json.dumps({"count": count, "project": project, "branch": branch}, indent=2),
        encoding="utf-8",
    )
    return count


def enrich_commit_counts(
    rows, *, cache_dir, token=None, tokens=None, offline=False, refresh_cache=False,
    limit=None, projects=None, jobs=1,
):
    by_project = {row["project"]: row for row in rows}
    if projects:
        missing = [project for project in projects if project not in by_project]
        if missing:
            raise ValueError("Commit-count projects are absent: " + ", ".join(missing))
        population = [by_project[project] for project in dict.fromkeys(projects)]
    else:
        population = [row for row in rows if row.get("metadata_eligible") == "true"]
    if limit is not None:
        population = population[:limit]

    pool = _token_pool(token, tokens)

    def _fetch(index, row):
        return row, _commit_count(
            row["project"], row.get("default_branch") or "HEAD",
            cache_dir=cache_dir, tokens=pool, start_index=index, offline=offline,
            refresh_cache=refresh_cache,
        )

    # Each row starts on one token round-robin by index, so normal traffic
    # spreads evenly across the pool with no shared mutable cursor between
    # concurrent workers. But a *retry* (rate limit, transient error) walks
    # forward through the same pool from that starting point -- so if the
    # token this row started on happens to be the one that's currently
    # exhausted, the row fails over to another token immediately instead of
    # this worker sitting idle for up to an hour waiting on that one token's
    # reset while the rest of the pool has spare quota.
    completed = 0
    with ThreadPoolExecutor(max_workers=max(1, jobs)) as executor:
        futures = [executor.submit(_fetch, index, row) for index, row in enumerate(population)]
        for future in as_completed(futures):
            row, count = future.result()
            completed += 1
            print(f"[{completed}/{len(population)}] counting commits for {row['project']}")
            if count is None:
                row["total_commits"] = ""
                row["total_commits_source"] = "github-default-branch-rest"
                row["commit_count_status"] = "unavailable-http-404"
                row["pass_commits_ge_1000"] = "false"
                continue
            row["total_commits"] = count
            row["total_commits_source"] = "github-default-branch-rest"
            row["commit_count_status"] = "completed"
            row["pass_commits_ge_1000"] = _bool(count >= 1000)
    return rows


def enrich_pull_request_counts(
    rows,
    *,
    cache_dir,
    token=None,
    tokens=None,
    offline=False,
    refresh_cache=False,
    limit=None,
    projects=None,
    as_of=None,
    include_descriptive=False,
    jobs=1,
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
        population = [
            row for row in rows if row.get("pass_commits_ge_1000") == "true"
        ]
    population = population if limit is None else population[:limit]

    pool = _token_pool(token, tokens)

    def _fetch(index, row):
        project = row["project"]
        total_prs = _search_count(
            project, "", cache_dir=cache_dir, tokens=pool, start_index=index,
            offline=offline, refresh_cache=refresh_cache,
        )
        descriptive = {}
        if total_prs is not None and include_descriptive:
            descriptive["merged_prs"] = _search_count(
                project, "is:merged", cache_dir=cache_dir, tokens=pool,
                start_index=index, offline=offline, refresh_cache=refresh_cache,
            ) or 0
            descriptive["merged_prs_last_24_months"] = _search_count(
                project, f"is:merged merged:>={cutoff}", cache_dir=cache_dir,
                tokens=pool, start_index=index, offline=offline,
                refresh_cache=refresh_cache,
            ) or 0
            descriptive["open_prs"] = _search_count(
                project, "is:open", cache_dir=cache_dir, tokens=pool,
                start_index=index, offline=offline, refresh_cache=refresh_cache,
            ) or 0
        return row, total_prs, descriptive

    with ThreadPoolExecutor(max_workers=max(1, jobs)) as executor:
        futures = [executor.submit(_fetch, index, row) for index, row in enumerate(population)]
        for future in as_completed(futures):
            row, total_prs, descriptive = future.result()
            project = row["project"]
            if total_prs is None:
                row["total_prs"] = ""
                row["pass_total_prs_gt_50"] = "not-evaluated"
                row["total_prs_scan_status"] = "unsearchable-repository-renamed-or-removed"
                print(f"  cannot search PRs for {project} (renamed/transferred/removed); skipping")
                continue
            row["total_prs"] = total_prs
            row.update(descriptive)
            row["pass_total_prs_gt_50"] = _bool(int(row["total_prs"]) > 50)
    return rows


def write_manifest(rows, path=DEFAULT_OUTPUT):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = list(FIELDS)
    fields.extend(
        key for row in rows for key in row
        if key not in fields
    )
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    return path


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Discover native GitHub repositories containing Ansible code."
    )
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument(
        "--input", type=Path,
        help="enrich an existing merged/hydrated candidate CSV instead of rediscovering",
    )
    parser.add_argument("--cache-dir", type=Path, default=DEFAULT_CACHE)
    parser.add_argument("--query", action="append", dest="queries")
    parser.add_argument(
        "--pages",
        type=int,
        help="bounded diagnostic mode; omit for complete creation-time partitioning",
    )
    parser.add_argument("--per-page", type=int, default=100)
    parser.add_argument("--offline", action="store_true")
    parser.add_argument(
        "--refresh-cache",
        action="store_true",
        help="Ignore cached responses and retrieve current GitHub data",
    )
    parser.add_argument("--enrich-prs", action="store_true")
    parser.add_argument("--enrich-commits", action="store_true")
    parser.add_argument(
        "--enrich-pr-details", action="store_true",
        help="also collect descriptive merged/recent/open PR counts",
    )
    parser.add_argument("--enrich-limit", type=int, default=None)
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
    parser.add_argument(
        "--jobs", type=int, default=1,
        help="Concurrent enrichment requests. GitHub's rate limit is "
             "per-token, so this only helps throughput when combined with "
             "multiple GITHUB_TOKENS; with a single token it just closes "
             "the gap between observed and rate-limit-ceiling throughput.",
    )
    args = parser.parse_args(argv)
    as_of = (
        datetime.fromisoformat(args.as_of.replace("Z", "+00:00"))
        if args.as_of
        else datetime.now(timezone.utc)
    )
    token = os.environ.get("GITHUB_TOKEN")
    tokens_env = os.environ.get("GITHUB_TOKENS")
    tokens = [item.strip() for item in tokens_env.split(",") if item.strip()] if tokens_env else None
    if args.input:
        with args.input.open(newline="", encoding="utf-8") as stream:
            rows = list(csv.DictReader(stream))
    else:
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
    if args.enrich_commits:
        rows = enrich_commit_counts(
            rows, cache_dir=args.cache_dir, token=token, tokens=tokens,
            offline=args.offline, refresh_cache=args.refresh_cache,
            limit=args.enrich_limit, projects=args.enrich_projects,
            jobs=args.jobs,
        )
    if args.enrich_prs:
        rows = enrich_pull_request_counts(
            rows,
            cache_dir=args.cache_dir,
            token=token,
            tokens=tokens,
            offline=args.offline,
            refresh_cache=args.refresh_cache,
            limit=args.enrich_limit,
            projects=args.enrich_projects,
            as_of=as_of,
            include_descriptive=args.enrich_pr_details,
            jobs=args.jobs,
        )
    output = write_manifest(rows, args.output)
    eligible = sum(row.get("preclone_eligible") == "true" for row in rows)
    print(f"Wrote {len(rows)} GitHub candidates ({eligible} pre-clone eligible) to {output}")
    print(
        "Set collect_for_screening=true to calculate post-clone gates; "
        "set selected=true only after they pass."
    )


if __name__ == "__main__":
    main()
