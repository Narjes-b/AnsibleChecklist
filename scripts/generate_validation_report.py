#!/usr/bin/env python3
"""
Generate a precision report CSV from a validation sample CSV.

Usage (from repo root):
    python scripts/generate_validation_report.py
"""

import csv
import math
import sys
from collections import defaultdict

INPUT_PATH = "study/validation-v6/sample.csv"
OUTPUT_PATH = "study/validation-v6/results_report.csv"

OUTPUT_COLUMNS = [
    "level",
    "name",
    "category",
    "provider",
    "n_sampled",
    "n_tp",
    "n_fp",
    "n_uncertain",
    "n_out_of_scope",
    "n_decidable",
    "precision_pct",
    "ci_lo_pct",
    "ci_hi_pct",
    "precision_tier",
    "fp_root_cause",
]

WILSON_Z = 1.96

# fp_root_cause text for low-precision rules.
# Keys are either full rule_id (provider/name) or just the name suffix.
FP_ROOT_CAUSES = {
    "undocumented-complex-task": (
        "Fires on any task with a Jinja expression regardless of complexity; "
        "threshold too permissive — needs AST-based complexity scoring"
    ),
    "plaintext-sensitive-variable": (
        "Cannot distinguish placeholder defaults (empty string, 'changeme', '{{ var }}') "
        "from real secrets; needs entropy check + SOPS/Vault/Jinja awareness"
    ),
    "incomplete-task": (
        "Fires on TODO/FIXME markers inside YAML comment lines (#) which are not active "
        "configuration; needs to gate on non-comment context"
    ),
    "incohesive-play": (
        "Cohesion detection relies on task-name pattern-matching, not semantic task grouping; "
        "produces near-random results"
    ),
    "incohesive-playbook": (
        "Same root cause as incohesive-play — cohesion metric is unreliable"
    ),
    "variable-use-before-definition": (
        "Ansible cross-file variable injection (set_fact in included tasks, group_vars, "
        "role defaults) is the norm; single-file analysis always FP"
    ),
    "broken-role-dependency": (
        "Likely Galaxy API lookup failure or missing collections in offline test env; "
        "all 5 sampled items were FP"
    ),
    "unused-include-vars": (
        "Requires cross-file analysis to confirm consumption; vars may be used in "
        "included tasks or role dependencies"
    ),
    "unscoped-shell-variable": (
        "PowerShell, csh/tcsh, and multi-line heredoc scripts are not distinguished from "
        "bash; shell-type detection needed"
    ),
    "duplicate-task-names": (
        "Fires on intentional conditional re-use patterns (same task name used under "
        "when: conditions) — needs to check when: clause presence"
    ),
    "shell-instead-of-module": (
        "Read-only query commands (hostname read, timedatectl query) have no module "
        "equivalents; needs read vs write command distinction"
    ),
    "invalid-task-attribute-type": (
        "environment: '{{ dict_var }}' is valid when the variable is a dict at runtime; "
        "cannot determine Jinja variable type statically"
    ),
    "gitleaks/kubernetes-secret-yaml": (
        "Regex too broad; matches non-secret base64 config values in ConfigMaps"
    ),
    "default-credentials": (
        "Cannot distinguish demo/documentation credentials from real deployments "
        "without deployment context"
    ),
    "unnecessary-abstraction": (
        "Heuristic too aggressive; what looks unnecessary to static analysis may serve "
        "testing or reuse purposes"
    ),
    "unnecessary-set-fact": (
        "Requires cross-file analysis to confirm variable is truly unused; "
        "include_tasks consumers are invisible to single-file analysis"
    ),
    "ansible-lint/command-instead-of-module": (
        "Read-only commands and platform-specific wrappers (timeout, strace) have no "
        "Ansible equivalents; needs read/write distinction"
    ),
    "gitleaks/generic-api-key": (
        "Generic high-entropy pattern matches SHA-1 hashes, GPG fingerprints, and "
        "other non-credential hex values"
    ),
    "insecure-permissions": (
        "Some mode values flagged are intentional (setgid for shared directories, "
        "world-readable for public assets)"
    ),
    "ansibleguard/read-only-command-change": (
        "changed_when not strictly required for read-only commands; "
        "some legitimate uses flagged"
    ),
    "silent-error-suppression": (
        "ignore_errors + register is a valid probe pattern; "
        "needs to check downstream register consumption"
    ),
    "high-coupling": (
        "Normal role entry-point dispatching pattern (main.yml with multiple "
        "import_tasks) is misidentified as high coupling"
    ),
}


def wilson_ci(n_tp: int, n_decidable: int) -> tuple[float, float]:
    """Return (ci_lo, ci_hi) Wilson score interval for precision."""
    z = WILSON_Z
    z2 = z * z
    p = n_tp / n_decidable
    n = n_decidable
    center = p + z2 / (2 * n)
    margin = z * math.sqrt(p * (1 - p) / n + z2 / (4 * n * n))
    denom = 1 + z2 / n
    ci_lo = max(0.0, (center - margin) / denom)
    ci_hi = min(1.0, (center + margin) / denom)
    return ci_lo, ci_hi


def assign_tier(n_decidable: int, precision: float | None) -> str:
    """Assign a precision tier label."""
    if n_decidable == 0 or precision is None:
        return "EXCLUDE"
    if n_decidable < 5:
        return "INSUFFICIENT_SAMPLE"
    if precision < 0.25:
        return "EXCLUDE"
    if precision < 0.50:
        return "CRITICAL"
    if precision < 0.75:
        return "NEEDS_IMPROVEMENT"
    if precision < 0.90:
        return "GOOD"
    return "EXCELLENT"


def lookup_fp_root_cause(rule_id: str) -> str:
    """Return fp_root_cause text for a rule_id, or empty string."""
    # Try full rule_id first, then the suffix after the last '/'
    if rule_id in FP_ROOT_CAUSES:
        return FP_ROOT_CAUSES[rule_id]
    suffix = rule_id.split("/")[-1]
    return FP_ROOT_CAUSES.get(suffix, "")


def extract_provider(rule_id: str) -> str:
    """Extract provider prefix from rule_id."""
    if "/" in rule_id:
        return rule_id.split("/")[0]
    return ""


def compute_stats(rows: list[dict]) -> dict:
    """Aggregate label counts and derived metrics from a list of rows."""
    n_sampled = len(rows)
    n_tp = sum(1 for r in rows if r["consensus_label"] == "true-positive")
    n_fp = sum(1 for r in rows if r["consensus_label"] == "false-positive")
    n_uncertain = sum(1 for r in rows if r["consensus_label"] == "uncertain")
    n_out_of_scope = sum(1 for r in rows if r["consensus_label"] == "out-of-scope")
    n_decidable = n_tp + n_fp

    if n_decidable > 0:
        precision = n_tp / n_decidable
        ci_lo, ci_hi = wilson_ci(n_tp, n_decidable)
        precision_pct = round(precision * 100, 1)
        ci_lo_pct = round(ci_lo * 100, 1)
        ci_hi_pct = round(ci_hi * 100, 1)
    else:
        precision = None
        precision_pct = ""
        ci_lo_pct = ""
        ci_hi_pct = ""

    tier = assign_tier(n_decidable, precision)

    return {
        "n_sampled": n_sampled,
        "n_tp": n_tp,
        "n_fp": n_fp,
        "n_uncertain": n_uncertain,
        "n_out_of_scope": n_out_of_scope,
        "n_decidable": n_decidable,
        "precision_pct": precision_pct,
        "ci_lo_pct": ci_lo_pct,
        "ci_hi_pct": ci_hi_pct,
        "precision_tier": tier,
        "_precision": precision,  # kept for tier re-use, stripped before output
    }


def build_report_row(
    level: str,
    name: str,
    category: str,
    provider: str,
    rows: list[dict],
    fp_root_cause: str = "",
) -> dict:
    stats = compute_stats(rows)
    stats.pop("_precision", None)
    return {
        "level": level,
        "name": name,
        "category": category,
        "provider": provider,
        **stats,
        "fp_root_cause": fp_root_cause,
    }


def main() -> None:
    # ------------------------------------------------------------------ load
    with open(INPUT_PATH, newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))

    print(f"Loaded {len(rows)} rows from {INPUT_PATH}", file=sys.stderr)

    # ------------------------------------------------------------------ slice helpers
    # Occurrence rows only (excludes clean-file-review) for category/rule roll-ups
    occ_rows = [r for r in rows if r["validation_unit"] == "occurrence"]
    # Positive-finding precision must never include clean-file negative-review
    # rows.  Mixing them produced the conflicting 73.4% vs 72.6% baselines.
    all_rows = occ_rows
    pc_rows = [
        r for r in occ_rows if r["paper_comparable_cohort"] == "true"
    ]

    # ------------------------------------------------------------------ overall rows
    report_rows: list[dict] = []

    report_rows.append(
        build_report_row("overall", "overall", "", "", all_rows)
    )
    report_rows.append(
        build_report_row(
            "overall_paper_comparable",
            "overall_paper_comparable",
            "",
            "",
            pc_rows,
        )
    )

    # ------------------------------------------------------------------ category rows
    cat_buckets: dict[str, list[dict]] = defaultdict(list)
    for r in occ_rows:
        cat = r["finding_category"]
        if cat and cat != "clean-file":
            cat_buckets[cat].append(r)

    category_report_rows = []
    for cat, cat_rows in cat_buckets.items():
        category_report_rows.append(
            build_report_row("category", cat, "", "", cat_rows)
        )

    # Sort categories by n_decidable descending
    category_report_rows.sort(key=lambda r: r["n_decidable"], reverse=True)
    report_rows.extend(category_report_rows)

    # ------------------------------------------------------------------ rule rows
    rule_buckets: dict[str, list[dict]] = defaultdict(list)
    for r in occ_rows:
        rid = r["rule_id"]
        if rid:
            rule_buckets[rid].append(r)

    # Determine finding_category per rule_id (all consistent, take first)
    rule_category: dict[str, str] = {}
    for r in occ_rows:
        rid = r["rule_id"]
        if rid and rid not in rule_category:
            rule_category[rid] = r["finding_category"]

    rule_report_rows = []
    for rid, rule_rows in rule_buckets.items():
        stats = compute_stats(rule_rows)
        tier = stats["precision_tier"]
        prec = stats.pop("_precision", None)

        # fp_root_cause only for EXCLUDE/CRITICAL tiers
        fp_rc = ""
        if tier in ("EXCLUDE", "CRITICAL"):
            fp_rc = lookup_fp_root_cause(rid)

        rule_report_rows.append(
            {
                "level": "rule",
                "name": rid,
                "category": rule_category.get(rid, ""),
                "provider": extract_provider(rid),
                **stats,
                "fp_root_cause": fp_rc,
            }
        )

    # Sort rules by n_decidable descending
    rule_report_rows.sort(key=lambda r: r["n_decidable"], reverse=True)
    report_rows.extend(rule_report_rows)

    # ------------------------------------------------------------------ write
    with open(OUTPUT_PATH, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=OUTPUT_COLUMNS)
        writer.writeheader()
        writer.writerows(report_rows)

    print(f"Wrote {len(report_rows)} rows to {OUTPUT_PATH}", file=sys.stderr)


if __name__ == "__main__":
    main()
