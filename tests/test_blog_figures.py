"""The blog figures must draw inside their own plot area."""

import importlib.util
import re
from pathlib import Path

import pandas as pd

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


def test_uncertainty_grid_takes_every_q1_round_and_no_ecb_three_year_line():
    data = figures.uncertainty_grid_data(MEASURES)
    spans = data.groupby(["survey", "column", "horizon_class"]).year.agg(
        ["min", "max", "size"]
    )
    for column in figures.GRID_COLUMNS:
        for horizon in figures.GRID_HORIZONS:
            assert tuple(spans.loc["us", column, horizon]) == (2010, 2026, 17)
        assert tuple(spans.loc["ecb", column, "next_year"]) == (2010, 2026, 17)
        # The ECB asks two calendar years out in Q1 rounds only from 2013.
        assert tuple(spans.loc["ecb", column, "year_after_next"]) == (2013, 2026, 14)
        assert ("ecb", column, "three_years_ahead") not in spans.index


def test_uncertainty_grid_plots_the_published_measures_at_their_horizons():
    data = figures.uncertainty_grid_data(MEASURES)
    published = MEASURES[
        (MEASURES.quarter == 1)
        & MEASURES.horizon_class.isin(HORIZON_YEARS)
        & MEASURES.year.between(*figures.GRID_YEARS)
    ]
    merged = data.merge(
        published,
        on=["survey", "variable", "year", "horizon_class", "target_year"],
        suffixes=("", "_published"),
        validate="one_to_one",
    )
    assert len(merged) == len(data)
    assert (merged.total_sd == merged.total_sd_published).all()
    assert (merged.bin_scheme == merged.bin_scheme_published).all()
    # Each line's target year sits its horizon's number of years past the round.
    horizons = merged.horizon_class.map(HORIZON_YEARS)
    assert (merged.target_year - merged.year == horizons).all()


def _line_paths(svg):
    colors = "|".join(figures.GRID_BLUES.values())
    return re.findall(rf'<path d="M([^"]+)" fill="none" stroke="({colors})"', svg)


def test_uncertainty_grid_draws_each_line_inside_its_own_cell():
    svg = figures.uncertainty_grid_figure(MEASURES)
    boxes = list(figures.grid_cells().values())
    paths = _line_paths(svg)
    assert len(paths) == 3 + 3 + 2 + 2  # US cells three lines, ECB cells two
    for path, _ in paths:
        points = [tuple(map(float, pair.split(","))) for pair in path.split(" L")]
        xs = [x for x, _ in points]
        assert xs == sorted(xs)  # one point per round, left to right
        inside = [
            box
            for box in boxes
            if all(
                box[0] <= x <= box[0] + box[2] and box[1] <= y <= box[1] + box[3]
                for x, y in points
            )
        ]
        assert len(inside) == 1
    # Every cell's lines share one y scale, so one ceiling must clear every value.
    assert figures.uncertainty_grid_data(MEASURES).total_sd.max() < figures.GRID_Y_MAX


def test_uncertainty_grid_description_carries_the_latest_values():
    svg = figures.uncertainty_grid_figure(MEASURES)
    description = re.search(r"<desc>(.*)</desc>", svg).group(1)
    assert "US unemployment rate in 2026Q1: next year 0.61" in description
    assert "three years out 0.67" in description
    assert "Euro area real gdp growth in 2026Q1" in description
    assert description.count("three years out") == 2  # US cells only
