"""
Week 5 — 1D constant-velocity Kalman filter for position tracking.

PROBLEM
-------
Track a 1D moving object measured by a noisy position sensor. State = [pos, vel].
Implement predict/update; show the filtered estimate beats raw measurements.

State model:  x_k = F x_{k-1} + w,   F = [[1, dt], [0, 1]]
Measurement:  z_k = H x_k + v,       H = [1, 0]   (we only measure position)

Run:  python w5_kalman_1d.py
"""
import numpy as np


class KalmanFilter1D:
    def __init__(self, dt, process_var, meas_var):
        self.F = np.array([[1, dt], [0, 1.0]])
        self.H = np.array([[1.0, 0.0]])
        q = process_var
        self.Q = q * np.array([[dt**3 / 3, dt**2 / 2], [dt**2 / 2, dt]])
        self.R = np.array([[meas_var]])
        self.x = np.zeros((2, 1))
        self.P = np.eye(2) * 500.0          # large initial uncertainty

    def predict(self):
        self.x = self.F @ self.x
        self.P = self.F @ self.P @ self.F.T + self.Q
        return self.x

    def update(self, z):
        y = np.array([[z]]) - self.H @ self.x          # innovation
        S = self.H @ self.P @ self.H.T + self.R
        K = self.P @ self.H.T @ np.linalg.inv(S)        # Kalman gain
        self.x = self.x + K @ y
        self.P = (np.eye(2) - K @ self.H) @ self.P
        return self.x


if __name__ == "__main__":
    rng = np.random.default_rng(0)
    dt = 0.1
    n = 100
    true_pos = np.cumsum(np.full(n, 1.0 * dt))         # const velocity = 1 m/s
    meas_std = 0.7
    meas = true_pos + rng.normal(0, meas_std, n)

    kf = KalmanFilter1D(dt, process_var=0.05, meas_var=meas_std**2)
    est = []
    for z in meas:
        kf.predict()
        kf.update(z)
        est.append(kf.x[0, 0])
    est = np.array(est)

    raw_err = np.sqrt(np.mean((meas - true_pos) ** 2))
    kf_err = np.sqrt(np.mean((est - true_pos) ** 2))
    print(f"RMSE raw measurements: {raw_err:.3f}")
    print(f"RMSE Kalman estimate : {kf_err:.3f}")
    print(f"estimated final velocity: {kf.x[1,0]:.3f} (truth 1.0)")
    assert kf_err < raw_err, "filter should beat raw measurements"
    print("OK")
