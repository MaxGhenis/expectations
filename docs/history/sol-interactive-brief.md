# Build brief 2: full-matrix interactive + two pipeline cleanups

You are continuing work on this repo (read `SOL_REPORT.md` — the report of the
pipeline build you are extending, and `interactive/PLAN.md`). NO network
access; everything is local. Do not touch `paper/`, `LITREVIEW.md`,
`SOL_REPORT.md`, or `data/raw/download.sh` inputs other than as instructed.
Commit nothing. Write your report to `INTERACTIVE_REPORT.md` (NOT the -o
target file — that gets clobbered by the harness).

## Part A — pipeline cleanups (then rerun build + tests)

1. **HICPX calibration.** A new local realization file exists:
   `data/raw/ecb_ea_hicpx_yoy_monthly.csv` (ECB Data Portal csvdata,
   ICP.M.U2.N.XEF000.4.ANR; its TITLE column self-describes as "HICP -
   All-items excluding energy and food", matching the dataset description's
   HICPX definition at `data/docs/ecb_spf_dataset_description.txt:45,407`).
   Wire it into `realizations.py` and calibration exactly parallel to HICP
   (same rolling/calendar target matching, same E-status flagging and
   actual-only sensitivity accounting). Update coverage/tests.
2. **Drop UNEMP10.** `individual_unemp10.xlsx` is an HTML error page; verify
   against the documentation's list of 10-year variables, then remove
   UNEMP10 handling from the pipeline, delete the bogus file, drop its
   line from `data/raw/download.sh`, and update `coverage.csv` and tests so
   nothing references it. README mention too if any.

Rerun `uv run --no-sync python -m forecast_uncertainty.build` and
`uv run --no-sync pytest -q`; all green before Part B ships.

## Part B — wire the interactive to the full matrix

Base: `interactive/index.html` + `interactive/gen_data.py` (working 3-view
mockup on seed data — keep its design language, palette, and interaction
patterns exactly; it was built against a design-system spec).

1. **`gen_data.py` switches to `outputs/`** (`measures.csv`,
   `calibration.csv`, `longrun_points.csv`) and emits `data.js` with the
   full matrix. Budget: keep `data.js` under ~1.2 MB — include only fields
   the views use (year, quarter, horizon_class, horizon_years, n, mean,
   median, within_sd, disagreement, total_sd, share_between, iqr, q25, q75;
   calibration: consensus, realized, total_sd, q05, q95, inside flags).
   Round to 3-4 significant decimals. Keep a `meta` block naming sources
   and generation provenance (outputs/ + build date read from file mtime is
   fine).
2. **Live controls.** Survey (US SPF, ECB SPF), variable (per survey, human
   labels: Real GDP growth, GDP price inflation, Unemployment rate, Core
   CPI, Core PCE, HICP, Core HICP), horizon (per survey/variable:
   US current/next/+2/+3 year, ECB current/next/year-after-next/rolling
   1y/rolling 2y/longer term), and for the decomposition view a measure
   toggle: SD decomposition (total/within/disagreement) vs pooled IQR.
   Remove the disabled placeholder options. A rounds toggle: Q1 only vs
   all quarterly rounds (all-rounds shows the fixed-event sawtooth; note
   line explains it).
3. **Views.**
   - Decomposition (as now, driven by selection).
   - Consensus fan (as now for US GDP incl. the 10-year point series from
     longrun_points; for other selections show median + pooled q25-q75 from
     measures).
   - Calibration (as now, driven by selection — all variables with
     calibration rows; keep the miss rings + year labels; note line states
     the coverage % computed from the shown series).
   - NEW: Term structure — for the selected survey+variable, mean stated
     uncertainty (within_sd and total_sd) by horizon class, Q1/balanced
     samples like SOL_REPORT.md's tables; a small-multiples or grouped-line
     treatment, one axis, same palette slots.
4. **Design constraints (hard):** keep the CSS token block and palette
   slots 1-3 exactly (they are validated light+dark); text always in ink
   tokens, never series colors; one y-axis per chart; legend present for
   >=2 series plus selective direct labels; crosshair tooltips; a data
   table per view; light/dark both work. No new dependencies, no chart
   libraries, no network calls. Page must still work served statically.
5. **Sanity checks in `gen_data.py`:** assert non-empty series per emitted
   (survey, variable, horizon) combo; assert data.js size budget; print a
   manifest summary (combos × rows).

## Report — `INTERACTIVE_REPORT.md`

Coverage of the emitted matrix (combos, rows, data.js bytes), the HICPX
calibration coverage numbers (both flags, actual-only variant), what
UNEMP10 removal touched, test counts, and any judgment calls (each traced
to a doc line or SOL_REPORT.md section). Honest gaps list. Sentence-case
headings. Leave the working tree uncommitted.
