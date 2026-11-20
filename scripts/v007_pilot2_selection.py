#!/usr/bin/env python3
"""Pilot-2 item selection (plan v2, step 4) as a pure, testable function.

Input: candidate rows (the same dicts the pilot-1 builder produces: ``family_id``, ``rule_id``,
``repository``, ``path``, ``occurrence_id``, ``selection_rank_sha256``, optional ``author``,
``object_kind``) from CALIBRATION repositories only. Output: the selected rows per family.

Rules (plan v2 section 6 and the pilot-1 findings):
- never reuse a pilot-1 occurrence (memory effects);
- exclude vendored third-party content, bot-authored commits and merge commits;
- at most ``PER_REPOSITORY_CAP`` items per repository per family;
- at most one item per (repository, rule, directory) so sibling files are not near-duplicates;
- then the pilot-1 round-robin over rules with one-per-repository preference (``select_family``),
  then up to ``RARE_SLOTS`` reserved slots, one item per rare rule (population < 5).
Every exclusion is counted so the selection can be audited.
"""

from __future__ import annotations

from collections import Counter, defaultdict
from pathlib import PurePosixPath
import re
import sys
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.v007_validation_pilot import select_family  # noqa: E402

PER_FAMILY = 25
PER_REPOSITORY_CAP = 2
RARE_SLOTS = 3
VENDORED_DIR = re.compile(r"(^|/)(vendor|vendored|third[-_]party|external|node_modules)(/|$)", re.IGNORECASE)
GALAXY_ROLE_DIR = re.compile(r"(^|/)roles/[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+(/|$)")
BOT_AUTHOR = re.compile(r"\[bot\]|dependabot|renovate|github-actions|pre-commit-ci|\bbot@|-bot\b", re.IGNORECASE)


MERGE_SUBJECT = re.compile(r"^Merge (?:branch|pull request|remote-tracking|tag|commit|pr|changes|[\w./-]+ into )", re.IGNORECASE)
JSON_PATCH_KEYS = {"op", "path", "value", "from"}
NON_ANSIBLE_NAMES = {
    "kustomization.yaml", "kustomization.yml", "chart.yaml", "chart.yml", "values.yaml", "docker-compose.yml",
    "docker-compose.yaml", "compose.yml", "compose.yaml", ".gitlab-ci.yml", "mkdocs.yml", "mkdocs.yaml", "taskfile.yml",
    "taskfile.yaml", ".pre-commit-config.yaml", ".readthedocs.yml", ".readthedocs.yaml", "renovate.yaml",
}


def is_non_ansible_yaml(path: str, text: str) -> bool:
    """File names of other tools, Kubernetes manifests (apiVersion+kind) and JSON6902 patches (op/path/value lists)."""
    import yaml

    if PurePosixPath(path).name.lower() in NON_ANSIBLE_NAMES:
        return True
    try:
        documents = [d for d in yaml.safe_load_all(text) if d is not None]
    except yaml.YAMLError:
        return False
    for document in documents:
        if isinstance(document, dict) and "apiVersion" in document and "kind" in document:
            return True
        if isinstance(document, list) and document and all(isinstance(i, dict) and "op" in i and set(i) <= JSON_PATCH_KEYS for i in document):
            return True
    return False


def exclusion_reason(row: dict[str, str], pilot1_ids: set[str]) -> str | None:
    if row["occurrence_id"] in pilot1_ids:
        return "pilot-1 item"
    path = row.get("path", "")
    if VENDORED_DIR.search(path) or GALAXY_ROLE_DIR.search(path):
        return "vendored third-party content"
    if BOT_AUTHOR.search(row.get("author", "")):
        return "bot-authored commit"
    if row.get("object_kind") == "git_commit" and (
        row.get("is_merge", "").lower() in {"1", "true", "yes"} or MERGE_SUBJECT.match(row.get("subject", ""))
    ):
        return "merge commit"
    if row.get("non_ansible_yaml") == "true":
        return "non-Ansible YAML"
    return None


def select_pilot2(
    candidates: list[dict[str, str]],
    pilot1_ids: set[str],
    population_count_by_rule: dict[str, int],
    per_family: int = PER_FAMILY,
) -> tuple[dict[str, list[dict[str, str]]], Counter]:
    excluded: Counter = Counter()
    kept: dict[str, list[dict[str, str]]] = defaultdict(list)
    seen_directory: set[tuple[str, str, str]] = set()
    for row in sorted(candidates, key=lambda r: (r["selection_rank_sha256"], r["occurrence_id"])):
        reason = exclusion_reason(row, pilot1_ids)
        if reason:
            excluded[reason] += 1
            continue
        key = (row["repository"], row["rule_id"], str(PurePosixPath(row.get("path", "")).parent))
        if key in seen_directory:
            excluded["sibling of an earlier candidate"] += 1
            continue
        seen_directory.add(key)
        kept[row["family_id"]].append(row)
    selected: dict[str, list[dict[str, str]]] = {}
    for family, rows in kept.items():
        _, rare = select_family(rows, population_count_by_rule, per_family)
        # Rare rules (population < 5) are skipped by the round-robin, yet the codebook must be
        # exercised on them: reserve up to RARE_SLOTS items, one per rare rule.
        reserved = [next(row for row in rows if row["rule_id"] == rule) for rule in rare][:RARE_SLOTS]
        chosen, _ = select_family(rows, population_count_by_rule, per_family - len(reserved))
        chosen = chosen + reserved
        per_repo: Counter = Counter()
        final = []
        for row in chosen:
            if per_repo[row["repository"]] >= PER_REPOSITORY_CAP:
                excluded["repository cap"] += 1
                continue
            per_repo[row["repository"]] += 1
            final.append(row)
        selected[family] = final
    return selected, excluded
