# Submission and release readiness

The September 2026 revision is preserved and locally validated on `ai-growth-divergence-closure-20260907`. It is ready for substantive review. Submission, publication and merging remain pending; no remote PR was created because GitHub access was unavailable.

The paper supports a descriptive professional-growth baseline: central forecasts declined, reconstructed uncertainty changed modestly, US probabilities above 4% fell, and the ECB's small longer-term tail increased. Retain the following qualifications in any submission or release:

- Main comparisons use fixed Q1 horizons and only two recent rounds (2025–26), against five rounds in 2015–19. All-round sensitivity averages within year first and mixes calendar horizon lengths.
- This is neither an AI causal estimate nor evidence of within-person updating, statistical equivalence or a matched disagreement between forecasters and AI experts. Conditional, global and distant-horizon AI scenarios are not interchangeable with annual US/euro-area unconditional distributions.
- Literal-bin bounds identify threshold probabilities, not sampling confidence intervals. Small probability in an open tail does not bound its growth magnitude. Means and spreads require the documented within-bin and tail reconstruction.
- Forecast evaluation uses revised/archived outcomes and overlapping targets, not historical release vintages or a real-time backtest. CRPS skill uses the ratio of mean losses on matched eligible rows; row-level percentage skill remains a sensitivity.

Validation on 7 September: 130 tests passed; Ruff lint/format and full-revision whitespace checks passed. Offline reproduction matched all nine output CSVs, companion JSON and three PNG figures byte for byte. Tracker numerical content matched after excluding modification/build timestamps. SVG output now has stable identifiers, no creation timestamp and no trailing whitespace; repeated builds are byte-identical, and normalized SVG structure is unchanged. All five new ECB source hashes match their provenance manifest.

The exact four manuscript Python chunks were executed directly: all three generated tables match the preserved HTML, and 23 inline values occur in both HTML and PDF. Both equations have native MathML and all three figures are embedded. All eight PDF pages were visually inspected without clipping or overlap. Browser validation and clean independent review are documented by the prior revision; this closure reran JavaScript syntax and preserved-render checks, not a new browser or independent semantic review.

Two environment gates remain. `git fetch origin main` failed with `Could not resolve host: github.com`; live ownership, current main, existing PR heads and remote permissions remain unverified. `bash scripts/build_paper.sh` failed because Jupyter could not bind a local socket (`PermissionError: [Errno 1] Operation not permitted`). The original HTML/PDF remain unchanged; direct calculation verification does not replace a successful full Quarto render.

Next: from this isolated worktree, verify the live repository and branch ownership, fetch and safely integrate current main if needed, complete the normal Quarto HTML/PDF render, then open the prepared draft PR. Before release, Max must choose the outlet/release route and approve the final framing and deployment/submission. Retain the existing 2026Q3 snapshot unless a separately authorized refresh is intended. No additional model changes or new AI-comparator estimates are required for this closure.

The local audit, exact source snapshot, logs, manuscript verification script, draft PR body and handoff live in `/Users/maxghenis/capacity-sprint-20260907/spf-closure/`. `RESEARCH_REVISION.md` records the research revision itself; this note records the subsequent preservation and validation limits.
