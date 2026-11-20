#!/usr/bin/env python3
"""Discover source repositories referenced by Ansible Galaxy roles/collections."""

from __future__ import annotations

import argparse
import csv
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import time
from urllib.parse import urljoin, urlparse

import requests


GALAXY = "https://galaxy.ansible.com"
ROLES = f"{GALAXY}/api/v1/roles/"
COLLECTIONS = f"{GALAXY}/api/v3/plugin/ansible/content/published/collections/index/"
DEFAULT_CACHE = Path("study/cache/galaxy")
DEFAULT_OUTPUT = Path("study/manifests/galaxy-candidates-v2.csv")


def _cache_path(cache_dir, url, params=None):
    identity = json.dumps({"url": url, "params": params or {}}, sort_keys=True)
    return Path(cache_dir) / f"galaxy-{hashlib.sha256(identity.encode()).hexdigest()[:24]}.json"


def _get(url, *, params=None, cache_dir=DEFAULT_CACHE, refresh=False, offline=False):
    cache = _cache_path(cache_dir, url, params)
    if cache.is_file() and (offline or not refresh):
        return json.loads(cache.read_text(encoding="utf-8"))
    if offline:
        raise FileNotFoundError(f"Offline Galaxy cache does not exist: {cache}")
    delay = 2
    for attempt in range(5):
        try:
            response = requests.get(
                url, params=params, timeout=60,
                headers={"User-Agent": "ansibleguard-study/2"},
            )
            if response.status_code in {429, 500, 502, 503, 504}:
                response.raise_for_status()
            response.raise_for_status()
            payload = response.json()
            cache.parent.mkdir(parents=True, exist_ok=True)
            cache.write_text(json.dumps(payload, indent=2), encoding="utf-8")
            return payload
        except (requests.RequestException, ValueError):
            if attempt == 4:
                raise
            time.sleep(delay)
            delay = min(delay * 2, 30)
    raise RuntimeError(f"Could not retrieve {url}")


def github_project(url):
    value = str(url or "").strip()
    if value.startswith("git@github.com:"):
        value = "https://github.com/" + value.split(":", 1)[1]
    parsed = urlparse(value)
    if parsed.netloc.lower() not in {"github.com", "www.github.com"}:
        return ""
    parts = [part for part in parsed.path.strip("/").split("/") if part]
    if len(parts) < 2:
        return ""
    return f"{parts[0]}/{parts[1].removesuffix('.git')}"


def _base_row(kind, galaxy_id, name, source_url, project, discovered_at, **extra):
    resolved = bool(project)
    return {
        "selection_protocol_version": "2",
        "source_host": "galaxy",
        "project": project or f"galaxy:{kind}:{name}",
        "canonical_repository": project.lower() if project else "",
        "source_url": source_url,
        "galaxy_url": source_url,
        "clone_url": f"https://github.com/{project}.git" if resolved else "",
        "github_url": f"https://github.com/{project}" if resolved else "",
        "galaxy_kind": kind,
        "galaxy_id": galaxy_id,
        "galaxy_name": name,
        "repository_resolution_status": "github-resolved" if resolved else "unresolved",
        "discovery_sources": "ansible-galaxy",
        "discovery_methods": f"galaxy-{kind}-registry",
        "discovery_coverage_scope": "published-ansible-galaxy-registry",
        "discovery_coverage_warning": "registry-entry-may-be-stale-or-have-no-source-repository",
        "discovery_query": f"ansible-galaxy:{kind}",
        "discovered_at_utc": discovered_at,
        "stars_used_for_selection": "false",
        **extra,
    }


def discover_roles(*, cache_dir=DEFAULT_CACHE, refresh=False, offline=False, limit=None):
    rows, page, seen = [], 1, 0
    discovered_at = datetime.now(timezone.utc).isoformat()
    while True:
        payload = _get(
            ROLES, params={"page_size": 500, "page": page}, cache_dir=cache_dir,
            refresh=refresh, offline=offline,
        )
        for item in payload.get("results", []):
            project = ""
            if item.get("github_user") and item.get("github_repo"):
                project = f"{item['github_user']}/{str(item['github_repo']).removesuffix('.git')}"
            namespace = ((item.get("summary_fields") or {}).get("namespace") or {}).get("name", "")
            role_name = f"{namespace}.{item.get('name', '')}" if namespace else item.get("name", "")
            rows.append(_base_row(
                "role", item.get("id", ""), role_name,
                f"{GALAXY}/ui/standalone/roles/{item.get('id', '')}/",
                project, discovered_at,
                galaxy_download_count=item.get("download_count", ""),
                galaxy_updated_at=item.get("modified", ""),
                galaxy_version=item.get("commit", ""),
            ))
            seen += 1
            if limit is not None and seen >= limit:
                return rows
        if not payload.get("next"):
            return rows
        page += 1


def discover_collections(*, cache_dir=DEFAULT_CACHE, refresh=False, offline=False, limit=None):
    rows, offset, seen = [], 0, 0
    discovered_at = datetime.now(timezone.utc).isoformat()
    while True:
        payload = _get(
            COLLECTIONS, params={"limit": 100, "offset": offset},
            cache_dir=cache_dir, refresh=refresh, offline=offline,
        )
        for item in payload.get("data", []):
            version = item.get("highest_version") or {}
            detail_url = urljoin(GALAXY, version.get("href", ""))
            detail = _get(
                detail_url, cache_dir=cache_dir, refresh=refresh, offline=offline
            ) if detail_url else {}
            metadata = detail.get("metadata") or {}
            project = github_project(metadata.get("repository"))
            name = f"{item.get('namespace', '')}.{item.get('name', '')}"
            rows.append(_base_row(
                "collection", (detail.get("collection") or {}).get("id", ""),
                name, f"{GALAXY}/ui/repo/published/{name.replace('.', '/')}/",
                project, discovered_at,
                galaxy_download_count=item.get("download_count", ""),
                galaxy_updated_at=item.get("updated_at", ""),
                galaxy_version=version.get("version", ""),
            ))
            seen += 1
            if limit is not None and seen >= limit:
                return rows
        next_link = (payload.get("links") or {}).get("next")
        if not next_link:
            return rows
        offset += 100


def deduplicate(rows):
    merged = {}
    for row in rows:
        key = row.get("canonical_repository") or row["project"].lower()
        if key not in merged:
            merged[key] = dict(row)
            continue
        current = merged[key]
        for field in ("galaxy_kind", "galaxy_id", "galaxy_name", "galaxy_url"):
            values = set(filter(None, str(current.get(field, "")).split(";")))
            values.update(filter(None, str(row.get(field, "")).split(";")))
            current[field] = ";".join(sorted(values))
    return sorted(merged.values(), key=lambda row: row["project"].lower())


def write_rows(rows, output):
    rows = list(rows)
    fields = list(dict.fromkeys(key for row in rows for key in row))
    Path(output).parent.mkdir(parents=True, exist_ok=True)
    with Path(output).open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main(argv=None):
    parser = argparse.ArgumentParser(description="Discover repositories referenced by Ansible Galaxy.")
    parser.add_argument("--kind", choices=("roles", "collections", "both"), default="both")
    parser.add_argument("--cache-dir", type=Path, default=DEFAULT_CACHE)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--refresh-cache", action="store_true")
    parser.add_argument("--offline", action="store_true")
    parser.add_argument("--limit", type=int, help="diagnostic only; omit for complete registry")
    args = parser.parse_args(argv)
    rows = []
    if args.kind in {"roles", "both"}:
        rows.extend(discover_roles(
            cache_dir=args.cache_dir, refresh=args.refresh_cache,
            offline=args.offline, limit=args.limit,
        ))
    if args.kind in {"collections", "both"}:
        rows.extend(discover_collections(
            cache_dir=args.cache_dir, refresh=args.refresh_cache,
            offline=args.offline, limit=args.limit,
        ))
    rows = deduplicate(rows)
    write_rows(rows, args.output)
    resolved = sum(row["repository_resolution_status"] == "github-resolved" for row in rows)
    metadata = {
        "schema_version": 1,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "kind": args.kind,
        "diagnostic_limit": args.limit,
        "unique_candidates": len(rows),
        "github_resolved": resolved,
        "unresolved": len(rows) - resolved,
        "source": GALAXY,
    }
    args.output.with_suffix(".metadata.json").write_text(
        json.dumps(metadata, indent=2), encoding="utf-8"
    )
    print(f"Wrote {len(rows)} unique Galaxy candidates; GitHub-resolved={resolved}")


if __name__ == "__main__":
    main()
