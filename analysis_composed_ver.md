# QECO-ADAPT 분석 본문 구성안

## 1. 서론

모바일 엣지 컴퓨팅(Mobile Edge Computing, MEC)에서 연산 오프로딩은 단말의 한정된 계산 능력과 배터리 제약을 줄이는 주요 기술이다. 그러나 이용자 수가 늘어나고 단일 edge node에 작업 요청이 몰리면 처리 delay, deadline violation, dropped task가 동시에 증가할 수 있다[6]. 따라서 deadline-sensitive MEC 환경에서는 에너지 절감뿐 아니라 QoE, Delay, Energy, Dropped tasks를 함께 살펴야 한다.

기존 QECO는 task completion, delay, energy를 반영해 장기 QoE를 극대화하는 D3QN/LSTM 기반 오프로딩 알고리즘이다[2]. 본 분석은 QECO를 모든 조건에서 대체하는 신규 구조를 제시하기보다, 단일 edge dense 환경에서 QECO의 초기 수렴 손실을 낮추기 위한 보완형 변형인 QECO-ADAPT를 살펴본다. QECO-ADAPT는 기존 QECO reward 위에 effective load 기반 energy weight와 offloading gating을 더한다.

비교 대상 중 DROO는 wireless powered MEC의 binary online offloading 및 계산 시간 절감 측면의 baseline으로만 사용한다[1]. 본문에서 제시하는 QoE, Delay, Dropped tasks는 각 원논문의 지표를 그대로 대조한 것이 아니라, 공통 MEC 평가 환경에서 동일 지표로 재측정한 결과이다.

## 2. 본론

### 2.1 실험 기준과 평가 방식

QECO 원문은 50 mobile devices (MDs)와 5 edge nodes (ENs)를 기본 평가 환경으로 사용하므로, edge당 평균 사용자 밀도는 10 MDs/EN이다[2]. 본 분석은 이를 기준 밀도 $d_0=10$으로 두고, edge 수를 1로 고정한 조건에서 사용자 수를 10, 30, 50, 80으로 늘렸다. 각 조건은 원문 기준 1x, 3x, 5x, 8x dense stress condition으로 볼 수 있다.

주요 비교 기준은 전체 400 episode 평균이다. QECO-ADAPT의 요지는 최종 안정 구간의 일방적 우월성이 아니라, 초반 warm-up 구간에서 쌓이는 QoE 손실과 dropped-task count를 줄이는 데 있기 때문이다. QoE는 높을수록 좋고, Delay, Energy, Dropped tasks, Runtime은 낮을수록 바람직하다. Dropped tasks는 drop probability가 아니라 episode별 deadline 내 완료되지 않은 task count이다.

따라서 전체 평균은 학습 초반의 탐색과 수렴 지연을 포함한 실용적 성능 지표로 사용하고, final 10% 평균은 후반 안정 구간에서 기존 QECO의 성능을 어느 정도 추종하는지 확인하는 보조 지표로 둔다. 이 구분은 QECO-ADAPT의 장점이 최종 수렴값 자체보다 warm-up 손실 감소에 있는지를 판단하기 위한 기준이다.

### 2.2 QECO-ADAPT의 부하 적응형 제어 구조

QECO-ADAPT는 사용자 수, 시간대별 task arrival profile, 사용자 활동성, edge 수를 활용해 edge 하나가 처리해야 하는 effective load를 산정한다. 사용자 집합을 $\mathcal{U}=\{1,\ldots,N\}$, edge node 집합을 $\mathcal{E}=\{1,\ldots,M\}$으로 두고, 시간대별 task 생성 profile을 $\mathbf{b}=(b_1,\ldots,b_K)$, 사용자별 활동성 계수를 $a_u\in[a_{\min},a_{\max}]$로 둔다. 사용자 $u$가 시간 $t$에 task를 생성할 확률은 다음과 같다.

$$
p_{\mathrm{arrive}}(u,t)
=\min\left(1,\max\left(0,b_{\kappa(t)}a_u\right)\right)
$$

여기서 $\kappa(t)$는 시간 $t$가 속한 task arrival profile index이다. 평균 profile과 평균 사용자 활동성은 아래와 같다.

$$
\bar{b}=\frac{1}{K}\sum_{k=1}^{K}b_k,\qquad
\bar{a}=\frac{1}{N}\sum_{u=1}^{N}a_u
$$

이를 바탕으로 edge 하나가 평균적으로 처리하는 task pressure를 다음과 같이 정의한다.

$$
L_{\mathrm{eff}}=\frac{N\bar{b}\bar{a}}{M}
$$

$L_{\mathrm{eff}}$는 사용자 수가 늘면 증가하고, edge 수가 늘면 감소한다. 본 분석처럼 $M=1$인 경우 사용자 수 증가는 곧 단일 edge dense stress 증가로 이어진다. 온라인 MEC에서 stochastic task arrival, wireless quality, queue backlog를 함께 고려해야 한다는 관점은 관련 연구에서도 반복적으로 제시된다[4][5].

QECO-ADAPT는 이 유효 부하를 adaptive gating과 energy weight에 적용한다. edge당 부하 scale constant를 $\lambda$라고 하면, gating strength는 다음과 같다.

$$
g(L_{\mathrm{eff}})
=\frac{L_{\mathrm{eff}}}{L_{\mathrm{eff}}+M\lambda}
$$

$g(L_{\mathrm{eff}})$는 load가 높아질수록 증가하며, 높은 부하에서 energy-aware behavior를 강화하는 계수로 활용된다. Adaptive energy weight는 다음과 같다.

$$
w_E=w_0\left(1+g(L_{\mathrm{eff}})\right)^{\rho}
$$

본 분석에서는 $w_0=1.20$, $\rho=0.35$, $\lambda=10$을 사용한다. $\rho<1$은 부하 증가에 따른 energy weight 상승을 완화해 QoE와 Drop의 급격한 저하를 줄이기 위한 설정이다.

이 weight는 QECO reward의 energy cost 항에 들어간다. task $i$의 scaled energy를 $E_i^{scaled}$, delay를 $D_i$, 단말 energy state를 $s_i$, 허용 최대 delay를 $D_{\max}$라고 하면 비용 항과 reward는 다음과 같다.

$$
C_i^{adapt}
=2\left(s_iD_i+(1-s_i)w_EE_i^{scaled}\right)
$$

$$
r_{\mathrm{done}}=\alpha D_{\max},\quad \alpha=4
$$

$$
r_i^{adapt}=
\begin{cases}
-C_i^{adapt}, & \text{if unfinished}\\
r_{\mathrm{done}}-C_i^{adapt}, & \text{otherwise}
\end{cases}
$$

여기서 unfinished task는 deadline 내 끝나지 않은 task이다. $\alpha=4$는 이론적으로 유도된 계수라기보다 기존 QECO 공개 구현의 completion reward scale을 공통 평가에서 보존한 calibration parameter로 해석한다. QECO-ADAPT는 completion reward scale은 유지하고, energy cost 항의 $w_E$와 부하 기반 gating만 조절한다.

본 설정에서는 $D_{\max}=10$이므로 $r_{\mathrm{done}}=40$이다. 이 값은 delay 및 scaled energy cost와 비교해 task completion 자체가 충분히 큰 양의 보상으로 기능하도록 하는 margin이며, QECO-ADAPT의 차이는 completion reward가 아니라 부하에 따른 energy cost 재가중에 있다.

이 조절은 기존 QECO reward에 대한 policy-invariant reward shaping이 아니다. 부하가 증가할수록 delay와 energy 사이의 상대 가중치가 달라지므로, QECO-ADAPT의 정책은 기존 QoE objective를 그대로 최적화한 정책이라기보다 dense 환경의 energy pressure와 dropped-task 누적을 낮추도록 다시 가중한 surrogate reward에 대한 정책이다. 따라서 QoE, Delay, Energy, Dropped tasks를 함께 제시해 trade-off를 확인한다.

학습 절차는 기존 QECO의 Dueling Double DQN과 LSTM 기반 load history 입력을 따른다[2]. 다만 즉시 보상 항에 기존 QECO reward 대신 $r_t^{adapt}$가 포함되므로, adaptive energy weight와 gating 효과가 Q-learning target에 반영된다. 본 연구는 새로운 network 구조가 아니라 기존 QECO 실행 구조를 유지한 lightweight adaptation으로 정의된다. 이는 partial offloading이나 per-frame iterative solver를 추가하지 않고 부하 반응성을 더한다는 점에서 연산 부담을 제한한다[1][3][7].

시점 $t$의 관측 상태를 $o_t$, edge-load history를 $h_t$, 선택 action을 $a_t$라고 하면 replay에 기록되는 experience는 다음과 같이 요약할 수 있다.

$$
e_t=\left(o_t,h_t,a_t,r_t^{adapt},o_{t+1},h_{t+1}\right)
$$

Double DQN target은 evaluation network로 다음 action을 고르고 target network로 그 값을 평가하는 구조를 보존한다.

$$
y_j
=r_j^{adapt}
+\gamma Q\left(
o_{j+1},h_{j+1},
\arg\max_{a\in\mathcal{A}}Q(o_{j+1},h_{j+1},a;\theta);
\theta^{-}
\right)
$$

Mini-batch loss는 다음과 같다.

$$
\mathcal{L}(\theta)
=\frac{1}{B}\sum_{j=1}^{B}
\left(y_j-Q(o_j,h_j,a_j;\theta)\right)^2
$$

이 세 식은 QECO-ADAPT가 별도 최적화 solver가 아니라 replay transition의 reward 항을 통해 기존 QECO 학습 루프에 들어간다는 점을 나타낸다.

### 2.3 전체 episode 평균 기준 성능 변화

다음 표는 전체 400 episode 평균 기준으로 QECO 대비 QECO-ADAPT의 변화량을 요약한 것이다. QoE는 증가가 이득이며, Delay, Energy, Dropped tasks, Runtime은 감소가 개선이다.

괄호 안의 값은 성능 해석 기준의 상대 개선 또는 손실이다. 예를 들어 Energy와 Dropped tasks는 값이 낮아질수록 좋으므로, 음수 변화량이 성능 측면에서 이득으로 표시된다. 이 표는 final-window 성능보다 전체 학습 과정에서 누적된 손실 감소를 확인하기 위한 정리이다.

| Users | Density | ΔQoE | ΔDelay | ΔEnergy | ΔDropped tasks | ΔRuntime |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 10 | 1x | -2.1422 (-9.13%) | +0.2348 (-3.65%) | -1.0399 (+7.83%) | +13.0650 (-32.85%) | +0.0796 (-5.07%) |
| 30 | 3x | +1.2513 (+10.97%) | -0.1039 (+1.30%) | -1.0290 (+5.37%) | -21.3000 (+5.88%) | -0.1366 (+3.12%) |
| 50 | 5x | +2.6892 (+41.45%) | -0.1565 (+1.87%) | -2.4354 (+12.25%) | -79.0525 (+10.25%) | +0.7119 (-10.98%) |
| 80 | 8x | +3.3372 (+89.51%) | -0.1473 (+1.72%) | -3.6481 (+18.29%) | -154.8800 (+11.17%) | +1.0311 (-10.83%) |

1x 조건에서는 QECO-ADAPT가 Energy를 줄였지만 QoE, Delay, Dropped tasks 측면에서는 손실을 보였다. 이는 원문 QECO의 기본 edge당 밀도에서는 기존 QoE 중심 균형이 더 알맞다는 의미이다. 반면 3x부터는 QoE, Delay, Energy, Dropped tasks가 함께 개선되어, QECO-ADAPT가 초반 수렴 구간의 누적 손실을 줄이는 방향으로 작동함을 나타낸다.

![S2 full episode average comparison](./experiment_results/comparisons/user_30_ep_400_edge_1/comparison_averages.png)

**그림 1. 3x density 조건의 전체 episode 평균 비교.** `user=30, edge=1`에서 QECO-ADAPT는 전체 평균 기준 모든 핵심 지표를 개선한다.

`user=30, edge=1`은 QECO-ADAPT가 실질적으로 작동하기 시작하는 첫 구간이다. QoE는 10.97% 증가했고, Delay, Energy, Dropped tasks, Runtime도 모두 나아졌다. 마지막 10% 평균만 보면 차이가 작아 보일 수 있지만, 전체 평균에서는 초반 수렴 손실이 줄어드는 효과가 확인된다.

5x와 8x 조건에서는 QoE 개선 폭과 Energy 절감 폭이 더 커졌다. 특히 `user=50, edge=1`은 QoE 41.45% 증가, Energy 12.25% 감소, Dropped tasks 10.25% 감소가 함께 나타나는 대표 구간이다. Dense MEC에서 중요한 점은 에너지를 낮추면서도 task completion 손실을 키우지 않는 것인데, 이 조건에서는 두 방향의 개선이 동시에 관찰된다.

![S4 full episode average comparison](./experiment_results/comparisons/user_50_ep_400_edge_1/comparison_averages.png)

**그림 2. 5x density 조건의 전체 episode 평균 비교.** `user=50, edge=1`은 QECO-ADAPT의 energy-aware control이 가장 균형 있게 나타나는 조건이다.

![S6 full episode average comparison](./experiment_results/comparisons/user_80_ep_400_edge_1/comparison_averages.png)

**그림 3. 8x density 조건의 전체 episode 평균 비교.** 극고밀도 단일 edge에서도 QoE, Energy, Dropped tasks가 향상된다.

`user=80, edge=1`에서는 모든 알고리즘이 강한 deadline pressure를 받는다. 그럼에도 QECO-ADAPT는 QoE를 89.51% 높이고, Energy를 18.29% 줄였으며, Dropped tasks도 11.17% 개선하였다. 다만 5x와 8x에서는 Runtime이 약 10% 내외로 증가하므로, 적용 시 성능 향상과 계산 비용 증가의 trade-off를 함께 검토해야 한다.

8x 조건에서는 전체 평균과 함께 smoothed time-series를 같이 보는 것이 중요하다. 그림 4의 25-episode moving average 기준으로 QECO-ADAPT는 학습이 진행되면서 DROO 대비 Delay, QoE, Dropped tasks 성능을 순차적으로 넘어선다. 본 실험에서는 Delay 기준 약 195 episode 이후, QoE 기준 약 272 episode 이후, Dropped tasks 기준 약 265 episode 이후 DROO보다 우세한 smoothed 성능을 유지하였다. 다만 Energy는 DROO가 전 구간에서 더 낮으므로, 이 결과는 에너지 단독 우세가 아니라 QoE-Delay-Drop 관점의 수렴 지향 우세로 해석해야 한다.

![S6 smoothed episode time-series comparison](./experiment_results/comparisons/user_80_ep_400_edge_1/comparison_timeseries_smoothed.png)

**그림 4. 8x density 조건의 smoothed episode time-series 비교.** QECO-ADAPT의 이점은 final 구간의 단순 우세보다 episode 전반의 손실 누적 완화로 보는 것이 적절하다.

### 2.4 후반 안정 구간과 QECO 추종성

전체 episode 평균에서는 QECO-ADAPT의 이득이 크게 나타나지만, final 10% 평균에서는 차이가 작아진다. 예를 들어 `user=30, edge=1`은 전체 평균 기준으로 모든 주요 지표가 개선되지만, 후반 안정 구간에서는 QECO와 거의 같은 수준으로 수렴한다. 따라서 QECO-ADAPT의 핵심 가치는 최종 성능을 급격히 높이는 데보다 초반 warm-up 손실을 줄이는 데 있다.

이 특성 때문에 QECO-ADAPT는 기존 QECO의 후반 안정 정책을 완전히 대체하는 알고리즘이라기보다, 초반 수렴 과정에서 발생하는 QoE 손실과 dropped-task count 누적을 줄이고 이후에는 QECO 수준의 안정 정책을 따라가는 보완형 알고리즘으로 보는 것이 적절하다. 이는 환경 변화 후 재학습이 필요하거나 사용자가 갑자기 증가하는 dense MEC 상황에서 정책 warm-up 비용을 낮추는 장점으로 이어질 수 있다.

따라서 final 10% 평균만을 주 지표로 삼으면 QECO-ADAPT의 개선 폭이 과소평가될 수 있다. 본 분석에서 전체 episode 평균을 함께 제시하는 이유는, 학습 과정에서 발생하는 누적 QoE 손실과 dropped-task count 감소를 직접 확인하기 위해서이다.

## 3. 결론

본 분석은 QECO 원문의 edge당 사용자 밀도 10 MDs/EN을 기준으로 단일 edge dense stress condition을 구성하고, QECO-ADAPT의 부하 적응형 제어 효과를 살펴보았다. 결과적으로 QECO-ADAPT는 1x 저부하 조건에서는 QoE와 dropped-task count 측면에서 불리했지만, 3x 이상의 dense 조건에서는 전체 episode 평균 기준 QoE, Delay, Energy, Dropped tasks를 함께 개선하였다.

특히 `user=30`부터 개선이 나타났고, `user=50`과 `user=80`에서는 QoE 개선 폭과 Energy 절감 폭이 더 커졌다. 이는 단일 edge에 사용자 부하가 집중되는 상황에서 부하 기반 energy weight와 gating이 초반 혼잡 손실을 완화하는 방향으로 작동했음을 보여준다. 반대로 저부하에서는 adaptive energy penalty가 불필요하게 보수적으로 작동할 수 있으므로, QECO-ADAPT의 유효 구간은 환경 의존적으로 판단해야 한다.

종합하면 QECO-ADAPT는 QECO를 모든 환경에서 대체하는 범용 알고리즘이 아니라, dense MEC 환경에서 초반 수렴 손실을 줄이고 후반에는 QECO 수준의 안정 정책을 따라가는 보완형 알고리즘으로 정의하는 것이 타당하다. 또한 이는 기존 QECO objective의 무손실 개선이 아니라 reward landscape를 부하 적응적으로 다시 가중하는 방식이므로, 원래 QoE 최적 정책의 보존을 이론적으로 보장하지 않는다. 향후에는 다중 seed, 목표 QoE 도달 episode, dropped-task 안정화 episode 같은 직접 수렴 지표를 추가해 warm-up 손실 감소 효과를 검증할 필요가 있다.

## 참고문헌

[1] L. Huang, S. Bi, and Y.-J. Angela Zhang, "Deep Reinforcement Learning for Online Computation Offloading in Wireless Powered Mobile-Edge Computing Networks," IEEE Transactions on Mobile Computing, vol. 19, no. 11, pp. 2581-2593, Nov. 2020, doi: 10.1109/TMC.2019.2928811.
인용 용도: DROO baseline의 원논문 및 online binary offloading/계산 시간 단축 근거.
원문 근거: binary offloading policy와 computation time 축소.

[2] I. Rahmaty, H. Shah-Mansouri, and A. Movaghar, "QECO: A QoE-Oriented Computation Offloading Algorithm Based on Deep Reinforcement Learning for Mobile Edge Computing," IEEE Transactions on Network Science and Engineering, vol. 12, no. 4, pp. 3118-3130, 2025, doi: 10.1109/TNSE.2025.3556809.
인용 용도: QECO의 QoE reward, D3QN/LSTM 구조, 50 MDs/5 ENs 평가 설정 근거.
원문 근거: task completion rate, task delay, energy consumption을 반영한 QoE와 50 MDs/5 ENs 설정.

[3] H. Sun, X. Chen, Q. Shi, M. Hong, X. Fu, and N. D. Sidiropoulos, "Learning to optimize: Training deep neural networks for wireless resource management," in Proc. IEEE SPAWC, 2017, pp. 1-6, doi: 10.1109/SPAWC.2017.8227766.
인용 용도: 반복 최적화 기반 무선 자원 관리의 real-time computational cost 및 learning-based approximation 근거.

[4] S. Bi, L. Huang, H. Wang, and Y.-J. A. Zhang, "Lyapunov-Guided Deep Reinforcement Learning for Stable Online Computation Offloading in Mobile-Edge Computing Networks," IEEE Transactions on Wireless Communications, vol. 20, no. 11, pp. 7519-7537, 2021, doi: 10.1109/TWC.2021.3085319.
인용 용도: time-varying channel, stochastic task arrival, queue stability가 online MEC에서 중요하다는 근거.

[5] S. Chen and W. Jiang, "Online dynamic multi-user computation offloading and resource allocation for HAP-assisted MEC: an energy efficient approach," Journal of Cloud Computing, vol. 13, article 92, 2024, doi: 10.1186/s13677-024-00645-5.
인용 용도: dynamic task arrival, wireless communication quality, energy-efficient online offloading/resource allocation 근거.

[6] M. Tang and V. W. Wong, "Deep Reinforcement Learning for Task Offloading in Mobile Edge Computing Systems," IEEE Transactions on Mobile Computing, vol. 21, no. 6, pp. 1985-1997, Jun. 2022, doi: 10.1109/TMC.2020.3036871.
인용 용도: edge load 증가가 processing delay와 deadline expiration/drop으로 연결될 수 있다는 근거.

[7] L. Sun, R. Liang, L. Wan, K. Liu, Z. Ning, and J. Wang, "Online Partial Computation Offloading Optimization in Wireless Powered Mobile Edge Computing Network," IEEE Transactions on Cognitive Communications and Networking, vol. 12, pp. 1481-1495, 2026, doi: 10.1109/TCCN.2025.3612741.
인용 용도: partial offloading의 유연성과 그에 따른 online optimization/resource scheduling 복잡성 근거.
부가 설명: 본 연구의 QECO-ADAPT는 partial offloading처럼 action space를 확장하지 않고, 기존 QECO의 action structure를 유지한 채 effective load에 따라 energy penalty와 offloading 보수화 강도를 조정하는 lightweight adaptation으로 차별화된다.
