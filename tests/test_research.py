import pandas as pd
import pytest

from expectations.research import benchmark_summary, period_comparisons


def test_benchmark_summary_compares_same_rows_and_ratios_of_means():
    frame = pd.DataFrame(
        {
            "survey": ["us"] * 3,
            "variable": ["PRGDP"] * 3,
            "crps_pooled": [0.2, 5.0, 100.0],
            "crps_gaussian": [0.1, 10.0, None],
            "skill_vs_gaussian": [-1.0, 0.5, None],
            "crps_climatology": [0.1, 10.0, None],
            "skill_vs_climatology": [-1.0, 0.5, None],
        }
    )
    row = benchmark_summary(frame).iloc[0]
    assert row.n == 2
    assert row.skill_ratio_of_means == pytest.approx(1 - 5.2 / 10.1)
    assert row.mean_row_skill == pytest.approx(-0.25)


def test_period_comparisons_balance_years_and_separate_round_selection():
    moments = pd.DataFrame(
        [
            {
                "survey": "us",
                "variable": "PRGDP",
                "horizon_class": "next_year",
                "year": year,
                "quarter": quarter,
                **dict.fromkeys(
                    ["mean", "within_sd", "disagreement", "total_sd", "iqr", "q95"],
                    value,
                ),
            }
            for year, quarter, value in [(2025, 1, 2), (2025, 2, 4), (2026, 1, 9)]
        ]
    )
    tails = moments.assign(threshold=5, probability_lower=0.01, probability_upper=0.03)
    result = period_comparisons(moments, tails)
    recent = result[result.window == "2025–26"].set_index("rounds")
    assert recent.loc["Q1", "mean"] == 5.5
    assert recent.loc["all (equal year weight)", "mean"] == 6.0
    assert recent.loc["Q1", "n_round_targets"] == 2
    assert recent.loc["all (equal year weight)", "n_years"] == 2


def test_zero_benchmark_loss_row_is_excluded_from_both_summaries():
    """A benchmark loss of zero leaves row skill undefined, so n must drop it."""
    frame = pd.DataFrame(
        {
            "survey": ["us"] * 3,
            "variable": ["PRGDP"] * 3,
            "crps_pooled": [0.2, 5.0, 1.0],
            "crps_gaussian": [0.1, 10.0, 0.0],
            "skill_vs_gaussian": [-1.0, 0.5, None],
            "crps_climatology": [0.1, 10.0, 0.0],
            "skill_vs_climatology": [-1.0, 0.5, None],
        }
    )
    summary = benchmark_summary(frame)

    for _, row in summary.iterrows():
        assert row.n == 2
        assert row.benchmark_crps == pytest.approx(10.1 / 2)
        assert row.pooled_crps == pytest.approx(5.2 / 2)
        assert row.skill_ratio_of_means == pytest.approx(1 - 5.2 / 10.1)
        assert row.mean_row_skill == pytest.approx(-0.25)
