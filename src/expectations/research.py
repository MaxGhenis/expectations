"""Reproducible summaries for the growth-beliefs research question.

The main comparison fixes the survey quarter at Q1. All-round sensitivities
first average within survey year, so an incomplete latest year has the same
weight as each preceding year. These are descriptive comparisons, not tests
of an AI treatment effect or of equivalence between periods.
"""

from __future__ import annotations

import pandas as pd

WINDOWS = {
    "2006–09": (2006, 2009),
    "2010–14": (2010, 2014),
    "2015–19": (2015, 2019),
    "2020–24": (2020, 2024),
    "2025–26": (2025, 2026),
    "2010–19": (2010, 2019),
    "2023–26": (2023, 2026),
}
GROWTH_SERIES = {
    "US next year": ("us", "PRGDP", "next_year"),
    "US three years ahead": ("us", "PRGDP", "three_years_ahead"),
    "ECB longer term": ("ecb", "rgdp", "longer_term"),
}


def select_series(frame: pd.DataFrame, name: str, *, q1: bool = True):
    survey, variable, horizon = GROWTH_SERIES[name]
    selected = frame[
        (frame.survey == survey)
        & (frame.variable == variable)
        & (frame.horizon_class == horizon)
        & (frame.year >= 2006)
    ]
    if q1:
        selected = selected[selected.quarter == 1]
    return selected.copy()


def period_comparisons(measures: pd.DataFrame, tails: pd.DataFrame) -> pd.DataFrame:
    """Compare levels, spreads and separately identified upper-tail bounds."""
    rows = []
    moment_fields = ["mean", "within_sd", "disagreement", "total_sd", "iqr", "q95"]
    tail_fields = ["probability_lower", "probability_upper"]
    for q1 in (True, False):
        for name in GROWTH_SERIES:
            selected = select_series(measures, name, q1=q1)
            selected_tails = select_series(tails, name, q1=q1)
            for window, (start, end) in WINDOWS.items():
                subset = selected[selected.year.between(start, end)]
                if subset.empty:
                    continue
                annual = subset.groupby("year")[moment_fields].mean()
                base = {
                    "series": name,
                    "rounds": "Q1" if q1 else "all (equal year weight)",
                    "window": window,
                    "n_years": len(annual),
                    "n_round_targets": len(subset),
                    **annual.mean().to_dict(),
                }
                for threshold, group in selected_tails[
                    selected_tails.year.between(start, end)
                ].groupby("threshold"):
                    annual_tails = group.groupby("year")[tail_fields].mean()
                    if set(annual_tails.index) != set(annual.index):
                        raise ValueError("Tail and moment comparison years differ")
                    rows.append(
                        {
                            **base,
                            "threshold": threshold,
                            **annual_tails.mean().to_dict(),
                        }
                    )
    return pd.DataFrame(rows)


def benchmark_summary(scores: pd.DataFrame) -> pd.DataFrame:
    """Ratio of mean CRPS on matched rows; retain mean row skill as sensitivity.

    Both statistics describe the same rows: those with a pooled score and a
    strictly positive benchmark score. Row-level skill is undefined against a
    benchmark loss of zero, so admitting such a row would leave ``n`` counting
    an observation that ``mean_row_skill`` silently dropped.
    """
    rows = []
    for (survey, variable), group in scores.groupby(["survey", "variable"]):
        for benchmark in ("climatology", "gaussian"):
            column = f"crps_{benchmark}"
            eligible = group.dropna(subset=["crps_pooled", column])
            eligible = eligible[eligible[column] > 0]
            reference = eligible[column].mean()
            pooled = eligible.crps_pooled.mean()
            rows.append(
                {
                    "survey": survey,
                    "variable": variable,
                    "benchmark": benchmark,
                    "n": len(eligible),
                    "pooled_crps": pooled,
                    "benchmark_crps": reference,
                    "skill_ratio_of_means": (
                        1 - pooled / reference if reference > 0 else float("nan")
                    ),
                    "mean_row_skill": eligible[f"skill_vs_{benchmark}"].mean(),
                }
            )
    return pd.DataFrame(rows)
