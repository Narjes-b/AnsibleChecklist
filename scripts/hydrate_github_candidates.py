#!/usr/bin/env python3
"""Hydrate Galaxy-resolved GitHub repositories with current GitHub metadata."""

from __future__ import annotations

import argparse
import csv
from datetime import datetime, timezone
import os
from pathlib import Path

try:
    from scripts.discover_github_ansible import (
        API_ROOT, DEFAULT_CACHE, _cache_path, _request_json, repository_row,
    )
except ModuleNotFoundError:
    from discover_github_ansible import (
        API_ROOT, DEFAULT_CACHE, _cache_path, _request_json, repository_row,
    )


def _read(path):
    with Path(path).open(newline="", encoding="utf-8") as stream:
        return list(csv.DictReader(stream))


def hydrate(rows, *, as_of, cache_dir=DEFAULT_CACHE, token=None, offline=False, refresh=False):
    hydrated = []
    for index, source in enumerate(rows, 1):
        project = source.get("canonical_repository") or source.get("project", "")
        if "/" not in project or project.startswith("galaxy:"):
            hydrated.append(dict(source))
            continue
        if source.get("repository_id") and source.get("source_host") == "github":
            hydrated.append(dict(source))
            continue
        print(f"[{index}/{len(rows)}] hydrating GitHub metadata for {project}")
        try:
            item = _request_json(
                f"{API_ROOT}/repos/{project}", params={},
                cache_path=_cache_path(cache_dir, "repository-detail", {"project": project}),
                token=token, offline=offline, refresh_cache=refresh,
            )
        except Exception as exc:
            row = dict(source)
            row["repository_resolution_status"] = "github-metadata-failed"
            row["repository_resolution_error"] = str(exc)
            hydrated.append(row)
            continue
        row = repository_row(
            item, source.get("discovery_query") or "seed:ansible-galaxy",
            datetime.now(timezone.utc).isoformat(), as_of,
        )
        for field, value in source.items():
            if value not in {None, ""} and (field.startswith("galaxy_") or field not in row):
                row[field] = value
        sources = set(filter(None, str(source.get("discovery_sources", "")).split(";")))
        sources.add("github")
        row["discovery_sources"] = ";".join(sorted(sources))
        methods = set(filter(None, str(source.get("discovery_methods", "")).split(";")))
        methods.add("github-repository-hydration")
        row["discovery_methods"] = ";".join(sorted(methods))
        row["canonical_repository"] = project.lower()
        row["repository_resolution_status"] = "github-hydrated"
        hydrated.append(row)
    return hydrated


def _write(rows, output):
    fields = list(dict.fromkeys(key for row in rows for key in row))
    Path(output).parent.mkdir(parents=True, exist_ok=True)
    with Path(output).open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main(argv=None):
    parser = argparse.ArgumentParser(description="Hydrate GitHub metadata for merged candidate sources.")
    parser.add_argument("candidates", type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--cache-dir", type=Path, default=DEFAULT_CACHE)
    parser.add_argument("--as-of", required=True)
    parser.add_argument("--offline", action="store_true")
    parser.add_argument("--refresh-cache", action="store_true")
    args = parser.parse_args(argv)
    as_of = datetime.fromisoformat(args.as_of.replace("Z", "+00:00"))
    rows = hydrate(
        _read(args.candidates), as_of=as_of, cache_dir=args.cache_dir,
        token=os.environ.get("GITHUB_TOKEN"), offline=args.offline,
        refresh=args.refresh_cache,
    )
    _write(rows, args.output)
    print(f"Wrote {len(rows)} hydrated candidates")


if __name__ == "__main__":
    main()
