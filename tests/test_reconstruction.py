"""How printed bin labels become continuous support, and what that choice moves."""

from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from expectations.bins import (
    RECONSTRUCTION,
    RECONSTRUCTIONS,
    BinScheme,
    support_intervals,
    us_bin_scheme,
)
from expectations.measures import bin_midpoints, round_stats
from expectations.scores import histogram_cdf, histogram_crps

ROOT = Path(__file__).resolve().parents[1]

LABELS = [(None, 1), (1, 1.9), (2, 2.9), (3, 3.9), (4, None)]


def test_the_primary_reconstruction_is_contiguous():
    assert RECONSTRUCTION == "contiguous"
    assert set(RECONSTRUCTIONS) == {"contiguous", "literal", "midpoint"}


def test_contiguous_extends_each_upper_label_to_the_next_lower_label():
    assert support_intervals(LABELS) == ((None, 1), (1, 2), (2, 3), (3, 4), (4, None))


def test_literal_keeps_the_printed_labels():
    assert support_intervals(LABELS, "literal") == tuple(LABELS)


def test_midpoint_splits_each_strip_between_labels():
    support = support_intervals(LABELS, "midpoint")
    assert support[0] == (None, 1)  # no strip between "below 1" and "1.0 to 1.9"
    assert support[1] == pytest.approx((1, 1.95))
    assert support[2] == pytest.approx((1.95, 2.95))
    assert support[3] == pytest.approx((2.95, 3.95))
    assert support[4][0] == pytest.approx(3.95) and support[4][1] is None


def test_source_order_is_preserved():
    descending = list(reversed(LABELS))
    assert support_intervals(descending) == tuple(reversed(support_intervals(LABELS)))


def test_half_point_and_negative_labels():
    ecb = [(None, -1.0), (-1.0, -0.6), (-0.5, -0.1), (0.0, 0.4), (0.5, None)]
    assert support_intervals(ecb) == (
        (None, -1.0),
        (-1.0, -0.5),
        (-0.5, 0.0),
        (0.0, 0.5),
        (0.5, None),
    )


def test_uneven_modern_us_bins_stay_uneven():
    support = dict(enumerate(us_bin_scheme("PRGDP", 2026, 1).support()))
    finite = [
        upper - lower for lower, upper in support.values() if None not in (lower, upper)
    ]
    assert len(set(np.round(finite, 9))) > 1
    assert (4, 5.5) in support.values()  # 4.0 stays a bin edge


def test_lower_labels_never_move_under_the_primary_reconstruction():
    for year in (1969, 1975, 1985, 1995, 2012, 2021, 2026):
        scheme = us_bin_scheme("PRGDP", year, 1)
        for (lower, _), (support_lower, _) in zip(scheme.intervals, scheme.support()):
            assert lower == support_lower


def test_unknown_convention_and_overlap_fail_loudly():
    with pytest.raises(ValueError, match="Unknown reconstruction"):
        support_intervals(LABELS, "rounded")
    with pytest.raises(ValueError, match="overlap"):
        support_intervals([(0, 1.2), (1, 2)])
    with pytest.raises(ValueError, match="open tail"):
        support_intervals([(0, None), (1, 2)])


def test_scheme_midpoints_follow_the_convention():
    scheme = BinScheme("toy", tuple(LABELS))
    assert scheme.midpoints == pytest.approx((0.55, 1.45, 2.45, 3.45, 4.45))
    assert scheme.support_midpoints() == pytest.approx((0.5, 1.5, 2.5, 3.5, 4.5))
    assert scheme.support_midpoints("literal") == pytest.approx(scheme.midpoints)


def test_worked_example_mean_pit_and_crps():
    """Equal mass on "2.0 to 2.9" and "3.0 to 3.9", outcome 2.95 in the old strip."""
    labels = [(1, 1.9), (2, 2.9), (3, 3.9), (4, 4.9)]
    weights = np.array([0.0, 0.5, 0.5, 0.0])
    expected = {
        "literal": {"mean": 2.95, "pit": 0.5, "crps": 0.175},
        "contiguous": {"mean": 3.0, "pit": 0.475, "crps": 0.167917},
    }
    for convention, want in expected.items():
        intervals = list(support_intervals(labels, convention))
        stats = round_stats(weights[None, :] * 100, bin_midpoints(intervals), intervals)
        assert stats["mean"] == pytest.approx(want["mean"])
        assert histogram_cdf(weights, intervals, 2.95) == pytest.approx(want["pit"])
        assert histogram_crps(weights, intervals, 2.95) == pytest.approx(
            want["crps"], abs=1e-6
        )


def test_the_variance_identity_survives_every_convention():
    rng = np.random.default_rng(7)
    raw = rng.dirichlet(np.ones(len(LABELS)), size=9) * 100
    for convention in RECONSTRUCTIONS:
        intervals = list(support_intervals(LABELS, convention))
        stats = round_stats(raw, bin_midpoints(intervals), intervals)
        assert stats["within_sd"] ** 2 + stats["disagreement"] ** 2 == pytest.approx(
            stats["total_sd"] ** 2, rel=1e-12
        )


def test_published_sensitivity_table_records_what_the_choice_moves():
    table = pd.read_csv(ROOT / "outputs" / "reconstruction_sensitivity.csv")
    assert set(table.convention) == set(RECONSTRUCTIONS)
    wide = table.pivot(index="statistic", columns="convention", values="value")

    # The window comparison: every mean shifts by the same twentieth of a point.
    for statistic in ("us_next_year_mean_2015_19", "us_next_year_mean_2025_26"):
        assert wide.loc[statistic, "contiguous"] - wide.loc[
            statistic, "literal"
        ] == pytest.approx(0.05, abs=0.002)
    fall = lambda convention: (
        wide.loc["us_next_year_mean_2015_19", convention]
        - wide.loc["us_next_year_mean_2025_26", convention]
    )
    assert fall("contiguous") == pytest.approx(fall("literal"), abs=0.002)

    # 4.0 is a printed lower label, so only the midpoint reading can move P(>4%).
    for statistic in (
        "us_next_year_p_above_4_2015_19",
        "us_next_year_p_above_4_2025_26",
    ):
        assert wide.loc[statistic, "contiguous"] == pytest.approx(
            wide.loc[statistic, "literal"]
        )

    # The one-sigma count is the headline that moves: target year 2011 sits on the band's edge.
    assert wide.loc["us_q1_next_year_inside_1sd", "literal"] == 23
    assert wide.loc["us_q1_next_year_inside_1sd", "contiguous"] == 22
    assert wide.loc["us_q1_next_year_inside_1sd", "midpoint"] == 23
    assert wide.loc["us_q1_next_year_targets", "contiguous"] == 33

    # The published outputs use the primary reconstruction.
    measures = pd.read_csv(ROOT / "outputs" / "measures.csv")
    row = measures[
        (measures.survey == "us")
        & (measures.variable == "PRGDP")
        & (measures.year == 2026)
        & (measures.quarter == 1)
        & (measures.horizon_class == "next_year")
    ].iloc[0]
    assert row.total_sd == pytest.approx(
        wide.loc["us_next_year_total_sd_2026q1", "contiguous"]
    )
