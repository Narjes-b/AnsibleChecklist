#!/usr/bin/env python3
"""Build a frozen repository×metric-band manual-review sample."""

from __future__ import annotations

import argparse
from collections import defaultdict
import csv
import gzip
import hashlib
import json
from pathlib import Path

try:
    from scripts.build_threshold_benchmark import (
        OBSERVATION_FIELDS, SEED, _band, _review_file_has_content, _write_csv,
    )
except ModuleNotFoundError:  # Direct execution places scripts/ on sys.path.
    from build_threshold_benchmark import (
        OBSERVATION_FIELDS, SEED, _band, _review_file_has_content, _write_csv,
    )


LABEL_FIELDS = [
    "sample_stratum", "metric_band", "stratum_population",
    "inclusion_probability", "sampling_weight", "review_question",
    "context_start_line", "context_end_line", "source_total_lines",
    "context_complete", "context_strategy", "source_context",
    "reviewer_1_label", "reviewer_1_reason", "reviewer_2_label",
    "reviewer_2_reason", "initial_agreement", "adjudicated_label",
    "adjudication_reason", "ai_label", "ai_reason", "ai_prompt_version",
    "ai_model_version",
]


def _read_rows(path: Path):
    opener = gzip.open if path.suffix == ".gz" else path.open
    if path.suffix == ".gz":
        stream = opener(path, "rt", newline="", encoding="utf-8")
    else:
        stream = opener("r", newline="", encoding="utf-8")
    with stream:
        yield from csv.DictReader(stream)


def _repository_roots(path: Path) -> dict[str, Path]:
    with path.open(newline="", encoding="utf-8") as stream:
        return {
            row["project"]: Path(row["repository_path"])
            for row in csv.DictReader(stream)
        }


def _distribution(path: Path, metric_id: str) -> dict:
    with path.open(newline="", encoding="utf-8") as stream:
        for row in csv.DictReader(stream):
            if row["metric_id"] == metric_id:
                return row
    raise ValueError(f"metric not found in distribution summary: {metric_id}")


def _context(row: dict, roots: dict[str, Path], lines_after: int):
    path = roots[row["project"]] / row["path"]
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeError):
        return 0, 0, 0, False, "unavailable", ""
    line = max(1, int(row["line"]))
    total = len(lines)
    if row["unit"] == "file" and total > 400:
        ranges = [(1, 120), (max(1, total // 2 - 79), min(total, total // 2 + 80)), (max(1, total - 119), total)]
        chunks = []
        previous_end = 0
        for range_start, range_end in ranges:
            if range_start <= previous_end:
                range_start = previous_end + 1
            if range_start > range_end:
                continue
            if previous_end and range_start > previous_end + 1:
                chunks.append(f"     …: [{range_start - previous_end - 1} lines omitted]")
            chunks.extend(
                f"{number:>6}: {lines[number - 1]}"
                for number in range(range_start, range_end + 1)
            )
            previous_end = range_end
        return 1, total, total, False, "first-middle-last", "\n".join(chunks)
    if row["unit"] == "file":
        start, end, strategy = 1, total, "complete-file"
    else:
        start = max(1, line - 5)
        end = min(total, line + (160 if row["unit"] == "play" else lines_after))
        strategy = "play-window" if row["unit"] == "play" else "local-window"
    rendered = "\n".join(f"{number:>6}: {lines[number - 1]}" for number in range(start, end + 1))
    return start, end, total, start == 1 and end == total, strategy, rendered


def build_sample(
    observations: Path,
    distribution_summary: Path,
    repositories_manifest: Path,
    metric_id: str,
    question: str,
    context_lines: int,
):
    distribution = _distribution(distribution_summary, metric_id)
    q1 = float(distribution["q1"])
    median = float(distribution["median"])
    q3 = float(distribution["q3"])
    current = float(distribution["current_threshold"])
    metric_rows = [
        row for row in _read_rows(observations)
        if row["metric_id"] == metric_id
    ]
    population = len(metric_rows)
    current_count = sum(row["current_prediction"] == "true" for row in metric_rows)
    census_current_positives = 0 < current_count <= 200
    groups = defaultdict(list)
    census_rows = []
    for row in metric_rows:
        band = _band(
            float(row["value"]), q1, median, q3, current,
            distribution["comparator"],
        )
        if census_current_positives and row["current_prediction"] == "true":
            chosen = dict(row)
            chosen["metric_band"] = band
            census_rows.append(chosen)
        else:
            groups[(row["project"], band, row["current_prediction"])].append(row)

    roots = _repository_roots(repositories_manifest)
    selected = []
    for chosen in census_rows:
        start, end, total, complete, strategy, context = _context(chosen, roots, context_lines)
        chosen.update({
            "sample_stratum": f"{chosen['project']}|current-positive-census|{chosen['observation_id']}",
            "stratum_population": 1,
            "inclusion_probability": "1.0000000000",
            "sampling_weight": 1,
            "review_question": question,
            "context_start_line": start,
            "context_end_line": end,
            "source_total_lines": total,
            "context_complete": str(complete).lower(),
            "context_strategy": strategy,
            "source_context": context,
            "reviewer_1_label": "", "reviewer_1_reason": "",
            "reviewer_2_label": "", "reviewer_2_reason": "",
            "initial_agreement": "", "adjudicated_label": "",
            "adjudication_reason": "", "ai_label": "", "ai_reason": "",
            "ai_prompt_version": "", "ai_model_version": "",
        })
        selected.append(chosen)
    for (project, band, prediction), rows in sorted(groups.items()):
        ranked = sorted(
            rows,
            key=lambda row: hashlib.sha256(
                f"{SEED}\0{metric_id}\0{row['observation_id']}".encode()
            ).hexdigest(),
        )
        chosen = dict(ranked[0])
        start, end, total, complete, strategy, context = _context(chosen, roots, context_lines)
        chosen.update({
            "sample_stratum": f"{project}|{band}|current={prediction}",
            "metric_band": band,
            "stratum_population": len(rows),
            "inclusion_probability": f"{1 / len(rows):.10f}",
            "sampling_weight": len(rows),
            "review_question": question,
            "context_start_line": start,
            "context_end_line": end,
            "source_total_lines": total,
            "context_complete": str(complete).lower(),
            "context_strategy": strategy,
            "source_context": context,
            "reviewer_1_label": "",
            "reviewer_1_reason": "",
            "reviewer_2_label": "",
            "reviewer_2_reason": "",
            "initial_agreement": "",
            "adjudicated_label": "",
            "adjudication_reason": "",
            "ai_label": "",
            "ai_reason": "",
            "ai_prompt_version": "",
            "ai_model_version": "",
        })
        selected.append(chosen)
    return selected, population, distribution


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("metric_id")
    parser.add_argument("--question", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--context-lines", type=int, default=80)
    parser.add_argument(
        "--observations",
        default="study/threshold-benchmark-v007/observations.csv.gz",
    )
    parser.add_argument(
        "--distribution-summary",
        default="study/threshold-benchmark-v007/distribution-summary.csv",
    )
    parser.add_argument(
        "--repositories-manifest",
        default="study/runs/v007-207/input/repositories.csv",
    )
    args = parser.parse_args(argv)
    output = Path(args.output)
    output.mkdir(parents=True, exist_ok=True)
    selected, population, distribution = build_sample(
        Path(args.observations), Path(args.distribution_summary),
        Path(args.repositories_manifest), args.metric_id, args.question,
        args.context_lines,
    )
    fields = OBSERVATION_FIELDS + LABEL_FIELDS
    frozen = output / "review-sample.csv"
    working = output / "review-labels.csv"
    _write_csv(frozen, selected, fields)
    if not _review_file_has_content(working):
        _write_csv(working, selected, fields)

    manifest = {
        "schema_version": 1,
        "seed": SEED,
        "metric_id": args.metric_id,
        "population_observations": population,
        "sample_rows": len(selected),
        "sample_projects": len({row["project"] for row in selected}),
        "distribution": distribution,
        "review_sample_sha256": hashlib.sha256(frozen.read_bytes()).hexdigest(),
        "working_labels_are_mutable": True,
        "artifacts": {},
    }
    mutable = {
        "agreement-status.json", "review-labels.csv",
        "agreement-pilot-labels.csv", "agreement-pilot-status.json",
        "reviewer-disagreements.csv", "sample-manifest.json",
        "threshold-scores.csv", "human-ai-agreement.json",
    }
    for artifact in sorted(output.iterdir()):
        if artifact.is_file() and artifact.name not in mutable:
            manifest["artifacts"][artifact.name] = hashlib.sha256(
                artifact.read_bytes()
            ).hexdigest()
    (output / "sample-manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(manifest, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
