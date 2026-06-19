#!/usr/bin/env python3
"""End-to-end SfM *geometry* demo on synthetic data -- no images, no OpenCV needed.

This isolates the numerical heart of SfM (triangulation + bundle adjustment) so you
can run and trust it without a dataset or feature matching:

  1. Make a known 3D point cloud and a ring of known cameras looking at it.
  2. Project the points into every camera (these are our perfect correspondences).
  3. Perturb the cameras and points (simulating a noisy SfM initialisation).
  4. Run bundle adjustment and watch the reprojection cost collapse and the
     recovered geometry snap back toward ground truth.

Only requires numpy + scipy (see sfm/bundle.py).
"""

from __future__ import annotations

import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sfm.bundle import bundle_adjust, project  # noqa: E402


def rodrigues(rvec: np.ndarray) -> np.ndarray:
    theta = np.linalg.norm(rvec)
    if theta < 1e-12:
        return np.eye(3)
    k = rvec / theta
    K = np.array([[0, -k[2], k[1]], [k[2], 0, -k[0]], [-k[1], k[0], 0]])
    return np.eye(3) + np.sin(theta) * K + (1 - np.cos(theta)) * (K @ K)


def make_scene(n_points=120, n_cameras=8, seed=0):
    rng = np.random.default_rng(seed)
    K = np.array([[800.0, 0, 320.0], [0, 800.0, 240.0], [0, 0, 1.0]])

    # A blob of 3D points around the origin.
    points = rng.normal(scale=1.0, size=(n_points, 3))
    points[:, 2] += 6.0                      # push in front of the cameras

    # Cameras on a ring at radius R, all looking roughly at the origin.
    cams = np.zeros((n_cameras, 6))
    R_ring = 4.0
    for i in range(n_cameras):
        ang = 2 * np.pi * i / n_cameras * 0.5      # half ring -> good overlap
        C = np.array([R_ring * np.sin(ang), 0.3 * np.sin(2 * ang), R_ring * (1 - np.cos(ang))])
        # look-at toward scene center (0,0,6)
        forward = np.array([0, 0, 6.0]) - C
        forward /= np.linalg.norm(forward)
        up = np.array([0, 1.0, 0])
        right = np.cross(up, forward); right /= np.linalg.norm(right)
        true_up = np.cross(forward, right)
        Rmat = np.vstack([right, true_up, forward])    # world->camera rows
        t = -Rmat @ C
        rvec = _mat_to_rvec(Rmat)
        cams[i, :3] = rvec
        cams[i, 3:] = t
    return K, points, cams


def _mat_to_rvec(R: np.ndarray) -> np.ndarray:
    ang = np.arccos(np.clip((np.trace(R) - 1) / 2, -1, 1))
    if ang < 1e-9:
        return np.zeros(3)
    ax = np.array([R[2, 1] - R[1, 2], R[0, 2] - R[2, 0], R[1, 0] - R[0, 1]])
    return ax / (2 * np.sin(ang)) * ang


def main() -> int:
    K, points, cams = make_scene()
    n_cam, n_pt = cams.shape[0], points.shape[0]

    # Build observations: project every point into every camera (full visibility).
    cam_idx, pt_idx, pixels = [], [], []
    for ci in range(n_cam):
        proj = project(points, np.repeat(cams[ci:ci + 1], n_pt, axis=0), K)
        for pi in range(n_pt):
            cam_idx.append(ci); pt_idx.append(pi); pixels.append(proj[pi])
    cam_idx = np.array(cam_idx); pt_idx = np.array(pt_idx); pixels = np.array(pixels)

    # Perturb everything to simulate a noisy initialisation. Keep camera 0 fixed
    # as the gauge (in a real pipeline the first camera fixes the coordinate frame).
    rng = np.random.default_rng(42)
    cams_noisy = cams.copy()
    cams_noisy[1:, :3] += rng.normal(scale=0.03, size=(n_cam - 1, 3))
    cams_noisy[1:, 3:] += rng.normal(scale=0.10, size=(n_cam - 1, 3))
    points_noisy = points + rng.normal(scale=0.15, size=points.shape)

    def reproj_rmse(cam_params, pts):
        proj = project(pts[pt_idx], cam_params[cam_idx], K)
        return float(np.sqrt(np.mean(np.sum((proj - pixels) ** 2, axis=1))))

    print(f"Scene: {n_cam} cameras, {n_pt} points, {len(pixels)} observations.")
    print(f"Reprojection RMSE before BA: {reproj_rmse(cams_noisy, points_noisy):8.3f} px")

    result = bundle_adjust(cams_noisy, points_noisy, cam_idx, pt_idx, pixels, K, verbose=0)

    print(f"Reprojection RMSE after  BA: {reproj_rmse(result.camera_params, result.points3d):8.3f} px")
    print(f"BA cost {result.cost_before:.1f} -> {result.cost_after:.1f}")

    # Sanity: recovered points should be close to ground truth (up to the fixed gauge).
    pt_err = np.median(np.linalg.norm(result.points3d - points, axis=1))
    print(f"Median 3D point error after BA: {pt_err:.4f} (world units)")
    ok = reproj_rmse(result.camera_params, result.points3d) < 0.5 and pt_err < 0.1
    print("RESULT:", "PASS" if ok else "CHECK")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
