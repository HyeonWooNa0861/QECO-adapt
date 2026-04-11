#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt


ROOT_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = ROOT_DIR / "experiment_results" / "formula_visualizations"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def main() -> int:
    fig = plt.figure(figsize=(12.5, 9.0))
    fig.patch.set_facecolor("white")

    title_style = {"fontsize": 18, "fontweight": "bold", "color": "#1f2d3a"}
    section_style = {"fontsize": 13, "fontweight": "bold", "color": "#2f4f6f"}
    formula_style = {"fontsize": 15, "color": "#111111"}
    note_style = {"fontsize": 11, "color": "#444444"}

    fig.text(0.05, 0.945, "Metric Aggregation Formulas for Common MEC Evaluation", **title_style)

    fig.text(0.05, 0.875, "1. Task-level QoE", **section_style)
    fig.text(
        0.07,
        0.82,
        r"$\tilde{E}_{t,u}=10\cdot\frac{E^{comp}_{t,u}+E^{trans}_{t,u}-0}{20-0}$",
        **formula_style,
    )
    fig.text(
        0.07,
        0.765,
        r"$C_{t,u}=2\left(s_u d_{t,u}+(1-s_u)\tilde{E}_{t,u}\right)$",
        **formula_style,
    )
    fig.text(
        0.07,
        0.705,
        r"$QoE_{t,u}=-C_{t,u}\;\;(\mathrm{unfinished}),\quad QoE_{t,u}=4D_{\max}-C_{t,u}\;\;(\mathrm{finished})$",
        **formula_style,
    )

    fig.text(0.05, 0.625, "2. Episode-level aggregation", **section_style)
    fig.text(
        0.07,
        0.57,
        r"$\mathcal{A}_e=\{(t,u)\mid task\_size_{t,u}>0\}$",
        **formula_style,
    )
    fig.text(
        0.07,
        0.515,
        r"$QoE_e=\frac{1}{|\mathcal{A}_e|}\sum_{(t,u)\in\mathcal{A}_e}QoE_{t,u},\quad "
        r"Delay_e=\frac{1}{|\mathcal{A}_e|}\sum_{(t,u)\in\mathcal{A}_e}d_{t,u}$",
        **formula_style,
    )
    fig.text(
        0.07,
        0.455,
        r"$Energy_e=\frac{1}{|\mathcal{A}_e|}\sum_{(t,u)\in\mathcal{A}_e}"
        r"\left(E^{ue\_comp}_{t,u}+E^{ue\_trans}_{t,u}+\sum_kE^{edge\_comp}_{t,u,k}+\sum_kE^{idle}_{t,u,k}\right)$",
        **formula_style,
    )
    fig.text(
        0.07,
        0.395,
        r"$Drop_e=\sum_{t,u}unfinished\_task_{t,u}$",
        **formula_style,
    )

    fig.text(0.05, 0.315, "3. Final comparison aggregation", **section_style)
    fig.text(
        0.07,
        0.26,
        r"$Final(M)=\frac{1}{K}\sum_{i=N-K+1}^{N}M_i,\quad K=\max(1,\lfloor0.1N\rfloor)$",
        **formula_style,
    )
    fig.text(
        0.07,
        0.205,
        r"$M\in\{QoE,Delay,Energy,Drop\}$, using the raw episode series rather than the aligned comparison axis.",
        **formula_style,
    )

    fig.text(
        0.05,
        0.115,
        "Interpretation: QoE, Delay, and Energy are averaged over arrived tasks in each episode; "
        "Drop is the number of unfinished tasks. The final table reports the mean of the last 10% raw episodes.",
        **note_style,
    )

    output_path = OUTPUT_DIR / "metric_aggregation_formula.png"
    fig.savefig(output_path, dpi=160, bbox_inches="tight")
    plt.close(fig)

    print(f"Metric formula visualization: {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
