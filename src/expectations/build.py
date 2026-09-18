"""Build all tidy pipeline outputs from the local survey files."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from expectations.benchmarks import add_benchmark_scores
from expectations.growth import growth_tail_table
from expectations.measures import round_stats
from expectations.realizations import (
    calibration_table,
    load_realizations,
)
from expectations.scores import score_density_calibration

ROOT = Path(__file__).resolve().parents[2]
RAW_DIR = ROOT / "data" / "raw"
OUTPUT_DIR = ROOT / "outputs"

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

MEASURE_COLUMNS = [
    *DENSITY_METADATA,
    "n",
    "mean",
    "median",
    "within_sd",
    "disagreement",
    "total_sd",
    "share_between",
    "q05",
    "q10",
    "q25",
    "q50",
    "q75",
    "q90",
    "q95",
    "iqr",
]


def aggregate_density(
    density: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Aggregate a tidy respondent-by-bin frame into round-target measures."""
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
        "respondent",
    )
    required = {
        *DENSITY_METADATA,
        response_column,
        "bin_index",
        "probability",
        "lower",
        "upper",
        "midpoint",
    }
    missing = sorted(required.difference(data.columns))
    if missing:
        raise ValueError(f"Density frame is missing columns: {missing}")

    measure_rows: list[dict[str, Any]] = []
    coverage_rows: list[dict[str, Any]] = []
    grouped = data.groupby(DENSITY_METADATA, dropna=False, observed=True, sort=True)
    for key, group in grouped:
        metadata = dict(zip(DENSITY_METADATA, key, strict=True))
        bin_rows = (
            group[["bin_index", "lower", "upper", "midpoint"]]
            .drop_duplicates()
            .sort_values("bin_index")
        )
        if bin_rows["bin_index"].duplicated().any():
            raise ValueError(f"Inconsistent bins for density group: {metadata}")
        probabilities = (
            group.set_index([response_column, "bin_index"])["probability"]
            .unstack("bin_index")
            .reindex(columns=bin_rows["bin_index"])
            .to_numpy(dtype=float)
        )
        intervals = [
            (_endpoint(row.lower), _endpoint(row.upper))
            for row in bin_rows.itertuples(index=False)
        ]
        stats = round_stats(
            probabilities,
            bin_rows["midpoint"].to_numpy(dtype=float),
            intervals,
        )
        coverage_rows.append(
            {
                **metadata,
                **{
                    name: stats[name]
                    for name in (
                        "rows_total",
                        "rows_all_nan",
                        "rows_nonempty",
                        "rows_kept",
                        "rows_dropped",
                    )
                },
            }
        )
        if stats["n"] == 0:
            continue
        measure_rows.append(
            {
                **metadata,
                **{name: stats[name] for name in MEASURE_COLUMNS if name in stats},
            }
        )

    measures = pd.DataFrame(measure_rows).reindex(columns=MEASURE_COLUMNS)
    coverage_detail = pd.DataFrame(coverage_rows)
    return _sort_round_targets(measures), coverage_detail


def summarize_density_coverage(details: pd.DataFrame) -> pd.DataFrame:
    """Collapse group-level filter counts to survey-variable coverage."""
    rows: list[dict[str, Any]] = []
    for (survey, variable), group in details.groupby(["survey", "variable"], sort=True):
        active = group[group["rows_nonempty"] > 0]
        rounds = active[["year", "quarter"]].drop_duplicates()
        rows.append(
            {
                "survey": survey,
                "variable": variable,
                "rounds_parsed": len(rounds),
                "first_round": _round_extreme(rounds, "min"),
                "last_round": _round_extreme(rounds, "max"),
                "target_groups": len(active),
                "rows_kept": int(active["rows_kept"].sum()),
                "rows_dropped": int(active["rows_dropped"].sum()),
                "rows_all_nan": int(group["rows_all_nan"].sum()),
                "note": "",
            }
        )
    return pd.DataFrame(rows)


def simple_coverage(
    frame: pd.DataFrame,
    *,
    note: str = "not subject to histogram sum filter",
) -> pd.DataFrame:
    """Coverage rows for point forecasts or recession probabilities."""
    rows: list[dict[str, Any]] = []
    for (survey, variable), group in frame.groupby(["survey", "variable"], sort=True):
        rounds = group[["year", "quarter"]].drop_duplicates()
        rows.append(
            {
                "survey": survey,
                "variable": variable,
                "rounds_parsed": len(rounds),
                "first_round": _round_extreme(rounds, "min"),
                "last_round": _round_extreme(rounds, "max"),
                "target_groups": len(group),
                "rows_kept": int(group["n"].sum()),
                "rows_dropped": 0,
                "rows_all_nan": 0,
                "note": note,
            }
        )
    return pd.DataFrame(rows)


def add_recession_realizations(
    recess: pd.DataFrame, realizations: pd.DataFrame
) -> pd.DataFrame:
    """Attach realized decline indicators and probability forecast scores."""
    actual = realizations[
        (realizations["survey"] == "us_spf") & (realizations["variable"] == "recess")
    ][["target_period", "realized", "source"]]
    output = recess.merge(
        actual, on="target_period", how="left", validate="many_to_one"
    )
    if "concept" in output:
        incompatible = output["concept"] != "chain_weighted_real_gdp"
        output.loc[incompatible, ["realized", "source"]] = [np.nan, pd.NA]
    mean_column = "mean_probability" if "mean_probability" in output else "mean"
    output["error"] = output["realized"] - output[mean_column]
    output["brier_score"] = (
        output["realized"] / 100.0 - output[mean_column] / 100.0
    ) ** 2
    return _sort_round_targets(output)


def build_outputs(
    *,
    raw_dir: str | Path = RAW_DIR,
    output_dir: str | Path = OUTPUT_DIR,
) -> dict[str, pd.DataFrame]:
    """Run the local pipeline, including GDP tail probability bounds."""
    from expectations.ecb_spf import parse_ecb_round
    from expectations.us_spf import (
        DENSITY_VARIABLES,
        parse_longrun_points,
        parse_us_density,
        recess_stats,
    )

    raw = Path(raw_dir)
    destination = Path(output_dir)
    destination.mkdir(parents=True, exist_ok=True)

    us_measure_frames: list[pd.DataFrame] = []
    us_detail_frames: list[pd.DataFrame] = []
    score_density_frames: list[pd.DataFrame] = []
    for variable in DENSITY_VARIABLES:
        variable_density = parse_us_density(variable, data_dir=raw)
        variable_measures, variable_details = aggregate_density(variable_density)
        us_measure_frames.append(variable_measures)
        us_detail_frames.append(variable_details)
        score_density_frames.append(
            variable_density.assign(response_id=variable_density["response_index"])
        )
    us_measures = pd.concat(us_measure_frames, ignore_index=True)
    us_details = pd.concat(us_detail_frames, ignore_index=True)

    ecb_measure_frames: list[pd.DataFrame] = []
    ecb_detail_frames: list[pd.DataFrame] = []
    round_paths = sorted((raw / "ecb_spf").glob("[0-9][0-9][0-9][0-9]Q[1-4].csv"))
    if not round_paths:
        raise FileNotFoundError(f"No ECB SPF rounds found in {raw / 'ecb_spf'}")
    for path in round_paths:
        round_density = parse_ecb_round(path)
        round_measures, round_details = aggregate_density(round_density)
        ecb_measure_frames.append(round_measures)
        ecb_detail_frames.append(round_details)
        score_density_frames.append(
            round_density.assign(response_id=round_density["respondent"])
        )
    ecb_measures = pd.concat(ecb_measure_frames, ignore_index=True)
    ecb_details = pd.concat(ecb_detail_frames, ignore_index=True)

    measures = _sort_round_targets(pd.concat([us_measures, ecb_measures]))
    longrun = _sort_round_targets(parse_longrun_points(data_dir=raw))
    recess = recess_stats(path=raw / "individual_recess.xlsx")
    recess["target_period"] = (
        recess["target_year"].astype(str) + "Q" + recess["target_quarter"].astype(str)
    )
    recess["horizon_quarters"] = recess["horizon_quarter"]
    recess = _sort_round_targets(recess)
    realizations = load_realizations(raw)
    recess = add_recession_realizations(recess, realizations)
    calibration = _sort_round_targets(calibration_table(measures, realizations))
    all_densities = pd.concat(score_density_frames, ignore_index=True)
    distribution_scores = score_density_calibration(calibration, all_densities)
    scores = _sort_round_targets(add_benchmark_scores(distribution_scores, raw_dir=raw))
    growth_tails = _sort_round_targets(growth_tail_table(all_densities))

    coverage = pd.concat(
        [
            summarize_density_coverage(pd.concat([us_details, ecb_details])),
            simple_coverage(longrun),
            simple_coverage(recess),
        ],
        ignore_index=True,
    )
    coverage = coverage.sort_values(["survey", "variable"]).reset_index(drop=True)

    outputs = {
        "measures.csv": measures,
        "longrun_points.csv": longrun,
        "recess.csv": recess,
        "calibration.csv": calibration,
        "scores.csv": scores,
        "coverage.csv": coverage,
        "growth_tails.csv": growth_tails,
    }
    for filename, frame in outputs.items():
        frame.to_csv(destination / filename, index=False)
    return outputs


def _endpoint(value: object) -> float | None:
    return None if pd.isna(value) else float(value)


def _round_extreme(rounds: pd.DataFrame, operation: str) -> object:
    if rounds.empty:
        return pd.NA
    values = [(int(row.year), int(row.quarter)) for row in rounds.itertuples()]
    year, quarter = min(values) if operation == "min" else max(values)
    return f"{year}Q{quarter}"


def _sort_round_targets(frame: pd.DataFrame) -> pd.DataFrame:
    columns = [
        column
        for column in (
            "survey",
            "variable",
            "year",
            "quarter",
            "target_year",
            "target_period",
            "horizon_years",
            "horizon_quarters",
        )
        if column in frame
    ]
    return frame.sort_values(columns, kind="stable", na_position="last").reset_index(
        drop=True
    )


def main() -> None:
    build_outputs()


if __name__ == "__main__":
    main()
