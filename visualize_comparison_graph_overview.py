#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt


ROOT_DIR = Path(__file__).resolve().parent
COMPARISON_DIR = ROOT_DIR / "experiment_results" / "comparisons"

SCENARIOS = [
    ("S1: users=10, edges=1", "user_10_ep_400_edge_1"),
    ("S2: users=30, edges=1", "user_30_ep_400_edge_1"),
    ("S3: users=30, edges=3", "user_30_ep_400_edge_3"),
    ("S4: users=50, edges=1", "user_50_ep_400_edge_1"),
    ("S5: users=50, edges=10", "user_50_ep_400_edge_10"),
    ("S6: users=80, edges=1", "user_80_ep_400_edge_1"),
    ("S7: users=80, edges=3", "user_80_ep_400_edge_3"),
]


def render_overview(filename: str, output_name: str, title: str) -> Path:
    fig, axes = plt.subplots(4, 2, figsize=(18, 26))
    fig.patch.set_facecolor("white")
    axes_flat = axes.flatten()

    for ax, (label, folder) in zip(axes_flat, SCENARIOS):
        image_path = COMPARISON_DIR / folder / filename
        image = plt.imread(image_path)
        ax.imshow(image)
        ax.set_title(label, fontsize=13, fontweight="bold", pad=8)
        ax.axis("off")

    for ax in axes_flat[len(SCENARIOS):]:
        ax.axis("off")

    fig.suptitle(title, fontsize=20, fontweight="bold", y=0.995)
    plt.tight_layout(rect=(0, 0, 1, 0.985))

    output_path = COMPARISON_DIR / output_name
    fig.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    return output_path


def main() -> int:
    finals_path = render_overview(
        "comparison_finals.png",
        "comparison_finals_overview.png",
        "Final 10% Mean Comparison Across MEC Scenarios",
    )
    timeseries_path = render_overview(
        "comparison_timeseries_smoothed.png",
        "comparison_timeseries_smoothed_overview.png",
        "Smoothed Episode Time-Series Across MEC Scenarios",
    )

    print(f"Final comparison overview: {finals_path}")
    print(f"Smoothed time-series overview: {timeseries_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
