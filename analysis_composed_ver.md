# QECO-ADAPT 분석 본문 구성안

## 1. 서론

모바일 엣지 컴퓨팅(Mobile Edge Computing, MEC) 환경에서 계산 오프로딩은 사용자 단말의 제한된 계산 능력과 배터리 제약을 완화하기 위한 핵심 기술이다. 그러나 사용자가 증가하고 단일 edge node에 작업 요청이 집중되면, edge node의 처리 부하가 커지고 task delay, energy consumption, deadline violation이 함께 증가할 수 있다. 특히 deadline-sensitive task가 존재하는 MEC 환경에서는 오프로딩 결정이 단순히 에너지 절감만을 목표로 할 수 없으며, 사용자 체감 품질(Quality of Experience, QoE), 지연 시간, 에너지 소비, dropped-task count를 동시에 고려해야 한다.

기존 QECO는 QoE-Oriented Computation Offloading을 목표로 하는 강화학습 기반 오프로딩 알고리즘으로, task completion, delay, energy를 함께 반영해 장기 QoE를 최대화하도록 설계된다. 이러한 QoE 중심 구조는 저부하 또는 일반적인 MEC 조건에서 안정적인 성능을 보이지만, 단일 edge node에 사용자가 집중되는 dense 환경에서는 학습 초반의 불안정성과 높은 부하에 따른 energy pressure가 동시에 나타날 수 있다. 즉 기존 QECO는 후반 안정 정책에서는 강점을 가지지만, 부하가 빠르게 증가하는 환경에서 warm-up 구간의 QoE 손실과 dropped-task 누적을 줄이는 데에는 추가적인 보완이 필요하다.

본 분석은 이러한 문제의식에서 출발하여 QECO-ADAPT의 단일 edge dense 환경 성능을 검토한다. QECO-ADAPT는 기존 QECO의 QoE reward 구조 위에 effective load 기반 energy weight와 offloading gating을 결합한 변형 알고리즘이다. 본 분석의 목적은 QECO-ADAPT가 기존 QECO를 모든 조건에서 대체할 수 있는지 확인하는 것이 아니라, 사용자 밀도가 증가하는 단일 edge 환경에서 QECO의 초반 수렴 손실을 줄이고, 이후 후반 안정 구간에서는 QECO의 성능을 얼마나 잘 따라가는지 확인하는 데 있다.

## 2. 본론

### 2.1 실험 기준과 평가 방식

QECO 원문은 기본 실험 환경으로 50 mobile devices (MDs)와 5 edge nodes (ENs)를 사용하므로, edge당 평균 사용자 밀도는 10 MDs/EN으로 볼 수 있다. 본 분석에서는 이 값을 기준 밀도 $d_0=10$으로 두고, edge 수를 1로 고정한 상태에서 사용자 수를 10, 30, 50, 80으로 증가시켰다. 따라서 각 조건은 원문 QECO의 edge당 사용자 밀도 대비 1x, 3x, 5x, 8x dense stress condition으로 해석된다. 이 방식은 edge 확장 효과를 제거하고, 단일 edge node가 감당해야 하는 사용자 밀도 증가가 QECO-ADAPT의 성능에 어떤 영향을 미치는지 직접 관찰하기 위한 구성이다.

본 분석에서는 전체 400 episode 평균을 주 비교 기준으로 사용한다. QECO-ADAPT의 핵심 이점은 최종 안정 구간에서의 일방적 우월성이 아니라, 학습 초반부터 QoE 손실과 dropped-task count 누적을 줄이는 수렴성에 있기 때문이다. 따라서 전체 episode 평균은 warm-up 구간에서의 손실까지 포함하는 지표로 사용한다. 반면 final 10% 평균은 후반 안정 구간에서 QECO-ADAPT가 기존 QECO의 성능을 얼마나 잘 따라가는지 확인하는 보조 지표로 해석한다.

평가 지표는 QoE, Delay, Energy, Dropped tasks, Runtime이다. QoE는 높을수록 좋고, Delay, Energy, Dropped tasks, Runtime은 낮을수록 좋다. 여기서 Dropped tasks는 전체 task 대비 drop probability가 아니라, 각 episode에서 deadline 내 완료되지 못한 task count의 평균값이다. 따라서 Dropped tasks의 변화율은 drop rate가 아니라 dropped-task count의 상대적 이득 또는 손실로 해석해야 한다.

### 2.2 QECO-ADAPT의 부하 적응형 제어 구조

QECO-ADAPT는 사용자 수, 시간대별 task arrival profile, 사용자 활동성, edge 수를 이용해 edge 하나가 감당해야 하는 effective load를 추정한다. 이 값은 단순 사용자 수가 아니라, 실제 task 발생 가능성과 edge 자원 수를 함께 반영한 부하 지표이다. 사용자 수가 증가하면 effective load는 증가하고, edge 수가 증가하면 edge당 부하는 감소한다. 본 분석은 edge 수를 1로 고정하므로 사용자 수 증가는 곧 단일 edge dense stress 증가로 연결된다.

부하 적응형 구성식은 다음과 같이 정리할 수 있다. 먼저 사용자 집합을 $\mathcal{U}=\{1,\ldots,N\}$, edge node 집합을 $\mathcal{E}=\{1,\ldots,M\}$으로 둔다. 여기서 $N$은 사용자 수, $M$은 edge node 수이다. 시간대별 기본 task 발생 profile은 $\mathbf{b}=(b_1,\ldots,b_K)$로 정의하며, 사용자별 활동성 계수는 $a_u\in[a_{\min},a_{\max}]$로 둔다. 사용자 $u$가 시간 $t$에 task를 발생시킬 확률은 다음과 같다.

$$
p_{\mathrm{arrive}}(u,t)
=\min\left(1,\max\left(0,b_{\kappa(t)}a_u\right)\right)
$$

여기서 $\kappa(t)$는 시간 $t$가 속한 task arrival profile index이다. 본 분석에서는 평균 task 발생 profile과 평균 사용자 활동성을 이용해 edge 하나가 감당하는 유효 부하를 다음과 같이 정의한다.

$$
\bar{b}=\frac{1}{K}\sum_{k=1}^{K}b_k,\qquad
\bar{a}=\frac{1}{N}\sum_{u=1}^{N}a_u
$$

$$
L_{\mathrm{eff}}=\frac{N\bar{b}\bar{a}}{M}
$$

이때 $L_{\mathrm{eff}}$는 edge 하나에 평균적으로 도착할 것으로 예상되는 task pressure를 의미한다. 즉 사용자 수 $N$이 증가하면 $L_{\mathrm{eff}}$는 커지고, edge 수 $M$이 증가하면 edge당 부하가 나뉘기 때문에 $L_{\mathrm{eff}}$는 작아진다. 본 분석처럼 $M=1$로 고정하면 사용자 수 증가가 곧 effective load 증가로 이어진다.

QECO-ADAPT는 이 유효 부하를 adaptive gating과 energy weight에 반영한다. edge당 부하 스케일 상수를 $\lambda$라고 하면, gating denominator에 들어가는 scale은 $c=M\lambda$로 정의된다. Adaptive gating strength는 다음과 같다.

$$
g(L_{\mathrm{eff}})
=\frac{L_{\mathrm{eff}}}{L_{\mathrm{eff}}+M\lambda}
$$

따라서 $g(L_{\mathrm{eff}})$는 $0$ 이상 $1$ 미만의 값을 가지며, 부하가 커질수록 증가한다. 이 값은 부하가 높아질 때 에너지 항을 더 민감하게 반영하기 위한 조절 계수로 사용된다. Adaptive energy weight는 다음과 같이 정의된다.

$$
w_E=w_0\left(1+g(L_{\mathrm{eff}})\right)^{\rho}
$$

여기서 $w_0$는 기본 energy weight, $\rho$는 부하 증가에 따른 weight 증가 곡률을 조절하는 exponent이다. 본 분석에서 사용한 값은 $w_0=1.20$, $\rho=0.35$, $\lambda=10$이다. $\rho<1$로 설정하면 부하가 증가하더라도 energy weight가 급격히 폭증하지 않고 완만하게 증가한다.

마지막으로 이 adaptive energy weight는 기존 QECO reward의 energy cost 항에 반영된다. task $i$의 scaled energy를 $E_i^{scaled}$, delay를 $D_i$, 단말 energy state를 $s_i$, 최대 허용 delay를 $D_{\max}$라고 하면, QECO-ADAPT의 비용 항과 reward는 다음과 같이 표현된다.

$$
C_i^{adapt}
=2\left(s_iD_i+(1-s_i)w_EE_i^{scaled}\right)
$$

$$
r_i^{adapt}=
\begin{cases}
-C_i^{adapt}, & \text{if unfinished}\\
4D_{\max}-C_i^{adapt}, & \text{otherwise}
\end{cases}
$$

여기서 unfinished task는 deadline 내 완료되지 못한 task를 의미한다. 따라서 QECO-ADAPT는 task가 완료되지 못한 경우에는 비용을 그대로 penalty로 부여하고, 완료된 경우에는 최대 허용 delay 기준 보상에서 adaptive cost를 차감한다. 이 구성식은 DQN의 전체 학습 과정이나 neural network parameter update를 새로 정의하는 식이 아니라, 기존 QECO 학습 구조 위에 추가된 부하 적응형 reward/control 항을 정의하는 식이다.

![QECO-ADAPT mathematical definitions](./experiment_results/formula_visualizations/qeco_adapt_math_definitions.png)

**그림 1. QECO-ADAPT의 부하 적응형 구성식.** Task arrival model, effective load, adaptive gating, adaptive energy reward의 정의를 요약한 그림이다. 이 그림은 DQN 전체 학습 과정이 아니라 QECO reward 위에 추가되는 adaptive control term을 설명한다.

QECO-ADAPT의 핵심은 부하가 증가할수록 energy-aware behavior를 강화하되, 기존 QECO의 action structure를 크게 바꾸지 않는다는 점이다. 기존 QECO reward에서 energy term에 adaptive energy weight를 적용하고, 부하가 큰 상황에서 과도한 오프로딩 또는 에너지 소비가 발생하지 않도록 보수화 강도를 조절한다. 이는 per-frame iterative solver를 추가하는 방식이 아니라 닫힌형 수식으로 penalty strength를 조정하는 방식이므로, 기존 QECO의 실행 구조를 유지하면서 부하 반응성을 추가할 수 있다.

### 2.3 전체 episode 평균 기준 성능 변화

다음 표는 전체 400 episode 평균 기준으로 QECO 대비 QECO-ADAPT의 변화량을 정리한 것이다. 괄호 안의 값은 성능 해석 기준의 상대 이득 또는 손실이다. QoE는 증가가 이득이므로 양수 변화가 좋고, Delay, Energy, Dropped tasks, Runtime은 감소가 이득이므로 값이 줄어들 때 괄호 안에 `+%`로 표시하였다.

| Users | Density | ΔQoE | ΔDelay | ΔEnergy | ΔDropped tasks | ΔRuntime |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 10 | 1x | -2.1422 (-9.13%) | +0.2348 (-3.65%) | -1.0399 (+7.83%) | +13.0650 (-32.85%) | +0.0796 (-5.07%) |
| 30 | 3x | +1.2513 (+10.97%) | -0.1039 (+1.30%) | -1.0290 (+5.37%) | -21.3000 (+5.88%) | -0.1366 (+3.12%) |
| 50 | 5x | +2.6892 (+41.45%) | -0.1565 (+1.87%) | -2.4354 (+12.25%) | -79.0525 (+10.25%) | +0.7119 (-10.98%) |
| 80 | 8x | +3.3372 (+89.51%) | -0.1473 (+1.72%) | -3.6481 (+18.29%) | -154.8800 (+11.17%) | +1.0311 (-10.83%) |

1x 조건에서는 QECO-ADAPT가 Energy를 줄였지만 QoE, Delay, Dropped tasks 측면에서 손실을 보였다. 이는 원문 QECO의 기본 edge당 밀도 수준에서는 기존 QECO의 QoE 중심 균형이 더 적합하다는 점을 의미한다. 낮은 부하에서는 adaptive energy penalty가 불필요하게 보수적으로 작동할 수 있으며, 에너지 절감 효과가 task completion 안정성 손실을 상쇄하지 못한다.

반면 3x 조건부터는 QECO-ADAPT의 이득이 뚜렷하게 나타난다. `user=30, edge=1`에서 QECO-ADAPT는 QoE를 10.97% 높이고, Delay, Energy, Dropped tasks, Runtime을 모두 개선하였다. 이 결과는 QECO-ADAPT가 단순히 후반 안정 구간에서 QECO보다 높은 최종 성능을 내는 알고리즘이라기보다, 학습 초반 구간에서 QoE 손실과 dropped-task count 누적을 줄이는 방향으로 작동한다는 점을 보여준다.

![S2 full episode average comparison](./experiment_results/comparisons/user_30_ep_400_edge_1/comparison_averages.png)

**그림 2. 3x density 조건의 전체 episode 평균 비교.** `user=30, edge=1` 조건에서 QECO-ADAPT는 전체 평균 기준 QoE, Delay, Energy, Dropped tasks, Runtime을 모두 개선한다.

5x 조건은 QECO-ADAPT의 장점이 가장 균형 있게 확인되는 대표 구간이다. `user=50, edge=1`에서 QECO-ADAPT는 QoE를 41.45% 높이고, Energy를 12.25% 줄였으며, Dropped tasks도 10.25% 개선하였다. Dense MEC에서 중요한 점은 에너지만 낮추는 것이 아니라, 에너지 절감이 task completion 손실로 이어지지 않아야 한다는 점이다. 이 조건에서 QECO-ADAPT는 Energy 절감과 QoE 개선, dropped-task count 감소를 함께 달성하므로, 단일 edge dense 환경에서 실질적인 적용 타당성이 가장 뚜렷하게 나타난다.

![S4 full episode average comparison](./experiment_results/comparisons/user_50_ep_400_edge_1/comparison_averages.png)

**그림 3. 5x density 조건의 전체 episode 평균 비교.** `user=50, edge=1` 조건은 QECO-ADAPT의 초반 수렴 이점과 energy-aware control이 함께 확인되는 대표 사례이다.

8x 조건에서는 모든 알고리즘이 강한 deadline pressure를 받는다. 그럼에도 `user=80, edge=1`에서 QECO-ADAPT는 QoE를 89.51% 높이고, Energy를 18.29% 줄였으며, Dropped tasks를 11.17% 개선하였다. 이 결과는 극고밀도 단일 edge 환경에서 QECO-ADAPT가 초반부터 혼잡 손실을 줄이고, 높은 부하에서도 QECO보다 더 효율적인 평균 정책 품질에 도달할 수 있음을 보여준다. 다만 Runtime은 5x와 8x 조건에서 각각 10% 내외의 손실이 발생하므로, 적용 시에는 성능 개선과 계산 비용 증가 사이의 trade-off를 함께 고려해야 한다.

![S6 full episode average comparison](./experiment_results/comparisons/user_80_ep_400_edge_1/comparison_averages.png)

**그림 4. 8x density 조건의 전체 episode 평균 비교.** 극고밀도 단일 edge 조건에서도 QECO-ADAPT는 전체 평균 기준 QoE, Energy, Dropped tasks를 개선한다.

### 2.4 후반 안정 구간과 QECO 추종성

전체 episode 평균에서는 QECO-ADAPT의 이득이 크게 나타나지만, final 10% 평균에서는 그 차이가 상대적으로 작아진다. 예를 들어 `user=30, edge=1` 조건에서는 전체 평균 기준 QECO-ADAPT가 QoE, Delay, Energy, Dropped tasks를 모두 개선하지만, 후반 안정 구간에서는 QECO와 거의 같은 수준으로 수렴한다. 이는 QECO-ADAPT의 이득이 후반 성능을 폭발적으로 높이는 데서 나오는 것이 아니라, 초반 warm-up 구간의 손실을 줄이는 데서 나온다는 점을 뒷받침한다.

따라서 QECO-ADAPT는 기존 QECO의 후반 안정 정책을 완전히 대체하는 알고리즘이라기보다, 초반 수렴 과정에서 발생하는 QoE 손실과 dropped-task count 누적을 줄이고 이후에는 QECO 수준의 안정 정책을 따라가는 보완형 알고리즘으로 해석하는 것이 적절하다. 이러한 특성은 동적 MEC 환경에서 환경 변화 후 재학습이 필요하거나, 사용자가 갑자기 증가하는 dense 상황에서 정책 warm-up 비용을 줄이는 장점으로 연결될 수 있다.

## 3. 결론

본 분석은 QECO 원문의 edge당 사용자 밀도 10 MDs/EN을 기준으로 단일 edge dense stress condition을 구성하고, QECO-ADAPT가 사용자 밀도 증가에 따라 어떤 성능 변화를 보이는지 평가하였다. 분석 결과, QECO-ADAPT는 1x 저부하 조건에서는 QECO 대비 QoE와 dropped-task count 측면에서 불리했다. 이는 부하가 낮은 환경에서는 기존 QECO의 QoE 중심 reward 균형이 더 적합하며, adaptive energy penalty가 오히려 task completion 안정성을 해칠 수 있음을 의미한다.

그러나 3x 이상의 dense 조건에서는 QECO-ADAPT의 효과가 명확하게 나타났다. 전체 episode 평균 기준으로 `user=30`부터 QoE, Delay, Energy, Dropped tasks가 동시에 개선되었고, `user=50`과 `user=80`에서는 QoE 개선 폭과 Energy 절감 폭이 더 커졌다. 특히 5x와 8x 조건에서는 dropped-task count도 10% 이상 감소하여, 단일 edge에 사용자 부하가 집중되는 상황에서 QECO-ADAPT의 부하 적응형 제어가 실질적인 의미를 가진다는 점을 확인하였다.

종합하면 QECO-ADAPT는 QECO를 모든 환경에서 대체하는 범용 알고리즘이 아니다. 오히려 저부하에서는 기존 QECO가 더 안정적이며, QECO-ADAPT는 dense MEC 환경에서 초반 수렴 손실을 줄이고 후반에는 QECO 수준의 안정 정책을 따라가는 보완형 알고리즘으로 정의하는 것이 타당하다. 향후에는 다중 seed 반복 실험, 목표 QoE 도달 episode, dropped-task 안정화 episode와 같은 직접적인 수렴 지표를 추가하여 QECO-ADAPT의 warm-up 손실 감소 효과를 더 엄밀하게 검증할 필요가 있다.
