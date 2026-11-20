"""Write the complete developer and GitHub pull-request report."""

from __future__ import annotations

from collections import Counter
import json
import os
from pathlib import Path
from urllib.parse import quote

from .findings import (
    CATEGORY_PRIORITY,
    developer_priority_key,
    finding_category,
    is_optional_finding,
)
from .occurrences import occurrence_findings
from .sarif_writer import write_sarif
from .csv_writer import write_findings_to_csv
from .text_writer import write_findings_to_txt
from .llm_explain import assessment_text


from .output_contract import CONTRACT_URI, SCHEMA_VERSION


CONTRACT = CONTRACT_URI


def _write_json(path, payload):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def _safe(value):
    return str(value).replace("|", "\\|").replace("\n", " ")


def _ordered_categories(counts):
    priority = {category: index for index, category in enumerate(CATEGORY_PRIORITY)}
    return sorted(counts, key=lambda item: (priority.get(item, len(priority)), item))


def _location(item, source_url=None):
    file = str(item.get("file", "."))
    line = int(item.get("line") or 1)
    label = f"`{_safe(file)}:{line}`"
    if not source_url:
        return label
    target = f"{source_url.rstrip('/')}/{quote(file, safe='/')}#L{line}"
    return f"[{label}]({target})"


def _display_rule_id(item):
    """Return a human-readable rule identifier for the finding table.

    For ansible-lint findings the concept_id is the generic 'ansible-lint-issue'
    which gives no signal in a table cell.  Use the native rule ID instead
    (e.g. 'fqcn[action-core]') so reviewers see the actual check name.
    """
    concept_id = item.get("concept_id", "")
    if concept_id == "ansible-lint-issue":
        native = item.get("native_rule_id") or item.get("rule_id", "")
        if native and native != "ansible-lint-issue":
            return native
    return concept_id or item.get("rule_id", "finding")


def _changed_line_label(item):
    """Classify how this finding relates to the diff.

    direct   — the finding is on a line that was directly changed
    indirect — the finding is in a changed file but not on a changed line
    -        — the finding is in a file not touched by this PR
    """
    if item.get("on_changed_line"):
        return "direct"
    if item.get("in_changed_file") or item.get("caused_by_diff"):
        return "indirect"
    return "-"


def _message_with_llm_suggestion(item):
    """Append the per-occurrence AI explanation/fix (ansibleguard diff
    --explain) to the finding's message, always with its disclaimer --
    see llm_explain.py's module docstring for why this is never shown
    without that caveat attached."""
    message = item.get("message", "")
    assessment = assessment_text(item)
    if assessment:
        return f"{message} {assessment}".strip()
    if item.get("llm_status") != "ok" or not item.get("llm_suggested_fix"):
        return message
    suggestion = f"AI suggestion (unverified): {item['llm_suggested_fix']}"
    if item.get("llm_disclaimer"):
        suggestion = f"{suggestion} ({item['llm_disclaimer']})"
    return f"{message} {suggestion}" if message else suggestion


def _finding_table(lines, findings, *, source_url=None):
    lines.extend(
        [
            "| Category | Severity | Rule | Location | Changed line | Message |",
            "|---|---|---|---|---:|---|",
        ]
    )
    for item in sorted(findings, key=developer_priority_key):
        lines.append(
            "| " + " | ".join(
                (
                    _safe(finding_category(item)),
                    _safe(item.get("severity", "warning")),
                    _safe(_display_rule_id(item)),
                    _location(item, source_url),
                    _changed_line_label(item),
                    _safe(_message_with_llm_suggestion(item)),
                )
            ) + " |"
        )


def _provider_breakdown(findings):
    """Return (ansibleguard_count, ansible_lint_count, other_count)."""
    ag, al, other = 0, 0, 0
    for item in findings:
        provider = item.get("provider", "ansibleguard")
        concept_id = item.get("concept_id", "")
        if provider == "ansible-lint" or concept_id == "ansible-lint-issue":
            al += 1
        elif provider == "ansibleguard":
            ag += 1
        else:
            other += 1
    return ag, al, other


def _blocking_finding_label(introduced):
    """Return a short label for the finding that would trigger a policy failure.

    Picks the first error-severity finding, or the first actionable finding
    if there are no errors — to name the root cause in the failure banner.
    """
    errors = [f for f in introduced if f.get("severity") == "error"]
    pool = errors or [f for f in introduced if not is_optional_finding(f)]
    if not pool:
        return None
    item = sorted(pool, key=developer_priority_key)[0]
    rule = _display_rule_id(item)
    return f"{rule} at {item.get('file', '?')}:{item.get('line', '?')}"


def render_summary(
    comparison, policy, playbooks, *, mode="changed", source_url=None
):
    selected = [item for item in playbooks if mode == "all" or item["affected"]]
    by_severity = policy.get("introduced_by_severity", {})
    introduced = comparison.get("introduced", [])
    fixed = comparison.get("fixed", [])
    actionable = [item for item in introduced if not is_optional_finding(item)]
    optional = [item for item in introduced if is_optional_finding(item)]
    by_category = policy.get("introduced_by_category") or dict(
        Counter(finding_category(item) for item in introduced)
    )
    failed = policy["conclusion"] == "failure"
    status = "Failed" if failed else "Passed"
    ag_count, al_count, other_count = _provider_breakdown(introduced)
    provider_parts = []
    if ag_count:
        provider_parts.append(f"{ag_count} from AnsibleGuard")
    if al_count:
        provider_parts.append(f"{al_count} from ansible-lint")
    if other_count:
        provider_parts.append(f"{other_count} other")
    provider_note = f" ({', '.join(provider_parts)})" if provider_parts else ""
    lines = [
        "# AnsibleGuard PR Report",
        "",
        f"Status: **{status}**",
    ]
    if comparison.get("source_context", {}).get("status") == "unavailable":
        lines.extend(["", "> Source for these saved results is unavailable. Playbook/source summaries and AI explanations were not generated."])
    if failed:
        blocker = _blocking_finding_label(introduced)
        if blocker:
            lines.append(f"> Blocking finding: `{blocker}`")
    compatibility = comparison.get("snapshot_compatibility") or {}
    broken = policy.get("introduced_parse_failures") or []
    if broken:
        lines.append(
            "> **Parse regression:** this change makes "
            + ", ".join(f"`{path}`" for path in broken)
            + " unparseable as YAML."
        )
    excluded_files = compatibility.get("excluded_files") or []
    if excluded_files:
        shown = ", ".join(f"`{path}`" for path in excluded_files[:5])
        more = f" and {len(excluded_files) - 5} more" if len(excluded_files) > 5 else ""
        lines.append(
            f"> **Not compared:** {shown}{more} could not be parsed on at least one side; "
            "findings in these files were excluded from both base and head."
        )
    excluded = compatibility.get("excluded_providers") or []
    if excluded:
        lines.append(
            "> **Partial comparison:** "
            + ", ".join(f"`{name}`" for name in excluded)
            + " did not complete on at least one side, so its findings were excluded "
            "from both base and head. AnsibleGuard and every completed provider were compared."
        )
    lines.extend(
        [
            "",
            f"- {len(selected)} affected playbook(s) shown",
            f"- {len(introduced)} finding(s) introduced{provider_note} "
            f"({by_severity.get('error', 0)} errors, {by_severity.get('warning', 0)} warnings, {by_severity.get('note', 0)} notes)",
            f"- {len(actionable)} actionable finding(s); {len(optional)} optional policy finding(s)",
            f"- {len(fixed)} finding(s) fixed",
            f"- {len(comparison.get('unchanged', []))} finding(s) unchanged",
            f"- {len(comparison.get('moved', []))} finding(s) moved",
            "",
            "## Introduced findings by category",
            "",
        ]
    )
    if not by_category:
        lines.append("No introduced findings were found.")
    else:
        lines.extend(["| Category | Introduced |", "|---|---:|"])
        for category in _ordered_categories(by_category):
            lines.append(f"| {_safe(category)} | {by_category[category]} |")
    lines.extend(
        [
        "",
        "## Playbook results",
        "",
        ]
    )
    if not selected:
        lines.append("No playbooks were affected by this change.")
    else:
        lines.extend(
            [
                "| Playbook | Status | Changed tasks | New errors | New warnings | Fixed | Existing |",
                "|---|---:|---:|---:|---:|---:|---:|",
            ]
        )
        for item in selected:
            counts = item["findings"]
            severity = counts.get("introduced_by_severity", {})
            lines.append(
                "| " + " | ".join(
                    (
                        f"`{_safe(item['path'])}`",
                        item["status"],
                        str(item["changed_tasks"]),
                        str(severity.get("error", 0)),
                        str(severity.get("warning", 0)),
                        str(counts["fixed"]),
                        str(counts["unchanged"]),
                    )
                ) + " |"
            )
    lines.extend(["", "## Actionable introduced findings", ""])
    if not actionable:
        lines.append("No actionable introduced findings were found.")
    else:
        _finding_table(lines, actionable, source_url=source_url)
    if optional:
        lines.extend(
            [
                "",
                "<details>",
                f"<summary>Optional policy findings ({len(optional)})</summary>",
                "",
            ]
        )
        _finding_table(lines, optional, source_url=source_url)
        lines.extend(["", "</details>"])
    if fixed:
        lines.extend(
            [
                "",
                "<details>",
                f"<summary>Fixed findings ({len(fixed)})</summary>",
                "",
            ]
        )
        _finding_table(lines, fixed, source_url=source_url)
        lines.extend(["", "</details>"])
    lines.extend(
        [
            "",
            "> Repository totals count each occurrence once. A shared role finding may be referenced by more than one playbook.",
            "",
        ]
    )
    return "\n".join(lines)


def write_diff_report(
    output_root,
    comparison,
    policy,
    playbooks,
    *,
    repo_root,
    changed_lines=None,
    summary_mode="changed",
    source_url=None,
):
    output_root = Path(output_root)
    diff_dir = output_root / "diff"
    diff_dir.mkdir(parents=True, exist_ok=True)
    payload = {
        "schema_version": SCHEMA_VERSION,
        "contract": CONTRACT,
        "kind": "pr-comparison",
        "comparison": comparison,
        "policy": policy,
        "changed_lines": {
            key: sorted(value) for key, value in sorted((changed_lines or {}).items())
        },
        "playbooks": playbooks,
    }
    _write_json(diff_dir / "comparison.json", payload)
    _write_json(diff_dir / "introduced.json", {
        "schema_version": SCHEMA_VERSION, "contract": CONTRACT, "kind": "introduced-occurrences",
        "items": comparison.get("introduced", []),
    })
    actionable = [
        item
        for item in comparison.get("introduced", [])
        if not is_optional_finding(item)
    ]
    _write_json(diff_dir / "introduced-actionable.json", {
        "schema_version": SCHEMA_VERSION,
        "contract": CONTRACT,
        "kind": "introduced-occurrences",
        "scope": "actionable",
        "items": actionable,
    })
    _write_json(diff_dir / "fixed.json", {
        "schema_version": SCHEMA_VERSION, "contract": CONTRACT, "kind": "fixed-occurrences",
        "items": comparison.get("fixed", []),
    })
    _write_json(diff_dir / "playbooks.json", {
        "schema_version": SCHEMA_VERSION, "contract": CONTRACT, "kind": "playbook-summary",
        "items": playbooks,
    })
    introduced_findings = occurrence_findings(comparison.get("introduced", []))
    for finding, occurrence in zip(introduced_findings, comparison.get("introduced", [])):
        for key in ("on_changed_line", "caused_by_diff", "in_changed_file"):
            if key in occurrence:
                finding[key] = occurrence[key]
    write_sarif(introduced_findings, diff_dir / "introduced.sarif", repo_root)
    write_findings_to_csv(introduced_findings, diff_dir / "introduced.csv")
    write_findings_to_txt(
        introduced_findings, diff_dir / "introduced.txt", title="Introduced findings"
    )
    actionable_findings = occurrence_findings(actionable)
    for finding, occurrence in zip(actionable_findings, actionable):
        for key in (
            "on_changed_line",
            "caused_by_diff",
            "in_changed_file",
            "finding_category",
            "policy",
        ):
            if key in occurrence:
                finding[key] = occurrence[key]
    write_sarif(
        actionable_findings,
        diff_dir / "introduced-actionable.sarif",
        repo_root,
    )
    write_findings_to_csv(
        actionable_findings, diff_dir / "introduced-actionable.csv"
    )
    write_findings_to_txt(
        actionable_findings,
        diff_dir / "introduced-actionable.txt",
        title="Introduced actionable findings",
    )
    (diff_dir / "summary.md").write_text(
        render_summary(
            comparison,
            policy,
            playbooks,
            mode=summary_mode,
            source_url=source_url or os.environ.get("ANSIBLEGUARD_SOURCE_URL"),
        ),
        encoding="utf-8",
    )
    return payload
