"""Draw the two static figures used by the blog post on maxghenis.com.

Both read the published outputs and the US microdata, so they move with the
pipeline. Usage::

    uv run python scripts/build_blog_figures.py --out ../maxghenis.com/src/content/blog/images
"""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

from expectations.measures import filter_probability_rows, finite_intervals
from expectations.us_spf import parse_us_density

ROOT = Path(__file__).resolve().parents[1]
OUTPUTS = ROOT / "outputs"

# The blog's palette: ink text on cream. Red and blue follow the tracker's flag
# coding (US, euro area); the two amber steps order an older and a newer window.
INK, MUTED, GRID = "#0f172a", "#64748b", "#e7e2d6"
AMBER_OLD, AMBER_NEW = "#d97706", "#78350f"
RED, BLUE = "#e34948", "#2a78d6"
FONT = 'font-family="system-ui, -apple-system, sans-serif"'
WINDOWS = {"2015–19": range(2015, 2020), "2025–26": (2025, 2026)}


def _text(
    x: float,
    y: float,
    body: str,
    *,
    size: float = 12,
    fill: str = MUTED,
    extra: str = "",
) -> str:
    return f'<text x="{x:.1f}" y="{y:.1f}" {FONT} font-size="{size}" fill="{fill}" {extra}>{body}</text>'


def pooled_density(density: pd.DataFrame, years) -> pd.DataFrame:
    """Average the pooled histogram over the window's rounds, as percent per point."""
    window = density[density.year.isin(years)]
    if window.bin_scheme.nunique() != 1:
        raise ValueError("A window must share one bin scheme")
    pooled = []
    for _, group in window.groupby("year"):
        matrix = group.pivot_table(
            index="response_index",
            columns="bin_index",
            values="probability",
            dropna=False,
        )
        weights, _ = filter_probability_rows(matrix.to_numpy())
        pooled.append(pd.Series(weights.mean(axis=0), index=matrix.columns))
    bins = window.drop_duplicates("bin_index").sort_values("bin_index")
    bounds = finite_intervals(
        [
            (
                None if pd.isna(lower) else float(lower),
                None if pd.isna(upper) else float(upper),
            )
            for lower, upper in zip(bins.lower, bins.upper)
        ]
    )
    frame = pd.DataFrame({"lo": bounds[:, 0], "hi": bounds[:, 1]}, index=bins.bin_index)
    frame["p"] = pd.concat(pooled, axis=1).mean(axis=1).reindex(frame.index)
    frame["density"] = 100 * frame.p / (frame.hi - frame.lo)
    return frame.sort_values("lo").reset_index(drop=True)


def step_path(frame: pd.DataFrame, x, y, x0: float, x1: float) -> str:
    """An SVG step path for the bins that intersect the plotted range [x0, x1].

    A bin wholly outside the range is skipped: clipping its endpoints would reverse
    them and draw a segment into the margin.
    """
    points = []
    for row in frame.itertuples():
        if row.hi <= x0 or row.lo >= x1:
            continue
        points += [
            (x(max(row.lo, x0)), y(row.density)),
            (x(min(row.hi, x1)), y(row.density)),
        ]
    return "M" + " L".join(f"{a:.1f},{b:.1f}" for a, b in points)


def growth_density_figure() -> str:
    comparison = pd.read_csv(OUTPUTS / "growth_comparison.csv")
    comparison = comparison[
        (comparison.series == "US next year")
        & (comparison.rounds == "Q1")
        & (comparison.threshold == 4.0)
    ].set_index("window")
    density = parse_us_density("PRGDP")
    density = density[(density.quarter == 1) & (density.horizon_class == "next_year")]
    curves = {label: pooled_density(density, years) for label, years in WINDOWS.items()}

    width, height, left, right, top, bottom = 760, 400, 52, 20, 64, 46
    inner_w, inner_h = width - left - right, height - top - bottom
    x0, x1, y_max = -4.5, 7.5, 50.0
    x = lambda value: left + (value - x0) / (x1 - x0) * inner_w
    y = lambda value: top + (y_max - value) / y_max * inner_h

    def steps(frame: pd.DataFrame) -> str:
        return step_path(frame, x, y, x0, x1)

    parts = [
        (
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" role="img" '
            'aria-label="Pooled next-year US growth forecast distributions, 2015 to 2019 average versus 2025 to 2026 average">'
        ),
        _text(
            left,
            24,
            "US next-year growth: the pooled forecast distribution",
            size=17,
            fill=INK,
            extra='font-weight="650"',
        ),
        _text(
            left,
            44,
            "US SPF Q1 rounds, average of the pooled respondent histograms. Percent probability per percentage point of growth.",
            size=12.5,
        ),
    ]
    for tick in range(-4, 8, 2):
        parts.append(
            f'<line x1="{x(tick):.1f}" y1="{top}" x2="{x(tick):.1f}" y2="{top + inner_h}" stroke="{GRID}"/>'
        )
        parts.append(
            _text(x(tick), top + inner_h + 18, f"{tick}%", extra='text-anchor="middle"')
        )
    for tick in (10, 20, 30, 40, 50):
        parts.append(
            f'<line x1="{left}" y1="{y(tick):.1f}" x2="{left + inner_w}" y2="{y(tick):.1f}" stroke="{GRID}"/>'
        )
        parts.append(
            _text(left - 8, y(tick) + 4, f"{tick}%", extra='text-anchor="end"')
        )
    parts.append(
        f'<line x1="{left}" y1="{y(0):.1f}" x2="{left + inner_w}" y2="{y(0):.1f}" stroke="{MUTED}"/>'
    )
    parts.append(
        f'<line x1="{x(4):.1f}" y1="{top + 6}" x2="{x(4):.1f}" y2="{top + inner_h}" stroke="{INK}" stroke-dasharray="4 4"/>'
    )
    for label, color in (("2015–19", AMBER_OLD), ("2025–26", AMBER_NEW)):
        parts.append(
            f'<path d="{steps(curves[label])}" fill="none" stroke="{color}" stroke-width="2.5"/>'
        )
    old_peak = curves["2015–19"].loc[curves["2015–19"].density.idxmax()]
    new_peak = curves["2025–26"].loc[curves["2025–26"].density.idxmax()]
    old_mean, new_mean = (comparison.loc[label, "mean"] for label in WINDOWS)
    parts.append(
        _text(
            x(old_peak.hi) + 8,
            y(old_peak.density) + 4,
            f"2015–19 · mean {old_mean:.2f}%",
            size=12.5,
            fill=AMBER_OLD,
            extra='font-weight="600"',
        )
    )
    parts.append(
        _text(
            x(new_peak.lo) - 8,
            y(new_peak.density) + 4,
            f"2025–26 · mean {new_mean:.2f}%",
            size=12.5,
            fill=AMBER_NEW,
            extra='font-weight="600" text-anchor="end"',
        )
    )
    old_tail, new_tail = (
        100 * comparison.loc[label, "probability_lower"] for label in WINDOWS
    )
    parts.append(
        _text(
            x(4) + 8,
            top + 20,
            f"P(&gt;4%): {old_tail:.1f}% → {new_tail:.1f}%",
            size=12.5,
            fill=INK,
        )
    )
    return "\n".join([*parts, "</svg>"])


def cross_survey_figure() -> str:
    measures = pd.read_csv(OUTPUTS / "measures.csv")
    q1 = measures[(measures.quarter == 1) & (measures.horizon_class == "next_year")]
    series = [
        (
            "US (US SPF)",
            RED,
            q1[(q1.survey == "us") & (q1.variable == "PRGDP") & (q1.year >= 1992)],
        ),
        (
            "Euro area (ECB SPF)",
            BLUE,
            q1[(q1.survey == "ecb") & (q1.variable == "rgdp")],
        ),
    ]
    width, height, left, right, top, bottom = 760, 380, 52, 200, 64, 42
    inner_w, inner_h = width - left - right, height - top - bottom
    x0, x1, y_max = 1992, 2026, 2.5
    x = lambda value: left + (value - x0) / (x1 - x0) * inner_w
    y = lambda value: top + (y_max - value) / y_max * inner_h
    parts = [
        (
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" role="img" '
            'aria-label="Pooled total standard deviation of next-year real GDP growth forecasts, US versus euro area, 1992 to 2026">'
        ),
        _text(
            left,
            24,
            "Uncertainty of real GDP growth forecasts (next year)",
            size=17,
            fill=INK,
            extra='font-weight="650"',
        ),
        _text(
            left,
            44,
            "Pooled total SD of each survey&#8217;s densities, percentage points. Q1 rounds; US from 1992Q1.",
            size=12.5,
        ),
    ]
    for tick in np.arange(0.5, 2.51, 0.5):
        parts.append(
            f'<line x1="{left}" y1="{y(tick):.1f}" x2="{left + inner_w}" y2="{y(tick):.1f}" stroke="{GRID}"/>'
        )
        parts.append(
            _text(left - 8, y(tick) + 4, f"{tick:.1f}pp", extra='text-anchor="end"')
        )
    for tick in range(1995, 2030, 5):
        parts.append(
            _text(x(tick), top + inner_h + 18, str(tick), extra='text-anchor="middle"')
        )
    parts.append(
        f'<line x1="{left}" y1="{y(0):.1f}" x2="{left + inner_w}" y2="{y(0):.1f}" stroke="{MUTED}"/>'
    )
    for label, color, frame in series:
        frame = frame.sort_values("year")
        path = "M" + " L".join(
            f"{x(row.year):.1f},{y(row.total_sd):.1f}" for row in frame.itertuples()
        )
        last = frame.iloc[-1]
        parts.append(
            f'<path d="{path}" fill="none" stroke="{color}" stroke-width="2"/>'
        )
        parts.append(
            f'<circle cx="{x(last.year):.1f}" cy="{y(last.total_sd):.1f}" r="3.5" fill="{color}"/>'
        )
        parts.append(
            _text(
                x(last.year) + 8,
                y(last.total_sd) + 4,
                f"{label} {last.total_sd:.2f}",
                size=12.5,
                fill=INK,
                extra='font-weight="600"',
            )
        )
    return "\n".join([*parts, "</svg>"])


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--out", type=Path, required=True, help="directory for the two SVG files"
    )
    out = parser.parse_args().out
    out.mkdir(parents=True, exist_ok=True)
    (out / "expectations-growth-density.svg").write_text(growth_density_figure())
    (out / "expectations-us-ea-sd.svg").write_text(cross_survey_figure())
    print(f"wrote two figures to {out}")


if __name__ == "__main__":
    main()
