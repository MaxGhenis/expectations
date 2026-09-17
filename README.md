# expectations

**Live tracker: https://maxghenis.com/expectations/ · working paper:
https://maxghenis.com/expectations/paper/**

What do professional forecasters say they don't know? This repo computes
elicited (stated) macroeconomic forecast uncertainty from the probability
distributions that forecasters themselves report, across every variable,
horizon, and round of the two surveys that collect them:

- **US SPF** (Philadelphia Fed, quarterly): density forecasts for real
  output growth (PRGDP), GDP price inflation (PRPGDP), unemployment
  (PRUNEMP), core CPI (PRCCPI), core PCE (PRCPCE), and recession
  probability (RECESS), plus 10-year point forecasts (RGDP10, CPI10,
  PCE10).
- **ECB SPF** (quarterly since 1999Q1): density forecasts for euro-area
  HICP and core HICP inflation, real GDP growth, and unemployment at
  one-year, two-year, and longer-term horizons.

For each (survey, variable, round, target) it decomposes pooled
uncertainty by the law of total variance:

```
total variance = mean within-forecaster variance + between-forecaster variance
                 (individual uncertainty)          (disagreement)
```

and evaluates calibration and proper scores against realized outcomes, including
strictly expanding-window climatology and Gaussian benchmarks.

## Layout

- `data/raw/` — downloaded source files (see `data/raw/download.sh`)
- `data/docs/` — survey documentation (bin schemes) as PDF + extracted text
- `src/forecast_uncertainty/` — parsing, measures, scores, benchmarks,
  realizations, and build
- `outputs/` — tidy CSVs consumed by the paper and the interactive, including
  `scores.csv`
- `tests/` — pytest suite, incl. golden-value tests against the seed
  pipeline (`tests/fixtures/seed/`)

## Usage

```bash
uv sync
uv run python -m forecast_uncertainty.build   # writes outputs/*.csv
uv run pytest
```

## Data sources

- Philadelphia Fed SPF individual files:
  https://www.philadelphiafed.org/surveys-and-data/real-time-data-research/survey-of-professional-forecasters
- ECB SPF microdata (rounds 1999Q1–present):
  https://www.ecb.europa.eu/stats/ecb_surveys/survey_of_professional_forecasters/html/index.en.html
- Realizations: BEA/BLS via DBnomics; euro area via the ECB Data Portal
  API. Latest vintage (see limitations in the paper draft).
