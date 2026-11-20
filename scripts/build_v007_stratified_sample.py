#!/usr/bin/env python3
"""Build an impact-weighted, stratified sample of AnsibleGuard occurrences from the
v0.0.7 clean 127-repo corpus, replacing the earlier flat 50-per-family design.

Stratification: rules are ranked by total occurrence count across the clean corpus,
then bucketed into cumulative-share tiers (Pareto-style), so the sample reflects what
actually dominates the real dataset rather than giving every family equal weight.
Within each rule, allocation is sqrt(count)-weighted (dampens domination by the single
largest rule) with a floor of 1 and a cap per rule, to keep full-corpus coverage while
staying within a human-reviewable total.

Expects a local v007_full_repro.py reproduction checkout (see
study/runs/v007-full-repro-2026/README.md on the chore/v007-reproducible-full-run
branch) and the teammate study branch's rule-family-map.csv
(study/validation-v007-human/mappings/rule-family-map.csv on study/v007-human-validation).

Usage:
    python scripts/build_stratified_sample.py \\
        --repro-root ~/ansibleguard-v007-repro \\
        --family-map ~/ansibleguard-v007-repro/rule-family-map.csv \\
        --target-total 400 --per-rule-cap 22
"""
import argparse
import csv
import hashlib
import json
import math
from collections import defaultdict
from pathlib import Path


def parse_args():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--repro-root", type=Path, default=Path.home() / "ansibleguard-v007-repro",
                   help="root of the local v007 full-reproduction checkout (default: ~/ansibleguard-v007-repro)")
    p.add_argument("--run-id", default="v007-full-repro-2026", help="run id under study/runs and study/cache")
    p.add_argument("--family-map", type=Path, default=None,
                   help="path to rule-family-map.csv (default: <repro-root>/rule-family-map.csv)")
    p.add_argument("--out-dir", type=Path, default=None,
                   help="output directory (default: <repro-root>/stratified-sample)")
    p.add_argument("--target-total", type=int, default=400, help="target sample size before context-extraction losses")
    p.add_argument("--per-rule-cap", type=int, default=22, help="max rows allocated to any single rule")
    p.add_argument("--context-window", type=int, default=14, help="lines before/after the anchor line to include")
    return p.parse_args()


ARGS = parse_args()
RUN_DIR = ARGS.repro_root / "study" / "runs" / ARGS.run_id
CACHE_REPOS_DIR = ARGS.repro_root / "study" / "cache" / ARGS.run_id / "repositories"
REPOS_CSV = RUN_DIR / "input" / "repositories.csv"
FAMILY_MAP_CSV = ARGS.family_map or (ARGS.repro_root / "rule-family-map.csv")
OUT_DIR = ARGS.out_dir or (ARGS.repro_root / "stratified-sample")
TARGET_TOTAL = ARGS.target_total
PER_RULE_CAP = ARGS.per_rule_cap
CONTEXT_WINDOW = ARGS.context_window

OUT_DIR.mkdir(exist_ok=True, parents=True)


def load_family_map():
    m = {}
    with open(FAMILY_MAP_CSV, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            m[row["rule_id"]] = row
    return m


def load_repo_rows():
    with open(REPOS_CSV, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def iter_occurrences(repo_rows):
    for row in repo_rows:
        project = row["project"]
        sha = row["commit_sha"]
        repo_dir = RUN_DIR / "repositories" / project.replace("/", "__") / sha
        occ_path = repo_dir / "canonical" / "occurrences.json"
        if not occ_path.is_file():
            continue
        try:
            data = json.loads(occ_path.read_text(encoding="utf-8"))
        except Exception as e:
            print(f"WARN: failed to parse {occ_path}: {e}", file=sys.stderr)
            continue
        for item in data.get("items", []):
            native_rules = item.get("native_rules") or []
            rule_id = next((r for r in native_rules if r.startswith("ansibleguard/")), None)
            if not rule_id:
                continue
            yield {
                "rule_id": rule_id,
                "concept_id": item.get("concept_id", ""),
                "occurrence_id": item.get("occurrence_id", ""),
                "project": project,
                "commit_sha": sha,
                "file": item.get("file", ""),
                "line": item.get("line", 1),
                "severity": item.get("severity", ""),
                "message": item.get("message", ""),
                "source_root": CACHE_REPOS_DIR / project,
            }


def tier_for(cum_share):
    if cum_share <= 50:
        return "A-dominant"
    if cum_share <= 80:
        return "B-major"
    if cum_share <= 95:
        return "C-moderate"
    return "D-long-tail"


def extract_context(source_root: Path, file_rel: str, line: int):
    if not file_rel or file_rel == ".":
        return None
    candidate = source_root / file_rel
    if not candidate.is_file():
        return None
    try:
        lines = candidate.read_text(encoding="utf-8", errors="replace").splitlines()
    except Exception:
        return None
    if not lines:
        return None
    line = max(1, min(line, len(lines)))
    start = max(1, line - CONTEXT_WINDOW)
    end = min(len(lines), line + CONTEXT_WINDOW)
    out = []
    for n in range(start, end + 1):
        marker = ">>" if n == line else "  "
        out.append(f"{marker} {n:>5} | {lines[n - 1]}")
    return "\n".join(out)


def main():
    family_map = load_family_map()
    repo_rows = load_repo_rows()
    print(f"scanning {len(repo_rows)} repositories for canonical occurrences...")

    all_occ = list(iter_occurrences(repo_rows))
    print(f"total ansibleguard-native occurrences loaded: {len(all_occ)}")

    by_rule = defaultdict(list)
    for occ in all_occ:
        by_rule[occ["rule_id"]].append(occ)

    rule_counts = sorted(((r, len(v)) for r, v in by_rule.items()), key=lambda x: -x[1])
    total_count = sum(c for _, c in rule_counts)

    # cumulative share + tier assignment
    cum = 0.0
    rule_info = {}
    for rule_id, count in rule_counts:
        cum += 100.0 * count / total_count
        rule_info[rule_id] = {"count": count, "cum_share": cum, "tier": tier_for(cum)}

    # sqrt-weighted allocation normalized to TARGET_TOTAL, floor 1, cap PER_RULE_CAP
    weights = {r: math.sqrt(c) for r, c in rule_counts}
    weight_sum = sum(weights.values())
    raw_alloc = {r: max(1, round(TARGET_TOTAL * w / weight_sum)) for r, w in weights.items()}
    alloc = {r: min(PER_RULE_CAP, min(a, rule_info[r]["count"])) for r, a in raw_alloc.items()}

    print(f"rules with occurrences: {len(rule_counts)}; target total: {TARGET_TOTAL}; actual total after cap: {sum(alloc.values())}")

    selected_rows = []
    skipped_no_context = 0
    for rule_id, n in alloc.items():
        occs = by_rule[rule_id]
        # prefer one per distinct repo first: dedupe by project, keep first occurrence per repo
        by_repo = defaultdict(list)
        for occ in occs:
            by_repo[occ["project"]].append(occ)
        one_per_repo = [v[0] for v in by_repo.values()]
        pool = one_per_repo if len(one_per_repo) >= n else occs

        def rank_key(occ):
            h = hashlib.sha256(f"v007-stratified-v1|{rule_id}|{occ['occurrence_id']}".encode()).hexdigest()
            return h

        pool_sorted = sorted(pool, key=rank_key)
        taken = 0
        for occ in pool_sorted:
            if taken >= n:
                break
            ctx = extract_context(occ["source_root"], occ["file"], occ["line"])
            if ctx is None:
                skipped_no_context += 1
                continue
            fam = family_map.get(rule_id, {})
            selected_rows.append({
                "sample_id": f"V007STRAT-{rule_id.split('/')[-1].upper()}-{taken+1:03d}",
                "rule_id": rule_id,
                "concept_id": occ["concept_id"],
                "review_family": fam.get("family_name", "unmapped"),
                "tier": rule_info[rule_id]["tier"],
                "rule_total_occurrences": rule_info[rule_id]["count"],
                "rule_cumulative_share_percent": round(rule_info[rule_id]["cum_share"], 2),
                "repository": occ["project"],
                "commit_sha": occ["commit_sha"],
                "path": occ["file"],
                "line": occ["line"],
                "severity": occ["severity"],
                "message": occ["message"],
                "occurrence_id": occ["occurrence_id"],
                "source_context": ctx,
            })
            taken += 1

    print(f"selected rows: {len(selected_rows)}; skipped (no readable file context): {skipped_no_context}")

    fieldnames = ["sample_id", "rule_id", "concept_id", "review_family", "tier",
                  "rule_total_occurrences", "rule_cumulative_share_percent",
                  "repository", "commit_sha", "path", "line", "severity", "message",
                  "occurrence_id", "source_context"]
    out_csv = OUT_DIR / "stratified-sample.csv"
    with open(out_csv, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for row in selected_rows:
            w.writerow(row)
    print("wrote:", out_csv)

    # manifest documenting the design
    manifest = {
        "target_total": TARGET_TOTAL,
        "actual_total": len(selected_rows),
        "per_rule_cap": PER_RULE_CAP,
        "context_window_lines": CONTEXT_WINDOW,
        "total_occurrences_in_corpus": total_count,
        "rules_in_corpus": len(rule_counts),
        "tier_boundaries_cumulative_share_percent": {"A-dominant": "0-50", "B-major": "50-80", "C-moderate": "80-95", "D-long-tail": "95-100"},
        "per_rule": [
            {"rule_id": r, "count": c, "cum_share_percent": round(rule_info[r]["cum_share"], 2),
             "tier": rule_info[r]["tier"], "allocated": alloc[r],
             "family": family_map.get(r, {}).get("family_name", "unmapped")}
            for r, c in rule_counts
        ],
    }
    manifest_path = OUT_DIR / "stratified-sample-manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print("wrote:", manifest_path)


if __name__ == "__main__":
    main()
