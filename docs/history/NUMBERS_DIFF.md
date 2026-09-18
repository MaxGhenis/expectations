# Numbers diff: the panorama manuscript against the corrected construction

Every figure in the `r2` column is recomputed from the outputs committed with revision r2 (`git show 03f0304:outputs/`), and every figure in the `Now` column from the outputs in this working tree. Where r2 stated a literal that its own outputs did not support, both the claim and the r2-era computation appear, so the two kinds of correction stay separate: a number that moved because the construction changed, and a number that was never what the pipeline said.

Three changes drive the movement. Respondent variances now spread each bin's mass uniformly inside the bin instead of massing it at the midpoint, which raises every within-forecaster SD. Disagreement is now the population variance across respondent means rather than the sample variance, which lowers it. CRPS skill is now one minus the ratio of mean losses on matched rows rather than the mean of row-level skill, which changes several signs.

The first two changes touch the second moment and nothing else. Comparing the two `measures.csv` files row by row on their 3,695 shared keys, `within_sd`, `disagreement`, `total_sd` and `share_between` differ on every row, while `mean` differs on 2 rows, `median` on 1 and the pooled quartiles on 2. Those few rows are responses the tightened probability filter now rejects, not a moment effect: the mean of a uniform distribution over a literal bin is that bin's midpoint, and an open tail closed at one adjacent-bin width is itself a finite bin. So the consensus means, medians and IQRs below stand while the uncertainty levels move.

`Wiring` says where the manuscript now gets the value. `[RECOMPUTE: ...]` and `[REFRAME]` markers are inline in `paper/index.qmd` for sentences that cannot carry the new number without a rewrite.

## Abstract

| Statement | r2 | Now | Wiring |
|---|---|---|---|
| round-target distributions | 3,695 | 3,695 | inline, `v['n_measures']` |
| euro-area inflation uncertainty above its pre-2021 level in 2026 | a third; computed 50% on the mean through 2020 and 35% on 2010-19 | 49% on the mean through 2020, 34% on 2010-19 | inline, `v['hicp_gap']` (through-2020 basis) |
| disagreement share of total variance, growth | a sixth (US 16.8%, euro area 15.7%) | US 15.5%, euro area 14.9% | inline, `v['sh_growth_lo']`/`v['sh_growth_hi']`, @tbl-disagreement |
| largest disagreement share of any variable | at most a third (32.5%, US core PCE) | 30.4% (US core CPI) | inline, `v['sh_max']` |
| ten-year IQR against next-year IQR, 2026 | 0.2pp vs 0.4pp | 0.2pp vs 0.4pp (pooled next-year predictive IQR 1.5pp) | inline; marked [REFRAME] |
| one-sigma coverage of next-year US growth | 69.7% over 33 years | 69.7% over 33 years | inline, `v['cov_pct']`, `v['cov_years']` |
| densities beat the consensus-plus-error Gaussian | only for growth and the euro area (row-mean skill) | everywhere except US GDP prices (-1.3%) and ECB HICP (-0.2%) (ratio-of-means skill) | marked [RECOMPUTE], @tbl-skill |

## Measures

| Statement | r2 | Now | Wiring |
|---|---|---|---|
| current-year uncertainty falls from Q1 to Q4 | 24-41% (24.2-41.1%) | 23.1-36.0% | inline, `v['shrink_lo']`/`v['shrink_hi']`, @tbl-shrinkage |
| pooled CRPS gain over the average individual, all rows | 9.2% | 9.3% | inline, `v['crps_gain']` |
| the same gain by survey-variable-horizon cell | 3.5-18.7% (3.5-18.7%) | 3.5-18.7% | inline, `v['gain_lo']`/`v['gain_hi']`, @tbl-skill |
| wide-bin era against the matched pre window, US growth within SD | 1.102 → 1.756 (+59.4%) | 1.134 → 1.839 (+62.2%) | @tbl-bins |
| the same window, pooled IQR | 1.418 → 1.985 (+39.9%) | 1.418 → 1.985 (+39.9%) | @tbl-bins |
| 2024Q1-to-Q2 bin boundary, next-year US growth total SD | 1.803 → 1.405 (-22.1%) | 1.855 → 1.445 (-22.1%) | @tbl-bins |

## Five stylized facts

| Fact | Statement | r2 | Now | Wiring |
|---|---|---|---|---|
| 1 | pooled SD of next-year US growth, 1992 | 1.24 | 1.26 | inline, `v['t1992']` |
| 1 | mean through 2020 | 1.26 | 1.28 | inline, `v['mean_1992_2020']` |
| 1 | 2021 peak | 2.10 | 2.18 | inline, `v['t2021']` |
| 1 | 2026 | 1.36 | 1.40 | inline, `v['t2026']` |
| 1 | 2010-19 mean | 1.25 | 1.27 | inline, `v['dec_1019']` |
| 1 | 2020-24 mean | 1.74 | 1.80 | inline, `v['dec_2024']` |
| 1 | euro-area growth peak (year) | 2.62 (2020) | 2.62 (2020) | @tbl-stability |
| 2 | median between share, US growth / euro-area growth / euro-area prices | 17% / 16% / 14% | 15% / 15% / 14% | inline, `v['sh_usgdp']`, `v['sh_ecbgdp']`, `v['sh_hicp']` |
| 2 | median between share, US core CPI / core PCE | 32% / 32% | 30% / 30% | inline, `v['sh_usccpi']`, `v['sh_uscpce']` |
| 2 | point-forecast spread understates stated uncertainty by | two-to-threefold (1.8–2.6x) | 1.8–2.7x | inline, `v['ratio_lo']`/`v['ratio_hi']` |
| 3 | US growth within SD, h=2 then h=3 | 1.368 then 1.384 (+0.017) | 1.405 then 1.421 (+0.016) | inline, `v['prgdp_h2']`, `v['prgdp_h3']`, `v['prgdp_h3_gain']` |
| 3 | ECB growth total SD, rolling 1y against longer term | 0.856 vs 0.813 | 0.864 vs 0.820 | inline, `v['ecb_roll1_total']`, `v['ecb_lt_total']` |
| 4 | next-year US growth outcomes inside +/-1 SD | 23 of 33 | 23 of 33 | inline, `v['cov_n']` |
| 4 | outcome years covered | 1993-2025 | 1993-2025 | inline, `v['cov_span']` |
| 4 | longest run of target years missing +/-1 SD on every forecast | six straight years claimed; 4 computed (1996-1999) | 4 (1996-1999) | inline, `v['run_len']`, `v['run_span']` |
| 4 | euro-area one-sigma coverage by variable | 49-57% claimed; 49-57% excluding core HICP, 49-60% including it | 48-60% (all four variables) | inline, `v['ecb_cov_lo']`/`v['ecb_cov_hi']`, @tbl-coverage |
| 4 | US growth CRPS skill against climatology | 40% (row mean) | 38% (ratio of means; row mean 40%) | inline, `v['skill_clim_usgdp']` |
| 4 | US growth CRPS skill against the Gaussian | 6.2% (row mean) | 6.4% (ratio of means) | inline, `v['skill_gauss_usgdp']` |
| 4 | 2020-22 inflation upper-tail to lower-tail pinball ratio | five to nine (4.9-8.9x) | 4.8-8.9x | inline, `v['pin_lo']`/`v['pin_hi']`, @tbl-tails |
| 4 | 2008-09 growth pinball 05 against 95 | US 0.572 vs 0.196 | US 0.572 vs 0.196 | @tbl-tails |
| 5 | ECB longer-term total SD change after 2021 | +31% | +30% | inline, `v['lt_sd_pct']` |
| 5 | ECB rolling-1y total SD change after 2021 | +56% | +55% | inline, `v['roll_sd_pct']` |
| 5 | ECB longer-term consensus | 1.8% → 2.0% | 1.8% → 2.0% | inline, `v['lt_cons_early']`/`v['lt_cons_late']` |
| 5 | ECB rolling-1y consensus | 1.6% → 2.3% | 1.6% → 2.3% | inline, `v['roll_cons_early']`/`v['roll_cons_late']` |
| 5 | ECB longer-term uncertainty relative to its series high | series high claimed; 0.91 in 2026 against 0.99 in 2023 | 0.91 in 2026 against 0.99 in 2023 | marked [RECOMPUTE], @tbl-longterm |

## Other sections

| Section | Statement | r2 | Now | Wiring |
|---|---|---|---|---|
| Introduction | 2026 medians: next year, ten year | 1.8% and 2.1% | 1.8% and 2.1% | inline, `v['med_ny']`, `v['med_10y']`; comparison marked [REFRAME] |
| Introduction | forecast-outcome pairs | 3,070 | 3,070 | inline, `v['n_cal']` |
| Measures | within-bin mass and disagreement construction | bin midpoints; sample variance across respondent means | uniform within the literal bin; population variance across respondent means | marked [RECOMPUTE] |
| Five facts, draft note | source of the balanced-sample and post-2021 comparisons | `SOL_REPORT.md` and `SCORES_REPORT.md`, pending computation | `outputs/panorama_*.csv`, computed at render | note rewritten |
| Section 6, What better elicitation would look like | published AI growth-effect range and the 2020 bin widening precedent | 0.1-30pp a year; 2020Q2 widening | unchanged (literature and documentation, not pipeline output) | no wiring needed |
| Conclusion | the 2026 pair | 0.4pp and 0.2pp | 0.4pp and 0.2pp | inline; marked [REFRAME] |
| Data and limitations | repository URL | github.com/MaxGhenis/forecast-uncertainty | github.com/MaxGhenis/expectations | corrected |

## Statements whose direction changed

- **The Gaussian benchmark.** On row-mean skill the elicited densities lost to the consensus-plus-error Gaussian for US GDP prices, unemployment, core CPI and core PCE, and beat it across the euro area. On the ratio-of-means definition they beat it for US unemployment (+7.4%), core CPI (+3.3%) and core PCE (+2.4%), and lose for ECB HICP (-0.2%). The abstract's "only for growth and the euro area" and the fifth fact's "for US inflation and unemployment the elicited shape adds nothing" both fail, in opposite directions. The switch is the definition, not the data: the r2 outputs give the same ratio-of-means signs.

- **The ECB longer-term series high.** The manuscript says stated long-run uncertainty now sits at its series high. It does not, and did not at r2: the longer-term total SD peaks at 0.99 in 2023 and stands at 0.91 in 2026. The post-2021 rise is real; the record level is not.

- **The late-1990s miss cluster.** "Six straight target years" is 4: every forecast of 1996 through 1999 misses the band, and 1995 and 2000 do not. The r2 outputs give the same four years.

- **The ten-year against next-year IQR.** Both numbers are cross-sectional spreads of central tendencies: the IQR of ten-year point forecasts against the IQR of next-year density means. The sentence presents them as a term structure of stated uncertainty, which they are not. The pooled next-year predictive IQR is 1.51pp, against 0.2pp for the decade's point forecasts. Four sentences are marked [REFRAME] rather than deleted.

- **Euro-area inflation "a third above its pre-2021 level".** The claim holds against the 2010-19 mean (34%) but not against the mean through 2020 (49%), which is what "pre-2021" says. The manuscript now states the through-2020 comparison; pick the basis deliberately.

- **Core HICP is calibrated.** The euro-area coverage literal traces to `SOL_REPORT.md`, which records core HICP as having no matched realization and no calibration rows. It has 176 of them, and had the same number at r2, so the range should have spanned four euro-area variables in r2 and does now. Its coverage is the highest of the four, which is what widens the top of the range.

## Values that did not move

The 2026 medians, the wide-era pooled IQR (1.985 against 1.418 before, identical to r2 in both windows), the ECB consensus paths, the by-cell pooling-gain range and the one-sigma coverage count for next-year US growth (23 of 33) are unchanged. They are wired to the panorama tables anyway, so a later data refresh cannot strand them.
