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
