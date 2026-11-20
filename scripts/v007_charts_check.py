#!/usr/bin/env python3
"""Independent check of v007_charts.py data against the run's OWN summaries (different code path)."""
import json, sys
from pathlib import Path
import pandas as pd

run, charts = Path(sys.argv[1]), Path(sys.argv[2]) / "data"
agg = run / "aggregate"
summ = json.loads((agg / "aggregate-summary.json").read_text())
bad = []

def check(name, got, want):
    ok = got == want
    print(("ok   " if ok else "FAIL ") + f"{name}: chart={got} summary={want}")
    if not ok:
        bad.append(name)

rd = lambda n: pd.read_csv(charts / n)
d = rd("02-raw-vs-canonical.csv").set_index("measure")["count"]
check("raw findings", int(d["raw findings"]), summ["raw_findings"])
check("canonical", int(d["canonical occurrences"]), summ["canonical_occurrences"])
p = rd("03-findings-by-provider.csv").set_index("provider")["findings"]
check("ansibleguard provider", int(p["ansibleguard"]), summ["internal_occurrences"])
check("ansible-lint provider", int(p["ansible-lint"]), summ["ansible_lint_occurrences"])
check("gitleaks provider", int(p["gitleaks"]), summ["gitleaks_occurrences"])
tot = {n: int(rd(n).iloc[:, 1].sum()) for n in ("08-severity-distribution.csv", "09-confidence-distribution.csv", "10-certainty-distribution.csv", "11-actionability-distribution.csv")}
for n, t in tot.items():
    check(n + " sums to internal source", t, summ["internal_source_occurrences"])
check("uncertain", int(rd("10-certainty-distribution.csv").set_index("certainty").loc["UNCERTAIN", "findings"]), summ["uncertain_occurrences"])
rules = pd.read_csv(agg / "rule-summary-internal.csv").set_index("rule_id")
t4 = rd("04-top-rules.csv").set_index("rule_id")
src_rules = rules[rules.index.isin(t4.index)]
common = t4.index.intersection(rules.index)
check("rule counts vs rule-summary-internal (rules in both)", {r: int(t4.loc[r, "occurrences"]) for r in common if rules.loc[r, "findings"] != t4.loc[r, "occurrences"]}, {})
check("rules with occurrences", len(t4), int((rules["findings"] > 0).sum()))
check("repositories sum", int(rd("06-findings-per-repository-distribution.csv")["repositories"].sum()), summ["analyzable_repositories"])
check("density sum", int(rd("07-findings-density.csv")["repositories"].sum()), summ["analyzable_repositories"])
check("scatter rows", len(rd("14-repository-size-vs-findings.csv")), summ["analyzable_repositories"])
check("scatter total", int(rd("14-repository-size-vs-findings.csv")["internal_source_occurrences"].sum()), summ["internal_source_occurrences"])
check("runtime sum", int(rd("13-runtime-distribution.csv")["repositories"].sum()), summ["repositories"])
check("status", rd("01-repository-execution-status.csv").set_index("status")["repositories"].to_dict(), {"complete": 171, "partial": 35, "failed": summ["failed_repositories"]})
req = rd("04b-top-required-rules.csv")
check("required total", int(req["occurrences"].sum()), int(pd.read_csv(agg / "all-internal-source-occurrences.csv", usecols=["policy"])["policy"].eq("required").sum()))
print("FAILED:", bad or "none"); sys.exit(1 if bad else 0)
