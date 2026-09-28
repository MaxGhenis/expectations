"""Outcome snapshots must be current, pinned, and never drop a published year.

The US unemployment and core CPI outcomes once came from a DBnomics mirror that
stopped at January 2025, so every 2025 target went unscored without an error.
These tests fail on that kind of gap: a series that ends before a period its
publisher has released, or a published target with no realization.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from expectations.outcome_sources import (
    ECB_OUTCOME_MANIFEST,
    OUTCOME_SNAPSHOTS,
    US_OUTCOME_MANIFEST,
    US_OUTCOME_SOURCES,
    check_publication_currency,
    latest_certainly_published,
    load_bls_file,
    load_dbnomics_file,
    outcome_snapshots,
)
from expectations.realizations import (
    DEFAULT_RAW_DIR,
    load_realizations,
    load_us_realization_history,
    q4_over_q4_growth,
    unresolved_published_targets,
)

ROOT = Path(__file__).resolve().parents[1]


def _us_manifest() -> dict:
    return json.loads((DEFAULT_RAW_DIR / US_OUTCOME_MANIFEST).read_text())


def _bls(filename: str):
    return load_bls_file((DEFAULT_RAW_DIR / filename).read_bytes())


def test_every_published_forecast_target_has_a_realization():
    """No target the surveys asked about is silently left unscored."""
    measures = pd.read_csv(ROOT / "outputs" / "measures.csv", low_memory=False)
    missing = unresolved_published_targets(measures)
    assert missing.empty, missing.to_string()


@pytest.mark.parametrize(
    "key", [key for key in OUTCOME_SNAPSHOTS if key[2] == "annual"], ids=str
)
def test_every_published_target_year_has_a_realization(key):
    """Each annual outcome runs without a gap to the latest year surely published."""
    survey, variable, _ = key
    snapshot = outcome_snapshots()[key]
    last = int(
        latest_certainly_published(
            "annual", lag_days=snapshot["lag_days"], as_of=snapshot["as_of"]
        )
    )
    realized = load_realizations()
    years = realized[
        (realized.survey == survey)
        & (realized.variable == variable)
        & realized.target_period.str.fullmatch(r"\d{4}")
    ].target_year.astype(int)
    assert years.max() >= last
    assert sorted(years) == list(range(years.min(), years.max() + 1))


def test_snapshot_dates_describe_the_committed_bytes():
    snapshots = outcome_snapshots()
    assert set(snapshots) == set(OUTCOME_SNAPSHOTS)
    for manifest_name in (US_OUTCOME_MANIFEST, ECB_OUTCOME_MANIFEST):
        manifest = json.loads((DEFAULT_RAW_DIR / manifest_name).read_text())
        entries = manifest["sources"] | manifest.get("rolling_archives", {})
        for filename, entry in entries.items():
            payload = (DEFAULT_RAW_DIR / filename).read_bytes()
            assert hashlib.sha256(payload).hexdigest() == entry["sha256"], filename


def test_us_snapshot_bounds_agree_with_their_sources():
    for (survey, _, _), (manifest, files, lag_days) in OUTCOME_SNAPSHOTS.items():
        if survey == "us_spf":
            assert manifest == US_OUTCOME_MANIFEST
            assert lag_days == max(
                US_OUTCOME_SOURCES[name]["lag_days"] for name in files
            )


def test_us_sources_are_pinned_and_current():
    manifest = _us_manifest()
    assert set(manifest["sources"]) == set(US_OUTCOME_SOURCES)
    assert check_publication_currency(manifest["sources"]) == []
    for filename, entry in manifest["sources"].items():
        payload = (DEFAULT_RAW_DIR / filename).read_bytes()
        assert hashlib.sha256(payload).hexdigest() == entry["sha256"]
        assert entry["retrieved_at_utc"]


def test_frozen_dbnomics_bls_mirror_is_no_longer_read():
    for name in (
        "dbnomics_us_unrate_monthly.json",
        "dbnomics_us_corecpi_sa_monthly.json",
        "dbnomics_us_cpi_sa_monthly.json",
    ):
        assert not (DEFAULT_RAW_DIR / name).exists()
    sources = load_realizations().source
    assert not sources[sources.str.contains("BLS")].str.contains("DBnomics").any()


def test_october_2025_is_recorded_as_not_collected_in_every_bls_series():
    for filename, specification in US_OUTCOME_SOURCES.items():
        if (
            specification["provider"] != "bls"
            or specification["frequency"] != "monthly"
        ):
            continue
        series = _bls(filename)
        assert (2025, 10) in series.unavailable_months, filename
        assert (2025, 9) in series.monthly and (2025, 11) in series.monthly


def test_2025_unemployment_is_the_official_bls_annual_average():
    """Regression: 2025 lacks October, and was dropped before this fix."""
    official = _bls("bls_ln_LNU04000000_annual.json")
    realized = load_realizations().set_index(["survey", "variable", "target_period"])
    row = realized.loc[("us_spf", "prunemp", "2025")]

    assert row.realized == official.annual_averages["2025"] == 4.3
    assert row.realization_concept == "annual_average_civilian_unemployment_rate"
    assert "LNU04000000 official annual average" in row.source
    assert "did not collect 2025-10" in row.source
    assert "11-month averages that exclude October" in official.annual_notes["2025"]
    # Every earlier year is complete and keeps the monthly mean.
    earlier = realized.loc[("us_spf", "prunemp")].drop(index="2025")
    assert earlier.source.eq("BLS LNS14000000 (latest vintage)").all()


def test_2025_core_cpi_fills_october_from_its_neighbours():
    series = _bls("bls_cu_CUSR0000SA0L1E_monthly.json")
    months = series.monthly
    october = (months[(2025, 9)] + months[(2025, 11)]) / 2
    q4_2025 = np.mean([october, months[(2025, 11)], months[(2025, 12)]])
    q4_2024 = np.mean([months[(2024, month)] for month in (10, 11, 12)])
    realized = load_realizations().set_index(["survey", "variable", "target_period"])
    row = realized.loc[("us_spf", "prccpi", "2025")]

    assert row.realized == pytest.approx(100 * (q4_2025 / q4_2024 - 1), abs=1e-12)
    assert "did not collect 2025-10" in row.source
    # Only growth into or out of fourth-quarter 2025 touches the filled month.
    filled = realized.loc[("us_spf", "prccpi")].source.str.contains("did not collect")
    assert set(filled[filled].index) <= {"2025", "2026"}


def test_monthly_mean_agrees_with_the_official_annual_average():
    """Differential: two BLS routes to the same annual concept, complete years."""
    means = _bls("bls_ln_LNS14000000_monthly.json").complete_year_means()
    official = _bls("bls_ln_LNU04000000_annual.json").annual_averages
    shared = sorted(set(means) & set(official))
    differences = {year: abs(means[year] - official[year]) for year in shared}

    assert shared[0] == "1948"
    assert len(shared) >= 77
    # Rounding to 0.1 allows 0.05; seasonal adjustment of the monthly components
    # does not add up to exactly zero over a year, which accounts for the rest.
    assert max(differences.values()) <= 0.1
    recorded = _us_manifest()["verification"][
        "unemployment_monthly_mean_vs_official_annual_average"
    ]
    assert recorded["matched_years"] == len(shared)
    assert recorded["max_absolute_difference_pp"] == pytest.approx(
        max(differences.values())
    )


@pytest.mark.parametrize(
    "filename",
    ["bls_cu_CUSR0000SA0L1E_monthly.json", "dbnomics_us_corepce_price_monthly.json"],
)
def test_q4_growth_matches_an_independent_resample(filename):
    """Differential: the outcome rule against a pandas quarterly resample."""
    if filename.startswith("bls_"):
        series = _bls(filename)
        monthly, not_collected = series.monthly_series(), series.unavailable_periods()
    else:
        monthly = load_dbnomics_file((DEFAULT_RAW_DIR / filename).read_bytes())
        not_collected = frozenset()
    growth = q4_over_q4_growth(monthly, not_collected=not_collected)

    indexed = monthly.copy()
    indexed.index = pd.PeriodIndex(indexed.index, freq="M")
    quarterly = indexed.groupby(indexed.index.asfreq("Q")).agg(["mean", "count"])
    q4 = quarterly[(quarterly.index.quarter == 4) & (quarterly["count"] == 3)]["mean"]
    q4.index = q4.index.year
    reference = {
        str(year): 100 * (value / q4[year - 1] - 1)
        for year, value in q4.items()
        if year - 1 in q4.index
    }
    unfilled = growth[growth.filled_months.map(len) == 0]
    assert set(unfilled.index) == set(reference)
    for year, value in reference.items():
        assert unfilled.loc[year, "realized"] == pytest.approx(value, abs=1e-12)


def test_bea_mirror_matched_bea_at_retrieval():
    recorded = _us_manifest()["verification"]["bea"]
    bea_files = {
        name
        for name, spec in US_OUTCOME_SOURCES.items()
        if spec["provider"] == "dbnomics"
    }
    assert set(recorded) == bea_files
    for entry in recorded.values():
        assert entry["matched_periods"] > 50
        # BEA's bulk files print the same rounded values the mirror carries.
        assert entry["max_absolute_difference"] <= 5e-4


def test_history_loader_reaches_back_to_1948_for_unemployment():
    history = load_us_realization_history()
    unemployment = history[history.variable == "prunemp"].target_year.astype(int)
    assert unemployment.min() == 1948
    assert unemployment.max() >= 2025
