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


def main() -> None:
    frames = {}
    for convention in RECONSTRUCTIONS:
        if convention == RECONSTRUCTION:
            names = ("measures", "growth_tails", "calibration", "scores")
            frames[convention] = {
                f"{name}.csv": pd.read_csv(OUTPUTS / f"{name}.csv") for name in names
            }
            continue
        with tempfile.TemporaryDirectory() as scratch:
            frames[convention] = build_outputs(
                output_dir=scratch, convention=convention
            )
    rows = [
        {"convention": convention, "statistic": statistic, "value": value}
        for convention, outputs in frames.items()
        for statistic, value in headline(outputs).items()
    ]
    table = pd.DataFrame(rows).sort_values(["statistic", "convention"])
    table.to_csv(OUTPUTS / "reconstruction_sensitivity.csv", index=False)
    print(table.pivot(index="statistic", columns="convention", values="value").round(4))


if __name__ == "__main__":
    main()
