"""Tests for the panorama tables the main manuscript reads.

Each table is checked against an independent computation over the same
``outputs/*.csv`` rows, so a convention drifting inside
``forecast_uncertainty.panorama`` cannot silently move a manuscript number.
"""

from pathlib import Path

import pandas as pd
import pytest

from forecast_uncertainty import panorama

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "outputs"


@pytest.fixture(scope="module")
def measures():
    return pd.read_csv(OUT / "measures.csv")


@pytest.fixture(scope="module")
def calibration():
    return pd.read_csv(OUT / "calibration.csv")


@pytest.fixture(scope="module")
def scores():
    return pd.read_csv(OUT / "scores.csv")


@pytest.fixture(scope="module")
def benchmarks():
    return pd.read_csv(OUT / "benchmark_summary.csv")


def test_primary_sample_drops_only_the_us_gnp_era(measures):
    sample = panorama.primary_sample(measures)
    dropped = measures.loc[measures.index.difference(sample.index)]
    assert set(dropped.variable) == {"PRGDP", "PRPGDP"}
    assert set(dropped.survey) == {"us"}
    assert dropped.year.max() < panorama.GDP_SAMPLE_START
    assert not dropped.concept.isin(
        ["real_gdp", "chain_weighted_gdp_price_index"]
    ).any()


def test_event_year_matches_target_year_wherever_it_is_recorded(calibration):
    parsed = panorama.event_year(calibration)
    recorded = calibration.target_year.notna()
    assert (parsed[recorded] == calibration.target_year[recorded]).all()
    assert parsed.notna().all()


def test_coverage_counts_equal_calibration_sums(calibration):
    coverage = panorama.coverage_summary(calibration)
    for row in coverage.itertuples():
        group = calibration[
            (calibration.survey == row.survey) & (calibration.variable == row.variable)
        ]
        if row.sample == "Q1 next year":
            group = group[(group.quarter == 1) & (group.horizon_class == "next_year")]
        elif row.sample == "rolling 1y":
            group = group[group.horizon_class == "rolling_1y"]
        assert row.n == len(group)
        assert row.inside_1sd == group.inside_1sd.sum()
        assert row.inside_pooled_90 == group.inside_pooled_90.sum()
        assert row.inside_1sd_pct == pytest.approx(100 * group.inside_1sd.mean())
        assert row.inside_pooled_90_pct == pytest.approx(
            100 * group.inside_pooled_90.mean()
        )


def test_us_term_structure_means_match_a_direct_groupby(measures):
    term = panorama.us_term_structure(measures)
    for variable, (start, end) in panorama.US_TERM_WINDOWS.items():
        direct = measures[
            (measures.survey == "us")
            & (measures.variable == variable)
            & (measures.quarter == 1)
            & measures.year.between(
                max(start, panorama.GDP_SAMPLE_START)
                if variable in panorama.GDP_SAMPLE
                else start,
                end,
            )
        ]
        expected = direct.groupby("horizon_years")[["within_sd", "total_sd"]].mean()
        actual = term[term.variable == variable].set_index("horizon_years")
        assert len(actual) == len(expected)
        for horizon in expected.index:
            assert actual.loc[horizon, "within_sd"] == pytest.approx(
                expected.loc[horizon, "within_sd"]
            )
            assert actual.loc[horizon, "total_sd"] == pytest.approx(
                expected.loc[horizon, "total_sd"]
            )


def test_us_term_structure_windows_are_balanced(measures):
    term = panorama.us_term_structure(measures)
    for variable, group in term.groupby("variable"):
        assert group.n_rounds.nunique() == 1, f"{variable} horizons are unbalanced"


def test_ecb_term_structure_balances_rounds_and_averages_duplicates(measures):
    term = panorama.ecb_term_structure(measures)
    for variable, group in term.groupby("variable"):
        assert group.n_rounds.nunique() == 1, f"{variable} horizons are unbalanced"
        assert set(group.horizon_key) == set(panorama.ECB_MODERN_HORIZONS)

    # Duplicate early longer-term targets must be averaged, not counted twice.
    panel = panorama.ecb_round_panel(measures)
    duplicates = (
        measures[
            (measures.survey == "ecb")
            & (measures.variable == "hicp")
            & (measures.horizon_class == "longer_term")
        ]
        .groupby(["year", "quarter"])
        .size()
    )
    assert (duplicates > 1).any(), "fixture no longer exercises duplicate targets"
    assert (
        panel[(panel.variable == "hicp") & (panel.horizon_class == "longer_term")]
        .groupby(["year", "quarter"])
        .size()
        .max()
        == 1
    )


def test_stability_summary_reads_the_headline_series(measures):
    series = panorama.headline_series(measures)
    summary = panorama.stability_summary(measures).set_index(["survey", "variable"])
    prgdp = series[(series.survey == "us") & (series.variable == "PRGDP")]
    row = summary.loc[("us", "PRGDP")]
    assert row.first_year == prgdp.year.min() == panorama.GDP_SAMPLE_START
    assert row.peak_value == pytest.approx(prgdp.total_sd.max())
    assert row.peak_year == int(prgdp.loc[prgdp.total_sd.idxmax(), "year"])
    assert row.mean_through_2020 == pytest.approx(
        prgdp[prgdp.year <= 2020].total_sd.mean()
    )
    # The ECB basis is the annual mean of its quarterly rolling-1y rounds.
    hicp = measures[
        (measures.survey == "ecb")
        & (measures.variable == "hicp")
        & (measures.horizon_class == "rolling_1y")
    ]
    assert summary.loc[("ecb", "hicp"), "value_2026"] == pytest.approx(
        hicp[hicp.year == 2026].total_sd.mean()
    )


def test_disagreement_deciles_are_ordered_and_bounded(measures):
    shares = panorama.disagreement_shares(measures)
    columns = [f"decile_{step}" for step in range(10, 100, 10)]
    for row in shares.itertuples():
        values = [getattr(row, column) for column in columns]
        assert values == sorted(values)
        assert 0 <= values[0] and values[-1] <= 100
        assert row.median == pytest.approx(row.decile_50)
    assert shares.n_rounds.sum() == len(panorama.primary_sample(measures))


def test_fixed_event_shrinkage_percent_matches_its_own_levels(measures):
    shrinkage = panorama.fixed_event_shrinkage(measures)
    for row in shrinkage.itertuples():
        assert row.pct_change_q1_q4 == pytest.approx(
            100 * (row.total_sd_q4 / row.total_sd_q1 - 1)
        )
        assert row.n_q1 == row.n_q2 == row.n_q3 == row.n_q4
        assert row.total_sd_q4 < row.total_sd_q1


def test_miss_cluster_runs_are_maximal_and_consecutive(calibration):
    clusters = panorama.miss_clusters(calibration)
    assert clusters.n_forecasts.sum() == len(calibration)
    assert (clusters.all_miss_1sd == (clusters.run_length > 0)).all()
    for (survey, variable), group in clusters.groupby(["survey", "variable"]):
        for (start, end), run in group.dropna(subset=["run_start"]).groupby(
            ["run_start", "run_end"]
        ):
            years = sorted(run.event_year)
            assert years == list(range(int(start), int(end) + 1))
            assert (run.run_length == len(years)).all()
            # A maximal run cannot be extended by an adjacent all-miss year.
            neighbours = group[group.event_year.isin([start - 1, end + 1])]
            assert not neighbours.all_miss_1sd.any()


def test_longer_term_shift_balances_both_horizons(measures):
    shift = panorama.longer_term_shift(measures)
    for variable, group in shift.groupby("variable"):
        assert group.n_rounds_through_2020.nunique() == 1
        assert group.n_rounds_2021_2026.nunique() == 1
        assert set(group.horizon_key) == {"rolling_1y", "longer_term"}
    for row in shift.itertuples():
        assert row.pct_change_total_sd == pytest.approx(
            100 * (row.total_sd_2021_2026 / row.total_sd_through_2020 - 1)
        )
        assert row.change_consensus == pytest.approx(
            row.consensus_2021_2026 - row.consensus_through_2020
        )
        assert row.series_high_total_sd >= row.total_sd_2026


def test_skill_summary_preserves_the_ratio_of_means_definition(benchmarks, scores):
    skill = panorama.skill_summary(benchmarks, scores).set_index(["survey", "variable"])
    source = benchmarks.set_index(["survey", "variable", "benchmark"])
    for (survey, variable, benchmark), row in source.iterrows():
        computed = skill.loc[(survey, variable), f"skill_pct_{benchmark}"]
        assert computed == pytest.approx(100 * row.skill_ratio_of_means)
        assert skill.loc[(survey, variable), f"n_{benchmark}"] == row.n
        assert row.skill_ratio_of_means == pytest.approx(
            1 - row.pooled_crps / row.benchmark_crps
        )


def test_pooling_gain_is_positive_on_every_cell_and_row(scores):
    gain = panorama.pooling_gain(scores)
    assert gain.n.sum() == len(scores)
    assert (gain.rows_pooled_better == gain.n).all()
    assert (gain.gain_pct > 0).all()
    for row in gain.itertuples():
        cell = scores[
            (scores.survey == row.survey)
            & (scores.variable == row.variable)
            & (scores.horizon_class == row.horizon_class)
        ]
        assert row.gain_pct == pytest.approx(
            100 * (1 - cell.crps_pooled.mean() / cell.crps_individual_mean.mean())
        )


def test_tail_losses_count_rows_by_event_year(scores):
    losses = panorama.tail_losses(scores)
    years = panorama.event_year(scores)
    for row in losses.itertuples():
        start, end = panorama.TAIL_WINDOWS[row.window]
        cell = scores[
            years.between(start, end)
            & (scores.survey == row.survey)
            & (scores.variable == row.variable)
        ]
        assert row.n == len(cell)
        assert row.pinball_05 == pytest.approx(cell.pinball_05.mean())
        assert row.pinball_95 == pytest.approx(cell.pinball_95.mean())
        assert (row.larger_tail == "upper (95)") == (row.pinball_95 > row.pinball_05)


def test_pit_decile_shares_account_for_every_scored_row(scores):
    deciles = panorama.pit_deciles(scores)
    columns = [f"decile_{step}" for step in range(1, 11)]
    assert deciles.n.sum() == scores.pit.notna().sum()
    for row in deciles.itertuples():
        shares = [getattr(row, column) for column in columns]
        assert sum(shares) == pytest.approx(100)
        assert row.share_extreme_deciles == pytest.approx(shares[0] + shares[-1])


def test_bin_era_windows_hold_the_documented_round_counts(measures):
    eras = panorama.bin_era_comparison(measures)
    expected = {"pre": 16, "wide": 16, "post": 10}
    for row in eras.itertuples():
        if row.comparison == "era":
            assert row.n_rounds == expected[row.period.split(" ")[0]]
            assert row.n_rows == 4 * row.n_rounds
        else:
            assert row.n_rounds == 1
            assert row.n_rows == 1


def test_written_tables_match_the_module(
    tmp_path, measures, calibration, scores, benchmarks
):
    """The committed CSVs must be what the current code produces."""
    tables = panorama.build_all(measures, calibration, scores, benchmarks)
    assert set(tables) == {
        "panorama_1",
        "panorama_2",
        "panorama_3",
        "panorama_4",
        "panorama_5",
        "panorama_5_clusters",
        "panorama_6",
        "panorama_7",
        "panorama_7_gain",
        "panorama_8",
        "panorama_9",
        "panorama_10",
    }
    for stem, frame in tables.items():
        written = OUT / f"{stem}.csv"
        assert written.exists(), f"{stem}.csv is missing; run scripts/build_panorama.py"
        fresh = tmp_path / f"{stem}.csv"
        frame.to_csv(fresh, index=False)
        assert fresh.read_text() == written.read_text(), (
            f"{stem}.csv is stale; run scripts/build_panorama.py"
        )
