#!/usr/bin/env python3
"""RQ1: Reviewer A/B agreement, adjudication sheet and precision on the
350-item agreement pilot.

Steps, all rerunnable:

1. Agreement between Reviewer A and Reviewer B on the semantic label
   (positive / negative / uncertain / unreviewable) and the actionability
   label: raw agreement, Cohen's kappa and Gwet's AC1, overall and per family.
2. Adjudication sheet: every item where A and B give different semantic labels
   (required) or the same semantic but different actionability labels
   (optional). Reviewers fill ``final_semantic_label`` and the other blank
   columns; the sheet is read back on the next run and never overwritten.
3. Final labels: the shared label where A and B agree, the adjudicated label
   otherwise. Items still waiting for adjudication are reported as pending.
4. Precision = positive / (positive + negative), per family and per rule, with
   Wilson and repository-cluster bootstrap 95% intervals and bounds that count
   every uncertain item as negative (lower) or positive (upper).
5. Carry-over to a later run: each pilot item is matched to the later run's
   occurrences; items the later version no longer reports are listed, and
   precision is recomputed on the items it still reports.
6. A family-weighted overall precision using each family's share of the later
   run's required occurrences.

Precision diagnostics are computed only from settled labels. Until
adjudication is complete, the agreed-only figures are provisional and biased
towards easier cases. Settled labels do not establish evaluation eligibility:
pilot exclusions persist, and this script has no design-aware population
precision estimator.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import random
from collections import Counter, defaultdict
from pathlib import Path

SEMANTIC = ["positive", "negative", "uncertain", "unreviewable"]
ACTIONABILITY = ["blocking", "actionable", "advisory", "not-actionable", "not-applicable", "uncertain"]
SHEET_COLUMNS = [
    "issue_id", "priority", "review_family", "rule_id", "repository", "path", "line_start", "context_file",
    "reviewer_a_label_semantic", "reviewer_b_label_semantic", "reviewer_a_label_actionability",
    "reviewer_b_label_actionability", "reviewer_a_reason_code", "reviewer_b_reason_code",
    "reviewer_a_explanation", "reviewer_b_explanation",
    "final_semantic_label", "final_actionability_label", "adjudication_reason", "adjudicated_by", "adjudication_date",
]
BOOTSTRAP_SEED = 20261022


def read(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as source:
        return list(csv.DictReader(source))


def write(path: Path, rows: list[dict], columns: list[str] | None = None) -> None:
    columns = columns or (list(rows[0]) if rows else [])
    with path.open("w", newline="", encoding="utf-8") as target:
        writer = csv.DictWriter(target, fieldnames=columns, extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({k: (f"{v:.4f}" if isinstance(v, float) else v) for k, v in row.items()})


def family_key(name: str) -> str:
    return name.lower().replace("/", "_").replace(" ", "_")


def cohen_kappa(pairs: list[tuple[str, str]]) -> float:
    n = len(pairs)
    if not n:
        return float("nan")
    observed = sum(a == b for a, b in pairs) / n
    left, right = Counter(a for a, _ in pairs), Counter(b for _, b in pairs)
    expected = sum(left[k] * right[k] for k in set(left) | set(right)) / (n * n)
    return (observed - expected) / (1 - expected) if expected < 1 else float("nan")


def gwet_ac1(pairs: list[tuple[str, str]], categories: list[str]) -> float:
    n = len(pairs)
    if not n:
        return float("nan")
    observed = sum(a == b for a, b in pairs) / n
    counts = Counter(a for a, _ in pairs) + Counter(b for _, b in pairs)
    q = len(categories)
    expected = sum((counts[k] / (2 * n)) * (1 - counts[k] / (2 * n)) for k in categories) / (q - 1)
    return (observed - expected) / (1 - expected) if expected < 1 else float("nan")


def wilson(successes: int, total: int) -> tuple[float, float]:
    if not total:
        return float("nan"), float("nan")
    z, p = 1.96, successes / total
    centre = (p + z * z / (2 * total)) / (1 + z * z / total)
    half = z * math.sqrt(p * (1 - p) / total + z * z / (4 * total * total)) / (1 + z * z / total)
    return centre - half, centre + half


def cluster_bootstrap(items: list[dict], draws: int = 2000) -> tuple[float, float]:
    """Percentile interval of precision when whole repositories are resampled."""
    by_repo: dict[str, list[str]] = defaultdict(list)
    for item in items:
        by_repo[item["repository"]].append(item["final_semantic"])
    repos = sorted(by_repo)
    if not repos:
        return float("nan"), float("nan")
    rng = random.Random(BOOTSTRAP_SEED)
    values = []
    for _ in range(draws):
        pos = neg = 0
        for repo in (rng.choice(repos) for _ in repos):
            labels = by_repo[repo]
            pos += labels.count("positive")
            neg += labels.count("negative")
        if pos + neg:
            values.append(pos / (pos + neg))
    values.sort()
    if not values:
        return float("nan"), float("nan")
    return values[int(0.025 * (len(values) - 1))], values[int(0.975 * (len(values) - 1))]


def precision_row(group: str, items: list[dict]) -> dict:
    counts = Counter(item["final_semantic"] for item in items)
    pos, neg, unc, unr = (counts.get(k, 0) for k in SEMANTIC)
    decidable = pos + neg
    low, high = wilson(pos, decidable)
    boot_low, boot_high = cluster_bootstrap(items)
    reviewable = pos + neg + unc
    return {
        "group": group, "items": len(items), "positive": pos, "negative": neg, "uncertain": unc, "unreviewable": unr,
        "precision": pos / decidable if decidable else float("nan"),
        "wilson_low": low, "wilson_high": high, "cluster_low": boot_low, "cluster_high": boot_high,
        "bound_uncertain_as_negative": pos / reviewable if reviewable else float("nan"),
        "bound_uncertain_as_positive": (pos + unc) / reviewable if reviewable else float("nan"),
        "repositories": len({item["repository"] for item in items}),
    }


def pct(value: float) -> str:
    return "n/a" if value is None or (isinstance(value, float) and math.isnan(value)) else f"{100 * value:.1f}%"


def sample_scope(master: list[dict], manifest: dict) -> dict:
    """Adjudication completeness never overrides a calibration exclusion.

    Even an eligible sample needs a design-aware estimator. This legacy
    agreement script does not implement one and emits descriptive diagnostics.
    """
    pilot = any(
        str(row.get(key, "")).lower() == "true"
        for row in master for key in ("is_pilot", "is_agreement_pilot")
    )
    excluded = manifest.get("eligible_for_performance_scoring") is False or any(
        str(row.get("eligible_for_performance_scoring", "")).lower() == "false"
        for row in master
    )
    if pilot or excluded:
        scope = "calibration-only"
        reason = "Pilot or sample metadata excludes performance scoring."
    else:
        scope = "descriptive-only"
        reason = "This script has no design-aware population precision estimator."
    return {
        "evidence_scope": scope,
        "sample_declared_eligible": manifest.get("eligible_for_performance_scoring"),
        "eligible_for_performance_scoring": False,
        "population_precision_status": "not-estimated",
        "reason": reason,
    }


def load_later_run(paths: list[Path]) -> tuple[set[str], set[tuple[str, str, str, str]]]:
    ids, keys = set(), set()
    for path in paths:
        with path.open(newline="", encoding="utf-8") as source:
            for row in csv.DictReader(source):
                ids.add(row["occurrence_id"])
                keys.add((row["project"], row["file"], row["line"], row["rule_id"]))
    return ids, keys


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--labels", type=Path, required=True,
                        help="consolidated Reviewer A/B label comparison CSV")
    parser.add_argument("--master", type=Path,
                        default=Path("study/validation-v007-human/samples/agreement-pilot/agreement-pilot-master.csv"))
    parser.add_argument("--sample-manifest", type=Path, default=None,
                        help="sample provenance; otherwise discover the manifest beside the master")
    parser.add_argument("--output-dir", type=Path, default=Path("study/rq1-agreement-pilot"))
    parser.add_argument("--later-occurrences", type=Path, nargs="*", default=[],
                        help="later run's all-internal-source-occurrences.csv and all-review-occurrences.csv")
    parser.add_argument("--later-label", default="later run")
    parser.add_argument("--rule-profile", type=Path, default=None, help="later run's rule-profile.csv, for family weights")
    args = parser.parse_args(argv)
    out = args.output_dir
    out.mkdir(parents=True, exist_ok=True)

    labels = read(args.labels)
    master_rows = read(args.master)
    master = {row["sample_id"]: row for row in master_rows}
    if len(master) != len(master_rows):
        parser.error("duplicate sample IDs in master")
    missing = sorted({row["issue_id"] for row in labels} - master.keys())
    if missing:
        parser.error(f"label IDs absent from master: {missing}")
    manifest_path = args.sample_manifest
    if manifest_path is None:
        candidate = args.master.with_name(args.master.stem.removesuffix("-master") + "-manifest.json")
        if candidate.is_file():
            manifest_path = candidate
    manifest = json.loads(manifest_path.read_text(encoding="utf-8")) if manifest_path else {}
    scope = sample_scope(master_rows, manifest)
    scope_suffix = "-calibration" if scope["evidence_scope"] == "calibration-only" else "-descriptive"
    sheet_path = out / "adjudication-sheet.csv"
    previous = {row["issue_id"]: row for row in read(sheet_path)} if sheet_path.exists() else {}

    # 1. Agreement.
    agreement_rows = []
    families = sorted({row["review_family"] for row in labels})
    for group in ["All families", *families]:
        subset = labels if group == "All families" else [r for r in labels if r["review_family"] == group]
        sem = [(r["reviewer_a_label_semantic"], r["reviewer_b_label_semantic"]) for r in subset]
        act = [(r["reviewer_a_label_actionability"], r["reviewer_b_label_actionability"]) for r in subset]
        agreement_rows.append({
            "group": group, "items": len(subset),
            "semantic_agreement": sum(a == b for a, b in sem) / len(sem),
            "semantic_kappa": cohen_kappa(sem), "semantic_ac1": gwet_ac1(sem, SEMANTIC),
            "actionability_agreement": sum(a == b for a, b in act) / len(act),
            "actionability_kappa": cohen_kappa(act), "actionability_ac1": gwet_ac1(act, ACTIONABILITY),
        })
    write(out / "agreement.csv", agreement_rows)
    confusion = Counter((r["reviewer_a_label_semantic"], r["reviewer_b_label_semantic"]) for r in labels)

    # 2. Adjudication sheet (keeps anything already filled in).
    sheet = []
    for r in labels:
        sem_differs = r["reviewer_a_label_semantic"] != r["reviewer_b_label_semantic"]
        act_differs = r["reviewer_a_label_actionability"] != r["reviewer_b_label_actionability"]
        if not (sem_differs or act_differs):
            continue
        filled = previous.get(r["issue_id"], {})
        sheet.append({
            **{k: r.get(k, "") for k in SHEET_COLUMNS},
            "priority": "required (semantic)" if sem_differs else "optional (actionability only)",
            "context_file": f"study/validation-v007-human/samples/agreement-pilot/context/{r['issue_id']}.md",
            **{k: filled.get(k, "") for k in SHEET_COLUMNS[16:]},
        })
    sheet.sort(key=lambda s: (s["priority"] != "required (semantic)", s["review_family"], s["issue_id"]))
    write(sheet_path, sheet, SHEET_COLUMNS)
    adjudicated = {s["issue_id"]: s for s in sheet if s["final_semantic_label"].strip() in SEMANTIC}
    invalid = [s["issue_id"] for s in sheet if s["final_semantic_label"].strip() and s["final_semantic_label"].strip() not in SEMANTIC]

    # 3. Final labels.
    finals = []
    for r in labels:
        a, b = r["reviewer_a_label_semantic"], r["reviewer_b_label_semantic"]
        if a == b:
            final, source = a, "agreed"
        elif r["issue_id"] in adjudicated:
            final, source = adjudicated[r["issue_id"]]["final_semantic_label"].strip(), "adjudicated"
        else:
            final, source = "", "pending"
        m = master.get(r["issue_id"], {})
        finals.append({"issue_id": r["issue_id"], "review_family": r["review_family"], "rule_id": r["rule_id"],
                       "repository": r["repository"], "path": r["path"], "line_start": r["line_start"],
                       "occurrence_id": m.get("occurrence_id", ""), "reviewer_a": a, "reviewer_b": b,
                       "final_semantic": final, "final_source": source})
    pending = sum(1 for f in finals if f["final_source"] == "pending")
    complete = pending == 0
    decided = [f for f in finals if f["final_semantic"]]
    suffix = scope_suffix + ("" if complete else "-provisional")
    report_status = {
        "schema_version": 1,
        **scope,
        "adjudication_complete": complete,
        "pending_adjudication": pending,
        "sample_manifest": str(manifest_path) if manifest_path else None,
        "input_sha256": {
            "labels": hashlib.sha256(args.labels.read_bytes()).hexdigest(),
            "master": hashlib.sha256(args.master.read_bytes()).hexdigest(),
            "sample_manifest": hashlib.sha256(manifest_path.read_bytes()).hexdigest() if manifest_path else None,
        },
        "precision_table_suffix": suffix,
    }
    (out / "report-status.json").write_text(json.dumps(report_status, indent=2) + "\n", encoding="utf-8")

    def scoped(row):
        return {**row, "evidence_scope": scope["evidence_scope"],
                "eligible_for_performance_scoring": False, "adjudication_complete": complete}

    # 4. Precision.
    def tables(items: list[dict], suffix: str) -> tuple[list[dict], list[dict]]:
        fam = [scoped(precision_row("All families", items))] + [
            scoped(precision_row(f, [i for i in items if i["review_family"] == f])) for f in families]
        rules = sorted({i["rule_id"] for i in items})
        rule_rows = [scoped(precision_row(r, [i for i in items if i["rule_id"] == r])) for r in rules]
        for row in rule_rows:
            row["review_family"] = next(i["review_family"] for i in items if i["rule_id"] == row["group"])
        write(out / f"precision-by-family{suffix}.csv", fam)
        write(out / f"precision-by-rule{suffix}.csv", rule_rows)
        return fam, rule_rows

    family_rows, rule_rows = tables(decided, suffix)

    # 5. Carry-over to the later run.
    later_rows = later_family = None
    carry_path = out / "carry-over-to-later-run.csv"
    if args.later_occurrences or carry_path.exists():
        if args.later_occurrences:
            ids, keys = load_later_run(args.later_occurrences)
            for f in finals:
                by_id = f["occurrence_id"] in ids
                by_key = (f["repository"], f["path"], f["line_start"], f["rule_id"]) in keys
                f["in_later_run"] = "yes" if (by_id or by_key) else "no"
                f["matched_by"] = "occurrence_id" if by_id else ("location" if by_key else "")
        else:
            # The later run's raw exports are not in Git; reuse the committed matching.
            matched = {row["issue_id"]: row for row in read(carry_path)}
            for f in finals:
                f["in_later_run"] = matched[f["issue_id"]]["in_later_run"]
                f["matched_by"] = matched[f["issue_id"]]["matched_by"]
        write(carry_path, finals)
        kept = [f for f in decided if f["in_later_run"] == "yes"]
        later_family = [scoped(precision_row("All families", kept))] + [
            scoped(precision_row(fam, [i for i in kept if i["review_family"] == fam])) for fam in families]
        write(out / f"precision-by-family-later-run{suffix}.csv", later_family)
        later_rows = finals
    else:
        write(out / "final-labels.csv", finals)

    # 6. Family-weighted overall precision.
    weighted = None
    if args.rule_profile:
        weights = defaultdict(int)
        for row in read(args.rule_profile):
            weights[row["family"]] += int(row["required_occurrences"] or 0)
        base = later_family or family_rows
        usable = [(r, weights[family_key(r["group"])]) for r in base[1:]
                  if weights.get(family_key(r["group"])) and not math.isnan(r["precision"])]
        total = sum(w for _, w in usable)
        if total:
            estimate = sum(r["precision"] * w for r, w in usable) / total
            variance = sum((w / total) ** 2 * r["precision"] * (1 - r["precision"]) / max(1, r["positive"] + r["negative"])
                           for r, w in usable)
            weighted = (estimate, estimate - 1.96 * math.sqrt(variance), estimate + 1.96 * math.sqrt(variance),
                        [(r["group"], w / total) for r, w in usable])

    # Report.
    state = "complete" if complete else f"in progress: {pending} of {len(finals)} items still need adjudication"
    adj_required = sum(1 for s in sheet if s["priority"].startswith("required"))
    adj_done = sum(1 for s in sheet if s["priority"].startswith("required") and s["issue_id"] in adjudicated)
    lines = ["# RQ1 — agreement and descriptive precision diagnostics\n",
             "Generated by `scripts/rq1_precision.py`; rerun it after editing `adjudication-sheet.csv`.\n",
             f"**Evidence scope: {scope['evidence_scope']}. Population precision: not estimated.**\n",
             f"> {scope['reason']} Completing adjudication does not make these figures final population results. "
             "Uncertain/unreviewable cases, selection weights and evaluation independence require separate analysis.\n",
             f"**Adjudication status: {state}.** Required items adjudicated: {adj_done} of {adj_required}.",
             ("" if complete else "\n> Until adjudication is complete, every precision figure below is **provisional**: it uses "
              "only items where A and B already agree (plus any adjudicated so far). Those are the easier cases, so the "
              "figures are biased and must not be reported as results.\n"),
             (f"\n> Invalid `final_semantic_label` values (use {', '.join(SEMANTIC)}): {', '.join(invalid)}\n" if invalid else ""),
             "## 1. Agreement between Reviewer A and Reviewer B\n",
             "| Group | Items | Semantic agreement | Cohen's κ | Gwet's AC1 | Actionability agreement | κ | AC1 |",
             "|---|---:|---:|---:|---:|---:|---:|---:|"]
    for r in agreement_rows:
        lines.append(f"| {r['group']} | {r['items']} | {pct(r['semantic_agreement'])} | {r['semantic_kappa']:.2f} | "
                     f"{r['semantic_ac1']:.2f} | {pct(r['actionability_agreement'])} | {r['actionability_kappa']:.2f} | "
                     f"{r['actionability_ac1']:.2f} |")
    lines += ["", "Semantic labels, Reviewer A (rows) against Reviewer B (columns):\n",
              "| A \\ B | " + " | ".join(SEMANTIC) + " |", "|---|" + "---:|" * len(SEMANTIC)]
    lines += [f"| {a} | " + " | ".join(str(confusion.get((a, b), 0)) for b in SEMANTIC) + " |" for a in SEMANTIC]
    lines += ["", "κ corrects for chance using each reviewer's own label frequencies; AC1 is more stable when one label "
              "dominates. Common reading: 0.41–0.60 moderate, 0.61–0.80 substantial.\n",
              "## 2. Final labels\n",
              f"- Agreed by A and B: {sum(1 for f in finals if f['final_source'] == 'agreed')}",
              f"- Adjudicated: {sum(1 for f in finals if f['final_source'] == 'adjudicated')}",
              f"- Pending adjudication: {pending}\n",
              f"## 3. Precision{' (provisional)' if not complete else ''}\n",
              "Precision = positive / (positive + negative). Uncertain and unreviewable items are reported, not hidden; the "
              "bounds show the range if every uncertain item were negative or positive.\n",
              "| Family | Items | Pos | Neg | Unc | Unrev | Precision | Wilson 95% | Repo-cluster 95% | Bounds |",
              "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|"]
    for r in family_rows:
        lines.append(f"| {r['group']} | {r['items']} | {r['positive']} | {r['negative']} | {r['uncertain']} | {r['unreviewable']} | "
                     f"{pct(r['precision'])} | {pct(r['wilson_low'])}–{pct(r['wilson_high'])} | "
                     f"{pct(r['cluster_low'])}–{pct(r['cluster_high'])} | "
                     f"{pct(r['bound_uncertain_as_negative'])}–{pct(r['bound_uncertain_as_positive'])} |")
    small = [r for r in rule_rows if r["positive"] + r["negative"] < 5]
    lines += ["", f"Per-rule results are in `precision-by-rule{suffix}.csv` "
              f"({len(rule_rows)} rules; {len(small)} have fewer than 5 decidable items, so their precision is not informative).\n"]
    if later_rows is not None:
        dropped = [f for f in later_rows if f["in_later_run"] == "no"]
        by_label = Counter(f["final_semantic"] or "pending" for f in dropped)
        lines += [f"## 4. Carry-over to {args.later_label}{' (provisional)' if not complete else ''}\n",
                  f"- Pilot items still reported by {args.later_label}: {len(later_rows) - len(dropped)} of {len(later_rows)} "
                  f"(matched by occurrence ID: {sum(1 for f in later_rows if f['matched_by'] == 'occurrence_id')}, "
                  f"by location and rule: {sum(1 for f in later_rows if f['matched_by'] == 'location')}).",
                  f"- No longer reported: {len(dropped)} — by final label: "
                  + ", ".join(f"{k} {v}" for k, v in sorted(by_label.items())) + ".",
                  "- Items no longer reported are excluded below; a dropped negative is a false positive the fixes removed.\n",
                  "| Family | Items | Pos | Neg | Precision | Wilson 95% | Repo-cluster 95% |", "|---|---:|---:|---:|---:|---:|---:|"]
        for r in later_family:
            lines.append(f"| {r['group']} | {r['items']} | {r['positive']} | {r['negative']} | {pct(r['precision'])} | "
                         f"{pct(r['wilson_low'])}–{pct(r['wilson_high'])} | {pct(r['cluster_low'])}–{pct(r['cluster_high'])} |")
        lines.append("")
    if weighted:
        estimate, low, high, shares = weighted
        lines += ["## 5. Exploratory family-reweighted fraction (not population precision)\n",
                  f"Each family's precision weighted by its share of required occurrences in {args.later_label}: "
                  f"**{pct(estimate)}** (approximate 95% interval {pct(low)}–{pct(high)}). Weights: "
                  + ", ".join(f"{g} {100 * s:.1f}%" for g, s in shares) + ".",
                  "Review/history is not in the static-source rule profile and is left out of the weighting. The pilot "
                  "uses unequal within-family sampling and development data; family reweighting alone does not correct "
                  "the sampling design. This remains descriptive even after adjudication.\n"]
    lines += ["## Files\n",
              "- `adjudication-sheet.csv` — fill `final_semantic_label` (and optionally the other final columns) for every "
              "`required` row; see `ADJUDICATION_GUIDE.md`.",
              f"- Current precision tables use suffix `{suffix}`; older differently suffixed files are historical.",
              "- `report-status.json` records evidence scope, eligibility, adjudication and input hashes.",
              "- `agreement.csv`, current precision tables, `carry-over-to-later-run.csv`."]
    (out / "RQ1_RESULTS.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(out / "RQ1_RESULTS.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
