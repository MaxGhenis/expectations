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

## Done (all nine fixes)

1. **hashchange** — `applyHash` now also runs on `hashchange`, then re-renders and
   re-canonicalizes. `writeHash` stays on `history.replaceState`, which does not fire
   `hashchange`, so the listener cannot loop.
2. **ARIA tabs** — ids, `aria-controls="panel"`, roving `tabindex`, Left/Right/Home/End
   with wrap, `role="tabpanel"` + `aria-labelledby` on `#panel`, one `setActiveTab` owning
   the state. The `<style>` block, every `class` attribute and every inline `style` are
   byte-identical to `origin/main`, so the visual design is unchanged by construction.
3. **Benchmark wording** — the scores note, README (two places), `site/paper/index.html`
   and three `benchmarks.py` docstrings now say target-period completion and revised data.
   `grep -c "information available"` over the whole page is 0.
4. **Historical concepts** — `concept` carried into all three bundles; each non-Overview
   view appends an era sentence in plain words and names the concept in the hover tooltip
   for exactly the non-modern rounds. Ranges are computed from the rows actually plotted.
5. **Pooled median fan** — `q50` carried into the measure bundle; the fan's line, y-domain
   and end label read it, labelled "pooled median" in legend, tooltip, table and note. The
   respondent-mean median stays as "Median of respondent means". The decomposition IQR
   table had the same mixed pair and now shows pooled q50 between pooled q25 and q75.
6. **Signed weights** — `histogram_cdf`, `histogram_crps` and `histogram_quantiles` reject
   negative or nonfinite mass. No internal signed path existed: every pipeline histogram
   goes through `filter_probability_rows`, which already rejects negative cells. The old
   "signed source-style weights" test asserted nonnegativity on input the filter cannot
   emit; it now asserts the rejection and the non-monotonicity motivating it.
7. **README acquisition** — both invocations documented for what each does.
8. **Eurostat comparator** — archived at `data/raw/eurostat_ea20_rgdp_growth_annual.json`,
   pinned by SHA-256 in the same manifest, reused unless `--refresh`. Verified loader in
   `realizations.py` checks URL, checksum and all four JSON-stat dimensions. Still 5 of 30
   years (2012, 2014, 2017, 2019, 2024) differ at one decimal.
9. **Tests** — `tests/test_site_bundle.py`, Node-free, plus new scoring and provenance
   tests. Every new site check was mutation-tested.

## Verification

- `uv run pytest -q` → 204 passed (165 on `origin/main`).
- `uv run ruff format --check` and `ruff check` over `src tests scripts site/gen_data.py` → clean.
- Full pipeline rebuild (`expectations.build`, `build_research.py`, `build_panorama.py`)
  leaves every `outputs/*.csv` byte-identical: the new guards change no result.
- 54 jsdom assertions against the real page (harness kept outside the repo, since CI has
  no Node step) covering hashchange, the whole tab pattern, era notes and tooltips per
  view, and that the fan's end label reports q50 rather than the respondent-mean median.
- Every ECB source entry in the manifest is byte-identical to `origin/main`'s.

## Next

- [x] all nine fixes
- [ ] push and open the PR (do not merge)
