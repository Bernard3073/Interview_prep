"""Sparse bundle adjustment with scipy.optimize.least_squares.

Jointly refines every camera pose and 3D point to minimise total reprojection
error. The Jacobian is huge but *sparse* -- each residual (one observation)
depends only on its own camera's 6 parameters and its own point's 3 parameters --
so we hand scipy a sparsity pattern and let its trust-region solver exploit it.
This is the small-scale analogue of the Schur-complement trick real BA libraries
(Ceres/g2o/GTSAM) use; see Week 10 section B1.

Camera parameterisation: 6 numbers per camera = Rodrigues rotation vector (3) +
translation (3). Intrinsics K are shared and held fixed here.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy.optimize import least_squares
from scipy.sparse import lil_matrix


def rotate(points: np.ndarray, rot_vecs: np.ndarray) -> np.ndarray:
    """Rotate points by Rodrigues rotation vectors (vectorised, numpy-only).

    points:   (N, 3)
    rot_vecs: (N, 3) axis-angle
    """
    theta = np.linalg.norm(rot_vecs, axis=1)[:, np.newaxis]
    with np.errstate(invalid="ignore", divide="ignore"):
        v = rot_vecs / theta
    v = np.nan_to_num(v)                                  # handle theta == 0
    dot = np.sum(points * v, axis=1)[:, np.newaxis]
    cos_t = np.cos(theta)
    sin_t = np.sin(theta)
    return cos_t * points + sin_t * np.cross(v, points) + dot * (1 - cos_t) * v


def project(points: np.ndarray, camera_params: np.ndarray, K: np.ndarray) -> np.ndarray:
    """Project points using per-observation camera params (rvec+tvec) and shared K."""
    p = rotate(points, camera_params[:, :3]) + camera_params[:, 3:6]
    p = p[:, :2] / p[:, 2, np.newaxis]                   # perspective divide
    fx, fy, cx, cy = K[0, 0], K[1, 1], K[0, 2], K[1, 2]
    u = fx * p[:, 0] + cx
    v = fy * p[:, 1] + cy
    return np.stack([u, v], axis=1)


def _residuals(params, n_cameras, n_points, cam_idx, pt_idx, pixels, K):
    cam = params[: n_cameras * 6].reshape((n_cameras, 6))
    pts = params[n_cameras * 6:].reshape((n_points, 3))
    proj = project(pts[pt_idx], cam[cam_idx], K)
    return (proj - pixels).ravel()


def _sparsity(n_cameras, n_points, cam_idx, pt_idx):
    m = cam_idx.size * 2                                  # 2 residuals per observation
    n = n_cameras * 6 + n_points * 3
    A = lil_matrix((m, n), dtype=int)
    i = np.arange(cam_idx.size)
    for s in range(6):                                   # camera block
        A[2 * i, cam_idx * 6 + s] = 1
        A[2 * i + 1, cam_idx * 6 + s] = 1
    for s in range(3):                                   # point block
        A[2 * i, n_cameras * 6 + pt_idx * 3 + s] = 1
        A[2 * i + 1, n_cameras * 6 + pt_idx * 3 + s] = 1
    return A


@dataclass
class BAResult:
    camera_params: np.ndarray   # (n_cameras, 6) rvec+tvec
    points3d: np.ndarray        # (n_points, 3)
    cost_before: float
    cost_after: float


def bundle_adjust(
    camera_params: np.ndarray,   # (n_cameras, 6)
    points3d: np.ndarray,        # (n_points, 3)
    cam_idx: np.ndarray,         # (n_obs,) camera index per observation
    pt_idx: np.ndarray,          # (n_obs,) point index per observation
    pixels: np.ndarray,          # (n_obs, 2) observed pixel per observation
    K: np.ndarray,
    verbose: int = 0,
) -> BAResult:
    """Run sparse bundle adjustment and return refined cameras + points."""
    n_cameras = camera_params.shape[0]
    n_points = points3d.shape[0]
    x0 = np.hstack([camera_params.ravel(), points3d.ravel()])

    r0 = _residuals(x0, n_cameras, n_points, cam_idx, pt_idx, pixels, K)
    cost_before = 0.5 * float(np.dot(r0, r0))

    A = _sparsity(n_cameras, n_points, cam_idx, pt_idx)
    res = least_squares(
        _residuals,
        x0,
        jac_sparsity=A,
        x_scale="jac",
        ftol=1e-4,
        method="trf",
        loss="huber",                # robust kernel: a few bad matches don't dominate
        f_scale=2.0,                 # ~2 px inlier scale for the Huber transition
        verbose=verbose,
        args=(n_cameras, n_points, cam_idx, pt_idx, pixels, K),
    )
    cost_after = float(res.cost)

    cam = res.x[: n_cameras * 6].reshape((n_cameras, 6))
    pts = res.x[n_cameras * 6:].reshape((n_points, 3))
    return BAResult(camera_params=cam, points3d=pts, cost_before=cost_before, cost_after=cost_after)
