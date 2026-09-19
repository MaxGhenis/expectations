# expectations

What professional forecasters expect, and how sure they say they are. This repository computes every probability distribution reported in the US and ECB Surveys of Professional Forecasters since 1968, and serves them as a live tracker and two working papers.

**Live: https://maxghenis.com/expectations/**

- **Tracker** — [maxghenis.com/expectations](https://maxghenis.com/expectations/): decomposition, consensus fan, calibration, term structure and proper scores for every variable and horizon in both surveys. Every view is a shareable URL.
- **What do forecasters say they don't know?** — [paper](https://maxghenis.com/expectations/paper/) (source: [paper/index.qmd](paper/index.qmd)). Every elicited density in both surveys, pooled by the law of total variance into stated individual uncertainty and disagreement, calibrated against outcomes and scored against expanding-window benchmarks built from target periods already complete at each round.
- **Growth expectations in the AI era** — [paper](https://maxghenis.com/expectations/growth/paper/) (source: [paper/growth/index.qmd](paper/growth/index.qmd)) and [companion](https://maxghenis.com/expectations/growth/). Whether professional GDP forecasts moved toward faster growth, in levels, spreads and upper-tail probabilities bounded from the literal survey bins.

Every number in both manuscripts computes from `outputs/` when the paper renders.

## Reproduce

Python 3.13+ and `uv` are required. Rendering the manuscripts also requires Quarto with Typst support. The lockfile pins the Python environment; Matplotlib and Jupyter are development dependencies for the research artifacts.

```bash
uv sync --dev
unzip -q -o data/raw/ecb_spf_individual_forecasts.zip -d data/raw/ecb_spf
uv run python -m expectations.build
uv run python scripts/build_research.py
uv run python scripts/build_panorama.py
uv run python site/gen_data.py
bash scripts/build_paper.sh
uv run pytest -q
uv run ruff check src tests scripts site/gen_data.py
uv run ruff format --check src tests scripts site/gen_data.py
uv run python -m http.server 8769 --directory site
```

Open `http://localhost:8769/`. The paper build installs its Jupyter kernel inside this checkout's `.venv`, so it depends on no global kernel or other checkout. After a manuscript revision, bump the `?v=` parameter in that paper's wrapper (`site/paper/index.html` or `site/growth/paper/index.html`); `tests/test_paper_embed.py` locks the links together.

## Outputs and methods

- `measures.csv`: pooled moments, quantiles and disagreement for every survey, variable, round and target. Moments, quantiles and CRPS all use one distribution: each printed bin label read as contiguous support ("2.0 to 2.9" covers [2, 3), so lower labels such as 4.0 stay bin edges), uniform within each bin, open tails closed at one adjacent-bin width.
- `reconstruction_sensitivity.csv`: the headline statistics under that reading and two alternatives — the printed labels taken literally, with empty 0.1-point strips between bins, and boundaries halfway across each strip — written by `scripts/build_reconstruction_sensitivity.py`. Means move by 0.05 points between readings and the window comparisons do not move; the ±1σ coverage count is 22 of 33 under the primary reading and 23 of 33 under the other two.
- `calibration.csv`, `scores.csv`, `benchmark_summary.csv`: outcomes, coverage flags, CRPS, pinball losses, PITs, and skill against expanding-window climatology and a Gaussian around the consensus. Both benchmark windows admit only target periods that completed strictly before the forecast round, and both read the same revised (latest-vintage) outcomes the forecasts are scored against; the pipeline holds no real-time data vintages, so this is not a real-time backtest. Skill is one minus the ratio of mean CRPS on matched eligible observations; mean row-level skill stays as a sensitivity.
- `panorama_*.csv`: the summary tables behind the full paper, `paper/index.qmd` (stability, disagreement shares, term structure, fixed-event shrinkage, coverage and miss clusters, the ECB longer-term shift, skill, tails, PITs, bin-era comparisons), written by `scripts/build_panorama.py`.
- `growth_tails.csv`, `growth_comparison.csv`: real GDP probabilities above 3%, 4%, 5% and 10% with lower and upper bounds set by the bin edges, and fixed-Q1 and all-round period comparisons. The bounds never close an open tail, and they are identification bounds, not confidence intervals.
- `coverage.csv`, `longrun_points.csv`, `recess.csv`: parsing coverage, ten-year point forecasts and recession probabilities.

Each retained respondent receives equal weight within a round. Nonfinite and out-of-range probabilities are rejected, partial missing cells count as zero, and totals must lie strictly within two points of 100 before normalization. The mixture decomposition uses population variance across respondent means and includes within-bin variance, so within plus between equals the pooled mixture's variance exactly. Moments remain conditional on the tail reconstruction: small open-tail probability does not cap how large growth in that tail can be.

The archive covers US density variables PRGDP, PRPGDP, PRUNEMP, PRCCPI and PRCPCE, plus recession probabilities and ten-year point forecasts; ECB densities cover GDP, HICP, core HICP and unemployment. Historical US output concepts stay labeled separately.

## Source snapshots

Raw survey files and outcome snapshots are committed, so rebuilding runs offline once dependencies are installed. Official annual ECB outcomes come with a reproducible acquisition script, which has two distinct invocations:

```bash
# Verify the committed inputs and rewrite the manifest. Any file whose bytes
# already match its recorded checksum is reused, not re-downloaded.
uv run python scripts/download_ecb_annual_realizations.py

# Re-download every source, replacing the committed inputs with today's vintage.
uv run python scripts/download_ecb_annual_realizations.py --refresh
```

Neither command is needed to reproduce the committed snapshot. Without `--refresh` the script only fetches a source that is missing or fails its checksum, so it re-verifies the [provenance manifest](data/raw/ecb_annual_realizations_sources.json) without re-vintaging anything; it does rewrite the manifest, whose top-level `retrieved_at_utc` records the run itself while each source entry keeps its own retrieval time. `--refresh` replaces every source and is how the inputs are deliberately re-vintaged. Annual GDP uses the ECB's published annual real GDP growth rate. Annual HICP and core HICP use the official annual-average index-growth series at publisher precision. Archived rolling outcomes are unchanged. Eurostat's published EA20 annual growth is archived alongside as a comparator only — never an emitted outcome — so the manifest's record that the two official series differ in 5 of 30 years at one decimal reproduces offline. All outcomes are revised-data snapshots, so the evaluation is not a real-time backtest.

Primary sources: [Philadelphia Fed SPF](https://www.philadelphiafed.org/surveys-and-data/real-time-data-research/survey-of-professional-forecasters), [ECB SPF](https://www.ecb.europa.eu/stats/ecb_surveys/survey_of_professional_forecasters/html/index.en.html), BEA/BLS via archived DBnomics files, and the ECB Data Portal. AI-comparator source details are in [paper/AI_COMPARATORS.md](paper/AI_COMPARATORS.md); the verified literature review is in [docs/LITREVIEW.md](docs/LITREVIEW.md).

Earlier planning documents and build reports live in [docs/history](docs/history/) with supersession notices. Use the regenerated outputs, not their numbers.
