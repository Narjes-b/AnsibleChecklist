#!/usr/bin/env python3
"""Split a complete candidate ledger by strong versus weak Ansible evidence."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


EXTRA_FIELDS = (
    "discovery_evidence_strength",
    "discovery_evidence_basis",
    "primary_enrichment_stratum",
)


def classify_evidence(row):
    queries = str(row.get("discovery_query") or "").split(";")
    sources = set(str(row.get("discovery_sources") or "").split(";"))
    if any(query.strip().startswith("topic:ansible") for query in queries):
        return "strong", "explicit-ansible-topic", "true"
    if "ansible-galaxy" in sources:
        return "strong", "ansible-galaxy-source", "true"
    if any("ansible in:name,description,topics" in query for query in queries):
        return "weak", "metadata-text-only", "false"
    return "unclassified", "no-recognized-ansible-discovery-evidence", "false"


def stratify(input_path, strong_path, weak_path, summary_path):
    counts = {
        "all_candidates": 0,
        "strong_candidates": 0,
        "weak_candidates": 0,
        "unclassified_candidates": 0,
        "strong_metadata_eligible": 0,
        "weak_metadata_eligible": 0,
    }
    with Path(input_path).open(newline="", encoding="utf-8") as source:
        reader = csv.DictReader(source)
        fields = list(reader.fieldnames or [])
        fields.extend(field for field in EXTRA_FIELDS if field not in fields)
        Path(strong_path).parent.mkdir(parents=True, exist_ok=True)
        Path(weak_path).parent.mkdir(parents=True, exist_ok=True)
        with (
            Path(strong_path).open("w", newline="", encoding="utf-8") as strong_stream,
            Path(weak_path).open("w", newline="", encoding="utf-8") as weak_stream,
        ):
            strong_writer = csv.DictWriter(strong_stream, fieldnames=fields, lineterminator="\n")
            weak_writer = csv.DictWriter(weak_stream, fieldnames=fields, lineterminator="\n")
            strong_writer.writeheader()
            weak_writer.writeheader()
            for row in reader:
                strength, basis, primary = classify_evidence(row)
                row.update({
                    "discovery_evidence_strength": strength,
                    "discovery_evidence_basis": basis,
                    "primary_enrichment_stratum": primary,
                })
                counts["all_candidates"] += 1
                if strength == "strong":
                    strong_writer.writerow(row)
                    counts["strong_candidates"] += 1
                    counts["strong_metadata_eligible"] += row.get("metadata_eligible") == "true"
                else:
                    weak_writer.writerow(row)
                    key = "weak_candidates" if strength == "weak" else "unclassified_candidates"
                    counts[key] += 1
                    if strength == "weak":
                        counts["weak_metadata_eligible"] += row.get("metadata_eligible") == "true"
    counts["strong_retained_percent"] = round(
        100 * counts["strong_candidates"] / counts["all_candidates"], 2
    ) if counts["all_candidates"] else 0.0
    summary = {
        "schema_version": 1,
        "criterion": "explicit Ansible topic or Ansible Galaxy source",
        "use": "primary enrichment stratum; weak rows remain preserved for sensitivity analysis",
        **counts,
    }
    Path(summary_path).parent.mkdir(parents=True, exist_ok=True)
    Path(summary_path).write_text(json.dumps(summary, indent=2), encoding="utf-8")
    return summary


def main(argv=None):
    parser = argparse.ArgumentParser(description="Stratify candidates by Ansible discovery evidence.")
    parser.add_argument("candidates", type=Path)
    parser.add_argument("--strong-output", required=True, type=Path)
    parser.add_argument("--weak-output", required=True, type=Path)
    parser.add_argument("--summary-output", required=True, type=Path)
    args = parser.parse_args(argv)
    summary = stratify(
        args.candidates, args.strong_output, args.weak_output, args.summary_output
    )
    print(
        f"Stratified {summary['all_candidates']} candidates: "
        f"strong={summary['strong_candidates']}, weak={summary['weak_candidates']}, "
        f"unclassified={summary['unclassified_candidates']}"
    )


if __name__ == "__main__":
    main()
