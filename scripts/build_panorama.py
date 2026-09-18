"""Write the panorama tables the main manuscript reads.

Run: uv run --no-sync python scripts/build_panorama.py
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from expectations.panorama import build_all

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs"


def load() -> dict[str, pd.DataFrame]:
    return {
        "measures": pd.read_csv(OUT / "measures.csv"),
        "calibration": pd.read_csv(OUT / "calibration.csv"),
        "scores": pd.read_csv(OUT / "scores.csv"),
        "benchmarks": pd.read_csv(OUT / "benchmark_summary.csv"),
    }


def main() -> None:
    tables = build_all(**load())
    for stem, frame in tables.items():
        path = OUT / f"{stem}.csv"
        frame.to_csv(path, index=False)
        print(f"wrote {path.relative_to(ROOT)} ({len(frame)} rows)")


if __name__ == "__main__":
    main()
