# Progress: external-review fixes

Branch `astra-review-fixes`, cut from `origin/main`. PR target: `main`.
Out of scope by brief: `paper/*.qmd`, bin reconstruction (`bins.py` endpoints,
`measures.round_stats` math), merging, deploying.

## State

Baseline before any change: `uv run pytest -q` → 165 passed; ruff format/check clean.

## Done

- Scouted the repository: `site/index.html`, `site/gen_data.py`,
  `src/expectations/{scores,measures,benchmarks,realizations}.py`,
  `scripts/download_ecb_annual_realizations.py`, `data/raw/ecb_annual_realizations_sources.json`,
  tests, CI. Confirmed every finding in the brief against the code.

## Findings confirmed against the code

1. `applyHash()` runs once at load; no `hashchange` listener. `writeHash()` uses
   `history.replaceState`, which does not fire `hashchange`, so a listener is safe.
2. `#tabs` buttons carry `role="tab"`/`aria-selected` only: no roving `tabindex`,
   no keyboard handler, no `aria-controls`, and `#panel` has no `role="tabpanel"`.
3. `site/index.html:751` claims benchmarks "use only information available before
   each forecast round". `benchmarks.period_completion_ordinal` filters on target
   *completion*, and `realizations.load_realization_history` supplies revised
   (latest-vintage) values.
4. `site/gen_data.py` omits `concept` from all three bundles. `outputs/measures.csv`
   carries US PRGDP `nominal_gnp` (1968Q4–1981Q2), `real_gnp` (1981Q3–1991Q4),
   `real_gdp` (1992Q1–); PRPGDP `gnp_implicit_deflator` (1968Q4–1991Q4),
   `gdp_implicit_deflator` (1992Q1–1995Q4), `chain_weighted_gdp_price_index` (1996Q1–).
   calibration/scores keep PRPGDP `gdp_implicit_deflator` but have no pre-1992 PRGDP rows.
5. Fan centre is `median` (median of respondents' density-implied means); band is
   pooled q25–q75. `outputs/measures.csv` already has pooled `q50`.
6. `scores._normalized_histogram` checks finiteness and a positive *total*, never
   per-bin non-negativity. `histogram_cdf([-1,2],[(0,1),(1,2)],.5)` → -0.5.
   `tests/test_scores.py::test_crps_is_nonnegative_for_random_and_signed_source_style_weights`
   exercises a tiny negative weight.
7. README shows `download_ecb_annual_realizations.py` with no `--refresh`, while the
   prose describes refreshing. The script reuses verified local copies by default.
8. The manifest records a Eurostat EA20 comparison (5 of 30 years differ at one
   decimal) but no archived Eurostat response exists under `data/raw/`.

## Next

- [ ] 1 hashchange
- [ ] 2 ARIA tabs
- [ ] 3 benchmark wording
- [ ] 4 concept eras
- [ ] 5 pooled median fan
- [ ] 6 reject negative weights
- [ ] 7 README acquisition commands
- [ ] 8 archive Eurostat comparator
- [ ] 9 tests
- [ ] ruff + pytest, push, open PR
