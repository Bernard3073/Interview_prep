"""
Week 4 — RANSAC for robust line (and plane) fitting.

PROBLEM
-------
Fit a 2D line to points that contain ~40% outliers. Plain least squares fails;
RANSAC recovers the true line. Implement the RANSAC loop yourself, including the
adaptive iteration-count formula.

Run:  python w4_ransac.py
"""
import numpy as np


def fit_line_2pts(p1, p2):
    """Line through 2 points as (a, b, c) with a*x + b*y + c = 0, ‖(a,b)‖=1."""
    d = p2 - p1
    n = np.array([-d[1], d[0]], float)
    n /= np.linalg.norm(n) + 1e-12
    c = -n @ p1
    return n[0], n[1], c


def point_line_dist(pts, model):
    a, b, c = model
    return np.abs(pts @ np.array([a, b]) + c)


def ransac_line(pts, thresh=0.5, p_success=0.99, max_iters=1000, rng=None):
    rng = rng or np.random.default_rng(0)
    n = len(pts)
    best_inliers = np.zeros(n, bool)
    best_model = None
    iters = max_iters
    i = 0
    while i < iters and i < max_iters:
        idx = rng.choice(n, 2, replace=False)
        model = fit_line_2pts(pts[idx[0]], pts[idx[1]])
        inliers = point_line_dist(pts, model) < thresh
        if inliers.sum() > best_inliers.sum():
            best_inliers = inliers
            best_model = model
            # adaptive N: w = inlier ratio, s = 2 (minimal sample)
            w = max(inliers.mean(), 1e-6)
            denom = np.log(1 - w ** 2)
            if denom < 0:
                iters = min(max_iters, int(np.log(1 - p_success) / denom) + 1)
        i += 1
    # Refit on inliers via total least squares
    inl = pts[best_inliers]
    centroid = inl.mean(axis=0)
    _, _, Vt = np.linalg.svd(inl - centroid)
    normal = Vt[-1]
    refined = (normal[0], normal[1], -normal @ centroid)
    return refined, best_inliers, i


if __name__ == "__main__":
    rng = np.random.default_rng(42)
    # True line y = 0.5x + 1
    x = np.linspace(0, 10, 100)
    y = 0.5 * x + 1 + rng.normal(0, 0.1, x.shape)
    pts = np.column_stack([x, y])
    # Inject 40 outliers
    out = rng.uniform([0, -5], [10, 10], size=(40, 2))
    data = np.vstack([pts, out])

    model, inliers, used = ransac_line(data, thresh=0.4, rng=rng)
    slope = -model[0] / model[1]
    intercept = -model[2] / model[1]
    print(f"RANSAC line: slope={slope:.3f}, intercept={intercept:.3f}")
    print(f"inliers={inliers.sum()} (of {len(data)}), iterations used={used}")
    assert abs(slope - 0.5) < 0.1 and abs(intercept - 1.0) < 0.3
    print("OK")
