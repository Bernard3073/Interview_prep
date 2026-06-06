# Week 1 — Math Foundations

> The goal of week 1 is not to relearn all of math, but to make the handful of
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
`f(x) = Σ ‖rᵢ(x)‖²`.

- **Gradient descent:** `x ← x − α ∇f`. Simple, slow, needs step tuning.
- **Gauss–Newton:** linearize residuals `r(x+Δ) ≈ r + J Δ`, solve
  `JᵀJ Δ = −Jᵀ r`. Fast near the solution; can diverge far away.
- **Levenberg–Marquardt:** `(JᵀJ + λI) Δ = −Jᵀ r`. Interpolates between GN
  (λ→0) and gradient descent (λ→∞). The default for bundle adjustment / pose-graph.

> Know the GN normal equation cold — it's the same `JᵀJ Δ = −Jᵀ r` you'll write
> for EKF Jacobians, BA, ICP, and pose-graph optimization.

---

## Interview-style questions
1. When would you use the normal equations vs. SVD for least squares?
2. You have `Ax = 0`; how do you find a nontrivial `x`? Why the smallest singular value?
3. Why is the covariance matrix symmetric positive semi-definite? What do its eigenvectors mean?
4. Derive the Gauss–Newton update from a first-order Taylor expansion.
5. What's the geometric interpretation of Mahalanobis distance vs. Euclidean?

## Resources
- *MIT 18.06* (Strang) lectures on SVD, least squares, eigenvalues.
- *Mathematics for Machine Learning* (Deisenroth) — Ch. 2–5, free PDF.
- 3Blue1Brown "Essence of Linear Algebra" for geometric intuition.

➡ **Coding:** `coding-practice/robotics/w1_least_squares.py`, `w1_covariance.py`
