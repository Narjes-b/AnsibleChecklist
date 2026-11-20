#!/usr/bin/env python3
"""Materialize review-ready studies for every remaining scalar threshold."""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import csv
import gzip
import hashlib
import json
from pathlib import Path

try:
    from scripts.build_threshold_benchmark import (
        OBSERVATION_FIELDS, SEED, _band, _review_file_has_content, _write_csv,
    )
    from scripts.build_threshold_review_sample import LABEL_FIELDS, _context
except ModuleNotFoundError:
    from build_threshold_benchmark import (
        OBSERVATION_FIELDS, SEED, _band, _review_file_has_content, _write_csv,
    )
    from build_threshold_review_sample import LABEL_FIELDS, _context


STUDIES = {
    "long_statement_chars": {
        "slug": "long-statement",
        "question": "Is this source line excessively long in a way that materially harms readability or maintainability?",
        "positive": "The line combines too much logic/data or should be reformatted, decomposed, or moved to a clearer representation.",
        "negative": "The line remains clear and cohesive, or its length is unavoidable and changing it would not improve the code.",
        "guidance": "Long URLs and base64-like blobs were excluded before sampling. Judge YAML/Jinja readability, not length alone.",
    },
    "complex_expression_score": {
        "slug": "complex-expression",
        "question": "Is this Jinja or conditional expression too complex and in need of simplification?",
        "positive": "The expression is difficult to reason about and should be split, named, precomputed, or simplified.",
        "negative": "The expression is understandable and expresses one cohesive condition or transformation.",
        "guidance": "Inspect operators, filters, indexing, nesting, and length together. The numerical score is only a proxy.",
    },
    "complex_expression_length_chars": {
        "slug": "complex-expression-length",
        "question": "Is this Jinja or conditional expression too complex and in need of simplification?",
        "positive": "The complete expression is difficult to reason about and should be split, named, precomputed, or simplified.",
        "negative": "The complete expression remains understandable and expresses one cohesive condition or transformation.",
        "guidance": "In production, crossing this cutoff adds two points to the expression score; it is not an independent finding. Judge the whole expression, not character count alone.",
    },
    "excessive_nesting_depth": {
        "slug": "excessive-nesting",
        "question": "Is this task nested too deeply for clear and safe maintenance?",
        "positive": "The block/rescue/always nesting obscures control flow or should be flattened/extracted.",
        "negative": "The nesting is shallow, purposeful, and makes error handling or grouping clearer.",
        "guidance": "Depth zero is ordinary top-level task structure. Judge the surrounding block and recovery logic.",
    },
    "long_task_name_chars": {
        "slug": "long-task-name",
        "question": "Is this task name unnecessarily long or difficult to scan?",
        "positive": "The name contains excessive detail, duplicated context, or prose that should be shortened without losing intent.",
        "negative": "The name is long because the operational distinction is necessary and remains clear.",
        "guidance": "Do not reward short but vague names. A useful task name should say what the task accomplishes.",
    },
    "task_name_special_chars": {
        "slug": "task-name-special-characters",
        "question": "Does this task or its parent play have an inconsistent name that materially harms clarity?",
        "positive": "The task or parent-play characters are decorative, confusing, or inconsistent with a readable naming convention.",
        "negative": "The punctuation is ordinary technical notation or is necessary to identify the operation.",
        "guidance": "Jinja expressions and common technical punctuation are already excluded. Candidate replay varies the task-name cutoff while holding the parent play-name cutoff fixed.",
    },
    "play_name_special_chars": {
        "slug": "play-name-special-characters",
        "question": "Does this task or its parent play have an inconsistent name that materially harms clarity?",
        "positive": "The task or parent-play characters are decorative, confusing, or inconsistent with a readable naming convention.",
        "negative": "The punctuation is ordinary technical notation or necessary to identify the operation.",
        "guidance": "Production propagates a play-name violation to each task in that play, so this study uses task units and holds the task-name cutoff fixed while varying the play-name cutoff.",
    },
    "large_play_loc": {
        "slug": "large-play-loc",
        "question": "Is this Ansible play excessively large and in need of decomposition?",
        "positive": "The play combines separable responsibilities or is too large to understand and test as one unit.",
        "negative": "The play is cohesive and its size is justified by one clear orchestration responsibility.",
        "guidance": "Review source size together with task count and task content; LOC alone is not a defect.",
    },
    "large_play_task_count": {
        "slug": "large-play-task-count",
        "question": "Is this Ansible play excessively large and in need of decomposition?",
        "positive": "The tasks form separable stages that should be roles/includes or separate plays.",
        "negative": "The task sequence is cohesive and splitting it would create unnecessary indirection.",
        "guidance": "Imported task files and block containers must not be confused with executable task count.",
    },
    "large_play_avg_task_size": {
        "slug": "large-play-average-task-size",
        "question": "Is this Ansible play excessively large and in need of decomposition?",
        "positive": "Several tasks contain overly large operations and the play would benefit from decomposition.",
        "negative": "The average is driven by cohesive declarative tasks or otherwise appropriate detail.",
        "guidance": "Inspect multiple tasks in the play; one unusual task can distort an average.",
    },
    "large_playbook_loc": {
        "slug": "large-playbook-loc",
        "question": "Is this Ansible artifact excessively large and in need of decomposition?",
        "positive": "The file contains separable concerns or is too large to maintain safely as one artifact.",
        "negative": "The file is cohesive and its source size is justified by one clear responsibility.",
        "guidance": "The production implementation computes this metric for admitted Ansible documents, including task files; judge the actual artifact kind.",
    },
    "large_playbook_play_count": {
        "slug": "large-playbook-play-count",
        "question": "Is this Ansible artifact excessively large and in need of decomposition?",
        "positive": "The plays represent separable workflows that should be split or imported.",
        "negative": "The plays form one understandable orchestration workflow.",
        "guidance": "Many admitted documents contain zero plays because they are task/variable artifacts; those are valid negative units for this metric.",
    },
    "large_playbook_avg_play_size": {
        "slug": "large-playbook-average-play-size",
        "question": "Is this Ansible artifact excessively large and in need of decomposition?",
        "positive": "The plays are generally too large and should be decomposed into roles, includes, or smaller plays.",
        "negative": "The average play size is appropriate for the cohesive workflow.",
        "guidance": "Inspect the individual plays because averages can hide one extreme play or many empty/small plays.",
    },
    "large_playbook_task_count": {
        "slug": "large-playbook-task-count",
        "question": "Is this Ansible artifact excessively large and in need of decomposition?",
        "positive": "The task population covers separable responsibilities and should be decomposed.",
        "negative": "The tasks implement one cohesive workflow and are appropriately grouped.",
        "guidance": "Judge task cohesion as well as count; task-only files are included by the production metric.",
    },
    "large_playbook_avg_task_size": {
        "slug": "large-playbook-average-task-size",
        "question": "Would an average-task-size cutoff be a useful additional signal that this artifact needs decomposition?",
        "positive": "Multiple tasks are overly large or complex and should be decomposed.",
        "negative": "The average reflects cohesive declarative detail rather than poor abstraction.",
        "guidance": "This accepted legacy cutoff is currently unused by production. Treat this as a counterfactual design study, not current detector performance.",
    },
    "high_coupling_import_count": {
        "slug": "high-coupling-import-count",
        "question": "Does this playbook have harmful dependency coupling?",
        "positive": "The dependencies make behavior difficult to trace or bind unrelated components together.",
        "negative": "The imports are a clear modularization/dispatch mechanism and do not create harmful coupling.",
        "guidance": "Import-only dispatchers are normalized to zero by the detector and should not be called coupled merely for being modular.",
    },
    "high_coupling_role_count": {
        "slug": "high-coupling-role-count",
        "question": "Does this playbook have harmful dependency coupling?",
        "positive": "The role dependencies combine unrelated responsibilities or make the play difficult to reuse and reason about.",
        "negative": "The roles form one clear orchestration composition and their number is justified.",
        "guidance": "Role count is a proxy; architectural cohesion and dependency direction are the real judgment.",
    },
    "undocumented_complex_boolean_ops": {
        "slug": "undocumented-complex-boolean-ops",
        "question": "Is this task condition complex enough to require a preceding rationale comment?",
        "positive": "The condition or surrounding task logic is difficult enough that an explanatory rationale is needed and is missing.",
        "negative": "The task is understandable without an extra rationale comment, or an adequate preceding comment is present.",
        "guidance": "This cutoff is one branch of an OR rule with Jinja-filter count and nesting depth. Candidate replay changes only the Boolean-operator cutoff while holding the other two at production defaults.",
    },
    "undocumented_complex_jinja_filters": {
        "slug": "undocumented-complex-jinja-filters",
        "question": "Is this task's Jinja filtering complex enough to require a preceding rationale comment?",
        "positive": "The transformations or surrounding task logic are difficult enough that an explanatory rationale is needed and is missing.",
        "negative": "The task is understandable without an extra rationale comment, or an adequate preceding comment is present.",
        "guidance": "This cutoff is one branch of an OR rule with Boolean-operator count and nesting depth. Candidate replay changes only the filter cutoff while holding the other two at production defaults.",
    },
    "undocumented_complex_nesting_depth": {
        "slug": "undocumented-complex-nesting",
        "question": "Is this task nested deeply enough to require a preceding rationale comment?",
        "positive": "The nested control flow or surrounding task logic is difficult enough that an explanatory rationale is needed and is missing.",
        "negative": "The task is understandable without an extra rationale comment, or an adequate preceding comment is present.",
        "guidance": "This cutoff is one branch of an OR rule with Boolean-operator and Jinja-filter counts. Candidate replay changes only nesting while holding the other two at production defaults.",
    },
    "cohesion_playbook_score": {
        "slug": "incohesive-playbook-score",
        "question": "Does this playbook combine unrelated responsibility domains so strongly that it should be decomposed?",
        "positive": "Multiple plays show conservatively gated domain fragmentation that makes the playbook difficult to understand or reuse.",
        "negative": "The playbook remains cohesive, or ordinary module diversity is justified by one orchestration goal.",
        "guidance": "Lower scores are more suspicious. The detector currently emits 0 only after a conservative gate and otherwise at least 0.5, so many numerical candidates may be behaviorally equivalent.",
    },
    "complex_playbook_budget": {
        "slug": "complex-playbook-budget",
        "question": "Is this Ansible artifact overly complex because several size and dependency dimensions compound?",
        "positive": "The combined source size, plays, tasks, imports, and roles create an artifact that should be decomposed.",
        "negative": "The combined dimensions remain maintainable and support one cohesive orchestration responsibility.",
        "guidance": "The value is LOC/110 + plays/4 + tasks/15 + imports/4 + roles/5. Production uses a fixed budget cutoff of 2.0; this study tests its distribution and alternatives.",
    },
}


def _read_table(path: Path) -> list[dict]:
    with path.open(newline="", encoding="utf-8") as stream:
        return list(csv.DictReader(stream))


def _source_context(row: dict, roots: dict[str, Path]):
    return _context(row, roots, 80)


def _codebook(metric_id: str, config: dict) -> str:
    return f"""# {metric_id} labeling codebook

## Review question

{config['question']}

Judge the underlying maintainability condition, not whether the current numerical threshold fired.

## Labels

- `positive`: {config['positive']}
- `negative`: {config['negative']}
- `uncertain`: the supplied source and repository context are insufficient for a responsible decision.

## Metric-specific guidance

{config['guidance']}

Review the complete relevant source unit when the excerpt is insufficient. Record concrete evidence rather than restating the numerical value. Two humans label independently; Cohen's kappa must reach at least 0.80 on a pilot before primary labels are frozen. Preserve original labels and adjudicate disagreements separately.
"""


def _results(metric_id: str, config: dict, distribution: dict, sensitivity: list[dict], sample: list[dict]) -> str:
    current = next(row for row in sensitivity if "current" in row["candidate_sources"].split(";"))
    q3 = next(row for row in sensitivity if "q3" in row["candidate_sources"].split(";"))
    current_count = int(current["predicted_positive_observations"])
    q3_count = int(q3["predicted_positive_observations"])
    ratio = "undefined because the current threshold produces zero predictions" if current_count == 0 else f"{q3_count / current_count:.2f} times the current volume"
    table = "\n".join(
        f"| {row['candidate_sources']} | {row['threshold']} | {int(row['predicted_positive_observations']):,} | {100 * float(row['observation_candidate_rate']):.2f}% | {row['repositories_with_prediction']}/{row['eligible_repositories']} |"
        for row in sensitivity
    )
    bands = Counter(row["metric_band"] for row in sample)
    lower_tail = distribution["comparator"] == "<"
    whisker_label = "Tukey lower whisker" if lower_tail else "Tukey upper whisker"
    whisker_value = distribution["lower_whisker"] if lower_tail else distribution["upper_whisker"]
    extreme_label = "Minimum" if lower_tail else "Maximum"
    extreme_value = distribution["minimum"] if lower_tail else distribution["maximum"]
    return f"""# {metric_id} threshold study

## Simple meaning

{config['question']}

The corpus contains **{int(distribution['observations']):,} {distribution['unit']} observations** across **{distribution['repositories']} repositories**.

## Distribution

- Q1: {distribution['q1']}
- Median: {distribution['median']}
- Q3: {distribution['q3']}
- Current threshold: {distribution['current_threshold']} using `{distribution['comparator']}`
- {whisker_label}: {whisker_value}
- {extreme_label}: {extreme_value}

## Sensitivity

| Candidate source | Threshold | Predictions | Observation rate | Repositories affected |
|---|---:|---:|---:|---:|
{table}

At Q3, the detector would produce **{q3_count:,}** predictions. At the current threshold it produces **{current_count:,}**. Q3 therefore represents **{ratio}**.

This volume comparison is descriptive, not a precision result. No candidate is selected before independent labels exist.

## Review sample

The frozen sample contains **{len(sample):,} rows** from **{len({row['project'] for row in sample})} repositories**. It uses one deterministic SHA-ranked observation per available repository × metric-band × current-prediction stratum and records inverse-probability weights. When the complete current-positive population contains at most 200 observations, every current positive is included with weight 1.

Band counts: {', '.join(f'{key}={value}' for key, value in sorted(bands.items()))}.

The working file is `review-labels.csv`. Human agreement, precision, recall, F1, and F0.5 are pending independent human labels. The AI fields remain blank until human consensus is frozen.
"""


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default="study/threshold-benchmark-v007")
    parser.add_argument("--observations", default="study/threshold-benchmark-v007/observations.csv.gz")
    parser.add_argument("--repositories", default="study/runs/v007-207/input/repositories.csv")
    args = parser.parse_args(argv)
    root = Path(args.root)
    distributions = {row["metric_id"]: row for row in _read_table(root / "distribution-summary.csv")}
    all_sensitivity = _read_table(root / "candidate-sensitivity.csv")
    sensitivity = defaultdict(list)
    for row in all_sensitivity:
        sensitivity[row["metric_id"]].append(row)
    with Path(args.repositories).open(newline="", encoding="utf-8") as stream:
        roots = {row["project"]: Path(row["repository_path"]) for row in csv.DictReader(stream)}

    states = {}
    for metric_id, distribution in distributions.items():
        if metric_id not in STUDIES:
            continue
        current_count = int(next(
            row["predicted_positive_observations"]
            for row in sensitivity[metric_id]
            if "current" in row["candidate_sources"].split(";")
        ))
        states[metric_id] = {
            "population": 0,
            "groups": defaultdict(lambda: {"count": 0, "rank": None, "row": None}),
            "census_rows": [],
            "census_current_positives": 0 < current_count <= 200,
        }

    with gzip.open(args.observations, "rt", newline="", encoding="utf-8") as stream:
        for row in csv.DictReader(stream):
            metric_id = row["metric_id"]
            if metric_id not in states:
                continue
            distribution = distributions[metric_id]
            band = _band(
                float(row["value"]), float(distribution["q1"]),
                float(distribution["median"]), float(distribution["q3"]),
                float(distribution["current_threshold"]),
                distribution["comparator"],
            )
            state = states[metric_id]
            state["population"] += 1
            if state["census_current_positives"] and row["current_prediction"] == "true":
                chosen = dict(row)
                chosen["metric_band"] = band
                state["census_rows"].append(chosen)
                continue
            group = state["groups"][(row["project"], band, row["current_prediction"])]
            group["count"] += 1
            rank = hashlib.sha256(
                f"{SEED}\0{metric_id}\0{row['observation_id']}".encode()
            ).hexdigest()
            if group["rank"] is None or rank < group["rank"]:
                group["rank"] = rank
                group["row"] = dict(row)

    summary = []
    for metric_id, config in STUDIES.items():
        state = states[metric_id]
        directory = root / config["slug"]
        directory.mkdir(parents=True, exist_ok=True)
        sample = []
        for chosen in state["census_rows"]:
            start, end, total, complete, strategy, context = _source_context(chosen, roots)
            chosen.update({
                "sample_stratum": f"{chosen['project']}|current-positive-census|{chosen['observation_id']}",
                "stratum_population": 1,
                "inclusion_probability": "1.0000000000",
                "sampling_weight": 1,
                "review_question": config["question"],
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
            sample.append(chosen)
        for (project, band, prediction), group in sorted(state["groups"].items()):
            chosen = dict(group["row"])
            start, end, total, complete, strategy, context = _source_context(chosen, roots)
            chosen.update({
                "sample_stratum": f"{project}|{band}|current={prediction}",
                "metric_band": band,
                "stratum_population": group["count"],
                "inclusion_probability": f"{1 / group['count']:.10f}",
                "sampling_weight": group["count"],
                "review_question": config["question"],
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
            sample.append(chosen)
        fields = OBSERVATION_FIELDS + LABEL_FIELDS
        frozen = directory / "review-sample.csv"
        working = directory / "review-labels.csv"
        _write_csv(frozen, sample, fields)
        if not _review_file_has_content(working):
            _write_csv(working, sample, fields)
        _write_csv(directory / "candidate-sensitivity.csv", sensitivity[metric_id], list(sensitivity[metric_id][0]))
        (directory / "LABELING_CODEBOOK.md").write_text(_codebook(metric_id, config), encoding="utf-8")
        (directory / "RESULTS.md").write_text(
            _results(metric_id, config, distributions[metric_id], sensitivity[metric_id], sample),
            encoding="utf-8",
        )
        agreement_status = {
            "paired_items": 0, "agreements": 0, "disagreements": 0,
            "raw_agreement": None, "cohens_kappa": None, "gwet_ac1": None,
            "label_prevalence": {}, "label_specific_agreement": {},
            "confusion_matrix": {},
            "target": 0.8,
            "minimum_paired": 50, "status": "insufficient-independent-labels",
        }
        status_path = directory / "agreement-status.json"
        if not status_path.exists() or json.loads(status_path.read_text(encoding="utf-8")).get("paired_items") == 0:
            status_path.write_text(json.dumps(agreement_status, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        scores = directory / "threshold-scores.csv"
        if not scores.exists():
            scores.write_text("metric_id,threshold\n", encoding="utf-8")
        manifest = {
            "schema_version": 1,
            "seed": SEED,
            "metric_id": metric_id,
            "population_observations": state["population"],
            "sample_rows": len(sample),
            "sample_projects": len({row["project"] for row in sample}),
            "review_sample_sha256": hashlib.sha256(frozen.read_bytes()).hexdigest(),
            "artifacts": {},
            "working_labels_are_mutable": True,
        }
        mutable = {
            "review-labels.csv", "agreement-status.json", "threshold-scores.csv",
            "human-ai-agreement.json", "reviewer-disagreements.csv",
            "sample-manifest.json", "agreement-pilot-labels.csv",
            "agreement-pilot-status.json",
        }
        for artifact in sorted(directory.iterdir()):
            if artifact.is_file() and artifact.name not in mutable:
                manifest["artifacts"][artifact.name] = hashlib.sha256(artifact.read_bytes()).hexdigest()
        (directory / "sample-manifest.json").write_text(
            json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
        summary.append({
            "metric_id": metric_id, "slug": config["slug"],
            "population": state["population"], "sample_rows": len(sample),
            "sample_projects": manifest["sample_projects"],
        })
        print(f"{metric_id}: population={state['population']} sample={len(sample)} projects={manifest['sample_projects']}", flush=True)
    (root / "all-study-samples.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
