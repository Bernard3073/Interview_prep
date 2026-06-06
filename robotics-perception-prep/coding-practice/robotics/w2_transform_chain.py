"""
Week 2 — Compose SE(3) transforms and project a world point into the camera.

PROBLEM
-------
Given:
  - T_world_body : robot pose in the world
  - T_body_cam   : camera mounted on the robot (extrinsic)
  - a 3D point in the WORLD frame
Compute the point in the CAMERA frame using homogeneous transforms, and verify
the inverse-transform identity  T^-1 = [R^T  -R^T t].

Run:  python w2_transform_chain.py
"""
import numpy as np


def make_T(R, t):
    T = np.eye(4)
    T[:3, :3] = R
    T[:3, 3] = t
    return T


def inv_T(T):
    R = T[:3, :3]
    t = T[:3, 3]
    Ti = np.eye(4)
    Ti[:3, :3] = R.T
    Ti[:3, 3] = -R.T @ t
    return Ti


def transform_point(T, p):
    ph = np.array([*p, 1.0])
    return (T @ ph)[:3]


def Rz(a):
    c, s = np.cos(a), np.sin(a)
    return np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]])


if __name__ == "__main__":
    # Robot at (5, 2, 0), yawed 90 deg.
    T_world_body = make_T(Rz(np.pi / 2), np.array([5.0, 2.0, 0.0]))
    # Camera 0.3 m forward, 0.1 m up, no rotation relative to body.
    T_body_cam = make_T(np.eye(3), np.array([0.3, 0.0, 0.1]))

    # Chain: world -> body -> cam  means we need T_cam_world = inv(T_world_cam)
    T_world_cam = T_world_body @ T_body_cam
    T_cam_world = inv_T(T_world_cam)

    p_world = np.array([6.0, 2.0, 0.5])
    p_cam = transform_point(T_cam_world, p_world)
    print("point in camera frame:", np.round(p_cam, 4))

    # Inverse identity check
    assert np.allclose(inv_T(T_world_cam) @ T_world_cam, np.eye(4), atol=1e-12)
    # Round trip: cam -> world -> cam
    back = transform_point(T_world_cam, p_cam)
    assert np.allclose(back, p_world, atol=1e-12)
    print("Transform chain + inverse identity OK")
