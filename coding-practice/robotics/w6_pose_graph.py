"""
Week 6 — 1D/2D pose-graph optimization (Gauss-Newton), minimal version.

PROBLEM
-------
Optimize a chain of robot poses on a line given:
  - odometry constraints between consecutive poses (drifty)
  - a loop-closure constraint tying the last pose back to the first
Minimize Σ ‖(x_j - x_i) - measured_ij‖² / σ². This is the essence of graph SLAM,
stripped to 1D so the math is transparent.

Run:  python w6_pose_graph.py
"""
import numpy as np


def optimize_pose_graph(n, edges, anchor=0, iters=10):
    """
    n: number of poses (1D positions).
    edges: list of (i, j, measured_displacement, information_weight).
    anchor: pose index fixed to 0 to remove the gauge freedom.
    Returns optimized poses (n,).
    """
    x = np.zeros(n)
    # init by chaining odometry edges
    for (i, j, d, _) in edges:
        if j == i + 1:
            x[j] = x[i] + d

    for _ in range(iters):
        H = np.zeros((n, n))
        b = np.zeros(n)
        for (i, j, d, w) in edges:
            # residual r = (x_j - x_i) - d ; Jacobians: dr/dx_i=-1, dr/dx_j=+1
            r = (x[j] - x[i]) - d
            H[i, i] += w
            H[j, j] += w
            H[i, j] -= w
            H[j, i] -= w
            b[i] += w * r
            b[j] -= w * r
        # Anchor to fix gauge
        H[anchor, :] = 0
        H[:, anchor] = 0
        H[anchor, anchor] = 1
        b[anchor] = 0
        dx = np.linalg.solve(H, -b)
        x += dx
        if np.linalg.norm(dx) < 1e-12:
            break
    return x


if __name__ == "__main__":
    # True poses: evenly spaced every 1.0 m, 5 poses on a loop back to start.
    n = 5
    true = np.array([0.0, 1.0, 2.0, 3.0, 4.0])

    # Odometry measurements with drift (each ~1.0 but biased high)
    odom = [(i, i + 1, 1.1, 1.0) for i in range(n - 1)]
    # Loop closure: we KNOW pose 4 is actually 4.0 from pose 0 (e.g. recognized place)
    loop = [(0, 4, 4.0, 5.0)]   # higher weight: we trust the loop closure more
    edges = odom + loop

    est = optimize_pose_graph(n, edges)
    print("odometry-only drift at last pose:", round(0 + sum(1.1 for _ in range(4)), 3))
    print("optimized poses:", np.round(est, 3))
    print("true poses     :", true)
    assert abs(est[-1] - 4.0) < 0.2, "loop closure should pull drift back"
    print("Pose-graph optimization OK")
