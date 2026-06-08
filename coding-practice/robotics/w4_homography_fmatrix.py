"""
Week 4 — Homography (DLT) and the 8-point fundamental matrix.

PROBLEM
-------
1. Estimate a homography H from >=4 point correspondences via the DLT + SVD.
2. Estimate the fundamental matrix F from >=8 correspondences (normalized
   8-point algorithm), enforcing rank-2.
Both are classic "solve A x = 0 with SVD" problems.

Run:  python w4_homography_fmatrix.py
"""
import numpy as np


def estimate_homography(src, dst):
    """src, dst: (N,2). Returns 3x3 H mapping src -> dst (homogeneous)."""
    A = []
    for (x, y), (u, v) in zip(src, dst):
        A.append([-x, -y, -1, 0, 0, 0, u * x, u * y, u])
        A.append([0, 0, 0, -x, -y, -1, v * x, v * y, v])
    A = np.asarray(A)
    _, _, Vt = np.linalg.svd(A)
    H = Vt[-1].reshape(3, 3)
    return H / H[2, 2]


def _normalize(pts):
    """Hartley normalization: center to origin, scale mean dist to sqrt(2)."""
    c = pts.mean(axis=0)
    d = np.sqrt(((pts - c) ** 2).sum(axis=1)).mean()
    s = np.sqrt(2) / (d + 1e-12)
    T = np.array([[s, 0, -s * c[0]], [0, s, -s * c[1]], [0, 0, 1]])
    ph = np.column_stack([pts, np.ones(len(pts))])
    return (T @ ph.T).T[:, :2], T


def estimate_fundamental(p1, p2):
    """Normalized 8-point algorithm. Returns 3x3 F with x2^T F x1 = 0."""
    n1, T1 = _normalize(p1)
    n2, T2 = _normalize(p2)
    A = []
    for (x1, y1), (x2, y2) in zip(n1, n2):
        A.append([x2 * x1, x2 * y1, x2, y2 * x1, y2 * y1, y2, x1, y1, 1])
    A = np.asarray(A)
    _, _, Vt = np.linalg.svd(A)
    F = Vt[-1].reshape(3, 3)
    # Enforce rank 2
    U, S, Vt2 = np.linalg.svd(F)
    S[-1] = 0
    F = U @ np.diag(S) @ Vt2
    # Denormalize
    F = T2.T @ F @ T1
    return F / F[2, 2]


if __name__ == "__main__":
    rng = np.random.default_rng(0)

    # --- Homography test: apply a known H, recover it ---
    H_true = np.array([[1.1, 0.2, 30], [-0.1, 1.05, -10], [0.0002, 0.0001, 1.0]])
    src = rng.uniform(0, 200, size=(10, 2))
    sh = np.column_stack([src, np.ones(10)])
    dh = (H_true @ sh.T).T
    dst = dh[:, :2] / dh[:, 2:3]
    H = estimate_homography(src, dst)
    assert np.allclose(H, H_true, atol=1e-6), "homography recovery failed"
    print("Homography recovered OK")

    # --- Fundamental matrix: synthetic two-view points must satisfy x2^T F x1 = 0
    F = np.array([[0, -0.0003, 0.02], [0.0003, 0, -0.05], [-0.015, 0.04, 1.0]])
    pts1 = rng.uniform(50, 450, size=(20, 2))
    # Build matching points lying on epipolar lines (construct consistent pairs)
    # For a synthetic check we instead verify the solver on points generated to
    # satisfy a known F via its epipolar lines:
    p1h = np.column_stack([pts1, np.ones(20)])
    lines2 = (F @ p1h.T).T                       # epipolar line in image 2: a,b,c
    pts2 = []
    for (a, b, c) in lines2:
        x = rng.uniform(50, 450)
        y = -(a * x + c) / b                     # pick a point on the line
        pts2.append([x, y])
    pts2 = np.array(pts2)
    F_est = estimate_fundamental(pts1, pts2)
    # Residual of epipolar constraint should be tiny
    p2h = np.column_stack([pts2, np.ones(20)])
    res = np.abs(np.einsum("ij,ij->i", p2h, (F_est @ p1h.T).T))
    print("max epipolar residual:", res.max())
    assert res.max() < 1e-6
    print("Fundamental matrix OK")
