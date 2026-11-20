#!/usr/bin/env python3
"""Review the frozen v0.0.7 variable-resolution samples with source evidence.

The output is a single-agent, code-assisted review.  It must not be described
as independent human ground truth or inter-rater agreement evidence.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

import yaml
from jinja2 import Environment, TemplateSyntaxError, meta


RULE = "ansibleguard/unguarded-variable"
MESSAGE_VAR = re.compile(r"(?:Internal variable|Input variable|Runtime input variable) '([^']+)'|Variable '([^']+)'")
JINJA = re.compile(r"{{(.*?)}}|{%(.*?)%}", re.DOTALL)
IDENT = re.compile(r"\b[A-Za-z_][A-Za-z0-9_]*\b")
CONTROL_EXPR = re.compile(r"^\s*(?:when|until|failed_when|changed_when):\s*([^\n#]+)", re.MULTILINE)
YAML_DEF = re.compile(r"^\s*([A-Za-z_][A-Za-z0-9_]*)\s*:")
REGISTER_DEF = re.compile(r"^\s*register:\s*([A-Za-z_][A-Za-z0-9_]*)\s*$")
EXCLUDED = {
    "and", "or", "not", "true", "false", "none", "True", "False", "None",
    "if", "else", "for", "in", "is", "defined", "undefined", "default", "bool",
    "int", "float", "string", "list", "dict", "length", "lower", "upper", "trim",
    "map", "select", "selectattr", "reject", "rejectattr", "join", "split", "replace",
    "regex_replace", "regex_search", "regex_findall", "from_json", "to_json", "to_yaml",
    "from_yaml", "combine", "flatten", "unique", "sort", "first", "last", "min", "max",
    "sum", "range", "zip", "product", "lookup", "query", "q", "omit", "item",
    "ansible_loop", "hostvars", "groups", "group_names", "inventory_hostname",
    "inventory_hostname_short", "playbook_dir", "role_path", "inventory_dir", "vars",
    "environment", "hostvars", "groups", "omit", "result", "results",
}


LABEL_FIELDS = [
    "sample_kind", "sampling_seed", "sampling_stratum", "project", "commit_sha",
    "file", "line", "occurrence_id", "concept_id", "rule_id", "resolution_status",
    "uncertainty_sources", "variable", "classification_correct", "defect_label",
    "root_cause_label", "suppression_safe", "runtime_failure_if_executed",
    "actionable_without_more_context", "evidence_needed", "reviewer_confidence",
    "matched_detector_occurrence", "definition_site_count", "definition_sites",
    "argument_contract", "source_context", "rationale", "reviewer",
]


def read_csv(path: Path) -> list[dict]:
    with path.open(newline="", encoding="utf-8") as stream:
        return list(csv.DictReader(stream))


def write_csv(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=LABEL_FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def variable_from_message(message: str) -> str:
    match = MESSAGE_VAR.search(message or "")
    if not match:
        return ""
    return (match.group(1) or match.group(2)).split(".", 1)[0].split("[", 1)[0]


def context(path: Path, line: int, radius: int = 8) -> str:
    try:
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError:
        return ""
    start = max(0, line - radius - 1)
    end = min(len(lines), line + radius)
    return "\n".join(f"{index + 1}: {lines[index]}" for index in range(start, end))


def argument_contract(repository: Path, relative: str, variable: str) -> str:
    source = repository / relative
    for parent in source.parents:
        if parent == repository.parent:
            break
        paths = tuple(parent.glob("meta/argument_specs.y*ml"))
        if not paths:
            continue
        try:
            within_role = source.relative_to(parent).parts
        except ValueError:
            continue
        entry = Path(relative).stem if within_role and within_role[0] == "tasks" else "main"
        for path in paths:
            try:
                payload = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
                spec = (payload.get("argument_specs") or {}).get(entry) or {}
                option = (spec.get("options") or {}).get(variable)
            except (OSError, yaml.YAMLError, AttributeError):
                return "unreadable"
            if isinstance(option, dict):
                return "required" if option.get("required") is True else "optional"
        return "none"
    return "none"


def extract_source_variables(text: str) -> dict[str, list[int]]:
    found: dict[str, list[int]] = defaultdict(list)
    spans = []
    environment = Environment()
    try:
        global_tokens = meta.find_undeclared_variables(environment.parse(text))
    except TemplateSyntaxError:
        global_tokens = None
    for match in JINJA.finditer(text):
        line_start = text.rfind("\n", 0, match.start()) + 1
        if text[line_start:match.start()].lstrip().startswith("#"):
            continue
        expression = match.group(1) or match.group(2) or ""
        spans.append((match.start(), match.group(0), expression))
    for match in CONTROL_EXPR.finditer(text):
        expression = match.group(1)
        spans.append((match.start(1), "{{ " + expression + " }}", expression))
    for offset, template, expression in spans:
        line = text.count("\n", 0, offset) + 1
        guarded = "| default" in expression or " is defined" in expression or " is undefined" in expression
        try:
            tokens = meta.find_undeclared_variables(environment.parse(template))
        except TemplateSyntaxError:
            without_literals = re.sub(r"'(?:\\.|[^'\\])*'|\"(?:\\.|[^\"\\])*\"", "", expression)
            tokens = set(IDENT.findall(without_literals))
        if global_tokens is not None:
            tokens &= global_tokens
        for token in tokens:
            if token in EXCLUDED or token.startswith("ansible_") or token.isupper():
                continue
            if guarded and re.search(rf"\b{re.escape(token)}\b", expression):
                continue
            found[token].append(line)
    return found


def requested_variables(positive: list[dict], source: list[dict]) -> dict[str, set[str]]:
    wanted: dict[str, set[str]] = defaultdict(set)
    for row in positive:
        variable = variable_from_message(row["message"])
        if variable:
            wanted[row["project"]].add(variable)
    for row in source:
        path = Path(row["repository_path"]) / row["file"]
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        wanted[row["project"]].update(extract_source_variables(text))
    return wanted


def definition_index(repositories: dict[str, Path], wanted: dict[str, set[str]]) -> dict[tuple[str, str], list[str]]:
    index: dict[tuple[str, str], list[str]] = defaultdict(list)
    for project, variables in wanted.items():
        repository = repositories[project]
        for path in repository.rglob("*.y*ml"):
            if ".git" in path.parts or not path.is_file():
                continue
            try:
                lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
            except OSError:
                continue
            relative = str(path.relative_to(repository))
            definition_file = any(
                part in {"defaults", "vars", "group_vars", "host_vars", "inventory"}
                for part in path.relative_to(repository).parts
            )
            scoped_indent: int | None = None
            for line_number, line in enumerate(lines, 1):
                register = REGISTER_DEF.match(line)
                if register and register.group(1) in variables:
                    index[(project, register.group(1))].append(f"{relative}:{line_number}")
                stripped = line.lstrip()
                indent = len(line) - len(stripped)
                if re.match(r"^(?:ansible\.builtin\.)?set_fact:\s*$", stripped) or stripped == "vars:":
                    scoped_indent = indent
                    continue
                if scoped_indent is not None and stripped and not stripped.startswith("#") and indent <= scoped_indent:
                    scoped_indent = None
                match = YAML_DEF.match(line)
                is_definition = definition_file and indent == 0
                is_definition = is_definition or (scoped_indent is not None and indent > scoped_indent)
                if match and is_definition and match.group(1) in variables:
                    index[(project, match.group(1))].append(f"{relative}:{line_number}")
    return index


def common(row: dict, sample_kind: str, variable: str, repository: Path, sites: list[str], contract: str) -> dict:
    line = int(float(row.get("line") or 1))
    return {
        "sample_kind": sample_kind,
        "sampling_seed": row.get("sampling_seed", "v007-variable-resolution-primary-20260917"),
        "sampling_stratum": row.get("sampling_stratum", row.get("resolution_status", "")),
        "project": row["project"],
        "commit_sha": row.get("commit_sha", ""),
        "file": row.get("file", ""),
        "line": line,
        "occurrence_id": row.get("occurrence_id", ""),
        "concept_id": row.get("concept_id", ""),
        "rule_id": row.get("rule_id", RULE),
        "resolution_status": row.get("resolution_status", ""),
        "uncertainty_sources": row.get("uncertainty_sources", "[]"),
        "variable": variable,
        "definition_site_count": len(sites),
        "definition_sites": json.dumps(sites[:20]),
        "argument_contract": contract,
        "source_context": context(repository / row.get("file", ""), line),
        "reviewer": "codex-agent-source-reviewer",
    }


def review_positive(row: dict, repository: Path, index: dict[tuple[str, str], list[str]]) -> dict:
    variable = variable_from_message(row["message"])
    sites = index.get((row["project"], variable), [])
    contract = argument_contract(repository, row["file"], variable)
    item = common(row, "emitted-positive", variable, repository, sites, contract)
    status = row["resolution_status"]
    blockers = row.get("uncertainty_sources", "[]")
    if status == "CANDIDATE_MISSING":
        if contract == "required":
            values = ("no", "FP", "required_external_input", "no", "no", "none", "high",
                      "A directly applicable required role argument proves the value is validated before task execution.")
        elif not sites:
            values = ("yes", "TP", "internal_missing", "yes", "yes", "none", "medium",
                      "Source review found no YAML definition, applicable argument contract, default, or guard for the reported root variable.")
        else:
            values = ("unclear", "UNCERTAIN", "genuinely_uncertain", "unknown", "no", "caller", "medium",
                      "Definitions exist elsewhere in the repository, but source review cannot prove that one reaches this use site.")
    elif status == "EXTERNAL_INPUT_UNCERTAIN":
        correct = "no" if contract == "required" else "yes"
        label = "FP" if contract == "required" else "UNCERTAIN"
        root = "required_external_input" if contract == "required" else "caller_parameter"
        values = (correct, label, root, "unknown", "no", "caller", "high" if contract == "required" else "medium",
                  "The input is required and prevalidated." if contract == "required" else
                  f"External-input blockers are present ({blockers}); repository source cannot prove all caller values.")
    else:
        dynamic = any(name in blockers for name in ("dynamic", "conditional", "include", "fact", "runtime"))
        values = ("yes" if dynamic else "unclear", "UNCERTAIN", "genuinely_uncertain", "unknown", "no", "runtime", "medium",
                  f"Runtime blockers are present ({blockers}); static source review cannot establish the executed value flow.")
    (
        item["classification_correct"], item["defect_label"], item["root_cause_label"],
        item["runtime_failure_if_executed"], item["actionable_without_more_context"],
        item["evidence_needed"], item["reviewer_confidence"], item["rationale"],
    ) = values
    item["suppression_safe"] = "not-applicable"
    item["matched_detector_occurrence"] = "yes"
    return item


def review_source_blocks(
    source: list[dict], repositories: dict[str, Path],
    index: dict[tuple[str, str], list[str]], occurrences: list[dict]
) -> tuple[list[dict], list[dict]]:
    occurrence_map: dict[tuple[str, str, str], list[dict]] = defaultdict(list)
    for occurrence in occurrences:
        if occurrence["rule_id"] != RULE:
            continue
        variable = variable_from_message(occurrence["message"])
        occurrence_map[(occurrence["project"], occurrence["file"], variable)].append(occurrence)
    block_labels, issue_labels = [], []
    for row in source:
        repository = repositories[row["project"]]
        path = repository / row["file"]
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            text = ""
        variables = extract_source_variables(text)
        supported, matched, uncertain = 0, 0, 0
        for variable, lines in sorted(variables.items()):
            sites = index.get((row["project"], variable), [])
            contract = argument_contract(repository, row["file"], variable)
            emitted = occurrence_map.get((row["project"], row["file"], variable), [])
            internal_name = variable.startswith("__") or ("roles/" in row["file"] and "_" in variable)
            if contract == "required" or sites:
                continue
            if not internal_name:
                uncertain += 1
                continue
            supported += 1
            if emitted:
                matched += 1
            synthetic = {
                **row,
                "line": lines[0],
                "occurrence_id": emitted[0]["occurrence_id"] if emitted else "",
                "concept_id": emitted[0]["concept_id"] if emitted else "manual-source-review",
                "rule_id": RULE,
                "resolution_status": emitted[0]["resolution_status"] if emitted else "MISSED_SOURCE_CANDIDATE",
                "uncertainty_sources": emitted[0]["uncertainty_sources"] if emitted else "[]",
            }
            item = common(synthetic, "source-first-issue", variable, repository, sites, contract)
            item.update({
                "classification_correct": "yes" if emitted else "not-applicable",
                "defect_label": "TP",
                "root_cause_label": "internal_missing",
                "suppression_safe": "not-applicable",
                "runtime_failure_if_executed": "yes",
                "actionable_without_more_context": "yes",
                "evidence_needed": "none",
                "reviewer_confidence": "medium",
                "matched_detector_occurrence": "yes" if emitted else "no",
                "rationale": "Source-first review found an unguarded internal-looking variable with no YAML definition or required argument contract; detector matching was performed only after identification.",
            })
            issue_labels.append(item)
        block = common({**row, "line": 1}, "source-first-block", "", repository, [], "not-applicable")
        block.update({
            "classification_correct": "not-applicable",
            "defect_label": "TP" if supported else ("UNCERTAIN" if uncertain else "TN"),
            "root_cause_label": "source_block_with_supported_issue" if supported else "no_supported_issue_found",
            "suppression_safe": "not-applicable",
            "runtime_failure_if_executed": "unknown",
            "actionable_without_more_context": "yes" if supported else "no",
            "evidence_needed": "none" if supported or not uncertain else "runtime",
            "reviewer_confidence": "medium",
            "matched_detector_occurrence": f"{matched}/{supported}" if supported else "not-applicable",
            "definition_site_count": "",
            "definition_sites": "[]",
            "source_context": context(path, 1, 12),
            "rationale": f"Reviewed {len(variables)} unguarded Jinja/control-expression roots; supported issues={supported}, matched={matched}, unresolved external/runtime candidates={uncertain}.",
        })
        block_labels.append(block)
    return block_labels, issue_labels


def review_suppressed(rows: list[dict], repositories: dict[str, Path], index: dict[tuple[str, str], list[str]]) -> list[dict]:
    labels = []
    for row in rows:
        if row.get("sample_kind") != "removed-required-argument-census":
            continue
        repository = repositories[row["project"]]
        variable = variable_from_message(row["message"])
        sites = index.get((row["project"], variable), [])
        contract = argument_contract(repository, row["file"], variable)
        item = common(row, "removed-required-argument-census", variable, repository, sites, contract)
        safe = contract == "required"
        item.update({
            "classification_correct": "not-applicable",
            "defect_label": "FP" if safe else "UNCERTAIN",
            "root_cause_label": "required_external_input" if safe else "genuinely_uncertain",
            "suppression_safe": "yes" if safe else "unclear",
            "runtime_failure_if_executed": "no" if safe else "unknown",
            "actionable_without_more_context": "no",
            "evidence_needed": "none" if safe else "caller",
            "reviewer_confidence": "high" if safe else "low",
            "matched_detector_occurrence": "removed",
            "rationale": "Applicable role argument specification marks the root input required; Ansible validates it before direct entry-point execution." if safe else
                         "The expected required argument contract was not independently recovered from the frozen source path.",
        })
        labels.append(item)
    return labels


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--positive-sample", type=Path, required=True)
    parser.add_argument("--source-sample", type=Path, required=True)
    parser.add_argument("--suppressed-labels", type=Path, required=True)
    parser.add_argument("--repositories", type=Path, required=True)
    parser.add_argument("--occurrences", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()

    positive = read_csv(args.positive_sample)
    source = read_csv(args.source_sample)
    suppressed = read_csv(args.suppressed_labels)
    repo_rows = read_csv(args.repositories)
    occurrences = read_csv(args.occurrences)
    repositories = {row["project"]: Path(row["repository_path"]) for row in repo_rows}
    wanted = requested_variables(positive, source)
    for row in suppressed:
        variable = variable_from_message(row.get("message", ""))
        if variable:
            wanted[row["project"]].add(variable)
    index = definition_index(repositories, wanted)

    positive_labels = [review_positive(row, repositories[row["project"]], index) for row in positive]
    source_blocks, source_issues = review_source_blocks(source, repositories, index, occurrences)
    suppressed_review = review_suppressed(suppressed, repositories, index)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    write_csv(args.output_dir / "emitted-positive-labels.csv", positive_labels)
    write_csv(args.output_dir / "source-first-block-labels.csv", source_blocks)
    write_csv(args.output_dir / "source-first-issue-labels.csv", source_issues)
    write_csv(args.output_dir / "suppressed-census-labels.csv", suppressed_review)
    write_csv(args.output_dir / "all-review-labels.csv", suppressed_review + positive_labels + source_blocks)

    summary = {
        "schema_version": 1,
        "reviewer": "codex-agent-source-reviewer",
        "review_method": "single-agent code-assisted source review",
        "independent_human_gold_standard": False,
        "suppressed": Counter(row["suppression_safe"] for row in suppressed_review),
        "positive_defect_labels": Counter(row["defect_label"] for row in positive_labels),
        "classification_correct": Counter(row["classification_correct"] for row in positive_labels),
        "source_blocks": Counter(row["defect_label"] for row in source_blocks),
        "source_supported_issues": len(source_issues),
        "source_supported_issues_matched": sum(row["matched_detector_occurrence"] == "yes" for row in source_issues),
    }
    serializable = {key: dict(value) if isinstance(value, Counter) else value for key, value in summary.items()}
    (args.output_dir / "review-summary.json").write_text(
        json.dumps(serializable, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(serializable, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
