"""Pure statistical functions for reported forecast histograms."""

from __future__ import annotations

from collections.abc import Iterable, Sequence

import numpy as np

QUANTILES = (0.05, 0.10, 0.25, 0.50, 0.75, 0.90, 0.95)


def finite_intervals(
    intervals: Sequence[tuple[float | None, float | None]],
) -> np.ndarray:
    """Replace open tails by one adjacent-bin width, preserving input order.

    Degenerate finite intervals are retained as point masses.  They are useful
    for the scoring primitives even though the survey bin schemes themselves
    contain only positive-width intervals.
    """
    if not intervals:
        raise ValueError("At least one interval is required")

    if any(lower is None and upper is None for lower, upper in intervals):
        raise ValueError("An interval cannot be open at both ends")
    has_open_tail = any(lower is None or upper is None for lower, upper in intervals)
    has_positive_width = any(
        lower is not None and upper is not None and upper > lower
        for lower, upper in intervals
    )
    if has_open_tail and not has_positive_width:
        raise ValueError("An adjacent closed interval is required for open tails")

    output: list[tuple[float, float]] = []
    for index, (lower, upper) in enumerate(intervals):
        if lower is None:
            width = _nearest_width(intervals, index)
            lower = float(upper) - width
        elif upper is None:
            width = _nearest_width(intervals, index)
            upper = float(lower) + width
        if upper < lower:
            raise ValueError(f"Invalid interval: {(lower, upper)}")
        output.append((float(lower), float(upper)))
    return np.asarray(output, dtype=float)


def _nearest_width(
    intervals: Sequence[tuple[float | None, float | None]],
    index: int,
) -> float:
    for distance in range(1, len(intervals)):
        for cursor in (index - distance, index + distance):
            if not 0 <= cursor < len(intervals):
                continue
            lower, upper = intervals[cursor]
            if lower is not None and upper is not None and upper > lower:
                return float(upper - lower)
    raise ValueError("Open tail has no adjacent closed interval")


def bin_midpoints(
    intervals: Sequence[tuple[float | None, float | None]],
) -> np.ndarray:
    """Return midpoints, using the adjacent-bin-width convention for open tails."""
    bounds = finite_intervals(intervals)
    return bounds.mean(axis=1)


def pooled_quantiles(
    weights: np.ndarray,
    intervals: Sequence[tuple[float | None, float | None]],
    quantiles: Iterable[float] = QUANTILES,
) -> dict[str, float]:
    """Quantiles of the mean histogram, with mass uniform inside each bin."""
    levels = tuple(float(quantile) for quantile in quantiles)
    values = histogram_quantiles(weights, intervals, levels)
    return {
        _quantile_name(quantile): float(value)
        for quantile, value in zip(levels, values, strict=True)
    }


def histogram_quantiles(
    weights: np.ndarray,
    intervals: Sequence[tuple[float | None, float | None]],
    quantiles: Iterable[float] = QUANTILES,
) -> np.ndarray:
    """Return inverse-CDF values for a pooled piecewise-uniform histogram.

    Two-dimensional weights are averaged across rows before normalization,
    matching :func:`pooled_quantiles`.  The array return form is convenient for
    dense quantile grids used to connect pinball loss and CRPS.
    """
    probabilities = np.asarray(weights, dtype=float)
    if probabilities.ndim == 2:
        probabilities = probabilities.mean(axis=0)
    if probabilities.ndim != 1 or probabilities.size != len(intervals):
        raise ValueError("Weights and intervals have incompatible shapes")
    levels = np.asarray(tuple(float(quantile) for quantile in quantiles), dtype=float)
    if levels.ndim != 1:
        raise ValueError("Quantiles must be one-dimensional")
    if np.any(~np.isfinite(levels)) or np.any((levels < 0) | (levels > 1)):
        invalid = levels[(~np.isfinite(levels)) | (levels < 0) | (levels > 1)][0]
        raise ValueError(f"Invalid quantile: {invalid}")

    total = probabilities.sum()
    if not np.isfinite(total) or total <= 0:
        return np.full(levels.shape, np.nan, dtype=float)
    probabilities = probabilities / total

    raw_order = np.argsort(
        [-np.inf if lower is None else lower for lower, _ in intervals], kind="stable"
    )
    bounds = finite_intervals(intervals)[raw_order]
    probabilities = probabilities[raw_order]
    cumulative = np.cumsum(probabilities)
    indices = np.searchsorted(cumulative, levels, side="left")
    indices = np.minimum(indices, len(bounds) - 1)
    masses = probabilities[indices]
    prior = np.where(indices == 0, 0.0, cumulative[np.maximum(indices - 1, 0)])
    fractions = np.divide(
        levels - prior,
        masses,
        out=np.zeros_like(levels),
        where=masses > 0,
    )
    lower = bounds[indices, 0]
    upper = bounds[indices, 1]
    return lower + np.clip(fractions, 0, 1) * (upper - lower)


def _quantile_name(quantile: float) -> str:
    return f"q{round(100 * quantile):02d}"


def filter_probability_rows(
    probabilities: np.ndarray,
) -> tuple[np.ndarray, dict[str, int]]:
    """Keep valid percentage histograms and normalize each retained row to one.

    Partial missing responses are interpreted as zero.  Every supplied value must
    be finite and in [0, 100], and the row total must be strictly within two
    percentage points of 100.  Invalid values are rejected, never clipped.
    """
    values = np.asarray(probabilities, dtype=float)
    if values.ndim != 2:
        raise ValueError("Probabilities must be a two-dimensional array")
    all_nan = np.isnan(values).all(axis=1)
    nonempty = values[~all_nan]
    filled = np.where(np.isnan(nonempty), 0.0, nonempty)
    valid_values = (np.isfinite(filled) & (filled >= 0.0) & (filled <= 100.0)).all(
        axis=1
    )
    filled = np.where(valid_values[:, None], filled, 0.0)
    sums = filled.sum(axis=1)
    valid = valid_values & (np.abs(sums - 100.0) < 2.0)
    kept = filled[valid]
    if kept.size:
        kept = kept / kept.sum(axis=1, keepdims=True)
    counts = {
        "rows_total": len(values),
        "rows_all_nan": int(all_nan.sum()),
        "rows_nonempty": len(nonempty),
        "rows_kept": int(valid.sum()),
        "rows_dropped": int((~valid).sum()),
    }
    return kept, counts


def round_stats(
    probabilities: np.ndarray,
    midpoints: Sequence[float],
    intervals: Sequence[tuple[float | None, float | None]] | None = None,
) -> dict[str, float | int]:
    """Decompose the variance of the equally weighted respondent mixture.

    With intervals, each bin is uniform over its finite bounds, consistently with
    pooled quantiles and CRPS.  Without intervals, mass is at the supplied
    midpoints.  Disagreement uses population variance across the retained
    respondents, including zero for a single respondent, so within plus between
    is exactly the empirical mixture variance.
    """
    mids = np.asarray(midpoints, dtype=float)
    values = np.asarray(probabilities, dtype=float)
    if mids.ndim != 1 or values.ndim != 2 or values.shape[1] != mids.size:
        raise ValueError("Probabilities and midpoints have incompatible shapes")
    if not np.isfinite(mids).all():
        raise ValueError("Midpoints must be finite")
    bin_variances = np.zeros_like(mids)
    if intervals is not None:
        if len(intervals) != mids.size:
            raise ValueError("Intervals and midpoints have incompatible shapes")
        bounds = finite_intervals(intervals)
        if not np.isfinite(bounds).all():
            raise ValueError("Interval bounds must be finite after closing tails")
        centers = bounds.mean(axis=1)
        if not np.allclose(mids, centers, rtol=0.0, atol=1e-12):
            raise ValueError("Midpoints must match the interval centers")
        mids = centers
        bin_variances = np.square(bounds[:, 1] - bounds[:, 0]) / 12.0
    weights, counts = filter_probability_rows(values)
    result: dict[str, float | int] = {"n": counts["rows_kept"], **counts}
    if not len(weights):
        result.update(
            {
                "mean": np.nan,
                "median": np.nan,
                "within_sd": np.nan,
                "disagreement": np.nan,
                "total_sd": np.nan,
                "share_between": np.nan,
            }
        )
        if intervals is not None:
            result.update({_quantile_name(q): np.nan for q in QUANTILES})
            result["iqr"] = np.nan
        return result

    individual_means = (weights * mids).sum(axis=1)
    individual_variances = (
        weights * (np.square(mids - individual_means[:, None]) + bin_variances)
    ).sum(axis=1)
    within_variance = float(individual_variances.mean())
    between_variance = float(individual_means.var(ddof=0))
    total_variance = within_variance + between_variance
    result.update(
        {
            "mean": float(individual_means.mean()),
            "median": float(np.median(individual_means)),
            "within_sd": float(np.sqrt(within_variance)),
            "disagreement": float(np.sqrt(between_variance)),
            "total_sd": float(np.sqrt(total_variance)),
            "share_between": (
                float(between_variance / total_variance)
                if total_variance > 0
                else np.nan
            ),
        }
    )
    if intervals is not None:
        quantile_values = pooled_quantiles(weights, intervals)
        result.update(quantile_values)
        result["iqr"] = quantile_values["q75"] - quantile_values["q25"]
    return result
