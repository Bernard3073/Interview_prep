"""
Week 3 — Project 3D points to pixels with K[R|t] and add lens distortion.

PROBLEM
-------
1. Build the intrinsic matrix K.
2. Project 3D world points to pixels:  x ~ K [R|t] X.
3. Apply radial+tangential distortion in normalized coordinates.
4. (Bonus) Verify that undistort(distort(x)) ≈ x via a tiny iterative undistort.

Run:  python w3_projection.py
"""
import numpy as np


def intrinsics(fx, fy, cx, cy):
    return np.array([[fx, 0, cx], [0, fy, cy], [0, 0, 1.0]])


def project(K, R, t, X_world):
    """X_world: (N,3). Returns pixels (N,2) and depths (N,)."""
    Xc = (R @ X_world.T + t.reshape(3, 1)).T      # to camera frame
    z = Xc[:, 2]
    xn = Xc[:, :2] / z[:, None]                    # normalized image coords
    pix = (K @ np.column_stack([xn, np.ones(len(xn))]).T).T
    return pix[:, :2], z


def distort(xn, dist):
    """xn: (N,2) normalized coords. dist = [k1,k2,p1,p2,k3]. Returns distorted xn."""
    k1, k2, p1, p2, k3 = dist
    x, y = xn[:, 0], xn[:, 1]
    r2 = x * x + y * y
    radial = 1 + k1 * r2 + k2 * r2 ** 2 + k3 * r2 ** 3
    x_d = x * radial + 2 * p1 * x * y + p2 * (r2 + 2 * x * x)
    y_d = y * radial + p1 * (r2 + 2 * y * y) + 2 * p2 * x * y
    return np.column_stack([x_d, y_d])


def undistort_iter(xd, dist, iters=50):
    """Recover normalized coords from distorted ones by fixed-point iteration.

    Solve  xn*radial + tangential = xd  for xn:
        xn <- (xd - tangential(xn)) / radial(xn)
    """
    k1, k2, p1, p2, k3 = dist
    x = xd.copy()
    for _ in range(iters):
        xx, yy = x[:, 0], x[:, 1]
        r2 = xx * xx + yy * yy
        radial = 1 + k1 * r2 + k2 * r2 ** 2 + k3 * r2 ** 3
        dx = 2 * p1 * xx * yy + p2 * (r2 + 2 * xx * xx)
        dy = p1 * (r2 + 2 * yy * yy) + 2 * p2 * xx * yy
        x = (xd - np.column_stack([dx, dy])) / radial[:, None]
    return x


if __name__ == "__main__":
    K = intrinsics(800, 800, 320, 240)
    R = np.eye(3)
    t = np.array([0.0, 0.0, 0.0])
    X = np.array([[0.0, 0.0, 5.0], [1.0, 0.5, 5.0], [-1.0, -0.5, 8.0]])

    pix, z = project(K, R, t, X)
    print("pixels:\n", np.round(pix, 2))
    assert np.allclose(pix[0], [320, 240])          # on-axis point -> principal pt

    dist = np.array([-0.28, 0.10, 0.0005, -0.0004, 0.0])
    xn = (X[:, :2] / X[:, 2:3])
    xd = distort(xn, dist)
    xr = undistort_iter(xd, dist)
    assert np.allclose(xr, xn, atol=1e-4)
    print("Projection + distort/undistort round-trip OK")
