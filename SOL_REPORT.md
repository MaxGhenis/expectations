> Historical development document. Superseded for current findings and methods by the September 2026 growth-beliefs revision: see `RESEARCH_REVISION.md`, `paper/index.qmd`, and regenerated `outputs/`. Numbers below may use the former midpoint/sample-variance convention and approximate annual outcomes.

# Forecast-uncertainty pipeline report

## Result

The pipeline is complete for every locally usable US and ECB SPF input. It writes
3,695 round-target density summaries, 254 US long-run point summaries, 1,156 US
recession-probability summaries, 2,894 concept-matched calibration rows, and a
14-row coverage audit. The command is:

```sh
PYTHONPATH=src UV_CACHE_DIR=/private/tmp/forecast-uncertainty-uv-cache \
  uv run --no-sync python -m forecast_uncertainty.build
```

The `--no-sync` qualification was necessary in this offline environment. A direct
`uv sync` was attempted, but dependency resolution tried to reach the package
index; the repository's already provisioned `.venv` contains the runtime and
development dependencies declared in `pyproject.toml`. No dependency was added.

The deliverables are:

- `outputs/measures.csv` — all density measures and pooled quantiles.
- `outputs/longrun_points.csv` — RGDP10, CPI10, and PCE10 point dispersion.
- `outputs/recess.csv` — RECESS1–5 summaries and concept-compatible outcomes.
- `outputs/calibration.csv` — forecast errors and both coverage flags.
- `outputs/coverage.csv` — filter accounting and source coverage.

## Coverage

For a density, “kept,” “dropped,” and “all-NaN” count respondent-target
histograms. For point and recession files, “kept” counts nonmissing individual
observations and the sum-to-100 filter is not applicable.

| Survey | Variable | Rounds | First–last | Target groups | Kept | Dropped | All-NaN |
|---|---|---:|---|---:|---:|---:|---:|
| ECB | HICP | 111 | 1999Q1–2026Q3 | 633 | 27,698 | 3 | 7,870 |
| ECB | HICPX | 39 | 2017Q1–2026Q3 | 234 | 6,455 | 3 | 5,395 |
| ECB | RGDP | 111 | 1999Q1–2026Q3 | 633 | 27,120 | 3 | 8,481 |
| ECB | UNEMP | 111 | 1999Q1–2026Q3 | 633 | 24,980 | 9 | 9,879 |
| US | PRGDP | 232 | 1968Q4–2026Q3 | 553 | 17,673 | 9 | 3,668 |
| US | PRPGDP | 232 | 1968Q4–2026Q3 | 413 | 13,932 | 0 | 1,942 |
| US | PRUNEMP | 70 | 2009Q2–2026Q3 | 280 | 7,917 | 0 | 3,035 |
| US | PRCCPI | 79 | 2007Q1–2026Q3 | 158 | 5,150 | 0 | 1,206 |
| US | PRCPCE | 79 | 2007Q1–2026Q3 | 158 | 4,900 | 0 | 1,456 |
| US | RECESS | 232 | 1968Q4–2026Q3 | 1,156 | 41,660 | 0 | 0 |
| US | RGDP10 | 35 | 1992Q1–2026Q1 | 35 | 1,127 | 0 | 0 |
| US | CPI10 | 140 | 1991Q4–2026Q3 | 140 | 4,664 | 0 | 0 |
| US | PCE10 | 79 | 2007Q1–2026Q3 | 79 | 2,506 | 0 | 0 |
| US | UNEMP10 | 0 | — | 0 | 0 | 0 | 0 |

All 27 sum-filter drops are explicit zero vectors rather than near-100 rounding
cases. The nine US drops are PRGDP responses in 2013Q3 (two far horizons),
2016Q1 (two far horizons), 2017Q1 (all four horizons), and 2025Q1 (the farthest
horizon). The 18 ECB drops all occur in 2018Q1: three each for HICP, HICPX, and
RGDP and nine for unemployment. Entirely missing histograms are counted before
NaNs are replaced by zero and are not called filter failures.

## Headline findings

### Stability of total pooled uncertainty

For the US, these are Q1 next-calendar-year total SDs. For the ECB, they are
annual means of the quarterly rolling-one-year total SDs; 2026 contains Q1–Q3.
The US PRGDP and PRPGDP summaries use the primary 1992+ GDP sample.

| Series | Years | Full-sample mean | 2010–19 mean | 2020–24 mean | Peak | 2026 |
|---|---:|---:|---:|---:|---|---:|
| US PRGDP | 1992–2026 | 1.336 | 1.250 | 1.744 | 2.104 (2021) | 1.361 |
| US PRPGDP | 1992–2026 | 0.923 | 0.806 | 0.761 | 1.270 (2008) | 0.653 |
| US PRUNEMP | 2010–2026 | 0.784 | 0.721 | 0.959 | 1.194 (2021) | 0.589 |
| US PRCCPI | 2007–2026 | 0.713 | 0.679 | 0.796 | 0.970 (2022) | 0.639 |
| US PRCPCE | 2007–2026 | 0.677 | 0.653 | 0.736 | 0.993 (2022) | 0.615 |
| ECB HICP | 1999–2026 | 0.684 | 0.676 | 0.965 | 1.219 (2023) | 0.913 |
| ECB HICPX | 2017–2026 | 0.729 | 0.555* | 0.838 | 1.077 (2023) | 0.707 |
| ECB RGDP | 1999–2026 | 0.838 | 0.727 | 1.577 | 2.616 (2020) | 0.786 |
| ECB UNEMP | 1999–2026 | 0.677 | 0.700 | 0.938 | 1.285 (2020) | 0.696 |

\*HICPX's pre-shock comparison contains 2017–19 only.

The pre-pandemic level is fairly stable for US real GDP and the main ECB
variables, but “stable” does not mean invariant. Pandemic-era uncertainty rose
39.5% for PRGDP, 42.8% for ECB HICP, 116.9% for ECB growth, and 34.1% for ECB
unemployment relative to 2010–19. US GDP-price uncertainty instead declined.
PRGDP's complete Q1 next-year series reproduces the validated seed measures
exactly in all four decomposition columns (test tolerance `1e-9`).

### How much is disagreement?

The table reports the distribution of `share_between`. US PRGDP and PRPGDP
again exclude the pre-1992 annex.

| Survey-variable | Rows | P25 | Median | P75 | Share of rows at or below 20% |
|---|---:|---:|---:|---:|---:|
| ECB HICP | 633 | 10.0% | 14.3% | 21.9% | 70.6% |
| ECB HICPX | 234 | 9.4% | 15.3% | 24.7% | 67.9% |
| ECB RGDP | 633 | 11.3% | 15.7% | 23.4% | 66.7% |
| ECB UNEMP | 633 | 17.8% | 26.7% | 38.3% | 31.0% |
| US PRGDP | 418 | 12.3% | 16.8% | 22.2% | 64.6% |
| US PRPGDP | 278 | 20.5% | 27.1% | 35.1% | 23.7% |
| US PRUNEMP | 280 | 19.3% | 25.6% | 33.9% | 28.2% |
| US PRCCPI | 158 | 21.8% | 32.1% | 45.7% | 19.6% |
| US PRCPCE | 158 | 24.9% | 32.5% | 40.0% | 12.0% |

Thus the “10–20%” characterization works well for ECB prices and growth and US
real GDP, but not as a universal fact. Between-forecaster variation is materially
larger for unemployment and the US inflation densities.

### Term structure and fixed-event shrinkage

US Q1 means below are `within_sd / total_sd`. Restricting the four-horizon
variables to 2010–26 supplies a balanced 17-round comparison.

| Variable and sample | h=0 | h=1 | h=2 | h=3 |
|---|---:|---:|---:|---:|
| PRGDP, 2010–26 | 1.137 / 1.276 | 1.294 / 1.412 | 1.368 / 1.481 | 1.384 / 1.485 |
| PRUNEMP, 2010–26 | 0.562 / 0.640 | 0.662 / 0.784 | 0.718 / 0.880 | 0.750 / 0.937 |
| PRPGDP, 1992–26 | 0.680 / 0.822 | 0.779 / 0.923 | — | — |
| PRCCPI, 2007–26 | 0.497 / 0.653 | 0.575 / 0.713 | — | — |
| PRCPCE, 2007–26 | 0.490 / 0.624 | 0.551 / 0.677 | — | — |

PRGDP nearly plateaus after two years, whereas unemployment continues to rise.
The missing PRPGDP h=2 and h=3 cells reflect the documented/local two-block
structure, not a finding about its term structure.

The fixed-event effect is strong. In the clean 2010–19 sample, mean current-year
total SD falls monotonically as information arrives:

| Variable | Q1 | Q2 | Q3 | Q4 | Q1-to-Q4 change |
|---|---:|---:|---:|---:|---:|
| PRGDP | 1.088 | 0.969 | 0.846 | 0.668 | −38.6% |
| PRPGDP | 0.714 | 0.671 | 0.633 | 0.517 | −27.7% |
| PRUNEMP | 0.555 | 0.497 | 0.418 | 0.326 | −41.1% |
| PRCCPI | 0.604 | 0.569 | 0.510 | 0.438 | −27.5% |
| PRCPCE | 0.589 | 0.543 | 0.523 | 0.446 | −24.2% |

ECB values are round-balanced means over the 105 rounds containing all three
modern horizon classes (39 for HICPX). Early duplicate longer-term targets are
first averaged within round. Cells are `within_sd / total_sd / IQR`.

| Variable | Rolling 1y | Rolling 2y | Longer term |
|---|---:|---:|---:|
| HICP | 0.603 / 0.693 / 0.849 | 0.665 / 0.731 / 0.869 | 0.697 / 0.745 / 0.850 |
| HICPX | 0.620 / 0.730 / 0.891 | 0.682 / 0.769 / 0.890 | 0.734 / 0.804 / 0.896 |
| RGDP | 0.710 / 0.856 / 1.009 | 0.754 / 0.849 / 0.958 | 0.759 / 0.813 / 0.926 |
| UNEMP | 0.589 / 0.688 / 0.805 | 0.670 / 0.814 / 0.967 | 0.796 / 1.017 / 1.233 |

HICP within uncertainty rises through two years and then plateaus. RGDP within
uncertainty also plateaus, while total uncertainty is highest at one year because
short-horizon disagreement is larger. Unemployment uncertainty keeps rising.

### Calibration

These are all round-target rows with a verified local realization mapping. An
error is `realized − consensus_mean`; both interval checks are inclusive.

| Survey-variable | n | Inside ±1 total SD | Inside pooled 90% |
|---|---:|---:|---:|
| US PRGDP | 382 | 74.9% | 85.3% |
| US PRPGDP | 268 | 82.5% | 92.5% |
| US PRUNEMP | 228 | 63.6% | 86.4% |
| US PRCCPI | 140 | 82.9% | 88.6% |
| US PRCPCE | 148 | 76.4% | 87.2% |
| ECB HICP | 575 | 56.7% | 71.8% |
| ECB RGDP | 579 | 48.9% | 65.3% |
| ECB UNEMP | 574 | 55.9% | 81.5% |

For the directly comparable one-year series, Q1 next-year US coverage is
69.7%/78.8% for PRGDP, 69.7%/93.9% for PRPGDP, 57.1%/85.7% for unemployment,
82.4%/88.2% for core CPI, and 72.2%/88.9% for core PCE. ECB rolling-one-year
coverage is 49.0%/72.1% for HICP (actual-only observations), 50.5%/70.1% for
growth, and 67.0%/85.8% for unemployment.

Misses cluster rather than arriving evenly. For US PRGDP, all eight forecasts of
each 1996–99 outcome miss ±1 SD; 15 of 16 forecasts of 2020 and 12 of 16 for
2021 miss it. Every US PRPGDP, PRCCPI, and PRCPCE forecast for 2021 and 2022
misses both bands. US unemployment has 14 of 16 ±1 SD misses for 2020. For the
ECB, all 16 calendar-target HICP forecasts for 2022 miss both bands; 2020, 2021,
and 2023 are also miss-heavy. Growth misses cluster around 2008–09, 2020–21,
and several post-crisis outcomes; unemployment's clearest clusters include 2009
and 2012. Forecasts of a shared realization are not independent, so these counts
are descriptive rather than inference-ready.

All realizations are latest-vintage. Eighteen HICP calibration rows use 2025
observations containing an ECB `E` status. Excluding them leaves 557 actual-only
rows and lowers coverage to 55.3% and 70.9%, respectively. HICPX has no local,
verifiably matched realization and is intentionally absent from calibration.

### ECB longer-term shift

“Longer term” is the accurate label: since 2001Q2 it is four calendar years ahead
in Q1/Q2 and five in Q3/Q4, while early Q1 surveys also contain a rolling
five-year target. The comparison below balances at the round level and separates
through-2020 from 2021–26.

| Variable | Rolling-1y total SD | Longer-term total SD |
|---|---:|---:|
| HICP | 0.608 → 0.965 (+58.8%) | 0.699 → 0.913 (+30.6%) |
| HICPX | 0.588 → 0.829 (+41.1%) | 0.734 → 0.853 (+16.3%) |
| RGDP | 0.752 → 1.170 (+55.6%) | 0.778 → 0.934 (+20.0%) |
| UNEMP | 0.641 → 0.814 (+26.9%) | 1.008 → 1.045 (+3.7%) |

For HICP specifically, longer-term consensus inflation moves from 1.824% to
1.999%, while the rolling-one-year consensus moves much more—from 1.582% to
2.287%. Both expected inflation and uncertainty therefore shift after 2021, but
the longer-term series moves much less than the one-year series.

## Bin-change mechanics

The US `bin_scheme` field identifies every era. To isolate the conspicuously wide
2020Q2–2024Q1 grids, the table compares matched windows and averages all four
horizons equally: pre is 2016Q2–2020Q1 (16 rounds), wide is 2020Q2–2024Q1 (16),
and post is 2024Q2–2026Q3 (10).

| Variable-period | Within SD | Total SD | Pooled IQR |
|---|---:|---:|---:|
| PRGDP pre | 1.102 | 1.205 | 1.418 |
| PRGDP wide | 1.756 | 1.972 | 1.985 |
| PRGDP post | 1.233 | 1.308 | 1.495 |
| PRUNEMP pre | 0.583 | 0.688 | 1.005 |
| PRUNEMP wide | 0.938 | 1.151 | 1.439 |
| PRUNEMP post | 0.575 | 0.632 | 0.724 |

Wide/pre changes are +59.4% for within SD, +63.6% for total SD, but +39.9% for
IQR in PRGDP. They are +60.9%, +67.2%, and +43.2% for unemployment. Thus the
within-SD/IQR ratio rises 13.9% for PRGDP and 12.4% for unemployment; the
total-SD/IQR ratio rises 16.9% and 16.8%. This divergence is the signature
expected when coarser bins and wider tail closures inflate moments more than
central quantiles, although the pandemic also raised genuine uncertainty and
disagreement.

At the clean 2024Q1-to-Q2 scheme boundary, next-year PRGDP within SD and total
SD fall 22.3% and 22.1%, while IQR falls only 3.9%. The corresponding
unemployment changes are −35.0%, −35.3%, and −36.2%. These one-quarter changes
remain descriptive because the information set also changed.

## Judgment calls and documentary basis

| Decision | Implementation and source |
|---|---|
| US target concepts | PRGDP is nominal GNP through 1981Q2, real GNP through 1991Q4, then real GDP (`spf-documentation.txt:1581–1585`). PRPGDP changes from the GNP deflator to GDP prices (`:1586–1590`); the 1992–95 implicit-deflator qualification is at `:1512–1517`. Concepts are retained row by row. |
| US target definitions | PRGDP and PRPGDP are annual-average/annual-average (`:1497–1517`); PRCCPI and PRCPCE are Q4/Q4 with Q4 equal to the October–December average (`:1519–1551`); PRUNEMP is the 12-month average (`:1553–1562`). |
| US schemes and blocks | Every literal edge comes from Tables 6–9 (`:1662–1836`). Table 7 documents PRGDP's four blocks and its 2020Q2 and 2024Q2 schemes (`:1756–1779`); Table 9 does the same for unemployment (`:1814–1836`). Table 6 documents only two PRPGDP blocks (`:1662–1721`). |
| Early US targets | The pre-1981 next-year exceptions are encoded exactly from `:1604–1612`. Because the documentation says 1985Q1 and 1986Q1 targets cannot be confirmed (`:1614–1618`), those blocks remain named but have null target year/horizon and never calibrate. |
| US horizon quarters | `4*(target_year − YEAR) + (4 − QUARTER) + 1` is interpreted as the inclusive number of quarters from the survey quarter through target-year Q4: Q1 current/next are 4/8 and Q4 current/next are 1/5. This matches fixed calendar-year events (`:1505–1509`) and, for the modern sample, information through the preceding quarter (`:220–227`, `:288–307`). |
| RECESS | RECESS1–5 mean current quarter through the following four, with a decline defined quarter over quarter (`:1564–1570`, `:1635–1659`). Outcomes are attached only to the chain-weighted-real-GDP concept. |
| ECB variables | HICP is year-on-year HICP, RGDP is year-on-year real GDP, and unemployment is a labor-force percentage (`ecb_spf_dataset_description.txt:19–30`). HICPX point/density timing is documented at `:43–45` and `:470–472`. |
| ECB horizons | Calendar and rolling definitions come from `:48–73`; the pre-2001Q2 seven-horizon structure and Q1-only five-year targets are at `:79–97`. Raw year/month/quarter labels are preserved as specified at `:152–157`; calendar-year rows are annual averages (`:477–481`). Rolling `horizon_years` is nominally 1, 2, or 5; calendar targets use the exact target-year difference. |
| ECB bin edges | Headers are self-describing (`:165–168`, `:437–456`). Finite bins retain their literal closed endpoints: `F0_0T0_4` is `[0.0, 0.4]`, followed by (for example) `[0.5, 0.9]`; no `+0.1` or 0.45 boundary is introduced. This leaves zero-mass 0.1 gaps in the continuous surrogate. The “closed interval” legend is at `:404`, and open-tail semantics are at `:405–414`. Per the requested construction, an open tail is truncated to the width of the adjacent literal finite bin. |
| Histogram interpolation | Respondent moments use documented bin midpoints, with open tails closed by one adjacent-bin width. Pooled quantiles treat mass as uniform inside each literal closed bin and interpolate linearly; gaps carry zero mass. This is the paper's imposed construction, not a survey-provider claim. |
| Realization matching | Modern US mappings follow the documented target aggregations above. The local core-PCE JSON identifies DPCCRG-M as “PCE excluding food and energy,” so the mapping is confirmed. ECB rolling observations match the raw month/quarter target and calendar targets use complete-year averages. No uncertain concept is silently joined. |

## Gaps and anomalies

- `individual_unemp10.xlsx` is an HTML error page, not an Excel workbook. UNEMP10
  is therefore reported as zero coverage; it is not inferred from another file.
- The build brief says PRPGDP has four blocks after 2009Q2, but both the official
  Table 6 and the local `PRPGDP1`–`PRPGDP20` columns support only current and next
  year. The pipeline follows the documented/local two-block structure.
- No core-HICP realization file was supplied, so HICPX calibration is empty.
  The local core-CPI series ends in 2025Q1, limiting complete Q4/Q4 outcomes to
  2024; the core-PCE file supports a complete 2025.
- Per the requested 1992+ realization mapping, latest BEA real-GDP and GDP-price
  series are used beginning in 1992. The survey documentation nevertheless says
  1992–95 forecasts used fixed-weight real GDP and the GDP implicit deflator
  (`spf-documentation.txt:1509–1517`), so those early modern rows are not a
  vintage-perfect national-accounts match. They remain flagged by forecast and
  realization concept columns for sensitivity work.
- All realization data are latest-vintage; real-time vintage calibration is future
  work. ECB HICP has estimated 2025 observations as described above. The ECB
  source codes also mix a changing-composition HICP aggregate (`U2`) with fixed
  EA20 GDP and unemployment series (`I9`), another interpretation caveat.
- Two tiny negative source probabilities are retained because the specified filter
  tests only the sum: HICPX 2023Q1, target 2024, forecaster 115 (−0.01757223),
  and RGDP 2023Q1, target 2024Q3, forecaster 107 (−0.01213819). Their histograms
  still sum within tolerance. They are source anomalies, not corrections.
- Four RECESS fifth-horizon cells are wholly missing (1969Q1, 1969Q3, 1970Q1,
  and 1974Q3), explaining 1,156 rather than 1,160 round-horizon groups. Only 600
  of the 1,156 rows have concept-compatible realized outcomes; pre-1996
  fixed-weight GDP/GNP forecasts intentionally remain unscored.
- Core HICP has point forecasts in 2016Q4 but density forecasts only from 2017Q1,
  exactly as the ECB note states. The pipeline counts density coverage from 2017Q1.
- In 2019Q2, explanatory text discusses an HICP release-timing exception, while
  the raw files retain their explicit rolling target labels. Calibration follows
  the raw `TARGET_PERIOD`, not an inferred replacement.
- The 1990Q2 US survey is retrospective and has only nine respondents
  (`spf-documentation.txt:985–991`). Historical forecaster IDs are also not always
  stable persons or firms (`:1389–1412`); this does not affect round-level results
  but matters for future panel analysis.

## Validation

The final suite contains 43 tests covering every distinct US bin era, ECB open and
closed header forms, literal ECB edges, strict sum filtering, pooled interpolation,
the total-variance identity, concept guards, source coverage, and the seed golden
regressions. On the generated output there are no duplicate round-target keys,
quantiles are ordered, every variance share lies in `[0,1]`, and the maximum
absolute error in `total_sd² = within_sd² + disagreement²` is `3.6e-15`.

Final checks:

```text
uv run --no-sync pytest -q          43 passed, 2 benign openpyxl warnings
uv run --no-sync ruff format ...    10 files already formatted
uv run --no-sync ruff check ...     All checks passed
```

The openpyxl warnings concern unparseable workbook header/footer decoration; no
worksheet data are skipped.
