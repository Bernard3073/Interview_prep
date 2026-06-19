"""Two-view geometry: essential matrix, pose recovery, triangulation, reprojection.

These are the numerical primitives behind SfM. The image pipeline uses OpenCV's
robust estimators; the pure-numpy helpers (project / reprojection_error) are also
used by bundle adjustment and the synthetic tests.
"""

from __future__ import annotations

import cv2
import numpy as np


def estimate_pose(
    pts1: np.ndarray,
    pts2: np.ndarray,
    K: np.ndarray,
    ransac_thresh: float = 1.0,
) -> tuple[np.ndarray, np.ndarray, np.ndarray] | None:
    """Recover relative pose (R, t) of camera 2 w.r.t. camera 1 from matched pixels.

    Returns (R, t, inlier_mask) with R: 3x3, t: unit-norm 3-vector (scale is
    unobservable from two views), inlier_mask: bool over the input matches.
    """
    E, mask = cv2.findEssentialMat(
        pts1, pts2, K, method=cv2.RANSAC, prob=0.999, threshold=ransac_thresh
    )
    if E is None:
        return None
    # recoverPose enforces the cheirality check (points in front of both cameras)
    # and picks the single physically valid (R, t) out of the four decompositions.
    _, R, t, mask_pose = cv2.recoverPose(E, pts1, pts2, K, mask=mask)
    inliers = mask_pose.ravel() > 0
    return R, t.ravel(), inliers


def triangulate(P1: np.ndarray, P2: np.ndarray, pts1: np.ndarray, pts2: np.ndarray) -> np.ndarray:
    """Linear (DLT) triangulation of corresponding pixels into 3D world points.

    P1, P2 are 3x4 projection matrices (K[R|t]). pts1, pts2 are (N,2) pixels.
    Returns (N, 3) world points.
    """
    pts1h = pts1.T.astype(np.float64)   # cv2 wants 2xN
    pts2h = pts2.T.astype(np.float64)
    X_h = cv2.triangulatePoints(P1, P2, pts1h, pts2h)  # 4 x N homogeneous
    X = (X_h[:3] / X_h[3]).T
    return X


def project(points3d: np.ndarray, R: np.ndarray, t: np.ndarray, K: np.ndarray) -> np.ndarray:
    """Project (N,3) world points into pixels with camera (R, t) and intrinsics K."""
    Xc = points3d @ R.T + t                       # world -> camera
    z = Xc[:, 2:3]
    uv = (Xc / z) @ K.T                            # perspective divide + intrinsics
    return uv[:, :2]


def reprojection_error(points3d, R, t, K, pixels) -> np.ndarray:
    """Per-point reprojection residual magnitude (pixels)."""
    proj = project(points3d, R, t, K)
    return np.linalg.norm(proj - pixels, axis=1)


def in_front(points3d: np.ndarray, R: np.ndarray, t: np.ndarray) -> np.ndarray:
    """Cheirality mask: True where the point is in front of the camera (z > 0)."""
    Xc = points3d @ R.T + t
    return Xc[:, 2] > 0
