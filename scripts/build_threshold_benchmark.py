#!/usr/bin/env python3
"""Build a reproducible numerical-threshold benchmark over a frozen corpus.

This script deliberately separates three things that are often conflated:

1. descriptive distributions and candidate thresholds;
2. deterministic candidate-rate sensitivity;
3. precision/recall/F-score estimation, which requires independent labels.

It scans only files admitted by the frozen file-classification manifests.  A
single parsed document is reused by every extractor so the benchmark measures
the same source units as AnsibleGuard without reparsing each file per rule.
"""

from __future__ import annotations

import argparse
from collections import defaultdict
from contextlib import redirect_stdout
import csv
import gzip
import hashlib
import html
import io
import json
import math
from pathlib import Path
import re
import statistics
from typing import Iterable

from ansibleguard.detectors.detect_large_play import calculate_metrics_play
from ansibleguard.detectors.detect_large_playbook import calculate_metrics_playbook
from ansibleguard.detectors.high_coupling import high_coupling
from ansibleguard.detectors.large_task import calculate_metrics_task
from ansibleguard.detectors.paper_candidates import (
    JINJA_RE,
    NESTED_SECTIONS,
    TASK_SECTIONS,
    _BASE64_BLOB_RE,
    _ExpressionLocator,
    _URL_RE,
    _file_role_threshold_multiplier,
    _iter_tasks,
    _walk_values,
)
from ansibleguard.detectors.review_checklist import _has_preceding_comment, _task_line
from ansibleguard.detectors.sem_cohesion import calculate_similarity
from ansibleguard.detectors.source_lines import source_line
from ansibleguard.document import inspect_document


SEED = "v007-threshold-benchmark-20260917"

# The comparator matches the production detector.  The threshold is the
# current repository default, not a value inferred from this corpus.
METRICS = {
    "large_task_loc": ("large-task", "task", 15.0, ">"),
    "long_task_name_chars": ("long-task-name", "task", 75.0, ">"),
    "task_name_special_chars": ("inconsistent-naming-convention", "task", 3.0, ">"),
    "large_play_loc": ("large-play", "play", 50.0, ">"),
    "large_play_task_count": ("large-play", "play", 7.0, ">"),
    "large_play_avg_task_size": ("large-play", "play", 15.0, ">"),
    "large_playbook_loc": ("large-playbook", "file", 110.0, ">"),
    "large_playbook_play_count": ("large-playbook", "file", 4.0, ">"),
    "large_playbook_avg_play_size": ("large-playbook", "file", 50.0, ">"),
    "large_playbook_task_count": ("large-playbook", "file", 15.0, ">"),
    "large_playbook_avg_task_size": ("large-playbook", "file", 15.0, ">"),
    "high_coupling_import_count": ("high-coupling", "file", 4.0, ">"),
    "high_coupling_role_count": ("high-coupling", "file", 5.0, ">"),
    "complex_expression_score": ("complex-expression", "expression", 6.0, ">="),
    "complex_expression_length_chars": ("complex-expression", "expression", 100.0, ">"),
    "long_statement_chars": ("long-statement", "line", 160.0, ">"),
    "excessive_nesting_depth": ("excessive-nesting", "task", 3.0, ">"),
    "missing_abstraction_leaf_tasks": ("missing-abstraction", "file", 10.0, ">"),
    "undocumented_complex_boolean_ops": ("undocumented-complex-task", "task", 4.0, ">="),
    "undocumented_complex_jinja_filters": ("undocumented-complex-task", "task", 4.0, ">="),
    "undocumented_complex_nesting_depth": ("undocumented-complex-task", "task", 5.0, ">"),
    "play_name_special_chars": ("inconsistent-naming-convention", "task", 3.0, ">"),
    "cohesion_playbook_score": ("incohesive-playbook", "file", 0.4, "<"),
    "complex_playbook_budget": ("complex-playbook", "file", 2.0, ">"),
}

OBSERVATION_FIELDS = [
    "observation_id", "metric_id", "rule_id", "unit", "project", "commit_sha",
    "repository_size_quartile", "path", "document_type", "line", "name",
    "value", "current_threshold", "comparator", "eligible", "current_prediction",
    "threshold_multiplier", "has_existing_abstraction",
    "base_score", "boolean_ops", "jinja_filters", "nesting_depth",
    "has_preceding_comment", "source_ordinal",
    "play_loc", "play_task_count", "play_avg_task_size",
    "playbook_loc", "playbook_play_count", "playbook_avg_play_size",
    "playbook_task_count", "playbook_avg_task_size",
    "import_count", "role_count", "task_special_chars",
    "play_special_chars", "parent_play_name",
]

REVIEW_CONTENT_FIELDS = [
    "reviewer_1_label", "reviewer_1_reason", "reviewer_2_label",
    "reviewer_2_reason", "initial_agreement", "adjudicated_label",
    "adjudication_reason", "ai_label", "ai_reason", "ai_prompt_version",
    "ai_model_version",
]


def _truth(value: str) -> bool:
    return str(value).strip().lower() in {"1", "true", "yes", "y"}


def _float(value) -> float:
    return float(value or 0)


def _format_number(value: float) -> str:
    return str(int(value)) if float(value).is_integer() else f"{value:.4f}".rstrip("0").rstrip(".")


def _quantile(values: list[float], probability: float) -> float:
    """Inclusive linear quantile, equivalent to common box-plot quantiles."""
    if not values:
        return math.nan
    ordered = sorted(values)
    if len(ordered) == 1:
        return ordered[0]
    position = (len(ordered) - 1) * probability
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        return ordered[lower]
    fraction = position - lower
    return ordered[lower] + (ordered[upper] - ordered[lower]) * fraction


def _candidate_value(value: float) -> float:
    # Observations are persisted to four decimal places.  Candidate cutoffs
    # retain the same precision so rounding cannot move borderline cases.
    return round(value, 4)


def _prediction(row: dict, threshold: float) -> bool:
    if not _truth(row.get("eligible", "true")):
        return False
    value = _float(row["value"])
    if row["metric_id"].startswith("large_play_"):
        loc_threshold = threshold if row["metric_id"] == "large_play_loc" else 50
        task_threshold = threshold if row["metric_id"] == "large_play_task_count" else 7
        avg_threshold = threshold if row["metric_id"] == "large_play_avg_task_size" else 15
        return (
            _float(row.get("play_loc")) > loc_threshold
            or _float(row.get("play_task_count")) > task_threshold
            or _float(row.get("play_avg_task_size")) > avg_threshold
        )
    if row["metric_id"] in {
        "large_playbook_loc", "large_playbook_play_count",
        "large_playbook_avg_play_size", "large_playbook_task_count",
    }:
        loc_threshold = threshold if row["metric_id"] == "large_playbook_loc" else 110
        play_threshold = threshold if row["metric_id"] == "large_playbook_play_count" else 4
        avg_play_threshold = threshold if row["metric_id"] == "large_playbook_avg_play_size" else 50
        task_threshold = threshold if row["metric_id"] == "large_playbook_task_count" else 15
        return (
            _float(row.get("playbook_loc")) > loc_threshold
            or _float(row.get("playbook_play_count")) > play_threshold
            or _float(row.get("playbook_avg_play_size")) > avg_play_threshold
            or _float(row.get("playbook_task_count")) > task_threshold
        )
    if row["metric_id"].startswith("high_coupling_"):
        import_threshold = threshold if row["metric_id"].endswith("import_count") else 4
        role_threshold = threshold if row["metric_id"].endswith("role_count") else 5
        return (
            _float(row.get("import_count")) > import_threshold
            or _float(row.get("role_count")) > role_threshold
        )
    if row["metric_id"] == "task_name_special_chars":
        return value > threshold or _float(row.get("play_special_chars")) > 3
    if row["metric_id"] == "play_name_special_chars":
        return _float(row.get("task_special_chars")) > 3 or value > threshold
    if row["metric_id"] == "complex_expression_length_chars":
        return _float(row.get("base_score")) + (2 if value > threshold else 0) >= 6
    if row["metric_id"].startswith("undocumented_complex_"):
        if _truth(row.get("has_preceding_comment", "false")):
            return False
        boolean_threshold = threshold if row["metric_id"].endswith("boolean_ops") else 4
        filter_threshold = threshold if row["metric_id"].endswith("jinja_filters") else 4
        nesting_threshold = threshold if row["metric_id"].endswith("nesting_depth") else 5
        return (
            _float(row.get("boolean_ops")) >= boolean_threshold
            or _float(row.get("jinja_filters")) >= filter_threshold
            or _float(row.get("nesting_depth")) > nesting_threshold
        )
    if row["metric_id"] == "missing_abstraction_leaf_tasks":
        if _truth(row.get("has_existing_abstraction", "false")):
            return False
        multiplier = _float(row.get("threshold_multiplier") or 1)
        effective = max(3, int(threshold * multiplier))
        return value > effective
    if row["comparator"] == ">=":
        return value >= threshold
    if row["comparator"] == "<":
        return value < threshold
    return value > threshold


def _observation(
    metric_id: str,
    project: str,
    commit_sha: str,
    size_quartile: str,
    relative_path: str,
    document_type: str,
    line,
    name,
    value,
    *,
    eligible=True,
    threshold_multiplier=1.0,
    has_existing_abstraction=False,
    base_score="",
    boolean_ops="",
    jinja_filters="",
    nesting_depth="",
    has_preceding_comment=False,
    identity_suffix="",
    source_ordinal="",
    play_loc="",
    play_task_count="",
    play_avg_task_size="",
    playbook_loc="",
    playbook_play_count="",
    playbook_avg_play_size="",
    playbook_task_count="",
    playbook_avg_task_size="",
    import_count="",
    role_count="",
    task_special_chars="",
    play_special_chars="",
    parent_play_name="",
) -> dict:
    rule_id, unit, current, comparator = METRICS[metric_id]
    identity = "\0".join(
        [metric_id, project, commit_sha, relative_path, str(line or 1),
         str(name or ""), str(value), str(identity_suffix)]
    )
    row = {
        "observation_id": hashlib.sha256(identity.encode()).hexdigest(),
        "metric_id": metric_id,
        "rule_id": rule_id,
        "unit": unit,
        "project": project,
        "commit_sha": commit_sha,
        "repository_size_quartile": size_quartile,
        "path": relative_path,
        "document_type": document_type,
        "line": line or 1,
        "name": str(name or ""),
        "value": _format_number(float(value)),
        "current_threshold": _format_number(current),
        "comparator": comparator,
        "eligible": str(bool(eligible)).lower(),
        "current_prediction": "",
        "threshold_multiplier": _format_number(float(threshold_multiplier)),
        "has_existing_abstraction": str(bool(has_existing_abstraction)).lower(),
        "base_score": base_score,
        "boolean_ops": boolean_ops,
        "jinja_filters": jinja_filters,
        "nesting_depth": nesting_depth,
        "has_preceding_comment": str(bool(has_preceding_comment)).lower(),
        "source_ordinal": source_ordinal,
        "play_loc": play_loc,
        "play_task_count": play_task_count,
        "play_avg_task_size": play_avg_task_size,
        "playbook_loc": playbook_loc,
        "playbook_play_count": playbook_play_count,
        "playbook_avg_play_size": playbook_avg_play_size,
        "playbook_task_count": playbook_task_count,
        "playbook_avg_task_size": playbook_avg_task_size,
        "import_count": import_count,
        "role_count": role_count,
        "task_special_chars": task_special_chars,
        "play_special_chars": play_special_chars,
        "parent_play_name": parent_play_name,
    }
    row["current_prediction"] = str(_prediction(row, current)).lower()
    return row


def _expression_rows(document, text: str):
    locator = _ExpressionLocator(text)
    seen = set()
    for key, value in _walk_values(document):
        candidates = JINJA_RE.findall(value)
        if key in {"when", "changed_when", "failed_when", "until"}:
            candidates.append(value)
        for expression in candidates:
            normalized = expression.strip()
            if not normalized or normalized in seen:
                continue
            seen.add(normalized)
            base_score = (
                len(re.findall(r"\b(?:and|or|not|in|is)\b", normalized))
                + len(re.findall(r"==|!=|>=|<=|>|<", normalized))
                + normalized.count("|")
                + normalized.count("(")
                + normalized.count("[")
                + normalized.count("?")
            )
            score = base_score
            if len(normalized) > 100:
                score += 2
            yield locator.line_for(normalized), normalized[:160], score, base_score, len(normalized)


def _file_observations(repo: dict, manifest_row: dict) -> tuple[list[dict], str | None]:
    root = Path(repo["repository_path"])
    relative = manifest_row["path"]
    path = root / relative
    parsed = inspect_document(path)
    if parsed.parse_status != "parsed":
        return [], parsed.parse_status

    project = repo["project"]
    commit = repo["commit_sha"]
    size_quartile = repo.get("project_size_quartile", "")
    document_type = manifest_row.get("document_type") or parsed.document_type
    rows: list[dict] = []

    # Several legacy metric functions print "not a playbook" for valid task,
    # vars, and metadata documents.  Those messages are diagnostic noise, not
    # scan failures, so capture them while preserving raised exceptions.
    with redirect_stdout(io.StringIO()):
        task_metrics, _ = calculate_metrics_task(path, parsed_document=parsed)
        play_metrics = calculate_metrics_play(path, parsed_document=parsed) or {"Plays": []}
    plays = play_metrics.get("Plays", [])
    play_by_id = {play.get("play_id", index): play for index, play in enumerate(plays)}
    for index, task in enumerate(task_metrics):
        parent_play = play_by_id.get(task.get("play_id"), {})
        task_special = task.get("special_chars", 0)
        play_special = parent_play.get("special_chars", 0)
        common = (project, commit, size_quartile, relative, document_type, task.get("line"), task.get("task_name") or f"task-{index}")
        identity = {"identity_suffix": f"task:{index}", "source_ordinal": index}
        naming = {
            **identity,
            "task_special_chars": task_special,
            "play_special_chars": play_special,
            "parent_play_name": parent_play.get("Play_name", ""),
        }
        rows.append(_observation("large_task_loc", *common, task.get("LOC_task", 0), **identity))
        rows.append(_observation("long_task_name_chars", *common, task.get("task_name_len", 0), **identity))
        rows.append(_observation("task_name_special_chars", *common, task_special, **naming))
        # Production propagates a play-name violation to every task in that
        # play, so the experimental unit here must also be the task.
        rows.append(_observation("play_name_special_chars", *common, play_special, **naming))

    for index, play in enumerate(plays):
        common = (project, commit, size_quartile, relative, document_type, play.get("line"), play.get("Play_name") or f"play-{index}")
        evidence = {
            "identity_suffix": f"play:{index}", "source_ordinal": index,
            "play_loc": play.get("LOC_play", 0),
            "play_task_count": play.get("num_tasks_in_play", 0),
            "play_avg_task_size": play.get("avg_task_play", 0),
        }
        rows.append(_observation("large_play_loc", *common, play.get("LOC_play", 0), **evidence))
        rows.append(_observation("large_play_task_count", *common, play.get("num_tasks_in_play", 0), **evidence))
        rows.append(_observation("large_play_avg_task_size", *common, play.get("avg_task_play", 0), **evidence))

    with redirect_stdout(io.StringIO()):
        playbook = calculate_metrics_playbook(path, parsed_document=parsed) or {}
    production_file_unit = document_type in {"playbook", "tasks", "handlers"}
    if playbook and production_file_unit:
        common = (project, commit, size_quartile, relative, document_type, 1, relative)
        playbook_evidence = {
            "playbook_loc": playbook.get("LOC_playbook", 0),
            "playbook_play_count": playbook.get("num_plays", 0),
            "playbook_avg_play_size": playbook.get("avg_play_size", 0),
            "playbook_task_count": playbook.get("num_nested_tasks_playbook", 0),
            "playbook_avg_task_size": playbook.get("avg_nested_task_playbook", 0),
        }
        rows.append(_observation("large_playbook_loc", *common, playbook.get("LOC_playbook", 0), **playbook_evidence))
        rows.append(_observation("large_playbook_play_count", *common, playbook.get("num_plays", 0), **playbook_evidence))
        rows.append(_observation("large_playbook_avg_play_size", *common, playbook.get("avg_play_size", 0), **playbook_evidence))
        rows.append(_observation("large_playbook_task_count", *common, playbook.get("num_nested_tasks_playbook", 0), **playbook_evidence))
        # This accepted legacy threshold is not part of the production OR.
        rows.append(_observation("large_playbook_avg_task_size", *common, playbook.get("avg_nested_task_playbook", 0), **playbook_evidence))

    with redirect_stdout(io.StringIO()):
        coupling = high_coupling(path, parsed_document=parsed)
    if coupling is not None and production_file_unit:
        common = (project, commit, size_quartile, relative, document_type, 1, relative)
        coupling_evidence = {
            "import_count": coupling.get("Num_Imports", 0),
            "role_count": coupling.get("Num_Roles", 0),
        }
        rows.append(_observation("high_coupling_import_count", *common, coupling.get("Num_Imports", 0), **coupling_evidence))
        rows.append(_observation("high_coupling_role_count", *common, coupling.get("Num_Roles", 0), **coupling_evidence))

    if playbook and production_file_unit:
        coupling_values = coupling or {}
        budget = (
            playbook.get("LOC_playbook", 0) / 110
            + playbook.get("num_plays", 0) / 4
            + playbook.get("num_nested_tasks_playbook", 0) / 15
            + coupling_values.get("Num_Imports", 0) / 4
            + coupling_values.get("Num_Roles", 0) / 5
        )
        rows.append(_observation(
            "complex_playbook_budget", project, commit, size_quartile, relative,
            document_type, 1, relative, budget,
            playbook_loc=playbook.get("LOC_playbook", 0),
            playbook_play_count=playbook.get("num_plays", 0),
            playbook_task_count=playbook.get("num_nested_tasks_playbook", 0),
            import_count=coupling_values.get("Num_Imports", 0),
            role_count=coupling_values.get("Num_Roles", 0),
        ))

    cohesion = calculate_similarity(path, parsed_document=parsed)
    if cohesion is not None:
        rows.append(_observation(
            "cohesion_playbook_score", project, commit, size_quartile, relative,
            document_type, 1, relative, cohesion,
        ))

    for expression_index, (line, expression, score, base_score, expression_length) in enumerate(
        _expression_rows(parsed.document, parsed.source_text)
    ):
        identity = {"identity_suffix": f"expression:{expression_index}", "source_ordinal": expression_index}
        rows.append(_observation(
            "complex_expression_score", project, commit, size_quartile, relative,
            document_type, line, expression, score, **identity,
        ))
        rows.append(_observation(
            "complex_expression_length_chars", project, commit, size_quartile,
            relative, document_type, line, expression, expression_length,
            base_score=base_score, **identity,
        ))

    for line_number, source in enumerate(parsed.source_text.splitlines(), 1):
        if not source.strip() or source.lstrip().startswith("#"):
            continue
        stripped = source.strip()
        if _URL_RE.search(stripped) or _BASE64_BLOB_RE.match(stripped):
            continue
        rows.append(_observation(
            "long_statement_chars", project, commit, size_quartile, relative,
            document_type, line_number, stripped[:160], len(source.expandtabs(2)),
        ))

    tasks = list(_iter_tasks(parsed.document))
    source_lines = parsed.source_text.splitlines()
    for index, (task, depth) in enumerate(tasks):
        task_line = source_line(task, fallback=1)
        rows.append(_observation(
            "excessive_nesting_depth", project, commit, size_quartile, relative,
            document_type, task_line, task.get("name", f"task-{index}"), depth,
            identity_suffix=f"nested-task:{index}", source_ordinal=index,
        ))
        condition = task.get("when", "")
        if isinstance(condition, list):
            condition = " and ".join(str(item) for item in condition)
        condition = str(condition)
        boolean_ops = len(re.findall(r"\b(?:and|or)\b", condition, re.IGNORECASE))
        jinja_filters = len(re.findall(r"\|\s*[A-Za-z_]\w*", condition))
        # Use the same source-aware task locator as production.
        undocumented_line = _task_line(parsed.source_text, task)
        documented = _has_preceding_comment(source_lines, undocumented_line)
        evidence = {
            "boolean_ops": boolean_ops,
            "jinja_filters": jinja_filters,
            "nesting_depth": depth,
            "has_preceding_comment": documented,
            "identity_suffix": f"nested-task:{index}",
            "source_ordinal": index,
        }
        common = (
            project, commit, size_quartile, relative, document_type,
            undocumented_line,
            task.get("name", f"task-{index}"),
        )
        rows.append(_observation(
            "undocumented_complex_boolean_ops", *common, boolean_ops, **evidence,
        ))
        rows.append(_observation(
            "undocumented_complex_jinja_filters", *common, jinja_filters, **evidence,
        ))
        rows.append(_observation(
            "undocumented_complex_nesting_depth", *common, depth, **evidence,
        ))

    if document_type in {"playbook", "tasks", "handlers"}:
        leaf_tasks = [
            task for task, _ in tasks
            if not any(section in task for section in NESTED_SECTIONS)
        ]
        abstraction_keys = {
            "include_tasks", "import_tasks", "include_role", "import_role",
            "ansible.builtin.include_tasks", "ansible.builtin.import_tasks",
            "ansible.builtin.include_role", "ansible.builtin.import_role",
        }
        has_abstraction = any(abstraction_keys.intersection(task) for task, _ in tasks)
        if isinstance(parsed.document, list):
            has_abstraction = has_abstraction or any(
                isinstance(entry, dict) and bool(entry.get("roles"))
                for entry in parsed.document
            )
        multiplier = _file_role_threshold_multiplier(path)
        rows.append(_observation(
            "missing_abstraction_leaf_tasks", project, commit, size_quartile,
            relative, document_type, 1, relative, len(leaf_tasks),
            # Files that already use an abstraction remain part of the rule's
            # target population, but are deterministic negatives at every
            # leaf-task threshold.
            eligible=True,
            threshold_multiplier=multiplier,
            has_existing_abstraction=has_abstraction,
        ))
    return rows, None


def _repositories(manifest: Path) -> list[dict]:
    with manifest.open(newline="", encoding="utf-8") as stream:
        rows = list(csv.DictReader(stream))
    sizes = sorted(int(float(row.get("production_ansible_files") or 0)) for row in rows)
    q1, q2, q3 = (_quantile(sizes, probability) for probability in (0.25, 0.5, 0.75))
    for row in rows:
        size = int(float(row.get("production_ansible_files") or 0))
        row["project_size_quartile"] = "Q1" if size <= q1 else "Q2" if size <= q2 else "Q3" if size <= q3 else "Q4"
    return rows


def _classified_files(repo: dict) -> list[dict]:
    manifest = Path(repo["classification_manifest"])
    with manifest.open(newline="", encoding="utf-8") as stream:
        selected = {}
        for row in csv.DictReader(stream):
            if _truth(row.get("included")) and row.get("parse_status") == "parsed":
                selected.setdefault(row["path"], row)
        return list(selected.values())


def _write_csv(path: Path, rows: Iterable[dict], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.suffix == ".gz":
        stream_context = gzip.open(path, mode="wt", newline="", encoding="utf-8")
    else:
        stream_context = path.open(mode="w", newline="", encoding="utf-8")
    with stream_context as stream:
        writer = csv.DictWriter(stream, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def _read_csv(path: Path) -> list[dict]:
    if path.suffix == ".gz":
        stream_context = gzip.open(path, mode="rt", newline="", encoding="utf-8")
    else:
        stream_context = path.open(mode="r", newline="", encoding="utf-8")
    with stream_context as stream:
        return list(csv.DictReader(stream))


def _review_file_has_content(path: Path) -> bool:
    """Protect real review work while allowing blank templates to refresh."""
    if not path.exists():
        return False
    return any(
        str(row.get(field, "")).strip()
        for row in _read_csv(path)
        for field in REVIEW_CONTENT_FIELDS
    )


def _candidate_rows(observations: list[dict]) -> tuple[list[dict], dict[str, list[float]]]:
    grouped: dict[str, list[dict]] = defaultdict(list)
    for row in observations:
        if _truth(row["eligible"]):
            grouped[row["metric_id"]].append(row)
    output = []
    candidate_map = {}
    for metric_id in METRICS:
        rows = grouped.get(metric_id, [])
        values = [_float(row["value"]) for row in rows]
        if not values:
            continue
        q1 = _quantile(values, 0.25)
        q2 = _quantile(values, 0.50)
        q3 = _quantile(values, 0.75)
        if METRICS[metric_id][3] == "<":
            # A Tukey fence is descriptive and may fall outside the metric's
            # attainable domain (for example, a negative similarity score).
            # Clamp it to the observed support so every tested cutoff is real.
            lower_fence = max(min(values), q1 - 1.5 * (q3 - q1))
            derived = [
                ("tukey_lower_fence", lower_fence),
                ("p05", _quantile(values, 0.05)),
                ("p10", _quantile(values, 0.10)),
                ("p20", _quantile(values, 0.20)),
                ("q1", q1), ("q2_median", q2), ("q3", q3),
                ("current", METRICS[metric_id][2]),
            ]
        else:
            derived = [
                ("q1", q1), ("q2_median", q2), ("q3", q3),
                ("tukey_upper_fence", q3 + 1.5 * (q3 - q1)),
                ("p80", _quantile(values, 0.80)),
                ("p90", _quantile(values, 0.90)),
                ("p95", _quantile(values, 0.95)),
                ("current", METRICS[metric_id][2]),
            ]
        unique = sorted({_candidate_value(value) for _, value in derived})
        candidate_map[metric_id] = unique
        labels_by_value: dict[float, list[str]] = defaultdict(list)
        for label, value in derived:
            labels_by_value[_candidate_value(value)].append(label)
        projects = {row["project"] for row in rows}
        for threshold in unique:
            predicted = [row for row in rows if _prediction(row, threshold)]
            output.append({
                "metric_id": metric_id,
                "rule_id": METRICS[metric_id][0],
                "candidate_sources": ";".join(labels_by_value[threshold]),
                "threshold": _format_number(threshold),
                "eligible_observations": len(rows),
                "predicted_positive_observations": len(predicted),
                "observation_candidate_rate": f"{len(predicted) / len(rows):.8f}",
                "eligible_repositories": len(projects),
                "repositories_with_prediction": len({row["project"] for row in predicted}),
                "repository_candidate_rate": f"{len({row['project'] for row in predicted}) / len(projects):.8f}",
            })
    return output, candidate_map


def _distribution_rows(observations: list[dict]) -> list[dict]:
    grouped: dict[str, list[dict]] = defaultdict(list)
    for row in observations:
        if _truth(row["eligible"]):
            grouped[row["metric_id"]].append(row)
    output = []
    for metric_id, rows in sorted(grouped.items()):
        values = [_float(row["value"]) for row in rows]
        by_project: dict[str, list[float]] = defaultdict(list)
        for row in rows:
            by_project[row["project"]].append(_float(row["value"]))
        repo_medians = [statistics.median(items) for items in by_project.values()]
        q1, q2, q3 = (_quantile(values, p) for p in (0.25, 0.5, 0.75))
        lower_fence = q1 - 1.5 * (q3 - q1)
        upper_fence = q3 + 1.5 * (q3 - q1)
        lower_whisker = min(value for value in values if value >= lower_fence)
        upper_whisker = max(value for value in values if value <= upper_fence)
        output.append({
            "metric_id": metric_id,
            "rule_id": METRICS[metric_id][0],
            "unit": METRICS[metric_id][1],
            "observations": len(values),
            "repositories": len(by_project),
            "minimum": _format_number(min(values)),
            "q1": _format_number(q1),
            "median": _format_number(q2),
            "q3": _format_number(q3),
            "maximum": _format_number(max(values)),
            "iqr": _format_number(q3 - q1),
            "lower_whisker": _format_number(lower_whisker),
            "upper_whisker": _format_number(upper_whisker),
            "outlier_count": sum(value < lower_whisker or value > upper_whisker for value in values),
            "mean": f"{statistics.fmean(values):.4f}",
            "repository_median_q1": _format_number(_quantile(repo_medians, 0.25)),
            "repository_median": _format_number(_quantile(repo_medians, 0.50)),
            "repository_median_q3": _format_number(_quantile(repo_medians, 0.75)),
            "current_threshold": _format_number(METRICS[metric_id][2]),
            "comparator": METRICS[metric_id][3],
        })
    return output


def _svg_boxplots(distributions: list[dict], path: Path) -> None:
    width = 1120
    row_height = 48
    left = 285
    right = 1080
    height = 55 + row_height * len(distributions)
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="white"/>',
        '<style>text{font-family:Arial,sans-serif;font-size:12px}.title{font-size:18px;font-weight:700}.axis{stroke:#94a3b8}.box{fill:#bfdbfe;stroke:#1d4ed8;stroke-width:1.5}.median{stroke:#0f172a;stroke-width:2}.current{stroke:#dc2626;stroke-width:2;stroke-dasharray:4 3}.whisker{stroke:#475569}</style>',
        '<text x="20" y="28" class="title">Numerical detector distributions (per-metric log₁₀(value + 1) scale)</text>',
    ]
    for index, row in enumerate(distributions):
        y = 55 + index * row_height
        maximum = max(_float(row["upper_whisker"]), _float(row["current_threshold"]), 1)
        scale_max = math.log10(maximum + 1)
        def x(value):
            return left + (math.log10(max(0, _float(value)) + 1) / scale_max) * (right - left)
        q1, median, q3 = x(row["q1"]), x(row["median"]), x(row["q3"])
        minimum, maximum_x = x(row["lower_whisker"]), x(row["upper_whisker"])
        current = x(row["current_threshold"])
        label = html.escape(row["metric_id"])
        parts.extend([
            f'<text x="20" y="{y + 16}">{label}</text>',
            f'<line x1="{left}" y1="{y + 14}" x2="{right}" y2="{y + 14}" class="axis"/>',
            f'<line x1="{minimum:.2f}" y1="{y + 14}" x2="{maximum_x:.2f}" y2="{y + 14}" class="whisker"/>',
            f'<rect x="{q1:.2f}" y="{y + 5}" width="{max(1, q3-q1):.2f}" height="18" class="box"/>',
            f'<line x1="{median:.2f}" y1="{y + 4}" x2="{median:.2f}" y2="{y + 24}" class="median"/>',
            f'<line x1="{current:.2f}" y1="{y}" x2="{current:.2f}" y2="{y + 28}" class="current"/>',
            f'<text x="{right - 190}" y="{y + 39}">Q1={row["q1"]} M={row["median"]} Q3={row["q3"]} current={row["current_threshold"]}</text>',
        ])
    parts.append('</svg>')
    path.write_text("\n".join(parts) + "\n", encoding="utf-8")


def _band(
    value: float, q1: float, q2: float, q3: float, current: float,
    comparator: str = ">",
) -> str:
    # Keep duplicate cut points. Sparse count metrics often have Q1=median=Q3
    # at zero; retaining four positions gives empty bands where appropriate
    # without making the band assignment crash or inventing cut points.
    if comparator == "<":
        if value < current:
            return "B1_current_positive_lower_tail"
        if value <= q1:
            return "B2_current_to_q1"
        if value <= q2:
            return "B3_q1_to_median"
        if value <= q3:
            return "B4_median_to_q3"
        return "B5_q3_or_higher"
    boundaries = sorted([q1, q2, q3, current])
    if value <= boundaries[0]:
        return "B1_low"
    if value <= boundaries[1]:
        return "B2_lower_middle"
    if value <= boundaries[2]:
        return "B3_upper_middle"
    if value <= boundaries[3]:
        return "B4_high"
    return "B5_current_positive_tail"


def _source_context(row: dict, repository_roots: dict[str, Path]) -> tuple[int, int, int, bool, str, str]:
    source = repository_roots[row["project"]] / row["path"]
    try:
        lines = source.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeError):
        return 0, 0, 0, False, "unavailable", ""
    line = max(1, int(row["line"]))
    if len(lines) <= 400:
        start, end, strategy = 1, len(lines), "complete-file"
    else:
        start = max(1, line - 5)
        end = min(len(lines), line + 80)
        strategy = "local-window"
    rendered = "\n".join(f"{number:>6}: {lines[number - 1]}" for number in range(start, end + 1))
    return start, end, len(lines), start == 1 and end == len(lines), strategy, rendered


def _review_sample(
    observations: list[dict], distributions: list[dict], repositories: list[dict]
) -> list[dict]:
    """One deterministic draw per repository, band, and prediction state.

    Because each selected row has probability 1/N within its project×band
    stratum, N is also its inverse-probability weight.
    """
    summary = {row["metric_id"]: row for row in distributions}
    candidates = [row for row in observations if row["metric_id"] == "large_task_loc"]
    groups: dict[tuple[str, str, str], list[dict]] = defaultdict(list)
    stats = summary["large_task_loc"]
    for row in candidates:
        band = _band(
            _float(row["value"]), _float(stats["q1"]), _float(stats["median"]),
            _float(stats["q3"]), _float(stats["current_threshold"]),
            stats["comparator"],
        )
        groups[(row["project"], band, row["current_prediction"])].append(row)
    selected = []
    repository_roots = {row["project"]: Path(row["repository_path"]) for row in repositories}
    for (project, band, prediction), rows in sorted(groups.items()):
        ranked = sorted(
            rows,
            key=lambda row: hashlib.sha256(
                f"{SEED}\0{row['observation_id']}".encode()
            ).hexdigest(),
        )
        chosen = dict(ranked[0])
        context_start, context_end, total, complete, strategy, context = _source_context(chosen, repository_roots)
        chosen.update({
            "sample_stratum": f"{project}|{band}|current={prediction}",
            "metric_band": band,
            "stratum_population": len(rows),
            "inclusion_probability": f"{1 / len(rows):.10f}",
            "sampling_weight": len(rows),
            "review_question": "Should this executable Ansible task be considered excessively large and in need of decomposition?",
            "context_start_line": context_start,
            "context_end_line": context_end,
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
    return selected


def _write_protocol(path: Path, repository_count: int, observations: int, sample_size: int) -> None:
    path.write_text(f"""# Numerical-threshold benchmark protocol

## Frozen inputs

- Corpus: `{repository_count}` repositories from `study/runs/v007-207/input/repositories.csv`.
- Source units: files with `included=true` and `parse_status=parsed` in each frozen classification manifest.
- Sampling seed: `{SEED}`.
- Extracted scalar observations: `{observations}`.

## Analysis stages

1. **Distribution:** compute Q1, median, Q3, IQR, tail percentiles, Tukey fences, and repository-median quartiles. Lower-is-worse metrics use lower-tail rather than upper-tail candidates.
2. **Sensitivity:** replay every candidate threshold and report both occurrence-level and repository-level candidate rates.
3. **Manual review:** keep `large-task-review-sample.csv` frozen and enter independent labels in `large-task-review-labels.csv`. The sample contains `{sample_size}` rows, normally one draw per repository×metric-band×current-prediction stratum, with inverse-probability weights. Rare current-positive populations are censused in metric-specific packets.
4. **Agreement pilot:** compare two independent reviewers. Report raw agreement, Cohen's kappa, Gwet's AC1, and label-specific agreement. Refine the codebook on new pilot rounds until kappa is at least 0.80; do not tune agreement on the primary or held-out evaluation set.
5. **Threshold scoring:** after adjudication, score each threshold using weighted precision, recall, F1 and F0.5 with project-cluster bootstrap confidence intervals. Precision alone is not a valid selection objective.
6. **AI comparison:** only after the human codebook and labels are frozen, obtain blinded structured AI judgments and compare those judgments with adjudicated human labels.

## Label vocabulary

Use `positive`, `negative`, or `uncertain`. A positive means the underlying code-quality condition is present, independent of whether the current numerical threshold fires. Reviewers must not see the other reviewer's answer or the AI answer.

## Important limitation

The automated stages do not create a human gold standard. Human-to-human agreement requires two genuinely independent people. Agent, heuristic, or Claude labels must be reported as AI-assisted labels and cannot be renamed human labels.
""", encoding="utf-8")


def build(args) -> dict:
    output = Path(args.output)
    output.mkdir(parents=True, exist_ok=True)
    repositories = _repositories(Path(args.repositories_manifest))
    observations_path = output / "observations.csv.gz"
    if args.reuse_observations:
        observations = _read_csv(observations_path)
        failures_path = output / "scan-failures.csv"
        failures = _read_csv(failures_path) if failures_path.exists() else []
        print(f"reused {len(observations)} frozen observations", flush=True)
    else:
        observations = []
        failures = []
        for repo_index, repo in enumerate(repositories, 1):
            files = _classified_files(repo)
            for manifest_row in files:
                try:
                    rows, failure = _file_observations(repo, manifest_row)
                    observations.extend(rows)
                    if failure:
                        failures.append({"project": repo["project"], "path": manifest_row["path"], "failure": failure})
                except Exception as exc:  # Preserve evidence and continue the corpus scan.
                    failures.append({"project": repo["project"], "path": manifest_row["path"], "failure": f"{type(exc).__name__}: {exc}"})
            if repo_index % 5 == 0 or repo_index == len(repositories):
                print(f"processed {repo_index}/{len(repositories)} repositories; observations={len(observations)}; failures={len(failures)}", flush=True)

        observations.sort(key=lambda row: (row["metric_id"], row["project"], row["path"], int(row["line"]), row["observation_id"]))
        _write_csv(observations_path, observations, OBSERVATION_FIELDS)
    distributions = _distribution_rows(observations)
    distribution_fields = list(distributions[0])
    _write_csv(output / "distribution-summary.csv", distributions, distribution_fields)
    sensitivity, candidate_map = _candidate_rows(observations)
    _write_csv(output / "candidate-sensitivity.csv", sensitivity, list(sensitivity[0]))
    _svg_boxplots(distributions, output / "boxplots.svg")

    review = _review_sample(observations, distributions, repositories)
    review_fields = OBSERVATION_FIELDS + [
        "sample_stratum", "metric_band", "stratum_population", "inclusion_probability",
        "sampling_weight", "review_question", "reviewer_1_label", "reviewer_1_reason",
        "context_start_line", "context_end_line", "source_total_lines",
        "context_complete", "context_strategy", "source_context",
        "reviewer_2_label", "reviewer_2_reason", "initial_agreement", "adjudicated_label",
        "adjudication_reason", "ai_label", "ai_reason", "ai_prompt_version", "ai_model_version",
    ]
    _write_csv(output / "large-task-review-sample.csv", review, review_fields)
    working_labels = output / "large-task-review-labels.csv"
    if not _review_file_has_content(working_labels):
        _write_csv(working_labels, review, review_fields)
    _write_csv(output / "scan-failures.csv", failures, ["project", "path", "failure"])
    _write_protocol(output / "PROTOCOL.md", len(repositories), len(observations), len(review))

    manifest = {
        "schema_version": 1,
        "seed": SEED,
        "repositories_manifest": str(Path(args.repositories_manifest)),
        "repository_count": len(repositories),
        "observation_count": len(observations),
        "scan_failure_count": len(failures),
        "large_task_review_sample_count": len(review),
        "candidate_thresholds": candidate_map,
        "artifacts": {},
    }
    mutable_artifacts = {
        "agreement-status.json", "large-task-review-labels.csv",
        "large-task-agreement-pilot-labels.csv",
        "large-task-agreement-pilot-status.json",
        "reviewer-disagreements.csv", "threshold-scores.csv",
    }
    for artifact in sorted(output.iterdir()):
        if (
            artifact.is_file()
            and artifact.name != "benchmark-manifest.json"
            and artifact.name not in mutable_artifacts
        ):
            manifest["artifacts"][artifact.name] = hashlib.sha256(artifact.read_bytes()).hexdigest()
    (output / "benchmark-manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return manifest


def main(argv=None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--repositories-manifest",
        default="study/runs/v007-207/input/repositories.csv",
    )
    parser.add_argument("--output", default="study/threshold-benchmark-v007")
    parser.add_argument(
        "--reuse-observations",
        action="store_true",
        help="Rebuild summaries and samples from the existing observations.csv.gz",
    )
    args = parser.parse_args(argv)
    manifest = build(args)
    print(json.dumps(manifest, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
