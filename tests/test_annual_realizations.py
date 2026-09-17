"""Calendar-year outcomes must be the published annual rates.

Growth in annual levels is retained as the cross-check that verifies a published
annual rate against its own subannual observations, never as an emitted outcome.
"""

import hashlib
import json
import shutil
from pathlib import Path

import pandas as pd
import pytest

from forecast_uncertainty.realizations import (
    DEFAULT_RAW_DIR,
    _ecb_level_annual_rows,
    _load_ecb_series,
    _load_verified_ecb_companion,
    load_ecb_realizations,
    load_realization_history,
)

OFFICIAL_ANNUAL_GDP_KEY = "MNA.A.N.I9.W2.S1.S1.B.B1GQ._Z._Z._Z.EUR_R_B1GQ.Y.GOY"


def _level_rows(periods, values, statuses=None):
    return pd.DataFrame(
        {
            "TIME_PERIOD": periods,
            "OBS_VALUE": values,
            "OBS_STATUS": statuses or ["A"] * len(periods),
        }
    )


def _annual(observations, frequency="quarterly"):
    return _ecb_level_annual_rows(
        observations,
        variable="rgdp",
        frequency=frequency,
        concept="annual_average_real_gdp_growth",
        source="synthetic levels",
    ).set_index("target_period")


def test_covid_rebound_annual_gdp_uses_summed_levels():
    observations = _level_rows(
        [
            f"{year}-Q{quarter}"
            for year in (2019, 2020, 2021)
            for quarter in range(1, 5)
        ],
        [100] * 4 + [100, 50, 100, 100] + [100] * 4,
    )
    annual = _annual(observations)
    assert annual.loc["2020", "realized"] == pytest.approx(-12.5)
    # Rebound: 400 / 350 - 1 = 14.29%, while mean quarterly YoY is 25%.
    assert annual.loc["2021", "realized"] == pytest.approx(100 * (400 / 350 - 1))
    assert annual.loc["2021", "realized"] != pytest.approx(25)


def test_annual_inflation_uses_average_index_levels():
    observations = _level_rows(
        [f"{year}-{month:02d}" for year in (2020, 2021) for month in range(1, 13)],
        [50] * 6 + [100] * 6 + [100] * 12,
    )
    annual = _annual(observations, frequency="monthly")
    assert annual.loc["2021", "realized"] == pytest.approx(100 / 3)
    assert annual.loc["2021", "realized"] != pytest.approx(50)


@pytest.mark.parametrize("missing", ["2020-Q2", "2021-Q4"])
def test_annual_growth_requires_both_complete_consecutive_years(missing):
    observations = _level_rows(
        [f"{year}-Q{quarter}" for year in (2020, 2021) for quarter in range(1, 5)],
        [100] * 4 + [110] * 4,
    )
    assert _annual(observations[observations.TIME_PERIOD != missing]).empty


def test_incomplete_intervening_year_cannot_be_bridged():
    observations = _level_rows(
        [f"{year}-Q{quarter}" for year in (2019, 2021) for quarter in range(1, 5)],
        [100] * 4 + [110] * 4,
    )
    assert _annual(observations).empty


def test_annual_growth_status_includes_denominator_year():
    observations = _level_rows(
        [f"{year}-Q{quarter}" for year in (2020, 2021) for quarter in range(1, 5)],
        [100] * 4 + [110] * 4,
        ["E"] + ["A"] * 7,
    )
    assert _annual(observations).loc["2021", "observation_status"] == "A+E"


def test_duplicate_quarter_cannot_substitute_for_missing_quarter():
    observations = _level_rows(
        [f"2020-Q{q}" for q in (1, 2, 3, 4)] + [f"2021-Q{q}" for q in (1, 2, 2, 4)],
        [100] * 4 + [110] * 4,
    )
    assert _annual(observations).empty


def test_official_annual_inflation_agrees_with_index_growth_within_rounding():
    annual = load_ecb_realizations()
    for variable, first in (("hicp", 1997), ("hicpx", 2002)):
        levels = pd.read_csv(DEFAULT_RAW_DIR / f"ecb_ea_{variable}_index_monthly.csv")
        derived = _annual(levels, frequency="monthly")["realized"]
        official = annual[
            (annual.variable == variable) & annual.target_period.str.fullmatch(r"\d{4}")
        ].set_index("target_period")["realized"]
        compared = derived.to_frame("derived").join(official, how="inner")
        assert list(compared.index) == [str(year) for year in range(first, 2026)]
        assert (compared.derived - compared.realized).abs().max() <= 0.05


def _official_annual_gdp():
    annual = load_ecb_realizations()
    return annual[
        (annual.variable == "rgdp") & annual.target_period.str.fullmatch(r"\d{4}")
    ].set_index("target_period")


def test_annual_gdp_is_the_published_growth_rate_not_a_level_aggregation():
    published = _load_ecb_series(DEFAULT_RAW_DIR / "ecb_ea_rgdp_growth_annual.csv")
    published = published.set_index("TIME_PERIOD")["OBS_VALUE"]
    emitted = _official_annual_gdp()

    assert emitted.realization_concept.eq("official_annual_real_gdp_growth_rate").all()
    assert emitted.source.str.contains(OFFICIAL_ANNUAL_GDP_KEY).all()
    pd.testing.assert_series_equal(
        emitted.realized, published.loc[emitted.index], check_names=False
    )
    # The published rate is not the adjusted-level aggregation it replaces.
    adjusted = pd.read_csv(DEFAULT_RAW_DIR / "ecb_ea_rgdp_level_quarterly.csv")
    superseded = _annual(adjusted)["realized"]
    assert (superseded.loc["2004"] - emitted.realized.loc["2004"]) == pytest.approx(
        -0.2488, abs=5e-5
    )


def test_published_annual_gdp_matches_its_own_nonadjusted_quarterly_levels():
    levels = pd.read_csv(DEFAULT_RAW_DIR / "ecb_ea_rgdp_level_nsa_quarterly.csv")
    derived = _annual(levels)["realized"]
    emitted = _official_annual_gdp().realized
    compared = derived.to_frame("derived").join(emitted, how="inner")

    assert list(compared.index) == [str(year) for year in range(1996, 2026)]
    assert (compared.derived - compared.realized).abs().max() < 1e-9


def test_corrected_annual_gdp_preserves_archived_rolling_growth():
    annual = load_ecb_realizations()
    old = pd.read_csv(DEFAULT_RAW_DIR / "ecb_ea_rgdp_yoy_quarterly.csv")
    rolling = annual[
        (annual.variable == "rgdp") & annual.target_period.str.contains("Q")
    ].set_index("target_period")["realized"]
    assert rolling.to_dict() == dict(
        zip(old.TIME_PERIOD.str.replace("-", ""), old.OBS_VALUE, strict=True)
    )


def test_annual_history_retains_all_previously_available_calendar_targets():
    actual = load_ecb_realizations()
    history = load_realization_history()
    for variable, first in (("hicp", 1997), ("hicpx", 1997), ("rgdp", 1996)):
        selected = actual[
            (actual.variable == variable) & actual.target_period.str.fullmatch(r"\d{4}")
        ]
        assert selected.target_period.tolist() == [str(y) for y in range(first, 2026)]
        historical = history[
            (history.survey == "ecb_spf")
            & (history.variable == variable)
            & history.target_period.str.fullmatch(r"\d{4}")
        ]
        pd.testing.assert_frame_equal(
            selected.reset_index(drop=True), historical.reset_index(drop=True)
        )
        assert selected.source.str.contains("annual companion retrieved").all()


@pytest.mark.parametrize("corruption", ["hash", "identity", "key"])
def test_annual_source_identity_and_hash_are_verified(tmp_path: Path, corruption):
    filename = "ecb_ea_hicp_growth_annual.csv"
    key = "ICP.A.U2.N.000000.4.AVR"
    manifest = json.loads(
        (DEFAULT_RAW_DIR / "ecb_annual_realizations_sources.json").read_text()
    )
    payload = (DEFAULT_RAW_DIR / filename).read_bytes()
    if corruption == "hash":
        payload += b"\n"
    elif corruption == "identity":
        manifest["sources"][filename]["url"] = "https://example.org/wrong-series"
    else:
        payload = payload.replace(key.encode(), b"ICP.A.U2.N.XEF000.4.AVR")
        manifest["sources"][filename]["sha256"] = hashlib.sha256(payload).hexdigest()
    (tmp_path / filename).write_bytes(payload)
    (tmp_path / "ecb_annual_realizations_sources.json").write_text(json.dumps(manifest))
    with pytest.raises(ValueError, match="checksum|identity|series key"):
        _load_verified_ecb_companion(tmp_path, filename=filename, expected_key=key)


def _companion_copy(tmp_path: Path, filename: str, edit):
    """Copy the raw sources, rewrite one companion and re-pin its checksum."""
    for path in DEFAULT_RAW_DIR.glob("ecb_ea_*.csv"):
        shutil.copy(path, tmp_path / path.name)
    manifest = json.loads(
        (DEFAULT_RAW_DIR / "ecb_annual_realizations_sources.json").read_text()
    )
    path = tmp_path / filename
    edit(pd.read_csv(path)).to_csv(path, index=False)
    manifest["sources"][filename]["sha256"] = hashlib.sha256(
        path.read_bytes()
    ).hexdigest()
    (tmp_path / "ecb_annual_realizations_sources.json").write_text(json.dumps(manifest))
    return tmp_path


def test_missing_annual_companion_target_raises_instead_of_dropping_score(tmp_path):
    raw = _companion_copy(
        tmp_path,
        "ecb_ea_hicp_growth_annual.csv",
        lambda observations: observations[observations.TIME_PERIOD != 2024],
    )
    with pytest.raises(
        ValueError, match="Missing ECB hicp annual companion years.*2024"
    ):
        load_ecb_realizations(raw)


def test_annual_companion_year_published_after_the_archive_is_kept(tmp_path):
    def append_2026(observations):
        later = observations.iloc[[-1]].copy()
        later["TIME_PERIOD"] = 2026
        later["OBS_VALUE"] = 1.9
        later["OBS_STATUS"] = "P"
        return pd.concat([observations, later], ignore_index=True)

    raw = _companion_copy(tmp_path, "ecb_ea_hicp_growth_annual.csv", append_2026)
    annual = load_ecb_realizations(raw)
    calendar = annual[
        (annual.variable == "hicp") & annual.target_period.str.fullmatch(r"\d{4}")
    ].set_index("target_period")

    # The frozen rolling archive stops in 2025 and must not veto a later outcome.
    assert calendar.index.tolist() == [str(year) for year in range(1997, 2027)]
    assert calendar.loc["2026", "realized"] == pytest.approx(1.9)
    assert calendar.loc["2026", "observation_status"] == "P"


def test_pre_archive_companion_years_stay_out_of_the_outcome_history():
    annual = load_ecb_realizations()
    core = annual[
        (annual.variable == "hicpx") & annual.target_period.str.fullmatch(r"\d{4}")
    ]
    published = pd.read_csv(DEFAULT_RAW_DIR / "ecb_ea_hicpx_growth_annual.csv")

    # The official series reaches back to 1991; the monthly archive starts in 1997.
    assert published.TIME_PERIOD.min() == 1991
    assert core.target_period.min() == "1997"


def test_calendar_inflation_status_unions_the_archived_monthly_flags():
    annual = load_ecb_realizations()
    calendar = annual[annual.target_period.str.fullmatch(r"\d{4}")].set_index(
        ["variable", "target_period"]
    )["observation_status"]
    official = {
        variable: pd.read_csv(
            DEFAULT_RAW_DIR / f"ecb_ea_{variable}_growth_annual.csv",
            dtype={"TIME_PERIOD": str},
        ).set_index("TIME_PERIOD")["OBS_STATUS"]
        for variable in ("hicp", "hicpx")
    }

    # Both official 2025 observations are final while archived 2025 months are
    # estimates, and 2017 core inflation carries a series break in one month.
    assert official["hicp"].loc["2025"] == "A"
    assert official["hicpx"].loc["2025"] == "A"
    assert calendar.loc[("hicp", "2025")] == "A+E"
    assert calendar.loc[("hicpx", "2025")] == "A+E"
    assert calendar.loc[("hicpx", "2017")] == "A+B"
    assert calendar.loc[("hicp", "2024")] == "A"
    # GDP statuses come from the published annual series; its archive is final.
    assert calendar.loc[("rgdp", "1996")] == "A"


def test_blank_observation_status_is_rejected(tmp_path: Path):
    path = tmp_path / "blank_status.csv"
    path.write_text("TIME_PERIOD,OBS_VALUE,OBS_STATUS\n2024,1.0,A\n2025,1.5, \n")
    with pytest.raises(ValueError, match="Missing ECB observation status"):
        _load_ecb_series(path)
