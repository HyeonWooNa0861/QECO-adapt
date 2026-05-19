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


def main() -> int:
    base_profile = SharedExperiment.QECO_ARRIVAL_BASE_PROFILE
    base_profile_mean = sum(base_profile) / len(base_profile)
    user_activity_mean = (SharedExperiment.QECO_USER_ACTIVITY_MIN + SharedExperiment.QECO_USER_ACTIVITY_MAX) / 2.0
    load_scale_actual = SharedExperiment.NUM_EDGES * SharedExperiment.QECO_ADAPT_LOAD_SCALE

    fig = plt.figure(figsize=(13.5, 10.5))
    fig.patch.set_facecolor("white")

    title_style = {"fontsize": 18, "fontweight": "bold", "color": "#1f2d3a"}
    section_style = {"fontsize": 13, "fontweight": "bold", "color": "#2f4f6f"}
    formula_style = {"fontsize": 15, "color": "#111111"}
    note_style = {"fontsize": 10.5, "color": "#444444"}

    fig.text(0.05, 0.95, "QECO-ADAPT Mathematical Definitions", **title_style)

    fig.text(0.05, 0.885, "3.1 Task arrival model", **section_style)
    fig.text(
        0.07,
        0.835,
        r"$\mathcal{U}=\{1,2,\ldots,N\},\quad \mathcal{E}=\{1,2,\ldots,M\}$",
        **formula_style,
    )
    fig.text(
        0.07,
        0.785,
        r"$\mathbf{b}=(b_1,b_2,\ldots,b_K),\quad 0\leq b_k\leq 1,\quad "
        r"a_u\in[a_{\min},a_{\max}]$",
        **formula_style,
    )
    fig.text(
        0.07,
        0.735,
        r"$p_{\mathrm{arrive}}(u,t)=\mathrm{clip}(b_{\kappa(t)}a_u,0,1)"
        r"=\min\{1,\max(0,b_{\kappa(t)}a_u)\}$",
        **formula_style,
    )

    fig.text(0.05, 0.655, "3.2 Effective load", **section_style)
    fig.text(
        0.07,
        0.605,
        r"$\bar{b}=\frac{1}{K}\sum_{k=1}^{K}b_k,\quad "
        r"\bar{a}=\frac{1}{N}\sum_{u=1}^{N}a_u\approx\frac{a_{\min}+a_{\max}}{2}$",
        **formula_style,
    )
    fig.text(
        0.07,
        0.555,
        r"$L_{\mathrm{eff}}=\frac{N\bar{b}\bar{a}}{M}$",
        **formula_style,
    )

    fig.text(0.05, 0.475, "3.3 Adaptive gating", **section_style)
    fig.text(
        0.07,
        0.425,
        r"$c=M\lambda,\quad "
        r"g(L_{\mathrm{eff}})=\frac{L_{\mathrm{eff}}}{L_{\mathrm{eff}}+c}"
        r"=\frac{L_{\mathrm{eff}}}{L_{\mathrm{eff}}+M\lambda}$",
        **formula_style,
    )
    fig.text(
        0.07,
        0.375,
        r"$0\leq g(L_{\mathrm{eff}})<1,\quad "
        r"\frac{\partial g}{\partial L_{\mathrm{eff}}}"
        r"=\frac{M\lambda}{(L_{\mathrm{eff}}+M\lambda)^2}>0$",
        **formula_style,
    )

    fig.text(0.05, 0.295, "3.4 Adaptive energy weight and reward", **section_style)
    fig.text(
        0.07,
        0.245,
        r"$w_E=w_0\left(1+g(L_{\mathrm{eff}})\right)^{\rho}$",
        **formula_style,
    )
    fig.text(
        0.07,
        0.195,
        r"$E_i^{\mathrm{scaled}}=10\cdot\mathrm{Normalize}"
        r"(E_i^{\mathrm{comp}}+E_i^{\mathrm{trans}};0,20)$",
        **formula_style,
    )
    fig.text(
        0.07,
        0.145,
        r"$C_i^{\mathrm{adapt}}=2\left(s_iD_i+(1-s_i)w_EE_i^{\mathrm{scaled}}\right)$",
        **formula_style,
    )
    fig.text(
        0.07,
        0.095,
        r"$r_i^{\mathrm{adapt}}=-C_i^{\mathrm{adapt}}\;(\mathrm{unfinished}),\quad "
        r"r_i^{\mathrm{adapt}}=4D_{\max}-C_i^{\mathrm{adapt}}\;(\mathrm{finished})$",
        **formula_style,
    )

    fig.text(
        0.05,
        0.035,
        "Experiment constants: "
        f"b={base_profile}, mean(b)={base_profile_mean:.3f}, "
        f"mean(a)={user_activity_mean:.3f}, lambda={SharedExperiment.QECO_ADAPT_LOAD_SCALE}, "
        f"c={load_scale_actual:.3f}, w0={SharedExperiment.QECO_ADAPT_BASE_ENERGY_WEIGHT}, "
        f"rho={SharedExperiment.QECO_ADAPT_USER_EXPONENT}.",
        **note_style,
    )

    output_path = OUTPUT_DIR / "qeco_adapt_math_definitions.png"
    fig.savefig(output_path, dpi=160, bbox_inches="tight")
    plt.close(fig)

    print(f"QECO-ADAPT math definitions visualization: {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
