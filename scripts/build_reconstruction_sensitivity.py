"""Record what the bin-reconstruction choice moves.

The published outputs read each printed bin label as contiguous support
("2.0 to 2.9" covers [2, 3)). This script runs the whole pipeline under the two
alternatives as well — the printed labels taken literally, and boundaries halfway
across each strip between labels — and writes the headline statistics under all
three to ``outputs/reconstruction_sensitivity.csv``.
"""

from __future__ import annotations

import tempfile
from pathlib import Path

import pandas as pd

from expectations.bins import RECONSTRUCTION, RECONSTRUCTIONS
from expectations.build import build_outputs

ROOT = Path(__file__).resolve().parents[1]
OUTPUTS = ROOT / "outputs"
WINDOWS = {"2015_19": range(2015, 2020), "2025_26": (2025, 2026)}
HORIZONS = ("current_year", "next_year", "year_after_next", "three_years_ahead")
GROUP_KEYS = [
    "survey",
    "variable",
    "year",
    "quarter",
    "horizon_class",
    "target_year",
    "target_period",
]


def _q1(frame: pd.DataFrame, survey: str, variable: str, horizon: str) -> pd.DataFrame:
    return frame[
        (frame.survey == survey)
        & (frame.variable == variable)
        & (frame.quarter == 1)
        & (frame.horizon_class == horizon)
    ]


def headline(outputs: dict[str, pd.DataFrame]) -> dict[str, float]:
    measures, tails = outputs["measures.csv"], outputs["growth_tails.csv"]
    calibration, scores = outputs["calibration.csv"], outputs["scores.csv"]
    tails = tails[tails.threshold == 4.0]
    stats: dict[str, float] = {}
    for label, survey, variable, horizon in (
        ("us_next_year", "us", "PRGDP", "next_year"),
        ("ecb_longer_term", "ecb", "rgdp", "longer_term"),
    ):
        for window, years in WINDOWS.items():
            rounds = _q1(measures, survey, variable, horizon)
            rounds = rounds[rounds.year.isin(years)]
            stats[f"{label}_mean_{window}"] = rounds["mean"].mean()
            stats[f"{label}_total_sd_{window}"] = rounds["total_sd"].mean()
            above = _q1(tails, survey, variable, horizon)
            above = above[above.year.isin(years)]
            # Where 4.0 is a bin edge the two bounds coincide; the midpoint reading
            # moves that edge to 3.95, so only a range is identified there.
            stats[f"{label}_p_above_4_{window}"] = above["probability_lower"].mean()
            stats[f"{label}_p_above_4_upper_{window}"] = above[
                "probability_upper"
            ].mean()
    for survey, variable in (("us", "PRGDP"), ("ecb", "rgdp")):
        latest = _q1(measures, survey, variable, "next_year")
        stats[f"{survey}_next_year_total_sd_2026q1"] = latest[latest.year == 2026][
            "total_sd"
        ].iloc[0]
        scored = _q1(scores, survey, variable, "next_year")
        stats[f"{survey}_q1_next_year_mean_crps"] = scored["crps_pooled"].mean()
    covered = _q1(calibration, "us", "PRGDP", "next_year")
    stats["us_q1_next_year_targets"] = len(covered)
    stats["us_q1_next_year_inside_1sd"] = int(covered["inside_1sd"].sum())
    stats["us_q1_next_year_inside_pooled_90"] = int(covered["inside_pooled_90"].sum())
    recent = measures[
        (measures.survey == "us")
        & (measures.variable == "PRGDP")
        & (measures.quarter == 1)
        & (measures.year >= 2010)
    ]
    for offset, horizon in enumerate(HORIZONS):
        stats[f"us_q1_total_sd_2010_26_year_plus_{offset}"] = recent[
            recent.horizon_class == horizon
        ]["total_sd"].mean()
    real = measures[(measures.variable == "PRGDP") & (measures.concept == "real_gdp")]
    stats["us_real_gdp_median_between_share"] = real["share_between"].median()
    return stats


def all_groups(primary: pd.DataFrame, alternative: pd.DataFrame) -> dict[str, float]:
    """How far every round-target's mean and SD move, primary minus alternative.

    The headline windows are not the whole panel: a distribution with mass in an
    open tail moves with that tail's closure width, not with the bin midpoints.
    """
    keyed = [
        frame.assign(
            **{key: frame[key].astype("string").fillna("") for key in GROUP_KEYS}
        )
        for frame in (primary, alternative)
    ]
    merged = keyed[0].merge(
        keyed[1], on=GROUP_KEYS, suffixes=("", "_alt"), validate="1:1"
    )
    if len(merged) != len(primary):
        raise ValueError("Every round-target must match across reconstructions")
    shift = merged["mean"] - merged["mean_alt"]
    ratio = merged["total_sd"] / merged["total_sd_alt"] - 1
    worst = merged.loc[ratio.idxmax()]
    print(
        f"largest SD move: {worst.survey} {worst.variable} {worst.year}Q{worst.quarter} "
        f"{worst.horizon_class} ({ratio.max():+.1%}, mean shift {shift[ratio.idxmax()]:+.3f})"
    )
    return {
        "all_groups_n": len(merged),
        "all_groups_mean_shift_median": shift.median(),
        "all_groups_mean_shift_p05": shift.quantile(0.05),
        "all_groups_mean_shift_p95": shift.quantile(0.95),
        "all_groups_mean_shift_min": shift.min(),
        "all_groups_mean_shift_max": shift.max(),
        "all_groups_share_mean_lower_under_primary": (shift < 0).mean(),
        "all_groups_sd_ratio_median": ratio.median(),
        "all_groups_sd_ratio_p95": ratio.quantile(0.95),
        "all_groups_sd_ratio_max": ratio.max(),
        "all_groups_share_sd_ratio_above_1pct": (ratio.abs() > 0.01).mean(),
    }


def main() -> None:
    names = ("measures", "growth_tails", "calibration", "scores")
    frames = {}
    for convention in RECONSTRUCTIONS:
        # Every reading is read back from CSV, so keys and dtypes compare like for like.
        if convention == RECONSTRUCTION:
            frames[convention] = {
                f"{name}.csv": pd.read_csv(OUTPUTS / f"{name}.csv") for name in names
            }
            continue
        with tempfile.TemporaryDirectory() as scratch:
            build_outputs(output_dir=scratch, convention=convention)
            frames[convention] = {
                f"{name}.csv": pd.read_csv(Path(scratch) / f"{name}.csv")
                for name in names
            }
    rows = [
        {"convention": convention, "statistic": statistic, "value": value}
        for convention, outputs in frames.items()
        for statistic, value in headline(outputs).items()
    ]
    primary = frames[RECONSTRUCTION]["measures.csv"]
    for convention, outputs in frames.items():
        if convention == RECONSTRUCTION:
            continue
        rows += [
            {"convention": convention, "statistic": statistic, "value": value}
            for statistic, value in all_groups(primary, outputs["measures.csv"]).items()
        ]
    table = pd.DataFrame(rows).sort_values(["statistic", "convention"])
    table.to_csv(OUTPUTS / "reconstruction_sensitivity.csv", index=False)
    print(table.pivot(index="statistic", columns="convention", values="value").round(4))


if __name__ == "__main__":
    main()
