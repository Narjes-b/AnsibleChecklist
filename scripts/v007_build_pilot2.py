#!/usr/bin/env python3
"""Build the pilot-2 sample, v2 bundles and blank v2 reviewer forms from a finished run.

Uses CALIBRATION repositories only (frozen split), REQUIRED occurrences only, the frozen
rule-to-family map, and the pilot-2 selection rules (``v007_pilot2_selection``): no pilot-1 item
(matched by repository, rule, path and line), no vendored/bot/merge content, per-repository cap,
no sibling files. Bundles come from ``v007_bundle_context_v2`` and must pass
``v007_bundle_validate_v2`` (which includes the residual-secret scan) before anything is written
as final. The output directory must not exist (write-once).

Output: ``context/<sample_id>.md``, ``pilot2-master.csv`` (visible columns + selection metadata),
``reviewer-a/pilot2.csv`` and ``reviewer-b/pilot2.csv`` (blank v2 forms), ``pilot2-manifest.json``.
"""

from __future__ import annotations

import argparse
import csv
import gzip
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path
import subprocess
import sys

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.v007_bundle_context_v2 import review_context, static_context  # noqa: E402
from scripts.v007_bundle_validate_v2 import check_bundle  # noqa: E402
from scripts.v007_pilot2_selection import PER_FAMILY, is_non_ansible_yaml, select_pilot2  # noqa: E402
from scripts.v007_review_schema_v2 import v2_family_file  # noqa: E402
from scripts.v007_review_schema_v2 import V2_COLUMNS, build_blank  # noqa: E402
from scripts.v007_validation_pilot import (  # noqa: E402
    FAMILY_CODEBOOKS, FAMILY_QUESTIONS, REVIEW_MESSAGE_ONLY_RULE_IDS, REVIEW_RULE_IDS, REVIEWER_VISIBLE_COLUMNS,
)

SEED = "v007-pilot2-20261016"
IDENTITY = "v007-pilot2-v1"
MASTER_EXTRA = ["selection_rank_sha256", "source_occurrence_id", "is_pilot", "eligible_for_performance_scoring"]


def sha(*parts: str) -> str:
    return hashlib.sha256("|".join(parts).encode("utf-8")).hexdigest()


def read_csv(path: Path) -> list[dict[str, str]]:
    with open(path, newline="", encoding="utf-8") as stream:
        return list(csv.DictReader(stream))


def git(repo: Path, *args: str) -> str:
    result = subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True)
    return result.stdout.strip() if result.returncode == 0 else ""


def find_clone(roots: list[Path], repository: str) -> Path | None:
    for root in roots:
        candidate = root / repository
        if (candidate / ".git").exists() or (candidate / "HEAD").exists():
            return candidate
    return None


def snapshot_subjects(run_dir: Path, index_row: dict[str, str]) -> dict[tuple[str, str, str], str]:
    path = run_dir / index_row["canonical_occurrences"]
    opener = gzip.open if path.suffix == ".gz" else open
    with opener(path, "rt", encoding="utf-8") as stream:
        data = json.load(stream)
    items = data if isinstance(data, list) else data.get("items", [])
    return {(str(i.get("occurrence_id", "")), str(i.get("file", "")), str(i.get("line", ""))): str(i.get("semantic_subject") or "")
            for i in items if i.get("canonical_provider") == "ansibleguard"}


def load_candidates(run_dir: Path, validation_dir: Path, clone_roots: list[Path]):
    split = {r["repository"]: r for r in read_csv(validation_dir / "splits/repository-split.csv") if r["split"] == "calibration"}
    family_map = {r["rule_id"]: r for r in read_csv(validation_dir / "mappings/rule-family-map.csv")}
    index = {r["repository"]: r for r in read_csv(run_dir / "raw/raw-output-index.csv")}
    candidates, population = [], Counter()
    subjects_cache: dict[str, dict] = {}
    parents: dict[str, str] = {}
    meta_cache: dict[tuple[str, str], tuple[str, str]] = {}
    non_ansible_cache: dict[tuple[str, str, str], str] = {}
    for path_name, review in (("aggregate/all-internal-source-occurrences.csv", False), ("aggregate/all-review-occurrences.csv", True)):
        with open(run_dir / path_name, newline="", encoding="utf-8") as stream:
            for row in csv.DictReader(stream):
                repository, rule = row["project"], row["rule_id"]
                if repository not in split or row.get("policy") != "required" or rule not in family_map:
                    continue
                mapping = family_map[rule]
                if (mapping["panel"] == "review-history") != review or (review and rule not in REVIEW_RULE_IDS):
                    continue
                if row["commit_sha"] != split[repository]["commit_sha"]:
                    raise RuntimeError(f"run commit differs from the frozen split for {repository}")
                population[rule] += 1
                clone = find_clone(clone_roots, repository)
                if clone is None:
                    raise RuntimeError(f"no local clone for {repository}")
                family = mapping["family_id"]
                if review:
                    parent = parents.setdefault(repository, git(clone, "rev-parse", "--verify", f"{row['commit_sha']}^1"))
                    if not parent and rule not in REVIEW_MESSAGE_ONLY_RULE_IDS:
                        continue
                    if (repository, row["commit_sha"]) not in meta_cache:
                        meta_cache[(repository, row["commit_sha"])] = (
                            git(clone, "show", "-s", "--format=%an <%ae>", row["commit_sha"]),
                            "true" if len(git(clone, "show", "-s", "--format=%P", row["commit_sha"]).split()) > 1 else "false")
                    author, merge = meta_cache[(repository, row["commit_sha"])]
                    commit_subject = git(clone, "show", "-s", "--format=%s", row["commit_sha"])
                    subject, non_ansible, kind, ctx = "", "false", "git_commit", f"{repository}@{parent}..{row['commit_sha']}" if parent else f"{repository}@{row['commit_sha']}:commit-message"
                else:
                    if repository not in subjects_cache:
                        subjects_cache[repository] = snapshot_subjects(run_dir, index[repository])
                    subject = subjects_cache[repository].get((row["occurrence_id"], row["file"], row["line"]), "")
                    parent, author, merge, commit_subject = "", "", "false", ""
                    cache_key = (repository, row["commit_sha"], row["file"])
                    if cache_key not in non_ansible_cache:
                        blob = git(clone, "show", f"{row['commit_sha']}:{row['file']}")
                        non_ansible_cache[cache_key] = "true" if blob and is_non_ansible_yaml(row["file"], blob) else "false"
                    non_ansible = non_ansible_cache[cache_key]
                    kind = subject.split(":", 1)[0].strip() if ":" in subject else "source_location"
                    ctx = f"{repository}@{row['commit_sha']}:{row['file']}"
                occurrence_id = sha(IDENTITY, repository, row["commit_sha"], rule, row["occurrence_id"])
                candidates.append({
                    "occurrence_id": occurrence_id, "source_occurrence_id": row["occurrence_id"],
                    "selection_rank_sha256": sha(SEED, family, rule, occurrence_id), "repository": repository,
                    "commit_sha": row["commit_sha"], "rule_id": rule, "concept_id": row["concept_id"],
                    "panel": mapping["panel"], "family_id": family, "path": row["file"], "line_start": row["line"],
                    "line_end": row["line"], "object_kind": kind, "object_id": sha(IDENTITY, "object", repository, row["file"], row["line"], subject),
                    "semantic_subject": subject, "source_context_ref": ctx, "_parent_sha": parent, "_repo": str(clone),
                    "author": author, "is_merge": merge, "subject": commit_subject, "non_ansible_yaml": non_ansible,
                })
    return candidates, population, family_map


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--run-dir", type=Path, required=True)
    parser.add_argument("--validation-dir", type=Path, required=True)
    parser.add_argument("--pilot1-master", type=Path, required=True)
    parser.add_argument("--clone-root", type=Path, action="append", required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--per-family", type=int, default=PER_FAMILY)
    args = parser.parse_args()
    if args.output_dir.exists():
        raise SystemExit(f"refusing to write into existing {args.output_dir}")
    candidates, population, family_map = load_candidates(args.run_dir, args.validation_dir, args.clone_root)
    pilot1_keys = {(r["repository"], r["rule_id"], r["path"], r["line_start"]) for r in read_csv(args.pilot1_master)}
    pilot1_ids = {c["occurrence_id"] for c in candidates if (c["repository"], c["rule_id"], c["path"], c["line_start"]) in pilot1_keys}
    selected, excluded = select_pilot2(candidates, pilot1_ids, dict(population), args.per_family)
    out = args.output_dir
    (out / "context").mkdir(parents=True)
    master, problems, dropped = [], [], []
    for family in sorted(selected):
        number = 0
        for cand in selected[family]:
            sample_id = f"V007PILOT2-{family.upper()}-{number + 1:03d}"
            try:
                builder = review_context if family == "review_history" else static_context
                text, inline = builder({**cand, "sample_id": sample_id}, family, v2_family_file(FAMILY_CODEBOOKS[family]), Path(cand["_repo"]))
            except RuntimeError as error:
                dropped.append((cand["occurrence_id"], str(error)[:120]))
                continue
            found = check_bundle(text)
            if found:
                problems.append((sample_id, found))
            number += 1
            (out / "context" / f"{sample_id}.md").write_text(text, encoding="utf-8")
            master.append({
                "sample_id": sample_id, "occurrence_id": cand["occurrence_id"], "panel": cand["panel"], "rule_id": cand["rule_id"],
                "concept_id": cand["concept_id"], "review_family": family, "codebook_path": FAMILY_CODEBOOKS[family],
                "review_question": FAMILY_QUESTIONS[family], "repository": cand["repository"], "commit_sha": cand["commit_sha"],
                "path": cand["path"], "line_start": cand["line_start"], "line_end": cand["line_end"],
                "object_kind": cand["object_kind"], "object_id": cand["object_id"], "source_context": inline,
                "context_bundle_path": f"context/{sample_id}.md", "selection_rank_sha256": cand["selection_rank_sha256"],
                "source_occurrence_id": cand["source_occurrence_id"], "is_pilot": "true", "eligible_for_performance_scoring": "false",
            })
    for sample_id, found in problems:
        print(f"BUNDLE PROBLEM {sample_id}: {found}")
    columns = [*REVIEWER_VISIBLE_COLUMNS, *MASTER_EXTRA]
    with open(out / "pilot2-master.csv", "w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=columns, lineterminator="\n")
        writer.writeheader()
        writer.writerows(master)
    blanks = build_blank(master)
    for reviewer in ("reviewer-a", "reviewer-b"):
        (out / reviewer).mkdir()
        with open(out / reviewer / "pilot2.csv", "w", newline="", encoding="utf-8") as stream:
            writer = csv.DictWriter(stream, fieldnames=V2_COLUMNS, lineterminator="\n")
            writer.writeheader()
            writer.writerows(blanks)
    manifest = {
        "identity": IDENTITY, "seed": SEED, "run_dir": str(args.run_dir), "items": len(master),
        "per_family": dict(Counter(r["review_family"] for r in master)), "per_rule": dict(Counter(r["rule_id"] for r in master)),
        "exclusions": dict(excluded), "dropped_after_selection": dropped, "bundle_problems": len(problems),
        "pilot1_overlap_candidates_excluded": len(pilot1_ids),
        "sha256": {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in (out / "pilot2-master.csv", out / "reviewer-a/pilot2.csv")},
    }
    (out / "pilot2-manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({k: manifest[k] for k in ("items", "per_family", "exclusions", "bundle_problems", "dropped_after_selection")}, indent=1))
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
