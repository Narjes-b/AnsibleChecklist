#!/usr/bin/env python3
"""Create a complete project/file inventory and two-reviewer validation ledger."""

from __future__ import annotations

import argparse
from collections import Counter
import csv
import json
from pathlib import Path

try:
    from scripts.run_study_pilot import classification_manifest_path, output_path
except ModuleNotFoundError:  # direct ``python scripts/prepare_manual_validation.py``
    from run_study_pilot import classification_manifest_path, output_path


INVENTORY_FIELDS = (
    "project", "commit_sha", "path", "file_class", "document_type",
    "ansible_artifact_kind", "import_only", "primary_ansibleguard_cohort",
    "paper_comparable_cohort", "cohort_reason",
    "loc", "project_production_files", "project_size_quartile",
    "file_loc_quartile", "project_purpose_auto", "project_purpose_manual",
    "ecosystem_cluster", "repository_family", "independence_review_status",
    "canonical_occurrences", "analysis_status", "analysis_diagnostic",
    "eligible_for_clean_review", "clean_for_manual_review",
)
LABEL_FIELDS = (
    "project", "commit_sha", "path", "document_type", "loc",
    "ansible_artifact_kind", "import_only", "primary_ansibleguard_cohort",
    "paper_comparable_cohort", "cohort_reason",
    "project_size_quartile", "file_loc_quartile", "validation_unit",
    "project_purpose_auto", "project_purpose_manual", "ecosystem_cluster",
    "repository_family", "independence_review_status",
    "sample_stratum", "occurrence_id", "concept_id", "rule_id", "provider",
    "finding_category", "line", "severity", "confidence", "message",
    "auto_label", "auto_reason",
    "reviewer_1_label", "reviewer_1_reason", "reviewer_2_label",
    "reviewer_2_reason", "initial_agreement", "adjudicated_label",
    "adjudicated_reason", "consensus_label", "consensus_reason",
)
VALIDATION_LABELS = frozenset({
    "true-positive", "false-positive", "uncertain", "out-of-scope",
    "no-missed-finding", "false-negative",
})
REPOSITORY_EVIDENCE_FIELDS = (
    "project", "commit_sha", "project_purpose_auto",
    "project_purpose_auto_confidence", "project_purpose_evidence",
    "repository_owner", "repository_family", "ecosystem_cluster",
    "production_ansible_files", "production_ansible_loc",
    "production_ansible_repository_file_percent", "ansible_touching_commits",
    "first_ansible_commit_date_utc", "latest_ansible_commit_date_utc",
    "ansible_content_fingerprint", "exact_ansible_duplicate_group",
)
REPOSITORY_REVIEW_FIELDS = REPOSITORY_EVIDENCE_FIELDS + (
    "purpose_reviewer_1_category", "purpose_reviewer_1_reason",
    "purpose_reviewer_2_category", "purpose_reviewer_2_reason",
    "purpose_consensus_category", "purpose_consensus_reason",
    "independence_reviewer_1_status", "independence_reviewer_1_related_projects",
    "independence_reviewer_1_reason", "independence_reviewer_2_status",
    "independence_reviewer_2_related_projects", "independence_reviewer_2_reason",
    "independence_consensus_status", "independence_consensus_related_projects",
    "independence_consensus_reason",
)


def _read_csv(path):
    with Path(path).open(newline="", encoding="utf-8") as stream:
        return list(csv.DictReader(stream))


def _quartiles(values):
    ordered = sorted((value, index) for index, value in enumerate(values))
    result = {}
    size = len(ordered)
    for rank, (_, index) in enumerate(ordered):
        result[index] = min(4, (rank * 4 // size) + 1) if size else 1
    return result


def _occurrences(path):
    if not path.is_file():
        return []
    payload = json.loads(path.read_text(encoding="utf-8"))
    return payload.get("items", []) if isinstance(payload, dict) else payload


# parse_status values that mean semantic analysis was impossible — the file cannot
# serve as a clean negative review unit because we have no evidence it is clean.
_INELIGIBLE_PARSE_STATUSES = {"invalid", "unsupported"}


def _file_parse_statuses(snapshot_root):
    """Return {relative_path: (parse_status, diagnostic_message)} for every
    per-file report.json found under snapshot_root/files/."""
    result = {}
    files_dir = snapshot_root / "files"
    if not files_dir.is_dir():
        return result
    for report_path in files_dir.rglob("report.json"):
        try:
            data = json.loads(report_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        rel_path = data.get("file", "")
        if not rel_path:
            continue
        parse_status = data.get("parse_status", "")
        # Capture the first matching diagnostic message for this file if present.
        result[rel_path] = parse_status
    # Current output writes project diagnostics at the snapshot root; retain
    # the summary path for older output layouts. Internal analysis failures
    # make a file ineligible for clean-negative sampling even when parsing was
    # reported as successful.
    for diag_path in (
        snapshot_root / "diagnostics.json",
        snapshot_root / "summary" / "diagnostics.json",
    ):
        if not diag_path.is_file():
            continue
        try:
            payload = json.loads(diag_path.read_text(encoding="utf-8"))
            items = payload.get("items", payload) if isinstance(payload, dict) else payload
            for entry in items:
                rel_path = entry.get("file", "")
                if rel_path and rel_path != "." and entry.get("status") == "analysis-error":
                    result[rel_path] = "invalid"
        except (OSError, json.JSONDecodeError):
            continue
    return result


def build_ledgers(frozen_rows, classification_dir, snapshots_root, profile="technical-full"):
    projects = []
    for frozen in frozen_rows:
        if frozen.get("status") != "collected":
            continue
        project, sha = frozen["project"], frozen["commit_sha"]
        manifest = classification_manifest_path(classification_dir, project, sha)
        classified = [row for row in _read_csv(manifest) if row.get("included") == "true"]
        snapshot = output_path(snapshots_root, project, sha, profile)
        occurrences = _occurrences(snapshot / "canonical" / "occurrences.json")
        by_file = {}
        for occurrence in occurrences:
            by_file.setdefault(occurrence.get("file", ""), []).append(occurrence)
        parse_statuses = _file_parse_statuses(snapshot)
        projects.append((frozen, classified, by_file, parse_statuses))

    project_quartiles = _quartiles([len(classified) for _, classified, _, _ in projects])
    inventory = []
    labels = []
    for project_index, (frozen, classified, by_file, parse_statuses) in enumerate(projects):
        loc_values = [int(row.get("loc") or 0) for row in classified]
        loc_quartiles = _quartiles(loc_values)
        for file_index, row in enumerate(classified):
            path = row["path"]
            file_occurrences = by_file.get(path, [])
            parse_status = parse_statuses.get(path, "")
            analysis_failed = parse_status in _INELIGIBLE_PARSE_STATUSES
            # A file is eligible for clean-file review only when analysis
            # completed normally.  A file with parse_status=invalid or
            # parse_status=unsupported produced zero occurrences because
            # analysis was impossible, not because the file is defect-free.
            eligible_for_clean_review = not analysis_failed
            analysis_status = parse_status if parse_status else "analyzed"
            analysis_diagnostic = parse_status if analysis_failed else ""
            common = {
                "project": frozen["project"],
                "commit_sha": frozen["commit_sha"],
                "path": path,
                "document_type": row.get("document_type", ""),
                "ansible_artifact_kind": row.get("ansible_artifact_kind", ""),
                "import_only": row.get("import_only", ""),
                "primary_ansibleguard_cohort": row.get("primary_ansibleguard_cohort", ""),
                "paper_comparable_cohort": row.get("paper_comparable_cohort", ""),
                "cohort_reason": row.get("cohort_reason", ""),
                "loc": int(row.get("loc") or 0),
                "project_size_quartile": f"Q{project_quartiles[project_index]}",
                "file_loc_quartile": f"Q{loc_quartiles[file_index]}",
                "project_purpose_auto": frozen.get("project_purpose_auto", ""),
                "project_purpose_manual": frozen.get("project_purpose_manual", ""),
                "ecosystem_cluster": frozen.get("ecosystem_cluster", ""),
                "repository_family": frozen.get("repository_family", ""),
                "independence_review_status": frozen.get("independence_review_status", ""),
            }
            inventory.append(
                {
                    **common,
                    "file_class": row.get("file_class", ""),
                    "project_production_files": len(classified),
                    "canonical_occurrences": len(file_occurrences),
                    "analysis_status": analysis_status,
                    "analysis_diagnostic": analysis_diagnostic,
                    "eligible_for_clean_review": "true" if eligible_for_clean_review else "false",
                    "clean_for_manual_review": (
                        "true" if (not file_occurrences and eligible_for_clean_review)
                        else "false"
                    ),
                }
            )
            if analysis_failed:
                # Do not emit a clean-file-review label row for a file that
                # failed analysis; zero occurrences here is not evidence of
                # cleanliness.  Occurrence rows still appear if the canonical
                # index somehow contains matches (shouldn't happen, but safe).
                units = file_occurrences or []
            else:
                units = file_occurrences or [None]
            for occurrence in units:
                finding_category = (
                    occurrence.get("finding_category", "uncategorized")
                    if occurrence else "clean-file"
                )
                labels.append(
                    {
                        **common,
                        "validation_unit": "occurrence" if occurrence else "clean-file-review",
                        "sample_stratum": "|".join((
                            common["project_size_quartile"],
                            common["file_loc_quartile"],
                            common["ansible_artifact_kind"] or "unclassified",
                            finding_category,
                        )),
                        "occurrence_id": occurrence.get("occurrence_id", "") if occurrence else "",
                        "concept_id": occurrence.get("concept_id", "") if occurrence else "",
                        "rule_id": (occurrence.get("native_rules") or [""])[0] if occurrence else "",
                        "provider": occurrence.get("canonical_provider", "") if occurrence else "",
                        "finding_category": finding_category,
                        "line": occurrence.get("line", "") if occurrence else "",
                        "severity": occurrence.get("severity", "") if occurrence else "",
                        "confidence": occurrence.get("confidence", "") if occurrence else "",
                        "message": occurrence.get("message", "") if occurrence else "",
                        "auto_label": "",
                        "auto_reason": "",
                        "reviewer_1_label": "",
                        "reviewer_1_reason": "",
                        "reviewer_2_label": "",
                        "reviewer_2_reason": "",
                        "initial_agreement": "",
                        "adjudicated_label": "",
                        "adjudicated_reason": "",
                        "consensus_label": "",
                        "consensus_reason": "",
                    }
                )
    return inventory, labels


def summarize_validation(rows):
    """Validate completed labels and calculate transparent agreement metrics."""
    completed_pairs = []
    consensus = []
    errors = []
    for index, row in enumerate(rows, 2):
        first = row.get("reviewer_1_label", "").strip()
        second = row.get("reviewer_2_label", "").strip()
        final = (
            row.get("adjudicated_label", "").strip()
            or row.get("consensus_label", "").strip()
        )
        for field, value in (
            ("reviewer_1_label", first),
            ("reviewer_2_label", second),
            ("adjudicated_label", final),
        ):
            if value and value not in VALIDATION_LABELS:
                errors.append(f"row {index}: invalid {field}={value!r}")
        if bool(first) != bool(second):
            errors.append(f"row {index}: both independent reviewer labels are required together")
        if first and second:
            completed_pairs.append((first, second))
        if final:
            consensus.append((row.get("validation_unit", ""), final))
    if errors:
        raise ValueError("; ".join(errors))

    agreements = sum(first == second for first, second in completed_pairs)
    kappa = _cohens_kappa(completed_pairs)
    occurrence_consensus = [
        label for unit, label in consensus if unit == "occurrence"
    ]
    true_positive = occurrence_consensus.count("true-positive")
    false_positive = occurrence_consensus.count("false-positive")
    precision_denominator = true_positive + false_positive
    return {
        "schema_version": 1,
        "rows": len(rows),
        "independently_double_labeled": len(completed_pairs),
        "initial_agreements": agreements,
        "initial_percent_agreement": (
            agreements / len(completed_pairs) if completed_pairs else None
        ),
        "consensus_completed": len(consensus),
        "consensus_by_label": {
            label: sum(value == label for _, value in consensus)
            for label in sorted(VALIDATION_LABELS)
        },
        "occurrence_precision": (
            true_positive / precision_denominator if precision_denominator else None
        ),
        "false_negative_clean_file_reviews": sum(
            unit == "clean-file-review" and label == "false-negative"
            for unit, label in consensus
        ),
        "cohens_kappa": kappa,
        "interpretation": (
            "Chance-corrected agreement (Cohen's kappa) is reported alongside "
            "percent agreement; kappa is None when fewer than two independently "
            "double-labeled rows exist or when both reviewers used only one, "
            "identical category (chance agreement is then 100% and kappa is "
            "undefined rather than meaningfully perfect)."
        ),
    }


def _cohens_kappa(pairs):
    """Chance-corrected inter-rater agreement for two raters over a fixed label set.

    Standard two-rater kappa: (observed_agreement - chance_agreement) /
    (1 - chance_agreement), where chance_agreement is derived from each
    rater's own marginal label distribution (not a shared/assumed one) so it
    reflects how these two raters actually used the label set on this sample.
    """
    if not pairs:
        return None
    total = len(pairs)
    first_counts = Counter(first for first, _ in pairs)
    second_counts = Counter(second for _, second in pairs)
    observed_agreement = sum(first == second for first, second in pairs) / total
    labels = set(first_counts) | set(second_counts)
    chance_agreement = sum(
        (first_counts.get(label, 0) / total) * (second_counts.get(label, 0) / total)
        for label in labels
    )
    if chance_agreement >= 1:
        return None
    return (observed_agreement - chance_agreement) / (1 - chance_agreement)


def build_repository_reviews(frozen_rows):
    reviews = []
    for frozen in frozen_rows:
        if frozen.get("status") != "collected":
            continue
        reviews.append(
            {
                **{field: frozen.get(field, "") for field in REPOSITORY_EVIDENCE_FIELDS},
                **{
                    field: ""
                    for field in REPOSITORY_REVIEW_FIELDS
                    if field not in REPOSITORY_EVIDENCE_FIELDS
                },
            }
        )
    return reviews


def _write(path, fields, rows):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def main(argv=None):
    parser = argparse.ArgumentParser(description="Prepare full two-reviewer validation ledgers.")
    parser.add_argument("frozen_manifest", type=Path)
    parser.add_argument("--classification-dir", type=Path, required=True)
    parser.add_argument("--snapshots-root", type=Path, required=True)
    parser.add_argument("--inventory-output", type=Path, required=True)
    parser.add_argument("--labels-output", type=Path, required=True)
    parser.add_argument("--repository-review-output", type=Path)
    parser.add_argument("--profile", default="technical-full")
    args = parser.parse_args(argv)
    inventory, labels = build_ledgers(
        _read_csv(args.frozen_manifest), args.classification_dir,
        args.snapshots_root, args.profile,
    )
    _write(args.inventory_output, INVENTORY_FIELDS, inventory)
    _write(args.labels_output, LABEL_FIELDS, labels)
    reviews = build_repository_reviews(_read_csv(args.frozen_manifest))
    if args.repository_review_output:
        _write(args.repository_review_output, REPOSITORY_REVIEW_FIELDS, reviews)
    print(
        f"Wrote {len(inventory)} production-file inventory rows and "
        f"{len(labels)} independent-review units; "
        f"repository-review rows={len(reviews)}."
    )


if __name__ == "__main__":
    main()
