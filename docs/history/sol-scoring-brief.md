# Build brief 3: proper scores — CRPS, pinball, PIT, benchmarks

You are extending this repo (read `SOL_REPORT.md` and `INTERACTIVE_REPORT.md`
first — they document the pipeline and interactive you are building on). NO
network; all data local. Do not touch `paper/`, `LITREVIEW.md`, the two
existing reports, or raw inputs. Commit nothing. Write your report to
`SCORES_REPORT.md` (the -o target is a throwaway the harness clobbers).

## Part A — scoring machinery (`measures.py` / new `scores.py`)

The pooled mixture CDF is piecewise linear: uniform mass within each literal
closed bin, zero-mass gaps (ECB), open tails closed at one adjacent-bin
width — exactly the construction behind the emitted quantiles. Implement:

1. **CRPS, exact closed form** for a piecewise-linear CDF F and realization y:
   integrate (F(x) − 1{x ≥ y})² segment by segment analytically. Validate in
   tests against (a) brute-force numerical integration on random histograms
   (atol 1e-8), (b) the known identity CRPS = E|X−y| − ½E|X−X′| computed by
   Monte Carlo on a few cases (loose tol), (c) CRPS = |x₀ − y| for a point
   mass, (d) the closed form for Uniform(a,b). CRPS ≥ 0 always.
2. **Pinball (quantile) loss** at τ ∈ {0.05, 0.10, 0.25, 0.50, 0.75, 0.90,
   0.95} using quantiles from the same CDF: ρ_τ(y, q) = (1{y ≤ q} − τ)(q − y).
   Test the identity that 2·∫₀¹ pinball dτ = CRPS via a fine τ-grid
   approximation on random histograms.
3. **PIT** = F(y) for every calibrated row (uniform under ideal calibration).
4. **Individual CRPS**: mean CRPS across each round's individual forecaster
   histograms (same closed form per forecaster), so pooled-vs-average-
   individual skill is comparable. Same response filters as measures.

## Part B — benchmarks (no lookahead, ever)

Per (survey, variable, horizon_class), scored on exactly the rows that have a
verified realization (the calibration.csv universe):

1. **Climatology**: the empirical distribution of realized values available
   strictly before the forecast round (expanding window; realization
   publication lags may be approximated by using target periods completed
   before the round's year-quarter — state the convention). Empirical-sample
   CRPS closed form: CRPS = mean|xᵢ − y| − (1/2n²)ΣΣ|xᵢ − xⱼ|. Require a
   minimum window of 10 observations; earlier rows get no benchmark score
   (flag, don't fudge). Use the longest local realization history available
   (the US annual series reach far back; ECB series are short — report
   honestly how short).
2. **Gaussian-around-consensus**: N(consensus mean of that round, σ), σ =
   RMSE of that survey-variable-horizon's consensus errors over the same
   expanding window (min 10). Gaussian CRPS closed form (Gneiting-Raftery).
3. Skill scores: 1 − CRPS_survey / CRPS_benchmark per row; report
   period-averaged versions (full sample, pre/post 2020).

## Part C — outputs, report, interactive

1. New `outputs/scores.csv`: keys as calibration.csv plus crps_pooled,
   crps_individual_mean, pinball_05…pinball_95, pit, crps_climatology,
   crps_gaussian, skill_vs_climatology, skill_vs_gaussian (nullable where
   benchmark window is short).
2. `SCORES_REPORT.md`: per survey-variable-horizon tables of mean CRPS and
   both skill scores (full sample and pre/post-2020); pooled vs
   average-individual CRPS (does the disagreement variance earn its keep?);
   which tails carry the losses in the known miss clusters (pinball at
   05/95 around 1996–2001, 2008–09, 2020–22); PIT summary (deciles) per
   variable; every judgment call traced (window conventions, lag handling);
   honest gaps.
3. Interactive: add a **Scores** view — CRPS over time for the selected
   survey/variable/horizon with the two benchmark series (3 lines max,
   existing palette slots in order, same axes/tooltip/table/legend patterns
   as the other views; extend gen_data.py with a compact scores dataset;
   keep data.js under the 1.2 MB budget — thin fields or round harder if
   needed and say so). Wire it into the URL-hash state. Keep the token
   block byte-identical.
4. `uv run --no-sync pytest -q` green (new tests included),
   `ruff format`/`check` clean, `gen_data.py` assertions extended to the
   scores dataset. Leave the tree uncommitted.
