#!/usr/bin/env python3
"""Validate returned V007 pilot labels and produce blinded agreement outputs.

The script never edits Reviewer A or B files. It refuses to overwrite existing
agreement or adjudication outputs and writes results only after both submitted
files pass schema, identity, evidence, and decision-field checks.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

import sys

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.v007_validation_pilot import (
    MASTER_COLUMNS,
    PILOT_CODEBOOK_INPUTS,
    REVIEWER_COLUMNS,
    REVIEWER_DECISION_COLUMNS,
    REVIEWER_VISIBLE_COLUMNS,
    _git,
    sha256_bytes,
    sha256_file,
)


SEMANTIC_LABELS = ("positive", "negative", "uncertain", "unreviewable")
ACTIONABILITY_LABELS = (
    "blocking", "actionable", "advisory", "not-actionable", "uncertain", "not-applicable"
)
YES_NO_UNCERTAIN = ("yes", "no", "uncertain")
AGREEMENT_FIELDS = {
    "semantic_label": SEMANTIC_LABELS,
    "actionability_label": ACTIONABILITY_LABELS,
    "context_sufficient": YES_NO_UNCERTAIN,
    "requires_external_context": YES_NO_UNCERTAIN,
}
DISAGREEMENT_FIELDS = tuple(
    column for column in REVIEWER_DECISION_COLUMNS if column not in {"evidence_notes", "reviewer_notes"}
)


class ReviewerInputError(ValueError):
    """A returned workbook violates the frozen pilot contract."""


def _read_table(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    try:
        with path.open("r", encoding="utf-8-sig", newline="") as stream:
            reader = csv.DictReader(stream)
            header = list(reader.fieldnames or [])
            if len(header) != len(set(header)):
                raise ReviewerInputError(f"duplicate column names in {path.name}")
            rows: list[dict[str, str]] = []
            for row_number, row in enumerate(reader, start=2):
                if None in row:
                    raise ReviewerInputError(f"extra CSV cells in {path.name} at row {row_number}")
                rows.append({key: value or "" for key, value in row.items() if key is not None})
            return header, rows
    except (OSError, UnicodeError, csv.Error) as error:
        raise ReviewerInputError(f"cannot read {path.name}: {error}") from error


def _reason_codes(validation_dir: Path, codebook_path: str) -> set[str]:
    path = validation_dir / codebook_path
    try:
        content = path.read_text(encoding="utf-8")
    except OSError as error:
        raise ReviewerInputError(f"missing family codebook {codebook_path}") from error
    match = re.search(r"^## Reason codes\s*$([\s\S]*?)(?=^## |\Z)", content, re.MULTILINE)
    if not match:
        raise ReviewerInputError(f"family codebook has no reason-code list: {codebook_path}")
    return set(re.findall(r"`([^`]+)`", match.group(1)))


def validate_reviewer_file(
    validation_dir: Path,
    master_rows: list[dict[str, str]],
    path: Path,
    reviewer_name: str,
) -> list[dict[str, str]]:
    header, rows = _read_table(path)
    if header != REVIEWER_COLUMNS:
        raise ReviewerInputError(f"{reviewer_name}: columns differ from the frozen reviewer schema")
    if len(rows) != len(master_rows):
        raise ReviewerInputError(
            f"{reviewer_name}: expected {len(master_rows)} rows, found {len(rows)}"
        )

    master_ids = [row.get("sample_id", "") for row in master_rows]
    returned_ids = [row.get("sample_id", "") for row in rows]
    if not all(master_ids) or len(master_ids) != len(set(master_ids)):
        raise ReviewerInputError("frozen master contains missing or duplicate sample IDs")
    if returned_ids != master_ids:
        raise ReviewerInputError(f"{reviewer_name}: sample IDs or row order differ from the master")

    reason_cache: dict[str, set[str]] = {}
    for position, (master, returned) in enumerate(zip(master_rows, rows), start=1):
        sample_id = master["sample_id"]
        for column in REVIEWER_VISIBLE_COLUMNS:
            if returned.get(column, "") != master.get(column, ""):
                raise ReviewerInputError(
                    f"{reviewer_name}: frozen evidence changed at row {position} ({sample_id})"
                )
        if any(not returned.get(column, "").strip() for column in REVIEWER_DECISION_COLUMNS[:6]):
            raise ReviewerInputError(f"{reviewer_name}: required decision missing at row {position} ({sample_id})")
        semantic = returned["semantic_label"].strip()
        actionability = returned["actionability_label"].strip()
        context_sufficient = returned["context_sufficient"].strip()
        external_needed = returned["requires_external_context"].strip()
        external_type = returned["external_context_type"].strip()
        if semantic not in SEMANTIC_LABELS:
            raise ReviewerInputError(f"{reviewer_name}: invalid semantic label at row {position} ({sample_id})")
        if actionability not in ACTIONABILITY_LABELS:
            raise ReviewerInputError(f"{reviewer_name}: invalid actionability label at row {position} ({sample_id})")
        if context_sufficient not in YES_NO_UNCERTAIN:
            raise ReviewerInputError(f"{reviewer_name}: invalid context_sufficient at row {position} ({sample_id})")
        if external_needed not in YES_NO_UNCERTAIN:
            raise ReviewerInputError(f"{reviewer_name}: invalid requires_external_context at row {position} ({sample_id})")
        if (semantic in {"negative", "unreviewable"}) != (actionability == "not-applicable"):
            raise ReviewerInputError(f"{reviewer_name}: actionability conflicts with semantic label at row {position} ({sample_id})")
        if external_needed == "no" and external_type != "none":
            raise ReviewerInputError(f"{reviewer_name}: external context type must be none at row {position} ({sample_id})")
        if external_needed == "yes" and (not external_type or external_type == "none"):
            raise ReviewerInputError(f"{reviewer_name}: required external context type is missing at row {position} ({sample_id})")
        if not returned.get("evidence_notes", "").strip():
            raise ReviewerInputError(f"{reviewer_name}: evidence note missing at row {position} ({sample_id})")
        if semantic in {"uncertain", "unreviewable"} and not returned.get("reviewer_notes", "").strip():
            raise ReviewerInputError(f"{reviewer_name}: uncertainty explanation missing at row {position} ({sample_id})")
        codebook = master.get("codebook_path", "")
        if codebook not in reason_cache:
            reason_cache[codebook] = _reason_codes(validation_dir, codebook)
        if returned.get("reason_code", "").strip() not in reason_cache[codebook]:
            raise ReviewerInputError(f"{reviewer_name}: invalid reason code at row {position} ({sample_id})")
    return rows


def _agreement_metrics(
    reviewer_a: list[str], reviewer_b: list[str], categories: Iterable[str]
) -> dict[str, Any]:
    labels = tuple(categories)
    if len(reviewer_a) != len(reviewer_b):
        raise ValueError("paired labels must have equal lengths")
    unknown = (set(reviewer_a) | set(reviewer_b)) - set(labels)
    if unknown:
        raise ValueError(f"labels outside the declared scale: {sorted(unknown)}")
    n = len(reviewer_a)
    if n == 0:
        raise ValueError("agreement is undefined for an empty pilot")

    matrix = {a: {b: 0 for b in labels} for a in labels}
    count_a = Counter(reviewer_a)
    count_b = Counter(reviewer_b)
    for a, b in zip(reviewer_a, reviewer_b):
        matrix[a][b] += 1
    observed = sum(matrix[label][label] for label in labels) / n
    chance_kappa = sum(count_a[label] * count_b[label] for label in labels) / (n * n)
    kappa = (observed - chance_kappa) / (1 - chance_kappa) if chance_kappa < 1 else None

    category_count = len(labels)
    average_prevalence = {
        label: (count_a[label] + count_b[label]) / (2 * n) for label in labels
    }
    chance_ac1 = (
        sum(p * (1 - p) for p in average_prevalence.values()) / (category_count - 1)
        if category_count > 1
        else 0.0
    )
    ac1 = (observed - chance_ac1) / (1 - chance_ac1) if chance_ac1 < 1 else None
    specific = {
        label: (
            2 * matrix[label][label] / (count_a[label] + count_b[label])
            if count_a[label] + count_b[label]
            else None
        )
        for label in labels
    }
    return {
        "n": n,
        "raw_agreement": observed,
        "cohens_kappa": kappa,
        "cohens_kappa_target_0_80_met": None if kappa is None else kappa >= 0.80,
        "gwets_ac1": ac1,
        "chance_agreement_cohen": chance_kappa,
        "chance_agreement_ac1": chance_ac1,
        "category_count": category_count,
        "prevalence": {
            label: {
                "reviewer_a_count": count_a[label],
                "reviewer_b_count": count_b[label],
                "reviewer_a_proportion": count_a[label] / n,
                "reviewer_b_proportion": count_b[label] / n,
                "mean_proportion": average_prevalence[label],
            }
            for label in labels
        },
        "category_specific_agreement": specific,
        "confusion_matrix_reviewer_a_rows_reviewer_b_columns": matrix,
    }


def compare_reviewers(
    validation_dir: Path,
    master_path: Path,
    reviewer_a_path: Path,
    reviewer_b_path: Path,
    output_dir: Path | None = None,
) -> dict[str, Any]:
    master_header, master_rows = _read_table(master_path)
    if master_header != MASTER_COLUMNS:
        raise ReviewerInputError("master columns differ from the frozen pilot schema")
    if not master_rows:
        raise ReviewerInputError("frozen pilot master is empty")
    if reviewer_a_path.resolve() == reviewer_b_path.resolve():
        raise ReviewerInputError("Reviewer A and B must be supplied as separate returned files")
    if any(row.get(column, "").strip() for row in master_rows for column in REVIEWER_DECISION_COLUMNS):
        raise ReviewerInputError("frozen pilot master must remain unlabeled")
    if any(row.get("eligible_for_performance_scoring") != "false" for row in master_rows):
        raise ReviewerInputError("pilot master contains a row eligible for performance scoring")

    manifest_path = validation_dir / "samples/agreement-pilot/agreement-pilot-manifest.json"
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        master_relative = master_path.resolve().relative_to(validation_dir.resolve()).as_posix()
        master_record = manifest.get("files", {}).get(master_relative, {})
    except (OSError, json.JSONDecodeError, ValueError) as error:
        raise ReviewerInputError("cannot verify the frozen pilot manifest/master") from error
    if (
        manifest.get("row_count") != len(master_rows)
        or manifest.get("eligible_for_performance_scoring") is not False
        or master_record.get("sha256") != sha256_file(master_path)
    ):
        raise ReviewerInputError("frozen master does not match its pilot manifest")
    current_codebook_hashes = {
        relative: sha256_file(validation_dir / relative)
        for relative in PILOT_CODEBOOK_INPUTS
    }
    codebook_bundle_hash = sha256_bytes(json.dumps(
        current_codebook_hashes, sort_keys=True, separators=(",", ":")
    ).encode("utf-8"))
    if (
        manifest.get("inputs", {}).get("pilot_codebooks_sha256") != current_codebook_hashes
        or manifest.get("inputs", {}).get("pilot_codebook_bundle_sha256") != codebook_bundle_hash
    ):
        raise ReviewerInputError("pilot codebooks or reviewer instructions changed after the pilot was frozen")

    rows_a = validate_reviewer_file(validation_dir, master_rows, reviewer_a_path, "Reviewer A")
    rows_b = validate_reviewer_file(validation_dir, master_rows, reviewer_b_path, "Reviewer B")
    fields: dict[str, Any] = {}
    for field, categories in AGREEMENT_FIELDS.items():
        a_values = [row[field].strip().lower() for row in rows_a]
        b_values = [row[field].strip().lower() for row in rows_b]
        fields[field] = _agreement_metrics(a_values, b_values, categories)

    disagreements = []
    for master, row_a, row_b in zip(master_rows, rows_a, rows_b):
        different = [field for field in DISAGREEMENT_FIELDS if row_a[field] != row_b[field]]
        if different:
            disagreements.append({
                "sample_id": master["sample_id"],
                "occurrence_id": master["occurrence_id"],
                "review_family": master["review_family"],
                "rule_id": master["rule_id"],
                "repository": master["repository"],
                "different_fields": ";".join(different),
                **{f"reviewer_a_{field}": row_a[field] for field in DISAGREEMENT_FIELDS},
                **{f"reviewer_b_{field}": row_b[field] for field in DISAGREEMENT_FIELDS},
            })

    report = {
        "schema_version": 1,
        "created_at_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "stage": "agreement-pilot",
        "pilot_master_sha256": sha256_file(master_path),
        "pilot_source_commit": manifest.get("source_commit"),
        "pilot_generator_commit": manifest.get("script_commit"),
        "pilot_generator_sha256": manifest.get("script_sha256"),
        "pilot_codebook_bundle_sha256": codebook_bundle_hash,
        "reviewer_a_sha256": sha256_file(reviewer_a_path),
        "reviewer_b_sha256": sha256_file(reviewer_b_path),
        "agreement_script_commit": _git(
            Path(__file__).resolve().parents[1], "rev-parse", "HEAD"
        ).stdout.strip(),
        "agreement_script_sha256": sha256_file(Path(__file__).resolve()),
        "row_count": len(master_rows),
        "semantic_agreement_target": "Cohen's kappa >= 0.80; interpret with AC1, prevalence, and category-specific agreement",
        "metric_definitions": {
            "cohens_kappa": "nominal, unweighted; chance agreement is the sum of the products of the two reviewers' category marginals",
            "gwets_ac1": "nominal AC1; the declared response scale fixes q, uses mean reviewer marginal prevalence p_k, and chance agreement sum(p_k * (1-p_k))/(q-1)",
            "category_specific_agreement": "2*n_kk/(n_k_reviewer_a+n_k_reviewer_b); undefined when neither reviewer uses category k",
            "citation": "Gwet, K. L. (2008). Computing inter-rater reliability and its variance in the presence of high agreement. British Journal of Mathematical and Statistical Psychology, 61, 29-48. https://doi.org/10.1348/000711006X126600",
        },
        "fields": fields,
        "semantic_label_disagreement_count": sum(
            1 for row in zip(rows_a, rows_b) if row[0]["semantic_label"] != row[1]["semantic_label"]
        ),
        "any_decision_disagreement_count": len(disagreements),
        "human_files_preserved_without_modification": True,
    }

    if output_dir is not None:
        summary_json = output_dir / "results/agreement-summary.json"
        summary_csv = output_dir / "results/agreement-summary.csv"
        disagreement_csv = output_dir / "adjudication/disagreements.csv"
        report_md = output_dir / "HUMAN_AGREEMENT_REPORT.md"
        destinations = (summary_json, summary_csv, disagreement_csv, report_md)
        existing = [str(path) for path in destinations if path.exists()]
        if existing:
            raise ReviewerInputError("refusing to overwrite existing outputs: " + ", ".join(existing))
        summary_json.parent.mkdir(parents=True, exist_ok=True)
        disagreement_csv.parent.mkdir(parents=True, exist_ok=True)
        summary_csv_rows = _summary_csv_rows(fields)
        report["outputs"] = {
            "agreement_summary_json": str(summary_json),
            "agreement_summary_csv": str(summary_csv),
            "disagreements_csv": str(disagreement_csv),
            "human_agreement_report": str(report_md),
        }
        _write_new_text(summary_json, json.dumps(report, indent=2, sort_keys=True) + "\n")
        _write_new_csv(summary_csv, summary_csv_rows, [
            "field", "metric", "category", "value", "reviewer_a_count", "reviewer_b_count"
        ])
        disagreement_columns = [
            "sample_id", "occurrence_id", "review_family", "rule_id", "repository", "different_fields",
            *[f"reviewer_a_{field}" for field in DISAGREEMENT_FIELDS],
            *[f"reviewer_b_{field}" for field in DISAGREEMENT_FIELDS],
        ]
        _write_new_csv(disagreement_csv, disagreements, disagreement_columns)
        _write_new_text(report_md, _markdown_report(report))
    return report


def _markdown_report(report: dict[str, Any]) -> str:
    semantic = report["fields"]["semantic_label"]
    lines = [
        "# V0.0.7 agreement-pilot human agreement report",
        "",
        f"Analysis time: `{report['created_at_utc']}`",
        "",
        "This report describes reviewer agreement on the calibration-only codebook pilot. It is not an estimate of detector precision, recall, or held-out performance.",
        "",
        f"- Paired items: **{report['row_count']}**",
        f"- Semantic-label disagreements: **{report['semantic_label_disagreement_count']}**",
        f"- Rows with any non-note decision disagreement: **{report['any_decision_disagreement_count']}**",
        f"- Cohen's kappa target (0.80) met: **{semantic['cohens_kappa_target_0_80_met']}**",
        "",
        "## Agreement coefficients",
        "",
        "| Field | Exact agreement | Cohen's kappa | Gwet's AC1 |",
        "|---|---:|---:|---:|",
    ]
    for field, metrics in report["fields"].items():
        lines.append(
            f"| {field} | {metrics['raw_agreement']:.4f} | "
            f"{_format_metric(metrics['cohens_kappa'])} | {_format_metric(metrics['gwets_ac1'])} |"
        )
    lines.extend([
        "",
        "## Semantic-label prevalence and category-specific agreement",
        "",
        "| Label | Reviewer A n (%) | Reviewer B n (%) | Specific agreement |",
        "|---|---:|---:|---:|",
    ])
    for label, values in semantic["prevalence"].items():
        specific = semantic["category_specific_agreement"][label]
        lines.append(
            f"| {label} | {values['reviewer_a_count']} ({values['reviewer_a_proportion']:.3f}) | "
            f"{values['reviewer_b_count']} ({values['reviewer_b_proportion']:.3f}) | {_format_metric(specific)} |"
        )
    lines.extend([
        "",
        "The full confusion matrices for the four categorical decision fields are in `results/agreement-summary.json`; the flattened coefficients/prevalence are in `results/agreement-summary.csv`. Disagreements are listed in `adjudication/disagreements.csv`. Adjudication remains a separate human step.",
        "",
        "## Interpretation",
        "",
        "Interpret kappa together with AC1, category prevalence, and label-specific agreement. If agreement is below the predeclared target or disagreement is systematic, revise the codebook using only this pilot and draw a new pilot; do not add pilot items to performance scoring.",
        "",
    ])
    return "\n".join(lines)


def _format_metric(value: float | None) -> str:
    return "not estimable" if value is None else f"{value:.4f}"


def _summary_csv_rows(fields: dict[str, Any]) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for field, metrics in fields.items():
        for metric in ("raw_agreement", "cohens_kappa", "gwets_ac1"):
            value = metrics[metric]
            rows.append({"field": field, "metric": metric, "category": "", "value": "" if value is None else str(value), "reviewer_a_count": "", "reviewer_b_count": ""})
        for category, details in metrics["prevalence"].items():
            rows.append({"field": field, "metric": "reviewer_a_prevalence", "category": category, "value": str(details["reviewer_a_proportion"]), "reviewer_a_count": str(details["reviewer_a_count"]), "reviewer_b_count": str(details["reviewer_b_count"])})
            rows.append({"field": field, "metric": "reviewer_b_prevalence", "category": category, "value": str(details["reviewer_b_proportion"]), "reviewer_a_count": str(details["reviewer_a_count"]), "reviewer_b_count": str(details["reviewer_b_count"])})
            specific = metrics["category_specific_agreement"][category]
            rows.append({"field": field, "metric": "category_specific_agreement", "category": category, "value": "" if specific is None else str(specific), "reviewer_a_count": str(details["reviewer_a_count"]), "reviewer_b_count": str(details["reviewer_b_count"])})
        for a, columns in metrics["confusion_matrix_reviewer_a_rows_reviewer_b_columns"].items():
            for b, count in columns.items():
                rows.append({"field": field, "metric": "confusion_count", "category": f"{a}|{b}", "value": str(count), "reviewer_a_count": "", "reviewer_b_count": ""})
    return rows


def _write_new_text(path: Path, content: str) -> None:
    with path.open("x", encoding="utf-8", newline="") as stream:
        stream.write(content)


def _write_new_csv(path: Path, rows: list[dict[str, str]], columns: list[str]) -> None:
    with path.open("x", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=columns, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--validation-dir", type=Path, default=Path("study/validation-v007-human"))
    parser.add_argument("--master", type=Path, help="defaults to the frozen agreement-pilot master")
    parser.add_argument("--reviewer-a", required=True, type=Path, help="separately returned Reviewer A CSV")
    parser.add_argument("--reviewer-b", required=True, type=Path, help="separately returned Reviewer B CSV")
    parser.add_argument("--output-dir", type=Path, help="defaults to --validation-dir; outputs are write-once")
    args = parser.parse_args()
    validation_dir = args.validation_dir.resolve()
    master_path = args.master or (validation_dir / "samples/agreement-pilot/agreement-pilot-master.csv")
    output_dir = args.output_dir.resolve() if args.output_dir else validation_dir
    try:
        report = compare_reviewers(
            validation_dir, master_path.resolve(), args.reviewer_a.resolve(), args.reviewer_b.resolve(), output_dir
        )
    except ReviewerInputError as error:
        parser.error(str(error))
    print(json.dumps({
        "row_count": report["row_count"],
        "semantic_label": {
            "raw_agreement": report["fields"]["semantic_label"]["raw_agreement"],
            "cohens_kappa": report["fields"]["semantic_label"]["cohens_kappa"],
            "gwets_ac1": report["fields"]["semantic_label"]["gwets_ac1"],
            "disagreements": report["semantic_label_disagreement_count"],
        },
        "outputs": report.get("outputs", {}),
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
