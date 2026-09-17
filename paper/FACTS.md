> Historical development document. Superseded for current findings and methods by the September 2026 growth-beliefs revision: see `RESEARCH_REVISION.md`, `paper/index.qmd`, and regenerated `outputs/`. Numbers below may use the former midpoint/sample-variance convention and approximate annual outcomes.

# Ground-truth sheet

Every claim the paper may state, with its verification status. Writers cite
nothing outside this sheet plus LITREVIEW.md (verified citations only).
Status codes: COMPUTED (this repo, this session), DOC (read in the survey
documentation in `data/docs/`), PENDING-SOL (awaiting the full pipeline),
PENDING-LIT (awaiting the verified lit review). Unresolved items carry
`[NEEDS …]` markers in the draft; resolve, never delete.

## The construction

- Law of total variance on reported histograms: total pooled variance =
  mean within-forecaster variance + between-forecaster variance
  (disagreement). Midpoint mass per bin; open tails get the adjacent bin's
  width. Rows kept when |Σprobs − 100| < 2, renormalized. COMPUTED (seed
  pipeline, `data/docs/seed_spf_density_pipeline.py`).

## US SPF — computed series (next-year PRGDP, Q1 rounds, 1992–2026)

- Total pooled SD: 1.24pp in 1992; mean 1.26pp over 1992–2020; peak 2.10pp
  in 2021; 1.36pp in 2026. COMPUTED.
- Disagreement share of total variance: median 0.18, decile range
  0.12–0.32, max 0.41 (2009). Average individual SD ≈ 0.89 × total SD.
  COMPUTED.
- ±1σ (total) coverage of realized annual-average real GDP growth: 23 of 33
  target years, 69.7% (theory: 68%). COMPUTED.
- Missed targets: 1996, 1997, 1998, 1999, 2000 (all upside), 2001
  (downside), 2008, 2009 (downside), 2020 (downside), 2021 (upside) — six
  consecutive misses 1996–2001, then only regime shifts. COMPUTED.
  NOTE: supersedes the earlier "five straight" phrasing; 2001 also missed.
- 2026 Q1: next-year consensus median 1.83%, IQR 0.40pp; 10-year average
  annual (RGDP10, point forecasts) median 2.1%, IQR 0.20pp. The decade
  answer is tighter than the next-year answer. COMPUTED.

## US SPF — survey structure

- Density variables and start dates: PRGDP/PRPGDP histograms back to 1968Q4
  (output concept changes: nominal GNP → real GNP 1981Q3 → real GDP 1992Q1;
  bin schemes in documentation Table 7); PRCCPI and PRCPCE (Q4/Q4 core CPI
  and core PCE growth) since 2007Q1; PRUNEMP since 2009Q2; RECESS
  (probability of a decline in real GDP, current + next four quarters).
  DOC (`data/docs/spf-documentation.txt` lines 59–90, 639–652, Table 7).
- Density horizons: current and next year only, until 2009Q2; current
  through +3 years after (PRGDP extension stated at line 66–69; PRPGDP and
  PRUNEMP block structure consistent with 4 target years by column count —
  PENDING-SOL for the doc-exact statement per variable).
- 2020Q2–2024Q1: much wider PRGDP bins (16+ … below −12); mechanically
  inflates measured SDs. DOC (Table 7) + seed. Magnitude of the mechanical
  effect: PENDING-SOL (IQR vs SD divergence).
- 10-year variables (RGDP10, CPI10, PCE10, UNEMP10) are single point
  forecasts — no densities at any horizon beyond +3. COMPUTED (file
  structure) + DOC.

## ECB SPF — survey structure

- Microdata: 111 quarterly rounds, 1999Q1–2026Q3, published openly.
  COMPUTED (files in `data/raw/ecb_spf/`).
- Density variables: HICP inflation, core HICP (since 2017Q1), real GDP
  growth, unemployment rate. DOC (dataset description, line 407 for core).
- Horizons: current year, next year(, year after next — PENDING-SOL);
  rolling 1y and 2y ahead of latest data; and a longer-term calendar year —
  four years ahead in Q1/Q2 rounds, five years ahead in Q3/Q4 rounds; in
  early years the longer-term question ran only in Q1 rounds. DOC
  (description lines 54–95, 105–113). Never call it a flat "five-year"
  series.
- Bin edges are encoded in the data column headers (`F0_0T0_4` styles) —
  scheme changes are self-describing. COMPUTED (2021Q2.csv inspected).

## Full-pipeline results (COMPUTED — SOL_REPORT.md; verified: 43 tests
green in an independent run, golden regression exact vs seed, LOTV
identity max error 4e-16)

- Coverage: 3,695 density round-target summaries; US PRGDP/PRPGDP/RECESS
  232 rounds 1968Q4–2026Q3; ECB 111 rounds all variables; 2,894
  concept-matched calibration rows.
- Stability + spike-decay: US PRGDP total SD 2010–19 mean 1.250, 2020–24
  mean 1.744, 2026 1.361. ECB RGDP 0.727 → 1.577 (2020–24; peak 2.616 in
  2020) → 0.786 in 2026. ECB HICP 0.676 → 0.965, still 0.913 in 2026 —
  inflation uncertainty has NOT fully decayed in the EA. US PRPGDP
  pandemic-era uncertainty DECLINED (0.806 → 0.761).
- Disagreement share (median share_between): US PRGDP 16.8%, ECB HICP
  14.3%, ECB RGDP 15.7% — but US core CPI 32.1%, core PCE 32.5%, PRPGDP
  27.1%, PRUNEMP 25.6%, ECB UNEMP 26.7%. Disagreement is the minority
  share everywhere (no median reaches 33%); the "10–20%" phrasing holds
  only for growth and EA prices. Say "a sixth to a third."
- Term structure (US Q1 2010–26, within/total): PRGDP h0 1.14/1.28 → h1
  1.29/1.41 → h2 1.37/1.48 → h3 1.38/1.49 — rises then plateaus after two
  years. PRUNEMP keeps rising through h3. ECB (balanced rounds,
  within/total): RGDP total INVERTS mildly — 0.86 at rolling-1y vs 0.81
  longer-term; HICP plateaus ~2y; UNEMP keeps rising (1.02 longer-term).
- Fixed-event shrinkage (2010–19 current-year total SD, Q1→Q4): PRGDP
  −38.6%, PRUNEMP −41.1%, PRPGDP −27.7%, PRCCPI −27.5%, PRCPCE −24.2%.
- Calibration (±1σ / pooled-90% coverage, all horizons): US PRGDP
  74.9/85.3, PRPGDP 82.5/92.5, PRUNEMP 63.6/86.4, PRCCPI 82.9/88.6,
  PRCPCE 76.4/87.2. ECB overconfident: HICP 56.7/71.8, RGDP 48.9/65.3,
  UNEMP 55.9/81.5. Q1 next-year US PRGDP 69.7% (= seed). Miss clusters:
  1996–99 (every forecast of those outcomes), 2020–21; every US
  PRPGDP/PRCCPI/PRCPCE forecast of 2021 AND 2022 missed both bands; all
  16 ECB calendar HICP forecasts of 2022 missed both bands. Counts are
  descriptive (shared realizations, not independent).
- ECB longer-term shift (through-2020 → 2021–26, total SD): HICP 0.699 →
  0.913 (+30.6%) vs rolling-1y +58.8%; longer-term consensus 1.824% →
  1.999% vs 1y 1.582% → 2.287%. Long expectations moved less than short —
  but they moved.
- Bin mechanics: 2020Q2–2024Q1 wide-bin era raised PRGDP within SD +59.4%
  vs pre-window but pooled IQR only +39.9%; at the clean 2024Q2 boundary
  next-year PRGDP SD fell 22% while IQR fell 3.9% — the mechanical
  signature. Use IQR for cross-era statements.
- CORRECTIONS to earlier claims: PRPGDP has TWO target-year blocks
  (current + next) per documentation Table 6 — not four; the SPF has NO
  UNEMP10 variable (the downloaded file was an HTML error page); RGDP10
  runs Q1-only 1992Q1–2026Q1 (35 rounds), CPI10 quarterly since 1991Q4.
- HICPX calibration COMPUTED (lane 2): 60.2% ±1σ / 72.7% pooled-90% over
  176 rows (57.7%/69.2% excluding ECB estimate-status observations);
  realization concept-verified "All-items excluding energy and food".

## Proper scores (COMPUTED — SCORES_REPORT.md; verified: 74 tests green in
an independent run, pooled≤individual on all 3,070 rows, skill identities
exact, Scores view browser-checked)

- Pooled vs average individual CRPS: 0.741 vs 0.817, a 9.25% gain; every
  row improves. CAVEAT: the sign is structural (CRPS is convex in the CDF,
  so the linear pool beats the average individual by Jensen) — the
  empirical content is the magnitude (3.5–18.7% by cell) and its
  cross-section: gains are smallest at ECB longer horizons, where the
  disagreement share is smallest.
- Climatology skill (expanding window, min 10 obs, no lookahead): positive
  for all nine survey-variables, +15.3% (ECB HICP, ECB RGDP) to +57.1%
  (US core CPI). Negative cells exist: US unemployment +3y −19.4%; ECB
  unemployment rolling-2y −16.6% and longer-term −21.2% (long-horizon
  unemployment densities lose to unconditional history).
- Gaussian-around-consensus (RMSE of past errors, same expanding rules) is
  the hard benchmark: variable-level skill positive for US real GDP
  (+6.2%) and all four ECB variables; NEGATIVE for US GDP prices,
  unemployment, core CPI, and core PCE — for those, the elicited density
  shape adds nothing beyond the consensus point wrapped in its own error
  history. It also adapts after 2020 (its RMSE learns the misses).
- Tails carry the clusters (pinball 05 vs 95, by target years): 2008–09
  growth losses in the LOWER tail (ECB 2.286 vs 0.215; US 0.572 vs 0.196);
  2020–22 inflation losses in the UPPER tail by factors ~5–9 (US GDP
  prices, both US cores, ECB HICP, ECB core); late-1990s US output upper
  tail. 2020–22 US growth balanced (crash + rebound).
- PIT: ECB real GDP U-shaped — 45.8% of rows in the two extreme deciles
  (underdispersion); ECB HICP 36.9%; US unemployment left-skewed (mean PIT
  0.355; 22.4% in the bottom decile).
- Benchmark coverage: climatology scored on 2,717/3,070 rows, Gaussian on
  2,451 (min-10 windows; ECB annual histories are 26–30 years; ECB core
  HICP longer-term has no Gaussian at all). Correlated rows, no
  significance tests — descriptive.
- Lit anchors verified: Boero, Smith and Wallis (2011, IJF 27(2), 379–393 —
  in the LITREVIEW corpus) on scoring rules and survey density forecasts;
  Gneiting and Raftery (2007), "Strictly Proper Scoring Rules, Prediction,
  and Estimation," JASA 102(477), 359–378 — VERIFIED from the fetched paper
  this session (DOI 10.1198/016214506000001437).

## Literature (verified — LITREVIEW.md, 84 works, all fetch-checked)

- AI-growth published range 0.1–30pp/yr: VERIFIED (Shenk 2026 AI Frontiers;
  Cunningham 2025 compilation of 33 forecasts; anchors Acemoglu 2024,
  Briggs–Kodnani 2023, Aghion–Bunel 2024, Davidson 2021, Erdil–Besiroglu
  2023; Karger et al. 2026 = the FRI + Chicago Fed survey, NBER WP 35046).
- "No survey anywhere regularly elicits 10-year-ahead growth densities":
  SUPPORTED by the verified inventory; sharpened by two one-off partial
  precedents (Christensen–Gillingham–Nordhaus 2018; Karger et al. 2026).
  State with the word "regularly."
- No live cross-survey uncertainty tracker exists: VERIFIED ABSENCE (ECB
  dashboard = latest 3 rounds only; FRED carries no SPF series; Philly Fed
  error-statistics page renders empty).
- Novelty per component: (a) decomposition DONE (Wallis school); (b) US
  long series PARTIAL (D'Amico–Orphanides 2008 the antecedent); (c)
  cross-Atlantic PARTIAL (Glas–Hartmann 2022 pool for rounding only);
  (d) panorama + term structure OPEN as assembly; (e) calibration method
  DONE, 2020s panel OPEN; (f) interactive OPEN; (g) elicitation-gap
  framing OPEN.
- US bin history (SPF documentation, verified): 15 bins 1968Q4, 6 from
  1981Q3, 10 from 1992Q1, 11 from 2009Q2; changes 2020Q2 and 2024Q2.
- Appendix 8 of LITREVIEW.md lists unverified items — cite NOTHING from it
  without fresh verification.

## Prohibitions

- No fabricated mechanisms; no numbers not on this sheet or in LITREVIEW.md.
- No process narration or review history in the paper.
- Realizations are latest-vintage: state as a scope limit, flat and active.
- Uncertainty ≠ disagreement is the founding distinction of this
  literature (Zarnowitz–Lambros) — the paper never conflates the terms.
- Nothing publishes without Max.
