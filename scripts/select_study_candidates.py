#!/usr/bin/env python3
"""Apply Selection Protocol v2 without deleting any discovered candidate."""

from __future__ import annotations

import argparse
import csv
from datetime import datetime, timedelta, timezone
from pathlib import Path


GATES = (
    ("unique_repository", "gate_unique_repository"),
    ("public", "gate_public"),
    ("not_disabled", "gate_not_disabled"),
    ("not_fork", "gate_not_fork"),
    ("not_archived", "gate_not_archived"),
    ("not_mirror", "gate_not_mirror"),
    ("not_template", "gate_not_template"),
    ("not_generated", "gate_not_generated"),
    ("last_commit_within_6_years", "gate_last_commit_within_6_years"),
    ("at_least_1000_commits", "gate_commits_ge_1000"),
    ("more_than_50_total_prs", "gate_total_prs_gt_50"),
    ("confirmed_production_ansible", "gate_confirmed_production_ansible"),
    ("at_least_50_merged_ansible_prs", "gate_merged_ansible_prs_ge_50"),
)
GATE_FIELDS = tuple(field for _, field in GATES)


def _state(condition):
    if condition is None:
        return "not-evaluated"
    return "true" if condition else "false"


def _bool_field(row, field, *, invert=False):
    value = str(row.get(field, "")).strip().lower()
    if value not in {"true", "false"}:
        return None
    result = value == "true"
    return not result if invert else result


def _not_template(row):
    """True unless the repository is a GitHub template repository.

    Prefers the raw `is_template` flag; falls back to the discovery
    stage's precomputed `pass_not_template`. Rows from sources that
    predate this field (or non-GitHub sources with no such concept)
    have neither -- those default to passing rather than
    not-evaluated, since "no template signal available" is not the
    same as "template status pending enrichment" and must not turn
    into a new pending gate that regresses every pre-existing row.
    """
    is_template = _bool_field(row, "is_template", invert=True)
    if is_template is not None:
        return is_template
    pass_field = _bool_field(row, "pass_not_template")
    return pass_field if pass_field is not None else True


def _not_generated(row):
    """True unless the repository matched the generated-repository heuristic."""
    match = _bool_field(row, "generated_repository_match", invert=True)
    if match is not None:
        return match
    pass_field = _bool_field(row, "pass_not_generated")
    return pass_field if pass_field is not None else True


def _integer(row, field):
    value = str(row.get(field, "")).strip()
    try:
        return int(value)
    except ValueError:
        return None


def _date(row):
    value = row.get("commit_date_utc") or row.get("pushed_at") or ""
    try:
        return datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except ValueError:
        return None


def _backfill_discovery_evidence(row):
    """Describe legacy discovery honestly without changing its selection result."""
    if not row.get("discovery_sources") and row.get("source_host"):
        row["discovery_sources"] = row["source_host"]
    query = str(row.get("discovery_query") or "").lower()
    if not row.get("discovery_methods") and query:
        methods = []
        if "topic:" in query:
            methods.append("github-topic-search")
        if "in:name,description,topics" in query:
            methods.append("github-metadata-text-search")
        row["discovery_methods"] = ";".join(methods or ["legacy-github-query"])
    if not row.get("discovery_coverage_scope") and query:
        prefiltered = "fork:false" in query or "archived:false" in query
        row["discovery_coverage_scope"] = (
            "historical-prefiltered-github-search"
            if prefiltered else "union-of-configured-github-searches"
        )
        row["discovery_coverage_warning"] = (
            "historical-query-cannot-reconstruct-prefilter-attrition"
            if prefiltered else
            "not-all-ansible-repositories;repositories-without-matching-topics-or-metadata-may-be-missed"
        )


def merge_rows(candidate_rows, frozen_rows=()):
    frozen = {row["project"]: row for row in frozen_rows if row.get("project")}
    merged = []
    for candidate in candidate_rows:
        row = dict(candidate)
        collected = frozen.get(row.get("project"))
        if collected:
            for key, value in collected.items():
                if value not in {None, ""}:
                    row[key] = value
        merged.append(row)
    return merged


def evaluate_rows(rows, as_of):
    seen = set()
    evaluated = []
    cutoff = as_of - timedelta(days=6 * 365)
    for source in rows:
        row = dict(source)
        _backfill_discovery_evidence(row)
        identity = str(row.get("repository_id") or row.get("project") or "").lower()
        unique = bool(identity) and identity not in seen
        seen.add(identity)
        last_commit = _date(row)
        production_files = _integer(row, "production_ansible_files")
        commits = _integer(row, "total_commits")
        total_prs = _integer(row, "total_prs")
        ansible_prs = _integer(row, "merged_ansible_changing_prs")
        private_present = str(row.get("private", "")).strip() != ""
        public_gate = (
            _bool_field(row, "private", invert=True)
            if private_present
            else _bool_field(row, "pass_public")
        )
        if public_gate is None and row.get("source_host") == "github":
            public_gate = True
        row.update(
            {
                "selection_protocol_version": "2",
                "selection_as_of_utc": as_of.isoformat(),
                "gate_unique_repository": _state(unique),
                "gate_public": _state(public_gate),
                "gate_not_disabled": _state(_bool_field(row, "disabled", invert=True)),
                "gate_not_fork": _state(_bool_field(row, "fork", invert=True)),
                "gate_not_archived": _state(_bool_field(row, "archived", invert=True)),
                "gate_not_mirror": _state(not bool(str(row.get("mirror_url", "")).strip())),
                "gate_not_template": _state(_not_template(row)),
                "gate_not_generated": _state(_not_generated(row)),
                "gate_last_commit_within_6_years": _state(last_commit >= cutoff if last_commit else None),
                "gate_confirmed_production_ansible": _state(production_files > 0 if production_files is not None else None),
                "gate_commits_ge_1000": _state(commits >= 1000 if commits is not None else None),
                "gate_total_prs_gt_50": _state(total_prs > 50 if total_prs is not None else None),
                "gate_merged_ansible_prs_ge_50": _state(ansible_prs >= 50 if ansible_prs is not None else None),
                "stars_used_for_selection": "false",
                "descriptive_evidence_used_for_selection": "false",
            }
        )
        evidence_groups = {
            "project_purpose": ("project_purpose_auto",),
            "independence": ("repository_owner", "repository_family", "ansible_content_fingerprint"),
            "ansible_significance": (
                "production_ansible_files", "production_ansible_loc",
                "repository_total_files", "production_ansible_repository_file_percent",
            ),
            "ansible_history": (
                "ansible_touching_commits", "first_ansible_commit_date_utc",
                "latest_ansible_commit_date_utc",
            ),
            "pr_audit": ("ansible_pr_scan_status", "merged_ansible_changing_prs"),
            "ansible_activity": ("latest_ansible_commit_date_utc",),
            "discovery_coverage": ("discovery_sources", "discovery_methods", "discovery_coverage_scope"),
        }
        missing_groups = []
        for group, fields in evidence_groups.items():
            values = [str(row.get(field, "")).strip() for field in fields]
            complete = all(value and value not in {"not-evaluated", "unknown"} for value in values)
            row[f"evidence_{group}_status"] = "recorded" if complete else "not-evaluated"
            if not complete:
                missing_groups.append(group)
        row["descriptive_evidence_status"] = "complete" if not missing_groups else "partial"
        row["descriptive_evidence_missing"] = ";".join(missing_groups)
        failures = [name for name, field in GATES if row[field] == "false"]
        pending = [name for name, field in GATES if row[field] == "not-evaluated"]
        row["all_exclusion_reasons"] = ";".join(failures)
        row["pending_evaluations"] = ";".join(pending)
        row["first_exclusion_stage"] = failures[0] if failures else ""
        row["final_eligible"] = (
            "false" if failures else "not-evaluated" if pending else "true"
        )
        metadata_fields = (
            "gate_public", "gate_not_disabled", "gate_not_fork",
            "gate_not_archived", "gate_not_mirror",
            "gate_not_template", "gate_not_generated",
            "gate_last_commit_within_6_years",
        )
        metadata_failures = [field.removeprefix("gate_") for field in metadata_fields if row[field] == "false"]
        metadata_pending = any(row[field] == "not-evaluated" for field in metadata_fields)
        row["metadata_eligible"] = (
            "false" if metadata_failures else "not-evaluated" if metadata_pending else "true"
        )
        row["metadata_exclusion_reasons_v2"] = ";".join(metadata_failures)
        cheap_fields = (
            "gate_unique_repository", "gate_public", "gate_not_disabled",
            "gate_not_fork", "gate_not_archived", "gate_not_mirror",
            "gate_not_template", "gate_not_generated",
            "gate_last_commit_within_6_years", "gate_total_prs_gt_50",
            "gate_commits_ge_1000",
        )
        row["screening_eligible"] = _state(
            all(row[field] == "true" for field in cheap_fields)
        )
        row["collect_for_screening"] = row["screening_eligible"]
        evaluated.append(row)
    return evaluated


def build_attrition(rows):
    original_total = len(rows)
    active = list(rows)
    report = []
    for position, (name, field) in enumerate(GATES, 1):
        passed = [row for row in active if row[field] == "true"]
        failed = [row for row in active if row[field] == "false"]
        pending = [row for row in active if row[field] == "not-evaluated"]
        report.append(
            {
                "stage": position,
                "criterion": name,
                "before": len(active),
                "removed": len(failed),
                "pending": len(pending),
                "remaining": len(passed),
                "removed_percent": round(100 * len(failed) / len(active), 2) if active else 0.0,
                "cumulative_removed_percent": (
                    round(100 * (original_total - len(passed)) / original_total, 2)
                    if original_total else 0.0
                ),
            }
        )
        active = passed
    return report


def apply_final_tie_breaker(rows):
    """Rank final_eligible repositories by stars, descending, as a pure ordering aid.

    Stars are never a gate and never affect final_eligible -- every other
    computation in this module is star-blind. This assigns
    `final_eligible_rank` only so a downstream manual step choosing a
    target-sized subset among otherwise-tied-eligible repositories has a
    deterministic, auditable tie-breaker instead of arbitrary CSV order.
    """
    eligible = [row for row in rows if row.get("final_eligible") == "true"]
    eligible.sort(key=lambda row: _integer(row, "stars") or 0, reverse=True)
    for rank, row in enumerate(eligible, 1):
        row["final_eligible_rank"] = rank
    for row in rows:
        row.setdefault("final_eligible_rank", "")
    return rows


def _passes_with(row, overrides):
    for _, field in GATES:
        state = overrides.get(field, row[field])
        if state != "true":
            return False
    return True


def build_sensitivity(rows, as_of):
    scenarios = []
    variations = {
        "last_commit_years": (4, 6, 8),
        "minimum_commits": (500, 1000, 1500, 2000),
        "minimum_total_prs_exclusive": (25, 50, 100),
        "minimum_merged_ansible_prs": (25, 50, 100),
    }
    for criterion, values in variations.items():
        for value in values:
            retained = 0
            possible = 0
            criterion_evaluated = 0
            criterion_passed = 0
            for row in rows:
                overrides = {}
                if criterion == "last_commit_years":
                    date = _date(row)
                    overrides["gate_last_commit_within_6_years"] = _state(
                        date >= as_of - timedelta(days=value * 365) if date else None
                    )
                elif criterion == "minimum_commits":
                    number = _integer(row, "total_commits")
                    overrides["gate_commits_ge_1000"] = _state(number >= value if number is not None else None)
                elif criterion == "minimum_total_prs_exclusive":
                    number = _integer(row, "total_prs")
                    overrides["gate_total_prs_gt_50"] = _state(number > value if number is not None else None)
                else:
                    number = _integer(row, "merged_ansible_changing_prs")
                    overrides["gate_merged_ansible_prs_ge_50"] = _state(number >= value if number is not None else None)
                retained += _passes_with(row, overrides)
                varied_state = next(iter(overrides.values()))
                criterion_evaluated += varied_state != "not-evaluated"
                criterion_passed += varied_state == "true"
                possible += all(
                    overrides.get(field, row[field]) != "false"
                    for _, field in GATES
                )
            scenarios.append(
                {
                    "criterion": criterion,
                    "value": value,
                    "repositories_retained": retained,
                    "repositories_possibly_retained_pending_evidence": possible,
                    "criterion_evaluated": criterion_evaluated,
                    "criterion_passed": criterion_passed,
                    "candidate_population": len(rows),
                    "retained_percent": round(100 * retained / len(rows), 2) if rows else 0.0,
                    "primary_value": "true" if value in {6, 1000, 50} else "false",
                }
            )
    return scenarios


def _read(path):
    if path is None:
        return []
    with Path(path).open(newline="", encoding="utf-8") as stream:
        return list(csv.DictReader(stream))


def _write(path, rows, fields=None):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    rows = list(rows)
    fields = fields or list(dict.fromkeys(key for row in rows for key in row))
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(
            stream, fieldnames=fields, extrasaction="ignore", lineterminator="\n"
        )
        writer.writeheader()
        writer.writerows(rows)


def main(argv=None):
    parser = argparse.ArgumentParser(description="Apply explainable Selection Protocol v2 gates.")
    parser.add_argument("candidates", type=Path, nargs="+")
    parser.add_argument("--frozen", type=Path, action="append")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--attrition-output", type=Path, required=True)
    parser.add_argument("--sensitivity-output", type=Path, required=True)
    parser.add_argument("--as-of", help="fixed UTC selection cutoff")
    args = parser.parse_args(argv)
    as_of = datetime.fromisoformat(args.as_of.replace("Z", "+00:00")) if args.as_of else datetime.now(timezone.utc)
    candidate_rows = [row for path in args.candidates for row in _read(path)]
    frozen_rows = [row for path in (args.frozen or []) for row in _read(path)]
    rows = evaluate_rows(merge_rows(candidate_rows, frozen_rows), as_of)
    apply_final_tie_breaker(rows)
    _write(args.output, rows)
    _write(args.attrition_output, build_attrition(rows))
    _write(args.sensitivity_output, build_sensitivity(rows, as_of))
    eligible = sum(row["final_eligible"] == "true" for row in rows)
    pending = sum(row["final_eligible"] == "not-evaluated" for row in rows)
    print(f"Wrote {len(rows)} candidates: eligible={eligible}, pending={pending}")


if __name__ == "__main__":
    main()
