import pytest

from expectations.bins import (
    BinScheme,
    ecb_intervals,
    parse_ecb_header,
    us_bin_scheme,
)


@pytest.mark.parametrize(
    ("header", "expected"),
    [
        ("TN1_0", (None, -1.0)),
        ("T0_0", (None, 0.0)),
        ("FN1_0TN0_6", (-1.0, -0.6)),
        ("FN0_2T0_2", (-0.2, 0.2)),
        ("F0_0T0_4", (0.0, 0.4)),
        ("F4_0", (4.0, None)),
    ],
)
def test_ecb_header_parser(header, expected):
    assert parse_ecb_header(header) == expected


def test_ecb_effective_edges_preserve_literal_closed_grid_labels():
    literal = [
        parse_ecb_header(name)
        for name in ["TN0_8", "FN0_7TN0_3", "FN0_2T0_2", "F0_3T0_7", "F0_8"]
    ]

    assert ecb_intervals(literal) == (
        (None, -0.8),
        (-0.7, -0.3),
        (-0.2, 0.2),
        (0.3, 0.7),
        (0.8, None),
    )
    assert BinScheme("ecb_test", ecb_intervals(literal)).midpoints == pytest.approx(
        (-1.0, -0.5, 0.0, 0.5, 1.0)
    )


@pytest.mark.parametrize(
    ("variable", "year", "quarter", "name", "bins"),
    [
        ("prgdp", 1968, 4, "prgdp_1968q4_1973q1", 15),
        ("prgdp", 1981, 3, "prgdp_1981q3_1991q4", 6),
        ("prgdp", 1992, 1, "prgdp_1992q1_2009q1", 10),
        ("prgdp", 2009, 2, "prgdp_2009q2_2020q1", 11),
        ("prgdp", 2020, 2, "prgdp_wide_2020q2_2024q1", 11),
        ("prgdp", 2024, 2, "prgdp_2024q2_present", 11),
        ("prpgdp", 1985, 2, "prpgdp_1985q2_1991q4", 6),
        ("prpgdp", 2014, 1, "prpgdp_2014q1_present", 10),
        ("prunemp", 2020, 2, "prunemp_wide_2020q2_2024q1", 10),
        ("prccpi", 2007, 1, "prccpi_2007q1_present", 10),
    ],
)
def test_us_bin_eras(variable, year, quarter, name, bins):
    scheme = us_bin_scheme(variable, year, quarter)
    assert scheme.name == name
    assert len(scheme.intervals) == bins


def test_seed_scheme_midpoints_are_unchanged():
    assert us_bin_scheme("prgdp", 1992, 1).midpoints == pytest.approx(
        (6.45, 5.45, 4.45, 3.45, 2.45, 1.45, 0.45, -0.55, -1.55, -2.45)
    )


@pytest.mark.parametrize(
    ("variable", "year", "quarter", "expected"),
    [
        (
            "prpgdp",
            1968,
            4,
            (
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
            ),
        ),
        (
            "prpgdp",
            1973,
            2,
            (
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
            ),
        ),
        (
            "prgdp",
            1974,
            4,
            (
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
            ),
        ),
        (
            "prpgdp",
            1981,
            3,
            ((12, None), (10, 11.9), (8, 9.9), (6, 7.9), (4, 5.9), (None, 4)),
        ),
        (
            "prpgdp",
            1985,
            2,
            ((10, None), (8, 9.9), (6, 7.9), (4, 5.9), (2, 3.9), (None, 2)),
        ),
        (
            "prpgdp",
            1992,
            1,
            (
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
            ),
        ),
        (
            "prpgdp",
            2014,
            1,
            (
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
            ),
        ),
        (
            "prgdp",
            1981,
            3,
            ((6, None), (4, 5.9), (2, 3.9), (0, 1.9), (-2, -0.1), (None, -2)),
        ),
        (
            "prgdp",
            2009,
            2,
            (
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
            ),
        ),
        (
            "prgdp",
            2020,
            2,
            (
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
            ),
        ),
        (
            "prgdp",
            2024,
            2,
            (
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
            ),
        ),
        (
            "prunemp",
            2009,
            2,
            (
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
            ),
        ),
        (
            "prunemp",
            2014,
            1,
            (
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
            ),
        ),
        (
            "prunemp",
            2020,
            2,
            (
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
            ),
        ),
        (
            "prunemp",
            2024,
            2,
            (
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
            ),
        ),
        (
            "prccpi",
            2007,
            1,
            (
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
            ),
        ),
        (
            "prcpce",
            2007,
            1,
            (
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
            ),
        ),
    ],
)
def test_all_documented_us_bin_edges(variable, year, quarter, expected):
    assert us_bin_scheme(variable, year, quarter).intervals == expected
