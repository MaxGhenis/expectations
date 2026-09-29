"""The blog figures must draw inside their own plot area."""

import importlib.util
import re
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "build_blog_figures", ROOT / "scripts" / "build_blog_figures.py"
)
figures = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(figures)


def test_step_path_skips_bins_outside_the_plotted_range():
    frame = pd.DataFrame(
        {
            "lo": [-7.2, -5.1, -3.0, 0.0, 7.0, 9.0],
            "hi": [-5.1, -3.0, 0.0, 7.0, 9.0, 11.0],
            "density": [0.1, 0.5, 20.0, 12.0, 0.4, 0.1],
        }
    )
    x0, x1, left, width = -4.5, 7.5, 52.0, 688.0
    x = lambda value: left + (value - x0) / (x1 - x0) * width
    path = figures.step_path(frame, x, lambda value: 300 - value, x0, x1)
    xs = [float(pair.split(",")[0]) for pair in re.findall(r"[-\d.]+,[-\d.]+", path)]
    assert min(xs) >= left and max(xs) <= left + width
    assert xs == sorted(xs)  # the curve never doubles back
    assert len(xs) == 2 * 4  # the two outermost bins lie wholly outside the range


MEASURES = pd.read_csv(ROOT / "outputs" / "measures.csv")
HORIZON_YEARS = {"next_year": 1, "year_after_next": 2, "three_years_ahead": 3}
ROUND = ["survey", "column", "year"]


@pytest.fixture(scope="module")
def densities():
    us = pd.concat(
        figures.parse_us_density(variables["us"])
        for variables in figures.GRID_COLUMNS.values()
    )
    return us, figures.load_ecb_spf()


@pytest.fixture(scope="module")
def grid(densities):
    return figures.uncertainty_grid_data(*densities)


@pytest.fixture(scope="module")
def grid_svg(grid):
    return figures.uncertainty_grid_figure(grid)


def test_uncertainty_grid_takes_every_q1_round_and_no_ecb_three_year_line(grid):
    spans = grid.groupby(["survey", "column", "horizon_class"]).year.agg(
        ["min", "max", "size"]
    )
    for column in figures.GRID_COLUMNS:
        for horizon in figures.GRID_HORIZONS:
            assert tuple(spans.loc["us", column, horizon]) == (2010, 2026, 17)
        assert tuple(spans.loc["ecb", column, "next_year"]) == (2010, 2026, 17)
        # The ECB asks two calendar years out in Q1 rounds only from 2013.
        assert tuple(spans.loc["ecb", column, "year_after_next"]) == (2013, 2026, 14)
        assert ("ecb", column, "three_years_ahead") not in spans.index


def test_uncertainty_grid_pools_one_panel_per_round_on_one_bin_scheme(grid):
    per_round = grid.groupby(ROUND)
    assert (per_round.n.nunique() == 1).all()  # the same forecasters at every horizon
    assert (per_round.bin_scheme.nunique() == 1).all()  # and the same bins
    assert (grid.n <= grid.n_answered).all()
    assert (grid.n > 0).all()
    horizons = grid.horizon_class.map(HORIZON_YEARS)
    assert (grid.target_year - grid.year == horizons).all()


def test_uncertainty_grid_matches_the_published_measures_where_everyone_is_in(grid):
    published = MEASURES[
        (MEASURES.quarter == 1)
        & MEASURES.horizon_class.isin(HORIZON_YEARS)
        & MEASURES.year.between(*figures.GRID_YEARS)
    ]
    merged = grid.merge(
        published,
        on=["survey", "variable", "year", "horizon_class", "target_year"],
        suffixes=("", "_published"),
        validate="one_to_one",
    )
    assert len(merged) == len(grid)
    # The panel starts from exactly the histograms the published filter keeps.
    assert (merged.n_answered == merged.n_published).all()
    assert (merged.bin_scheme == merged.bin_scheme_published).all()
    # Where every forecaster who answered a horizon is in the panel, the panel
    # SD is the published SD: same filter, same bins, same pooling.
    everyone = merged[merged.n == merged.n_answered]
    assert len(everyone) > 60  # includes every ECB two-year row
    assert np.allclose(everyone.total_sd, everyone.total_sd_published, atol=1e-12)


def _independent_panel(density, variable, year):
    """A second, vectorized build of one round's panel: valid at every horizon."""
    frame = density[
        (density.variable == variable)
        & (density.quarter == 1)
        & (density.year == year)
        & density.horizon_class.isin(HORIZON_YEARS)
    ]
    blocks = {}
    for horizon, block in frame.groupby("horizon_class"):
        bins = block[["bin_index", "lower", "upper"]].drop_duplicates()
        bins = bins.sort_values("bin_index")
        values = block.pivot_table(
            index="respondent",
            columns="bin_index",
            values="probability",
            aggfunc="first",
            dropna=False,
        ).reindex(columns=bins.bin_index)
        filled = values.fillna(0.0)
        valid = (
            values.notna().any(axis=1)
            & ((filled >= 0) & (filled <= 100)).all(axis=1)
            & ((filled.sum(axis=1) - 100).abs() < 2)
        )
        intervals = [
            (None if pd.isna(lo) else float(lo), None if pd.isna(hi) else float(hi))
            for lo, hi in zip(bins.lower, bins.upper, strict=True)
        ]
        blocks[horizon] = (values[valid], intervals)
    members = set.intersection(*(set(values.index) for values, _ in blocks.values()))
    return {
        horizon: figures.round_stats(
            values.loc[sorted(members)].to_numpy(),
            figures.finite_intervals(intervals).mean(axis=1),
            intervals,
        )
        for horizon, (values, intervals) in blocks.items()
    }


def test_uncertainty_grid_panel_matches_an_independent_rebuild(grid, densities):
    us, ecb = densities
    for (survey, variable, year), rows in grid.groupby(["survey", "variable", "year"]):
        rebuilt = _independent_panel(us if survey == "us" else ecb, variable, year)
        assert set(rebuilt) == set(rows.horizon_class)
        for row in rows.itertuples():
            assert row.n == rebuilt[row.horizon_class]["n"]
            assert np.isclose(
                row.total_sd, rebuilt[row.horizon_class]["total_sd"], atol=1e-12
            )


def _contrast(foreground, background):
    def luminance(color):
        channels = [int(color[i : i + 2], 16) / 255 for i in (1, 3, 5)]
        linear = [
            c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
            for c in channels
        ]
        return 0.2126 * linear[0] + 0.7152 * linear[1] + 0.0722 * linear[2]

    light, dark = sorted((luminance(foreground), luminance(background)), reverse=True)
    return (light + 0.05) / (dark + 0.05)


def test_uncertainty_grid_colors_clear_three_to_one_on_the_blog_page():
    for color in figures.GRID_BLUES.values():
        assert _contrast(color, figures.CREAM) >= 3


def test_uncertainty_grid_legend_pairs_each_color_with_its_horizon(grid_svg):
    keys = re.findall(
        r'<line [^>]*y1="68"[^>]*stroke="(#[0-9a-f]{6})"[^>]*/>\n<text [^>]*>([^<]+)</text>',
        grid_svg,
    )
    labels = {
        figures.GRID_BLUES[h]: label for h, label in figures.GRID_HORIZONS.items()
    }
    assert len(keys) == len(labels)
    for color, text in keys:
        assert text.startswith(labels[color])


def test_uncertainty_grid_year_labels_and_bin_markers_sit_at_their_years(
    grid, grid_svg
):
    start, end = figures.GRID_YEARS
    boxes = figures.grid_cells()

    def cell_at(x, y):
        found = [
            key
            for key, (ox, oy, w, h) in boxes.items()
            if ox - 0.1 <= x <= ox + w + 0.1 and oy - 0.1 <= y <= oy + h + 20
        ]
        assert len(found) == 1
        return found[0]

    def year_at(key, x):
        ox, _, w, _ = boxes[key]
        return start + (x - ox) / w * (end - start)

    labels = re.findall(
        r'<text x="([\d.]+)" y="([\d.]+)"[^>]*>(20\d\d)</text>', grid_svg
    )
    assert len(labels) == 2 * len(range(start, end + 1, 4))
    for x, y, year in labels:
        key = cell_at(float(x), float(y))
        assert abs(year_at(key, float(x)) - int(year)) < 0.01
    markers = {}
    for x, y in re.findall(
        r'<line x1="([\d.]+)" y1="([\d.]+)" x2="[\d.]+" y2="[\d.]+" '
        r'stroke="[^"]+" stroke-dasharray="3 3"/>',
        grid_svg,
    ):
        if float(y) < figures.GRID_TOP:  # the legend's key
            continue
        key = cell_at(float(x), float(y))
        markers.setdefault(key, []).append(round(year_at(key, float(x)), 2))
    for key, cell in grid.groupby(["survey", "column"]):
        assert sorted(markers.get(key, [])) == figures.bin_changes(cell)


def _plotted_lines(svg):
    colors = {color: horizon for horizon, color in figures.GRID_BLUES.items()}
    pattern = rf'<path d="M([^"]+)" fill="none" stroke="({"|".join(colors)})"'
    for path, color in re.findall(pattern, svg):
        points = [tuple(map(float, pair.split(","))) for pair in path.split(" L")]
        yield colors[color], points


def test_uncertainty_grid_draws_every_value_in_its_own_cell_and_color(grid, grid_svg):
    start, end = figures.GRID_YEARS
    boxes = figures.grid_cells()
    drawn = {}
    count = {}
    for horizon, points in _plotted_lines(grid_svg):
        cells = [
            key
            for key, (ox, oy, w, h) in boxes.items()
            if all(ox <= x <= ox + w and oy <= y <= oy + h for x, y in points)
        ]
        assert len(cells) == 1
        ox, oy, w, h = boxes[cells[0]]
        count[(*cells[0], horizon)] = count.get((*cells[0], horizon), 0) + 1
        # Invert the scales: back from pixels to rounds and points of SD.
        drawn[(*cells[0], horizon)] = [
            (
                start + (x - ox) / w * (end - start),
                (1 - (y - oy) / h) * figures.GRID_Y_MAX,
            )
            for x, y in points
        ]
    expected = grid.groupby(["survey", "column", "horizon_class"])
    assert set(drawn) == set(expected.groups)
    assert set(count.values()) == {1}  # each line drawn exactly once
    for key, rows in expected:
        years, values = zip(*drawn[key], strict=True)
        # Coordinates print to 0.1 px: about 0.005 years and 0.0015 points.
        assert np.allclose(years, rows.year, atol=0.01)
        assert np.allclose(values, rows.total_sd, atol=0.002)
    assert grid.total_sd.max() < figures.GRID_Y_MAX


def test_uncertainty_grid_marks_each_change_of_bins_between_plotted_rounds(grid):
    changes = {
        key: figures.bin_changes(cell)
        for key, cell in grid.groupby(["survey", "column"])
    }
    assert changes == {
        ("us", "Real GDP growth"): [2020.5, 2024.5],
        ("us", "Unemployment rate"): [2013.5, 2020.5, 2024.5],
        ("ecb", "Real GDP growth"): [2020.5, 2022.5],
        ("ecb", "Unemployment rate"): [2017.5, 2022.5],
    }


def test_uncertainty_grid_description_carries_the_latest_values(grid, grid_svg):
    description = re.search(r"<desc>(.*)</desc>", grid_svg).group(1)
    latest = grid[grid.year == figures.GRID_YEARS[1]].set_index(
        ["survey", "column", "horizon_class"]
    )
    for (survey, column, horizon), row in latest.iterrows():
        label = figures.GRID_HORIZONS[horizon].lower()
        assert f"{label} {row.total_sd:.2f}" in description
    assert description.count("three years out") == 2  # US cells only


def test_uncertainty_grid_y_labels_sit_on_their_gridlines(grid_svg):
    for survey in figures.GRID_ROWS:
        ox, oy, _, h = figures.grid_cells()[survey, next(iter(figures.GRID_COLUMNS))]
        labels = re.findall(
            rf'<text x="{ox - 6:.1f}" y="([\d.]+)"[^>]*>([\d.]+)</text>', grid_svg
        )
        in_cell = {
            text: float(y) for y, text in labels if oy - 5 <= float(y) <= oy + h + 5
        }
        assert set(in_cell) == {"0", "0.5", "1.0", "1.5", "2.0"}
        for text, y in in_cell.items():
            expected = oy + h * (1 - float(text) / figures.GRID_Y_MAX) + 4
            assert abs(y - expected) < 0.1


def test_uncertainty_grid_description_names_each_cell_with_its_own_values(
    grid, grid_svg
):
    description = re.search(r"<desc>(.*)</desc>", grid_svg).group(1)
    end = figures.GRID_YEARS[1]
    for survey, (name, _) in figures.GRID_ROWS.items():
        for column in figures.GRID_COLUMNS:
            cell = grid[
                (grid.survey == survey) & (grid.column == column) & (grid.year == end)
            ].set_index("horizon_class")
            values = ", ".join(
                f"{label.lower()} {cell.total_sd[horizon]:.2f}"
                for horizon, label in figures.GRID_HORIZONS.items()
                if horizon in cell.index
            )
            column_name = column[0].lower() + column[1:]
            assert f"{name} {column_name} in {end}Q1: {values}." in description


def test_uncertainty_grid_refuses_a_round_with_no_common_forecasters():
    rows = []
    for horizon, respondent, target in (
        ("next_year", "a", 2027),
        ("three_years_ahead", "b", 2029),
    ):
        for bin_index, (lower, upper) in enumerate(((None, 5.0), (5.0, None))):
            rows.append(
                {
                    "horizon_class": horizon,
                    "respondent": respondent,
                    "bin_index": bin_index,
                    "probability": 50.0,
                    "lower": lower,
                    "upper": upper,
                    "bin_scheme": "test",
                    "target_year": target,
                }
            )
    with pytest.raises(ValueError, match="no forecaster answered every horizon"):
        figures._balanced_round(
            pd.DataFrame(rows), "us", "Unemployment rate", "PRUNEMP", 2026
        )
