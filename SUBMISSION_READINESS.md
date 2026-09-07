# Submission and release readiness

The September 2026 revision is preserved and locally validated on `ai-growth-divergence-closure-20260907`. It is ready for substantive review through a draft PR. Submission, publication and merging remain pending.

The paper supports a descriptive professional-growth baseline: central forecasts declined, reconstructed uncertainty changed modestly, US probabilities above 4% fell, and the ECB's small longer-term tail increased. Retain the following qualifications in any submission or release:

- Main comparisons use fixed Q1 horizons and only two recent rounds (2025–26), against five rounds in 2015–19. All-round sensitivity averages within year first and mixes calendar horizon lengths.
- This is neither an AI causal estimate nor evidence of within-person updating, statistical equivalence or a matched disagreement between forecasters and AI experts. Conditional, global and distant-horizon AI scenarios are not interchangeable with annual US/euro-area unconditional distributions.
- Literal-bin bounds identify threshold probabilities, not sampling confidence intervals. Small probability in an open tail does not bound its growth magnitude. Means and spreads require the documented within-bin and tail reconstruction.
- Forecast evaluation uses revised/archived outcomes and overlapping targets, not historical release vintages or a real-time backtest. CRPS skill uses the ratio of mean losses on matched eligible rows; row-level percentage skill remains a sensitivity.

Validation on 7 September: 130 tests passed; Ruff lint/format and full-revision whitespace checks passed. Offline reproduction matched all nine output CSVs, companion JSON and three PNG figures byte for byte. Tracker numerical content matched after excluding modification/build timestamps. SVG output now has stable identifiers, no creation timestamp and no trailing whitespace; repeated builds are byte-identical, and normalized SVG structure is unchanged. All five new ECB source hashes match their provenance manifest.

The exact four manuscript Python chunks were executed directly: all three generated tables match the preserved HTML, and 23 inline values occur in both HTML and PDF. Both equations have native MathML and all three figures are embedded. All eight PDF pages were visually inspected without clipping or overlap. Browser validation and clean independent review are documented by the prior revision; this closure reran JavaScript syntax and preserved-render checks, not a new browser or independent semantic review.

Both initial environment gates were resolved on 7 September in the normal local runtime. Live GitHub checks verified the repository owner, `main` default branch, write permission and absence of an existing PR. A successful fetch confirmed current `origin/main` is still `ade2384f269d72456ec65fc4d0e4172b14c650d9`, so no base integration was needed. `bash scripts/build_paper.sh` completed both Quarto HTML and PDF outputs. HTML is byte-identical to the preserved render; PDF differences are limited to creation/modification metadata and its generated instance identifier. Extracted PDF text is identical. All eight newly rendered PDF pages were inspected without clipping or overlap, and all five paper-embed tests pass.

Next: review the draft PR and its research framing. Before release, Max must choose the outlet/release route and approve the final framing and deployment/submission. Retain the existing 2026Q3 snapshot unless a separately authorized refresh is intended. No additional model changes or new AI-comparator estimates are required for this closure.

The local audit, exact source snapshot, logs, manuscript verification script, draft PR body and handoff live in `/Users/maxghenis/capacity-sprint-20260907/spf-closure/`. `RESEARCH_REVISION.md` records the research revision itself; this note records the subsequent preservation and validation limits.
