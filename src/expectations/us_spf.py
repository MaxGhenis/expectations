"""Parsers for individual-response files from the US SPF."""

from __future__ import annotations

import warnings
import zipfile
from collections.abc import Iterable
from pathlib import Path

import numpy as np
import pandas as pd

from .bins import BinScheme, us_bin_scheme

DEFAULT_DATA_DIR = Path(__file__).resolve().parents[2] / "data" / "raw"
DENSITY_VARIABLES = ("PRGDP", "PRPGDP", "PRUNEMP", "PRCCPI", "PRCPCE")
LONGRUN_VARIABLES = ("RGDP10", "CPI10", "PCE10")

_EARLY_NEXT_YEAR_ROUNDS = {
    (1968, 4),
    (1969, 4),
    (1970, 4),
    (1971, 4),
    (1972, 3),
    (1972, 4),
    (1973, 4),
    (1975, 4),
    (1976, 4),
    (1977, 4),
    (1978, 4),
    (1979, 2),
    (1979, 3),
    (1979, 4),
}
_AMBIGUOUS_TARGET_ROUNDS = {(1985, 1), (1986, 1)}

_DENSITY_COLUMNS = [
    "survey",
    "variable",
    "concept",
    "year",
    "quarter",
    "target_year",
    "horizon_class",
    "horizon_years",
    "horizon_quarters",
    "bin_scheme",
    "target_block",
    "response_index",
    "respondent",
    "industry",
    "bin_index",
    "raw_bin_number",
    "source_column",
    "probability",
    "lower",
    "upper",
    "midpoint",
]


def parse_us_density(
    variable: str,
    path: str | Path | None = None,
    data_dir: str | Path = DEFAULT_DATA_DIR,
) -> pd.DataFrame:
    """Read one US density workbook into a respondent-by-bin tidy table.

    Probability values remain in percentage points and missing cells remain NaN.
    The response filter and normalization therefore operate on the original data.
    """
    name = _density_variable(variable)
    source = Path(path) if path is not None else _individual_path(name, data_dir)
    return tidy_us_density(_read_excel(source), name)


def tidy_us_density(frame: pd.DataFrame, variable: str) -> pd.DataFrame:
    """Reshape an already-loaded US density sheet without filtering responses."""
    name = _density_variable(variable)
    required = {"YEAR", "QUARTER", "ID", "INDUSTRY"}
    missing = required.difference(frame.columns)
    if missing:
        raise ValueError(f"Missing required US SPF columns: {sorted(missing)}")

    data = frame.copy(deep=False)
    data = data.assign(_response_index=np.arange(len(data), dtype=np.int64))
    pieces: list[pd.DataFrame] = []
    for (raw_year, raw_quarter), round_frame in data.groupby(
        ["YEAR", "QUARTER"], sort=True, dropna=False
    ):
        if pd.isna(raw_year) or pd.isna(raw_quarter):
            continue
        year, quarter = int(raw_year), int(raw_quarter)
        if not _density_active(name, year, quarter):
            continue
        scheme = us_bin_scheme(name, year, quarter)
        for target_block, offset in enumerate(
            us_target_offsets(name, year, quarter), start=1
        ):
            pieces.append(
                _tidy_density_block(
                    round_frame,
                    name,
                    year,
                    quarter,
                    scheme,
                    target_block,
                    offset,
                )
            )

    if not pieces:
        return pd.DataFrame(columns=_DENSITY_COLUMNS)
    output = pd.concat(pieces, ignore_index=True)
    for column in ("target_year", "horizon_years", "horizon_quarters"):
        output[column] = output[column].astype("Int64")
    return output.loc[:, _DENSITY_COLUMNS]


def parse_all_us_densities(
    data_dir: str | Path = DEFAULT_DATA_DIR,
    variables: Iterable[str] = DENSITY_VARIABLES,
) -> pd.DataFrame:
    """Parse all requested US density workbooks into one tidy table."""
    frames = [parse_us_density(variable, data_dir=data_dir) for variable in variables]
    if not frames:
        return pd.DataFrame(columns=_DENSITY_COLUMNS)
    return pd.concat(frames, ignore_index=True)


def _tidy_density_block(
    round_frame: pd.DataFrame,
    variable: str,
    year: int,
    quarter: int,
    scheme: BinScheme,
    target_block: int,
    offset: int | None,
) -> pd.DataFrame:
    count = len(scheme.intervals)
    first = (target_block - 1) * count + 1
    numbers = list(range(first, first + count))
    value_columns = [f"{variable}{number}" for number in numbers]
    missing = set(value_columns).difference(round_frame.columns)
    if missing:
        raise ValueError(
            f"{variable} {year}Q{quarter} needs missing columns: {sorted(missing)}"
        )

    block = round_frame[["_response_index", "ID", "INDUSTRY", *value_columns]].melt(
        id_vars=["_response_index", "ID", "INDUSTRY"],
        value_vars=value_columns,
        var_name="source_column",
        value_name="probability",
    )
    numeric = pd.to_numeric(block["probability"], errors="coerce")
    invalid = block["probability"].notna() & numeric.isna()
    if invalid.any():
        bad = block.loc[invalid, "probability"].iloc[0]
        raise ValueError(
            f"Nonnumeric probability in {variable} {year}Q{quarter}: {bad!r}"
        )
    block["probability"] = numeric

    by_column = {column: index for index, column in enumerate(value_columns)}
    zero_based = block["source_column"].map(by_column).astype(int)
    intervals = scheme.intervals
    midpoints = scheme.midpoints
    block["bin_index"] = zero_based
    block["raw_bin_number"] = zero_based + first
    block["lower"] = zero_based.map(lambda index: intervals[index][0])
    block["upper"] = zero_based.map(lambda index: intervals[index][1])
    block["midpoint"] = zero_based.map(lambda index: midpoints[index])

    if offset is None:
        target_year = pd.NA
        horizon_class = pd.NA
        horizon_years = pd.NA
        horizon_quarters = pd.NA
    else:
        target_year = year + offset
        horizon_class = _horizon_class(offset)
        horizon_years = offset
        horizon_quarters = 4 * offset + (4 - quarter) + 1

    return block.rename(
        columns={
            "_response_index": "response_index",
            "ID": "respondent",
            "INDUSTRY": "industry",
        }
    ).assign(
        survey="us",
        variable=variable,
        concept=us_concept(variable, year, quarter),
        year=year,
        quarter=quarter,
        target_year=target_year,
        horizon_class=horizon_class,
        horizon_years=horizon_years,
        horizon_quarters=horizon_quarters,
        bin_scheme=scheme.name,
        target_block=target_block,
    )


def us_target_offsets(variable: str, year: int, quarter: int) -> tuple[int | None, ...]:
    """Return target-year offsets for each contiguous block in a density file."""
    name = _density_variable(variable)
    date = (int(year), int(quarter))
    if not _density_active(name, *date):
        raise ValueError(f"{name} was not active in {date[0]}Q{date[1]}")
    if name in {"PRGDP", "PRPGDP"} and date <= (1981, 2):
        return (1,) if date in _EARLY_NEXT_YEAR_ROUNDS else (0,)
    if name in {"PRGDP", "PRPGDP"} and date in _AMBIGUOUS_TARGET_ROUNDS:
        return (None, None)
    if name in {"PRGDP", "PRUNEMP"} and date >= (2009, 2):
        return 0, 1, 2, 3
    return 0, 1


def us_concept(variable: str, year: int, quarter: int) -> str:
    """Return the elicited target concept documented for a US SPF round."""
    name = variable.upper()
    date = (int(year), int(quarter))
    if name == "PRGDP":
        if date <= (1981, 2):
            return "nominal_gnp"
        if date <= (1991, 4):
            return "real_gnp"
        return "real_gdp"
    if name == "PRPGDP":
        if date <= (1991, 4):
            return "gnp_implicit_deflator"
        if date <= (1995, 4):
            return "gdp_implicit_deflator"
        return "chain_weighted_gdp_price_index"
    if name == "PRCCPI":
        return "core_cpi"
    if name == "PRCPCE":
        return "chain_weighted_core_pce"
    if name == "PRUNEMP":
        return "civilian_unemployment_rate"
    if name == "RECESS":
        if date <= (1991, 4):
            return "fixed_weighted_real_gnp"
        if date <= (1995, 4):
            return "fixed_weighted_real_gdp"
        return "chain_weighted_real_gdp"
    raise KeyError(f"Unknown US SPF variable: {variable}")


def _horizon_class(offset: int) -> str:
    return {
        0: "current_year",
        1: "next_year",
        2: "year_after_next",
        3: "three_years_ahead",
    }[offset]


def _density_active(variable: str, year: int, quarter: int) -> bool:
    date = (year, quarter)
    starts = {
        "PRGDP": (1968, 4),
        "PRPGDP": (1968, 4),
        "PRCCPI": (2007, 1),
        "PRCPCE": (2007, 1),
        "PRUNEMP": (2009, 2),
    }
    return date >= starts[variable]


def _density_variable(variable: str) -> str:
    name = variable.upper()
    if name not in DENSITY_VARIABLES:
        raise KeyError(f"Unknown US density variable: {variable}")
    return name


def longrun_point_stats(
    variable: str,
    path: str | Path | None = None,
    data_dir: str | Path = DEFAULT_DATA_DIR,
) -> pd.DataFrame:
    """Compute per-round cross-sectional statistics for one long-run point forecast."""
    name = variable.upper()
    if name not in LONGRUN_VARIABLES:
        raise KeyError(f"Unknown US long-run point variable: {variable}")
    source = Path(path) if path is not None else _individual_path(name, data_dir)
    frame = _read_excel(source)
    required = {"YEAR", "QUARTER", "ID", name}
    missing = required.difference(frame.columns)
    if missing:
        raise ValueError(f"Missing required {name} columns: {sorted(missing)}")
    values = frame[["YEAR", "QUARTER", "ID", name]].copy()
    values[name] = _numeric_values(values[name], context=name)
    values = values.dropna(subset=[name])

    rows: list[dict[str, float | int | str]] = []
    for (year, quarter), group in values.groupby(["YEAR", "QUARTER"], sort=True):
        observations = group[name].to_numpy(dtype=float)
        rows.append(
            {
                "survey": "us",
                "variable": name,
                "year": int(year),
                "quarter": int(quarter),
                "n": len(observations),
                "mean": float(observations.mean()),
                "median": float(np.median(observations)),
                "sd": (
                    float(observations.std(ddof=1)) if len(observations) > 1 else np.nan
                ),
                "iqr": float(
                    np.quantile(observations, 0.75) - np.quantile(observations, 0.25)
                ),
            }
        )
    return pd.DataFrame(
        rows,
        columns=[
            "survey",
            "variable",
            "year",
            "quarter",
            "n",
            "mean",
            "median",
            "sd",
            "iqr",
        ],
    )


def parse_longrun_points(
    data_dir: str | Path = DEFAULT_DATA_DIR,
    variables: Iterable[str] = LONGRUN_VARIABLES,
    *,
    strict: bool = False,
) -> pd.DataFrame:
    """Combine long-run point statistics, reporting malformed local inputs."""
    frames: list[pd.DataFrame] = []
    errors: dict[str, str] = {}
    for variable in variables:
        try:
            frames.append(longrun_point_stats(variable, data_dir=data_dir))
        except (FileNotFoundError, OSError, ValueError) as error:
            if strict:
                raise
            name = variable.upper()
            errors[name] = str(error)
            warnings.warn(f"Skipping {name}: {error}", stacklevel=2)
    output = (
        pd.concat(frames, ignore_index=True)
        if frames
        else pd.DataFrame(
            columns=[
                "survey",
                "variable",
                "year",
                "quarter",
                "n",
                "mean",
                "median",
                "sd",
                "iqr",
            ]
        )
    )
    output.attrs["errors"] = errors
    return output


def recess_stats(
    path: str | Path | None = None,
    data_dir: str | Path = DEFAULT_DATA_DIR,
) -> pd.DataFrame:
    """Compute round statistics for probabilities of quarterly GDP declines."""
    source = Path(path) if path is not None else _individual_path("RECESS", data_dir)
    return recess_stats_from_frame(_read_excel(source))


def recess_stats_from_frame(frame: pd.DataFrame) -> pd.DataFrame:
    """Compute RECESS statistics from an already-loaded individual-response sheet."""
    probability_columns = [f"RECESS{index}" for index in range(1, 6)]
    required = {"YEAR", "QUARTER", "ID", *probability_columns}
    missing = required.difference(frame.columns)
    if missing:
        raise ValueError(f"Missing required RECESS columns: {sorted(missing)}")

    rows: list[dict[str, float | int | str]] = []
    for (raw_year, raw_quarter), group in frame.groupby(["YEAR", "QUARTER"], sort=True):
        year, quarter = int(raw_year), int(raw_quarter)
        for index, column in enumerate(probability_columns):
            observations = _numeric_values(group[column], context=column).dropna()
            if observations.empty:
                continue
            target_year, target_quarter = _shift_quarter(year, quarter, index)
            rows.append(
                {
                    "survey": "us",
                    "variable": "RECESS",
                    "concept": us_concept("RECESS", year, quarter),
                    "year": year,
                    "quarter": quarter,
                    "horizon_quarter": index,
                    "target_year": target_year,
                    "target_quarter": target_quarter,
                    "n": len(observations),
                    "mean_probability": float(observations.mean()),
                    "median": float(observations.median()),
                    "disagreement": (
                        float(observations.std(ddof=1))
                        if len(observations) > 1
                        else np.nan
                    ),
                }
            )
    return pd.DataFrame(
        rows,
        columns=[
            "survey",
            "variable",
            "concept",
            "year",
            "quarter",
            "horizon_quarter",
            "target_year",
            "target_quarter",
            "n",
            "mean_probability",
            "median",
            "disagreement",
        ],
    )


def _shift_quarter(year: int, quarter: int, offset: int) -> tuple[int, int]:
    zero_based = year * 4 + (quarter - 1) + offset
    return zero_based // 4, zero_based % 4 + 1


def _individual_path(variable: str, data_dir: str | Path) -> Path:
    return Path(data_dir) / f"individual_{variable.lower()}.xlsx"


def _numeric_values(values: pd.Series, *, context: str) -> pd.Series:
    numeric = pd.to_numeric(values, errors="coerce")
    invalid = values.notna() & numeric.isna()
    if invalid.any():
        raise ValueError(
            f"Nonnumeric value in {context}: {values.loc[invalid].iloc[0]!r}"
        )
    return numeric


def _read_excel(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(path)
    if path.suffix.lower() == ".xlsx" and not zipfile.is_zipfile(path):
        raise ValueError(f"Not a valid XLSX workbook: {path}")
    return pd.read_excel(path)


load_us_density = parse_us_density
load_us_densities = parse_all_us_densities
load_longrun_points = parse_longrun_points
parse_recess = recess_stats
