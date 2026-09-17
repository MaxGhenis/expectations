# SPF research revision closure — 7 September 2026

## State

The completed revision is committed in the isolated `/Users/maxghenis/forecast-uncertainty-spf-closure-20260907` worktree on `ai-growth-divergence-closure-20260907`. Local validation, live-base verification and a normal Quarto re-render are complete; the branch is prepared for its authorized remote draft PR. Nothing was published, submitted or merged. The source checkout remains at its original HEAD and dirty state.

## Done

- Read global instructions and `RESEARCH_REVISION.md`; no project AGENTS/CLAUDE files were present. Inspected Git state, remotes, worktrees and cached base before edits.
- Archived binary working/index diffs and all 57 changed/untracked files with SHA-256 hashes in `/Users/maxghenis/capacity-sprint-20260907/spf-closure/snapshot/`; verified the restored continuation byte for byte.
- Committed the progress checkpoint and complete research revision separately. Source HEAD and cached `origin/main` were `ade2384f269d72456ec65fc4d0e4172b14c650d9`; live fetch failed. An initial progress-only commit mistakenly made in the source worktree was reversed immediately; HEAD, status, both diffs and all source hashes were verified identical to the snapshot.
- Ran the existing suite once: 130 tests passed (three spreadsheet header/footer warnings), Ruff lint and formatting passed.
- Reproduced all nine output CSVs, companion JSON and three PNG figures exactly from the local snapshots. Tracker content matches except build/file-time metadata. Verified all five new ECB source hashes.
- Corrected actual packaging issues: recognize publisher CRLF without changing bytes; emit deterministic SVG identifiers, omit creation dates and strip generated trailing whitespace. Repeated figure builds match byte for byte; normalized SVG structure and PNG bytes are unchanged. Full revision whitespace checks pass.
- Executed all four original manuscript Python chunks without a socket: three generated tables match HTML exactly, 23 inline computed values occur in HTML/PDF, two MathML equations and three embedded figures are present. Visually inspected all eight PDF pages. JavaScript syntax checks pass; retained prior browser/independent-review evidence without repeating it.
- Wrote `SUBMISSION_READINESS.md` and prepared a draft PR title/body plus an offline handoff in the lane directory. Normal Quarto rendering failed at Jupyter local socket binding; preserved HTML/PDF bytes remain unchanged.
- Confirmed automatic resets stay disabled and the no-reset hold stays enabled; used no resets, paid overflow, new paid compute or external messaging.
- Completed the local delivery follow-up outside the restricted Subfleet sandbox: verified live GitHub ownership, admin access, no existing PRs and unchanged current main; rendered HTML/PDF with Quarto successfully; inspected all eight new PDF pages and passed all five paper-embed tests. HTML and extracted PDF text are unchanged; only PDF metadata and its generated instance identifier changed. Full logs and the eventual draft URL are recorded in the lane's `delivery-followup.md`.

## Next

1. Push this continuation and create the prepared draft PR; live checks and normal rendering are complete. No force push, merge, publication or submission is authorized.
2. Max chooses the outlet/release route and approves final framing and release. Keep the current model choices and 2026Q3 snapshot unless a separate refresh is authorized.

---

## Historical progress (preserved)

> Historical development document. Superseded for current findings and methods by the September 2026 growth-beliefs revision: see `RESEARCH_REVISION.md`, `paper/index.qmd`, and regenerated `outputs/`. Numbers below may use the former midpoint/sample-variance convention and approximate annual outcomes.

# Progress

## State

Build brief 3 is complete. Exact distribution scores, strictly expanding
benchmarks, `outputs/scores.csv`, the URL-wired Scores view, and
`SCORES_REPORT.md` are implemented, regenerated, and independently audited. Per
this brief's explicit instruction, no commits were created and the finished tree
remains uncommitted.

## Done

- Read `SOL_REPORT.md` and `INTERACTIVE_REPORT.md` completely before inspecting
  implementation details.
- Recorded the pre-existing unrelated changes to `paper/PAPER.md` and
  `lane3-note.md`; neither will be touched.
- Reconciled the contradictory commit instructions in favor of the task-specific
  “commit nothing” and “leave the tree uncommitted” requirements.
- Traced the respondent-density aggregation, concept-safe realization join,
  output build, compact interactive bundle, renderers, and URL-hash state.
- Fixed the no-lookahead convention: a target is usable only when its annual,
  quarterly, or monthly completion quarter is strictly before the forecast
  round; benchmark histories use the longest compatible local series.
- Confirmed the compact Scores view needs only nine emitted fields and should
  keep `data.js` comfortably below 1.2 MB at the existing four-significant-digit
  rounding.
- Recorded the original 1,080-byte CSS token block SHA-256
  (`acd919a4fe11dd8e737168379518c8fa32468c4372007834a63edd160cf6b69b`)
  for byte-identity verification.
- Implemented exact segment-integrated histogram CRPS, right-continuous PIT,
  seven pinball losses, empirical-sample CRPS, and Gaussian CRPS, including
  degenerate point-mass support and shared quantile construction.
- Added tests against dense numerical integration, the Monte Carlo energy
  identity, point-mass and Uniform closed forms, the integrated-pinball identity,
  response filtering, benchmark formulas, period cutoffs, and future-data
  invariance.
- Added full-history realization loading and minimum-10 expanding climatology and
  prior-error Gaussian benchmarks with explicit history counts and nullable skill.
- Rebuilt a 3,070-row `outputs/scores.csv` matching calibration exactly; all
  distribution scores are finite, pooled CRPS never exceeds average-individual
  CRPS, and PIT lies in `[0, 1]`.
- Added the Scores tab, compact score data, three palette-ordered lines, null-gap
  handling, tooltip/table/legend behavior, and URL-hash dispatch.
- Regenerated `interactive/data.js` at 800,301 bytes (66.7% of its 1.2 MB budget)
  with all 38 score combinations and full source-schema assertions.
- Wrote the requested per-horizon, pooling, tail-cluster, PIT, benchmark-gap,
  judgment-call, and validation analysis to `SCORES_REPORT.md`.
- Audited all 76 Scores states (38 combinations times Q1/all), including hash
  round-trips, tooltips, tables, null gaps, and fair duplicate-round aggregation.
- Passed the full 74-test suite, Ruff format/check, deterministic data generation,
  JavaScript syntax, token-integrity, source/output reconstruction, and
  working-tree audits.

## Next

- Review the uncommitted implementation and report.
