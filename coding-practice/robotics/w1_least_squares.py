"""
Week 1 — Least squares line fit via SVD / normal equations.

PROBLEM
-------
Given noisy 2D points, fit the best line y = m*x + b in the least-squares sense.
Then fit a *total* least-squares line (errors in both x and y) using SVD, which is
the more "robotics-correct" way when both coordinates are noisy.

Try it yourself first, then compare with the reference below.

Run:  python w1_least_squares.py
"""
import numpy as np


def fit_line_ols(x, y):
    """Ordinary least squares: minimize vertical residuals. Returns (m, b)."""
    A = np.column_stack([x, np.ones_like(x)])      # [x 1]
    # Solve A @ [m, b] = y  (normal equations via lstsq for stability)
    (m, b), *_ = np.linalg.lstsq(A, y, rcond=None)
    return m, b


def fit_line_tls(points):
    """Total least squares via SVD. Returns (n, c) for line  n·p = c, ‖n‖=1.

    The line passes through the centroid; the normal is the singular vector of the
    SMALLEST singular value (direction of least variance).
    """
    p = np.asarray(points, float)
    centroid = p.mean(axis=0)
    U, S, Vt = np.linalg.svd(p - centroid)
    normal = Vt[-1]                  # smallest singular value -> normal direction
    c = normal @ centroid
    return normal, c


if __name__ == "__main__":
    rng = np.random.default_rng(0)
    x = np.linspace(0, 10, 50)
    true_m, true_b = 2.0, 1.0
    y = true_m * x + true_b + rng.normal(0, 1.0, x.shape)

    m, b = fit_line_ols(x, y)
    print(f"OLS:  m={m:.3f}, b={b:.3f}   (truth m={true_m}, b={true_b})")

    n, c = fit_line_tls(np.column_stack([x, y]))
    # Convert normal form to slope-intercept for comparison:  n0*x + n1*y = c
    m_tls = -n[0] / n[1]
    b_tls = c / n[1]
    print(f"TLS:  m={m_tls:.3f}, b={b_tls:.3f}")
    assert abs(m - true_m) < 0.3 and abs(b - true_b) < 0.6
    print("OK")
