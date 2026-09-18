import math
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from expectations.benchmarks import (
    add_benchmark_scores,
    empirical_sample_crps,
    gaussian_crps,
    period_completion_ordinal,
)
from expectations.realizations import (
    load_realization_history,
    load_us_realizations,
)

ROOT = Path(__file__).resolve().parents[1]


def test_empirical_sample_crps_matches_pairwise_definition():
    sample = np.array([-2.0, -0.5, 1.0, 1.0, 4.5])
    realized = 0.75
    pairwise = np.abs(sample[:, None] - sample[None, :])
    expected = np.mean(np.abs(sample - realized)) - 0.5 * np.mean(pairwise)

    assert empirical_sample_crps(sample, realized) == pytest.approx(expected)
    assert empirical_sample_crps([2.0], -1.0) == pytest.approx(3.0)


def test_gaussian_crps_known_cases():
    expected_at_mean = (math.sqrt(2.0) - 1.0) / math.sqrt(math.pi)
    assert gaussian_crps(0.0, 1.0, 0.0) == pytest.approx(expected_at_mean)
    assert gaussian_crps(2.0, 0.0, -1.0) == pytest.approx(3.0)
    with pytest.raises(ValueError, match="cannot be negative"):
        gaussian_crps(0.0, -1.0, 0.0)


def test_period_completion_quarter_convention():
    assert period_completion_ordinal("2001") == 4 * 2001 + 4
    assert period_completion_ordinal("2001Q2") == 4 * 2001 + 2
    assert period_completion_ordinal("2001Feb") == 4 * 2001 + 1
    assert period_completion_ordinal("2001-09") == 4 * 2001 + 3
    assert period_completion_ordinal(pd.NA, target_year=2001.0) == 4 * 2001 + 4
    with pytest.raises(ValueError, match="Unsupported target period"):
        period_completion_ordinal("2001-W01")
    with pytest.raises(ValueError, match="required"):
        period_completion_ordinal(pd.NA)


def test_full_history_loader_preserves_calibration_loader_and_extends_history():
    calibration = load_us_realizations()
    calibration_counts = calibration.groupby("variable").size().to_dict()
    assert calibration_counts == {
        "prccpi": 18,
        "prcpce": 19,
        "prgdp": 34,
        "prpgdp": 34,
        "prunemp": 16,
        "recess": 138,
    }

    history = load_realization_history()
    expected = {
        ("us_spf", "prgdp", "annual_average_real_gdp_growth"): (96, 1930, 2025),
        (
            "us_spf",
            "prpgdp",
            "annual_average_gdp_price_index_growth",
        ): (96, 1930, 2025),
        (
            "us_spf",
            "prunemp",
            "annual_average_civilian_unemployment_rate",
        ): (77, 1948, 2024),
        (
            "us_spf",
            "prccpi",
            "q4_over_q4_core_cpi_inflation",
        ): (67, 1958, 2024),
        (
            "us_spf",
            "prcpce",
            "q4_over_q4_core_pce_inflation",
        ): (66, 1960, 2025),
    }
    for key, (count, first_year, last_year) in expected.items():
        survey, variable, concept = key
        group = history[
            (history["survey"] == survey)
            & (history["variable"] == variable)
            & (history["realization_concept"] == concept)
        ]
        years = group["target_year"].astype(int)
        assert (len(group), years.min(), years.max()) == (
            count,
            first_year,
            last_year,
        )


def _scored_row(
    *,
    label: str,
    year: int,
    quarter: int,
    target_year: int,
    error: float,
    horizon: str = "next_year",
    concept: str = "annual_concept",
    realized: float = 5.0,
    mean: float = 4.0,
) -> dict[str, object]:
    return {
        "label": label,
        "survey": "us",
        "variable": "PRGDP",
        "year": year,
        "quarter": quarter,
        "target_year": target_year,
        "target_period": pd.NA,
        "horizon_class": horizon,
        "realization_concept": concept,
        "realized": realized,
        "consensus_mean": mean,
        "error": error,
        "crps_pooled": 0.5,
    }


def test_benchmarks_use_strict_completed_periods_and_minimum_windows():
    rows = [
        _scored_row(
            label=f"mature_{index}",
            year=1980 + index,
            quarter=1,
            target_year=1981 + index,
            error=float(index + 1),
            concept="point_concept" if index == 0 else "annual_concept",
        )
        for index in range(10)
    ]
    rows.extend(
        [
            _scored_row(
                label="unrealized_prior",
                year=1990,
                quarter=3,
                target_year=2005,
                error=1_000.0,
            ),
            _scored_row(
                label="other_horizon",
                year=1980,
                quarter=1,
                target_year=1981,
                error=1_000.0,
                horizon="current_year",
            ),
            _scored_row(
                label="probe_nine",
                year=1990,
                quarter=4,
                target_year=2000,
                error=1.0,
            ),
            _scored_row(
                label="probe_ten",
                year=1991,
                quarter=1,
                target_year=2001,
                error=1.0,
            ),
        ]
    )
    scored = pd.DataFrame(rows).sample(frac=1.0, random_state=42).set_index("label")

    history_rows = [
        {
            "survey": "us_spf",
            "variable": "prgdp",
            "target_year": year,
            "target_period": str(year),
            "realized": float(year - 1981),
            "realization_concept": "annual_concept",
        }
        for year in range(1981, 1992)
    ]
    history_rows.extend(
        {
            "survey": "us_spf",
            "variable": "prgdp",
            "target_year": year,
            "target_period": str(year),
            "realized": 10_000.0,
            "realization_concept": "wrong_concept",
        }
        for year in range(1960, 1981)
    )
    history = pd.DataFrame(history_rows)

    result = add_benchmark_scores(scored, history)
    nine = result.loc["probe_nine"]
    ten = result.loc["probe_ten"]

    assert (nine["n_climatology"], nine["n_gaussian"]) == (9, 9)
    assert pd.isna(nine["crps_climatology"])
    assert pd.isna(nine["crps_gaussian"])

    expected_sample = np.arange(10, dtype=float)
    expected_sigma = math.sqrt(np.mean(np.square(np.arange(1.0, 11.0))))
    assert (ten["n_climatology"], ten["n_gaussian"]) == (10, 10)
    assert ten["crps_climatology"] == pytest.approx(
        empirical_sample_crps(expected_sample, 5.0)
    )
    assert ten["crps_gaussian"] == pytest.approx(
        gaussian_crps(4.0, expected_sigma, 5.0)
    )
    assert ten["skill_vs_climatology"] == pytest.approx(
        1.0 - 0.5 / ten["crps_climatology"]
    )

    future = pd.concat(
        [
            history,
            pd.DataFrame(
                [
                    {
                        "survey": "us_spf",
                        "variable": "prgdp",
                        "target_year": 2099,
                        "target_period": "2099",
                        "realized": 1_000_000.0,
                        "realization_concept": "annual_concept",
                    }
                ]
            ),
        ],
        ignore_index=True,
    )
    with_future = add_benchmark_scores(scored.iloc[::-1], future).sort_index()
    original = result.sort_index()
    pd.testing.assert_frame_equal(
        original[list(result.columns)],
        with_future[list(result.columns)],
    )


def test_local_benchmark_availability_regressions():
    calibration = pd.read_csv(ROOT / "outputs" / "calibration.csv")
    calibration["crps_pooled"] = 1.0
    scored = add_benchmark_scores(calibration)

    assert len(scored) == len(calibration) == 3070
    us = scored[scored["survey"] == "us"]
    assert us["crps_climatology"].notna().all()

    first_us_gdp = scored[
        (scored["survey"] == "us")
        & (scored["variable"] == "PRGDP")
        & (scored["year"] == 1992)
        & (scored["quarter"] == 1)
        & (scored["horizon_class"] == "current_year")
    ].iloc[0]
    assert first_us_gdp["n_climatology"] == 62

    hicp_current = scored[
        (scored["survey"] == "ecb")
        & (scored["variable"] == "hicp")
        & (scored["horizon_class"] == "current_year")
    ]
    assert (
        hicp_current.loc[hicp_current["year"] < 2007, "crps_climatology"].isna().all()
    )
    hicp_2007q1 = hicp_current[
        (hicp_current["year"] == 2007) & (hicp_current["quarter"] == 1)
    ].iloc[0]
    assert hicp_2007q1["n_climatology"] == 10
    assert pd.notna(hicp_2007q1["crps_climatology"])

    first_hicp_rolling = scored[
        (scored["survey"] == "ecb")
        & (scored["variable"] == "hicp")
        & (scored["year"] == 1999)
        & (scored["quarter"] == 1)
        & (scored["horizon_class"] == "rolling_1y")
    ].iloc[0]
    assert first_hicp_rolling["n_climatology"] == 24
    assert pd.notna(first_hicp_rolling["crps_climatology"])

    hicpx_long = scored[
        (scored["survey"] == "ecb")
        & (scored["variable"] == "hicpx")
        & (scored["horizon_class"] == "longer_term")
    ]
    assert not hicpx_long.empty
    assert (hicpx_long["n_gaussian"] == 0).all()
    assert hicpx_long["crps_gaussian"].isna().all()
