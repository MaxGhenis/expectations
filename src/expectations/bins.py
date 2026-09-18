"""Probability-bin definitions for the US and ECB SPF datasets."""

from __future__ import annotations

import re
from dataclasses import dataclass

type Interval = tuple[float | None, float | None]


@dataclass(frozen=True)
class BinScheme:
    """A named sequence of probability intervals in source-column order."""

    name: str
    intervals: tuple[Interval, ...]

    def __post_init__(self) -> None:
        if not self.name:
            raise ValueError("A bin scheme needs a name")
        if len(self.intervals) < 2:
            raise ValueError("A bin scheme needs at least two intervals")
        for lower, upper in self.intervals:
            if lower is None and upper is None:
                raise ValueError("An interval cannot be open at both ends")
            if lower is not None and upper is not None and lower >= upper:
                raise ValueError(f"Invalid interval: {(lower, upper)}")

    @property
    def midpoints(self) -> tuple[float, ...]:
        """Midpoints in source order, closing tails by one adjacent-bin width."""
        output: list[float] = []
        for index, (lower, upper) in enumerate(self.intervals):
            if lower is None:
                width = _adjacent_width(self.intervals, index, prefer=-1)
                lower = float(upper) - width
            elif upper is None:
                width = _adjacent_width(self.intervals, index, prefer=1)
                upper = float(lower) + width
            output.append((float(lower) + float(upper)) / 2)
        return tuple(output)


def _adjacent_width(intervals: tuple[Interval, ...], index: int, prefer: int) -> float:
    for direction in (prefer, -prefer):
        cursor = index + direction
        while 0 <= cursor < len(intervals):
            lower, upper = intervals[cursor]
            if lower is not None and upper is not None:
                return float(upper - lower)
            cursor += direction
    raise ValueError("An open tail needs an adjacent closed interval")


def _scheme(name: str, intervals: list[Interval]) -> BinScheme:
    return BinScheme(name=name, intervals=tuple(intervals))


PGDP_1968Q4_1973Q1 = _scheme(
    "prpgdp_1968q4_1973q1",
    [
        (10, None),
        (9, 9.9),
        (8, 8.9),
        (7, 7.9),
        (6, 6.9),
        (5, 5.9),
        (4, 4.9),
        (3, 3.9),
        (2, 2.9),
        (1, 1.9),
        (0, 0.9),
        (-1, -0.1),
        (-2, -1.1),
        (-3, -2.1),
        (None, -3),
    ],
)

PGDP_1973Q2_1974Q3 = _scheme(
    "prpgdp_1973q2_1974q3",
    [
        (12, None),
        (11, 11.9),
        (10, 10.9),
        (9, 9.9),
        (8, 8.9),
        (7, 7.9),
        (6, 6.9),
        (5, 5.9),
        (4, 4.9),
        (3, 3.9),
        (2, 2.9),
        (1, 1.9),
        (0, 0.9),
        (-1, -0.1),
        (None, -1),
    ],
)

PGDP_1974Q4_1981Q2 = _scheme(
    "prpgdp_1974q4_1981q2",
    [
        (16, None),
        (15, 15.9),
        (14, 14.9),
        (13, 13.9),
        (12, 12.9),
        (11, 11.9),
        (10, 10.9),
        (9, 9.9),
        (8, 8.9),
        (7, 7.9),
        (6, 6.9),
        (5, 5.9),
        (4, 4.9),
        (3, 3.9),
        (None, 3),
    ],
)

PRPGDP_1981Q3_1985Q1 = _scheme(
    "prpgdp_1981q3_1985q1",
    [(12, None), (10, 11.9), (8, 9.9), (6, 7.9), (4, 5.9), (None, 4)],
)

PRPGDP_1985Q2_1991Q4 = _scheme(
    "prpgdp_1985q2_1991q4",
    [(10, None), (8, 9.9), (6, 7.9), (4, 5.9), (2, 3.9), (None, 2)],
)

PRPGDP_1992Q1_2013Q4 = _scheme(
    "prpgdp_1992q1_2013q4",
    [
        (8, None),
        (7, 7.9),
        (6, 6.9),
        (5, 5.9),
        (4, 4.9),
        (3, 3.9),
        (2, 2.9),
        (1, 1.9),
        (0, 0.9),
        (None, 0),
    ],
)

HALF_POINT_INFLATION = _scheme(
    "half_point_inflation_2014q1_present",
    [
        (4, None),
        (3.5, 3.9),
        (3, 3.4),
        (2.5, 2.9),
        (2, 2.4),
        (1.5, 1.9),
        (1, 1.4),
        (0.5, 0.9),
        (0, 0.4),
        (None, 0),
    ],
)

PRGDP_1981Q3_1991Q4 = _scheme(
    "prgdp_1981q3_1991q4",
    [(6, None), (4, 5.9), (2, 3.9), (0, 1.9), (-2, -0.1), (None, -2)],
)

PRGDP_1992Q1_2009Q1 = _scheme(
    "prgdp_1992q1_2009q1",
    [
        (6, None),
        (5, 5.9),
        (4, 4.9),
        (3, 3.9),
        (2, 2.9),
        (1, 1.9),
        (0, 0.9),
        (-1, -0.1),
        (-2, -1.1),
        (None, -2),
    ],
)

PRGDP_2009Q2_2020Q1 = _scheme(
    "prgdp_2009q2_2020q1",
    [
        (6, None),
        (5, 5.9),
        (4, 4.9),
        (3, 3.9),
        (2, 2.9),
        (1, 1.9),
        (0, 0.9),
        (-1, -0.1),
        (-2, -1.1),
        (-3, -2.1),
        (None, -3),
    ],
)

PRGDP_2020Q2_2024Q1 = _scheme(
    "prgdp_wide_2020q2_2024q1",
    [
        (16, None),
        (10, 15.9),
        (7, 9.9),
        (4, 6.9),
        (2.5, 3.9),
        (1.5, 2.4),
        (0, 1.4),
        (-3, -0.1),
        (-6, -3.1),
        (-12, -6.1),
        (None, -12),
    ],
)

PRGDP_2024Q2_PRESENT = _scheme(
    "prgdp_2024q2_present",
    [
        (9, None),
        (7, 8.9),
        (5.5, 6.9),
        (4, 5.4),
        (2.5, 3.9),
        (1.5, 2.4),
        (0, 1.4),
        (-1.5, -0.1),
        (-3, -1.6),
        (-5.1, -3.1),
        (None, -5.1),
    ],
)

PRUNEMP_2009Q2_2013Q4 = _scheme(
    "prunemp_2009q2_2013q4",
    [
        (11, None),
        (10, 10.9),
        (9.5, 9.9),
        (9, 9.4),
        (8.5, 8.9),
        (8, 8.4),
        (7.5, 7.9),
        (7, 7.4),
        (6, 6.9),
        (None, 6),
    ],
)

PRUNEMP_2014Q1_2020Q1 = _scheme(
    "prunemp_2014q1_2020q1",
    [
        (9, None),
        (8, 8.9),
        (7.5, 7.9),
        (7, 7.4),
        (6.5, 6.9),
        (6, 6.4),
        (5.5, 5.9),
        (5, 5.4),
        (4, 4.9),
        (None, 4),
    ],
)

PRUNEMP_2020Q2_2024Q1 = _scheme(
    "prunemp_wide_2020q2_2024q1",
    [
        (15, None),
        (12, 14.9),
        (10, 11.9),
        (8, 9.9),
        (7, 7.9),
        (6, 6.9),
        (5, 5.9),
        (4, 4.9),
        (3, 3.9),
        (None, 3),
    ],
)

PRUNEMP_2024Q2_PRESENT = _scheme(
    "prunemp_2024q2_present",
    [
        (9.9, None),
        (8.3, 9.8),
        (7.2, 8.2),
        (6.1, 7.1),
        (5.5, 6),
        (4.9, 5.4),
        (4.3, 4.8),
        (3.7, 4.2),
        (3.1, 3.6),
        (None, 3.1),
    ],
)


def us_bin_scheme(variable: str, year: int, quarter: int) -> BinScheme:
    """Return the documented bin scheme for a US SPF density round."""
    name = variable.upper()
    date = (int(year), int(quarter))
    if date[1] not in {1, 2, 3, 4}:
        raise ValueError(f"Invalid quarter: {quarter}")

    if name in {"PRGDP", "PRPGDP"} and date < (1968, 4):
        raise ValueError(f"{name} was not surveyed before 1968Q4")
    if name == "PRGDP":
        if date <= (1973, 1):
            return _renamed(PGDP_1968Q4_1973Q1, "prgdp_1968q4_1973q1")
        if date <= (1974, 3):
            return _renamed(PGDP_1973Q2_1974Q3, "prgdp_1973q2_1974q3")
        if date <= (1981, 2):
            return _renamed(PGDP_1974Q4_1981Q2, "prgdp_1974q4_1981q2")
        if date <= (1991, 4):
            return PRGDP_1981Q3_1991Q4
        if date <= (2009, 1):
            return PRGDP_1992Q1_2009Q1
        if date <= (2020, 1):
            return PRGDP_2009Q2_2020Q1
        if date <= (2024, 1):
            return PRGDP_2020Q2_2024Q1
        return PRGDP_2024Q2_PRESENT

    if name == "PRPGDP":
        if date <= (1973, 1):
            return PGDP_1968Q4_1973Q1
        if date <= (1974, 3):
            return PGDP_1973Q2_1974Q3
        if date <= (1981, 2):
            return PGDP_1974Q4_1981Q2
        if date <= (1985, 1):
            return PRPGDP_1981Q3_1985Q1
        if date <= (1991, 4):
            return PRPGDP_1985Q2_1991Q4
        if date <= (2013, 4):
            return PRPGDP_1992Q1_2013Q4
        return _renamed(HALF_POINT_INFLATION, "prpgdp_2014q1_present")

    if name in {"PRCCPI", "PRCPCE"}:
        if date < (2007, 1):
            raise ValueError(f"{name} was not surveyed before 2007Q1")
        return _renamed(HALF_POINT_INFLATION, f"{name.lower()}_2007q1_present")

    if name == "PRUNEMP":
        if date < (2009, 2):
            raise ValueError("PRUNEMP was not surveyed before 2009Q2")
        if date <= (2013, 4):
            return PRUNEMP_2009Q2_2013Q4
        if date <= (2020, 1):
            return PRUNEMP_2014Q1_2020Q1
        if date <= (2024, 1):
            return PRUNEMP_2020Q2_2024Q1
        return PRUNEMP_2024Q2_PRESENT

    raise KeyError(f"Unknown US density variable: {variable}")


def _renamed(scheme: BinScheme, name: str) -> BinScheme:
    return BinScheme(name=name, intervals=scheme.intervals)


_ECB_HEADER = re.compile(
    r"^(?:F(?P<lower_negative>N)?(?P<lower>\d+(?:_\d+)?))?"
    r"(?:T(?P<upper_negative>N)?(?P<upper>\d+(?:_\d+)?))?$"
)


def parse_ecb_header(name: str) -> Interval:
    """Parse an ECB interval code, retaining its literal labeled endpoints."""
    header = name.strip().upper()
    match = _ECB_HEADER.fullmatch(header)
    if match is None or (match["lower"] is None and match["upper"] is None):
        raise ValueError(f"Not an ECB probability-bin header: {name!r}")
    lower = _ecb_number(match["lower"], match["lower_negative"])
    upper = _ecb_number(match["upper"], match["upper_negative"])
    if lower is not None and upper is not None and lower >= upper:
        raise ValueError(f"ECB interval endpoints are not increasing: {name!r}")
    return lower, upper


def _ecb_number(value: str | None, negative: str | None) -> float | None:
    if value is None:
        return None
    number = float(value.replace("_", "."))
    return -number if negative else number


def ecb_intervals(
    intervals: list[Interval] | tuple[Interval, ...],
) -> tuple[Interval, ...]:
    """Validate and sort literal ECB interval labels from low to high.

    Annexes 3 and 5 define the finite ranges as closed, one-decimal-grid
    intervals. Thus 0.0--0.4 retains those literal bounds even when followed by
    0.5--0.9; the continuous surrogate has a 0.1 gap and does not shift either
    reported endpoint.
    """
    if not intervals:
        raise ValueError("At least one ECB interval is required")
    ordered = sorted(
        intervals,
        key=lambda bounds: float("-inf") if bounds[0] is None else bounds[0],
    )
    for index, (lower, upper) in enumerate(ordered):
        if lower is None and index != 0:
            raise ValueError("Only the first interval may have an open lower tail")
        if upper is None and index != len(ordered) - 1:
            raise ValueError("Only the last interval may have an open upper tail")
        if index + 1 < len(ordered):
            next_lower = ordered[index + 1][0]
            if upper is None or next_lower is None or upper > next_lower:
                raise ValueError("ECB intervals overlap or have misplaced open tails")
    return tuple(ordered)


contiguous_ecb_intervals = ecb_intervals
ecb_contiguous_intervals = ecb_intervals
