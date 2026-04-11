from __future__ import annotations

import json
import random
import shutil
import time
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parent


class SharedExperiment:
    # Shared comparison settings
    NAME = "droo_qeco_common_setup"
    RANDOM_SEED = 42
    NUM_USERS = 10
    NUM_EDGES = 1
    NUM_COMPONENTS = 1
    MAX_DELAY = 10

    # QECO-specific settings kept in the common file so both algorithms are
    # launched from the same scenario definition.
    QECO_EPISODES = 400
    QECO_TIME_SLOTS = 100
    QECO_TASK_ARRIVE_PROB = 0.3
    QECO_ARRIVAL_BASE_PROFILE = (0.18, 0.30, 0.42, 0.24)
    QECO_USER_ACTIVITY_MIN = 0.7
    QECO_USER_ACTIVITY_MAX = 1.3
    COMPARISON_POINTS = QECO_EPISODES
    HYBRID_ALPHA = 0.15
    HYBRID_BETA = 0.65
    HYBRID_EPSILON = 0.25
    HYBRID_CD_LAMBDA = 0.08
    HYBRID_QOE_MIN = -20.0
    HYBRID_THROUGHPUT_REF = 10.0
    QECO_ADAPT_BASE_ENERGY_WEIGHT = 1.20
    QECO_ADAPT_USER_EXPONENT = 0.35
    QECO_ADAPT_LOAD_SCALE = 10.0
    QECO_ADAPT_MIN_ENERGY_STATE = 0.35
    QECO_ADAPT_EDGE_BACKLOG_THRESHOLD = 12.0
    QECO_ADAPT_SIZE_THRESHOLD = 1.5

    # DROO-specific settings tied to the same shared comparison profile.
    DROO_CHANNEL_FRAMES = 30000
    DROO_MEMORY_SIZE = 1024
    DROO_DELTA = 32
    DROO_DECODER_MODE = "OP"

    RESULT_ROOT = ROOT_DIR / "experiment_results"

    @classmethod
    def as_dict(cls) -> dict:
        return {
            "name": cls.NAME,
            "random_seed": cls.RANDOM_SEED,
            "num_users": cls.NUM_USERS,
            "num_edges": cls.NUM_EDGES,
            "num_components": cls.NUM_COMPONENTS,
            "max_delay": cls.MAX_DELAY,
            "qeco": {
                "episodes": cls.QECO_EPISODES,
                "time_slots": cls.QECO_TIME_SLOTS,
                "task_arrive_prob": cls.QECO_TASK_ARRIVE_PROB,
                "arrival_profile": {
                    "base_profile": cls.QECO_ARRIVAL_BASE_PROFILE,
                    "user_activity_min": cls.QECO_USER_ACTIVITY_MIN,
                    "user_activity_max": cls.QECO_USER_ACTIVITY_MAX,
                },
                "hybrid_reward": {
                    "alpha": cls.HYBRID_ALPHA,
                    "beta": cls.HYBRID_BETA,
                    "epsilon": cls.HYBRID_EPSILON,
                    "cd_lambda": cls.HYBRID_CD_LAMBDA,
                    "qoe_min": cls.HYBRID_QOE_MIN,
                    "throughput_ref": cls.HYBRID_THROUGHPUT_REF,
                },
                "qeco_adapt": {
                    "base_energy_weight": cls.QECO_ADAPT_BASE_ENERGY_WEIGHT,
                    "user_exponent": cls.QECO_ADAPT_USER_EXPONENT,
                    "load_scale": cls.QECO_ADAPT_LOAD_SCALE,
                    "min_energy_state": cls.QECO_ADAPT_MIN_ENERGY_STATE,
                    "edge_backlog_threshold": cls.QECO_ADAPT_EDGE_BACKLOG_THRESHOLD,
                    "size_threshold": cls.QECO_ADAPT_SIZE_THRESHOLD,
                },
            },
            "comparison": {
                "points": cls.COMPARISON_POINTS,
                "axis_name": "episode",
            },
            "droo": {
                "channel_frames": cls.DROO_CHANNEL_FRAMES,
                "memory_size": cls.DROO_MEMORY_SIZE,
                "delta": cls.DROO_DELTA,
                "decoder_mode": cls.DROO_DECODER_MODE,
            },
        }


def apply_global_seed(seed: int, *, use_torch: bool = False, use_tensorflow: bool = False) -> None:
    random.seed(seed)
    try:
        import numpy as np

        np.random.seed(seed)
    except Exception:
        pass

    if use_torch:
        try:
            import torch

            torch.manual_seed(seed)
            if torch.cuda.is_available():
                torch.cuda.manual_seed_all(seed)
        except Exception:
            pass

    if use_tensorflow:
        try:
            import tensorflow.compat.v1 as tf

            tf.set_random_seed(seed)
        except Exception:
            pass


def create_run_dir(algorithm: str) -> Path:
    run_dir = SharedExperiment.RESULT_ROOT / algorithm / time.strftime("run_%Y%m%d_%H%M%S")
    run_dir.mkdir(parents=True, exist_ok=True)
    return run_dir


def create_named_run_dir(algorithm: str, name: str, *, overwrite: bool = False) -> Path:
    run_dir = SharedExperiment.RESULT_ROOT / algorithm / name
    if overwrite and run_dir.exists():
        shutil.rmtree(run_dir)
    run_dir.mkdir(parents=True, exist_ok=True)
    return run_dir


def write_experiment_snapshot(output_dir: Path, extra: dict | None = None) -> Path:
    snapshot = SharedExperiment.as_dict()
    if extra:
        snapshot["extra"] = extra

    target = output_dir / "experiment_config.json"
    with open(target, "w") as f:
        json.dump(snapshot, f, indent=2)
    return target


def resample_series(values: list[float], target_points: int) -> list[float]:
    if not values:
        return []
    if target_points <= 0:
        raise ValueError("target_points must be positive")

    if len(values) == target_points:
        return [float(value) for value in values]

    try:
        import numpy as np
    except Exception as exc:
        raise RuntimeError("numpy is required to resample series") from exc

    arr = np.asarray(values, dtype=float)
    if len(arr) > target_points:
        bins = np.array_split(arr, target_points)
        return [float(bin_values.mean()) for bin_values in bins]

    source_x = np.linspace(0.0, 1.0, len(arr))
    target_x = np.linspace(0.0, 1.0, target_points)
    return [float(value) for value in np.interp(target_x, source_x, arr)]
