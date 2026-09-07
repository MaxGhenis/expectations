# Growth expectations in the AI era

How have professional GDP forecast levels, uncertainty and high-growth probabilities changed as AI has advanced?

This revision centers the US and ECB Surveys of Professional Forecasters' growth outlooks. It compares Q1 surveys at fixed calendar horizons, preserves the COVID episode, and calculates upper-tail probability bounds from literal survey bins. It retains the broader all-variable tracker and calibration pipeline.

The paper finds limited movement toward rapid growth, with a qualification: the ECB's small high-growth tail increased. This is a descriptive result about overall growth beliefs. It does not establish AI's causal contribution or a matched unconditional disagreement with every AI scenario. See [revision findings and corrections](RESEARCH_REVISION.md).

## Read and explore

- Manuscript source: [paper/index.qmd](paper/index.qmd)
- Rendered manuscript: [HTML](site/paper/web/index.html) and [PDF](site/paper/web/index.pdf)
- Research companion: `site/growth/` — baseline, survey-round and threshold comparisons
- Full tracker: `site/index.html` — decomposition, fan, calibration, term structure and scores
- Existing public release: [tracker](https://forecast-uncertainty.vercel.app) and [paper](https://forecast-uncertainty.vercel.app/paper/). The local revision is not automatically deployed.

## Reproduce

Python 3.13+ and `uv` are required. Rendering the manuscript also requires Quarto with Typst support. The lockfile pins the Python environment; Matplotlib and Jupyter are development dependencies for research artifacts.

```bash
uv sync --dev
unzip -q -o data/raw/ecb_spf_individual_forecasts.zip -d data/raw/ecb_spf
uv run python -m forecast_uncertainty.build
uv run python scripts/build_research.py
uv run python site/gen_data.py
bash scripts/build_paper.sh
uv run pytest -q
uv run ruff check src tests scripts site/gen_data.py
uv run ruff format --check src tests scripts site/gen_data.py
uv run python -m http.server 8769 --directory site
```

Open `http://localhost:8769/growth/`. The paper build installs its Jupyter kernel inside this checkout's `.venv`, avoiding dependence on a global kernel or another checkout. The PDF and HTML embed the computed tables and charts.

## Outputs and methods

- `measures.csv`: empirical pooled moments, quantiles and disagreement. Moments, quantiles and CRPS consistently use uniform finite bins and adjacent-width closure of open tails.
- `growth_tails.csv`: real GDP probabilities above 3%, 4%, 5% and 10%, with literal-bin lower/upper bounds. These bounds never close an open tail. Boundary points have zero mass under a continuous-outcome convention. Bounds are not statistical confidence intervals.
- `growth_comparison.csv`: fixed-Q1 and equal-year-weight all-round comparisons across documented windows.
- `benchmark_summary.csv`: ratio of mean CRPS on matched eligible observations, with mean row-level skill retained as a sensitivity.
- `calibration.csv`, `scores.csv`, `coverage.csv`, `longrun_points.csv`, `recess.csv`: full-survey supporting data.

Each retained respondent receives equal weight within a round. Nonfinite and out-of-range probabilities are rejected, partial missing cells count as zero, and totals must be strictly within two points of 100 before normalization. The mixture decomposition uses population variance across respondent means (`ddof=0`) and includes within-bin variance. Its moments remain conditional on the tail reconstruction; small open-tail probability does not cap the possible magnitude of growth in that tail.

The full archive covers US density variables PRGDP, PRPGDP, PRUNEMP, PRCCPI and PRCPCE, plus recession probabilities and long-run point forecasts; ECB densities cover GDP, HICP, core HICP and unemployment. Historical US output concepts remain labeled separately. Only real GDP enters the current research comparisons.

## Source snapshots

Raw survey files and original outcome snapshots are committed. Rebuilding is offline once dependencies are installed. This revision adds official annual ECB outcome inputs with a reproducible acquisition script:

```bash
uv run python scripts/download_ecb_annual_realizations.py
```

That command refreshes annual companion inputs and their [provenance manifest](data/raw/ecb_annual_realizations_sources.json); it is not needed for reproducing the committed snapshot. Annual GDP uses growth in complete quarterly-level sums. Annual HICP/HICPX use official annual-average index-growth observations at publisher precision. Archived rolling outcomes remain unchanged. These are revised-data snapshots, not a real-time forecast evaluation.

Primary sources: [Philadelphia Fed SPF](https://www.philadelphiafed.org/surveys-and-data/real-time-data-research/survey-of-professional-forecasters), [ECB SPF](https://www.ecb.europa.eu/stats/ecb_surveys/survey_of_professional_forecasters/html/index.en.html), BEA/BLS via archived DBnomics files, and the ECB Data Portal. AI-comparator source details are in [paper/AI_COMPARATORS.md](paper/AI_COMPARATORS.md).

Older planning documents and reports are retained with supersession notices. Their numerical claims should not be substituted for the regenerated outputs.
