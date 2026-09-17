"""Acquire annual-outcome companion sources without replacing rolling snapshots.

Run from the repository root with ``python scripts/download_ecb_annual_realizations.py``.
The legacy ICP series match the existing rolling files' classification/geography;
they stop in December 2025. New HICP flow observations are intentionally not spliced
into these archived series. Retrieval time is not an economic vintage identifier.

Sources already present with the recorded checksum are reused rather than
re-downloaded, so adding a companion never silently re-vintages the others.
``--refresh`` downloads every source again. Each manifest entry carries its own
retrieval time; the top-level time is only the most recent acquisition run.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
from collections import defaultdict
from datetime import UTC, datetime
from pathlib import Path
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
MANIFEST = RAW / "ecb_annual_realizations_sources.json"
SOURCES = {
    "ecb_ea_rgdp_growth_annual.csv": (
        "MNA.A.N.I9.W2.S1.S1.B.B1GQ._Z._Z._Z.EUR_R_B1GQ.Y.GOY"
    ),
    "ecb_ea_rgdp_level_quarterly.csv": "MNA.Q.Y.I9.W2.S1.S1.B.B1GQ._Z._Z._Z.EUR.LR.N",
    "ecb_ea_rgdp_level_nsa_quarterly.csv": (
        "MNA.Q.N.I9.W2.S1.S1.B.B1GQ._Z._Z._Z.EUR.LR.N"
    ),
    "ecb_ea_hicp_index_monthly.csv": "ICP.M.U2.N.000000.4.INX",
    "ecb_ea_hicpx_index_monthly.csv": "ICP.M.U2.N.XEF000.4.INX",
    "ecb_ea_hicp_growth_annual.csv": "ICP.A.U2.N.000000.4.AVR",
    "ecb_ea_hicpx_growth_annual.csv": "ICP.A.U2.N.XEF000.4.AVR",
}
METADATA_COLUMNS = (
    "TITLE",
    "TITLE_COMPL",
    "COMMENT_TS",
    "REF_AREA",
    "ADJUSTMENT",
    "FREQ",
    "UNIT",
    "UNIT_MEASURE",
    "UNIT_MULT",
    "UNIT_INDEX_BASE",
    "REF_YEAR_PRICE",
    "DECIMALS",
    "LAST_UPDATE",
)
NOTES = [
    (
        "Annual real GDP growth is the official ECB annual growth rate "
        "(MNA ... EUR_R_B1GQ.Y.GOY, titled 'Gross domestic product at market "
        "prices, annual growth rate'), non-adjusted, previous-year prices, fixed "
        "EA20 composition. It replaces growth in sums of "
        "calendar-and-seasonally-adjusted quarterly levels, which is not the "
        "published annual rate."
    ),
    (
        "Verification records that the official annual rate equals growth in "
        "sums of the non-adjusted quarterly levels, and how far the superseded "
        "adjusted-level sums departed from it."
    ),
    (
        "The ECB annual rate is not identical to Eurostat's published EA20 "
        "annual growth (nama_10_gdp, B1GQ, CLV_PCH_PRE); verification records "
        "the year-by-year deviation and the years that differ at one decimal. "
        "Both are official publications of different aggregates, so neither is "
        "a rounding of the other."
    ),
    "Annual HICP and HICPX use official annual-average index growth (AVR), rounded by the publisher to 0.1 percentage point; not mean monthly year-on-year growth.",
    "Monthly HICP indexes are retained to verify annual growth wherever both full years exist. HICPX index months are missing in 1997–2000; published annual AVR avoids losing those calendar benchmark targets.",
    "Existing rolling raw files are preserved. Their original retrieval dates are unrecorded; do not infer identical vintages from this companion retrieval date.",
    "GDP companion level implied quarterly year-on-year growth is compared with the archived rolling values in verification; retrieval date alone does not establish vintage equality.",
    "Calendar inflation values are the official annual observations. Their emitted status is the union of the official annual status and the archived subannual statuses for the same year, so a provisional month is not hidden by a final annual flag.",
    "Legacy ICP flow is discontinued; the new HICP flow is not spliced into this 1997–2025 outcome history.",
]
EUROSTAT_ANNUAL_GROWTH_URL = (
    "https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/"
    "nama_10_gdp?format=JSON&geo=EA20&na_item=B1GQ&unit=CLV_PCH_PRE"
)


def _rows(payload: bytes) -> list[dict[str, str]]:
    return list(csv.DictReader(io.StringIO(payload.decode("utf-8-sig"))))


def _values(payload: bytes) -> dict[str, float]:
    return {row["TIME_PERIOD"]: float(row["OBS_VALUE"]) for row in _rows(payload)}


def _annual_sums(levels: dict[str, float]) -> dict[str, float]:
    grouped: dict[str, dict[str, float]] = defaultdict(dict)
    for period, level in levels.items():
        grouped[period[:4]][period[5:]] = level
    return {
        year: sum(quarters.values())
        for year, quarters in grouped.items()
        if set(quarters) == {"Q1", "Q2", "Q3", "Q4"}
    }


def _growth(annual: dict[str, float]) -> dict[str, float]:
    return {
        year: 100 * (value / annual[str(int(year) - 1)] - 1)
        for year, value in annual.items()
        if str(int(year) - 1) in annual
    }


def _deviation_summary(
    left: dict[str, float], right: dict[str, float]
) -> dict[str, object]:
    shared = sorted(set(left) & set(right))
    deviations = {year: abs(left[year] - right[year]) for year in shared}
    rounded = [year for year in shared if round(left[year], 1) != round(right[year], 1)]
    return {
        "matched_years": len(shared),
        "first_year": shared[0],
        "last_year": shared[-1],
        "mean_absolute_difference_pp": sum(deviations.values()) / len(deviations),
        "max_absolute_difference_pp": max(deviations.values()),
        "max_absolute_difference_year": max(deviations, key=deviations.__getitem__),
        "years_differing_at_one_decimal": rounded,
    }


def _eurostat_annual_growth() -> dict[str, float]:
    request = Request(
        EUROSTAT_ANNUAL_GROWTH_URL,
        headers={"User-Agent": "forecast-uncertainty-research/1"},
    )
    with urlopen(request, timeout=45) as response:
        payload = json.loads(response.read().decode("utf-8"))
    periods = {
        position: period
        for period, position in payload["dimension"]["time"]["category"][
            "index"
        ].items()
    }
    return {periods[int(key)]: float(value) for key, value in payload["value"].items()}


def verify_companions(acquired: dict[str, bytes]) -> dict:
    verification = {}
    official = _values(acquired["ecb_ea_rgdp_growth_annual.csv"])
    title = _rows(acquired["ecb_ea_rgdp_growth_annual.csv"])[0]["TITLE"]
    if "annual growth rate" not in title.lower():
        raise ValueError(f"Annual GDP companion is not a growth rate: {title!r}")

    adjusted = _values(acquired["ecb_ea_rgdp_level_quarterly.csv"])
    rolling_path = RAW / "ecb_ea_rgdp_yoy_quarterly.csv"
    rolling = _values(rolling_path.read_bytes())
    differences = [
        abs(
            100 * (level / adjusted[f"{int(period[:4]) - 1}{period[4:]}"] - 1)
            - rolling[period]
        )
        for period, level in adjusted.items()
        if f"{int(period[:4]) - 1}{period[4:]}" in adjusted and period in rolling
    ]
    verification["rgdp_quarterly_yoy_vs_archived_rolling"] = {
        "matched_periods": len(differences),
        "max_absolute_difference_pp": max(differences),
        "archived_rolling_sha256": hashlib.sha256(
            rolling_path.read_bytes()
        ).hexdigest(),
    }
    verification["rgdp_official_annual_title"] = title
    verification["rgdp_official_annual_vs_nonadjusted_quarterly_sums"] = (
        _deviation_summary(
            official,
            _growth(
                _annual_sums(_values(acquired["ecb_ea_rgdp_level_nsa_quarterly.csv"]))
            ),
        )
    )
    verification["rgdp_official_annual_vs_superseded_adjusted_quarterly_sums"] = (
        _deviation_summary(official, _growth(_annual_sums(adjusted)))
    )
    verification["rgdp_official_annual_vs_eurostat_published_annual_growth"] = {
        "eurostat_url": EUROSTAT_ANNUAL_GROWTH_URL,
        **_deviation_summary(official, _eurostat_annual_growth()),
    }

    for variable in ("hicp", "hicpx"):
        index = _values(acquired[f"ecb_ea_{variable}_index_monthly.csv"])
        annual = _values(acquired[f"ecb_ea_{variable}_growth_annual.csv"])
        grouped: dict[str, dict[int, float]] = defaultdict(dict)
        for period, level in index.items():
            grouped[period[:4]][int(period[5:])] = level
        means = {
            year: sum(months.values()) / 12
            for year, months in grouped.items()
            if set(months) == set(range(1, 13))
        }
        differences = {
            year: abs(100 * (value / means[str(int(year) - 1)] - 1) - annual[year])
            for year, value in means.items()
            if str(int(year) - 1) in means and year in annual
        }
        verification[f"{variable}_avr_vs_annual_index_growth"] = {
            "matched_years": len(differences),
            "first_year": min(differences),
            "last_year": max(differences),
            "max_absolute_difference_pp": max(differences.values()),
            "published_avr_precision_pp": 0.1,
            "index_based_growth_unavailable_years": sorted(
                set(annual) - set(differences)
            ),
        }
    return verification


def describe(
    payload: bytes, *, key: str, url: str, retrieved_at_utc: str
) -> dict[str, object]:
    records = _rows(payload)
    if not records or {row["KEY"] for row in records} != {key}:
        raise ValueError(f"Unexpected or empty series for {url}")
    periods = [row["TIME_PERIOD"] for row in records]
    if len(set(periods)) != len(periods):
        raise ValueError(f"Duplicate periods for {url}")
    flow = key.split(".", 1)[0]
    first = records[0]
    return {
        "series_key": key,
        "url": url,
        "portal_url": f"https://data.ecb.europa.eu/data/datasets/{flow}/{key}",
        "sha256": hashlib.sha256(payload).hexdigest(),
        "observations": len(records),
        "first_period": min(periods),
        "last_period": max(periods),
        "retrieved_at_utc": retrieved_at_utc,
        "metadata": {
            column: first[column] for column in METADATA_COLUMNS if first.get(column)
        },
    }


def series_url(key: str) -> str:
    flow, series = key.split(".", 1)
    return f"https://data-api.ecb.europa.eu/service/data/{flow}/{series}?format=csvdata"


def download(url: str) -> bytes:
    request = Request(url, headers={"User-Agent": "forecast-uncertainty-research/1"})
    with urlopen(request, timeout=45) as response:
        return response.read()


def reusable(filename: str, key: str) -> bytes | None:
    """Return the stored bytes when they already match the recorded checksum."""
    path = RAW / filename
    if not path.exists() or not MANIFEST.exists():
        return None
    entry = json.loads(MANIFEST.read_text())["sources"].get(filename)
    payload = path.read_bytes()
    if (
        entry is None
        or entry.get("series_key") != key
        or entry.get("sha256") != hashlib.sha256(payload).hexdigest()
    ):
        return None
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--refresh",
        action="store_true",
        help="re-download every source instead of reusing verified local copies",
    )
    arguments = parser.parse_args()

    now = datetime.now(UTC).isoformat()
    previous = (
        json.loads(MANIFEST.read_text()) if MANIFEST.exists() else {"sources": {}}
    )
    sources: dict[str, dict[str, object]] = {}
    acquired: dict[str, bytes] = {}
    fetched: list[str] = []
    for filename, key in SOURCES.items():
        url = series_url(key)
        payload = None if arguments.refresh else reusable(filename, key)
        if payload is None:
            payload = download(url)
            fetched.append(filename)
            retrieved = now
        else:
            retrieved = previous["sources"][filename].get(
                "retrieved_at_utc", previous.get("retrieved_at_utc", now)
            )
        sources[filename] = describe(
            payload, key=key, url=url, retrieved_at_utc=retrieved
        )
        acquired[filename] = payload

    manifest = {
        "retrieved_at_utc": now,
        "notes": NOTES,
        "sources": sources,
        "verification": verify_companions(acquired),
    }
    for filename in fetched:
        (RAW / filename).write_bytes(acquired[filename])
    MANIFEST.write_text(json.dumps(manifest, indent=2) + "\n")
    print(
        f"Recorded {len(acquired)} ECB annual-outcome companion sources in {RAW} "
        f"({len(fetched)} downloaded, {len(acquired) - len(fetched)} reused)"
    )


if __name__ == "__main__":
    main()
