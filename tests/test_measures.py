import numpy as np
import pytest

from expectations.measures import (
    filter_probability_rows,
    finite_intervals,
    histogram_quantiles,
    round_stats,
)


def test_midpoint_moments_equal_independently_pooled_distribution():
    probabilities = np.array(
        [
            [20.0, 80.0, 0.0],
            [0.0, 40.0, 60.0],
            [50.0, 0.0, 50.0],
        ]
    )
    midpoints = np.array([-1.0, 0.0, 2.0])
    stats = round_stats(probabilities, midpoints)
    pooled = (probabilities / 100.0).mean(axis=0)
    expected_mean = pooled @ midpoints
    expected_variance = pooled @ (midpoints - expected_mean) ** 2

    assert stats["mean"] == pytest.approx(expected_mean)
    assert stats["total_sd"] ** 2 == pytest.approx(expected_variance)

    assert stats["total_sd"] ** 2 == pytest.approx(
        stats["within_sd"] ** 2 + stats["disagreement"] ** 2
    )
    assert stats["share_between"] == pytest.approx(
        stats["disagreement"] ** 2 / stats["total_sd"] ** 2
    )


def test_sum_filter_is_strict_and_fills_partial_nan_with_zero():
    probabilities = np.array(
        [
            [50.0, 50.0, np.nan],
            [49.0, 49.0, 0.0],
            [51.0, 51.0, 0.0],
            [np.nan, np.nan, np.nan],
            [20.0, 40.0, 39.5],
        ]
    )

    weights, counts = filter_probability_rows(probabilities)

    assert counts == {
        "rows_total": 5,
        "rows_all_nan": 1,
        "rows_nonempty": 4,
        "rows_kept": 2,
        "rows_dropped": 2,
    }
    np.testing.assert_allclose(weights.sum(axis=1), 1.0)


def test_filter_rejects_invalid_cells_even_when_total_is_near_100():
    probabilities = np.array(
        [
            [-0.01, 50.01, 50.0],
            [100.5, 0.0, np.nan],
            [np.inf, -np.inf, 100.0],
            [np.inf, 0.0, np.nan],
            [-np.inf, 100.0, np.nan],
            [100.0, 0.0, np.nan],
            [49.5, 49.5, np.nan],
            [50.5, 50.5, np.nan],
        ]
    )

    weights, counts = filter_probability_rows(probabilities)

    assert counts["rows_kept"] == 3
    assert counts["rows_dropped"] == 5
    np.testing.assert_allclose(
        weights, [[1.0, 0.0, 0.0], [0.5, 0.5, 0.0], [0.5, 0.5, 0.0]]
    )


@pytest.mark.parametrize(
    "intervals, probabilities",
    [
        ([(-2.0, 0.0), (0.0, 4.0)], [[100.0, 0.0], [0.0, 100.0]]),
        (
            [(-3.0, -2.0), (0.0, 2.0), (4.0, 7.0)],
            [[19.8, 49.5, 29.7], [50.5, 0.0, 50.5]],
        ),
        ([(None, 0.0), (0.0, 2.0), (2.0, None)], [[25.0, 50.0, 25.0]]),
        ([(0.0, 0.0), (2.0, 2.0)], [[100.0, 0.0], [0.0, 100.0]]),
    ],
)
def test_uniform_moments_match_independent_mixture_integration(
    intervals, probabilities
):
    bounds = finite_intervals(intervals)
    centers = bounds.mean(axis=1)
    values = np.asarray(probabilities)
    weights = values / values.sum(axis=1, keepdims=True)

    # Gauss-Legendre integration is exact for both x and x².  This checks the
    # actual uniform mixture independently of the width²/12 decomposition.
    nodes, integration_weights = np.polynomial.legendre.leggauss(3)
    locations = centers[:, None] + np.diff(bounds, axis=1) * nodes / 2.0
    bin_first = locations @ (integration_weights / 2.0)
    bin_second = locations**2 @ (integration_weights / 2.0)
    respondent_first = weights @ bin_first
    respondent_second = weights @ bin_second
    pooled = weights.mean(axis=0)
    pooled_first = pooled @ bin_first
    pooled_variance = pooled @ bin_second - pooled_first**2

    stats = round_stats(values, centers, intervals)

    assert stats["n"] == len(values)
    assert stats["mean"] == pytest.approx(pooled_first)
    assert stats["within_sd"] ** 2 == pytest.approx(
        np.mean(respondent_second - respondent_first**2)
    )
    assert stats["disagreement"] ** 2 == pytest.approx(
        np.mean((respondent_first - pooled_first) ** 2)
    )
    assert stats["total_sd"] ** 2 == pytest.approx(pooled_variance)
    assert stats["total_sd"] ** 2 == pytest.approx(
        stats["within_sd"] ** 2 + stats["disagreement"] ** 2
    )


@pytest.mark.parametrize("intervals", [None, [(0.0, 0.0), (2.0, 2.0)]])
def test_single_respondent_has_zero_disagreement(intervals):
    stats = round_stats(np.array([[50.0, 50.0]]), [0.0, 2.0], intervals)

    assert stats["mean"] == pytest.approx(1.0)
    assert stats["within_sd"] == pytest.approx(1.0)
    assert stats["total_sd"] == pytest.approx(1.0)
    assert stats["disagreement"] == 0.0
    assert stats["share_between"] == 0.0


def test_single_uniform_forecast_has_bin_variance():
    stats = round_stats(np.array([[100.0]]), [2.0], [(0.0, 4.0)])

    assert stats["mean"] == 2.0
    assert stats["disagreement"] == 0.0
    assert stats["within_sd"] ** 2 == pytest.approx(4.0 / 3.0)
    assert stats["total_sd"] ** 2 == pytest.approx(4.0 / 3.0)


def test_single_point_forecast_has_zero_total_variance():
    stats = round_stats(np.array([[100.0]]), [2.0], [(2.0, 2.0)])

    assert stats["mean"] == 2.0
    assert stats["within_sd"] == 0.0
    assert stats["disagreement"] == 0.0
    assert stats["total_sd"] == 0.0
    assert np.isnan(stats["share_between"])


def test_intervals_and_moments_cannot_describe_different_distributions():
    with pytest.raises(ValueError, match="match the interval centers"):
        round_stats(np.array([[100.0]]), [2.0], [(0.0, 2.0)])


def test_pooled_quantiles_are_uniform_within_bins_and_report_iqr():
    probabilities = np.array([[25.0, 50.0, 25.0], [25.0, 50.0, 25.0]])
    intervals = [(None, 0.0), (0.0, 1.0), (1.0, None)]

    stats = round_stats(probabilities, [-0.5, 0.5, 1.5], intervals)

    assert stats["q25"] == pytest.approx(0.0)
    assert stats["q50"] == pytest.approx(0.5)
    assert stats["q75"] == pytest.approx(1.0)
    assert stats["iqr"] == pytest.approx(1.0)


def test_quantiles_require_normalized_weights_instead_of_rescaling_them():
    """Rescaling a normalized histogram would decide bin-edge quantiles by rounding."""
    intervals = [(None, 0.0), (0.0, 1.0), (1.0, None)]

    assert histogram_quantiles([0.25, 0.5, 0.25], intervals, [0.75]) == pytest.approx(
        [1.0]
    )
    with pytest.raises(ValueError, match="must sum to one"):
        histogram_quantiles([25.0, 50.0, 25.0], intervals, [0.75])
    assert np.isnan(histogram_quantiles([0.0, 0.0, 0.0], intervals, [0.75])).all()
