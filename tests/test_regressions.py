from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from forecast_uncertainty.build import add_recession_realizations, aggregate_density
from forecast_uncertainty.ecb_spf import parse_ecb_round
from forecast_uncertainty.measures import finite_intervals
from forecast_uncertainty.realizations import (
    calibration_table,
    load_ecb_realizations,
    load_us_realizations,
)
from forecast_uncertainty.us_spf import LONGRUN_VARIABLES, parse_us_density

ROOT = Path(__file__).resolve().parents[1]
SEED = ROOT / "tests" / "fixtures" / "seed"


@pytest.fixture(scope="module")
def prgdp_density():
    return parse_us_density("PRGDP")


@pytest.fixture(scope="module")
def prgdp_measures(prgdp_density):
    measures, _ = aggregate_density(prgdp_density)
    return measures


@pytest.fixture(scope="module")
def q1_next_year_reference_moments(prgdp_density):
    """Retain the historical midpoint calculation without changing its fixtures.

    Also integrate the pooled uniform histogram directly, independently of
    round_stats, for checking the corrected production moments and coverage.
    """
    density = prgdp_density[
        (prgdp_density["quarter"] == 1)
        & (prgdp_density["horizon_class"] == "next_year")
    ]
    records = []
    for year, group in density.groupby("year"):
        bins = (
            group[["bin_index", "midpoint", "lower", "upper"]]
            .drop_duplicates()
            .sort_values("bin_index")
        )
        probabilities = group.pivot(
            index="response_index", columns="bin_index", values="probability"
        ).to_numpy()
        probabilities = probabilities[~np.isnan(probabilities).all(axis=1)]
        probabilities = np.nan_to_num(probabilities)
        probabilities = probabilities[np.abs(probabilities.sum(axis=1) - 100.0) < 2.0]
        weights = probabilities / probabilities.sum(axis=1, keepdims=True)
        midpoints = bins["midpoint"].to_numpy()
        individual_means = weights @ midpoints
        legacy_within = np.mean(weights @ midpoints**2 - individual_means**2)
        legacy_between = individual_means.var(ddof=1)
        intervals = [
            (None if pd.isna(lower) else lower, None if pd.isna(upper) else upper)
            for lower, upper in bins[["lower", "upper"]].itertuples(
                index=False, name=None
            )
        ]
        bounds = finite_intervals(intervals)
        lower, upper = bounds.T
        pooled = weights.mean(axis=0)
        uniform_mean = pooled @ ((lower + upper) / 2.0)
        uniform_second = pooled @ ((lower**2 + lower * upper + upper**2) / 3.0)
        records.append(
            {
                "year": year,
                "n": len(weights),
                "within_sd": np.sqrt(legacy_within),
                "disagreement": np.sqrt(legacy_between),
                "total_sd": np.sqrt(legacy_within + legacy_between),
                "share_between": legacy_between / (legacy_within + legacy_between),
                "uniform_mean": uniform_mean,
                "uniform_total_sd": np.sqrt(uniform_second - uniform_mean**2),
            }
        )
    return pd.DataFrame(records).set_index("year")


def test_legacy_next_year_q1_prgdp_reconstruction_matches_seed(
    q1_next_year_reference_moments,
):
    expected = pd.read_csv(SEED / "spf_uncertainty_disagreement.csv")
    aligned = q1_next_year_reference_moments.loc[expected["YEAR"]]

    np.testing.assert_array_equal(aligned["n"], expected["n"])
    for actual_column, expected_column in (
        ("within_sd", "within_sd"),
        ("disagreement", "dis"),
        ("total_sd", "total"),
        ("share_between", "share_between"),
    ):
        np.testing.assert_allclose(
            aligned[actual_column], expected[expected_column], rtol=0, atol=1e-9
        )


def test_next_year_q1_prgdp_matches_integrated_uniform_mixture(
    prgdp_measures, q1_next_year_reference_moments
):
    actual = prgdp_measures[
        (prgdp_measures["quarter"] == 1)
        & (prgdp_measures["horizon_class"] == "next_year")
    ].set_index("year")
    expected = q1_next_year_reference_moments.loc[actual.index]

    np.testing.assert_array_equal(actual["n"], expected["n"])
    np.testing.assert_allclose(
        actual["mean"], expected["uniform_mean"], rtol=0, atol=1e-12
    )
    np.testing.assert_allclose(
        actual["total_sd"], expected["uniform_total_sd"], rtol=0, atol=1e-12
    )
    np.testing.assert_allclose(
        actual["disagreement"] ** 2,
        expected["disagreement"] ** 2 * (expected["n"] - 1) / expected["n"],
        rtol=0,
        atol=1e-12,
    )
    assert (actual["within_sd"] > expected["within_sd"]).all()


def test_next_year_q1_prgdp_calibration_preserves_seed_errors(
    prgdp_measures, q1_next_year_reference_moments
):
    expected = pd.read_csv(SEED / "spf_errors.csv")
    calibration = calibration_table(prgdp_measures, load_us_realizations())
    actual = calibration[
        (calibration["quarter"] == 1) & (calibration["horizon_class"] == "next_year")
    ].set_index(["year", "target_year"])
    assert len(actual) == len(expected)
    keys = pd.MultiIndex.from_frame(expected[["YEAR", "target"]])
    aligned = actual.loc[keys]

    np.testing.assert_allclose(aligned["realized"], expected["g"], rtol=0, atol=1e-12)
    np.testing.assert_allclose(aligned["error"], expected["err"], rtol=0, atol=1e-12)
    moments = q1_next_year_reference_moments.loc[expected["YEAR"]]
    legacy_inside = np.abs(expected["err"].to_numpy()) <= moments["total_sd"].to_numpy()
    assert legacy_inside.tolist() == expected["inside"].tolist()
    uniform_inside = (
        np.abs(aligned["error"].to_numpy()) <= moments["uniform_total_sd"].to_numpy()
    )
    assert aligned["inside_1sd"].astype(bool).tolist() == uniform_inside.tolist()


def test_documented_round_coverage_and_core_starts():
    ecb_paths = sorted((ROOT / "data" / "raw" / "ecb_spf").glob("*.csv"))
    assert len(ecb_paths) == 111
    assert ecb_paths[0].stem == "1999Q1"
    assert ecb_paths[-1].stem == "2026Q3"

    prccpi = parse_us_density("PRCCPI")
    rounds = prccpi[["year", "quarter"]].drop_duplicates()
    assert len(rounds) == 79
    assert tuple(rounds.iloc[0]) == (2007, 1)
    assert tuple(rounds.iloc[-1]) == (2026, 3)

    point_only = parse_ecb_round(ROOT / "data" / "raw" / "ecb_spf" / "2016Q4.csv")
    core_point_only = point_only[point_only["variable"] == "hicpx"]
    assert not core_point_only.empty
    assert core_point_only["probability"].isna().all()

    first_density = parse_ecb_round(ROOT / "data" / "raw" / "ecb_spf" / "2017Q1.csv")
    assert (
        first_density.loc[first_density["variable"] == "hicpx", "probability"]
        .notna()
        .any()
    )


def test_hicpx_realizations_support_calendar_and_rolling_calibration():
    realizations = load_ecb_realizations()
    core = realizations[realizations["variable"] == "hicpx"].set_index("target_period")

    assert len(core) == 377
    assert core.loc["2024Dec", "realized"] == pytest.approx(2.7)
    assert core.loc["2024Dec", "observation_status"] == "A"
    assert core.loc["2025", "realized"] == pytest.approx(2.4)
    assert core.loc["2025", "observation_status"] == "A"

    forecasts = pd.DataFrame(
        [
            {
                "survey": "ecb",
                "variable": "hicpx",
                "target_period": target,
                "mean": 2.5,
                "total_sd": 1.0,
                "q05": 1.0,
                "q95": 4.0,
            }
            for target in ("2024Dec", "2025")
        ]
    )
    calibration = calibration_table(forecasts, realizations)

    assert calibration["target_period"].tolist() == ["2024Dec", "2025"]
    estimated = calibration["observation_status"].str.contains("E", na=False)
    assert estimated.tolist() == [False, False]


def test_generated_hicpx_calibration_coverage():
    """Stored calibration must agree with filtered, reconstructed source data.

    Historical counts used midpoint dispersion and retained one negative source
    probability; they are not golden values for the corrected distribution.
    """
    frames = []
    for path in sorted((ROOT / "data" / "raw" / "ecb_spf").glob("*.csv")):
        density = parse_ecb_round(path)
        core_density = density[density["variable"] == "hicpx"]
        if not core_density.empty:
            frames.append(core_density)
    measures, _ = aggregate_density(pd.concat(frames, ignore_index=True))
    reconstructed = calibration_table(measures, load_ecb_realizations())

    calibration = pd.read_csv(ROOT / "outputs" / "calibration.csv")
    core = calibration[
        (calibration["survey"] == "ecb") & (calibration["variable"] == "hicpx")
    ]
    keys = ["year", "quarter", "target_period"]
    columns = [
        "n",
        "total_sd",
        "q05",
        "q95",
        "realized",
        "inside_1sd",
        "inside_pooled_90",
        "observation_status",
    ]
    assert not core.empty
    pd.testing.assert_frame_equal(
        core.set_index(keys)[columns].sort_index(),
        reconstructed.set_index(keys)[columns].sort_index(),
        check_dtype=False,
        rtol=0.0,
        atol=1e-12,
    )


@pytest.mark.parametrize("variable, respondent", [("hicpx", "115"), ("rgdp", "107")])
def test_ecb_negative_source_cells_drop_their_response(variable, respondent):
    density = parse_ecb_round(ROOT / "data" / "raw" / "ecb_spf" / "2023Q1.csv")
    negative = density[(density["variable"] == variable) & (density["probability"] < 0)]
    assert len(negative) == 1
    assert negative.iloc[0]["respondent"] == respondent
    group = density[
        (density["variable"] == variable)
        & (density["target_period"] == negative.iloc[0]["target_period"])
    ]
    probabilities = group.pivot(
        index="respondent", columns="bin_index", values="probability"
    ).fillna(0.0)
    legacy_retained = (probabilities.sum(axis=1) - 100.0).abs() < 2.0
    assert legacy_retained.loc[respondent]

    measures, coverage = aggregate_density(group)

    assert measures.iloc[0]["n"] == int(legacy_retained.sum()) - 1
    assert coverage.iloc[0]["rows_dropped"] >= 1


def test_generated_scores_match_calibration_and_flag_benchmark_windows():
    calibration = pd.read_csv(ROOT / "outputs" / "calibration.csv")
    scores = pd.read_csv(ROOT / "outputs" / "scores.csv")

    assert len(scores) == len(calibration) == 3070
    assert scores.columns[: len(calibration.columns)].tolist() == list(
        calibration.columns
    )
    pd.testing.assert_frame_equal(
        scores[list(calibration.columns)], calibration, check_dtype=False
    )

    distribution_columns = [
        "crps_pooled",
        "crps_individual_mean",
        "pinball_05",
        "pinball_10",
        "pinball_25",
        "pinball_50",
        "pinball_75",
        "pinball_90",
        "pinball_95",
        "pit",
    ]
    assert scores[distribution_columns].notna().all().all()
    assert scores[distribution_columns[:-1]].ge(0.0).all().all()
    assert scores["pit"].between(0.0, 1.0).all()
    assert (scores["crps_pooled"] <= scores["crps_individual_mean"] + 1e-10).all()

    for name in ("climatology", "gaussian"):
        benchmark = scores[f"crps_{name}"]
        eligible = scores[f"n_{name}"] >= 10
        assert benchmark.notna().equals(eligible)
        expected_skill = 1.0 - scores["crps_pooled"] / benchmark
        np.testing.assert_allclose(
            scores.loc[eligible, f"skill_vs_{name}"],
            expected_skill.loc[eligible],
            rtol=0.0,
            atol=1e-12,
        )
        assert scores.loc[~eligible, f"skill_vs_{name}"].isna().all()


def test_documented_longrun_point_configuration():
    assert LONGRUN_VARIABLES == ("RGDP10", "CPI10", "PCE10")


def test_calibration_excludes_us_gnp_concepts():
    forecasts = pd.DataFrame(
        [
            {
                "survey": "us",
                "variable": "PRGDP",
                "concept": concept,
                "target_year": 1992,
                "mean": 2.0,
                "total_sd": 1.0,
                "q05": 0.0,
                "q95": 4.0,
            }
            for concept in ("nominal_gnp", "real_gnp", "real_gdp")
        ]
        + [
            {
                "survey": "us",
                "variable": "PRPGDP",
                "concept": concept,
                "target_year": 1992,
                "mean": 2.0,
                "total_sd": 1.0,
                "q05": 0.0,
                "q95": 4.0,
            }
            for concept in ("gnp_implicit_deflator", "gdp_implicit_deflator")
        ]
    )
    realizations = pd.DataFrame(
        [
            {
                "survey": "us_spf",
                "variable": variable,
                "target_period": "1992",
                "realized": 2.5,
            }
            for variable in ("prgdp", "prpgdp")
        ]
    )

    calibration = calibration_table(forecasts, realizations)

    assert calibration[["variable", "concept"]].to_records(index=False).tolist() == [
        ("PRGDP", "real_gdp"),
        ("PRPGDP", "gdp_implicit_deflator"),
    ]


def test_recession_realizations_require_chain_weighted_gdp_concept():
    forecasts = pd.DataFrame(
        [
            {
                "survey": "us",
                "variable": "RECESS",
                "concept": concept,
                "year": 1996,
                "quarter": 1,
                "target_period": "1996Q1",
                "mean_probability": 25.0,
            }
            for concept in ("fixed_weighted_real_gdp", "chain_weighted_real_gdp")
        ]
    )
    realizations = pd.DataFrame(
        [
            {
                "survey": "us_spf",
                "variable": "recess",
                "target_period": "1996Q1",
                "realized": 0.0,
                "source": "test",
            }
        ]
    )

    scored = add_recession_realizations(forecasts, realizations)

    assert scored.loc[0, ["realized", "source"]].isna().all()
    assert scored.loc[1, "realized"] == 0.0
    assert scored.loc[1, "source"] == "test"
