"""Where each outcome series comes from, and when it must be current.

This module holds the provenance side of the outcomes: the archived source files,
the manifests that date and checksum them, a parser for BLS API documents, and
the publication bounds that decide whether a snapshot has fallen behind its
publisher. How an outcome is computed from these files lives in
:mod:`expectations.realizations`.
"""

from __future__ import annotations

import calendar
import hashlib
import json
import re
from collections.abc import Mapping
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

DEFAULT_RAW_DIR = Path(__file__).resolve().parents[2] / "data" / "raw"

_MONTH_NUMBERS = {
    name.lower(): index for index, name in enumerate(calendar.month_abbr) if index
}

US_OUTCOME_MANIFEST = "us_realizations_sources.json"
BLS_API_URL = "https://api.bls.gov/publicAPI/v2/timeseries/data/"

# Every US outcome file, its publisher and the latest period it must contain.
# ``lag_days`` is a deliberately generous bound on how long after a period ends
# its publisher has released it: well beyond the usual lag of a few weeks, with
# room for delays like those after the 2025 lapse in appropriations (BLS released
# September 2025 employment data on November 20, 51 days after the month ended).
# The bounds therefore say when an outcome must be present, not when it first
# appears, and a snapshot that misses one has fallen behind its publisher.
US_OUTCOME_SOURCES: dict[str, dict[str, Any]] = {
    "bls_ln_LNS14000000_monthly.json": {
        "provider": "bls",
        "series_id": "LNS14000000",
        "first_year": 1948,
        "frequency": "monthly",
        "lag_days": 60,
        "role": "civilian unemployment rate, seasonally adjusted, monthly",
    },
    "bls_ln_LNU04000000_annual.json": {
        "provider": "bls",
        "series_id": "LNU04000000",
        "first_year": 1948,
        "frequency": "annual",
        "lag_days": 60,
        "role": (
            "civilian unemployment rate, not seasonally adjusted; read only for "
            "BLS's official annual averages (period M13)"
        ),
    },
    "bls_cu_CUSR0000SA0L1E_monthly.json": {
        "provider": "bls",
        "series_id": "CUSR0000SA0L1E",
        "first_year": 1957,
        "frequency": "monthly",
        "lag_days": 60,
        "role": "CPI-U less food and energy, seasonally adjusted, monthly index",
    },
    "dbnomics_us_rgdp_growth_annual.json": {
        "provider": "dbnomics",
        "series": "BEA/NIPA-T10101/A191RL-A",
        "bea_series": "A191RL",
        "bea_frequency": "A",
        "frequency": "annual",
        "lag_days": 90,
        "role": "real GDP, annual percent change",
    },
    "dbnomics_us_gdp_price_index_annual.json": {
        "provider": "dbnomics",
        "series": "BEA/NIPA-T10104/A191RG-A",
        "bea_series": "A191RG",
        "bea_frequency": "A",
        "frequency": "annual",
        "lag_days": 90,
        "role": "GDP chain-type price index, annual level",
    },
    "dbnomics_us_rgdp_growth_quarterly.json": {
        "provider": "dbnomics",
        "series": "BEA/NIPA-T10101/A191RL-Q",
        "bea_series": "A191RL",
        "bea_frequency": "Q",
        "frequency": "quarterly",
        "lag_days": 90,
        "role": "real GDP, quarterly percent change at an annual rate",
    },
    "dbnomics_us_corepce_price_monthly.json": {
        "provider": "dbnomics",
        "series": "BEA/NIPA-T20804/DPCCRG-M",
        "bea_series": "DPCCRG",
        "bea_frequency": "M",
        "frequency": "monthly",
        "lag_days": 90,
        "role": "PCE price index excluding food and energy, monthly level",
    },
}


@dataclass(frozen=True)
class BlsSeries:
    """One BLS series as archived from the BLS Public Data API.

    ``unavailable_months`` are months BLS publishes as ``-`` with a footnote: a
    month BLS says it did not collect, as opposed to one not yet released.
    """

    series_id: str
    monthly: Mapping[tuple[int, int], float]
    unavailable_months: tuple[tuple[int, int], ...]
    annual_averages: Mapping[str, float]
    annual_notes: Mapping[str, str]

    def monthly_series(self) -> pd.Series:
        """Published monthly values indexed by ``YYYY-MM``."""
        return pd.Series(
            {
                f"{year}-{month:02d}": value
                for (year, month), value in self.monthly.items()
            },
            dtype=float,
        ).sort_index()

    def monthly_periods(self) -> list[str]:
        return list(self.monthly_series().index)

    def unavailable_periods(self) -> frozenset[str]:
        return frozenset(
            f"{year}-{month:02d}" for year, month in self.unavailable_months
        )

    def complete_year_means(self) -> dict[str, float]:
        """Mean of the twelve published months, for each complete year."""
        years: dict[int, list[float]] = {}
        for (year, _), value in self.monthly.items():
            years.setdefault(year, []).append(value)
        return {
            str(year): float(np.mean(values))
            for year, values in sorted(years.items())
            if len(values) == 12
        }


def load_bls_file(payload: bytes) -> BlsSeries:
    """Parse an archived BLS API document, rejecting anything ambiguous.

    A value of ``-`` is accepted only with a footnote, and is recorded as a month
    BLS did not collect; every other value must be numeric. Annual averages
    (period ``M13``) keep BLS's footnote, which states how BLS computed them.
    """
    document = json.loads(payload.decode("utf-8"))
    series_id = document["series_id"]
    monthly: dict[tuple[int, int], float] = {}
    unavailable: list[tuple[int, int]] = []
    annual: dict[str, float] = {}
    notes: dict[str, str] = {}
    seen: set[tuple[str, str]] = set()
    for point in document["data"]:
        year, period, value = str(point["year"]), point["period"], point["value"]
        if (year, period) in seen:
            raise ValueError(f"Duplicate BLS observation {series_id} {year} {period}")
        seen.add((year, period))
        match = re.fullmatch(r"M(\d{2})", period)
        if not re.fullmatch(r"\d{4}", year) or match is None:
            raise ValueError(f"Unexpected BLS period {series_id} {year} {period}")
        position = int(match.group(1))
        footnotes = "; ".join(
            note["text"] for note in point.get("footnotes", []) if note.get("text")
        )
        if position == 13:
            annual[year] = float(value)
            if footnotes:
                notes[year] = footnotes
            continue
        if not 1 <= position <= 12:
            raise ValueError(f"Unexpected BLS period {series_id} {year} {period}")
        if value.strip() == "-":
            if not footnotes:
                raise ValueError(
                    f"BLS {series_id} {year} {period} is blank without a footnote"
                )
            unavailable.append((int(year), position))
            continue
        monthly[(int(year), position)] = float(value)
    return BlsSeries(
        series_id=series_id,
        monthly=dict(sorted(monthly.items())),
        unavailable_months=tuple(sorted(unavailable)),
        annual_averages=dict(sorted(annual.items())),
        annual_notes=notes,
    )


def dbnomics_series_url(series: str) -> str:
    """DBnomics API address for one ``provider/dataset/series`` code."""
    return (
        f"https://api.db.nomics.world/v22/series/{series}"
        "?observations=1&metadata=true&format=json"
    )


def load_dbnomics_file(payload: bytes, *, label: str = "payload") -> pd.Series:
    """Parse one archived DBnomics series response into a period-indexed series."""
    return _parse_dbnomics(json.loads(payload.decode("utf-8")), label=label)


def period_end(period: str) -> date:
    """Last calendar day of an outcome period (``YYYY``, ``YYYY-MM``, ``YYYY-Qn``,
    ``YYYYQn`` or ``YYYYMon``)."""
    text = str(period)
    if re.fullmatch(r"\d{4}", text):
        return date(int(text), 12, 31)
    if match := re.fullmatch(r"(\d{4})-?Q([1-4])", text):
        year, month = int(match.group(1)), 3 * int(match.group(2))
    elif match := re.fullmatch(r"(\d{4})-(\d{2})", text):
        year, month = int(match.group(1)), int(match.group(2))
    elif (match := re.fullmatch(r"(\d{4})([A-Za-z]{3})", text)) and (
        match.group(2).lower() in _MONTH_NUMBERS
    ):
        year, month = int(match.group(1)), _MONTH_NUMBERS[match.group(2).lower()]
    else:
        raise ValueError(f"Unrecognized outcome period: {period}")
    return date(year, month, calendar.monthrange(year, month)[1])


def certainly_published(period: str, *, lag_days: int, as_of: date) -> bool:
    """Whether ``period`` ended at least ``lag_days`` before ``as_of``."""
    return period_end(period) + timedelta(days=lag_days) <= as_of


def latest_certainly_published(frequency: str, *, lag_days: int, as_of: date) -> str:
    """The most recent period of ``frequency`` its publisher has surely released."""
    cutoff = as_of - timedelta(days=lag_days)
    if frequency == "annual":
        year = cutoff.year if cutoff >= date(cutoff.year, 12, 31) else cutoff.year - 1
        return str(year)
    month = pd.Period(cutoff, freq="M")
    if cutoff != period_end(f"{month.year}-{month.month:02d}"):
        month -= 1
    if frequency == "monthly":
        return f"{month.year}-{month.month:02d}"
    if frequency == "quarterly":
        quarter = month.asfreq("Q")
        if month.month % 3:
            quarter -= 1
        return f"{quarter.year}-Q{quarter.quarter}"
    raise ValueError(f"Unknown frequency: {frequency}")


def check_publication_currency(
    sources: Mapping[str, Mapping[str, Any]],
    specifications: Mapping[str, Mapping[str, Any]] = US_OUTCOME_SOURCES,
) -> list[str]:
    """Name each source that stops before a period its publisher has released.

    ``sources`` are manifest entries carrying ``last_period`` and
    ``retrieved_at_utc``. A mirror that stopped updating, like the DBnomics BLS
    provider, fails here instead of silently shortening the outcome history.
    """
    problems: list[str] = []
    for filename, specification in specifications.items():
        entry = sources.get(filename)
        if entry is None:
            problems.append(f"{filename}: missing from the manifest")
            continue
        as_of = datetime.fromisoformat(entry["retrieved_at_utc"]).date()
        required = latest_certainly_published(
            specification["frequency"],
            lag_days=specification["lag_days"],
            as_of=as_of,
        )
        if period_end(entry["last_period"]) < period_end(required):
            problems.append(
                f"{filename}: ends at {entry['last_period']}, but {required} was "
                f"published more than {specification['lag_days']} days before "
                f"its retrieval on {as_of}"
            )
    return problems


ECB_OUTCOME_MANIFEST = "ecb_annual_realizations_sources.json"

# For every outcome series: the manifest that dates its snapshot, the files it is
# built from, and the publication bound (days after a period ends) described at
# ``US_OUTCOME_SOURCES``. ``annual`` covers calendar-year targets and
# ``rolling`` month and quarter targets. HICP dates come from the ECOICOP v2
# successor files, which carry every period after the legacy series ends. The
# euro-area GDP bound is the widest: on September 28, 2026 the ECB series still
# ended at 2026Q1, 90 days after the second quarter closed.
OUTCOME_SNAPSHOTS: dict[tuple[str, str, str], tuple[str, tuple[str, ...], int]] = {
    ("us_spf", "prunemp", "annual"): (
        US_OUTCOME_MANIFEST,
        ("bls_ln_LNS14000000_monthly.json", "bls_ln_LNU04000000_annual.json"),
        60,
    ),
    ("us_spf", "prccpi", "annual"): (
        US_OUTCOME_MANIFEST,
        ("bls_cu_CUSR0000SA0L1E_monthly.json",),
        60,
    ),
    ("us_spf", "prcpce", "annual"): (
        US_OUTCOME_MANIFEST,
        ("dbnomics_us_corepce_price_monthly.json",),
        90,
    ),
    ("us_spf", "prgdp", "annual"): (
        US_OUTCOME_MANIFEST,
        ("dbnomics_us_rgdp_growth_annual.json",),
        90,
    ),
    ("us_spf", "prpgdp", "annual"): (
        US_OUTCOME_MANIFEST,
        ("dbnomics_us_gdp_price_index_annual.json",),
        90,
    ),
    ("us_spf", "recess", "rolling"): (
        US_OUTCOME_MANIFEST,
        ("dbnomics_us_rgdp_growth_quarterly.json",),
        90,
    ),
    ("ecb_spf", "hicp", "rolling"): (
        ECB_OUTCOME_MANIFEST,
        ("ecb_ea_hicp_yoy_monthly_ecoicop2.csv",),
        60,
    ),
    ("ecb_spf", "hicp", "annual"): (
        ECB_OUTCOME_MANIFEST,
        ("ecb_ea_hicp_growth_annual_ecoicop2.csv",),
        60,
    ),
    ("ecb_spf", "hicpx", "rolling"): (
        ECB_OUTCOME_MANIFEST,
        ("ecb_ea_hicpx_yoy_monthly_ecoicop2.csv",),
        60,
    ),
    ("ecb_spf", "hicpx", "annual"): (
        ECB_OUTCOME_MANIFEST,
        ("ecb_ea_hicpx_growth_annual_ecoicop2.csv",),
        60,
    ),
    ("ecb_spf", "rgdp", "rolling"): (
        ECB_OUTCOME_MANIFEST,
        ("ecb_ea_rgdp_yoy_quarterly.csv",),
        150,
    ),
    ("ecb_spf", "rgdp", "annual"): (
        ECB_OUTCOME_MANIFEST,
        ("ecb_ea_rgdp_growth_annual.csv",),
        150,
    ),
    ("ecb_spf", "unemp", "rolling"): (
        ECB_OUTCOME_MANIFEST,
        ("ecb_ea_unemployment_monthly.csv",),
        60,
    ),
    ("ecb_spf", "unemp", "annual"): (
        ECB_OUTCOME_MANIFEST,
        ("ecb_ea_unemployment_monthly.csv",),
        60,
    ),
}


def outcome_snapshots(
    raw_dir: str | Path = DEFAULT_RAW_DIR,
) -> dict[tuple[str, str, str], dict[str, Any]]:
    """Snapshot date, first period and publication bound of every outcome series.

    The date is the earliest retrieval date among the series' files. A rolling
    ECB archive whose retrieval went unrecorded uses the date of the commit that
    added it, an upper bound. Each file's checksum must match its manifest entry,
    so a date always describes the bytes on disk.
    """
    directory = Path(raw_dir)
    manifests: dict[str, dict[str, Any]] = {}
    snapshots: dict[tuple[str, str, str], dict[str, Any]] = {}
    for key, (manifest_name, filenames, lag_days) in OUTCOME_SNAPSHOTS.items():
        if manifest_name not in manifests:
            manifests[manifest_name] = json.loads(
                (directory / manifest_name).read_text()
            )
        manifest = manifests[manifest_name]
        dates: list[date] = []
        first_periods: list[str] = []
        for filename in filenames:
            entry = manifest["sources"].get(filename) or manifest.get(
                "rolling_archives", {}
            ).get(filename)
            if entry is None:
                raise ValueError(f"{filename} is missing from {manifest_name}")
            payload = (directory / filename).read_bytes()
            if hashlib.sha256(payload).hexdigest() != entry["sha256"]:
                raise ValueError(f"{filename} does not match its {manifest_name} entry")
            stamp = entry.get("retrieved_at_utc") or entry["retrieved_no_later_than"]
            dates.append(datetime.fromisoformat(stamp).date())
            first_periods.append(entry["first_period"])
        snapshots[key] = {
            "as_of": min(dates),
            "first_period": max(first_periods, key=period_end),
            "lag_days": lag_days,
        }
    return snapshots


def _parse_dbnomics(payload: dict[str, Any], *, label: str) -> pd.Series:
    try:
        documents = payload["series"]["docs"]
        document = documents[0]
        periods = document["period"]
        values = document["value"]
    except (KeyError, IndexError, TypeError) as error:
        raise ValueError(f"Unexpected DBnomics structure in {label}") from error
    if len(documents) != 1 or len(periods) != len(values):
        raise ValueError(f"Invalid DBnomics series dimensions in {label}")
    if len(periods) != len(set(periods)):
        raise ValueError(f"Duplicate DBnomics periods in {label}")
    numeric = pd.to_numeric(pd.Series(values, index=pd.Index(periods)), errors="coerce")
    if numeric.isna().any():
        bad = numeric.index[numeric.isna()].tolist()
        raise ValueError(f"Missing or nonnumeric DBnomics values in {label}: {bad}")
    return numeric.astype(float).sort_index()


__all__ = [
    "BLS_API_URL",
    "ECB_OUTCOME_MANIFEST",
    "OUTCOME_SNAPSHOTS",
    "US_OUTCOME_MANIFEST",
    "US_OUTCOME_SOURCES",
    "BlsSeries",
    "certainly_published",
    "check_publication_currency",
    "dbnomics_series_url",
    "latest_certainly_published",
    "load_bls_file",
    "load_dbnomics_file",
    "outcome_snapshots",
    "period_end",
]
