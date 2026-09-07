"""Acquire annual-outcome companion sources without replacing rolling snapshots.

Run from the repository root with ``python scripts/download_ecb_annual_realizations.py``.
The legacy ICP series match the existing rolling files' classification/geography;
they stop in December 2025. New HICP flow observations are intentionally not spliced
into these archived series. Retrieval time is not an economic vintage identifier.
"""

from __future__ import annotations

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
SOURCES = {
    "ecb_ea_rgdp_level_quarterly.csv": "MNA.Q.Y.I9.W2.S1.S1.B.B1GQ._Z._Z._Z.EUR.LR.N",
    "ecb_ea_hicp_index_monthly.csv": "ICP.M.U2.N.000000.4.INX",
    "ecb_ea_hicpx_index_monthly.csv": "ICP.M.U2.N.XEF000.4.INX",
    "ecb_ea_hicp_growth_annual.csv": "ICP.A.U2.N.000000.4.AVR",
    "ecb_ea_hicpx_growth_annual.csv": "ICP.A.U2.N.XEF000.4.AVR",
}


def verify_companions(acquired: dict[str, bytes]) -> dict:
    def values(payload: bytes) -> dict[str, float]:
        return {
            row["TIME_PERIOD"]: float(row["OBS_VALUE"])
            for row in csv.DictReader(io.StringIO(payload.decode("utf-8-sig")))
        }

    verification = {}
    gdp = values(acquired["ecb_ea_rgdp_level_quarterly.csv"])
    rolling_path = RAW / "ecb_ea_rgdp_yoy_quarterly.csv"
    rolling = values(rolling_path.read_bytes())
    differences = [
        abs(
            100 * (level / gdp[f"{int(period[:4]) - 1}{period[4:]}"] - 1)
            - rolling[period]
        )
        for period, level in gdp.items()
        if f"{int(period[:4]) - 1}{period[4:]}" in gdp and period in rolling
    ]
    verification["rgdp_quarterly_yoy_vs_archived_rolling"] = {
        "matched_periods": len(differences),
        "max_absolute_difference_pp": max(differences),
        "archived_rolling_sha256": hashlib.sha256(
            rolling_path.read_bytes()
        ).hexdigest(),
    }
    for variable in ("hicp", "hicpx"):
        index = values(acquired[f"ecb_ea_{variable}_index_monthly.csv"])
        annual = values(acquired[f"ecb_ea_{variable}_growth_annual.csv"])
        grouped = defaultdict(dict)
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


def main() -> None:
    manifest = {
        "retrieved_at_utc": datetime.now(UTC).isoformat(),
        "notes": [
            "Annual GDP is growth in sums of four quarterly chain-linked volume levels, calendar and seasonally adjusted, fixed EA20 composition.",
            "Annual HICP and HICPX use official annual-average index growth (AVR), rounded by the publisher to 0.1 percentage point; not mean monthly year-on-year growth.",
            "Monthly HICP indexes are retained to verify annual growth wherever both full years exist. HICPX index months are missing in 1997–2000; published annual AVR avoids losing those calendar benchmark targets.",
            "Existing rolling raw files are preserved. Their original retrieval dates are unrecorded; do not infer identical vintages from this companion retrieval date.",
            "GDP companion level implied quarterly year-on-year growth is compared with the archived rolling values in verification; retrieval date alone does not establish vintage equality.",
            "Calendar inflation statuses are those of the official annual observation, and can differ from statuses in the archived monthly growth series.",
            "Legacy ICP flow is discontinued; the new HICP flow is not spliced into this 1997–2025 outcome history.",
        ],
        "sources": {},
    }
    acquired = {}
    for filename, key in SOURCES.items():
        flow, series = key.split(".", 1)
        url = f"https://data-api.ecb.europa.eu/service/data/{flow}/{series}?format=csvdata"
        request = Request(
            url, headers={"User-Agent": "forecast-uncertainty-research/1"}
        )
        with urlopen(request, timeout=45) as response:
            payload = response.read()
        records = list(csv.DictReader(io.StringIO(payload.decode("utf-8-sig"))))
        if not records or {row["KEY"] for row in records} != {key}:
            raise ValueError(f"Unexpected or empty series for {url}")
        periods = [row["TIME_PERIOD"] for row in records]
        if len(set(periods)) != len(periods):
            raise ValueError(f"Duplicate periods for {url}")
        first = records[0]
        manifest["sources"][filename] = {
            "series_key": key,
            "url": url,
            "portal_url": f"https://data.ecb.europa.eu/data/datasets/{flow}/{key}",
            "sha256": hashlib.sha256(payload).hexdigest(),
            "observations": len(records),
            "first_period": min(periods),
            "last_period": max(periods),
            "metadata": {
                column: first[column]
                for column in (
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
                if first.get(column)
            },
        }
        acquired[filename] = payload
    manifest["verification"] = verify_companions(acquired)
    for filename, payload in acquired.items():
        (RAW / filename).write_bytes(payload)
    (RAW / "ecb_annual_realizations_sources.json").write_text(
        json.dumps(manifest, indent=2) + "\n"
    )
    print(f"Recorded {len(acquired)} ECB annual-outcome companion sources in {RAW}")


if __name__ == "__main__":
    main()
