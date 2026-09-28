"""Acquire the US outcome series and pin them in a provenance manifest.

Run from the repository root with ``uv run python scripts/download_us_realizations.py``.

BLS series come straight from the BLS Public Data API (v2), because the DBnomics
mirror of the BLS provider stopped at January 2025 even after re-indexing in
March 2026. BEA series still come through DBnomics, which carries BEA releases
promptly; each one is cross-checked against BEA's own bulk NIPA files, so a
mirror that falls behind or diverges from the publisher fails here rather than
reaching the outputs.

Every series must reach the latest period its publisher has certainly released by
the retrieval time (``expectations.realizations.OUTCOME_PUBLICATION_LAGS``). A
frozen mirror therefore stops the refresh instead of silently shortening the
outcome history.

Sources already present with the recorded checksum are reused rather than
re-downloaded; ``--refresh`` downloads every source again. Set ``BLS_API_KEY`` to
use a registered BLS key (20 years per request instead of 10); the key is never
written to disk.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import os
import time
from datetime import UTC, datetime
from pathlib import Path
from urllib.request import Request, urlopen

from expectations.outcome_sources import (
    BLS_API_URL,
    US_OUTCOME_MANIFEST,
    US_OUTCOME_SOURCES,
    check_publication_currency,
    dbnomics_series_url,
    load_bls_file,
    load_dbnomics_file,
)

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
MANIFEST = RAW / US_OUTCOME_MANIFEST
USER_AGENT = "expectations-research/1 (github.com/MaxGhenis/expectations)"
BEA_BULK_URL = "https://apps.bea.gov/national/Release/TXT/NipaData{frequency}.txt"
NOTES = [
    (
        "BLS series come from the BLS Public Data API v2. The DBnomics BLS "
        "provider, which this repository used until September 2026, ends at "
        "January 2025 for both LNS14000000 and CUSR0000SA0L1E although DBnomics "
        "re-indexed it in March 2026; it is no longer used."
    ),
    (
        "Each BLS file stores the API's data points verbatim, including the "
        "footnotes that mark a month as not collected. October 2025 is such a "
        "month for every series here: BLS did not collect it during the lapse "
        "in appropriations."
    ),
    (
        "LNU04000000 is fetched for its official annual averages (period M13). "
        "BLS states that its 2025 annual averages are 11-month averages that "
        "exclude October."
    ),
    (
        "BEA series come through DBnomics and are compared with BEA's own bulk "
        "NIPA files at retrieval; 'verification' records the matched periods "
        "and the largest difference."
    ),
    (
        "Retrieval time is not an economic vintage identifier. All outcomes are "
        "revised (latest-vintage) data."
    ),
]


def _request(url: str, *, body: dict | None = None) -> bytes:
    data = None if body is None else json.dumps(body).encode()
    headers = {"User-Agent": USER_AGENT}
    if body is not None:
        headers["Content-Type"] = "application/json"
    request = Request(url, data=data, headers=headers)
    with urlopen(request, timeout=120) as response:
        return response.read()


def _response_headers(url: str) -> dict[str, str]:
    request = Request(url, method="HEAD", headers={"User-Agent": USER_AGENT})
    with urlopen(request, timeout=60) as response:
        return dict(response.headers)


def fetch_bls(series_ids: list[str], first_year: int, last_year: int) -> dict:
    """Collect BLS series over every year, verbatim, one JSON document each.

    All series share each request, so a full refresh costs one request per
    decade (eight for 1948 onward), well inside the keyless limit of 25 a day.
    """
    key = os.environ.get("BLS_API_KEY")
    span = 20 if key else 10
    requests: list[dict[str, object]] = []
    messages: list[str] = []
    points: dict[str, list[dict[str, object]]] = {series: [] for series in series_ids}
    for start in range(first_year, last_year + 1, span):
        end = min(start + span - 1, last_year)
        body: dict[str, object] = {
            "seriesid": series_ids,
            "startyear": str(start),
            "endyear": str(end),
            "annualaverage": True,
        }
        payload = json.loads(
            _request(
                BLS_API_URL, body={**body, "registrationkey": key} if key else body
            )
        )
        if payload.get("status") != "REQUEST_SUCCEEDED":
            raise RuntimeError(
                f"BLS request {start}-{end} failed: {payload.get('message')}"
            )
        for series in payload["Results"]["series"]:
            if series["seriesID"] not in points:
                raise RuntimeError(f"BLS returned unrequested {series['seriesID']}")
            points[series["seriesID"]].extend(
                {field: value for field, value in point.items() if field != "latest"}
                for point in series["data"]
            )
        requests.append(body)
        messages.extend(str(message) for message in payload.get("message", []))
        time.sleep(1)
    documents = {}
    for series_id, data in points.items():
        data.sort(key=lambda point: (point["year"], point["period"]))
        document = {
            "source": "BLS Public Data API v2",
            "url": BLS_API_URL,
            "series_id": series_id,
            "requests": requests,
            "messages": [message for message in messages if series_id in message],
            "data": data,
        }
        documents[series_id] = (
            json.dumps(document, indent=1, ensure_ascii=False) + "\n"
        ).encode()
    return documents


def fetch_dbnomics(series: str) -> bytes:
    return _request(dbnomics_series_url(series))


def bea_bulk_values(frequency: str) -> tuple[dict[str, dict[str, float]], str]:
    """Read BEA's bulk NIPA file for one frequency, keyed by series then period."""
    url = BEA_BULK_URL.format(frequency=frequency)
    text = _request(url).decode("utf-8-sig")
    values: dict[str, dict[str, float]] = {}
    for row in csv.reader(io.StringIO(text)):
        if not row or row[0].startswith("%"):
            continue
        code, period, value = row
        values.setdefault(code, {})[period] = float(value.replace(",", ""))
    modified = _response_headers(url).get("Last-Modified", "")
    return values, modified


def _bea_period(period: str, frequency: str) -> str:
    """Translate a DBnomics period into BEA's bulk-file notation."""
    if frequency == "Q":
        return period.replace("-", "")
    if frequency == "M":
        return period.replace("-", "M")
    return period


def verify_bea(acquired: dict[str, bytes]) -> dict[str, object]:
    """Compare every DBnomics BEA series with BEA's own bulk NIPA file."""
    verification: dict[str, object] = {}
    bulk: dict[str, tuple[dict[str, dict[str, float]], str]] = {}
    for filename, spec in US_OUTCOME_SOURCES.items():
        if spec["provider"] != "dbnomics":
            continue
        code, frequency = spec["bea_series"], spec["bea_frequency"]
        if frequency not in bulk:
            bulk[frequency] = bea_bulk_values(frequency)
        published, modified = bulk[frequency]
        mirror = load_dbnomics_file(acquired[filename])
        publisher = published[code]
        matched = {
            period: abs(value - publisher[_bea_period(period, frequency)])
            for period, value in mirror.items()
            if _bea_period(period, frequency) in publisher
        }
        latest_publisher = max(publisher, key=lambda period: (len(period), period))
        latest_mirror = _bea_period(max(mirror.index), frequency)
        if not matched:
            raise ValueError(f"No BEA bulk periods match {filename}")
        if (len(latest_mirror), latest_mirror) < (
            len(latest_publisher),
            latest_publisher,
        ):
            raise ValueError(
                f"{filename} ends at {latest_mirror}, but BEA's bulk file already "
                f"reaches {latest_publisher}"
            )
        worst = max(matched, key=matched.__getitem__)
        verification[filename] = {
            "bea_bulk_url": BEA_BULK_URL.format(frequency=frequency),
            "bea_bulk_last_modified": modified,
            "bea_series": code,
            "matched_periods": len(matched),
            "max_absolute_difference": matched[worst],
            "max_absolute_difference_period": worst,
            "bea_bulk_last_period": latest_publisher,
        }
    return verification


def verify_bls(acquired: dict[str, bytes]) -> dict[str, object]:
    """Record how the official annual average relates to the monthly mean."""
    monthly = load_bls_file(acquired["bls_ln_LNS14000000_monthly.json"])
    annual = load_bls_file(acquired["bls_ln_LNU04000000_annual.json"])
    official = annual.annual_averages
    means = monthly.complete_year_means()
    shared = sorted(set(official) & set(means))
    differences = {year: abs(means[year] - official[year]) for year in shared}
    worst = max(differences, key=differences.__getitem__)
    return {
        "unemployment_monthly_mean_vs_official_annual_average": {
            "matched_years": len(shared),
            "first_year": shared[0],
            "last_year": shared[-1],
            "max_absolute_difference_pp": differences[worst],
            "max_absolute_difference_year": worst,
            "official_annual_average_precision_pp": 0.1,
        },
        "months_bls_marks_not_collected": {
            filename: [
                f"{year}-{month:02d}"
                for year, month in load_bls_file(payload).unavailable_months
            ]
            for filename, payload in acquired.items()
            if filename.startswith("bls_")
        },
    }


def describe(filename: str, payload: bytes, *, retrieved_at_utc: str) -> dict:
    spec = US_OUTCOME_SOURCES[filename]
    if spec["provider"] == "bls":
        series = load_bls_file(payload)
        periods = series.monthly_periods() + [
            str(year) for year in series.annual_averages
        ]
        if series.series_id != spec["series_id"]:
            raise ValueError(f"{filename} holds {series.series_id}")
        url = BLS_API_URL
        identity = {"series_id": spec["series_id"]}
    else:
        observations = load_dbnomics_file(payload)
        periods = list(observations.index)
        url = dbnomics_series_url(spec["series"])
        identity = {"series": spec["series"]}
    monthly = [period for period in periods if "-" in period]
    last_period = max(monthly) if monthly else max(periods)
    return {
        **identity,
        "provider": spec["provider"],
        "url": url,
        "sha256": hashlib.sha256(payload).hexdigest(),
        "observations": len(periods),
        "first_period": min(periods),
        "last_period": last_period,
        "retrieved_at_utc": retrieved_at_utc,
        "role": spec["role"],
    }


def reusable(filename: str) -> bytes | None:
    path = RAW / filename
    if not path.exists() or not MANIFEST.exists():
        return None
    entry = json.loads(MANIFEST.read_text())["sources"].get(filename)
    payload = path.read_bytes()
    if entry is None or entry.get("sha256") != hashlib.sha256(payload).hexdigest():
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

    now = datetime.now(UTC)
    stamp = now.isoformat()
    previous = (
        json.loads(MANIFEST.read_text()) if MANIFEST.exists() else {"sources": {}}
    )
    sources: dict[str, dict] = {}
    acquired: dict[str, bytes] = {}
    fetched: list[str] = []
    reused = {
        filename: payload
        for filename in US_OUTCOME_SOURCES
        if not arguments.refresh and (payload := reusable(filename)) is not None
    }
    bls_needed = [
        filename
        for filename, spec in US_OUTCOME_SOURCES.items()
        if spec["provider"] == "bls" and filename not in reused
    ]
    bls_documents = (
        fetch_bls(
            [US_OUTCOME_SOURCES[filename]["series_id"] for filename in bls_needed],
            min(US_OUTCOME_SOURCES[filename]["first_year"] for filename in bls_needed),
            now.year,
        )
        if bls_needed
        else {}
    )
    for filename, spec in US_OUTCOME_SOURCES.items():
        if filename in reused:
            payload = reused[filename]
            retrieved = previous["sources"][filename]["retrieved_at_utc"]
        else:
            payload = (
                bls_documents[spec["series_id"]]
                if spec["provider"] == "bls"
                else fetch_dbnomics(spec["series"])
            )
            fetched.append(filename)
            retrieved = stamp
        sources[filename] = describe(filename, payload, retrieved_at_utc=retrieved)
        acquired[filename] = payload

    stale = check_publication_currency(sources)
    if stale:
        raise SystemExit("Refusing stale outcome sources:\n  " + "\n  ".join(stale))

    manifest = {
        "retrieved_at_utc": stamp,
        "notes": NOTES,
        "sources": sources,
        "verification": {**verify_bls(acquired), "bea": verify_bea(acquired)},
    }
    for filename in fetched:
        (RAW / filename).write_bytes(acquired[filename])
    MANIFEST.write_text(json.dumps(manifest, indent=2) + "\n")
    print(
        f"Recorded {len(sources)} US outcome sources in {MANIFEST.relative_to(ROOT)} "
        f"({len(fetched)} downloaded, {len(sources) - len(fetched)} reused)"
    )


if __name__ == "__main__":
    main()
