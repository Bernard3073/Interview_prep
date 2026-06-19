"""Camera intrinsics and a pose container.

Conventions (state these in an interview before writing transform code!):
  * World->camera transform: x_cam = R @ x_world + t   (R, t are world->camera).
  * Projection matrix P = K [R | t], a 3x4 matrix mapping homogeneous world
    points to homogeneous pixels.
  * Rotation stored as a 3x3 matrix; bundle adjustment uses the Rodrigues
    rotation *vector* (axis * angle) as the 3-parameter representation.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass
class PinholeIntrinsics:
    """Pinhole camera intrinsics. We assume zero skew and square-ish pixels."""

    fx: float
    fy: float
    cx: float
    cy: float

    @classmethod
    def from_image_size(cls, width: int, height: int, focal: float | None = None) -> "PinholeIntrinsics":
        """A reasonable default when calibration is unknown: focal ~ image width,
        principal point at the image center. Good enough to *demo* SfM; for
        production you always use a calibrated K."""
        f = focal if focal is not None else 1.2 * max(width, height)
        return cls(fx=f, fy=f, cx=width / 2.0, cy=height / 2.0)

    @property
    def K(self) -> np.ndarray:
        return np.array(
            [[self.fx, 0.0, self.cx],
             [0.0, self.fy, self.cy],
             [0.0, 0.0, 1.0]],
            dtype=np.float64,
        )


@dataclass
class Camera:
    """A registered camera: its world->camera rotation R (3x3) and translation t (3,)."""

    R: np.ndarray
    t: np.ndarray

    @classmethod
    def identity(cls) -> "Camera":
        return cls(R=np.eye(3), t=np.zeros(3))

    @property
    def projection(self) -> np.ndarray:
        """The 3x4 [R | t] (without K)."""
        return np.hstack([self.R, self.t.reshape(3, 1)])

    def P(self, K: np.ndarray) -> np.ndarray:
        """Full 3x4 projection matrix K [R | t]."""
        return K @ self.projection

    @property
    def center(self) -> np.ndarray:
        """Camera center in world coordinates: C = -R^T t."""
        return -self.R.T @ self.t
