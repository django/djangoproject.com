#!/usr/bin/env python3
"""
Generate an SVG release roadmap image from machine-readable data, similar to
https://devguide.python.org/versions/.

Usage:
  python tools/generate_release_roadmap.py --data data/releases.json --out djangoproject/static/img/release-roadmap.svg

The input is a JSON array of objects with keys:
- version: string, e.g. "5.2"
- release_date: YYYY-MM-DD
- bugfix_end: YYYY-MM-DD
- security_end: YYYY-MM-DD
- is_lts: boolean
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
from dataclasses import dataclass
from typing import List

DATE_FMT = "%Y-%m-%d"


@dataclass
class Cycle:
    version: str
    release_date: dt.date
    bugfix_end: dt.date
    security_end: dt.date
    is_lts: bool

    @classmethod
    def from_dict(cls, d: dict) -> Cycle:
        return cls(
            version=str(d["version"]),
            release_date=dt.date.fromisoformat(d["release_date"]),
            bugfix_end=dt.date.fromisoformat(d["bugfix_end"]),
            security_end=dt.date.fromisoformat(d["security_end"]),
            is_lts=bool(d.get("is_lts", False)),
        )


def load_cycles(path: str) -> list[Cycle]:
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    cycles = [Cycle.from_dict(x) for x in data]
    # sort newest first for display
    cycles.sort(key=lambda c: (c.release_date, c.version), reverse=True)
    return cycles


def month_floor(d: dt.date) -> dt.date:
    return dt.date(d.year, d.month, 1)


def month_add(d: dt.date, months: int) -> dt.date:
    y = d.year + (d.month - 1 + months) // 12
    m = (d.month - 1 + months) % 12 + 1
    day = min(
        d.day,
        [
            31,
            29 if y % 4 == 0 and (y % 100 != 0 or y % 400 == 0) else 28,
            31,
            30,
            31,
            30,
            31,
            31,
            30,
            31,
            30,
            31,
        ][m - 1],
    )
    return dt.date(y, m, day)


def generate_svg(
    cycles: list[Cycle],
    width=1100,
    row_h=24,
    row_gap=14,
    left_margin=150,
    right_margin=20,
    top_margin=60,
    bottom_margin=30,
) -> str:
    # Determine time bounds
    min_start = min(c.release_date for c in cycles)
    max_end = max(c.security_end for c in cycles)

    # pad bounds by one month on each side
    min_start = month_add(month_floor(min_start), -1)
    max_end = month_add(month_floor(max_end), 1)

    # build a list of month ticks from min_start to max_end
    ticks = []
    t = dt.date(min_start.year, min_start.month, 1)
    while t <= max_end:
        ticks.append(t)
        t = month_add(t, 1)

    inner_w = width - left_margin - right_margin

    def x_for(date: dt.date) -> float:
        # linear mapping by months
        total_months = (max_end.year - min_start.year) * 12 + (
            max_end.month - min_start.month
        )
        if total_months == 0:
            return left_margin
        months_from_start = (
            (date.year - min_start.year) * 12
            + (date.month - min_start.month)
            + (date.day - 1) / 31.0
        )
        return left_margin + inner_w * (months_from_start / total_months)

    height = top_margin + bottom_margin + len(cycles) * (row_h + row_gap) - row_gap

    # SVG header
    parts = [
        f"<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 {width} {height}' width='{width}' height='{height}' role='img' aria-labelledby='title desc'>",
        "<title id='title'>Django release roadmap</title>",
        "<desc id='desc'>Shows bugfix and security-only support windows for Django releases</desc>",
        "<style>\n        text { font-family: system-ui, -apple-system, Segoe UI, Roboto, Ubuntu, Cantarell, Noto Sans, sans-serif; fill: #111; font-size: 12px; }\n        .label { font-weight: 600; }\n        .bugfix { fill: #44b78b; } /* Django green */\n        .security { fill: #f0ad4e; } /* amber */\n        .lts { stroke: #2c9c74; stroke-width: 2; }\n        .axis line { stroke: #ccc; }\n        .grid { stroke: #eee; }\n        .legend text { font-size: 12px; }\n        .legend rect { stroke: #999; fill-opacity: 0.9; }\n        </style>",
    ]

    # axis and month grid
    axis_y = top_margin - 25
    parts.append(f"<g class='axis'>")
    parts.append(
        f"<line x1='{left_margin}' y1='{axis_y}' x2='{width - right_margin}' y2='{axis_y}' />"
    )
    parts.append("</g>")

    # month tick labels for Jan of each year
    parts.append("<g class='grid'>")
    for tick in ticks:
        x = x_for(tick)
        if tick.month == 1:
            parts.append(
                f"<line x1='{x:.1f}' y1='{axis_y}' x2='{x:.1f}' y2='{height - bottom_margin}' stroke='#ddd' />"
            )
            parts.append(f"<text x='{x + 3:.1f}' y='{axis_y - 6}'>{tick.year}</text>")
    parts.append("</g>")

    # legend
    legend_x = left_margin
    legend_y = 20
    parts.append("<g class='legend'>")
    parts.append(
        f"<rect x='{legend_x - 10}' y='{legend_y - 16}' width='260' height='22' rx='4' ry='4' fill='#fff' stroke='#ccc' />"
    )
    parts.append(
        f"<rect x='{legend_x}' y='{legend_y - 12}' width='24' height='12' class='bugfix' />"
    )
    parts.append(f"<text x='{legend_x + 30}' y='{legend_y - 2}'>Bugfix support</text>")
    parts.append(
        f"<rect x='{legend_x + 130}' y='{legend_y - 12}' width='24' height='12' class='security' />"
    )
    parts.append(f"<text x='{legend_x + 160}' y='{legend_y - 2}'>Security-only</text>")
    parts.append("</g>")

    # rows for cycles
    y = top_margin
    for c in cycles:
        # label
        label = f"{c.version}{' LTS' if c.is_lts else ''}"
        parts.append(
            f"<text class='label' x='10' y='{y + row_h * 0.7:.1f}'>{label}</text>"
        )
        # bars
        x1 = x_for(c.release_date)
        x2 = x_for(c.bugfix_end)
        x3 = x_for(c.security_end)
        # bugfix bar
        parts.append(
            f"<rect x='{x1:.1f}' y='{y:.1f}' width='{max(0.5, x2 - x1):.1f}' height='{row_h}' class='bugfix {'lts' if c.is_lts else ''}' />"
        )
        # security bar
        parts.append(
            f"<rect x='{x2:.1f}' y='{y:.1f}' width='{max(0.5, x3 - x2):.1f}' height='{row_h}' class='security {'lts' if c.is_lts else ''}' />"
        )
        # end markers
        parts.append(
            f"<text x='{x3 + 4:.1f}' y='{y + row_h * 0.7:.1f}' fill='#555'>{c.security_end.strftime('%b %Y')}</text>"
        )
        y += row_h + row_gap

    parts.append("</svg>")
    return "\n".join(parts)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    cycles = load_cycles(args.data)

    # simple validation
    for c in cycles:
        if not (c.release_date <= c.bugfix_end <= c.security_end):
            raise SystemExit(
                f"Invalid dates for {c.version}: release <= bugfix_end <= security_end is required"
            )

    svg = generate_svg(cycles)

    # ensure output directory exists
    out_path = args.out
    import os

    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(svg)


if __name__ == "__main__":
    main()
