"""High-growth probabilities identified by the edges of the surveys' GDP bins.

Unlike moment and quantile calculations, these bounds never close an open tail.
For a threshold inside a bin, all or none of that bin's probability can exceed
the threshold. Bounds assume continuous growth outcomes: a bin beginning at t
counts entirely toward P(growth > t), while a bin ending at t counts entirely
below it. Point mass exactly on a boundary would require separate elicitation.
"""

from __future__ import annotations

from collections.abc import Iterable
from typing import Any

import numpy as np
import pandas as pd

from expectations.measures import filter_probability_rows

# Bin endpoints and thresholds are percentage growth rates parsed from survey
# labels, so an endpoint this close to a threshold is that endpoint, not a bound
# strictly inside the bin. Comparing them exactly would let representation error
# turn an intended edge into a straddling bin.
EDGE_TOLERANCE = 1e-9

# Kept independent of build.py so that build can import this module.
DENSITY_METADATA = [
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
]

GROWTH_TAIL_COLUMNS = [
    *DENSITY_METADATA,
    "threshold",
    "n",
    "probability_lower",
    "probability_upper",
    "probability_uniform",
    "n_positive_lower",
    "n_positive_upper",
    "share_positive_lower",
    "share_positive_upper",
    "open_tail_threshold",
]


def growth_tail_table(
    density: pd.DataFrame,
    thresholds: Iterable[float] = (3.0, 4.0, 5.0, 10.0),
) -> pd.DataFrame:
    """Pool respondent bounds for P(real GDP growth > threshold), in fractions.

    Selects US ``PRGDP`` densities with concept ``real_gdp`` and ECB ``rgdp``
    densities with concept ``real_gdp_yoy`` (variable names are case insensitive).
    Earlier US nominal-GNP and real-GNP forecasts are excluded. Thresholds and bin
    endpoints are percentage growth rates, so 4 means 4%, while returned
    probabilities and respondent shares are in [0, 1]. Groups and response
    selection follow ``aggregate_density``: partially missing rows fill with
    zero, invalid rows are dropped, retained rows normalize to one, and every
    retained respondent receives equal weight. Groups with no valid responses
    are omitted. Bin schemes remain separate when elicited ranges change.

    ``probability_lower`` sums mass in bins wholly above the threshold;
    ``probability_upper`` also includes mass in bins straddling it. No within-bin
    shape or finite-tail assumption enters those bounds, apart from the
    continuous-boundary convention documented above. Endpoints within
    ``EDGE_TOLERANCE`` of the threshold are compared as that edge, so binary
    representation error cannot turn an intended edge into a straddling bin.
    Bounds use the bin support the density frame carries (``bins.support_intervals``);
    under the literal reading the strips between printed labels receive no mass.

    ``probability_uniform`` interpolates only within finite bins. It is missing
    whenever the threshold lies strictly inside an open tail, even if that bin
    has zero pooled mass. It never uses an invented outer endpoint. The
    ``n_positive_*`` and ``share_positive_*`` columns bound how many respondents
    assign any positive exceedance probability; an upper bound is not a count
    of respondents who actually believe growth will exceed the threshold.
    """
    levels = np.asarray(tuple(thresholds), dtype=float)
    if levels.ndim != 1 or np.any(~np.isfinite(levels)):
        raise ValueError("Growth thresholds must be finite numbers")
    levels = np.unique(levels)
    if "variable" not in density:
        raise ValueError("Density frame is missing columns: ['variable']")
    if density.empty or not levels.size:
        return pd.DataFrame(columns=GROWTH_TAIL_COLUMNS)
    data = density[density["variable"].str.lower().isin(("prgdp", "rgdp"))].copy()
    if data.empty:
        return pd.DataFrame(columns=GROWTH_TAIL_COLUMNS)

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
        "respondent",
    )
    required = {
        *DENSITY_METADATA,
        response_column,
        "bin_index",
        "probability",
        "lower",
        "upper",
    }
    missing = sorted(required.difference(data.columns))
    if missing:
        raise ValueError(f"Density frame is missing columns: {missing}")

    variable = data["variable"].str.lower()
    real_gdp = ((variable == "prgdp") & (data["concept"] == "real_gdp")) | (
        (variable == "rgdp") & (data["concept"] == "real_gdp_yoy")
    )
    data = data[real_gdp]

    rows: list[dict[str, Any]] = []
    grouped = data.groupby(DENSITY_METADATA, dropna=False, observed=True, sort=True)
    for key, group in grouped:
        metadata = dict(zip(DENSITY_METADATA, key, strict=True))
        bins = (
            group[["bin_index", "lower", "upper"]]
            .drop_duplicates()
            .sort_values("bin_index")
        )
        if bins["bin_index"].duplicated().any():
            raise ValueError(f"Inconsistent bins for density group: {metadata}")
        lower, upper = _open_bounds(bins)
        probabilities = (
            group.set_index([response_column, "bin_index"])["probability"]
            .unstack("bin_index")
            .reindex(columns=bins["bin_index"])
            .to_numpy(dtype=float)
        )
        weights, counts = filter_probability_rows(probabilities)
        if not counts["rows_kept"]:
            continue
        n = len(weights)
        for threshold in levels:
            edge_lower = _snap_to_threshold(lower, threshold)
            edge_upper = _snap_to_threshold(upper, threshold)
            above = edge_lower >= threshold
            possibly_above = edge_upper > threshold
            straddles = (edge_lower < threshold) & possibly_above
            open_tail = bool(
                np.any(straddles & (~np.isfinite(lower) | ~np.isfinite(upper)))
            )
            individual_lower = weights[:, above].sum(axis=1)
            individual_upper = weights[:, possibly_above].sum(axis=1)
            uniform = np.nan
            if not open_tail:
                fractions = above.astype(float)
                fractions[straddles] = (edge_upper[straddles] - threshold) / (
                    edge_upper[straddles] - edge_lower[straddles]
                )
                uniform = float(np.mean(weights @ fractions))
            positive_lower = int(np.count_nonzero(individual_lower > 0))
            positive_upper = int(np.count_nonzero(individual_upper > 0))
            rows.append(
                {
                    **metadata,
                    "threshold": float(threshold),
                    "n": n,
                    "probability_lower": float(np.mean(individual_lower)),
                    "probability_upper": float(np.mean(individual_upper)),
                    "probability_uniform": uniform,
                    "n_positive_lower": positive_lower,
                    "n_positive_upper": positive_upper,
                    "share_positive_lower": positive_lower / n,
                    "share_positive_upper": positive_upper / n,
                    "open_tail_threshold": open_tail,
                }
            )
    return pd.DataFrame(rows, columns=GROWTH_TAIL_COLUMNS)


def _snap_to_threshold(endpoints: np.ndarray, threshold: float) -> np.ndarray:
    """Return endpoints with near-threshold values set to the threshold itself.

    Infinite endpoints are never within tolerance, so open tails are untouched.
    """
    return np.where(
        np.abs(endpoints - threshold) <= EDGE_TOLERANCE, threshold, endpoints
    )


def _open_bounds(bins: pd.DataFrame) -> tuple[np.ndarray, np.ndarray]:
    """Validate ranges without filling their gaps or truncating their tails."""
    lower = bins["lower"].to_numpy(dtype=float, na_value=np.nan)
    upper = bins["upper"].to_numpy(dtype=float, na_value=np.nan)
    lower = np.where(np.isnan(lower), -np.inf, lower)
    upper = np.where(np.isnan(upper), np.inf, upper)
    if np.any(lower >= upper) or np.any(np.isneginf(lower) & np.isposinf(upper)):
        raise ValueError("Density bins need increasing, at least one finite endpoint")
    order = np.argsort(lower, kind="stable")
    if np.any(upper[order][:-1] > lower[order][1:]):
        raise ValueError("Density bins must not overlap")
    return lower, upper
