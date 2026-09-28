"""Rules that turn published monthly data into annual and fourth-quarter outcomes.

Example tests pin each rule on a hand-built case; property tests check that the
rule holds for every generated pattern of published, not-collected and absent
months.
"""

from __future__ import annotations

import json
from datetime import date, timedelta

import numpy as np
import pandas as pd
import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from expectations.outcome_sources import (
    certainly_published,
    check_publication_currency,
    latest_certainly_published,
    load_bls_file,
    period_end,
)
from expectations.realizations import annual_unemployment_rates, q4_over_q4_growth

NOT_COLLECTED = "Data unavailable due to the 2025 lapse in appropriations."
ANNUAL_NOTE = (
    "Annual estimates for 2025 are 11-month averages that exclude October. "
    "Data for October 2025 were not collected due to the federal government "
    "shutdown."
)


def _bls_document(series_id, months, annual=None):
    """Build a BLS API document; ``months`` maps (year, month) to value or '-'."""
    data = []
    for (year, month), value in sorted(months.items()):
        footnotes = [{"code": "X", "text": NOT_COLLECTED}] if value == "-" else [{}]
        data.append(
            {
                "year": str(year),
                "period": f"M{month:02d}",
                "periodName": "",
                "value": value if value == "-" else f"{value}",
                "footnotes": footnotes,
            }
        )
    for year, (value, note) in sorted((annual or {}).items()):
        data.append(
            {
                "year": str(year),
                "period": "M13",
                "periodName": "Annual",
                "value": f"{value}",
                "footnotes": [{"text": note}] if note else [{}],
            }
        )
    return load_bls_file(
        json.dumps({"series_id": series_id, "data": data}).encode("utf-8")
    )


def _year(year, values):
    return {(year, month): value for month, value in enumerate(values, start=1)}


# ---------------------------------------------------------------- examples


def test_year_with_one_month_not_collected_takes_the_official_annual_average():
    """The 2025 case: October never collected, BLS averages the other eleven."""
    months = {
        **_year(2024, [3.7, 3.9, 3.9, 3.9, 4.0, 4.1, 4.2, 4.2, 4.1, 4.1, 4.2, 4.1]),
        **_year(2025, [4.0, 4.2, 4.2, 4.2, 4.3, 4.1, 4.3, 4.3, 4.4, "-", 4.5, 4.4]),
    }
    monthly = _bls_document("LNS14000000", months)
    official = _bls_document(
        "LNU04000000", {}, {2024: (4.0, ""), 2025: (4.3, ANNUAL_NOTE)}
    )
    rates = annual_unemployment_rates(monthly, official)

    assert rates.index.tolist() == ["2024", "2025"]
    # A complete year keeps its monthly mean even though an official one exists.
    assert rates.loc["2024", "realized"] == pytest.approx(
        np.mean(list(months.values())[:12])
    )
    assert rates.loc["2024", "source"] == "BLS LNS14000000 (latest vintage)"
    assert rates.loc["2025", "realized"] == 4.3
    assert "LNU04000000 official annual average" in rates.loc["2025", "source"]
    assert "did not collect 2025-10" in rates.loc["2025", "source"]
    assert "11-month averages that exclude October" in rates.loc["2025", "source"]


def test_year_with_a_missing_month_waits_for_the_official_average():
    months = _year(2025, [4.0] * 9 + ["-", 4.5, 4.4])
    monthly = _bls_document("LNS14000000", months)
    assert annual_unemployment_rates(monthly, _bls_document("LNU04000000", {})).empty


def test_year_still_in_progress_has_no_outcome():
    monthly = _bls_document("LNS14000000", _year(2026, [4.3] * 8))
    assert annual_unemployment_rates(monthly, _bls_document("LNU04000000", {})).empty


def test_official_average_with_an_unexplained_gap_raises():
    """A truncated monthly file must not make a published year vanish."""
    months = _year(2025, [4.0] * 11)  # December simply absent
    monthly = _bls_document("LNS14000000", months)
    official = _bls_document("LNU04000000", {}, {2025: (4.3, ANNUAL_NOTE)})
    with pytest.raises(ValueError, match=r"lacks months \[12\]"):
        annual_unemployment_rates(monthly, official)


def test_blank_bls_value_needs_a_footnote():
    payload = {
        "series_id": "LNS14000000",
        "data": [{"year": "2025", "period": "M10", "value": "-", "footnotes": [{}]}],
    }
    with pytest.raises(ValueError, match="blank without a footnote"):
        load_bls_file(json.dumps(payload).encode())


def test_duplicate_bls_period_is_rejected():
    point = {"year": "2025", "period": "M01", "value": "4.0", "footnotes": [{}]}
    payload = {"series_id": "LNS14000000", "data": [point, point]}
    with pytest.raises(ValueError, match="Duplicate BLS observation"):
        load_bls_file(json.dumps(payload).encode())


def _monthly_index(values):
    return pd.Series(values, dtype=float)


def test_not_collected_october_is_filled_from_its_neighbours():
    index = {f"2024-{month:02d}": 100.0 + month for month in range(1, 13)}
    index |= {f"2025-{month:02d}": 110.0 + month for month in range(1, 13)}
    del index["2025-10"]
    growth = q4_over_q4_growth(
        _monthly_index(index), not_collected=frozenset({"2025-10"})
    )
    q4_2024 = np.mean([110.0, 111.0, 112.0])
    q4_2025 = np.mean([(119.0 + 121.0) / 2, 121.0, 122.0])
    assert growth.loc["2025", "realized"] == pytest.approx(
        100 * (q4_2025 / q4_2024 - 1)
    )
    assert growth.loc["2025", "filled_months"] == ("2025-10",)


def test_absent_fourth_quarter_month_is_never_filled():
    index = {
        f"{year}-{month:02d}": 100.0 for year in (2024, 2025) for month in range(1, 13)
    }
    del index["2025-10"]
    growth = q4_over_q4_growth(_monthly_index(index))
    assert "2025" not in growth.index


def test_not_collected_month_needs_both_neighbours():
    index = {f"2024-{month:02d}": 100.0 for month in range(1, 13)}
    index |= {"2025-10": 101.0, "2025-11": 101.0}
    growth = q4_over_q4_growth(
        _monthly_index(index), not_collected=frozenset({"2025-12"})
    )
    assert "2025" not in growth.index


def test_stale_mirror_is_caught_by_publication_currency():
    """The failure this guard exists for: a mirror frozen at January 2025."""
    frozen = {
        "bls_ln_LNS14000000_monthly.json": {
            "last_period": "2025-01",
            "retrieved_at_utc": "2026-03-14T02:13:43+00:00",
        }
    }
    specification = {
        "bls_ln_LNS14000000_monthly.json": {"frequency": "monthly", "lag_days": 60}
    }
    problems = check_publication_currency(frozen, specification)
    assert len(problems) == 1
    assert "ends at 2025-01, but 2025-12 was published" in problems[0]


@pytest.mark.parametrize(
    "period, expected",
    [
        ("2025", date(2025, 12, 31)),
        ("2025-02", date(2025, 2, 28)),
        ("2024-02", date(2024, 2, 29)),
        ("2025-Q3", date(2025, 9, 30)),
        ("2026Q2", date(2026, 6, 30)),
        ("2026Jun", date(2026, 6, 30)),
    ],
)
def test_period_end(period, expected):
    assert period_end(period) == expected


def test_latest_certainly_published_examples():
    as_of = date(2026, 9, 28)
    assert latest_certainly_published("annual", lag_days=60, as_of=as_of) == "2025"
    assert latest_certainly_published("monthly", lag_days=60, as_of=as_of) == "2026-06"
    assert (
        latest_certainly_published("quarterly", lag_days=90, as_of=as_of) == "2026-Q2"
    )
    assert (
        latest_certainly_published("quarterly", lag_days=91, as_of=as_of) == "2026-Q1"
    )


# ---------------------------------------------------------------- properties

MONTH_STATE = st.sampled_from(["published", "not_collected", "absent"])


@st.composite
def unemployment_years(draw):
    """Per-year month states, values and whether BLS published an annual mean."""
    years = {}
    for year in range(2020, 2020 + draw(st.integers(1, 4))):
        states = draw(st.lists(MONTH_STATE, min_size=12, max_size=12))
        values = draw(
            st.lists(
                st.floats(2.0, 15.0, allow_nan=False).map(lambda x: round(x, 1)),
                min_size=12,
                max_size=12,
            )
        )
        official = draw(st.none() | st.floats(2.0, 15.0).map(lambda x: round(x, 1)))
        years[year] = (states, values, official)
    return years


@settings(max_examples=300, deadline=None)
@given(unemployment_years())
def test_annual_unemployment_rule_holds_for_every_month_pattern(years):
    months, annual = {}, {}
    for year, (states, values, official) in years.items():
        for month, (state, value) in enumerate(zip(states, values, strict=True), 1):
            if state == "published":
                months[(year, month)] = value
            elif state == "not_collected":
                months[(year, month)] = "-"
        if official is not None:
            annual[year] = (official, "")
    monthly = _bls_document("LNS14000000", months)
    official_series = _bls_document("LNU04000000", {}, annual)

    unexplained = [
        year
        for year, (states, _, official) in years.items()
        if official is not None
        and "published" in states  # a year BLS knows about
        and states.count("published") < 12
        and "absent" in states
    ] + [
        year
        for year, (states, _, official) in years.items()
        if official is not None
        and "published" not in states
        and "not_collected" in states
        and "absent" in states
    ]
    if unexplained:
        with pytest.raises(ValueError, match="lacks months"):
            annual_unemployment_rates(monthly, official_series)
        return
    rates = annual_unemployment_rates(monthly, official_series)

    for year, (states, values, official) in years.items():
        key = str(year)
        known = "published" in states or "not_collected" in states
        if states.count("published") == 12:
            assert rates.loc[key, "realized"] == pytest.approx(np.mean(values))
        elif known and official is not None:
            assert rates.loc[key, "realized"] == official
            assert "did not collect" in rates.loc[key, "source"]
        else:
            assert key not in rates.index


@st.composite
def price_indexes(draw):
    """A positive monthly index over consecutive years with some months missing."""
    first = draw(st.integers(2000, 2020))
    count = draw(st.integers(2, 4))
    periods = [
        f"{year}-{month:02d}"
        for year in range(first, first + count)
        for month in range(1, 13)
    ]
    values = draw(
        st.lists(
            st.floats(50.0, 500.0, allow_nan=False),
            min_size=len(periods),
            max_size=len(periods),
        )
    )
    states = draw(
        st.lists(
            st.sampled_from(["published"] * 6 + ["not_collected", "absent"]),
            min_size=len(periods),
            max_size=len(periods),
        )
    )
    return periods, values, states


def _reference_q4_growth(index: dict[str, float]) -> dict[str, float]:
    """Independent reference: a pandas quarterly resample of complete quarters."""
    series = pd.Series(index)
    series.index = pd.PeriodIndex(series.index, freq="M")
    quarterly = series.groupby(series.index.asfreq("Q")).agg(["mean", "count"])
    q4 = quarterly[(quarterly.index.quarter == 4) & (quarterly["count"] == 3)]["mean"]
    q4.index = q4.index.year
    return {
        str(year): 100 * (value / q4[year - 1] - 1)
        for year, value in q4.items()
        if year - 1 in q4.index
    }


@settings(max_examples=300, deadline=None)
@given(price_indexes(), st.floats(0.01, 100.0))
def test_q4_growth_rule_holds_for_every_month_pattern(generated, scale):
    periods, values, states = generated
    published = {
        period: value
        for period, value, state in zip(periods, values, states, strict=True)
        if state == "published"
    }
    not_collected = frozenset(
        period
        for period, state in zip(periods, states, strict=True)
        if state == "not_collected"
    )
    growth = q4_over_q4_growth(pd.Series(published), not_collected=not_collected)

    # Filling exactly the eligible months reproduces the independent reference.
    completed = dict(published)
    for period in not_collected:
        month = pd.Period(period, freq="M")
        before, after = str(month - 1), str(month + 1)
        if month.month in (10, 11, 12) and before in published and after in published:
            completed[period] = (published[before] + published[after]) / 2
    reference = _reference_q4_growth(completed)
    assert set(growth.index) == set(reference)
    for year, value in reference.items():
        assert growth.loc[year, "realized"] == pytest.approx(value, rel=1e-9, abs=1e-9)
        filled = set(growth.loc[year, "filled_months"])
        assert filled <= not_collected
        assert all(month[:4] in {year, str(int(year) - 1)} for month in filled)

    # Growth rates do not depend on the index base.
    rescaled = q4_over_q4_growth(
        pd.Series(published) * scale, not_collected=not_collected
    )
    pd.testing.assert_series_equal(
        rescaled["realized"], growth["realized"], rtol=1e-9, atol=1e-9
    )


@settings(max_examples=300, deadline=None)
@given(
    st.dates(date(1990, 1, 1), date(2040, 12, 31)),
    st.integers(0, 400),
    st.sampled_from(["annual", "quarterly", "monthly"]),
)
def test_latest_certainly_published_is_the_maximal_published_period(
    as_of, lag, frequency
):
    latest = latest_certainly_published(frequency, lag_days=lag, as_of=as_of)
    assert certainly_published(latest, lag_days=lag, as_of=as_of)

    step = {"annual": "Y", "quarterly": "Q", "monthly": "M"}[frequency]
    following = pd.Period(latest.replace("-Q", "Q"), freq=step) + 1
    label = {
        "annual": str(following.year),
        "quarterly": f"{following.year}-Q{following.quarter}" if step == "Q" else "",
        "monthly": f"{following.year}-{following.month:02d}" if step == "M" else "",
    }[frequency]
    assert not certainly_published(label, lag_days=lag, as_of=as_of)
    # A later snapshot never requires less.
    later = latest_certainly_published(
        frequency, lag_days=lag, as_of=as_of + timedelta(days=1)
    )
    assert period_end(later) >= period_end(latest)
