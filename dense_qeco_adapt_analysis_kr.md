# 단일 엣지 Dense 증가에 따른 QECO-ADAPT 이점 분석 자료

## 1. 분석 목적과 범위

본 자료는 논문 본문에 대한 해설 보고서가 아니라, 현재 공통 실험 결과 지표를 바탕으로 `QECO-ADAPT`가 dense 상황에서 어떤 이점을 가지는지 정리한 별도 분석 자료이다. 분석 범위는 단일 edge 환경으로 제한한다. 즉 edge 수는 항상 `1`로 고정하고, 사용자 수만 `10`, `30`, `50`, `80`으로 증가시켜 사용자 밀도 증가에 따른 성능 변화를 비교한다. 이 설정은 edge 확장 효과를 제거하고, 단일 edge가 감당해야 하는 부하가 증가할 때 QECO-ADAPT가 기존 QECO 대비 어떤 방향으로 작동하는지를 보기 위한 것이다.

비교 기준은 기존 QECO와 QECO-ADAPT의 마지막 10% episode 평균 지표이다. 사용한 지표는 `QoE`, `Delay`, `Energy`, `Drop`, `Runtime`이며, `QoE`는 높을수록 좋고 `Delay`, `Energy`, `Drop`, `Runtime`은 낮을수록 좋다. 본 분석에서 dense 상황은 단순히 사용자가 많다는 뜻이 아니라, 단일 edge에 집중되는 task 처리 부담이 커지고 deadline violation 및 energy pressure가 함께 증가하는 조건을 의미한다.

## 2. 단일 edge 사용자 증가 실험 결과

아래 표는 `edge=1`에서 사용자 수가 증가할 때 QECO 대비 QECO-ADAPT의 변화량을 정리한 것이다. 괄호 안의 비율은 QECO 대비 상대 변화율이다.

| Users | ΔQoE | ΔDelay | ΔEnergy | ΔDrop | ΔRuntime | 해석 |
| ---: | ---: | ---: | ---: | ---: | ---: | --- |
| 10 | -1.7895 (-6.54%) | +0.3271 (+5.74%) | -0.9622 (-7.56%) | +10.9500 (+63.48%) | +0.0796 (+5.07%) | 저부하에서는 energy 절감 외 이점이 약하고 drop 악화가 큼 |
| 30 | -0.0709 (-0.40%) | -0.0129 (-0.17%) | -0.3169 (-2.06%) | +4.8500 (+1.95%) | -0.1366 (-3.12%) | 전이 구간으로, energy와 delay는 개선되나 drop은 아직 악화 |
| 50 | +0.2907 (+2.12%) | -0.0367 (-0.47%) | -0.3488 (-2.53%) | -11.3750 (-2.03%) | +0.7119 (+10.98%) | dense 단일 edge에서 QoE, delay, energy, drop이 모두 개선 |
| 80 | +0.2094 (+1.82%) | -0.0344 (-0.42%) | -0.6711 (-5.42%) | -6.6750 (-0.65%) | +1.0311 (+10.83%) | 극고부하에서 QoE와 energy 개선이 유지되며 drop도 소폭 완화 |

이 표에서 가장 중요한 변화는 사용자 수가 `50` 이상일 때 나타난다. `user=10`에서는 QECO-ADAPT가 energy를 줄이지만 QoE, delay, drop이 악화된다. 이 결과는 저부하 단일 edge 환경에서는 adaptive energy penalty가 오히려 과도하게 보수적인 방향으로 작동할 수 있음을 보여준다. 즉 QECO-ADAPT는 낮은 부하에서 QECO를 대체하기 위한 알고리즘이라기보다, 부하가 충분히 커졌을 때 효과가 나타나는 dense-aware 변형으로 보는 것이 적절하다.

`user=30`은 전이 구간이다. QECO-ADAPT는 QECO 대비 delay를 `0.17%`, energy를 `2.06%`, runtime을 `3.12%` 줄였지만 QoE는 `0.40%` 낮아졌고 drop은 `1.95%` 증가했다. 이 구간에서는 부하가 증가하기 시작했지만, QECO-ADAPT의 보수화가 task completion 안정성으로 충분히 연결되지는 못했다. 따라서 `user=30, edge=1`은 QECO-ADAPT의 이점이 부분적으로만 나타나는 경계 조건으로 해석할 수 있다.

`user=50`에서는 양상이 바뀐다. QECO-ADAPT는 QoE를 `2.12%` 높이고, delay를 `0.47%`, energy를 `2.53%`, drop을 `2.03%` 낮췄다. 이는 단일 edge에서 사용자 밀도가 충분히 높아졌을 때 QECO-ADAPT가 단순 energy 절감형 정책이 아니라 QoE와 drop까지 함께 개선하는 방향으로 작동할 수 있음을 보여주는 핵심 결과이다. 특히 dense 상황에서는 energy만 낮추고 drop이 늘어나면 실사용 이점이 약해지는데, `user=50`에서는 energy와 drop이 동시에 감소했다는 점이 중요하다.

`user=80`에서는 단일 edge가 처리해야 하는 부하가 매우 커진다. 이 조건에서 QECO-ADAPT는 QoE를 `1.82%` 높였고 energy를 `5.42%` 줄였다. drop 감소는 `0.65%`로 크지 않지만, 극단적인 혼잡 조건에서 drop을 크게 낮추기는 어렵다는 점을 고려하면 QoE와 energy 개선이 동시에 유지된 것은 의미가 있다. 즉 `user=80`에서는 QECO-ADAPT의 이점이 drop 대폭 감소보다는 energy pressure 완화와 QoE 유지에 더 강하게 나타난다.

## 3. Dense 증가에 따른 QECO-ADAPT의 동작 해석

단일 edge 환경에서 사용자 수가 증가하면 edge 하나가 처리해야 하는 task arrival pressure가 직접적으로 커진다. 이때 기존 QECO는 QoE 중심의 균형 정책을 유지하지만, 부하 증가에 따른 energy pressure를 별도로 조절하는 구조는 제한적이다. QECO-ADAPT는 effective load를 기반으로 energy weight와 보수화 강도를 조절하므로, 사용자 수가 증가할수록 energy-aware behavior가 더 강해진다.

다만 이 adaptive behavior는 항상 긍정적으로 작동하지 않는다. `user=10`에서는 task 처리 여유가 상대적으로 크기 때문에 보수적인 energy control이 QoE와 drop 측면에서 손실로 나타난다. `user=30`에서는 일부 지표가 개선되지만 drop이 아직 악화된다. 따라서 QECO-ADAPT의 효과는 부하가 낮은 구간에서는 제한적이며, 단일 edge 기준으로는 `user=50` 이상에서 본격적으로 장점이 나타난다고 볼 수 있다.

이 관점에서 `user=50`은 QECO-ADAPT의 dense threshold를 보여주는 중요한 지점이다. 이 구간에서 QoE, delay, energy, drop이 모두 QECO 대비 개선되기 때문이다. 특히 QoE가 증가하면서 energy와 drop이 동시에 감소했다는 점은 dense MEC 환경에서 실질적이다. 일반적으로 energy를 줄이려는 정책은 처리 지연이나 drop을 증가시킬 위험이 있고, drop을 줄이려는 정책은 더 많은 자원 사용을 유발할 수 있다. 그러나 `user=50, edge=1`에서는 QECO-ADAPT가 이 trade-off를 비교적 안정적으로 조절했다.

`user=80`에서는 drop 자체가 매우 큰 수준으로 올라가기 때문에 모든 알고리즘이 deadline pressure를 강하게 받는다. 이 상황에서는 QECO-ADAPT가 drop을 대폭 줄이기보다는 energy를 크게 줄이고 QoE를 보존 또는 개선하는 쪽으로 장점이 나타난다. 따라서 극고밀도 단일 edge 환경에서 QECO-ADAPT의 주요 이점은 task completion을 급격히 회복하는 것보다, 심한 혼잡 속에서도 energy cost를 낮추고 QoE를 유지하는 데 있다고 해석할 수 있다.

## 4. Runtime 관점

QECO-ADAPT는 `user=50`과 `user=80`에서 QECO 대비 runtime이 약 `11%` 증가했다. 이는 단일 edge dense 구간에서 얻는 QoE, energy, drop 개선과 함께 고려해야 하는 비용이다. 다만 이 runtime 증가는 CD와 같은 반복 최적화 기반 알고리즘의 구조적 overhead와는 성격이 다르다. QECO-ADAPT는 기존 QECO 실행 흐름에 닫힌형 adaptive weighting을 추가하는 방식이므로, runtime은 여전히 QECO와 같은 초 단위 범위에 머문다.

따라서 단일 edge dense 환경에서 QECO-ADAPT의 선택 기준은 명확하다. 계산 시간이 최우선이고 부하가 낮다면 QECO가 더 적합할 수 있다. 반대로 사용자 수가 충분히 증가해 energy와 drop의 동시 관리가 중요해지는 구간에서는 약 `10%` 내외의 runtime 증가를 감수하고도 QECO-ADAPT를 사용할 근거가 생긴다. 특히 `user=50`에서는 QoE, delay, energy, drop이 모두 개선되었기 때문에 runtime 증가를 감수할 수 있는 실험적 근거가 가장 강하다.

## 5. 결론

단일 edge dense 증가 실험에서 QECO-ADAPT는 저부하 환경보다 고부하 환경에서 더 뚜렷한 이점을 보였다. `user=10`에서는 energy 절감은 있었지만 QoE와 drop이 크게 악화되어 QECO-ADAPT의 적용 이점이 약했다. `user=30`에서는 energy와 delay가 개선되었으나 QoE와 drop 측면에서는 아직 불안정했다. 반면 `user=50`부터는 QoE, delay, energy, drop이 동시에 개선되었고, `user=80`에서도 QoE와 energy 개선이 유지되었다.

따라서 현재 결과 지표 기준으로 QECO-ADAPT의 핵심 장점은 단일 edge dense 상황에서 나타나는 부하 적응형 energy-drop 조절 능력이다. 특히 `user=50, edge=1`은 QECO-ADAPT의 이점이 가장 균형 있게 확인된 대표 조건이며, `user=80, edge=1`은 극고부하에서도 energy 절감과 QoE 개선이 유지되는 조건이다. 이를 바탕으로 QECO-ADAPT는 “저부하 범용 대체 알고리즘”이라기보다, 단일 edge가 높은 사용자 밀도를 감당해야 하는 dense MEC 환경에서 QECO의 QoE 중심 정책을 보완하는 적응형 변형 알고리즘으로 정의하는 것이 적절하다.
