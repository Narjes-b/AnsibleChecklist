#!/usr/bin/env python3
"""Build a stratified random sample from the validation label ledger.

Produces study/validation/sample.csv — a reproducible, fixed-seed subset of
labels.csv that is balanced across concepts, categories, repositories, and
artifact kinds, and that keeps the mandatory separate strata for
`missing-tags` (optional-policy style) and `unguarded-variable` (all
confidence:low) so they do not distort the main precision estimate.

Usage
-----
    python scripts/build_stratified_sample.py \\
        study/validation/labels.csv \\
        --output study/validation/sample.csv \\
        [--seed 42] [--total 500]
"""

from __future__ import annotations

import argparse
import csv
import random
from collections import defaultdict
from pathlib import Path

# ---------------------------------------------------------------------------
# Allocation table
# ---------------------------------------------------------------------------
# (target_n, per_repo_cap)
# concept-level entries override category-level entries for the same rows.

CONCEPT_ALLOC: dict[str, tuple[int, int]] = {
    # ---------------------------------------------------------------------------
    # High-volume style/lint — capped hard to prevent single-rule/single-repo dominance
    # ---------------------------------------------------------------------------
    "ansible-lint-issue":             (200,  2),  # 36k pool; cap=2 keeps diversity
    "fqcn-migration":                 (150,  3),  # 27k pool; new in v0.0.3; 100% so far (6 items)
    "missing-tags":                   ( 30,  2),  # optional-policy stratum; mostly uncertain
    "unguarded-variable":             ( 10,  1),  # descriptive stratum only (99.6% not in repo)
    "yaml-truthy-value":              (100,  3),  # 4.7k pool; 100% precision so far
    "yaml-formatting":                (100,  3),  # 10.5k pool; 100% precision so far
    "long-yaml-line":                 ( 80,  3),  # 7.9k pool; 100% precision so far
    "long-task-name":                 ( 60,  3),  # 6.7k pool
    "unnamed-task":                   ( 80,  3),  # 9k pool; 80% precision (was 10 items)
    "unnamed-play":                   ( 60,  3),  # 985 pool; 100% so far (2 items)
    "loop-legacy-syntax":             ( 80,  3),  # 5.5k pool; new in v0.0.3; 100% so far (4 items)
    "duplicate-task-names":           ( 80,  3),  # 2.5k pool; 40% precision (was 15 items) — FP from non-Ansible YAML
    "unnecessary-set-fact":           ( 60,  3),  # 932 pool; 50% precision (was 10 items)
    "redirected-module":              ( 60,  3),  # 649 pool; 0 sampled before
    # ---------------------------------------------------------------------------
    # Security — headline claims for paper; need tight CIs
    # ---------------------------------------------------------------------------
    "credential-log-exposure":        (200,  5),  # 5.2k pool; 71% precision (was 67 items)
    "hardcoded-secret":               ( 90,  4),  # 103 pool; 30% precision — near-exhaust the pool
    "plaintext-sensitive-variable":   (100,  4),  # 798 pool; 10% precision — need many to confirm
    "missing-validate-certs":         ( 80,  4),  # 608 pool; 100% so far (10 items)
    "insecure-permissions":           (120,  5),  # 2.8k pool; 60% precision (was 38 items)
    "default-credentials":            ( 60,  4),  # 195 pool; 33% precision (was 4 items)
    "become-scope-too-broad":         ( 60,  3),  # 360 pool; new in v0.0.3; only 2 items before
    "unscoped-shell-variable":        ( 60,  3),  # 165 pool; 50% precision
    # ---------------------------------------------------------------------------
    # Correctness — second headline category
    # ---------------------------------------------------------------------------
    "invalid-task-attribute-type":    (100,  4),  # 544 pool; 40% precision (was 20) — runtime dict FP
    "non-idempotent-command":         (150,  4),  # 5k pool; 65% precision (was 40 items)
    "overriding-facts":               ( 60,  3),  # 88 pool; 62% precision (was 8 items)
    "variable-use-before-definition": ( 60,  3),  # 140 pool; 0 sampled before
    "unexpected-task-location":       ( 60,  3),  # 93 pool; 0% so far (2 items) — need more
    "inconsistent-naming-convention": ( 50,  3),  # 64 pool
    "role-variable-precedence-collision": (40, 3), # 55 pool
    "duplicate-mapping-key":          ( 12,  2),  # 14 pool — near-exhaust
    "missing-bool-filters":           ( 15,  2),  # 17 pool — near-exhaust
    "missing-handler":                (  3,  1),  # 3 pool
    "invalid-numeric-value":          (  5,  1),  # 5 pool
    "broken-role-dependency":         (  5,  1),  # 5 pool
    "unsafe-file-write":              (  3,  1),  # 3 pool
    # ---------------------------------------------------------------------------
    # Reliability
    # ---------------------------------------------------------------------------
    "unhandled-failure-suppression":  (120,  4),  # 2.9k pool; 76% precision (was 24 items)
    "read-only-command-change":       ( 60,  3),  # 747 pool; 83% so far (5 items)
    "unused-handler":                 ( 25,  3),  # 30 pool — near-exhaust
    # ---------------------------------------------------------------------------
    # Maintainability — largest category by volume
    # ---------------------------------------------------------------------------
    "large-task":                     (150,  3),  # 14k pool; 100% precision
    "complex-expression":             (100,  3),  # 11k pool; 100% precision
    "undocumented-complex-task":      (150,  3),  # 11.8k pool; 8% precision — need many to characterise
    "shell-module-migration":         ( 80,  3),  # 1.3k pool; 60% precision (was 15 items)
    "missing-abstraction":            ( 80,  3),  # 1.3k pool; 100% so far (11 items)
    "large-playbook":                 ( 80,  3),  # 2.6k pool; 100% so far
    "large-play":                     ( 60,  3),  # 1.2k pool; 100% so far
    "module-deprecation":             ( 60,  3),  # 1k pool; 0% from 1 item — need more
    "duplicated-code":                ( 60,  3),  # 531 pool; 100% so far (2 items)
    "high-coupling":                  ( 60,  3),  # 896 pool; 0% from 1 item — need more
    "unnecessary-abstraction":        ( 60,  3),  # 658 pool
    "incomplete-task":                ( 80,  3),  # 829 pool; 0% precision — characterise the FP pattern
    "unused-registered-variable":     ( 50,  3),  # 707 pool
    "unused-include-vars":            ( 40,  3),  # 46 pool — near-exhaust
    "redundant-default-value":        ( 18,  2),  # 20 pool — near-exhaust
    "excessive-nesting":              ( 16,  2),  # 18 pool — near-exhaust
    "missing-file-extension":         (  9,  2),  # 10 pool — near-exhaust
    "vault-inline-overload":          (  1,  1),  # 1 pool
    # ---------------------------------------------------------------------------
    # Structure / cohesion / compatibility
    # ---------------------------------------------------------------------------
    "complex-playbook":               ( 60,  3),  # 2.7k pool; 100% so far
    "incohesive-playbook":            ( 60,  3),  # 489 pool; was 3 items (all oos)
    "incohesive-play":                ( 50,  3),  # 418 pool
    "unstructured-module":            ( 50,  3),  # 361 pool
    "insufficient-modularization":    ( 60,  3),  # 85 pool
    "role-readme-absent":             ( 80,  3),  # 2.5k pool; new in v0.0.3
    "molecule-test-absent":           ( 60,  3),  # 1.7k pool; new in v0.0.3
    # ---------------------------------------------------------------------------
    # Dependencies
    # ---------------------------------------------------------------------------
    "unpinned-ansible-dependency":    ( 60,  3),  # 457 pool; 90% precision (was 10 items)
    # ---------------------------------------------------------------------------
    # Hardcoded-secret sub-pool exhausted above; no further concept entries needed
    # ---------------------------------------------------------------------------
}

CATEGORY_ALLOC: dict[str, tuple[int, int]] = {
    # Residual budget for any concepts not explicitly listed above.
    # Most rules are covered by CONCEPT_ALLOC; these catch the long tail.
    "security":        ( 50, 4),
    "correctness":     ( 50, 4),
    "reliability":     ( 30, 3),
    "maintainability": ( 50, 4),
    "documentation":   ( 30, 3),
    "structure":       ( 30, 3),
    "cohesion":        ( 20, 3),
    "compatibility":   ( 20, 3),
    "dependencies":    ( 20, 3),
    "testing":         ( 20, 2),
    "style":           ( 50, 3),
    "lint":            (  0, 0),  # fully handled by ansible-lint-issue above
}

NEGATIVE_TARGET: int = 120   # clean-file-review rows — scaled up with sample
NEGATIVE_PER_REPO_CAP: int = 3


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _read_csv(path: Path) -> list[dict]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def _cap_per_repo(rows: list[dict], cap: int) -> list[dict]:
    """Return rows with at most `cap` items per project."""
    counts: dict[str, int] = defaultdict(int)
    result = []
    for row in rows:
        project = row["project"]
        if counts[project] < cap:
            counts[project] += 1
            result.append(row)
    return result


def _sample(
    rng: random.Random, pool: list[dict], n: int, per_repo_cap: int,
    *, stratum: str, seed: int,
) -> list[dict]:
    """Shuffle, cap, sample, and retain reproducible inclusion evidence."""
    shuffled = pool.copy()
    rng.shuffle(shuffled)
    capped = _cap_per_repo(shuffled, per_repo_cap)
    probability = min(1.0, n / len(capped)) if capped else 0.0
    return [
        {
            **row,
            "sampling_stratum": stratum,
            "sampling_seed": seed,
            "inclusion_probability": f"{probability:.12g}",
            "stratum_population": len(capped),
        }
        for row in capped[:n]
    ]


# ---------------------------------------------------------------------------
# Main sampler
# ---------------------------------------------------------------------------

def build_sample(
    labels: list[dict],
    seed: int = 42,
    total: int = 500,
) -> list[dict]:
    rng = random.Random(seed)
    selected_ids: set[str] = set()
    result: list[dict] = []

    def _add(rows: list[dict]) -> None:
        for row in rows:
            uid = row.get("occurrence_id") or id(row)
            if uid not in selected_ids:
                selected_ids.add(str(uid))
                result.append(row)

    occurrences = [r for r in labels if r["validation_unit"] == "occurrence"]
    negatives   = [r for r in labels if r["validation_unit"] == "clean-file-review"]

    # 1. Concept-level overrides -------------------------------------------------
    concept_handled: set[str] = set()
    for concept_id, (target, repo_cap) in CONCEPT_ALLOC.items():
        if target == 0:
            concept_handled.add(concept_id)
            continue
        pool = [r for r in occurrences if r["concept_id"] == concept_id]
        _add(_sample(
            rng, pool, target, repo_cap,
            stratum=f"concept:{concept_id}", seed=seed,
        ))
        concept_handled.add(concept_id)

    # 2. Category-level allocation -----------------------------------------------
    for category, (target, repo_cap) in CATEGORY_ALLOC.items():
        if target == 0:
            continue
        pool = [
            r for r in occurrences
            if r["finding_category"] == category
            and r["concept_id"] not in concept_handled
        ]
        _add(_sample(
            rng, pool, target, repo_cap,
            stratum=f"category:{category}", seed=seed,
        ))

    # 3. Negative (clean-file-review) stratum ------------------------------------
    _add(_sample(
        rng, negatives, NEGATIVE_TARGET, NEGATIVE_PER_REPO_CAP,
        stratum="clean-file-review", seed=seed,
    ))

    # 4. Shuffle the final sample for presentation (hides allocation seams) ------
    rng.shuffle(result)

    print(
        f"Sample: {len(result)} items "
        f"({sum(1 for r in result if r['validation_unit'] == 'occurrence')} occurrences, "
        f"{sum(1 for r in result if r['validation_unit'] == 'clean-file-review')} clean-file-review)"
    )
    _print_breakdown(result)
    return result


def _print_breakdown(rows: list[dict]) -> None:
    from collections import Counter
    cat_counts = Counter(r["finding_category"] for r in rows)
    concept_counts = Counter(r["concept_id"] for r in rows)
    print("\n--- by finding_category ---")
    for cat, n in cat_counts.most_common():
        print(f"  {n:4d}  {cat}")
    print("\n--- top concepts ---")
    for concept, n in concept_counts.most_common(15):
        print(f"  {n:4d}  {concept or '(clean-file)'}")


def main(argv=None) -> None:
    parser = argparse.ArgumentParser(description="Build stratified validation sample.")
    parser.add_argument("labels_csv", type=Path)
    parser.add_argument("--output", type=Path, default=Path("study/validation/sample.csv"))
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--total", type=int, default=500,
                        help="Approximate total target (informational; actual total is "
                             "determined by the allocation table).")
    args = parser.parse_args(argv)

    labels = _read_csv(args.labels_csv)
    sample = build_sample(labels, seed=args.seed, total=args.total)
    _write_csv(args.output, sample)
    print(f"\nWrote {len(sample)} rows to {args.output}")


if __name__ == "__main__":
    main()
