#!/bin/bash
# Raw data downloads for the expectations pipeline.
# Sources: Philadelphia Fed SPF individual files + documentation; ECB SPF
# microdata; FRED realization series. Run from data/raw/.
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

# FRED realizations (latest vintage; vintage-aware evaluation can come later via ALFRED)
for id in A191RL1A225NBEA GDPC1 UNRATE CPIAUCSL CORESTICKM159SFRBATL PCEPILFE CPILFESL; do
  fetch "https://fred.stlouisfed.org/graph/fredgraph.csv?id=${id}" "fred_${id}.csv"
done
