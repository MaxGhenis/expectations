"""Draw the static figures used by the blog on maxghenis.com.

All three read the published outputs (the density figure also reads the US
microdata), so they move with the pipeline. Usage::

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

# The horizon grid: one row per survey, one column per variable, one line per
# calendar-year horizon. The ECB asks at most two calendar years ahead, so its
# rows stop at the year after next. Horizons are ordered, so they take one
# blue ramp, light to dark (validated as an ordinal ramp on the cream surface).
GRID_HORIZONS = {
    "next_year": "Next year",
    "year_after_next": "Two years out",
    "three_years_ahead": "Three years out",
}
GRID_BLUES = {
    "next_year": "#86b6ef",
    "year_after_next": "#2a78d6",
    "three_years_ahead": "#104281",
}
GRID_ROWS = {"us": ("US", "US SPF"), "ecb": ("Euro area", "ECB SPF")}
GRID_COLUMNS = {
    "Real GDP growth": {"us": "PRGDP", "ecb": "rgdp"},
    "Unemployment rate": {"us": "PRUNEMP", "ecb": "unemp"},
}
GRID_YEARS = (2010, 2026)
# One y scale for all four cells, so every line reads in the same points.
GRID_Y_MAX = 2.25
GRID_WIDTH, GRID_HEIGHT = 760, 534
GRID_LEFT, GRID_TOP, GRID_GUTTER, GRID_RIGHT = 120, 116, 24, 16
GRID_CELL_W = (GRID_WIDTH - GRID_LEFT - GRID_GUTTER - GRID_RIGHT) / 2
GRID_CELL_H, GRID_ROW_GAP = 150, 26
# The US survey printed wider bins from 2020Q2 through 2024Q1. On a
# year-plus-quarter axis that is [2020.25, 2024.25): the 2021–24 Q1 rounds.
US_WIDE_BINS = (2020.25, 2024.25)


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


def uncertainty_grid_data(measures: pd.DataFrame) -> pd.DataFrame:
    """Pooled total SD of each Q1 round in the grid window, per cell and horizon."""
    start, end = GRID_YEARS
    pieces = []
    for column, variables in GRID_COLUMNS.items():
        for survey, variable in variables.items():
            cell = measures[
                (measures.survey == survey)
                & (measures.variable == variable)
                & (measures.quarter == 1)
                & measures.year.between(start, end)
                & measures.horizon_class.isin(GRID_HORIZONS)
            ]
            pieces.append(cell.assign(column=column))
    frame = pd.concat(pieces, ignore_index=True)
    keys = ["survey", "column", "horizon_class", "year"]
    if frame.duplicated(keys).any():
        raise ValueError("A grid cell has two rows for one round and horizon")
    columns = [*keys, "variable", "target_year", "bin_scheme", "n", "total_sd"]
    return frame[columns].sort_values(keys).reset_index(drop=True)


def _grid_description(data: pd.DataFrame) -> str:
    end = GRID_YEARS[1]
    latest = data[data.year == end].set_index(["survey", "column", "horizon_class"])
    sentences = []
    for survey, (name, _) in GRID_ROWS.items():
        for column in GRID_COLUMNS:
            values = ", ".join(
                f"{label.lower()} {latest.total_sd[survey, column, horizon]:.2f}"
                for horizon, label in GRID_HORIZONS.items()
                if (survey, column, horizon) in latest.index
            )
            sentences.append(f"{name} {column.lower()} in {end}Q1: {values}.")
    return " ".join(sentences)


def grid_cells() -> dict[tuple[str, str], tuple[float, float, float, float]]:
    """Each cell's plot box, (x, y, width, height), keyed by (survey, column)."""
    cells = {}
    for row, survey in enumerate(GRID_ROWS):
        for col, column in enumerate(GRID_COLUMNS):
            cells[survey, column] = (
                GRID_LEFT + col * (GRID_CELL_W + GRID_GUTTER),
                GRID_TOP + row * (GRID_CELL_H + GRID_ROW_GAP),
                GRID_CELL_W,
                GRID_CELL_H,
            )
    return cells


def uncertainty_grid_figure(measures: pd.DataFrame) -> str:
    """Small multiples: pooled total SD by horizon, US and euro area, 2010–26."""
    data = uncertainty_grid_data(measures)
    if data.total_sd.max() >= GRID_Y_MAX:
        raise ValueError("A value exceeds GRID_Y_MAX; raise it so no line clips")
    width, height = GRID_WIDTH, GRID_HEIGHT
    start, end = GRID_YEARS
    cells = grid_cells()
    parts = [
        (
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" role="img" '
            'aria-label="Small multiples of forecast uncertainty by horizon: pooled total '
            "standard deviation of first-quarter survey densities, 2010 to 2026, for real GDP "
            'growth and the unemployment rate in the US and the euro area">'
        ),
        f"<desc>{_grid_description(data)}</desc>",
        _text(
            16,
            26,
            "Uncertainty of growth and unemployment forecasts, by horizon",
            size=17,
            fill=INK,
            extra='font-weight="650"',
        ),
        _text(
            16,
            46,
            "Pooled total SD of each survey&#8217;s densities, percentage points. "
            f"First-quarter rounds, {start}–{end}.",
            size=12.5,
        ),
    ]
    key_x = 16.0
    for horizon, label in GRID_HORIZONS.items():
        text = label + (" (US only)" if horizon == "three_years_ahead" else "")
        parts.append(
            f'<line x1="{key_x:.1f}" y1="68" x2="{key_x + 18:.1f}" y2="68" '
            f'stroke="{GRID_BLUES[horizon]}" stroke-width="2.5" stroke-linecap="round"/>'
        )
        parts.append(_text(key_x + 24, 72, text, size=12, fill=INK))
        key_x += 24 + 6.6 * len(text) + 22
    for column in GRID_COLUMNS:
        ox, oy, _, _ = cells["us", column]
        parts.append(
            _text(
                ox,
                oy - 12,
                column,
                size=13,
                fill=INK,
                extra='font-weight="650"',
            )
        )
    for row, (survey, (name, source)) in enumerate(GRID_ROWS.items()):
        for col, column in enumerate(GRID_COLUMNS):
            ox, oy, cell_w, cell_h = cells[survey, column]
            if col == 0:
                parts.append(
                    _text(
                        16,
                        oy + cell_h / 2 - 2,
                        name,
                        size=13,
                        fill=INK,
                        extra='font-weight="650"',
                    )
                )
                parts.append(_text(16, oy + cell_h / 2 + 14, source, size=11.5))
            parts += _grid_cell(
                data[(data.survey == survey) & (data.column == column)],
                (ox, oy, cell_w, cell_h),
                tick_labels=col == 0,
                year_labels=row == len(GRID_ROWS) - 1,
                wide_bins=survey == "us",
                wide_bins_label=survey == "us" and col == 0,
            )
    notes = [
        (
            "The ECB survey asks at most two calendar years ahead. Within a round, "
            "every horizon shares the same bins;"
        ),
        "shading marks the wider bins the US survey used from 2020Q2 through 2024Q1.",
    ]
    for offset, line in enumerate(notes):
        parts.append(_text(16, height - 50 + 15 * offset, line, size=11.5))
    parts.append(
        _text(
            16,
            height - 10,
            "Source: US and ECB Surveys of Professional Forecasters, individual "
            "responses · maxghenis.com/expectations",
            size=11.5,
        )
    )
    return "\n".join([*parts, "</svg>"])


def _grid_cell(
    cell: pd.DataFrame,
    box: tuple[float, float, float, float],
    *,
    tick_labels: bool,
    year_labels: bool,
    wide_bins: bool,
    wide_bins_label: bool,
) -> list[str]:
    ox, oy, cell_w, cell_h = box
    start, end = GRID_YEARS
    x = lambda year: ox + (year - start) / (end - start) * cell_w
    y = lambda value: oy + cell_h * (1 - value / GRID_Y_MAX)
    parts = []
    if wide_bins:
        x0, x1 = (x(edge) for edge in US_WIDE_BINS)
        parts.append(
            f'<rect x="{x0:.1f}" y="{oy:.1f}" width="{x1 - x0:.1f}" height="{cell_h:.1f}" '
            f'fill="{MUTED}" fill-opacity="0.09"/>'
        )
        if wide_bins_label:
            parts.append(
                _text(
                    (x0 + x1) / 2,
                    oy + cell_h - 8,
                    "wider bins",
                    size=10.5,
                    extra='text-anchor="middle"',
                )
            )
    for tick in (0.5, 1.0, 1.5, 2.0):
        parts.append(
            f'<line x1="{ox:.1f}" y1="{y(tick):.1f}" x2="{ox + cell_w:.1f}" '
            f'y2="{y(tick):.1f}" stroke="{GRID}"/>'
        )
        if tick_labels:
            parts.append(
                _text(
                    ox - 6,
                    y(tick) + 4,
                    f"{tick:.1f}",
                    size=11,
                    extra='text-anchor="end"',
                )
            )
    parts.append(
        f'<line x1="{ox:.1f}" y1="{y(0):.1f}" x2="{ox + cell_w:.1f}" y2="{y(0):.1f}" '
        f'stroke="{MUTED}"/>'
    )
    if year_labels:
        # The outer labels hug their cell's edges so neighboring cells' labels
        # never meet across the gutter.
        for year in range(start, end + 1, 4):
            anchor = {start: "start", end: "end"}.get(year, "middle")
            parts.append(
                _text(
                    x(year),
                    y(0) + 16,
                    str(year),
                    size=11,
                    extra=f'text-anchor="{anchor}"',
                )
            )
    wide = cell.pivot(index="year", columns="horizon_class", values="total_sd")
    for horizon in GRID_HORIZONS:
        if horizon not in wide:
            continue
        series = wide[horizon].dropna()
        path = "M" + " L".join(
            f"{x(year):.1f},{y(value):.1f}" for year, value in series.items()
        )
        parts.append(
            f'<path d="{path}" fill="none" stroke="{GRID_BLUES[horizon]}" stroke-width="2" '
            'stroke-linejoin="round" stroke-linecap="round"/>'
        )
    return parts


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--out", type=Path, required=True, help="directory for the SVG files"
    )
    out = parser.parse_args().out
    out.mkdir(parents=True, exist_ok=True)
    measures = pd.read_csv(OUTPUTS / "measures.csv")
    (out / "expectations-growth-density.svg").write_text(growth_density_figure())
    (out / "expectations-us-ea-sd.svg").write_text(cross_survey_figure())
    (out / "expectations-uncertainty-grid.svg").write_text(
        uncertainty_grid_figure(measures)
    )
    print(f"wrote three figures to {out}")


if __name__ == "__main__":
    main()
