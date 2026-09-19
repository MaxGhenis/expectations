import math
from itertools import pairwise

import numpy as np
import pandas as pd
import pytest

from expectations.build import aggregate_density
from expectations.measures import finite_intervals, histogram_quantiles
from expectations.scores import (
    empirical_crps,
    gaussian_crps,
    histogram_cdf,
    histogram_crps,
    pinball_loss,
    score_density_calibration,
)


def _random_histogram(rng, bin_count):
    cursor = float(rng.uniform(-4.0, -1.0))
    intervals = []
    for _ in range(bin_count):
        width = float(rng.uniform(0.5, 1.25))
        intervals.append((cursor, cursor + width))
        cursor += width + float(rng.uniform(0.05, 0.4))
    intervals[0] = (None, intervals[0][1])
    intervals[-1] = (intervals[-1][0], None)
    weights = rng.dirichlet(np.ones(bin_count))
    if rng.random() < 0.5:
        intervals.reverse()
        weights = weights[::-1]
    return weights, intervals


def _numerical_crps(weights, intervals, realization):
    bounds = finite_intervals(intervals)
    knots = np.unique(
        np.concatenate((bounds.ravel(), np.asarray([float(realization)])))
    )
    score = 0.0
    for left, right in pairwise(knots):
        grid = np.linspace(left, right, 20_001)
        cdf = histogram_cdf(weights, intervals, grid)
        observation_step = 1.0 if left >= realization else 0.0
        score += float(np.trapezoid((cdf - observation_step) ** 2, grid))
    return score


def _sample_histogram(rng, weights, intervals, size):
    masses = np.asarray(weights, dtype=float)
    masses = masses / masses.sum()
    bounds = finite_intervals(intervals)
    components = rng.choice(len(masses), size=size, p=masses)
    lower = bounds[components, 0]
    widths = bounds[components, 1] - lower
    return lower + widths * rng.random(size)


def _uniform_crps(lower, upper, realization):
    width = upper - lower
    if realization < lower:
        return lower - realization + width / 3.0
    if realization > upper:
        return realization - upper + width / 3.0
    return ((realization - lower) ** 3 + (upper - realization) ** 3) / (3.0 * width**2)


def test_histogram_cdf_respects_literal_gaps_tails_and_point_masses():
    intervals = [(None, 0.0), (0.5, 1.0), (2.0, None)]
    values = np.asarray(
        [-1.0, -0.25, 0.0, 0.25, 0.5, 0.75, 1.0, 1.5, 2.0, 2.25, 2.5, 3.0]
    )

    actual = histogram_cdf([0.2, 0.5, 0.3], intervals, values)

    np.testing.assert_allclose(
        actual,
        [0.0, 0.1, 0.2, 0.2, 0.2, 0.45, 0.7, 0.7, 0.7, 0.85, 1.0, 1.0],
    )
    np.testing.assert_allclose(
        histogram_cdf([1.0], [(1.5, 1.5)], np.asarray([1.4, 1.5, 1.6])),
        [0.0, 1.0, 1.0],
    )


def test_exact_crps_matches_brute_force_numerical_integration():
    rng = np.random.default_rng(20260826)
    for bin_count in (3, 4, 5, 6, 7, 8):
        weights, intervals = _random_histogram(rng, bin_count)
        bounds = finite_intervals(intervals)
        realization = float(
            rng.uniform(bounds[:, 0].min() - 1.0, bounds[:, 1].max() + 1.0)
        )

        exact = histogram_crps(weights, intervals, realization)
        numerical = _numerical_crps(weights, intervals, realization)

        assert exact >= 0.0
        assert exact == pytest.approx(numerical, rel=0.0, abs=1e-8)


def test_crps_matches_energy_identity_by_monte_carlo():
    cases = [
        ([0.2, 0.5, 0.3], [(None, -1.0), (-0.5, 0.5), (1.0, None)], 0.2),
        ([0.15, 0.25, 0.6], [(-2.0, -1.0), (0.0, 0.0), (1.0, 3.0)], 4.0),
        ([1.0], [(2.25, 2.25)], -0.75),
    ]
    rng = np.random.default_rng(9137)
    for weights, intervals, realization in cases:
        first = _sample_histogram(rng, weights, intervals, 300_000)
        second = _sample_histogram(rng, weights, intervals, 300_000)
        monte_carlo = np.mean(np.abs(first - realization)) - 0.5 * np.mean(
            np.abs(first - second)
        )

        assert histogram_crps(weights, intervals, realization) == pytest.approx(
            monte_carlo, abs=0.012
        )


@pytest.mark.parametrize("realization", [-4.0, 1.5, 7.0])
def test_point_mass_crps_is_absolute_error(realization):
    assert histogram_crps([1.0], [(1.5, 1.5)], realization) == pytest.approx(
        abs(1.5 - realization)
    )


@pytest.mark.parametrize("realization", [-4.0, -1.0, 0.25, 2.0, 5.0])
def test_uniform_crps_closed_form(realization):
    lower, upper = -1.0, 2.0
    expected = _uniform_crps(lower, upper, realization)

    assert histogram_crps([7.0], [(lower, upper)], realization) == pytest.approx(
        expected
    )


def test_crps_is_nonnegative_for_random_histograms():
    rng = np.random.default_rng(73)
    for _ in range(100):
        weights, intervals = _random_histogram(rng, int(rng.integers(3, 9)))
        realization = float(rng.normal())
        assert histogram_crps(weights, intervals, realization) >= 0.0


# Signed mass reaches no public entry point legitimately: every histogram in the
# pipeline is normalized by filter_probability_rows, which rejects negative
# cells outright. A negative bin makes the "CDF" non-monotone, so these
# primitives reject it rather than returning a number that reads like a score.
TWO_BINS = [(0.0, 1.0), (1.0, 2.0)]
WEIGHTED_ENTRY_POINTS = {
    "histogram_cdf": lambda weights: histogram_cdf(weights, TWO_BINS, 0.5),
    "histogram_crps": lambda weights: histogram_crps(weights, TWO_BINS, 0.5),
    "histogram_quantiles": lambda weights: histogram_quantiles(
        weights, TWO_BINS, [0.5]
    ),
}


@pytest.mark.parametrize(
    "call", WEIGHTED_ENTRY_POINTS.values(), ids=WEIGHTED_ENTRY_POINTS
)
@pytest.mark.parametrize("weights", [[-1.0, 2.0], [-1e-9, 1.0 + 1e-9]])
def test_public_distribution_functions_reject_negative_weights(call, weights):
    with pytest.raises(ValueError, match="must be nonnegative"):
        call(weights)


@pytest.mark.parametrize(
    "call", WEIGHTED_ENTRY_POINTS.values(), ids=WEIGHTED_ENTRY_POINTS
)
@pytest.mark.parametrize("bad", [math.nan, math.inf, -math.inf])
def test_public_distribution_functions_reject_nonfinite_weights(call, bad):
    with pytest.raises(ValueError, match="must be finite"):
        call([bad, 1.0])


def test_negative_weights_would_otherwise_produce_a_non_monotone_cdf():
    """The rejected input is not merely unusual; it breaks the CDF contract."""
    masses, bounds = np.asarray([-1.0, 2.0]), TWO_BINS
    unchecked = [
        float(
            sum(
                mass * min(max((value - lower) / (upper - lower), 0.0), 1.0)
                for mass, (lower, upper) in zip(masses, bounds, strict=True)
            )
        )
        for value in (0.0, 0.5, 1.0, 1.5, 2.0)
    ]

    assert min(unchecked) < 0.0
    assert any(later < earlier for earlier, later in pairwise(unchecked))


def test_rejection_happens_before_the_sum_to_one_check():
    """A signed histogram summing to one must still be refused."""
    with pytest.raises(ValueError, match="must be nonnegative"):
        histogram_quantiles([-0.25, 1.25], TWO_BINS, [0.5])


def test_two_dimensional_offsetting_signs_cannot_hide_behind_the_mean():
    rows = np.asarray([[-0.5, 1.5], [1.5, -0.5]])

    assert np.allclose(rows.mean(axis=0), [0.5, 0.5])
    with pytest.raises(ValueError, match="must be nonnegative"):
        histogram_quantiles(rows, TWO_BINS, [0.5])


def test_all_zero_weights_remain_the_documented_degenerate_case():
    assert np.isnan(histogram_quantiles([0.0, 0.0], TWO_BINS, [0.5])).all()


def test_a_nonfinite_total_from_finite_weights_still_returns_missing_values():
    """Rejecting signed mass must not narrow the documented degenerate case.

    Each weight here is finite, so the new guard lets them through, but their
    sum overflows.  That case returned missing values before and still does.
    """
    weights = [1e308, 1e308]
    with np.errstate(over="ignore"):
        assert np.isfinite(np.asarray(weights)).all()
        assert not np.isfinite(np.sum(weights))
        assert np.isnan(histogram_quantiles(weights, TWO_BINS, [0.5])).all()


def test_histogram_quantiles_handle_gaps_points_and_dense_grids():
    levels = np.asarray([0.0, 0.1, 0.25, 0.3, 0.5, 0.5001, 0.75, 1.0])

    actual = histogram_quantiles(
        [0.25, 0.25, 0.5],
        [(0.0, 1.0), (2.0, 2.0), (3.0, 4.0)],
        levels,
    )

    np.testing.assert_allclose(actual, [0.0, 0.4, 1.0, 2.0, 2.0, 3.0002, 3.5, 4.0])


def test_integrated_pinball_loss_matches_crps():
    rng = np.random.default_rng(8102)
    levels = np.linspace(0.0, 1.0, 200_001)
    for bin_count in (3, 5, 7, 9):
        weights, intervals = _random_histogram(rng, bin_count)
        bounds = finite_intervals(intervals)
        realization = float(
            rng.uniform(bounds[:, 0].min() - 0.5, bounds[:, 1].max() + 0.5)
        )
        quantiles = histogram_quantiles(weights, intervals, levels)
        losses = np.fromiter(
            (
                pinball_loss(realization, quantile, level)
                for quantile, level in zip(quantiles, levels, strict=True)
            ),
            dtype=float,
            count=len(levels),
        )

        integrated = 2.0 * np.trapezoid(losses, levels)

        assert integrated == pytest.approx(
            histogram_crps(weights, intervals, realization), abs=3e-6
        )


@pytest.mark.parametrize(
    ("realization", "quantile", "tau", "expected"),
    [(2.0, 1.0, 0.25, 0.25), (1.0, 2.0, 0.25, 0.75), (1.0, 1.0, 0.9, 0.0)],
)
def test_pinball_loss_definition(realization, quantile, tau, expected):
    assert pinball_loss(realization, quantile, tau) == pytest.approx(expected)


def test_pinball_loss_rejects_invalid_level():
    with pytest.raises(ValueError, match="Invalid quantile level"):
        pinball_loss(0.0, 1.0, 1.01)


def test_empirical_crps_matches_pairwise_definition():
    sample = np.asarray([-2.0, -0.5, 0.5, 3.0, 3.0])
    realization = 1.25
    expected = np.mean(np.abs(sample - realization)) - 0.5 * np.mean(
        np.abs(sample[:, None] - sample[None, :])
    )

    assert empirical_crps(sample, realization) == pytest.approx(expected)
    assert empirical_crps([2.0], -1.0) == pytest.approx(3.0)


def test_gaussian_crps_closed_form_and_point_limit():
    expected_at_mean = 2.5 * (math.sqrt(2.0) - 1.0) / math.sqrt(math.pi)

    assert gaussian_crps(1.0, 2.5, 1.0) == pytest.approx(expected_at_mean)
    assert gaussian_crps(1.0, 0.0, -2.0) == pytest.approx(3.0)
    assert gaussian_crps(0.0, 1.0, -1.5) == pytest.approx(gaussian_crps(0.0, 1.0, 1.5))
    with pytest.raises(ValueError, match="cannot be negative"):
        gaussian_crps(0.0, -1.0, 0.0)


def test_calibration_scoring_reuses_the_round_response_filter():
    metadata = {
        "survey": "test",
        "variable": "growth",
        "concept": "annual_growth",
        "year": 2020,
        "quarter": 1,
        "target_year": 2021,
        "target_period": "2021",
        "horizon_class": "next_year",
        "horizon_years": 1,
        "horizon_quarters": 8,
        "bin_scheme": "fixture",
    }
    intervals = [(-1.0, 0.0), (0.0, 1.0), (1.0, 2.0)]
    responses = [
        [50.0, 50.0, np.nan],
        [49.0, 49.0, 0.0],
        [np.nan, np.nan, np.nan],
        [10.0, 20.0, 70.0],
    ]
    rows = []
    for response_index, probabilities in enumerate(responses):
        for bin_index, ((lower, upper), probability) in enumerate(
            zip(intervals, probabilities, strict=True)
        ):
            rows.append(
                {
                    **metadata,
                    "response_index": response_index,
                    "bin_index": bin_index,
                    "probability": probability,
                    "lower": lower,
                    "upper": upper,
                    "midpoint": (lower + upper) / 2.0,
                }
            )
    density = pd.DataFrame(rows)
    measures, _ = aggregate_density(density)
    calibration = measures.assign(realized=0.75)

    scored = score_density_calibration(calibration, density)

    assert len(scored) == 1
    assert scored.loc[0, "n"] == 2
    retained = np.asarray([[0.5, 0.5, 0.0], [0.1, 0.2, 0.7]])
    pooled = retained.mean(axis=0)
    expected_individual = np.mean(
        [histogram_crps(row, intervals, 0.75) for row in retained]
    )
    assert scored.loc[0, "crps_pooled"] == pytest.approx(
        histogram_crps(pooled, intervals, 0.75)
    )
    assert scored.loc[0, "crps_individual_mean"] == pytest.approx(expected_individual)
    assert scored.loc[0, "pit"] == pytest.approx(histogram_cdf(pooled, intervals, 0.75))
    assert scored.loc[0, "crps_pooled"] <= scored.loc[0, "crps_individual_mean"]
