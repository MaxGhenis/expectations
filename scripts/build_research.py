"""Build the paper's tables, figures and public growth research bundle."""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from expectations.research import (
    GROWTH_SERIES,
    benchmark_summary,
    period_comparisons,
    select_series,
)

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs"
FIGURES = ROOT / "site" / "figures"
BLUE, ORANGE, GREEN = "#2469a8", "#b94d25", "#187b60"


def style_axis(ax, ylabel):
    ax.set_ylabel(ylabel)
    ax.set_xlim(2006, 2026)
    ax.set_xticks([2006, 2010, 2015, 2020, 2026])
    ax.grid(axis="y", color="#e4e6e8", linewidth=0.65)
    ax.set_axisbelow(True)
    ax.spines[["top", "right"]].set_visible(False)
    ax.axvspan(2020, 2024.2, color="#90979f", alpha=0.10, linewidth=0)
    ax.axvline(2022.9, color="#777777", linewidth=0.7, linestyle=":")


def save(fig, name):
    FIGURES.mkdir(parents=True, exist_ok=True)
    fig.savefig(FIGURES / f"{name}.png", dpi=180, bbox_inches="tight")
    # Fixed IDs and no creation timestamp make identical inputs byte-reproducible.
    svg = FIGURES / f"{name}.svg"
    with matplotlib.rc_context({"svg.hashsalt": "forecast-uncertainty"}):
        fig.savefig(svg, bbox_inches="tight", metadata={"Date": None})
    svg.write_text(
        "\n".join(line.rstrip() for line in svg.read_text().splitlines()) + "\n"
    )
    plt.close(fig)


def make_figures(measures, tails, longrun):
    plt.rcParams.update(
        {"font.size": 10, "axes.titlesize": 11, "figure.facecolor": "white"}
    )
    names = list(GROWTH_SERIES)
    titles = [
        "US: next calendar year",
        "US: three calendar years ahead",
        "Euro area: four calendar years ahead",
    ]
    fig, axes = plt.subplots(3, 1, figsize=(8.8, 9.0), layout="constrained")
    for ax, name, title in zip(axes, names, titles, strict=True):
        d = select_series(measures, name).sort_values("year")
        ax.fill_between(
            d.year,
            d.q05,
            d.q95,
            color=BLUE,
            alpha=0.13,
            label="Pooled 5th–95th percentiles",
        )
        ax.plot(d.year, d["mean"], color=BLUE, lw=2, label="Pooled mean")
        ax.set_title(title, loc="left", fontweight="bold")
        style_axis(ax, "Annual real GDP growth (%)")
        ax.set_ylim(min(-4, d.q05.min() - 0.2), max(7, d.q95.max() + 0.2))
    axes[0].legend(loc="upper left", frameon=False, ncol=2, fontsize=9)
    axes[-1].set_xlabel("Survey year (Q1 rounds only)")
    save(fig, "growth-outlook")

    fig, axes = plt.subplots(2, 2, figsize=(9.2, 6.4), layout="constrained")
    for ax, name, title in zip(axes.flat, names, titles, strict=False):
        d = select_series(measures, name).sort_values("year")
        ax.plot(d.year, d.total_sd, color=BLUE, lw=2, label="Pooled SD")
        ax.plot(d.year, d.iqr, color=ORANGE, lw=1.7, linestyle="--", label="Pooled IQR")
        style_axis(ax, "Percentage points")
        ax.set_title(title.replace("calendar ", ""), loc="left", fontweight="bold")
        ax.set_ylim(bottom=0)
    axes[0, 0].legend(frameon=False, fontsize=9)
    ax = axes[1, 1]
    d = longrun[(longrun.variable == "RGDP10") & (longrun.year >= 2006)].sort_values(
        "year"
    )
    ax.plot(d.year, d["median"], color=GREEN, lw=2)
    ax.set_title("US: ten-year median point forecast", loc="left", fontweight="bold")
    style_axis(ax, "Average annual growth (%)")
    ax.set_ylim(0, 4)
    for ax in axes[1]:
        ax.set_xlabel("Survey year (Q1)")
    save(fig, "growth-spread")

    fig, axes = plt.subplots(3, 2, figsize=(9.2, 8.2), layout="constrained")
    for i, (name, title) in enumerate(zip(names, titles, strict=True)):
        d = select_series(tails, name)
        for j, threshold in enumerate([4.0, 5.0]):
            ax = axes[i, j]
            t = d[d.threshold == threshold].sort_values("year")
            ax.fill_between(
                t.year,
                100 * t.probability_lower,
                100 * t.probability_upper,
                color=BLUE,
                alpha=0.18,
            )
            ax.plot(
                t.year,
                100 * t.probability_upper,
                color=BLUE,
                lw=1.5,
                label="Upper bound",
            )
            ax.plot(
                t.year,
                100 * t.probability_lower,
                color=BLUE,
                lw=1,
                linestyle="--",
                label="Lower bound",
            )
            style_axis(ax, "Probability (%)")
            ax.set_title(
                f"{title.replace('calendar ', '')}\nGrowth above {threshold:g}%",
                loc="left",
                fontsize=10,
            )
            ax.set_ylim(0, max(8, np.ceil(t.probability_upper.max() * 100 / 5) * 5))
    axes[0, 0].legend(frameon=False, fontsize=8)
    for ax in axes[-1]:
        ax.set_xlabel("Survey year (Q1)")
    save(fig, "growth-upper-tails")


def main():
    measures = pd.read_csv(OUT / "measures.csv")
    tails = pd.read_csv(OUT / "growth_tails.csv")
    scores = pd.read_csv(OUT / "scores.csv")
    longrun = pd.read_csv(OUT / "longrun_points.csv")
    comparisons = period_comparisons(measures, tails)
    comparisons.to_csv(OUT / "growth_comparison.csv", index=False)
    benchmark_summary(scores).to_csv(OUT / "benchmark_summary.csv", index=False)
    make_figures(measures, tails, longrun)
    records = comparisons.where(pd.notna(comparisons), None).to_dict("records")
    destination = ROOT / "site" / "growth"
    destination.mkdir(exist_ok=True)
    payload = {
        "as_of": "2026Q3",
        "comparison": records,
        "note": "Q1 comparisons use the 2026Q1 round; all-round sensitivities include 2026Q1–Q3 with equal weight per survey year. Bounds reflect bin resolution, not sampling confidence intervals.",
    }
    (destination / "data.json").write_text(
        json.dumps(payload, allow_nan=False, indent=2) + "\n"
    )
    print(
        f"Wrote {len(comparisons)} comparison rows, benchmark summary and three figures"
    )


if __name__ == "__main__":
    main()
