"""A small, readable incremental Structure-from-Motion pipeline.

Modules
-------
camera          : pinhole intrinsics + camera-pose container.
features        : SIFT detection / description (OpenCV).
matching        : Lowe-ratio matching + fundamental-matrix geometric verification.
geometry        : essential matrix, pose recovery, triangulation, reprojection.
tracks          : union-find feature tracks across many images.
bundle          : sparse bundle adjustment (scipy.least_squares).
reconstruction  : the incremental SfM driver tying it all together.
io_utils        : image loading + PLY export.

The same pipeline that, scaled up and fed aerial survey imagery + GPS/IMU pose
priors, produces the geometric world models described in the Week 10/11 notes.
"""

from .camera import Camera, PinholeIntrinsics
from .reconstruction import IncrementalSfM

__all__ = ["Camera", "PinholeIntrinsics", "IncrementalSfM"]
