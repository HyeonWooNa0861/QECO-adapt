# QECO-ADAPT 발표 예상 질의응답

이 문서는 `26-1_알파_나현우_5_7.pdf` 논문형 자료와 `Dense MEC 환경에서 QECO-ADAPT의 부하 적응형 오프로딩 성능 분석.pdf` 발표 자료를 함께 기준으로 작성한 질의응답 준비 노트이다. 답변의 핵심 방향은 다음 세 가지이다.

- QECO-ADAPT는 QECO를 대체하는 범용 알고리즘이 아니라, dense MEC에서 QECO의 초기 수렴 손실을 줄이는 보완형 변형이다.
- 핵심 기여는 effective load 기반 adaptive energy weight와 offloading gating을 QECO reward/action 흐름에 결합한 것이다.
- 결과 해석은 최종 10% 성능이 아니라 전체 400 episode 평균과 warm-up 손실 완화 관점에서 해야 한다.

## 1. 발표 핵심 문장

질문이 넓게 들어오면 아래 문장으로 시작하면 안전하다.

> 본 연구는 원문 QECO의 edge당 사용자 밀도 10 MDs/EN을 기준점으로 삼아, 단일 edge에 사용자 부하가 집중될 때 QECO-ADAPT가 어떤 구간에서 유효한지 검토한 실험입니다. QECO-ADAPT는 기존 QECO의 D3QN/LSTM 구조와 action space를 유지하되, effective load를 이용해 energy cost와 offloading gating을 조정하여 dense 환경의 초기 warm-up 손실과 dropped-task 누적을 줄이는 보완형 알고리즘입니다.

## 2. 핵심 수치 요약

전체 400 episode 평균 기준 QECO 대비 QECO-ADAPT 변화량이다. QoE는 증가가 개선이고, Delay, Energy, Dropped tasks, Runtime은 감소가 개선이다.

| Users | Density | QoE | Delay | Energy | Dropped tasks | Runtime |
|---:|---:|---:|---:|---:|---:|---:|
| 10 | 1x | -9.13% | -3.65% | +7.83% | -32.85% | -5.07% |
| 30 | 3x | +10.97% | +1.30% | +5.37% | +5.88% | +3.12% |
| 50 | 5x | +41.45% | +1.87% | +12.25% | +10.25% | -10.98% |
| 80 | 8x | +89.51% | +1.72% | +18.29% | +11.17% | -10.83% |

주의: 표의 `+`는 성능상 이득, `-`는 성능상 손실을 뜻한다. 예를 들어 1x의 Dropped tasks `-32.85%`는 drop probability가 아니라 평균 dropped-task count가 QECO보다 증가했다는 뜻이다.

## 3. 연구 동기 관련 질문

### Q1. 왜 기존 QECO를 그대로 쓰지 않고 QECO-ADAPT를 설계했는가?

기존 QECO는 QoE, delay, energy를 함께 고려하는 D3QN/LSTM 기반 알고리즘이지만, 단일 edge에 사용자가 몰리는 dense stress 조건에서는 초기 학습 구간에서 QoE 손실과 dropped-task 누적이 커질 수 있다. QECO-ADAPT는 QECO의 구조를 바꾸기보다, effective load에 따라 energy cost와 offloading 선택을 더 조심스럽게 조정해 dense 환경의 warm-up 손실을 줄이기 위해 설계했다.

짧게 답하면:

> QECO의 장점은 유지하되, 단일 edge dense 환경에서 초반 수렴 손실과 dropped-task 누적을 줄이기 위한 부하 적응형 보완입니다.

### Q2. QECO-ADAPT가 QECO보다 항상 좋은 알고리즘인가?

아니다. 1x 저부하 조건에서는 QECO-ADAPT가 energy는 줄였지만 QoE, delay, dropped tasks에서는 QECO보다 불리했다. 따라서 QECO-ADAPT는 모든 환경에서 QECO를 대체하는 범용 알고리즘이 아니라, 사용자 밀도가 3x 이상으로 증가하는 dense 조건에서 효과가 나타나는 환경 의존형 보완 알고리즘이다.

### Q3. 왜 단일 edge 환경만 실험했는가?

원문 QECO의 기본 환경은 50 MDs와 5 ENs이며, edge당 평균 사용자 밀도는 10 MDs/EN이다. 본 연구는 원문 전체 환경을 그대로 재현하려는 것이 아니라, 이 edge당 밀도를 기준으로 단일 edge에 부하가 집중될 때 알고리즘이 어떻게 변하는지 stress test한 것이다. 그래서 edge 수를 1로 고정하고 사용자 수를 10, 30, 50, 80으로 늘려 1x, 3x, 5x, 8x 조건을 만들었다.

### Q4. 원문 QECO와 직접 비교했다고 말해도 되는가?

주의해서 말해야 한다. 본 실험은 원문 QECO의 전체 multi-edge 환경을 그대로 재현한 것이 아니라, 원문에서 제시된 edge당 사용자 밀도를 기준으로 단일 edge dense stress 조건을 구성한 것이다. 따라서 "QECO 원문보다 우수하다"가 아니라 "원문 기준 edge당 밀도보다 부하가 증가하는 단일 edge 조건에서 QECO 대비 어떤 변화가 나타나는지 분석했다"라고 말하는 것이 정확하다.

## 4. 방법론 및 수식 관련 질문

### Q5. effective load는 무엇인가?

effective load는 edge 하나가 평균적으로 감당해야 하는 task pressure를 단순화한 지표이다. 사용자 수, 평균 task arrival profile, 평균 사용자 활동성, edge 수를 반영한다.

```text
L_eff = N * b_bar * a_bar / M
```

여기서 `N`은 사용자 수, `M`은 edge 수, `b_bar`는 평균 task arrival profile, `a_bar`는 평균 사용자 활동성이다. 사용자가 늘면 `L_eff`는 증가하고, edge 수가 늘면 감소한다.

### Q6. gating strength는 어떤 역할인가?

gating strength는 effective load를 실제 adaptive control 강도로 바꾸는 계수이다.

```text
g(L_eff) = L_eff / (L_eff + M * lambda)
```

부하가 커질수록 `g`가 증가하므로, QECO-ADAPT는 dense 조건에서 energy-aware behavior와 보수적 offloading 선택을 강화한다. 반대로 edge 수가 늘면 `L_eff`는 낮아지고 `M * lambda`는 커져 gating이 완화된다.

### Q7. scale constant는 현재 얼마인가?

코드 기준 per-edge load scale인 `lambda`는 10.0이다. 실제 gating denominator에 들어가는 scale constant는 `c = M * lambda`이다. 현재 공통 실험은 `M = 1`이므로 실제 scale constant도 10.0이다.

```text
lambda = 10.0
M = 1
c = M * lambda = 10.0
```

### Q8. adaptive energy weight는 무엇을 의미하는가?

adaptive energy weight는 QECO reward의 energy cost 항에 곱해지는 동적 가중치이다.

```text
w_E = w_0 * (1 + g(L_eff))^rho
```

현재 설정은 `w_0 = 1.20`, `rho = 0.35`, `lambda = 10.0`이다. `w_0`는 기본 energy emphasis이고, `rho`는 부하 증가에 따른 energy weight 증가 곡률을 조절한다. `rho < 1`이므로 부하가 증가해도 energy penalty가 과도하게 폭증하지 않도록 완만하게 증가한다.

### Q9. a_bar와 b_bar가 energy weight 곡선을 직접 제어하는가?

직접 제어하지 않는다. `a_bar`와 `b_bar`는 `L_eff`를 계산하는 입력값이다. energy weight 곡선 자체는 `w_0`, `rho`, `lambda`가 제어한다.

정확한 구분은 다음과 같다.

| 기호 | 역할 |
|---|---|
| `b_bar` | 평균 task arrival profile |
| `a_bar` | 평균 사용자 활동성 |
| `lambda` | gating strength의 load scale |
| `w_0` | energy weight 기준값 |
| `rho` | energy weight 증가 곡률 |
| `alpha` | completion reward scale |

### Q10. alpha는 energy weight 파라미터인가?

아니다. `alpha = 4`는 completion reward scale이다.

```text
r_done = alpha * D_max
```

현재 `D_max = 10`이므로 `r_done = 40`이다. `alpha`는 energy weight 곡선을 제어하는 값이 아니라 기존 QECO 공개 구현의 completion reward scale을 유지하기 위한 calibration parameter로 보는 것이 적절하다.

### Q11. QECO-ADAPT는 policy-invariant reward shaping인가?

아니다. 이 점은 분명히 말해야 한다. policy-invariant reward shaping은 reward를 바꾸더라도 최적 정책이 보존되는 형태를 의미한다. 그러나 QECO-ADAPT는 energy cost의 상대 가중치를 바꾸고, offloading action도 gating으로 local action으로 바꿀 수 있다. 따라서 기존 QECO의 최적 정책이 그대로 유지된다고 보장할 수 없다.

정확한 표현은 다음과 같다.

> QECO-ADAPT는 policy-invariant reward shaping이 아니라, load-adaptive reward/cost reweighting과 offloading gating을 결합한 방식입니다.

### Q12. action space는 바뀌었는가?

action space 자체는 기존 QECO와 같다. 다만 QECO-ADAPT는 DQN이 선택한 offloading action을 그대로 실행하지 않고, gating 조건에 따라 local action으로 바꿀 수 있다. 그래서 학습 구조와 action 후보는 유지되지만 실제 실행 정책은 기존 QECO와 달라질 수 있다.

## 5. 결과 해석 관련 질문

### Q13. 1x 조건에서 왜 QECO-ADAPT가 불리했는가?

1x는 원문 QECO의 edge당 기본 밀도와 같은 저부하 조건이다. 이 경우 edge 처리 여유가 상대적으로 충분하므로, QECO의 기존 QoE 중심 균형이 더 적합하다. QECO-ADAPT의 energy-aware penalty와 gating은 energy를 줄이는 데는 도움이 됐지만, QoE와 dropped-task 안정성 손실을 상쇄할 정도의 이득을 만들지 못했다.

핵심 수치:

- Energy: 7.83% 개선
- QoE: 9.13% 감소
- Delay: 3.65% 증가
- Dropped tasks: 32.85% 증가

### Q14. 3x부터 성능이 좋아진 이유는 무엇인가?

3x부터는 단일 edge가 처리해야 하는 task pressure가 커진다. 이때 QECO-ADAPT의 adaptive energy weight와 gating이 과도한 energy usage와 불리한 offloading을 억제하면서 초반 수렴 구간의 손실을 줄인다. 결과적으로 전체 episode 평균 기준 QoE, Delay, Energy, Dropped tasks가 함께 개선된다.

### Q15. 5x와 8x에서 QoE 개선폭이 큰 이유는 무엇인가?

5x와 8x는 단일 edge에 deadline pressure가 강하게 걸리는 조건이다. 기존 QECO는 초반 학습 구간에서 혼잡과 dropped-task 누적의 영향을 크게 받지만, QECO-ADAPT는 부하가 커질수록 energy-aware behavior와 offloading 보수화를 강화한다. 이 때문에 전체 400 episode 평균에서 warm-up 손실이 줄어 QoE 개선폭이 크게 나타난다.

### Q16. QECO-ADAPT가 DROO보다 항상 좋은가?

항상 좋다고 말하면 안 된다. 8x smoothed time-series 기준으로 QoE, Delay, Dropped tasks에서는 episode 진행 후 QECO-ADAPT가 우세한 구간이 나타나지만, Energy만 보면 DROO가 더 낮은 구간이 있다. 따라서 QECO-ADAPT의 장점은 energy 단독 최적화가 아니라 QoE-Delay-Drop 균형과 수렴 안정성 관점에서 해석해야 한다.

### Q17. 왜 final 10%가 아니라 전체 400 episode 평균을 주 지표로 삼았는가?

QECO-ADAPT의 목적은 최종 안정 구간에서 QECO를 크게 압도하는 것이 아니라, 초기 warm-up 과정에서 쌓이는 QoE 손실과 dropped-task 누적을 줄이는 것이다. final 10%만 보면 후반에 QECO와 유사하게 수렴하는 특성 때문에 개선 폭이 과소평가될 수 있다. 그래서 전체 episode 평균을 주 지표로 삼고, final 10%는 안정 구간 추종성을 확인하는 보조 지표로 사용했다.

### Q18. Runtime overhead는 어떻게 해석해야 하는가?

5x와 8x에서는 QECO-ADAPT가 QECO보다 약 11% 더 긴 trimmed median episode runtime을 보였다. 이는 adaptive weighting과 gating 계산이 추가되기 때문으로 볼 수 있다. 다만 반복 최적화 solver를 매 frame 수행하는 방식이 아니므로 구조적으로 큰 overhead라기보다는 QECO와 같은 실행 범위 안에서 발생한 추가 비용이다. 적용 여부는 dense 환경에서 얻는 QoE, Energy, dropped-task 개선과 약 10% 내외 runtime 증가의 trade-off로 판단해야 한다.

### Q19. Dropped tasks는 drop probability인가?

아니다. 본 자료의 Dropped tasks는 episode별 deadline 내 완료되지 못한 task count의 평균이다. 따라서 `Dropped tasks 32.85% 증가`는 drop probability가 32.85%라는 뜻이 아니라, QECO 대비 평균 dropped-task count가 그 비율만큼 증가했다는 뜻이다.

## 6. novelty와 기여 관련 질문

### Q20. QECO-ADAPT의 novelty는 무엇인가?

큰 신경망 구조를 새로 제안한 것이 아니라, 기존 QECO 구조 위에 dense-load-aware control을 가볍게 결합한 점이 핵심이다. 구체적으로는 다음 세 가지가 기여이다.

- 원문 QECO의 edge당 사용자 밀도를 기준으로 단일 edge dense stress setup을 구성했다.
- effective load 기반 gating strength와 adaptive energy weight를 정의했다.
- QECO의 D3QN/LSTM 구조를 유지하면서 reward/cost reweighting과 offloading gating으로 warm-up 손실을 줄이는 보완형 정책을 검증했다.

### Q21. 기존 energy-aware offloading 연구와 무엇이 다른가?

기존 연구들은 energy minimization, queue stability, Lyapunov optimization, resource allocation 등을 직접 다루는 경우가 많다. QECO-ADAPT는 별도의 per-frame iterative solver나 명시적 Lyapunov drift-plus-penalty 문제를 추가하지 않고, QECO의 reward 흐름 안에서 effective load 기반 동적 energy weight와 gating을 적용한다. 즉 이론적 최적화 보장보다는, 기존 QECO 구현에 결합 가능한 lightweight adaptive control이라는 점이 차별점이다.

### Q22. Lyapunov stability를 보장하는가?

아니다. QECO-ADAPT는 queue stability의 형식적 보장을 제공하지 않는다. 다만 stochastic task arrival와 edge load dynamics가 중요하다는 기존 연구 흐름을 반영해, effective load가 증가할 때 energy penalty와 offloading 보수화를 강화하도록 설계했다. 따라서 안정성 보장 알고리즘이라기보다 dense stress 조건에서의 경험적 성능 개선 알고리즘으로 제시하는 것이 정확하다.

## 7. 한계 및 방어 질문

### Q23. seed가 하나라면 결과 신뢰성이 부족하지 않은가?

그 지적은 타당하다. 현재 결과는 동일 seed와 공통 환경에서 알고리즘 간 차이를 비교한 재현성 있는 stress test로 볼 수 있지만, 통계적 일반화를 위해서는 다중 seed 실험이 필요하다. 향후 연구에서는 다중 seed 평균과 분산, 목표 QoE 도달 episode, dropped-task 안정화 episode 같은 직접 수렴 지표를 추가해 검증할 계획이라고 답하면 된다.

### Q24. 왜 400 episode인가?

현재 공통 비교 환경에서 동일 episode budget으로 알고리즘을 비교하기 위해 400 episode를 사용했다. QECO-ADAPT의 목적이 후반 최종 성능만이 아니라 초반 warm-up 손실 완화이므로, 400 episode 전체 평균과 smoothed trend를 함께 보는 방식이 적합하다. 다만 원문 QECO와 완전 동일한 학습 episode 수 재현은 아니므로, 이 부분은 stress test 조건의 한계로 인정하는 것이 좋다.

### Q25. 단일 edge stress test만으로 multi-edge dense 환경도 좋아진다고 말할 수 있는가?

그렇게 단정하면 안 된다. 본 실험은 단일 edge에서 부하 집중 효과를 분리해 관찰한 것이다. multi-edge 환경에서는 routing, edge 간 workload distribution, edge capacity 분산 효과가 추가되므로 별도 실험이 필요하다. 현재 결론은 "단일 edge에 사용자 밀도가 집중될 때 3x 이상에서 QECO-ADAPT의 유효성이 나타났다"로 제한해야 한다.

### Q26. QECO-ADAPT가 energy를 낮추는데 왜 QoE도 좋아지는가?

저부하에서는 energy penalty가 QoE 손실로 이어질 수 있다. 실제로 1x에서 그런 현상이 나타났다. 그러나 dense 조건에서는 과도한 offloading과 energy usage가 deadline miss와 dropped-task 누적으로 이어질 수 있다. QECO-ADAPT는 부하 증가 시 energy-aware behavior와 offloading gating을 강화해 초반 혼잡 손실을 줄이고, 결과적으로 전체 episode 평균 QoE도 개선한다.

### Q27. 8x에서 QoE 개선이 89.51%로 큰데 과장 아닌가?

비율이 큰 이유는 QECO의 8x 평균 QoE 기준값이 낮기 때문이다. 절대 변화량은 `+3.3372`이고, 이를 QECO 평균 대비 비율로 환산하면 `+89.51%`가 된다. 따라서 발표에서는 비율만 강조하기보다 절대 변화량과 함께 설명하는 것이 안전하다.

### Q28. QECO-ADAPT의 정책이 기존 QECO의 최적 정책과 다른가?

다르다. 기존 QECO는 DQN이 선택한 action을 그대로 실행하고, 고정된 reward cost를 사용한다. QECO-ADAPT는 adaptive energy weight로 reward landscape를 바꾸고, gating으로 실제 offloading action을 local action으로 바꿀 수 있다. 따라서 기존 QECO의 최적 정책을 보존한다고 말할 수 없고, dense load 조건에 맞춘 다른 실행 정책으로 보는 것이 정확하다.

## 8. 추가 심화 질의

### Q29. QECO-ADAPT와 유사한 QECO 기반 부하 적응형 알고리즘 논문이 존재하는가?

QECO의 저널 발간 이후 문헌으로 범위를 좁혀 다시 보면, 현재 확인한 범위에서는 "QECO를 직접 기반으로 삼아 effective load, offloading gating, adaptive energy weight를 추가한 동일 구조의 QECO 기반 부하 적응형 알고리즘"은 명확히 확인되지 않았다. 따라서 발표에서는 다음처럼 답하는 것이 가장 안전하다.

> QECO 발간 이후 논문 중에서도 본 연구처럼 QECO의 D3QN/LSTM 구조를 유지한 채 effective-load 기반 gating과 adaptive energy weight를 결합한 동일 구조의 QECO 기반 변형은 확인하지 못했습니다. 다만 2026년 이후 문헌에서 dynamic edge load, adaptive reward/weighting, workload-aware scheduling을 다루는 인접 연구는 확인되며, 본 연구는 그런 문제의식을 QECO 구조 위에 lightweight하게 결합했다는 점에서 차별화됩니다.

QECO-ADAPT의 유사성 검증에 직접 사용할 수 있는 발간 이후 참고문헌 후보는 다음과 같다.

| 논문 | 참고문헌 정보 | 유사성 | 차별점 |
|---|---|---|---|
| D3QN-LMA | Y. Mao, X. Tang, J. Lu, H. Li, and C. Wang, "D3QN-LMA: A memory-augmented deep reinforcement learning framework for energy-latency tradeoff optimization in mobile edge computing," Advanced Engineering Informatics, vol. 72, article 104431, 2026, doi: 10.1016/j.aei.2026.104431. ScienceDirect: https://www.sciencedirect.com/science/article/pii/S1474034626001230 | D3QN, LSTM, dynamic edge load, adaptive weight adjustment, QECO를 baseline으로 비교한다는 점에서 가장 가까운 발간 이후 유사 연구 | QECO를 직접 확장한 구조가 아니라 multi-head attention과 hierarchical optimization을 포함한 별도 알고리즘이다. 또한 QECO-ADAPT의 `L_eff -> g(L_eff) -> w_E` 수식 및 action-level gating 구조와는 다르다 |
| PreAlloc-A2C | C. Wang, X. Tang, J. Lu, J. Yang, and P. Yuan, "A Deep Reinforcement Learning-Based Pre-Allocation Mechanism for Efficient Task Offloading in Mobile Edge Computing," Computers, Materials & Continua, vol. 88, no. 1, article 45, 2026, doi: 10.32604/cmc.2026.078998. Tech Science: https://www.techscience.com/cmc/v88n1/67307/html | workload 변화, LSTM 기반 server load 예측, delay-energy-drop rate를 함께 최적화한다는 점에서 문제의식이 유사하다 | QECO 기반이 아니며 D3QN 계열도 아니다. actor-critic 기반 pre-allocation/task-server matching 구조이므로, QECO-ADAPT의 QECO reward 보완형 설계와 직접 겹치지 않는다 |

코멘트:

> QECO 이후에도 dynamic load와 adaptive weighting을 다루는 연구는 존재한다. 그러나 확인된 발간 이후 문헌들은 QECO를 그대로 보완하는 구조가 아니라 별도 알고리즘 구조를 제안한다. 따라서 QECO-ADAPT는 "완전히 새로운 문제"라기보다 "QECO 구조를 유지하면서 부하 적응형 reward/cost reweighting과 gating을 결합한 lightweight variant"로 포지셔닝하는 것이 가장 안전하다.

참고:

- Tang and Wong의 DRL offloading, delay-aware energy-efficient DRL offloading 등은 배경 연구로는 유용하지만 QECO 저널 발간 이전 문헌이므로, "QECO 발간 이후 유사성 판단" 표에서는 제외한다.
- QECO 원 논문은 기준 논문으로 별도 인용한다. 유사성 판단 표에서는 발간 이후 후속/인접 연구만 배치한다.

### Q30. edge당 평균 부하를 산출하는 방식이라면 평균 부하는 딥러닝 과정에서 계속 변화하는가?

현재 구현 기준으로는 계속 변화하지 않는다. `L_eff = N * b_bar * a_bar / M`에서 `N`, `M`, `b_bar`, `a_bar`는 한 실험 시나리오 안에서 고정된 설정값이다. 따라서 `effective_load`, `gating_strength`, `adaptive energy weight`는 현재 코드에서는 episode마다 학습되거나 gradient로 업데이트되는 신경망 weight가 아니라, 시나리오 시작 시 결정되는 deterministic control parameter에 가깝다.

다만 실제 환경의 instantaneous load는 계속 변한다. 예를 들어 각 time slot에서 task arrival, edge backlog, local/transmission time, energy state는 변하고, 이 값들은 DQN의 observation과 LSTM state에 반영된다. 또한 QECO-ADAPT의 gating은 고정된 gating strength를 기준으로 하되, 매 time slot의 observation을 보고 실제 action을 바꿀 수 있다.

정리하면 다음과 같다.

| 구분 | 현재 구현에서 변화 여부 | 설명 |
|---|---|---|
| `L_eff` | 실험 중 고정 | 사용자 수, 평균 profile, 평균 활동성, edge 수로 계산 |
| `g(L_eff)` | 실험 중 고정 | `L_eff`와 `M * lambda`로 계산 |
| `w_E` | 실험 중 고정 | reward 계산마다 같은 scenario-level weight 사용 |
| edge backlog | time slot마다 변화 | 환경 상태이며 gating 조건과 DQN observation에 반영 |
| DQN/LSTM 내부 weight | 학습 중 변화 | reward signal에 따라 Q-network가 업데이트됨 |

짧게 답하면:

> 평균 부하 자체가 학습 중 계속 갱신되는 구조는 아닙니다. 현재는 시나리오 단위의 부하 계수로 계산하고, 딥러닝 과정에서 변하는 것은 DQN/LSTM의 내부 파라미터와 매 time slot의 관측 상태입니다.

### Q31. gating strength는 기존 QECO와 어떤 차별점이 있는가?

기존 QECO에는 별도의 gating strength가 없다. 기존 QECO는 D3QN이 observation을 입력받아 action을 선택하면 그 action이 그대로 실행된다. 반면 QECO-ADAPT는 D3QN이 offloading action을 선택하더라도, effective load 기반 gating strength와 현재 observation 조건을 이용해 일부 offloading을 local action으로 바꿀 수 있다.

QECO-ADAPT에서 gating이 추가된 이유는 dense 환경의 초기 학습 구간에서 불리한 offloading을 줄이기 위해서이다. 단일 edge에 사용자가 몰리면 edge backlog와 transmission delay가 증가하고, deadline 내 완료되지 못하는 task가 누적될 수 있다. 이때 기존 QECO는 학습이 충분히 안정되기 전까지 과도한 offloading을 선택할 수 있으므로 warm-up 손실이 커질 수 있다. QECO-ADAPT의 gating은 이런 구간에서 offloading을 더 보수적으로 실행하게 만드는 안전장치 역할을 한다.

현재 gating은 다음 조건에서 DQN의 offloading action을 local action으로 바꿀 수 있다.

- 단말 energy state가 gating threshold 이하인 경우
- edge backlog가 threshold 이상인 경우
- task size가 작아 offloading 이득이 제한적인 경우
- local processing time이 transmission time보다 짧거나 같은 경우

짧게 답하면:

> QECO에는 없는 action-level 보정 계층입니다. 기존 QECO가 DQN action을 그대로 실행한다면, QECO-ADAPT는 dense load 조건에서 불리한 offloading을 줄이기 위해 effective-load 기반 gating으로 action을 한 번 더 점검합니다.

### Q32. adaptive energy weight는 초기 딥러닝 가중치만을 결정하는가?

아니다. adaptive energy weight는 신경망의 초기 weight를 정하는 값이 아니다. DQN의 layer weight 초기화와는 별개이며, reward function 안에서 energy cost 항에 곱해지는 가중치이다.

QECO-ADAPT의 reward 계산은 다음 형태이다.

```text
C_i^adapt = 2 * (s_i * D_i + (1 - s_i) * w_E * E_i^scaled)
```

여기서 `w_E`가 adaptive energy weight이다. 이 값은 매 transition reward를 계산할 때 energy cost를 얼마나 강하게 반영할지 결정한다. 따라서 학습 초기만이 아니라 전체 training 과정에서 Q-learning target, TD error, Q-value 업데이트, 이후 action preference에 계속 영향을 준다.

현재 구현에서는 `w_E`가 episode마다 재학습되는 값은 아니지만, reward가 저장되는 모든 시점에 적용된다. 즉 "초기값"이 아니라 "학습 전 과정의 reward landscape를 바꾸는 scenario-level coefficient"이다.

짧게 답하면:

> adaptive energy weight는 딥러닝 모델의 초기 가중치가 아니라 reward 계산에 계속 들어가는 비용 계수입니다. 따라서 전체 학습 과정에서 Q-value가 어떤 action을 더 좋게 평가할지에 지속적으로 영향을 줍니다.

### Q33. adaptive energy weight는 기존 energy weight와 어떤 차별점이 있는 수식인가?

기존 QECO에는 명시적인 adaptive energy weight 수식이 없다. 기존 QECO의 energy term은 사실상 고정 weight로 reward cost에 들어간다.

기존 QECO:

```text
C_i = 2 * (s_i * D_i + (1 - s_i) * E_i^scaled)
```

QECO-ADAPT:

```text
w_E = w_0 * (1 + g(L_eff))^rho
C_i^adapt = 2 * (s_i * D_i + (1 - s_i) * w_E * E_i^scaled)
```

즉 기존 QECO를 `w_E = 1`인 고정 energy cost 구조로 보면, QECO-ADAPT는 `w_E`를 effective load에 따라 조정하는 구조이다.

이 수식을 사용한 이유는 세 가지이다.

첫째, `g(L_eff)`는 0과 1 사이에서 부하가 증가할수록 커지는 값이므로, dense load를 reward에 반영하기 쉽다.

둘째, `w_0`는 기본 energy-aware bias를 준다. 현재 `w_0 = 1.20`이므로 QECO-ADAPT는 기존 QECO보다 energy cost를 기본적으로 조금 더 민감하게 본다.

셋째, `rho = 0.35 < 1`을 사용해 증가 곡선을 sublinear하게 만들었다. 부하가 커진다고 energy penalty가 과도하게 폭증하면 QoE와 dropped-task가 악화될 수 있으므로, 완만하게 증가하도록 설계한 것이다.

짧게 답하면:

> 기존 QECO에는 부하에 따라 변하는 energy weight가 없었습니다. QECO-ADAPT는 effective load를 `g(L_eff)`로 정규화하고, `w_0(1+g)^rho` 형태로 energy penalty를 완만하게 키워 dense 환경에서 energy-aware behavior를 강화합니다.

## 9. 발표 중 피해야 할 표현

아래 표현은 질의응답에서 공격 포인트가 될 수 있으므로 피하는 것이 좋다.

| 피해야 할 표현 | 권장 표현 |
|---|---|
| QECO-ADAPT가 QECO를 완전히 대체한다 | dense MEC에서 QECO를 보완한다 |
| 모든 환경에서 QECO-ADAPT가 우수하다 | 3x 이상 dense 조건에서 유효성이 나타난다 |
| QECO 원문 환경을 그대로 재현했다 | 원문 edge당 밀도를 기준으로 단일 edge stress test를 구성했다 |
| policy-invariant reward shaping이다 | load-adaptive reward/cost reweighting이다 |
| a, b, gamma가 energy weight 곡선을 제어한다 | a_bar, b_bar는 effective load 입력값이고, w0, rho, lambda가 곡선을 제어한다 |
| adaptive energy weight가 딥러닝 초기 weight이다 | reward 계산에 계속 적용되는 energy cost 계수이다 |
| 평균 부하가 학습 중 자동으로 계속 업데이트된다 | 현재 구현에서는 시나리오 단위 고정 계수이며, 변하는 것은 observation과 DQN/LSTM 파라미터이다 |
| drop probability가 개선됐다 | 평균 dropped-task count가 개선됐다 |
| energy 최적화 알고리즘이다 | QoE-Delay-Energy-Drop 균형을 조정하는 알고리즘이다 |

## 10. 빠른 답변 모음

### "한 문장으로 기여를 말하면?"

> QECO-ADAPT는 원문 QECO의 구조를 유지하면서 effective load 기반 energy weight와 offloading gating을 추가해, 단일 edge dense 환경에서 초기 warm-up 손실과 dropped-task 누적을 줄이는 보완형 알고리즘입니다.

### "가장 중요한 결과는?"

> 1x에서는 QECO가 더 적합했지만, 3x부터는 전체 400 episode 평균 기준 QoE, Delay, Energy, Dropped tasks가 함께 개선됐고, 5x와 8x에서 개선폭이 가장 뚜렷했습니다.

### "왜 전체 평균을 보나?"

> QECO-ADAPT의 핵심 가치는 final-window 최고 성능이 아니라 초기 수렴 손실 완화이기 때문에, 전체 episode 평균이 알고리즘의 목적을 더 잘 반영합니다.

### "가장 큰 한계는?"

> 단일 seed와 단일 edge stress setup이므로, 다중 seed와 multi-edge 확장 실험을 통해 일반성을 더 검증해야 합니다.

### "정책 불변 shaping인가?"

> 아닙니다. energy cost와 실제 offloading action을 바꾸기 때문에 기존 QECO의 최적 정책 보존을 보장하지 않으며, load-adaptive reward/cost reweighting으로 설명하는 것이 맞습니다.

### "상수는 어떻게 정했나?"

> `lambda=10`, `w0=1.20`, `rho=0.35`, `alpha=4`는 닫힌형 최적해에서 나온 값이 아니라 공통 MEC 실험 환경에서 QECO의 completion reward scale을 유지하면서 부하 증가에 따른 energy-aware behavior를 유도하기 위한 calibration parameter입니다.

### "유사 논문이 있나?"

> QECO 자체와 동적 edge load를 다루는 D3QN/LSTM 계열 연구는 있습니다. 다만 QECO 구조를 유지한 채 effective-load 기반 gating과 adaptive energy weight를 붙인 동일한 QECO-ADAPT 구조는 확인하지 못했습니다.

### "평균 부하는 학습 중 계속 변하나?"

> 현재 구현에서는 아닙니다. effective load는 시나리오 단위 고정 계수이고, 학습 중 변하는 것은 관측 상태와 DQN/LSTM의 내부 파라미터입니다.

### "adaptive energy weight는 초기 weight인가?"

> 아닙니다. 신경망 초기값이 아니라 reward 계산에 계속 들어가는 energy cost 계수입니다.

## 11. 최종 방어 논리

발표 마지막 질의에서 연구의 의미를 다시 정리해야 할 때는 다음 흐름으로 답하면 된다.

1. 원문 QECO는 QoE 중심 offloading에서 강점이 있다.
2. 하지만 단일 edge dense stress 조건에서는 초기 warm-up 손실과 dropped-task 누적이 커질 수 있다.
3. QECO-ADAPT는 구조를 크게 바꾸지 않고 effective load 기반 energy weight와 gating을 추가한다.
4. 1x에서는 QECO가 더 적합했지만, 3x 이상에서는 전체 평균 기준 주요 지표가 함께 개선됐다.
5. 따라서 QECO-ADAPT는 QECO 대체제가 아니라 dense MEC 조건에서 선택적으로 사용할 수 있는 부하 적응형 보완 알고리즘이다.
