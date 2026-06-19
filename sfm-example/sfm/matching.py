"""Descriptor matching + geometric verification.

Two stages, both essential:
  1. Nearest-neighbour matching with **Lowe's ratio test** to reject ambiguous
     matches (the descriptor of the best match must be clearly better than the
     second best).
  2. **Geometric verification** with a RANSAC fundamental-matrix fit to throw out
     matches that are mutually inconsistent with a single rigid two-view geometry.

The output of stage 2 is what we trust enough to build tracks from.
"""

from __future__ import annotations

from dataclasses import dataclass

import cv2
import numpy as np

from .features import ImageFeatures


@dataclass
class PairMatches:
    """Verified matches between image i and image j."""

    i: int
    j: int
    matches: np.ndarray   # (M, 2) int: (kp index in i, kp index in j)

    def __len__(self) -> int:
        return len(self.matches)


def _ratio_match(desc1: np.ndarray, desc2: np.ndarray, ratio: float) -> np.ndarray:
    """Mutual? No -- one-directional kNN + Lowe ratio. Returns (M,2) index pairs."""
    if len(desc1) == 0 or len(desc2) == 0:
        return np.empty((0, 2), dtype=int)
    bf = cv2.BFMatcher(cv2.NORM_L2)
    knn = bf.knnMatch(desc1.astype(np.float32), desc2.astype(np.float32), k=2)
    good = []
    for pair in knn:
        if len(pair) < 2:
            continue
        m, n = pair
        if m.distance < ratio * n.distance:        # Lowe's ratio test
            good.append((m.queryIdx, m.trainIdx))
    return np.array(good, dtype=int).reshape(-1, 2)


def match_pair(
    feat_i: ImageFeatures,
    feat_j: ImageFeatures,
    i: int,
    j: int,
    ratio: float = 0.75,
    ransac_thresh: float = 1.5,
    min_matches: int = 20,
) -> PairMatches | None:
    """Match two images and geometrically verify with the fundamental matrix."""
    raw = _ratio_match(feat_i.descriptors, feat_j.descriptors, ratio)
    if len(raw) < min_matches:
        return None

    pts_i = feat_i.xy[raw[:, 0]]
    pts_j = feat_j.xy[raw[:, 1]]

    # RANSAC fundamental matrix: rejects matches inconsistent with epipolar geometry.
    F, inlier_mask = cv2.findFundamentalMat(
        pts_i, pts_j, method=cv2.FM_RANSAC, ransacReprojThreshold=ransac_thresh, confidence=0.999
    )
    if F is None or inlier_mask is None:
        return None
    inliers = inlier_mask.ravel().astype(bool)
    verified = raw[inliers]
    if len(verified) < min_matches:
        return None
    return PairMatches(i=i, j=j, matches=verified)


def match_exhaustive(
    feats: list[ImageFeatures],
    ratio: float = 0.75,
    ransac_thresh: float = 1.5,
    min_matches: int = 20,
) -> list[PairMatches]:
    """Match every image pair (O(n^2)). Fine for the small datasets in this demo;
    at scale you would use a vocabulary tree / image-retrieval shortlist instead."""
    pairs: list[PairMatches] = []
    n = len(feats)
    for i in range(n):
        for j in range(i + 1, n):
            pm = match_pair(feats[i], feats[j], i, j, ratio, ransac_thresh, min_matches)
            if pm is not None:
                pairs.append(pm)
    return pairs
