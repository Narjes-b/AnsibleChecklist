#!/usr/bin/env python3
"""Count merged PRs that change production Ansible paths, with cached evidence."""

from __future__ import annotations

import argparse
import csv
from datetime import datetime, timezone
import json
import os
from pathlib import Path, PurePosixPath
import subprocess
import time

import requests
import yaml

from ansibleguard.document import AnsibleSafeLoader, _classify

try:
    from scripts.discover_github_ansible import (
        API_ROOT,
        _cache_path,
        _headers,
        _request_json,
    )
except ModuleNotFoundError:  # direct ``python scripts/enrich_ansible_prs.py``
    from discover_github_ansible import API_ROOT, _cache_path, _headers, _request_json


EXCLUDED_PARTS = {
    ".github", ".gitlab", "molecule", "test", "tests", "docs", "examples",
    "example", "ci", "zuul", "changelogs", "releasenotes",
}
ANSIBLE_PARTS = {
    "playbooks", "roles", "tasks", "handlers", "defaults", "vars",
    "group_vars", "host_vars", "inventory", "inventories",
}
METADATA_NAMES = {"galaxy.yml", "galaxy.yaml", "requirements.yml", "requirements.yaml"}
PR_FIELDS = (
    "project", "pr_number", "pr_url", "base_sha", "head_sha", "merge_sha", "merged_at",
    "changed_files", "change_statuses", "renamed_or_previous_paths",
    "ansible_changed_files", "ansible_change_evidence", "qualification_basis",
    "paper_comparable_changed_files", "primary_qualifies",
    "paper_comparable_qualifies", "qualifies", "evidence_source",
    "file_list_complete",
)
PROJECT_EVIDENCE_SCHEMA = 3
PROJECT_PROGRESS_SCHEMA = 4
GRAPHQL_QUERY_VERSION = 1
GRAPHQL_ROOT = "https://api.github.com/graphql"
DEFAULT_THRESHOLD = 50
DEFAULT_PR_PAGE_SIZE = 20
DEFAULT_FILE_PAGE_SIZE = 100
GRAPHQL_PULL_REQUEST_PAGE = """
query AnsibleChangingPullRequests(
  $owner: String!
  $name: String!
  $cursor: String
  $prPageSize: Int!
  $filePageSize: Int!
) {
  repository(owner: $owner, name: $name) {
    pullRequests(
      first: $prPageSize
      after: $cursor
      states: [MERGED]
      orderBy: {field: CREATED_AT, direction: DESC}
    ) {
      totalCount
      pageInfo {
        endCursor
        hasNextPage
      }
      edges {
        cursor
        node {
          number
          url
          mergedAt
          baseRefOid
          headRefOid
          mergeCommit { oid }
          files(first: $filePageSize) {
            totalCount
            pageInfo {
              endCursor
              hasNextPage
            }
            nodes {
              path
              changeType
            }
          }
        }
      }
    }
  }
  rateLimit {
    cost
    remaining
    resetAt
  }
}
"""


def is_production_ansible_path(filename, known_paths=()):
    path = PurePosixPath(str(filename).replace("\\", "/"))
    spelling = path.as_posix().lstrip("./")
    if spelling in set(known_paths):
        return True
    parts = {part.lower() for part in path.parts}
    if parts & EXCLUDED_PARTS:
        return False
    if path.name.lower() in METADATA_NAMES:
        return True
    if path.suffix.lower() not in {".yml", ".yaml"}:
        return False
    return bool(parts & ANSIBLE_PARTS)


def _excluded_path(filename):
    return bool({part.lower() for part in PurePosixPath(filename).parts} & EXCLUDED_PARTS)


def _paper_path(filename):
    parts = {part.lower() for part in PurePosixPath(filename).parts}
    return bool(parts & {"playbooks", "tasks", "roles"}) and not bool(
        parts & {"vars", "defaults", "group_vars", "host_vars", "inventory", "inventories"}
    )


def _parse_utc_datetime(value):
    parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _content_confirms_ansible(repository, revisions, filename):
    repository = Path(repository) if repository else None
    if repository is None or not (repository / ".git").is_dir():
        return False
    for revision in revisions:
        if not revision:
            continue
        result = subprocess.run(
            ["git", "show", f"{revision}:{filename}"],
            cwd=repository,
            capture_output=True,
        )
        if result.returncode:
            continue
        try:
            document = yaml.load(result.stdout.decode("utf-8"), Loader=AnsibleSafeLoader)
        except (UnicodeDecodeError, yaml.YAMLError):
            continue
        if _classify(Path(filename), document) in {"playbook", "tasks"}:
            return True
    return False


def _paged(url, params, *, cache_dir, token, offline, refresh_cache):
    page = 1
    while True:
        page_params = {**params, "per_page": 100, "page": page}
        payload = _request_json(
            url,
            params=page_params,
            cache_path=_cache_path(cache_dir, "ansible-prs", {"url": url, **page_params}),
            token=token,
            offline=offline,
            refresh_cache=refresh_cache,
        )
        if not isinstance(payload, list):
            raise ValueError(f"expected a list from {url}")
        yield from payload
        if len(payload) < 100:
            break
        page += 1


def _atomic_write_json(path, payload, retries=5):
    """Write payload to path atomically, tolerating transient Windows locks.

    Path.replace() (os.replace) can fail with WinError 5 "Access is denied"
    when the target is briefly held open by another process -- antivirus
    scanning, search indexing, a concurrent reader -- even though nothing in
    this codebase holds a lasting lock on it. Confirmed in practice during a
    large checkpoint-heavy run: a single such failure previously aborted the
    entire enrichment pass over one transient, self-clearing condition.
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    delay = 0.2
    for attempt in range(retries):
        try:
            temporary.replace(path)
            return
        except PermissionError:
            if attempt == retries - 1:
                raise
            time.sleep(delay)
            delay = min(delay * 2, 5)


def _wait_in_chunks(seconds, reason):
    remaining = max(1, int(seconds))
    while remaining:
        wait = min(remaining, 60)
        print(f"{reason}; waiting {remaining}s before retrying GraphQL")
        time.sleep(wait)
        remaining -= wait


def _graphql_cache_path(cache_dir, variables):
    return _cache_path(
        cache_dir,
        "ansible-pr-graphql",
        {
            "query_version": GRAPHQL_QUERY_VERSION,
            **variables,
        },
    )


def _graphql_request(
    variables,
    *,
    cache_dir,
    token=None,
    offline=False,
    refresh_cache=False,
    retries=20,
    timeout=90,
):
    cache_path = _graphql_cache_path(cache_dir, variables)
    if cache_path.is_file() and (offline or not refresh_cache):
        payload = json.loads(cache_path.read_text(encoding="utf-8"))
        payload["_cache_hit"] = True
        return payload
    if offline:
        raise FileNotFoundError(f"Offline GitHub GraphQL cache does not exist: {cache_path}")
    if not token:
        raise RuntimeError("GITHUB_TOKEN is required for GitHub GraphQL PR enrichment")

    delay = 2
    for attempt in range(retries):
        try:
            response = requests.post(
                GRAPHQL_ROOT,
                json={"query": GRAPHQL_PULL_REQUEST_PAGE, "variables": variables},
                headers=_headers(token),
                timeout=timeout,
            )
        except requests.RequestException:
            if attempt == retries - 1:
                raise
            _wait_in_chunks(delay, "GitHub GraphQL request failed")
            delay = min(delay * 2, 60)
            continue

        try:
            payload = response.json()
        except ValueError:
            payload = {}
        messages = " ".join(
            str(item.get("message", ""))
            for item in payload.get("errors", [])
            if isinstance(item, dict)
        ).lower()
        retry_after = response.headers.get("Retry-After")
        remaining = response.headers.get("X-RateLimit-Remaining")
        primary = remaining == "0" or "rate limit" in messages
        secondary = (
            response.status_code == 429
            or retry_after is not None
            or "secondary rate limit" in messages
            or "abuse detection" in messages
        )
        if response.status_code in {403, 429} and not primary and not secondary:
            response.raise_for_status()
        if response.status_code in {403, 429} or primary or secondary:
            if attempt == retries - 1:
                response.raise_for_status()
                raise RuntimeError(f"GitHub GraphQL errors: {payload.get('errors', [])}")
            if retry_after:
                try:
                    wait = max(1, int(retry_after))
                except ValueError:
                    wait = 60
                reason = "GitHub GraphQL Retry-After"
            elif primary:
                reset = int(response.headers.get("X-RateLimit-Reset", "0"))
                wait = max(1, reset - int(time.time()) + 1)
                reason = "GitHub GraphQL primary rate limit"
            else:
                wait = min(max(60, delay), 300)
                reason = "GitHub GraphQL secondary rate limit"
            _wait_in_chunks(wait, reason)
            delay = min(delay * 2, 300)
            continue
        if response.status_code in {500, 502, 503, 504}:
            if attempt == retries - 1:
                response.raise_for_status()
            _wait_in_chunks(delay, f"GitHub GraphQL returned HTTP {response.status_code}")
            delay = min(delay * 2, 60)
            continue

        response.raise_for_status()
        if payload.get("errors"):
            raise RuntimeError(f"GitHub GraphQL errors: {payload['errors']}")
        if not isinstance(payload.get("data"), dict):
            raise ValueError("GitHub GraphQL response did not contain a data object")
        _atomic_write_json(cache_path, payload)
        payload["_cache_hit"] = False
        return payload
    raise RuntimeError("Could not retrieve GitHub GraphQL PR page")


def _build_pr_evidence(
    project,
    pull,
    files,
    *,
    known_paths=(),
    paper_paths=(),
    repository=None,
    evidence_source="rest",
    file_list_complete=True,
):
    number = int(pull["number"])
    names = [item.get("filename", "") for item in files]
    revisions = (
        pull.get("merge_commit_sha", ""),
        (pull.get("head") or {}).get("sha", ""),
        (pull.get("base") or {}).get("sha", ""),
    )
    ansible = []
    paper = []
    paper_paths = set(paper_paths)
    details = []
    bases = set()
    for item in files:
        name = item.get("filename", "")
        previous = item.get("previous_filename", "")
        basis = ""
        matched_path = name
        if is_production_ansible_path(name, known_paths):
            basis = "classified-or-layout-path"
        elif previous and is_production_ansible_path(previous, known_paths):
            basis = "renamed-from-production-ansible-path"
            matched_path = previous
        elif (
            PurePosixPath(name).suffix.lower() in {".yml", ".yaml"}
            and not _excluded_path(name)
            and _content_confirms_ansible(repository, revisions, name)
        ):
            basis = "parsed-ansible-content-at-frozen-revision"
        if basis:
            ansible.append(name)
            bases.add(basis)
            detail = f"{item.get('status', 'unknown')}:{name}"
            if previous:
                detail += f"<-{previous}"
            details.append(f"{detail}[{basis};matched={matched_path}]")
            if (
                name in paper_paths or previous in paper_paths
                or (
                    basis == "parsed-ansible-content-at-frozen-revision"
                    and _paper_path(name)
                )
            ):
                paper.append(name)
    return {
        "project": project,
        "pr_number": number,
        "pr_url": pull.get("html_url", ""),
        "base_sha": (pull.get("base") or {}).get("sha", ""),
        "head_sha": (pull.get("head") or {}).get("sha", ""),
        "merge_sha": pull.get("merge_commit_sha", ""),
        "merged_at": pull.get("merged_at", ""),
        "changed_files": len(names),
        "change_statuses": ";".join(
            f"{item.get('status', 'unknown')}:{item.get('filename', '')}"
            for item in files
        ),
        "renamed_or_previous_paths": ";".join(
            f"{item.get('previous_filename')}->{item.get('filename', '')}"
            for item in files if item.get("previous_filename")
        ),
        "ansible_changed_files": ";".join(ansible),
        "ansible_change_evidence": ";".join(details),
        "qualification_basis": (
            ";".join(sorted(bases)) if bases else "no-production-ansible-change"
        ),
        "paper_comparable_changed_files": ";".join(paper),
        "primary_qualifies": "true" if ansible else "false",
        "paper_comparable_qualifies": "true" if paper else "false",
        "qualifies": "true" if ansible else "false",
        "evidence_source": evidence_source,
        "file_list_complete": "true" if file_list_complete else "false",
    }


def evaluate_project_prs(
    project,
    *,
    cache_dir,
    token=None,
    offline=False,
    refresh_cache=False,
    known_paths=(),
    paper_paths=(),
    repository=None,
):
    """Legacy exact REST evaluator retained for compatibility and auditing."""
    evidence = []
    pulls = _paged(
        f"{API_ROOT}/repos/{project}/pulls",
        {"state": "closed", "sort": "created", "direction": "desc"},
        cache_dir=cache_dir, token=token, offline=offline,
        refresh_cache=refresh_cache,
    )
    for pull in pulls:
        if not pull.get("merged_at"):
            continue
        number = int(pull["number"])
        files = list(
            _paged(
                f"{API_ROOT}/repos/{project}/pulls/{number}/files",
                {}, cache_dir=cache_dir, token=token, offline=offline,
                refresh_cache=refresh_cache,
            )
        )
        evidence.append(
            _build_pr_evidence(
                project,
                pull,
                files,
                known_paths=known_paths,
                paper_paths=paper_paths,
                repository=repository,
            )
        )
    return evidence


def _git_object_exists(repository, revision):
    if not revision:
        return False
    result = subprocess.run(
        ["git", "cat-file", "-e", f"{revision}^{{commit}}"],
        cwd=repository,
        capture_output=True,
    )
    return result.returncode == 0


def _git_changed_files(repository, base_sha, head_sha, expected_count):
    repository = Path(repository) if repository else None
    if repository is None or not (repository / ".git").is_dir():
        return None
    if not (
        _git_object_exists(repository, base_sha)
        and _git_object_exists(repository, head_sha)
    ):
        return None
    result = subprocess.run(
        ["git", "diff", "--name-status", "-M", f"{base_sha}...{head_sha}"],
        cwd=repository,
        capture_output=True,
        text=True,
    )
    if result.returncode:
        return None
    status_names = {
        "A": "added",
        "D": "removed",
        "M": "modified",
        "T": "changed",
        "U": "changed",
        "X": "changed",
        "B": "changed",
    }
    files = []
    for line in result.stdout.splitlines():
        columns = line.split("\t")
        if len(columns) < 2:
            continue
        code = columns[0]
        kind = code[:1]
        if kind in {"R", "C"} and len(columns) >= 3:
            files.append(
                {
                    "filename": columns[2],
                    "previous_filename": columns[1],
                    "status": "renamed" if kind == "R" else "copied",
                }
            )
        else:
            files.append(
                {
                    "filename": columns[1],
                    "status": status_names.get(kind, "changed"),
                }
            )
    if len(files) != int(expected_count or 0):
        return None
    return files


def _graphql_pull_as_rest(node):
    return {
        "number": node["number"],
        "html_url": node.get("url", ""),
        "merged_at": node.get("mergedAt", ""),
        "merge_commit_sha": (node.get("mergeCommit") or {}).get("oid", ""),
        "head": {"sha": node.get("headRefOid", "")},
        "base": {"sha": node.get("baseRefOid", "")},
    }


def _graphql_changed_files(
    project,
    node,
    *,
    repository,
    cache_dir,
    token,
    offline,
    refresh_cache,
):
    connection = node.get("files") or {}
    total = int(connection.get("totalCount") or 0)
    pull = _graphql_pull_as_rest(node)

    # A frozen local clone can recover previous names for renames without an
    # API request. Use it only when its count agrees with GitHub's count.
    local_files = _git_changed_files(
        repository,
        (pull.get("base") or {}).get("sha", ""),
        (pull.get("head") or {}).get("sha", ""),
        total,
    )
    if local_files is not None:
        return local_files, "local-git", True

    nodes = connection.get("nodes") or []
    if not connection.get("pageInfo", {}).get("hasNextPage") and len(nodes) == total:
        status_names = {
            "ADDED": "added",
            "COPIED": "copied",
            "DELETED": "removed",
            "MODIFIED": "modified",
            "RENAMED": "renamed",
            "CHANGED": "changed",
        }
        files = [
            {
                "filename": item.get("path", ""),
                "status": status_names.get(
                    str(item.get("changeType") or "CHANGED"), "changed"
                ),
            }
            for item in nodes
        ]
        return files, "graphql", True

    # Nested GraphQL file connections have an independent cursor for every PR.
    # Oversized PRs are uncommon, so the existing fully cached REST endpoint is
    # a simpler and auditable fallback than managing many nested cursors.
    number = int(node["number"])
    files = list(
        _paged(
            f"{API_ROOT}/repos/{project}/pulls/{number}/files",
            {},
            cache_dir=cache_dir,
            token=token,
            offline=offline,
            refresh_cache=refresh_cache,
        )
    )
    return files, "rest-files-fallback", True


def _new_project_progress(row, mode, threshold, as_of):
    return {
        "schema_version": PROJECT_PROGRESS_SCHEMA,
        "query_version": GRAPHQL_QUERY_VERSION,
        "project": row["project"],
        "commit_sha": row.get("commit_sha", ""),
        "requested_mode": mode,
        "threshold": threshold,
        "as_of_utc": as_of.isoformat(),
        "status": "in_progress",
        "cursor": None,
        "has_next_page": True,
        "pages_completed": 0,
        "merged_pr_total": None,
        "merged_pr_total_as_of": None,
        "merged_prs_seen": 0,
        "merged_prs_examined": 0,
        "evidence": [],
        "rate_limit": {},
        "updated_at_utc": datetime.now(timezone.utc).isoformat(),
    }


def _qualifying_count(progress):
    return sum(item.get("qualifies") == "true" for item in progress["evidence"])


def _progress_is_terminal(progress, mode, threshold):
    status = progress.get("status")
    count = _qualifying_count(progress)
    if mode == "threshold" and count >= threshold:
        return True
    if status in {"complete_exact", "exhausted_below_threshold"}:
        return True
    return False


def evaluate_project_prs_graphql(
    row,
    *,
    checkpoint_path,
    cache_dir,
    token=None,
    offline=False,
    refresh_cache=False,
    known_paths=(),
    paper_paths=(),
    repository=None,
    mode="threshold",
    threshold=DEFAULT_THRESHOLD,
    pr_page_size=DEFAULT_PR_PAGE_SIZE,
    as_of=None,
    on_progress=None,
):
    project = row["project"]
    try:
        owner, name = project.split("/", 1)
    except ValueError as error:
        raise ValueError(f"GitHub project must be owner/name: {project}") from error

    if Path(checkpoint_path).is_file() and not refresh_cache:
        progress = _read_project_progress(checkpoint_path, row, as_of=as_of)
        if as_of is None and progress.get("as_of_utc"):
            as_of = _parse_utc_datetime(progress["as_of_utc"])
    else:
        as_of = as_of or datetime.now(timezone.utc)
        progress = _new_project_progress(row, mode, threshold, as_of)
    as_of = as_of or datetime.now(timezone.utc)
    checkpoint_as_of = progress.get("as_of_utc")
    if checkpoint_as_of and _parse_utc_datetime(checkpoint_as_of) != as_of:
        raise ValueError(
            f"checkpoint as-of changed for {project}; use the original --as-of "
            "or --refresh-cache"
        )
    progress["as_of_utc"] = as_of.isoformat()
    if progress.get("query_version") not in {None, GRAPHQL_QUERY_VERSION}:
        raise ValueError(
            f"checkpoint query version changed for {project}; use --refresh-cache"
        )
    progress["requested_mode"] = mode
    progress["threshold"] = threshold
    if _progress_is_terminal(progress, mode, threshold):
        return progress
    progress["status"] = "in_progress"
    progress.pop("error", None)

    while True:
        variables = {
            "owner": owner,
            "name": name,
            "cursor": progress.get("cursor"),
            "prPageSize": pr_page_size,
            "filePageSize": DEFAULT_FILE_PAGE_SIZE,
        }
        payload = _graphql_request(
            variables,
            cache_dir=cache_dir,
            token=token,
            offline=offline,
            refresh_cache=refresh_cache,
        )
        data = payload["data"]
        repository_data = data.get("repository")
        if repository_data is None:
            raise ValueError(f"GitHub GraphQL repository was not found: {project}")
        connection = repository_data["pullRequests"]
        progress["merged_pr_total"] = int(connection.get("totalCount") or 0)
        progress["rate_limit"] = dict(data.get("rateLimit") or {})
        progress["rate_limit"]["current"] = not payload.get("_cache_hit", False)
        edges = connection.get("edges") or []

        for edge in edges:
            node = edge["node"]
            progress["merged_prs_seen"] = progress.get("merged_prs_seen", 0) + 1
            merged_at = _parse_utc_datetime(node["mergedAt"])
            if merged_at > as_of:
                progress["cursor"] = edge["cursor"]
                progress["updated_at_utc"] = datetime.now(timezone.utc).isoformat()
                _write_project_progress(checkpoint_path, progress)
                continue
            files, source, complete = _graphql_changed_files(
                project,
                node,
                repository=repository,
                cache_dir=cache_dir,
                token=token,
                offline=offline,
                refresh_cache=refresh_cache,
            )
            pull = _graphql_pull_as_rest(node)
            progress["evidence"].append(
                _build_pr_evidence(
                    project,
                    pull,
                    files,
                    known_paths=known_paths,
                    paper_paths=paper_paths,
                    repository=repository,
                    evidence_source=source,
                    file_list_complete=complete,
                )
            )
            progress["merged_prs_examined"] += 1
            progress["cursor"] = edge["cursor"]
            progress["updated_at_utc"] = datetime.now(timezone.utc).isoformat()
            if mode == "threshold" and _qualifying_count(progress) >= threshold:
                progress["status"] = "threshold_reached"
                progress["has_next_page"] = True
                _write_project_progress(checkpoint_path, progress)
                if on_progress:
                    on_progress(progress)
                print(
                    f"  {project}: threshold reached; examined="
                    f"{progress['merged_prs_examined']}/"
                    f"{progress['merged_pr_total']} qualifying="
                    f"{_qualifying_count(progress)}"
                )
                return progress
            _write_project_progress(checkpoint_path, progress)

        page_info = connection.get("pageInfo") or {}
        progress["cursor"] = page_info.get("endCursor") or progress.get("cursor")
        progress["has_next_page"] = bool(page_info.get("hasNextPage"))
        progress["pages_completed"] += 1
        progress["updated_at_utc"] = datetime.now(timezone.utc).isoformat()
        if not progress["has_next_page"]:
            progress["merged_pr_total_as_of"] = progress["merged_prs_examined"]
            progress["status"] = (
                "complete_exact"
                if mode == "exact" or _qualifying_count(progress) >= threshold
                else "exhausted_below_threshold"
            )
        _write_project_progress(checkpoint_path, progress)
        if on_progress:
            on_progress(progress)
        print(
            f"  {project}: examined={progress['merged_prs_examined']}/"
            f"{progress['merged_pr_total']} qualifying={_qualifying_count(progress)} "
            f"graphql_remaining={progress['rate_limit'].get('remaining', 'unknown')}"
        )
        if not progress["has_next_page"]:
            return progress


def _known_paths(classification_dir, project):
    paths, paper_paths = set(), set()
    prefix = project.replace("/", "__") + "__"
    for manifest in Path(classification_dir).glob(prefix + "*.csv"):
        with manifest.open(newline="", encoding="utf-8") as stream:
            for row in csv.DictReader(stream):
                if row.get("included") == "true":
                    paths.add(row["path"])
                if row.get("paper_comparable_cohort") == "true":
                    paper_paths.add(row["path"])
    return paths, paper_paths


def enrich_rows(rows, evidence_by_project):
    for row in rows:
        project = row.get("project", "")
        if project not in evidence_by_project:
            row.setdefault("merged_ansible_changing_prs", "")
            row.setdefault("ansible_pr_scan_status", "not-evaluated")
            row.setdefault("pass_merged_ansible_prs_ge_50", "not-evaluated")
            continue
        result = evidence_by_project[project]
        if isinstance(result, dict):
            evidence = result["evidence"]
            status = result.get("status", "in_progress")
            exact = status in {"complete_exact", "exhausted_below_threshold"}
            examined = result.get("merged_prs_examined", len(evidence))
            total = result.get("merged_pr_total")
            total_as_of = result.get("merged_pr_total_as_of")
            seen = result.get("merged_prs_seen", examined)
            pages = result.get("pages_completed", "")
            mode = result.get("requested_mode", "")
            as_of = result.get("as_of_utc", "")
        else:
            evidence = result
            status = "legacy_complete_exact"
            exact = True
            examined = len(evidence)
            total = len(evidence)
            total_as_of = len(evidence)
            seen = len(evidence)
            pages = ""
            mode = "legacy-rest-exact"
            as_of = ""
        count = sum(item["qualifies"] == "true" for item in evidence)
        paper_count = sum(
            item.get("paper_comparable_qualifies") == "true" for item in evidence
        )
        row["merged_ansible_changing_prs"] = str(count)
        row["merged_paper_comparable_prs"] = str(paper_count)
        row["merged_ansible_pr_count_is_exact"] = "true" if exact else "false"
        row["merged_ansible_pr_count_lower_bound"] = str(count)
        row["ansible_prs_examined"] = str(examined)
        row["ansible_prs_seen"] = str(seen)
        row["merged_pr_total_graphql"] = "" if total is None else str(total)
        row["merged_pr_total_as_of"] = (
            "" if total_as_of is None else str(total_as_of)
        )
        row["ansible_pr_as_of_utc"] = as_of
        row["ansible_pr_pages_completed"] = str(pages)
        row["ansible_pr_scan_mode"] = mode
        row["ansible_pr_scan_status"] = status
        if count >= 50:
            row["pass_merged_ansible_prs_ge_50"] = "true"
        elif status in {"exhausted_below_threshold", "complete_exact", "legacy_complete_exact"}:
            row["pass_merged_ansible_prs_ge_50"] = "false"
        else:
            row["pass_merged_ansible_prs_ge_50"] = "not-evaluated"
    return rows


def _eligible_rows(rows):
    eligible = []
    for row in rows:
        total = str(row.get("total_prs") or "").strip()
        metadata_ok = (
            row.get("metadata_eligible", row.get("preclone_eligible")) == "true"
        )
        commits = str(row.get("total_commits") or "").strip()
        production = str(row.get("production_ansible_files") or "").strip()
        if (
            metadata_ok
            and total.isdigit() and int(total) > 50
            and commits.isdigit() and int(commits) >= 1000
            and production.isdigit() and int(production) >= 1
        ):
            eligible.append(row)
    return eligible


def _project_evidence_path(cache_dir, row):
    return _cache_path(
        cache_dir,
        "ansible-pr-project",
        {
            "schema_version": PROJECT_EVIDENCE_SCHEMA,
            "project": row["project"],
            "commit_sha": row.get("commit_sha", ""),
        },
    )


def _read_project_evidence(path):
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if payload.get("schema_version") not in {
        PROJECT_EVIDENCE_SCHEMA,
        PROJECT_PROGRESS_SCHEMA,
    }:
        raise ValueError(f"unsupported project PR checkpoint: {path}")
    evidence = payload.get("evidence")
    if not isinstance(evidence, list):
        raise ValueError(f"invalid project PR checkpoint: {path}")
    return evidence


def _write_project_evidence(path, row, evidence):
    _atomic_write_json(
        path,
        {
            "schema_version": PROJECT_EVIDENCE_SCHEMA,
            "project": row["project"],
            "commit_sha": row.get("commit_sha", ""),
            "evidence": evidence,
        },
    )


def _read_project_progress(path, row=None, as_of=None):
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    schema = payload.get("schema_version")
    if schema == PROJECT_EVIDENCE_SCHEMA:
        evidence = payload.get("evidence")
        if not isinstance(evidence, list):
            raise ValueError(f"invalid legacy project PR checkpoint: {path}")
        original_count = len(evidence)
        if as_of is not None:
            evidence = [
                item
                for item in evidence
                if not item.get("merged_at")
                or _parse_utc_datetime(item["merged_at"]) <= as_of
            ]
        return {
            "schema_version": PROJECT_PROGRESS_SCHEMA,
            "query_version": None,
            "project": payload.get("project", (row or {}).get("project", "")),
            "commit_sha": payload.get(
                "commit_sha", (row or {}).get("commit_sha", "")
            ),
            "requested_mode": "legacy-rest-exact",
            "threshold": DEFAULT_THRESHOLD,
            "as_of_utc": as_of.isoformat() if as_of is not None else "",
            "status": "complete_exact",
            "cursor": None,
            "has_next_page": False,
            "pages_completed": 0,
            "merged_pr_total": original_count,
            "merged_pr_total_as_of": len(evidence),
            "merged_prs_seen": original_count,
            "merged_prs_examined": len(evidence),
            "evidence": evidence,
            "rate_limit": {},
            "updated_at_utc": payload.get("updated_at_utc", ""),
            "legacy_checkpoint": True,
            "legacy_prs_after_as_of_excluded": original_count - len(evidence),
        }
    if schema != PROJECT_PROGRESS_SCHEMA:
        raise ValueError(f"unsupported project PR checkpoint: {path}")
    if not isinstance(payload.get("evidence"), list):
        raise ValueError(f"invalid project PR checkpoint: {path}")
    if row and (
        payload.get("project") != row.get("project")
        or payload.get("commit_sha", "") != row.get("commit_sha", "")
    ):
        raise ValueError(f"project PR checkpoint identity mismatch: {path}")
    return payload


def _write_project_progress(path, progress):
    progress = dict(progress)
    progress["schema_version"] = PROJECT_PROGRESS_SCHEMA
    progress["query_version"] = GRAPHQL_QUERY_VERSION
    _atomic_write_json(path, progress)


PROGRESS_FIELDS = (
    "project",
    "commit_sha",
    "status",
    "requested_mode",
    "threshold",
    "as_of_utc",
    "merged_pr_total",
    "merged_pr_total_as_of",
    "merged_prs_seen",
    "merged_prs_examined",
    "qualifying_ansible_prs",
    "count_is_exact",
    "pages_completed",
    "cursor",
    "graphql_cost",
    "graphql_remaining",
    "graphql_reset_at",
    "graphql_rate_current",
    "legacy_prs_after_as_of_excluded",
    "error",
    "updated_at_utc",
)


def _write_progress_ledger(path, eligible_rows, progress_by_project):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    with temporary.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=PROGRESS_FIELDS)
        writer.writeheader()
        for row in eligible_rows:
            project = row["project"]
            progress = progress_by_project.get(project)
            if progress is None:
                writer.writerow(
                    {
                        "project": project,
                        "commit_sha": row.get("commit_sha", ""),
                        "status": "pending",
                    }
                )
                continue
            rate = progress.get("rate_limit") or {}
            status = progress.get("status", "in_progress")
            writer.writerow(
                {
                    "project": project,
                    "commit_sha": row.get("commit_sha", ""),
                    "status": status,
                    "requested_mode": progress.get("requested_mode", ""),
                    "threshold": progress.get("threshold", DEFAULT_THRESHOLD),
                    "as_of_utc": progress.get("as_of_utc", ""),
                    "merged_pr_total": progress.get("merged_pr_total", ""),
                    "merged_pr_total_as_of": progress.get(
                        "merged_pr_total_as_of", ""
                    ),
                    "merged_prs_seen": progress.get("merged_prs_seen", 0),
                    "merged_prs_examined": progress.get("merged_prs_examined", 0),
                    "qualifying_ansible_prs": _qualifying_count(progress),
                    "count_is_exact": (
                        "true"
                        if status in {"complete_exact", "exhausted_below_threshold"}
                        else "false"
                    ),
                    "pages_completed": progress.get("pages_completed", 0),
                    "cursor": progress.get("cursor") or "",
                    "graphql_cost": rate.get("cost", ""),
                    "graphql_remaining": rate.get("remaining", ""),
                    "graphql_reset_at": rate.get("resetAt", ""),
                    "graphql_rate_current": str(
                        rate.get("current", "")
                    ).lower(),
                    "legacy_prs_after_as_of_excluded": progress.get(
                        "legacy_prs_after_as_of_excluded", ""
                    ),
                    "error": progress.get("error", ""),
                    "updated_at_utc": progress.get("updated_at_utc", ""),
                }
            )
    temporary.replace(path)


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Enrich frozen GitHub candidates with merged Ansible-changing PRs."
    )
    parser.add_argument("candidates", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--evidence-output", type=Path, required=True)
    parser.add_argument("--cache-dir", type=Path, default=Path("study/cache/github"))
    parser.add_argument("--classification-dir", type=Path, default=Path("study/manifests/file-classification"))
    parser.add_argument(
        "--mode",
        choices=("threshold", "exact"),
        default="threshold",
        help="stop after proving the threshold, or enumerate every merged PR",
    )
    parser.add_argument("--threshold", type=int, default=DEFAULT_THRESHOLD)
    parser.add_argument(
        "--pr-page-size",
        type=int,
        default=DEFAULT_PR_PAGE_SIZE,
        help="merged PRs requested per GraphQL page (1-100)",
    )
    parser.add_argument(
        "--progress-output",
        type=Path,
        help="durable per-project progress CSV (default: <output>.progress.csv)",
    )
    parser.add_argument(
        "--as-of",
        default=os.environ.get("STUDY_AS_OF"),
        help="freeze eligible PR evidence at this ISO-8601 time (default: STUDY_AS_OF or now)",
    )
    parser.add_argument("--offline", action="store_true")
    parser.add_argument("--refresh-cache", action="store_true")
    args = parser.parse_args(argv)
    if args.threshold < 50:
        parser.error("--threshold must be at least 50 for the approved study gate")
    if not 1 <= args.pr_page_size <= 100:
        parser.error("--pr-page-size must be between 1 and 100")
    try:
        as_of = (
            _parse_utc_datetime(args.as_of)
            if args.as_of
            else datetime.now(timezone.utc)
        )
    except ValueError:
        parser.error("--as-of must be an ISO-8601 timestamp")
    progress_output = args.progress_output or args.output.with_suffix(".progress.csv")
    with args.candidates.open(newline="", encoding="utf-8") as stream:
        reader = csv.DictReader(stream)
        rows = list(reader)
        fields = list(reader.fieldnames or [])
    token = os.environ.get("GITHUB_TOKEN")
    if not token and not args.offline:
        parser.error("GITHUB_TOKEN is required unless --offline is used")
    progress_by_project = {}
    eligible = _eligible_rows(rows)
    if not args.refresh_cache:
        for row in eligible:
            checkpoint = _project_evidence_path(args.cache_dir, row)
            if checkpoint.is_file():
                progress_by_project[row["project"]] = _read_project_progress(
                    checkpoint, row, as_of=as_of
                )

    def record_progress(current):
        progress_by_project[current["project"]] = current
        _write_progress_ledger(progress_output, eligible, progress_by_project)

    _write_progress_ledger(progress_output, eligible, progress_by_project)
    for index, row in enumerate(eligible, 1):
        project = row["project"]
        checkpoint = _project_evidence_path(args.cache_dir, row)
        if project in progress_by_project:
            progress = progress_by_project[project]
            if (
                progress.get("as_of_utc")
                and _parse_utc_datetime(progress["as_of_utc"]) != as_of
            ):
                raise ValueError(
                    f"checkpoint as-of changed for {project}; use the original "
                    "--as-of or --refresh-cache"
                )
            if _progress_is_terminal(progress, args.mode, args.threshold):
                print(f"[{index}/{len(eligible)}] reusing PR checkpoint for {project}")
                continue
            print(
                f"[{index}/{len(eligible)}] resuming {project} after "
                f"{progress['merged_prs_examined']} merged PRs"
            )
        else:
            print(f"[{index}/{len(eligible)}] inspecting merged PR files for {project}")
        known_paths, paper_paths = _known_paths(args.classification_dir, project)
        try:
            progress = evaluate_project_prs_graphql(
                row,
                checkpoint_path=checkpoint,
                cache_dir=args.cache_dir,
                token=token,
                offline=args.offline,
                refresh_cache=args.refresh_cache,
                known_paths=known_paths,
                paper_paths=paper_paths,
                repository=row.get("repository_path"),
                mode=args.mode,
                threshold=args.threshold,
                pr_page_size=args.pr_page_size,
                as_of=as_of,
                on_progress=record_progress,
            )
        except Exception as error:
            status_code = getattr(getattr(error, "response", None), "status_code", None)
            if status_code in {401, 403, 429} or (
                args.offline and isinstance(error, FileNotFoundError)
            ):
                raise
            if checkpoint.is_file():
                progress = _read_project_progress(checkpoint, row, as_of=as_of)
            else:
                progress = _new_project_progress(
                    row, args.mode, args.threshold, as_of
                )
            progress["status"] = "failed"
            progress["error"] = f"{type(error).__name__}: {error}"
            progress["updated_at_utc"] = datetime.now(timezone.utc).isoformat()
            _write_project_progress(checkpoint, progress)
            print(f"  {project}: failed: {progress['error']}")
        progress_by_project[project] = progress
        _write_progress_ledger(progress_output, eligible, progress_by_project)
    enrich_rows(rows, progress_by_project)
    for field in (
        "merged_ansible_changing_prs",
        "merged_paper_comparable_prs",
        "merged_ansible_pr_count_is_exact",
        "merged_ansible_pr_count_lower_bound",
        "ansible_prs_examined",
        "ansible_prs_seen",
        "merged_pr_total_graphql",
        "merged_pr_total_as_of",
        "ansible_pr_as_of_utc",
        "ansible_pr_pages_completed",
        "ansible_pr_scan_mode",
        "ansible_pr_scan_status",
        "pass_merged_ansible_prs_ge_50",
    ):
        if field not in fields:
            fields.append(field)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)
    args.evidence_output.parent.mkdir(parents=True, exist_ok=True)
    with args.evidence_output.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=PR_FIELDS)
        writer.writeheader()
        for project in sorted(progress_by_project):
            writer.writerows(progress_by_project[project]["evidence"])
    metadata = {
        "schema_version": 4,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "criterion": "merged pull request changes at least one production Ansible path",
        "change_semantics": "added, modified, removed, and renamed paths count when production classification is evidenced",
        "excluded_path_classes": sorted(EXCLUDED_PARTS),
        "collector": "graphql-with-local-git-and-rest-files-fallback",
        "mode": args.mode,
        "threshold": args.threshold,
        "as_of_utc": as_of.isoformat(),
        "count_semantics": (
            "lower-bound-at-threshold" if args.mode == "threshold" else "exact"
        ),
        "progress_output": str(progress_output),
        "projects_evaluated": len(progress_by_project),
    }
    args.evidence_output.with_suffix(".metadata.json").write_text(
        json.dumps(metadata, indent=2), encoding="utf-8"
    )


if __name__ == "__main__":
    main()
