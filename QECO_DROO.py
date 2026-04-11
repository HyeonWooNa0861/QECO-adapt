#!/usr/bin/env python3
"""Helpers for reproducing DROO and QECO experiments.

This script does not assume the repositories already exist, and it defaults to
"plan" mode so you can inspect commands before executing them.
"""

from __future__ import annotations

import argparse
import shlex
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List

from common_experiment import SharedExperiment


SCRIPT_DIR = Path(__file__).resolve().parent
DEFAULT_BASE_DIR = SCRIPT_DIR
ALGORITHM_ALIASES = {"qeco-adapt": "qeco_adapt"}


def normalize_algorithm_name(algorithm: str) -> str:
    return ALGORITHM_ALIASES.get(algorithm, algorithm)


def display_algorithm_name(algorithm: str) -> str:
    normalized = normalize_algorithm_name(algorithm)
    if normalized == "qeco_adapt":
        return "QECO-ADAPT"
    return normalized.upper()


@dataclass(frozen=True)
class ProjectConfig:
    name: str
    git_url: str
    repo_dir: Path
    env_dir: Path
    install_packages: List[str]
    notes: List[str]


PROJECTS = {
    "droo": ProjectConfig(
        name="DROO",
        git_url="https://github.com/revenol/DROO.git",
        repo_dir=DEFAULT_BASE_DIR / "DROO",
        env_dir=DEFAULT_BASE_DIR / "env_droo",
        install_packages=["numpy", "scipy", "tensorflow==2.8.0"],
        notes=[
            "Everything is stored under the Alpha_1 directory.",
            "TensorFlow 2.x baseline is selected by default.",
            "You can switch to PyTorch with --framework pytorch when running.",
            "Main entry points are main.py, mainTF2.py, and mainPyTorch.py.",
        ],
    ),
    "qeco": ProjectConfig(
        name="QECO",
        git_url="https://github.com/ImanRHT/QECO.git",
        repo_dir=DEFAULT_BASE_DIR / "QECO",
        env_dir=DEFAULT_BASE_DIR / "env_qeco",
        install_packages=[
            "numpy>=1.17.0",
            "scipy",
            "matplotlib>=3.0.0",
            "tensorflow==2.8.0",
            "protobuf<3.21",
        ],
        notes=[
            "Everything is stored under the Alpha_1 directory.",
            "QECO uses TensorFlow 2.8.0 in the published repository.",
            "Hybrid-CD guidance also requires scipy inside the QECO environment.",
            "Pin protobuf below 3.21 to avoid TensorFlow 2.8 import errors.",
            "Check Config.py before training to align the scenario with DROO.",
            "The standard entry point is main.py.",
        ],
    ),
}


DROO_FRAMEWORKS = {
    "tensorflow1": "main.py",
    "tensorflow2": "mainTF2.py",
    "pytorch": "mainPyTorch.py",
}


DROO_FRAMEWORK_PACKAGES = {
    "tensorflow1": ["numpy", "scipy", "tensorflow==1.15.0"],
    "tensorflow2": ["numpy", "scipy", "tensorflow==2.8.0"],
    "pytorch": ["numpy", "scipy", "torch"],
}


def shell_join(parts: Iterable[str]) -> str:
    return " ".join(shlex.quote(part) for part in parts)


def run_shell(command: List[str], execute: bool, cwd: Path | None = None) -> int:
    text = shell_join(command)
    location = f"  [cwd: {cwd}]" if cwd else ""
    print(f"$ {text}{location}")
    if not execute:
        return 0
    completed = subprocess.run(command, cwd=str(cwd) if cwd else None, check=False)
    return completed.returncode


def venv_python(env_dir: Path) -> Path:
    return env_dir / "bin" / "python"


def venv_pip(env_dir: Path) -> Path:
    return env_dir / "bin" / "pip"


def ensure_known_project(project: str) -> ProjectConfig:
    try:
        return PROJECTS[project]
    except KeyError as exc:
        raise SystemExit(f"Unknown project: {project}") from exc


def create_env_commands(config: ProjectConfig, python_bin: str) -> List[List[str]]:
    return [
        [python_bin, "-m", "venv", str(config.env_dir)],
        [str(venv_pip(config.env_dir)), "install", "--upgrade", "pip"],
        [str(venv_pip(config.env_dir)), "install", *config.install_packages],
    ]


def selected_packages(config: ProjectConfig, framework: str | None = None) -> List[str]:
    if config.name == "DROO" and framework:
        return DROO_FRAMEWORK_PACKAGES[framework]
    return config.install_packages


def clone_command(config: ProjectConfig) -> List[str]:
    return ["git", "clone", config.git_url, str(config.repo_dir)]


def repo_status_lines(config: ProjectConfig) -> List[str]:
    lines = [
        f"- repo_dir: {config.repo_dir}",
        f"- env_dir: {config.env_dir}",
        f"- repo_exists: {'yes' if config.repo_dir.exists() else 'no'}",
        f"- env_exists: {'yes' if config.env_dir.exists() else 'no'}",
    ]
    return lines


def droo_run_file(repo_dir: Path, framework: str) -> Path:
    filename = DROO_FRAMEWORKS[framework]
    return repo_dir / filename


def print_project_info(config: ProjectConfig, framework: str | None = None) -> None:
    print(f"[{config.name}]")
    print(f"- git: {config.git_url}")
    for line in repo_status_lines(config):
        print(line)
    print("- common_shared_experiment:")
    print(f"  - users: {SharedExperiment.NUM_USERS}")
    print(f"  - edges: {SharedExperiment.NUM_EDGES}")
    print(f"  - components: {SharedExperiment.NUM_COMPONENTS}")
    print(f"  - max_delay: {SharedExperiment.MAX_DELAY}")
    print(f"  - seed: {SharedExperiment.RANDOM_SEED}")
    print(f"  - qeco_episodes: {SharedExperiment.QECO_EPISODES}")
    print(f"  - qeco_time_slots: {SharedExperiment.QECO_TIME_SLOTS}")
    print(f"  - qeco_arrival_base_profile: {SharedExperiment.QECO_ARRIVAL_BASE_PROFILE}")
    print(f"  - qeco_user_activity_range: ({SharedExperiment.QECO_USER_ACTIVITY_MIN}, {SharedExperiment.QECO_USER_ACTIVITY_MAX})")
    print(f"  - comparison_points: {SharedExperiment.COMPARISON_POINTS}")
    print(f"  - hybrid_alpha: {SharedExperiment.HYBRID_ALPHA}")
    print(f"  - hybrid_beta: {SharedExperiment.HYBRID_BETA}")
    print(f"  - hybrid_epsilon: {SharedExperiment.HYBRID_EPSILON}")
    print(f"  - hybrid_cd_lambda: {SharedExperiment.HYBRID_CD_LAMBDA}")
    print(f"  - qeco_adapt_base_energy_weight: {SharedExperiment.QECO_ADAPT_BASE_ENERGY_WEIGHT}")
    print(f"  - qeco_adapt_user_exponent: {SharedExperiment.QECO_ADAPT_USER_EXPONENT}")
    print(f"  - qeco_adapt_load_scale: {SharedExperiment.QECO_ADAPT_LOAD_SCALE}")
    print(f"  - qeco_adapt_min_energy_state: {SharedExperiment.QECO_ADAPT_MIN_ENERGY_STATE}")
    print(f"  - qeco_adapt_edge_backlog_threshold: {SharedExperiment.QECO_ADAPT_EDGE_BACKLOG_THRESHOLD}")
    print(f"  - qeco_adapt_size_threshold: {SharedExperiment.QECO_ADAPT_SIZE_THRESHOLD}")
    print("- original_project_settings:")
    if config.name == "DROO":
        print(f"  - droo_channel_frames: {SharedExperiment.DROO_CHANNEL_FRAMES}")
        print(f"  - droo_memory_size: {SharedExperiment.DROO_MEMORY_SIZE}")
        print(f"  - droo_delta: {SharedExperiment.DROO_DELTA}")
        print(f"  - droo_decoder_mode: {SharedExperiment.DROO_DECODER_MODE}")
    else:
        print(f"  - qeco_episodes: {SharedExperiment.QECO_EPISODES}")
        print(f"  - qeco_time_slots: {SharedExperiment.QECO_TIME_SLOTS}")
        print(f"  - qeco_task_arrive_prob: {SharedExperiment.QECO_TASK_ARRIVE_PROB}")
    print("- packages:")
    for package in selected_packages(config, framework):
        print(f"  - {package}")
    print("- notes:")
    for note in config.notes:
        print(f"  - {note}")


def handle_info(args: argparse.Namespace) -> int:
    if args.project == "all":
        for index, config in enumerate(PROJECTS.values()):
            if index:
                print()
            print_project_info(config)
        return 0

    print_project_info(ensure_known_project(args.project))
    return 0


def handle_clone(args: argparse.Namespace) -> int:
    config = ensure_known_project(args.project)
    config.repo_dir.parent.mkdir(parents=True, exist_ok=True)
    if config.repo_dir.exists():
        print(f"{config.name} repository already exists: {config.repo_dir}")
        return 0
    return run_shell(clone_command(config), execute=args.execute)


def handle_setup(args: argparse.Namespace) -> int:
    config = ensure_known_project(args.project)
    framework = args.framework if args.project == "droo" else None
    print_project_info(config, framework=framework)
    print()
    print("Environment setup commands:")
    packages = selected_packages(config, framework)
    exit_code = 0
    commands = [
        [args.python_bin, "-m", "venv", str(config.env_dir)],
        [str(venv_pip(config.env_dir)), "install", "--upgrade", "pip"],
        [str(venv_pip(config.env_dir)), "install", *packages],
    ]
    for command in commands:
        exit_code = run_shell(command, execute=args.execute)
        if exit_code != 0:
            return exit_code
    return exit_code


def handle_run(args: argparse.Namespace) -> int:
    config = ensure_known_project(args.project)
    if args.project == "qeco":
        target = config.repo_dir / "main.py"
        framework_label = "tensorflow2"
    else:
        framework_label = args.framework
        target = droo_run_file(config.repo_dir, args.framework)

    print_project_info(config, framework=framework_label if args.project == "droo" else None)
    print(f"- selected_framework: {framework_label}")
    print(f"- entrypoint: {target}")

    if not config.repo_dir.exists():
        print(f"\nRepository is missing. Clone first with:")
        print(f"$ {shell_join(clone_command(config))}")
        return 1

    if not target.exists():
        print(f"\nEntrypoint not found: {target}")
        if args.project == "droo":
            print("Available DROO framework options: tensorflow1, tensorflow2, pytorch")
        return 1

    python_bin = venv_python(config.env_dir)
    if not python_bin.exists():
        print(f"\nVirtual environment is missing. Create it first with:")
        print(f"$ {shell_join([args.python_bin, '-m', 'venv', str(config.env_dir)])}")
        return 1

    return run_shell([str(python_bin), str(target)], execute=args.execute, cwd=config.repo_dir)


def handle_compare(args: argparse.Namespace) -> int:
    compare_script = SCRIPT_DIR / "compare_results.py"
    python_bin = venv_python(PROJECTS["qeco"].env_dir)
    if not python_bin.exists():
        print("QECO virtual environment is missing. Create it first with:")
        print(f"$ {shell_join([args.python_bin, '-m', 'venv', str(PROJECTS['qeco'].env_dir)])}")
        return 1

    command = [str(python_bin), str(compare_script)]
    if args.droo_run:
        command.extend(["--droo-run", args.droo_run])
    if args.qeco_run:
        command.extend(["--qeco-run", args.qeco_run])
    if getattr(args, "cd_run", None):
        command.extend(["--cd-run", args.cd_run])
    if args.qeco_adapt_run:
        command.extend(["--qeco-adapt-run", args.qeco_adapt_run])
    if args.twdqn_run:
        command.extend(["--twdqn-run", args.twdqn_run])
    if getattr(args, "algorithms", None):
        command.extend(["--algorithms", *args.algorithms])
    if args.hybrid_run:
        command.extend(["--hybrid-run", args.hybrid_run])
    if args.output_dir:
        command.extend(["--output-dir", args.output_dir])
    if args.smoothing_window:
        command.extend(["--smoothing-window", str(args.smoothing_window)])
    return run_shell(command, execute=args.execute, cwd=SCRIPT_DIR)


def handle_compare_cqa(args: argparse.Namespace) -> int:
    delegated_args = argparse.Namespace(
        droo_run=None,
        qeco_run=args.qeco_run,
        cd_run=args.cd_run,
        qeco_adapt_run=args.qeco_adapt_run,
        twdqn_run=None,
        hybrid_run=None,
        algorithms=["cd", "qeco", "qeco_adapt"],
        output_dir=args.output_dir,
        smoothing_window=args.smoothing_window,
        python_bin=args.python_bin,
        execute=args.execute,
    )
    return handle_compare(delegated_args)


def handle_common_run(args: argparse.Namespace) -> int:
    project_key = normalize_algorithm_name(args.algorithm)
    env_key = "qeco" if project_key in {"qeco", "qeco_adapt", "twdqn", "hybrid"} else "droo"
    config = PROJECTS[env_key]
    python_bin = venv_python(config.env_dir)
    if not python_bin.exists():
        print(f"{config.name} virtual environment is missing. Create it first with:")
        print(f"$ {shell_join([args.python_bin, '-m', 'venv', str(config.env_dir)])}")
        return 1

    target = SCRIPT_DIR / "common_eval.py"
    print(f"[COMMON {display_algorithm_name(project_key)}]")
    print(f"- shared_users: {SharedExperiment.NUM_USERS}")
    print(f"- shared_edges: {SharedExperiment.NUM_EDGES}")
    print(f"- shared_components: {SharedExperiment.NUM_COMPONENTS}")
    print(f"- shared_seed: {SharedExperiment.RANDOM_SEED}")
    print(f"- qeco_episodes: {SharedExperiment.QECO_EPISODES}")
    print(f"- comparison_points: {SharedExperiment.COMPARISON_POINTS}")
    if project_key == "hybrid":
        print(f"- reward: hybrid_qeco_reward")
        print(f"- alpha: {args.alpha}")
        print(f"- beta: {args.beta}")
        print(f"- epsilon: {args.epsilon}")
        print(f"- cd_lambda: {SharedExperiment.HYBRID_CD_LAMBDA}")
        if args.tag:
            print(f"- tag: {args.tag}")
    elif project_key == "qeco_adapt":
        print(f"- reward: qeco_adapt_energy_aware_adaptive_reward")
        base_profile_mean = sum(SharedExperiment.QECO_ARRIVAL_BASE_PROFILE) / len(SharedExperiment.QECO_ARRIVAL_BASE_PROFILE)
        user_activity_mean = (SharedExperiment.QECO_USER_ACTIVITY_MIN + SharedExperiment.QECO_USER_ACTIVITY_MAX) / 2.0
        effective_load = SharedExperiment.NUM_USERS * base_profile_mean * user_activity_mean / max(SharedExperiment.NUM_EDGES, 1)
        actual_load_scale = SharedExperiment.NUM_EDGES * SharedExperiment.QECO_ADAPT_LOAD_SCALE
        print(f"- effective_load_formula_actual: users * mean(base_profile) * mean(user_activity) / edges")
        print(f"- effective_load: {effective_load:.4f}")
        print(f"- load_scale_base: {SharedExperiment.QECO_ADAPT_LOAD_SCALE}")
        print(f"- load_scale_actual: {actual_load_scale:.4f}")
        print(f"- load_scale_rule: edges * load_scale_base")
        print(f"- gating_formula: effective_load / (effective_load + edges * load_scale_base)")
        print(f"- energy_weight_formula: base * (1 + gating_strength)^exponent")
        print(f"- base_energy_weight: {SharedExperiment.QECO_ADAPT_BASE_ENERGY_WEIGHT}")
        print(f"- user_exponent: {SharedExperiment.QECO_ADAPT_USER_EXPONENT}")
        print(f"- min_energy_state: {SharedExperiment.QECO_ADAPT_MIN_ENERGY_STATE}")
        print(f"- edge_backlog_threshold: {SharedExperiment.QECO_ADAPT_EDGE_BACKLOG_THRESHOLD}")
        print(f"- size_threshold: {SharedExperiment.QECO_ADAPT_SIZE_THRESHOLD}")
    command_algorithm = "qeco-adapt" if project_key == "qeco_adapt" else project_key
    command = [str(python_bin), str(target), command_algorithm]
    if project_key == "hybrid":
        command.extend(["--alpha", str(args.alpha), "--beta", str(args.beta), "--epsilon", str(args.epsilon)])
        if args.tag:
            command.extend(["--tag", args.tag])
    return run_shell(command, execute=args.execute, cwd=SCRIPT_DIR)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Prepare and run separated environments for DROO and QECO."
    )
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Actually execute commands. Without this flag, commands are only printed.",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    info_parser = subparsers.add_parser("info", help="Show project configuration.")
    info_parser.add_argument("project", choices=["droo", "qeco", "all"])
    info_parser.set_defaults(handler=handle_info)

    clone_parser = subparsers.add_parser("clone", help="Show or run repository clone command.")
    clone_parser.add_argument("project", choices=["droo", "qeco"])
    clone_parser.set_defaults(handler=handle_clone)

    setup_parser = subparsers.add_parser("setup", help="Create a venv and install packages.")
    setup_parser.add_argument("project", choices=["droo", "qeco"])
    setup_parser.add_argument(
        "--framework",
        choices=["tensorflow1", "tensorflow2", "pytorch"],
        default="tensorflow2",
        help="Only used for DROO.",
    )
    setup_parser.add_argument(
        "--python-bin",
        default=sys.executable or "python3",
        help="Python interpreter used to create the venv.",
    )
    setup_parser.set_defaults(handler=handle_setup)

    run_parser = subparsers.add_parser("run", help="Run the selected project entry point.")
    run_parser.add_argument("project", choices=["droo", "qeco"])
    run_parser.add_argument(
        "--framework",
        choices=["tensorflow1", "tensorflow2", "pytorch"],
        default="tensorflow2",
        help="Only used for DROO.",
    )
    run_parser.add_argument(
        "--python-bin",
        default=sys.executable or "python3",
        help="Shown in guidance when the venv does not exist yet.",
    )
    run_parser.set_defaults(handler=handle_run)

    compare_parser = subparsers.add_parser(
        "compare", help="Create comparison charts from experiment_results."
    )
    compare_parser.add_argument("--droo-run", help="Optional explicit DROO run directory.")
    compare_parser.add_argument("--qeco-run", help="Optional explicit QECO run directory.")
    compare_parser.add_argument("--cd-run", help="Optional explicit CD run directory.")
    compare_parser.add_argument("--qeco-adapt-run", help="Optional explicit QECO-ADAPT run directory.")
    compare_parser.add_argument("--twdqn-run", help="Optional explicit Tang&Wong DQN run directory.")
    compare_parser.add_argument("--hybrid-run", help="Optional explicit HYBRID-QECO run directory.")
    compare_parser.add_argument(
        "--algorithms",
        nargs="+",
        choices=["droo", "qeco", "cd", "qeco_adapt", "qeco-adapt", "twdqn"],
        help="Optional algorithm subset to include in the comparison.",
    )
    compare_parser.add_argument("--output-dir", help="Optional output directory for comparison charts.")
    compare_parser.add_argument(
        "--smoothing-window",
        type=int,
        default=25,
        help="Moving-average window for the smoothed timeseries chart.",
    )
    compare_parser.add_argument(
        "--python-bin",
        default=sys.executable or "python3",
        help="Shown in guidance when the QECO venv does not exist yet.",
    )
    compare_parser.set_defaults(handler=handle_compare)

    compare_cqa_parser = subparsers.add_parser(
        "compare-cqa",
        help="Create comparison charts using only CD, QECO, and QECO-ADAPT.",
    )
    compare_cqa_parser.add_argument("--cd-run", help="Optional explicit CD run directory.")
    compare_cqa_parser.add_argument("--qeco-run", help="Optional explicit QECO run directory.")
    compare_cqa_parser.add_argument("--qeco-adapt-run", help="Optional explicit QECO-ADAPT run directory.")
    compare_cqa_parser.add_argument("--output-dir", help="Optional output directory for comparison charts.")
    compare_cqa_parser.add_argument(
        "--smoothing-window",
        type=int,
        default=25,
        help="Moving-average window for the smoothed timeseries chart.",
    )
    compare_cqa_parser.add_argument(
        "--python-bin",
        default=sys.executable or "python3",
        help="Shown in guidance when the QECO venv does not exist yet.",
    )
    compare_cqa_parser.set_defaults(handler=handle_compare_cqa)

    common_run_parser = subparsers.add_parser(
        "common-run",
        help="Run DROO, QECO, QECO-ADAPT, CD, Tang&Wong DQN, or HYBRID-QECO inside the shared common evaluation environment.",
    )
    common_run_parser.add_argument("algorithm", choices=["droo", "qeco", "qeco_adapt", "qeco-adapt", "cd", "twdqn", "hybrid"])
    common_run_parser.add_argument("--alpha", type=float, default=SharedExperiment.HYBRID_ALPHA)
    common_run_parser.add_argument("--beta", type=float, default=SharedExperiment.HYBRID_BETA)
    common_run_parser.add_argument("--epsilon", type=float, default=SharedExperiment.HYBRID_EPSILON)
    common_run_parser.add_argument("--tag", help="Optional label for hybrid-only studies.")
    common_run_parser.add_argument(
        "--python-bin",
        default=sys.executable or "python3",
        help="Shown in guidance when the required venv does not exist yet.",
    )
    common_run_parser.set_defaults(handler=handle_common_run)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return args.handler(args)


if __name__ == "__main__":
    raise SystemExit(main())
