"""Fail when the committed outputs no longer match what the pipeline produces.

Rebuilds the core tables from the raw survey files into a scratch directory and
compares each with its committed copy. The comparison is numeric, not byte for
byte: floats print differently in the sixteenth digit across platforms.
"""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path

import pandas as pd

from expectations.build import build_outputs

ROOT = Path(__file__).resolve().parents[1]
OUTPUTS = ROOT / "outputs"


def stale_outputs() -> list[str]:
    stale = []
    with tempfile.TemporaryDirectory() as scratch:
        build_outputs(output_dir=scratch)
        for fresh_path in sorted(Path(scratch).glob("*.csv")):
            committed_path = OUTPUTS / fresh_path.name
            if not committed_path.exists():
                stale.append(f"{fresh_path.name}: not committed")
                continue
            fresh, committed = pd.read_csv(fresh_path), pd.read_csv(committed_path)
            try:
                pd.testing.assert_frame_equal(
                    fresh, committed, check_exact=False, rtol=1e-9, atol=1e-12
                )
            except AssertionError as difference:
                stale.append(f"{fresh_path.name}: {str(difference).splitlines()[0]}")
    return stale


def main() -> None:
    stale = stale_outputs()
    if stale:
        print("Committed outputs differ from a fresh build:")
        for line in stale:
            print(f"  {line}")
        print("Run `uv run python -m expectations.build` and commit the result.")
        sys.exit(1)
    print("outputs/ matches a fresh build")


if __name__ == "__main__":
    main()
