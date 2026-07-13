# Week 4 — Math Foundations

> The goal of this week is not to relearn all of math, but to make the handful of
> operations that show up *everywhere* in perception feel automatic: SVD, least
> squares, Gaussians, and iterative optimization.

---

## 1. Linear algebra you actually use

### Vectors & matrices
- A matrix is a **linear map**. `y = A x` sends vector `x` to `y`.
- **Dot product** `a·b = |a||b|cosθ` → projection, similarity, angle.
- **Cross product** `a×b` → a vector perpendicular to both; magnitude = area of
  parallelogram. In robotics it appears as the **skew-symmetric matrix** `[a]ₓ`:

```
        [  0  -a3   a2 ]
[a]ₓ =  [  a3   0  -a1 ]      so that  a × b = [a]ₓ b
        [ -a2  a1   0  ]
```

### Eigen-decomposition
- `A v = λ v`: `v` is a direction unchanged by `A` (only scaled by `λ`).
- For a **symmetric** matrix (e.g. a covariance), eigenvectors are orthogonal and
  eigenvalues are real → principal axes of an ellipsoid. This is the backbone of
  PCA and uncertainty visualization.

### Singular Value Decomposition (SVD) — *the* perception workhorse
```
A = U Σ Vᵀ          U, V orthogonal;  Σ diagonal ≥ 0 (singular values)
```
Why you keep meeting it:
- **Solve homogeneous systems** `A x = 0` (8-point algorithm, homography,
  triangulation): the solution is the right-singular vector of the **smallest**
  singular value (last column of `V`).
- **Best rank-k approximation** (Eckart–Young) → denoising, enforcing rank-2 on a
  fundamental matrix.
- **Pseudo-inverse** `A⁺ = V Σ⁺ Uᵀ` → least squares.
- **Orthogonal Procrustes**: best rotation aligning two point sets (used in ICP).

> Interview reflex: "How do I solve `Ax = 0` with `x ≠ 0`?" → SVD, take last
> column of `V`. "How do I solve `Ax = b` overdetermined?" → least squares.

---

## 2. Least squares

Given `A x ≈ b` with more equations than unknowns, minimize `‖Ax − b‖²`.

- **Normal equations:** `x = (AᵀA)⁻¹ Aᵀ b`. Fast, but `AᵀA` squares the condition
  number → numerically worse.
- **SVD / QR:** more stable, preferred in practice.
- **Weighted least squares:** `min (Ax−b)ᵀ W (Ax−b)`; `W = Σ⁻¹` uses measurement
  covariance. This is exactly what filters and bundle adjustment do.

**Total least squares** (errors in both `A` and `b`) → solved via SVD; this is how
you fit a line/plane when *all* coordinates are noisy.

---

## 3. Probability for estimation

- **Bayes' rule:** `p(x|z) ∝ p(z|x) p(x)` — posterior ∝ likelihood × prior. This is
  the entire conceptual basis of filtering and SLAM back-ends.
- **Gaussian (normal) distribution:** fully described by mean `μ` and covariance
  `Σ`. Closed under linear transforms and conditioning — *why* Kalman filters are
  Gaussian.
  - `x ~ N(μ, Σ)`, then `Ax+b ~ N(Aμ+b, AΣAᵀ)`.
- **Covariance matrix** `Σ`: diagonal = variances, off-diagonal = correlation.
  Eigen-decomposition gives the uncertainty ellipse.
- **Mahalanobis distance** `d² = (x−μ)ᵀ Σ⁻¹ (x−μ)` — distance that accounts for
  correlation/scale. Used for gating/outlier rejection in data association.

---

## 4. Optimization (nonlinear least squares)

Most perception "solve" steps minimize a sum of squared residuals
`f(x) = ½‖r(x)‖² = ½ Σ rᵢ(x)²`.

- **Gradient descent:** `x ← x − α ∇f`. Simple, slow, needs step tuning.
- **Gauss–Newton:** linearize residuals `r(x+Δ) ≈ r + J Δ`, solve
  `JᵀJ Δ = −Jᵀ r`. Fast near the solution; can diverge far away.
- **Levenberg–Marquardt:** `(JᵀJ + λI) Δ = −Jᵀ r`. Interpolates between GN
  (λ→0) and gradient descent (λ→∞). The default for bundle adjustment / pose-graph.

> Know the GN normal equation cold — it's the same `JᵀJ Δ = −Jᵀ r` you'll write
> for EKF Jacobians, BA, ICP, and pose-graph optimization.

### First-order Taylor expansion (the tool under the hood)

Every method above relies on replacing a nonlinear function with a local linear
model. For a vector function `r: ℝⁿ → ℝᵐ`, the **first-order Taylor expansion**
around the current estimate `x` is

```
r(x + Δ) ≈ r(x) + J Δ        J = ∂r/∂x ∈ ℝ^{m×n}   (the Jacobian)
```

`J` collects the partial derivatives: row `i` is `∇rᵢ(x)ᵀ`. Geometrically this is
the **tangent (hyper)plane** to `r` at `x`; it is accurate for small steps `Δ` and
degrades as `Δ` grows or the function curves sharply. Linearizing the *residual*
(cheap, first derivatives only) is what makes Gauss–Newton avoid the full Hessian.

### Deriving the Gauss–Newton update

**1. Cost.** Minimize `f(x) = ½‖r(x)‖²` (the ½ just cancels a 2 later).

**2. Linearize the residual** with the first-order Taylor expansion:
`r(x+Δ) ≈ r(x) + J Δ`.

**3. Substitute** to get a quadratic in the step `Δ`:

```
f(x+Δ) ≈ ½‖r + J Δ‖² = ½ (rᵀr + 2 rᵀJ Δ + Δᵀ JᵀJ Δ)
```

**4. Minimize over `Δ`** by setting the gradient to zero:

```
∂f/∂Δ = Jᵀr + JᵀJ Δ = 0   ⟹   (JᵀJ) Δ = −Jᵀ r     ← GN normal equation
```

Then update `x ← x + Δ` and re-linearize. Iterate to convergence.

**Why drop the Hessian?** The exact Newton step uses
`H = JᵀJ + Σᵢ rᵢ ∇²rᵢ`. Gauss–Newton **approximates `H ≈ JᵀJ`**, discarding the
`Σᵢ rᵢ ∇²rᵢ` term. That term is negligible when residuals `rᵢ` are small or the
problem is nearly linear — exactly the regime near a good solution — so GN
converges almost as fast as Newton while needing only first derivatives. Bonus:
`JᵀJ` is automatically symmetric PSD.

**When GN breaks → Levenberg–Marquardt.** Far from the optimum `JᵀJ` can be
ill-conditioned/singular and the step overshoots. LM damps it:

```
(JᵀJ + λI) Δ = −Jᵀ r
   λ→0   : recovers Gauss–Newton (fast near the solution)
   λ→∞   : Δ ≈ −(1/λ) Jᵀr, a small gradient-descent step (safe, slow)
```

LM adapts `λ` per iteration (shrink it after a successful step, grow it after a
rejected one) — a trust-region strategy that keeps you in the region where the
linearization is trustworthy.

---

## Interview-style questions
*Click a question to reveal a model answer.*

??? When would you use the normal equations vs. SVD for least squares?
Normal equations `x = (AᵀA)⁻¹Aᵀb` are fast and fine when `A` is well-conditioned and you want speed. But forming `AᵀA` **squares the condition number**, so you lose precision on ill-conditioned or nearly-collinear systems. Prefer **SVD (or QR)** when accuracy/robustness matters or `A` may be rank-deficient: SVD reveals the rank via the singular values and gives the minimum-norm solution. Rule of thumb: prototype / huge-sparse → normal equations or conjugate gradient; numerically sensitive → SVD/QR.

??? You have `Ax = 0`; how do you find a nontrivial `x`? Why the smallest singular value?
Stack the constraints into `A` and minimize `‖Ax‖` subject to `‖x‖ = 1`. Using `A = UΣVᵀ` and `y = Vᵀx`, you minimize `Σ σᵢ² yᵢ²` under `‖y‖ = 1`, which puts all the weight on the **smallest singular value** — so the solution is the corresponding right-singular vector, the **last column of V**. If a singular value is ~0, that column is an exact null-space direction. This is exactly how the 8-point algorithm, homography (DLT), and triangulation are solved.

??? Why is the covariance matrix symmetric positive semi-definite? What do its eigenvectors mean?
`Σ = E[(x−μ)(x−μ)ᵀ]` is symmetric by construction, and PSD because for any vector `a`, `aᵀΣa = Var(aᵀx) ≥ 0` (a variance can't be negative). Its **eigenvectors are the principal axes** of the uncertainty ellipsoid and its **eigenvalues are the variances** along those axes (so `√λ` is the std). This is the basis of PCA and of drawing covariance/uncertainty ellipses.

??? Derive the Gauss–Newton update from a first-order Taylor expansion.
Minimize `f(x) = ½‖r(x)‖²`. Linearize the residual: `r(x+Δ) ≈ r(x) + JΔ` with `J = ∂r/∂x`. Substitute: `f ≈ ½‖r + JΔ‖²`. Set the gradient w.r.t. `Δ` to zero: `Jᵀ(r + JΔ) = 0`, giving the normal equation **`(JᵀJ)Δ = −Jᵀr`**. Iterate `x ← x + Δ`. Levenberg–Marquardt damps this as `(JᵀJ + λI)Δ = −Jᵀr` to stay stable far from the optimum.

??? What's the geometric interpretation of Mahalanobis distance vs. Euclidean?
Euclidean distance treats every direction equally (equidistant points form a circle/sphere). Mahalanobis `d² = (x−μ)ᵀΣ⁻¹(x−μ)` rescales by the covariance, so distance is measured in **standard deviations along the (possibly correlated) principal axes** — equidistant points form the covariance ellipse, not a circle. That makes it the correct metric for outlier gating and data association, because it accounts for the shape of the sensor noise.

## Resources
- *MIT 18.06* (Strang) lectures on SVD, least squares, eigenvalues.
- *Mathematics for Machine Learning* (Deisenroth) — Ch. 2–5, free PDF.
- 3Blue1Brown "Essence of Linear Algebra" for geometric intuition.

➡ **Practice (solve in-site):** [w1_least_squares.py](practice.html?p=rob-least-squares-line), [w1_covariance.py](practice.html?p=rob-covariance-mahalanobis)
