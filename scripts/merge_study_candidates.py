#!/usr/bin/env python3
"""Union candidate sources while preserving provenance and unresolved entries."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

try:
    from scripts.discover_ansible_galaxy import github_project
except ModuleNotFoundError:
    from discover_ansible_galaxy import github_project


MULTI_FIELDS = {
    "discovery_sources", "discovery_methods", "discovery_query", "galaxy_url",
    "galaxy_kind", "galaxy_id", "galaxy_name",
}


def _read(path):
    with Path(path).open(newline="", encoding="utf-8") as stream:
        return list(csv.DictReader(stream))


def canonical(row):
    project = str(row.get("canonical_repository") or "").strip()
    if not project:
        project = github_project(row.get("github_url") or row.get("clone_url") or "")
    if not project and "/" in str(row.get("project") or "") and not str(row["project"]).startswith("galaxy:"):
        project = row["project"]
    return project.lower() if project else f"{row.get('source_host', '')}:{row.get('project', '')}".lower()


def merge_candidates(manifests):
    merged = {}
    for path in manifests:
        for source in _read(path):
            key = canonical(source)
            source["canonical_repository"] = key if ":" not in key.split("/", 1)[0] else ""
            if key not in merged:
                merged[key] = dict(source)
                continue
            target = merged[key]
            for field, value in source.items():
                if value in {None, ""}:
                    continue
                if field in MULTI_FIELDS:
                    values = set(filter(None, str(target.get(field, "")).split(";")))
                    values.update(filter(None, str(value).split(";")))
                    target[field] = ";".join(sorted(values))
                elif not target.get(field) or source.get("source_host") == "github":
                    target[field] = value
    return sorted(merged.values(), key=lambda row: canonical(row))


def write(rows, output):
    fields = list(dict.fromkeys(key for row in rows for key in row))
    Path(output).parent.mkdir(parents=True, exist_ok=True)
    with Path(output).open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main(argv=None):
    parser = argparse.ArgumentParser(description="Merge and deduplicate study candidate manifests.")
    parser.add_argument("manifests", nargs="+", type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args(argv)
    rows = merge_candidates(args.manifests)
    write(rows, args.output)
    print(f"Wrote {len(rows)} deduplicated candidates from {len(args.manifests)} sources")


if __name__ == "__main__":
    main()
