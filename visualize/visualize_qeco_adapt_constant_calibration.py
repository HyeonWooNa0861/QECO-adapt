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

from common_experiment import SharedExperiment


OUTPUT_DIR = REPO_ROOT / "experiment_results" / "formula_visualizations"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def gating(users: int, edges: int) -> tuple[float, float, float]:
    mean_b = sum(SharedExperiment.QECO_ARRIVAL_BASE_PROFILE) / len(SharedExperiment.QECO_ARRIVAL_BASE_PROFILE)
    mean_a = (SharedExperiment.QECO_USER_ACTIVITY_MIN + SharedExperiment.QECO_USER_ACTIVITY_MAX) / 2.0
    load = users * mean_b * mean_a / max(edges, 1)
    scale = edges * SharedExperiment.QECO_ADAPT_LOAD_SCALE
    return load, scale, load / (load + scale)


def main() -> int:
    base_profile = SharedExperiment.QECO_ARRIVAL_BASE_PROFILE
    mean_b = sum(base_profile) / len(base_profile)
    mean_a = (SharedExperiment.QECO_USER_ACTIVITY_MIN + SharedExperiment.QECO_USER_ACTIVITY_MAX) / 2.0
    lambda_base = SharedExperiment.QECO_ADAPT_LOAD_SCALE
    w0 = SharedExperiment.QECO_ADAPT_BASE_ENERGY_WEIGHT
    rho = SharedExperiment.QECO_ADAPT_USER_EXPONENT

    fig = plt.figure(figsize=(13.5, 9.5))
    fig.patch.set_facecolor("white")

    title_style = {"fontsize": 18, "fontweight": "bold", "color": "#1f2d3a"}
    section_style = {"fontsize": 13, "fontweight": "bold", "color": "#2f4f6f"}
    formula_style = {"fontsize": 15, "color": "#111111"}
    note_style = {"fontsize": 10.5, "color": "#444444"}

    fig.text(0.05, 0.95, "QECO-ADAPT Calibration Constants", **title_style)

    fig.text(0.05, 0.885, "Arrival and user-activity calibration", **section_style)
    fig.text(
        0.07,
        0.835,
        r"$\mathbf{b}=(0.18,0.30,0.42,0.24),\quad "
        rf"\bar{{b}}={mean_b:.3f}\approx 0.3$",
        **formula_style,
    )
    fig.text(
        0.07,
        0.79,
        r"$a_{\min}=0.7,\quad a_{\max}=1.3,\quad "
        rf"\bar{{a}}=\frac{{a_{{\min}}+a_{{\max}}}}{{2}}={mean_a:.1f}$",
        **formula_style,
    )
    fig.text(
        0.07,
        0.735,
        "Interpretation: the mean arrival load stays close to the original 0.3 setting, "
        "while time-of-day variation and user heterogeneity are introduced.",
        **note_style,
    )

    fig.text(0.05, 0.655, "Edge-proportional gating scale", **section_style)
    fig.text(
        0.07,
        0.605,
        rf"$\lambda={lambda_base:.0f}\;(\mathrm{{per\ edge\ load\ scale}}),\quad c=M\lambda$",
        **formula_style,
    )
    fig.text(
        0.07,
        0.555,
        r"$g(L_{\mathrm{eff}})=\frac{L_{\mathrm{eff}}}{L_{\mathrm{eff}}+M\lambda}$",
        **formula_style,
    )
    fig.text(
        0.07,
        0.505,
        "Interpretation: increasing the number of edge nodes both lowers per-edge load "
        "and increases the scale constant, so gating becomes less aggressive.",
        **note_style,
    )

    ax = fig.add_axes([0.07, 0.275, 0.55, 0.17])
    ax.axis("off")
    table_rows = []
    for edges in (1, 3, 10):
        load, scale, g = gating(users=30, edges=edges)
        table_rows.append([f"{edges}", f"{load:.2f}", f"{scale:.2f}", f"{g:.3f}"])
    table = ax.table(
        cellText=table_rows,
        colLabels=["Edges M", "L_eff at N=30", "c=Mlambda", "g(L_eff)"],
        loc="center",
        cellLoc="center",
    )
    table.auto_set_font_size(False)
    table.set_fontsize(10.5)
    table.scale(1.0, 1.45)
    for (row, col), cell in table.get_celld().items():
        cell.set_edgecolor("#d0d7de")
        if row == 0:
            cell.set_facecolor("#eaf2f8")
            cell.set_text_props(weight="bold", color="#1f2d3a")
        else:
            cell.set_facecolor("white")

    fig.text(0.05, 0.205, "Adaptive energy weighting", **section_style)
    fig.text(
        0.07,
        0.155,
        rf"$w_0={w0:.2f},\quad \rho={rho:.2f},\quad "
        r"w_E=w_0(1+g)^{\rho}$",
        **formula_style,
    )
    fig.text(
        0.07,
        0.105,
        "Interpretation: w0 gives a mild baseline energy emphasis, while rho<1 makes "
        "the energy penalty increase sublinearly as load grows.",
        **note_style,
    )

    fig.text(
        0.05,
        0.045,
        "These constants are calibration parameters for the common MEC experiment, "
        "not closed-form optimal values. They are chosen to preserve QECO's QoE stability "
        "while adding load-aware energy control.",
        **note_style,
    )

    output_path = OUTPUT_DIR / "qeco_adapt_constant_calibration.png"
    fig.savefig(output_path, dpi=160, bbox_inches="tight")
    plt.close(fig)

    print(f"QECO-ADAPT constant calibration visualization: {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
