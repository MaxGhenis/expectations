"""Archived realization series and forecast-calibration helpers.

The local files contain revised observations, not the real-time vintages that were
available when forecasts were submitted.  Loaders therefore expose source metadata
and never fill incomplete calendar years or missing target concepts.
"""

from __future__ import annotations

import calendar
import hashlib
import json
import re
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

DEFAULT_RAW_DIR = Path(__file__).resolve().parents[2] / "data" / "raw"

# Archived Eurostat EA20 comparator, pinned in the same manifest as the ECB
# companions. It is compared against the emitted ECB annual rate, never emitted.
EUROSTAT_EA20_ANNUAL_GDP_FILE = "eurostat_ea20_rgdp_growth_annual.json"
EUROSTAT_EA20_ANNUAL_GDP_URL = (
    "https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/"
    "nama_10_gdp?format=JSON&geo=EA20&na_item=B1GQ&unit=CLV_PCH_PRE"
)
EUROSTAT_EA20_ANNUAL_GDP_DIMENSIONS = {
    "freq": "A",
    "unit": "CLV_PCH_PRE",
    "na_item": "B1GQ",
    "geo": "EA20",
}

REALIZATION_COLUMNS = [
    "survey",
    "variable",
    "target_year",
    "target_period",
    "realized",
    "realization_concept",
    "source",
    "observation_status",
]

_MONTH_ABBREVIATIONS = {
    index: name for index, name in enumerate(calendar.month_abbr) if index
}
_MONTH_NUMBERS = {name.lower(): index for index, name in _MONTH_ABBREVIATIONS.items()}

_US_CALIBRATION_START_YEARS = {
    "prgdp": 1992,
    "prpgdp": 1992,
    "prunemp": 2009,
    "prccpi": 2007,
    "prcpce": 2007,
    "recess": 1992,
}
_US_FULL_HISTORY_START_YEARS = {variable: 0 for variable in _US_CALIBRATION_START_YEARS}

# Official annual companion series: pinned key, emitted concept, precision note.
# GDP uses the publisher's own annual growth rate rather than any aggregation of
# quarterly levels; the manifest records that it equals growth in sums of the
# non-adjusted quarterly levels and how far the superseded adjusted-level sums
# departed from it.
_ECB_ANNUAL_COMPANIONS = {
    "rgdp": (
        "MNA.A.N.I9.W2.S1.S1.B.B1GQ._Z._Z._Z.EUR_R_B1GQ.Y.GOY",
        "official_annual_real_gdp_growth_rate",
        "official annual growth rate, non-adjusted, previous-year prices",
    ),
    "hicp": (
        "ICP.A.U2.N.000000.4.AVR",
        "annual_average_hicp_index_growth",
        "official AVR rounded to 0.1 percentage point",
    ),
    "hicpx": (
        "ICP.A.U2.N.XEF000.4.AVR",
        "annual_average_hicpx_index_growth",
        "official AVR rounded to 0.1 percentage point",
    ),
}


def load_us_realizations(raw_dir: str | Path = DEFAULT_RAW_DIR) -> pd.DataFrame:
    """Return documented US SPF realization mappings in tidy form.

    Mappings begin in 1992, when the output target switches from GNP to GDP.
    Annual unemployment and fourth-quarter inflation observations are emitted only
    when every required source month is present.  ``recess`` is expressed on the
    survey's percentage-point scale: 100 for a real-GDP decline and 0 otherwise.
    """
    return _load_us_realizations(raw_dir, start_years=_US_CALIBRATION_START_YEARS)


def load_us_realization_history(
    raw_dir: str | Path = DEFAULT_RAW_DIR,
) -> pd.DataFrame:
    """Return the longest compatible US realization histories available locally.

    Unlike :func:`load_us_realizations`, this loader does not trim observations to
    each density survey's calibration era.  It is intended for strictly expanding
    benchmark windows; joining it directly to forecasts still requires the usual
    survey-concept compatibility checks.
    """
    return _load_us_realizations(raw_dir, start_years=_US_FULL_HISTORY_START_YEARS)


def _load_us_realizations(
    raw_dir: str | Path,
    *,
    start_years: dict[str, int],
) -> pd.DataFrame:
    directory = Path(raw_dir)
    frames: list[pd.DataFrame] = []

    real_gdp = _load_dbnomics_series(directory / "dbnomics_us_rgdp_growth_annual.json")
    frames.append(
        _annual_rows(
            real_gdp,
            survey="us_spf",
            variable="prgdp",
            start_year=start_years["prgdp"],
            concept="annual_average_real_gdp_growth",
            source="BEA NIPA-T10101/A191RL-A (latest vintage)",
        )
    )

    gdp_price = _load_dbnomics_series(
        directory / "dbnomics_us_gdp_price_index_annual.json"
    )
    gdp_price_growth = _annual_growth(gdp_price)
    frames.append(
        _annual_rows(
            gdp_price_growth,
            survey="us_spf",
            variable="prpgdp",
            start_year=start_years["prpgdp"],
            concept="annual_average_gdp_price_index_growth",
            source="BEA NIPA-T10104/A191RG-A (latest vintage)",
        )
    )

    unemployment = _load_dbnomics_series(directory / "dbnomics_us_unrate_monthly.json")
    frames.append(
        _annual_rows(
            _complete_period_averages(unemployment, frequency="monthly"),
            survey="us_spf",
            variable="prunemp",
            start_year=start_years["prunemp"],
            concept="annual_average_civilian_unemployment_rate",
            source="BLS LNS14000000 (latest vintage)",
        )
    )

    core_cpi = _load_dbnomics_series(directory / "dbnomics_us_corecpi_sa_monthly.json")
    frames.append(
        _annual_rows(
            _q4_over_q4_growth(core_cpi),
            survey="us_spf",
            variable="prccpi",
            start_year=start_years["prccpi"],
            concept="q4_over_q4_core_cpi_inflation",
            source="BLS CUSR0000SA0L1E (latest vintage)",
        )
    )

    core_pce = _load_dbnomics_series(
        directory / "dbnomics_us_corepce_price_monthly.json"
    )
    frames.append(
        _annual_rows(
            _q4_over_q4_growth(core_pce),
            survey="us_spf",
            variable="prcpce",
            start_year=start_years["prcpce"],
            concept="q4_over_q4_core_pce_inflation",
            source="BEA NIPA-T20804/DPCCRG-M (latest vintage)",
        )
    )

    quarterly_gdp = _load_dbnomics_series(
        directory / "dbnomics_us_rgdp_growth_quarterly.json"
    )
    frames.append(_recession_rows(quarterly_gdp, start_year=start_years["recess"]))
    return _finish_realizations(pd.concat(frames, ignore_index=True))


def load_ecb_realizations(raw_dir: str | Path = DEFAULT_RAW_DIR) -> pd.DataFrame:
    """Return calendar-year and rolling-period ECB SPF realizations.

    Calendar GDP growth is the publisher's official annual growth rate, and
    calendar inflation the official annual-average index-growth series (AVR),
    published to 0.1 percentage point. Neither is reconstructed from subannual
    observations: growth in summed quarterly levels and mean subannual
    year-on-year growth are both distinct from the published annual rate.
    Annual unemployment remains the mean of twelve monthly rates, as no official
    annual companion is archived for it. Rolling targets retain their archived
    source snapshots; per-source annual companion retrieval dates and the unknown
    rolling retrieval dates are distinguished in source metadata.

    ``observation_status`` reports every published flag behind a value, so a
    provisional input is never hidden by a final aggregate flag:

    * ``hicp``, ``hicpx``, ``rgdp`` calendar years: the union of the official
      annual observation's own status and the archived subannual statuses for
      the same calendar year, when that archive year is complete. A calendar
      year published after the frozen archive ends keeps the annual
      observation's own status alone.
    * ``unemp`` calendar years: the union of the twelve monthly archive
      statuses, which are also the only source of the value.
    * Rolling targets: the status of that single archived observation.
    """
    directory = Path(raw_dir)
    specifications = (
        (
            "hicp",
            directory / "ecb_ea_hicp_yoy_monthly.csv",
            "monthly",
            "year_on_year_hicp_inflation",
            "ECB Data Portal ICP.M.U2.N.000000.4.ANR",
        ),
        (
            "hicpx",
            directory / "ecb_ea_hicpx_yoy_monthly.csv",
            "monthly",
            "year_on_year_hicpx_inflation",
            "ECB Data Portal ICP.M.U2.N.XEF000.4.ANR",
        ),
        (
            "rgdp",
            directory / "ecb_ea_rgdp_yoy_quarterly.csv",
            "quarterly",
            "year_on_year_real_gdp_growth",
            ("ECB Data Portal MNA.Q.Y.I9.W2.S1.S1.B.B1GQ._Z._Z._Z.EUR.LR.GY"),
        ),
        (
            "unemp",
            directory / "ecb_ea_unemployment_monthly.csv",
            "monthly",
            "unemployment_rate",
            "ECB Data Portal LFSI.M.I9.S.UNEHRT.TOTAL0.15_74.T",
        ),
    )
    frames: list[pd.DataFrame] = []
    for variable, path, frequency, concept, source in specifications:
        source += " (archived snapshot; original retrieval date unrecorded)"
        observations = _load_ecb_series(path)
        frames.append(
            _ecb_rolling_rows(
                observations,
                variable=variable,
                frequency=frequency,
                concept=concept,
                source=source,
            )
        )
        if variable == "unemp":
            annual = _ecb_annual_rows(
                observations,
                variable=variable,
                frequency=frequency,
                concept=f"calendar_year_average_{concept}",
                source=source,
            )
        else:
            annual = _load_ecb_calendar_growth(directory, variable=variable)
            archive_statuses = _complete_period_statuses(
                observations, frequency=frequency
            )
            annual = _corroborated_annual_companion(
                annual, archive_statuses, variable=variable
            )
        frames.append(annual)
    return _finish_realizations(pd.concat(frames, ignore_index=True))


def _corroborated_annual_companion(
    annual: pd.DataFrame, archive_statuses: dict[str, str], *, variable: str
) -> pd.DataFrame:
    """Keep the archive's calendar targets and any later published year.

    Missing companion years must fail rather than silently drop scores, so every
    complete year of the frozen rolling archive has to be present. Companion
    years the archive cannot corroborate are then kept or dropped by position:
    every year from the archive's first complete year onwards is kept, including
    a complete year published after the archive ends, while earlier years have
    no subannual snapshot behind them at all and are dropped. Statuses take the
    union of the annual observation's own flag and the archive's flags for that
    year.
    """
    expected_years = set(archive_statuses)
    missing_years = expected_years.difference(annual["target_period"])
    if missing_years:
        raise ValueError(
            f"Missing ECB {variable} annual companion years: {sorted(missing_years)}"
        )
    if expected_years:
        first_expected = min(int(year) for year in expected_years)
        annual = annual[annual["target_year"] >= first_expected].copy()
    else:
        annual = annual.copy()
    annual["observation_status"] = [
        _union_statuses(own, archive_statuses.get(year))
        for year, own in zip(
            annual["target_period"], annual["observation_status"], strict=True
        )
    ]
    return annual


def _union_statuses(*statuses: object) -> str:
    """Join every distinct observation flag behind one emitted value."""
    flags = {
        flag
        for status in statuses
        if status is not None and not pd.isna(status)
        for flag in str(status).split("+")
        if flag.strip()
    }
    if not flags:
        raise ValueError("Realization rows require at least one observation status")
    return "+".join(sorted(flags))


def _load_ecb_calendar_growth(directory: Path, *, variable: str) -> pd.DataFrame:
    """Read one verified official annual growth series at publisher precision."""
    expected_key, concept, qualifier = _ECB_ANNUAL_COMPANIONS[variable]
    filename = f"ecb_ea_{variable}_growth_annual.csv"
    observations, source = _load_verified_ecb_companion(
        directory, filename=filename, expected_key=expected_key
    )
    if not observations["TIME_PERIOD"].str.fullmatch(r"\d{4}").all():
        raise ValueError(f"Invalid annual ECB periods in {filename}")
    frame = _annual_rows(
        observations.set_index("TIME_PERIOD")["OBS_VALUE"],
        survey="ecb_spf",
        variable=variable,
        start_year=0,
        concept=concept,
        source=f"{source}; {qualifier}",
    )
    statuses = observations.set_index("TIME_PERIOD")["OBS_STATUS"]
    frame["observation_status"] = frame["target_period"].map(statuses)
    return frame


def _verified_manifest_payload(
    directory: Path, *, filename: str, expected_url: str, label: str
) -> tuple[bytes, dict[str, Any]]:
    """Return archived bytes only when the manifest pins this exact response.

    The manifest is the single provenance register for every archived annual
    source: the recorded URL must be the one we meant to fetch, and the recorded
    checksum must match the committed bytes.  A source whose entry is missing,
    repointed or stale therefore fails loudly instead of being read.
    """
    manifest = json.loads(
        (directory / "ecb_annual_realizations_sources.json").read_text()
    )
    entry = manifest["sources"][filename]
    payload = (directory / filename).read_bytes()
    if entry["url"] != expected_url:
        raise ValueError(f"Unexpected {label} source identity for {filename}")
    if hashlib.sha256(payload).hexdigest() != entry["sha256"]:
        raise ValueError(f"{label} source checksum mismatch for {filename}")
    if not entry.get("retrieved_at_utc"):
        raise ValueError(f"Missing {label} source retrieval date for {filename}")
    return payload, entry


def _load_verified_ecb_companion(
    directory: Path, *, filename: str, expected_key: str
) -> tuple[pd.DataFrame, str]:
    path = directory / filename
    flow, series = expected_key.split(".", 1)
    expected_url = (
        f"https://data-api.ecb.europa.eu/service/data/{flow}/{series}?format=csvdata"
    )
    _, entry = _verified_manifest_payload(
        directory, filename=filename, expected_url=expected_url, label="ECB annual"
    )
    if entry["series_key"] != expected_key:
        raise ValueError(f"Unexpected ECB annual source identity for {filename}")
    keys = pd.read_csv(path, usecols=["KEY"])["KEY"]
    if keys.empty or not keys.eq(expected_key).all():
        raise ValueError(f"Unexpected ECB series key in {filename}")
    source = (
        f"ECB Data Portal {expected_key} (annual companion retrieved "
        f"{entry['retrieved_at_utc']}; rolling archive retrieval date unrecorded)"
    )
    return _load_ecb_series(path), source


def load_eurostat_ea20_annual_growth(
    raw_dir: str | Path = DEFAULT_RAW_DIR,
) -> pd.Series:
    """Return archived Eurostat EA20 annual real GDP growth, indexed by year.

    This series is a provenance comparator, never an emitted outcome: the
    euro-area annual GDP outcome this repository scores against is the ECB's own
    published annual growth rate.  Eurostat's EA20 aggregate is a different
    official publication of a related concept, so the two differ in some years at
    one decimal, and archiving the response makes that recorded difference
    reproducible offline instead of dependent on a refetch.
    """
    payload, _ = _verified_manifest_payload(
        Path(raw_dir),
        filename=EUROSTAT_EA20_ANNUAL_GDP_FILE,
        expected_url=EUROSTAT_EA20_ANNUAL_GDP_URL,
        label="Eurostat comparator",
    )
    dataset = json.loads(payload.decode("utf-8"))
    for dimension, expected in EUROSTAT_EA20_ANNUAL_GDP_DIMENSIONS.items():
        categories = set(dataset["dimension"][dimension]["category"]["index"])
        if categories != {expected}:
            raise ValueError(
                f"Eurostat comparator {dimension} is {sorted(categories)}, "
                f"not {expected!r}"
            )
    periods = {
        position: period
        for period, position in dataset["dimension"]["time"]["category"][
            "index"
        ].items()
    }
    values = {
        periods[int(position)]: float(value)
        for position, value in dataset["value"].items()
    }
    return pd.Series(values, name="realized", dtype=float).sort_index()


def load_realizations(raw_dir: str | Path = DEFAULT_RAW_DIR) -> pd.DataFrame:
    """Load every local, concept-matched US and ECB realization."""
    return _finish_realizations(
        pd.concat(
            [load_us_realizations(raw_dir), load_ecb_realizations(raw_dir)],
            ignore_index=True,
        )
    )


def load_realization_history(
    raw_dir: str | Path = DEFAULT_RAW_DIR,
) -> pd.DataFrame:
    """Load the longest local histories for expanding forecast benchmarks."""
    return _finish_realizations(
        pd.concat(
            [
                load_us_realization_history(raw_dir),
                load_ecb_realizations(raw_dir),
            ],
            ignore_index=True,
        )
    )


def calibration_table(
    measures: pd.DataFrame,
    realizations: pd.DataFrame | None = None,
    *,
    raw_dir: str | Path = DEFAULT_RAW_DIR,
) -> pd.DataFrame:
    """Inner-join density measures to verified realizations and score coverage.

    The calibration error follows the validated seed convention:
    ``realized - consensus_mean``.  Interval checks are inclusive and nullable;
    missing dispersion or quantiles never become a false non-coverage result.
    """
    required = {"survey", "variable", "mean", "total_sd", "q05", "q95"}
    missing = sorted(required.difference(measures.columns))
    if missing:
        raise ValueError(f"Measures are missing required columns: {missing}")
    if "target_period" not in measures and "target_year" not in measures:
        raise ValueError("Measures require target_period or target_year")

    actuals = (
        load_realizations(raw_dir) if realizations is None else realizations.copy()
    )
    actual_required = {"survey", "variable", "target_period", "realized"}
    missing_actual = sorted(actual_required.difference(actuals.columns))
    if missing_actual:
        raise ValueError(f"Realizations are missing required columns: {missing_actual}")

    forecasts = measures.copy()
    forecasts["_survey_key"] = forecasts["survey"].map(_canonical_survey)
    forecasts["_variable_key"] = [
        _canonical_variable(survey, variable)
        for survey, variable in zip(
            forecasts["_survey_key"], forecasts["variable"], strict=False
        )
    ]
    forecasts = _compatible_forecast_concepts(forecasts)
    forecasts["_target_key"] = _measure_target_keys(forecasts)

    actuals["_survey_key"] = actuals["survey"].map(_canonical_survey)
    actuals["_variable_key"] = [
        _canonical_variable(survey, variable)
        for survey, variable in zip(
            actuals["_survey_key"], actuals["variable"], strict=False
        )
    ]
    actuals["_target_key"] = actuals["target_period"].map(_canonical_target_period)
    duplicate_keys = actuals.duplicated(
        ["_survey_key", "_variable_key", "_target_key"], keep=False
    )
    if duplicate_keys.any():
        keys = actuals.loc[
            duplicate_keys, ["_survey_key", "_variable_key", "_target_key"]
        ].drop_duplicates()
        raise ValueError(f"Duplicate realization keys: {keys.to_dict('records')}")

    metadata_columns = [
        column
        for column in (
            "_survey_key",
            "_variable_key",
            "_target_key",
            "realized",
            "realization_concept",
            "source",
            "observation_status",
        )
        if column in actuals
    ]
    result = forecasts.merge(
        actuals[metadata_columns],
        on=["_survey_key", "_variable_key", "_target_key"],
        how="inner",
        validate="many_to_one",
    )
    result["consensus_mean"] = pd.to_numeric(result["mean"], errors="coerce")
    result["realized"] = pd.to_numeric(result["realized"], errors="coerce")
    result["error"] = result["realized"] - result["consensus_mean"]

    result["inside_1sd"] = _nullable_inside(
        result["error"].abs(), pd.to_numeric(result["total_sd"], errors="coerce")
    )
    lower = pd.to_numeric(result["q05"], errors="coerce")
    upper = pd.to_numeric(result["q95"], errors="coerce")
    realized = result["realized"]
    valid_90 = realized.notna() & lower.notna() & upper.notna()
    inside_90 = pd.Series(pd.NA, index=result.index, dtype="boolean")
    inside_90.loc[valid_90] = (realized.loc[valid_90] >= lower.loc[valid_90]) & (
        realized.loc[valid_90] <= upper.loc[valid_90]
    )
    result["inside_pooled_90"] = inside_90
    return result.drop(columns=["_survey_key", "_variable_key", "_target_key"])


def _load_dbnomics_series(path: Path) -> pd.Series:
    with path.open(encoding="utf-8") as file:
        payload: dict[str, Any] = json.load(file)
    try:
        documents = payload["series"]["docs"]
        document = documents[0]
        periods = document["period"]
        values = document["value"]
    except (KeyError, IndexError, TypeError) as error:
        raise ValueError(f"Unexpected DBnomics structure in {path}") from error
    if len(documents) != 1 or len(periods) != len(values):
        raise ValueError(f"Invalid DBnomics series dimensions in {path}")
    if len(periods) != len(set(periods)):
        raise ValueError(f"Duplicate DBnomics periods in {path}")
    numeric = pd.to_numeric(pd.Series(values, index=pd.Index(periods)), errors="coerce")
    if numeric.isna().any():
        bad = numeric.index[numeric.isna()].tolist()
        raise ValueError(f"Missing or nonnumeric DBnomics values in {path}: {bad}")
    return numeric.astype(float).sort_index()


def _load_ecb_series(path: Path) -> pd.DataFrame:
    observations = pd.read_csv(
        path,
        usecols=["TIME_PERIOD", "OBS_VALUE", "OBS_STATUS"],
        dtype={"TIME_PERIOD": "string", "OBS_STATUS": "string"},
    )
    observations["OBS_VALUE"] = pd.to_numeric(
        observations["OBS_VALUE"], errors="coerce"
    )
    if observations[["TIME_PERIOD", "OBS_VALUE"]].isna().any().any():
        raise ValueError(f"Missing ECB realization period or value in {path}")
    if observations["TIME_PERIOD"].duplicated().any():
        raise ValueError(f"Duplicate ECB realization periods in {path}")
    # A blank flag would otherwise reach status unions as the string "nan".
    observations["OBS_STATUS"] = observations["OBS_STATUS"].str.strip()
    if (
        observations["OBS_STATUS"].isna().any()
        or observations["OBS_STATUS"].eq("").any()
    ):
        raise ValueError(f"Missing ECB observation status in {path}")
    return observations.sort_values("TIME_PERIOD").reset_index(drop=True)


def _annual_growth(levels: pd.Series) -> pd.Series:
    indexed = {int(period): float(value) for period, value in levels.items()}
    growth = {
        str(year): 100.0 * (value / indexed[year - 1] - 1.0)
        for year, value in indexed.items()
        if year - 1 in indexed
    }
    return pd.Series(growth, dtype=float).sort_index()


def _complete_period_averages(series: pd.Series, *, frequency: str) -> pd.Series:
    parsed = _parsed_periods(series, frequency=frequency)
    expected = 12 if frequency == "monthly" else 4
    output: dict[str, float] = {}
    for year, group in parsed.groupby("year", sort=True):
        positions = set(group["position"].astype(int))
        if len(group) == expected and positions == set(range(1, expected + 1)):
            output[str(int(year))] = float(group["value"].mean())
    return pd.Series(output, dtype=float)


def _q4_over_q4_growth(series: pd.Series) -> pd.Series:
    parsed = _parsed_periods(series, frequency="monthly")
    q4: dict[int, float] = {}
    for year, group in parsed.groupby("year", sort=True):
        quarter = group[group["position"].isin((10, 11, 12))]
        if set(quarter["position"].astype(int)) == {10, 11, 12}:
            q4[int(year)] = float(quarter["value"].mean())
    growth = {
        str(year): 100.0 * (value / q4[year - 1] - 1.0)
        for year, value in q4.items()
        if year - 1 in q4
    }
    return pd.Series(growth, dtype=float).sort_index()


def _parsed_periods(series: pd.Series, *, frequency: str) -> pd.DataFrame:
    pattern = r"^(\d{4})-(\d{2})$" if frequency == "monthly" else r"^(\d{4})-Q([1-4])$"
    records: list[tuple[int, int, float]] = []
    for period, value in series.items():
        match = re.fullmatch(pattern, str(period))
        if match is None:
            raise ValueError(f"Invalid {frequency} realization period: {period}")
        records.append((int(match.group(1)), int(match.group(2)), float(value)))
    return pd.DataFrame(records, columns=["year", "position", "value"])


def _annual_rows(
    series: pd.Series,
    *,
    survey: str,
    variable: str,
    start_year: int,
    concept: str,
    source: str,
) -> pd.DataFrame:
    rows = [
        {
            "survey": survey,
            "variable": variable,
            "target_year": year,
            "target_period": str(year),
            "realized": float(value),
            "realization_concept": concept,
            "source": source,
            "observation_status": pd.NA,
        }
        for period, value in series.items()
        if (year := int(period)) >= start_year
    ]
    return pd.DataFrame(rows, columns=REALIZATION_COLUMNS)


def _recession_rows(series: pd.Series, *, start_year: int) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for period, growth in series.items():
        match = re.fullmatch(r"(\d{4})-Q([1-4])", str(period))
        if match is None:
            raise ValueError(f"Invalid quarterly real-GDP period: {period}")
        year, quarter = int(match.group(1)), int(match.group(2))
        if year < start_year:
            continue
        rows.append(
            {
                "survey": "us_spf",
                "variable": "recess",
                "target_year": year,
                "target_period": f"{year}Q{quarter}",
                "realized": 100.0 if float(growth) < 0 else 0.0,
                "realization_concept": "quarterly_real_gdp_decline_indicator",
                "source": "BEA NIPA-T10101/A191RL-Q (latest vintage)",
                "observation_status": pd.NA,
            }
        )
    return pd.DataFrame(rows, columns=REALIZATION_COLUMNS)


def _ecb_rolling_rows(
    observations: pd.DataFrame,
    *,
    variable: str,
    frequency: str,
    concept: str,
    source: str,
) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    pattern = r"(\d{4})-(\d{2})" if frequency == "monthly" else r"(\d{4})-Q([1-4])"
    for row in observations.itertuples(index=False):
        match = re.fullmatch(pattern, str(row.TIME_PERIOD))
        if match is None:
            raise ValueError(f"Invalid ECB {frequency} period: {row.TIME_PERIOD}")
        year, position = int(match.group(1)), int(match.group(2))
        target = (
            f"{year}{_MONTH_ABBREVIATIONS[position]}"
            if frequency == "monthly"
            else f"{year}Q{position}"
        )
        rows.append(
            {
                "survey": "ecb_spf",
                "variable": variable,
                "target_year": year,
                "target_period": target,
                "realized": float(row.OBS_VALUE),
                "realization_concept": concept,
                "source": source,
                "observation_status": row.OBS_STATUS,
            }
        )
    return pd.DataFrame(rows, columns=REALIZATION_COLUMNS)


def _ecb_annual_rows(
    observations: pd.DataFrame,
    *,
    variable: str,
    frequency: str,
    concept: str,
    source: str,
) -> pd.DataFrame:
    values = pd.Series(
        observations["OBS_VALUE"].to_numpy(),
        index=observations["TIME_PERIOD"].astype(str),
        dtype=float,
    )
    annual = _complete_period_averages(values, frequency=frequency)
    statuses = _complete_period_statuses(observations, frequency=frequency)
    frame = _annual_rows(
        annual,
        survey="ecb_spf",
        variable=variable,
        start_year=0,
        concept=concept,
        source=source,
    )
    frame["observation_status"] = frame["target_period"].map(statuses).astype("string")
    return frame


def _ecb_level_annual_rows(
    observations: pd.DataFrame,
    *,
    variable: str,
    frequency: str,
    concept: str,
    source: str,
) -> pd.DataFrame:
    """Growth in annual levels, requiring both full consecutive years.

    The ratio of two complete annual means equals the ratio of their sums. No
    emitted realization is built this way: every calendar-year outcome now comes
    from a published annual series. This remains the reconstruction that
    cross-checks those published series against their own subannual levels,
    which is how the official annual inflation rate is verified in the tests.
    Status flags include every source observation in numerator and denominator.
    """
    if (observations["OBS_VALUE"] <= 0).any():
        raise ValueError("Annual growth requires strictly positive ECB levels")
    levels = observations.set_index("TIME_PERIOD")["OBS_VALUE"]
    annual = _complete_period_averages(levels, frequency=frequency)
    growth = _annual_growth(annual)
    statuses = _complete_period_statuses(observations, frequency=frequency)
    frame = _annual_rows(
        growth,
        survey="ecb_spf",
        variable=variable,
        start_year=0,
        concept=concept,
        source=source,
    )
    frame["observation_status"] = frame["target_period"].map(
        lambda year: _union_statuses(statuses[year], statuses[str(int(year) - 1)])
    )
    return frame


def _complete_period_statuses(
    observations: pd.DataFrame, *, frequency: str
) -> dict[str, str]:
    expected = 12 if frequency == "monthly" else 4
    pattern = r"^(\d{4})-(\d{2})$" if frequency == "monthly" else r"^(\d{4})-Q([1-4])$"
    parsed: list[tuple[str, int, str]] = []
    for period, status in zip(
        observations["TIME_PERIOD"], observations["OBS_STATUS"], strict=False
    ):
        match = re.fullmatch(pattern, str(period))
        if match is None:
            raise ValueError(f"Invalid ECB {frequency} period: {period}")
        parsed.append((match.group(1), int(match.group(2)), str(status)))
    frame = pd.DataFrame(parsed, columns=["year", "position", "status"])
    output: dict[str, str] = {}
    for year, group in frame.groupby("year", sort=True):
        if len(group) != expected or set(group["position"]) != set(
            range(1, expected + 1)
        ):
            continue
        output[str(year)] = _union_statuses(*group["status"])
    return output


def _finish_realizations(frame: pd.DataFrame) -> pd.DataFrame:
    output = frame.reindex(columns=REALIZATION_COLUMNS).copy()
    output["target_year"] = pd.array(output["target_year"], dtype="Int64")
    output["target_period"] = output["target_period"].astype("string")
    output["realized"] = pd.to_numeric(output["realized"], errors="raise")
    output["observation_status"] = output["observation_status"].astype("string")
    key = ["survey", "variable", "target_period"]
    if output.duplicated(key).any():
        duplicates = output.loc[output.duplicated(key, keep=False), key]
        raise ValueError(f"Duplicate realization rows: {duplicates.to_dict('records')}")
    return output.sort_values(key, kind="stable").reset_index(drop=True)


def _measure_target_keys(frame: pd.DataFrame) -> pd.Series:
    if "target_period" in frame:
        target = frame["target_period"].map(_canonical_target_period)
    else:
        target = pd.Series(pd.NA, index=frame.index, dtype="string")
    if "target_year" in frame:
        years = frame["target_year"].map(_canonical_target_period)
        target = target.where(target.notna(), years)
    return target.astype("string")


def _canonical_target_period(value: object) -> object:
    if value is None or pd.isna(value):
        return pd.NA
    if isinstance(value, (int, np.integer)):
        return str(int(value))
    if isinstance(value, (float, np.floating)) and float(value).is_integer():
        return str(int(value))
    text = str(value).strip()
    if re.fullmatch(r"\d{4}\.0", text):
        return text[:4]
    if match := re.fullmatch(r"(\d{4})[- ]?Q([1-4])", text, flags=re.IGNORECASE):
        return f"{match.group(1)}Q{match.group(2)}"
    if match := re.fullmatch(r"(\d{4})[- ](\d{2})", text):
        month = int(match.group(2))
        if month in _MONTH_ABBREVIATIONS:
            return f"{match.group(1)}{_MONTH_ABBREVIATIONS[month]}"
    if match := re.fullmatch(r"([A-Za-z]{3})\s+(\d{4})", text):
        month = _MONTH_NUMBERS.get(match.group(1).lower())
        if month is not None:
            return f"{match.group(2)}{_MONTH_ABBREVIATIONS[month]}"
    if match := re.fullmatch(r"(\d{4})([A-Za-z]{3})", text):
        month = _MONTH_NUMBERS.get(match.group(2).lower())
        if month is not None:
            return f"{match.group(1)}{_MONTH_ABBREVIATIONS[month]}"
    return text


def _canonical_survey(value: object) -> str:
    key = re.sub(r"[^a-z0-9]+", "_", str(value).strip().lower()).strip("_")
    aliases = {
        "us": "us_spf",
        "us_spf": "us_spf",
        "spf_us": "us_spf",
        "philadelphia_spf": "us_spf",
        "ecb": "ecb_spf",
        "ecb_spf": "ecb_spf",
        "spf_ecb": "ecb_spf",
    }
    return aliases.get(key, key)


def _canonical_variable(survey: str, value: object) -> str:
    key = re.sub(r"[^a-z0-9]+", "_", str(value).strip().lower()).strip("_")
    if survey == "ecb_spf":
        aliases = {
            "growth": "rgdp",
            "gdp": "rgdp",
            "real_gdp": "rgdp",
            "real_gdp_growth": "rgdp",
            "real_gdp_yoy": "rgdp",
            "inflation": "hicp",
            "hicp_yoy": "hicp",
            "core_hicp": "hicpx",
            "core_inflation": "hicpx",
            "hicpx_yoy_ex_food_energy": "hicpx",
            "unemployment": "unemp",
            "unemployment_rate": "unemp",
        }
        return aliases.get(key, key)
    return key


def _compatible_forecast_concepts(frame: pd.DataFrame) -> pd.DataFrame:
    """Exclude US GNP-era forecasts before joining modern GDP realizations."""
    if "concept" not in frame:
        return frame
    survey = frame["_survey_key"]
    variable = frame["_variable_key"]
    concept = frame["concept"].astype("string")
    incompatible = (survey == "us_spf") & (
        ((variable == "prgdp") & (concept != "real_gdp"))
        | (
            (variable == "prpgdp")
            & ~concept.isin(["gdp_implicit_deflator", "chain_weighted_gdp_price_index"])
        )
    )
    return frame.loc[~incompatible].copy()


def _nullable_inside(distance: pd.Series, width: pd.Series) -> pd.Series:
    valid = distance.notna() & width.notna()
    output = pd.Series(pd.NA, index=distance.index, dtype="boolean")
    output.loc[valid] = distance.loc[valid] <= width.loc[valid]
    return output


__all__ = [
    "DEFAULT_RAW_DIR",
    "EUROSTAT_EA20_ANNUAL_GDP_DIMENSIONS",
    "EUROSTAT_EA20_ANNUAL_GDP_FILE",
    "EUROSTAT_EA20_ANNUAL_GDP_URL",
    "REALIZATION_COLUMNS",
    "calibration_table",
    "load_ecb_realizations",
    "load_eurostat_ea20_annual_growth",
    "load_realization_history",
    "load_realizations",
    "load_us_realization_history",
    "load_us_realizations",
]
