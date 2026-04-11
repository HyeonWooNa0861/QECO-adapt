# QECO-ADAPT 수식 삽입용 텍스트

아래 수식은 논문, 보고서, 발표자료에 복사해 넣기 쉽도록 Markdown/LaTeX 형태로 정리한 것이다.

## 1. 짧은 삽입본

```latex
\[
\mathcal{U}=\{1,2,\ldots,N\},\quad \mathcal{E}=\{1,2,\ldots,M\}
\]

\[
p_{\mathrm{arrive}}(u,t)
=\operatorname{clip}\left(b_{\kappa(t)}a_u,0,1\right)
=\min\left(1,\max\left(0,b_{\kappa(t)}a_u\right)\right)
\]

\[
\bar{b}=\frac{1}{K}\sum_{k=1}^{K}b_k,\quad
\bar{a}=\frac{1}{N}\sum_{u=1}^{N}a_u
\]

\[
L_{\mathrm{eff}}=\frac{N\bar{b}\bar{a}}{M}
\]

\[
c=M\lambda,\quad
g(L_{\mathrm{eff}})
=\frac{L_{\mathrm{eff}}}{L_{\mathrm{eff}}+c}
=\frac{L_{\mathrm{eff}}}{L_{\mathrm{eff}}+M\lambda}
\]

\[
w_E=w_0\left(1+g(L_{\mathrm{eff}})\right)^{\rho}
\]

\[
E_i^{\mathrm{scaled}}
=10\cdot \operatorname{Normalize}
\left(E_i^{\mathrm{comp}}+E_i^{\mathrm{trans}};0,20\right)
\]

\[
C_i^{\mathrm{adapt}}
=2\left(s_iD_i+(1-s_i)w_EE_i^{\mathrm{scaled}}\right)
\]

\[
r_i^{\mathrm{adapt}}
=
\begin{cases}
-C_i^{\mathrm{adapt}}, & \text{if task } i \text{ is unfinished},\\
4D_{\max}-C_i^{\mathrm{adapt}}, & \text{otherwise}.
\end{cases}
\]
```

## 2. 본문 설명 포함 삽입본

```latex
Let \(\mathcal{U}=\{1,2,\ldots,N\}\) denote the set of mobile users and
\(\mathcal{E}=\{1,2,\ldots,M\}\) denote the set of edge nodes. The time-dependent
base arrival profile is defined as
\[
\mathbf{b}=(b_1,b_2,\ldots,b_K),\quad 0\le b_k\le 1,
\]
and the activity coefficient of user \(u\) is denoted by
\[
a_u\in[a_{\min},a_{\max}],\quad u\in\mathcal{U}.
\]
The task arrival probability of user \(u\) at time slot \(t\) is then defined as
\[
p_{\mathrm{arrive}}(u,t)
=\operatorname{clip}\left(b_{\kappa(t)}a_u,0,1\right)
=\min\left(1,\max\left(0,b_{\kappa(t)}a_u\right)\right),
\]
where \(\kappa(t)\in\{1,\ldots,K\}\) maps time slot \(t\) to the corresponding
base-profile segment.

The average base arrival intensity and the average user activity are given by
\[
\bar{b}=\frac{1}{K}\sum_{k=1}^{K}b_k,\quad
\bar{a}=\frac{1}{N}\sum_{u=1}^{N}a_u.
\]
When user activities are uniformly assigned between \(a_{\min}\) and \(a_{\max}\),
\(\bar{a}\) can be approximated as
\[
\bar{a}\approx\frac{a_{\min}+a_{\max}}{2}.
\]
The effective load handled by each edge node is defined as
\[
L_{\mathrm{eff}}=\frac{N\bar{b}\bar{a}}{M}.
\]

To convert the effective load into an adaptive control coefficient, QECO-ADAPT
defines the scale constant \(c\) and the gating strength \(g(L_{\mathrm{eff}})\) as
\[
c=M\lambda,
\]
\[
g(L_{\mathrm{eff}})
=\frac{L_{\mathrm{eff}}}{L_{\mathrm{eff}}+c}
=\frac{L_{\mathrm{eff}}}{L_{\mathrm{eff}}+M\lambda}.
\]
Since
\[
\frac{\partial g}{\partial L_{\mathrm{eff}}}
=\frac{M\lambda}{(L_{\mathrm{eff}}+M\lambda)^2}>0,
\]
the gating strength monotonically increases with the effective load while
remaining bounded in \([0,1)\).

The adaptive energy weight is defined as
\[
w_E=w_0\left(1+g(L_{\mathrm{eff}})\right)^{\rho},
\]
where \(w_0\) is the base energy weight and \(\rho\) controls the curvature of
the adaptive increase.

For task \(i\), the scaled energy term is computed as
\[
E_i^{\mathrm{scaled}}
=10\cdot \operatorname{Normalize}
\left(E_i^{\mathrm{comp}}+E_i^{\mathrm{trans}};0,20\right).
\]
The adaptive cost and reward are defined as
\[
C_i^{\mathrm{adapt}}
=2\left(s_iD_i+(1-s_i)w_EE_i^{\mathrm{scaled}}\right),
\]
\[
r_i^{\mathrm{adapt}}
=
\begin{cases}
-C_i^{\mathrm{adapt}}, & \text{if task } i \text{ is unfinished},\\
4D_{\max}-C_i^{\mathrm{adapt}}, & \text{otherwise}.
\end{cases}
\]
```

## 3. 본 실험 상수

```latex
\[
\mathbf{b}=(0.18,0.30,0.42,0.24),\quad
a_{\min}=0.7,\quad
a_{\max}=1.3
\]

\[
\bar{b}=0.285,\quad
\bar{a}=1.0,\quad
\lambda=10,\quad
w_0=1.20,\quad
\rho=0.35
\]
```

## 4. 기호 설명

| 기호 | 의미 |
| --- | --- |
| \(N\) | 사용자 수 |
| \(M\) | edge node 수 |
| \(\mathcal{U}\) | 사용자 집합 |
| \(\mathcal{E}\) | edge node 집합 |
| \(\mathbf{b}\) | 시간대별 base task arrival profile |
| \(b_k\) | \(k\)번째 base profile 값 |
| \(a_u\) | 사용자 \(u\)의 활동성 계수 |
| \(p_{\mathrm{arrive}}(u,t)\) | 사용자 \(u\), 시간 \(t\)의 task arrival probability |
| \(L_{\mathrm{eff}}\) | edge 하나가 평균적으로 감당하는 effective load |
| \(\lambda\) | edge당 load scale base |
| \(c\) | gating scale constant |
| \(g(L_{\mathrm{eff}})\) | adaptive gating strength |
| \(w_E\) | adaptive energy weight |
| \(w_0\) | base energy weight |
| \(\rho\) | energy weight 증가 곡률 exponent |
| \(s_i\) | task \(i\)를 처리하는 사용자 단말의 energy state |
| \(D_i\) | task \(i\)의 processing delay |
| \(D_{\max}\) | 최대 허용 delay |
| \(C_i^{\mathrm{adapt}}\) | QECO-ADAPT 비용 항 |
| \(r_i^{\mathrm{adapt}}\) | QECO-ADAPT reward |

## 5. 상수 설정 근거 삽입본

```text
The constants used in QECO-ADAPT are calibration parameters for the common MEC
experiment rather than closed-form optimal values. The base arrival profile
\(\mathbf{b}=(0.18,0.30,0.42,0.24)\) is chosen so that its mean
\(\bar{b}=0.285\) remains close to the original task arrival probability of
0.3, while still introducing time-of-day variation. The activity range
\([a_{\min},a_{\max}]=[0.7,1.3]\) represents heterogeneous user behavior while
preserving the average activity \(\bar{a}=1.0\).

The parameter \(\lambda=10\) is a per-edge load scale, not the full gating
constant. The actual scale constant is \(c=M\lambda\), where \(M\) is the number
of edge nodes. Therefore, when more edge nodes are available, the per-edge load
\(L_{\mathrm{eff}}=N\bar{b}\bar{a}/M\) decreases while the scale constant
\(c=M\lambda\) increases. These two effects jointly reduce the gating strength
and prevent unnecessary conservative offloading when edge capacity is sufficient.

The base energy weight \(w_0=1.20\) gives QECO-ADAPT a mild energy-aware bias
relative to the original QECO reward. The exponent \(\rho=0.35<1\) makes the
increase of the adaptive energy penalty sublinear with respect to the gating
strength. This prevents the energy penalty from growing too aggressively as the
number of users increases, thereby reducing the risk of degrading QoE and Drop.
```
