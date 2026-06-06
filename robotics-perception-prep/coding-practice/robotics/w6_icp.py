"""
Week 6 — 2D Iterative Closest Point (point-to-point).

PROBLEM
-------
Align a source point cloud to a target cloud that differs by an unknown rigid
transform (R, t). Implement:
  - nearest-neighbor correspondence
  - the closed-form SVD solution for the best rigid transform (Umeyama/Kabsch)
  - the ICP iteration loop until convergence

Run:  python w6_icp.py
"""
import numpy as np


def best_rigid_transform(A, B):
    """Find R, t minimizing ‖R A_i + t − B_i‖² (Kabsch). A, B: (N,2)."""
    ca, cb = A.mean(0), B.mean(0)
    AA, BB = A - ca, B - cb
    H = AA.T @ BB
    U, _, Vt = np.linalg.svd(H)
    R = Vt.T @ U.T
    if np.linalg.det(R) < 0:                # reflection fix
        Vt[-1] *= -1
        R = Vt.T @ U.T
    t = cb - R @ ca
    return R, t


def nearest_neighbors(src, dst):
    # brute force; in practice use a kd-tree
    idx = np.array([np.argmin(((dst - p) ** 2).sum(1)) for p in src])
    return idx


def icp(src, dst, max_iter=50, tol=1e-6):
    src_cur = src.copy()
    R_tot, t_tot = np.eye(2), np.zeros(2)
    prev_err = np.inf
    for it in range(max_iter):
        idx = nearest_neighbors(src_cur, dst)
        matched = dst[idx]
        R, t = best_rigid_transform(src_cur, matched)
        src_cur = (R @ src_cur.T).T + t
        R_tot = R @ R_tot
        t_tot = R @ t_tot + t
        err = np.mean(np.linalg.norm(src_cur - matched, axis=1))
        if abs(prev_err - err) < tol:
            break
        prev_err = err
    return R_tot, t_tot, err, it + 1


if __name__ == "__main__":
    rng = np.random.default_rng(0)
    # Target cloud: an L-shape
    t1 = np.column_stack([np.linspace(0, 5, 60), np.zeros(60)])
    t2 = np.column_stack([np.zeros(60), np.linspace(0, 5, 60)])
    target = np.vstack([t1, t2])

    # Source = target transformed by known R, t (+ small noise)
    ang = np.deg2rad(20)
    R_true = np.array([[np.cos(ang), -np.sin(ang)], [np.sin(ang), np.cos(ang)]])
    t_true = np.array([1.5, -0.8])
    source = (R_true @ target.T).T + t_true + rng.normal(0, 0.01, target.shape)

    # ICP should recover the INVERSE transform mapping source back to target.
    R_est, t_est, err, iters = icp(source, target)
    ang_est = np.degrees(np.arctan2(R_est[1, 0], R_est[0, 0]))
    print(f"recovered rotation: {ang_est:.2f} deg (truth {-20:.2f})")
    print(f"final mean error: {err:.4f}, iterations: {iters}")
    assert err < 0.05
    print("ICP OK")
