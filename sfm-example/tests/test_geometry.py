"""Unit tests for the geometry + bundle-adjustment core (numpy/scipy only).

Run with:  python -m pytest -q   (or: python tests/test_geometry.py)
These do NOT require OpenCV; they validate the pure-numpy primitives that
underpin the whole pipeline.
"""

from __future__ import annotations

import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sfm.bundle import bundle_adjust, project, rotate  # noqa: E402


def _K():
    return np.array([[800.0, 0, 320.0], [0, 800.0, 240.0], [0, 0, 1.0]])


def test_rotate_identity():
    pts = np.random.default_rng(0).normal(size=(10, 3))
    out = rotate(pts, np.zeros((10, 3)))
    assert np.allclose(out, pts)


def test_rotate_90_deg_z():
    # +90 deg about z maps (1,0,0) -> (0,1,0)
    pt = np.array([[1.0, 0.0, 0.0]])
    rvec = np.array([[0.0, 0.0, np.pi / 2]])
    out = rotate(pt, rvec)
    assert np.allclose(out, [[0.0, 1.0, 0.0]], atol=1e-6)


def test_project_principal_point():
    # A point on the optical axis projects to the principal point.
    K = _K()
    pt = np.array([[0.0, 0.0, 5.0]])
    cam = np.zeros((1, 6))
    uv = project(pt, cam, K)
    assert np.allclose(uv, [[K[0, 2], K[1, 2]]], atol=1e-9)


def test_bundle_adjustment_reduces_cost():
    rng = np.random.default_rng(1)
    K = _K()
    n_cam, n_pt = 5, 40
    points = rng.normal(size=(n_pt, 3)); points[:, 2] += 6.0
    cams = np.zeros((n_cam, 6))
    cams[:, 3] = np.linspace(-1, 1, n_cam)        # slide along x
    cams[:, 5] = 0.0

    cam_idx, pt_idx, pix = [], [], []
    for c in range(n_cam):
        proj = project(points, np.repeat(cams[c:c + 1], n_pt, axis=0), K)
        for p in range(n_pt):
            cam_idx.append(c); pt_idx.append(p); pix.append(proj[p])
    cam_idx, pt_idx, pix = map(np.array, (cam_idx, pt_idx, pix))

    cams_n = cams.copy(); cams_n[1:, 3:] += rng.normal(scale=0.05, size=(n_cam - 1, 3))
    points_n = points + rng.normal(scale=0.1, size=points.shape)

    res = bundle_adjust(cams_n, points_n, cam_idx, pt_idx, pix, K)
    assert res.cost_after < res.cost_before * 0.1   # cost should collapse


if __name__ == "__main__":
    # Minimal runner so you can execute without pytest installed.
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    failed = 0
    for fn in fns:
        try:
            fn(); print(f"PASS {fn.__name__}")
        except AssertionError as e:
            failed += 1; print(f"FAIL {fn.__name__}: {e}")
    raise SystemExit(1 if failed else 0)
