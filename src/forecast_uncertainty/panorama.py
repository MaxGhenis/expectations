"""Panorama summaries: the whole-survey tables behind the main manuscript.

Every function is a pure transformation of the pipeline's own
``outputs/*.csv`` frames, so each manuscript number has one definition that
lives in code rather than in prose. The conventions follow the pipeline
reports:

* US headline series are Q1 rounds at the next-calendar-year horizon; ECB
  headline series are annual means of the quarterly rolling-one-year rows.
* US real-GDP and GDP-price summaries use the 1992 onward real-GDP sample,
  excluding the nominal- and real-GNP eras.
* Term-structure comparisons are balanced: US windows keep only Q1 rounds
  carrying every horizon in the window, and ECB rows keep only rounds
  carrying all three modern horizon classes after duplicate early
  longer-term targets are averaged within the round.
* CRPS skill is one minus the ratio of mean losses on matched eligible rows
  (``benchmark_summary.csv``); row-level mean skill travels beside it as a
  sensitivity.
* Cluster windows classify a row by the event year parsed from
  ``target_period``, falling back to ``target_year``.

Repeated forecasts of one realization are not independent, so the coverage,
cluster and loss tables are descriptive.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

VARIABLE_LABELS = {
    ("us", "PRGDP"): "US real GDP",
    ("us", "PRPGDP"): "US GDP prices",
    ("us", "PRUNEMP"): "US unemployment",
    ("us", "PRCCPI"): "US core CPI",
    ("us", "PRCPCE"): "US core PCE",
    ("ecb", "hicp"): "ECB HICP",
    ("ecb", "hicpx"): "ECB core HICP",
    ("ecb", "rgdp"): "ECB real GDP",
    ("ecb", "unemp"): "ECB unemployment",
}

#: US variables whose pre-1992 rows forecast nominal or real GNP instead.
GDP_SAMPLE = {"PRGDP", "PRPGDP"}
GDP_SAMPLE_START = 1992

#: Balanced Q1 windows for the US term structure, by variable.
US_TERM_WINDOWS = {
    "PRGDP": (2010, 2026),
    "PRUNEMP": (2010, 2026),
    "PRPGDP": (1992, 2026),
    "PRCCPI": (2007, 2026),
    "PRCPCE": (2007, 2026),
}

ECB_MODERN_HORIZONS = ("rolling_1y", "rolling_2y", "longer_term")
MOMENT_FIELDS = ["mean", "within_sd", "disagreement", "total_sd", "iqr"]

SHRINKAGE_WINDOW = (2010, 2019)
LONG_TERM_SPLIT = 2020

#: Wide-bin era windows as inclusive (year, quarter) round bounds.
BIN_ERAS = {
    "pre": ((2016, 2), (2020, 1)),
    "wide": ((2020, 2), (2024, 1)),
    "post": ((2024, 2), (2026, 3)),
}
BIN_ERA_VARIABLES = ("PRGDP", "PRUNEMP")

#: Event-year windows for the clustered-loss comparison.
TAIL_WINDOWS = {
    "1996–2001": (1996, 2001),
    "2008–09": (2008, 2009),
    "2020–22": (2020, 2022),
}

DECILES = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]
TAIL_FIELDS = ["n", "pinball_05", "pinball_95", "ratio_95_over_05", "larger_tail"]


def label(survey: str, variable: str) -> str:
    """Report label for a survey-variable pair."""
    return VARIABLE_LABELS[(survey, variable)]


def _labelled(frame: pd.DataFrame) -> pd.DataFrame:
    """Insert the report label after the survey-variable key columns."""
    out = frame.copy()
    out.insert(2, "label", [label(s, v) for s, v in zip(out.survey, out.variable)])
    return out


def primary_sample(frame: pd.DataFrame) -> pd.DataFrame:
    """Drop the US pre-1992 GNP-era rows from a measures-shaped frame."""
    annex = (
        (frame.survey == "us")
        & frame.variable.isin(GDP_SAMPLE)
        & (frame.year < GDP_SAMPLE_START)
    )
    return frame[~annex].copy()


def _round_index(frame: pd.DataFrame) -> pd.Series:
    return frame.year * 4 + frame.quarter - 1


def event_year(frame: pd.DataFrame) -> pd.Series:
    """Realization event year: the leading year of ``target_period``.

    Calendar targets carry a bare ``YYYY`` label, so this equals
    ``target_year`` for every calendar row and supplies the year that ECB
    rolling monthly and quarterly targets leave null.
    """
    parsed = frame.target_period.astype(str).str.extract(r"^(\d{4})")[0]
    return pd.to_numeric(parsed, errors="coerce").fillna(frame.target_year)


def _pct_change(old: float, new: float) -> float:
    return 100 * (new / old - 1) if old else float("nan")


def headline_series(measures: pd.DataFrame) -> pd.DataFrame:
    """Annual headline series: US Q1 next-year rows, ECB rolling-1y means.

    Returns one row per survey-variable-year with the pooled moments, so the
    stability summary and any trajectory chart share a single definition.
    """
    sample = primary_sample(measures)
    rows = []
    for (survey, variable), group in sample.groupby(["survey", "variable"]):
        if survey == "us":
            selected = group[
                (group.quarter == 1) & (group.horizon_class == "next_year")
            ]
            basis = "Q1 next calendar year"
        else:
            selected = group[group.horizon_class == "rolling_1y"]
            basis = "annual mean of quarterly rolling 1y"
        if selected.empty:
            continue
        annual = selected.groupby("year")[MOMENT_FIELDS].mean().reset_index()
        annual.insert(0, "survey", survey)
        annual.insert(1, "variable", variable)
        annual["basis"] = basis
        annual["n_rounds"] = (
            selected.groupby("year").size().reindex(annual.year).to_numpy()
        )
        rows.append(annual)
    return _labelled(pd.concat(rows, ignore_index=True))


def stability_summary(measures: pd.DataFrame) -> pd.DataFrame:
    """Total-SD levels of the headline series: start, decades, peak, 2026."""
    series = headline_series(measures)
    rows = []
    for (survey, variable), group in series.groupby(["survey", "variable"]):
        annual = group.set_index("year").sort_index()
        total = annual.total_sd
        through = total[total.index <= LONG_TERM_SPLIT]
        peak_year = int(total.idxmax())
        first_year = int(total.index.min())
        value_2026 = float(total.loc[2026]) if 2026 in total.index else float("nan")
        rows.append(
            {
                "survey": survey,
                "variable": variable,
                "basis": annual.basis.iloc[0],
                "first_year": first_year,
                "last_year": int(total.index.max()),
                "n_years": len(total),
                "value_first_year": float(total.iloc[0]),
                "mean_full": float(total.mean()),
                "mean_through_2020": float(through.mean()),
                "mean_2010_2019": float(
                    total[total.index.isin(range(2010, 2020))].mean()
                ),
                "mean_2020_2024": float(
                    total[total.index.isin(range(2020, 2025))].mean()
                ),
                "peak_value": float(total.max()),
                "peak_year": peak_year,
                "value_2026": value_2026,
                "pct_2026_vs_through_2020": _pct_change(through.mean(), value_2026),
                "pct_2020_2024_vs_2010_2019": _pct_change(
                    total[total.index.isin(range(2010, 2020))].mean(),
                    total[total.index.isin(range(2020, 2025))].mean(),
                ),
            }
        )
    return _labelled(pd.DataFrame(rows))


def disagreement_shares(measures: pd.DataFrame) -> pd.DataFrame:
    """Deciles of the between-forecaster variance share, per survey-variable.

    ``median_total_over_disagreement`` is the median ratio of pooled total SD
    to disagreement SD: the factor by which point-forecast spread understates
    stated uncertainty on a typical round-target.
    """
    sample = primary_sample(measures).dropna(subset=["share_between"])
    rows = []
    for (survey, variable), group in sample.groupby(["survey", "variable"]):
        share = 100 * group.share_between
        quantiles = share.quantile(DECILES)
        ratio = (group.total_sd / group.disagreement).replace([np.inf, -np.inf], np.nan)
        rows.append(
            {
                "survey": survey,
                "variable": variable,
                "n_rounds": len(group),
                **{
                    f"decile_{round(100 * q)}": float(quantiles.loc[q]) for q in DECILES
                },
                "median": float(share.median()),
                "share_at_or_below_20": float(100 * (share <= 20).mean()),
                "median_total_over_disagreement": float(ratio.median()),
            }
        )
    return _labelled(pd.DataFrame(rows))


def us_term_structure(measures: pd.DataFrame) -> pd.DataFrame:
    """Balanced US Q1 term structure by horizon, one window per variable."""
    sample = primary_sample(measures)
    rows = []
    for variable, (start, end) in US_TERM_WINDOWS.items():
        group = sample[
            (sample.survey == "us")
            & (sample.variable == variable)
            & (sample.quarter == 1)
            & sample.year.between(start, end)
        ].dropna(subset=["horizon_years"])
        if group.empty:
            continue
        horizons = sorted(group.horizon_years.unique())
        present = group.groupby("year").horizon_years.nunique()
        balanced_years = present[present == len(horizons)].index
        balanced = group[group.year.isin(balanced_years)]
        for horizon in horizons:
            cell = balanced[balanced.horizon_years == horizon]
            rows.append(
                {
                    "survey": "us",
                    "variable": variable,
                    "sample": f"Q1 {start}–{end % 100:02d}",
                    "horizon_key": f"h{int(horizon)}",
                    "horizon_years": float(horizon),
                    "n_rounds": len(cell),
                    "within_sd": float(cell.within_sd.mean()),
                    "total_sd": float(cell.total_sd.mean()),
                    "iqr": float(cell.iqr.mean()),
                }
            )
    return _labelled(pd.DataFrame(rows))


def ecb_round_panel(measures: pd.DataFrame) -> pd.DataFrame:
    """One row per ECB round and modern horizon class.

    Early Q1 rounds carry a rolling five-year target alongside the calendar
    longer-term target; both are labelled ``longer_term``, so duplicates are
    averaged within the round before any round is called balanced.
    """
    group = measures[
        (measures.survey == "ecb") & measures.horizon_class.isin(ECB_MODERN_HORIZONS)
    ]
    return (
        group.groupby(["survey", "variable", "year", "quarter", "horizon_class"])[
            MOMENT_FIELDS
        ]
        .mean()
        .reset_index()
    )


def _balanced_ecb_rounds(panel: pd.DataFrame) -> pd.DataFrame:
    present = panel.groupby(["variable", "year", "quarter"]).horizon_class.nunique()
    keys = present[present == len(ECB_MODERN_HORIZONS)].index
    index = pd.MultiIndex.from_frame(panel[["variable", "year", "quarter"]])
    return panel[index.isin(keys)].copy()


def ecb_term_structure(measures: pd.DataFrame) -> pd.DataFrame:
    """Round-balanced ECB term structure across the three modern horizons."""
    balanced = _balanced_ecb_rounds(ecb_round_panel(measures))
    rows = []
    for (variable, horizon), cell in balanced.groupby(["variable", "horizon_class"]):
        rows.append(
            {
                "survey": "ecb",
                "variable": variable,
                "sample": "round-balanced",
                "horizon_key": horizon,
                "horizon_years": float("nan"),
                "n_rounds": len(cell),
                "within_sd": float(cell.within_sd.mean()),
                "total_sd": float(cell.total_sd.mean()),
                "iqr": float(cell.iqr.mean()),
            }
        )
    order = {name: position for position, name in enumerate(ECB_MODERN_HORIZONS)}
    frame = pd.DataFrame(rows)
    frame["_order"] = frame.horizon_key.map(order)
    frame = frame.sort_values(["variable", "_order"]).drop(columns="_order")
    return _labelled(frame.reset_index(drop=True))


def term_structure(measures: pd.DataFrame) -> pd.DataFrame:
    """US and ECB balanced term structures in one table."""
    return pd.concat(
        [us_term_structure(measures), ecb_term_structure(measures)], ignore_index=True
    )


def fixed_event_shrinkage(measures: pd.DataFrame) -> pd.DataFrame:
    """Current-year total SD by survey quarter over the clean 2010–19 window."""
    start, end = SHRINKAGE_WINDOW
    sample = primary_sample(measures)
    current = sample[
        (sample.horizon_class == "current_year") & sample.year.between(start, end)
    ]
    rows = []
    for (survey, variable), group in current.groupby(["survey", "variable"]):
        by_quarter = group.groupby("quarter").total_sd.agg(["mean", "size"])
        record = {
            "survey": survey,
            "variable": variable,
            "window": f"{start}–{end}",
        }
        for quarter in (1, 2, 3, 4):
            if quarter in by_quarter.index:
                record[f"total_sd_q{quarter}"] = float(by_quarter.loc[quarter, "mean"])
                record[f"n_q{quarter}"] = int(by_quarter.loc[quarter, "size"])
            else:
                record[f"total_sd_q{quarter}"] = float("nan")
                record[f"n_q{quarter}"] = 0
        record["pct_change_q1_q4"] = _pct_change(
            record["total_sd_q1"], record["total_sd_q4"]
        )
        rows.append(record)
    return _labelled(pd.DataFrame(rows))


def _coverage_row(survey: str, variable: str, sample: str, group: pd.DataFrame) -> dict:
    return {
        "survey": survey,
        "variable": variable,
        "sample": sample,
        "n": len(group),
        "inside_1sd": int(group.inside_1sd.sum()),
        "inside_1sd_pct": float(100 * group.inside_1sd.mean()),
        "inside_pooled_90": int(group.inside_pooled_90.sum()),
        "inside_pooled_90_pct": float(100 * group.inside_pooled_90.mean()),
        "first_event_year": int(event_year(group).min()),
        "last_event_year": int(event_year(group).max()),
    }


def coverage_summary(calibration: pd.DataFrame) -> pd.DataFrame:
    """Interval coverage over all calibrated horizons and the one-year rows."""
    rows = []
    for (survey, variable), group in calibration.groupby(["survey", "variable"]):
        rows.append(_coverage_row(survey, variable, "all horizons", group))
        one_year = group[(group.quarter == 1) & (group.horizon_class == "next_year")]
        if not one_year.empty:
            rows.append(_coverage_row(survey, variable, "Q1 next year", one_year))
        rolling = group[group.horizon_class == "rolling_1y"]
        if not rolling.empty:
            rows.append(_coverage_row(survey, variable, "rolling 1y", rolling))
    return _labelled(pd.DataFrame(rows))


def miss_clusters(calibration: pd.DataFrame) -> pd.DataFrame:
    """Interval misses by target year, with the all-miss consecutive runs.

    ``run_length`` labels each row in a maximal run of consecutive target
    years whose every forecast fell outside the ±1 SD band, so the longest
    cluster can be read off the table instead of restated in prose.
    """
    frame = calibration.assign(event_year=event_year(calibration).astype(int))
    rows = []
    for (survey, variable), group in frame.groupby(["survey", "variable"]):
        by_year = group.groupby("event_year").agg(
            n_forecasts=("inside_1sd", "size"),
            n_inside_1sd=("inside_1sd", "sum"),
            n_inside_pooled_90=("inside_pooled_90", "sum"),
        )
        by_year["n_miss_1sd"] = by_year.n_forecasts - by_year.n_inside_1sd
        by_year["n_miss_pooled_90"] = by_year.n_forecasts - by_year.n_inside_pooled_90
        by_year["all_miss_1sd"] = by_year.n_inside_1sd == 0
        by_year["all_miss_pooled_90"] = by_year.n_inside_pooled_90 == 0
        by_year = by_year.reset_index()
        by_year.insert(0, "survey", survey)
        by_year.insert(1, "variable", variable)
        rows.append(_annotate_runs(by_year))
    frame = pd.concat(rows, ignore_index=True)
    columns = [
        "survey",
        "variable",
        "event_year",
        "n_forecasts",
        "n_miss_1sd",
        "n_miss_pooled_90",
        "all_miss_1sd",
        "all_miss_pooled_90",
        "run_start",
        "run_end",
        "run_length",
    ]
    return _labelled(frame[columns])


def _annotate_runs(by_year: pd.DataFrame) -> pd.DataFrame:
    """Label maximal runs of consecutive all-miss target years."""
    frame = by_year.sort_values("event_year").reset_index(drop=True)
    frame["run_start"] = pd.NA
    frame["run_end"] = pd.NA
    frame["run_length"] = 0
    years = frame.event_year.astype(int).to_list()
    flags = frame.all_miss_1sd.to_list()

    def close(run: list[int]) -> None:
        if not run:
            return
        frame.loc[run, "run_start"] = years[run[0]]
        frame.loc[run, "run_end"] = years[run[-1]]
        frame.loc[run, "run_length"] = len(run)

    run: list[int] = []
    for position, flag in enumerate(flags):
        if flag and run and years[run[-1]] == years[position] - 1:
            run.append(position)
            continue
        close(run)
        run = [position] if flag else []
    close(run)
    return frame


def longer_term_shift(measures: pd.DataFrame) -> pd.DataFrame:
    """ECB one-year and longer-term uncertainty and consensus, split at 2021.

    Both horizons are read from the same round-balanced panel, so the change
    at one horizon is never averaged over a different set of rounds than the
    change at the other.
    """
    balanced = _balanced_ecb_rounds(ecb_round_panel(measures))
    rows = []
    for (variable, horizon), cell in balanced.groupby(["variable", "horizon_class"]):
        if horizon == "rolling_2y":
            continue
        early = cell[cell.year <= LONG_TERM_SPLIT]
        late = cell[cell.year > LONG_TERM_SPLIT]
        annual = cell.groupby("year").total_sd.mean()
        rows.append(
            {
                "survey": "ecb",
                "variable": variable,
                "horizon_key": horizon,
                "series_high_total_sd": float(annual.max()),
                "series_high_year": int(annual.idxmax()),
                "total_sd_2026": (
                    float(annual.loc[2026]) if 2026 in annual.index else float("nan")
                ),
                "n_rounds_through_2020": len(early),
                "n_rounds_2021_2026": len(late),
                "total_sd_through_2020": float(early.total_sd.mean()),
                "total_sd_2021_2026": float(late.total_sd.mean()),
                "pct_change_total_sd": _pct_change(
                    early.total_sd.mean(), late.total_sd.mean()
                ),
                "consensus_through_2020": float(early["mean"].mean()),
                "consensus_2021_2026": float(late["mean"].mean()),
                "change_consensus": float(late["mean"].mean() - early["mean"].mean()),
            }
        )
    frame = pd.DataFrame(rows).sort_values(["variable", "horizon_key"])
    return _labelled(frame.reset_index(drop=True))


def pooling_gain(scores: pd.DataFrame) -> pd.DataFrame:
    """Pooled versus average-individual CRPS, by survey-variable-horizon cell."""
    rows = []
    keys = ["survey", "variable", "horizon_class"]
    for (survey, variable, horizon), cell in scores.groupby(keys):
        pooled = cell.crps_pooled.mean()
        individual = cell.crps_individual_mean.mean()
        rows.append(
            {
                "survey": survey,
                "variable": variable,
                "horizon_class": horizon,
                "n": len(cell),
                "pooled_crps": float(pooled),
                "individual_crps": float(individual),
                "gain": float(individual - pooled),
                "gain_pct": float(100 * (1 - pooled / individual)),
                "rows_pooled_better": int(
                    (cell.crps_pooled <= cell.crps_individual_mean).sum()
                ),
            }
        )
    return _labelled(pd.DataFrame(rows))


def skill_summary(benchmarks: pd.DataFrame, scores: pd.DataFrame) -> pd.DataFrame:
    """Ratio-of-means CRPS skill per survey-variable, beside the pooling gain."""
    wide = benchmarks.pivot(
        index=["survey", "variable"],
        columns="benchmark",
        values=[
            "n",
            "pooled_crps",
            "benchmark_crps",
            "skill_ratio_of_means",
            "mean_row_skill",
        ],
    )
    wide.columns = [f"{field}_{benchmark}" for field, benchmark in wide.columns]
    frame = wide.reset_index()
    gains = []
    for (survey, variable), cell in scores.groupby(["survey", "variable"]):
        pooled = cell.crps_pooled.mean()
        individual = cell.crps_individual_mean.mean()
        gains.append(
            {
                "survey": survey,
                "variable": variable,
                "n_scored": len(cell),
                "gain_pct": float(100 * (1 - pooled / individual)),
            }
        )
    frame = frame.merge(pd.DataFrame(gains), on=["survey", "variable"])
    for benchmark in ("climatology", "gaussian"):
        frame[f"skill_pct_{benchmark}"] = (
            100 * frame[f"skill_ratio_of_means_{benchmark}"]
        )
        frame[f"row_skill_pct_{benchmark}"] = 100 * frame[f"mean_row_skill_{benchmark}"]
    return _labelled(frame)


def tail_losses(scores: pd.DataFrame) -> pd.DataFrame:
    """Mean 05 and 95 pinball loss inside each clustered-event window."""
    frame = scores.copy()
    frame["event_year"] = event_year(frame)
    rows = []
    for window, (start, end) in TAIL_WINDOWS.items():
        subset = frame[frame.event_year.between(start, end)]
        for (survey, variable), cell in subset.groupby(["survey", "variable"]):
            lower = float(cell.pinball_05.mean())
            upper = float(cell.pinball_95.mean())
            rows.append(
                {
                    "window": window,
                    "survey": survey,
                    "variable": variable,
                    "n": len(cell),
                    "pinball_05": lower,
                    "pinball_95": upper,
                    "ratio_95_over_05": upper / lower if lower else float("nan"),
                    "larger_tail": "upper (95)" if upper > lower else "lower (05)",
                }
            )
    out = _labelled(pd.DataFrame(rows)[["survey", "variable", *TAIL_FIELDS]])
    out.insert(0, "window", [row["window"] for row in rows])
    return out


def pit_deciles(scores: pd.DataFrame) -> pd.DataFrame:
    """Share of calibrated rows per PIT decile, with the final decile closed."""
    edges = np.linspace(0, 1, 11)
    rows = []
    for (survey, variable), cell in scores.dropna(subset=["pit"]).groupby(
        ["survey", "variable"]
    ):
        counts = np.histogram(cell.pit.clip(0, 1), bins=edges)[0]
        record = {
            "survey": survey,
            "variable": variable,
            "n": len(cell),
            "mean_pit": float(cell.pit.mean()),
        }
        for position, count in enumerate(counts, start=1):
            record[f"decile_{position}"] = float(100 * count / len(cell))
        record["share_extreme_deciles"] = record["decile_1"] + record["decile_10"]
        rows.append(record)
    return _labelled(pd.DataFrame(rows))


def bin_era_comparison(measures: pd.DataFrame) -> pd.DataFrame:
    """Wide-bin era levels and the clean 2024Q1-to-Q2 scheme boundary.

    Era rows average every Q1–Q4 round and every horizon in the window
    equally; boundary rows hold the horizon fixed at next year, so the only
    documented change between them is the bin scheme and one quarter of
    information.
    """
    sample = measures[
        (measures.survey == "us") & measures.variable.isin(BIN_ERA_VARIABLES)
    ].copy()
    sample["round_index"] = _round_index(sample)
    rows = []
    for variable, group in sample.groupby("variable"):
        for period, ((y0, q0), (y1, q1)) in BIN_ERAS.items():
            cell = group[group.round_index.between(y0 * 4 + q0 - 1, y1 * 4 + q1 - 1)]
            rows.append(
                _era_row(variable, "era", f"{period} ({y0}Q{q0}–{y1}Q{q1})", cell)
            )
        boundary = group[group.horizon_class == "next_year"]
        for year, quarter in ((2024, 1), (2024, 2)):
            cell = boundary[(boundary.year == year) & (boundary.quarter == quarter)]
            rows.append(
                _era_row(variable, "boundary (next year)", f"{year}Q{quarter}", cell)
            )
    return pd.DataFrame(rows)


def _era_row(variable: str, comparison: str, period: str, cell: pd.DataFrame) -> dict:
    within = float(cell.within_sd.mean())
    total = float(cell.total_sd.mean())
    iqr = float(cell.iqr.mean())
    return {
        "survey": "us",
        "variable": variable,
        "label": label("us", variable),
        "comparison": comparison,
        "period": period,
        "n_rounds": int(cell.groupby(["year", "quarter"]).ngroups),
        "n_rows": len(cell),
        "within_sd": within,
        "total_sd": total,
        "iqr": iqr,
        "within_over_iqr": within / iqr if iqr else float("nan"),
        "total_over_iqr": total / iqr if iqr else float("nan"),
    }


def build_all(
    measures: pd.DataFrame,
    calibration: pd.DataFrame,
    scores: pd.DataFrame,
    benchmarks: pd.DataFrame,
) -> dict[str, pd.DataFrame]:
    """Every panorama table, keyed by its ``outputs/`` file stem."""
    return {
        "panorama_1": stability_summary(measures),
        "panorama_2": disagreement_shares(measures),
        "panorama_3": term_structure(measures),
        "panorama_4": fixed_event_shrinkage(measures),
        "panorama_5": coverage_summary(calibration),
        "panorama_5_clusters": miss_clusters(calibration),
        "panorama_6": longer_term_shift(measures),
        "panorama_7": skill_summary(benchmarks, scores),
        "panorama_7_gain": pooling_gain(scores),
        "panorama_8": tail_losses(scores),
        "panorama_9": pit_deciles(scores),
        "panorama_10": bin_era_comparison(measures),
    }
