#!/usr/bin/env python3
"""Render Estuaries and Coasts submission figures from frozen figure-data sidecars.

No model fitting or endpoint selection occurs here. Output is journal-sized artwork:
174 mm width, EPS vector primary, 600 dpi TIFF, and PNG QA preview.
"""
from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

MM_PER_INCH = 25.4
FULL_WIDTH_IN = 174.0 / MM_PER_INCH

plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["Arial", "Helvetica", "DejaVu Sans"],
    "font.size": 8,
    "axes.titlesize": 8,
    "axes.labelsize": 8,
    "xtick.labelsize": 7,
    "ytick.labelsize": 7,
    "legend.fontsize": 7,
    "ps.fonttype": 42,
    "pdf.fonttype": 42,
    "axes.linewidth": 0.6,
    "lines.linewidth": 1.0,
})

STATE_LABELS = {
    "recorded_detection": "Recorded detection",
    "focal_frequency": "Focal frequency",
    "braun_blanquet_index": "Braun–Blanquet index",
    "blade_length_mm": "Blade length",
    "shoot_density_m2": "Shoot density",
}

MARKERS = ["o", "s", "^", "D", "v", "P"]
LINESTYLES = ["-", "--", "-.", ":", (0, (5, 1)), (0, (3, 1, 1, 1))]


def panel_letter(ax, letter: str):
    ax.text(
        0.0, 1.02, letter,
        transform=ax.transAxes,
        ha="left", va="bottom",
        fontweight="bold", fontsize=9,
    )


def save(fig: plt.Figure, outdir: Path, number: int):
    outdir.mkdir(parents=True, exist_ok=True)
    stem = f"Fig{number}"
    fig.savefig(outdir / f"{stem}.eps", format="eps", bbox_inches="tight")
    fig.savefig(outdir / f"{stem}.tif", format="tiff", dpi=600, bbox_inches="tight")
    fig.savefig(outdir / f"{stem}_QA.png", format="png", dpi=220, bbox_inches="tight")
    plt.close(fig)


def figure1(primary: Path, outdir: Path):
    nodes = pd.read_csv(primary / "figure1A_tampa_nodes.csv")
    state = pd.read_csv(primary / "figure1B_state_hierarchy.csv")

    fig, axes = plt.subplots(1, 2, figsize=(FULL_WIDTH_IN, 2.85),
                             gridspec_kw={"width_ratios": [1.0, 1.15]})
    ax = axes[0]
    for i, (wb, g) in enumerate(nodes.groupby("water_body", sort=True)):
        ax.scatter(
            g["longitude"], g["latitude"],
            s=16, marker=MARKERS[i % len(MARKERS)],
            facecolors="none", edgecolors=f"C{i}",
            linewidths=0.8, label=wb,
        )
    panel_letter(ax, "a")
    ax.set_xlabel("Longitude")
    ax.set_ylabel("Latitude")
    ax.legend(frameon=False, loc="upper left", bbox_to_anchor=(0.0, -0.14), ncol=2)
    ax.grid(alpha=0.15, linewidth=0.4)

    ax = axes[1]
    d = state.copy()
    d["label"] = d["state_dimension"].map(STATE_LABELS)
    y = np.arange(len(d))
    h = 0.32
    ax.barh(y - h/2, d["stable_node_r2"], height=h, hatch="//",
            facecolor="white", edgecolor="black", label="Stable transect identity")
    ax.barh(y + h/2, d["year_r2"], height=h, hatch="..",
            facecolor="white", edgecolor="0.4", label="Year")
    ax.set_yticks(y, d["label"])
    ax.invert_yaxis()
    ax.set_xlim(0, 1)
    ax.set_xlabel("Descriptive $R^2$")
    ax.legend(frameon=False, loc="lower right")
    ax.grid(axis="x", alpha=0.15, linewidth=0.4)
    panel_letter(ax, "b")
    fig.subplots_adjust(bottom=0.24, wspace=0.28)
    save(fig, outdir, 1)


def slope_panel(ax, d, state, xlabel, letter):
    x = d[d["state"] == state].copy().sort_values("water_body")
    if len(x) == 0:
        ax.axis("off")
        return
    y = np.arange(len(x))
    err = np.vstack([x["slope"] - x["ci_low"], x["ci_high"] - x["slope"]])
    ax.errorbar(x["slope"], y, xerr=err, fmt="o", color="black",
                ecolor="black", capsize=2.5, markersize=3.5)
    ax.axvline(0, linewidth=0.7, linestyle="--", color="0.5")
    ax.set_yticks(y, x["water_body"].str.replace(" Tampa Bay", "", regex=False))
    ax.set_xlabel(xlabel)
    ax.grid(axis="x", alpha=0.15, linewidth=0.4)
    panel_letter(ax, letter)


def figure2(primary: Path, outdir: Path):
    slopes = pd.read_csv(primary / "figure2E_canonical_slopes.csv")
    fig, axes = plt.subplots(2, 2, figsize=(FULL_WIDTH_IN, 4.7))
    slope_panel(axes[0,0], slopes, "recorded_detection", "Detection slope (yr$^{-1}$)", "a")
    slope_panel(axes[0,1], slopes, "blade_length_mm", "Blade length (mm yr$^{-1}$)", "b")
    slope_panel(axes[1,0], slopes, "shoot_density_m2", "Shoot density (shoots m$^{-2}$ yr$^{-1}$)", "c")
    slope_panel(axes[1,1], slopes, "focal_frequency", "Frequency slope (yr$^{-1}$)", "d")
    fig.tight_layout(pad=1.0)
    save(fig, outdir, 2)


def figure3(primary: Path, nps: Path, outdir: Path):
    lower = pd.read_csv(primary / "figure3A_lower_tampa_community.csv")
    ext = pd.read_csv(nps / "figure3B_nps_repeated_cover_trajectories.csv")
    fig, axes = plt.subplots(1, 2, figsize=(FULL_WIDTH_IN, 3.0))

    ax = axes[0]
    series = [
        ("Thalassia_frequency", "Thalassia"),
        ("Syringodium_frequency", "Syringodium"),
        ("Halodule_frequency", "Halodule"),
    ]
    for i, (col, label) in enumerate(series):
        ax.plot(
            lower["year"], lower[col],
            marker=MARKERS[i], linestyle=LINESTYLES[i],
            markersize=3, label=label,
        )
    ax.set_xlabel("Year")
    ax.set_ylabel("Mean transect frequency")
    ax.legend(frameon=False)
    ax.grid(alpha=0.15, linewidth=0.4)
    panel_letter(ax, "a")

    ax = axes[1]
    loc = ext.groupby(["Location", "year"], as_index=False)["focal_mean_cover"].mean()
    for i, (name, g) in enumerate(loc.groupby("Location", sort=True)):
        ax.plot(
            g["year"], g["focal_mean_cover"],
            marker=MARKERS[i % len(MARKERS)],
            linestyle=LINESTYLES[i % len(LINESTYLES)],
            markersize=2.5, label=name,
        )
    ax.set_xlabel("Year")
    ax.set_ylabel("Mean $Zostera$ cover (%)")
    ax.legend(frameon=False, ncol=1)
    ax.grid(alpha=0.15, linewidth=0.4)
    panel_letter(ax, "b")
    fig.tight_layout(pad=1.0)
    save(fig, outdir, 3)


def figure4(primary: Path, outdir: Path):
    d = pd.read_csv(primary / "figure4A_B_source_state_before_outcome.csv")
    ys = pd.read_csv(primary / "figure4C_target_year_logloss_delta.csv")
    fig, axes = plt.subplots(1, 3, figsize=(FULL_WIDTH_IN, 2.55))

    order = ["recorded_persistence", "recorded_loss"]
    labels = ["Persistence\n(n=664)", "Loss\n(n=24)"]
    data = [d.loc[d["next_year_state"] == k, "focal_frequency"].dropna().to_numpy(float) for k in order]
    axes[0].boxplot(data, tick_labels=labels, showfliers=False,
                    boxprops={"color":"black"}, whiskerprops={"color":"black"},
                    capprops={"color":"black"}, medianprops={"color":"black"})
    axes[0].set_ylabel("Source-year focal frequency")
    axes[0].grid(axis="y", alpha=0.15, linewidth=0.4)
    panel_letter(axes[0], "a")

    data = [d.loc[d["next_year_state"] == k, "bb_cover_mean_all_points"].dropna().to_numpy(float) for k in order]
    axes[1].boxplot(data, tick_labels=labels, showfliers=False,
                    boxprops={"color":"black"}, whiskerprops={"color":"black"},
                    capprops={"color":"black"}, medianprops={"color":"black"})
    axes[1].set_ylabel("Braun–Blanquet index")
    axes[1].grid(axis="y", alpha=0.15, linewidth=0.4)
    panel_letter(axes[1], "b")

    ax = axes[2]
    ax.axhline(0, linewidth=0.7, linestyle="--", color="0.5")
    ax.plot(ys["target_year"], ys["quantitative_minus_baseline"],
            marker="o", markersize=2.5, color="black")
    row = ys[ys["target_year"] == 2016]
    if len(row) == 1:
        x = float(row["target_year"].iloc[0])
        y = float(row["quantitative_minus_baseline"].iloc[0])
        ax.annotate("2016", xy=(x, y), xytext=(x+1.0, y),
                    arrowprops={"arrowstyle":"->", "lw":0.6}, fontsize=7)
    ax.set_xlabel("Target year")
    ax.set_ylabel("$\Delta$ log loss\n(quantitative − baseline)")
    ax.grid(alpha=0.15, linewidth=0.4)
    panel_letter(ax, "c")

    fig.tight_layout(pad=0.8)
    save(fig, outdir, 4)


def main(primary: Path, nps: Path, outdir: Path):
    figure1(primary, outdir)
    figure2(primary, outdir)
    figure3(primary, nps, outdir)
    figure4(primary, outdir)


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--primary", type=Path, default=Path("results/generated/figure_data"))
    p.add_argument("--nps", type=Path, default=Path("results/generated_nps_figure/figure_data"))
    p.add_argument("--out", type=Path, default=Path("results/generated_esco_figures"))
    a = p.parse_args()
    main(a.primary, a.nps, a.out)
