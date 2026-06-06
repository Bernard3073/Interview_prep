# Week 5 — State Estimation & Filtering

> Sensors are noisy and arrive over time. Filtering fuses a motion model with
> measurements to maintain a best estimate **and its uncertainty**.

---

## 1. The recursive Bayes filter

Everything below is a special case of:

```
predict:  bel⁻(xₜ) = ∫ p(xₜ | xₜ₋₁, uₜ) bel(xₜ₋₁) dxₜ₋₁
update:   bel(xₜ)  ∝ p(zₜ | xₜ) · bel⁻(xₜ)
```
- **Predict** pushes belief through the **motion model** (uncertainty grows).
- **Update** multiplies in the **measurement likelihood** (uncertainty shrinks).
- Different assumptions on these distributions → KF, EKF, UKF, particle filter.

---

## 2. Kalman Filter (linear, Gaussian)

![Kalman predict/update loop](images/kalman-loop.svg)

Assumes linear motion/measurement and Gaussian noise. State `x ~ N(x̂, P)`.

```
Predict:   x̂⁻ = F x̂ + B u
           P⁻  = F P Fᵀ + Q
Update:    K   = P⁻ Hᵀ (H P⁻ Hᵀ + R)⁻¹      (Kalman gain)
           x̂   = x̂⁻ + K (z − H x̂⁻)            (innovation = z − H x̂⁻)
           P   = (I − K H) P⁻
```
- `F` motion, `H` measurement, `Q` process noise, `R` measurement noise.
- **Kalman gain** `K` interpolates between prediction and measurement based on
  relative confidence: noisy sensor (`R` large) → trust prediction, and vice versa.
- It is the **optimal** estimator under the linear-Gaussian assumptions.

> The whole filter is "weighted average of prediction and measurement, weighted by
> their covariances." If you can say that, you understand it.

---

## 3. Extended Kalman Filter (EKF)

Real motion/measurement models are nonlinear. EKF **linearizes** them with
Jacobians at the current estimate:

```
x̂⁻ = f(x̂, u)                 F = ∂f/∂x |x̂
z_pred = h(x̂⁻)               H = ∂h/∂x |x̂⁻
(then same gain/update equations as KF, using F and H)
```
- Pros: cheap, ubiquitous (robot localization, VIO, GPS/IMU fusion).
- Cons: linearization error → can diverge if highly nonlinear or poorly
  initialized; Jacobians are error-prone to derive.

## 4. Unscented Kalman Filter (UKF)

Instead of linearizing, propagate a deterministic set of **sigma points** through
the nonlinear function and recompute mean/covariance.
- More accurate than EKF for strong nonlinearity, no Jacobians needed.
- Slightly more compute; same Gaussian assumption.

## 5. Particle Filter (Monte Carlo)

Represent the belief by **weighted samples** — handles non-Gaussian, multimodal
beliefs (e.g. the "kidnapped robot" / global localization).

```
for each particle: propagate via motion model (+noise)
weight by measurement likelihood p(z|x)
resample proportional to weight  (deal with particle depletion)
```
- Used in **Monte Carlo Localization (AMCL)** on known maps.
- Cost grows with state dimension (curse of dimensionality) → great in 2D/3D pose,
  not for high-D states.

---

## 6. Making filters actually work

- **Tuning `Q` and `R`:** too-small `R` → overconfident, ignores good sensor; too
  small `Q` → filter "locks up" and lags reality. Start from sensor datasheets.
- **Innovation gating:** reject measurements whose Mahalanobis distance is too
  large (outlier/false association).
- **Consistency:** check **NEES/NIS** — is the actual error consistent with the
  reported covariance? An "optimistic" filter (P too small) is dangerous.
- **Observability:** is the state even recoverable from the measurements? (e.g.
  monocular VIO scale needs motion/excitation).

---

## Interview-style questions
1. Derive the Kalman gain — what is it trading off?
2. EKF vs. UKF vs. particle filter: when does each break down?
3. What is the innovation, and how do you use it to reject outliers?
4. Your EKF diverges. List the things you'd check.
5. Why can't a particle filter scale to a 12-D state?
6. What does it mean for a filter to be "inconsistent / overconfident"?

## Resources
- Thrun, Burgard, Fox, *Probabilistic Robotics* — Ch. 2–4, 7–8 (the canonical text).
- Roger Labbe, *Kalman and Bayesian Filters in Python* — free, interactive notebooks.
- Cyrill Stachniss filtering lectures (YouTube).

➡ **Coding:** `coding-practice/robotics/w5_kalman_1d.py`, `w5_ekf_localization.py`
