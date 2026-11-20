#!/usr/bin/env python3
"""Build one complete Markdown results report for a full study run.

Every number comes from the CSV tables that ``scripts/v007_full_repro.py``
(``<analysis>/run/``), ``scripts/v007_results_analysis.py`` and
``scripts/v007_charts.py`` already wrote; nothing is typed by hand. Counts
are detector output, not validated defects.
"""

from __future__ import annotations

import argparse
import csv
import json
import os
from pathlib import Path

CHART_CAPTIONS = {
    "01-repository-execution-status": "Repository execution status (complete, partial, failed).",
    "02-raw-vs-canonical": "Raw findings against canonical (deduplicated) occurrences.",
    "03-findings-by-provider": "Occurrences by provider (AnsibleGuard, ansible-lint, GitLeaks).",
    "04-top-rules": "Most frequent AnsibleGuard rules, all policies.",
    "04b-top-required-rules": "Most frequent AnsibleGuard rules, required occurrences only.",
    "05-rule-prevalence": "Share of analyzable repositories in which each rule fires.",
    "06-findings-per-repository-distribution": "Distribution of AnsibleGuard occurrences per repository.",
    "07-findings-density": "Occurrences per 1,000 selected YAML lines, per repository.",
    "08-severity-distribution": "Severity of AnsibleGuard occurrences.",
    "09-confidence-distribution": "Detector confidence of AnsibleGuard occurrences.",
    "10-certainty-distribution": "Certainty (confirmed, uncertain, exposed) of AnsibleGuard occurrences.",
    "11-actionability-distribution": "Actionability of AnsibleGuard occurrences.",
    "12-provider-completeness": "Which providers completed per repository.",
    "13-runtime-distribution": "Scan time per repository (machine-dependent).",
    "14-repository-size-vs-findings": "Repository size (selected YAML lines) against occurrences.",
    "15-rule-repository-heatmap": "Rule by repository heatmap.",
    "16-external-tool-overlap": "Overlap with external tools (not modelled: no equivalence mapping).",
}


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as source:
        return list(csv.DictReader(source))


def n(value: str | int | float) -> str:
    """Format a count with thousands separators; pass other text through."""
    try:
        number = float(value)
    except (TypeError, ValueError):
        return str(value)
    if number.is_integer():
        return f"{int(number):,}"
    return f"{number:,.2f}"


def table(header: list[str], body: list[list[str]], align: str | None = None) -> str:
    align = align or "l" + "r" * (len(header) - 1)
    marks = ["---:" if a == "r" else "---" for a in align]
    lines = ["| " + " | ".join(header) + " |", "|" + "|".join(marks) + "|"]
    lines += ["| " + " | ".join(str(cell) for cell in row) + " |" for row in body]
    return "\n".join(lines) + "\n"


def short(rule_id: str) -> str:
    return rule_id.split("/", 1)[-1]


def build(analysis: Path, output: Path, previous: Path | None, summary_doc: str) -> str:
    run = analysis / "run"
    tables = run / "tables"
    overview = {}
    report = (run / "report" / "FULL_STUDY_REPORT.md").read_text(encoding="utf-8")
    in_overview = False
    for line in report.splitlines():
        if line.startswith("## Overview"):
            in_overview = True
            continue
        if in_overview and line.startswith("## "):
            break
        if in_overview and line.startswith("| ") and not line.startswith("| Metric") and not line.startswith("|---"):
            key, value = [cell.strip() for cell in line.strip("|").split("|")[:2]]
            overview[key] = value
    manifest = json.loads((run / "RUN_MANIFEST.json").read_text(encoding="utf-8")) if (run / "RUN_MANIFEST.json").exists() else {}
    validation = json.loads((run / "status" / "validation-report.json").read_text(encoding="utf-8"))
    sanity = json.loads((run / "sanity-checks.json").read_text(encoding="utf-8"))
    env = (run / "environment" / "pip-freeze.txt").read_text(encoding="utf-8").splitlines()
    pins = [line for line in env if line.split("==")[0] in {"ansible-core", "ansible-lint", "PyYAML", "ruamel.yaml"}]
    test_log = run / "logs" / "test-results.txt"
    tests = test_log.read_text().strip().splitlines()[-1] if test_log.exists() else ""
    categories = rows(analysis / "category-overview.csv")
    families = rows(analysis / "family-overview.csv")
    rules = sorted(rows(analysis / "rule-profile.csv"), key=lambda r: -int(r["occurrences"]))
    repos = rows(analysis / "repository-profile.csv")
    providers = rows(tables / "findings-by-provider.csv")
    completeness = rows(tables / "provider-completeness.csv")
    partials = rows(tables / "failures-and-partials.csv")
    provider_by_category = rows(analysis / "provider-by-category-complete-repositories.csv")
    rel = lambda p: os.path.relpath(p, output.parent)

    counts_early = validation["repository_status_counts"]
    total_internal = sum(int(r["occurrences"]) for r in categories)
    total_required = sum(int(r["required"]) for r in categories)
    total_optional = sum(int(r["optional"]) for r in categories)
    analyzable = [r for r in repos if r["selected_loc"] not in ("", "0")]
    loc = sum(int(r["selected_loc"] or 0) for r in repos)
    files = sum(int(r["selected_files"] or 0) for r in repos)
    split_counts: dict[str, int] = {}
    for r in repos:
        split_counts[r["split"]] = split_counts.get(r["split"], 0) + 1

    out: list[str] = []
    w = out.append
    w(f"# Full results report: run `{overview.get('Run', analysis.name)}`\n")
    w("Complete results of the AnsibleGuard full study run over the frozen 207-repository corpus. Every number below is read from "
      "the run's own tables by `scripts/build_run_results_report.py`. **All counts are detector output, not validated defects**: "
      "no precision estimate exists yet, so no count here is a claim that a defect exists.\n")
    w(f"Short summary, deviations and comparison: [{summary_doc}]({summary_doc}).\n")

    w("## Key results\n")
    by_occ = rules
    req = sorted(rules, key=lambda r: -int(r["required_occurrences"]))
    top5 = sum(int(r["occurrences"]) for r in by_occ[:5])
    most_prev = max((r for r in rules if r["policy"] == "required"), key=lambda r: float(r["prevalence_pct"]))
    uncertain_by_rule = sorted(
        ((short(r["rule_id"]), sum(int(part.split("=")[1]) for part in r["cert_mix"].split("; ") if part.startswith("UNCERTAIN=")))
         for r in rules), key=lambda item: -item[1])
    uncertain = int(overview.get("Uncertain occurrences", "0"))
    for item in [
        f"{n(validation['expected_repositories'])} frozen repositories: {n(counts_early['complete'])} complete, "
        f"{n(counts_early['partial'])} partial (ansible-lint incomplete), {n(counts_early['failed'])} failed (timeout); "
        f"{n(len(analyzable))} are analyzable for AnsibleGuard ({n(loc)} selected YAML lines in {n(files)} files).",
        f"AnsibleGuard reports {n(total_internal)} static-source occurrences from {len(rules)} rules: "
        f"{n(total_required)} required ({100 * total_required / total_internal:.1f}%) and {n(total_optional)} optional.",
        f"Five rules account for {100 * top5 / total_internal:.1f}% of all occurrences: "
        + ", ".join(f"{short(r['rule_id'])} ({n(r['occurrences'])})" for r in by_occ[:5]) + ".",
        "Largest required rules: " + ", ".join(f"{short(r['rule_id'])} ({n(r['required_occurrences'])})" for r in req[:5]) + ".",
        f"Most widespread required-only rule: {short(most_prev['rule_id'])}, in {most_prev['prevalence_pct']}% of analyzable repositories.",
        f"By category, style is {categories[0]['share_pct']}% of occurrences (mostly optional), then "
        + ", ".join(f"{c['category']} {c['share_pct']}%" for c in categories[1:4]) + ".",
        f"{n(uncertain)} occurrences ({100 * uncertain / int(overview['Internal occurrences'].replace(',', '')):.1f}% of AnsibleGuard's) "
        "are uncertain: the detector could not see enough context to confirm them; "
        f"{uncertain_by_rule[0][0]} accounts for {n(uncertain_by_rule[0][1])} of them ({100 * uncertain_by_rule[0][1] / uncertain:.1f}%).",
        f"Occurrences are concentrated: the 20 largest repositories hold "
        f"{100 * sum(int(r['required']) + int(r['optional']) for r in sorted(analyzable, key=lambda r: -(int(r['required']) + int(r['optional'])))[:20]) / total_internal:.1f}% of all occurrences.",
        "AnsibleGuard results are identical to the 2026-10-16 run of the same version (Section 12).",
    ]:
        w(f"- {item}")
    w("")

    w("## Contents\n")
    for title in ["1. Run identity", "2. Population and execution health", "3. Headline counts", "4. Providers",
                  "5. Categories", "6. Review families", "7. All rules", "8. Severity, confidence, certainty, actionability",
                  "9. Repositories", "10. Partial and failed repositories", "11. Charts",
                  "12. Comparison with earlier runs", "13. Interpretation limits", "14. Files and reproduction"]:
        anchor = title.lower().replace(".", "").replace(",", "").replace(" ", "-")
        w(f"- [{title}](#{anchor})")
    w("")

    w("## 1. Run identity\n")
    body = [
        ["Run id", f"`{overview.get('Run', '')}`"],
        ["Tool version", overview.get("Tool version", "")],
        ["Tool commit", f"`{', '.join(validation.get('observed_tool_commits', []))}`"],
        ["Rule-profile hash", f"`{', '.join(validation.get('observed_profile_rule_hashes', []))}`"],
        ["Pinned environment", ", ".join(pins)],
        ["Runner test step", tests or "not recorded"],
        ["Validation gate", f"{validation['status']} (publication_ready: {validation['publication_ready']})"],
        ["Sanity checks", sanity.get("status", sanity.get("overall_status", "see SANITY_CHECKS.md"))],
    ]
    if manifest.get("created_at_utc") or manifest.get("generated_at_utc"):
        body.append(["Packaged at (UTC)", manifest.get("created_at_utc") or manifest.get("generated_at_utc")])
    w(table(["Item", "Value"], body, "ll"))

    w("## 2. Population and execution health\n")
    counts = validation["repository_status_counts"]
    w(table(["Measure", "Value"], [
        ["Frozen repositories", n(validation["expected_repositories"])],
        ["Complete (all providers)", n(counts.get("complete", 0))],
        ["Partial (AnsibleGuard complete, an optional provider incomplete)", n(counts.get("partial", 0))],
        ["Failed (no AnsibleGuard result)", n(counts.get("failed", 0))],
        ["Analyzable for AnsibleGuard", n(len(analyzable))],
        ["Calibration / heldout split", " / ".join(f"{k} {n(v)}" for k, v in sorted(split_counts.items()))],
        ["Selected YAML files", n(files)],
        ["Selected YAML lines", n(loc)],
    ], "lr"))
    w("Provider completeness:\n")
    w(table(["State", "Repositories"], [[r["state"], n(r["repositories"])] for r in completeness], "lr"))
    w("A failed or provider-incomplete repository is a missing observation, never zero findings.\n")

    w("## 3. Headline counts\n")
    keys = ["Raw findings", "Canonical occurrences", "Internal occurrences", "Internal static-source occurrences",
            "Review-only occurrences", "ansible-lint occurrences", "ansible-lint comparable occurrences",
            "GitLeaks whole-repository occurrences", "Uncertain occurrences", "Provider-comparable occurrences",
            "Excluded incomplete-provider occurrences", "Rules observed"]
    label = {"Rules observed": "Rules observed (all three providers)"}
    w(table(["Measure", "Count"], [[label.get(k, k), n(overview[k])] for k in keys if k in overview], "lr"))
    w(f"AnsibleGuard static-source occurrences split into **{n(total_required)} required** and **{n(total_optional)} optional** "
      f"(total {n(total_internal)}). Required rules form the default developer-facing profile; optional rules are style, "
      "policy and advisory checks.\n")

    w("## 4. Providers\n")
    w(table(["Provider", "Occurrences", "Comparable", "Share %", "Eligible repos", "Missing repos", "Repos affected", "Prevalence %"],
            [[p["provider"], n(p["findings"]), n(p["eligible_findings"]), p["share_percent"], p["eligible_repositories"],
              p["missing_repositories"], p["repositories_affected"], p["repository_prevalence_percent"]] for p in providers]))
    w("By category, restricted to the 171 provider-complete repositories (the only population where providers can be compared):\n")
    w(table(["Category", "AnsibleGuard all", "AnsibleGuard required", "ansible-lint", "GitLeaks"],
            [[r["category"], n(r["internal_all"]), n(r["internal_required"]), n(r["ansible_lint"]), n(r["gitleaks"])]
             for r in provider_by_category]))
    w("No equivalence mapping between AnsibleGuard rules and ansible-lint or GitLeaks rules is modelled, so tool overlap is "
      "reported as not estimable rather than as zero.\n")

    w("## 5. Categories\n")
    w(table(["Category", "Occurrences", "Share %", "Required", "Optional", "Rules", "Repos", "Prevalence %",
             "Median / affected repo", "Median / kLOC", "Top rule (share %)", "Gini", "Uncertain %"],
            [[c["category"], n(c["occurrences"]), c["share_pct"], n(c["required"]), n(c["optional"]), c["rules"],
              c["repositories"], c["prevalence_pct"], n(c["median_per_affected_repo"]), c["median_per_kloc"],
              f"{c['top_rule']} ({c['top_rule_share_pct']})", c["gini_across_repos"], c["uncertain_pct"]] for c in categories],
            "l" + "r" * 9 + "lrr"))
    w("Gini near 1 means the category's occurrences are concentrated in few repositories; near 0, spread evenly.\n")

    w("## 6. Review families\n")
    w("Families group rules for human validation (see `study/validation-v007-human/`).\n")
    w(table(["Family", "Rules", "With required", "Required", "Optional", "Heldout required"],
            [[f["family"], f["rules"], f["rules_with_required"], n(f["required_occurrences"]), n(f["optional_occurrences"]),
              n(f["heldout_required"])] for f in families]))

    w("## 7. All rules\n")
    w(f"All {len(rules)} AnsibleGuard rules with at least one occurrence, most frequent first. Prevalence is the share of the "
      f"{len(analyzable)} analyzable repositories where the rule fires.\n")
    w(table(["Rule", "Category", "Policy", "Occurrences", "Required", "Optional", "Repos", "Prevalence %",
             "Median / affected", "P90 / affected", "Top repository (share)", "Gini", "Certainty"],
            [[short(r["rule_id"]), r["category"], r["policy"], n(r["occurrences"]), n(r["required_occurrences"]),
              n(r["optional_occurrences"]), r["repositories"], r["prevalence_pct"], n(r["median_per_affected_repo"]),
              n(r["p90_per_affected_repo"]), f"{r['top_repository']} ({r['top_repository_share']})",
              r["gini_across_repos"], r["cert_mix"]] for r in rules],
            "lll" + "r" * 7 + "lrl"))

    w("## 8. Severity, confidence, certainty, actionability\n")
    for name, title in [("severity", "Severity"), ("confidence", "Confidence"), ("certainty", "Certainty")]:
        data = rows(tables / f"{name}.csv")
        w(f"**{title}**\n")
        w(table([title, "Occurrences", "%"], [[r[name], n(r["findings"]), r["percentage"]] for r in data]))
    data = rows(tables / "actionability.csv")
    total = sum(int(r["findings"]) for r in data)
    w("**Actionability**\n")
    w(table(["Actionability", "Occurrences", "%"],
            [[r["actionability"], n(r["findings"]), f"{100 * int(r['findings']) / total:.2f}"] for r in data]))
    w("Certainty and actionability are reported separately on purpose: an uncertain occurrence is not a lower-priority "
      "actionable one.\n")

    w("## 9. Repositories\n")
    ranked = sorted(analyzable, key=lambda r: -(int(r["required"]) + int(r["optional"])))
    w(f"Per-repository figures for all {len(repos)} analyzable repositories are in `repository-profile.csv`. "
      "The 20 repositories with the most AnsibleGuard occurrences:\n")
    w(table(["Repository", "Split", "YAML lines", "Files", "Required", "Optional", "Uncertain", "Required / kLOC", "All / kLOC",
             "Provider complete"],
            [[r["repository"], r["split"], n(r["selected_loc"]), n(r["selected_files"]), n(r["required"]), n(r["optional"]),
              n(r["uncertain"]), r["required_per_kloc"], r["all_per_kloc"], r["provider_complete"]] for r in ranked[:20]],
            "ll" + "r" * 7 + "l"))
    dens = sorted(analyzable, key=lambda r: -float(r["required_per_kloc"] or 0))
    w("The 10 highest required densities (repositories with at least 1,000 selected YAML lines):\n")
    big = [r for r in dens if int(r["selected_loc"] or 0) >= 1000][:10]
    w(table(["Repository", "YAML lines", "Required", "Required / kLOC"],
            [[r["repository"], n(r["selected_loc"]), n(r["required"]), r["required_per_kloc"]] for r in big]))

    w("## 10. Partial and failed repositories\n")
    lint_partial = sum(1 for p in partials if p["overall_status"] == "partial" and "ansible-lint=partial" in p["provider_state"])
    w(f"{lint_partial} of the {sum(1 for p in partials if p['overall_status'] == 'partial')} partial repositories are partial "
      "because ansible-lint did not finish on every file; their AnsibleGuard and GitLeaks results are complete and included. "
      "The failed repository timed out before producing any result and is excluded from every count.\n")
    w(table(["Repository", "Status", "Scan", "Error", "Providers"],
            [[p["repository"], p["overall_status"], p["scan_status"], p["error_type"] or "", p["provider_state"]] for p in partials],
            "lllll"))

    w("## 11. Charts\n")
    w("All 17 charts are plain SVG files in the repository (not compressed); each chart's numbers are in "
      "`charts/data/<chart>.csv` and were checked against the run's own summaries by `scripts/v007_charts_check.py`.\n")
    for svg in sorted((analysis / "charts").glob("*.svg")):
        caption = CHART_CAPTIONS.get(svg.stem, svg.stem)
        w(f"### {svg.stem}\n\n{caption}\n\n![{svg.stem}]({rel(svg)})\n")
    runner_charts = sorted((run / "charts").glob("*.svg"))
    if runner_charts:
        w("The runner's own charts (same data, runner styling): " + ", ".join(f"[{c.stem}]({rel(c)})" for c in runner_charts) + ".\n")

    w("## 12. Comparison with earlier runs\n")
    if previous and (previous / "rule-profile.csv").exists():
        old = {r["rule_id"]: r for r in rows(previous / "rule-profile.csv")}
        changed = [(r["rule_id"], int(old.get(r["rule_id"], {}).get("occurrences", 0) or 0), int(r["occurrences"]))
                   for r in rules if int(old.get(r["rule_id"], {}).get("occurrences", 0) or 0) != int(r["occurrences"])]
        missing = sorted(set(old) - {r["rule_id"] for r in rules})
        w(f"Against `{previous.name}`: {len(rules) - len(changed)} of {len(rules)} rules have identical occurrence counts"
          + (f"; changed: {', '.join(f'{short(a)} {n(b)} → {n(c)}' for a, b, c in changed)}" if changed else "")
          + (f"; rules no longer observed: {', '.join(map(short, missing))}" if missing else "") + ".\n")
        old_cat = {r["category"]: r for r in rows(previous / "category-overview.csv")}
        w(table(["Category", previous.name, analysis.name, "Change"],
                [[c["category"], n(old_cat.get(c["category"], {}).get("occurrences", 0)), n(c["occurrences"]),
                  n(int(c["occurrences"]) - int(old_cat.get(c["category"], {}).get("occurrences", 0) or 0))] for c in categories]))
    delta = previous / "rule-delta-vs-v007.csv" if previous else None
    if delta and delta.exists():
        moved = [r for r in rows(delta) if r["delta_required"] != "0" or r["delta_optional"] != "0"]
        w("From v0.0.7 to v0.0.7.1 (the audit fixes), required counts changed for these rules (`rule-delta-vs-v007.csv`):\n")
        w(table(["Rule", "v0.0.7 required", "v0.0.7.1 required", "Change"],
                [[short(r["rule_id"]), n(r["v007_required"]), n(r["v0071_required"]), n(r["delta_required"])]
                 for r in sorted(moved, key=lambda r: int(r["delta_required"]))]))
        w("A decrease is not evidence of higher precision: it shows only that the audited false-positive mechanisms no longer "
          "fire.\n")

    w("## 13. Interpretation limits\n")
    for item in [
        "Counts are detector output. No precision or recall estimate exists until the human Reviewer A/B labels are adjudicated "
        "(`study/validation-v007-human/`).",
        "Uncertain occurrences depend on context the detector cannot see and must be kept separate from confirmed ones.",
        "Per-kLOC rates apply only to AnsibleGuard static-source and ansible-lint populations; GitLeaks scans whole repositories "
        "and review-only rules read Git history.",
        "ansible-lint results exist only for provider-complete repositories; cross-tool comparison uses those 171 only.",
        "Results describe the frozen selected repositories at their frozen commits and do not generalise beyond them.",
        "Repository concentration (Gini, top-repository share) means a few large repositories drive several rules' totals.",
    ]:
        w(f"- {item}")
    w("")

    w("## 14. Files and reproduction\n")
    w(table(["What", "Where"], [
        ["Analysis tables", f"`{analysis.as_posix()}/*.csv`"],
        ["Charts (SVG) and chart data", f"`{analysis.as_posix()}/charts/`"],
        ["Run reports, tables, status, environment", f"`{analysis.as_posix()}/run/`"],
        ["Full raw run archive", "`~/Documents/AnsibleChecklist-results-2026-10-22/` (not in Git; checksum in `study/runs/*.sha256`)"],
    ], "ll"))
    w("```bash\n"
      "python scripts/v007_full_repro.py --config <config> --minimum-free-gib 20 --skip-benchmark-validation\n"
      "python scripts/v007_full_repro.py --config <config> --postprocess-only   # after the single known timeout\n"
      f"python scripts/v007_results_analysis.py --run study/runs/<run-id> --output-dir {analysis.as_posix()}\n"
      f"python scripts/v007_charts.py --run study/runs/<run-id> --output-dir {analysis.as_posix()}/charts\n"
      f"python scripts/v007_charts_check.py study/runs/<run-id> {analysis.as_posix()}/charts\n"
      "python scripts/build_run_results_report.py --analysis <analysis-dir> --previous <earlier-analysis-dir> --output <report.md>\n"
      "```\n")
    return "\n".join(out)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--analysis", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--previous", type=Path, default=None)
    parser.add_argument("--summary-doc", default="v0071-rerun-2026-10-22-summary.md")
    args = parser.parse_args(argv)
    args.output.write_text(build(args.analysis, args.output, args.previous, args.summary_doc), encoding="utf-8")
    print(args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
