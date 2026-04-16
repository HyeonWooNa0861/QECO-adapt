#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from statistics import mean, median

ROOT_DIR = Path(__file__).resolve().parent
EXPERIMENT_ROOT = ROOT_DIR / "experiment_results"
AVAILABLE_ALGORITHMS = ("droo", "qeco", "cd", "qeco_adapt", "twdqn")
ALGORITHM_ALIASES = {"qeco-adapt": "qeco_adapt"}
DEFAULT_ALGORITHMS = ("droo", "qeco", "qeco_adapt", "twdqn")
OUTPUT_NAME_TOKENS = {"qeco_adapt": "qeco-adapt"}
LABELS = {
    "droo": "DROO",
    "qeco": "QECO",
    "cd": "CD",
    "qeco_adapt": "QECO-ADAPT",
    "twdqn": "Tang&Wong DQN",
}
COLORS = {
    "droo": "#0b6e4f",
    "qeco": "#b33f62",
    "cd": "#7a5195",
    "qeco_adapt": "#2f7ed8",
    "twdqn": "#d08c00",
}
FONT_SCALE = 2
BASE_FONT_SIZE = 10 * FONT_SCALE
TITLE_FONT_SIZE = 12 * FONT_SCALE
AXIS_LABEL_FONT_SIZE = 10 * FONT_SCALE
TICK_FONT_SIZE = 10 * FONT_SCALE
LEGEND_FONT_SIZE = 10 * FONT_SCALE
BAR_VALUE_FONT_SIZE = 8 * FONT_SCALE
NOTE_FONT_SIZE = 9 * FONT_SCALE


def configure_plot_fonts(plt) -> None:
    plt.rcParams.update(
        {
            "font.size": BASE_FONT_SIZE,
            "axes.titlesize": TITLE_FONT_SIZE,
            "axes.labelsize": AXIS_LABEL_FONT_SIZE,
            "xtick.labelsize": TICK_FONT_SIZE,
            "ytick.labelsize": TICK_FONT_SIZE,
            "legend.fontsize": LEGEND_FONT_SIZE,
        }
    )


def style_axis_text(ax, x_label_rotation: int | None = None) -> None:
    ax.title.set_fontsize(TITLE_FONT_SIZE)
    ax.xaxis.label.set_fontsize(AXIS_LABEL_FONT_SIZE)
    ax.yaxis.label.set_fontsize(AXIS_LABEL_FONT_SIZE)
    ax.tick_params(axis="both", labelsize=TICK_FONT_SIZE)
    if x_label_rotation is not None:
        ax.tick_params(axis="x", labelrotation=x_label_rotation)
        for label in ax.get_xticklabels():
            label.set_ha("right")


def format_bar_value(value: float) -> str:
    abs_value = abs(value)
    if abs_value >= 100:
        return f"{value:.1f}"
    if abs_value >= 10:
        return f"{value:.2f}"
    return f"{value:.3f}"


def annotate_bars(ax, bars) -> None:
    heights = [bar.get_height() for bar in bars]
    if heights:
        max_height = max(heights)
        min_height = min(heights)
        if max_height > 0:
            ax.set_ylim(top=max_height * 1.24)
        if min_height < 0:
            ax.set_ylim(bottom=min_height * 1.24)

    for bar in bars:
        height = bar.get_height()
        ax.annotate(
            format_bar_value(height),
            xy=(bar.get_x() + bar.get_width() / 2, height),
            xytext=(0, 8),
            textcoords="offset points",
            ha="center",
            va="bottom",
            fontsize=BAR_VALUE_FONT_SIZE,
            rotation=0,
        )

def load_run_profile(run_dir: Path) -> dict:
    config_path = run_dir / "experiment_config.json"
    if not config_path.exists():
        raise FileNotFoundError(f"Missing experiment_config.json in run directory: {run_dir}")
    with open(config_path) as f:
        payload = json.load(f)
    return {
        "num_users": payload.get("num_users"),
        "num_edges": payload.get("num_edges"),
        "episodes": payload.get("qeco", {}).get("episodes"),
        "max_delay": payload.get("max_delay"),
    }


def scenario_title_from_profile(profile: dict) -> str:
    return (
        f"user_{profile['num_users']}"
        f"_ep_{profile['episodes']}"
        f"_edge_{profile['num_edges']}"
    )


def default_output_name(algorithms: tuple[str, ...], profile: dict) -> str:
    if algorithms == DEFAULT_ALGORITHMS:
        return scenario_title_from_profile(profile)
    algorithm_tokens = [OUTPUT_NAME_TOKENS.get(algorithm, algorithm) for algorithm in algorithms]
    return f"{scenario_title_from_profile(profile)}__{'-'.join(algorithm_tokens)}"


def normalize_algorithm_name(algorithm: str) -> str:
    return ALGORITHM_ALIASES.get(algorithm, algorithm)


def ensure_matching_profiles(run_dirs: dict[str, Path]) -> dict:
    profiles = {algorithm: load_run_profile(run_dir) for algorithm, run_dir in run_dirs.items()}
    anchor_algorithm = next(iter(run_dirs))
    anchor = profiles[anchor_algorithm]
    mismatches: list[str] = []
    for algorithm, profile in profiles.items():
        for key in ("num_users", "num_edges", "episodes", "max_delay"):
            if profile[key] != anchor[key]:
                mismatches.append(
                    f"{algorithm}.{key}={profile[key]} (expected {anchor[key]} from {anchor_algorithm})"
                )
    if mismatches:
        raise ValueError(
            "Selected runs are from different experiment environments: "
            + "; ".join(mismatches)
        )
    return anchor


def latest_run_dir(algorithm: str) -> Path:
    base_dir = EXPERIMENT_ROOT / algorithm
    if not base_dir.exists():
        raise FileNotFoundError(f"No result directory found for {algorithm}: {base_dir}")

    run_dirs = sorted(path for path in base_dir.iterdir() if path.is_dir() and path.name.startswith("run_"))
    if not run_dirs:
        raise FileNotFoundError(f"No run directories found for {algorithm}: {base_dir}")
    for run_dir in reversed(run_dirs):
        if has_required_metrics(run_dir):
            return run_dir
    raise FileNotFoundError(f"No completed run directories found for {algorithm}: {base_dir}")


def resolve_run_dir(algorithm: str, requested: str | None) -> Path:
    if requested:
        run_dir = Path(requested).expanduser().resolve()
        if not run_dir.exists():
            raise FileNotFoundError(f"Run directory does not exist: {run_dir}")
        return run_dir
    return latest_run_dir(algorithm)


def read_metric_file(path: Path) -> list[float]:
    values: list[float] = []
    with open(path) as f:
        for raw_line in f:
            line = raw_line.strip()
            if line:
                values.append(float(line))
    return values


def metric_base_dir(run_dir: Path) -> Path:
    required = ("QoE.txt", "Delay.txt", "Energy.txt", "Drop.txt")
    if all((run_dir / filename).exists() for filename in required):
        return run_dir
    comparison_dir = run_dir / "comparison_ready"
    if comparison_dir.exists():
        return comparison_dir
    compat_dir = run_dir / "qeco_compatible"
    if compat_dir.exists():
        return compat_dir
    return run_dir


def has_required_metrics(run_dir: Path) -> bool:
    base = metric_base_dir(run_dir)
    required = ("QoE.txt", "Delay.txt", "Energy.txt", "Drop.txt")
    return all((base / filename).exists() for filename in required)


def metric_series(run_dir: Path) -> dict[str, list[float]]:
    base = metric_base_dir(run_dir)
    return {
        "qoe": read_metric_file(base / "QoE.txt"),
        "delay": read_metric_file(base / "Delay.txt"),
        "energy": read_metric_file(base / "Energy.txt"),
        "drop": read_metric_file(base / "Drop.txt"),
    }


def raw_metric_series(run_dir: Path) -> dict[str, list[float]]:
    required = ("QoE.txt", "Delay.txt", "Energy.txt", "Drop.txt")
    if not all((run_dir / filename).exists() for filename in required):
        return metric_series(run_dir)
    return {
        "qoe": read_metric_file(run_dir / "QoE.txt"),
        "delay": read_metric_file(run_dir / "Delay.txt"),
        "energy": read_metric_file(run_dir / "Energy.txt"),
        "drop": read_metric_file(run_dir / "Drop.txt"),
    }


def episode_runtime_series(run_dir: Path) -> list[float]:
    runtime_path = run_dir / "EpisodeRuntime.txt"
    if not runtime_path.exists():
        return []
    return read_metric_file(runtime_path)


def aligned_metric_values(all_metrics: dict[str, dict[str, list[float]]], metric: str) -> dict[str, list[float]]:
    limit = min(len(series[metric]) for series in all_metrics.values())
    return {algorithm: all_metrics[algorithm][metric][:limit] for algorithm in all_metrics}


def moving_average(values: list[float], window: int) -> list[float]:
    if window <= 1 or len(values) <= 1:
        return list(values)
    if window > len(values):
        window = len(values)

    averaged: list[float] = []
    running_sum = 0.0
    for index, value in enumerate(values):
        running_sum += value
        if index >= window:
            running_sum -= values[index - window]
        current_window = min(index + 1, window)
        averaged.append(running_sum / current_window)
    return averaged


def summary_stats(values: list[float]) -> dict[str, float]:
    if not values:
        return {"mean": 0.0, "final": 0.0}
    return {"mean": mean(values), "final": values[-1]}


def tail_mean(values: list[float], ratio: float = 0.1) -> float:
    if not values:
        return 0.0
    tail_count = max(1, int(len(values) * ratio))
    return mean(values[-tail_count:])


def trimmed_values(values: list[float], trim_ratio: float = 0.1) -> list[float]:
    if not values:
        return []
    ordered = sorted(values)
    trim_count = int(len(ordered) * trim_ratio)
    if trim_count * 2 >= len(ordered):
        return ordered
    return ordered[trim_count: len(ordered) - trim_count]


def runtime_stats(values: list[float], trim_ratio: float = 0.1) -> dict[str, float]:
    if not values:
        return {
            "count": 0,
            "trim_ratio": trim_ratio,
            "median": 0.0,
            "trimmed_mean": 0.0,
            "trimmed_median": 0.0,
        }
    trimmed = trimmed_values(values, trim_ratio)
    return {
        "count": len(values),
        "trim_ratio": trim_ratio,
        "median": median(values),
        "trimmed_mean": mean(trimmed),
        "trimmed_median": median(trimmed),
    }


def write_summary(output_dir: Path, payload: dict) -> None:
    with open(output_dir / "comparison_summary.json", "w") as f:
        json.dump(payload, f, indent=2)


def write_finals_table(
    output_dir: Path,
    final_metrics: dict[str, dict[str, list[float]]],
    runtime_data: dict[str, list[float]],
    algorithms: tuple[str, ...],
) -> dict:
    payload = {
        algorithm: {
            "label": LABELS[algorithm],
            "final_source": "raw_episode_series",
            "final_window_ratio": 0.1,
            "final_window_count": max(1, int(len(final_metrics[algorithm]["qoe"]) * 0.1)),
            "qoe_final": tail_mean(final_metrics[algorithm]["qoe"], 0.1),
            "delay_final": tail_mean(final_metrics[algorithm]["delay"], 0.1),
            "energy_final": tail_mean(final_metrics[algorithm]["energy"], 0.1),
            "drop_final": tail_mean(final_metrics[algorithm]["drop"], 0.1),
            "runtime_trimmed_median": runtime_stats(runtime_data[algorithm])["trimmed_median"],
        }
        for algorithm in algorithms
    }
    with open(output_dir / "comparison_finals.json", "w") as f:
        json.dump(payload, f, indent=2)

    csv_lines = ["algorithm,label,qoe_final,delay_final,energy_final,drop_final,runtime_trimmed_median"]
    for algorithm in algorithms:
        row = payload[algorithm]
        csv_lines.append(
            ",".join(
                [
                    algorithm,
                    row["label"],
                    f"{row['qoe_final']:.6f}",
                    f"{row['delay_final']:.6f}",
                    f"{row['energy_final']:.6f}",
                    f"{row['drop_final']:.6f}",
                    f"{row['runtime_trimmed_median']:.6f}",
                ]
            )
        )
    with open(output_dir / "comparison_finals.csv", "w") as f:
        f.write("\n".join(csv_lines) + "\n")
    return payload


def render_charts(
    all_metrics: dict[str, dict[str, list[float]]],
    output_dir: Path,
    smoothing_window: int,
    algorithms: tuple[str, ...],
) -> int:
    import matplotlib.pyplot as plt

    configure_plot_fonts(plt)
    aligned = {
        metric: aligned_metric_values(all_metrics, metric)
        for metric in ("qoe", "delay", "energy", "drop")
    }
    num_points = len(next(iter(aligned["qoe"].values())))
    x_axis = list(range(1, num_points + 1))
    metric_labels = {
        "qoe": "QoE",
        "delay": "Delay",
        "energy": "Energy",
        "drop": "Drop",
    }

    fig, axs = plt.subplots(4, 1, figsize=(12, 22))
    for ax, metric in zip(axs, ("qoe", "delay", "energy", "drop")):
        for algorithm in algorithms:
            ax.plot(
                x_axis,
                aligned[metric][algorithm],
                color=COLORS[algorithm],
                label=LABELS[algorithm],
                linewidth=1.8,
            )
        ax.set_title(f"{metric_labels[metric]} Comparison")
        ax.set_xlabel("Aligned Step")
        ax.set_ylabel(metric_labels[metric])
        ax.grid(True, linestyle="--", alpha=0.5)
        ax.legend(fontsize=LEGEND_FONT_SIZE)
        style_axis_text(ax)

    plt.tight_layout()
    fig.savefig(output_dir / "comparison_timeseries.png", dpi=120, bbox_inches="tight")
    plt.close(fig)

    fig, axs = plt.subplots(4, 1, figsize=(12, 22))
    for ax, metric in zip(axs, ("qoe", "delay", "energy", "drop")):
        for algorithm in algorithms:
            raw_values = aligned[metric][algorithm]
            smooth_values = moving_average(raw_values, smoothing_window)
            ax.plot(
                x_axis,
                raw_values,
                color=COLORS[algorithm],
                linewidth=1.0,
                alpha=0.22,
            )
            ax.plot(
                x_axis,
                smooth_values,
                color=COLORS[algorithm],
                label=LABELS[algorithm],
                linewidth=2.0,
            )
        ax.set_title(
            f"{metric_labels[metric]} Comparison (Smoothed: Moving Average, window={smoothing_window})"
        )
        ax.set_xlabel("Aligned Step")
        ax.set_ylabel(metric_labels[metric])
        ax.grid(True, linestyle="--", alpha=0.5)
        ax.legend(fontsize=LEGEND_FONT_SIZE)
        style_axis_text(ax)
        ax.text(
            0.99,
            0.02,
            f"Smoothing: moving average (window={smoothing_window})",
            transform=ax.transAxes,
            ha="right",
            va="bottom",
            fontsize=NOTE_FONT_SIZE,
            color="#444444",
            bbox={"boxstyle": "round,pad=0.25", "facecolor": "white", "alpha": 0.7, "edgecolor": "#cccccc"},
        )

    plt.tight_layout()
    fig.savefig(output_dir / "comparison_timeseries_smoothed.png", dpi=120, bbox_inches="tight")
    plt.close(fig)

    fig, axs = plt.subplots(2, 2, figsize=(13, 8))
    for ax, metric in zip(axs.flat, ("qoe", "delay", "energy", "drop")):
        averages = [mean(aligned[metric][algorithm]) for algorithm in algorithms]
        bars = ax.bar(
            [LABELS[algorithm] for algorithm in algorithms],
            averages,
            color=[COLORS[algorithm] for algorithm in algorithms],
            width=0.6,
        )
        annotate_bars(ax, bars)
        ax.set_title(f"Average {metric_labels[metric]}")
        ax.grid(True, axis="y", linestyle="--", alpha=0.4)
        style_axis_text(ax, x_label_rotation=20)

    plt.tight_layout()
    fig.savefig(output_dir / "comparison_averages.png", dpi=120, bbox_inches="tight")
    plt.close(fig)
    return num_points


def render_finals_chart(final_metrics: dict[str, dict[str, list[float]]], output_dir: Path, algorithms: tuple[str, ...]) -> None:
    import matplotlib.pyplot as plt

    configure_plot_fonts(plt)
    fig, axs = plt.subplots(2, 2, figsize=(13, 8))
    for ax, metric in zip(axs.flat, ("qoe", "delay", "energy", "drop")):
        finals = [tail_mean(final_metrics[algorithm][metric], 0.1) for algorithm in algorithms]
        bars = ax.bar(
            [LABELS[algorithm] for algorithm in algorithms],
            finals,
            color=[COLORS[algorithm] for algorithm in algorithms],
            width=0.6,
        )
        annotate_bars(ax, bars)
        ax.set_title(f"Raw Episode Final 10% Mean {metric.capitalize()}")
        ax.grid(True, axis="y", linestyle="--", alpha=0.4)
        style_axis_text(ax, x_label_rotation=20)

    plt.tight_layout()
    fig.savefig(output_dir / "comparison_finals.png", dpi=120, bbox_inches="tight")
    plt.close(fig)


def render_runtime_chart(runtime_data: dict[str, list[float]], output_dir: Path, algorithms: tuple[str, ...]) -> None:
    import matplotlib.pyplot as plt

    configure_plot_fonts(plt)
    trimmed_medians = [runtime_stats(runtime_data[algorithm])["trimmed_median"] for algorithm in algorithms]
    fig, ax = plt.subplots(figsize=(10, 5))
    bars = ax.bar(
        [LABELS[algorithm] for algorithm in algorithms],
        trimmed_medians,
        color=[COLORS[algorithm] for algorithm in algorithms],
        width=0.6,
    )
    annotate_bars(ax, bars)
    ax.set_title("Trimmed Median Episode Runtime")
    ax.set_ylabel("Seconds per Episode")
    ax.grid(True, axis="y", linestyle="--", alpha=0.4)
    style_axis_text(ax, x_label_rotation=20)
    plt.tight_layout()
    fig.savefig(output_dir / "comparison_runtime.png", dpi=120, bbox_inches="tight")
    plt.close(fig)


def main() -> int:
    parser = argparse.ArgumentParser(description="Create multi-algorithm comparison charts.")
    parser.add_argument(
        "--algorithms",
        nargs="+",
        choices=AVAILABLE_ALGORITHMS + tuple(ALGORITHM_ALIASES),
        default=list(DEFAULT_ALGORITHMS),
        help="Algorithms to include in the comparison. Defaults to the main comparison set.",
    )
    parser.add_argument("--droo-run", help="Optional explicit DROO run directory.")
    parser.add_argument("--qeco-run", help="Optional explicit QECO run directory.")
    parser.add_argument("--cd-run", help="Optional explicit CD run directory.")
    parser.add_argument("--qeco-adapt-run", help="Optional explicit QECO-ADAPT run directory.")
    parser.add_argument("--twdqn-run", help="Optional explicit Tang&Wong DQN run directory.")
    parser.add_argument("--hybrid-run", help="Optional explicit HYBRID-QECO run directory.")
    parser.add_argument(
        "--output-dir",
        help="Optional output directory for comparison charts. Defaults to a folder under experiment_results/comparisons.",
    )
    parser.add_argument(
        "--smoothing-window",
        type=int,
        default=25,
        help="Moving-average window used only for the smoothed timeseries chart.",
    )
    args = parser.parse_args()
    algorithms = tuple(normalize_algorithm_name(algorithm) for algorithm in args.algorithms)

    requested_runs = {
        "droo": args.droo_run,
        "qeco": args.qeco_run,
        "cd": args.cd_run,
        "qeco_adapt": args.qeco_adapt_run,
        "twdqn": args.twdqn_run,
    }
    run_dirs = {algorithm: resolve_run_dir(algorithm, requested_runs[algorithm]) for algorithm in algorithms}
    scenario_profile = ensure_matching_profiles(run_dirs)

    if args.output_dir:
        output_dir = Path(args.output_dir).expanduser().resolve()
        output_dir.mkdir(parents=True, exist_ok=True)
    else:
        output_dir = (
            EXPERIMENT_ROOT
            / "comparisons"
            / default_output_name(algorithms, scenario_profile)
        )
        output_dir.mkdir(parents=True, exist_ok=True)

    all_metrics = {algorithm: metric_series(run_dirs[algorithm]) for algorithm in algorithms}
    final_metrics = {algorithm: raw_metric_series(run_dirs[algorithm]) for algorithm in algorithms}
    runtime_data = {algorithm: episode_runtime_series(run_dirs[algorithm]) for algorithm in algorithms}
    episode_points = render_charts(all_metrics, output_dir, args.smoothing_window, algorithms)
    render_finals_chart(final_metrics, output_dir, algorithms)
    render_runtime_chart(runtime_data, output_dir, algorithms)
    finals_table = write_finals_table(output_dir, final_metrics, runtime_data, algorithms)

    summary = {
        "runs": {algorithm: str(run_dirs[algorithm]) for algorithm in algorithms},
        "output_dir": str(output_dir),
        "scenario_title": scenario_title_from_profile(scenario_profile),
        "scenario_profile": scenario_profile,
        "algorithms": list(algorithms),
        "episode_points": episode_points,
        "finals_source": {
            "series": "raw episode QoE/Delay/Energy/Drop files in each run directory",
            "window_ratio": 0.1,
            "note": "Time-series, averages, and finals use raw episode series when available; compatibility output is used only as a fallback.",
        },
        "metrics": {
            metric: {
                algorithm: summary_stats(aligned_metric_values(all_metrics, metric)[algorithm])
                for algorithm in algorithms
            }
            for metric in ("qoe", "delay", "energy", "drop")
        },
        "runtime": {
            algorithm: runtime_stats(runtime_data[algorithm])
            for algorithm in algorithms
        },
        "finals_only": finals_table,
        "visualization": {
            "smoothing_method": "moving_average",
            "smoothing_window": args.smoothing_window,
            "smoothed_chart": str(output_dir / "comparison_timeseries_smoothed.png"),
        },
    }
    write_summary(output_dir, summary)

    for algorithm in algorithms:
        print(f"{LABELS[algorithm]} run: {run_dirs[algorithm]}")
    print(f"Comparison output: {output_dir}")
    print("Created:")
    print(f"- {output_dir / 'comparison_timeseries.png'}")
    print(f"- {output_dir / 'comparison_timeseries_smoothed.png'}")
    print(f"- {output_dir / 'comparison_averages.png'}")
    print(f"- {output_dir / 'comparison_finals.png'}")
    print(f"- {output_dir / 'comparison_runtime.png'}")
    print(f"- {output_dir / 'comparison_summary.json'}")
    print(f"- {output_dir / 'comparison_finals.json'}")
    print(f"- {output_dir / 'comparison_finals.csv'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
