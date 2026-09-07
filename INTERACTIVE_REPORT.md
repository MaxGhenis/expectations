> Historical development document. Superseded for current findings and methods by the September 2026 growth-beliefs revision: see `RESEARCH_REVISION.md`, `paper/index.qmd`, and regenerated `outputs/`. Numbers below may use the former midpoint/sample-variance convention and approximate annual outcomes.

# Full-matrix interactive and pipeline cleanup report

## Result

Build brief 2 is complete. The pipeline now calibrates ECB core HICP (HICPX)
against the supplied local realization series, UNEMP10 has been removed from all
active pipeline surfaces, and the static interactive is driven by the complete
survey-variable-horizon matrix in `outputs/`.

The page retains the original CSS token block and palette slots byte-for-byte. It
has live dependent controls, Q1/all-round behavior, SD/IQR selection, four SVG
views, crosshair tooltips, legends where multiple series appear, and a data table
for every view. It adds no dependency or network call.

No commit was created for this brief. All deliverable changes remain in the
working tree.

## Emitted matrix

`interactive/gen_data.py` reads `outputs/measures.csv`,
`outputs/calibration.csv`, and `outputs/longrun_points.csv`. Rows use compact
positional arrays with one field manifest, and numeric values are rounded to four
significant digits.

| Dataset | Emitted combinations | Emitted rows | Notes |
|---|---:|---:|---|
| Measures | 38 survey-variable-horizon combinations | 3,687 | All selectable horizons for nine survey-variable pairs |
| Calibration | 38 survey-variable-horizon combinations | 3,070 | Every selectable combination has at least one matched realization |
| Long-run points | 3 survey-variable combinations | 254 | RGDP10, CPI10, and PCE10 |
| Total | — | 7,011 | Compact rows across the three sources |

`interactive/data.js` is **621,259 bytes**, 51.8% of the enforced 1,200,000-byte
budget. Its metadata names all three `outputs/` sources, their modification times,
the generator, build date `2026-08-26`, rounding rule, row counts, and exclusions.
The generator prints the same manifest and asserts the exact expected 38-combo
matrix for measures, calibration, and controls, non-empty series for every combo,
valid schemas, no null/non-finite view values, unique keys, and the size limit.

The source measures file has 3,695 rows. Eight PRGDP/PRPGDP rows from 1985Q1 and
1986Q1 have no documented target year or horizon and are deliberately excluded
from the selectable bundle; this exclusion is recorded in metadata.

## HICPX calibration

`data/raw/ecb_ea_hicpx_yoy_monthly.csv` is now loaded through the same monthly
rolling-target and complete-calendar-year paths as headline HICP. The raw ECB
observation status is retained on both rolling and annual rows.

| Sensitivity | Rows | Inside ±1 total SD | Inside pooled q05–q95 |
|---|---:|---:|---:|
| All statuses | 176 | 106 / 176 (60.2%) | 128 / 176 (72.7%) |
| Exclude every status containing `E` | 156 | 90 / 156 (57.7%) | 108 / 156 (69.2%) |

The 176 calibration rows comprise 152 `A`, four `A+B`, 16 `A+E`, and four `E`
statuses. “Actual-only” above follows the existing HICP sensitivity convention:
exclude every row whose status contains `E`. The four `A+B` rows are retained
because `B` is not an estimate flag. For a narrower literal `OBS_STATUS == "A"`
check, the figures would be 86/152 (56.6%) and 104/152 (68.4%).

The implementation is grounded in the HICPX definition at
`data/docs/ecb_spf_dataset_description.txt:43–45,407`, its point/density start at
`:470–472`, and the calendar/rolling matching rules summarized in
`SOL_REPORT.md:246–250`. The realization file supplies 348 monthly observations
plus 29 complete annual averages. It ends in 2025, so forecasts requiring a 2026
HICPX realization remain uncalibrated.

## UNEMP10 removal

The supposed `data/raw/individual_unemp10.xlsx` was verified as an 18,401-byte
HTML 404 response, not an XLSX workbook. The official macro long-run list names
RGDP10, PROD10, CPI10, and PCE10 but no unemployment analogue
(`data/docs/spf-documentation.txt:1268–1271`); the detailed 10-year dictionary is
at `:511–569`.

Removal touched:

- `src/forecast_uncertainty/us_spf.py`: removed UNEMP10 from
  `LONGRUN_VARIABLES`.
- `src/forecast_uncertainty/build.py`: removed the synthetic zero-coverage row.
- `data/raw/download.sh`: removed the invalid download target.
- `README.md`: removed UNEMP10 from the inventory and added core HICP to the ECB
  description.
- `data/raw/individual_unemp10.xlsx`: deleted the invalid HTML file; it remains
  recoverable from Git history.
- `outputs/coverage.csv`: regenerated with 13 real source rows instead of 14.
- `tests/test_regressions.py`: asserts the documented long-run configuration and
  the HICPX calibration coverage numerators.

No active code, test, downloader, README inventory, or generated output references
UNEMP10. Historical mentions remain only in files the brief explicitly prohibited
editing, task artifacts, and this report.

## Interactive behavior

The dependent controls expose:

- US SPF: real GDP growth, GDP price inflation, unemployment, core CPI, and core
  PCE; current/next year and +2/+3 years where the source variable supplies them.
- ECB SPF: real GDP growth, unemployment, HICP, and core HICP; current year, next
  year, year after next, rolling one year, rolling two years, and longer term.
- Q1-only or all quarterly forecast rounds. The all-round note explains the
  fixed-calendar-event sawtooth.
- SD decomposition or pooled IQR in the decomposition view.

The four views are:

- **Decomposition:** total SD, average within-forecaster SD, and disagreement, or
  pooled IQR under the alternate measure toggle. Early duplicate ECB longer-term
  targets are averaged within forecast round.
- **Consensus fan:** selected median with its true pooled q25–q75 band. US real
  GDP also shows the RGDP10 median; its reported IQR appears in the tooltip and
  table, without inventing quartile endpoints absent from `longrun_points.csv`.
- **Calibration:** consensus ± total SD and realized outcomes, emitted miss flags,
  miss rings/year labels, both emitted coverage flags, and percentages computed
  from exactly the currently shown rows. The x-axis is explicitly labeled in the
  note as forecast round rather than target period.
- **Term structure:** mean total and within SD by available horizon on balanced
  samples. US variables use Q1 rounds; ECB uses rolling one year, rolling two
  years, and longer term, averaging duplicate longer-term targets within round
  before balancing.

The term calculations reproduce `SOL_REPORT.md:108–145` to three decimals:
17 balanced Q1 rounds for PRGDP and PRUNEMP, 35 for PRPGDP, 20 each for PRCCPI
and PRCPCE; and 105 balanced quarterly rounds for HICP, RGDP, and unemployment
and 39 for HICPX.

Every view has one y-axis, a crosshair tooltip, a data table, and selective direct
labels. Every view with two or more series has a legend. All chart and annotation
text uses ink/muted tokens; series colors are confined to marks and swatches. The
original light/system-dark/explicit-dark token declarations, including palette
slots 1–3, are byte-identical to the base file.

## Judgment calls

| Decision | Basis |
|---|---|
| Treat HICPX as core HICP excluding food and energy | ECB description `:43–45,407`; the local CSV `TITLE` is “HICP - All-items excluding energy and food.” |
| Define the actual-only sensitivity by exclusion of statuses containing `E`, retaining `A+B` | This is exactly the headline-HICP convention recorded in the `SOL_REPORT.md` Calibration section (`:183–186`). |
| Omit the eight null-horizon 1985Q1/1986Q1 US rows from interactive controls | The provider cannot confirm those targets (`spf-documentation.txt:1614–1618`), matching the `SOL_REPORT.md` “Early US targets” decision (`:243`). |
| Use Q1/balanced US samples and balanced ECB rolling 1y/2y/longer-term samples; average duplicate longer-term targets within round | `SOL_REPORT.md` “Term structure and fixed-event shrinkage” (`:108–145`). |
| Explain the all-quarter sawtooth as information arriving for fixed calendar events | The within-year shrinkage evidence is in `SOL_REPORT.md:125–134`. |
| Overlay only RGDP10 on US real GDP and do not synthesize a long-run quartile band | RGDP10 is the documented real-GDP 10-year variable (`spf-documentation.txt:533–539`); CPI10/PCE10 are headline inflation (`:511–530`), while the interactive variables are core. The generated long-run schema provides median and IQR width, not q25/q75 endpoints. |

## Validation

The required final pipeline sequence passed after all cleanups:

```text
UV_CACHE_DIR=/private/tmp/forecast-uncertainty-uv-cache \
  uv run --no-sync python -m forecast_uncertainty.build

UV_CACHE_DIR=/private/tmp/forecast-uncertainty-uv-cache \
  uv run --no-sync pytest -q
46 passed, 2 warnings
```

The warnings are openpyxl failures to parse decorative workbook header/footer
content; worksheet data are not skipped. The build itself emits the same benign
warning while opening the nine valid US workbooks.

Additional checks:

```text
interactive/gen_data.py
  measures 38 combos × 3,687 rows
  calibration 38 combos × 3,070 rows
  longrun 3 combos × 254 rows
  data.js 621,259 bytes

ruff format --check src tests interactive/gen_data.py
  11 files already formatted
ruff check src tests interactive/gen_data.py
  All checks passed!
```

Independent audits found zero identity, rounded-value, or Boolean-flag mismatches
between `data.js` and the three output CSVs. Generated outputs have no duplicate
round-target keys, quantiles remain ordered, variance shares remain in `[0,1]`,
and the largest total-variance identity residual is `3.55e-15`.

Inline JavaScript parses successfully. A mock DOM exercised 313 distinct
control/view/measure states across all 38 horizon combinations, with non-empty
charts and tables and required multi-series legends. Static checks also confirmed
the byte-identical token block, absence of placeholder options, and absence of
network URLs or calls.

## Honest gaps

- The HICPX realization file ends in 2025, so no 2026 HICPX target is calibrated.
- All realizations remain latest-vintage rather than real-time vintage, and
  multiple forecasts of one outcome are not independent, as already cautioned in
  the `SOL_REPORT.md` Calibration and gaps sections.
- `longrun_points.csv` reports an IQR width but not its q25/q75 endpoints. The
  interactive therefore draws the RGDP10 median only and reports its IQR
  numerically rather than fabricating a band.
- Real-browser screenshot validation could not run in this managed environment:
  both installed Chromium binaries abort on the macOS Mach-port sandbox, and no
  WebKit or Firefox browser binary is installed. JavaScript syntax, full-matrix
  rendering logic, theme-token integrity, and 313 states were validated without a
  browser.
- `SOL_REPORT.md` remains an intentionally untouched historical handoff and still
  describes the pre-cleanup HICPX/UNEMP10 gaps. This report supersedes those two
  statements; the brief explicitly prohibited editing `SOL_REPORT.md`.
- The unrelated `lane2-note.err.log` working-tree modification was left untouched.

## Working tree

No files under `paper/`, `LITREVIEW.md`, `SOL_REPORT.md`, or any valid raw input
were changed. No commit command was issued. The implementation, regenerated
outputs, `PROGRESS.md`, and this report remain uncommitted as requested.
