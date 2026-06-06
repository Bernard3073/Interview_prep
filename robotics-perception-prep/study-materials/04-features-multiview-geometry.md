# Week 4 — Features & Multi-View Geometry

> This is the heart of classical perception: find repeatable points, match them
> across images, and use the matches to recover camera motion and 3D structure.

---

## 1. Feature detection

A good keypoint is **repeatable** (found again under viewpoint/lighting change) and
**localizable** (well-defined position).

- **Harris corner:** looks at the second-moment matrix `M = Σ ∇I ∇Iᵀ` over a
  window. Two large eigenvalues → corner; one → edge; none → flat. Response
  `R = det(M) − k·tr(M)²`.
- **FAST:** checks a ring of 16 pixels around a candidate — fast enough for
  real-time SLAM front-ends.
- **Blob detectors (DoG / LoG):** find scale + location → SIFT keypoints.

## 2. Feature description & matching

- **SIFT:** 128-D histogram-of-gradients descriptor; scale & rotation invariant.
  Gold standard for accuracy (now patent-free).
- **ORB:** FAST + rotated BRIEF, binary descriptor; matched with **Hamming
  distance**. Fast, the default in ORB-SLAM.
- **Matching:** nearest neighbor in descriptor space; apply **Lowe's ratio test**
  (`d1 / d2 < 0.7..0.8`) to reject ambiguous matches; cross-check; then geometric
  verification with RANSAC.

## 3. RANSAC — robust fitting

Matches contain outliers; least squares alone gets wrecked by them.

```
repeat N times:
    sample the minimal set (e.g. 4 pts for homography, 8 for F)
    fit the model
    count inliers (residual < threshold)
keep the model with the most inliers; refit on all inliers
```
- Choose `N` from desired success prob `p` and inlier ratio `w`:
  `N = log(1−p) / log(1 − wˢ)`.
- Variants: MSAC, PROSAC, LO-RANSAC.

> RANSAC shows up far beyond CV — plane fitting in point clouds, line fitting,
> any model-with-outliers situation. Know the loop and the `N` formula.

## 4. Epipolar geometry (two views)

![Epipolar geometry](images/epipolar-geometry.svg)

A 3D point seen in two cameras gives corresponding pixels `x ↔ x'`. They satisfy:

```
x'ᵀ F x = 0          (fundamental matrix, uncalibrated, pixels)
x'ᵀ E x = 0          (essential matrix, calibrated/normalized rays)
E = K'ᵀ F K           E = [t]ₓ R
```
- A point in image 1 constrains its match in image 2 to lie on a line (the
  **epipolar line**) → reduces matching from 2D to 1D search.
- **8-point algorithm** estimates `F` linearly (SVD), with Hartley normalization;
  enforce rank-2 by zeroing the smallest singular value.
- **5-point algorithm** estimates `E` from calibrated cameras (minimal → great with
  RANSAC).
- Decompose `E = [t]ₓR` → 4 solutions for `(R, t)`; pick the one with points in
  front of both cameras (cheirality). Translation is recovered **up to scale**.

## 5. Homography (planar / pure rotation)

`x' = H x` (3×3) relates two views of a **plane** or images under **pure camera
rotation**. Uses: image stitching/panoramas, AR marker pose, ground-plane warps
(bird's-eye view). Estimated from ≥4 correspondences (DLT + SVD).

> Decision: planar scene or pure rotation → homography; general 3D scene with
> translation → fundamental/essential matrix.

## 6. Triangulation & PnP

- **Triangulation:** given `x ↔ x'` and known camera matrices, recover the 3D point
  (linear DLT via SVD, then nonlinear refine of reprojection error).
- **PnP (Perspective-n-Point):** given known 3D points and their 2D projections,
  find the camera pose `(R, t)`. P3P (minimal, 3 pts) + RANSAC + nonlinear refine.
  This is how you **relocalize** against a known map.

## 7. Bundle adjustment

The grand nonlinear least squares that jointly refines **all camera poses and 3D
points** by minimizing total reprojection error:

```
min Σ_i Σ_j ρ( ‖ x_ij − π(K, T_i, X_j) ‖² )
```
- Solved with LM; exploits **sparsity** (Schur complement) because each point sees
  few cameras. `ρ` is a robust (Huber) kernel to tame outliers.
- The back-end of essentially every SfM / visual SLAM system.

---

## Interview-style questions
1. Harris vs. SIFT vs. ORB — when would you pick each?
2. What does `x'ᵀ F x = 0` mean geometrically? Why rank-2?
3. Why is monocular translation only recoverable up to scale? How do you fix the scale?
4. Homography vs. fundamental matrix — what scene geometry distinguishes them?
5. Derive how many RANSAC iterations you need for 50% inliers, 4-point model, 99% success.
6. What makes bundle adjustment tractable for thousands of points?

## Resources
- Hartley & Zisserman, *Multiple View Geometry* — the bible (Ch. 9–11, 18).
- Szeliski Ch. 7–8, 11.
- Cyrill Stachniss "Photogrammetry" YouTube lectures (excellent, intuitive).

➡ **Coding:** `coding-practice/robotics/w4_ransac.py`, `w4_homography_fmatrix.py`
