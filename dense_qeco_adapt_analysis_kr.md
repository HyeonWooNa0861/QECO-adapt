# Dense MEC 환경에서 QECO-ADAPT의 이점 분석 보고서

## 1. 보고서 목적

본 보고서는 공통 MEC 평가 환경에서 관찰된 QECO-ADAPT의 이점을 dense 상황에 초점을 맞추어 정리한다. 여기서 dense 상황은 단순히 사용자 수가 많은 경우만을 의미하지 않는다. 사용자 수가 증가하거나, edge 하나가 처리해야 하는 평균 task arrival pressure가 커지거나, 다중 edge 환경에서도 전체 system load가 높아져 offloading decision의 작은 차이가 QoE, delay, energy, drop에 동시에 영향을 주는 조건을 의미한다. 본 실험에서는 `user=50`, `user=80` 조건을 중심으로 dense 상황을 해석하되, `user=30` 조건은 중간 부하 전이 구간으로 함께 참고한다.

QECO-ADAPT는 QECO의 QoE-oriented reward 구조를 유지하면서, effective load에 따라 energy penalty와 offloading 보수화 강도를 조절하는 변형 알고리즘이다. 따라서 이 알고리즘의 핵심 가치는 모든 시나리오에서 무조건 가장 높은 성능을 내는 데 있지 않다. 더 정확한 장점은 부하가 커지는 구간에서 QoE와 delay를 크게 훼손하지 않으면서 energy와 drop을 동시에 낮추는 방향으로 정책을 조정한다는 점이다. 이는 dense MEC 환경에서 중요한 의미를 가진다. 사용자가 적거나 edge 자원이 충분한 환경에서는 기존 QECO의 균형 정책만으로도 충분하지만, 사용자가 증가하고 deadline violation 위험이 커질수록 단순 QoE 최대화만으로는 energy와 drop의 동시 관리가 어려워질 수 있기 때문이다.

## 2. Dense 시나리오에서의 핵심 관찰

QECO-ADAPT의 장점은 `user=50` 이상 조건에서 비교적 명확하게 나타난다. 특히 `S4: user=50, edge=1`에서는 QECO 대비 QoE가 `+2.12%` 증가했고, delay는 `-0.47%`, energy는 `-2.53%`, drop은 `-2.03%` 감소하였다. 이 결과는 단일 edge가 많은 사용자를 처리해야 하는 고부하 조건에서 QECO-ADAPT가 단순히 energy를 줄이는 데 그치지 않고, QoE와 drop까지 동시에 개선할 수 있음을 보여준다. 즉 S4는 QECO-ADAPT가 dense 단일 edge 환경에서 가장 설득력 있게 작동한 대표 사례이다.

`S5: user=50, edge=10`은 edge 수가 충분히 많은 조건이지만, 전체 사용자 수가 높아 system-level load가 여전히 큰 시나리오이다. 이 조건에서 QECO-ADAPT는 QECO 대비 QoE를 `+1.87%` 높였고, delay를 `-1.35%`, energy를 `-1.39%`, drop을 `-6.31%` 줄였다. 특히 drop 감소 폭이 상대적으로 크다는 점이 중요하다. edge가 늘어나면 단순히 처리 자원이 증가하기 때문에 모든 알고리즘이 이득을 볼 수 있지만, QECO-ADAPT는 이 상황에서도 task completion 안정성을 더 확보하는 방향으로 작동했다. 이는 adaptive penalty가 오프로딩 결정을 과도하게 억제하기보다, edge 자원 증가와 load pressure 사이에서 적절한 균형점을 찾는 데 기여했을 가능성을 시사한다.

추가 dense 비교점인 `user=50, edge=3`에서도 유사한 경향이 확인된다. 이 조건에서 QECO-ADAPT는 QECO 대비 QoE를 `+1.32%` 높였고, delay를 `-0.38%`, energy를 `-0.18%`, drop을 `-2.04%` 낮추었다. runtime은 `+4.71%` 증가했지만, 이는 S4와 S5에서 관찰된 runtime 증가보다 낮은 수준이다. 이 결과는 edge가 1개에서 10개로 크게 증가하는 극단 조건뿐 아니라, 중간 수준의 edge 확장 조건에서도 QECO-ADAPT가 QoE와 drop을 동시에 개선할 수 있음을 보여준다.

`S6: user=80, edge=1`은 매우 높은 부하의 단일 edge 조건이다. 이 경우 QECO-ADAPT는 QECO 대비 QoE를 `+1.82%` 개선했고, energy를 `-5.42%` 줄였다. drop 감소는 `-0.65%`로 크지는 않았지만, 사용자가 80명으로 증가한 극단적 단일 edge 환경에서 QoE와 energy를 동시에 개선했다는 점은 의미가 있다. 이 시나리오에서는 모든 알고리즘이 높은 drop 수준을 피하기 어렵기 때문에, QECO-ADAPT의 장점은 drop을 급격히 낮추는 것보다 같은 혼잡 조건에서 energy pressure를 줄이면서 QoE를 유지하는 데 있다.

`S7: user=80, edge=3`에서는 QECO-ADAPT가 QECO 대비 QoE `+1.94%`, delay `-0.68%`, energy `-1.14%`, drop `-2.37%`를 기록했다. 또한 runtime도 `-0.29%`로 거의 동일하거나 소폭 낮았다. 이 결과는 dense 환경에서도 edge 수가 어느 정도 확보되면 QECO-ADAPT의 adaptive load control이 더 안정적으로 작동할 수 있음을 보여준다. 즉 QECO-ADAPT는 단일 edge 극한 상황뿐 아니라, 다중 edge 고부하 환경에서도 QoE-delay-energy-drop 균형을 개선하는 방향으로 효과를 보였다.

## 3. QECO-ADAPT가 dense 상황에서 유리한 이유

첫째, QECO-ADAPT는 사용자 수와 edge 수를 동시에 반영한 effective load를 사용한다. 단순 사용자 수만으로 penalty를 키우면 edge 수가 많은 환경에서도 지나치게 보수적인 정책이 될 수 있다. 반대로 edge 수만 고려하면 실제 task arrival pressure를 충분히 반영하지 못한다. QECO-ADAPT는 사용자 수, base arrival profile, user activity, edge 수를 결합해 edge당 평균 부하를 계산하고, 이 값에 따라 energy weight를 조절한다. 이 구조는 dense MEC 환경에서 자원 압박을 보다 직접적으로 반영한다.

둘째, QECO-ADAPT의 energy control은 급격한 penalty가 아니라 완만한 adaptive weight 증가로 설계되어 있다. 이 점은 dense 상황에서 특히 중요하다. 높은 부하에서 energy penalty를 과도하게 강화하면 offloading이 지나치게 보수화되어 QoE와 drop이 악화될 수 있다. 반면 penalty가 너무 약하면 QECO와 거의 동일하게 동작해 dense 상황의 energy pressure를 줄이지 못한다. 본 실험에서 QECO-ADAPT가 S4, S5, S6, S7에서 QoE를 유지하거나 개선하면서 energy와 drop을 함께 낮춘 것은 이러한 완만한 조절 구조가 어느 정도 유효했음을 보여준다.

셋째, QECO-ADAPT는 CD와 같은 반복 최적화 기반 방법을 추가하지 않고도 dense 상황에 반응한다. CD는 `user=10`, `edge=1`, `episode=400` 보조 실험에서도 trimmed median runtime이 `14.3218s`로 QECO 계열보다 약 10배 길었다. 반면 QECO-ADAPT는 기존 QECO의 실행 흐름 위에 닫힌형 adaptive 계산을 더하는 방식이므로, runtime이 QECO와 같은 초 단위 범위에 머문다. S4, S5, S6에서는 QECO보다 runtime이 증가했지만, 그 차이는 약 `8%~11%` 수준이며 CD와 같은 구조적 병목과는 성격이 다르다. 특히 S7에서는 QECO-ADAPT의 runtime이 QECO보다 소폭 낮게 측정되었다.

## 4. Dense 환경에서의 해석상 한계

QECO-ADAPT의 이점은 dense 상황에서 강화되지만, 이것이 모든 조건에서 QECO-ADAPT가 우월하다는 뜻은 아니다. `S2: user=30, edge=1`에서는 energy와 delay는 개선되었지만 QoE가 `-0.40%` 낮아지고 drop이 `+1.95%` 증가했다. 이는 중간 부하 단일 edge 조건에서 adaptive penalty가 아직 충분한 이득으로 이어지지 않을 수 있음을 보여준다. 또한 `S3: user=30, edge=3`에서는 QoE와 drop은 개선되었지만 energy가 `+0.84%` 증가했다. 따라서 QECO-ADAPT는 저부하 또는 중간 전이 구간에서 항상 더 좋은 선택이라기보다, 부하가 높아지고 energy-drop trade-off가 중요해지는 구간에서 장점이 커지는 알고리즘으로 해석해야 한다.

또한 현재 분석은 단일 seed 기반 공통 평가 결과를 중심으로 한다. dense 환경에서의 장점을 더 엄밀하게 주장하려면 다중 seed 반복 실험, 목표 QoE 도달 episode, drop 안정화 episode, queue length 또는 deadline violation ratio 같은 추가 지표가 필요하다. 본 보고서의 결론은 현재 comparison 결과에 기반한 중간 분석이며, 최종 논문에서는 그림 자료와 함께 이러한 한계를 명시하는 것이 바람직하다.

## 5. 그림 삽입 계획

본 보고서는 텍스트 중심으로 구성되며, 이후 본문 또는 부록에 그림을 추가하면 총 3~4페이지 분량으로 확장될 수 있다. 우선 삽입할 그림은 dense 시나리오 중심으로 구성하는 것이 적절하다. 첫 번째 그림은 `S4: user=50, edge=1`의 average, final, runtime, smoothed time-series를 묶은 그래프가 적합하다. 이 시나리오는 QECO-ADAPT가 QoE, delay, energy, drop을 동시에 개선한 대표 사례이기 때문이다. 두 번째 그림은 추가 dense 비교점인 `user=50, edge=3` 또는 `S7: user=80, edge=3`을 제시하는 것이 좋다. `user=50, edge=3`은 중간 수준의 edge 확장에서 QECO-ADAPT의 균형 개선을 보여주고, S7은 더 높은 사용자 수의 다중 edge dense 환경에서 QoE, delay, energy, drop이 함께 개선되는 결과를 보여준다. 필요하면 S6를 추가해 극단적 단일 edge 부하에서 energy 개선 효과가 나타난다는 점을 보조할 수 있다.

## 6. 결론

Dense MEC 상황에서 QECO-ADAPT의 핵심 이점은 QoE를 크게 희생하지 않으면서 energy와 drop을 함께 조절하는 데 있다. S4, S5, S6, S7 결과는 사용자 수가 증가하거나 edge당 부하가 커질수록 QECO-ADAPT가 기존 QECO보다 더 나은 균형점을 찾을 수 있음을 보여준다. 특히 S4와 S7은 QECO-ADAPT의 장점을 가장 명확하게 보여주는 시나리오이다. S4는 고부하 단일 edge 환경에서 QECO 대비 QoE, delay, energy, drop을 모두 개선했고, S7은 매우 높은 사용자 수와 다중 edge 조건에서도 같은 방향의 개선을 보였다.

따라서 QECO-ADAPT는 모든 MEC 환경에서 범용적으로 우월한 알고리즘이라기보다, dense condition에서 부하 적응형 energy control을 통해 QoE-delay-energy-drop 균형을 개선하는 환경 민감형 변형 알고리즘으로 정의하는 것이 타당하다. 이 관점은 본 연구의 주장 방향과도 잘 맞는다. 즉 QECO-ADAPT의 학술적 기여는 기존 QECO를 대체하는 새로운 절대 우위 알고리즘이 아니라, QoE 기반 DRL 오프로딩 정책에 dense-aware adaptive control을 결합해 고부하 MEC 조건에서 더 안정적인 운영 균형을 제공한다는 점에 있다.
