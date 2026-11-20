"""
Writes a SARIF 2.1.0 document from the flat findings list produced by
findings.build_findings_list(). See https://sarifweb.azurewebsites.net/
for the spec; GitHub's Code Scanning feature natively renders results from
a file in this shape as inline PR annotations when uploaded via
github/codeql-action/upload-sarif in a CI workflow.
"""

import json
from pathlib import Path

from .llm_explain import ASSESSMENT_FIELDS

from .findings import RULE_CATALOG

TOOL_NAME = "AnsibleGuard"
TOOL_VERSION = "0.0.1"
TOOL_INFO_URI = "https://github.com/ansibleguard/ansibleguard"
_ANSIBLE_LINT_DOCS_URI = "https://ansible-lint.readthedocs.io/rules/{rule}/"


def _to_repo_relative(file_path, repo_root):
    """
    SARIF artifactLocation.uri must be relative to the repo root for
    GitHub to correctly map an annotation back to the right file in a PR
    diff -- an absolute path here silently fails to annotate anything.
    """
    path = Path(file_path)
    if not path.is_absolute():
        return path.as_posix().removeprefix("./")
    try:
        return str(path.resolve().relative_to(Path(repo_root).resolve()))
    except ValueError:
        # Not actually under repo_root (e.g. a single file passed with no
        # shared root) -- fall back to just the filename rather than
        # emitting an absolute path GitHub can't map.
        return Path(file_path).name


def _effective_rule_id(finding):
    """Return the SARIF ruleId for a finding.

    For ansible-lint findings the generic concept_id 'ansible-lint-issue'
    would collapse all 65k+ lint findings into one rule in GitHub Code
    Scanning.  Use the native rule ID (e.g. 'fqcn[action-core]') instead
    so each lint check gets its own rule node, annotation colour, and
    dismissal scope.
    """
    concept_id = finding.get("concept_id", finding["rule_id"])
    if concept_id == "ansible-lint-issue":
        native = finding.get("native_rule_id") or finding["rule_id"]
        if native and native != "ansible-lint-issue":
            return native
    return finding["rule_id"]


def _build_rules(all_findings=()):
    rules = []
    seen = set()
    for rule_id, meta in RULE_CATALOG.items():
        seen.add(rule_id)
        rules.append(
            {
                "id": rule_id,
                "shortDescription": {"text": meta["description"]},
                "fullDescription": {"text": meta["description"]},
                "help": {"text": meta.get("remediation", meta["description"])},
                "defaultConfiguration": {"level": meta["level"]},
                "properties": {
                    "category": meta.get("category", "general"),
                    "confidence": meta.get("confidence", "medium"),
                    "status": meta.get("status", "active"),
                    "taxonomy": meta.get("taxonomy", "MAINTAINABILITY_SIGNAL"),
                    "actionability": meta.get("actionability", "advisory"),
                },
            }
        )
    for finding in all_findings:
        rule_id = _effective_rule_id(finding)
        if rule_id in seen:
            continue
        seen.add(rule_id)
        concept_id = finding.get("concept_id", rule_id)
        is_ansible_lint = concept_id == "ansible-lint-issue"
        # Strip the bracketed tag for the base rule name used in docs URLs,
        # e.g. 'fqcn[action-core]' → 'fqcn'.
        base_rule = rule_id.split("[")[0].rstrip()
        entry = {
            "id": rule_id,
            "shortDescription": {
                "text": (
                    f"ansible-lint: {rule_id}"
                    if is_ansible_lint
                    else f"AnsibleGuard: {rule_id}."
                )
            },
            "help": {
                "text": finding.get(
                    "remediation",
                    (
                        f"See ansible-lint documentation for {rule_id}."
                        if is_ansible_lint
                        else "Review the finding in project context."
                    ),
                )
            },
            "defaultConfiguration": {"level": finding.get("severity", "warning")},
            "properties": {
                "category": "ansible-lint" if is_ansible_lint else "canonical-occurrence",
                "concept_id": concept_id,
                "confidence": finding.get("confidence", "medium"),
            },
        }
        if is_ansible_lint:
            entry["helpUri"] = _ANSIBLE_LINT_DOCS_URI.format(rule=base_rule)
        rules.append(entry)
    return rules


def build_sarif(all_findings, repo_root):
    """all_findings: flat list across every file, as produced by
    findings.build_findings_list() (called once per file, concatenated)."""
    results = []
    for f in all_findings:
        uri = _to_repo_relative(f["file"], repo_root)
        result = {
                "ruleId": _effective_rule_id(f),
                "level": f["severity"],
                "message": {"text": f["message"]},
                "locations": [
                    {
                        "physicalLocation": {
                            "artifactLocation": {
                                "uri": uri
                            },
                            "region": {"startLine": f["line"]},
                        }
                    }
                ],
                "properties": {
                    "provider": f.get("provider", "ansibleguard"),
                    "native_rule_id": f.get("native_rule_id", f["rule_id"]),
                    "concept_id": f.get("concept_id", f["rule_id"]),
                    "detectors": f.get("detectors", []),
                    "confidence": f.get("confidence", "medium"),
                    "remediation": f.get("remediation"),
                    "help_url": f.get("help_url"),
                    "taxonomy": f.get("taxonomy"),
                    "actionability": f.get("actionability"),
                    "rule_maturity": f.get("rule_maturity"),
                    "analysis_population": f.get("analysis_population"),
                    "source_population": f.get("source_population"),
                },
            }
        stable = f.get("semantic_key") or f.get("finding_id")
        if stable:
            # GitHub uses partial fingerprints to retain identity when line
            # numbers move between commits.
            result["partialFingerprints"] = {
                "ansibleguardSemanticId/v1": str(stable),
            }
        result["properties"].update(
            {
                key: f[key]
                for key in (
                    "on_changed_line",
                    "caused_by_diff",
                    "in_changed_file",
                    "finding_category",
                    "policy",
                )
                if key in f
            }
        )
        # Optional LLM enrichment (ansibleguard diff --explain). Deliberately
        # kept in `properties` rather than SARIF's native `fix` object: SARIF
        # requires `fix.artifactChanges` to point at an exact, trustworthy
        # replacement range, and this model has a measured false-positive
        # blind spot (see llm_explain.py's module docstring) -- presenting
        # its answer as SARIF's native "suggested fix" would overstate how
        # much to trust it. `llm_disclaimer` always travels with the rest of
        # these fields so a renderer can't show one without the other.
        if f.get("llm_status"):
            result["properties"].update(
                {
                    key: f[key]
                    for key in (
                        "llm_status",
                        *ASSESSMENT_FIELDS,
                        "llm_model",
                        "llm_explanation",
                        "llm_why_in_this_context",
                        "llm_suggested_fix",
                        "llm_fixed_code_snippet",
                        "llm_confidence",
                        "llm_limitations",
                        "llm_disclaimer",
                        "llm_error",
                    )
                    if key in f
                }
            )
        results.append(result)

    return {
        "$schema": "https://raw.githubusercontent.com/oasis-tcs/sarif-spec/main/sarif-2.1/schema/sarif-schema-2.1.0.json",
        "version": "2.1.0",
        "runs": [
            {
                "tool": {
                    "driver": {
                        "name": TOOL_NAME,
                        "informationUri": TOOL_INFO_URI,
                        "version": TOOL_VERSION,
                        "rules": _build_rules(all_findings),
                    }
                },
                "results": results,
            }
        ],
    }


def write_sarif(all_findings, output_path, repo_root):
    sarif_doc = build_sarif(all_findings, repo_root)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(sarif_doc, f, indent=2)
