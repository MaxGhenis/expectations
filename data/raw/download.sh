#!/bin/bash
# Raw survey downloads for the expectations pipeline.
# Sources: Philadelphia Fed SPF individual files + documentation. Run from
# data/raw/. Outcome series are acquired, checksummed and dated by their own
# scripts, run from the repository root:
#   uv run python scripts/download_us_realizations.py
#   uv run python scripts/download_ecb_annual_realizations.py
set -uo pipefail
UA="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"
PHIL="https://www.philadelphiafed.org/-/media/frbp/assets/surveys-and-data/survey-of-professional-forecasters"

fetch () { # fetch <url> <out>
  if curl -fsSL -A "$UA" "$1" -o "$2"; then echo "OK   $2 ($(du -h "$2" | cut -f1))";
  else echo "FAIL $2  <- $1"; rm -f "$2"; fi
}

# US SPF individual density + long-run point files
for v in prgdp prpgdp prunemp prccpi prcpce recess rgdp10 cpi10 pce10; do
  fetch "$PHIL/data-files/files/individual_${v}.xlsx" "individual_${v}.xlsx"
done

# SPF documentation (bin schemes, Table 7 and friends)
fetch "$PHIL/spf-documentation.pdf" "../docs/spf-documentation.pdf"
