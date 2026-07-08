"""
Writes a SARIF 2.1.0 document from the flat findings list produced by
findings.build_findings_list(). See https://sarifweb.azurewebsites.net/
for the spec; GitHub's Code Scanning feature natively renders results from
a file in this shape as inline PR annotations when uploaded via
github/codeql-action/upload-sarif in a CI workflow.
"""

import json
from pathlib import Path

from .findings import RULE_CATALOG

TOOL_NAME = "AnsibleGuard"
TOOL_VERSION = "0.1.0"
TOOL_INFO_URI = "https://github.com/your-org/ansibleguard"  # update once packaged


def _to_repo_relative(file_path, repo_root):
    """
    SARIF artifactLocation.uri must be relative to the repo root for
    GitHub to correctly map an annotation back to the right file in a PR
    diff -- an absolute path here silently fails to annotate anything.
    """
    try:
        return str(Path(file_path).resolve().relative_to(Path(repo_root).resolve()))
    except ValueError:
        # Not actually under repo_root (e.g. a single file passed with no
        # shared root) -- fall back to just the filename rather than
        # emitting an absolute path GitHub can't map.
        return Path(file_path).name


def _build_rules():
    rules = []
    for rule_id, meta in RULE_CATALOG.items():
        rules.append(
            {
                "id": rule_id,
                "shortDescription": {"text": meta["description"]},
                "defaultConfiguration": {"level": meta["level"]},
                "properties": {"category": meta.get("category", "general")},
            }
        )
    return rules


def build_sarif(all_findings, repo_root):
    """all_findings: flat list across every file, as produced by
    findings.build_findings_list() (called once per file, concatenated)."""
    results = []
    for f in all_findings:
        results.append(
            {
                "ruleId": f["rule_id"],
                "level": f["severity"],
                "message": {"text": f["message"]},
                "locations": [
                    {
                        "physicalLocation": {
                            "artifactLocation": {
                                "uri": _to_repo_relative(f["file"], repo_root)
                            },
                            "region": {"startLine": f["line"]},
                        }
                    }
                ],
            }
        )

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
                        "rules": _build_rules(),
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
