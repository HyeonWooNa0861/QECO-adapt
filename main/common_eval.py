#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path


MAIN_DIR = Path(__file__).resolve().parent
ROOT_DIR = MAIN_DIR.parent
QECO_DIR = ROOT_DIR / "QECO"
DROO_DIR = ROOT_DIR / "DROO"

if str(MAIN_DIR) not in sys.path:
    sys.path.insert(0, str(MAIN_DIR))
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))
if str(QECO_DIR) not in sys.path:
    sys.path.insert(0, str(QECO_DIR))
if str(DROO_DIR) not in sys.path:
    sys.path.insert(0, str(DROO_DIR))

from baselines import CDBinaryOffloadPolicy, build_twdqn_agents
from common_experiment import (
    SharedExperiment,
    apply_global_seed,
    create_run_dir,
    resample_series,
    write_experiment_snapshot,
)


def save_series(values, path: Path) -> None:
    with open(path, "w") as f:
        for value in values:
            f.write(f"{value}\n")


def normalize(parameter, minimum, maximum):
    normalized_parameter = (parameter - minimum) / (maximum - minimum)
    return normalized_parameter


def qoe_function(delay, max_delay, unfinish_task, ue_energy_state, ue_comp_energy, ue_trans_energy, edge_comp_energy, ue_idle_energy):
    edge_energy = next((e for e in edge_comp_energy if e != 0), 0)
    idle_energy = next((e for e in ue_idle_energy if e != 0), 0)
    energy_cons = ue_comp_energy + ue_trans_energy
    scaled_energy = normalize(energy_cons, 0, 20) * 10
    cost = 2 * ((ue_energy_state * delay) + ((1 - ue_energy_state) * scaled_energy))
    reward = max_delay * 4
    if unfinish_task:
        return -cost
    return reward - cost


def qeco_adapt_reward_function(
    delay,
    max_delay,
    unfinish_task,
    ue_energy_state,
    ue_comp_energy,
    ue_trans_energy,
    edge_comp_energy,
    ue_idle_energy,
    energy_weight,
):
    energy_cons = ue_comp_energy + ue_trans_energy
    scaled_energy = normalize(energy_cons, 0, 20) * 10
    cost = 2 * ((ue_energy_state * delay) + ((1 - ue_energy_state) * (energy_weight * scaled_energy)))
    reward = max_delay * 4
    if unfinish_task:
        return -cost
    return reward - cost


def qeco_adapt_effective_load() -> float:
    base_profile_mean = sum(SharedExperiment.QECO_ARRIVAL_BASE_PROFILE) / len(SharedExperiment.QECO_ARRIVAL_BASE_PROFILE)
    user_activity_mean = (SharedExperiment.QECO_USER_ACTIVITY_MIN + SharedExperiment.QECO_USER_ACTIVITY_MAX) / 2.0
    return (
        max(SharedExperiment.NUM_USERS, 0)
        * base_profile_mean
        * user_activity_mean
        / max(SharedExperiment.NUM_EDGES, 1)
    )


def qeco_adapt_gating_strength() -> float:
    effective_load = qeco_adapt_effective_load()
    load_scale = max(SharedExperiment.NUM_EDGES * SharedExperiment.QECO_ADAPT_LOAD_SCALE, 1e-6)
    return effective_load / (effective_load + load_scale)


def qeco_adapt_energy_weight() -> float:
    scaled_user_factor = 1.0 + qeco_adapt_gating_strength()
    return SharedExperiment.QECO_ADAPT_BASE_ENERGY_WEIGHT * (
        scaled_user_factor ** SharedExperiment.QECO_ADAPT_USER_EXPONENT
    )


def apply_qeco_adapt_gating(observation, proposed_action: int) -> int:
    if proposed_action == 0:
        return 0
    gating_strength = qeco_adapt_gating_strength()
    task_size = float(observation[0])
    estimated_local_time = float(observation[1])
    estimated_tran_time = float(observation[2])
    edge_backlog = float(observation[3]) if len(observation) > 3 else 0.0
    energy_state = float(observation[-1])

    min_energy_state = SharedExperiment.QECO_ADAPT_MIN_ENERGY_STATE * gating_strength
    edge_backlog_threshold = SharedExperiment.QECO_ADAPT_EDGE_BACKLOG_THRESHOLD / max(gating_strength, 1e-6)
    size_threshold = SharedExperiment.QECO_ADAPT_SIZE_THRESHOLD * gating_strength

    if energy_state <= min_energy_state:
        return 0
    if edge_backlog >= edge_backlog_threshold:
        return 0
    if task_size <= size_threshold and estimated_tran_time >= 0:
        return 0
    if estimated_local_time >= 0 and estimated_tran_time >= 0 and estimated_local_time <= estimated_tran_time:
        return 0
    return proposed_action


def build_task_arrivals(env, config, np_module):
    bitarrive_size = np_module.random.uniform(env.min_arrive_size, env.max_arrive_size, size=[env.n_time, env.n_ue])
    time_profile = np_module.repeat(
        np_module.asarray(SharedExperiment.QECO_ARRIVAL_BASE_PROFILE, dtype=float),
        int(np_module.ceil(env.n_time / len(SharedExperiment.QECO_ARRIVAL_BASE_PROFILE))),
    )[: env.n_time]
    user_activity = np_module.linspace(
        SharedExperiment.QECO_USER_ACTIVITY_MIN,
        SharedExperiment.QECO_USER_ACTIVITY_MAX,
        env.n_ue,
    )
    task_prob = np_module.clip(time_profile[:, None] * user_activity[None, :], 0.0, 1.0)
    bitarrive_size = bitarrive_size * (np_module.random.uniform(0, 1, size=[env.n_time, env.n_ue]) < task_prob)
    bitarrive_size[-env.max_delay:, :] = np_module.zeros([env.max_delay, env.n_ue])

    bitarrive_dens = np_module.zeros([env.n_time, env.n_ue])
    for i in range(len(bitarrive_size)):
        for j in range(len(bitarrive_size[i])):
            if bitarrive_size[i][j] != 0:
                bitarrive_dens[i][j] = config.TASK_COMP_DENS[np_module.random.randint(0, len(config.TASK_COMP_DENS))]
    return bitarrive_size, bitarrive_dens


def generate_channel_traces(num_time, num_users, np_module):
    return np_module.random.uniform(low=1e-7, high=1e-5, size=(num_time, num_users))


def compute_env_metrics(env, np_module):
    qoe_values = []
    delay_values = []
    energy_values = []

    for time_index in range(env.n_time):
        for ue_index in range(env.n_ue):
            task_size = env.arrive_task_size[time_index, ue_index]
            if task_size == 0:
                continue

            delay = env.process_delay[time_index, ue_index]
            unfinished = env.unfinish_task[time_index, ue_index]
            ue_comp_energy = env.ue_comp_energy[time_index, ue_index]
            ue_tran_energy = env.ue_tran_energy[time_index, ue_index]
            edge_comp_energy = env.edge_comp_energy[time_index, ue_index]
            ue_idle_energy = env.ue_idle_energy[time_index, ue_index]

            qoe_values.append(
                qoe_function(
                    delay,
                    env.max_delay,
                    unfinished,
                    env.ue_energy_state[ue_index],
                    ue_comp_energy,
                    ue_tran_energy,
                    edge_comp_energy,
                    ue_idle_energy,
                )
            )
            delay_values.append(delay)
            energy_values.append(
                ue_comp_energy
                + ue_tran_energy
                + float(np_module.sum(edge_comp_energy))
                + float(np_module.sum(ue_idle_energy))
            )

    drop_count = float(np_module.sum(env.unfinish_task))
    avg_qoe = float(np_module.mean(qoe_values)) if qoe_values else 0.0
    avg_delay = float(np_module.mean(delay_values)) if delay_values else 0.0
    avg_energy = float(np_module.mean(energy_values)) if energy_values else 0.0
    return {
        "qoe": avg_qoe,
        "delay": avg_delay,
        "energy": avg_energy,
        "drop": drop_count,
    }


def save_common_outputs(run_dir: Path, episode_metrics: dict[str, list[float]], metadata: dict) -> None:
    save_series(episode_metrics["qoe"], run_dir / "QoE.txt")
    save_series(episode_metrics["delay"], run_dir / "Delay.txt")
    save_series(episode_metrics["energy"], run_dir / "Energy.txt")
    save_series(episode_metrics["drop"], run_dir / "Drop.txt")
    save_series(range(1, len(episode_metrics["qoe"]) + 1), run_dir / "Episode.txt")
    if "episode_runtime" in episode_metrics:
        save_series(episode_metrics["episode_runtime"], run_dir / "EpisodeRuntime.txt")

    comparison_dir = run_dir / "comparison_ready"
    comparison_dir.mkdir(parents=True, exist_ok=True)
    save_series(resample_series(episode_metrics["qoe"], SharedExperiment.COMPARISON_POINTS), comparison_dir / "QoE.txt")
    save_series(resample_series(episode_metrics["delay"], SharedExperiment.COMPARISON_POINTS), comparison_dir / "Delay.txt")
    save_series(resample_series(episode_metrics["energy"], SharedExperiment.COMPARISON_POINTS), comparison_dir / "Energy.txt")
    save_series(resample_series(episode_metrics["drop"], SharedExperiment.COMPARISON_POINTS), comparison_dir / "Drop.txt")
    save_series(range(1, SharedExperiment.COMPARISON_POINTS + 1), comparison_dir / "ComparisonStep.txt")

    with open(run_dir / "common_eval_metadata.json", "w") as f:
        json.dump(metadata, f, indent=2)


def algorithm_log_label(algorithm_name: str) -> str:
    if algorithm_name == "qeco_adapt":
        return "QECO-ADAPT"
    return algorithm_name.upper()


def normalize_algorithm_name(algorithm_name: str) -> str:
    return "qeco_adapt" if algorithm_name == "qeco-adapt" else algorithm_name


def qeco_style_policy_name(algorithm_name: str) -> str:
    policy_names = {
        "qeco": "qeco_d3qn_lstm",
        "qeco_adapt": "qeco_adapt_energy_aware_gating_d3qn_lstm",
        "twdqn": "tang_wong_adapted_dqn",
    }
    try:
        return policy_names[algorithm_name]
    except KeyError as exc:
        raise ValueError(f"Unknown QECO-style algorithm: {algorithm_name}") from exc


def run_binary_offload_common(algorithm_name: str, policy_name: str) -> Path:
    import numpy as np
    from Config import Config
    from MEC_Env import MEC
    from memoryPyTorch import MemoryDNN
    from optimization import bisection

    apply_global_seed(SharedExperiment.RANDOM_SEED, use_torch=True)
    run_dir = create_run_dir(algorithm_name)
    write_experiment_snapshot(
        run_dir,
        extra={"algorithm": algorithm_name.upper(), "evaluation_mode": "common_env", "policy": policy_name},
    )

    env = MEC(Config.N_UE, Config.N_EDGE, Config.N_TIME, Config.N_COMPONENT, Config.MAX_DELAY)
    mem = None
    cd_policy = None
    if policy_name == "droo":
        mem = MemoryDNN(
            net=[SharedExperiment.NUM_USERS, 120, 80, SharedExperiment.NUM_USERS],
            learning_rate=0.01,
            training_interval=10,
            batch_size=128,
            memory_size=SharedExperiment.DROO_MEMORY_SIZE,
        )
    elif policy_name == "cd":
        cd_policy = CDBinaryOffloadPolicy()

    episode_metrics = {"qoe": [], "delay": [], "energy": [], "drop": [], "episode_runtime": []}
    decoder_mode = SharedExperiment.DROO_DECODER_MODE
    adaptive_k = SharedExperiment.NUM_USERS

    for episode in range(SharedExperiment.QECO_EPISODES):
        episode_start = time.perf_counter()
        if episode % 20 == 0:
            print(f"[{algorithm_name.upper()} common] episode {episode}/{SharedExperiment.QECO_EPISODES}")
        bitarrive_size, bitarrive_dens = build_task_arrivals(env, Config, np)
        channel_traces = generate_channel_traces(env.n_time, env.n_ue, np)
        observation_all, lstm_state_all = env.reset(bitarrive_size, bitarrive_dens)
        done = False
        k_idx_his = []

        while not done:
            time_index = env.time_count
            h = channel_traces[time_index, :]
            if policy_name == "droo":
                m_list = mem.decode(h * 1e6, adaptive_k, decoder_mode)
                rewards = []
                for mode in m_list:
                    objective, _, _ = bisection(h, mode)
                    rewards.append(objective)
                best_idx = int(np.argmax(rewards))
                best_mode = np.asarray(m_list[best_idx], dtype=int)
                mem.encode(h * 1e6, best_mode)
                k_idx_his.append(best_idx)
            elif policy_name == "cd":
                best_mode = cd_policy.select_mode(h)
            else:
                raise ValueError(f"Unknown binary offloading policy: {policy_name}")

            action_all = np.zeros([env.n_ue], dtype=int)
            active_tasks = observation_all[:, 0] > 0
            for ue_index in range(env.n_ue):
                if not active_tasks[ue_index]:
                    action_all[ue_index] = 0
                else:
                    action_all[ue_index] = 1 if best_mode[ue_index] == 1 else 0

            observation_all, lstm_state_all, done = env.step(action_all)

            if (
                policy_name == "droo"
                and time_index > 0
                and time_index % SharedExperiment.DROO_DELTA == 0
                and k_idx_his
            ):
                adaptive_k = min(max(k_idx_his[-SharedExperiment.DROO_DELTA:]) + 2, SharedExperiment.NUM_USERS)

        metrics = compute_env_metrics(env, np)
        for key in episode_metrics:
            if key == "episode_runtime":
                continue
            episode_metrics[key].append(metrics[key])
        episode_metrics["episode_runtime"].append(time.perf_counter() - episode_start)
        if episode % 20 == 0:
            print(
                f"[{algorithm_name.upper()} common] qoe={metrics['qoe']:.3f} delay={metrics['delay']:.3f} "
                f"energy={metrics['energy']:.3f} drop={metrics['drop']:.1f} "
                f"ep_time={episode_metrics['episode_runtime'][-1]:.4f}s"
            )

    save_common_outputs(
        run_dir,
        episode_metrics,
        metadata={
            "algorithm": algorithm_name.upper(),
            "evaluation_mode": "common_env",
            "common_axis": "episode",
            "comparison_points": SharedExperiment.COMPARISON_POINTS,
            "policy": policy_name,
            "runtime_metric": "per_episode_wall_clock_seconds",
        },
    )
    return run_dir


def run_droo_common() -> Path:
    return run_binary_offload_common("droo", "droo")


def run_cd_common() -> Path:
    return run_binary_offload_common("cd", "cd")


def reward_for_algorithm(
    algorithm_name: str,
    env,
    ue_index: int,
    time_index: int,
):
    if algorithm_name == "qeco_adapt":
        return {
            "reward": qeco_adapt_reward_function(
                env.process_delay[time_index, ue_index],
                env.max_delay,
                env.unfinish_task[time_index, ue_index],
                env.ue_energy_state[ue_index],
                env.ue_comp_energy[time_index, ue_index],
                env.ue_tran_energy[time_index, ue_index],
                env.edge_comp_energy[time_index, ue_index],
                env.ue_idle_energy[time_index, ue_index],
                qeco_adapt_energy_weight(),
            )
        }

    return {
        "reward": qoe_function(
            env.process_delay[time_index, ue_index],
            env.max_delay,
            env.unfinish_task[time_index, ue_index],
            env.ue_energy_state[ue_index],
            env.ue_comp_energy[time_index, ue_index],
            env.ue_tran_energy[time_index, ue_index],
            env.edge_comp_energy[time_index, ue_index],
            env.ue_idle_energy[time_index, ue_index],
        )
    }


def run_qeco_style_common(algorithm_name: str) -> Path:
    import numpy as np
    import tensorflow.compat.v1 as tf
    from Config import Config
    from D3QN import DuelingDoubleDeepQNetwork
    from MEC_Env import MEC

    apply_global_seed(SharedExperiment.RANDOM_SEED, use_tensorflow=True)
    run_dir = create_run_dir(algorithm_name)
    log_label = algorithm_log_label(algorithm_name)
    models_dir = run_dir / "models"
    models_dir.mkdir(parents=True, exist_ok=True)
    write_experiment_snapshot(
        run_dir,
        extra={
            "algorithm": algorithm_name.upper(),
            "evaluation_mode": "common_env",
            "models_dir": str(models_dir),
            "policy": qeco_style_policy_name(algorithm_name),
            "qeco_adapt_reward": (
                {
                    "effective_load": qeco_adapt_effective_load(),
                    "energy_weight": qeco_adapt_energy_weight(),
                    "base_energy_weight": SharedExperiment.QECO_ADAPT_BASE_ENERGY_WEIGHT,
                    "user_exponent": SharedExperiment.QECO_ADAPT_USER_EXPONENT,
                    "load_scale_base": SharedExperiment.QECO_ADAPT_LOAD_SCALE,
                    "load_scale_actual": SharedExperiment.NUM_EDGES * SharedExperiment.QECO_ADAPT_LOAD_SCALE,
                    "gating_strength": qeco_adapt_gating_strength(),
                    "min_energy_state": SharedExperiment.QECO_ADAPT_MIN_ENERGY_STATE,
                    "edge_backlog_threshold": SharedExperiment.QECO_ADAPT_EDGE_BACKLOG_THRESHOLD,
                    "size_threshold": SharedExperiment.QECO_ADAPT_SIZE_THRESHOLD,
                }
                if algorithm_name == "qeco_adapt"
                else None
            ),
        },
    )

    env = MEC(Config.N_UE, Config.N_EDGE, Config.N_TIME, Config.N_COMPONENT, Config.MAX_DELAY)
    if algorithm_name == "twdqn":
        ue_RL_list = build_twdqn_agents(env, Config)
    else:
        ue_RL_list = [
            DuelingDoubleDeepQNetwork(
                env.n_actions,
                env.n_features,
                env.n_lstm_state,
                env.n_time,
                learning_rate=Config.LEARNING_RATE,
                reward_decay=Config.REWARD_DECAY,
                e_greedy=Config.E_GREEDY,
                replace_target_iter=Config.N_NETWORK_UPDATE,
                memory_size=Config.MEMORY_SIZE,
            )
            for _ in range(Config.N_UE)
        ]

    tf.set_random_seed(SharedExperiment.RANDOM_SEED)
    episode_metrics = {"qoe": [], "delay": [], "energy": [], "drop": [], "episode_runtime": []}
    rl_step = 0

    for episode in range(Config.N_EPISODE):
        episode_start = time.perf_counter()
        if episode % 20 == 0:
            print(f"[{log_label} common] episode {episode}/{Config.N_EPISODE}")
        bitarrive_size, bitarrive_dens = build_task_arrivals(env, Config, np)
        history = []
        for time_index in range(env.n_time):
            history.append([])
            for _ in range(env.n_ue):
                history[time_index].append(
                    {
                        "observation": np.zeros(env.n_features),
                        "lstm": np.zeros(env.n_lstm_state),
                        "action": np.nan,
                        "observation_": np.zeros(env.n_features),
                        "lstm_": np.zeros(env.n_lstm_state),
                    }
                )
        reward_indicator = np.zeros([env.n_time, env.n_ue])
        observation_all, lstm_state_all = env.reset(bitarrive_size, bitarrive_dens)
        done = False

        while not done:
            action_all = np.zeros([env.n_ue], dtype=int)
            for ue_index in range(env.n_ue):
                observation = np.squeeze(observation_all[ue_index, :])
                if np.sum(observation) == 0:
                    action_all[ue_index] = 0
                else:
                    action_all[ue_index] = ue_RL_list[ue_index].choose_action(observation)
                    if algorithm_name == "qeco_adapt":
                        action_all[ue_index] = apply_qeco_adapt_gating(observation, int(action_all[ue_index]))
                    if observation[0] != 0:
                        ue_RL_list[ue_index].do_store_action(episode, env.time_count, action_all[ue_index])

            observation_all_, lstm_state_all_, done = env.step(action_all)

            for ue_index in range(env.n_ue):
                ue_RL_list[ue_index].update_lstm(lstm_state_all_[ue_index, :])

            process_delay = env.process_delay
            unfinish_task = env.unfinish_task

            for ue_index in range(env.n_ue):
                history[env.time_count - 1][ue_index]["observation"] = observation_all[ue_index, :]
                history[env.time_count - 1][ue_index]["lstm"] = np.squeeze(lstm_state_all[ue_index, :])
                history[env.time_count - 1][ue_index]["action"] = action_all[ue_index]
                history[env.time_count - 1][ue_index]["observation_"] = observation_all_[ue_index]
                history[env.time_count - 1][ue_index]["lstm_"] = np.squeeze(lstm_state_all_[ue_index, :])

                update_index = np.where((1 - reward_indicator[:, ue_index]) * process_delay[:, ue_index] > 0)[0]
                if len(update_index) != 0:
                    for time_index in update_index:
                        reward_info = reward_for_algorithm(
                            algorithm_name,
                            env,
                            ue_index,
                            time_index,
                        )
                        reward = reward_info["reward"]
                        ue_RL_list[ue_index].store_transition(
                            history[time_index][ue_index]["observation"],
                            history[time_index][ue_index]["lstm"],
                            history[time_index][ue_index]["action"],
                            reward,
                            history[time_index][ue_index]["observation_"],
                            history[time_index][ue_index]["lstm_"],
                        )
                        ue_RL_list[ue_index].do_store_reward(episode, time_index, reward)
                        ue_RL_list[ue_index].do_store_delay(episode, time_index, process_delay[time_index, ue_index])
                        ue_RL_list[ue_index].do_store_energy(
                            episode,
                            time_index,
                            env.ue_comp_energy[time_index, ue_index],
                            env.ue_tran_energy[time_index, ue_index],
                            env.edge_comp_energy[time_index, ue_index],
                            env.ue_idle_energy[time_index, ue_index],
                        )
                        reward_indicator[time_index, ue_index] = 1

            rl_step += 1
            observation_all = observation_all_
            lstm_state_all = lstm_state_all_

            if (rl_step > 200) and (rl_step % 10 == 0):
                for ue in range(env.n_ue):
                    if hasattr(ue_RL_list[ue], "memory_counter") and ue_RL_list[ue].memory_counter > ue_RL_list[ue].n_lstm_step:
                        ue_RL_list[ue].learn()

        metrics = compute_env_metrics(env, np)
        for key in episode_metrics:
            if key == "episode_runtime":
                continue
            episode_metrics[key].append(metrics[key])
        episode_metrics["episode_runtime"].append(time.perf_counter() - episode_start)
        if episode % 20 == 0:
            print(
                f"[{log_label} common] qoe={metrics['qoe']:.3f} delay={metrics['delay']:.3f} "
                f"energy={metrics['energy']:.3f} drop={metrics['drop']:.1f} "
                f"ep_time={episode_metrics['episode_runtime'][-1]:.4f}s"
            )

    save_common_outputs(
        run_dir,
        episode_metrics,
        metadata={
            "algorithm": algorithm_name.upper(),
            "evaluation_mode": "common_env",
            "common_axis": "episode",
            "comparison_points": SharedExperiment.COMPARISON_POINTS,
            "policy": qeco_style_policy_name(algorithm_name),
            "runtime_metric": "per_episode_wall_clock_seconds",
            "qeco_adapt_reward": (
                {
                    "effective_load": qeco_adapt_effective_load(),
                    "energy_weight": qeco_adapt_energy_weight(),
                    "gating_strength": qeco_adapt_gating_strength(),
                }
                if algorithm_name == "qeco_adapt"
                else None
            ),
        },
    )
    return run_dir


def run_qeco_common() -> Path:
    return run_qeco_style_common("qeco")


def run_qeco_adapt_common() -> Path:
    return run_qeco_style_common("qeco_adapt")


def run_twdqn_common() -> Path:
    return run_qeco_style_common("twdqn")


def main() -> int:
    parser = argparse.ArgumentParser(description="Run baselines inside the shared common evaluation environment.")
    parser.add_argument("algorithm", choices=["droo", "qeco", "qeco_adapt", "qeco-adapt", "cd", "twdqn"])
    args = parser.parse_args()

    os.chdir(str(ROOT_DIR))
    algorithm = normalize_algorithm_name(args.algorithm)
    if algorithm == "droo":
        run_dir = run_droo_common()
    elif algorithm == "cd":
        run_dir = run_cd_common()
    elif algorithm == "qeco_adapt":
        run_dir = run_qeco_adapt_common()
    elif algorithm == "twdqn":
        run_dir = run_twdqn_common()
    else:
        run_dir = run_qeco_common()

    print(f"Common evaluation run directory: {run_dir}")
    print(f"Comparison-ready output: {run_dir / 'comparison_ready'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
