#!/bin/bash
# Render the manuscript and sync it under the site's /paper/web/ route.
# The public /paper/ URL serves the hand-written wrapper (site/paper/index.html),
# never the raw render — see the paper-embed pattern. Bump the ?v= version in
# the wrapper on every revision; tests/test_paper_embed.py locks the lockstep.
set -euo pipefail
cd "$(dirname "$0")/.."

mkdir -p paper/figures
cp site/figures/*.png paper/figures/

"$PWD/.venv/bin/python" -m ipykernel install --prefix "$PWD/.venv" \
  --name forecast-uncertainty-local --display-name "Forecast uncertainty (local)"
JUPYTER_PATH="$PWD/.venv/share/jupyter" QUARTO_PYTHON="$PWD/.venv/bin/python" \
  quarto render paper/index.qmd --to all --execute-daemon 0

mkdir -p site/paper/web
rsync -a --delete paper/out/index.html paper/out/index.pdf site/paper/web/
if [ -d paper/out/index_files ]; then
  rsync -a --delete paper/out/index_files/ site/paper/web/index_files/
fi
echo "synced paper/out -> site/paper/web"
