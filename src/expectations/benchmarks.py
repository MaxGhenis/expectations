"""Expanding-window CRPS benchmarks for calibrated density forecasts.

Every benchmark window admits only target periods that completed strictly before
the forecast round being scored, so no benchmark is fitted on an outcome its
forecast was still predicting.  The outcome values themselves are the revised
(latest-vintage) series from :mod:`expectations.realizations`; this repository
archives no real-time data vintages, so the benchmarks are not a reconstruction
of the information set a forecaster actually held.
"""

from __future__ import annotations

import math
import re
from pathlib import Path

import numpy as np
import pandas as pd

from expectations.realizations import (
    DEFAULT_RAW_DIR,
    _canonical_survey,
    _canonical_target_period,
    _canonical_variable,
    load_realization_history,
)
from expectations.scores import empirical_crps, gaussian_crps

MIN_BENCHMARK_OBSERVATIONS = 10

BENCHMARK_COLUMNS = (
    "n_climatology",
    "n_gaussian",
    "crps_climatology",
    "crps_gaussian",
    "skill_vs_climatology",
    "skill_vs_gaussian",
)

_MONTH_NUMBERS = {
    "jan": 1,
    "feb": 2,
    "mar": 3,
    "apr": 4,
    "may": 5,
    "jun": 6,
    "jul": 7,
    "aug": 8,
    "sep": 9,
    "oct": 10,
    "nov": 11,
    "dec": 12,
}


empirical_sample_crps = empirical_crps


def period_completion_ordinal(
    target_period: object = None,
    *,
    target_year: object = None,
) -> int:
    """Map a target to the quarter in which its target period completes.

    Annual targets complete in Q4, quarterly targets in their named quarter, and
    monthly targets in the quarter containing the named month.  Benchmark windows
    use a strict comparison against this ordinal, so a target is not available to
    a forecast made in its completion quarter.  Completion of the target period is
    the filter, not publication of the statistic: the outcome for a period that has
    just ended is used as soon as the period ends, at its revised value.
    """
    canonical = _canonical_target_period(target_period)
    if canonical is None or pd.isna(canonical):
        canonical = _canonical_target_period(target_year)
    if canonical is None or pd.isna(canonical):
        raise ValueError("A target period or target year is required")

    text = str(canonical)
    if match := re.fullmatch(r"(\d{4})", text):
        year = int(match.group(1))
        quarter = 4
    elif match := re.fullmatch(r"(\d{4})Q([1-4])", text):
        year = int(match.group(1))
        quarter = int(match.group(2))
    elif match := re.fullmatch(r"(\d{4})([A-Za-z]{3})", text):
        year = int(match.group(1))
        month = _MONTH_NUMBERS.get(match.group(2).lower())
        if month is None:
            raise ValueError(f"Unsupported target period: {target_period!r}")
        quarter = (month + 2) // 3
    else:
        raise ValueError(f"Unsupported target period: {target_period!r}")
    return 4 * year + quarter


def add_benchmark_scores(
    scored: pd.DataFrame,
    realization_history: pd.DataFrame | None = None,
    *,
    raw_dir: str | Path = DEFAULT_RAW_DIR,
    min_history: int = MIN_BENCHMARK_OBSERVATIONS,
) -> pd.DataFrame:
    """Append expanding-window climatology and Gaussian benchmark scores.

    ``scored`` must be the full calibration-row universe with a pooled CRPS.
    Climatology uses the longest local realization history matching the row's exact
    realization concept.  Gaussian scale uses prior errors from the exact
    ``(survey, variable, horizon_class)`` group.  Both windows admit only targets
    whose target period completed strictly before the current forecast round, and
    both read revised outcomes rather than the vintages published at that time.
    """
    if (
        isinstance(min_history, bool)
        or not isinstance(min_history, (int, np.integer))
        or min_history <= 0
    ):
        raise ValueError("min_history must be a positive integer")

    mean_column = "consensus_mean" if "consensus_mean" in scored else "mean"
    required = {
        "survey",
        "variable",
        "horizon_class",
        "year",
        "quarter",
        "realized",
        "realization_concept",
        "error",
        "crps_pooled",
        mean_column,
    }
    missing = sorted(required.difference(scored.columns))
    if missing:
        raise ValueError(f"Scored calibration rows are missing columns: {missing}")
    if "target_period" not in scored and "target_year" not in scored:
        raise ValueError("Scored calibration rows require a target period or year")

    history = (
        load_realization_history(raw_dir)
        if realization_history is None
        else realization_history.copy()
    )
    history_required = {
        "survey",
        "variable",
        "realized",
        "realization_concept",
    }
    missing_history = sorted(history_required.difference(history.columns))
    if missing_history:
        raise ValueError(f"Realization history is missing columns: {missing_history}")
    if "target_period" not in history and "target_year" not in history:
        raise ValueError("Realization history requires a target period or year")

    output = scored.copy()
    rounds = _round_ordinals(output)
    target_completions = _completion_ordinals(output)
    realized = _finite_numeric(output["realized"], name="realized")
    means = _finite_numeric(output[mean_column], name=mean_column)
    errors = _finite_numeric(output["error"], name="error")
    pooled = _finite_numeric(output["crps_pooled"], name="crps_pooled")
    if (pooled < 0.0).any():
        raise ValueError("crps_pooled cannot be negative")

    survey_keys = output["survey"].map(_canonical_survey).to_numpy(dtype=object)
    variable_keys = np.asarray(
        [
            _canonical_variable(survey, variable)
            for survey, variable in zip(survey_keys, output["variable"], strict=False)
        ],
        dtype=object,
    )
    concepts = _required_strings(output["realization_concept"], "realization_concept")
    horizons = _required_strings(output["horizon_class"], "horizon_class")

    actual_groups = _actual_history_groups(history)
    error_groups = _error_history_groups(
        survey_keys,
        variable_keys,
        horizons,
        rounds,
        target_completions,
        errors,
    )

    row_count = len(output)
    climatology_counts = np.zeros(row_count, dtype=np.int64)
    gaussian_counts = np.zeros(row_count, dtype=np.int64)
    climatology_scores = np.full(row_count, np.nan)
    gaussian_scores = np.full(row_count, np.nan)
    actual_cache: dict[tuple[tuple[str, str, str], int], np.ndarray] = {}
    sigma_cache: dict[tuple[tuple[str, str, str], int], tuple[int, float]] = {}

    for position in range(row_count):
        round_ordinal = int(rounds[position])
        actual_key = (
            str(survey_keys[position]),
            str(variable_keys[position]),
            str(concepts[position]),
        )
        actual_cache_key = (actual_key, round_ordinal)
        if actual_cache_key not in actual_cache:
            completions, values = actual_groups.get(
                actual_key,
                (np.empty(0, dtype=np.int64), np.empty(0, dtype=float)),
            )
            actual_cache[actual_cache_key] = values[completions < round_ordinal]
        sample = actual_cache[actual_cache_key]
        climatology_counts[position] = len(sample)
        if len(sample) >= min_history:
            climatology_scores[position] = empirical_sample_crps(
                sample, realized[position]
            )

        error_key = (
            str(survey_keys[position]),
            str(variable_keys[position]),
            str(horizons[position]),
        )
        sigma_cache_key = (error_key, round_ordinal)
        if sigma_cache_key not in sigma_cache:
            forecast_rounds, completions, group_errors = error_groups[error_key]
            eligible = (forecast_rounds < round_ordinal) & (completions < round_ordinal)
            eligible_errors = group_errors[eligible]
            sigma = (
                float(np.sqrt(np.mean(np.square(eligible_errors))))
                if len(eligible_errors) >= min_history
                else math.nan
            )
            sigma_cache[sigma_cache_key] = (len(eligible_errors), sigma)
        count, sigma = sigma_cache[sigma_cache_key]
        gaussian_counts[position] = count
        if count >= min_history:
            gaussian_scores[position] = gaussian_crps(
                means[position], sigma, realized[position]
            )

    output["n_climatology"] = climatology_counts
    output["n_gaussian"] = gaussian_counts
    output["crps_climatology"] = climatology_scores
    output["crps_gaussian"] = gaussian_scores
    output["skill_vs_climatology"] = _skill_scores(pooled, climatology_scores)
    output["skill_vs_gaussian"] = _skill_scores(pooled, gaussian_scores)
    return output


def _round_ordinals(frame: pd.DataFrame) -> np.ndarray:
    years = pd.to_numeric(frame["year"], errors="coerce").to_numpy(dtype=float)
    quarters = pd.to_numeric(frame["quarter"], errors="coerce").to_numpy(dtype=float)
    valid = (
        np.isfinite(years)
        & np.isfinite(quarters)
        & (years == np.floor(years))
        & (quarters == np.floor(quarters))
        & (quarters >= 1)
        & (quarters <= 4)
    )
    if not valid.all():
        raise ValueError("Forecast years and quarters must be valid integers")
    return years.astype(np.int64) * 4 + quarters.astype(np.int64)


def _completion_ordinals(frame: pd.DataFrame) -> np.ndarray:
    periods = (
        frame["target_period"]
        if "target_period" in frame
        else pd.Series(pd.NA, index=frame.index, dtype="string")
    )
    years = (
        frame["target_year"]
        if "target_year" in frame
        else pd.Series(pd.NA, index=frame.index, dtype="Int64")
    )
    completions: list[int] = []
    for index, period, year in zip(frame.index, periods, years, strict=False):
        try:
            completions.append(period_completion_ordinal(period, target_year=year))
        except ValueError as error:
            raise ValueError(f"Invalid target at row {index}: {error}") from error
    return np.asarray(completions, dtype=np.int64)


def _finite_numeric(series: pd.Series, *, name: str) -> np.ndarray:
    values = pd.to_numeric(series, errors="coerce").to_numpy(dtype=float)
    if not np.isfinite(values).all():
        raise ValueError(f"{name} must be finite on every scored row")
    return values


def _required_strings(series: pd.Series, name: str) -> np.ndarray:
    if series.isna().any():
        raise ValueError(f"{name} cannot be missing on scored rows")
    return series.astype(str).to_numpy(dtype=object)


def _actual_history_groups(
    history: pd.DataFrame,
) -> dict[tuple[str, str, str], tuple[np.ndarray, np.ndarray]]:
    work = history.copy()
    work["_survey_key"] = work["survey"].map(_canonical_survey)
    work["_variable_key"] = [
        _canonical_variable(survey, variable)
        for survey, variable in zip(work["_survey_key"], work["variable"], strict=False)
    ]
    if work["realization_concept"].isna().any():
        raise ValueError("realization_concept cannot be missing in realization history")
    work["_completion"] = _completion_ordinals(work)
    work["_realized"] = _finite_numeric(work["realized"], name="history realized")

    groups: dict[tuple[str, str, str], tuple[np.ndarray, np.ndarray]] = {}
    columns = ["_survey_key", "_variable_key", "realization_concept"]
    for key, group in work.groupby(columns, sort=False, observed=True):
        positions = group.index.to_numpy()
        groups[tuple(str(value) for value in key)] = (
            work.loc[positions, "_completion"].to_numpy(dtype=np.int64),
            work.loc[positions, "_realized"].to_numpy(dtype=float),
        )
    return groups


def _error_history_groups(
    survey_keys: np.ndarray,
    variable_keys: np.ndarray,
    horizons: np.ndarray,
    rounds: np.ndarray,
    completions: np.ndarray,
    errors: np.ndarray,
) -> dict[tuple[str, str, str], tuple[np.ndarray, np.ndarray, np.ndarray]]:
    positions_by_key: dict[tuple[str, str, str], list[int]] = {}
    for position, values in enumerate(zip(survey_keys, variable_keys, horizons)):
        key = tuple(str(value) for value in values)
        positions_by_key.setdefault(key, []).append(position)
    return {
        key: (
            rounds[positions],
            completions[positions],
            errors[positions],
        )
        for key, positions in positions_by_key.items()
    }


def _skill_scores(pooled: np.ndarray, benchmark: np.ndarray) -> np.ndarray:
    output = np.full(len(pooled), np.nan)
    valid = np.isfinite(benchmark) & (benchmark > 0.0)
    output[valid] = 1.0 - pooled[valid] / benchmark[valid]
    return output


__all__ = [
    "BENCHMARK_COLUMNS",
    "MIN_BENCHMARK_OBSERVATIONS",
    "add_benchmark_scores",
    "empirical_sample_crps",
    "gaussian_crps",
    "period_completion_ordinal",
]
