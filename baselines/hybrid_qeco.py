from __future__ import annotations


def hybrid_reward_components(
    *,
    qoe_function,
    normalize_function,
    delay,
    max_delay,
    unfinish_task,
    ue_energy_state,
    ue_comp_energy,
    ue_tran_energy,
    edge_comp_energy,
    ue_idle_energy,
    ue_bit_processed,
    ue_bit_transmitted,
    alpha,
    beta,
    epsilon,
    cd_lambda,
    action,
    cd_action,
    qoe_min,
    throughput_ref,
):
    qoe_score = qoe_function(
        delay,
        max_delay,
        unfinish_task,
        ue_energy_state,
        ue_comp_energy,
        ue_tran_energy,
        edge_comp_energy,
        ue_idle_energy,
    )
    qoe_score_norm = normalize_function(qoe_score, qoe_min, max_delay * 4)

    throughput_bits = ue_bit_processed + ue_bit_transmitted
    capped_throughput = min(float(throughput_bits), float(throughput_ref))
    throughput_score = normalize_function(capped_throughput, 0, throughput_ref)

    drop_penalty = 1.0 if unfinish_task else 0.0
    throughput_term = alpha * throughput_score
    qoe_term = beta * qoe_score_norm
    drop_term = epsilon * drop_penalty
    cd_alignment = 1.0 if int(action) == int(cd_action) else 0.0
    cd_alignment_term = cd_lambda * cd_alignment
    reward = throughput_term + qoe_term - drop_term + cd_alignment_term

    return {
        "reward": reward,
        "throughput_term": throughput_term,
        "qoe_term": qoe_term,
        "drop_penalty_term": drop_term,
        "cd_alignment_term": cd_alignment_term,
        "throughput_score": throughput_score,
        "qoe_score_norm": qoe_score_norm,
        "drop_penalty": drop_penalty,
        "cd_alignment": cd_alignment,
    }


def hybrid_reward_function(
    **kwargs,
):
    return hybrid_reward_components(**kwargs)["reward"]
