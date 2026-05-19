from __future__ import annotations


def build_twdqn_agents(env, config):
    """Independent baseline wrapper for a Tang&Wong-style vanilla DQN."""
    from D3QN import DuelingDoubleDeepQNetwork

    agent_kwargs = dict(
        learning_rate=config.LEARNING_RATE,
        reward_decay=config.REWARD_DECAY,
        e_greedy=config.E_GREEDY,
        replace_target_iter=config.N_NETWORK_UPDATE,
        memory_size=config.MEMORY_SIZE,
        dueling=False,
        double_q=False,
    )

    return [
        DuelingDoubleDeepQNetwork(
            env.n_actions,
            env.n_features,
            env.n_lstm_state,
            env.n_time,
            **agent_kwargs,
        )
        for _ in range(config.N_UE)
    ]
