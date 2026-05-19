#!/usr/bin/env python3
from __future__ import annotations

import os
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
MAIN_DIR = REPO_ROOT / "main"
if str(MAIN_DIR) not in sys.path:
    sys.path.insert(0, str(MAIN_DIR))

os.environ.setdefault("MPLBACKEND", "Agg")
if "MPLCONFIGDIR" not in os.environ:
    mpl_config_dir = Path(tempfile.gettempdir()) / "qeco_adapt_mplconfig"
    try:
        mpl_config_dir.mkdir(parents=True, exist_ok=True)
        os.environ["MPLCONFIGDIR"] = str(mpl_config_dir)
    except OSError:
        pass

import matplotlib.pyplot as plt
import numpy as np

from common_experiment import SharedExperiment


OUTPUT_DIR = REPO_ROOT / "experiment_results" / "formula_visualizations"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def saturating_gating(load: float, scale_constant: float) -> float:
    return load / (load + scale_constant)


def energy_weight_from_gating(gating_strength: float, base_energy_weight: float, exponent: float) -> float:
    return base_energy_weight * ((1.0 + gating_strength) ** exponent)


def main() -> int:
    base_energy_weight = SharedExperiment.QECO_ADAPT_BASE_ENERGY_WEIGHT
    exponent = SharedExperiment.QECO_ADAPT_USER_EXPONENT
    base_profile = SharedExperiment.QECO_ARRIVAL_BASE_PROFILE
    user_activity_min = SharedExperiment.QECO_USER_ACTIVITY_MIN
    user_activity_max = SharedExperiment.QECO_USER_ACTIVITY_MAX

    users_axis = np.arange(1, 201)
    mean_base_profile = sum(base_profile) / len(base_profile)
    mean_user_activity = (user_activity_min + user_activity_max) / 2.0
    effective_loads = [
        float(users) * mean_base_profile * mean_user_activity / max(SharedExperiment.NUM_EDGES, 1)
        for users in users_axis
    ]
    scale_constant = float(max(SharedExperiment.NUM_EDGES * SharedExperiment.QECO_ADAPT_LOAD_SCALE, 1e-6))
    gating_values = [
        saturating_gating(load, scale_constant)
        for load in effective_loads
    ]
    energy_values = [
        energy_weight_from_gating(g, base_energy_weight, exponent)
        for g in gating_values
    ]

    fig, axs = plt.subplots(2, 1, figsize=(10, 10))

    axs[0].plot(users_axis, gating_values, color="#2f7ed8", linewidth=2.2, label="Gating strength")
    axs[0].set_title("QECO-ADAPT Gating Strength vs Number of Users")
    axs[0].set_xlabel("Number of Users")
    axs[0].set_ylabel("Gating Strength")
    axs[0].grid(True, linestyle="--", alpha=0.4)
    axs[0].legend()
    axs[0].text(
        0.02,
        0.95,
        "effective_load(users) = users * mean(base_profile) * mean(user_activity) / edges\n"
        "g(users) = effective_load(users) / (effective_load(users) + edges * load_scale_base)\n"
        f"load_scale_base = {SharedExperiment.QECO_ADAPT_LOAD_SCALE}\n"
        f"edges = {SharedExperiment.NUM_EDGES}, c = {scale_constant:.3f}\n"
        f"mean(base_profile) = {mean_base_profile:.3f}\n"
        f"mean(user_activity) = {mean_user_activity:.3f}",
        transform=axs[0].transAxes,
        ha="left",
        va="top",
        fontsize=10,
        bbox={"boxstyle": "round,pad=0.3", "facecolor": "white", "alpha": 0.85, "edgecolor": "#cccccc"},
    )

    axs[1].plot(users_axis, energy_values, color="#0b6e4f", linewidth=2.2, label="Adaptive energy weight")
    axs[1].set_title("Adaptive Energy Weight vs Number of Users")
    axs[1].set_xlabel("Number of Users")
    axs[1].set_ylabel("Energy Weight")
    axs[1].grid(True, linestyle="--", alpha=0.4)
    axs[1].legend()
    axs[1].text(
        0.02,
        0.95,
        "energy_weight = base * (1 + gating_strength)^exponent\n"
        f"base = {base_energy_weight}\n"
        f"exponent = {exponent}\n"
        f"base_profile = {base_profile}\n"
        f"user_activity_range = ({user_activity_min}, {user_activity_max})",
        transform=axs[1].transAxes,
        ha="left",
        va="top",
        fontsize=10,
        bbox={"boxstyle": "round,pad=0.3", "facecolor": "white", "alpha": 0.85, "edgecolor": "#cccccc"},
    )

    plt.tight_layout()
    output_path = OUTPUT_DIR / "qeco_adapt_formula.png"
    fig.savefig(output_path, dpi=140, bbox_inches="tight")
    plt.close(fig)

    print(f"Formula visualization: {output_path}")
    print(f"- gating_formula: load / (load + c)")
    print(f"- scale_constant_rule: c = edges * load_scale_base")
    print(f"- scale_constant_value: {scale_constant}")
    print(f"- users_axis: 1..200")
    print(f"- base_energy_weight: {base_energy_weight}")
    print(f"- exponent: {exponent}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
