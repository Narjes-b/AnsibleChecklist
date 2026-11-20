#!/usr/bin/env python3
"""RQ2: which AnsibleGuard rules co-occur, at file and repository level.

Follows the co-occurrence method of Bessghaier et al. (SANER'24): association
rules (support, confidence, lift) and 2x2 association tests (Pearson
chi-squared, Benjamini-Hochberg q-values, Cramer's V). Two corrections over a
plain transaction count:

* Every analysed file is a transaction, including files with no finding.
  Counting only files with findings inflates every co-occurrence.
* Larger files trigger more rules, so two rules can co-occur only because
  both fire in big files. The Mantel-Haenszel odds ratio across file-size
  strata (lines-of-code quantiles) estimates the association within files of
  similar size; a pair whose adjusted odds ratio interval includes 1 is
  explained by file size.

Inputs are a run's ``aggregate/all-internal-source-occurrences.csv``, its
``aggregate/repository-summary.csv`` and the frozen per-file manifests.
Counts are detector output, not validated defects.
"""

from __future__ import annotations

import argparse
import csv
import glob
import math
from collections import defaultdict
from itertools import combinations
from pathlib import Path

POLICIES = {"required": {"required"}, "all": {"required", "optional"}}


def chi2_2x2(a: int, b: int, c: int, d: int) -> tuple[float, float]:
    """Pearson chi-squared (df=1) and its p-value for [[a, b], [c, d]]."""
    n = a + b + c + d
    rows, cols = (a + b, c + d), (a + c, b + d)
    if n == 0 or 0 in rows or 0 in cols:
        return float("nan"), float("nan")
    chi2 = n * (a * d - b * c) ** 2 / (rows[0] * rows[1] * cols[0] * cols[1])
    return chi2, math.erfc(math.sqrt(chi2 / 2))


def phi(a: int, b: int, c: int, d: int) -> float:
    """Signed phi coefficient; |phi| is Cramer's V for a 2x2 table."""
    denominator = math.sqrt((a + b) * (c + d) * (a + c) * (b + d))
    return (a * d - b * c) / denominator if denominator else float("nan")


def mantel_haenszel(strata: list[tuple[int, int, int, int]]) -> tuple[float, float, float, float]:
    """Mantel-Haenszel common odds ratio, its 95% CI (Robins-Breslow-Greenland)
    and the MH chi-squared p-value (continuity-corrected) over 2x2 strata."""
    sum_r = sum_s = sum_pr = sum_ps_qr = sum_qs = 0.0
    observed = expected = variance = 0.0
    for a, b, c, d in strata:
        n = a + b + c + d
        if n < 2:
            continue
        r, s = a * d / n, b * c / n
        p, q = (a + d) / n, (b + c) / n
        sum_r, sum_s = sum_r + r, sum_s + s
        sum_pr += p * r
        sum_ps_qr += p * s + q * r
        sum_qs += q * s
        observed += a
        expected += (a + b) * (a + c) / n
        variance += (a + b) * (c + d) * (a + c) * (b + d) / (n * n * (n - 1))
    if sum_r == 0 or sum_s == 0:
        odds = float("inf") if sum_r > 0 else float("nan")
        return odds, float("nan"), float("nan"), float("nan")
    odds = sum_r / sum_s
    var_log = sum_pr / (2 * sum_r ** 2) + sum_ps_qr / (2 * sum_r * sum_s) + sum_qs / (2 * sum_s ** 2)
    half = 1.96 * math.sqrt(var_log)
    chi2 = (abs(observed - expected) - 0.5) ** 2 / variance if variance else float("nan")
    p_value = math.erfc(math.sqrt(chi2 / 2)) if variance else float("nan")
    return odds, math.exp(math.log(odds) - half), math.exp(math.log(odds) + half), p_value


def benjamini_hochberg(p_values: list[float]) -> list[float]:
    order = sorted((p, i) for i, p in enumerate(p_values) if not math.isnan(p))
    q = [float("nan")] * len(p_values)
    running = 1.0
    for rank in range(len(order), 0, -1):
        p, i = order[rank - 1]
        running = min(running, p * len(order) / rank)
        q[i] = running
    return q


def quantile_strata(sizes: list[int], count: int) -> list[int]:
    """Assign each transaction to one of ``count`` size strata by rank."""
    order = sorted(range(len(sizes)), key=lambda i: sizes[i])
    strata = [0] * len(sizes)
    for rank, index in enumerate(order):
        strata[index] = min(count - 1, rank * count // len(sizes))
    return strata


def load(occurrences: Path, repository_summary: Path, manifests: Path):
    analysable = set()
    with repository_summary.open(newline="", encoding="utf-8") as source:
        for row in csv.DictReader(source):
            # "existing" marks a completed scan whose stored result was aggregated.
            if row.get("scan_status") in {"completed", "existing"}:
                analysable.add(row["project"])
    files: dict[tuple[str, str], int] = {}
    for path in sorted(glob.glob(str(manifests / "*.csv"))):
        with open(path, newline="", encoding="utf-8") as source:
            for row in csv.DictReader(source):
                if row["included"] == "true" and row["project"] in analysable:
                    files[(row["project"], row["path"])] = int(row["loc"] or 0)
    items = {name: defaultdict(set) for name in POLICIES}
    unmatched = 0
    with occurrences.open(newline="", encoding="utf-8") as source:
        for row in csv.DictReader(source):
            key = (row["project"], row["file"])
            if key not in files:
                unmatched += 1
                continue
            for name, allowed in POLICIES.items():
                if row["policy"] in allowed:
                    items[name][key].add(row["rule_id"].split("/", 1)[-1])
    return analysable, files, items, unmatched


def pair_table(transactions: list[set[str]], strata: list[int] | None, strata_count: int, min_pair: int) -> list[dict]:
    n = len(transactions)
    masks: dict[str, int] = defaultdict(int)
    for index, rules in enumerate(transactions):
        for rule in rules:
            masks[rule] |= 1 << index
    stratum_masks = []
    if strata is not None:
        stratum_masks = [0] * strata_count
        for index, stratum in enumerate(strata):
            stratum_masks[stratum] |= 1 << index
    rows = []
    for x, y in combinations(sorted(masks), 2):
        both = (masks[x] & masks[y]).bit_count()
        if both < min_pair:
            continue
        nx, ny = masks[x].bit_count(), masks[y].bit_count()
        a, b, c = both, nx - both, ny - both
        d = n - a - b - c
        chi2, p = chi2_2x2(a, b, c, d)
        row = {
            "rule_a": x, "rule_b": y, "transactions": n, "count_a": nx, "count_b": ny, "count_both": both,
            "support": both / n, "confidence_a_to_b": both / nx, "confidence_b_to_a": both / ny,
            "lift": both * n / (nx * ny), "chi2": chi2, "p_value": p, "phi": phi(a, b, c, d),
            "cramers_v": abs(phi(a, b, c, d)),
        }
        if stratum_masks:
            tables = []
            for mask in stratum_masks:
                sa = (masks[x] & masks[y] & mask).bit_count()
                sx, sy, sn = (masks[x] & mask).bit_count(), (masks[y] & mask).bit_count(), mask.bit_count()
                tables.append((sa, sx - sa, sy - sa, sn - sx - sy + sa))
            odds, low, high, mh_p = mantel_haenszel(tables)
            row.update({"mh_odds_ratio": odds, "mh_ci_low": low, "mh_ci_high": high, "mh_p_value": mh_p})
        rows.append(row)
    for key in ("p_value", "mh_p_value"):
        if rows and key in rows[0]:
            for row, q in zip(rows, benjamini_hochberg([r[key] for r in rows])):
                row[key.replace("p_value", "q_value")] = q
    return rows


def classify(row: dict) -> str:
    """Plain-language verdict used in the summary tables."""
    if not (row["q_value"] < 0.05 and row["lift"] > 1):
        return "not associated"
    if row.get("mh_odds_ratio") == float("inf"):
        return "nested"
    if "mh_ci_low" in row and not (row["mh_ci_low"] > 1 and row.get("mh_q_value", 0) < 0.05):
        return "explained by file size"
    return "associated" if row["cramers_v"] >= 0.1 else "associated (negligible effect)"


def write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    with path.open("w", newline="", encoding="utf-8") as target:
        writer = csv.DictWriter(target, fieldnames=list(rows[0]))
        writer.writeheader()
        for row in rows:
            writer.writerow({k: (f"{v:.6g}" if isinstance(v, float) else v) for k, v in row.items()})


def fmt(value: float, digits: int = 2) -> str:
    return "n/a" if value is None or (isinstance(value, float) and math.isnan(value)) else f"{value:.{digits}f}"


def association_table(rows: list[dict], tagged: bool) -> list[str]:
    lines = ["| Rule A | Rule B | Same family | Files both | Support % | Conf A→B | Conf B→A | Lift | V | OR | MH OR (95% CI) |",
             "|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|"]
    for r in rows:
        raw_or = (r["count_both"] * (r["transactions"] - r["count_a"] - r["count_b"] + r["count_both"])) / max(
            1, (r["count_a"] - r["count_both"]) * (r["count_b"] - r["count_both"]))
        same = ("yes" if r["same_family"] else "no") if tagged else "n/a"
        lines.append(f"| {r['rule_a']} | {r['rule_b']} | {same} | {r['count_both']:,} | {100 * r['support']:.2f} | "
                     f"{fmt(r['confidence_a_to_b'])} | {fmt(r['confidence_b_to_a'])} | {fmt(r['lift'])} | "
                     f"{fmt(r['cramers_v'], 3)} | {fmt(raw_or)} | {fmt(r['mh_odds_ratio'])} "
                     f"({fmt(r['mh_ci_low'])}–{fmt(r['mh_ci_high'])}) |")
    return lines


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--occurrences", type=Path, required=True)
    parser.add_argument("--repository-summary", type=Path, required=True)
    parser.add_argument("--manifests", type=Path, default=Path("study/manifests/file-classification-v007-207"))
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--strata", type=int, default=5, help="file-size strata (LOC quantiles)")
    parser.add_argument("--min-pair-files", type=int, default=30)
    parser.add_argument("--min-pair-repositories", type=int, default=10)
    parser.add_argument("--run-label", default="")
    parser.add_argument("--rule-profile", type=Path, default=None,
                        help="rule-profile.csv from v007_results_analysis.py, to tag each rule's category and review family")
    args = parser.parse_args(argv)
    args.output_dir.mkdir(parents=True, exist_ok=True)

    analysable, files, items, unmatched = load(args.occurrences, args.repository_summary, args.manifests)
    keys = sorted(files)
    sizes = [files[k] for k in keys]
    strata = quantile_strata(sizes, args.strata)
    bounds = []
    for s in range(args.strata):
        members = [sizes[i] for i in range(len(keys)) if strata[i] == s]
        bounds.append((min(members), max(members), len(members)))
    projects = sorted({p for p, _ in keys})

    family: dict[str, tuple[str, str]] = {}
    if args.rule_profile:
        with args.rule_profile.open(newline="", encoding="utf-8") as source:
            for row in csv.DictReader(source):
                family[row["rule_id"].split("/", 1)[-1]] = (row["category"], row["family"])

    results = {}
    for name in POLICIES:
        file_tx = [items[name].get(k, set()) for k in keys]
        repo_rules: dict[str, set[str]] = defaultdict(set)
        for (project, _), rules in items[name].items():
            repo_rules[project] |= rules
        repo_tx = [repo_rules.get(p, set()) for p in projects]
        file_rows = pair_table(file_tx, strata, args.strata, args.min_pair_files)
        repo_rows = pair_table(repo_tx, None, 0, args.min_pair_repositories)
        for row in file_rows + repo_rows:
            row["verdict"] = classify(row)
            fa, fb = family.get(row["rule_a"], ("", "")), family.get(row["rule_b"], ("", ""))
            row.update({"category_a": fa[0], "category_b": fb[0], "family_a": fa[1], "family_b": fb[1],
                        "same_family": bool(fa[1]) and fa[1] == fb[1]})
        file_rows.sort(key=lambda r: (-r["cramers_v"] if not math.isnan(r["cramers_v"]) else 0))
        repo_rows.sort(key=lambda r: (-r["cramers_v"] if not math.isnan(r["cramers_v"]) else 0))
        write_csv(args.output_dir / f"rq2-file-pairs-{name}.csv", file_rows)
        write_csv(args.output_dir / f"rq2-repository-pairs-{name}.csv", repo_rows)
        support = []
        for rule in sorted({r for tx in file_tx for r in tx}):
            nf = sum(1 for tx in file_tx if rule in tx)
            nr = sum(1 for tx in repo_tx if rule in tx)
            support.append({"rule": rule, "files": nf, "file_support": nf / len(file_tx),
                            "repositories": nr, "repository_support": nr / len(repo_tx)})
        support.sort(key=lambda r: -r["files"])
        write_csv(args.output_dir / f"rq2-rule-support-{name}.csv", support)
        results[name] = (file_tx, file_rows, repo_rows, support)

    lines = [f"# RQ2 rule co-occurrence{(' — ' + args.run_label) if args.run_label else ''}\n",
             "Generated by `scripts/rq2_cooccurrence.py`. Counts are detector output, not validated defects.\n",
             "## Population\n",
             f"- Analysable repositories: {len(projects)} (repositories whose scan completed).",
             f"- Transactions: {len(keys):,} analysed files (every included file, with or without findings); "
             f"{unmatched} occurrences did not match a manifest file.",
             "- File-size strata (lines of code): " + "; ".join(f"S{i + 1} {lo}–{hi} ({n:,} files)" for i, (lo, hi, n) in enumerate(bounds)) + ".",
             f"- A pair is tested when the two rules share at least {args.min_pair_files} files "
             f"(file level) or {args.min_pair_repositories} repositories (repository level).\n",
             "## How to read the verdicts\n",
             "- **associated**: lift > 1, BH q < 0.05, the size-adjusted Mantel–Haenszel odds-ratio interval lies above 1 "
             "(q < 0.05), and Cramér's V ≥ 0.1.",
             "- **associated (negligible effect)**: significant and size-robust, but V < 0.1.",
             "- **nested**: within every file-size stratum one rule never fires without the other "
             "(usually one rule's condition contains the other's).",
             "- **explained by file size**: significant overall, but not once file size is held constant.",
             "- **not associated**: lift ≤ 1 or not significant.\n"]
    tagged = bool(family)
    for name, title in (("required", "Required rules only"), ("all", "All rules (required and optional)")):
        file_tx, file_rows, repo_rows, support = results[name]
        verdicts = defaultdict(int)
        for row in file_rows:
            verdicts[row["verdict"]] += 1
        with_any = sum(1 for tx in file_tx if tx)
        with_two = sum(1 for tx in file_tx if len(tx) >= 2)
        lines += [f"## {title}\n",
                  f"- Files with at least one rule: {with_any:,} of {len(file_tx):,} ({100 * with_any / len(file_tx):.1f}%); "
                  f"with two or more distinct rules: {with_two:,} ({100 * with_two / len(file_tx):.1f}%).",
                  f"- Rules observed: {len(support)}. Pairs tested at file level: {len(file_rows):,} — "
                  + ", ".join(f"{k or 'other'} {v:,}" for k, v in sorted(verdicts.items(), key=lambda kv: -kv[1])) + ".\n",
                  "**Strongest size-robust file-level associations** (top 15 by Cramér's V):\n"]
        associated = [r for r in file_rows if r["verdict"] == "associated"]
        lines += association_table(associated[:15], tagged)
        if tagged:
            cross = [r for r in associated if not r["same_family"]]
            lines += ["", f"**Strongest size-robust associations across review families** ({len(cross)} of "
                      f"{len(associated)} associated pairs). Same-family rules often share a measurement (for example "
                      "playbook size) and overlap by construction, so these cross-family pairs are the stronger evidence "
                      "of related problems:\n"]
            lines += association_table(cross[:15], tagged)
        nested = [r for r in file_rows if r["verdict"] == "nested"]
        if nested:
            lines += ["", "**Nested pairs**:\n", "| Rule A | Rule B | Files both | Files A | Files B |", "|---|---|---:|---:|---:|"]
            lines += [f"| {r['rule_a']} | {r['rule_b']} | {r['count_both']:,} | {r['count_a']:,} | {r['count_b']:,} |"
                      for r in nested]
        explained = [r for r in file_rows if r["verdict"] == "explained by file size"][:10]
        if explained:
            lines += ["", "**Significant overall but explained by file size** (examples):\n",
                      "| Rule A | Rule B | Lift | V | MH OR (95% CI) |", "|---|---|---:|---:|---:|"]
            lines += [f"| {r['rule_a']} | {r['rule_b']} | {fmt(r['lift'])} | {fmt(r['cramers_v'], 3)} | "
                      f"{fmt(r['mh_odds_ratio'])} ({fmt(r['mh_ci_low'])}–{fmt(r['mh_ci_high'])}) |" for r in explained]
        repo_assoc = [r for r in repo_rows if r["verdict"].startswith("associated")][:10]
        lines += ["", f"**Repository level**: {len(repo_rows):,} pairs tested; "
                  f"{sum(1 for r in repo_rows if r['verdict'].startswith('associated'))} associated. Top 10 by V:\n",
                  "| Rule A | Rule B | Repos both | Lift | V | q |", "|---|---|---:|---:|---:|---:|"]
        lines += [f"| {r['rule_a']} | {r['rule_b']} | {r['count_both']} | {fmt(r['lift'])} | {fmt(r['cramers_v'], 3)} | "
                  f"{r['q_value']:.2g} |" for r in repo_assoc]
        lines.append("")
    lines += ["## Files\n",
              "- `rq2-file-pairs-{required,all}.csv`: every tested file-level pair with all measures and its verdict.",
              "- `rq2-repository-pairs-{required,all}.csv`: the same at repository level (no size adjustment).",
              "- `rq2-rule-support-{required,all}.csv`: how many files and repositories each rule appears in.\n",
              "## Limits\n",
              "- Co-occurrence is association, not causation, and is measured on detector output whose precision is not yet known (RQ1).",
              "- Repository-level results have only ~200 transactions and many near-universal rules, so file level is the primary unit.",
              "- File size is the only confounder adjusted for; role structure and repository style can also link rules.",
              "- Rules of the same review family often measure the same property, so part of their co-occurrence is by "
              "construction (see the cross-family table)."]
    (args.output_dir / "RQ2_RESULTS.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(args.output_dir / "RQ2_RESULTS.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
