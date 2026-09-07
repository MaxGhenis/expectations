> Historical development document. Superseded for current findings and methods by the September 2026 growth-beliefs revision: see `RESEARCH_REVISION.md`, `paper/index.qmd`, and regenerated `outputs/`. Numbers below may use the former midpoint/sample-variance convention and approximate annual outcomes.

# Proper-score and benchmark report

## Result

Build brief 3 is complete. The pipeline now writes `outputs/scores.csv` for the
exact 3,070-row `calibration.csv` universe. Each row contains exact pooled and
average-individual CRPS, pinball loss at 05/10/25/50/75/90/95, PIT, two strictly
expanding benchmarks, the benchmark history counts, and per-row skill scores.

The static interactive has a fifth, URL-addressable **Scores** view. It draws at
most three lines—pooled forecast, climatology, and Gaussian around consensus—in
the existing palette order. The compact bundle contains all 38 selectable score
combinations and is 800,301 bytes, 66.7% of the 1.2 MB budget. Four-significant-
digit rounding was sufficient; no harder thinning or categorical recoding was
needed.

No commit was created. No file under `paper/`, no raw input, `LITREVIEW.md`,
`SOL_REPORT.md`, or `INTERACTIVE_REPORT.md` was changed.

## What is scored

The forecast distribution is the same continuous surrogate used for the emitted
quantiles: probability is uniform within each literal closed bin, literal gaps
have zero density, and each open tail is closed at one adjacent finite-bin width.
The pooled histogram is the binwise mean across responses retained by the
existing filter (all-NaN responses excluded; partial NaNs set to zero; only sums
strictly within 2 points of 100 retained; retained responses normalized).

For every interval between a bin endpoint and/or the realization, the CDF is
affine. If `g0` and `g1` are the endpoint values of
`F(x) - 1{x >= y}` on a segment of length `L`, its exact CRPS contribution is

```text
L * (g0^2 + g0*g1 + g1^2) / 3.
```

Summing these contributions integrates gaps and support-to-realization distances
without a grid. Degenerate closed intervals are supported as point masses for
validation; their jumps have zero Lebesgue measure but alter the CDF to their
right. PIT is the right-continuous `F(y)`. Pinball uses the same histogram inverse
CDF and the requested definition. Average-individual CRPS applies the identical
closed form to every retained response before averaging.

The benchmark formulas are:

```text
Empirical CRPS = mean |xi - y| - (1 / 2n^2) sum_i sum_j |xi - xj|

Gaussian CRPS = sigma * [z(2 Phi(z) - 1) + 2 phi(z) - 1 / sqrt(pi)],
                z = (y - consensus) / sigma.
```

## Headline findings

- Pooling helps on every one of the 3,070 scored rows. Mean CRPS falls from
  0.817 for the average individual to 0.741 for the pooled distribution, a 9.25%
  reduction. The gain is not merely an increase in variance: averaging densities
  consistently improves the proper score.
- Mean climatology skill is positive for all nine survey-variable pairs. At the
  variable level it ranges from +15.3% for ECB HICP and ECB real GDP to +57.1%
  for US core CPI. Some longer-horizon cells are nevertheless negative.
- The Gaussian-around-consensus benchmark is much harder to beat. Variable-level
  mean skill is positive for US real GDP (+6.2%) and all four ECB variables, but
  negative for US GDP prices, unemployment, core CPI, and core PCE. It improves
  materially after 2020 because its expanding error RMSE adapts to prior misses.
- The 2008–09 growth loss is decisively in the lower tail: mean 05 pinball is
  2.286 for ECB growth versus 0.215 at 95, and 0.572 versus 0.196 for US growth.
  Pandemic/inflation-shock losses reverse direction for prices: 2020–22 95-loss
  exceeds 05-loss by factors of roughly 5–9 for US GDP prices, both core US
  inflation measures, ECB HICP, and ECB core HICP.
- PIT is far from uniformly spread for several variables. ECB real GDP puts 45.8%
  of rows in the two extreme deciles; ECB HICP puts 36.9% there. US unemployment
  is strongly left-skewed (mean PIT 0.355; 22.4% in the bottom decile), whereas
  ECB HICP/core HICP lean right.

## CRPS and benchmark skill by survey, variable, and horizon

Each cell is `rows / mean pooled CRPS / mean climatology skill [eligible rows] /
mean Gaussian skill [eligible rows]`. Skill is averaged from the row-level
`1 - CRPS_pooled / CRPS_benchmark`; it is not a ratio of period means. Positive
values favor the survey. “Pre-2020” means forecast rounds through 2019Q4 and
“2020+” begins in 2020Q1. CRPS is in percentage-point units.

### US SPF

| Variable | Horizon | Full | Pre-2020 | 2020+ |
|---|---|---:|---:|---:|
| US real GDP | Current year | 136 / 0.515 / +53.3% [136] / +4.0% [124] | 112 / 0.448 / +56.5% [112] / +4.8% [100] | 24 / 0.831 / +38.4% [24] / +1.0% [24] |
| US real GDP | Next year | 132 / 0.902 / +29.0% [132] / +13.1% [116] | 112 / 0.873 / +34.3% [112] / +13.2% [96] | 20 / 1.060 / -0.7% [20] / +12.4% [20] |
| US real GDP | +2 years | 59 / 0.850 / +37.6% [59] / -5.9% [40] | 43 / 0.994 / +36.5% [43] / -4.6% [24] | 16 / 0.462 / +40.7% [16] / -7.9% [16] |
| US real GDP | +3 years | 55 / 0.858 / +38.8% [55] / +5.1% [32] | 43 / 0.975 / +37.7% [43] / +8.4% [20] | 12 / 0.438 / +43.0% [12] / -0.2% [12] |
| US GDP prices | Current year | 136 / 0.348 / +65.2% [136] / -16.0% [124] | 112 / 0.246 / +68.7% [112] / -22.8% [100] | 24 / 0.820 / +49.0% [24] / +12.4% [24] |
| US GDP prices | Next year | 132 / 0.596 / +42.4% [132] / -0.1% [116] | 112 / 0.431 / +49.3% [112] / -2.5% [96] | 20 / 1.515 / +4.0% [20] / +11.3% [20] |
| US unemployment | Current year | 63 / 0.235 / +78.1% [63] / -28.0% [52] | 43 / 0.122 / +86.2% [43] / -61.4% [32] | 20 / 0.479 / +60.7% [20] / +25.6% [20] |
| US unemployment | Next year | 59 / 0.615 / +26.1% [59] / +11.4% [44] | 43 / 0.621 / +40.6% [43] / +4.2% [28] | 16 / 0.600 / -12.9% [16] / +24.1% [16] |
| US unemployment | +2 years | 55 / 0.794 / +2.6% [55] / +7.7% [36] | 43 / 0.838 / -9.9% [43] / +0.0% [24] | 12 / 0.637 / +47.3% [12] / +23.0% [12] |
| US unemployment | +3 years | 51 / 0.896 / -19.4% [51] / +5.6% [28] | 43 / 0.949 / -31.9% [43] / -0.7% [20] | 8 / 0.612 / +47.7% [8] / +21.5% [8] |
| US core CPI | Current year | 72 / 0.367 / +65.7% [72] / -1.3% [60] | 52 / 0.173 / +79.6% [52] / -4.8% [40] | 20 / 0.873 / +29.4% [20] / +5.9% [20] |
| US core CPI | Next year | 68 / 0.584 / +48.0% [68] / -6.7% [52] | 52 / 0.229 / +74.5% [52] / -12.8% [36] | 16 / 1.740 / -37.9% [16] / +7.1% [16] |
| US core PCE | Current year | 76 / 0.325 / +65.8% [76] / -8.1% [64] | 52 / 0.186 / +77.3% [52] / -12.0% [40] | 24 / 0.627 / +40.8% [24] / -1.5% [24] |
| US core PCE | Next year | 72 / 0.553 / +45.9% [72] / -1.7% [56] | 52 / 0.270 / +68.2% [52] / -6.9% [36] | 20 / 1.288 / -12.1% [20] / +7.6% [20] |

### ECB SPF

| Variable | Horizon | Full | Pre-2020 | 2020+ |
|---|---|---:|---:|---:|
| ECB HICP | Current year | 108 / 0.313 / +56.9% [76] / -7.2% [96] | 84 / 0.149 / +60.2% [52] / -13.5% [72] | 24 / 0.884 / +49.8% [24] / +11.7% [24] |
| ECB HICP | Next year | 104 / 0.766 / +10.9% [72] / +4.8% [88] | 84 / 0.479 / +15.6% [52] / +0.7% [68] | 20 / 1.972 / -1.4% [20] / +18.5% [20] |
| ECB HICP | +2 years | 70 / 1.057 / +5.8% [56] / +5.6% [56] | 54 / 0.584 / +4.8% [40] / +2.9% [40] | 16 / 2.652 / +8.4% [16] / +12.5% [16] |
| ECB HICP | Rolling 1y | 105 / 0.801 / +6.9% [105] / +5.4% [92] | 84 / 0.502 / +7.4% [84] / +2.1% [71] | 21 / 1.995 / +5.0% [21] / +16.7% [21] |
| ECB HICP | Rolling 2y | 101 / 0.932 / +6.8% [101] / +5.5% [84] | 84 / 0.583 / +7.7% [84] / +3.1% [67] | 17 / 2.655 / +2.2% [17] / +15.2% [17] |
| ECB HICP | Longer term | 87 / 0.961 / +5.6% [61] / -0.4% [58] | 81 / 1.003 / +10.0% [55] / -0.7% [52] | 6 / 0.384 / -34.2% [6] / +1.8% [6] |
| ECB core HICP | Current year | 36 / 0.208 / +47.2% [36] / -19.4% [24] | 12 / 0.118 / +40.3% [12] / — | 24 / 0.253 / +50.7% [24] / -19.4% [24] |
| ECB core HICP | Next year | 32 / 0.707 / +7.0% [32] / +23.9% [16] | 12 / 0.271 / +0.7% [12] / — | 20 / 0.968 / +10.7% [20] / +23.9% [16] |
| ECB core HICP | +2 years | 28 / 1.041 / +6.0% [28] / +13.6% [8] | 12 / 0.346 / -32.7% [12] / — | 16 / 1.563 / +35.0% [16] / +13.6% [8] |
| ECB core HICP | Rolling 1y | 33 / 0.702 / +28.1% [33] / +11.3% [20] | 12 / 0.257 / +7.1% [12] / — | 21 / 0.956 / +40.1% [21] / +11.3% [20] |
| ECB core HICP | Rolling 2y | 29 / 1.053 / +10.4% [29] / +22.4% [12] | 12 / 0.445 / -25.3% [12] / — | 17 / 1.482 / +35.6% [17] / +22.4% [12] |
| ECB core HICP | Longer term | 18 / 1.432 / +10.0% [18] / — | 12 / 1.776 / +2.0% [12] / — | 6 / 0.743 / +25.9% [6] / — |
| ECB real GDP | Current year | 108 / 0.532 / +34.9% [80] / +7.4% [96] | 84 / 0.442 / +21.7% [56] / +5.4% [72] | 24 / 0.847 / +65.9% [24] / +13.2% [24] |
| ECB real GDP | Next year | 104 / 1.167 / +6.7% [76] / +20.0% [88] | 84 / 1.259 / -8.7% [56] / +15.8% [68] | 20 / 0.781 / +49.7% [20] / +34.0% [20] |
| ECB real GDP | +2 years | 70 / 1.444 / +12.8% [58] / +23.4% [56] | 54 / 1.648 / +11.7% [42] / +23.8% [40] | 16 / 0.753 / +15.8% [16] / +22.3% [16] |
| ECB real GDP | Rolling 1y | 107 / 0.961 / +16.6% [107] / +14.7% [95] | 84 / 0.999 / +6.7% [84] / +10.5% [72] | 23 / 0.824 / +52.7% [23] / +28.1% [23] |
| ECB real GDP | Rolling 2y | 103 / 1.394 / +1.7% [103] / +17.6% [87] | 84 / 1.504 / -2.2% [84] / +14.7% [68] | 19 / 0.906 / +19.0% [19] / +27.7% [19] |
| ECB real GDP | Longer term | 87 / 1.403 / +22.8% [65] / +26.7% [58] | 81 / 1.490 / +19.6% [59] / +23.1% [52] | 6 / 0.222 / +54.6% [6] / +57.8% [6] |
| ECB unemployment | Current year | 104 / 0.214 / +81.8% [64] / +0.0% [92] | 80 / 0.209 / +83.5% [40] / -1.5% [68] | 24 / 0.232 / +79.0% [24] / +4.3% [24] |
| ECB unemployment | Next year | 104 / 0.481 / +61.7% [60] / +7.8% [88] | 84 / 0.497 / +56.4% [40] / +5.8% [68] | 20 / 0.410 / +72.1% [20] / +14.7% [20] |
| ECB unemployment | +2 years | 70 / 0.692 / +39.6% [50] / +5.8% [56] | 54 / 0.737 / +23.7% [34] / +2.3% [40] | 16 / 0.538 / +73.4% [16] / +14.4% [16] |
| ECB unemployment | Rolling 1y | 106 / 0.411 / +28.3% [99] / +5.7% [93] | 83 / 0.411 / +16.6% [76] / +3.7% [70] | 23 / 0.415 / +66.8% [23] / +11.8% [23] |
| ECB unemployment | Rolling 2y | 103 / 0.738 / -16.6% [95] / +6.3% [86] | 84 / 0.789 / -39.2% [76] / +2.5% [67] | 19 / 0.511 / +73.6% [19] / +19.7% [19] |
| ECB unemployment | Longer term | 87 / 1.336 / -21.2% [47] / +5.2% [58] | 81 / 1.374 / -33.9% [41] / +5.3% [52] | 6 / 0.820 / +65.1% [6] / +4.5% [6] |

The shock-period comparison is not a universal deterioration. Short-horizon
price CRPS rises sharply after 2020, while longer-horizon US real-GDP and ECB
real-GDP CRPS is lower. Those cells contain few post-2020 realized targets, so
they should not be read as stable structural breaks. Negative cells identify
specific cases where the survey loses to a benchmark despite positive aggregate
skill.

## Does disagreement earn its keep?

Yes in the forecast-combination sense. “Gain” below is average-individual CRPS
minus pooled CRPS; gain percent is `1 - pooled / individual` using the two group
means. Every row improves strictly, as expected from the convexity of CRPS when
the individual distributions are averaged.

| Variable | Horizon | n | Pooled | Avg individual | Gain | Gain % | Better rows |
|---|---|---:|---:|---:|---:|---:|---:|
| US real GDP | Current year | 136 | 0.515 | 0.593 | 0.077 | 13.1% | 136/136 |
| US real GDP | Next year | 132 | 0.902 | 1.006 | 0.105 | 10.4% | 132/132 |
| US real GDP | +2 years | 59 | 0.850 | 0.948 | 0.099 | 10.4% | 59/59 |
| US real GDP | +3 years | 55 | 0.858 | 0.950 | 0.092 | 9.7% | 55/55 |
| US GDP prices | Current year | 136 | 0.348 | 0.421 | 0.074 | 17.5% | 136/136 |
| US GDP prices | Next year | 132 | 0.596 | 0.686 | 0.090 | 13.2% | 132/132 |
| US unemployment | Current year | 63 | 0.235 | 0.285 | 0.049 | 17.4% | 63/63 |
| US unemployment | Next year | 59 | 0.615 | 0.699 | 0.084 | 12.0% | 59/59 |
| US unemployment | +2 years | 55 | 0.794 | 0.906 | 0.112 | 12.4% | 55/55 |
| US unemployment | +3 years | 51 | 0.896 | 1.030 | 0.134 | 13.0% | 51/51 |
| US core CPI | Current year | 72 | 0.367 | 0.448 | 0.081 | 18.1% | 72/72 |
| US core CPI | Next year | 68 | 0.584 | 0.672 | 0.088 | 13.1% | 68/68 |
| US core PCE | Current year | 76 | 0.325 | 0.400 | 0.075 | 18.7% | 76/76 |
| US core PCE | Next year | 72 | 0.553 | 0.632 | 0.079 | 12.5% | 72/72 |
| ECB HICP | Current year | 108 | 0.313 | 0.344 | 0.032 | 9.2% | 108/108 |
| ECB HICP | Next year | 104 | 0.766 | 0.818 | 0.052 | 6.4% | 104/104 |
| ECB HICP | +2 years | 70 | 1.057 | 1.107 | 0.050 | 4.6% | 70/70 |
| ECB HICP | Rolling 1y | 105 | 0.801 | 0.865 | 0.064 | 7.4% | 105/105 |
| ECB HICP | Rolling 2y | 101 | 0.932 | 0.984 | 0.052 | 5.3% | 101/101 |
| ECB HICP | Longer term | 87 | 0.961 | 1.002 | 0.041 | 4.1% | 87/87 |
| ECB core HICP | Current year | 36 | 0.208 | 0.252 | 0.044 | 17.5% | 36/36 |
| ECB core HICP | Next year | 32 | 0.707 | 0.770 | 0.063 | 8.2% | 32/32 |
| ECB core HICP | +2 years | 28 | 1.041 | 1.107 | 0.066 | 5.9% | 28/28 |
| ECB core HICP | Rolling 1y | 33 | 0.702 | 0.781 | 0.080 | 10.2% | 33/33 |
| ECB core HICP | Rolling 2y | 29 | 1.053 | 1.124 | 0.071 | 6.3% | 29/29 |
| ECB core HICP | Longer term | 18 | 1.432 | 1.483 | 0.051 | 3.5% | 18/18 |
| ECB real GDP | Current year | 108 | 0.532 | 0.582 | 0.050 | 8.5% | 108/108 |
| ECB real GDP | Next year | 104 | 1.167 | 1.237 | 0.070 | 5.7% | 104/104 |
| ECB real GDP | +2 years | 70 | 1.444 | 1.504 | 0.060 | 4.0% | 70/70 |
| ECB real GDP | Rolling 1y | 107 | 0.961 | 1.062 | 0.101 | 9.5% | 107/107 |
| ECB real GDP | Rolling 2y | 103 | 1.394 | 1.467 | 0.073 | 5.0% | 103/103 |
| ECB real GDP | Longer term | 87 | 1.403 | 1.453 | 0.051 | 3.5% | 87/87 |
| ECB unemployment | Current year | 104 | 0.214 | 0.263 | 0.049 | 18.5% | 104/104 |
| ECB unemployment | Next year | 104 | 0.481 | 0.556 | 0.075 | 13.5% | 104/104 |
| ECB unemployment | +2 years | 70 | 0.692 | 0.799 | 0.107 | 13.4% | 70/70 |
| ECB unemployment | Rolling 1y | 106 | 0.411 | 0.481 | 0.069 | 14.4% | 106/106 |
| ECB unemployment | Rolling 2y | 103 | 0.738 | 0.839 | 0.102 | 12.1% | 103/103 |
| ECB unemployment | Longer term | 87 | 1.336 | 1.493 | 0.157 | 10.5% | 87/87 |

The largest relative gains occur for current-year ECB unemployment (18.5%), US
core PCE (18.7%), US core CPI (18.1%), and US GDP prices (17.5%). The smallest
are at ECB longer horizons, where between-forecaster disagreement is generally a
smaller share of total uncertainty. “Earns its keep” does not mean disagreement
itself is desirable; it means retaining the diversity of individual predictive
distributions improves the pooled proper score rather than merely widening it.

## Which tails carry the clustered losses?

Windows below use the realization event year parsed from `target_period` (with
`target_year` as the fallback for US annual rows), not the forecast-round year,
and pool every calibrated horizon available for that variable. The 1996–2001 ECB
rows necessarily cover only the survey's 1999–2001 portion. A high 05 loss means
realizations fell below the lower forecast tail; a high 95 loss means they rose
above the upper forecast tail. These are descriptive row averages: repeated
forecasts of one target are not independent.

| Target years | Variable | n | Mean pinball 05 | Mean pinball 95 | Larger tail |
|---|---|---:|---:|---:|---|
| 1996–2001 | US real GDP | 48 | 0.153 | 0.258 | Upper (95) |
| 1996–2001 | US GDP prices | 48 | 0.047 | 0.100 | Upper (95) |
| 1996–2001 | ECB HICP | 34 | 0.060 | 0.049 | Lower (05) |
| 1996–2001 | ECB real GDP | 36 | 0.095 | 0.256 | Upper (95) |
| 1996–2001 | ECB unemployment | 29 | 0.126 | 0.065 | Lower (05) |
| 2008–09 | US real GDP | 16 | 0.572 | 0.196 | Lower (05) |
| 2008–09 | US GDP prices | 16 | 0.062 | 0.131 | Upper (95) |
| 2008–09 | US unemployment | 3 | 0.037 | 0.037 | Essentially balanced; very small n |
| 2008–09 | US core CPI | 16 | 0.043 | 0.057 | Upper (95) |
| 2008–09 | US core PCE | 16 | 0.045 | 0.074 | Upper (95) |
| 2008–09 | ECB HICP | 44 | 0.358 | 0.282 | Lower (05) |
| 2008–09 | ECB real GDP | 44 | 2.286 | 0.215 | Lower (05) |
| 2008–09 | ECB unemployment | 44 | 0.106 | 0.481 | Upper (95) |
| 2020–22 | US real GDP | 48 | 0.577 | 0.585 | Balanced across the crash and rebound |
| 2020–22 | US GDP prices | 24 | 0.154 | 1.370 | Upper (95) |
| 2020–22 | US unemployment | 48 | 0.109 | 0.707 | Upper (95) |
| 2020–22 | US core CPI | 24 | 0.147 | 1.190 | Upper (95) |
| 2020–22 | US core PCE | 24 | 0.135 | 0.966 | Upper (95) |
| 2020–22 | ECB HICP | 72 | 0.245 | 1.848 | Upper (95) |
| 2020–22 | ECB core HICP | 66 | 0.101 | 0.500 | Upper (95) |
| 2020–22 | ECB real GDP | 72 | 1.855 | 0.938 | Lower (05) |
| 2020–22 | ECB unemployment | 72 | 0.051 | 0.112 | Upper (95) |

The directional story is coherent. Late-1990s US output and price realizations
were predominantly high relative to reported distributions. The financial crisis
puts growth losses in the downside tail and unemployment in the upside tail.
The pandemic combines a growth collapse and rebound, while the subsequent price
and labor-market surprises load primarily on the upper tail.

## PIT deciles

Entries are shares of calibrated rows in half-open deciles `[0,.1)`, …,
`[.8,.9)`, with the final bin including 1. PIT is pooled across horizons within
each survey-variable pair. Under ideal continuous calibration, each cell would be
about 10%; these rows share targets and therefore do not support naive independent
uniformity tests.

| Variable | n | Mean PIT | 0–.1 | .1–.2 | .2–.3 | .3–.4 | .4–.5 | .5–.6 | .6–.7 | .7–.8 | .8–.9 | .9–1 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| US real GDP | 382 | 0.548 | 7.3% | 6.5% | 11.0% | 6.0% | 9.9% | 12.3% | 15.4% | 10.2% | 7.6% | 13.6% |
| US GDP prices | 268 | 0.468 | 6.3% | 14.9% | 12.3% | 8.6% | 12.3% | 13.1% | 11.9% | 9.0% | 5.6% | 6.0% |
| US unemployment | 228 | 0.355 | 22.4% | 10.5% | 11.4% | 17.5% | 14.5% | 9.2% | 3.1% | 1.8% | 2.6% | 7.0% |
| US core CPI | 140 | 0.558 | 1.4% | 9.3% | 7.9% | 11.4% | 10.7% | 15.0% | 15.7% | 9.3% | 7.1% | 12.1% |
| US core PCE | 148 | 0.492 | 4.1% | 15.5% | 10.8% | 14.2% | 7.4% | 13.5% | 8.1% | 8.8% | 6.1% | 11.5% |
| ECB HICP | 575 | 0.567 | 15.7% | 4.5% | 5.7% | 5.4% | 8.5% | 7.5% | 10.4% | 10.8% | 10.3% | 21.2% |
| ECB core HICP | 176 | 0.592 | 5.7% | 10.8% | 10.2% | 6.2% | 9.1% | 5.7% | 13.1% | 5.7% | 5.7% | 27.8% |
| ECB real GDP | 579 | 0.511 | 23.0% | 6.2% | 4.5% | 5.2% | 8.5% | 6.7% | 7.9% | 7.8% | 7.4% | 22.8% |
| ECB unemployment | 574 | 0.513 | 11.8% | 13.2% | 9.8% | 10.1% | 9.9% | 3.7% | 5.1% | 5.1% | 10.3% | 21.1% |

ECB growth's pronounced U shape is the clearest underdispersion signal. ECB HICP
also combines too many low and high PITs with a heavier upper extreme. US
unemployment's left skew indicates realizations were often below the forecast
distribution over its full sample; the upper-tail pandemic misses do not overturn
that longer-run pattern.

## Benchmark histories and availability

The climatology benchmark uses every compatible local realization whose target
period completed strictly before the forecast quarter. It is matched by exact
realization concept, so annual averages are never mixed with rolling monthly or
quarterly year-on-year observations. The local histories are:

| Survey-variable | Target definition | Local history | Observations |
|---|---|---:|---:|
| US real GDP | Annual-average growth | 1930–2025 | 96 |
| US GDP prices | Annual-average price-index growth | 1930–2025 | 96 |
| US unemployment | Annual average | 1948–2024 | 77 |
| US core CPI | Q4/Q4 inflation | 1958–2024 | 67 |
| US core PCE | Q4/Q4 inflation | 1960–2025 | 66 |
| ECB HICP | Monthly year-on-year | 1997-01–2025-12 | 348 |
| ECB HICP | Calendar-year average | 1997–2025 | 29 |
| ECB core HICP | Monthly year-on-year | 1997-01–2025-12 | 348 |
| ECB core HICP | Calendar-year average | 1997–2025 | 29 |
| ECB real GDP | Quarterly year-on-year | 1996Q1–2026Q1 | 121 |
| ECB real GDP | Calendar-year average | 1996–2025 | 30 |
| ECB unemployment | Monthly rate | 2000-01–2026-06 | 318 |
| ECB unemployment | Calendar-year average | 2000–2025 | 26 |

This is why the US climatology is available immediately, whereas early ECB
calendar-year rows are null: ECB HICP reaches ten completed annual observations
only in 2007Q1, ECB real GDP in 2006Q1, and ECB unemployment in 2010Q1. Rolling
ECB histories can mature earlier because they use monthly or quarterly points.
Core HICP forecasts start late enough that its retrospective local histories
already exceed ten.

The Gaussian benchmark has no presurvey error history. It uses every earlier
forecast error in the exact `(survey, variable, horizon_class)` group only after
both the forecast was issued and its target completed before the current round.
Each calibrated forecast row counts as one historical error, including multiple
rounds that forecast the same eventual target. Its scale is RMSE, not a demeaned
standard deviation, so systematic bias also widens the benchmark.

| Variable | Rows | Climatology scored | Gaussian scored |
|---|---:|---:|---:|
| US real GDP | 382 | 382 (100.0%) | 312 (81.7%) |
| US GDP prices | 268 | 268 (100.0%) | 240 (89.6%) |
| US unemployment | 228 | 228 (100.0%) | 160 (70.2%) |
| US core CPI | 140 | 140 (100.0%) | 112 (80.0%) |
| US core PCE | 148 | 148 (100.0%) | 120 (81.1%) |
| ECB HICP | 575 | 471 (81.9%) | 474 (82.4%) |
| ECB core HICP | 176 | 176 (100.0%) | 80 (45.5%) |
| ECB real GDP | 579 | 489 (84.5%) | 480 (82.9%) |
| ECB unemployment | 574 | 415 (72.3%) | 473 (82.4%) |

In total, climatology is scored on 2,717 rows and Gaussian on 2,451. The largest
specific hole is ECB core HICP longer term: all 18 rows have climatology, but no
row has ten previously completed same-horizon forecast errors, so all Gaussian
scores and skills are correctly null. Counts `n_climatology` and `n_gaussian` in
`scores.csv` make every early null explicit.

## Interactive implementation

`interactive/gen_data.py` reads `outputs/scores.csv` but emits only nine fields:
the six control/round identifiers and the three displayed CRPS values. It still
validates the full score source schema: exact null-normalized calibration keys,
all distribution losses, PIT bounds, integer history counts, benchmark/count
null equivalence, and skill identities. All 38 survey-variable-horizon
combinations are nonempty.

The Scores view:

- uses palette slots 1, 2, and 3 for pooled, climatology, and Gaussian;
- retains the existing single axis, crosshair tooltip, table, legend, and direct
  endpoint-label patterns;
- shows Q1-only or all quarterly rounds on the forecast-round axis;
- averages duplicate early ECB longer-term pooled scores within a round,
  consistent with the existing decomposition view, but displays a benchmark
  average only when every constituent target has that benchmark so pooled and
  benchmark lines never use different target sets;
- breaks paths across null benchmark gaps rather than visually bridging them;
- omits unavailable benchmark legend entries and names the gap in the note; and
- participates in the existing hash state through `view=scores`.

The CSS token block—from the first `:root` declaration to immediately before the
global `*` rule—remains byte-identical: 1,080 bytes, SHA-256
`acd919a4fe11dd8e737168379518c8fa32468c4372007834a63edd160cf6b69b`.

## Judgment calls

| Decision | Implementation and rationale |
|---|---|
| Forecast availability clock | A realization is eligible only if its completion quarter is strictly earlier than the forecast round. Annual `YYYY` completes in Q4; `YYYYQq` completes in that quarter; a monthly target completes in its containing quarter. Equality is excluded. This approximates publication lags without inventing unavailable release calendars. |
| Longest histories | Dedicated benchmark loading retains the full local US series instead of the calibration-era truncation. Existing calibration loading is unchanged. ECB already exposes its full local monthly/quarterly and complete-year histories. |
| Climatology comparability | Match exact survey, variable, and realization concept. This separates annual ECB averages from rolling point observations, including the early mixed longer-term rows. Within a horizon group, the expanding sample is otherwise the longest compatible local history. |
| Gaussian error sample | Require exact survey-variable-horizon class; include each prior forecast error only after its target completed and only if the forecast round itself is earlier. Shared realized targets can contribute multiple forecast errors because the scored unit is a forecast row. |
| Gaussian dispersion | Use `sqrt(mean(error^2))` exactly as RMSE, centered around the current round's consensus. At zero RMSE the Gaussian limit is absolute error. |
| Minimum window and flags | Both benchmarks require ten observations. Scores and skills are null below ten; explicit history counts flag why. Skill is also null for a zero benchmark CRPS rather than dividing by zero. |
| Period summaries | Split on forecast-round year: `<2020` versus `>=2020`. Report the arithmetic mean of per-row skill values over eligible rows. |
| Tail windows | Classify clusters by the event year parsed from `target_period`, falling back to `target_year` for US annual rows, and pool all calibrated horizons. This includes ECB rolling targets and aligns the loss with the event being forecast. |
| PIT | Use the ordinary right-continuous PIT `F(y)`, not a randomized PIT. The pooled distributions are continuous; values at 0 or 1 can arise when the finite imposed support misses the realization. Floating overshoot at 1 is clipped only at machine precision. |
| Source anomalies | Preserve the mandated response filter. The two documented tiny negative ECB response probabilities are not clipped. Their pooled bin masses remain positive; individual CRPS for those two responses is the nonnegative squared-CDF integral of a signed source curve and is disclosed as an anomaly. |
| ECB longer-term Gaussian grouping | Follow the literal horizon-class grouping. The three early rolling five-year errors can enter later annual longer-term RMSE once completed; concept-matching the Gaussian would create a different benchmark than requested. |
| Vintage/status | Use the same latest-vintage and ECB-status-inclusive realization universe as `calibration.csv`, including rows whose status contains `E`. |
| Interactive duplicate rounds | Average duplicate early ECB longer-term targets for display. A benchmark is displayed only when every target in that round has an eligible score, avoiding a comparison against a smaller target subset. This presentation rule does not change `scores.csv`. |
| Interactive compaction | Keep only fields used by the chart and round numeric values to four significant digits. Source CSV precision is untouched. |

## Validation

The required suite passes:

```text
UV_CACHE_DIR=/private/tmp/forecast-uncertainty-uv-cache \
  uv run --no-sync pytest -q
74 passed, 2 warnings

UV_CACHE_DIR=/private/tmp/forecast-uncertainty-uv-cache \
  uv run --no-sync ruff format src tests interactive/gen_data.py
15 files left unchanged

UV_CACHE_DIR=/private/tmp/forecast-uncertainty-uv-cache \
  uv run --no-sync ruff check src tests interactive/gen_data.py
All checks passed!
```

The two warnings are the existing openpyxl inability to parse decorative workbook
header/footer content; worksheet data are not skipped.

Mathematical tests cover dense numerical CRPS integration on randomized gapped and
open-tail histograms at `atol=1e-8`, the Monte Carlo energy identity, point masses,
the Uniform closed form, nonnegativity, exact gap/tail CDF values, the fine-grid
integrated-pinball identity, and empirical/Gaussian formulas. Integration tests
cover the exact response filter. Benchmark tests cover strict completion
boundaries, 9-versus-10 behavior, horizon/concept isolation, a not-yet-realized
prior forecast, row-order invariance, and invariance to appended future data.

Generated-output assertions establish:

- 3,070 score rows, exactly matching all calibration columns and row values;
- no duplicate 11-field forecast-target keys;
- finite nonnegative pooled/individual CRPS and seven pinball losses;
- PIT entirely in `[0,1]`;
- pooled CRPS no greater than average-individual CRPS on every row;
- benchmark presence exactly equivalent to its history count reaching ten;
- every nonnull skill equals `1 - pooled / benchmark`; and
- 38 compact score combinations in 800,301 bytes, below 1.2 MB.

The inline JavaScript parses under Node, generated compact score values reproduce
the source after the declared rounding, the Scores hash state renders through the
same dispatcher as the other views, and the token hash above is unchanged. A
mock-DOM audit rendered all 76 Scores states (38 combinations times Q1/all),
including nonempty tooltips and tables, control/hash round-trips, no more than
three visible series, and nullification of all 18 incomplete duplicate-round
benchmark cells.

## Honest gaps

- The availability rule is deliberately conservative at quarterly resolution,
  but it is not a historical release-date database. Annual revisions and actual
  publication days are not modeled.
- All outcomes are latest vintage. They are useful for ex-post scoring but not a
  real-time-vintage evaluation; ECB estimate statuses remain included.
- ECB annual histories are genuinely short (26–30 complete years), and the ECB
  forecast-error histories begin only with the survey. Early benchmark gaps are
  data limits, not filled estimates.
- ECB core HICP longer-term Gaussian scores are entirely unavailable under the
  ten-completed-error rule. Some pre/post cells elsewhere have only 6–8 eligible
  rows and are presented descriptively.
- The one-adjacent-bin-width tail closure is imposed by the project construction,
  not claimed by either survey provider. Extreme PIT values and CRPS therefore
  partly reflect that finite-support convention.
- The two tiny negative individual ECB probabilities are invalid distribution
  masses but are retained because the requested filter only tests the total.
  Pooled masses remain nonnegative; the affected average-individual scores should
  be interpreted with this caveat.
- Forecast rows sharing an eventual realization are correlated. No standard
  errors, significance tests, or independent-sample claims are made.
- Real-browser screenshot validation remains unavailable in this managed macOS
  sandbox; the static bundle, JavaScript syntax, full control matrix, hash state,
  token bytes, score provenance, and rendered mock-DOM states are audited instead.

## Working tree

The implementation, generated output, `PROGRESS.md`, and this report are left
uncommitted as requested. The task-specific “commit nothing” instruction was
followed despite the contradictory standing-order request for checkpoint commits.
