# Dense MEC 환경에서 QECO-ADAPT의 부하 적응형 오프로딩 성능 분석

## 1. 서론

모바일 엣지 컴퓨팅(Mobile Edge Computing, MEC)에서 연산 오프로딩은 QoE, Delay, Energy, 그리고 deadline 내 작업 완료를 함께 고려해야 하는 다목적 의사결정 문제이다. 이용자 수가 늘고 edge node에 작업 요청이 몰리면 처리 delay와 dropped task가 증가할 수 있으므로, dense MEC 환경에서는 에너지 절감만으로는 충분하지 않다. DROO는 wireless powered MEC에서 binary online offloading 기준선을 제시했으며[1], 기존 QECO는 task completion, delay, energy를 반영해 장기 QoE를 극대화하는 D3QN/LSTM 기반 알고리즘이다[2]. 무선 자원 관리에서는 학습 기반 최적화가 활용되며, online offloading에서는 queue stability와 stochastic task arrival가 중요하다. Tang and Wong의 DRL task offloading과 partial offloading 연구는 action 설계와 resource allocation 복잡성을 보여준다.

본 분석은 QECO를 대체하는 새 구조가 아니라, dense MEC 환경에서 초기 warm-up 손실을 낮추기 위한 보완형 변형인 QECO-ADAPT를 평가한다. QECO-ADAPT는 기존 QECO reward에 effective load 기반 energy weight와 offloading gating을 더한다.

## 2. 본론

### 2.1 실험 기준과 평가 방식

QECO 원문은 50 mobile devices (MDs)와 5 edge nodes (ENs)를 기본 평가 환경으로 사용하므로, edge당 평균 사용자 밀도는 10 MDs/EN이다[2]. 본 분석은 이를 기준 밀도 $d_0=10$으로 두고 edge 수를 1로 고정한 뒤, 사용자 수를 10, 30, 50, 80으로 늘렸다. 각 조건은 원문 기준 1x, 3x, 5x, 8x dense stress condition으로 해석된다.

주요 비교 기준은 전체 400 episode 평균이다. QECO-ADAPT의 목적은 최종 안정 구간에서 QECO를 압도하는 것이 아니라, 초반 warm-up 구간에 쌓이는 QoE 손실과 dropped-task count를 줄이는 데 있다. QoE는 높을수록 좋고, Delay, Energy, Dropped tasks, Runtime은 낮을수록 바람직하다. Dropped tasks는 drop probability가 아니라 episode별 deadline 내 미완료 task count이다. Final 10% 평균은 후반 안정 구간에서 QECO 성능을 얼마나 추종하는지 확인하는 보조 지표로 사용한다.

### 2.2 QECO-ADAPT의 부하 적응형 제어 구조

QECO-ADAPT는 사용자 수, 시간대별 task arrival profile, 사용자 활동성, edge 수를 이용해 edge 하나가 처리해야 하는 effective load를 산정한다[3]. 사용자 집합을 $\mathcal{U}=\{1,\ldots,N\}$, edge node 집합을 $\mathcal{E}=\{1,\ldots,M\}$, 시간대별 task 생성 profile을 $\mathbf{b}=(b_1,\ldots,b_K)$, 사용자별 활동성 계수를 $a_u\in[a_{\min},a_{\max}]$로 둔다. 사용자 $u$가 시간 $t$에 task를 생성할 확률은 다음과 같다.

$$
p_{\mathrm{arrive}}(u,t)
=\min\left(1,\max\left(0,b_{\kappa(t)}a_u\right)\right)
$$

평균 profile과 평균 사용자 활동성을 이용해 edge 하나가 평균적으로 처리하는 task pressure를 정의한다.

$$
\bar{b}=\frac{1}{K}\sum_{k=1}^{K}b_k,\qquad
\bar{a}=\frac{1}{N}\sum_{u=1}^{N}a_u
$$

$$
L_{\mathrm{eff}}=\frac{N\bar{b}\bar{a}}{M}
$$

$L_{\mathrm{eff}}$는 사용자 수가 늘면 증가하고, edge 수가 늘면 감소한다. 본 분석처럼 $M=1$인 경우 사용자 수 증가는 곧 단일 edge dense stress 증가로 이어진다. QECO-ADAPT는 이 유효 부하를 adaptive gating과 energy weight에 적용한다[4]. edge당 부하 scale constant를 $\lambda$라고 하면 gating strength는 다음과 같다.

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

여기서 unfinished task는 deadline 내 끝나지 않은 task이다. $\alpha=4$는 이론적 계수라기보다 기존 QECO 공개 구현의 completion reward scale을 공통 평가에서 보존한 calibration parameter로 해석한다. 본 설정에서는 $D_{\max}=10$이므로 $r_{\mathrm{done}}=40$이다. QECO-ADAPT는 completion reward scale은 유지하고, 부하에 따라 energy cost 항과 gating만 조절한다.

이 조절은 기존 QECO reward에 대한 policy-invariant reward shaping이 아니다. 부하가 증가하면 delay와 energy의 상대 가중치가 달라지며, QECO-ADAPT는 기존 QECO의 훈련 구조와 action space를 유지하되 보상 항과 offloading gating을 부하 조건에 따라 조절한다[5]. 학습 절차는 기존 QECO의 Dueling Double DQN과 LSTM 기반 load history 입력을 따르며, 즉시 보상 항에 기존 reward 대신 $r_t^{adapt}$가 포함된다.

### 2.3 전체 평균 성능 개선과 warm-up 손실 완화

다음 표는 전체 400 episode 평균 기준으로 QECO 대비 QECO-ADAPT의 변화량을 요약한 것이다. QoE는 증가가 이득이며, Delay, Energy, Dropped tasks, Runtime은 감소가 개선이다[1][6].

| Users | Density | ΔQoE | ΔDelay | ΔEnergy | ΔDropped tasks | ΔRuntime |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 10 | 1x | -2.1422 (-9.13%) | +0.2348 (-3.65%) | -1.0399 (+7.83%) | +13.0650 (-32.85%) | +0.0796 (-5.07%) |
| 30 | 3x | +1.2513 (+10.97%) | -0.1039 (+1.30%) | -1.0290 (+5.37%) | -21.3000 (+5.88%) | -0.1366 (+3.12%) |
| 50 | 5x | +2.6892 (+41.45%) | -0.1565 (+1.87%) | -2.4354 (+12.25%) | -79.0525 (+10.25%) | +0.7119 (-10.98%) |
| 80 | 8x | +3.3372 (+89.51%) | -0.1473 (+1.72%) | -3.6481 (+18.29%) | -154.8800 (+11.17%) | +1.0311 (-10.83%) |

1x 조건에서는 QECO-ADAPT가 Energy를 줄였지만 QoE, Delay, Dropped tasks 측면에서는 손실을 보였다. 이는 원문 QECO의 기본 edge당 밀도에서는 기존 QoE 중심 균형이 더 알맞다는 의미이다. 반면 3x부터는 QoE, Delay, Energy, Dropped tasks가 함께 개선되어, QECO-ADAPT가 초반 수렴 구간의 누적 손실을 줄이는 방향으로 작동함을 나타낸다.

![S2 full episode average comparison](./experiment_results/comparisons/user_30_ep_400_edge_1/comparison_averages.png)

**Fig. 1. Full-Episode Average Comparison under 3x Density.** **그림 1. 3x density 조건의 전체 episode 평균 비교.** `user=30, edge=1`에서 QECO-ADAPT는 전체 평균 기준 모든 핵심 지표를 개선한다.

5x와 8x 조건에서는 QoE 개선 폭과 Energy 절감 폭이 더 커졌다. `user=50, edge=1`은 QoE 41.45% 증가, Energy 12.25% 감소, Dropped tasks 10.25% 감소가 함께 나타나는 대표 구간이다. `user=80, edge=1`에서는 QoE를 89.51% 높이고, Energy를 18.29% 줄였으며, Dropped tasks도 11.17% 개선하였다. 다만 5x와 8x에서는 Runtime이 약 10% 내외로 증가하므로, 성능 향상과 계산 비용 증가의 trade-off를 함께 검토해야 한다.

![S4 full episode average comparison](./experiment_results/comparisons/user_50_ep_400_edge_1/comparison_averages.png)

**Fig. 2. Full-Episode Average Comparison under 5x Density.** **그림 2. 5x density 조건의 전체 episode 평균 비교.** `user=50, edge=1`은 QECO-ADAPT의 energy-aware control이 균형 있게 나타나는 조건이다.

![S6 full episode average comparison](./experiment_results/comparisons/user_80_ep_400_edge_1/comparison_averages.png)

**Fig. 3. Full-Episode Average Comparison under 8x Density.** **그림 3. 8x density 조건의 전체 episode 평균 비교.** 극고밀도 단일 edge에서도 QoE, Energy, Dropped tasks가 향상된다.

8x 조건에서는 전체 평균과 함께 smoothed time-series를 같이 보는 것이 중요하다. 본 실험에서 QECO-ADAPT는 Delay 기준 약 195 episode 이후, QoE 기준 약 272 episode 이후, Dropped tasks 기준 약 265 episode 이후 DROO보다 우세한 smoothed 성능을 유지하였다. 다만 Energy는 DROO가 전 구간에서 더 낮으므로, 이 결과는 에너지 단독 우세가 아니라 QoE-Delay-Drop 관점의 수렴 지향 우세로 해석해야 한다.

![S6 smoothed episode time-series comparison](./experiment_results/comparisons/user_80_ep_400_edge_1/comparison_timeseries_smoothed.png)

**Fig. 4. Smoothed Episode Time-Series Comparison under 8x Density.** **그림 4. 8x density 조건의 smoothed episode time-series 비교.** QECO-ADAPT의 이점은 final 구간의 단순 우세보다 episode 전반의 손실 누적 완화로 보는 것이 적절하다.

### 2.4 후반 안정 구간과 QECO 추종성

전체 episode 평균에서는 QECO-ADAPT의 이득이 크게 나타나지만, final 10% 평균에서는 차이가 작아진다. 예를 들어 `user=30, edge=1`은 전체 평균 기준으로 모든 주요 지표가 개선되지만, 후반 안정 구간에서는 QECO와 거의 같은 수준으로 수렴한다. 따라서 QECO-ADAPT의 핵심 가치는 최종 성능을 급격히 높이는 데보다 초반 warm-up 손실을 줄이는 데 있다. Final 10% 평균만 주 지표로 삼으면 이러한 개선 폭이 과소평가될 수 있다.

## 3. 결론

본 분석은 QECO 원문의 edge당 사용자 밀도 10 MDs/EN을 기준으로 edge 수를 1로 제한한 dense stress condition을 구성하고, QECO-ADAPT의 부하 적응형 제어 효과를 살펴보았다. QECO-ADAPT는 1x 저부하 조건에서는 QoE와 dropped-task count 측면에서 불리했지만, 3x 이상의 dense 조건에서는 전체 episode 평균 기준 QoE, Delay, Energy, Dropped tasks를 함께 개선하였다.

종합하면 QECO-ADAPT는 QECO를 모든 환경에서 대체하는 범용 알고리즘이 아니라, dense MEC 환경에서 초반 수렴 손실을 줄이고 후반에는 QECO 수준의 안정 정책을 따라가는 보완형 알고리즘으로 정의하는 것이 타당하다. 또한 QECO-ADAPT는 reward landscape를 조정하는 변형이므로, 기존 QoE 최적화 목표에서의 최적 정책이 그대로 유지된다고 이론적으로 보장하기는 어렵다. 향후에는 다중 seed, 목표 QoE 도달 episode, dropped-task 안정화 episode 같은 직접 수렴 지표를 추가해 warm-up 손실 감소 효과를 검증할 필요가 있다[3][7].

## 참고문헌

[1] L. Huang, S. Bi, and Y.-J. Angela Zhang, "Deep Reinforcement Learning for Online Computation Offloading in Wireless Powered Mobile-Edge Computing Networks," IEEE Transactions on Mobile Computing, vol. 19, no. 11, pp. 2581-2593, Nov. 2020, doi: 10.1109/TMC.2019.2928811.

[2] I. Rahmaty, H. Shah-Mansouri, and A. Movaghar, "QECO: A QoE-Oriented Computation Offloading Algorithm Based on Deep Reinforcement Learning for Mobile Edge Computing," IEEE Transactions on Network Science and Engineering, vol. 12, no. 4, pp. 3118-3130, 2025, doi: 10.1109/TNSE.2025.3556809.

[3] S. Bi, L. Huang, H. Wang, and Y.-J. A. Zhang, "Lyapunov-Guided Deep Reinforcement Learning for Stable Online Computation Offloading in Mobile-Edge Computing Networks," IEEE Transactions on Wireless Communications, vol. 20, no. 11, pp. 7519-7537, 2021, doi: 10.1109/TWC.2021.3085319.

[4] S. Chen and W. Jiang, "Online dynamic multi-user computation offloading and resource allocation for HAP-assisted MEC: an energy efficient approach," Journal of Cloud Computing, vol. 13, article 92, 2024, doi: 10.1186/s13677-024-00645-5.

[5] L. Sun, R. Liang, L. Wan, K. Liu, Z. Ning, and J. Wang, "Online Partial Computation Offloading Optimization in Wireless Powered Mobile Edge Computing Network," IEEE Transactions on Cognitive Communications and Networking, vol. 12, pp. 1481-1495, 2026, doi: 10.1109/TCCN.2025.3612741.

[6] M. Tang and V. W. Wong, "Deep Reinforcement Learning for Task Offloading in Mobile Edge Computing Systems," IEEE Transactions on Mobile Computing, vol. 21, no. 6, pp. 1985-1997, Jun. 2022, doi: 10.1109/TMC.2020.3036871.

[7] H. Sun, X. Chen, Q. Shi, M. Hong, X. Fu, and N. D. Sidiropoulos, "Learning to optimize: Training deep neural networks for wireless resource management," in Proc. IEEE SPAWC, 2017, pp. 1-6, doi: 10.1109/SPAWC.2017.8227766.
