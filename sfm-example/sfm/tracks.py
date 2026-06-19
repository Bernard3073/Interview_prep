"""Feature tracks: chain pairwise matches into multi-view correspondences.

A *track* is the set of (image, keypoint) observations that all correspond to the
same physical 3D point. We build tracks with union-find over the verified pairwise
matches: each match unions two (image, keypoint) nodes; connected components are
tracks.

We reject inconsistent tracks -- those that observe two different keypoints in the
*same* image (a sign of a bad match chain). Each surviving track becomes a
candidate 3D point in the reconstruction.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from .matching import PairMatches


class _UnionFind:
    def __init__(self) -> None:
        self.parent: dict = {}

    def find(self, x):
        self.parent.setdefault(x, x)
        root = x
        while self.parent[root] != root:
            root = self.parent[root]
        while self.parent[x] != root:    # path compression
            self.parent[x], x = root, self.parent[x]
        return root

    def union(self, a, b):
        ra, rb = self.find(a), self.find(b)
        if ra != rb:
            self.parent[ra] = rb


@dataclass
class Track:
    """One multi-view correspondence. obs maps image index -> keypoint index."""

    track_id: int
    obs: dict = field(default_factory=dict)   # {image_idx: keypoint_idx}

    def images(self):
        return self.obs.keys()


def build_tracks(pair_matches: list[PairMatches]) -> list[Track]:
    """Union-find tracks from verified pairwise matches, dropping inconsistent ones."""
    uf = _UnionFind()
    for pm in pair_matches:
        for ki, kj in pm.matches:
            uf.union((pm.i, int(ki)), (pm.j, int(kj)))

    # Group nodes by their union-find root.
    groups: dict = {}
    for node in list(uf.parent.keys()):
        groups.setdefault(uf.find(node), []).append(node)

    tracks: list[Track] = []
    tid = 0
    for nodes in groups.values():
        if len(nodes) < 2:
            continue
        obs: dict = {}
        consistent = True
        for (img, kp) in nodes:
            if img in obs and obs[img] != kp:
                consistent = False        # same image, two different keypoints -> bad
                break
            obs[img] = kp
        if consistent and len(obs) >= 2:
            tracks.append(Track(track_id=tid, obs=obs))
            tid += 1
    return tracks
