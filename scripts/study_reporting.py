"""Dependency-light tables and charts for reproducible repository studies."""

from __future__ import annotations

import csv
import html
import math
from pathlib import Path


PALETTE = (
    "#2563eb", "#dc2626", "#16a34a", "#d97706", "#7c3aed",
    "#0891b2", "#db2777", "#65a30d", "#4f46e5", "#64748b",
)


def read_csv(path: Path) -> list[dict[str, str]]:
    with Path(path).open(newline="", encoding="utf-8") as stream:
        return list(csv.DictReader(stream))


def write_csv(path: Path, rows: list[dict], fields: list[str] | None = None) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    if fields is None:
        fields = list(dict.fromkeys(key for row in rows for key in row))
    temporary = path.with_name(f".{path.name}.tmp")
    with temporary.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)
    temporary.replace(path)


def markdown_table(rows: list[dict], fields: list[str], limit: int | None = None) -> str:
    shown = rows if limit is None else rows[:limit]
    if not shown:
        return "_No rows._\n"
    labels = [field.replace("_", " ").title() for field in fields]
    lines = [
        "| " + " | ".join(labels) + " |",
        "|" + "|".join("---" for _ in fields) + "|",
    ]
    for row in shown:
        values = []
        for field in fields:
            value = str(row.get(field, "")).replace("|", "\\|").replace("\n", " ")
            values.append(value)
        lines.append("| " + " | ".join(values) + " |")
    return "\n".join(lines) + "\n"


def _svg(path: Path, width: int, height: int, body: str, title: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    document = (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" role="img" aria-label="{html.escape(title)}">'
        '<style>text{font-family:system-ui,sans-serif;fill:#172033}'
        '.title{font-size:20px;font-weight:700}.label{font-size:12px}'
        '.small{font-size:10px;fill:#475569}.grid{stroke:#e2e8f0;stroke-width:1}</style>'
        f'<rect width="100%" height="100%" fill="white"/><title>{html.escape(title)}</title>'
        f'{body}</svg>'
    )
    path.write_text(document, encoding="utf-8")


# Meaningful colours for ordinal categories; everything else uses one colour so
# that colour never suggests a meaning the data does not have.
SEMANTIC_COLORS = {
    "error": "#dc2626", "blocking": "#dc2626", "warning": "#d97706", "actionable": "#d97706",
    "note": "#64748b", "advisory": "#64748b", "informational": "#94a3b8",
    "high": "#1d4ed8", "medium": "#60a5fa", "low": "#bfdbfe",
}
SINGLE_SERIES_COLOR = "#2563eb"


def format_value(value: float) -> str:
    return f"{value:,.0f}" if float(value).is_integer() else f"{value:,.2f}"


def bar_chart(path: Path, rows: list[tuple[str, float]], title: str, *, limit=25,
              order: str = "value", semantic_colors: bool = False, subtitle: str = "") -> None:
    """Horizontal bar chart.

    ``order="value"`` ranks bars (top-N charts); ``order="given"`` keeps the
    caller's order, which bins and ordinal scales require. ``limit=None``
    draws every row; when rows are dropped the title says so.
    """
    total_rows = len(rows)
    if order == "value":
        rows = sorted(rows, key=lambda item: (-item[1], item[0]))
    rows = rows if limit is None else rows[:limit]
    if len(rows) < total_rows:
        title = f"{title} — top {len(rows)} of {total_rows}"
    width = 1000
    row_height = 27
    height = max(180, 90 + row_height * len(rows))
    left, right, top = 310, 80, 58
    plot_width = width - left - right
    maximum = max((value for _label, value in rows), default=1) or 1
    body = [f'<text x="24" y="32" class="title">{html.escape(title)}</text>']
    if subtitle:
        body.append(f'<text x="24" y="50" class="small">{html.escape(subtitle)}</text>')
        top += 10
        height += 10
    for index, (label, value) in enumerate(rows):
        y = top + index * row_height
        bar_width = plot_width * value / maximum
        color = SEMANTIC_COLORS.get(label.lower(), SINGLE_SERIES_COLOR) if semantic_colors else SINGLE_SERIES_COLOR
        body.append(
            f'<text x="{left - 8}" y="{y + 15}" text-anchor="end" class="label">'
            f'{html.escape(label[:52])}</text>'
            f'<rect x="{left}" y="{y}" width="{bar_width:.2f}" height="18" '
            f'rx="2" fill="{color}"/>'
            f'<text x="{left + bar_width + 6:.2f}" y="{y + 14}" class="label">'
            f'{format_value(value)}</text>'
        )
    _svg(path, width, height, "".join(body), title)


def pie_chart(path: Path, rows: list[tuple[str, float]], title: str, *, limit=10) -> None:
    ordered = sorted(((label, value) for label, value in rows if value > 0),
                     key=lambda item: (-item[1], item[0]))
    if len(ordered) > limit:
        ordered = ordered[: limit - 1] + [("Other", sum(v for _l, v in ordered[limit - 1:]))]
    total = sum(value for _label, value in ordered)
    width, height = 900, 500
    cx, cy, radius = 230, 265, 170
    body = [f'<text x="24" y="32" class="title">{html.escape(title)}</text>']
    angle = -math.pi / 2
    for index, (label, value) in enumerate(ordered):
        fraction = value / total if total else 0
        next_angle = angle + 2 * math.pi * fraction
        x1, y1 = cx + radius * math.cos(angle), cy + radius * math.sin(angle)
        x2, y2 = cx + radius * math.cos(next_angle), cy + radius * math.sin(next_angle)
        large = 1 if fraction > 0.5 else 0
        color = PALETTE[index % len(PALETTE)]
        if fraction >= 0.999999:
            body.append(f'<circle cx="{cx}" cy="{cy}" r="{radius}" fill="{color}"/>')
        else:
            body.append(
                f'<path d="M {cx} {cy} L {x1:.2f} {y1:.2f} '
                f'A {radius} {radius} 0 {large} 1 {x2:.2f} {y2:.2f} Z" fill="{color}"/>'
            )
        legend_y = 80 + index * 34
        body.append(
            f'<rect x="480" y="{legend_y - 14}" width="16" height="16" fill="{color}"/>'
            f'<text x="505" y="{legend_y}" class="label">{html.escape(label)}: '
            f'{value:,.0f} ({fraction * 100:.1f}%)</text>'
        )
        angle = next_angle
    if not ordered:
        body.append('<text x="450" y="250" text-anchor="middle">No findings</text>')
    _svg(path, width, height, "".join(body), title)


def heatmap(path: Path, repositories: list[str], categories: list[str],
            matrix: dict[tuple[str, str], float], title: str, *, limit=30) -> None:
    """Repository x rule heatmap.

    Numbers are raw counts. Colour intensity is each value relative to the
    largest value *in the same column*: a single global scale is dominated by
    one cell and hides every other rule's pattern. The column maximum is
    printed under each column so the colour scale can be read back.
    """
    repositories = repositories[:limit]
    cell_w, cell_h = 66, 26
    left, top = 300, 215
    width = left + cell_w * len(categories) + 40
    height = top + cell_h * (len(repositories) + 2) + 70
    column_max = {
        category: max((matrix.get((repo, category), 0) for repo in repositories), default=0) or 1
        for category in categories
    }
    body = [
        f'<text x="24" y="32" class="title">{html.escape(title)}</text>',
        '<text x="24" y="54" class="small">Numbers are raw counts. Colour intensity = value relative to the '
        'largest value in the same column (rule), so each rule\'s pattern is visible; the column maximum is shown below.</text>',
    ]
    for col, category in enumerate(categories):
        label = category.removeprefix("ansibleguard/")
        label = label if len(label) <= 30 else label[:29] + "…"
        x = left + col * cell_w + cell_w / 2
        body.append(
            f'<text x="{x:.1f}" y="{top - 10}" text-anchor="start" class="small" '
            f'transform="rotate(-55 {x:.1f} {top - 10})">{html.escape(label)}</text>'
        )
    for row, repository in enumerate(repositories):
        y = top + row * cell_h
        body.append(
            f'<text x="{left - 8}" y="{y + 17}" text-anchor="end" class="label">'
            f'{html.escape(repository[:44])}</text>'
        )
        for col, category in enumerate(categories):
            value = matrix.get((repository, category), 0)
            share = value / column_max[category]
            x = left + col * cell_w
            ink = "#ffffff" if share > 0.55 else "#172033"
            body.append(
                f'<rect x="{x}" y="{y}" width="{cell_w - 2}" height="{cell_h - 2}" '
                f'fill="#2563eb" fill-opacity="{0.06 + 0.94 * share:.3f}"/>'
                f'<text x="{x + cell_w / 2 - 1}" y="{y + 16}" text-anchor="middle" '
                f'class="small" style="fill:{ink}">{value:,.0f}</text>'
            )
    y = top + len(repositories) * cell_h + 14
    body.append(f'<text x="{left - 8}" y="{y + 12}" text-anchor="end" class="label" style="font-weight:700">column maximum</text>')
    for col, category in enumerate(categories):
        body.append(
            f'<text x="{left + col * cell_w + cell_w / 2 - 1}" y="{y + 12}" text-anchor="middle" '
            f'class="small" style="font-weight:700">{column_max[category]:,.0f}</text>'
        )
    _svg(path, width, height, "".join(body), title)


def nice_ticks(maximum: float, count: int = 5) -> list[float]:
    """Round tick positions from 0 to just above ``maximum``."""
    if maximum <= 0:
        return [0.0]
    raw = maximum / count
    magnitude = 10 ** math.floor(math.log10(raw))
    step = next(m * magnitude for m in (1, 2, 5, 10) if m * magnitude >= raw)
    ticks, value = [], 0.0
    while value <= maximum + step * 0.01:
        ticks.append(value)
        value += step
    return ticks


def spearman(xs: list[float], ys: list[float]) -> float:
    """Spearman rank correlation (average ranks; no third-party dependency)."""
    def rank(values: list[float]) -> list[float]:
        order = sorted(range(len(values)), key=values.__getitem__)
        result = [0.0] * len(values)
        i = 0
        while i < len(order):
            j = i
            while j + 1 < len(order) and values[order[j + 1]] == values[order[i]]:
                j += 1
            for k in range(i, j + 1):
                result[order[k]] = (i + j) / 2 + 1
            i = j + 1
        return result
    rx, ry = rank(xs), rank(ys)
    mx, my = sum(rx) / len(rx), sum(ry) / len(ry)
    numerator = sum((a - mx) * (b - my) for a, b in zip(rx, ry))
    denominator = math.sqrt(sum((a - mx) ** 2 for a in rx) * sum((b - my) ** 2 for b in ry))
    return numerator / denominator if denominator else float("nan")


def scatter_chart(
    path: Path,
    rows: list[tuple[str, float, float]],
    title: str,
    *,
    x_label: str,
    y_label: str,
    subtitle: str = "",
    log_scale: bool = False,
    label_outliers: int = 0,
) -> None:
    """Scatter plot with real ticks, optional log10(1+v) axes, and labelled outliers."""
    width, height = 1000, 700
    left, right, top, bottom = 105, 60, (88 if subtitle else 65), 95
    plot_width, plot_height = width - left - right, height - top - bottom
    def transform(value: float) -> float:
        return math.log10(value + 1) if log_scale else value
    max_x = max((x for _l, x, _y in rows), default=1) or 1
    max_y = max((y for _l, _x, y in rows), default=1) or 1
    tmax_x, tmax_y = transform(max_x) * 1.02, transform(max_y) * 1.02
    def ticks(maximum: float) -> list[float]:
        if log_scale:
            return [0.0] + [10.0 ** k for k in range(0, int(math.log10(maximum)) + 1)]
        return nice_ticks(maximum)
    body = [f'<text x="24" y="32" class="title">{html.escape(title)}</text>']
    if subtitle:
        body.append(f'<text x="24" y="54" class="small">{html.escape(subtitle)}</text>')
    for value in ticks(max_x):
        px = left + plot_width * transform(value) / tmax_x
        body.append(f'<line x1="{px:.1f}" y1="{top}" x2="{px:.1f}" y2="{top + plot_height}" class="grid"/>'
                    f'<text x="{px:.1f}" y="{top + plot_height + 18}" text-anchor="middle" class="small">{value:,.0f}</text>')
    for value in ticks(max_y):
        py = top + plot_height * (1 - transform(value) / tmax_y)
        body.append(f'<line x1="{left}" y1="{py:.1f}" x2="{left + plot_width}" y2="{py:.1f}" class="grid"/>'
                    f'<text x="{left - 8}" y="{py + 4:.1f}" text-anchor="end" class="small">{value:,.0f}</text>')
    axis_note = " (log scale, log10(1+value))" if log_scale else ""
    body += [
        f'<text x="{left + plot_width / 2}" y="{height - 28}" text-anchor="middle" class="label">{html.escape(x_label + axis_note)}</text>',
        f'<text x="25" y="{top + plot_height / 2}" text-anchor="middle" class="label" transform="rotate(-90 25 {top + plot_height / 2})">{html.escape(y_label + axis_note)}</text>',
    ]
    chosen: list[str] = []
    if label_outliers:
        by_y = sorted(rows, key=lambda r: -r[2])[:label_outliers]
        by_x = sorted(rows, key=lambda r: -r[1])[:max(1, label_outliers // 2)]
        ratio = sorted((r for r in rows if r[1] > 0), key=lambda r: -(r[2] / r[1]))[:max(1, label_outliers // 2)]
        low = sorted((r for r in rows if r[1] >= max_x * 0.25), key=lambda r: r[2] / r[1])[:1]
        for row in by_y + by_x + ratio + low:  # priority order, highest counts first
            if row[0] not in chosen:
                chosen.append(row[0])
    coordinates = {label: (left + plot_width * transform(x) / tmax_x, top + plot_height * (1 - transform(y) / tmax_y))
                   for label, x, y in rows}
    placed: list[tuple[float, float, float, float]] = []
    visible: set[str] = set()
    for label in chosen:  # greedy: skip a label that would overlap an earlier one
        px, py = coordinates[label]
        text = label[:34]
        box_w = 5.4 * len(text)
        x0 = px - 7 - box_w if px > left + plot_width - 190 else px + 7
        box = (x0, x0 + box_w, py - 9, py + 4)
        if not any(box[0] < b[1] and b[0] < box[1] and box[2] < b[3] and b[2] < box[3] for b in placed):
            placed.append(box)
            visible.add(label)
    for label, x, y in sorted(rows):
        px = left + plot_width * transform(x) / tmax_x
        py = top + plot_height * (1 - transform(y) / tmax_y)
        body.append(
            f'<circle cx="{px:.2f}" cy="{py:.2f}" r="4" fill="#2563eb" '
            f'fill-opacity="0.6"><title>{html.escape(label)}: {x:,.0f}, {y:,.0f}</title></circle>'
        )
        if label in visible:
            anchor, dx = ("end", -7) if px > left + plot_width - 190 else ("start", 7)
            body.append(f'<text x="{px + dx:.1f}" y="{py + 3:.1f}" text-anchor="{anchor}" class="small">{html.escape(label[:34])}</text>')
    _svg(path, width, height, "".join(body), title)


def optional_png(svg_paths: list[Path]) -> list[Path]:
    """Render PNG copies when cairosvg is available; SVG remains canonical."""
    try:
        import cairosvg  # type: ignore[import-not-found]
    except ImportError:
        return []
    outputs = []
    for svg_path in svg_paths:
        png_path = svg_path.with_suffix(".png")
        cairosvg.svg2png(url=str(svg_path), write_to=str(png_path))
        outputs.append(png_path)
    return outputs
