"""
Week 5 — 2D EKF localization with range-bearing landmark measurements.

PROBLEM
-------
A differential-drive robot with state [x, y, theta] moves with control [v, w] and
observes known landmarks via range + bearing. Implement the EKF: nonlinear motion
model f, measurement model h, and their Jacobians F and H.

Run:  python w5_ekf_localization.py
"""
import numpy as np


def wrap(a):
    return (a + np.pi) % (2 * np.pi) - np.pi


def motion(x, u, dt):
    px, py, th = x
    v, w = u
    return np.array([px + v * dt * np.cos(th),
                     py + v * dt * np.sin(th),
                     wrap(th + w * dt)])


def motion_jacobian(x, u, dt):
    _, _, th = x
    v, _ = u
    return np.array([[1, 0, -v * dt * np.sin(th)],
                     [0, 1,  v * dt * np.cos(th)],
                     [0, 0, 1.0]])


def meas(x, lm):
    dx, dy = lm[0] - x[0], lm[1] - x[1]
    r = np.hypot(dx, dy)
    b = wrap(np.arctan2(dy, dx) - x[2])
    return np.array([r, b])


def meas_jacobian(x, lm):
    dx, dy = lm[0] - x[0], lm[1] - x[1]
    q = dx * dx + dy * dy
    r = np.sqrt(q)
    return np.array([[-dx / r, -dy / r, 0],
                     [dy / q,  -dx / q, -1.0]])


def ekf_step(mu, P, u, dt, Q, z, lm, R):
    # Predict
    mu = motion(mu, u, dt)
    Fx = motion_jacobian(mu, u, dt)
    P = Fx @ P @ Fx.T + Q
    # Update with one landmark
    z_hat = meas(mu, lm)
    H = meas_jacobian(mu, lm)
    y = z - z_hat
    y[1] = wrap(y[1])
    S = H @ P @ H.T + R
    K = P @ H.T @ np.linalg.inv(S)
    mu = mu + K @ y
    mu[2] = wrap(mu[2])
    P = (np.eye(3) - K @ H) @ P
    return mu, P


if __name__ == "__main__":
    rng = np.random.default_rng(0)
    dt = 0.1
    landmarks = np.array([[10, 0], [10, 10], [0, 10]], float)
    Q = np.diag([0.02, 0.02, 0.01]) ** 2
    R = np.diag([0.3, np.deg2rad(2)]) ** 2

    x_true = np.array([0.0, 0.0, 0.0])
    mu = np.array([0.5, -0.5, 0.1])          # wrong initial guess
    P = np.diag([1.0, 1.0, 0.5])
    u = np.array([1.0, 0.1])                   # drive in a curve

    errs = []
    for k in range(200):
        x_true = motion(x_true, u, dt)
        lm = landmarks[k % len(landmarks)]
        z = meas(x_true, lm) + rng.multivariate_normal([0, 0], R)
        mu, P = ekf_step(mu, P, u, dt, Q, z, lm, R)
        errs.append(np.linalg.norm(mu[:2] - x_true[:2]))

    print(f"initial pos error ~ {errs[0]:.3f} m")
    print(f"final   pos error ~ {errs[-1]:.3f} m")
    assert errs[-1] < 0.5, "EKF should converge to the true trajectory"
    print("EKF localization OK")
