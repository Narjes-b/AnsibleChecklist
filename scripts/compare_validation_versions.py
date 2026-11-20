#!/usr/bin/env python3
"""Compare canonical occurrences from two frozen validation scan versions."""

from __future__ import annotations

import argparse
from collections import Counter
import csv
import json
from pathlib import Path

PAIR_FIELDS = (
    "project", "commit_sha", "status", "match", "concept_id", "file", "line",
    "severity", "confidence", "base_occurrence_id", "head_occurrence_id",
    "base_message", "head_message", "old_consensus_label", "old_consensus_reason",
)


def _unique_pairs(base_remaining, head_remaining, key_function, match):
    base_index = {}
    head_index = {}
    for identifier, item in base_remaining.items():
        key = key_function(item)
        if key is not None:
            base_index.setdefault(key, []).append(identifier)
    for identifier, item in head_remaining.items():
        key = key_function(item)
        if key is not None:
            head_index.setdefault(key, []).append(identifier)
    pairs = []
    for key in sorted(set(base_index) & set(head_index), key=str):
        if len(base_index[key]) != 1 or len(head_index[key]) != 1:
            continue
        base_id = base_index[key][0]
        head_id = head_index[key][0]
        pairs.append({
            "base": base_remaining.pop(base_id),
            "head": head_remaining.pop(head_id),
            "match": match,
        })
    return pairs


def compare_version_occurrences(base, head):
    """Linear-index comparison suitable for full immutable snapshot corpora."""
    base_remaining = {item["occurrence_id"]: item for item in base}
    head_remaining = {item["occurrence_id"]: item for item in head}
    unchanged = []
    for identifier in sorted(set(base_remaining) & set(head_remaining)):
        unchanged.append({
            "base": base_remaining.pop(identifier),
            "head": head_remaining.pop(identifier),
            "match": "exact",
        })
    moved = _unique_pairs(
        base_remaining,
        head_remaining,
        lambda item: (
            item.get("concept_id"),
            item.get("scan_mode", "source"),
            item.get("semantic_key"),
        ) if item.get("semantic_key") else None,
        "semantic",
    )
    # Message/remediation changes can change occurrence_id and semantic_key
    # while the finding remains at the same physical location. Pair unique
    # concept/file/line locations before calling them fixed or introduced.
    location = _unique_pairs(
        base_remaining,
        head_remaining,
        lambda item: (
            item.get("concept_id"),
            item.get("scan_mode", "source"),
            item.get("file"),
            int(item.get("line", 1)),
        ),
        "location",
    )
    uncertain = _unique_pairs(
        base_remaining,
        head_remaining,
        lambda item: (
            item.get("concept_id"),
            item.get("scan_mode", "source"),
            item.get("file"),
            tuple(sorted(item.get("native_rules", ()))),
        ) if item.get("concept_id") != "hardcoded-secret" else None,
        "uncertain-detector-shape",
    )
    ordering = lambda item: (
        item.get("file", ""), int(item.get("line", 1)), item.get("concept_id", "")
    )
    return {
        "introduced": sorted(head_remaining.values(), key=ordering),
        "fixed": sorted(base_remaining.values(), key=ordering),
        "moved": moved,
        "location": location,
        "uncertain": uncertain,
        "unchanged": unchanged,
    }


def _load_items(path):
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict) or not isinstance(payload.get("items"), list):
        raise ValueError(f"{path}: expected canonical occurrences payload")
    return payload["items"]


def _snapshot_file(root, project, commit_sha):
    return Path(root) / project.replace("/", "__") / commit_sha / "canonical" / "occurrences.json"


def _provider_scope(root, project, commit_sha, provider):
    path = Path(root) / project.replace("/", "__") / commit_sha / "run_metadata.json"
    if not path.is_file():
        return None
    metadata = json.loads(path.read_text(encoding="utf-8"))
    scope = metadata.get("analysis_scope", {}).get(provider, {})
    return scope.get("scope") if isinstance(scope, dict) else None


def _provider_occurrence(item, provider):
    return item.get("canonical_provider") == provider or any(
        detector.get("provider") == provider
        for detector in item.get("detectors", [])
        if isinstance(detector, dict)
    )


def _old_labels(path):
    if path is None:
        return {}
    with Path(path).open(newline="", encoding="utf-8") as stream:
        return {
            (row.get("project", ""), row.get("occurrence_id", "")): row
            for row in csv.DictReader(stream)
            if row.get("occurrence_id")
        }


def _row(project, commit_sha, status, item, *, other=None, match="", labels=None):
    base = item if status == "fixed" else other
    head = item if status == "introduced" else other
    if status in {"moved", "location", "uncertain", "unchanged"}:
        base, head = item, other
    display = head or base or {}
    label = (labels or {}).get((project, (base or {}).get("occurrence_id", "")), {})
    return {
        "project": project,
        "commit_sha": commit_sha,
        "status": status,
        "match": match,
        "concept_id": display.get("concept_id", ""),
        "file": display.get("file", ""),
        "line": display.get("line", 1),
        "severity": display.get("severity", ""),
        "confidence": display.get("confidence", ""),
        "base_occurrence_id": (base or {}).get("occurrence_id", ""),
        "head_occurrence_id": (head or {}).get("occurrence_id", ""),
        "base_message": (base or {}).get("message", ""),
        "head_message": (head or {}).get("message", ""),
        "old_consensus_label": (
            label.get("adjudicated_label") or label.get("consensus_label", "")
        ),
        "old_consensus_reason": (
            label.get("adjudicated_reason") or label.get("consensus_reason", "")
        ),
    }


def compare_roots(manifest, base_root, head_root, old_labels=None):
    labels = _old_labels(old_labels)
    rows = []
    repositories = []
    with Path(manifest).open(newline="", encoding="utf-8") as stream:
        manifest_rows = list(csv.DictReader(stream))
    for manifest_row in manifest_rows:
        project = manifest_row["project"]
        commit_sha = manifest_row["commit_sha"]
        base_path = _snapshot_file(base_root, project, commit_sha)
        head_path = _snapshot_file(head_root, project, commit_sha)
        missing = [name for name, path in (("base", base_path), ("head", head_path)) if not path.is_file()]
        if missing:
            repositories.append({
                "project": project, "commit_sha": commit_sha,
                "status": "missing-" + "-and-".join(missing),
                "base_occurrences": "", "head_occurrences": "",
                "introduced": "", "fixed": "", "moved": "",
                "location": "", "uncertain": "", "unchanged": "",
            })
            continue
        base = _load_items(base_path)
        head = _load_items(head_path)
        base_lint_scope = _provider_scope(
            base_root, project, commit_sha, "ansible_lint"
        )
        head_lint_scope = _provider_scope(
            head_root, project, commit_sha, "ansible_lint"
        )
        lint_scope_mismatch = bool(
            base_lint_scope and head_lint_scope
            and base_lint_scope != head_lint_scope
        )
        excluded_provider_occurrences = 0
        if lint_scope_mismatch:
            base_before, head_before = len(base), len(head)
            base = [item for item in base if not _provider_occurrence(item, "ansible-lint")]
            head = [item for item in head if not _provider_occurrence(item, "ansible-lint")]
            excluded_provider_occurrences = (
                base_before - len(base) + head_before - len(head)
            )
        comparison = compare_version_occurrences(base, head)
        for item in comparison["introduced"]:
            rows.append(_row(project, commit_sha, "introduced", item, labels=labels))
        for item in comparison["fixed"]:
            rows.append(_row(project, commit_sha, "fixed", item, labels=labels))
        for status in ("moved", "location", "uncertain", "unchanged"):
            for pair in comparison[status]:
                rows.append(_row(
                    project, commit_sha, status, pair["base"], other=pair["head"],
                    match=pair.get("match", ""), labels=labels,
                ))
        repositories.append({
            "project": project,
            "commit_sha": commit_sha,
            "status": "compared",
            "provider_scope_status": (
                "ansible-lint-excluded-scope-mismatch"
                if lint_scope_mismatch else "comparable"
            ),
            "excluded_noncomparable_provider_occurrences": (
                excluded_provider_occurrences
            ),
            "base_occurrences": len(base),
            "head_occurrences": len(head),
            **{key: len(comparison[key]) for key in ("introduced", "fixed", "moved", "location", "uncertain", "unchanged")},
        })
    return rows, repositories


def write_outputs(rows, repositories, output_dir):
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    with (output_dir / "paired-occurrences.csv").open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=PAIR_FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    repository_fields = (
        "project", "commit_sha", "status", "base_occurrences", "head_occurrences",
        "introduced", "fixed", "moved", "location", "uncertain", "unchanged",
        "provider_scope_status", "excluded_noncomparable_provider_occurrences",
    )
    with (output_dir / "repository-comparison.csv").open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=repository_fields)
        writer.writeheader()
        writer.writerows(repositories)
    review_rows = [row for row in rows if row["status"] != "unchanged"]
    with (output_dir / "paired-review-queue.csv").open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=PAIR_FIELDS)
        writer.writeheader()
        writer.writerows(review_rows)
    counts = Counter(row["status"] for row in rows)
    summary = {
        "schema_version": 1,
        "repositories_expected": len(repositories),
        "repositories_compared": sum(row["status"] == "compared" for row in repositories),
        "repositories_missing": sum(row["status"] != "compared" for row in repositories),
        "repositories_with_provider_scope_mismatch": sum(
            row.get("provider_scope_status")
            == "ansible-lint-excluded-scope-mismatch"
            for row in repositories
        ),
        "excluded_noncomparable_provider_occurrences": sum(
            int(row.get("excluded_noncomparable_provider_occurrences") or 0)
            for row in repositories
        ),
        "pair_status_counts": dict(sorted(counts.items())),
        "review_queue_items": len(review_rows),
        "concept_status_counts": {
            concept: dict(sorted(values.items()))
            for concept, values in sorted(
                (
                    concept,
                    Counter(row["status"] for row in rows if row["concept_id"] == concept),
                )
                for concept in {row["concept_id"] for row in rows}
            )
        },
    }
    (output_dir / "paired-summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return summary


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--base-root", required=True)
    parser.add_argument("--head-root", required=True)
    parser.add_argument("--old-labels")
    parser.add_argument("--output-dir", required=True)
    args = parser.parse_args(argv)
    rows, repositories = compare_roots(
        args.manifest, args.base_root, args.head_root, args.old_labels
    )
    summary = write_outputs(rows, repositories, args.output_dir)
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0 if summary["repositories_missing"] == 0 else 2


if __name__ == "__main__":
    raise SystemExit(main())
