import numpy as np
import pandas as pd
import pytest

from forecast_uncertainty.growth import GROWTH_TAIL_COLUMNS, growth_tail_table
from forecast_uncertainty.us_spf import parse_us_density


def density_frame(intervals, probabilities, **metadata):
    defaults = {
        "survey": "us",
        "variable": "prgdp",
        "concept": "real_gdp",
        "year": 2026,
        "quarter": 1,
        "target_year": 2027,
        "horizon_class": "next_year",
        "horizon_years": 1,
        "bin_scheme": "test",
        **metadata,
    }
    return pd.DataFrame(
        [
            {
                **defaults,
                "respondent": respondent,
                "bin_index": index,
                "lower": lower,
                "upper": upper,
                "probability": probability,
            }
            for respondent, row in enumerate(probabilities)
            for index, ((lower, upper), probability) in enumerate(
                zip(intervals, row, strict=True)
            )
        ]
    )


def test_exact_bin_edges_and_literal_gap_need_no_interpolation():
    frame = density_frame(
        [(None, 0), (0, 3.9), (4, 5.9), (6, None)],
        [[20, 40, 30, 10], [0, 80, 20, 0]],
    )
    tails = growth_tail_table(frame, [3.9, 3.95, 4, 6]).set_index("threshold")

    for threshold in (3.9, 3.95, 4):
        row = tails.loc[threshold]
        assert row.probability_lower == pytest.approx(0.3)
        assert row.probability_upper == pytest.approx(0.3)
        assert row.probability_uniform == pytest.approx(0.3)
        assert row.n_positive_lower == row.n_positive_upper == 2
        assert not row.open_tail_threshold
    assert tails.loc[6, "probability_lower"] == pytest.approx(0.05)
    assert tails.loc[6, "probability_upper"] == pytest.approx(0.05)
    assert tails.loc[6, "n_positive_lower"] == 1


def test_finite_straddling_bin_has_bounds_and_optional_uniform_estimate():
    frame = density_frame([(0, 4), (4, 8)], [[100, 0], [0, 100]])
    row = growth_tail_table(frame, [3]).iloc[0]

    assert row.probability_lower == pytest.approx(0.5)
    assert row.probability_upper == pytest.approx(1.0)
    assert row.probability_uniform == pytest.approx(0.625)
    assert row.n_positive_lower == 1
    assert row.n_positive_upper == 2
    assert row.share_positive_lower == pytest.approx(0.5)
    assert row.share_positive_upper == pytest.approx(1.0)


def test_positive_open_tail_cannot_imply_zero_extreme_growth_probability():
    frame = density_frame([(0, 4), (4, None)], [[90, 10], [100, 0]])
    tails = growth_tail_table(frame, [4, 5, 10, 1000]).set_index("threshold")

    assert tails.loc[4, "probability_lower"] == pytest.approx(0.05)
    assert tails.loc[4, "probability_uniform"] == pytest.approx(0.05)
    for threshold in (5, 10, 1000):
        row = tails.loc[threshold]
        assert row.probability_lower == 0
        assert row.probability_upper == pytest.approx(0.05)
        assert np.isnan(row.probability_uniform)
        assert row.open_tail_threshold
        assert row.n_positive_lower == 0
        assert row.n_positive_upper == 1


def test_empty_open_tail_still_does_not_receive_a_fabricated_uniform_density():
    frame = density_frame([(0, 4), (4, None)], [[100, 0]])
    row = growth_tail_table(frame, [10]).iloc[0]

    assert row.probability_lower == row.probability_upper == 0
    assert row.n_positive_lower == row.n_positive_upper == 0
    assert np.isnan(row.probability_uniform)
    assert row.open_tail_threshold


def test_negative_open_lower_tail_is_also_partially_identified():
    frame = density_frame([(None, -2), (-2, 4), (4, None)], [[20, 70, 10]])
    tails = growth_tail_table(frame, [-10, -2]).set_index("threshold")

    assert tails.loc[-10, "probability_lower"] == pytest.approx(0.8)
    assert tails.loc[-10, "probability_upper"] == pytest.approx(1.0)
    assert np.isnan(tails.loc[-10, "probability_uniform"])
    assert tails.loc[-2, "probability_lower"] == pytest.approx(0.8)
    assert tails.loc[-2, "probability_upper"] == pytest.approx(0.8)
    assert tails.loc[-2, "probability_uniform"] == pytest.approx(0.8)


def test_response_filter_normalizes_before_equal_weight_pooling():
    frame = density_frame(
        [(0, 4), (4, 8)],
        [
            [49, 50],
            [100, np.nan],
            [np.nan, np.nan],
            [49, 49],
            [51, 51],
            [-10, 110],
            [100, np.inf],
        ],
    )
    row = growth_tail_table(frame, [4]).iloc[0]

    assert row.n == 2
    assert row.probability_lower == pytest.approx((50 / 99) / 2)
    assert row.probability_upper == pytest.approx((50 / 99) / 2)
    assert row.n_positive_lower == row.n_positive_upper == 1


def test_omits_groups_with_no_valid_responses_and_keeps_empty_schema():
    frame = density_frame([(0, 4), (4, 8)], [[49, 49], [np.nan, np.nan]])
    tails = growth_tail_table(frame)

    assert tails.empty
    assert tails.columns.tolist() == GROWTH_TAIL_COLUMNS
    assert growth_tail_table(frame.iloc[:0]).columns.tolist() == GROWTH_TAIL_COLUMNS
    assert growth_tail_table(pd.DataFrame({"variable": []})).empty


def test_scheme_changes_do_not_pool_distinct_bins_or_fake_comparability():
    narrow = density_frame([(0, 4), (4, None)], [[90, 10]], bin_scheme="narrow")
    wide = density_frame([(0, 4), (4, 9), (9, None)], [[90, 8, 2]], bin_scheme="wide")
    tails = growth_tail_table(pd.concat([narrow, wide]), [10]).set_index("bin_scheme")

    assert tails.loc["narrow", "probability_upper"] == pytest.approx(0.1)
    assert tails.loc["wide", "probability_upper"] == pytest.approx(0.02)
    assert tails["probability_lower"].eq(0).all()
    assert tails["probability_uniform"].isna().all()
    assert tails["n"].eq(1).all()


def test_bounds_are_monotone_and_contain_uniform_finite_bin_probabilities():
    frame = density_frame(
        [(9, None), (4, 8.9), (0, 3.9), (None, 0)],
        [[2, 18, 60, 20], [0, 30, 70, 0]],
    )
    tails = growth_tail_table(frame, np.linspace(-10, 20, 151))

    assert tails.probability_lower.between(0, 1).all()
    assert tails.probability_upper.between(0, 1).all()
    assert (tails.probability_lower <= tails.probability_upper).all()
    assert (np.diff(tails.probability_lower) <= 1e-12).all()
    assert (np.diff(tails.probability_upper) <= 1e-12).all()
    interpolated = tails.dropna(subset=["probability_uniform"])
    assert (
        interpolated.probability_lower <= interpolated.probability_uniform + 1e-12
    ).all()
    assert (
        interpolated.probability_uniform <= interpolated.probability_upper + 1e-12
    ).all()


def test_uses_response_id_before_reused_respondent_identifier():
    frame = density_frame([(0, 4), (4, 8)], [[100, 0], [0, 100]])
    frame["response_id"] = frame["respondent"]
    frame["respondent"] = "same_label"

    row = growth_tail_table(frame, [4]).iloc[0]
    assert row.n == 2
    assert row.probability_lower == pytest.approx(0.5)


def test_undocumented_target_blocks_remain_separate():
    frame = density_frame(
        [(0, 4), (4, 8)], [[90, 10]], target_year=pd.NA, target_block=1
    )
    second = frame.assign(target_block=2, probability=[60, 40])
    tails = growth_tail_table(pd.concat([frame, second]), [4])

    assert tails.target_period.tolist() == [
        "undocumented_block_1",
        "undocumented_block_2",
    ]
    assert tails.probability_lower.tolist() == pytest.approx([0.1, 0.4])


def test_selects_only_gdp_variables_and_deduplicates_thresholds():
    gdp = density_frame([(0, 4), (4, 8)], [[90, 10]], variable="PRGDP")
    inflation = gdp.assign(variable="prpgdp")
    tails = growth_tail_table(pd.concat([gdp, inflation]), [4, 3, 4])

    assert tails.variable.eq("PRGDP").all()
    assert tails.threshold.tolist() == [3, 4]


def test_excludes_historical_gnp_and_preserves_both_real_gdp_concepts():
    us = density_frame([(0, 4), (4, 8)], [[90, 10]], variable="PRGDP")
    historical = [
        us.assign(year=1975, target_year=1976, concept="nominal_gnp"),
        us.assign(year=1985, target_year=1986, concept="real_gnp"),
    ]
    ecb = us.assign(survey="ecb", variable="rgdp", concept="real_gdp_yoy")
    tails = growth_tail_table(pd.concat([*historical, us, ecb]), [4])

    assert set(zip(tails.survey, tails.variable, tails.concept, strict=True)) == {
        ("us", "PRGDP", "real_gdp"),
        ("ecb", "rgdp", "real_gdp_yoy"),
    }
    assert tails.year.eq(2026).all()
    assert tails.probability_lower.tolist() == pytest.approx([0.1, 0.1])


@pytest.mark.parametrize("thresholds", [[np.nan], [np.inf], [-np.inf]])
def test_rejects_nonfinite_thresholds(thresholds):
    with pytest.raises(ValueError, match="finite"):
        growth_tail_table(pd.DataFrame({"variable": []}), thresholds)


@pytest.mark.parametrize(
    "intervals", [[(0, 5), (4, 8)], [(None, None)], [(4, 4)], [(5, 4)]]
)
def test_rejects_invalid_or_overlapping_bins(intervals):
    frame = density_frame(intervals, [[100 / len(intervals)] * len(intervals)])
    with pytest.raises(ValueError, match="bins"):
        growth_tail_table(frame)


def test_rejects_conflicting_endpoints_within_group():
    frame = density_frame([(0, 4), (4, 8)], [[90, 10], [80, 20]])
    frame.loc[(frame.respondent == 1) & (frame.bin_index == 1), "upper"] = 9
    with pytest.raises(ValueError, match="Inconsistent bins"):
        growth_tail_table(frame)


def test_actual_us_source_preserves_gdp_and_its_open_tail():
    density = parse_us_density("PRGDP")
    selected = density[
        (density.year == 2026) & (density.quarter == 1) & (density.horizon_years == 1)
    ]
    tails = growth_tail_table(selected, [4, 10]).set_index("threshold")

    assert tails.variable.eq("PRGDP").all()
    assert tails.survey.eq("us").all()
    assert tails.n.eq(28).all()
    assert tails.loc[4, "probability_lower"] == tails.loc[4, "probability_upper"]
    assert tails.loc[4, "probability_lower"] == pytest.approx(0.04443285714285715)
    assert tails.loc[10, "probability_lower"] == 0
    # One of 28 respondents places 1% in the source's open >=9% bin.
    assert tails.loc[10, "probability_upper"] == pytest.approx(0.01 / 28)
    assert np.isnan(tails.loc[10, "probability_uniform"])
