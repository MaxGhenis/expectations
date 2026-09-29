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
def grid():
    return figures.uncertainty_grid_data()


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
    assert len(everyone) > 60  # every US three-year row and every ECB two-year row
    assert np.allclose(everyone.total_sd, everyone.total_sd_published, atol=1e-12)


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
    for horizon, points in _plotted_lines(grid_svg):
        cells = [
            key
            for key, (ox, oy, w, h) in boxes.items()
            if all(ox <= x <= ox + w and oy <= y <= oy + h for x, y in points)
        ]
        assert len(cells) == 1
        ox, oy, w, h = boxes[cells[0]]
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
