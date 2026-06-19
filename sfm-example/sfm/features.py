"""Feature detection and description.

SIFT is the default: scale + rotation invariant, accurate, and now patent-free
(available in the main OpenCV package as cv2.SIFT_create). For real-time
front-ends you would swap in ORB or a learned detector (SuperPoint); the rest of
the pipeline is agnostic to the choice as long as you have keypoints + descriptors.
"""

from __future__ import annotations

from dataclasses import dataclass

import cv2
import numpy as np


@dataclass
class ImageFeatures:
    """Detected features for one image."""

    keypoints: list           # list[cv2.KeyPoint]
    descriptors: np.ndarray   # (N, 128) float32 for SIFT
    xy: np.ndarray            # (N, 2) pixel coordinates, cached for convenience


def detect(image_gray: np.ndarray, max_features: int = 8000) -> ImageFeatures:
    """Detect + describe SIFT features in a single grayscale image."""
    sift = cv2.SIFT_create(nfeatures=max_features)
    kps, desc = sift.detectAndCompute(image_gray, None)
    if desc is None:
        desc = np.zeros((0, 128), dtype=np.float32)
        kps = []
    xy = np.array([kp.pt for kp in kps], dtype=np.float64).reshape(-1, 2)
    return ImageFeatures(keypoints=list(kps), descriptors=desc, xy=xy)


def detect_many(images_gray: list[np.ndarray], max_features: int = 8000) -> list[ImageFeatures]:
    return [detect(img, max_features=max_features) for img in images_gray]
