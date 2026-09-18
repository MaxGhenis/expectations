"""Proper scoring rules for histogram and benchmark forecasts."""

from __future__ import annotations

import math
from collections.abc import Sequence
from itertools import pairwise
from typing import Any

import numpy as np
import pandas as pd

from .measures import (
    QUANTILES,
    filter_probability_rows,
    finite_intervals,
    histogram_quantiles,
    pooled_quantiles,
)

type Interval = tuple[float | None, float | None]

DENSITY_SCORE_KEYS = (
    "survey",
    "variable",
    "concept",
    "year",
    "quarter",
    "target_year",
    "target_period",
    "horizon_class",
    "horizon_years",
    "horizon_quarters",
    "bin_scheme",
)

DISTRIBUTION_SCORE_COLUMNS = (
    "crps_pooled",
    "crps_individual_mean",
    *(f"pinball_{round(100 * level):02d}" for level in QUANTILES),
    "pit",
)


def histogram_cdf(
    weights: Sequence[float] | np.ndarray,
    intervals: Sequence[Interval],
    value: float | np.ndarray,
) -> float | np.ndarray:
    """Evaluate the right-continuous CDF of a piecewise-uniform histogram.

    Literal gaps between intervals carry no mass.  Open tails are closed using
    one neighboring finite-bin width, and a zero-width interval is interpreted
    as a point mass.
    """
    masses, bounds = _normalized_histogram(weights, intervals)
    observations = np.asarray(value, dtype=float)
    result = np.zeros_like(observations, dtype=float)
    for mass, (lower, upper) in zip(masses, bounds, strict=True):
        width = upper - lower
        if width == 0:
            result += mass * (observations >= lower)
        else:
            result += mass * np.clip((observations - lower) / width, 0.0, 1.0)
    return float(result) if observations.ndim == 0 else result


def histogram_crps(
    weights: Sequence[float] | np.ndarray,
    intervals: Sequence[Interval],
    realization: float,
) -> float:
    """Integrate the histogram CRPS exactly over affine CDF segments.

    For each segment, the CDF minus the observation step is linear.  If its
    endpoint values are ``g0`` and ``g1`` over a segment of length ``L``, its
    squared integral is ``L * (g0**2 + g0*g1 + g1**2) / 3``.  Point-mass jumps
    have zero Lebesgue measure but affect every segment to their right.
    """
    y = float(realization)
    if not math.isfinite(y):
        raise ValueError("Realization must be finite")
    masses, bounds = _normalized_histogram(weights, intervals)
    knots = np.unique(np.concatenate((bounds.ravel(), np.asarray([y]))))
    widths = bounds[:, 1] - bounds[:, 0]
    positive_width = widths > 0

    score = 0.0
    for left, right in pairwise(knots):
        length = float(right - left)
        cdf_left = _cdf_at(masses, bounds, float(left))
        active = positive_width & (bounds[:, 0] <= left) & (bounds[:, 1] >= right)
        slope = float(np.sum(masses[active] / widths[active]))
        cdf_right_limit = cdf_left + slope * length
        observation_step = 1.0 if left >= y else 0.0
        g0 = cdf_left - observation_step
        g1 = cdf_right_limit - observation_step
        score += length * (g0 * g0 + g0 * g1 + g1 * g1) / 3.0
    return max(float(score), 0.0)


def pinball_loss(realization: float, quantile: float, tau: float) -> float:
    """Return quantile (pinball) loss at level ``tau``."""
    y = float(realization)
    q = float(quantile)
    level = float(tau)
    if not math.isfinite(level) or not 0.0 <= level <= 1.0:
        raise ValueError(f"Invalid quantile level: {tau}")
    if not math.isfinite(y) or not math.isfinite(q):
        raise ValueError("Realization and quantile must be finite")
    loss = ((1.0 if y <= q else 0.0) - level) * (q - y)
    return max(float(loss), 0.0)


def empirical_crps(sample: Sequence[float] | np.ndarray, realization: float) -> float:
    """Return CRPS for an equally weighted empirical forecast sample."""
    observations = np.asarray(sample, dtype=float)
    if observations.ndim != 1 or observations.size == 0:
        raise ValueError("Empirical sample must be a nonempty one-dimensional array")
    if not np.isfinite(observations).all():
        raise ValueError("Empirical sample must be finite")
    y = float(realization)
    if not math.isfinite(y):
        raise ValueError("Realization must be finite")

    ordered = np.sort(observations)
    count = len(ordered)
    coefficients = 2.0 * np.arange(count) - count + 1.0
    half_pairwise_mean = float(coefficients @ ordered) / count**2
    score = float(np.mean(np.abs(observations - y))) - half_pairwise_mean
    return max(score, 0.0)


def gaussian_crps(mean: float, sigma: float, realization: float) -> float:
    """Return the closed-form CRPS for a Gaussian forecast.

    This is the Gneiting--Raftery expression
    ``sigma * (z * (2 Phi(z) - 1) + 2 phi(z) - 1 / sqrt(pi))``.
    A zero standard deviation is treated as a point forecast.
    """
    location = float(mean)
    scale = float(sigma)
    y = float(realization)
    if not all(math.isfinite(value) for value in (location, scale, y)):
        raise ValueError("Gaussian score inputs must be finite")
    if scale < 0:
        raise ValueError("Gaussian standard deviation cannot be negative")
    if scale == 0:
        return abs(location - y)

    z = (y - location) / scale
    cdf = 0.5 * (1.0 + math.erf(z / math.sqrt(2.0)))
    density = math.exp(-0.5 * z * z) / math.sqrt(2.0 * math.pi)
    score = scale * (z * (2.0 * cdf - 1.0) + 2.0 * density - 1.0 / math.sqrt(math.pi))
    return max(float(score), 0.0)


def score_density_calibration(
    calibration: pd.DataFrame,
    density: pd.DataFrame,
) -> pd.DataFrame:
    """Append pooled and average-individual scores to calibration rows.

    Respondent histograms go through the same response filter used by
    :func:`expectations.measures.round_stats`.  The output preserves the
    calibration row order and columns, then appends the distribution-score fields.
    """
    required_calibration = {
        *DENSITY_SCORE_KEYS,
        "n",
        "realized",
        *(f"q{round(100 * level):02d}" for level in QUANTILES),
    }
    missing_calibration = sorted(required_calibration.difference(calibration.columns))
    if missing_calibration:
        raise ValueError(f"Calibration rows are missing columns: {missing_calibration}")

    data = density.copy()
    defaults: dict[str, Any] = {
        "target_year": pd.NA,
        "target_period": pd.NA,
        "horizon_years": np.nan,
        "horizon_quarters": np.nan,
    }
    for column, default in defaults.items():
        if column not in data:
            data[column] = default
    if "target_block" in data:
        ambiguous = data["target_year"].isna() & data["target_period"].isna()
        data.loc[ambiguous, "target_period"] = data.loc[ambiguous, "target_block"].map(
            lambda value: f"undocumented_block_{int(value)}"
        )

    response_column = next(
        (
            column
            for column in ("response_id", "response_index", "respondent")
            if column in data
        ),
        None,
    )
    required_density = {
        *DENSITY_SCORE_KEYS,
        "bin_index",
        "probability",
        "lower",
        "upper",
    }
    if response_column is None:
        required_density.add("respondent")
    missing_density = sorted(required_density.difference(data.columns))
    if missing_density:
        raise ValueError(f"Density rows are missing columns: {missing_density}")

    key_to_position: dict[tuple[object, ...], int] = {}
    for position, values in enumerate(
        calibration[list(DENSITY_SCORE_KEYS)].itertuples(index=False, name=None)
    ):
        key = _normalized_key(values)
        if key in key_to_position:
            raise ValueError(f"Duplicate calibration density key: {key}")
        key_to_position[key] = position

    scored: list[dict[str, float] | None] = [None] * len(calibration)
    grouped = data.groupby(
        list(DENSITY_SCORE_KEYS), dropna=False, observed=True, sort=False
    )
    for values, group in grouped:
        key = _normalized_key(values)
        position = key_to_position.get(key)
        if position is None:
            continue

        bin_rows = (
            group[["bin_index", "lower", "upper"]]
            .drop_duplicates()
            .sort_values("bin_index")
        )
        if bin_rows["bin_index"].duplicated().any():
            raise ValueError(f"Inconsistent bins for calibrated density group: {key}")
        probabilities = (
            group.set_index([response_column, "bin_index"])["probability"]
            .unstack("bin_index")
            .reindex(columns=bin_rows["bin_index"])
            .to_numpy(dtype=float)
        )
        weights, _ = filter_probability_rows(probabilities)
        expected_n = int(calibration.iloc[position]["n"])
        if len(weights) != expected_n:
            raise ValueError(
                f"Response-filter count changed for {key}: {len(weights)} != {expected_n}"
            )
        if not len(weights):
            raise ValueError(
                f"Calibrated density group has no retained responses: {key}"
            )

        intervals = [
            (_optional_endpoint(row.lower), _optional_endpoint(row.upper))
            for row in bin_rows.itertuples(index=False)
        ]
        pooled = weights.mean(axis=0)
        realization = float(calibration.iloc[position]["realized"])
        pooled_crps = histogram_crps(pooled, intervals, realization)
        individual_crps = float(
            np.mean(
                [
                    histogram_crps(individual, intervals, realization)
                    for individual in weights
                ]
            )
        )
        tolerance = 1e-10 * max(1.0, abs(individual_crps))
        if pooled_crps > individual_crps + tolerance:
            raise ValueError(f"Pooled CRPS exceeds average individual CRPS for {key}")

        quantiles = pooled_quantiles(pooled, intervals)
        for name, value in quantiles.items():
            emitted = float(calibration.iloc[position][name])
            if not math.isclose(value, emitted, rel_tol=0.0, abs_tol=1e-12):
                raise ValueError(
                    f"Recomputed {name} differs from calibration for {key}: "
                    f"{value} != {emitted}"
                )
        pit = float(histogram_cdf(pooled, intervals, realization))
        if pit < -1e-12 or pit > 1.0 + 1e-12:
            raise ValueError(f"Pooled PIT is outside [0, 1] for {key}: {pit}")
        row_scores = {
            "crps_pooled": pooled_crps,
            "crps_individual_mean": individual_crps,
            "pit": float(np.clip(pit, 0.0, 1.0)),
        }
        for level in QUANTILES:
            suffix = f"{round(100 * level):02d}"
            row_scores[f"pinball_{suffix}"] = pinball_loss(
                realization, quantiles[f"q{suffix}"], level
            )
        scored[position] = row_scores

    missing_positions = [index for index, values in enumerate(scored) if values is None]
    if missing_positions:
        examples = missing_positions[:5]
        raise ValueError(
            f"No respondent histogram found for {len(missing_positions)} "
            f"calibration rows; first positions: {examples}"
        )

    output = calibration.copy()
    for column in DISTRIBUTION_SCORE_COLUMNS:
        output[column] = [values[column] for values in scored if values is not None]
    return output


def _normalized_histogram(
    weights: Sequence[float] | np.ndarray,
    intervals: Sequence[Interval],
) -> tuple[np.ndarray, np.ndarray]:
    masses = np.asarray(weights, dtype=float)
    if masses.ndim != 1 or masses.size != len(intervals):
        raise ValueError("Weights and intervals have incompatible shapes")
    if not np.isfinite(masses).all():
        raise ValueError("Histogram weights must be finite")
    total = float(masses.sum())
    if total <= 0:
        raise ValueError("Histogram weights must have positive total mass")
    bounds = finite_intervals(intervals)
    if not np.isfinite(bounds).all():
        raise ValueError("Histogram bounds must be finite after closing tails")
    return masses / total, bounds


def _cdf_at(masses: np.ndarray, bounds: np.ndarray, value: float) -> float:
    widths = bounds[:, 1] - bounds[:, 0]
    positive_width = widths > 0
    fractions = np.zeros_like(masses)
    fractions[positive_width] = np.clip(
        (value - bounds[positive_width, 0]) / widths[positive_width],
        0.0,
        1.0,
    )
    fractions[~positive_width] = value >= bounds[~positive_width, 0]
    return float(masses @ fractions)


def _normalized_key(values: Sequence[object]) -> tuple[object, ...]:
    return tuple(_normalized_key_value(value) for value in values)


def _normalized_key_value(value: object) -> object:
    if value is None or pd.isna(value):
        return None
    if isinstance(value, np.generic):
        value = value.item()
    if isinstance(value, float) and value.is_integer():
        return int(value)
    return value


def _optional_endpoint(value: object) -> float | None:
    return None if pd.isna(value) else float(value)


__all__ = [
    "DENSITY_SCORE_KEYS",
    "DISTRIBUTION_SCORE_COLUMNS",
    "empirical_crps",
    "gaussian_crps",
    "histogram_cdf",
    "histogram_crps",
    "histogram_quantiles",
    "pinball_loss",
    "score_density_calibration",
]
