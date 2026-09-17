# Research revision: growth expectations in the AI era

Revised 5 September 2026 on branch `ai-growth-divergence-closure-20260907`, from `origin/main` at `ade2384f269d72456ec65fc4d0e4172b14c650d9`. The original checkout is preserved. This revision has not been published to the live site.

## Main finding

The joint behavior of levels, predictive spreads and upper tails provides the strongest result. Professional forecasts show limited movement toward rapid growth within the survey horizons. The result is more precise than saying point forecasts and uncertainty have been unchanged for twenty years: central forecasts have declined, some reconstructed uncertainty measures are modestly higher, and the ECB's small high-growth tail has increased.

The primary comparison uses Q1 rounds, holding the calendar horizon fixed. Period averages compare 2015–19 with 2025–26; the recent period contains just two rounds. The figures retain the COVID episode. Alternative baselines and equal-year-weight all-round results are available in the research companion.

| Forecast | Mean growth, earlier → recent | Pooled SD, earlier → recent | Probability above 4%, earlier → recent |
|---|---:|---:|---:|
| US next year | 2.14% → 1.84% | 1.27 → 1.43 pp | 5.62% → 4.22% |
| US year +3 | 1.97% → 1.86% | 1.41 → 1.47 pp | 5.97% → 4.85% |
| Euro area year +4 | 1.59% → 1.30% | 0.83 → 0.89 pp | 0.43% → 1.06% |

The 4% threshold is identified at common literal bin edges in these comparisons. More extreme thresholds require bounds, particularly in the ECB's open upper bin. Small open-tail probability does not bound the magnitude of growth conditional on reaching the tail, so unrestricted moments remain unidentified without a tail assumption.

The AI literature comparison is narrower than the initial hypothesis. The primary elicited-distribution source checked here does not establish a large unconditional near-term extreme-tail disagreement. Its conditional and distant-horizon results cannot be substituted for that comparison. See [the source audit](paper/AI_COMPARATORS.md). The manuscript presents a measurable professional baseline and identifies the matched elicitation needed to establish a direct disagreement.

## Corrections and additions

- Retained the existing parsers and all-variable tracker; rewrote the manuscript and added a GDP research companion.
- Made moments consistent with the distribution used for quantiles and scoring, including uniform within-bin variance. Used population variance across respondent means for the empirical-mixture identity.
- Rejected negative, nonfinite and above-100 probability entries before normalization. Two negative ECB responses in 2023Q1 are excluded.
- Replaced mean quarterly year-over-year GDP growth with the ECB's published annual real GDP growth rate. Annual inflation uses official annual-average index-growth observations at publisher precision. Added raw inputs, a reproducible download script and source hashes.
- Added literal-bin exceedance bounds above 3%, 4%, 5% and 10%. Historical nominal and real GNP observations remain in the tracker but are excluded from GDP tail outputs.
- Replaced headline mean row-level CRPS skill with one minus the ratio of mean losses on matched eligible observations. Retained row-level skill as a sensitivity. Neither evaluation reconstructs historical release vintages.
- Separated predictive uncertainty from disagreement among long-run point estimates. Preserved COVID observations and documented bin changes, changing panels and short recent samples.
- Generated every manuscript table from the rebuilt outputs and added three reproducible figures, an HTML manuscript, PDF and interactive comparison controls.

## Verification

The completed revision passes 139 tests, Ruff lint and formatting, and `git diff --check`. Tests independently integrate mixture moments, exercise open-tail identification, verify annual source aggregation, distinguish benchmark aggregation methods, and check that manuscript equations render inside the script-restricted embed.

The full pipeline, research figures, tracker data and Quarto HTML/PDF were rebuilt from the recorded raw snapshots. The PDF was rendered to page images and inspected; browser checks cover comparison controls, URL state, the paper links and responsive layout. Reproduction commands are in the [README](README.md).

## Artifacts

- [Manuscript source](paper/index.qmd), [rendered HTML](site/paper/web/index.html), [PDF](site/paper/web/index.pdf)
- Research companion: `site/growth/index.html`
- [Literal-bin GDP tail probabilities](outputs/growth_tails.csv)
- [Period comparisons](outputs/growth_comparison.csv)
- [Benchmark score summary](outputs/benchmark_summary.csv)
- [Annual ECB outcome provenance](data/raw/ecb_annual_realizations_sources.json)

Earlier planning and review documents remain as historical records. Their supersession notices identify numerical and framing claims that should no longer be used.
