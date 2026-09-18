"""Parser for individual-round ECB Survey of Professional Forecasters files."""

from __future__ import annotations

import csv
import re
from collections.abc import Iterable, Sequence
from pathlib import Path

import numpy as np
import pandas as pd

from .bins import BinScheme, ecb_intervals, parse_ecb_header

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_RAW_DIR = REPOSITORY_ROOT / "data" / "raw" / "ecb_spf"

OUTPUT_COLUMNS = (
    "survey",
    "variable",
    "concept",
    "year",
    "quarter",
    "target_period",
    "target_year",
    "horizon_class",
    "horizon_years",
    "horizon_quarters",
    "bin_scheme",
    "respondent",
    "bin_index",
    "probability",
    "lower",
    "upper",
    "midpoint",
)

SECTION_CAPTIONS = {
    "INFLATION EXPECTATIONS; YEAR-ON-YEAR CHANGE IN HICP": "hicp",
    "CORE INFLATION EXPECTATIONS; YEAR-ON-YEAR CHANGE IN CORE": "hicpx",
    "GROWTH EXPECTATIONS; YEAR-ON-YEAR CHANGE IN REAL GDP": "rgdp",
    "EXPECTED UNEMPLOYMENT RATE; PERCENTAGE OF LABOUR FORCE": "unemp",
}

CONCEPTS = {
    "hicp": "hicp_yoy",
    "hicpx": "hicpx_yoy_ex_food_energy",
    "rgdp": "real_gdp_yoy",
    "unemp": "unemployment_rate",
}

_ROUND_PATTERN = re.compile(r"^(?P<year>\d{4})Q(?P<quarter>[1-4])$")
_YEAR_PATTERN = re.compile(r"^\d{4}$")
_MONTH_PATTERN = re.compile(r"^(?P<year>\d{4})(?P<month>[A-Z][a-z]{2})$")
_QUARTER_PATTERN = re.compile(r"^(?P<year>\d{4})Q(?P<quarter>[1-4])$")
_MONTH_NUMBER = {
    "Jan": 1,
    "Feb": 2,
    "Mar": 3,
    "Apr": 4,
    "May": 5,
    "Jun": 6,
    "Jul": 7,
    "Aug": 8,
    "Sep": 9,
    "Oct": 10,
    "Nov": 11,
    "Dec": 12,
}


def parse_ecb_round(path: str | Path) -> pd.DataFrame:
    """Parse one stacked ECB SPF CSV into respondent-by-bin long form."""
    source = Path(path)
    year, quarter = _round_from_path(source)
    with source.open(encoding="utf-8-sig", newline="") as stream:
        rows = list(csv.reader(stream))

    frames: list[pd.DataFrame] = []
    markers = _section_markers(rows)
    for marker_index, (start, variable) in enumerate(markers):
        if variable is None:
            continue
        end = (
            markers[marker_index + 1][0]
            if marker_index + 1 < len(markers)
            else len(rows)
        )
        frame = _parse_section(
            rows[start + 1 : end],
            variable=variable,
            year=year,
            quarter=quarter,
            source=source,
        )
        if not frame.empty:
            frames.append(frame)
    if not frames:
        return _empty_frame()
    return pd.concat(frames, ignore_index=True)[list(OUTPUT_COLUMNS)]


def load_ecb_spf(raw_dir: str | Path = DEFAULT_RAW_DIR) -> pd.DataFrame:
    """Parse all ECB individual-round CSV files in chronological order."""
    directory = Path(raw_dir)
    paths = sorted(
        directory.glob("[0-9][0-9][0-9][0-9]Q[1-4].csv"), key=_round_from_path
    )
    if not paths:
        raise FileNotFoundError(f"No ECB SPF round files found in {directory}")
    frames = [parse_ecb_round(path) for path in paths]
    nonempty = [frame for frame in frames if not frame.empty]
    if not nonempty:
        return _empty_frame()
    return pd.concat(nonempty, ignore_index=True)[list(OUTPUT_COLUMNS)]


def parse_ecb_spf(path: str | Path = DEFAULT_RAW_DIR) -> pd.DataFrame:
    """Parse either one ECB round file or a directory of round files."""
    source = Path(path)
    return load_ecb_spf(source) if source.is_dir() else parse_ecb_round(source)


def _parse_section(
    rows: Sequence[Sequence[str]],
    *,
    variable: str,
    year: int,
    quarter: int,
    source: Path,
) -> pd.DataFrame:
    header_index = next(
        (
            index
            for index, row in enumerate(rows)
            if len(row) >= 3
            and tuple(cell.strip() for cell in row[:3])
            == ("TARGET_PERIOD", "FCT_SOURCE", "POINT")
        ),
        None,
    )
    if header_index is None:
        return _empty_frame()

    header = rows[header_index]
    bin_columns = [
        (index, value.strip())
        for index, value in enumerate(header[3:], start=3)
        if value.strip()
    ]
    if not bin_columns:
        return _empty_frame()

    ordered_bins = _ordered_bins(bin_columns)
    bin_headers = [header_name for _, header_name, _ in ordered_bins]
    intervals = ecb_intervals([bounds for _, _, bounds in ordered_bins])
    scheme_name = "|".join(bin_headers)
    midpoints = np.asarray(BinScheme(scheme_name, intervals).midpoints, dtype=float)

    targets: list[str] = []
    respondents: list[str] = []
    probability_rows: list[list[float]] = []
    for row_number, row in enumerate(rows[header_index + 1 :], start=header_index + 2):
        target = row[0].strip() if row else ""
        respondent = row[1].strip() if len(row) > 1 else ""
        if not target or not respondent:
            continue
        probabilities = [
            _parse_probability(
                row[column_index] if column_index < len(row) else "",
                source=source,
                row_number=row_number,
                header=header_name,
            )
            for column_index, header_name, _ in ordered_bins
        ]
        targets.append(target)
        respondents.append(respondent)
        probability_rows.append(probabilities)

    if not targets:
        return _empty_frame()

    horizon_metadata = _classify_targets(targets, survey_year=year)
    probabilities = np.asarray(probability_rows, dtype=float)
    row_count, bin_count = probabilities.shape
    repeated_targets = np.repeat(np.asarray(targets, dtype=object), bin_count)
    metadata = [horizon_metadata[target] for target in targets]

    result = pd.DataFrame(
        {
            "survey": "ecb",
            "variable": variable,
            "concept": CONCEPTS[variable],
            "year": year,
            "quarter": quarter,
            "target_period": repeated_targets,
            "target_year": np.repeat(
                np.asarray([item.target_year for item in metadata], dtype=object),
                bin_count,
            ),
            "horizon_class": np.repeat(
                np.asarray([item.horizon_class for item in metadata], dtype=object),
                bin_count,
            ),
            "horizon_years": np.repeat(
                np.asarray([item.horizon_years for item in metadata], dtype=float),
                bin_count,
            ),
            "horizon_quarters": pd.array(
                [pd.NA] * (row_count * bin_count), dtype="Int64"
            ),
            "bin_scheme": scheme_name,
            "respondent": np.repeat(np.asarray(respondents, dtype=object), bin_count),
            "bin_index": np.tile(np.arange(bin_count, dtype=int), row_count),
            "probability": probabilities.reshape(-1),
            "lower": np.tile(
                np.asarray(
                    [np.nan if lower is None else lower for lower, _ in intervals],
                    dtype=float,
                ),
                row_count,
            ),
            "upper": np.tile(
                np.asarray(
                    [np.nan if upper is None else upper for _, upper in intervals],
                    dtype=float,
                ),
                row_count,
            ),
            "midpoint": np.tile(midpoints, row_count),
        }
    )
    result["target_year"] = pd.array(result["target_year"], dtype="Int64")
    return result[list(OUTPUT_COLUMNS)]


def _section_markers(rows: Sequence[Sequence[str]]) -> list[tuple[int, str | None]]:
    markers: list[tuple[int, str | None]] = []
    for index, row in enumerate(rows):
        first = row[0].strip() if row else ""
        if first in SECTION_CAPTIONS:
            markers.append((index, SECTION_CAPTIONS[first]))
        elif first == "ASSUMPTIONS":
            markers.append((index, None))
    return markers


def _ordered_bins(
    bin_columns: Iterable[tuple[int, str]],
) -> list[tuple[int, str, tuple[float | None, float | None]]]:
    parsed = [
        (column_index, header, parse_ecb_header(header))
        for column_index, header in bin_columns
    ]
    return sorted(
        parsed,
        key=lambda item: float("-inf") if item[2][0] is None else item[2][0],
    )


def _parse_probability(
    value: str,
    *,
    source: Path,
    row_number: int,
    header: str,
) -> float:
    stripped = value.strip()
    if not stripped:
        return np.nan
    try:
        return float(stripped)
    except ValueError as error:
        raise ValueError(
            f"Invalid probability {value!r} in {source}, row {row_number}, {header}"
        ) from error


class _Horizon:
    __slots__ = ("horizon_class", "horizon_years", "target_year")

    def __init__(
        self,
        target_year: int | None,
        horizon_class: str,
        horizon_years: float,
    ) -> None:
        self.target_year = target_year
        self.horizon_class = horizon_class
        self.horizon_years = horizon_years


def _classify_targets(
    targets: Sequence[str], *, survey_year: int
) -> dict[str, _Horizon]:
    unique_targets = list(dict.fromkeys(targets))
    output: dict[str, _Horizon] = {}
    dated_targets: list[tuple[int, str]] = []
    for target in unique_targets:
        if _YEAR_PATTERN.fullmatch(target):
            target_year = int(target)
            difference = target_year - survey_year
            if difference < 0:
                raise ValueError(
                    f"Target year {target_year} predates survey year {survey_year}"
                )
            horizon_class = {
                0: "current_year",
                1: "next_year",
                2: "year_after_next",
            }.get(difference, "longer_term")
            output[target] = _Horizon(target_year, horizon_class, float(difference))
        else:
            dated_targets.append((_target_ordinal(target), target))

    nominal_horizons = (
        ("rolling_1y", 1.0),
        ("rolling_2y", 2.0),
        ("longer_term", 5.0),
    )
    for index, (_, target) in enumerate(sorted(dated_targets)):
        if index >= len(nominal_horizons):
            raise ValueError(
                f"More than three rolling targets found for survey year {survey_year}"
            )
        horizon_class, horizon_years = nominal_horizons[index]
        output[target] = _Horizon(None, horizon_class, horizon_years)
    return output


def _target_ordinal(target: str) -> int:
    month_match = _MONTH_PATTERN.fullmatch(target)
    if month_match is not None:
        month = month_match["month"]
        if month not in _MONTH_NUMBER:
            raise ValueError(f"Invalid ECB target month: {target!r}")
        return int(month_match["year"]) * 12 + _MONTH_NUMBER[month] - 1
    quarter_match = _QUARTER_PATTERN.fullmatch(target)
    if quarter_match is not None:
        return int(quarter_match["year"]) * 4 + int(quarter_match["quarter"]) - 1
    raise ValueError(f"Invalid ECB target period: {target!r}")


def _round_from_path(path: Path) -> tuple[int, int]:
    match = _ROUND_PATTERN.fullmatch(path.stem)
    if match is None:
        raise ValueError(f"ECB SPF filename is not YYYYQq.csv: {path.name!r}")
    return int(match["year"]), int(match["quarter"])


def _empty_frame() -> pd.DataFrame:
    return pd.DataFrame(columns=OUTPUT_COLUMNS)


parse_round = parse_ecb_round
load_all = load_ecb_spf
