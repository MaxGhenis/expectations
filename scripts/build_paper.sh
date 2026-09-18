#!/bin/bash
# Render both manuscripts and sync each under its own /paper/web/ route.
# The public /paper/ and /growth/paper/ URLs serve the hand-written wrappers
# (site/paper/index.html, site/growth/paper/index.html), never the raw render —
# see the paper-embed pattern. Bump the ?v= version in a wrapper on every
# revision; tests/test_paper_embed.py locks the lockstep for both.
set -euo pipefail
cd "$(dirname "$0")/.."

"$PWD/.venv/bin/python" -m ipykernel install --prefix "$PWD/.venv" \
  --name expectations-local --display-name "Expectations (local)"

render() {
  local source_dir="$1" web_dir="$2"
  mkdir -p "$source_dir/figures"
  cp site/figures/*.png "$source_dir/figures/"
  # One committed copy of the bibliography and citation style lives in paper/.
  # Typst will not read either from outside its own project root, so stage them
  # beside any manuscript that is its own Quarto project.
  if [ "$source_dir" != "paper" ]; then
    cp paper/references.bib paper/chicago-author-date.csl "$source_dir/"
  fi
  # Clear the last render first, so a failed render can never sync stale output.
  rm -f "$source_dir/out/index.html" "$source_dir/out/index.pdf"
  JUPYTER_PATH="$PWD/.venv/share/jupyter" QUARTO_PYTHON="$PWD/.venv/bin/python" \
    quarto render "$source_dir/index.qmd" --to all --execute-daemon 0
  mkdir -p "$web_dir"
  rsync -a --delete "$source_dir/out/index.html" "$source_dir/out/index.pdf" "$web_dir/"
  if [ -d "$source_dir/out/index_files" ]; then
    rsync -a --delete "$source_dir/out/index_files/" "$web_dir/index_files/"
  fi
  echo "synced $source_dir/out -> $web_dir"
}

render paper site/paper/web
render paper/growth site/growth/paper/web
