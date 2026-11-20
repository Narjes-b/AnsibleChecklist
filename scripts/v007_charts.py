#!/usr/bin/env python3
"""Pure-Python SVG charts (+ the CSV behind each) for one AnsibleGuard full run.

Every chart is computed from the raw run exports (``aggregate/all-*.csv``, ``tables/runtimes.csv``,
``input/repositories.csv``), never from another summary, so ``scripts/v007_charts_check.py`` can compare the
chart data with the run's own summaries as an independent check. Counts are detector output, not validated defects.
"""
from __future__ import annotations

import argparse
import csv
import html
import math
from pathlib import Path

import pandas as pd

INK, MUTED, GRID, BAR, ALT = "#172033", "#475569", "#e2e8f0", "#2563eb", "#d97706"
STYLE = (f"<style>text{{font-family:system-ui,sans-serif;fill:{INK}}}.title{{font-size:20px;font-weight:700}}"
         f".label{{font-size:12px}}.small{{font-size:10px;fill:{MUTED}}}.grid{{stroke:{GRID};stroke-width:1}}</style>")


def esc(text) -> str:
    return html.escape(str(text), quote=True)


def svg(title: str, width: int, height: int, body: list[str]) -> str:
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" '
            f'role="img" aria-label="{esc(title)}">{STYLE}<rect width="100%" height="100%" fill="white"/><title>{esc(title)}</title>'
            f'<text x="24" y="32" class="title">{esc(title)}</text>' + "".join(body) + "</svg>")


def fmt(value: float) -> str:
    return f"{value:,.0f}" if float(value).is_integer() else f"{value:,.1f}"


def hbar(title: str, labels: list[str], values: list[float], notes: list[str] | None = None, label_w: int = 260) -> str:
    row, top, width = 24, 56, 1000
    plot_w = width - label_w - 150
    peak = max(values) if values and max(values) > 0 else 1
    body = []
    for i, (label, value) in enumerate(zip(labels, values)):
        y = top + i * row
        w = plot_w * value / peak
        body.append(f'<text x="{label_w - 8}" y="{y + 13}" class="label" text-anchor="end">{esc(label)}</text>'
                    f'<rect x="{label_w}" y="{y}" width="{w:.1f}" height="16" fill="{BAR}"/>'
                    f'<text x="{label_w + w + 6:.1f}" y="{y + 13}" class="small">{fmt(value)}{esc(("  " + notes[i]) if notes else "")}</text>')
    return svg(title, width, top + len(labels) * row + 20, body)


def vbar(title: str, labels: list[str], values: list[float], ylabel: str = "repositories") -> str:
    width, height, left, bottom, top = 1000, 460, 70, 90, 60
    plot_w, plot_h = width - left - 30, height - top - bottom
    peak = max(values) if max(values) > 0 else 1
    step = plot_w / len(labels)
    body = [f'<text x="{left - 8}" y="{top - 8}" class="small" text-anchor="end">{esc(ylabel)}</text>']
    for k in range(5):
        y = top + plot_h * k / 4
        body.append(f'<line x1="{left}" x2="{width - 30}" y1="{y:.1f}" y2="{y:.1f}" class="grid"/>'
                    f'<text x="{left - 8}" y="{y + 4:.1f}" class="small" text-anchor="end">{peak * (1 - k / 4):,.0f}</text>')
    for i, (label, value) in enumerate(zip(labels, values)):
        h = plot_h * value / peak
        x = left + i * step + step * 0.15
        body.append(f'<rect x="{x:.1f}" y="{top + plot_h - h:.1f}" width="{step * 0.7:.1f}" height="{h:.1f}" fill="{BAR}"/>'
                    f'<text x="{x + step * 0.35:.1f}" y="{top + plot_h - h - 5:.1f}" class="small" text-anchor="middle">{fmt(value)}</text>'
                    f'<text x="{x + step * 0.35:.1f}" y="{top + plot_h + 16}" class="small" text-anchor="end" '
                    f'transform="rotate(-30 {x + step * 0.35:.1f} {top + plot_h + 16})">{esc(label)}</text>')
    return svg(title, width, height, body)


def scatter(title: str, xs: list[float], ys: list[float], xlabel: str, ylabel: str) -> str:
    width, height, left, bottom, top = 1000, 560, 80, 60, 56
    plot_w, plot_h = width - left - 30, height - top - bottom
    lx = [math.log10(x) for x in xs]
    ly = [math.log10(y + 1) for y in ys]
    x0, x1, y0, y1 = math.floor(min(lx)), math.ceil(max(lx)), 0, math.ceil(max(ly))
    body = [f'<text x="{left + plot_w / 2}" y="{height - 14}" class="label" text-anchor="middle">{esc(xlabel)} (log scale)</text>',
            f'<text x="18" y="{top + plot_h / 2}" class="label" text-anchor="middle" transform="rotate(-90 18 {top + plot_h / 2})">{esc(ylabel)} (log scale, +1)</text>']
    for e in range(x0, x1 + 1):
        x = left + plot_w * (e - x0) / (x1 - x0)
        body.append(f'<line x1="{x:.1f}" x2="{x:.1f}" y1="{top}" y2="{top + plot_h}" class="grid"/><text x="{x:.1f}" y="{top + plot_h + 16}" class="small" text-anchor="middle">{10 ** e:,}</text>')
    for e in range(y0, y1 + 1):
        y = top + plot_h - plot_h * (e - y0) / (y1 - y0)
        body.append(f'<line x1="{left}" x2="{width - 30}" y1="{y:.1f}" y2="{y:.1f}" class="grid"/><text x="{left - 8}" y="{y + 4:.1f}" class="small" text-anchor="end">{10 ** e - 1 if e else 0:,}</text>')
    for a, b in zip(lx, ly):
        body.append(f'<circle cx="{left + plot_w * (a - x0) / (x1 - x0):.1f}" cy="{top + plot_h - plot_h * (b - y0) / (y1 - y0):.1f}" r="3.2" fill="{BAR}" fill-opacity="0.55"/>')
    return svg(title, width, height, body)


def heatmap(title: str, rows: list[str], cols: list[str], matrix: list[list[float]]) -> str:
    cell, left, top = 26, 230, 190
    width, height = max(1000, left + len(cols) * cell + 200), top + len(rows) * cell + 20
    peak = max(max(r) for r in matrix) or 1
    body = []
    for j, col in enumerate(cols):
        x = left + j * cell + cell / 2
        body.append(f'<text x="{x:.1f}" y="{top - 8}" class="small" transform="rotate(-60 {x:.1f} {top - 8})">{esc(col.split("/")[-1])}</text>')
    for i, row in enumerate(rows):
        y = top + i * cell
        body.append(f'<text x="{left - 8}" y="{y + 17}" class="small" text-anchor="end">{esc(row)}</text>')
        for j, value in enumerate(matrix[i]):
            shade = math.log10(value + 1) / math.log10(peak + 1)
            body.append(f'<rect x="{left + j * cell}" y="{y}" width="{cell - 1}" height="{cell - 1}" fill="rgb({int(255 - 217 * shade)},{int(255 - 150 * shade)},255)"><title>{esc(row)} / {esc(col)}: {fmt(value)}</title></rect>')
    return svg(title, width, height, body)


def write(out: Path, name: str, svg_text: str, frame: pd.DataFrame) -> None:
    (out / f"{name}.svg").write_text(svg_text, encoding="utf-8")
    frame.to_csv(out / "data" / f"{name}.csv", index=False)


def binned(values, edges: list[float], names: list[str]) -> list[int]:
    counts = [0] * len(names)
    for v in values:
        for i in range(len(names)):
            if v >= edges[i] and (i == len(names) - 1 or v < edges[i + 1]):
                counts[i] += 1
                break
    return counts


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    run, out = args.run, args.output_dir
    (out / "data").mkdir(parents=True, exist_ok=True)
    agg = run / "aggregate"
    src = pd.read_csv(agg / "all-internal-source-occurrences.csv", usecols=["project", "rule_id", "severity", "certainty", "confidence", "policy", "actionability"], low_memory=False)
    raw = pd.read_csv(agg / "all-raw-findings.csv", usecols=["provider", "project"], low_memory=False)
    canon = pd.read_csv(agg / "all-canonical-occurrences.csv", usecols=["provider", "project", "provider_comparison_eligible"], low_memory=False)
    repos = pd.read_csv(agg / "repository-summary.csv", usecols=["project", "scan_status", "ansible_lint_status", "gitleaks_status", "selected_loc"])
    repos = repos[repos["scan_status"] != "aggregate"].reset_index(drop=True)  # the file ends with a totals row
    runtimes = pd.read_csv(run / "tables" / "runtimes.csv")
    n_target = len(repos)
    per_repo = src.groupby("project").size()
    loc = repos.set_index("project")["selected_loc"]
    analyz = sorted(repos.loc[repos["scan_status"] == "existing", "project"])
    n_an = len(analyz)
    counts = pd.Series({p: int(per_repo.get(p, 0)) for p in analyz})
    nr = src["rule_id"].nunique()

    status = repos.assign(state=lambda d: d.apply(lambda r: "complete" if r.ansible_lint_status == "completed" and r.gitleaks_status == "completed" else ("partial" if r.scan_status == "existing" else "failed"), axis=1))["state"].value_counts()
    write(out, "01-repository-execution-status", vbar(f"Repository execution status ({n_target} targeted repositories)", list(status.index), list(status.values)), status.rename_axis("status").reset_index(name="repositories"))

    d = pd.DataFrame({"measure": ["raw findings", "canonical occurrences"], "count": [len(raw), len(canon)]})
    write(out, "02-raw-vs-canonical", hbar("Raw findings versus canonical occurrences (all providers)", list(d["measure"]), list(d["count"]), label_w=200), d)

    prov = canon.groupby("provider").size().sort_values(ascending=False)
    write(out, "03-findings-by-provider", hbar("Canonical findings by provider (populations differ; do not compare bars)", list(prov.index), list(prov.values), label_w=160), prov.rename_axis("provider").reset_index(name="findings"))

    rules = src.groupby("rule_id").agg(occurrences=("rule_id", "size"), repositories=("project", "nunique")).sort_values("occurrences", ascending=False)
    top = rules.head(25)
    write(out, "04-top-rules", hbar(f"AnsibleGuard static-source occurrences by rule ({n_an} analyzable repositories) — top 25 of {nr}", [r.split("/")[-1] for r in top.index], list(top["occurrences"])), rules.reset_index())
    req = src[src["policy"] == "required"].groupby("rule_id").agg(occurrences=("rule_id", "size"), repositories=("project", "nunique")).sort_values("occurrences", ascending=False)
    t2 = req.head(25)
    write(out, "04b-top-required-rules", hbar(f"Required-policy occurrences by rule (per occurrence) — top 25 of {len(req)} rules", [r.split("/")[-1] for r in t2.index], list(t2["occurrences"])), req.reset_index())
    prev = rules.sort_values("repositories", ascending=False).head(25)
    write(out, "05-rule-prevalence", hbar(f"Rule prevalence: repositories affected out of {n_an} analyzable repositories — top 25 of {nr}", [r.split("/")[-1] for r in prev.index], list(prev["repositories"])), rules.sort_values("repositories", ascending=False).reset_index())

    names = ["0–9", "10–49", "50–99", "100–249", "250–499", "500–999", "1000–2499", "2500–4999", "5000+"]
    c = binned(counts.values, [0, 10, 50, 100, 250, 500, 1000, 2500, 5000], names)
    write(out, "06-findings-per-repository-distribution", vbar(f"Repositories by static-source occurrence count ({n_an} analyzable repositories)", names, c), pd.DataFrame({"bin": names, "repositories": c}))
    dens = pd.Series({p: counts[p] / loc[p] * 1000 for p in analyz if loc.get(p, 0) and loc[p] > 0})
    dn = ["0 to <25", "25 to <50", "50 to <100", "100 to <150", "150 to <200", "200 to <300", "300+"]
    dc = binned(dens.values, [0, 25, 50, 100, 150, 200, 300], dn)
    write(out, "07-findings-density", vbar(f"Repositories by static-source occurrences per 1,000 selected Ansible LOC ({len(dens)} repositories with LOC)", dn, dc), pd.DataFrame({"bin": dn, "repositories": dc}))

    for number, col, label in (("08", "severity", "severity"), ("09", "confidence", "detector confidence"), ("10", "certainty", "resolution certainty"), ("11", "actionability", "actionability")):
        s = src[col].value_counts()
        write(out, f"{number}-{col}-distribution", hbar(f"AnsibleGuard static-source occurrences by {label}", list(s.index), list(s.values), [f"{v / len(src) * 100:.1f}%" for v in s.values], label_w=160), s.rename_axis(col).reset_index(name="findings"))

    comp = repos.apply(lambda r: "core and optional providers complete" if r.ansible_lint_status == "completed" and r.gitleaks_status == "completed" else ("core result missing" if r.scan_status != "existing" else "core complete; optional provider incomplete"), axis=1).value_counts()
    write(out, "12-provider-completeness", vbar(f"Exclusive provider-completeness states ({n_target} repositories)", list(comp.index), list(comp.values)), comp.rename_axis("state").reset_index(name="repositories"))

    rt = runtimes["duration_seconds"]
    edges = list(range(0, 300, 60))
    rn = [f"{e}-{e + 59}" for e in edges] + ["300+"]
    rc = binned(rt.values, edges + [300], rn)
    write(out, "13-runtime-distribution", vbar("Repository runtime distribution (seconds)", rn, rc), pd.DataFrame({"duration_seconds_bin": rn, "repositories": rc}))

    sc = pd.DataFrame({"repository": analyz, "selected_loc": [loc.get(p, 0) for p in analyz], "internal_source_occurrences": [counts[p] for p in analyz]})
    sc = sc[sc["selected_loc"] > 0]
    write(out, "14-repository-size-vs-findings", scatter(f"Selected Ansible LOC versus AnsibleGuard static-source occurrences ({len(sc)} repositories with LOC)", list(sc["selected_loc"]), list(sc["internal_source_occurrences"]), "selected LOC", "occurrences"), sc)

    topr = list(counts.sort_values(ascending=False).head(30).index)
    toprules = list(rules.head(20).index)
    pivot = src.groupby(["project", "rule_id"]).size().unstack(fill_value=0).reindex(index=topr, columns=toprules, fill_value=0)
    write(out, "15-rule-repository-heatmap", heatmap("AnsibleGuard static-source rule × repository heatmap (30 largest repositories, 20 top rules)", topr, toprules, pivot.values.tolist()), pivot.reset_index())

    ex = pd.DataFrame({"mapping_status": ["not-modelled"], "note": ["No explicit equivalence mapping is defined; overlap is not estimable."]})
    write(out, "16-external-tool-overlap", svg("External-tool overlap", 1000, 120, [f'<text x="24" y="70" class="label">{esc(ex.note[0])}</text>']), ex)
    print(f"wrote 17 charts to {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
