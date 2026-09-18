# Build brief: forecast-uncertainty data pipeline

You are building the data pipeline for a new working paper by Max Ghenis:
"What do forecasters say they don't know?" — elicited macroeconomic forecast
uncertainty over time, from the probability distributions professional
forecasters themselves report in the US SPF (Philadelphia Fed) and the ECB SPF.
Everything you need is LOCAL in this repo — you have NO network access. If
something is missing, note it in the report; never fake or approximate silently.

## The core construction (already validated in a seed pipeline)

Read `data/docs/seed_spf_density_pipeline.py` first — it is the validated seed
(US PRGDP next-year, Q1 rounds only). Your job generalizes it to every density
variable, every horizon block, every quarterly round, both surveys.

Per (survey, variable, round, target): each forecaster i reports a histogram.
With bin midpoints `mid` and normalized weights W_i:

- m_i = Σ W_i·mid, v_i = Σ W_i·mid² − m_i²
- within_sd = sqrt(mean(v_i)) — average individual (stated) uncertainty
- disagreement = sd(m_i) (ddof=1) — between-forecaster
- total_sd = sqrt(mean(v_i) + var(m_i)) — law of total variance, the pooled
  mixture SD
- share_between = var(m_i) / (mean(v_i) + var(m_i))
- pooled mixture quantiles q05 q10 q25 q50 q75 q90 q95: aggregate the
  histograms (mean probability per bin across forecasters), treat mass as
  uniform within each closed bin, open tails get width equal to the adjacent
  bin's width; linear interpolation.
- Filters (same as seed): drop all-NaN rows, NaN→0, keep rows with
  |Σprobs − 100| < 2, renormalize.

Also compute `iqr = q75 − q25` of the pooled mixture — it is less sensitive to
the bin-scheme changes than the SD and serves as the robustness measure.

## US SPF inputs

`data/raw/individual_{prgdp,prpgdp,prunemp,prccpi,prcpce,recess}.xlsx` — one
sheet each, columns YEAR, QUARTER, ID, INDUSTRY, then VAR1..VARn probability
columns (percent). All files are padded to the full 1968Q4–2026 round panel;
rows are NaN before a variable's start. Also
`individual_{rgdp10,cpi10,pce10,unemp10}.xlsx` — 10-year-ahead POINT forecasts
(single value column); compute mean/median/dispersion (sd, IQR across
forecasters) per round for these.

**Bin schemes: parse them from `data/docs/spf-documentation.txt`** (extracted
from the official PDF; the PDF itself is next to it). Table 7 covers PRGDP —
the seed encodes the 1992Q1+ eras already (S1–S4 in the seed file; reuse and
verify against the doc). The analogous tables for PRPGDP, PRUNEMP,
PRCCPI/PRCPCE and the earlier eras are in the same documentation — encode ALL
eras from the tables, do NOT guess a single bin edge. Key structural facts to
verify in the doc, then implement:

- PRGDP/PRPGDP: 2 target years (current, next) before 2009Q2; 4 target years
  after (current..+3). Column blocks are contiguous per target year.
- PRUNEMP: since 2009Q2, 4 target years.
- PRCCPI/PRCPCE: since 2007Q1, 2 target years (current, next).
- Pre-1992 PRGDP/PRPGDP: densities go back to 1968Q4 for nominal GNP and
  switch concepts (nominal GNP → real GNP → real GDP; deflator concepts
  likewise). Encode what the documentation says and tag each row with a
  `concept` column (e.g. `nominal_gnp`, `real_gnp`, `real_gdp`) so the paper
  can use 1992+ as the primary sample and the earlier eras as an annex.
- 2020Q2–2024Q1 wide-bin era: tag `bin_scheme` per (round, variable) so the
  mechanical uncertainty inflation is identifiable.
- RECESS is NOT a histogram: RECESS1..5 are probabilities of a decline in real
  GDP in the current and next four quarters. Output a separate table: per
  round and horizon-quarter, mean probability, median, disagreement (sd).

**Fixed-event structure**: US targets are calendar years. For each round and
target-year block emit `target_year`, `horizon_years = target_year − YEAR`,
and `horizon_quarters = 4*(target_year − YEAR) + (4 − QUARTER) + 1` (quarters
of the target year still unknown at the survey; verify the convention makes
sense against the doc and state it in the report). Keep ALL quarterly rounds —
within-year uncertainty shrinkage as the event approaches is a result, not a
nuisance.

## ECB SPF inputs

`data/raw/ecb_spf/{YYYY}Q{Q}.csv` — 111 rounds 1999Q1–2026Q3. Format: stacked
sections, one per variable, each starting with a caption line (e.g.
"INFLATION EXPECTATIONS; YEAR-ON-YEAR CHANGE IN HICP") then a header
`TARGET_PERIOD,FCT_SOURCE,POINT,<bin columns>`. FCT_SOURCE is the anonymized
forecaster id. **Bin edges are self-describing in the column headers**:
`FN1_0TN0_6` = from −1.0 to −0.6, `F0_0T0_4` = 0.0–0.4, `TN1_0` = below −1.0,
`F4_0` = 4.0 and above. Write a header parser (F=from, T=to, N=negative);
this is era-proof — schemes changed over time (see Annex 3 of
`data/docs/ecb_spf_dataset_description.txt`) but headers always encode edges.
NOTE the ECB convention (dataset description, note under Annex 3): bins are
generally [lower, upper] labeled ranges like 0.0–0.4 with 0.5–0.9 next, i.e.
one-decimal grids; treat the effective continuous edges as adjacent (0.45
style midpoint conventions are NOT wanted — use bin edges lower→upper+0.1
adjacency? NO: read the description's exact statement about interval
boundaries and implement what it says; document your choice in the report).
Open tails: same adjacent-width convention as US.

Variables per round: HICP inflation, core HICP (since 2017Q1), real GDP
growth, unemployment rate (identify sections by caption text). TARGET_PERIOD
values mix calendar years ("2021"), rolling horizons ("Dec 2021", "2021Q2"
style), and a longer-term (~5-calendar-years-ahead) year. Classify each into:
`current_year`, `next_year`, `year_after_next`, `longer_term`, `rolling_1y`,
`rolling_2y` using the dataset description's definitions. Emit `target_period`
raw plus the classification and an approximate `horizon_years`.

## Realizations and calibration

Local realization files (all in `data/raw/`):

- `dbnomics_us_rgdp_growth_annual.json` (BEA A191RL-A, annual-average real GDP
  growth) → PRGDP target concept for 1992+ (verify in doc: annual-average over
  annual-average percent change).
- `dbnomics_us_gdp_price_index_annual.json` (A191RG-A levels) → compute annual
  growth → PRPGDP (1992+ concept).
- `dbnomics_us_unrate_monthly.json` (LNS14000000) → annual average → PRUNEMP.
- `dbnomics_us_cpi_sa_monthly.json`, `dbnomics_us_corecpi_sa_monthly.json`,
  `dbnomics_us_corepce_price_monthly.json` (NIPA T20804 DPCCRG-M — CONFIRM
  from the JSON metadata that this is the core PCE price index; if not, flag) →
  PRCCPI/PRCPCE target is Q4/Q4 core inflation (verify in doc) → compute Q4/Q4
  from monthly indices.
- `dbnomics_us_rgdp_growth_quarterly.json` → quarterly declines, for RECESS
  ex-post evaluation (a decline = negative q/q SAAR growth).
- `ecb_ea_hicp_yoy_monthly.csv`, `ecb_ea_rgdp_yoy_quarterly.csv`,
  `ecb_ea_unemployment_monthly.csv` (ECB Data Portal csvdata format) → ECB SPF
  calendar-year targets are annual averages (verify in the dataset
  description); rolling targets map to the specific month/quarter.

DBnomics JSON: `series.docs[0]` has parallel `period` and `value` arrays.

**Rule: a calibration row exists only where the realization concept verifiably
matches the elicited target concept per the documentation.** Where the mapping
is uncertain (e.g. pre-1992 concepts, core HICP), leave calibration empty and
list the gap in the report. All realizations are latest-vintage — note this
limitation explicitly in the report (real-time vintages are future work).

Calibration outputs per (survey, variable, horizon-class, round): consensus
mean, realized value, error, `inside_1sd` (|error| ≤ total_sd), and also
`inside_pooled_90` (realization within pooled mixture [q05, q95]).

## Deliverables

Package `src/forecast_uncertainty/` (src layout; pyproject is set up, use
`uv sync` then `uv run …`):

- `us_spf.py`, `ecb_spf.py` — parsers returning tidy long DataFrames
- `bins.py` — all US bin-scheme eras (from the doc) + the ECB header parser
- `measures.py` — round_stats, pooled quantiles, IQR (pure functions)
- `realizations.py` — realization series loaders + concept mappings
- `build.py` — `uv run python -m forecast_uncertainty.build` writes:
  - `outputs/measures.csv` — survey, variable, concept, year, quarter,
    target_year/target_period, horizon_class, horizon_years, horizon_quarters,
    bin_scheme, n, mean, median, within_sd, disagreement, total_sd,
    share_between, q05..q95, iqr
  - `outputs/longrun_points.csv` — the 10-year US point-forecast dispersion
  - `outputs/recess.csv`
  - `outputs/calibration.csv`
  - `outputs/coverage.csv` — rounds parsed per survey×variable, first/last
    round, rows kept/dropped by the sum-to-100 filter

Tests (pytest, `tests/`): bin-edge parsing per era incl. ECB header edge cases
(TN…, F…T…, open tails); law-of-total-variance identity on synthetic data;
sum-filter behavior; **golden-value regression**: next-year PRGDP Q1 measures
must reproduce `tests/fixtures/seed/spf_uncertainty_disagreement.csv` (columns
within_sd, dis, total, share_between; atol 1e-9 — the construction is
identical) and the calibration flags in `spf_errors.csv`; coverage counts
(e.g. 111 ECB rounds, PRCCPI starts 2007Q1). Run `uv run pytest` and
`uv run ruff format` before finishing.

## Report — write `SOL_REPORT.md`

1. Coverage table: rounds×variables parsed per survey, drops and why.
2. Computed headline numbers for the paper's five stylized facts:
   (a) stability of total pooled uncertainty (next-year PRGDP by year — must
   match seed — plus the same series for PRPGDP/PRUNEMP/PRCCPI/PRCPCE and ECB
   HICP/growth/unemployment 1y);
   (b) share_between distributions per survey×variable (is disagreement
   really only ~10–20% of total variance everywhere?);
   (c) the term structure of stated uncertainty: within_sd and total_sd by
   horizon_years 0–3 (US, fixed survey quarter = Q1 to control fixed-event
   effects, and also the within-year shrinkage pattern by quarter) and by ECB
   horizon class 1y/2y/5y — does stated uncertainty rise with horizon, and
   where does it plateau?;
   (d) calibration: ±1σ coverage and pooled-90% coverage per variable; where
   misses cluster in time;
   (e) the ECB longer-term (5y) series over 1999–2026 — level, and the
   post-2021 shift, vs the 1y series.
3. Bin-change mechanics: quantify the 2020Q2 wide-bin era's mechanical effect
   (e.g. within_sd vs pooled IQR divergence during 2020–2024).
4. Every judgment call you made (ECB bin edges, horizon conventions, target
   concept mappings), each traced to the doc line that justifies it.
5. Gaps and anomalies, honestly.

Conventions: sentence-case headings; comments only where the code can't speak;
`uv run` for everything; no new dependencies beyond pyproject without noting
why in the report. Do not modify `data/` (read-only inputs) except nothing —
outputs go to `outputs/`. Commit nothing — leave the working tree for review.
